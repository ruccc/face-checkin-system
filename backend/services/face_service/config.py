"""
人脸识别服务配置
"""
import os
from datetime import timedelta

# ==================== 服务配置 ====================
SERVICE_HOST = "0.0.0.0"
SERVICE_PORT = 8000
DEBUG = True

# ==================== 数据库配置 ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'data', 'face_service.db')}"
)

# ==================== 安全配置 ====================
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# ==================== 模型配置 ====================
MODEL_NAME = "buffalo_l"  # InsightFace 模型名称
DEVICE = "cpu"  # 使用 cpu 或 cuda

# ==================== 人脸检测配置 ====================
MIN_FACE_SIZE = 30  # 最小人脸尺寸
DETECTION_THRESHOLD = 0.5  # 检测阈值

# ==================== 人脸识别配置 ====================
SIMILARITY_THRESHOLD = 0.6  # 人脸相似度阈值，超过此值认为是同一人
QUALITY_THRESHOLD = 0.5  # 人脸质量分数阈值

# ==================== 文件上传配置 ====================
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# ==================== 日志配置 ====================
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "service.log")

# ==================== 性能配置 ====================
# 模型缓存有效期（秒）
MODEL_CACHE_TTL = 3600

# 最大并发处理数
MAX_CONCURRENT_REQUESTS = 10