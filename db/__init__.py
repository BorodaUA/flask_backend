from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


flask_backend_Base = declarative_base()
hacker_news_Base = declarative_base()


def create_session(db_uri):
    engine = create_engine(
        db_uri
    )
    session = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    )
    return session
