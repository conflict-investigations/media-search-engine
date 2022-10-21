import pickle
from flask import (
    Blueprint,
    jsonify,
    request,
    send_file,
)

from ..defaults import CONFIG
from ..processors import (
    BadFormatError,
    CSVFileProcessor,
    CSVFileExporter,
    FileProcessor,
)
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
    if (urls := request.args.get('urls')):
        urls = urls.split(',')
    else:
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
            if p not in results[u]:
                results[u].append(p)
    if not results:
        return jsonify(dict(
            message='Failure. Url not found in database',
            success=False,
        ))
    # Return results as .csv file for importing into Excel
    # https://stackoverflow.com/questions/35710361/python-flask-send-file-stringio-blank-files
    # TODO and untested at the moment
    as_csv = False
    if (req_json := request.get_json(silent=True)):
        as_csv = req_json.get('as_csv')
    if as_csv:
        mem = CSVFileExporter.convert_to_csv(results)
        return send_file(
            mem,
            as_attachment=True,
            download_name='results.csv',
            mimetype='text/csv',
        )
    return jsonify(dict(
        message='Success! Url found in database',
        success=True,
        dataset=results
    ))
