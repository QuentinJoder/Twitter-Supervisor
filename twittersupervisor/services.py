from twittersupervisor import TwitterApi
from twittersupervisor.models import AppUser, FollowEvent, TwitterUser


class TwitterUserService:

    @staticmethod
    def get_followers(username: str):
        user = AppUser.query.filter_by(screen_name=username).first()
        followers = user.followers
        serialized_followers = []
        for follower in followers:
            serialized_followers.append(follower.to_dict())
        return serialized_followers


class FollowEventService:

    @staticmethod
    def get_follow_events(username: str, follower_id: int):
        user_id = AppUser.query.filter_by(screen_name=username).first().id
        events_list = FollowEvent.query.filter_by(followed_id=user_id, follower_id=follower_id).all()
        serialized_events = []
        for event in events_list:
            serialized_events.append(event.to_dict())
        return serialized_events


class DirectMessageService:

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
                twitter_api.send_direct_message(username, message)

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
                twitter_api.send_direct_message(username, 'One of your follower\'s account ({}) has been deleted'
                                                .format(traitor_name))
            elif hasattr(error, 'api_code') and error.api_code == 63:
                traitor_name = cls._get_username(traitor)
                twitter_api.send_direct_message(username, 'One of your follower\'s account ({}) has been suspended'
                                                .format(traitor_name))

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
        user = AppUser.query.filter_by(screen_name=username).first()
        return TwitterApi(access_token=user.access_token, access_token_secret=user.access_token_secret)
