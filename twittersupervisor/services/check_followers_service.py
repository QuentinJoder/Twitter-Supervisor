from datetime import datetime
import logging
from enum import Enum

from twittersupervisor.models import AppUser, TwitterUser, FollowEvent, db
from twittersupervisor.twitter_api import TwitterApi

logger = logging.getLogger()


class CheckFollowersContext(Enum):
    FIRST_TIME = 'First time'
    PERIODIC_CHECK = 'Periodic check'


class CheckFollowersService:

    @classmethod
    def check_followers(cls, username: str, context: str):
        context = CheckFollowersContext(context)
        user = AppUser.query.filter_by(screen_name=username).one()
        logger.info("Check the followers of: @{0}".format(user.screen_name, user.id))
        twitter_api = TwitterApi(access_token=user.access_token, access_token_secret=user.access_token_secret)

        (new_followers_set, new_unfollowers_set) = cls._get_users_sets(twitter_api, user)
        cls._update_followers_and_unfollowers(user, new_followers_set, new_unfollowers_set)
        cls._create_follow_events(user.id, new_followers_set, new_unfollowers_set)

        if context == CheckFollowersContext.PERIODIC_CHECK:
            cls._present_new_followers(user.screen_name, new_followers_set, twitter_api)
            cls._denounce_traitors(user.screen_name, new_unfollowers_set, twitter_api)
        elif context == CheckFollowersContext.FIRST_TIME:
            twitter_api.send_direct_message(user.screen_name, "Welcome in Twitter Supervisor {} !"
                                            .format(user.screen_name))

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

    @staticmethod
    def _present_new_followers(username: str, followers_set: set, twitter_api: TwitterApi):
        if len(followers_set) != 0:  # Avoid useless "GET friendships/lookup" request
            # TODO Manage API error
            friendships_info = twitter_api.get_friendship_lookup(list(followers_set))
            for friendship_info in friendships_info:
                message = '@{} follows you now.'.format(friendship_info.screen_name)
                if friendship_info.connections['following']:
                    message = message + ' You are a follower of this user.'
                if friendship_info.connections['muting']:
                    message = message + ' You muted this user.'
                twitter_api.send_direct_message(username, message)
                user = TwitterUser(id=friendship_info.id, id_str=friendships_info.id_str,
                                   screen_name=friendship_info.screen_name, name=friendship_info.name)
                db.session.merge(user)
            db.session.commit()
            return

    @classmethod
    def _denounce_traitors(cls, username: str, unfollowers_set: set, twitter_api: TwitterApi):
        # TODO Rebuild this method (first a GET friendship/lookup the friendship/show for missing unfollowers)
        for traitor in unfollowers_set:
            friendships, error = twitter_api.get_friendship_show(username, traitor)
            if error is None:
                target_info = friendships[1]
                message = '@{} unfollowed you'.format(target_info.screen_name)
                source_info = friendships[0]
                if source_info.blocking:
                    message = message + ' You blocked him/her.'
                if source_info.blocked_by:
                    message = message + ' This user blocks you.'
                if source_info.following:
                    message = message + ' You are a follower of this user.'
                if source_info.muting:
                    message = message + ' You muted this user.'
                twitter_api.send_direct_message(username, message)
            elif hasattr(error, 'api_code') and error.api_code == 50:
                traitor_name = cls._get_username(traitor)
                twitter_api.send_direct_message(username, 'One of your follower\'s account ({}) has been deleted'
                                                .format(traitor_name))
            elif hasattr(error, 'api_code') and error.api_code == 63:
                traitor_name = cls._get_username(traitor)
                twitter_api.send_direct_message(username, 'One of your follower\'s account ({}) has been suspended'
                                                .format(traitor_name))
        return

    @staticmethod
    def _get_username(user_id):
        user = TwitterUser.query.filter_by(id=user_id).first()
        if user is None or user.screen_name is None:
            name = 'n°{}'.format(user_id)
        else:
            name = '@{}'.format(user.screen_name)
        return name
