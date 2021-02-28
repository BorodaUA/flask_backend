from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from db import hacker_news_Base as Base


class HackerNewsTopStory(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_top_story"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    hn_id = Column(Integer, unique=True)
    deleted = Column(Boolean)
    type = Column(String)
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
    #
    comments = relationship(
        "HackerNewsTopStoryComment",
        backref="hacker_news_top_story",
        order_by="desc(HackerNewsTopStoryComment.parsed_time)",
        lazy='subquery'
    )
    #
    origin = Column(String)
    parsed_time = Column(DateTime)


class HackerNewsTopStoryComment(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_top_story_comment"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    hn_id = Column(Integer)
    deleted = Column(Boolean)
    type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer, ForeignKey("hacker_news_top_story.hn_id"))
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)
    #
    origin = Column(String)
    parsed_time = Column(DateTime)
    updated_time = Column(DateTime)


class HackerNewsNewStory(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_new_story"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    hn_id = Column(Integer, unique=True)
    deleted = Column(Boolean)
    type = Column(String)
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
        "HackerNewsNewStoryComment",
        backref="hacker_news_new_story",
        order_by="desc(HackerNewsNewStoryComment.parsed_time)",
        lazy='subquery'
    )
    origin = Column(String)
    parsed_time = Column(DateTime)


class HackerNewsNewStoryComment(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_new_story_comment"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    hn_id = Column(Integer)
    deleted = Column(Boolean)
    type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer, ForeignKey("hacker_news_new_story.hn_id"))
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)
    #
    origin = Column(String)
    parsed_time = Column(DateTime)
    updated_time = Column(DateTime)
