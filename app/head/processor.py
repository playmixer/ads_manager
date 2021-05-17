from . import data


def init_app(app):
    @app.context_processor
    def add_processort():
        return dict(
            head={
                'data': data
            }
        )
