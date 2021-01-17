from twittersupervisor.models import db, FollowEvent, AppUser
import datetime


class FollowEventService:

    @staticmethod
    def get_follow_events(username: str, follower_id: int):
        user = AppUser.query.filter_by(screen_name=username).one()
        events_list = FollowEvent.query.filter_by(followed_id=user.id, follower_id=follower_id).all()
        return events_list

    @classmethod
    def create_follow_events(cls, target_id: int, new_followers_set: set, unfollowers_set: set):
        for follower_id in new_followers_set:
            event = FollowEvent(followed_id=target_id, follower_id=follower_id, following=True,
                                event_date=datetime.datetime.utcnow())
            db.session.add(event)
        for follower_id in unfollowers_set:
            event = FollowEvent(followed_id=target_id, follower_id=follower_id, following=False,
                                event_date=datetime.datetime.utcnow())
            db.session.add(event)
        db.session.commit()
