from unittest import TestCase
from tests import shared_test_data
from twittersupervisor import Config


class TestConfig(TestCase):

    CORRECT_TWITTER_API_CONFIG = {'username': 'ausername', 'consumer_key': 'aconsumerkey',
                                  'consumer_secret': 'aconsumersecret',
                                  'access_token': 'anaccesstoken',
                                  'access_token_secret': 'anaccesstokensecret'}
    CORRECT_DB_NAME = 'a_database_file.db'

    # Complete config file case
    def test_complete_config(self):
        complete_config = Config(shared_test_data.COMPLETE_CONFIG_FILE)
        self.assertEqual(complete_config.twitter_credentials, TestConfig.CORRECT_TWITTER_API_CONFIG)
        self.assertEqual(complete_config.database_name, TestConfig.CORRECT_DB_NAME)

    # Missing "database_name" entry case
    def test_missing_database(self):
        missing_db_config = Config("test_data/missing_database_config.json")
        self.assertEqual(missing_db_config.twitter_credentials, TestConfig.CORRECT_TWITTER_API_CONFIG)
        self.assertEqual(missing_db_config.database_name, Config.DEFAULT_DB_FILE)

    # Missing "twitter_api" sub-key case
    def test_missing_credentials(self):
        self.assertRaises(KeyError, Config, "test_data/missing_consumer_key_config.json")
