"""
人脸识别签到系统 API - 符合 README 规范
"""
import os
import json
import base64
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from config import (
    SERVICE_HOST, SERVICE_PORT, UPLOAD_DIR, MAX_FILE_SIZE,
    SIMILARITY_THRESHOLD, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, LOG_LEVEL
)
from database import get_db, init_db
from models import User, FaceFeature, SignRecord, LoginLog
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)
from face_encoder import get_encoder
from face_search import get_searcher

# ==================== 创建应用 ====================
app = FastAPI(
    title="人脸签到系统",
    description="基于人脸识别的签到系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== 中间件配置 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 日志配置 ====================
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 启动事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("正在初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")

    # 创建上传目录
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "faces"), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "signs"), exist_ok=True)

    logger.info(f"人脸签到系统已启动: http://{SERVICE_HOST}:{SERVICE_PORT}")


# ==================== 工具函数 ====================

def base64_to_image(image_base64: str):
    """将 base64 字符串转换为 OpenCV 图片"""
    import numpy as np
    import cv2

    if not image_base64:
        return None

    # 移除 data:image/xxx;base64, 前缀
    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]

    try:
        image_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        logger.error(f"base64转图片失败: {e}")
        return None


def save_upload_file(file: UploadFile, subdir: str) -> str:
    """保存上传的文件"""
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_DIR, subdir, filename)

    with open(filepath, "wb") as f:
        content = file.file.read()
        f.write(content)

    return filepath


def save_base64_image(image_base64: str, subdir: str) -> Optional[str]:
    """保存base64图片到文件"""
    import numpy as np
    import cv2

    image = base64_to_image(image_base64)
    if image is None:
        return None

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_DIR, subdir, filename)
    cv2.imwrite(filepath, image)
    return filepath


# ==================== API 接口 ====================

# 1. 注册接口 - POST /api/register
@app.post("/api/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    real_name: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    用户注册接口（基本信息 + 上传标准人脸照片）
    
    使用 multipart/form-data 格式
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 生成 user_id
    user_id = f"U{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"

    # 创建用户
    user = User(
        user_id=user_id,
        username=username,
        password_hash=get_password_hash(password),
        real_name=real_name,
        department=department,
        phone=phone,
        email=email
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        logger.error(f"创建用户失败: {e}")
        raise HTTPException(status_code=500, detail="用户创建失败")

    # 处理人脸照片
    photo_path = save_upload_file(photo, "faces")

    # 提取人脸特征
    import numpy as np
    import cv2
    image_bytes = photo.file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    encoder = get_encoder()
    result = encoder.encode_with_info(image)

    if not result['success'] or result['embedding'] is None:
        # 删除用户和照片
        db.delete(user)
        db.commit()
        if os.path.exists(photo_path):
            os.remove(photo_path)
        raise HTTPException(status_code=400, detail="未检测到人脸，请上传包含清晰人脸的照片")

    # 保存人脸特征
    face_feature = FaceFeature(
        user_id=user.id,
        embedding=json.dumps(result['embedding']),
        image_path=photo_path,
        quality_score=result['face_info']['det_score']
    )
    db.add(face_feature)
    db.commit()

    # 更新内存检索库
    searcher = get_searcher()
    searcher.add_face(
        user_id=str(user.id),
        embedding=result['embedding'],
        metadata={"username": user.username, "user_id": user.user_id, "real_name": user.real_name}
    )

    logger.info(f"用户注册成功: {username}")

    # 生成 token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "success": True,
        "message": "注册成功",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


# 2. 登录接口 - POST /api/login
@app.post("/api/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    返回 JWT token
    """
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")

    # 生成 token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"用户登录成功: {username}")

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user.to_dict()
    }


# 3. 注销接口 - POST /api/logout
@app.post("/api/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户注销接口
    需要登录
    """
    logger.info(f"用户注销: {current_user.username}")
    return {"success": True, "message": "注销成功"}


# 4. 签到接口 - POST /api/checkin
@app.post("/api/checkin")
async def checkin(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    拍照上传签到接口
    无需登录，通过人脸识别确定用户身份
    """
    # 保存签到照片
    photo_path = save_upload_file(photo, "signs")

    # 读取图片
    import numpy as np
    import cv2
    content = await photo.read()
    nparr = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 提取人脸特征
    encoder = get_encoder()
    result = encoder.encode_with_info(image)

    if not result['success'] or result['embedding'] is None:
        return {
            "success": False,
            "message": "未检测到人脸"
        }

    # 搜索匹配用户
    searcher = get_searcher()
    match = searcher.search(result['embedding'], SIMILARITY_THRESHOLD)

    if match:
        user_id = int(match['user_id'])
        user = db.query(User).filter(User.id == user_id).first()

        if user and user.is_active:
            # 创建签到记录
            sign_record = SignRecord(
                user_id=user.id,
                sign_type="face",
                confidence=match['similarity'],
                status="success"
            )
            db.add(sign_record)
            db.commit()

            logger.info(f"签到成功: {user.username}, 相似度: {match['similarity']:.3f}")

            return {
                "success": True,
                "message": "签到成功",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "real_name": user.real_name
                },
                "confidence": match['similarity'],
                "sign_time": sign_record.sign_time.isoformat()
            }

    return {
        "success": False,
        "message": "未识别到已注册用户"
    }


# 5. 查看签到记录 - GET /api/checkin/records
@app.get("/api/checkin/records")
async def get_checkin_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    查看签到记录接口
    需要登录
    """
    records = db.query(SignRecord).filter(
        SignRecord.user_id == current_user.id
    ).order_by(SignRecord.sign_time.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "total": len(records),
        "records": [r.to_dict() for r in records]
    }


# 6. 用户列表（照片库管理） - GET /api/users
@app.get("/api/users")
async def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    用户列表接口（照片库管理）
    需要登录
    """
    users = db.query(User).offset(skip).limit(limit).all()

    result = []
    for user in users:
        user_dict = user.to_dict()
        user_dict['face_registered'] = len(user.face_features) > 0
        user_dict['sign_count'] = len(user.sign_records)
        result.append(user_dict)

    return {
        "success": True,
        "total": db.query(User).count(),
        "users": result
    }


# 7. 删除用户 - DELETE /api/users/{id}
@app.delete("/api/users/{id}")
async def delete_user(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户接口
    需要登录
    """
    # 查找用户
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 删除人脸照片
    for face in user.face_features:
        if face.image_path and os.path.exists(face.image_path):
            os.remove(face.image_path)

    # 删除用户（关联数据会自动删除）
    db.delete(user)
    db.commit()

    # 从内存检索库删除
    searcher = get_searcher()
    searcher.remove_face(str(id))

    logger.info(f"删除用户: {user.username}")

    return {"success": True, "message": "用户删除成功"}


# ==================== 其他辅助接口 ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "Face Checkin System",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "人脸签到系统 API",
        "docs": "/docs",
        "health": "/api/health"
    }


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        reload=True
    )