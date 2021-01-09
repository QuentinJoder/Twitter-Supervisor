from flask import current_app, Blueprint, request, render_template, session, url_for, redirect
from tweepy import TweepError, OAuthHandler
import logging

from .database import Database

bp = Blueprint('auth', __name__, url_prefix='/auth')

oauth_store = {}


@bp.route('/request-token')
def request_token():
    callback_url = url_for('auth.callback', _external=True)
    logging.debug("Callback URL: {}".format(callback_url))
    auth = OAuthHandler(current_app.config['APP_CONSUMER_KEY'], current_app.config['APP_CONSUMER_SECRET'], callback_url)
    try:
        authorize_url = auth.get_authorization_url(signin_with_twitter=True)
    except TweepError as e:
        return render_template('error.html', error_message=e.reason)
    logging.debug(authorize_url)
    oauth_token = auth.request_token['oauth_token']
    oauth_token_secret = auth.request_token['oauth_token_secret']
    oauth_store[oauth_token] = oauth_token_secret
    return redirect(authorize_url)


@bp.route('/callback')
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
    auth = OAuthHandler(current_app.config['APP_CONSUMER_KEY'], current_app.config['APP_CONSUMER_SECRET'])
    auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_token_secret}
    try:
        (access_token, access_token_secret) = auth.get_access_token(oauth_verifier)
    except TweepError as error:
        logging.error("Unable to set access token & secret: {0}".format(error))
        return render_template('error.html', error_message=error.reason)
    auth.set_access_token(access_token, access_token_secret)
    username = auth.get_username()
    logging.debug("Username: {}".format(username))
    db = Database()
    db.create_user(username, access_token, access_token_secret)
    session['username'] = username
    return redirect(url_for('followers'))


