import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, FaceFeature
from schemas import RegisterRequest, LoginRequest, TokenResponse, MessageResponse
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api", tags=["认证"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/register", response_model=MessageResponse)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    student_id: str = Form(...),
    email: str = Form(None),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.student_id == student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")

    # Save uploaded photo
    ext = os.path.splitext(photo.filename or "photo.jpg")[1]
    photo_filename = f"{uuid.uuid4().hex}{ext}"
    photo_path = os.path.join(UPLOAD_DIR, photo_filename)
    with open(photo_path, "wb") as f:
        f.write(await photo.read())

    # 先进行人脸编码，失败则不创建用户
    from services.face_service import encode_face
    feature_bytes = encode_face(photo_path)
    if not feature_bytes:
        # 人脸编码失败，删除已上传的照片
        if os.path.exists(photo_path):
            os.remove(photo_path)
        raise HTTPException(status_code=400, detail="Face encoding failed: no face detected or model error")

    # 人脸编码成功后才创建用户
    user = User(
        username=username,
        password_hash=hash_password(password),
        name=name,
        student_id=student_id,
        email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    face_feature = FaceFeature(user_id=user.id, feature_vector=feature_bytes)
    db.add(face_feature)
    db.commit()

    return {"message": "Registration successful"}


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_name": user.name}


@router.post("/logout", response_model=MessageResponse)
def logout(current_user: User = Depends(get_current_user)):
    # Stateless JWT — client discards token
    return {"message": "Logged out successfully"}
