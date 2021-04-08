from flask import Blueprint, request, redirect, url_for, make_response, send_file, jsonify
from .views import render_json
from src import exceptions
from app.auth import Auth

__all__ = ['api_app_auth']

api_app_auth = Blueprint(
    'api_auth',
    __name__,
    template_folder='templates'
)


@api_app_auth.route('/signup', methods=['POST'])
def signup():
    try:
        json = request.json
        if not json:
            raise Exception('Not have json')

        username = json.get('username')
        password = json.get('password')
        device_id = json.get('device_id')
        if username is password is None:
            raise exceptions.NotHaveAttributes('No have attrs username or password')
        ip = request.remote_addr

        user = Auth.login_m(username, password)
        if not user:
            raise exceptions.NotAuthenticated('Username or password is not correct')

        jwt = Auth.gen_jwt(user)
        token = Auth.create_session(user, ip, device_id).token
        return render_json(result=True, data={
            'accessToken': jwt,
            'refreshToken': token
        })

    except exceptions.NotHaveAttributes as err:
        return render_json(result=False, message=str(err))
    except Exception as err:
        return render_json(result=False, message=str(err))


@api_app_auth.route('/refreshToken', methods=['POST'])
def refresh_token():
    ...
