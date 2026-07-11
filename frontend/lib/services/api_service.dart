import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';

/// API 服务 - 封装与后端的所有 HTTP 通信
class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  /// 获取存储的 JWT Token
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  /// 保存 JWT Token
  Future<void> setToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
  }

  /// 清除 JWT Token（注销时）
  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  /// 构建带认证的 Header
  Future<Map<String, String>> _headers({bool auth = false}) async {
    final headers = <String, String>{};
    if (auth) {
      final token = await getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  /// POST 请求（JSON body）
  Future<http.Response> post(String path, Map<String, dynamic> body,
      {bool auth = false}) async {
    final headers = await _headers(auth: auth);
    headers['Content-Type'] = 'application/json';
    final url = Uri.parse(ApiConfig.apiUrl(path));
    return await http.post(url, headers: headers, body: jsonEncode(body));
  }

  /// GET 请求
  Future<http.Response> get(String path, {bool auth = false}) async {
    final headers = await _headers(auth: auth);
    final url = Uri.parse(ApiConfig.apiUrl(path));
    return await http.get(url, headers: headers);
  }

  /// Multipart POST 请求（用于上传文件 + 表单数据）
  Future<http.StreamedResponse> multipartPost(
    String path,
    Map<String, String> fields,
    XFile? file,
    String fileFieldName, {
    bool auth = false,
  }) async {
    final headers = await _headers(auth: auth);
    final url = Uri.parse(ApiConfig.apiUrl(path));
    print('🔵 multipartPost: $url');

    final request = http.MultipartRequest('POST', url);
    request.headers.addAll(headers);

    // 添加表单字段
    request.fields.addAll(fields);

    // 添加文件
    if (file != null) {
      print('🔵 读取文件: ${file.name}');
      final bytes = await file.readAsBytes();
      print('🔵 文件大小: ${bytes.length} bytes');
      request.files.add(http.MultipartFile.fromBytes(
        fileFieldName,
        bytes,
        filename: file.name,
      ));
    }

    print('🔵 发送请求中...');
    final response = await request.send();
    print('🔵 响应状态码: ${response.statusCode}');
    return response;
  }

  // ==================== 注册接口 ====================

  /// 用户注册（含照片上传）
  /// 返回: { "message": "Registration successful" }
  Future<Map<String, dynamic>> register({
    required String username,
    required String password,
    required String name,
    required String studentId,
    String? email,
    required XFile photo,
  }) async {
    final response = await multipartPost(
      '/register',
      {
        'username': username,
        'password': password,
        'name': name,
        'student_id': studentId,
        if (email != null && email.isNotEmpty) 'email': email,
      },
      photo,
      'photo',
    );

    final body = await response.stream.bytesToString();
    final data = jsonDecode(body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw ApiException(data['detail'] ?? 'Registration failed');
    }

    return data;
  }

  // ==================== 登录接口 ====================

  /// 用户登录
  Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    final response = await post('/login', {
      'username': username,
      'password': password,
    });

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw ApiException(data['detail'] ?? 'Login failed');
    }

    // 保存 token
    await setToken(data['access_token'] as String);
    return data;
  }

  // ==================== 注销接口 ====================

  /// 用户注销
  Future<void> logout() async {
    try {
      await post('/logout', {}, auth: true);
    } finally {
      await clearToken();
    }
  }
}

/// API 异常
class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
