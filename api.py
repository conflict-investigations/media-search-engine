import pickle
from flask import (
    Blueprint,
    Flask,
    jsonify,
    render_template,
    request
)

DUMP_FILE = 'dump.pickle'

app = Flask(__name__)
api = Blueprint('api', __name__, url_prefix='/api/v1')
frontend = Blueprint('frontend', __name__, template_folder='.')

processed = {}
with open(DUMP_FILE, 'rb') as f:
    processed = pickle.load(f)

# Pre-cache jsonify operation
jsonified = None
with app.app_context():
    jsonified = jsonify(processed)

@api.route('/export', methods=['GET'])
def export():
    return jsonified

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

@frontend.route('/')
def view():
    return render_template('index.html')


app.register_blueprint(api)
app.register_blueprint(frontend)

if __name__ == '__main__':
    app.run(debug=True)
