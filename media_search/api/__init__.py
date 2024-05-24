import io
import json
import pickle
from typing import Any
from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_file,
)

from ..defaults import CONFIG
from ..processors import (
    BadFormatError,
    BellingcatCSVFileProcessor,
    CSVFileExporter,
    FileProcessor,
)
from ..utils import normalize_and_sanitize

url_prefix = '/api/v1.1'
api = Blueprint('api', __name__, url_prefix=url_prefix)

processed: dict[str, Any] = {}
with open(CONFIG.DUMP_FILE, 'rb') as f:
    processed = pickle.load(f)

def reply_json(results):
    mem: io.BytesIO = io.BytesIO()
    mem.write(json.dumps(results).encode())
    mem.seek(0)
    return send_file(
        mem,
        as_attachment=True,
        download_name='results.json',
        mimetype='text/json',  # application/json???
    )

def reply_csv(results):
    # Return results as .csv file for importing into Excel
    # https://stackoverflow.com/questions/35710361/python-flask-send-file-stringio-blank-files
    mem: io.BytesIO = CSVFileExporter.convert_to_csv(results)
    return send_file(
        mem,
        as_attachment=True,
        download_name='results.csv',
        mimetype='text/csv',
    )

def handle_error(message: str, resultformat: str, req: Any):
    return jsonify(dict(
        message=message,
        success=False,
    ))

def handle_query(urls: list[str], resultformat: str, req: Any):
    if not urls:
        return handle_error('Failure. No URLs supplied', resultformat, req)

    urls = list(map(normalize_and_sanitize, urls))
    results = {}
    for u in filter(lambda x: x in processed, urls):
        for p in processed[u]:
            if not results.get(u):
                results[u] = [p]
                continue
            if p not in results[u]:
                results[u].append(p)

    if current_app.config['LOGGING']:
        offset = len(url_prefix)
        ip = req.environ.get('HTTP_X_FORWARDED_FOR', req.remote_addr)
        current_app.logger.warning(
            "{url} ip: {ip}, format: {fmt}, results: {num_res}, query: {urls}".format( # noqa
                url=req.path[offset:], ip=ip, fmt=resultformat,
                num_res=len(results), urls=str(urls),
            )
        )

    if not results:
        return jsonify(dict(
            message='Failure. Url not found in database',
            success=False,
        ))

    if resultformat == 'json':
        return reply_json(results)
    if resultformat == 'csv':
        return reply_csv(results)

    return jsonify(dict(
        message='Success! Url found in database',
        success=True,
        dataset=results
    ))

@api.route('/', methods=['GET'])
def overview():
    RESPONSE = 'Available endpoints: /export, /query, /query/csv'
    return RESPONSE, 200

@api.route('/export', methods=['GET'])
def export():
    # TODO: Cache this
    return jsonify(processed)

@api.route('/query/csv', methods=['POST'])
def query_csv():
    # If there's no JSON, then it's probably a CSV file
    file = request.files.get('file')
    if not file:
        return 'No query supplied', 400

    try:
        urls: list[str] = BellingcatCSVFileProcessor(file).get_links()
    except UnicodeDecodeError as e:
        return handle_error(
                'Failure. Uploaded .csv file has bad format: %s' % e,
                None,
                None,
        )
    except BadFormatError:
        urls: list[str] = FileProcessor(file).get_links()

    resultformat: str = request.form.get('format', 'text')

    return handle_query(urls, resultformat, request)

@api.route('/query', methods=['GET', 'POST'])
def query():
    resultformat: str = 'text'
    urls: list[str] = []
    if request.method == 'GET':
        if (urls := request.args.get('urls')):
            urls = urls.split(',')
            resultformat = request.args.get('format', 'text')
    else:  # POST
        # Parse JSON body
        if (req_json := request.get_json(silent=True)):
            urls = req_json.get('urls')
            resultformat = req_json.get('format', 'text')

    return handle_query(urls, resultformat, request)
