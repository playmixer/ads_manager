from flask import Flask
from app.manage import manage_app
from app.auth import auth_app
from src.database import db
from src import processor

# from src.models import *


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    processor.init_app(app)

    app.register_blueprint(manage_app, url_prefix='/manage')
    app.register_blueprint(auth_app, url_prefix='/auth')

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
