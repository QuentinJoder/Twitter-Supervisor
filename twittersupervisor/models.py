from flask_sqlalchemy import SQLAlchemy
from .twitter_api import TwitterApi
import datetime
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class TwitterUser(db.Model):
    id: int
    id_str: str
    screen_name: str
    name: str

    __tablename__ = 'twitter_user'
    id = db.Column(db.Integer, primary_key=True)
    id_str = db.Column(db.String(TwitterApi.MAX_ID_STRING_LENGTH))
    screen_name = db.Column(db.String(TwitterApi.MAX_NAME_LENGTH), unique=True)
    name = db.Column(db.String(TwitterApi.MAX_NAME_LENGTH))
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'twitter_user',
        'polymorphic_on': type
    }


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True),
                     db.Column('followed_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True)
                     )

unfollowers = db.Table('unfollowers',
                       db.Column('unfollower_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True),
                       db.Column('unfollowed_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True)
                       )


@dataclass
class AppUser(TwitterUser):
    access_token: str
    access_token_secret: str
    followers: list[TwitterUser]
    unfollowers: list[TwitterUser]

    __tablename__ = 'app_user'
    access_token = db.Column(db.String)
    access_token_secret = db.Column(db.String)
    followers = db.relationship('TwitterUser', secondary=followers,
                                primaryjoin="TwitterUser.id == followers.c.followed_id",
                                secondaryjoin="TwitterUser.id == followers.c.follower_id",
                                backref='following')
    unfollowers = db.relationship('TwitterUser', secondary=unfollowers,
                                  primaryjoin="TwitterUser.id == unfollowers.c.unfollowed_id",
                                  secondaryjoin="TwitterUser.id == unfollowers.c.unfollower_id",
                                  backref='unfollowing')
    # TODO Create a Model for Settings

    __mapper_args__ = {
        'polymorphic_identity': 'app_user'
    }


@dataclass
class FollowEvent(db.Model):
    id: int
    followed_id: int
    follower_id: int
    following: bool
    event_date: datetime.datetime

    __tablename__ = 'follow_event'
    id = db.Column(db.Integer, primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('twitter_user.id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('twitter_user.id'), nullable=False)
    following = db.Column(db.Boolean, nullable=False)
    event_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

