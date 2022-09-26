from flask import (
    Blueprint,
    render_template,
)

frontend = Blueprint('frontend', __name__, url_prefix='/',
                     static_folder='static', template_folder='templates')

@frontend.route('/')
def view():
    return render_template('index.html')
