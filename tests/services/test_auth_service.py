from unittest.mock import patch

from pytest import raises
from tweepy import OAuthHandler, TweepError, User

from twittersupervisor.models import AppUser, db
from twittersupervisor.services.auth_service import AuthService, AuthException
from twittersupervisor.services.check_followers_service import CheckFollowersService
from twittersupervisor.twitter_api import TwitterApi


class TestAuthService:

    def test_get_authorize_url(self, app):
        # Check if an AuthException is raised in case of TweepError
        with app.app_context():
            with patch.object(OAuthHandler, 'get_authorization_url', side_effect=TweepError(reason="A reason")):
                with raises(AuthException) as exc_info:
                    AuthService.get_authorize_url('https://www.twittersupervisor.com/auth/callback')
                    assert exc_info.value.reason == "A reason"

    def test_login(self, app, monkeypatch):
        # Monkey patch
        def mock_verify_credentials(*args):
            return User.parse(None, json={'id': 1, 'id_str': "1", 'screen_name': "test", 'name': "Test"})

        def mock_get_access_token(*args):
            return 'access_token', 'access_token_secret'

        monkeypatch.setattr(OAuthHandler, 'get_access_token', mock_get_access_token)
        monkeypatch.setattr(TwitterApi, "verify_credentials", mock_verify_credentials)

        with app.app_context():
            with patch.object(AuthService, '_AuthService__merge_app_user', side_effect=AuthService._AuthService__merge_app_user) as merge_user_mock:
                with patch.object(CheckFollowersService, 'check_followers') as check_followers_mock:
                    # Case 1: User does not exist
                    AuthService.login("token", "token_secret", "verifier")
                    merge_user_mock.assert_called_once()
                    check_followers_mock.assert_called_once()
                    # Case 2: User does exist
                    check_followers_mock.reset_mock()
                    merge_user_mock.reset_mock()
                    AuthService.login("token", "token_secret", "verifier")
                    merge_user_mock.assert_not_called()
                    check_followers_mock.assert_not_called()
                    # Case 3: User has changed
                    user = AppUser.query.filter_by(id=1).one()
                    user.name = "Jean-louis"
                    db.session.merge(user)
                    db.session.commit()
                    AuthService.login("token", "token_secret", "verifier")
                    merge_user_mock.assert_called_once()
                    check_followers_mock.assert_not_called()
                    db.session.delete(user)
                    db.session.commit()

    def test_merge_app_user(self, app):
        with app.app_context():
            test_user = AppUser(id=2, id_str='2', screen_name='test2', name='Test 2', access_token='at',
                                access_token_secret='ats')
            twitter_user = User.parse(None, json={'id': 2, 'id_str': "2", 'screen_name': "test2", 'name': "Test 2"})
            user = AuthService._AuthService__merge_app_user(twitter_user, "at", "ats")
            assert test_user.id == user.id
            assert test_user.screen_name == user.screen_name
            assert test_user.name == user.name
            assert test_user.id_str == user.id_str
            assert test_user.access_token == user.access_token
            assert test_user.access_token_secret == user.access_token_secret
            auser = AppUser.query.filter_by(id=user.id).one()
            db.session.delete(auser)
            db.session.commit()

