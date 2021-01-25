from dataclasses import dataclass
from datetime import datetime

from flask import url_for

from twittersupervisor.models import AppUser, FollowEvent, TwitterUser, db


class ApiService:

    ITEMS_PER_PAGE = 50

    @classmethod
    def get_events(cls, username: str, page: int):
        user = AppUser.query.filter_by(screen_name=username).one()
        pagination = FollowEvent.query.filter_by(followed_id=user.id).order_by(db.desc(FollowEvent.event_date))\
            .paginate(page=page, per_page=cls.ITEMS_PER_PAGE)
        events = []
        for follow_event in pagination.items:
            follower = TwitterUser.query.filter_by(id=follow_event.follower_id).first()
            if follower is not None:
                events.append(EventDto(id=follow_event.id, user_screen_name=follower.screen_name,
                                       user_name=follower.name, following=follow_event.following,
                                       event_date=follow_event.event_date))
        return events, pagination

    @staticmethod
    def get_followers(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        return user.followers

    @staticmethod
    def get_unfollowers(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        return user.unfollowers

    @staticmethod
    def get_follow_events_by_follower(username: str, follower_id: int):
        user = AppUser.query.filter_by(screen_name=username).one()
        events_list = FollowEvent.query.filter_by(followed_id=user.id, follower_id=follower_id).all()
        return events_list


@dataclass
class EventDto:
    id: int
    user_screen_name: str
    user_name: str
    following: bool
    event_date: datetime
