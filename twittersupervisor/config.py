import logging
from os import environ
from .twitter_api import TwitterApi
from twitter import error


class Config:
    LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    DEFAULT_LOG_FILE = "twitter_supervisor.log"
    DEFAULT_LOG_LEVEL = "INFO"

    @staticmethod
    def set_logging_config(log_file_name, log_level):
        # logging to file
        logging.basicConfig(level=log_level,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=log_file_name)
        # logging to console
        console = logging.StreamHandler()
        console.setLevel(log_level)
        formatter = logging.Formatter('%(levelname)-8s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    @classmethod
    def check_config(cls, config, config_source):

        # Logging
        if 'LOG_LEVEL' not in config:
            if 'LOG_FILE' not in config:
                cls.set_logging_config(cls.DEFAULT_LOG_FILE, cls.DEFAULT_LOG_LEVEL)
                logging.warning("No 'LOG_LEVEL' and 'LOG_FILE' were found in {0}. Default values are used: LOG_FILE={1}"
                                ", LOG_LEVEL={2}".format(config_source, cls.DEFAULT_LOG_FILE, cls.DEFAULT_LOG_LEVEL))
            else:
                # TODO check if log file is valid (good name, can be written)
                cls.set_logging_config(config['LOG_FILE'], cls.DEFAULT_LOG_LEVEL)
                logging.warning("No 'LOG_LEVEL' was found in {0}. Default value is used: LOG_LEVEL={1}"
                                .format(config_source, cls.DEFAULT_LOG_LEVEL))
        else:
            if 'LOG_FILE' not in config:
                cls.set_logging_config(cls.DEFAULT_LOG_FILE, config['LOG_LEVEL'])
                logging.warning("No 'LOG_FILE' was found in {0}. Default value is used: LOG_FILE={1}"
                                .format(config_source, cls.DEFAULT_LOG_FILE))
            else:
                cls.set_logging_config(config['LOG_FILE'], config['LOG_LEVEL'])

        # Check if all the mandatory config keys are set
        if 'SECRET_KEY' not in config:
            raise ConfigException("No 'SECRET_KEY' key found in app config. Check the config source: {}"
                                  .format(config_source))
        if 'APP_CONSUMER_KEY' not in config:
            raise ConfigException("No 'APP_CONSUMER_KEY' key found in app config. Check the config source: {}"
                                  .format(config_source))
        if 'APP_CONSUMER_SECRET' not in config:
            raise ConfigException("No 'APP_CONSUMER_SECRET' key found in app config. Check the config source: {}"
                                  .format(config_source))
        if 'DATABASE_FILE' not in config:
            raise ConfigException("No 'DATABASE_FILE' key found in app config. Check the config source: {}"
                                  .format(config_source))

        # Check if Twitter API keys work
        if ('DEFAULT_ACCESS_TOKEN' in config) and ('DEFAULT_ACCESS_TOKEN_SECRET' in config):
            api = TwitterApi(config['DEFAULT_ACCESS_TOKEN'], config['DEFAULT_ACCESS_TOKEN_SECRET'],
                             config['APP_CONSUMER_KEY'], config['APP_CONSUMER_SECRET'])

            try:
                api.verify_credentials()
            except error as e:
                raise ConfigException(e.message)

    @classmethod
    def get_config_from_env(cls):
        config = dict()
        try:
            config['DEFAULT_ACCESS_TOKEN'] = environ['DEFAULT_ACCESS_TOKEN']
            config['DEFAULT_ACCESS_TOKEN_SECRET'] = environ['DEFAULT_ACCESS_TOKEN_SECRET']
            config['APP_CONSUMER_KEY'] = environ['APP_CONSUMER_KEY']
            config['APP_CONSUMER_SECRET'] = environ['APP_CONSUMER_SECRET']
            config['DEFAULT_USER'] = environ['DEFAULT_USER']
        except KeyError as ke:
            raise ConfigException("Missing required environment variable: {}".format(ke))
        return config


class ConfigException(Exception):

    def __init__(self, reason):
        self.message = reason
