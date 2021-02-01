from twittersupervisor.models import db, TwitterApi, TwitterUser, AppUser


class UpdateDataService:
    @classmethod
    def update_related_users_info(cls, username) -> int:
        # Get unknown users
        app_user = AppUser.query.filter_by(screen_name=username).one()
        related_users = app_user.followers.all() + app_user.unfollowers.all()
        unknown_users = []
        for user in related_users:
            if user.screen_name is None:
                unknown_users.append(user.id)

        # Decide what to do
        if len(unknown_users) == 0:
            return 0  # TODO Refresh users data regularly even if none is unknown
        users_id = unknown_users

        # Get users data
        twitter_api = TwitterApi(access_token=app_user.access_token, access_token_secret=app_user.access_token_secret)
        twitter_users = twitter_api.get_users_lookup(users_id)

        # Save it in DB
        for user in twitter_users:
            db_user = TwitterUser(id=user.id, id_str=user.id_str, name=user.name, screen_name=user.screen_name)
            db.session.merge(db_user)
        db.session.commit()
        return len(twitter_users)
