#!/bin/bash
# Web API 测试脚本

echo "=========================================="
echo "  Web API 功能测试"
echo "=========================================="

API_URL="http://localhost:8080/api"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_api() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5

    echo ""
    echo -e "${YELLOW}[测试]${NC} $test_name"

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    echo "请求: $method $endpoint"
    echo "状态码: $http_code"
    echo "响应: $body"

    if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
        echo -e "${GREEN}✓ 测试通过${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ 测试失败${NC}"
        ((TESTS_FAILED++))
    fi
}

echo ""
echo "========== 开始测试 =========="

# 测试1: 检查服务器状态
test_api "服务器状态检查" "GET" "/status"

# 测试2: 正确的登录信息
test_api "正确的登录 (admin/admin123)" "POST" "/login" \
    '{"username":"admin","password":"admin123"}'

# 测试3: 错误的登录信息
test_api "错误的登录 (admin/wrong)" "POST" "/login" \
    '{"username":"admin","password":"wrong"}'

# 测试4: 注册新用户
TIMESTAMP=$(date +%s%N)
NEW_USER="testuser_$TIMESTAMP"
test_api "注册新用户" "POST" "/register" \
    "{\"username\":\"$NEW_USER\",\"password\":\"test123456\"}"

# 测试5: 使用新用户登录
test_api "新用户登录" "POST" "/login" \
    "{\"username\":\"$NEW_USER\",\"password\":\"test123456\"}"

# 测试6: 用户名重复注册
test_api "重复注册用户名" "POST" "/register" \
    "{\"username\":\"admin\",\"password\":\"admin123\"}"

# 打印总结
echo ""
echo "========== 测试总结 =========="
echo -e "${GREEN}通过: $TESTS_PASSED${NC}"
echo -e "${RED}失败: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ 部分测试失败${NC}"
    exit 1
fi
