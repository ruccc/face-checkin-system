import uvicorn
import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from database import init_db, engine
from routers import auth, checkin, users, photos
import models  # ensure all models are imported before init_db

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main")

app = FastAPI(
    title="Face Checkin System",
    description="人脸签到系统后端 API",
    version="1.0.0",
)

# ==================== CORS 中间件 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 兜底中间件：确保所有响应都有 CORS 头 + 记录错误日志
class ForceCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            resp = JSONResponse(status_code=200, content={"detail": "OK"})
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PUT, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            return resp
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"未捕获异常 [{request.method} {request.url.path}]: {e}")
            logger.error(traceback.format_exc())
            response = JSONResponse(
                status_code=500,
                content={"detail": f"Internal Server Error: {str(e)}"},
            )
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response


app.add_middleware(ForceCORSMiddleware)

# ==================== 全局异常处理器 ====================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常 [{request.method} {request.url.path}]: {exc}")
    logger.error(traceback.format_exc())
    resp = JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"},
    )
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


# ==================== 路由注册 ====================
app.include_router(auth.router)
app.include_router(checkin.router)
app.include_router(users.router)
app.include_router(photos.router)


# ==================== 启动事件 ====================
@app.on_event("startup")
def on_startup():
    # 删除旧的分离式表
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    old_tables = ["checkin_records", "user_photos"]
    for table_name in old_tables:
        if table_name in inspector.get_table_names():
            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()
    init_db()
    logger.info("数据库初始化完成")

    # 预热人脸识别模型（提前加载，避免首次请求超时崩溃）
    try:
        from services.face_service import FaceEncoder
        logger.info("正在加载人脸识别模型 (buffalo_l)...")
        FaceEncoder()  # 触发模型下载和加载
        logger.info("✅ 人脸识别模型加载成功")
    except Exception as e:
        logger.error(f"❌ 人脸识别模型加载失败: {e}")
        logger.error(traceback.format_exc())


# ==================== 健康检查 ====================
@app.get("/")
def root():
    return {"message": "Face Checkin System API is running"}


@app.get("/health")
def health():
    """健康检查端点，用于排查问题"""
    health_info = {
        "status": "ok",
        "database": "unknown",
        "face_model": "unknown",
    }
    # 检查数据库
    try:
        from database import SessionLocal
        from sqlalchemy import text as sa_text
        db = SessionLocal()
        db.execute(sa_text("SELECT 1"))
        db.close()
        health_info["database"] = "ok"
    except Exception as e:
        health_info["database"] = f"error: {e}"

    # 检查人脸模型
    try:
        from services.face_service import _get_encoder
        enc = _get_encoder()
        health_info["face_model"] = "ok" if enc is not None else "not_loaded"
    except Exception as e:
        health_info["face_model"] = f"error: {e}"

    return health_info


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
