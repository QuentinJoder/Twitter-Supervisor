from flask import Flask, render_template, url_for
from tweepy import OAuthHandler, TweepError
import logging
from twittersupervisor import LoggingConfig


app = Flask(__name__)
app.config.from_pyfile('config.cfg', silent=False)
LoggingConfig.set_logging_config("twitter_supervisor.log", "DEBUG")


@app.route('/')
@app.route('/welcome')
def welcome():
    callback_url = url_for('followers', _external=True)
    logging.debug(callback_url)
    auth = OAuthHandler(app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'], callback_url)
    try:
        authorize_url = auth.get_authorization_url(signin_with_twitter=True)
    except TweepError as e:
        return render_template('error.html', error_message=e.reason)
    logging.debug(authorize_url)
    return render_template('welcome.html', authorize_url=authorize_url)


@app.route('/followers')
def followers():
    return render_template('followers.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


if __name__ == 'main':
    app.run()

