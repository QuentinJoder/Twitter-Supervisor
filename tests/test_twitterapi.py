import pytest
from time import sleep
from twitter import User, UserStatus
from tweepy import DirectMessage
from flask import current_app
from twittersupervisor import TwitterApi
from tests import conftest


# The purpose of this test class is to check if the libraries used to access the Twitter API and the API endpoints are
# still working as intended
class TestTwitterApi:

    @pytest.fixture(scope="class")
    def twitter_api(self, app):
        with app.app_context():
            config_dict = current_app.config
            return TwitterApi(access_token=config_dict['DEFAULT_ACCESS_TOKEN'],
                              access_token_secret=config_dict['DEFAULT_ACCESS_TOKEN_SECRET'],
                              consumer_key=config_dict['APP_CONSUMER_KEY'],
                              consumer_secret=config_dict['APP_CONSUMER_SECRET'],
                              username=config_dict['DEFAULT_USER'])

    @pytest.mark.api_call
    def test_verify_credentials(self, twitter_api):
        user = twitter_api.verify_credentials()
        assert isinstance(user, User)

    @pytest.mark.api_call
    def test_get_followers(self, twitter_api):
        followers_set = twitter_api.get_followers_set()
        assert isinstance(followers_set, set)

    @pytest.mark.api_call
    def test_get_user(self, twitter_api):
        user, error = twitter_api.get_user(conftest.TWITTER_USER_ID)
        assert isinstance(user, User)
        assert user.name == 'Twitter'
        assert user.screen_name == 'Twitter'
        assert error is None

    @pytest.mark.api_call
    def test_get_friendship_lookup(self, twitter_api):
        friendships = twitter_api.get_friendship_lookup([conftest.TWITTER_USER_ID])
        assert isinstance(friendships, list)
        friendship = friendships[0]
        assert isinstance(friendship, UserStatus)
        assert friendship.name == 'Twitter'
        assert friendship.screen_name == 'Twitter'

    @pytest.mark.api_call
    def test_send_message(self, twitter_api):
        message = twitter_api.send_direct_message("This is a test message.")
        assert isinstance(message, DirectMessage)
        sleep(2)  # Wait for DM to be "published" to prevent deletion error
        twitter_api.delete_direct_message(message.id)
