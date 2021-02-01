import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):

    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTGRES_DATABASE_URI = os.environ.get("POSTGRES_DATABASE_URI")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    ENV = "development"
    SQLALCHEMY_DATABASE_URI = os.environ.get("FLASK_BACKEND_DATABASE_URI")
    SQLALCHEMY_BINDS = {
        "flask_backend": os.environ.get("FLASK_BACKEND_DATABASE_URI"),
        "hacker_news": os.environ.get("HACKER_NEWS_DATABASE_URI"),
    }


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    ENV = "testing"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_FLASK_BACKEND_DATABASE_URI")
    SQLALCHEMY_BINDS = {
        "flask_backend": os.environ.get("TEST_FLASK_BACKEND_DATABASE_URI"),
        "hacker_news": os.environ.get("TEST_HACKER_NEWS_DATABASE_URI"),
    }


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
