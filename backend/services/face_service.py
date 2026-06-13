"""
Face encoding and search service.

这个模块提供了人脸检测、编码和检索的接口。
它调用 backend/services/face_service/ 中的实际模型实现。
"""

import os
import cv2
import numpy as np
from typing import Optional, Tuple

# 导入人脸编码器
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.face_service.face_encoder import FaceEncoder


# 全局编码器实例（延迟初始化）
_encoder = None


def _get_encoder() -> FaceEncoder:
    """获取或创建人脸编码器实例"""
    global _encoder
    if _encoder is None:
        _encoder = FaceEncoder()
    return _encoder


def encode_face(image_path: str) -> Optional[bytes]:
    """
    检测人脸并返回特征编码。

    Args:
        image_path: 上传的图片文件路径。

    Returns:
        特征向量作为bytes，如果未检测到人脸则返回None。
    """
    if not os.path.exists(image_path):
        return None

    # 读取图片（BGR格式）
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 使用人脸编码器提取特征
    encoder = _get_encoder()
    embedding = encoder.encode(img)

    if embedding is None:
        return None

    # 转换为bytes返回
    return embedding.tobytes()


def search_face(image_path: str, threshold: float = 0.6) -> Optional[Tuple[int, float]]:
    """
    检测人脸、编码并在数据库中搜索匹配项。

    Args:
        image_path: 签到照片的路径。
        threshold: 相似度阈值，用于接受匹配。

    Returns:
        如果找到匹配，返回(user_id, confidence)元组，否则返回None。
    """
    if not os.path.exists(image_path):
        return None

    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 提取特征
    encoder = _get_encoder()
    query_embedding = encoder.encode(img)

    if query_embedding is None:
        return None

    # 归一化查询向量
    query_vec = query_embedding / np.linalg.norm(query_embedding)

    # 从数据库读取所有用户特征进行比对
    # 导入成员A的数据库模型
    from database import SessionLocal
    from models import FaceFeature

    db = SessionLocal()
    try:
        face_features = db.query(FaceFeature).all()

        best_match_id = None
        best_similarity = -1

        for face_feature in face_features:
            # 从bytes转换为numpy数组
            stored_embedding = np.frombuffer(face_feature.feature_vector, dtype=np.float32)
            # 归一化存储的向量
            stored_vec = stored_embedding / np.linalg.norm(stored_embedding)

            # 计算余弦相似度
            similarity = np.dot(query_vec, stored_vec)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = face_feature.user_id

        # 检查是否超过阈值
        if best_match_id is not None and best_similarity >= threshold:
            return (best_match_id, float(best_similarity))

        return None

    finally:
        db.close()
