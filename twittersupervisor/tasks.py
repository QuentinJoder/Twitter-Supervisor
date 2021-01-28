from celery import shared_task
from celery.utils.log import get_task_logger
from .services import AppUserService, UpdateDataService, CheckFollowersService, CheckFollowersContext


logger = get_task_logger(__name__)


@shared_task()
def check_app_users_followers():
    app_users = AppUserService.get_app_users()
    for user in app_users:
        check_followers.delay(user.screen_name, CheckFollowersContext.PERIODIC_CHECK.value)


@shared_task()
def check_followers(username: str, context: str):
    CheckFollowersService.check_followers(username, context)


@shared_task()
def update_users_data():
    app_users = AppUserService.get_app_users()
    for app_user in app_users:
        update_related_users_data.delay(app_user.screen_name)
    logger.info("{0} 'update_related_users_data' tasks have been launched.".format(len(app_users)))


@shared_task()
def update_related_users_data(username: str):
    updated_users_number = UpdateDataService.update_related_users_info(username=username)
    if updated_users_number > 0:
        logger.info("{0} users related to {1} had their data updated.".format(updated_users_number, username))
