import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):

    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("FLASK_BACK_1_DATABASE_URI")


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "TEST_FLASK_BACK_1_DATABASE_URI"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    )

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}
