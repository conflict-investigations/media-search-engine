import pickle
from flask import (
    Blueprint,
    jsonify,
    request
)

from ..defaults import CONFIG
from ..processors import BadFormatError, CSVFileProcessor, FileProcessor
from ..utils import normalize_and_sanitize

api = Blueprint('api', __name__, url_prefix='/api/v1')

processed = {}
with open(CONFIG.DUMP_FILE, 'rb') as f:
    processed = pickle.load(f)

@api.route('/export', methods=['GET'])
def export():
    # TODO: Cache this
    return jsonify(processed)

@api.route('/query', methods=['GET', 'POST'])
def query():
    urls = request.args.get('urls')
    if not urls:
        # Be lenient and also parse JSON body
        if (req_json := request.get_json(silent=True)):
            urls = req_json.get('urls')
    if not urls:
        # If there's no JSON, then it's probably a CSV file
        file = request.files.get('file')
        if not file:
            return 'No query supplied', 400
        try:
            urls = CSVFileProcessor(file).get_links()
        except BadFormatError:
            urls = FileProcessor(file).get_links()
    urls = list(map(normalize_and_sanitize, urls))
    results = {}
    for u in filter(lambda x: x in processed, urls):
        for p in processed[u]:
            if not results.get(u):
                results[u] = [p]
                continue
            results[u].append(p)
    if not results:
        return jsonify(dict(
            message='Failure. Url not found in database',
            success=False,
        ))
    resp = dict(
        message='Success! Url found in database',
        success=True,
        dataset=results
    )
    return jsonify(resp)
