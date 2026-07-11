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
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")


class FaceFeature(Base):
    __tablename__ = "face_features"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feature_vector = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="face_features")


class Photo(Base):
    """统一照片表 - 包含注册照、签到照、手动上传的照片"""
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 签到失败时可为 NULL
    photo_path = Column(String(256), nullable=False)
    photo_type = Column(String(20), default="upload")  # register / checkin / upload
    has_face_feature = Column(String(1), default="0")   # 是否已提取人脸特征: 0/1
    # 签到相关字段（仅 photo_type=checkin 时有值）
    confidence = Column(Float, nullable=True)
    status = Column(String(20), nullable=True)           # success / failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="photos")
