from datetime import datetime
import logging
from enum import Enum

from twittersupervisor.models import AppUser, TwitterUser, FollowEvent, db, Settings
from twittersupervisor.twitter_api import TwitterApi, TwitterApiException

logger = logging.getLogger()


class CheckFollowersContext(Enum):
    FIRST_TIME = 'First time'
    PERIODIC_CHECK = 'Periodic check'


class CheckFollowersService:

    @classmethod
    def check_followers(cls, settings: Settings, context: CheckFollowersContext):
        # Setup
        user = settings.user
        logger.info("Check the followers of: @{0}".format(user.screen_name, user.id))
        twitter_api = TwitterApi(access_token=user.access_token, access_token_secret=user.access_token_secret)

        # Check rate limit
        rate_limit_status = twitter_api.rate_limit_status('followers')
        remaining_followers_ids = rate_limit_status['resources']['followers']['/followers/ids']['remaining']
        if remaining_followers_ids == 0:
            logger.warning("Abort 'check_followers' of @{} to respect rate limit of GET followers/ids".format(user.screen_name))
            return

        # Get users sets and update DB
        try:
            (new_followers_set, new_unfollowers_set) = cls._get_users_sets(twitter_api, user)
        except TwitterApiException as e:
            logger.error("Could not get current followers list of {0}, abort 'check_followers' because of error: {1}"
                         .format(user.screen_name, e.reason))
            return
        cls._update_followers_and_unfollowers(user, new_followers_set, new_unfollowers_set)
        cls._create_follow_events(user.id, new_followers_set, new_unfollowers_set)

        # TODO Add a direct message quota
        # TODO Act accordingly with settings
        # Send Direct Messages
        if context == CheckFollowersContext.PERIODIC_CHECK:
            if 0 < len(new_followers_set):
                cls.__present_new_followers(user.screen_name, new_followers_set, twitter_api)
            if 0 < len(new_unfollowers_set):
                cls.__denounce_traitors(user.screen_name, new_unfollowers_set, twitter_api)
        elif context == CheckFollowersContext.FIRST_TIME:
            cls.__send_direct_message(twitter_api, user.screen_name, "Welcome in Twitter Supervisor {} !"
                                      .format(user.screen_name))
            # TODO Launch an update_data task

        logger.info("@{0} has {1} new followers and has been unfollowed {2} times"
                    .format(user.screen_name, len(new_followers_set), len(new_unfollowers_set)))
        return

    @staticmethod
    def _get_users_sets(twitter_api: TwitterApi, user: AppUser) -> (set, set):
        previous_followers = set()
        for follower in user.followers:
            previous_followers.add(follower.id)
        current_followers = twitter_api.get_followers_set()
        new_followers_set = current_followers - previous_followers
        new_unfollowers_set = previous_followers - current_followers
        return new_followers_set, new_unfollowers_set

    @staticmethod
    def _update_followers_and_unfollowers(user: AppUser, new_followers_set: set, new_unfollowers_set: set):
        # Save new followers
        for follower_id in new_followers_set:
            follower = TwitterUser.query.filter_by(id=follower_id).first()
            if follower is None:
                follower = TwitterUser(id=follower_id, id_str=str(follower_id))
            else:
                user.unfollowers.remove(follower)
            user.followers.append(follower)

        # Save new unfollowers
        for unfollower in new_unfollowers_set:
            traitor = TwitterUser.query.filter_by(id=unfollower).one()
            user.followers.remove(traitor)
            user.unfollowers.append(traitor)

        # Commit and return
        db.session.commit()
        return new_followers_set, new_unfollowers_set

    @staticmethod
    def _create_follow_events(target_id: int, new_followers_set: set, unfollowers_set: set):
        for follower_id in new_followers_set:
            event = FollowEvent(followed_id=target_id, follower_id=follower_id, following=True,
                                event_date=datetime.utcnow())
            db.session.add(event)
        for follower_id in unfollowers_set:
            event = FollowEvent(followed_id=target_id, follower_id=follower_id, following=False,
                                event_date=datetime.utcnow())
            db.session.add(event)
        db.session.commit()
        return

    @classmethod
    def __present_new_followers(cls, username: str, followers_set: set, twitter_api: TwitterApi):
        if len(followers_set) > 10:
            cls.__send_direct_message(twitter_api, username,
                                      "Congratulations ! More than 10 account started following you during the "
                                      "last minute.")
            return

        # GET friendship/lookup
        try:
            friendships_info = twitter_api.get_friendships_lookup(list(followers_set))
        except TwitterApiException as e:
            logger.error("TwitterApiException: Could not GET friendship/lookup: {}".format(e.reason))
            return

        # Send DMs and update DB
        for friendship_info in friendships_info:
            message = '@{} follows you now.'.format(friendship_info.screen_name)
            if friendship_info.connections['following']:
                message = message + ' You are a follower of this user.'
            if friendship_info.connections['muting']:
                message = message + ' You muted this user.'
            cls.__send_direct_message(twitter_api, username, message)
            user = TwitterUser(id=friendship_info.id, id_str=friendship_info.id_str,
                               screen_name=friendship_info.screen_name, name=friendship_info.name)
            db.session.merge(user)
        db.session.commit()
        return

    @classmethod
    def __denounce_traitors(cls, username: str, unfollowers_set: set, twitter_api: TwitterApi):
        if len(unfollowers_set) > 10:
            cls.__send_direct_message(twitter_api, username,
                                      "Oops! More than 10 accounts unfollowed you during the last minute.")
            return

        for traitor in unfollowers_set:
            friendship, error = twitter_api.get_friendship_show(username, traitor)
            if error is None:
                target_info = friendship[0]
                message = '@{} unfollowed you'.format(target_info.screen_name)
                source_info = friendship[1]
                if source_info.blocking:
                    message = message + ' You blocked him/her.'
                if source_info.blocked_by:
                    message = message + ' This user blocks you.'
                if source_info.following:
                    message = message + ' You are a follower of this user.'
                if source_info.muting:
                    message = message + ' You muted this user.'
                cls.__send_direct_message(twitter_api, username, message)
            elif hasattr(error, 'api_code') and error.api_code == 50:
                traitor_name = cls.__get_username(traitor)
                cls.__send_direct_message(twitter_api, username, 'One of your follower\'s account ({}) has been deleted'
                                          .format(traitor_name))
            elif hasattr(error, 'api_code') and error.api_code == 63:
                traitor_name = cls.__get_username(traitor)
                cls.__send_direct_message(twitter_api, username,
                                          'One of your follower\'s account ({}) has been suspended'
                                          .format(traitor_name))
        return

    @staticmethod
    def __send_direct_message(twitter_api: TwitterApi, sender: str, message: str):
        try:
            twitter_api.send_direct_message(sender, message)
        except TwitterApiException as e:
            logger.error('TwitterApiException: Unable to send direct message: {}'.format(e.reason))

    @staticmethod
    def __get_username(user_id):
        user = TwitterUser.query.filter_by(id=user_id).first()
        if user is None or user.screen_name is None:
            name = 'n°{}'.format(user_id)
        else:
            name = '@{}'.format(user.screen_name)
        return name
