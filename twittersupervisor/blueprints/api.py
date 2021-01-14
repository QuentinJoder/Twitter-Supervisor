from flask import Blueprint, session, jsonify
from werkzeug.exceptions import abort
from twittersupervisor.models import AppUser, FollowEvent

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/followers')
def get_followers():
    if 'username' in session:
        user = AppUser.query.filter_by(screen_name=session['username']).first()
        followers = user.followers
        response = []
        for follower in followers:
            response.append(follower.to_dict())
        return jsonify(response)
    else:
        abort(401)


@api_bp.route('/followers/<int:follower_id>/events')
def events(follower_id):
    if 'username' in session:
        user_id = AppUser.query.filter_by(screen_name=session['username']).first().id
        events_list = FollowEvent.query.filter_by(followed_id=user_id, follower_id=follower_id).all()
        response = []
        for event in events_list:
            response.append(event.to_dict())
        return jsonify(events_list)
    else:
        abort(401)


