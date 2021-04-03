from app.auth import Auth


def init_app(app):
    @app.context_processor
    def add_processor():
        from src.utils import file_exists

        return dict(
            auth=Auth,
            file_is_exists=file_exists
        )