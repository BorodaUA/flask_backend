import os
from dotenv import load_dotenv
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
load_dotenv()
flask_backend_engine = create_engine(
    os.environ.get("FLASK_BACKEND_DATABASE_URI")
)
flask_backend_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=flask_backend_engine,
    )
)
flask_backend_Base = declarative_base()
