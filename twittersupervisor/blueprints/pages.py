from flask import Blueprint, render_template, session, url_for
from werkzeug.utils import redirect

pages = Blueprint(name='pages', import_name=__name__, url_prefix='/')


@pages.route('/')
@pages.route('/welcome')
def welcome():
    return render_template('welcome.html')


@pages.route('/followers')
def followers():
    if 'username' in session:
        return render_template('followers.html', title="Followers")
    else:
        redirect(url_for('welcome'))


@pages.route('/unfollowers')
def unfollowers():
    if 'username' in session:
        return render_template('followers.html', title="Unfollowers")
    else:
        redirect(url_for('welcome'))


@pages.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error_message=error), 404

