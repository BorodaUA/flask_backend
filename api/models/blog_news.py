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
        cascade="all,delete"
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
   
