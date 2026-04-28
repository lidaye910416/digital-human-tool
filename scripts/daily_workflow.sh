#!/bin/bash
# TechEcho Pro - 每日自动新闻收集与TTS生成
# 运行时间: 每天早上 7:00

cd /Users/jasonlee/digital-human-tool
export PYTHONPATH=/Users/jasonlee/digital-human-tool

# 日志文件
LOG_FILE="/Users/jasonlee/digital-human-tool/logs/workflow_$(date +%Y%m%d).log"
mkdir -p /Users/jasonlee/digital-human-tool/logs

echo "=========================================" >> $LOG_FILE
echo "开始执行: $(date)" >> $LOG_FILE
echo "=========================================" >> $LOG_FILE

# 执行工作流
python3 scripts/news_workflow.py --min-quality 50 >> $LOG_FILE 2>&1

echo "执行完成: $(date)" >> $LOG_FILE
echo "" >> $LOG_FILE
