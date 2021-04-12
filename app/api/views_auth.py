from flask import Blueprint, request, redirect, url_for, make_response, send_file, jsonify
from .views import render_json
from src import exceptions
from app.auth.auth import Auth
from src.logger import logger

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

        jwt = Auth.gen_jwt(user, device_id)
        token = Auth.create_session(user, ip, device_id).token
        return render_json(result=True, data={
            'accessToken': jwt,
            'refreshToken': token
        })

    except exceptions.NotHaveAttributes as err:
        return render_json(result=False, message=str(err))
    except Exception as err:
        logger.error('signup \n\t' + str(err))
        return render_json(result=False, message=str(err))


@api_app_auth.route('/signupToken', methods=['POST'])
def signup_token():
    try:
        json = request.json
        if not json:
            raise Exception('Not have json')

        token = json.get('personal_token')
        device_id = json.get('device_id')
        if token is None:
            raise exceptions.NotHaveAttributes('No have attrs personal_token')
        ip = request.remote_addr

        user = Auth.login_m_token(token)
        if not user:
            raise exceptions.NotAuthenticated('Token is not correct')

        jwt = Auth.gen_jwt(user, device_id)
        token = Auth.create_session(user, ip, device_id).token
        return render_json(result=True, data={
            'accessToken': jwt,
            'refreshToken': token
        })

    except exceptions.NotHaveAttributes as err:
        return render_json(result=False, message=str(err))
    except Exception as err:
        logger.error('signupToken \n\t' + str(err))
        return render_json(result=False, message=str(err))


@api_app_auth.route('/refreshToken', methods=['POST'])
def refresh_token():
    try:
        token = request.args.get('token')
        if not token:
            raise Exception('Args not have token')

        sess = Auth.refresh_session(token)

        if not sess:
            return '401 Unauthorized', 401

        user = sess.user
        jwt = Auth.gen_jwt(user, sess.device_id)
        token = sess.token
        return render_json(result=True, data={
            'accessToken': jwt,
            'refreshToken': token
        })
    except Exception as err:
        logger.error('refresh_token \n\t' + str(err))
        return render_json(result=False, message=str(err))


@api_app_auth.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        token = request.args.get('token')
        if not token:
            raise Exception('Args not have token')

        Auth.logout_m(token)

        return render_json(result=True, message='Logout')

    except Exception as err:
        logger.error('logout \n\t' + str(err))
        return render_json(result=False, message=str(err))
