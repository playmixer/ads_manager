def init_app(app):
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d'):
        return value.strftime(format) if value else ''
