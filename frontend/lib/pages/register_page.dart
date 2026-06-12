import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

/// 注册页面
class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _apiService = ApiService();
  final _picker = ImagePicker();

  // 表单控制器
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _nameController = TextEditingController();
  final _studentIdController = TextEditingController();
  final _emailController = TextEditingController();

  // 状态
  File? _selectedPhoto;
  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _nameController.dispose();
    _studentIdController.dispose();
    _emailController.dispose();
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
        setState(() {
          _selectedPhoto = File(picked.path);
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
                '选择标准人脸照片',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),
              ListTile(
                leading: const Icon(Icons.camera_alt, color: Colors.blue),
                title: const Text('拍照'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library, color: Colors.green),
                title: const Text('从相册选择'),
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

  /// 提交注册
  Future<void> _submitRegister() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedPhoto == null) {
      _showSnackBar('请上传标准人脸照片', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    try {
      await _apiService.register(
        username: _usernameController.text.trim(),
        password: _passwordController.text,
        name: _nameController.text.trim(),
        studentId: _studentIdController.text.trim(),
        email: _emailController.text.trim().isEmpty
            ? null
            : _emailController.text.trim(),
        photo: _selectedPhoto!,
      );

      if (!mounted) return;

      _showSnackBar('注册成功！请前往登录', isError: false);

      // 返回登录页
      Navigator.pop(context, true);
    } on ApiException catch (e) {
      _showSnackBar(e.message, isError: true);
    } catch (e) {
      _showSnackBar('网络错误，请检查服务器连接', isError: true);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: const Text('用户注册'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: const Color(0xFF4A90D9),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 标题区域
              const SizedBox(height: 10),
              const Icon(
                Icons.how_to_reg,
                size: 60,
                color: Color(0xFF4A90D9),
              ),
              const SizedBox(height: 10),
              const Text(
                '创建新账户',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF333333),
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                '请填写基本信息并上传标准人脸照片',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: Color(0xFF999999)),
              ),
              const SizedBox(height: 30),

              // 基本信息
              _buildSectionTitle('基本信息'),
              const SizedBox(height: 12),
              _buildTextField(
                controller: _usernameController,
                label: '用户名',
                hint: '请输入用户名',
                icon: Icons.person_outline,
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? '请输入用户名' : null,
              ),
              const SizedBox(height: 14),
              _buildTextField(
                controller: _nameController,
                label: '真实姓名',
                hint: '请输入真实姓名',
                icon: Icons.badge_outlined,
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? '请输入真实姓名' : null,
              ),
              const SizedBox(height: 14),
              _buildTextField(
                controller: _studentIdController,
                label: '学号',
                hint: '请输入学号',
                icon: Icons.school_outlined,
                keyboardType: TextInputType.text,
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? '请输入学号' : null,
              ),
              const SizedBox(height: 14),
              _buildTextField(
                controller: _emailController,
                label: '邮箱（选填）',
                hint: '请输入邮箱地址',
                icon: Icons.email_outlined,
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 24),

              // 密码
              _buildSectionTitle('设置密码'),
              const SizedBox(height: 12),
              _buildTextField(
                controller: _passwordController,
                label: '密码',
                hint: '请输入密码（至少6位）',
                icon: Icons.lock_outline,
                obscureText: _obscurePassword,
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscurePassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                    color: Colors.grey,
                  ),
                  onPressed: () =>
                      setState(() => _obscurePassword = !_obscurePassword),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return '请输入密码';
                  if (v.length < 6) return '密码至少6位';
                  return null;
                },
              ),
              const SizedBox(height: 14),
              _buildTextField(
                controller: _confirmPasswordController,
                label: '确认密码',
                hint: '请再次输入密码',
                icon: Icons.lock_outline,
                obscureText: _obscureConfirmPassword,
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscureConfirmPassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                    color: Colors.grey,
                  ),
                  onPressed: () => setState(() =>
                      _obscureConfirmPassword = !_obscureConfirmPassword),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return '请确认密码';
                  if (v != _passwordController.text) return '两次密码不一致';
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // 人脸照片上传
              _buildSectionTitle('标准人脸照片'),
              const SizedBox(height: 12),
              _buildPhotoUploadArea(),
              const SizedBox(height: 30),

              // 注册按钮
              SizedBox(
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _submitRegister,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF4A90D9),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 2,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Colors.white,
                          ),
                        )
                      : const Text(
                          '注  册',
                          style: TextStyle(fontSize: 18, letterSpacing: 4),
                        ),
                ),
              ),
              const SizedBox(height: 16),

              // 已有账户？去登录
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    '已有账户？',
                    style: TextStyle(color: Color(0xFF999999)),
                  ),
                  GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: const Text(
                      '去登录',
                      style: TextStyle(
                        color: Color(0xFF4A90D9),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
            ],
          ),
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

  /// 输入框组件
  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    bool obscureText = false,
    Widget? suffixIcon,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        hintStyle: const TextStyle(color: Color(0xFFCCCCCC), fontSize: 14),
        prefixIcon: Icon(icon, color: const Color(0xFF4A90D9)),
        suffixIcon: suffixIcon,
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF4A90D9), width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.red),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
    );
  }

  /// 照片上传区域
  Widget _buildPhotoUploadArea() {
    return GestureDetector(
      onTap: _showImagePickerSheet,
      child: Container(
        height: 200,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: const Color(0xFFE0E0E0),
            style: BorderStyle.solid,
          ),
        ),
        child: _selectedPhoto != null
            ? ClipRRect(
                borderRadius: BorderRadius.circular(11),
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Image.file(
                      _selectedPhoto!,
                      fit: BoxFit.cover,
                    ),
                    // 重新选择按钮
                    Positioned(
                      top: 8,
                      right: 8,
                      child: GestureDetector(
                        onTap: () => setState(() => _selectedPhoto = null),
                        child: Container(
                          padding: const EdgeInsets.all(6),
                          decoration: const BoxDecoration(
                            color: Colors.black54,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.close,
                            color: Colors.white,
                            size: 20,
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
                            vertical: 8, horizontal: 12),
                        color: Colors.black54,
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.touch_app, color: Colors.white, size: 16),
                            SizedBox(width: 4),
                            Text(
                              '点击更换照片',
                              style:
                                  TextStyle(color: Colors.white, fontSize: 13),
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
                  Icon(
                    Icons.add_a_photo,
                    size: 48,
                    color: Colors.grey.shade400,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '点击上传标准人脸照片',
                    style: TextStyle(
                      color: Color(0xFF4A90D9),
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    '请确保照片清晰、正面、光线充足',
                    style: TextStyle(
                      color: Color(0xFFCCCCCC),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
