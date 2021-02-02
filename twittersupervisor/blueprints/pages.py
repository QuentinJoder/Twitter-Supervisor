from flask import Blueprint, render_template, session, url_for, request
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from twittersupervisor.models import DirectMessageOption
from twittersupervisor.services.api_service import ApiService
from twittersupervisor.services.settings_service import SettingsService

pages = Blueprint(name='pages', import_name=__name__, url_prefix='/')


@pages.route('/')
@pages.route('/welcome')
def welcome():
    return render_template('welcome.html')


@pages.route('/events')
def events():
    if 'username' in session:
        page = __get_page()
        events_list, pagination = ApiService.get_events(session['username'], page)
        return render_template('events.html', events=events_list, pagination=pagination)
    else:
        return redirect(url_for('pages.welcome'))


@pages.route('/followers')
def followers():
    if 'username' in session:
        page = __get_page()
        followers_list = ApiService.get_followers(session['username'], page)
        return render_template('followers.html', pagination=followers_list, followers=True)
    else:
        return redirect(url_for('pages.welcome'))


@pages.route('/unfollowers')
def unfollowers():
    if 'username' in session:
        page = __get_page()
        pagination = ApiService.get_unfollowers(session['username'], page)
        return render_template('followers.html', pagination=pagination, followers=False)
    else:
        return redirect(url_for('pages.welcome'))


@pages.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' in session:
        if request.method == 'POST':
            dm_option = request.form['dm-option']
            user_settings = SettingsService.update_settings(session['username'], dm_option)
        else:
            user_settings = SettingsService.get_user_settings(session['username'])

        dm_options = {DirectMessageOption.FOLLOW_AND_UNFOLLOW: "Follow or Unfollow me",
                      DirectMessageOption.FOLLOW: "Follow me",
                      DirectMessageOption.UNFOLLOW: "Unfollow me",
                      DirectMessageOption.NO_MESSAGES: "Don't send any message"}
        return render_template('account_settings.html', settings=user_settings, dm_options=dm_options)
    else:
        return redirect(url_for('pages.welcome'))


def __get_page():
    try:
        return int(request.args.get('page', 1))
    except ValueError:
        abort(400)


@pages.errorhandler(400)
def bad_request(error):
    return render_template('error.html', error_message=error), 400


@pages.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error_message=error), 404

