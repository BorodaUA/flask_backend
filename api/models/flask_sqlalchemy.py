from flask_sqlalchemy import SQLAlchemy
from .user import metadata, Base

db = SQLAlchemy(metadata=metadata, model_class=Base)
