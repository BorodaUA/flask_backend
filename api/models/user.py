from sqlalchemy import Column, Integer, String, Boolean
from db import flask_backend_Base as Base


class UserModel(Base):
    __bind_key__ = "flask_backend"
    #
    __tablename__ = "users"
    #
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(128), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    user_uuid = Column(String(128), unique=True)
    email_address = Column(
        String(128),
        nullable=False,
        unique=True,
        index=True
    )
    is_activated = Column(Boolean, default=False)
    origin = Column(String(128), nullable=False)
