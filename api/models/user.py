from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, Boolean, MetaData

Base = declarative_base()


class UserModel(Base):
    __bind_key__ = "flask_backend"
    #
    __tablename__ = "users"
    #
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(128), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    user_uuid = Column(String(128), unique=True)
    email_address = Column(String(128), nullable=False, unique=True, index=True)
    is_activated = Column(Boolean, default=False)
    origin = Column(String(128), nullable=False)
