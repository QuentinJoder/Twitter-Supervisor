from flask import Blueprint, session, jsonify
from werkzeug.exceptions import abort
from twittersupervisor.services import ApiService

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/followers')  # TODO paging of results
def get_followers():
    if 'username' in session:
        followers = ApiService.get_followers(session['username'])
        return jsonify(followers)
    else:
        abort(401)


@api.route('/unfollowers')  # TODO paging of results
def get_unfollowers():
    if 'username' in session:
        unfollowers = ApiService.get_unfollowers(session['username'])
        return jsonify(unfollowers)
    else:
        abort(401)


@api.route('/followers/<string:follower_id_str>/events')
def get_events_by_follower(follower_id_str):
    if 'username' in session:
        try:
            follower_id = int(follower_id_str)
        except ValueError:
            abort(400)
        events_list = ApiService.get_follow_events_by_follower(session['username'], follower_id)
        return jsonify(events_list)
    else:
        abort(401)


