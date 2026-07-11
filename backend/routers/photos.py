import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, UserPhoto, FaceFeature
from schemas import UserPhotoResponse, MessageResponse
from auth import get_current_user

router = APIRouter(prefix="/api/photos", tags=["照片库"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=MessageResponse)
async def upload_photo(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传照片到个人照片库，并自动提取人脸特征"""
    ext = os.path.splitext(photo.filename or "photo.jpg")[1]
    photo_filename = f"{uuid.uuid4().hex}{ext}"
    photo_path = os.path.join(UPLOAD_DIR, photo_filename)
    with open(photo_path, "wb") as f:
        f.write(await photo.read())

    # 尝试提取人脸特征
    has_feature = "0"
    try:
        from services.face_service import encode_face
        feature_bytes = encode_face(photo_path)
        if feature_bytes:
            face_feature = FaceFeature(user_id=current_user.id, feature_vector=feature_bytes)
            db.add(face_feature)
            has_feature = "1"
    except Exception:
        # 人脸编码失败不影响照片存储，仅标记为无特征
        pass

    user_photo = UserPhoto(
        user_id=current_user.id,
        photo_path=photo_path,
        has_face_feature=has_feature,
    )
    db.add(user_photo)
    db.commit()

    return {"message": f"Photo uploaded successfully{' with face feature' if has_feature == '1' else ''}"}


@router.get("", response_model=List[UserPhotoResponse])
def list_photos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的照片列表"""
    photos = (
        db.query(UserPhoto)
        .filter(UserPhoto.user_id == current_user.id)
        .order_by(UserPhoto.created_at.desc())
        .all()
    )
    return photos


@router.get("/{photo_id}/file")
def get_photo_file(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取照片文件（用于前端预览）"""
    photo = db.query(UserPhoto).filter(
        UserPhoto.id == photo_id,
        UserPhoto.user_id == current_user.id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if not os.path.exists(photo.photo_path):
        raise HTTPException(status_code=404, detail="Photo file not found on disk")
    return FileResponse(photo.photo_path)


@router.delete("/{photo_id}", response_model=MessageResponse)
def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除照片（同时删除文件和对应的 FaceFeature）"""
    photo = db.query(UserPhoto).filter(
        UserPhoto.id == photo_id,
        UserPhoto.user_id == current_user.id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # 删除磁盘文件
    if os.path.exists(photo.photo_path):
        os.remove(photo.photo_path)

    db.delete(photo)
    db.commit()

    return {"message": "Photo deleted successfully"}
