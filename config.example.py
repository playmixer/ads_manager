from datetime import timedelta
import logging

sql_user = 'root'
sql_pass = 'root'
LOGGER_LEVEL = logging.INFO

SQLALCHEMY_DATABASE_URI = f'mysql://{sql_user}:{sql_pass}@localhost/advertise'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'secret_key_for_secure'
UPLOAD_FOLDER = 'uploads'

PERMANENT_SESSION_LIFETIME = timedelta(days=1)
