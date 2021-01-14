
from twittersupervisor.blueprints.auth import oauth_store
from tweepy import OAuthHandler
import pytest

from twittersupervisor.models import AppUser


class TestAuth:
    @pytest.mark.api_call
    def test_request_token(self, client, app):
        response = client.get('/auth/request-token')
        assert len(oauth_store) == 1
        assert response.status_code == 302
        assert "https://api.twitter.com/oauth/authenticate" in response.headers['Location']

    def test_callback(self, client, app, monkeypatch):
        # Monkey patch
        def mock_get_access_token(*args):
            return 'access_token', 'access_token_secret'

        def mock_get_username(*args):
            return 'JanKowalski'

        monkeypatch.setattr(OAuthHandler, 'get_access_token', mock_get_access_token)
        monkeypatch.setattr(OAuthHandler, "get_username", mock_get_username)

        # Nominal case
        with app.app_context():
            oauth_store['garbage'] = 'shit'
            client.get('/auth/callback?oauth_token=garbage&oauth_verifier=moregarbage')
            # Check if the given token and secret are stored in DB
            user = AppUser.query.filter_by(screen_name='JanKowalski').first()
            (access_token, access_token_secret) = user.access_token, user.access_token_secret
            assert access_token == 'access_token'
            assert access_token_secret == 'access_token_secret'

        # Access denied
        oauth_store['token'] = 'secret'
        client.get('/auth/callback?denied=token')
        assert 'token' not in oauth_store



