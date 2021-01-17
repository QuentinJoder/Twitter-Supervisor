from twittersupervisor.models import AppUser
from twittersupervisor.twitter_api import TwitterApi


class TwitterApiService:

    @staticmethod
    def get_twitter_api_instance(username: str) -> TwitterApi:
        user = AppUser.query.filter_by(screen_name=username).one()
        return TwitterApi(access_token=user.access_token, access_token_secret=user.access_token_secret)

    @staticmethod
    def get_twitter_api_instance_from_token(access_token: str, access_token_secret: str) -> TwitterApi:
        return TwitterApi(access_token=access_token, access_token_secret=access_token_secret)
