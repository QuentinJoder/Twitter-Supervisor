from flask import Blueprint, session, jsonify
from werkzeug.exceptions import abort
from twittersupervisor.services import AppUserService, FollowEventService

api_bp = Blueprint('api', __name__, url_prefix='/api')

# TODO paging of results
@api_bp.route('/followers')
def get_followers():
    if 'username' in session:
        followers = AppUserService.get_followers(session['username'])
        return jsonify(followers)
    else:
        abort(401)


@api_bp.route('/followers/<int:follower_id>/events')
def events(follower_id):
    if 'username' in session:
        events_list = FollowEventService.get_follow_events(session['username'], follower_id)
        return jsonify(events_list)
    else:
        abort(401)


