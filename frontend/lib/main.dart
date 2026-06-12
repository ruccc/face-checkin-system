import 'package:flutter/material.dart';
import 'pages/login_page.dart';

void main() {
  runApp(const FaceCheckinApp());
}

class FaceCheckinApp extends StatelessWidget {
  const FaceCheckinApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '人脸签到系统',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF4A90D9),
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const LoginPage(),
    );
  }
}
