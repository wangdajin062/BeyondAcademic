#!/bin/bash
# Web API 服务器启动脚本

echo "=========================================="
echo "  Java 登录系统 - Web API 服务器启动脚本"
echo "=========================================="

# 检查是否在项目根目录
if [ ! -d "Admin" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

cd Admin

# 检查Java是否安装
if ! command -v java &> /dev/null; then
    echo "错误: 未找到Java，请先安装Java"
    exit 1
fi

# 编译代码
echo ""
echo "正在编译代码..."
javac common/*.java
javac -cp . backend/*.java
javac -cp . webapi/*.java

if [ $? -ne 0 ]; then
    echo "编译失败"
    exit 1
fi

echo "编译成功"

# 获取端口参数
PORT=${1:-8080}

# 启动服务器
echo ""
echo "启动 Web API 服务器..."
echo "监听端口: $PORT"
echo "访问地址: http://localhost:$PORT"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

java -cp . webapi.WebApiServer $PORT
