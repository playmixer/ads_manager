from app.auth.auth import Auth
from datetime import datetime, timedelta


def utcnow(d: int = 0):
    return datetime.utcnow() + timedelta(days=d)


def init_app(app):
    @app.context_processor
    def add_processor():
        from src.utils import file_exists

        return dict(
            auth=Auth,
            file_is_exists=file_exists,
            utcnow=utcnow,
            list=list
        )
