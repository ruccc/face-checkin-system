import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, CheckinRecord
from schemas import CheckinRecordResponse, MessageResponse
from auth import get_current_user

router = APIRouter(prefix="/api/checkin", tags=["签到"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=MessageResponse)
async def checkin(photo: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(photo.filename or "photo.jpg")[1]
    photo_filename = f"{uuid.uuid4().hex}{ext}"
    photo_path = os.path.join(UPLOAD_DIR, photo_filename)
    with open(photo_path, "wb") as f:
        f.write(await photo.read())

    from services.face_service import search_face
    result = search_face(photo_path)

    if result is None:
        record = CheckinRecord(
            user_id=None,
            photo_path=photo_path,
            status="failed",
            confidence=None,
        )
        db.add(record)
        db.commit()
        return {"message": "Checkin failed: face not recognized"}

    user_id, confidence = result
    user = db.query(User).filter(User.id == user_id).first()
    record = CheckinRecord(
        user_id=user_id,
        photo_path=photo_path,
        status="success",
        confidence=confidence,
    )
    db.add(record)
    db.commit()
    return {"message": f"Checkin successful! Welcome, {user.name}"}


@router.get("/records", response_model=List[CheckinRecordResponse])
def get_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(CheckinRecord)
        .order_by(CheckinRecord.checkin_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for r in records:
        user_name = r.user.name if r.user else None
        student_id = r.user.student_id if r.user else None
        result.append(CheckinRecordResponse(
            id=r.id,
            user_id=r.user_id,
            user_name=user_name,
            student_id=student_id,
            checkin_time=r.checkin_time,
            confidence=r.confidence,
            status=r.status,
        ))
    return result
