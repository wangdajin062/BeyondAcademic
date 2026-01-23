#!/bin/bash
# 前端客户端启动脚本

echo "=========================================="
echo "  Java 注册登录系统 - 前端客户端启动脚本"
echo "=========================================="

# 检查是否在项目根目录
if [ ! -d "frontend" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Java是否安装
if ! command -v java &> /dev/null; then
    echo "错误: 未找到Java，请先安装Java"
    exit 1
fi

# 编译代码
echo ""
echo "正在编译代码..."
javac common/*.java
javac -cp . frontend/*.java

if [ $? -ne 0 ]; then
    echo "编译失败"
    exit 1
fi

echo "编译成功"

# 获取服务器地址和端口参数
HOST=${1:-localhost}
PORT=${2:-9999}

# 启动客户端
echo ""
echo "启动客户端..."
echo "服务器地址: $HOST"
echo "服务器端口: $PORT"
echo ""

java -cp . frontend.ClientMain $HOST $PORT
