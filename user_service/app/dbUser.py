import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    """
    SQLAlchemy model representing users table.
    """
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    email = Column(String(128), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    fullname = Column(String(128), nullable=False)
