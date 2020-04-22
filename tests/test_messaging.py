from unittest import TestCase, mock
from argparse import Namespace
from twitter import UserStatus
from twittersupervisor import Messaging, TwitterApi, Config
from tests import shared_test_data


class TestMessaging(TestCase):

    def setUp(self):
        self.twitter_api = TwitterApi(Config(shared_test_data.COMPLETE_CONFIG_FILE).twitter_credentials)

    def test_announce_follow_event_use_correct_media(self):
        with mock.patch('twittersupervisor.TwitterApi.get_friendship_lookup') as get_lookup:
            get_lookup.return_value = [UserStatus(id=783214, name="Twitter", screen_name="twitter")]
            with mock.patch('twittersupervisor.TwitterApi.send_direct_message', unsafe=True) as send_dm:
                # Case quiet
                self.messaging = Messaging(self.twitter_api, Namespace(quiet=True))
                self.messaging.announce_follow_event(True, [shared_test_data.TWITTER_USER_ID])
                send_dm.assert_not_called()
                # Case "not quiet"
                self.messaging.args = Namespace(quiet=False)
                self.messaging.announce_follow_event(True, [shared_test_data.TWITTER_USER_ID])
                send_dm.assert_called_once()

    # TODO Add more tests: special characters correctly managed, message corresponding to the connections...
