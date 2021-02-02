from flask import Blueprint, request, render_template, session, url_for, redirect

from twittersupervisor.services.auth_service import AuthService, AuthException

auth = Blueprint('auth', __name__, url_prefix='/auth')

oauth_store = {}


@auth.route('/request-token')
def request_token():
    callback_url = url_for('auth.callback', _external=True)
    try:
        authorize_url, token = AuthService.get_authorize_url(callback_url)
    except AuthException as error:
        return render_template('error.html', error_message=error.reason)
    oauth_token = token['oauth_token']
    oauth_token_secret = token['oauth_token_secret']
    oauth_store[oauth_token] = oauth_token_secret
    return redirect(authorize_url)


@auth.route('/callback')
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
    try:
        user = AuthService.login(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret,
                                 oauth_verifier=oauth_verifier)
    except AuthException as error:
        return render_template('error.html', error_message=error.reason)
    session['username'] = user.screen_name
    return redirect(url_for('pages.settings'))


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('pages.welcome'))
