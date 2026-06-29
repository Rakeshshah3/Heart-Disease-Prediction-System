from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String)
    prediction = Column(Integer)
    risk = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)