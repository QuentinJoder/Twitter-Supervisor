from sqlalchemy_serializer import SerializerMixin

from . import db, TwitterApi


class TwitterUser(db.Model, SerializerMixin):
    __tablename__ = 'twitter_user'
    serialize_only = ('id', 'screen_name', 'name')
    id = db.Column(db.Integer, primary_key=True)
    screen_name = db.Column(db.String(TwitterApi.MAX_NAME_LENGTH), unique=True)
    name = db.Column(db.String(TwitterApi.MAX_NAME_LENGTH))
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'twitter_user',
        'polymorphic_on': type
    }

    def __repr__(self):
        return "<TwitterUser id: {1}, screen_name: {1}, name: '{2}' >".format(self.id, self.screen_name,
                                                                              self.name)


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True),
                     db.Column('followed_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True)
                     )

unfollowers = db.Table('unfollowers',
                       db.Column('unfollower_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True),
                       db.Column('unfollowed_id', db.Integer, db.ForeignKey('twitter_user.id'), primary_key=True)
                       )


class AppUser(TwitterUser):
    __tablename__ = 'app_user'
    serialize_only = ('access_token', 'access_token_secret')
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
    # TODO Foreign Key for Settings

    __mapper_args__ = {
        'polymorphic_identity': 'app_user'
    }

    def __repr__(self):
        return '<AppUser %r>' % self.screen_name


class FollowEvent(db.Model, SerializerMixin):
    __tablename__ = 'follow_event'
    serialize_only = ('id', 'followed_id', 'follower_id', 'following')
    id = db.Column(db.Integer, primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('twitter_user.id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('twitter_user.id'), nullable=False)
    following = db.Column(db.Boolean, nullable=False)
