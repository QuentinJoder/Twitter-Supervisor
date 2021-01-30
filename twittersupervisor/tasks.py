import logging
from flask_apscheduler import APScheduler

from .services import AppUserService, UpdateDataService, CheckFollowersService, CheckFollowersContext


logger = logging.getLogger()
scheduler = APScheduler()


@scheduler.task('cron', id='CheckFollowers', minute='*/15')
def check_app_users_followers():
    with scheduler.app.app_context():
        app_users = AppUserService.get_app_users()
        for user in app_users:
            CheckFollowersService.check_followers(user.screen_name, CheckFollowersContext.PERIODIC_CHECK.value)


@scheduler.task('cron', id='UpdateUserData', minute='*/15')
def update_users_data():
    with scheduler.app.app_context():
        app_users = AppUserService.get_app_users()
        for app_user in app_users:
            updated_users_number = UpdateDataService.update_related_users_info(username=app_user.screen_name)
            if updated_users_number > 0:
                logger.info("{0} users related to {1} had their data updated.".format(updated_users_number, app_user.screen_name))
        logger.info("{0} 'update_related_users_data' tasks have been launched.".format(len(app_users)))
