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


class BlogNewsStory(Base):

    __bind_key__ = "flask_backend"
    #
    __tablename__ = "blog_news_story"
    #
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    #
    deleted = Column(Boolean)
    item_type = Column(String)
    by = Column(String)
    time = Column(DateTime)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer)
    poll = Column(Integer)
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
    )
    origin = Column(String(128), nullable=False)


class BlogNewsStoryComment(Base):

    __tablename__ = "blog_news_story_comment"
    #
    __bind_key__ = "flask_backend"
    #
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    #
    parse_dt = Column(DateTime)
    #
    by = Column(String)
    deleted = Column(Boolean)
    comment_id = Column(Integer)
    kids = Column(JSON)
    parent = Column(Integer, ForeignKey("blog_news_story.item_id"))
    text = Column(String)
    time = Column(Integer)
    comment_type = Column(String)
    origin = Column(String(128), nullable=False)
