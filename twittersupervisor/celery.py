from celery import Celery
import logging
from twittersupervisor import Config, Database, TwitterApi

# Logging
# logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='twitter_supervisor.log')
# logging to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Config
try:
    CONFIG = Config('./config.json')
except KeyError as e:
    logging.critical(e.args[0])
    raise

# Twitter API
TWITTER_API = TwitterApi(CONFIG.twitter_credentials)
if TWITTER_API.verify_credentials() is None:
    logging.critical("The Twitter API credentials in {} are not valid. Twitter Supervisor can not query the Twitter "
                     "API and work properly without correct credentials.".format(CONFIG.config_file_name))
    quit(2)

# Database
# TODO check if database file name is valid (end with .db, no weird character...)
DATABASE = Database(CONFIG.database_name)

logging.debug("Configuration loaded from: {}".format(CONFIG.config_file_name))
logging.debug("Data saved in: {}".format(DATABASE.database_name))
logging.debug("Username: {}".format(TWITTER_API.username))

app = Celery('twittersupervisor', broker='redis://localhost:6379/0', include=['twittersupervisor.tasks'])

logging.info('Celery launched !')

if __name__ == '__main__':
    app.start()
