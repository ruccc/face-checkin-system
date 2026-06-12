/// 人脸签到系统 - API 配置
class ApiConfig {
  /// 服务器公网 IP 地址
  static const String baseUrl = 'http://115.120.192.191:8000';

  /// API 前缀
  static const String apiPrefix = '/api';

  /// 获取完整 API 地址
  static String apiUrl(String path) => '$baseUrl$apiPrefix$path';
}
