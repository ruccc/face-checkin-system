# 人脸识别签到系统

## 项目概述

完整的人脸识别签到系统后端服务，包含用户管理、人脸注册、人脸识别、签到等功能。

## 功能特性

### 用户管理
- ✅ 用户注册（用户名 + 密码 + 基本信息）
- ✅ 用户登录（JWT Token认证）
- ✅ 用户注销
- ✅ 用户信息更新

### 人脸管理
- ✅ 人脸注册（上传标准人脸照片）
- ✅ 人脸删除
- ✅ 人脸状态查询
- ✅ 人脸识别（无需登录）

### 签到功能
- ✅ 人脸签到（自动识别用户）
- ✅ 手动签到
- ✅ 签到记录查询
- ✅ 今日签到状态
- ✅ 签到统计

### 管理功能
- ✅ 用户列表（管理员）
- ✅ 签到记录查询（管理员）
- ✅ 系统统计（管理员）

## 技术栈

- **Web框架**: FastAPI + Uvicorn
- **数据库**: SQLite + SQLAlchemy ORM
- **人脸识别**: InsightFace (ArcFace)
- **认证**: JWT Token
- **密码加密**: Bcrypt
- **容器化**: Docker + Docker Compose

## 项目结构

```
face_service/
├── config.py           # 配置文件
├── database.py         # 数据库配置
├── models.py           # 数据模型
├── auth.py             # 认证模块
├── face_detector.py    # 人脸检测
├── face_encoder.py     # 人脸编码
├── face_search.py      # 人脸检索
├── main.py             # API服务入口
├── requirements.txt    # Python依赖
├── Dockerfile          # Docker配置
├── docker-compose.yml  # Docker Compose配置
└── README.md           # 使用说明
```

## 快速开始

### 1. 本地运行

```bash
# 进入目录
cd face_service

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

服务启动后访问：
- API地址: http://localhost:8000
- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

### 2. Docker部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API文档

### 认证接口

#### 用户注册
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "123456",
  "real_name": "张三",
  "department": "研发部",
  "phone": "13800138000",
  "email": "zhangsan@example.com"
}

响应:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "user_id": "U20240101120000abc123",
    "username": "zhangsan",
    "real_name": "张三",
    ...
  }
}
```

#### 用户登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "123456"
}
```

#### 获取当前用户信息
```
GET /api/auth/me
Authorization: Bearer <token>
```

#### 用户登出
```
POST /api/auth/logout
Authorization: Bearer <token>
```

### 人脸接口

#### 注册人脸（需登录）
```
POST /api/face/register
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ..."
}

响应:
{
  "success": true,
  "message": "人脸注册成功",
  "face_info": {
    "bbox": [100, 100, 300, 300],
    "det_score": 0.99
  }
}
```

#### 人脸识别（无需登录）
```
POST /api/face/recognize
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
  "threshold": 0.6
}

响应:
{
  "success": true,
  "message": "识别成功",
  "user_id": 1,
  "username": "zhangsan",
  "real_name": "张三",
  "similarity": 0.85,
  "confidence_level": "high"
}
```

#### 获取人脸状态
```
GET /api/face/status
Authorization: Bearer <token>
```

#### 删除人脸
```
DELETE /api/face/remove
Authorization: Bearer <token>
```

### 签到接口

#### 用户签到
```
POST /api/sign/checkin
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
  "location": "公司门口",
  "device_info": "iPhone 14"
}

响应:
{
  "success": true,
  "message": "签到成功",
  "sign_record": {
    "id": 1,
    "user_name": "张三",
    "sign_type": "face",
    "sign_time": "2024-01-01T12:00:00",
    "status": "success",
    "confidence": 0.85
  }
}
```

#### 获取签到记录
```
GET /api/sign/records?skip=0&limit=20
Authorization: Bearer <token>
```

#### 获取今日签到状态
```
GET /api/sign/today
Authorization: Bearer <token>
```

### 管理接口（需管理员权限）

#### 获取所有用户
```
GET /api/admin/users?skip=0&limit=50
Authorization: Bearer <token>
```

#### 获取所有签到记录
```
GET /api/admin/sign_records?date=2024-01-01
Authorization: Bearer <token>
```

#### 获取统计数据
```
GET /api/admin/stats
Authorization: Bearer <token>
```

### 通用接口

#### 健康检查
```
GET /api/health
```

#### 公开统计
```
GET /api/stats/public
```

## 使用示例（Python）

```python
import requests
import base64

BASE_URL = "http://localhost:8001"

# 1. 注册用户
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "username": "test",
    "password": "123456",
    "real_name": "测试用户"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 读取图片并转为base64
with open("face.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

# 3. 注册人脸
response = requests.post(
    f"{BASE_URL}/api/face/register",
    headers=headers,
    json={"image_base64": image_base64}
)

# 4. 人脸签到（无需登录）
response = requests.post(
    f"{BASE_URL}/api/face/recognize",
    json={"image_base64": image_base64}
)
if response.json()["success"]:
    print(f"识别成功: {response.json()['real_name']}")
```

## 配置说明

在 `config.py` 中可以调整：

```python
# 服务配置
SERVICE_PORT = 8001
DEBUG = True

# 数据库
DATABASE_URL = "sqlite:///data/face_service.db"

# 安全配置
SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 人脸识别
MODEL_NAME = "buffalo_l"  # 模型名称
SIMILARITY_THRESHOLD = 0.6  # 相似度阈值
```

## Docker部署

```bash
# 构建镜像
docker build -t face-service .

# 运行容器
docker run -d -p 8001:8001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  --name face-service \
  face-service

# 使用 docker-compose
docker-compose up -d
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接URL | SQLite本地文件 |
| `SECRET_KEY` | JWT密钥 | 开发用密钥 |
| `SERVICE_PORT` | 服务端口 | 8001 |
| `LOG_LEVEL` | 日志级别 | INFO |

## 常见问题

### 1. 模型下载失败

InsightFace 模型托管在 HuggingFace，可设置镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 2. GPU加速

安装GPU版本：
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu
```

修改 `config.py`：
```python
DEVICE = "cuda"
```

### 3. 内存不足

使用更小的模型：
```python
MODEL_NAME = "buffalo_m"  # 或 "buffal
```