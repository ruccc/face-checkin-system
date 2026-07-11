import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import 'checkin_page.dart';

/// 主页 - 登录后进入，管理照片库和查看签到记录
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _apiService = ApiService();
  final _picker = ImagePicker();

  String _userName = '';
  int _currentTabIndex = 0;

  // 照片库状态
  List<Map<String, dynamic>> _photos = [];
  bool _photosLoading = false;

  // 签到记录状态
  List<Map<String, dynamic>> _records = [];
  bool _recordsLoading = false;

  @override
  void initState() {
    super.initState();
    _loadUserName();
    _loadPhotos();
    _loadRecords();
  }

  Future<void> _loadUserName() async {
    final name = await _apiService.getUserName();
    if (mounted) {
      setState(() => _userName = name ?? '用户');
    }
  }

  Future<void> _loadPhotos() async {
    setState(() => _photosLoading = true);
    try {
      final photos = await _apiService.listPhotos();
      if (mounted) setState(() => _photos = photos);
    } on ApiException catch (e) {
      _showSnackBar(e.message, isError: true);
    } catch (e) {
      _showSnackBar('加载照片失败', isError: true);
    } finally {
      if (mounted) setState(() => _photosLoading = false);
    }
  }

  Future<void> _loadRecords() async {
    setState(() => _recordsLoading = true);
    try {
      final records = await _apiService.getCheckinRecords();
      if (mounted) setState(() => _records = records);
    } on ApiException catch (e) {
      _showSnackBar(e.message, isError: true);
    } catch (e) {
      _showSnackBar('加载签到记录失败', isError: true);
    } finally {
      if (mounted) setState(() => _recordsLoading = false);
    }
  }

  Future<void> _uploadPhoto() async {
    try {
      final XFile? picked = await _picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
        maxWidth: 1024,
        maxHeight: 1024,
      );
      if (picked == null) return;

      setState(() => _photosLoading = true);

      try {
        await _apiService.uploadPhoto(photo: picked);
        _showSnackBar('照片上传成功', isError: false);
        await _loadPhotos();
      } on ApiException catch (e) {
        _showSnackBar(e.message, isError: true);
        if (mounted) setState(() => _photosLoading = false);
      }
    } catch (e) {
      _showSnackBar('选择照片失败', isError: true);
    }
  }

  Future<void> _deletePhoto(int photoId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('确认删除'),
        content: const Text('确定要删除这张照片吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('删除'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;

    try {
      await _apiService.deletePhoto(photoId);
      _showSnackBar('照片已删除', isError: false);
      await _loadPhotos();
    } on ApiException catch (e) {
      _showSnackBar(e.message, isError: true);
    } catch (e) {
      _showSnackBar('删除失败', isError: true);
    }
  }

  Future<void> _logout() async {
    try {
      await _apiService.logout();
    } catch (_) {}
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  void _goToCheckin() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const CheckinPage()),
    ).then((_) => _loadRecords());
  }

  void _showSnackBar(String message, {required bool isError}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red.shade600 : Colors.green.shade600,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: const Text('人脸签到系统'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: const Color(0xFF4A90D9),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: '退出登录',
            onPressed: _logout,
          ),
        ],
      ),
      body: Column(
        children: [
          // 用户信息卡片
          _buildUserCard(),
          // Tab 切换栏
          _buildTabBar(),
          // 内容区域
          Expanded(
            child: _currentTabIndex == 0 ? _buildPhotoGallery() : _buildRecordsList(),
          ),
        ],
      ),
      floatingActionButton: _currentTabIndex == 0
          ? FloatingActionButton(
              onPressed: _photosLoading ? null : _uploadPhoto,
              backgroundColor: const Color(0xFF4A90D9),
              child: const Icon(Icons.add_a_photo, color: Colors.white),
            )
          : FloatingActionButton(
              onPressed: _goToCheckin,
              backgroundColor: const Color(0xFF4A90D9),
              child: const Icon(Icons.camera_alt, color: Colors.white),
            ),
    );
  }

  /// 用户信息卡片
  Widget _buildUserCard() {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF4A90D9), Color(0xFF357ABD)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF4A90D9).withValues(alpha: 0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 28,
            backgroundColor: Colors.white.withValues(alpha: 0.3),
            child: Text(
              _userName.isNotEmpty ? _userName[0].toUpperCase() : '?',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '欢迎回来，$_userName',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    _buildStatBadge(Icons.photo_library, '${_photos.length} 张照片'),
                    const SizedBox(width: 16),
                    _buildStatBadge(Icons.check_circle, '${_records.length} 次签到'),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatBadge(IconData icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: Colors.white70),
        const SizedBox(width: 4),
        Text(
          text,
          style: const TextStyle(fontSize: 13, color: Colors.white70),
        ),
      ],
    );
  }

  /// Tab 切换栏
  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          _buildTab('照片库', Icons.photo_library, 0),
          _buildTab('签到记录', Icons.history, 1),
        ],
      ),
    );
  }

  Widget _buildTab(String label, IconData icon, int index) {
    final isActive = _currentTabIndex == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _currentTabIndex = index),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: isActive ? const Color(0xFF4A90D9) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 20,
                color: isActive ? Colors.white : const Color(0xFF999999),
              ),
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: isActive ? Colors.white : const Color(0xFF999999),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 照片库
  Widget _buildPhotoGallery() {
    if (_photosLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF4A90D9)));
    }

    if (_photos.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.photo_library_outlined, size: 72, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text(
              '照片库为空',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade500),
            ),
            const SizedBox(height: 8),
            Text(
              '点击右下角按钮上传照片',
              style: TextStyle(fontSize: 14, color: Colors.grey.shade400),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadPhotos,
      color: const Color(0xFF4A90D9),
      child: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3,
          crossAxisSpacing: 10,
          mainAxisSpacing: 10,
          childAspectRatio: 0.85,
        ),
        itemCount: _photos.length,
        itemBuilder: (context, index) {
          final photo = _photos[index];
          return _buildPhotoCard(photo);
        },
      ),
    );
  }

  Widget _buildPhotoCard(Map<String, dynamic> photo) {
    final photoId = photo['id'] as int;
    final hasFeature = photo['has_face_feature'] as String? ?? '0';
    final createdAt = photo['created_at'] as String? ?? '';

    return GestureDetector(
      onTap: () => _showPhotoDetail(photoId),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                child: _buildPhotoImage(photoId),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        hasFeature == '1' ? Icons.face : Icons.face_outlined,
                        size: 14,
                        color: hasFeature == '1' ? Colors.green : Colors.orange,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        hasFeature == '1' ? '已识别' : '无人脸',
                        style: TextStyle(
                          fontSize: 11,
                          color: hasFeature == '1' ? Colors.green : Colors.orange,
                        ),
                      ),
                      const Spacer(),
                      GestureDetector(
                        onTap: () => _deletePhoto(photoId),
                        child: const Icon(Icons.delete_outline, size: 16, color: Colors.red),
                      ),
                    ],
                  ),
                  if (createdAt.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Text(
                      _formatDate(createdAt),
                      style: const TextStyle(fontSize: 10, color: Color(0xFFBBBBBB)),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPhotoImage(int photoId) {
    return FutureBuilder<Uint8List?>(
      future: _fetchPhotoBytes(photoId),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
            child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF4A90D9)),
          );
        }
        if (snapshot.hasData && snapshot.data != null) {
          return Image.memory(snapshot.data!, fit: BoxFit.cover);
        }
        return const Icon(Icons.broken_image, color: Colors.grey, size: 40);
      },
    );
  }

  Future<Uint8List?> _fetchPhotoBytes(int photoId) async {
    try {
      final token = await _apiService.getToken();
      final url = Uri.parse(_apiService.photoFileUrl(photoId));
      final response = await http.get(url, headers: {
        if (token != null) 'Authorization': 'Bearer $token',
      });
      if (response.statusCode == 200) {
        return response.bodyBytes;
      }
    } catch (_) {}
    return null;
  }

  void _showPhotoDetail(int photoId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => _PhotoDetailPage(
          photoId: photoId,
          apiService: _apiService,
        ),
      ),
    );
  }

  /// 签到记录列表
  Widget _buildRecordsList() {
    if (_recordsLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF4A90D9)));
    }

    if (_records.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 72, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text(
              '暂无签到记录',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade500),
            ),
            const SizedBox(height: 8),
            Text(
              '点击右下角按钮去签到',
              style: TextStyle(fontSize: 14, color: Colors.grey.shade400),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadRecords,
      color: const Color(0xFF4A90D9),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _records.length,
        itemBuilder: (context, index) {
          final record = _records[index];
          return _buildRecordCard(record);
        },
      ),
    );
  }

  Widget _buildRecordCard(Map<String, dynamic> record) {
    final status = record['status'] as String? ?? 'success';
    final isSuccess = status == 'success';
    final checkinTime = record['checkin_time'] as String? ?? '';
    final confidence = record['confidence'] as double?;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: isSuccess
                ? const Color(0xFFE8F5E9)
                : const Color(0xFFFFEBEE),
            shape: BoxShape.circle,
          ),
          child: Icon(
            isSuccess ? Icons.check_circle : Icons.cancel,
            color: isSuccess ? const Color(0xFF4CAF50) : const Color(0xFFF44336),
            size: 28,
          ),
        ),
        title: Text(
          isSuccess ? '签到成功' : '签到失败',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: isSuccess ? const Color(0xFF2E7D32) : const Color(0xFFC62828),
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              _formatDateTime(checkinTime),
              style: const TextStyle(fontSize: 12, color: Color(0xFF999999)),
            ),
            if (isSuccess && confidence != null)
              Text(
                '置信度: ${(confidence * 100).toStringAsFixed(1)}%',
                style: const TextStyle(fontSize: 12, color: Color(0xFF66BB6A)),
              ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right, color: Color(0xFFCCCCCC)),
      ),
    );
  }

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso);
      return '${dt.month}/${dt.day}';
    } catch (_) {
      return '';
    }
  }

  String _formatDateTime(String iso) {
    try {
      final dt = DateTime.parse(iso);
      final localDt = dt.toLocal();
      return '${localDt.year}-${localDt.month.toString().padLeft(2, '0')}-${localDt.day.toString().padLeft(2, '0')} '
          '${localDt.hour.toString().padLeft(2, '0')}:${localDt.minute.toString().padLeft(2, '0')}:${localDt.second.toString().padLeft(2, '0')}';
    } catch (_) {
      return iso;
    }
  }
}

/// 照片详情页（全屏预览）
class _PhotoDetailPage extends StatelessWidget {
  final int photoId;
  final ApiService apiService;

  const _PhotoDetailPage({required this.photoId, required this.apiService});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Center(
        child: FutureBuilder<Uint8List?>(
          future: _fetchPhoto(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CircularProgressIndicator(color: Colors.white);
            }
            if (snapshot.hasData && snapshot.data != null) {
              return InteractiveViewer(
                child: Image.memory(snapshot.data!),
              );
            }
            return const Text(
              '无法加载照片',
              style: TextStyle(color: Colors.white70),
            );
          },
        ),
      ),
    );
  }

  Future<Uint8List?> _fetchPhoto() async {
    try {
      final token = await apiService.getToken();
      final url = Uri.parse(apiService.photoFileUrl(photoId));
      final response = await http.get(url, headers: {
        if (token != null) 'Authorization': 'Bearer $token',
      });
      if (response.statusCode == 200) {
        return response.bodyBytes;
      }
    } catch (_) {}
    return null;
  }
}
