from .twitter_api_service import TwitterApiService
from twittersupervisor.models import db, TwitterUser


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
