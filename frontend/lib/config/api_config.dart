/// 人脸签到系统 - API 配置
class ApiConfig {
  /// 本地后端地址：http://localhost:8000
  /// 服务器地址（远程服务器）
  static const String baseUrl = 'http://1.94.162.19:8000';

  /// API 前缀
  static const String apiPrefix = '/api';

  /// 获取完整 API 地址
  static String apiUrl(String path) => '$baseUrl$apiPrefix$path';
}
