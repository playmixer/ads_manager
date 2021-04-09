from . import Auth
from flask import redirect, url_for, request
from functools import wraps
import base64
import json
import datetime
from src.logger import logger


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        auth = Auth()
        if auth.is_authenticated():
            return f(*args, **kwargs)

        return redirect(url_for('auth.login', next=request.path))

    return wrap


def authenticated_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')

            if not Auth.is_authenticated():

                if not auth_header or not auth_header.startswith('Bearer'):
                    return '401 Unauthorized', 401

                _, token = auth_header.split(' ')
                if not Auth.verify_jwt(token):
                    return '401 Unauthorized', 401

                _, b64_payload, _ = token.split('.')
                payload = json.loads(base64.b64decode(b64_payload).decode())
                exp = datetime.datetime.strptime(payload['exp'], '%Y-%m-%dT%H:%M:%S')
                if exp < datetime.datetime.utcnow():
                    return '401 Unauthorized', 401

            return f(*args, **kwargs)
        except Exception as err:
            logger.error('authenticated_required \n\t' + str(err))
            return '401 Unauthorized', 401

    return wrap
