from twittersupervisor.twitter_api import TwitterApi
from twittersupervisor.models import AppUser, FollowEvent, TwitterUser, db


class TwitterUserService:
    @classmethod
    def update_related_users_info(cls, username, users_id):
        # Setup
        users_amount = len(users_id)
        twitter_api = TwitterApiService.get_twitter_api_instance(username)
        start = 0
        end = TwitterApi.USER_IDS_PER_USERS_LOOKUP
        iterations = 0
        twitter_users = []
        # Collect users data
        while iterations < TwitterApi.MAX_USERS_LOOKUP_PER_WINDOW and end < users_amount:
            twitter_users.extend(twitter_api.get_users_lookup(users_id[start:end]))
            start = end
            end += TwitterApi.USER_IDS_PER_USERS_LOOKUP
            iterations += 1
        if iterations != TwitterApi.MAX_USERS_LOOKUP_PER_WINDOW:
            twitter_users.extend(twitter_api.get_users_lookup(users_id[start: users_amount]))
        # Persist in DB
        for user in twitter_users:
            db.session.merge(TwitterUser(id=user.id, name=user.name, screen_name=user.screen_name))
        db.session.commit()


class AppUserService:

    @staticmethod
    def get_app_users():
        return AppUser.query.all()

    @staticmethod
    def get_app_user(username: str):
        return AppUser.query.filter_by(screen_name=username).one()

    @staticmethod
    def get_followers(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        followers = user.followers
        serialized_followers = []
        for follower in followers:
            serialized_followers.append(follower.to_dict())
        return serialized_followers

    @classmethod
    def update_followers_and_unfollowers(cls, user: AppUser):
        # Comparison
        previous_followers = cls._get_followers_set(user)
        twitter_api = TwitterApiService.get_twitter_api_instance(user.screen_name)
        current_followers = twitter_api.get_followers_set()
        new_followers_set = current_followers - previous_followers
        new_unfollowers_set = previous_followers - current_followers

        # Save new followers in DB
        for follower_id in new_followers_set:
            follower = TwitterUser.query.filter_by(id=follower_id).first()
            if follower is None:
                follower = TwitterUser(id=follower_id)
            else:
                try:
                    user.unfollowers.remove(follower)
                except ValueError:
                    pass
            user.followers.append(follower)

        # Save new unfollowers in DB
        for unfollower in new_unfollowers_set:
            traitor = TwitterUser.query.filter_by(id=unfollower).one()
            user.followers.remove(traitor)
            user.unfollowers.append(traitor)

        # Commit and return
        db.session.commit()
        return new_followers_set, new_unfollowers_set

    @classmethod
    def _get_followers_set(cls, user):
        result = set()
        for follower in user.followers:
            result.add(follower.id)
        return result


class FollowEventService:

    @staticmethod
    def get_follow_events(username: str, follower_id: int):
        user_id = AppUser.query.filter_by(screen_name=username).one().id
        events_list = FollowEvent.query.filter_by(followed_id=user_id, follower_id=follower_id).all()
        serialized_events = []
        for event in events_list:
            serialized_events.append(event.to_dict())
        return serialized_events


class DirectMessageService:

    @classmethod
    def send_direct_message(cls, sender_screen_name: str, text: str, api_instance=None):
        if api_instance is None:
            api_instance = TwitterApiService.get_twitter_api_instance(sender_screen_name)
        api_instance.send_direct_message(sender_screen_name, text)

    @classmethod
    def present_new_followers(cls, username: str, followers_set: set):
        if len(followers_set) != 0:  # Avoid useless "GET friendships/lookup" request
            twitter_api = TwitterApiService.get_twitter_api_instance(username)
            friendships_info = twitter_api.get_friendship_lookup(list(followers_set))
            for friendship_info in friendships_info:
                message = '@{} follows you now.'.format(friendship_info.screen_name)
                if friendship_info.connections['following']:
                    message = message + ' You are a follower of this user.'
                if friendship_info.connections['muting']:
                    message = message + ' You muted this user.'
                cls.send_direct_message(username, message, twitter_api)
                user = TwitterUser(id=friendship_info.id, screen_name=friendship_info.screen_name, name=friendship_info.name)
                db.session.merge(user)
            db.session.commit()

    @classmethod
    def denounce_traitors(cls, username, traitors):
        for traitor in traitors:
            twitter_api = TwitterApiService.get_twitter_api_instance(username)
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
                cls.send_direct_message(username, 'One of your follower\'s account ({}) has been deleted'
                                        .format(traitor_name), twitter_api)
            elif hasattr(error, 'api_code') and error.api_code == 63:
                traitor_name = cls._get_username(traitor)
                cls.send_direct_message(username, 'One of your follower\'s account ({}) has been suspended'
                                        .format(traitor_name), twitter_api)

    @staticmethod
    def _get_username(user_id):
        user = TwitterUser.query.filter_by(id=user_id).first()
        if user is None or user.screen_name is None:
            name = 'n°{}'.format(user_id)
        else:
            name = '@{}'.format(user.screen_name)
        return name


class TwitterApiService:

    @staticmethod
    def get_twitter_api_instance(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        return TwitterApi(access_token=user.access_token, access_token_secret=user.access_token_secret)
