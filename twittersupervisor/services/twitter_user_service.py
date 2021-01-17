from .twitter_api_service import TwitterApiService
from twittersupervisor.models import db, TwitterApi, TwitterUser
import logging


logger = logging.getLogger(__name__)


class TwitterUserService:
    @classmethod
    def update_related_users_info(cls, username, users_id):
        # Setup
        users_amount = len(users_id)
        twitter_api = TwitterApiService.get_twitter_api_instance(username)
        start = 0
        end = TwitterApi.USER_IDS_PER_USERS_LOOKUP
        iterations = 0
        twitter_users = []
        # Collect users data
        while iterations < TwitterApi.MAX_USERS_LOOKUP_PER_WINDOW and end < users_amount:
            twitter_users.extend(twitter_api.get_users_lookup(users_id[start:end]))
            start = end
            end += TwitterApi.USER_IDS_PER_USERS_LOOKUP
            iterations += 1
        if iterations != TwitterApi.MAX_USERS_LOOKUP_PER_WINDOW:
            twitter_users.extend(twitter_api.get_users_lookup(users_id[start: users_amount]))
        # Persist in DB
        for user in twitter_users:
            db_user = TwitterUser(id=user.id, name=user.name, screen_name=user.screen_name)
            logger.info(db_user)
            db.session.merge(db_user)
        db.session.commit()
        return len(twitter_users)
