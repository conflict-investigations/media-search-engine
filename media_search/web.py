import json
import logging
import os
from flask import Flask

from .api import api
from .defaults import CONFIG
from .frontend import frontend

app = Flask(__name__, static_folder=None)

# First, import defaults
app.config.update(**(CONFIG.__dict__))

# Then, try reading user-supplied config JSON
try:
    conf_path = os.path.join(os.getcwd(), CONFIG.CONFIG_FILE)
    app.config.from_file(conf_path, load=json.load)
except FileNotFoundError:
    pass

# https://stackoverflow.com/a/32341402/2193463
# Return cyrillic etc. as-is, not 'u\xxx'-encoded
class NonASCIIJSONEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        kwargs['ensure_ascii'] = False
        kwargs['indent'] = None
        super(NonASCIIJSONEncoder, self).__init__(**kwargs)


app.json_encoder = NonASCIIJSONEncoder

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

app.register_blueprint(api)
app.register_blueprint(frontend)

@app.route('/api/v1')
def outdated():
    return 'API v1 is outdated, please update', 400


if __name__ == '__main__':
    app.run(debug=True, port=8000)
