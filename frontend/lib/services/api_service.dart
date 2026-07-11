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

  /// 保存用户名
  Future<void> setUserName(String name) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('user_name', name);
  }

  /// 获取用户名
  Future<String?> getUserName() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('user_name');
  }

  /// 清除 JWT Token（注销时）
  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('user_name');
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
    // 保存用户名
    if (data['user_name'] != null) {
      await setUserName(data['user_name'] as String);
    }
    return data;
  }

  // ==================== 签到接口 ====================

  /// 人脸签到（无需登录，拍照上传后后端自动比对）
  /// 返回: { "message": "..." }
  Future<Map<String, dynamic>> checkin({
    required XFile photo,
  }) async {
    final response = await multipartPost(
      '/checkin',
      {},
      photo,
      'photo',
      auth: false,
    );

    final body = await response.stream.bytesToString();
    final data = jsonDecode(body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw ApiException(data['detail'] ?? 'Checkin failed');
    }

    return data;
  }

  // ==================== 照片库接口 ====================

  /// 上传照片到个人照片库
  Future<Map<String, dynamic>> uploadPhoto({required XFile photo}) async {
    final response = await multipartPost(
      '/photos',
      {},
      photo,
      'photo',
      auth: true,
    );

    final body = await response.stream.bytesToString();
    final data = jsonDecode(body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw ApiException(data['detail'] ?? 'Upload failed');
    }

    return data;
  }

  /// 获取照片列表
  Future<List<Map<String, dynamic>>> listPhotos() async {
    final response = await get('/photos', auth: true);

    if (response.statusCode != 200) {
      final data = jsonDecode(response.body);
      throw ApiException(data['detail'] ?? 'Failed to load photos');
    }

    final list = jsonDecode(response.body) as List;
    return list.cast<Map<String, dynamic>>();
  }

  /// 删除照片
  Future<Map<String, dynamic>> deletePhoto(int photoId) async {
    final headers = await _headers(auth: true);
    final url = Uri.parse(ApiConfig.apiUrl('/photos/$photoId'));
    final response = await http.delete(url, headers: headers);

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw ApiException(data['detail'] ?? 'Delete failed');
    }

    return data;
  }

  /// 获取照片预览 URL
  String photoFileUrl(int photoId) {
    return '${ApiConfig.baseUrl}${ApiConfig.apiPrefix}/photos/$photoId/file';
  }

  // ==================== 签到记录接口 ====================

  /// 获取当前用户的签到记录
  Future<List<Map<String, dynamic>>> getCheckinRecords({
    int skip = 0,
    int limit = 100,
  }) async {
    final response = await get(
      '/checkin/records?skip=$skip&limit=$limit',
      auth: true,
    );

    if (response.statusCode != 200) {
      final data = jsonDecode(response.body);
      throw ApiException(data['detail'] ?? 'Failed to load records');
    }

    final list = jsonDecode(response.body) as List;
    return list.cast<Map<String, dynamic>>();
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
