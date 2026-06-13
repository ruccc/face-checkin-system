"""
人脸编码模块 - 使用 InsightFace 进行人脸特征提取
"""
import numpy as np
from typing import List, Optional
from insightface.app import FaceAnalysis
from config import MODEL_NAME, DEVICE


class FaceEncoder:
    """人脸编码器"""

    def __init__(self):
        """初始化人脸编码模型"""
        self.app = FaceAnalysis(
            name=MODEL_NAME,
            providers=['CPUExecutionProvider'] if DEVICE == 'cpu' else ['CUDAExecutionProvider']
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def encode(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        对图片中的人脸进行编码

        Args:
            image: BGR格式的图片数组

        Returns:
            512维人脸特征向量，如果没有检测到人脸则返回None
        """
        faces = self.app.get(image)

        if len(faces) == 0:
            return None

        # 返回最大人脸的编码（通常图片中只有一个人脸）
        # 如果有多个，选择置信度最高的
        best_face = max(faces, key=lambda f: f.det_score)
        return best_face.embedding

    def encode_all(self, image: np.ndarray) -> List[np.ndarray]:
        """
        对图片中所有人脸进行编码

        Args:
            image: BGR格式的图片数组

        Returns:
            人脸特征向量列表
        """
        faces = self.app.get(image)
        return [face.embedding for face in faces if face.embedding is not None]

    def encode_with_info(self, image: np.ndarray) -> dict:
        """
        编码并返回详细信息

        Args:
            image: BGR格式的图片数组

        Returns:
            包含编码和位置信息的字典
        """
        faces = self.app.get(image)

        if len(faces) == 0:
            return {
                'success': False,
                'message': '未检测到人脸',
                'embedding': None,
                'face_info': None
            }

        best_face = max(faces, key=lambda f: f.det_score)

        return {
            'success': True,
            'message': f'检测到 {len(faces)} 张人脸',
            'embedding': best_face.embedding.tolist() if best_face.embedding is not None else None,
            'face_info': {
                'bbox': best_face.bbox.tolist(),
                'det_score': float(best_face.det_score),
                'kps': best_face.kps.tolist() if best_face.kps is not None else None
            }
        }


# 全局编码器实例
_encoder = None


def get_encoder() -> FaceEncoder:
    """获取全局人脸编码器实例"""
    global _encoder
    if _encoder is None:
        _encoder = FaceEncoder()
    return _encoder