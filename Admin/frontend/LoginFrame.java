package frontend;

import common.ApiResponse;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

/**
 * 前端登录界面 - 客户端GUI
 */
public class LoginFrame extends JFrame {
    private JTextField usernameField;
    private JPasswordField passwordField;
    private JButton loginButton;
    private JButton registerButton;
    private JLabel messageLabel;
    private ServerClient serverClient;

    public LoginFrame(String serverHost, int serverPort) {
        this.serverClient = new ServerClient(serverHost, serverPort);
        initializeUI();
    }

    private void initializeUI() {
        // 设置窗口属性
        setTitle("登录系统");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(400, 300);
        setLocationRelativeTo(null);
        setResizable(false);

        // 创建主面板
        JPanel mainPanel = new JPanel();
        mainPanel.setLayout(new GridBagLayout());
        mainPanel.setBackground(new Color(240, 240, 240));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(10, 10, 10, 10);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        // 标题标签
        JLabel titleLabel = new JLabel("用户登录");
        titleLabel.setFont(new Font("微软雅黑", Font.BOLD, 24));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        mainPanel.add(titleLabel, gbc);

        // 用户名标签和输入框
        JLabel usernameLabel = new JLabel("用户名:");
        usernameLabel.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridwidth = 1;
        gbc.gridy = 1;
        gbc.gridx = 0;
        mainPanel.add(usernameLabel, gbc);

        usernameField = new JTextField(20);
        usernameField.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 1;
        mainPanel.add(usernameField, gbc);

        // 密码标签和输入框
        JLabel passwordLabel = new JLabel("密码:");
        passwordLabel.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 0;
        gbc.gridy = 2;
        mainPanel.add(passwordLabel, gbc);

        passwordField = new JPasswordField(20);
        passwordField.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 1;
        mainPanel.add(passwordField, gbc);

        // 消息标签
        messageLabel = new JLabel("");
        messageLabel.setFont(new Font("微软雅黑", Font.PLAIN, 12));
        messageLabel.setForeground(Color.RED);
        gbc.gridx = 0;
        gbc.gridy = 3;
        gbc.gridwidth = 2;
        mainPanel.add(messageLabel, gbc);

        // 按钮面板
        JPanel buttonPanel = new JPanel();
        buttonPanel.setBackground(new Color(240, 240, 240));

        loginButton = new JButton("登录");
        loginButton.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        loginButton.setPreferredSize(new Dimension(100, 40));
        loginButton.addActionListener(e -> handleLogin());
        buttonPanel.add(loginButton);

        registerButton = new JButton("注册新用户");
        registerButton.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        registerButton.setPreferredSize(new Dimension(100, 40));
        registerButton.addActionListener(e -> handleRegister());
        buttonPanel.add(registerButton);

        gbc.gridx = 0;
        gbc.gridy = 4;
        gbc.gridwidth = 2;
        mainPanel.add(buttonPanel, gbc);

        setContentPane(mainPanel);
        setVisible(true);
    }

    private void handleLogin() {
        String username = usernameField.getText().trim();
        String password = new String(passwordField.getPassword());

        if (username.isEmpty() || password.isEmpty()) {
            messageLabel.setText("用户名和密码不能为空!");
            messageLabel.setForeground(Color.RED);
            return;
        }

        loginButton.setEnabled(false);
        messageLabel.setText("正在连接服务器...");
        messageLabel.setForeground(new Color(0, 102, 204));

        // 在后台线程中执行网络请求
        new Thread(() -> {
            ApiResponse response = serverClient.login(username, password);
            
            SwingUtilities.invokeLater(() -> {
                loginButton.setEnabled(true);
                if (response.isSuccess()) {
                    messageLabel.setText("登录成功!");
                    messageLabel.setForeground(new Color(0, 128, 0));
                    JOptionPane.showMessageDialog(LoginFrame.this, 
                        "欢迎 " + username + "!", "登录成功", JOptionPane.INFORMATION_MESSAGE);
                    clearFields();
                } else {
                    messageLabel.setText(response.getMessage());
                    messageLabel.setForeground(Color.RED);
                    passwordField.setText("");
                }
            });
        }).start();
    }

    private void handleRegister() {
        new RegisterFrame(serverClient, this);
    }

    private void clearFields() {
        usernameField.setText("");
        passwordField.setText("");
        messageLabel.setText("");
    }
}
