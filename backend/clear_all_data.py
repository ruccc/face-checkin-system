"""清空所有用户数据：数据库表 + 上传的照片文件"""
import os
import shutil
from database import SessionLocal
from sqlalchemy import text

# 1. 清空数据库
db = SessionLocal()
try:
    db.execute(text("DELETE FROM photos"))
    db.execute(text("DELETE FROM face_features"))
    db.execute(text("DELETE FROM users"))
    db.commit()
    print("[OK] 数据库已清空 (users, face_features, photos)")
finally:
    db.close()

# 2. 清空上传目录
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
if os.path.isdir(uploads_dir):
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print(f"[OK] uploads 目录已清空 ({uploads_dir})")
else:
    print("[INFO] uploads 目录不存在，无需清理")

print("\n所有用户数据已清空，可以重新注册了！")
