from celery.signals import after_setup_task_logger, setup_logging
from celery.utils.log import get_task_logger
import logging
from .celery import app, DATABASE, TWITTER_API
from .messaging import Messaging

LOGGER = get_task_logger(__name__)


# @after_setup_task_logger.connect
# def after_setup_task_logger_handler(logger, loglevel, logfile, format, **kwargs):
#     handler = logging.FileHandler('twitter_supervisor.log')
#     handler.setLevel(logging.DEBUG)
#     formatter = logging.Formatter(format)
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#     logger.propagate = False

@setup_logging.connect
def on_setup_logging(**kwargs):
    pass


@app.task
def check_followers(quiet):

    # Retrieve the previous followers set
    previous_followers = DATABASE.get_previous_followers_set()
    previous_followers_number = len(previous_followers)

    # Get the current followers set
    current_followers = TWITTER_API.get_followers_set()
    followers_number = len(current_followers)
    LOGGER.info("Current number of followers: {}".format(followers_number))

    # Comparison of the two sets of followers
    new_followers = current_followers - previous_followers
    traitors = previous_followers - current_followers

    # If there are no followers saved in DB, we consider it is the first use
    if previous_followers_number == 0:
        print("Thank you for using Twitter Supervisor, we are saving your followers for later use of the program...")
    else:
        LOGGER.info("Previous number of followers: {}".format(previous_followers_number))
        messaging = Messaging(TWITTER_API, quiet)
        messaging.announce_follow_event(True, new_followers)
        messaging.announce_follow_event(False, traitors)

    # Save the followers set in DB if there is change
    if len(new_followers) == 0 and len(traitors) == 0:
        LOGGER.info("\"[...] nihil novi sub sole.\" - Ecclesiastes 1:9")
    else:
        DATABASE.update_followers_table(new_followers, traitors)


@app.task
def delete_tweets(number_of_statuses_to_keep):
    deleted_tweets = TWITTER_API.delete_old_stuff('tweet', number_of_statuses_to_keep)
    LOGGER.info('{} tweets have been deleted.'.format(len(deleted_tweets)))


@app.task
def delete_retweets(number_of_retweets_to_keep):
    deleted_tweets = TWITTER_API.delete_old_stuff('retweet', number_of_retweets_to_keep)
    LOGGER.info('{} retweets have been deleted.'.format(len(deleted_tweets)))


@app.task
def delete_favorites(number_of_favs_to_keep):
    deleted_favorites = TWITTER_API.delete_old_stuff('favorite', number_of_favs_to_keep)
    LOGGER.info('{} favorites have been deleted.'.format(len(deleted_favorites)))
