from flask import Flask, render_template, url_for, request, redirect, session
from tweepy import OAuthHandler, TweepError
import logging

from .config_file_parser import ConfigFileParser
from .database import Database
from .messaging import Messaging
from .twitter_api import TwitterApi
from .logging_config import LoggingConfig
from .auth import bp


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

    # Blueprints and routes
    app.register_blueprint(auth.bp)

    @app.route('/')
    @app.route('/welcome')
    def welcome():
        return render_template('welcome.html')

    @app.route('/followers')
    def followers():
        if 'username' in session:
            username = session['username']
            db = Database()
            followers_list = db.get_followers()
            logging.debug(followers_list)
            return render_template('followers.html', username=username, followers=followers_list)
        else:
            render_template('error.html', error_message="You need to be logged in to access this page.")

    return app
