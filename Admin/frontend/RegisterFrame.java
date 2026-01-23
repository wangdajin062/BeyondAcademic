package frontend;

import common.ApiResponse;
import javax.swing.*;
import java.awt.*;

/**
 * 前端注册界面 - 客户端GUI
 */
public class RegisterFrame extends JFrame {
    private JTextField usernameField;
    private JPasswordField passwordField;
    private JPasswordField confirmPasswordField;
    private JTextField emailField;
    private JButton registerButton;
    private JButton cancelButton;
    private JLabel messageLabel;
    private ServerClient serverClient;
    private LoginFrame parentFrame;

    public RegisterFrame(ServerClient serverClient, LoginFrame parentFrame) {
        this.serverClient = serverClient;
        this.parentFrame = parentFrame;
        initializeUI();
    }

    private void initializeUI() {
        // 设置窗口属性
        setTitle("用户注册");
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        setSize(450, 400);
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
        JLabel titleLabel = new JLabel("创建新账户");
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

        // 邮箱标签和输入框
        JLabel emailLabel = new JLabel("邮箱:");
        emailLabel.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 0;
        gbc.gridy = 2;
        mainPanel.add(emailLabel, gbc);

        emailField = new JTextField(20);
        emailField.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 1;
        mainPanel.add(emailField, gbc);

        // 密码标签和输入框
        JLabel passwordLabel = new JLabel("密码:");
        passwordLabel.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 0;
        gbc.gridy = 3;
        mainPanel.add(passwordLabel, gbc);

        passwordField = new JPasswordField(20);
        passwordField.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 1;
        mainPanel.add(passwordField, gbc);

        // 确认密码标签和输入框
        JLabel confirmPasswordLabel = new JLabel("确认密码:");
        confirmPasswordLabel.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 0;
        gbc.gridy = 4;
        mainPanel.add(confirmPasswordLabel, gbc);

        confirmPasswordField = new JPasswordField(20);
        confirmPasswordField.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        gbc.gridx = 1;
        mainPanel.add(confirmPasswordField, gbc);

        // 消息标签
        messageLabel = new JLabel("");
        messageLabel.setFont(new Font("微软雅黑", Font.PLAIN, 12));
        messageLabel.setForeground(Color.RED);
        gbc.gridx = 0;
        gbc.gridy = 5;
        gbc.gridwidth = 2;
        mainPanel.add(messageLabel, gbc);

        // 按钮面板
        JPanel buttonPanel = new JPanel();
        buttonPanel.setBackground(new Color(240, 240, 240));

        registerButton = new JButton("注册");
        registerButton.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        registerButton.setPreferredSize(new Dimension(100, 40));
        registerButton.addActionListener(e -> handleRegister());
        buttonPanel.add(registerButton);

        cancelButton = new JButton("取消");
        cancelButton.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        cancelButton.setPreferredSize(new Dimension(100, 40));
        cancelButton.addActionListener(e -> dispose());
        buttonPanel.add(cancelButton);

        gbc.gridx = 0;
        gbc.gridy = 6;
        gbc.gridwidth = 2;
        mainPanel.add(buttonPanel, gbc);

        setContentPane(mainPanel);
        setVisible(true);
    }

    private void handleRegister() {
        String username = usernameField.getText().trim();
        String email = emailField.getText().trim();
        String password = new String(passwordField.getPassword());
        String confirmPassword = new String(confirmPasswordField.getPassword());

        // 本地验证
        if (username.isEmpty() || email.isEmpty() || password.isEmpty() || confirmPassword.isEmpty()) {
            messageLabel.setText("所有字段都不能为空!");
            messageLabel.setForeground(Color.RED);
            return;
        }

        if (username.length() < 3) {
            messageLabel.setText("用户名至少需要3个字符!");
            messageLabel.setForeground(Color.RED);
            return;
        }

        if (password.length() < 6) {
            messageLabel.setText("密码至少需要6个字符!");
            messageLabel.setForeground(Color.RED);
            return;
        }

        if (!password.equals(confirmPassword)) {
            messageLabel.setText("两次输入的密码不一致!");
            messageLabel.setForeground(Color.RED);
            confirmPasswordField.setText("");
            return;
        }

        if (!isValidEmail(email)) {
            messageLabel.setText("邮箱格式不正确!");
            messageLabel.setForeground(Color.RED);
            return;
        }

        registerButton.setEnabled(false);
        messageLabel.setText("正在连接服务器...");
        messageLabel.setForeground(new Color(0, 102, 204));

        // 在后台线程中执行网络请求
        new Thread(() -> {
            ApiResponse response = serverClient.register(username, password, email);
            
            SwingUtilities.invokeLater(() -> {
                registerButton.setEnabled(true);
                if (response.isSuccess()) {
                    messageLabel.setText("注册成功!");
                    messageLabel.setForeground(new Color(0, 128, 0));
                    JOptionPane.showMessageDialog(RegisterFrame.this, 
                        "注册成功!请返回登录窗口进行登录。", "成功", JOptionPane.INFORMATION_MESSAGE);
                    clearFields();
                    dispose();
                } else {
                    messageLabel.setText(response.getMessage());
                    messageLabel.setForeground(Color.RED);
                }
            });
        }).start();
    }

    private boolean isValidEmail(String email) {
        String emailRegex = "^[A-Za-z0-9+_.-]+@(.+)$";
        return email.matches(emailRegex);
    }

    private void clearFields() {
        usernameField.setText("");
        emailField.setText("");
        passwordField.setText("");
        confirmPasswordField.setText("");
        messageLabel.setText("");
    }
}
