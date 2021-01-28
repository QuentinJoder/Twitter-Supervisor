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
        users_number = len(unknown_users)
        if users_number == 0:
            return 0  # TODO Refresh users data regularly even if none is unknown
        users_id = unknown_users

        # Setup
        twitter_api = TwitterApi(access_token=app_user.access_token, access_token_secret=app_user.access_token_secret)
        start = 0
        end = TwitterApi.USER_IDS_PER_USERS_LOOKUP
        iterations = 0
        twitter_users = []

        # Collect users data
        # TODO Catch and handle TwitterApi errors
        while iterations < TwitterApi.MAX_USERS_LOOKUP_PER_WINDOW and end < users_number:
            twitter_users.extend(twitter_api.get_users_lookup(users_id[start:end]))
            start = end
            end += TwitterApi.USER_IDS_PER_USERS_LOOKUP
            iterations += 1
        if iterations != TwitterApi.MAX_USERS_LOOKUP_PER_WINDOW:
            twitter_users.extend(twitter_api.get_users_lookup(users_id[start: users_number]))

        # Save it in DB
        for user in twitter_users:
            db_user = TwitterUser(id=user.id, id_str=user.id_str, name=user.name, screen_name=user.screen_name)
            db.session.merge(db_user)
        db.session.commit()
        return len(twitter_users)
