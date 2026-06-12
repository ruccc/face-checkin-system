import 'package:flutter_test/flutter_test.dart';

import 'package:face_checkin/main.dart';

void main() {
  testWidgets('App should display login page', (WidgetTester tester) async {
    await tester.pumpWidget(const FaceCheckinApp());

    // 验证登录页面显示
    expect(find.text('人脸签到系统'), findsOneWidget);
    expect(find.text('Face Checkin System'), findsOneWidget);
    expect(find.text('登  录'), findsOneWidget);
    expect(find.text('立即注册'), findsOneWidget);
  });

  testWidgets('Login page should navigate to register page', (WidgetTester tester) async {
    await tester.pumpWidget(const FaceCheckinApp());

    // 点击"立即注册"
    await tester.tap(find.text('立即注册'));
    await tester.pumpAndSettle();

    // 验证进入注册页面
    expect(find.text('用户注册'), findsOneWidget);
    expect(find.text('创建新账户'), findsOneWidget);
    expect(find.text('注  册'), findsOneWidget);
  });
}
