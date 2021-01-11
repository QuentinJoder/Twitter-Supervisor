from flask import Blueprint, session, redirect, url_for, jsonify
from twittersupervisor.database import Database

api_bp = Blueprint('api', __name__, url_prefix='/api')

# TODO implement security
@api_bp.route('/followers')
def get_followers():
    if 'username' in session:
        db = Database()
        return jsonify(db.get_followers())
    else:
        redirect(url_for('welcome'))


@api_bp.route('/followers/<int:follower_id>/events')
def events(follower_id):
    if 'username' in session:
        db = Database()
        events_list = db.get_friendship_events(follower_id)
        return jsonify(events_list)
    else:
        redirect(url_for('welcome'))


