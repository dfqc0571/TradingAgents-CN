#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行每日报告生成任务的脚本
用于测试和手动执行报告生成
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# 自动加载.env文件
env_file = os.path.join(project_root, '.env')
if os.path.exists(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print("✅ .env文件加载成功")

from tradingagents.scheduled_tasks.daily_report import manual_generate_report

if __name__ == "__main__":
    print("开始执行每日交易决策报告任务...")
    result = manual_generate_report()
    print(f"任务执行结果: {result}")