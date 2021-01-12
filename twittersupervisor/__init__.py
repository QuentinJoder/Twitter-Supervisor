from flask import Flask, render_template, session, url_for
from os import path, environ
from sys import exit
import logging
from werkzeug.utils import redirect

# from .celery import make_celery
from .database import Database
from .messaging import Messaging
from .twitter_api import TwitterApi
from .config import Config, ConfigException
from .blueprints.auth import auth_bp
from .blueprints.api import api_bp

CONFIG_FILE = 'config.cfg'


def create_app(test_config=None):

    # Create the app
    app = Flask(__name__, instance_relative_config=True)
    app.instance_path = environ.get('FLASK_INSTANCE_PATH', default=app.instance_path)

    # Load from env. variables
    app.config.from_mapping(Config.get_config_from_env(), silent=True)
    config_source = "ENV variables"

    # Load from config file
    config_filepath = path.join(app.instance_path, CONFIG_FILE)
    if path.isfile(config_filepath):
        app.config.from_pyfile(CONFIG_FILE, silent=True)
        config_source += "+" + config_filepath

    # Load from test_config
    if test_config is not None:
        app.config.from_mapping(test_config)
        config_source += str("+ test_config")

    # Check if config works
    try:
        app.config = Config.check_config(app.config, config_source)
    except ConfigException as ce:
        logging.critical(ce.message)
        exit(1)

    # Celery
    # celery = make_celery(app)

    # Blueprints and routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.route('/')
    @app.route('/welcome')
    def welcome():
        return render_template('welcome.html')

    @app.route('/followers')
    def followers():
        if 'username' in session:
            return render_template('followers.html')
        else:
            redirect(url_for('welcome'))

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html', error_message=error), 404

    return app
