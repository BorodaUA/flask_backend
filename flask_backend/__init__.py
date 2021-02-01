from flask import Flask, g
from db import create_session
from config import config


def create_app(config_name):
    app = Flask(__name__)
    ###
    app.config.from_object(config[config_name])
    ###
    flask_backend_session = create_session(
            app.config['SQLALCHEMY_BINDS']['flask_backend']
        )
    hacker_news_session = create_session(
            app.config['SQLALCHEMY_BINDS']['hacker_news']
        )

    @app.before_request
    def pass_session():
        g.flask_backend_session = flask_backend_session
        g.hacker_news_session = hacker_news_session

    with app.app_context():
        from api.bp import api_bp
        app.register_blueprint(api_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if g.flask_backend_session:
            g.flask_backend_session.remove()
        if g.hacker_news_session:
            g.hacker_news_session.remove()

    return app
