# External dependencies
import argparse
import logging
# Custom dependencies
from twittersupervisor.tasks import check_followers, delete_tweets, delete_retweets, delete_favorites

# Default values
config_file_name = "config.json"

# Command line parsing & log config
parser = argparse.ArgumentParser(prog="twitter-supervisor")
parser.add_argument("--quiet", help="disable the sending of direct messages", action="store_true")
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

# Main function---------------------------------------------------------------------------------------------------------
quiet = args.quiet
check_followers.delay(quiet)

# Delete old tweets and favorites---------------------------------------------------------------------------------------

# Delete old tweets
if args.delete_tweets:
    NUMBER_OF_STATUSES_TO_KEEP = args.delete_tweets
    delete_tweets.delay(NUMBER_OF_STATUSES_TO_KEEP)

# Delete old retweets
if args.delete_retweets:
    NUMBER_OF_RETWEETS_TO_KEEP = args.delete_retweets
    delete_retweets.delay(NUMBER_OF_RETWEETS_TO_KEEP)

# Delete old favorites
if args.delete_favorites:
    NUMBER_OF_FAVORITES_TO_KEEP = args.delete_favorites
    delete_favorites.delay(NUMBER_OF_FAVORITES_TO_KEEP)

logging.info("TWITTER SUPERVISOR HAS DONE ITS WORK!")
