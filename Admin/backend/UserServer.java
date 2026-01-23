package backend;

import common.User;
import common.ApiResponse;
import java.io.*;
import java.net.*;
import java.util.*;

/**
 * 用户管理后端服务器
 * 处理用户注册、登录等业务逻辑
 */
public class UserServer {
    private int port;
    private ServerSocket serverSocket;
    private UserManager userManager;
    private boolean running = false;

    public UserServer(int port) {
        this.port = port;
        this.userManager = new UserManager();
    }

    /**
     * 启动服务器
     */
    public void start() {
        try {
            serverSocket = new ServerSocket(port);
            running = true;
            System.out.println("========================================");
            System.out.println("用户管理后端服务器已启动");
            System.out.println("监听端口: " + port);
            System.out.println("========================================\n");

            while (running) {
                Socket clientSocket = serverSocket.accept();
                // 为每个客户端创建新线程处理请求
                new ClientHandler(clientSocket, userManager).start();
            }
        } catch (IOException e) {
            if (running) {
                System.err.println("服务器错误: " + e.getMessage());
            }
        }
    }

    /**
     * 停止服务器
     */
    public void stop() {
        running = false;
        try {
            if (serverSocket != null && !serverSocket.isClosed()) {
                serverSocket.close();
            }
            System.out.println("服务器已关闭");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /**
     * 客户端请求处理线程
     */
    private static class ClientHandler extends Thread {
        private Socket socket;
        private UserManager userManager;

        public ClientHandler(Socket socket, UserManager userManager) {
            this.socket = socket;
            this.userManager = userManager;
        }

        @Override
        public void run() {
            try {
                ObjectInputStream in = new ObjectInputStream(socket.getInputStream());
                ObjectOutputStream out = new ObjectOutputStream(socket.getOutputStream());

                // 读取请求
                String request = (String) in.readObject();
                System.out.println("[" + new Date() + "] 收到请求: " + request);

                ApiResponse response = handleRequest(request, in);
                out.writeObject(response);
                out.flush();

                in.close();
                out.close();
                socket.close();
            } catch (Exception e) {
                System.err.println("处理客户端请求时出错: " + e.getMessage());
            }
        }

        /**
         * 处理客户端请求
         */
        private ApiResponse handleRequest(String request, ObjectInputStream in) {
            try {
                String[] parts = request.split(":");
                String action = parts[0];

                switch (action) {
                    case "login":
                        return handleLogin(parts);
                    case "register":
                        return handleRegister(in);
                    case "exists":
                        return handleUserExists(parts);
                    case "getUser":
                        return handleGetUser(parts);
                    default:
                        return new ApiResponse(false, "未知请求: " + action);
                }
            } catch (Exception e) {
                return new ApiResponse(false, "请求处理错误: " + e.getMessage());
            }
        }

        /**
         * 处理登录请求
         */
        private ApiResponse handleLogin(String[] parts) {
            if (parts.length < 3) {
                return new ApiResponse(false, "请求格式错误");
            }
            String username = parts[1];
            String password = parts[2];

            if (userManager.verifyUser(username, password)) {
                User user = userManager.getUser(username);
                return new ApiResponse(true, "登录成功", user);
            } else {
                return new ApiResponse(false, "用户名或密码错误");
            }
        }

        /**
         * 处理注册请求
         */
        private ApiResponse handleRegister(ObjectInputStream in) throws Exception {
            User user = (User) in.readObject();
            
            // 验证输入
            if (user.getUsername() == null || user.getUsername().trim().isEmpty()) {
                return new ApiResponse(false, "用户名不能为空");
            }
            if (user.getUsername().length() < 3) {
                return new ApiResponse(false, "用户名至少需要3个字符");
            }
            if (user.getPassword() == null || user.getPassword().length() < 6) {
                return new ApiResponse(false, "密码至少需要6个字符");
            }
            if (!isValidEmail(user.getEmail())) {
                return new ApiResponse(false, "邮箱格式不正确");
            }
            if (userManager.userExists(user.getUsername())) {
                return new ApiResponse(false, "用户名已存在");
            }

            if (userManager.registerUser(user.getUsername(), user.getPassword(), user.getEmail())) {
                return new ApiResponse(true, "注册成功");
            } else {
                return new ApiResponse(false, "注册失败");
            }
        }

        /**
         * 处理用户存在性检查
         */
        private ApiResponse handleUserExists(String[] parts) {
            if (parts.length < 2) {
                return new ApiResponse(false, "请求格式错误");
            }
            String username = parts[1];
            boolean exists = userManager.userExists(username);
            return new ApiResponse(true, exists ? "用户存在" : "用户不存在", exists);
        }

        /**
         * 处理获取用户信息
         */
        private ApiResponse handleGetUser(String[] parts) {
            if (parts.length < 2) {
                return new ApiResponse(false, "请求格式错误");
            }
            String username = parts[1];
            User user = userManager.getUser(username);
            if (user != null) {
                return new ApiResponse(true, "获取成功", user);
            } else {
                return new ApiResponse(false, "用户不存在");
            }
        }

        /**
         * 验证邮箱格式
         */
        private boolean isValidEmail(String email) {
            String emailRegex = "^[A-Za-z0-9+_.-]+@(.+)$";
            return email.matches(emailRegex);
        }
    }

    public static void main(String[] args) {
        int port = 9999;
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.out.println("端口号格式错误，使用默认端口: " + port);
            }
        }

        UserServer server = new UserServer(port);
        
        // 添加关闭钩子
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\n正在关闭服务器...");
            server.stop();
        }));

        server.start();
    }
}
