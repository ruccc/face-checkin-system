import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Photo
from schemas import UserResponse, MessageResponse
from auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).all()
    return users


@router.delete("/me", response_model=MessageResponse)
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """注销当前登录用户账号，清空关联的所有数据"""
    username = current_user.username

    # 1. 删除用户关联的照片文件（磁盘文件）
    photos = db.query(Photo).filter(Photo.user_id == current_user.id).all()
    for photo in photos:
        if photo.photo_path and os.path.exists(photo.photo_path):
            os.remove(photo.photo_path)

    # 2. 删除用户（级联删除 face_features 和 photos 数据库记录）
    db.delete(current_user)
    db.commit()

    return {"message": f"Account '{username}' has been deleted. All your data has been cleared."}


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted"}
