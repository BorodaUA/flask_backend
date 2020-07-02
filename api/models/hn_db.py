from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    Boolean,
    ForeignKey,
    MetaData,
)
from sqlalchemy.orm import relationship

Base = declarative_base()


class HackerNews_TopStories(Base):

    __bind_key__ = "hacker_news"
    #
    __tablename__ = "hacker_news_top_stories"
    #
    #
    id = Column(Integer, autoincrement=True)
    #
    parse_dt = Column(DateTime)
    #
    hn_url = Column(String)
    #
    item_id = Column(Integer, primary_key=True)
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

    ###
    comments = relationship(
        "HackerNews_TopStories_Comments",
        backref="hacker_news_top_stories",
        order_by="desc(HackerNews_TopStories_Comments.id)",
    )
    origin = Column(String(128), nullable=False)


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
    parent = Column(Integer, ForeignKey("hacker_news_top_stories.item_id"))
    text = Column(String)
    time = Column(Integer)
    comment_type = Column(String)
    origin = Column(String(128), nullable=False)


class HackerNews_NewStories(Base):

    __tablename__ = "hacker_news_new_stories"
    #
    __bind_key__ = "hacker_news"
    #
    id = Column(Integer)
    #
    parse_dt = Column(DateTime)
    #
    hn_url = Column(String)
    #
    item_id = Column(Integer, primary_key=True)
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
    comments = relationship(
        "HackerNews_NewStories_Comments",
        backref="hacker_news_new_stories",
        order_by="desc(HackerNews_NewStories_Comments.id)",
    )
    origin = Column(String(128), nullable=False)


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
    parent = Column(Integer, ForeignKey("hacker_news_new_stories.item_id"))
    text = Column(String)
    time = Column(Integer)
    comment_type = Column(String)
    origin = Column(String(128), nullable=False)
