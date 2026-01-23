package frontend;

import common.User;
import common.ApiResponse;
import java.io.*;
import java.net.Socket;

/**
 * 客户端通信类 - 与后端服务器通信
 */
public class ServerClient {
    private String host;
    private int port;
    private static final int TIMEOUT = 5000; // 5秒超时

    public ServerClient(String host, int port) {
        this.host = host;
        this.port = port;
    }

    /**
     * 用户登录
     */
    public ApiResponse login(String username, String password) {
        try {
            Socket socket = new Socket(host, port);
            socket.setSoTimeout(TIMEOUT);

            ObjectOutputStream out = new ObjectOutputStream(socket.getOutputStream());
            ObjectInputStream in = new ObjectInputStream(socket.getInputStream());

            // 发送登录请求
            String request = "login:" + username + ":" + password;
            out.writeObject(request);
            out.flush();

            // 接收响应
            ApiResponse response = (ApiResponse) in.readObject();

            in.close();
            out.close();
            socket.close();

            return response;
        } catch (Exception e) {
            return new ApiResponse(false, "连接服务器失败: " + e.getMessage());
        }
    }

    /**
     * 用户注册
     */
    public ApiResponse register(String username, String password, String email) {
        try {
            Socket socket = new Socket(host, port);
            socket.setSoTimeout(TIMEOUT);

            ObjectOutputStream out = new ObjectOutputStream(socket.getOutputStream());
            ObjectInputStream in = new ObjectInputStream(socket.getInputStream());

            // 发送注册请求
            String request = "register";
            out.writeObject(request);
            out.flush();

            // 发送用户对象
            User user = new User(username, password, email);
            out.writeObject(user);
            out.flush();

            // 接收响应
            ApiResponse response = (ApiResponse) in.readObject();

            in.close();
            out.close();
            socket.close();

            return response;
        } catch (Exception e) {
            return new ApiResponse(false, "连接服务器失败: " + e.getMessage());
        }
    }

    /**
     * 检查用户是否存在
     */
    public ApiResponse checkUserExists(String username) {
        try {
            Socket socket = new Socket(host, port);
            socket.setSoTimeout(TIMEOUT);

            ObjectOutputStream out = new ObjectOutputStream(socket.getOutputStream());
            ObjectInputStream in = new ObjectInputStream(socket.getInputStream());

            // 发送查询请求
            String request = "exists:" + username;
            out.writeObject(request);
            out.flush();

            // 接收响应
            ApiResponse response = (ApiResponse) in.readObject();

            in.close();
            out.close();
            socket.close();

            return response;
        } catch (Exception e) {
            return new ApiResponse(false, "连接服务器失败: " + e.getMessage());
        }
    }

    /**
     * 获取用户信息
     */
    public ApiResponse getUser(String username) {
        try {
            Socket socket = new Socket(host, port);
            socket.setSoTimeout(TIMEOUT);

            ObjectOutputStream out = new ObjectOutputStream(socket.getOutputStream());
            ObjectInputStream in = new ObjectInputStream(socket.getInputStream());

            // 发送获取用户请求
            String request = "getUser:" + username;
            out.writeObject(request);
            out.flush();

            // 接收响应
            ApiResponse response = (ApiResponse) in.readObject();

            in.close();
            out.close();
            socket.close();

            return response;
        } catch (Exception e) {
            return new ApiResponse(false, "连接服务器失败: " + e.getMessage());
        }
    }
}
