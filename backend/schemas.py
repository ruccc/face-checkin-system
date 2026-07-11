import datetime
from pydantic import BaseModel
from typing import Optional


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    student_id: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str = ""


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    student_id: str
    email: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class PhotoResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    photo_path: str
    photo_type: str
    has_face_feature: str
    confidence: Optional[float] = None
    status: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class CheckinRecordResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    student_id: Optional[str] = None
    checkin_time: datetime.datetime
    confidence: Optional[float] = None
    status: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
