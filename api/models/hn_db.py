from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    # create_engine,
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    Boolean,
    ForeignKey,
    MetaData,
)

# from sqlalchemy.orm import scoped_session, sessionmaker
# import os
# from dotenv import load_dotenv
# from flask_sqlalchemy import SQLAlchemy

# load_dotenv()

# db_address = os.environ.get("HACKER_NEWS_DATABASE_URI")


# engine = create_engine(db_address)
# db_session = scoped_session(
#     sessionmaker(autocommit=False, autoflush=False, bind=engine)
# )
# from db.db import db
Base = declarative_base()
# Base.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.get_engine('hacker_news')))
# Base.query = Base.session.query_property()
# Base.metadata.bind = db.get_engine('hacker_news')
# Base.query = db_session.query_property()

# metadata = MetaData()
# Base = declarative_base(metadata=metadata)

# from api.models.flask_sqlalchemy_bridge import db
# from db.db import Base
# from db.db import db


class HackerNews_TopStories(Base):
    # class HackerNews_TopStories(db.Model):
    # query = db.session(engine_options='hacker_news').query_property()
    __bind_key__ = "hacker_news"
    #
    __tablename__ = "hacker_news_top_stories"
    #
    #
    id = Column(Integer, primary_key=True)
    #
    parse_dt = Column(DateTime)
    #
    hn_url = Column(String)
    #
    item_id = Column(Integer)
    deleted = Column(Boolean)
    item_type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer)
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)


class HackerNews_TopStories_Comments(Base):

    __tablename__ = "hacker_news_top_stories_comments"
    #
    __bind_key__ = "hacker_news"
    #
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    #
    parse_dt = Column(DateTime)
    #
    by = Column(String)
    deleted = Column(Boolean)
    comment_id = Column(Integer)
    kids = Column(JSON)
    parent = Column(Integer)
    text = Column(String)
    time = Column(Integer)
    comment_type = Column(String)


class HackerNews_NewStories(Base):

    __tablename__ = "hacker_news_new_stories"
    #
    __bind_key__ = "hacker_news"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    #
    parse_dt = Column(DateTime)
    #
    hn_url = Column(String)
    #
    item_id = Column(Integer)
    deleted = Column(Boolean)
    item_type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer)
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)


class HackerNews_NewStories_Comments(Base):

    __tablename__ = "hacker_news_new_stories_comments"
    #
    __bind_key__ = "hacker_news"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    #
    parse_dt = Column(DateTime)
    #
    by = Column(String)
    deleted = Column(Boolean)
    comment_id = Column(Integer)
    kids = Column(JSON)
    parent = Column(Integer)
    text = Column(String)
    time = Column(Integer)
    comment_type = Column(String)


# def init_db():
#     Base.metadata.create_all(bind=engine)
