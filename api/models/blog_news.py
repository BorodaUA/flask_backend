from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from db import flask_backend_Base as Base


class BlogNewsStory(Base):

    __bind_key__ = "flask_backend"
    #
    __tablename__ = "blog_news_story"
    #
    #
    id = Column(Integer, primary_key=True, nullable=False)
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
    ###
    comments = relationship(
        "BlogNewsStoryComment",
        backref="blog_news_story",
        order_by="desc(BlogNewsStoryComment.id)",
        cascade="all,delete",
        lazy='subquery'
    )
    origin = Column(String)


class BlogNewsStoryComment(Base):

    __tablename__ = "blog_news_story_comment"
    #
    __bind_key__ = "flask_backend"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    deleted = Column(Boolean)
    type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer, ForeignKey("blog_news_story.id"))
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)
    origin = Column(String)
