from flask import Blueprint, session, jsonify
from werkzeug.exceptions import abort
from twittersupervisor.services.api_service import ApiService

api = Blueprint('api', __name__, url_prefix='/api')


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


