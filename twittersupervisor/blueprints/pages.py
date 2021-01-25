from flask import Blueprint, render_template, session, url_for
from werkzeug.utils import redirect

from twittersupervisor.services import ApiService

pages = Blueprint(name='pages', import_name=__name__, url_prefix='/')


@pages.route('/')
@pages.route('/welcome')
def welcome():
    return render_template('welcome.html')


@pages.route('/events')
@pages.route('/events/<int:page>')
def events(page=1):
    if 'username' in session:
        events_list, pagination = ApiService.get_events(session['username'], page)
        return render_template('events.html', events=events_list, pagination=pagination)
    else:
        return redirect(url_for('pages.welcome'))


@pages.route('/followers')
def followers():
    if 'username' in session:
        return render_template('followers.html')
    else:
        return redirect(url_for('pages.welcome'))


@pages.route('/unfollowers')
def unfollowers():
    if 'username' in session:
        return render_template('followers.html')
    else:
        return redirect(url_for('pages.welcome'))


@pages.route('/settings')
def settings():
    if 'username' in session:
        # TODO get the settings from DB
        return render_template('account_settings.html')
    else:
        return redirect(url_for('pages.welcome'))


@pages.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error_message=error), 404

