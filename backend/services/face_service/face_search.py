"""
人脸检索模块 - 人脸特征存储与比对
"""
import json
import os
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime
from .config import SIMILARITY_THRESHOLD
import os

FEATURE_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "face_features.json")


class FaceSearcher:
    """人脸检索器"""

    def __init__(self):
        """初始化人脸检索器"""
        self.feature_db: Dict[str, Dict[str, Any]] = {}
        self._load_db()

    def _load_db(self):
        """加载特征数据库"""
        if os.path.exists(FEATURE_DB_PATH):
            with open(FEATURE_DB_PATH, 'r', encoding='utf-8') as f:
                self.feature_db = json.load(f)

    def _save_db(self):
        """保存特征数据库"""
        os.makedirs(os.path.dirname(FEATURE_DB_PATH), exist_ok=True)
        with open(FEATURE_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.feature_db, f, ensure_ascii=False, indent=2)

    def add_face(self, user_id: str, embedding: List[float], metadata: Optional[Dict] = None) -> bool:
        """
        添加人脸特征到数据库

        Args:
            user_id: 用户ID
            embedding: 人脸特征向量
            metadata: 额外信息（如姓名等）

        Returns:
            是否添加成功
        """
        self.feature_db[user_id] = {
            'embedding': embedding,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat()
        }
        self._save_db()
        return True

    def remove_face(self, user_id: str) -> bool:
        """
        从数据库移除人脸特征

        Args:
            user_id: 用户ID

        Returns:
            是否移除成功
        """
        if user_id in self.feature_db:
            del self.feature_db[user_id]
            self._save_db()
            return True
        return False

    def search(self, query_embedding: List[float], threshold: Optional[float] = None) -> Optional[Dict]:
        """
        搜索匹配的人脸

        Args:
            query_embedding: 待查询的人脸特征向量
            threshold: 相似度阈值，默认使用配置中的值

        Returns:
            匹配结果，包含 user_id, similarity, metadata；未找到返回None
        """
        if threshold is None:
            threshold = SIMILARITY_THRESHOLD

        query_vec = np.array(query_embedding)
        query_vec = query_vec / np.linalg.norm(query_vec)  # 归一化

        best_match = None
        best_similarity = -1

        for user_id, data in self.feature_db.items():
            stored_vec = np.array(data['embedding'])
            stored_vec = stored_vec / np.linalg.norm(stored_vec)

            # 计算余弦相似度
            similarity = np.dot(query_vec, stored_vec)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'user_id': user_id,
                    'similarity': float(similarity),
                    'metadata': data.get('metadata', {}),
                    'created_at': data.get('created_at')
                }

        if best_match and best_similarity >= threshold:
            return best_match

        return None

    def search_top_k(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        搜索最相似的k个人脸

        Args:
            query_embedding: 待查询的人脸特征向量
            k: 返回数量

        Returns:
            匹配结果列表，按相似度降序排列
        """
        query_vec = np.array(query_embedding)
        query_vec = query_vec / np.linalg.norm(query_vec)

        results = []

        for user_id, data in self.feature_db.items():
            stored_vec = np.array(data['embedding'])
            stored_vec = stored_vec / np.linalg.norm(stored_vec)

            similarity = np.dot(query_vec, stored_vec)

            results.append({
                'user_id': user_id,
                'similarity': float(similarity),
                'metadata': data.get('metadata', {}),
                'created_at': data.get('created_at')
            })

        # 按相似度降序排序
        results.sort(key=lambda x: x['similarity'], reverse=True)

        return results[:k]

    def get_all_users(self) -> List[str]:
        """获取所有已注册用户ID"""
        return list(self.feature_db.keys())

    def get_user_count(self) -> int:
        """获取已注册用户数量"""
        return len(self.feature_db)

    def user_exists(self, user_id: str) -> bool:
        """检查用户是否已注册"""
        return user_id in self.feature_db


# 全局检索器实例
_searcher = None


def get_searcher() -> FaceSearcher:
    """获取全局人脸检索器实例"""
    global _searcher
    if _searcher is None:
        _searcher = FaceSearcher()
    return _searcher