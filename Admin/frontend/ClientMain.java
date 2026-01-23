package frontend;

/**
 * 前端客户端主程序入口
 */
public class ClientMain {
    public static void main(String[] args) {
        // 获取服务器地址和端口
        final String serverHost = args.length >= 1 ? args[0] : "localhost";
        final int serverPort;
        
        if (args.length >= 2) {
            try {
                serverPort = Integer.parseInt(args[1]);
            } catch (NumberFormatException e) {
                System.out.println("端口号格式错误，使用默认端口: 9999");
                main(new String[]{serverHost});
                return;
            }
        } else {
            serverPort = 9999;
        }

        System.out.println("========================================");
        System.out.println("      客户端正在启动...");
        System.out.println("服务器地址: " + serverHost);
        System.out.println("服务器端口: " + serverPort);
        System.out.println("========================================\n");

        // 使用Swing的线程安全方式启动GUI
        javax.swing.SwingUtilities.invokeLater(() -> {
            new LoginFrame(serverHost, serverPort);
        });
    }
}
