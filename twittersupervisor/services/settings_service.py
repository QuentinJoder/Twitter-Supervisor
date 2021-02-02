from twittersupervisor.models import AppUser, Settings, DirectMessageOption, db


class SettingsService:

    @staticmethod
    def get_all_settings():
        return Settings.query.all()

    @staticmethod
    def get_user_settings(username: str):
        user = AppUser.query.filter_by(screen_name=username).one()
        settings = Settings.query.filter_by(user_id=user.id).first()
        if settings is None:
            settings = Settings(user_id=user.id, dm_option=DirectMessageOption.FOLLOW_AND_UNFOLLOW)
            db.session.add(settings)
            db.session.commit()
        return settings

    @classmethod
    def update_settings(cls, username: str, dm_option_value: int):
        user = AppUser.query.filter_by(screen_name=username).one()
        settings = Settings.query.filter_by(user_id=user.id).first()
        dm_option = DirectMessageOption(int(dm_option_value))
        settings.dm_option = dm_option
        db.session.merge(settings)
        db.session.commit()
        return settings

    # TODO Add method to delete user => revoke access token
