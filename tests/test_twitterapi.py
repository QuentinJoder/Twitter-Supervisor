import pytest
from time import sleep
from tweepy.models import Relationship, User, Friendship
from tweepy import DirectMessage
from flask import current_app

from twittersupervisor.twitter_api import TwitterApi
from tests import conftest


# The purpose of this test class is to check if the libraries used to access the Twitter API and the API itself are
# still working as intended
class TestTwitterApi:

    @pytest.fixture(scope="class")
    def twitter_api(self, app):
        with app.app_context():
            config_dict = current_app.config
            return TwitterApi(access_token=config_dict['DEFAULT_ACCESS_TOKEN'],
                              access_token_secret=config_dict['DEFAULT_ACCESS_TOKEN_SECRET'],
                              consumer_key=config_dict['APP_CONSUMER_KEY'],
                              consumer_secret=config_dict['APP_CONSUMER_SECRET'])

    @pytest.mark.api_call
    def test_rate_limit_status(self, twitter_api):
        rate_limits = twitter_api.rate_limit_status('users,friendships,followers')
        # Useful to know if the rate limits of the endpoints used by Twitter Supervisor have changed
        assert rate_limits['resources']['followers']['/followers/ids']['limit'] == 15
        assert rate_limits['resources']['friendships']['/friendships/lookup']['limit'] == 15
        assert rate_limits['resources']['friendships']['/friendships/show']['limit'] == 180
        assert rate_limits['resources']['users']['/users/lookup']['limit'] == 900

    @pytest.mark.api_call
    def test_verify_credentials(self, twitter_api):
        user = twitter_api.verify_credentials()
        assert isinstance(user, User)

    @pytest.mark.api_call
    def test_get_followers(self, twitter_api):
        followers_set = twitter_api.get_followers_set()
        assert isinstance(followers_set, set)
        if len(followers_set) > 0:
            assert isinstance(followers_set.pop(), int)

    @pytest.mark.api_call
    def test_get_user(self, twitter_api):
        user, error = twitter_api.get_user(conftest.TWITTER_USER_ID)
        assert isinstance(user, User)
        assert user.name == 'Twitter'
        assert user.screen_name == 'Twitter'
        assert error is None

    @pytest.mark.api_call
    def test_users_lookup(self, twitter_api):
        users = twitter_api.get_users_lookup([conftest.TWITTER_USER_ID, conftest.LE_MONDE_USER_ID])
        assert isinstance(users, list)
        user = users[0]
        assert isinstance(user, User)
        assert user.screen_name == 'Twitter'

    @pytest.mark.api_call
    def test_get_friendships_lookup(self, twitter_api):
        friendships = twitter_api.get_friendships_lookup([conftest.TWITTER_USER_ID, conftest.LE_MONDE_USER_ID])
        assert isinstance(friendships, list)
        friendship = friendships[0]
        assert isinstance(friendship, Relationship)
        assert friendship.name == 'Twitter'
        assert friendship.screen_name == 'Twitter'

    @pytest.mark.api_call
    def test_get_friendship_show(self, twitter_api, app):
        with app.app_context():
            username = current_app.config['DEFAULT_USER']
            friendship, error = twitter_api.get_friendship_show(username, conftest.LE_MONDE_USER_ID)
            print(friendship)
            assert isinstance(friendship[0], Friendship)
            assert isinstance(friendship[1], Friendship)
            assert friendship[0].screen_name == username
            assert friendship[1].screen_name == "lemondefr"
            assert error is None

    @pytest.mark.api_call
    def test_send_message(self, twitter_api, app):
        with app.app_context():
            username = current_app.config['DEFAULT_USER']
            message = twitter_api.send_direct_message(username, "This is a test message.")
            assert isinstance(message, DirectMessage)
            sleep(2)  # Wait for DM to be "published" to prevent deletion error
            twitter_api.delete_direct_message(message.id)
