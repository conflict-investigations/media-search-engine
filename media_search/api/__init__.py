import pickle
from flask import (
    Blueprint,
    jsonify,
    request
)

DUMP_FILE = 'dump.pickle'

api = Blueprint('api', __name__, url_prefix='/api/v1')

processed = {}
with open(DUMP_FILE, 'rb') as f:
    processed = pickle.load(f)

# Pre-cache jsonify operation
# jsonified = None
# with current_app.app_context():
#     jsonified = jsonify(processed)

@api.route('/export', methods=['GET'])
def export():
    # return jsonified
    return jsonify(processed)

@api.route('/query', methods=['GET', 'POST'])
def query():
    url = request.args.get('url')
    if not url:
        # Be lenient and also parse JSON body
        url = request.get_json().get('url')
    if url not in processed:
        return jsonify(dict(
            message='Failure. Url not found in database',
            success=False,
        ))
    resp = dict(
        message='Success! Url found in database',
        success=True,
        dataset=processed[url]
    )
    return jsonify(resp)
