from flask import Blueprint, render_template, session, url_for, request
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from twittersupervisor.services.api_service import ApiService

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


@pages.route('/settings')
def settings():
    if 'username' in session:
        # TODO get the settings from DB
        return render_template('account_settings.html')
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

