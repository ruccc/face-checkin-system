# 人脸签到系统 (Face Checkin System)

## 项目简介
基于 FastAPI + SQLite 的人脸签到系统后端，支持注册、登录、签到、签到记录查看等功能。

## 技术栈
- 后端框架：FastAPI
- 数据库：SQLite (SQLAlchemy ORM)
- 认证：JWT Token
- 部署：华为云 ECS

## 团队成员

| 成员 | 角色 | 主要负责 |
|------|------|----------|
| 成员A | 后端开发 + 云部署 | 服务器架构、API接口、云端部署 |
| 成员B | 算法/模型 | 人脸检测、人脸编码与检索 |
| 成员C | 移动端开发 | 手机端UI、拍照上传、前后端联调 |

## 后端 API 地址

`http://115.120.192.191:8000`

## Swagger 文档

`http://115.120.192.191:8000/docs`

（可在浏览器中直接打开，在线测试所有接口）

## API 接口清单

| 方法 | 路径 | 说明 | 需登录 |
|------|------|------|--------|
| POST | /api/register | 注册（基本信息 + 上传标准照） | 否 |
| POST | /api/login | 登录，返回 JWT token | 否 |
| POST | /api/logout | 注销 | 是 |
| POST | /api/checkin | 拍照上传签到 | 否 |
| GET | /api/checkin/records | 查看签到记录 | 是 |
| GET | /api/users | 用户列表（照片库管理） | 是 |
| DELETE | /api/users/{id} | 删除用户 | 是 |

## 成员B 开发指引

需要实现 `backend/services/face_service.py` 中的两个函数：

### `encode_face(image_path: str) -> Optional[bytes]`
- 输入：上传的图片路径
- 输出：人脸特征向量（bytes），未检测到人脸返回 None
- 调用时机：用户注册时

### `search_face(image_path: str, threshold: float = 0.6) -> Optional[Tuple[int, float]]`
- 输入：签到照片路径
- 输出：(user_id, confidence) 或 None
- 调用时机：用户签到时

实现后 push 到 GitHub 即可。

## 成员C 开发指引

1. 访问 Swagger 文档查看所有接口的请求/响应格式
2. 注册接口使用 `multipart/form-data` 格式（含照片上传）
3. 登录后获取 token，后续请求在 Header 中添加 `Authorization: Bearer <token>`
4. 签到接口无需登录，只需上传照片

## GitHub 仓库

`https://github.com/ruccc/face-checkin-system`

## 本地启动

```bash
cd backend
pip install -r requirements.txt
export SECRET_KEY=your-secret-key
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
