from flask import current_app
from twitter import Api, error
import tweepy
import logging

# TODO Migrate to Twitter v2 when a python lib will manage it
# TODO Raise TwitterApiException for each method failure
class TwitterApi:

    MAX_USERNAME_LENGTH = 15
    DESTROY_STATUS_ENDPOINT = "https://api.twitter.com/1.1/statuses/destroy/:id.json"
    DESTROY_FAVORITE_ENDPOINT = "https://api.twitter.com/1.1/favorites/destroy.json"

    # Rate limit per 15 minutes window #
    POST_DIRECT_MESSAGE_RATE_LIMIT = 10

    # Maximum amount of friendships we can look at with "GET friendships/lookup"
    MAX_AMOUNT_FRIENDSHIPS_LOOKUP = 100

    def __init__(self, access_token, access_token_secret, consumer_key=None, consumer_secret=None, username=None):
        self.username = username
        if (consumer_key or consumer_secret) is None:
            consumer_key = current_app.config['APP_CONSUMER_KEY']
            consumer_secret = current_app.config['APP_CONSUMER_SECRET']
        # python-twitter
        self.api = Api(consumer_key=consumer_key,
                       consumer_secret=consumer_secret,
                       access_token_key=access_token,
                       access_token_secret=access_token_secret)
        # tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.tweepy_api = tweepy.API(auth)

    def check_rate_limit(self, endpoint_url):
        try:
            return self.api.CheckRateLimit(endpoint_url)
        except error.TwitterError as e:
            logging.critical('An error happened when rate limit of endpoint {} was checked: {}'.format(endpoint_url, e.message))
            return None

    def verify_credentials(self):
        try:
            return self.api.VerifyCredentials(None, True)
        except error.TwitterError as e:
            logging.error('An error happened while checking the Twitter API credentials validity: {}'.format(e.message))
            raise

    def get_followers_set(self):
        try:
            return set(self.api.GetFollowerIDs())
        except error.TwitterError as e:
            logging.critical('Twitter Supervisor is unable to get the user\'s followers IDs list: {}'.format(e.message))
            raise

    def get_user(self, user_id):
        try:
            return self.api.GetUser(user_id), None
        except error.TwitterError as e:
            logging.error('An error happened while searching for user n°{0}: {1}'.format(user_id, e.message))
            return None, e.message

    def get_friendship_lookup(self, users_id):
        try:
            return self.api.LookupFriendship(users_id)
        except error.TwitterError as e:
            logging.critical('An error happened while looking up friendships: {}'.format(e.message))
            raise

    def get_friendship_show(self, target_id):
        try:
            return self.tweepy_api.show_friendship(source_screen_name=self.username, target_id=target_id), None
        except tweepy.TweepError as e:
            return None, e

    def send_direct_message(self, text):
        logging.info('Sending direct message: \"{}\"'.format(text))
        try:
            return self.api.PostDirectMessage(text, screen_name=self.username)
        except error.TwitterError as e:
            logging.error('Unable to send direct message: {}'.format(e.message))
            return None

    def delete_direct_message(self, dm_id):
        try:
            return self.tweepy_api.destroy_direct_message(id=dm_id)
        except tweepy.TweepError as e:
            raise TwitterApiException("Unable to delete direct message n°{}: {}".format(dm_id, e.reason))

    def get_user_timeline(self):
        try:
            return self.api.GetUserTimeline(screen_name=self.username, count=200, since_id=20)
        except error.TwitterError as e:
            logging.error('Unable to get user @{0} timeline: {1}'.format(self.username, e.message))
            return None

    def get_favorites(self):
        try:
            return self.api.GetFavorites(screen_name=self.username, count=200, since_id=20)
        except error.TwitterError as e:
            logging.error('Unable to get user @{0} favorites: {1}'.format(self.username, e.message))
            return None

    def delete_status(self, status_id):
        try:
            return self.api.DestroyStatus(status_id)
        except error.TwitterError as e:
            logging.error('Unable to delete status n°{0} because of error: {1}'.format(status_id, e.message))
            return None

    def delete_favorite(self, status_id):
        try:
            return self.api.DestroyFavorite(status_id=status_id)
        except error.TwitterError as e:
            logging.error('Unable to delete favorite tweet n°{0} because of error: {1}'.format(status_id, e.message))
            return None

    def delete_old_stuff(self, items_type, number_of_preserved_items):
        if items_type == 'tweet' or items_type == 'retweet':
            items = self.get_user_timeline()
            rate_limit = self.check_rate_limit(self.DESTROY_STATUS_ENDPOINT)
            if items_type == 'retweet':
                items = list(filter(lambda x: x.retweeted is True, items))
        elif items_type == 'favorite':
            items = self.get_favorites()
            rate_limit = self.check_rate_limit(self.DESTROY_FAVORITE_ENDPOINT)
        else:
            logging.error('This type of item to delete is not valid: {0}'.format(items_type))
            return []

        if rate_limit is not None:
            logging.debug('Deletable status - Remaining: {} - Reset: {}'.format(rate_limit.remaining, rate_limit.reset))
            if rate_limit.remaining < len(items) - number_of_preserved_items:
                start_index = len(items) - rate_limit.remaining
            else:
                start_index = number_of_preserved_items
        else:
            logging.error('Unable to check the rate limit of the endpoint used to destroy {0}. No {0} will be deleted.')
            return []

        deleted_items = []
        for i in range(start_index, len(items)):
            if items_type == 'favorite':
                deleted_item = self.delete_favorite(items[i].id)
            else:
                deleted_item = self.delete_status(items[i].id)
            if deleted_item is not None:
                deleted_items.append(deleted_item)
            logging.info('Delete {0} n°{1} from {2}'.format(items_type, items[i].id, items[i].user.screen_name))
        return deleted_items


class TwitterApiException(Exception):

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason
