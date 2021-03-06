from unittest import TestCase, mock
from argparse import Namespace
from twitter import UserStatus
from twittersupervisor import Messaging, TwitterApi, ConfigFileParser, Database
from tests import shared_test_data


class TestMessaging(TestCase):

    def setUp(self):
        config = ConfigFileParser(shared_test_data.COMPLETE_CONFIG_FILE)
        self.twitter_api = TwitterApi(config.get_twitter_api_credentials())
        self.database = Database(config.get_database_filename())

    def test_publish_message_use_correct_media(self):
        with mock.patch('twittersupervisor.TwitterApi.get_friendship_lookup') as get_lookup:
            get_lookup.return_value = [UserStatus(id=783214, name="Twitter", screen_name="twitter")]
            with mock.patch('twittersupervisor.TwitterApi.send_direct_message', unsafe=True) as send_dm:
                # Case quiet
                messaging = Messaging(Namespace(quiet=True), self.twitter_api, self.database)
                messaging.present_new_followers([shared_test_data.TWITTER_USER_ID])
                send_dm.assert_not_called()
                # Case "not quiet"
                messaging = Messaging(Namespace(quiet=False), self.twitter_api, self.database)
                messaging.present_new_followers([shared_test_data.TWITTER_USER_ID])
                send_dm.assert_called_once()

    # TODO Add more tests: special characters correctly managed, message corresponding to the connections...
