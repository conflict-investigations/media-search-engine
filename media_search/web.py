from flask import (
    Flask,
)

from .api import api
from .frontend import frontend

app = Flask(__name__)

app.register_blueprint(api)
app.register_blueprint(frontend)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
