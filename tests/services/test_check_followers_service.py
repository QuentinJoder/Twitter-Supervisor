from twittersupervisor.models import TwitterUser, db
from twittersupervisor.services.check_followers_service import CheckFollowersService


class TestCheckFollowersService:

    def test_get_username(self, app):
        with app.app_context():
            # Missing screen_name case
            username = CheckFollowersService._CheckFollowersService__get_username(1)
            assert "n°" in username
            # screen_name in DB case
            user = TwitterUser(id=1, id_str='1', screen_name='test', name="Test")
            db.session.add(user)
            db.session.commit()
            username = CheckFollowersService._CheckFollowersService__get_username(1)
            assert username == "@test"
            # Cleanup
            db.session.delete(user)
            db.session.commit()
