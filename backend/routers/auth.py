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

    # Create user
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

    # TODO: Call member B's face encoding service to extract features from photo
    # and store in face_features table
    # For now, store a placeholder
    from services.face_service import encode_face
    feature_bytes = encode_face(photo_path)
    if feature_bytes:
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
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", response_model=MessageResponse)
def logout(current_user: User = Depends(get_current_user)):
    # Stateless JWT — client discards token
    return {"message": "Logged out successfully"}
