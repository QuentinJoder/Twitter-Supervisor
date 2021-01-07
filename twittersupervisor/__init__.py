from flask import Flask, render_template, url_for, request, redirect, session
from tweepy import OAuthHandler, TweepError
import logging

from .config_file_parser import ConfigFileParser
from .database import Database
from .messaging import Messaging
from .twitter_api import TwitterApi
from .logging_config import LoggingConfig


def create_app():
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.cfg', silent=True)

    # Logging
    try:
        log_level = app.config['LOG_LEVEL']
    except KeyError:
        log_level = 'INFO'
    LoggingConfig.set_logging_config('twitter_supervisor.log', log_level)

    oauth_store = {}
    # TODO Use SQLAlchemy (or any proper ORM)
    db = Database(app.config['DATABASE_FILE'])

    # TODO Put put '/callback' and '/request_token' in an 'auth' blueprint
    @app.route('/')
    @app.route('/welcome')
    def welcome():
        callback_url = url_for('callback', _external=True)
        logging.debug("Callback URL: {}".format(callback_url))
        auth = OAuthHandler(app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'], callback_url)
        try:
            authorize_url = auth.get_authorization_url(signin_with_twitter=True)
        except TweepError as e:
            return render_template('error.html', error_message=e.reason)
        logging.debug(authorize_url)
        oauth_token = auth.request_token['oauth_token']
        oauth_token_secret = auth.request_token['oauth_token_secret']
        oauth_store[oauth_token] = oauth_token_secret
        return render_template('welcome.html', authorize_url=authorize_url)

    @app.route('/callback')
    def callback():
        oauth_token = request.args.get('oauth_token')
        oauth_verifier = request.args.get('oauth_verifier')
        oauth_denied = request.args.get('denied')

        # if the OAuth request was denied, delete our local token
        # and show an error message
        if oauth_denied:
            if oauth_denied in oauth_store:
                del oauth_store[oauth_denied]
            return render_template('error.html', error_message="Could not login, your OAuth request was denied")

        if not oauth_token or not oauth_verifier:
            return render_template('error.html', error_message="Callback param(s) missing")

        # unless oauth_token is still stored locally, return error
        if oauth_token not in oauth_store:
            return render_template('error.html', error_message="OAuth Token not found locally")

        oauth_token_secret = oauth_store[oauth_token]
        auth = OAuthHandler(app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'])
        auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_token_secret}
        try:
            (access_token, access_token_secret) = auth.get_access_token(oauth_verifier)
        except TweepError as error:
            return render_template('error.html', error_message=error.reason)
        auth.set_access_token(access_token, access_token_secret)
        username = auth.get_username()
        logging.debug("Username: {}".format(username))
        db.create_user(username, access_token, access_token_secret)
        session['username'] = username
        return redirect(url_for('followers'))

    @app.route('/followers')
    def followers():
        if 'username' in session:
            username = session['username']
            followers_list = db.get_followers()
            logging.debug(followers_list)
            return render_template('followers.html', username=username, followers=followers_list)
        else:
            render_template('error.html', error_message="You need to be logged in to access this page.")

    return app
