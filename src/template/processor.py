from app.auth.auth import Auth
from datetime import datetime, timedelta


def date_now(d: int = 0):
    return datetime.utcnow() + timedelta(days=d)


def init_app(app):
    @app.context_processor
    def add_processor():
        from src.utils import file_exists

        return dict(
            auth=Auth,
            file_is_exists=file_exists,
            date_now=date_now,
            list=list
        )
