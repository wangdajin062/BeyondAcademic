package webapi;

import common.User;
import common.ApiResponse;
import backend.UserManager;
import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Web API 服务器 - 支持 HTTP 请求
 * 为Web前端提供 REST API 接口
 */
public class WebApiServer {
    private int port;
    private HttpServer httpServer;
    private UserManager userManager;

    public WebApiServer(int port) {
        this.port = port;
        this.userManager = new UserManager();
    }

    /**
     * 启动Web API服务器
     */
    public void start() {
        try {
            httpServer = HttpServer.create(new InetSocketAddress(port), 0);
            
            // 注册路由
            httpServer.createContext("/api/login", new LoginHandler(userManager));
            httpServer.createContext("/api/register", new RegisterHandler(userManager));
            httpServer.createContext("/api/status", new StatusHandler());
            httpServer.createContext("/", new StaticFileHandler());
            
            httpServer.setExecutor(null);
            httpServer.start();
            
            System.out.println("========================================");
            System.out.println("Web API 服务器已启动");
            System.out.println("监听端口: " + port);
            System.out.println("访问地址: http://localhost:" + port);
            System.out.println("========================================\n");
        } catch (IOException e) {
            System.err.println("启动Web API服务器失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 停止服务器
     */
    public void stop() {
        if (httpServer != null) {
            httpServer.stop(0);
            System.out.println("Web API 服务器已关闭");
        }
    }

    /**
     * 登录处理器
     */
    private static class LoginHandler implements HttpHandler {
        private UserManager userManager;

        public LoginHandler(UserManager userManager) {
            this.userManager = userManager;
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if ("POST".equals(exchange.getRequestMethod())) {
                handleCORS(exchange);
                
                try {
                    // 读取请求体
                    InputStream is = exchange.getRequestBody();
                    String requestBody = new String(is.readAllBytes(), StandardCharsets.UTF_8);
                    is.close();

                    // 解析JSON
                    Map<String, String> params = parseJson(requestBody);
                    String username = params.getOrDefault("username", "");
                    String password = params.getOrDefault("password", "");

                    System.out.println("[登录请求] 用户名: " + username);

                    // 验证用户
                    User user = userManager.login(username, password);
                    ApiResponse response;

                    if (user != null) {
                        response = new ApiResponse(true, "登录成功", user);
                        System.out.println("[登录成功] 用户: " + username);
                    } else {
                        response = new ApiResponse(false, "用户名或密码错误");
                        System.out.println("[登录失败] 用户名或密码错误: " + username);
                    }

                    sendJsonResponse(exchange, response, 200);
                } catch (Exception e) {
                    System.err.println("处理登录请求出错: " + e.getMessage());
                    ApiResponse response = new ApiResponse(false, "服务器错误");
                    sendJsonResponse(exchange, response, 500);
                }
            } else {
                exchange.sendResponseHeaders(405, 0);
                exchange.close();
            }
        }
    }

    /**
     * 注册处理器
     */
    private static class RegisterHandler implements HttpHandler {
        private UserManager userManager;

        public RegisterHandler(UserManager userManager) {
            this.userManager = userManager;
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if ("POST".equals(exchange.getRequestMethod())) {
                handleCORS(exchange);
                
                try {
                    // 读取请求体
                    InputStream is = exchange.getRequestBody();
                    String requestBody = new String(is.readAllBytes(), StandardCharsets.UTF_8);
                    is.close();

                    // 解析JSON
                    Map<String, String> params = parseJson(requestBody);
                    String username = params.getOrDefault("username", "");
                    String password = params.getOrDefault("password", "");

                    System.out.println("[注册请求] 用户名: " + username);

                    // 检查用户名是否已存在
                    if (userManager.userExists(username)) {
                        ApiResponse response = new ApiResponse(false, "用户名已存在");
                        System.out.println("[注册失败] 用户名已存在: " + username);
                        sendJsonResponse(exchange, response, 400);
                        return;
                    }

                    // 创建新用户
                    User newUser = new User(username, password);
                    boolean success = userManager.register(newUser);

                    ApiResponse response;
                    if (success) {
                        response = new ApiResponse(true, "注册成功", newUser);
                        System.out.println("[注册成功] 用户: " + username);
                        sendJsonResponse(exchange, response, 201);
                    } else {
                        response = new ApiResponse(false, "注册失败");
                        System.out.println("[注册失败] 数据库错误: " + username);
                        sendJsonResponse(exchange, response, 500);
                    }
                } catch (Exception e) {
                    System.err.println("处理注册请求出错: " + e.getMessage());
                    ApiResponse response = new ApiResponse(false, "服务器错误");
                    sendJsonResponse(exchange, response, 500);
                }
            } else {
                exchange.sendResponseHeaders(405, 0);
                exchange.close();
            }
        }
    }

    /**
     * 状态检查处理器
     */
    private static class StatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            handleCORS(exchange);
            
            Map<String, Object> status = new HashMap<>();
            status.put("success", true);
            status.put("message", "服务器正常运行");
            status.put("timestamp", System.currentTimeMillis());
            status.put("version", "1.0.0");

            sendJsonResponse(exchange, status, 200);
        }
    }

    /**
     * 静态文件处理器 - 提供HTML页面
     */
    private static class StaticFileHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            handleCORS(exchange);
            
            String path = exchange.getRequestURI().getPath();
            
            if (path.equals("/") || path.equals("/index.html")) {
                try {
                    // 尝试从多个可能的位置查找 HTML 文件
                    String[] possiblePaths = {
                        "web/index.html",
                        "../web/index.html",
                        "../../web/index.html",
                        "index.html"
                    };
                    
                    File file = null;
                    for (String possiblePath : possiblePaths) {
                        File f = new File(possiblePath);
                        if (f.exists()) {
                            file = f;
                            break;
                        }
                    }
                    
                    if (file != null && file.exists()) {
                        byte[] bytes = java.nio.file.Files.readAllBytes(file.toPath());
                        exchange.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
                        exchange.sendResponseHeaders(200, bytes.length);
                        exchange.getResponseBody().write(bytes);
                        exchange.close();
                    } else {
                        sendTextResponse(exchange, "404 Not Found - HTML 文件不存在，请检查 web/index.html 是否存在", 404);
                    }
                } catch (Exception e) {
                    sendTextResponse(exchange, "500 Internal Server Error: " + e.getMessage(), 500);
                }
            } else {
                sendTextResponse(exchange, "404 Not Found", 404);
            }
        }
    }

    /**
     * 处理CORS跨域请求
     */
    private static void handleCORS(HttpExchange exchange) {
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().add("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        exchange.getResponseHeaders().add("Access-Control-Allow-Headers", "Content-Type");
    }

    /**
     * 发送JSON响应
     */
    private static void sendJsonResponse(HttpExchange exchange, Object data, int statusCode) throws IOException {
        String json = convertToJson(data);
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(statusCode, bytes.length);
        exchange.getResponseBody().write(bytes);
        exchange.close();
    }

    /**
     * 发送文本响应
     */
    private static void sendTextResponse(HttpExchange exchange, String text, int statusCode) throws IOException {
        byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
        exchange.sendResponseHeaders(statusCode, bytes.length);
        exchange.getResponseBody().write(bytes);
        exchange.close();
    }

    /**
     * 简单的JSON解析（不使用外部库）
     */
    private static Map<String, String> parseJson(String json) {
        Map<String, String> result = new HashMap<>();
        // 移除首尾的大括号
        json = json.trim();
        if (json.startsWith("{")) json = json.substring(1);
        if (json.endsWith("}")) json = json.substring(0, json.length() - 1);

        // 分割键值对
        String[] pairs = json.split(",");
        for (String pair : pairs) {
            String[] kv = pair.split(":");
            if (kv.length == 2) {
                String key = kv[0].trim().replaceAll("\"", "");
                String value = kv[1].trim().replaceAll("\"", "");
                result.put(key, value);
            }
        }
        return result;
    }

    /**
     * 将对象转换为JSON字符串（简单实现）
     */
    private static String convertToJson(Object obj) {
        if (obj instanceof ApiResponse) {
            ApiResponse response = (ApiResponse) obj;
            return String.format("{\"success\":%b,\"message\":\"%s\",\"data\":null}",
                    response.isSuccess(),
                    escapeJson(response.getMessage()));
        } else if (obj instanceof Map) {
            Map<?, ?> map = (Map<?, ?>) obj;
            StringBuilder sb = new StringBuilder("{");
            int i = 0;
            for (Map.Entry<?, ?> entry : map.entrySet()) {
                if (i > 0) sb.append(",");
                sb.append("\"").append(entry.getKey()).append("\":");
                if (entry.getValue() instanceof String) {
                    sb.append("\"").append(escapeJson(entry.getValue().toString())).append("\"");
                } else {
                    sb.append(entry.getValue());
                }
                i++;
            }
            sb.append("}");
            return sb.toString();
        }
        return "{}";
    }

    /**
     * 转义JSON中的特殊字符
     */
    private static String escapeJson(String str) {
        return str.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    public static void main(String[] args) {
        int port = 8080;
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("无效的端口号，使用默认端口 8080");
            }
        }

        WebApiServer server = new WebApiServer(port);
        server.start();

        // 优雅关闭
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\n关闭Web API服务器...");
            server.stop();
        }));
    }
}
