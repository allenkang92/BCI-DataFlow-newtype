from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Boolean

class BCISession(Base):
    __tablename__ = "bci_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String, index=True)
    date_recorded = Column(DateTime)
    subject_id = Column(String)

    data_points = relationship("BCIData", back_populates="session")

class BCIData(Base):
    __tablename__ = "bci_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("bci_sessions.id"))
    timestamp = Column(DateTime, index=True)
    channel_1 = Column(Float)
    channel_2 = Column(Float)
    channel_3 = Column(Float)
    channel_4 = Column(Float)

    session = relationship("BCISession", back_populates="data_points")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)