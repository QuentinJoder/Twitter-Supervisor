# External dependencies
import argparse
import logging
import os.path
# Custom dependencies
from twittersupervisor import Config, Database, Messaging, TwitterApi
import logging_config

# Default values
config_file_name = "config.json"
logging_config.set_logging_config("twitter_supervisor.log")

# Command line parsing & log config
parser = argparse.ArgumentParser(prog="twitter-supervisor")
parser.add_argument("--quiet", help="disable the sending of direct messages", action="store_true")
parser.add_argument("--config", help="specify which configuration file to use. It must be a JSON file.", nargs=1,
                    metavar="CONFIG_FILE")
parser.add_argument("--database", help="specify which SQLite .db file to use", nargs=1, metavar="DB_FILE")
parser.add_argument("--delete_tweets",
                    help="delete old tweets of the account, preserve only the specified number (by default 50)",
                    nargs='?', metavar="NUM_OF_PRESERVED_TWEETS", type=int, const=50)
parser.add_argument("--delete_retweets",
                    help="delete old \"blank\" retweets (does not delete quoted statuses), preserve only the "
                         "specified number (by default 10)",
                    nargs='?', metavar="NUM_OF_PRESERVED_RETWEETS", type=int, const=10)
parser.add_argument("--delete_favorites",
                    help="delete old likes of the account, preserve only the specified number (by default 10)",
                    nargs='?', metavar="NUM_OF_PRESERVED_FAVORITES", type=int, const=10)
parser.add_argument("--version", action="version", version='%(prog)s v0.4.0')
args = parser.parse_args()
logging.debug('Parser arguments: {0}'.format(args))

logging.info('TWITTER SUPERVISOR STARTS!')

# Setup configuration---------------------------------------------------------------------------------------------------
# Config file
if args.config:
    if os.path.isfile(args.config[0]):
        config_file_name = args.config[0]
    else:
        logging.critical("Incorrect argument: \"{}\" is not a file or does not exist.".format(args.config[0]))
        quit(1)
try:
    config = Config(config_file_name)
except KeyError as e:
    logging.critical(e.args[0])
    raise

# Twitter API
twitter_api = TwitterApi(config.twitter_credentials)
if twitter_api.verify_credentials() is None:
    logging.critical("The Twitter API credentials in {} are not valid. Twitter Supervisor can not query the Twitter "
                     "API and work properly without correct credentials.".format(config.config_file_name))
    quit(2)

# Database
if args.database:
    # TODO check if database file name is valid (end with .db, no weird character...)
    database = Database(args.database[0])
else:
    database = Database(config.database_name)

logging.debug("Configuration loaded from: {}".format(config.config_file_name))
logging.debug("Data saved in: {}".format(database.database_name))
logging.debug("Username: {}".format(twitter_api.username))

# Main function---------------------------------------------------------------------------------------------------------

# Retrieve the previous followers set
previous_followers = database.get_previous_followers_set()
previous_followers_number = len(previous_followers)

# Get the current followers set
current_followers = twitter_api.get_followers_set()
followers_number = len(current_followers)
logging.info("Current number of followers: {}".format(followers_number))

# Comparison of the two sets of followers
new_followers = current_followers - previous_followers
traitors = previous_followers - current_followers

# If there are no followers saved in DB, we consider it is the first use
if previous_followers_number == 0:
    print("Thank you for using Twitter Supervisor, we are saving your followers for later use of the program...")
else:
    logging.info("Previous number of followers: {}".format(previous_followers_number))
    messaging = Messaging(twitter_api, args)
    messaging.announce_follow_event(True, new_followers)
    messaging.announce_follow_event(False, traitors)

# Save the followers set in DB if there is change
if len(new_followers) == 0 and len(traitors) == 0:
    logging.info("\"[...] nihil novi sub sole.\" - Ecclesiastes 1:9")
else:
    database.update_followers_table(new_followers, traitors)

# Delete old tweets and favorites---------------------------------------------------------------------------------------

# Delete old tweets
if args.delete_tweets:
    NUMBER_OF_STATUSES_TO_KEEP = args.delete_tweets
    deleted_tweets = twitter_api.delete_old_stuff('tweet', NUMBER_OF_STATUSES_TO_KEEP)
    logging.info('{} tweets have been deleted.'.format(len(deleted_tweets)))

# Delete old retweets
if args.delete_retweets:
    NUMBER_OF_RETWEETS_TO_KEEP = args.delete_retweets
    deleted_tweets = twitter_api.delete_old_stuff('retweet', NUMBER_OF_RETWEETS_TO_KEEP)
    logging.info('{} retweets have been deleted.'.format(len(deleted_tweets)))

# Delete old favorites
if args.delete_favorites:
    NUMBER_OF_FAVORITES_TO_KEEP = args.delete_favorites
    deleted_favorites = twitter_api.delete_old_stuff('favorite', NUMBER_OF_FAVORITES_TO_KEEP)
    logging.info('{} favorites have been deleted.'.format(len(deleted_favorites)))

logging.info("TWITTER SUPERVISOR HAS DONE ITS WORK!")
