#!/bin/bash
# 修复 Taro 3.6.40 的 Kernel.js 兼容性问题
# 问题：this.initialConfig.sourceRoot/outputRoot 可能为 undefined 导致 path.join 报错

echo "修复 Taro Kernel.js..."

FILE="node_modules/@tarojs/service/dist/Kernel.js"

if [ ! -f "$FILE" ]; then
    echo "错误：找不到 $FILE"
    echo "请确保在项目根目录执行此脚本"
    exit 1
fi

# 检查是否已经修复
if grep -q "helper.SOURCE_DIR" "$FILE"; then
    echo "已经修复，跳过"
    exit 0
fi

# 备份原文件
cp "$FILE" "$FILE.bak"
echo "已备份 $FILE -> $FILE.bak"

# 修复 sourceRoot
sed -i '' 's/this\.initialConfig\.sourceRoot),/this.initialConfig.sourceRoot || helper.SOURCE_DIR),/g' "$FILE"

# 修复 outputRoot
sed -i '' 's/this\.initialConfig\.outputRoot)/this.initialConfig.outputRoot || helper.OUTPUT_DIR)/g' "$FILE"

# 验证修复
if grep -q "helper.SOURCE_DIR" "$FILE"; then
    echo "✅ 修复成功！"
else
    echo "❌ 修复失败，恢复备份..."
    mv "$FILE.bak" "$FILE"
    exit 1
fi
