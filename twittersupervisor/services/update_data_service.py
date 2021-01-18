from twittersupervisor.models import db, TwitterApi, TwitterUser, AppUser


class UpdateDataService:
    @classmethod
    def update_related_users_info(cls, username, users_id):
        # Setup
        users_amount = len(users_id)
        user = AppUser.query.filter_by(screen_name=username).one()
        twitter_api = TwitterApi(access_token=user.access_token, access_token_secret=user.access_token_secret)
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

        # Save it in DB
        for user in twitter_users:
            db_user = TwitterUser(id=user.id, id_str=user.id_str, name=user.name, screen_name=user.screen_name)
            db.session.merge(db_user)
        db.session.commit()
        return len(twitter_users)