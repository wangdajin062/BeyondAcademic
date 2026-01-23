package backend;

import common.User;
import java.util.HashMap;
import java.util.Map;

/**
 * 后端用户管理类 - 处理数据存储和业务逻辑
 */
public class UserManager {
    private Map<String, User> users;

    public UserManager() {
        users = new HashMap<>();
        // 初始化测试数据
        users.put("admin", new User("admin", "admin123", "admin@example.com"));
        System.out.println("[UserManager] 已加载默认测试用户");
    }

    /**
     * 注册新用户
     */
    public synchronized boolean registerUser(String username, String password, String email) {
        if (users.containsKey(username)) {
            return false;
        }
        users.put(username, new User(username, password, email));
        System.out.println("[UserManager] 用户注册成功: " + username);
        return true;
    }

    /**
     * 注册新用户（Web API 版本）
     */
    public synchronized boolean register(User user) {
        if (users.containsKey(user.getUsername())) {
            return false;
        }
        users.put(user.getUsername(), user);
        System.out.println("[UserManager] 用户注册成功: " + user.getUsername());
        return true;
    }

    /**
     * 用户登录（Web API 版本）
     */
    public synchronized User login(String username, String password) {
        User user = users.get(username);
        if (user != null && user.getPassword().equals(password)) {
            System.out.println("[UserManager] 用户登录成功: " + username);
            return user;
        }
        System.out.println("[UserManager] 用户登录失败: " + username);
        return null;
    }

    /**
     * 验证用户凭证
     */
    public synchronized boolean verifyUser(String username, String password) {
        User user = users.get(username);
        boolean result = user != null && user.getPassword().equals(password);
        System.out.println("[UserManager] 用户登录验证: " + username + " -> " + (result ? "成功" : "失败"));
        return result;
    }

    /**
     * 检查用户是否存在
     */
    public synchronized boolean userExists(String username) {
        return users.containsKey(username);
    }

    /**
     * 获取用户信息
     */
    public synchronized User getUser(String username) {
        return users.get(username);
    }

    /**
     * 获取用户总数
     */
    public synchronized int getUserCount() {
        return users.size();
    }

    /**
     * 显示所有用户（仅用于调试）
     */
    public synchronized void printAllUsers() {
        System.out.println("\n========== 用户列表 ==========");
        System.out.println("总用户数: " + users.size());
        for (User user : users.values()) {
            System.out.println("  - " + user.getUsername() + " (" + user.getEmail() + ")");
        }
        System.out.println("==============================\n");
    }
}
