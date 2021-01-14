from unittest import mock
from twitter import UserStatus
from flask import current_app
from twittersupervisor.messaging import Messaging
from twittersupervisor.twitter_api import TwitterApi
from tests import conftest


class TestMessaging:

    def test_publish_message_use_correct_media(self, app):

        with app.app_context():
            twitter_api = TwitterApi(access_token=current_app.config['DEFAULT_ACCESS_TOKEN'],
                                     access_token_secret=current_app.config['DEFAULT_ACCESS_TOKEN_SECRET'],
                                     username="JanKowalski")

        with mock.patch('twittersupervisor.TwitterApi.get_friendship_lookup') as get_lookup:
            get_lookup.return_value = [UserStatus(id=783214, name="Twitter", screen_name="twitter")]
            with mock.patch('twittersupervisor.TwitterApi.send_direct_message', unsafe=True) as send_dm:
                # Case quiet
                messaging = Messaging(twitter_api)
                messaging.present_new_followers([conftest.TWITTER_USER_ID])
                send_dm.assert_not_called()
                # Case "not quiet"
                messaging = Messaging(twitter_api, quiet=False)
                messaging.present_new_followers([conftest.TWITTER_USER_ID])
                send_dm.assert_called_once()

    # TODO Add more tests: special characters correctly managed, message corresponding to the connections...
