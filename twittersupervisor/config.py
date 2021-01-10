import logging
from os import environ
from .twitter_api import TwitterApi
from twitter import error


class Config:
    LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    MANDATORY_KEYS = ['SECRET_KEY', 'APP_CONSUMER_KEY', 'APP_CONSUMER_SECRET']
    OPTIONAL_KEYS = ['DEFAULT_ACCESS_TOKEN', 'DEFAULT_ACCESS_TOKEN_SECRET', 'DEFAULT_USER', 'DATABASE_FILE',
                     'LOG_LEVEL', 'LOG_FILE']
    DEFAULT_VALUES = {'LOG_FILE': "twitter_supervisor.log", 'LOG_LEVEL': "INFO",
                      'DATABASE_FILE': "instance/twitter_supervisor.db"}

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
    def check_config_parameter(cls, key, value):
        def log_level():
            if value not in cls.LOG_LEVELS:
                return cls.DEFAULT_VALUES[key]
            return value

        def default_user():
            if len(value) > TwitterApi.MAX_USERNAME_LENGTH:
                return None
            return value
        # TODO LOW-PRIORITY: check if db file and log file have a valid name
        switcher = {'LOG_LEVEL': log_level, 'DEFAULT_USER': default_user}
        if key in switcher:
            return switcher[key]()
        return value

    @classmethod
    def check_config(cls, config, config_source):

        # Optional config keys
        for key in cls.OPTIONAL_KEYS:
            if key not in config:
                if key in cls.DEFAULT_VALUES:
                    config[key] = cls.DEFAULT_VALUES[key]
            else:
                config[key] = cls.check_config_parameter(key, config[key])

        cls.set_logging_config(config['LOG_FILE'], config['LOG_LEVEL'])

        # Raise exception if a mandatory config key is missing
        for key in cls.MANDATORY_KEYS:
            if key not in config:
                raise ConfigException("The mandatory config key '{0}' was not found in app config: {1}"
                                      .format(key, config_source))

        # Check if Twitter API keys work
        if ('DEFAULT_ACCESS_TOKEN' in config) and ('DEFAULT_ACCESS_TOKEN_SECRET' in config):
            api = TwitterApi(config['DEFAULT_ACCESS_TOKEN'], config['DEFAULT_ACCESS_TOKEN_SECRET'],
                             config['APP_CONSUMER_KEY'], config['APP_CONSUMER_SECRET'])
            try:
                api.verify_credentials()
            except error.TwitterError as e:
                raise ConfigException(e.message)

        # If debugging, log config
        # log_level = logging.getLogger().level
        # if log_level == logging.DEBUG:
        #     for key in config:
        #         logging.debug("app.config[{0}]={1}".format(key, config[key]))

        return config

    @classmethod
    def get_config_from_env(cls):
        config = dict()

        for key in cls.MANDATORY_KEYS:
            try:
                config[key] = environ[key]
            except KeyError as ke:
                raise ConfigException("Missing mandatory environment variable: {}".format(ke))

        for key in cls.OPTIONAL_KEYS:
            try:
                config[key] = environ[key]
            except KeyError:
                pass

        return config


class ConfigException(Exception):

    def __init__(self, reason):
        self.message = reason
