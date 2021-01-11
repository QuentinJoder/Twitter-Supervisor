from flask import Blueprint, session, jsonify
from werkzeug.exceptions import abort

from twittersupervisor.database import Database

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/followers')
def get_followers():
    if 'username' in session:
        db = Database()
        return jsonify(db.get_followers())
    else:
        abort(401)


@api_bp.route('/followers/<int:follower_id>/events')
def events(follower_id):
    if 'username' in session:
        db = Database()
        events_list = db.get_friendship_events(follower_id)
        return jsonify(events_list)
    else:
        abort(401)


