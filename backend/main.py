import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, engine
from routers import auth, checkin, users, photos
import models  # ensure all models are imported before init_db

app = FastAPI(
    title="Face Checkin System",
    description="人脸签到系统后端 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(checkin.router)
app.include_router(users.router)
app.include_router(photos.router)


@app.on_event("startup")
def on_startup():
    # 删除旧的分离式表（迁移到统一的 photos 表）
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    old_tables = ["checkin_records", "user_photos"]
    for table_name in old_tables:
        if table_name in inspector.get_table_names():
            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()
    init_db()


@app.get("/")
def root():
    return {"message": "Face Checkin System API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
