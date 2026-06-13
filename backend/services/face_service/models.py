"""
数据库模型 - SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)  # 用户ID
    username = Column(String(100), unique=True, index=True, nullable=False)  # 用户名
    password_hash = Column(String(255), nullable=False)  # 密码哈希
    real_name = Column(String(100), nullable=True)  # 真实姓名
    department = Column(String(100), nullable=True)  # 部门
    phone = Column(String(20), nullable=True)  # 电话
    email = Column(String(100), nullable=True)  # 邮箱
    role = Column(String(20), default="user")  # 角色: admin, user
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    face_features = relationship("FaceFeature", back_populates="user", cascade="all, delete-orphan")
    sign_records = relationship("SignRecord", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "real_name": self.real_name,
            "department": self.department,
            "phone": self.phone,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FaceFeature(Base):
    """人脸特征模型"""
    __tablename__ = "face_features"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 用户ID
    embedding = Column(Text, nullable=False)  # 人脸特征向量（JSON格式存储）
    image_path = Column(String(500), nullable=True)  # 人脸图片路径
    quality_score = Column(Float, nullable=True)  # 人脸质量分数
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    user = relationship("User", back_populates="face_features")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_path": self.image_path,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SignRecord(Base):
    """签到记录模型"""
    __tablename__ = "sign_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 用户ID
    sign_type = Column(String(20), default="face")  # 签到类型: face, manual
    confidence = Column(Float, nullable=True)  # 识别置信度
    sign_time = Column(DateTime, default=datetime.now)  # 签到时间
    location = Column(String(200), nullable=True)  # 签到地点
    device_info = Column(String(200), nullable=True)  # 设备信息
    status = Column(String(20), default="success")  # 状态: success, failed
    remark = Column(Text, nullable=True)  # 备注

    # 关系
    user = relationship("User", back_populates="sign_records")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.real_name if self.user else None,
            "sign_type": self.sign_type,
            "confidence": self.confidence,
            "sign_time": self.sign_time.isoformat() if self.sign_time else None,
            "location": self.location,
            "device_info": self.device_info,
            "status": self.status,
            "remark": self.remark
        }


class LoginLog(Base):
    """登录日志模型"""
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(100), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    login_time = Column(DateTime, default=datetime.now)
    status = Column(String(20), default="success")  # success, failed
    message = Column(String(200), nullable=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "ip_address": self.ip_address,
            "login_time": self.login_time.isoformat() if self.login_time else None,
            "status": self.status,
            "message": self.message
        }