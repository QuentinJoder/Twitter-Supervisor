import json
import logging


class Config:

    # Default values
    DEFAULT_DB_FILE = "followers.db"

    def __init__(self, config_file_name):
        self.config_file_name = config_file_name
        config = json.load(open(config_file_name, 'r'))

        if "twitter_api" in config:
            if "username" not in config["twitter_api"]:
                raise KeyError("No \"twitter_api\" \"username\" found in {}".format(config_file_name))
            elif "consumer_key" not in config["twitter_api"]:
                raise KeyError("No \"twitter_api\" \"consumer_key\" key found in {}".format(config_file_name))
            elif "consumer_secret" not in config["twitter_api"]:
                raise KeyError("No \"twitter_api\" \"consumer_secret\" key found in {}".format(config_file_name))
            elif "access_token" not in config["twitter_api"]:
                raise KeyError("No \"twitter_api\" \"access_token\" key found in {}".format(config_file_name))
            elif "access_token_secret" not in config["twitter_api"]:
                raise KeyError("No \"twitter_api\" \"access_token_secret\" key found in {}".format(config_file_name))
            else:
                self.twitter_credentials = config["twitter_api"]
        else:
            raise KeyError("No \"twitter_api\" key found in {}".format(config_file_name))

        if "database_file" in config:
            self.database_name = config["database_file"]
        else:
            logging.info("No database filename is specified in {}. Default value \"{}\" will be used."
                         .format(config_file_name, self.DEFAULT_DB_FILE))
            self.database_name = self.DEFAULT_DB_FILE
