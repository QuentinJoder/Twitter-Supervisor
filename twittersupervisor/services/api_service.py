from twittersupervisor.models import AppUser, FollowEvent


class ApiService:

    @staticmethod
    def get_followers(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        return user.followers

    @staticmethod
    def get_unfollowers(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        return user.unfollowers

    @staticmethod
    def get_follow_events(username: str, follower_id: int):
        user = AppUser.query.filter_by(screen_name=username).one()
        events_list = FollowEvent.query.filter_by(followed_id=user.id, follower_id=follower_id).all()
        return events_list
