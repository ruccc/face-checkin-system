import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

/// 签到页面 - 无需登录，拍照上传后后端自动比对人脸
class CheckinPage extends StatefulWidget {
  const CheckinPage({super.key});

  @override
  State<CheckinPage> createState() => _CheckinPageState();
}

class _CheckinPageState extends State<CheckinPage> {
  final _apiService = ApiService();
  final _picker = ImagePicker();

  // 状态
  XFile? _selectedPhoto;
  Uint8List? _selectedPhotoBytes;
  bool _isLoading = false;
  String? _resultMessage;
  bool? _isSuccess;

  @override
  void dispose() {
    super.dispose();
  }

  /// 选择照片（拍照或从相册）
  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? picked = await _picker.pickImage(
        source: source,
        imageQuality: 85,
        maxWidth: 1024,
        maxHeight: 1024,
      );
      if (picked != null) {
        final bytes = await picked.readAsBytes();
        setState(() {
          _selectedPhoto = picked;
          _selectedPhotoBytes = bytes;
          _resultMessage = null;
          _isSuccess = null;
        });
      }
    } catch (e) {
      _showSnackBar('获取图片失败: $e', isError: true);
    }
  }

  /// 显示选择照片方式的底部弹窗
  void _showImagePickerSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                '选择签到照片',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                '请拍摄或选择您的正脸照片进行签到',
                style: TextStyle(fontSize: 13, color: Color(0xFF999999)),
              ),
              const SizedBox(height: 20),
              ListTile(
                leading: const Icon(Icons.camera_alt, color: Colors.blue),
                title: const Text('拍照'),
                subtitle: const Text('使用相机拍摄'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library, color: Colors.green),
                title: const Text('从相册选择'),
                subtitle: const Text('选择已有照片'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickImage(ImageSource.gallery);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 提交签到
  Future<void> _submitCheckin() async {
    if (_selectedPhoto == null) {
      _showSnackBar('请先拍照或选择照片', isError: true);
      return;
    }

    setState(() {
      _isLoading = true;
      _resultMessage = null;
      _isSuccess = null;
    });

    try {
      final result = await _apiService.checkin(photo: _selectedPhoto!);

      if (!mounted) return;

      final message = result['message'] as String? ?? '签到完成';
      final isSuccess = message.contains('successful') ||
          message.contains('成功') ||
          message.contains('Welcome');

      setState(() {
        _resultMessage = message;
        _isSuccess = isSuccess;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _resultMessage = e.message;
        _isSuccess = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _resultMessage = '网络错误，请检查服务器连接';
        _isSuccess = false;
      });
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  /// 显示提示信息
  void _showSnackBar(String message, {required bool isError}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red.shade600 : Colors.green.shade600,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(16),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  /// 重置，准备下一次签到
  void _reset() {
    setState(() {
      _selectedPhoto = null;
      _selectedPhotoBytes = null;
      _resultMessage = null;
      _isSuccess = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: const Text('人脸签到'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: const Color(0xFF4A90D9),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.home_outlined),
            tooltip: '返回首页',
            onPressed: () => Navigator.pop(context),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 10),

            // 图标
            const Icon(
              Icons.camera_alt_rounded,
              size: 64,
              color: Color(0xFF4A90D9),
            ),
            const SizedBox(height: 12),
            const Text(
              '人脸签到',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF333333),
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              '拍照上传后系统将自动比对人脸完成签到',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Color(0xFF999999)),
            ),
            const SizedBox(height: 30),

            // 照片区域
            _buildSectionTitle('签到照片'),
            const SizedBox(height: 12),
            _buildPhotoArea(),
            const SizedBox(height: 30),

            // 提交按钮
            SizedBox(
              height: 50,
              child: ElevatedButton.icon(
                onPressed: (_isLoading || _selectedPhoto == null)
                    ? null
                    : _submitCheckin,
                icon: _isLoading
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.fingerprint, size: 22),
                label: Text(
                  _isLoading ? '正在识别中...' : '提交签到',
                  style: const TextStyle(fontSize: 17, letterSpacing: 2),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF4A90D9),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 2,
                  disabledBackgroundColor: Colors.grey.shade300,
                ),
              ),
            ),
            const SizedBox(height: 20),

            // 结果展示
            if (_resultMessage != null) _buildResultCard(),

            const SizedBox(height: 20),

            // 底部提示
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFEEEEEE)),
              ),
              child: const Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline, size: 18, color: Color(0xFF4A90D9)),
                      SizedBox(width: 8),
                      Text(
                        '签到说明',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF333333),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 10),
                  Text(
                    '1. 请确保拍照时光线充足、面部清晰可见\n'
                    '2. 照片中需包含完整正面人脸\n'
                    '3. 如识别失败，请重新拍照后再次尝试\n'
                    '4. 无需登录，直接拍照即可完成签到',
                    style: TextStyle(
                      fontSize: 13,
                      color: Color(0xFF666666),
                      height: 1.8,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  /// 区块标题
  Widget _buildSectionTitle(String title) {
    return Row(
      children: [
        Container(
          width: 4,
          height: 18,
          decoration: BoxDecoration(
            color: const Color(0xFF4A90D9),
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF333333),
          ),
        ),
      ],
    );
  }

  /// 照片区域
  Widget _buildPhotoArea() {
    return GestureDetector(
      onTap: _showImagePickerSheet,
      child: Container(
        height: 220,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: const Color(0xFFE0E0E0),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: _selectedPhotoBytes != null
            ? ClipRRect(
                borderRadius: BorderRadius.circular(15),
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Image.memory(
                      _selectedPhotoBytes!,
                      fit: BoxFit.cover,
                    ),
                    // 重新选择按钮
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Material(
                        color: Colors.black54,
                        borderRadius: BorderRadius.circular(20),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(20),
                          onTap: _showImagePickerSheet,
                          child: const Padding(
                            padding: EdgeInsets.all(8),
                            child: Icon(
                              Icons.refresh,
                              color: Colors.white,
                              size: 22,
                            ),
                          ),
                        ),
                      ),
                    ),
                    // 删除按钮
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Material(
                        color: Colors.red.withValues(alpha: 0.8),
                        borderRadius: BorderRadius.circular(20),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(20),
                          onTap: () => setState(() {
                            _selectedPhoto = null;
                            _selectedPhotoBytes = null;
                            _resultMessage = null;
                            _isSuccess = null;
                          }),
                          child: const Padding(
                            padding: EdgeInsets.all(8),
                            child: Icon(
                              Icons.close,
                              color: Colors.white,
                              size: 22,
                            ),
                          ),
                        ),
                      ),
                    ),
                    // 底部提示
                    Positioned(
                      bottom: 0,
                      left: 0,
                      right: 0,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            vertical: 10, horizontal: 16),
                        color: Colors.black54,
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.touch_app, color: Colors.white, size: 16),
                            SizedBox(width: 6),
                            Text(
                              '点击更换照片',
                              style: TextStyle(
                                  color: Colors.white, fontSize: 14),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 72,
                    height: 72,
                    decoration: BoxDecoration(
                      color: const Color(0xFF4A90D9).withValues(alpha: 0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.add_a_photo,
                      size: 36,
                      color: Color(0xFF4A90D9),
                    ),
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    '点击拍照或选择照片',
                    style: TextStyle(
                      color: Color(0xFF4A90D9),
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    '请确保照片清晰、正面、光线充足',
                    style: TextStyle(
                      color: Color(0xFFBBBBBB),
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  /// 签到结果卡片
  Widget _buildResultCard() {
    final isSuccess = _isSuccess ?? false;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isSuccess
            ? const Color(0xFFE8F5E9)
            : const Color(0xFFFFEBEE),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isSuccess
              ? const Color(0xFF4CAF50).withValues(alpha: 0.3)
              : const Color(0xFFF44336).withValues(alpha: 0.3),
        ),
      ),
      child: Column(
        children: [
          Icon(
            isSuccess ? Icons.check_circle : Icons.error_outline,
            size: 48,
            color: isSuccess
                ? const Color(0xFF4CAF50)
                : const Color(0xFFF44336),
          ),
          const SizedBox(height: 12),
          Text(
            isSuccess ? '签到成功！' : '签到失败',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: isSuccess
                  ? const Color(0xFF2E7D32)
                  : const Color(0xFFC62828),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _resultMessage!,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: isSuccess
                  ? const Color(0xFF388E3C)
                  : const Color(0xFFD32F2F),
            ),
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: _reset,
            icon: const Icon(Icons.refresh, size: 18),
            label: const Text('重新签到'),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF4A90D9),
              side: const BorderSide(color: Color(0xFF4A90D9)),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            ),
          ),
        ],
      ),
    );
  }
}
