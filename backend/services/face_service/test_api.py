"""
测试脚本 - 测试人脸识别服务的基本功能
"""
import base64
import requests
import sys
import os

# 服务地址
BASE_URL = "http://localhost:8001"


def image_to_base64(image_path: str) -> str:
    """将图片转换为 base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_detect(image_path: str):
    """测试人脸检测"""
    print("\n=== 测试人脸检测 ===")
    image_base64 = image_to_base64(image_path)

    response = requests.post(
        f"{BASE_URL}/detect",
        json={"image_base64": image_base64}
    )

    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"检测到 {result['face_count']} 张人脸")
    for i, face in enumerate(result['faces']):
        print(f"  人脸 {i+1}: 置信度 {face['det_score']:.3f}, 位置 {face['bbox']}")


def test_encode(image_path: str):
    """测试人脸编码"""
    print("\n=== 测试人脸编码 ===")
    image_base64 = image_to_base64(image_path)

    response = requests.post(
        f"{BASE_URL}/encode",
        json={"image_base64": image_base64}
    )

    print(f"状态码: {response.status_code}")
    result = response.json()
    if result['success']:
        print(f"编码成功，特征向量维度: {len(result['embedding'])}")
        return result['embedding']
    else:
        print(f"编码失败: {result['message']}")
        return None


def test_register(image_path: str, user_id: str, metadata: dict = None):
    """测试人脸注册"""
    print(f"\n=== 测试人脸注册 (用户: {user_id}) ===")
    image_base64 = image_to_base64(image_path)

    response = requests.post(
        f"{BASE_URL}/register",
        params={"user_id": user_id, "metadata": metadata},
        json={"image_base64": image_base64}
    )

    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"结果: {result['message']}")


def test_recognize(image_path: str):
    """测试人脸识别"""
    print("\n=== 测试人脸识别 ===")
    image_base64 = image_to_base64(image_path)

    response = requests.post(
        f"{BASE_URL}/recognize",
        json={"image_base64": image_base64}
    )

    print(f"状态码: {response.status_code}")
    result = response.json()
    if result['success']:
        print(f"识别成功!")
        print(f"  用户ID: {result['user_id']}")
        print(f"  相似度: {result['similarity']:.3f}")
        print(f"  元数据: {result['metadata']}")
    else:
        print(f"识别失败: {result['message']}")


def test_list_users():
    """测试列出用户"""
    print("\n=== 测试列出用户 ===")
    response = requests.get(f"{BASE_URL}/list_users")
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"已注册用户数: {result['count']}")
    print(f"用户列表: {result['users']}")


def test_remove_user(user_id: str):
    """测试移除用户"""
    print(f"\n=== 测试移除用户 (用户: {user_id}) ===")
    response = requests.delete(f"{BASE_URL}/remove_face/{user_id}")
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"结果: {result['message']}")


def main():
    """主测试流程"""
    print("=" * 50)
    print("人脸识别服务测试")
    print("=" * 50)

    # 检查是否提供了测试图片
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print(f"  python {sys.argv[0]} <图片路径>")
        print("\n示例:")
        print(f"  python {sys.argv[0]} test_face.jpg")
        return

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        return

    # 运行测试
    try:
        # 1. 健康检查
        test_health()

        # 2. 人脸检测
        test_detect(image_path)

        # 3. 人脸编码
        embedding = test_encode(image_path)

        # 4. 注册人脸
        test_register(image_path, "user_001", {"name": "测试用户", "department": "研发部"})

        # 5. 列出用户
        test_list_users()

        # 6. 人脸识别
        test_recognize(image_path)

        # 7. 移除用户
        test_remove_user("user_001")

        # 8. 再次列出用户
        test_list_users()

        print("\n" + "=" * 50)
        print("测试完成!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务，请确保服务已启动")
        print("启动命令: cd face_service && python main.py")
    except Exception as e:
        print(f"\n测试出错: {e}")


if __name__ == "__main__":
    main()