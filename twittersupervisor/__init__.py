from flask import Flask
from os import path, environ
from sys import exit
import logging

from .blueprints.auth import auth
from .blueprints.api import api
from .blueprints.pages import pages
from .config import Config, ConfigException

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

    # SQLAlchemy
    from .models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(pages)

    return app
