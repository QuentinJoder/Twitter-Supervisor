from pytest import raises
from unittest.mock import patch
from flask import current_app
from random import randint
from twittersupervisor.config import Config, ConfigException


class TestConfig:

    def test_set_logging_config(self):
        # Hard to test because log_level is set by pytest
        pass

    def test_check_config_parameter(self):
        # LOG LEVEL
        # Correct
        for log_level in Config.LOG_LEVELS:
            value = Config.check_config_parameter('LOG_LEVEL', log_level)
            assert value == log_level

        # Incorrect
        value = Config.check_config_parameter('LOG_LEVEL', 2)
        assert value == Config.DEFAULT_VALUES['LOG_LEVEL']
        value = Config.check_config_parameter('LOG_LEVEL', "Prout")
        assert value == Config.DEFAULT_VALUES['LOG_LEVEL']

        # DEFAULT_USER
        user = "Twitter"
        assert Config.check_config_parameter('DEFAULT_USER', user) == user
        user = "verymuchtolonguser"
        assert Config.check_config_parameter('DEFAULT_USER', user) is None

    def test_check_config(self, app):
        with patch('twittersupervisor.twitter_api.TwitterApi.verify_credentials') as vc_mock:
            vc_mock.return_value = "foo"

            # Perfect case
            with app.app_context():
                perfect_config = {'SECRET_KEY': "sk", 'APP_CONSUMER_KEY': current_app.config['APP_CONSUMER_KEY'],
                                  'APP_CONSUMER_SECRET': current_app.config['APP_CONSUMER_SECRET'],
                                  'DEFAULT_ACCESS_TOKEN': current_app.config['DEFAULT_ACCESS_TOKEN'],
                                  'DEFAULT_ACCESS_TOKEN_SECRET': current_app.config['DEFAULT_ACCESS_TOKEN_SECRET'],
                                  'DEFAULT_USER': current_app.config['DEFAULT_USER'],
                                  'SQLALCHEMY_DATABASE_URI': "sdu", 'LOG_LEVEL': "DEBUG", 'LOG_FILE': "lf.log"}
                assert perfect_config == Config.check_config(perfect_config, "config.cfg")
                assert perfect_config == Config.check_config(perfect_config, "ENV variables")
                assert vc_mock.call_count == 2

            # Missing optional key
            imperfect_config, missing_key = self.remove_random_key(Config.OPTIONAL_KEYS, perfect_config)
            checked_config = Config.check_config(imperfect_config, "config.cfg")
            for key in imperfect_config:
                if key is missing_key:
                    if key in Config.DEFAULT_VALUES:
                        assert checked_config[key] == Config.DEFAULT_VALUES[key]
                    else:
                        assert key not in checked_config
                else:
                    assert checked_config[key] == imperfect_config[key]

            # Missing mandatory key
            invalid_config, missing_key = self.remove_random_key(Config.MANDATORY_KEYS, imperfect_config)
            with raises(ConfigException) as exc_info:
                Config.check_config(invalid_config, "config.cfg")
                error_message = str("The mandatory config key '{0}' was not found in app config: {1}")
                assert exc_info.value.message == error_message.format(missing_key, "config.cfg")

            # ConfigException should be called
            vc_mock.side_effect = ConfigException("Test message")
            with raises(ConfigException) as exc_info:
                Config.check_config(perfect_config, "config.cfg")

            # Verify_credentials should not be called
            vc_mock.reset_mock()
            test_config = {'SECRET_KEY': "sk", 'APP_CONSUMER_KEY': "ack", 'APP_CONSUMER_SECRET': "acs",
                           'DEFAULT_ACCESS_TOKEN': "dat", 'DEFAULT_USER': "du",
                           'SQLALCHEMY_DATABASE_URI': "db.sqlite3", 'LOG_LEVEL': "DEBUG", 'LOG_FILE': "lf.log"}
            Config.check_config(test_config, "config.cfg")
            vc_mock.assert_not_called()

    def test_get_config_from_env(self, monkeypatch):
        # Perfect config
        test_config = {'SECRET_KEY': "sk", 'APP_CONSUMER_KEY': "ack", 'APP_CONSUMER_SECRET': "acs",
                       'DEFAULT_ACCESS_TOKEN': "dat", 'DEFAULT_ACCESS_TOKEN_SECRET': "dats", 'DEFAULT_USER': "du",
                       'SQLALCHEMY_DATABASE_URI': "db.sqlite3", 'LOG_LEVEL': "DEBUG", 'LOG_FILE': "lf.log"}
        for entry in test_config:
            monkeypatch.setenv(entry, test_config[entry])
        config = Config.get_config_from_env()
        assert config == test_config

        # Missing key with a default value
        incomplete_config, missing_key = self.remove_random_key(list(Config.DEFAULT_VALUES.keys()), test_config)
        monkeypatch.delenv(missing_key)
        incomplete_config[missing_key] = Config.DEFAULT_VALUES[missing_key]
        config = Config.get_config_from_env()
        assert config == incomplete_config

        # Missing key without default value
        keys_without_default = list(test_config.keys())
        for key in list(Config.DEFAULT_VALUES.keys()):
            keys_without_default.remove(key)
        another_config, missing_key = self.remove_random_key(keys_without_default, test_config)
        monkeypatch.delenv(missing_key)
        config = Config.get_config_from_env()
        assert config == another_config

    @staticmethod
    def remove_random_key(key_list: list, a_dict: dict):
        keys_number = len(key_list)
        number_to_remove = randint(0, keys_number - 1)
        removed_key = key_list[number_to_remove]
        a_dict.pop(removed_key)
        return a_dict, removed_key
