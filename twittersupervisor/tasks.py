from celery.utils.log import get_task_logger
from .services import AppUserService, UpdateDataService, CheckFollowersService, CheckFollowersContext
from . import create_celery_app

MAX_NUMBER_OF_DIRECT_MESSAGES = 15

celery = create_celery_app()
logger = get_task_logger(__name__)


@celery.task()
def check_app_users_followers():
    app_users = AppUserService.get_app_users()
    for user in app_users:
        check_followers.delay(user.screen_name, CheckFollowersContext.PERIODIC_CHECK.value)


@celery.task()
def check_followers(username: str, context: str):
    # TODO Manage quota of DM and other API call
    CheckFollowersService.check_followers(username, context)


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
            updated_users_number = UpdateDataService.update_related_users_info(username=app_user.screen_name,
                                                                               users_id=unknown_users)
            logger.info("{0} users related to {1} had their data updated.".format(updated_users_number,
                                                                                  app_user.screen_name))
    logger.info("Task 'update_users_data' finished.")
