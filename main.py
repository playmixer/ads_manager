from flask import Flask
from src.database import db
from src.template import processor, filters

# from src.models import *


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    processor.init_app(app)
    filters.init_app(app)

    from app.manage import manage_app
    from app.api import api_app
    from app.auth import auth_app

    app.register_blueprint(manage_app, url_prefix='/advertise')
    app.register_blueprint(auth_app, url_prefix='/auth')
    app.register_blueprint(api_app, url_prefix='/api/v0')

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
