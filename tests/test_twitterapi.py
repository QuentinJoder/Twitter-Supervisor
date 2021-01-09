import pytest
from twitter import User, DirectMessage, UserStatus
from flask import current_app
from twittersupervisor import TwitterApi
from tests import shared_test_data


class TestTwitterApi:
    INCOMPLETE_CREDENTIALS = {'username': 'ausername', 'consumer_key': 'aconsumerkey',
                              'consumer_secret': 'aconsumersecret',
                              'access_token_secret': 'anaccesstokensecret'}

    @pytest.fixture
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
        user, error = twitter_api.get_user(shared_test_data.TWITTER_USER_ID)
        assert isinstance(user, User)
        assert user.name == 'Twitter'
        assert user.screen_name == 'Twitter'
        assert error is None

    @pytest.mark.api_call
    def test_get_friendship_lookup(self, twitter_api):
        friendships = twitter_api.get_friendship_lookup([shared_test_data.TWITTER_USER_ID])
        assert isinstance(friendships, list)
        friendship = friendships[0]
        assert isinstance(friendship, UserStatus)
        assert friendship.name == 'Twitter'
        assert friendship.screen_name == 'Twitter'

    @pytest.mark.api_call
    def test_send_message(self, twitter_api):
        message = twitter_api.send_direct_message("This is a test message.")
        assert isinstance(message, DirectMessage)
