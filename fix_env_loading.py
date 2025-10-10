#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复环境变量加载问题的脚本
"""

import os
import sys

def load_env_file():
    """加载.env文件中的环境变量"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(project_root, '.env')
    
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 只有当环境变量尚未设置时才设置它
                    if key not in os.environ:
                        os.environ[key] = value.strip('"').strip("'")
        print("✅ .env文件加载成功")
        return True
    else:
        print("⚠️ .env文件未找到")
        return False

def test_default_stocks():
    """测试DEFAULT_STOCKS环境变量"""
    # 加载环境变量
    load_env_file()
    
    # 获取默认股票列表
    default_stocks = os.getenv('DEFAULT_STOCKS', '000001,000002,600000,600036').split(',')
    print(f"当前默认股票列表: {default_stocks}")
    
    # 测试定时任务中的逻辑
    from tradingagents.scheduled_tasks.daily_report import DEFAULT_STOCKS
    print(f"定时任务中使用的股票列表: {DEFAULT_STOCKS}")

if __name__ == "__main__":
    test_default_stocks()