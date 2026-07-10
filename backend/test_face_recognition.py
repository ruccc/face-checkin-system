"""
人脸检测功能测试脚本

使用方法：
1. 将测试照片放在 backend/ 目录下，命名为 test_face.jpg
2. 运行：python test_face_recognition.py
"""
import os
import sys
import cv2
import numpy as np

# 添加 face_service 到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.face_service.face_detector import FaceDetector
from services.face_service.face_encoder import FaceEncoder


def test_face_detection(image_path: str):
    """测试人脸检测"""
    print("\n" + "=" * 50)
    print("测试人脸检测")
    print("=" * 50)
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return False
    
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print("❌ 无法读取图片，请检查文件格式")
        return False
    
    print(f"图片尺寸: {img.shape[1]}x{img.shape[0]}")
    
    # 初始化检测器
    print("初始化人脸检测器...")
    try:
        detector = FaceDetector()
        print("✅ 检测器初始化成功")
    except Exception as e:
        print(f"❌ 检测器初始化失败: {e}")
        return False
    
    # 检测人脸
    print("检测人脸中...")
    faces = detector.detect(img)
    
    if len(faces) == 0:
        print("❌ 未检测到人脸")
        return False
    
    print(f"✅ 检测到 {len(faces)} 张人脸")
    
    # 打印人脸信息
    for i, face in enumerate(faces):
        print(f"\n人脸 {i+1}:")
        print(f"  边界框: {face['bbox']}")
        print(f"  检测置信度: {face['det_score']:.4f}")
        if face['kps']:
            print(f"  关键点数量: {len(face['kps'])}")
    
    return True


def test_face_encoding(image_path: str):
    """测试人脸编码"""
    print("\n" + "=" * 50)
    print("测试人脸编码")
    print("=" * 50)
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return False
    
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print("❌ 无法读取图片")
        return False
    
    # 初始化编码器
    print("初始化人脸编码器...")
    try:
        encoder = FaceEncoder()
        print("✅ 编码器初始化成功")
    except Exception as e:
        print(f"❌ 编码器初始化失败: {e}")
        return False
    
    # 编码人脸
    print("编码人脸特征...")
    result = encoder.encode_with_info(img)
    
    if not result['success']:
        print(f"❌ 编码失败: {result['message']}")
        return False
    
    print(f"✅ {result['message']}")
    print(f"特征向量维度: {len(result['embedding'])}")
    print(f"特征向量前10个值: {result['embedding'][:10]}")
    
    face_info = result['face_info']
    print(f"\n人脸位置信息:")
    print(f"  边界框: {face_info['bbox']}")
    print(f"  检测置信度: {face_info['det_score']:.4f}")
    
    return True


def test_face_match(image_path1: str, image_path2: str):
    """测试人脸匹配（两张照片是否为同一人）"""
    print("\n" + "=" * 50)
    print("测试人脸匹配")
    print("=" * 50)
    
    if not os.path.exists(image_path1) or not os.path.exists(image_path2):
        print("❌ 图片文件不存在")
        return False
    
    # 初始化编码器
    try:
        encoder = FaceEncoder()
    except Exception as e:
        print(f"❌ 编码器初始化失败: {e}")
        return False
    
    # 读取并编码两张图片
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)
    
    if img1 is None or img2 is None:
        print("❌ 无法读取图片")
        return False
    
    embedding1 = encoder.encode(img1)
    embedding2 = encoder.encode(img2)
    
    if embedding1 is None or embedding2 is None:
        print("❌ 无法编码人脸")
        return False
    
    # 计算余弦相似度
    sim = np.dot(embedding1 / np.linalg.norm(embedding1), 
                 embedding2 / np.linalg.norm(embedding2))
    
    print(f"余弦相似度: {sim:.4f}")
    
    if sim >= 0.6:
        print("✅ 两张照片是同一个人")
    else:
        print("⚠️ 两张照片不是同一个人")
    
    return True


def test_real_time_webcam():
    """测试实时摄像头人脸检测"""
    print("\n" + "=" * 50)
    print("测试实时摄像头人脸检测")
    print("=" * 50)
    
    print("初始化摄像头...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return False
    
    print("✅ 摄像头打开成功")
    print("按 'q' 退出")
    
    # 初始化检测器
    try:
        detector = FaceDetector()
        print("✅ 人脸检测器初始化成功")
    except Exception as e:
        print(f"❌ 检测器初始化失败: {e}")
        cap.release()
        return False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 无法读取摄像头帧")
            break
        
        # 检测人脸
        faces = detector.detect(frame)
        
        # 绘制人脸框
        for face in faces:
            x1, y1, x2, y2 = face['bbox']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{face['det_score']:.2f}", (x1, y1-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 显示结果
        cv2.imshow('Face Detection', frame)
        
        # 按 q 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ 测试完成")
    
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("人脸检测功能测试")
    print("=" * 50)
    
    # 默认测试图片路径
    test_image1 = os.path.join(os.path.dirname(__file__), "test_face.jpg")
    test_image2 = os.path.join(os.path.dirname(__file__), "test_face2.jpg")
    
    # 使用命令行参数或默认值
    import sys
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = "5"
    
    results = []
    
    if choice == "1" or choice == "5":
        results.append(("人脸检测", test_face_detection(test_image1)))
    
    if choice == "2" or choice == "5":
        results.append(("人脸编码", test_face_encoding(test_image1)))
    
    if choice == "3" or choice == "5":
        results.append(("人脸匹配", test_face_match(test_image1, test_image2)))
    
    if choice == "4":
        results.append(("实时摄像头", test_real_time_webcam()))
    
    # 输出结果汇总
    if choice != "4":
        print("\n" + "=" * 50)
        print("测试结果汇总")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{name}: {status}")
        
        print(f"\n通过: {passed}/{total}")
        
        if passed == total:
            print("\n🎉 所有测试通过！人脸识别功能正常。")
        else:
            print("\n⚠️ 部分测试未通过，请检查代码或测试图片。")


if __name__ == "__main__":
    main()
