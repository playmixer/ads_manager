from flask import session
from src.models import User


class Auth:
    username = None

    @classmethod
    def login(cls, username: str, password: str):
        if username == 'admin' and password == 'admin':
            session['auth'] = True
            session['username'] = username.lower()
            cls.username = username.lower()

    @classmethod
    def logout(cls):
        session['auth'] = False
        session['username'] = None

    @classmethod
    def is_authenticated(cls):
        return True if session.get('auth') and session.get('username') else False

    @classmethod
    def get_username(cls):
        return session.get('username')

    @classmethod
    def get_user(cls):
        if cls.is_authenticated():
            user = User.query.filter_by(username=cls.get_username()).first()
            return user
        return False
