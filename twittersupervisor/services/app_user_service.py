import logging
from dataclasses import asdict

from twittersupervisor.models import db, AppUser, TwitterUser
from .twitter_api_service import TwitterApiService


class AppUserService:

    @staticmethod
    def create_app_user(access_token: str, access_token_secret: str):
        twitter_api = TwitterApiService.get_twitter_api_instance_from_token(access_token, access_token_secret)
        twitter_user = twitter_api.verify_credentials()
        user = AppUser(id=twitter_user.id, screen_name=twitter_user.screen_name, name=twitter_user.name,
                       access_token=access_token, access_token_secret=access_token_secret)
        db.session.merge(user)
        db.session.commit()
        return user

    @staticmethod
    def get_app_users():
        return AppUser.query.all()

    @staticmethod
    def get_followers(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        followers = user.followers
        logging.info("Follower: {}".format(followers[0].id))
        serialized_followers = []
        for follower in followers:
            serialized_followers.append(follower.to_dict())
        logging.info("Serialized: {}".format(serialized_followers[0]))
        return serialized_followers

    @classmethod
    def update_followers_and_unfollowers(cls, user: AppUser):
        # Comparison
        previous_followers = cls._get_followers_set(user)
        twitter_api = TwitterApiService.get_twitter_api_instance(user.screen_name)
        current_followers = twitter_api.get_followers_set()
        new_followers_set = current_followers - previous_followers
        new_unfollowers_set = previous_followers - current_followers

        # Save new followers in DB
        for follower_id in new_followers_set:
            follower = TwitterUser.query.filter_by(id=follower_id).first()
            if follower is None:
                follower = TwitterUser(id=follower_id)
            else:
                try:
                    user.unfollowers.remove(follower)
                except ValueError:
                    pass
            user.followers.append(follower)

        # Save new unfollowers in DB
        for unfollower in new_unfollowers_set:
            traitor = TwitterUser.query.filter_by(id=unfollower).one()
            user.followers.remove(traitor)
            user.unfollowers.append(traitor)

        # Commit and return
        db.session.commit()
        return new_followers_set, new_unfollowers_set

    @classmethod
    def _get_followers_set(cls, user):
        result = set()
        for follower in user.followers:
            result.add(follower.id)
        return result