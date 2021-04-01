from . import Auth
from flask import redirect, url_for, request
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        auth = Auth()
        if auth.is_authenticated():
            return f(*args, **kwargs)

        return redirect(url_for('auth.login', next=request.path))

    return wrap
