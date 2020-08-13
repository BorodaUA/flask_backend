from flask import Flask
import os
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import database_exists
from sqlalchemy import create_engine
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from db.db import db
from config import config
from api.models import user, hn_db, blog_news


def create_app(config_name):
    app = Flask(__name__)
    ###
    app.config.from_object(config[config_name])
    ###
    if app.config["TESTING"] == False:
        db.init_app(app)

        @app.before_first_request
        def create_tables():
            # default_postgres_db = os.environ.get("POSTGRES_DATABASE_URI")
            # default_engine = create_engine(default_postgres_db)
            # eng = db.get_engine(bind="flask_backend")
            # url = "postgresql+psycopg2://webportal_user:12345@postgres_server:5432/flask_backend"
            # hard_url_back = "postgresql+psycopg2://postgres_server:5432@webportal_user:12345/flask_backend"
            # if not database_exists(url):
            #     with default_engine.connect() as conn:
            #         conn.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            #         conn.execute(
            #             f"CREATE DATABASE {db.get_engine(bind='flask_backend').url.database} ENCODING 'utf8' TEMPLATE template1"
            #         )
            # if not database_exists(db.get_engine(bind="hacker_news").url):
            #     with default_engine.connect() as conn:
            #         conn.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            #         conn.execute(
            #             f"CREATE DATABASE {db.get_engine(bind='hacker_news').url.database} ENCODING 'utf8' TEMPLATE template1"
            #         )
            #
            user.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="flask_backend"),
                )
            )
            user.Base.query = user.Base.session.query_property()
            # user.Base.metadata.create_all(db.get_engine(bind="flask_backend"))
            #
            hn_db.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="hacker_news"),
                )
            )
            hn_db.Base.query = hn_db.Base.session.query_property()
            #hn_db.Base.metadata.create_all(db.get_engine(bind="hacker_news"))
            #
            blog_news.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="flask_backend"),
                )
            )
            blog_news.Base.query = blog_news.Base.session.query_property()
            # blog_news.Base.metadata.create_all(db.get_engine(bind="flask_backend"))

    with app.app_context():
        from api.bp import api_bp

        app.register_blueprint(api_bp)

    return app
