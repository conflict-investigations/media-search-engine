from flask import Flask

from .api import api
from .frontend import frontend

app = Flask(__name__, static_folder=None)

app.register_blueprint(api)
app.register_blueprint(frontend)

# File uploads limited to 1MB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

if __name__ == '__main__':
    app.run(debug=True, port=8000)
