package integration;

import backend.UserServer;
import frontend.ServerClient;
import common.ApiResponse;
import java.util.Scanner;

/**
 * 集成测试 - 测试前后端通信
 */
public class IntegrationTest {
    public static void main(String[] args) throws Exception {
        // 启动后端服务器
        System.out.println("========================================");
        System.out.println("     前后端集成测试");
        System.out.println("========================================\n");

        UserServer server = new UserServer(9999);
        Thread serverThread = new Thread(() -> server.start());
        serverThread.setDaemon(true);
        serverThread.start();

        // 等待服务器启动
        Thread.sleep(2000);

        // 创建客户端
        frontend.ServerClient client = new ServerClient("localhost", 9999);

        System.out.println("\n========== 开始测试 ==========\n");

        // 测试1: 登录默认用户
        System.out.println("[测试1] 登录默认用户 (admin/admin123)");
        ApiResponse response = client.login("admin", "admin123");
        System.out.println("结果: " + (response.isSuccess() ? "✓ 成功" : "✗ 失败"));
        System.out.println("消息: " + response.getMessage() + "\n");

        // 测试2: 尝试用错误密码登录
        System.out.println("[测试2] 错误密码登录测试");
        response = client.login("admin", "wrong");
        System.out.println("结果: " + (response.isSuccess() ? "✗ 应失败但成功" : "✓ 正确拒绝"));
        System.out.println("消息: " + response.getMessage() + "\n");

        // 测试3: 注册新用户
        System.out.println("[测试3] 注册新用户 (testuser)");
        response = client.register("testuser", "password123", "test@example.com");
        System.out.println("结果: " + (response.isSuccess() ? "✓ 成功" : "✗ 失败"));
        System.out.println("消息: " + response.getMessage() + "\n");

        // 测试4: 用新注册用户登录
        System.out.println("[测试4] 新用户登录测试");
        response = client.login("testuser", "password123");
        System.out.println("结果: " + (response.isSuccess() ? "✓ 成功" : "✗ 失败"));
        System.out.println("消息: " + response.getMessage() + "\n");

        // 测试5: 检查用户存在性
        System.out.println("[测试5] 用户存在性检查");
        response = client.checkUserExists("testuser");
        System.out.println("结果: " + (response.isSuccess() ? "✓ 检查成功" : "✗ 失败"));
        System.out.println("消息: " + response.getMessage());
        System.out.println("数据: " + response.getData() + "\n");

        // 测试6: 尝试重复注册
        System.out.println("[测试6] 重复注册测试");
        response = client.register("testuser", "different", "different@example.com");
        System.out.println("结果: " + (response.isSuccess() ? "✗ 应失败但成功" : "✓ 正确拒绝"));
        System.out.println("消息: " + response.getMessage() + "\n");

        // 测试7: 获取用户信息
        System.out.println("[测试7] 获取用户信息");
        response = client.getUser("testuser");
        System.out.println("结果: " + (response.isSuccess() ? "✓ 成功" : "✗ 失败"));
        System.out.println("消息: " + response.getMessage());
        if (response.getData() != null) {
            System.out.println("用户信息: " + response.getData() + "\n");
        }

        System.out.println("========================================");
        System.out.println("            测试完成");
        System.out.println("========================================");
        System.out.println("✓ 前后端通信测试成功！");
        System.out.println("\n可以现在运行客户端: java -cp . frontend.ClientMain");
        
        server.stop();
    }
}
