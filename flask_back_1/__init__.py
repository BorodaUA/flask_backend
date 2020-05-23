from flask import Flask
import os


from api.models import user, hn_db
from api.models.flask_sqlalchemy import db
from dotenv import load_dotenv

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    ###
    # if test_config is None:
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("FLASK_BACK_1_DATABASE_URI")
    # elif test_config !=None:
    #     @app.teardown_appcontext
    # @app.teardown_request
    # def delete_tables(exception=None):
    #     db.drop_all()
    ###
    db.init_app(app)
    # flask_sqlalchemy.db.init_app(app)
    # user.init_db()
    hn_db.init_db()
    ###
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        # user.db_session.remove()
        hn_db.db_session.remove()
        # db.drop_all()

    ###
    # @app.before_first_request
    # def create_tables():
    #     db.create_all()
    ###
    with app.app_context():
        from api.bp import api_bp

        app.register_blueprint(api_bp)
        # delete_tables()
        ###
        # user.register_app_handlers(app, os.environ.get("FLASK_BACK_1_DATABASE_URI"))
        ###

    @app.route("/")
    def home_page():
        return "HOME PAGE"
        ###

    return app
