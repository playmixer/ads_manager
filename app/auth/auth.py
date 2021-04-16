from flask import session, current_app
from .models import User, Sessions, db, Role
from .utils import generate_string, encrypt_sha256, decrypt_sha256, get_token_from_header
import json
import base64
import datetime
from typing import List


class Auth:
    @classmethod
    def login_m(cls, username: str, password: str):
        user = User.check_password(username, password)
        return user

    @classmethod
    def logout_m(cls, token):
        return Sessions.delete_token(token)

    @classmethod
    def login_m_token(cls, token: str):
        user = User.check_personal_token(token)
        return user

    @classmethod
    def registration(cls, username, password):
        return User.registration(username, password)

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
    def refresh_session(cls, token):
        sess = Sessions.refresh(token)
        return sess

    @classmethod
    def gen_jwt(cls, user: User, device_id: str = ''):
        SECRET_KEY = current_app.config['SECRET_KEY']
        expiration = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
        header = {'alg': 'HS256', 'typ': 'JWT'}
        payload = {
            'user_id': user.id,
            'exp': expiration,
            'admin': False,
            'device_id': device_id
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

    @classmethod
    def get_jwt_payload(cls, jwt: str = None):
        if jwt is None:
            jwt = get_token_from_header()
        _, b64_payload, _ = jwt.split('.')
        jwt_decode = base64.b64decode(b64_payload)
        payload = json.loads(jwt_decode)
        return payload

    @classmethod
    def find_role(cls, *, roles: List[Role] = None, role_str: str = None):
        user = cls.get_user()
        roles_filtered = None
        if roles:
            roles_filtered = list(filter(lambda x: x in roles, user.roles))

        if role_str:
            role = Role.query.filter_by(title=role_str).first()
            if role:
                roles_filtered = list(filter(lambda x: x == role, user.roles))
        return roles_filtered
