from flask import Flask, render_template, session
from os import path
from sys import exit
import logging

from .database import Database
from .messaging import Messaging
from .twitter_api import TwitterApi
from .config import Config, ConfigException
from .auth import bp as auth_bp

CONFIG_FILE = 'config.cfg'


def create_app(test_config=None):

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    config_filepath = path.join(app.instance_path, CONFIG_FILE)
    try:
        if path.isfile(config_filepath):
            app.config.from_pyfile(CONFIG_FILE, silent=True)
            config_source = config_filepath
        else:
            app.config.from_mapping(Config.get_config_from_env(), silent=True)
            config_source = "ENV variables"
        if test_config is not None:
            app.config.from_mapping(test_config)
            config_source += str("+ test_config")
        app.config = Config.check_config(app.config, config_source)
    except ConfigException as ce:
        logging.critical(ce.message)
        exit(1)

    # Blueprints and routes
    app.register_blueprint(auth_bp)

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
