from flask import Flask, g
from db import flask_backend_session
from config import config


def create_app(config_name):
    app = Flask(__name__)
    ###
    app.config.from_object(config[config_name])
    ###

    @app.before_request
    def pass_session():
        g.flask_backend_session = flask_backend_session

    with app.app_context():
        from api.bp import api_bp
        app.register_blueprint(api_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        g.flask_backend_session.remove()

    return app
