/// 人脸签到系统 - API 配置
class ApiConfig {
  /// 服务器地址（本地开发用 localhost，部署时改为公网 IP）
  static const String baseUrl = 'http://127.0.0.1:8000';

  /// API 前缀
  static const String apiPrefix = '/api';

  /// 获取完整 API 地址
  static String apiUrl(String path) => '$baseUrl$apiPrefix$path';
}
