from app.auth.auth import Auth
from datetime import datetime, timedelta
from src.settings import settings


def date_now(d: int = 0):
    return datetime.utcnow() + timedelta(days=d)


def init_app(app):
    @app.context_processor
    def add_processor():
        from src.utils import file_exists
        from src import utils

        return dict(
            auth=Auth,
            file_is_exists=file_exists,
            date_now=date_now,
            list=list,
            settings=settings,
            utils=utils
        )
