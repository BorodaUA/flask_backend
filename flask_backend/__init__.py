from flask import Flask
from sqlalchemy.orm import scoped_session, sessionmaker
from db.db import db
from config import config
from api.models import user, hn_db, blog_news


def create_app(config_name):
    app = Flask(__name__)
    ###
    app.config.from_object(config[config_name])
    ###
    if not app.config["TESTING"]:
        db.init_app(app)

        @app.before_first_request
        def create_tables():
            user.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="flask_backend"),
                )
            )
            user.Base.query = user.Base.session.query_property()
            #
            hn_db.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="hacker_news"),
                )
            )
            hn_db.Base.query = hn_db.Base.session.query_property()
            #
            blog_news.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="flask_backend"),
                )
            )
            blog_news.Base.query = blog_news.Base.session.query_property()
    with app.app_context():
        from api.bp import api_bp
        app.register_blueprint(api_bp)

    return app
