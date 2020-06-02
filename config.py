import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):

    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    ENV = "development"
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    SQLALCHEMY_DATABASE_URI = os.environ.get("FLASK_BACK_1_DATABASE_URI")
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db1.db'
    # SQLALCHEMY_DATABASE_URI = os.environ.get("HACKER_NEWS_DATABASE_URI")
    SQLALCHEMY_BINDS = {
        "flask_back_1": os.environ.get("FLASK_BACK_1_DATABASE_URI"),
        "hacker_news": os.environ.get("HACKER_NEWS_DATABASE_URI"),
    }


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    ENV = "testing"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_FLASK_BACK_1_DATABASE_URI")
    SQLALCHEMY_BINDS = {
        "flask_back_1": os.environ.get("TEST_FLASK_BACK_1_DATABASE_URI"),
        "hacker_news": os.environ.get("TEST_HACKER_NEWS_DATABASE_URI"),
    }


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
