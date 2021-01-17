from celery.utils.log import get_task_logger
from .models import AppUser
from .services import AppUserService, DirectMessageService, TwitterUserService, FollowEventService
from . import create_celery_app

MAX_NUMBER_OF_DIRECT_MESSAGES = 15

celery = create_celery_app()
logger = get_task_logger(__name__)


@celery.task()
def check_app_users_followers():
    app_users = AppUserService.get_app_users()
    for user in app_users:
        check_followers(user)


@celery.task()
def check_followers(user: AppUser):
    logger.info("Check the followers of: @{0} (n°{1})".format(user.screen_name, user.id))
    (new_followers_set, unfollowers_set) = AppUserService.update_followers_and_unfollowers(user)
    # FollowEvents are created after the TwitterUsers because of foreign keys constraints
    FollowEventService.create_follow_events(user.id, new_followers_set, unfollowers_set)
    # TODO Implement a quota limitation (15 000 DM per day for the app, 1000 per day per user)
    if len(new_followers_set) > MAX_NUMBER_OF_DIRECT_MESSAGES:
        DirectMessageService.send_direct_message(user.screen_name,
                                                 "Congratulations, more than {} accounts started to "
                                                 "follow you recently".format(MAX_NUMBER_OF_DIRECT_MESSAGES))
    elif len(new_followers_set) > 0:
        DirectMessageService.present_new_followers(user.screen_name, new_followers_set)

    if len(unfollowers_set) > MAX_NUMBER_OF_DIRECT_MESSAGES:
        DirectMessageService.send_direct_message(user.screen_name, "Oh barnacles ! More than {} accounts ceased to "
                                                                   "follow you recently".format(MAX_NUMBER_OF_DIRECT_MESSAGES))
    elif len(unfollowers_set) > 0:
        DirectMessageService.denounce_traitors(user.screen_name, unfollowers_set)


@celery.task()
def update_users_data():
    logger.info("Task 'update_users_data' called !")
    app_users = AppUserService.get_app_users()
    for app_user in app_users:
        related_users = app_user.followers + app_user.unfollowers
        unknown_users = []
        for user in related_users:
            if user.screen_name is None:
                unknown_users.append(user.id)
        if len(unknown_users) > 0:
            updated_users_number = TwitterUserService.update_related_users_info(username=app_user.screen_name,
                                                                                users_id=unknown_users)
            logger.info("{0} users related to {1} had their data updated.".format(updated_users_number,
                                                                                  app_user.screen_name))
    logger.info("Task 'update_users_data' finished.")
