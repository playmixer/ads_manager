from flask import Blueprint, render_template
from . import processor
from app.auth import decorators

head_app = Blueprint(
    'head',
    __name__,
    template_folder='templates'
)

processor.init_app(head_app)


@head_app.route('/')
@decorators.login_required
def index():
    return render_template('head/head.html')
