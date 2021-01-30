from flask import session
import pytest

from twittersupervisor.models import AppUser
from twittersupervisor.blueprints.auth import oauth_store
from twittersupervisor.services.auth_service import AuthService


class TestAuth:
    @pytest.mark.api_call
    def test_request_token(self, client):
        response = client.get('/auth/request-token')
        assert len(oauth_store) == 1
        assert response.status_code == 302
        assert "https://api.twitter.com/oauth/authenticate" in response.headers['Location']

    def test_callback(self, client, monkeypatch):
        # Monkey patch
        def mock_login(*args, **kwargs):
            return AppUser(id=666, id_str='666', screen_name='JanKowalski', name='Jan Kowalski', access_token='at',
                           access_token_secret='ats')

        monkeypatch.setattr(AuthService, 'login', mock_login)

        # Access denied
        oauth_store['token'] = 'secret'
        client.get('/auth/callback?denied=token')
        assert 'token' not in oauth_store

        # Everything works
        oauth_store['garbage'] = 'shit'
        with client:
            client.get('/auth/callback?oauth_token=garbage&oauth_verifier=moregarbage')
            assert session['username'] == 'JanKowalski'

        # AuthException
        # TODO Test if the error template is rendered
