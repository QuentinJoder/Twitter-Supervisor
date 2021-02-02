import logging
from flask_apscheduler import APScheduler

from .services.settings_service import SettingsService
from .services.update_data_service import UpdateDataService
from .services.check_followers_service import CheckFollowersService, CheckFollowersContext


logger = logging.getLogger()
scheduler = APScheduler()


@scheduler.task('cron', id='CheckFollowers', minute='*/1')  # TODO Manage accounts with more than 5000 followers
def check_app_users_followers():
    with scheduler.app.app_context():
        settings_list = SettingsService.get_all_settings()
        for settings in settings_list:
            CheckFollowersService.check_followers(settings, CheckFollowersContext.PERIODIC_CHECK)


@scheduler.task('cron', id='UpdateUserData', minute='*/15')
def update_users_data():
    with scheduler.app.app_context():
        settings_list = SettingsService.get_all_settings()
        for settings in settings_list:
            updated_users_number = UpdateDataService.update_related_users_info(settings.user)
            if updated_users_number > 0:
                logger.info("{0} users related to {1} had their data updated.".format(updated_users_number,
                                                                                      settings.user.screen_name))
        logger.info("{0} 'update_related_users_data' tasks have been launched.".format(len(settings_list)))
