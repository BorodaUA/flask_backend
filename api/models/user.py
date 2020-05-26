from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean, MetaData

# import os
# from dotenv import load_dotenv

# load_dotenv()

# def register_app_handlers(app, db_address):


#     def database_connect(db_address):
#         engine = create_engine(db_address)
#         db_session = scoped_session(
#         sessionmaker(autocommit=False, autoflush=False, bind=engine)
#         )
#         return [engine, db_session]

#     return database_connect


# db_session = database_connect(os.environ.get("FLASK_BACK_1_DATABASE_URI"))[1]
# metadata = MetaData()
# db_address = os.environ.get("FLASK_BACK_1_DATABASE_URI")
# engine = create_engine(db_address)
# db_session = scoped_session(
#     sessionmaker(autocommit=False, autoflush=False, bind=engine)
# )
# from db.db import db
Base = declarative_base()
# Base.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))
# Base.query = Base.session.query_property()
# Base.metadata.bind = db.engine
# Base.query = db_session.query_property()
# Base.query = register_app_handlers.db_session.query_property()
# from api.models.flask_sqlalchemy_bridge import db
# from db.db import Base


class UserModel(Base):
    # class UserModel(db.Model):
    # query = db.session.query_property()
    __bind_key__ = "flask_back_1"
    #
    __tablename__ = "users"
    #
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(128), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    user_uuid = Column(String(128), unique=True)
    email_address = Column(String(128), nullable=False, unique=True, index=True)
    is_activated = Column(Boolean, default=False)


# def init_db():
#     Base.metadata.create_all(bind=engine)
