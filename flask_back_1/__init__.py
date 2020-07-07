from flask import Flask
import os
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import BaseQuery
from sqlalchemy_utils import database_exists, create_database

# from api.models import user, hn_db
# from api.models.flask_sqlalchemy_bridge import user_db, hacker_news_db
# from api.models.flask_sqlalchemy_bridge import db
# from dotenv import load_dotenv
from db.db import db


# load_dotenv()
from config import config
from api.models import user, hn_db


def create_app(config_name):
    app = Flask(__name__)
    ###
    app.config.from_object(config[config_name])
    # if test_config is None:
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get(
    #     "SQLALCHEMY_TRACK_MODIFICATIONS"
    # )
    # app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("FLASK_BACK_1_DATABASE_URI")
    # elif test_config !=None:
    #     @app.teardown_appcontext
    # @app.teardown_request
    # def delete_tables(exception=None):
    #     db.drop_all()
    ###
    if app.config["TESTING"] == False:
        db.init_app(app)

        @app.before_first_request
        def create_tables():
            back_engine = db.get_engine(bind="flask_back_1")
            #print('www', back_engine.url)
            if not database_exists(db.get_engine(bind="flask_back_1").url):
                create_database(db.get_engine(bind="flask_back_1").url)
            if not database_exists(db.get_engine(bind="hacker_news").url):
                create_database(db.get_engine(bind="hacker_news").url)
            user.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="flask_back_1"),
                )
            )
            user.Base.query = user.Base.session.query_property()
            user.Base.metadata.create_all(db.get_engine(bind="flask_back_1"))
            #
            hn_db.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="hacker_news"),
                )
            )
            hn_db.Base.query = hn_db.Base.session.query_property()
            hn_db.Base.metadata.create_all(db.get_engine(bind="hacker_news"))

    with app.app_context():
        from api.bp import api_bp

        app.register_blueprint(api_bp)

    return app
