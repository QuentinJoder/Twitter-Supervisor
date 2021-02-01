import logging

from twittersupervisor.models import AppUser, db
from twittersupervisor.twitter_api import TwitterApi, TwitterApiException
from .check_followers_service import CheckFollowersService, CheckFollowersContext

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    def get_authorize_url(callback_url: str) -> (str, dict):
        logger.debug("App callback URL: {}".format(callback_url))
        try:
            authorize_url, request_token = TwitterApi.get_authorize_url(callback_url)
        except TwitterApiException as e:
            raise AuthException(reason=e.reason)
        return authorize_url, request_token

    @classmethod
    def login(cls, oauth_token: str, oauth_token_secret: str, oauth_verifier: str) -> AppUser:
        # Get user, access token and secret
        try:
            (twitter_user, access_token, access_token_secret) = TwitterApi.get_twitter_credentials(oauth_token=oauth_token,
                                                                                                   oauth_token_secret=oauth_token_secret,
                                                                                                   oauth_verifier=oauth_verifier)
        except TwitterApiException as error:
            logger.error(error)
            raise AuthException(reason=error.reason)

        db_user = AppUser.query.filter_by(id=twitter_user.id).first()
        # New user
        if db_user is None:
            db_user = cls.__merge_app_user(twitter_user, access_token, access_token_secret)
            CheckFollowersService.check_followers(twitter_user.screen_name, CheckFollowersContext.FIRST_TIME)
        # Existing user, but he changed his name and/or screen name
        elif (db_user.screen_name != twitter_user.screen_name) or (db_user.name != twitter_user.name):
            db_user = cls.__merge_app_user(twitter_user, access_token, access_token_secret)
        return db_user

    @staticmethod
    def __merge_app_user(twitter_user, access_token: str, access_token_secret: str) -> AppUser:
        user = AppUser(id=twitter_user.id, id_str=twitter_user.id_str,
                       screen_name=twitter_user.screen_name, name=twitter_user.name,
                       access_token=access_token, access_token_secret=access_token_secret)
        db.session.merge(user)
        db.session.commit()
        return user


class AuthException(Exception):
    def __init__(self, reason):
        self.reason = reason
