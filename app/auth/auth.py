from flask import session, current_app
from .models import User, Sessions, db
from .utils import generate_string, encrypt_sha256, decrypt_sha256
import json
import base64
import datetime


class Auth:
    @classmethod
    def login_m(cls, username: str, password: str):
        user = User.check_password(username, password)
        return user

    @classmethod
    def gen_token(cls):
        token = generate_string(200)
        return token

    @classmethod
    def login(cls, username: str, password: str):
        user = User.check_password(username, password)
        if user:
            session['user'] = {
                'auth': True,
                'username': user.username,
                'user_id': user.id
            }
            return True

        cls.logout()
        return False

    @classmethod
    def logout(cls):
        session['user'] = None

    @classmethod
    def is_authenticated(cls):
        user = session.get('user')
        if user:
            return True if user.get('auth') and user.get('username') else False
        return False

    @classmethod
    def get_username(cls):
        user = session.get('user')
        if user:
            return user.get('username')

    @classmethod
    def get_user(cls):
        if cls.is_authenticated():
            user = User.query.filter_by(username=cls.get_username()).first()
            return user
        return False

    @classmethod
    def create_session(cls, user: User, ip: str, device_id: str):
        sess = Sessions.create(user, device_id, ip)
        return sess

    @classmethod
    def get_refresh_token(cls):
        return generate_string(50)

    @classmethod
    def gen_jwt(cls, user: User):
        SECRET_KEY = current_app.config['SECRET_KEY']
        expiration = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).timestamp()
        header = {'alg': 'HS256', 'typ': 'JWT'}
        payload = {
            'user_id': user.id,
            'exp': expiration,
            'admin': False
        }
        b64_header = base64.b64encode(json.dumps(header).encode()).decode()
        b64_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        signature = encrypt_sha256(SECRET_KEY.encode(), (b64_header + '.' + b64_payload).encode())
        return '%s.%s.%s' % (b64_header, b64_payload, signature)

    @classmethod
    def verify_jwt(cls, jwt: str):
        SECRET_KEY = current_app.config['SECRET_KEY']
        header, payload, signature = jwt.split('.')
        signature_verify = encrypt_sha256(SECRET_KEY.encode(), (header + '.' + payload).encode())
        if signature == signature_verify:
            header_dict = json.loads(base64.b64decode(header))
            payload_dict = json.loads(base64.b64decode(payload))
            return header_dict, payload_dict
        return False
