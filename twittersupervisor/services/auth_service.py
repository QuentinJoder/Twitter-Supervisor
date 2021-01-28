from twittersupervisor.models import AppUser, db
from twittersupervisor.twitter_api import TwitterApi


class AuthService:
    @staticmethod
    def create_app_user(access_token: str, access_token_secret: str):
        twitter_api = TwitterApi(access_token, access_token_secret)
        twitter_user = twitter_api.verify_credentials()
        user = AppUser(id=twitter_user.id, id_str=twitter_user.id_str,
                       screen_name=twitter_user.screen_name, name=twitter_user.name,
                       access_token=access_token, access_token_secret=access_token_secret)
        db.session.merge(user)
        db.session.commit()
        # TODO Launch a 'check_followers' task if it is a new user
        return user
