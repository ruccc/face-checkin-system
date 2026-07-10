"""
人脸检测模块 - 使用 InsightFace 进行人脸检测
"""
import numpy as np
from typing import List, Tuple, Optional
from insightface.app import FaceAnalysis
from .config import MODEL_NAME, DEVICE, MIN_FACE_SIZE, DETECTION_THRESHOLD


class FaceDetector:
    """人脸检测器"""

    def __init__(self):
        """初始化人脸检测模型"""
        self.app = FaceAnalysis(
            name=MODEL_NAME,
            providers=['CPUExecutionProvider'] if DEVICE == 'cpu' else ['CUDAExecutionProvider']
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def detect(self, image: np.ndarray) -> List[dict]:
        """
        检测图片中的人脸

        Args:
            image: BGR格式的图片数组

        Returns:
            人脸列表，每个人脸包含:
            - bbox: 边界框 [x1, y1, x2, y2]
            - kps: 关键点
            - det_score: 检测置信度
        """
        faces = self.app.get(image)

        results = []
        for face in faces:
            if face.det_score < DETECTION_THRESHOLD:
                continue

            # 检查人脸尺寸
            bbox = face.bbox.astype(int)
            face_width = bbox[2] - bbox[0]
            face_height = bbox[3] - bbox[1]

            if face_width < MIN_FACE_SIZE or face_height < MIN_FACE_SIZE:
                continue

            results.append({
                'bbox': bbox.tolist(),
                'kps': face.kps.tolist() if face.kps is not None else None,
                'det_score': float(face.det_score)
            })

        return results

    def detect_and_crop(self, image: np.ndarray) -> Tuple[List[np.ndarray], List[dict]]:
        """
        检测人脸并裁剪

        Args:
            image: BGR格式的图片数组

        Returns:
            (裁剪的人脸图片列表, 人脸信息列表)
        """
        faces = self.app.get(image)

        cropped_faces = []
        face_infos = []

        for face in faces:
            if face.det_score < DETECTION_THRESHOLD:
                continue

            bbox = face.bbox.astype(int)
            face_width = bbox[2] - bbox[0]
            face_height = bbox[3] - bbox[1]

            if face_width < MIN_FACE_SIZE or face_height < MIN_FACE_SIZE:
                continue

            # 裁剪人脸
            x1, y1, x2, y2 = bbox
            cropped = image[y1:y2, x1:x2]

            cropped_faces.append(cropped)
            face_infos.append({
                'bbox': bbox.tolist(),
                'kps': face.kps.tolist() if face.kps is not None else None,
                'det_score': float(face.det_score)
            })

        return cropped_faces, face_infos

    def get_face_count(self, image: np.ndarray) -> int:
        """
        获取图片中的人脸数量

        Args:
            image: BGR格式的图片数组

        Returns:
            人脸数量
        """
        faces = self.app.get(image)
        return len([f for f in faces if f.det_score >= DETECTION_THRESHOLD])


# 全局检测器实例
_detector = None


def get_detector() -> FaceDetector:
    """获取全局人脸检测器实例"""
    global _detector
    if _detector is None:
        _detector = FaceDetector()
    return _detector