import pytest
from twitter import User, DirectMessage, TwitterError, UserStatus
from unittest import TestCase
from twittersupervisor import ConfigFileParser, TwitterApi
from tests import shared_test_data


class ApiTest(TestCase):
    INCOMPLETE_CREDENTIALS = {'username': 'ausername', 'consumer_key': 'aconsumerkey',
                              'consumer_secret': 'aconsumersecret',
                              'access_token_secret': 'anaccesstokensecret'}
    CONFIG_FILE = 'config.json'

    def setUp(self):
        if self._testMethodName != 'test_init':
            self.twitter_api = TwitterApi(ConfigFileParser(ApiTest.CONFIG_FILE).get_twitter_api_credentials())

    def test_init(self):
        self.assertRaises(TypeError, TwitterApi, None)
        self.assertRaises(KeyError, TwitterApi, ApiTest.INCOMPLETE_CREDENTIALS)

    @pytest.mark.api_call
    def test_verify_credentials(self):
        user = self.twitter_api.verify_credentials()
        self.assertIsInstance(user, User)
        invalid_twitter_api = TwitterApi(ConfigFileParser(shared_test_data.COMPLETE_CONFIG_FILE)
                                         .get_twitter_api_credentials())
        with pytest.raises(TwitterError):
            invalid_twitter_api.verify_credentials()

    @pytest.mark.api_call
    def test_get_followers(self):
        followers_set = self.twitter_api.get_followers_set()
        self.assertIsInstance(followers_set, set)

    @pytest.mark.api_call
    def test_get_user(self):
        user, error = self.twitter_api.get_user(shared_test_data.TWITTER_USER_ID)
        self.assertIsInstance(user, User)
        self.assertEqual(user.name, 'Twitter')
        self.assertEqual(user.screen_name, 'Twitter')
        self.assertIsNone(error)

    @pytest.mark.api_call
    def test_get_friendship_lookup(self):
        friendships = self.twitter_api.get_friendship_lookup([shared_test_data.TWITTER_USER_ID])
        self.assertIsInstance(friendships, list)
        friendship = friendships[0]
        self.assertIsInstance(friendship, UserStatus)
        self.assertEqual(friendship.name, 'Twitter')
        self.assertEqual(friendship.screen_name, 'Twitter')

    @pytest.mark.api_call
    def test_send_message(self):
        message = self.twitter_api.send_direct_message("This is a test message.")
        self.assertIsInstance(message, DirectMessage)
