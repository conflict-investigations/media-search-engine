from json import JSONEncoder
from flask import Flask

from .api import api
from .frontend import frontend

app = Flask(__name__, static_folder=None)

# https://stackoverflow.com/a/32341402/2193463
# Return cyrillic etc. as-is, not 'u\xxx'-encoded
class NonASCIIJSONEncoder(JSONEncoder):
    def __init__(self, **kwargs):
        kwargs['ensure_ascii'] = False
        kwargs['indent'] = None
        super(NonASCIIJSONEncoder, self).__init__(**kwargs)


app.json_encoder = NonASCIIJSONEncoder

app.register_blueprint(api)
app.register_blueprint(frontend)

# File uploads limited to 1MB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

if __name__ == '__main__':
    app.run(debug=True, port=8000)
