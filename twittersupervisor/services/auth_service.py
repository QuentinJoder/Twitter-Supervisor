import logging

from flask import current_app
from tweepy import OAuthHandler, TweepError

from twittersupervisor.models import AppUser, db
from twittersupervisor.twitter_api import TwitterApi
from .check_followers_service import CheckFollowersService, CheckFollowersContext


class AuthService:

    @staticmethod
    def get_authorize_url(callback_url: str) -> (OAuthHandler, str):
        logging.debug("App callback URL: {}".format(callback_url))
        auth = OAuthHandler(current_app.config['APP_CONSUMER_KEY'], current_app.config['APP_CONSUMER_SECRET'],
                            callback_url)
        try:
            authorize_url = auth.get_authorization_url(signin_with_twitter=True)
        except TweepError as error:
            logging.error(error)
            raise AuthException(error)
        return auth, authorize_url

    @classmethod
    def login(cls, oauth_token: str, oauth_token_secret: str, oauth_verifier: str) -> AppUser:
        # Get access token and secret
        auth = OAuthHandler(current_app.config['APP_CONSUMER_KEY'], current_app.config['APP_CONSUMER_SECRET'])
        auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_token_secret}
        try:
            (access_token, access_token_secret) = auth.get_access_token(oauth_verifier)
            auth.set_access_token(access_token, access_token_secret)
            twitter_api = TwitterApi(access_token, access_token_secret)
            twitter_user = twitter_api.verify_credentials()
        except TweepError as error:
            logging.error(error)
            raise AuthException(reason=error.reason)

        db_user = AppUser.query.filter_by(id=twitter_user.id).first()
        # New user
        if db_user is None:
            db_user = cls.__merge_app_user(twitter_user, access_token, access_token_secret)
            CheckFollowersService.check_followers(twitter_user.screen_name, CheckFollowersContext.FIRST_TIME.value)
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
