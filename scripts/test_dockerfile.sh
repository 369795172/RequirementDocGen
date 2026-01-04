#!/bin/bash
# Quick test script for Dockerfile
# This script helps verify the Dockerfile works correctly

set -e

echo "=========================================="
echo "Dockerfile 测试脚本"
echo "=========================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装或未运行"
    echo "   请先安装 Docker 并启动 Docker daemon"
    exit 1
fi

echo "✅ Docker 可用"
echo ""

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon 未运行"
    echo "   请启动 Docker Desktop 或 Docker daemon"
    exit 1
fi

echo "✅ Docker daemon 运行中"
echo ""

# Build the image
# Change to project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📦 构建 Docker 镜像..."
cd "$PROJECT_ROOT"
docker build -t requirement-docgen-test . || {
    echo "❌ 构建失败"
    exit 1
}

echo "✅ 镜像构建成功"
echo ""

# Check if AI_BUILDER_TOKEN is set
if [ -z "$AI_BUILDER_TOKEN" ]; then
    echo "⚠️  警告: AI_BUILDER_TOKEN 未设置"
    echo "   使用测试 token（可能无法正常工作）"
    export AI_BUILDER_TOKEN="test-token"
fi

# Run the container
echo "🚀 启动容器..."
echo "   访问 http://localhost:8000 测试应用"
echo "   按 Ctrl+C 停止容器"
echo ""

docker run --rm -p 8000:8000 \
    -e PORT=8000 \
    -e AI_BUILDER_TOKEN="${AI_BUILDER_TOKEN}" \
    requirement-docgen-test

