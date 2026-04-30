#!/bin/bash
# TechEcho 项目初始化脚本
# 安装依赖并修复 Taro 兼容性问题

set -e

echo "=== TechEcho 项目初始化 ==="
echo ""

# 1. 清理旧依赖
echo "1/3 清理旧依赖..."
rm -rf node_modules app/node_modules yarn.lock package-lock.json

# 2. 安装依赖
echo "2/3 安装依赖 (yarn install)..."
yarn install

# 3. 修复 Taro Kernel.js
echo "3/3 修复 Taro 兼容性问题..."
bash scripts/fix-taro-kernel.sh

echo ""
echo "=== 初始化完成 ==="
echo ""
echo "构建微信小程序："
echo "  cd app && yarn taro build --type weapp"
echo ""
echo "构建 H5："
echo "  cd app && yarn taro build --type h5"
