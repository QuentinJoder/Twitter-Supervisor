from twittersupervisor import Database
from twittersupervisor.auth import oauth_store
from tweepy import OAuthHandler


class TestAuth:
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
            db = Database()
            client.get('/auth/callback?oauth_token=garbage&oauth_verifier=moregarbage')
            # Check if the given token and secret are stored in DB
            (access_token, access_token_secret) = db.get_user_token_and_secret('JanKowalski')
            assert access_token == 'access_token'
            assert access_token_secret == 'access_token_secret'

        # Access denied
        oauth_store['token'] = 'secret'
        client.get('/auth/callback?denied=token')
        assert 'token' not in oauth_store



