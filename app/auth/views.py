from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import *
from app.auth.auth import Auth

__all__ = ['auth_app']

auth_app = Blueprint(
    'auth',
    __name__,
    template_folder='templates'
)


@auth_app.route('/login', methods=['POST', 'GET'])
def login():
    form = FormLogin()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')

        auth = Auth()
        auth.login(username, password)
        if not auth.is_authenticated():
            flash('Не верный логин или пароль', 'error')
            return render_template('auth/login.html', form=form, error='error')
        return redirect(url_for('manage.index'))
    return render_template('auth/login.html', form=form)


@auth_app.route('/logout', methods=['POST', 'GET'])
def logout():
    auth = Auth()
    auth.logout()
    return redirect(url_for('auth.login'))
