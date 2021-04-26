from flask import Flask, render_template
from src.database import db
from src.template import processor, filters
from app.auth import decorators
import config

# from src.models import *


def create_app():
    subdirectory = config.SUBDIRECTORY

    app = Flask(
        __name__,
        static_url_path='/'.join([subdirectory, 'static'])
    )
    app.config.from_pyfile('config.flask.py')

    db.init_app(app)
    processor.init_app(app)
    filters.init_app(app)

    from app.manage import manage_app
    from app.api import api_app, api_app_auth
    from app.auth import auth_app
    from app.admin import admin
    from app.promo import promo_app

    subdirectory = config.SUBDIRECTORY

    app.register_blueprint(manage_app, url_prefix=subdirectory + '/manage')
    app.register_blueprint(promo_app, url_prefix=subdirectory + '/promo')
    app.register_blueprint(auth_app, url_prefix=subdirectory + '/auth')
    app.register_blueprint(api_app, url_prefix=subdirectory + '/api/v0')
    app.register_blueprint(api_app_auth, url_prefix=subdirectory + '/api/v0/auth')
    app.register_blueprint(admin, url_prefix=subdirectory + '/admin')

    app.errorhandler(404)(
        decorators.login_required(lambda x: render_template('404.html'))
    )

    return app


if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0')
