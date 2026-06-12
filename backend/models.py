import datetime
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(50), nullable=False)
    student_id = Column(String(30), unique=True, nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    face_features = relationship("FaceFeature", back_populates="user", cascade="all, delete-orphan")
    checkin_records = relationship("CheckinRecord", back_populates="user", cascade="all, delete-orphan")


class FaceFeature(Base):
    __tablename__ = "face_features"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feature_vector = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="face_features")


class CheckinRecord(Base):
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    checkin_time = Column(DateTime, default=datetime.datetime.utcnow)
    photo_path = Column(String(256))
    confidence = Column(Float, nullable=True)
    status = Column(String(20), default="success")

    user = relationship("User", back_populates="checkin_records")
