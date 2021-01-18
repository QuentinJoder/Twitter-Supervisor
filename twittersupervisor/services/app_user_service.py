from twittersupervisor.models import AppUser


class AppUserService:

    @staticmethod
    def get_app_users():
        return AppUser.query.all()

    # TODO Add method to delete user => revoke access token
