from flask import current_app
from tweepy import OAuthHandler, API, TweepError, models
import logging


class TwitterApi:  # TODO Migrate to Twitter v2 when possible
    MAX_SCREEN_NAME_LENGTH = 15
    MAX_NAME_LENGTH = 50
    MAX_ID_STRING_LENGTH = 20

    def __init__(self, access_token, access_token_secret, consumer_key=None, consumer_secret=None):
        if (consumer_key or consumer_secret) is None:
            consumer_key = current_app.config['APP_CONSUMER_KEY']
            consumer_secret = current_app.config['APP_CONSUMER_SECRET']
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = API(auth)

    def rate_limit_status(self, resources: str):
        try:
            return self.api.rate_limit_status(resources=resources)
        except TweepError as e:
            raise TwitterApiException(reason=e.reason)

    # Users, friendships -----------------------------------------------------------------------------------------------
    def verify_credentials(self):
        try:
            return self.api.verify_credentials(skip_status=True)
        except TweepError as e:
            raise TwitterApiException(reason=e.reason)

    def get_followers_set(self):
        try:
            return set(self.api.followers_ids())
        except TweepError as e:
            raise TwitterApiException(reason=e.reason)

    def get_user(self, user_id):
        try:
            return self.api.get_user(user_id), None
        except TweepError as e:
            raise TwitterApiException(reason=e.reason)

    def get_users_lookup(self, users_id):
        max_users_lookup_per_window = 900
        user_ids_per_users_lookup = 100
        try:
            start = 0
            end = user_ids_per_users_lookup
            iterations = 0
            twitter_users = []

            while iterations < max_users_lookup_per_window and end < len(users_id):
                twitter_users.extend(self.api.lookup_users(user_ids=users_id[start:end]))
                start = end
                end += user_ids_per_users_lookup
                iterations += 1
            if iterations != max_users_lookup_per_window:
                twitter_users.extend(self.api.lookup_users(user_ids=users_id[start: len(users_id)]))

            return twitter_users
        except TweepError as e:
            raise TwitterApiException(reason=e.reason)

    def get_friendships_lookup(self, users_ids):
        try:
            return self.api.lookup_friendships(user_ids=users_ids)
        except TweepError as e:
            raise TwitterApiException(reason=e.reason)

    def get_friendship_show(self, source_screen_name, target_id):
        try:
            return self.api.show_friendship(source_screen_name=source_screen_name, target_id=target_id), None
        except TweepError as e:
            return None, e  # Does not raise exception because error provide useful info (user deleted, suspended)

    # Direct Messages --------------------------------------------------------------------------------------------------
    def send_direct_message(self, sender_screen_name, text):
        logging.debug('Sending direct message: \"{}\"'.format(text))
        try:
            user = self.api.get_user(screen_name=sender_screen_name)
            return self.api.send_direct_message(text=text, recipient_id=user.id)
        except TweepError as e:
            raise TwitterApiException(e.reason)

    def delete_direct_message(self, dm_id):
        try:
            return self.api.destroy_direct_message(id=dm_id)
        except TweepError as e:
            raise TwitterApiException("Unable to delete direct message n°{}: {}".format(dm_id, e.reason))

    # Tweets, timeline, favorites --------------------------------------------------------------------------------------
    # def get_user_timeline(self, user_screen_name):
    #     try:
    #         return self.api.GetUserTimeline(screen_name=user_screen_name, count=200, since_id=20)
    #     except error.TwitterError as e:
    #         logging.error('Unable to get user @{0} timeline: {1}'.format(user_screen_name, e.message))
    #         return None
    # 
    # def get_favorites(self, screen_name):
    #     try:
    #         return self.api.GetFavorites(screen_name=screen_name, count=200, since_id=20)
    #     except error.TwitterError as e:
    #         logging.error('Unable to get user @{0} favorites: {1}'.format(screen_name, e.message))
    #         return None
    # 
    # def delete_status(self, status_id):
    #     try:
    #         return self.api.DestroyStatus(status_id)
    #     except error.TwitterError as e:
    #         logging.error('Unable to delete status n°{0} because of error: {1}'.format(status_id, e.message))
    #         return None
    # 
    # def delete_favorite(self, status_id):
    #     try:
    #         return self.api.DestroyFavorite(status_id=status_id)
    #     except error.TwitterError as e:
    #         logging.error('Unable to delete favorite tweet n°{0} because of error: {1}'.format(status_id, e.message))
    #         return None

    # def delete_old_stuff(self, items_type, number_of_preserved_items):
    #     if items_type == 'tweet' or items_type == 'retweet':
    #         items = self.get_user_timeline()
    #         rate_limit = self.check_rate_limit(self.DESTROY_STATUS_ENDPOINT)
    #         if items_type == 'retweet':
    #             items = list(filter(lambda x: x.retweeted is True, items))
    #     elif items_type == 'favorite':
    #         items = self.get_favorites()
    #         rate_limit = self.check_rate_limit(self.DESTROY_FAVORITE_ENDPOINT)
    #     else:
    #         logging.error('This type of item to delete is not valid: {0}'.format(items_type))
    #         return []
    # 
    #     if rate_limit is not None:
    #         logging.debug('Deletable status - Remaining: {} - Reset: {}'.format(rate_limit.remaining, rate_limit.reset))
    #         if rate_limit.remaining < len(items) - number_of_preserved_items:
    #             start_index = len(items) - rate_limit.remaining
    #         else:
    #             start_index = number_of_preserved_items
    #     else:
    #         logging.error('Unable to check the rate limit of the endpoint used to destroy {0}. No {0} will be deleted.')
    #         return []
    # 
    #     deleted_items = []
    #     for i in range(start_index, len(items)):
    #         if items_type == 'favorite':
    #             deleted_item = self.delete_favorite(items[i].id)
    #         else:
    #             deleted_item = self.delete_status(items[i].id)
    #         if deleted_item is not None:
    #             deleted_items.append(deleted_item)
    #         logging.info('Delete {0} n°{1} from {2}'.format(items_type, items[i].id, items[i].user.screen_name))
    #     return deleted_items

    # Static methods----------------------------------------------------------------------------------------------------
    @staticmethod
    def get_authorize_url(callback_url: str) -> (str, dict):
        try:
            auth = OAuthHandler(current_app.config['APP_CONSUMER_KEY'], current_app.config['APP_CONSUMER_SECRET'],
                                callback_url)
            authorize_url = auth.get_authorization_url(signin_with_twitter=True)
            return authorize_url, auth.request_token
        except TweepError as e:
            raise TwitterApiException(e)

    @staticmethod
    def get_twitter_credentials(oauth_token: str, oauth_token_secret: str, oauth_verifier: str) -> (models.User, str,
                                                                                                    str):
        try:
            auth = OAuthHandler(current_app.config['APP_CONSUMER_KEY'],
                                current_app.config['APP_CONSUMER_SECRET'])
            auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_token_secret}
            (access_token, access_token_secret) = auth.get_access_token(oauth_verifier)
            auth.set_access_token(access_token, access_token_secret)
            twitter_api = TwitterApi(access_token, access_token_secret)
            return twitter_api.verify_credentials(), access_token, access_token_secret
        except TweepError as e:
            raise TwitterApiException(reason=e.reason)


class TwitterApiException(Exception):

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason
