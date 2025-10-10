#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接性测试脚本
用于测试各个API接口是否正常工作
"""

import sys
import os
import requests
import json
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

def test_api_connectivity():
    """测试API连接性"""
    base_url = "http://localhost:8000"
    
    print("🔍 开始测试API连接性...")
    print(f"📍 API地址: {base_url}")
    print("=" * 50)
    
    # 1. 测试根路径
    print("1. 测试根路径 (/) ...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ 成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"   ❌ 失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    
    # 2. 测试健康检查
    print("2. 测试健康检查 (/health) ...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ 成功")
            health_data = response.json()
            print(f"   健康状态: {'健康' if health_data.get('healthy') else '不健康'}")
        else:
            print(f"   ❌ 失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    
    # 3. 测试市场概览
    print("3. 测试市场概览 (/market/overview) ...")
    try:
        response = requests.get(f"{base_url}/market/overview")
        if response.status_code == 200:
            print("   ✅ 成功")
            overview_data = response.json()
            summary = overview_data.get('market_summary', {})
            print(f"   股票总数: {summary.get('total_count', 'N/A')}")
        else:
            print(f"   ❌ 失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    
    # 4. 测试股票基础信息 (以平安银行为例)
    print("4. 测试股票基础信息 (/stock/000001/basic-info) ...")
    try:
        response = requests.get(f"{base_url}/stock/000001/basic-info")
        if response.status_code == 200:
            print("   ✅ 成功")
            basic_info = response.json()
            print(f"   股票名称: {basic_info.get('name', 'N/A')}")
        else:
            print(f"   ❌ 失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    
    # 5. 测试技术分析
    print("5. 测试技术分析 (/stock/000001/technical-analysis) ...")
    try:
        response = requests.get(f"{base_url}/stock/000001/technical-analysis")
        if response.status_code == 200:
            print("   ✅ 成功")
            tech_data = response.json()
            print(f"   技术指标状态: {tech_data.get('status', 'N/A')}")
        else:
            print(f"   ❌ 失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    
    # 6. 测试综合分析
    print("6. 测试综合分析 (/stock/000001/comprehensive-analysis) ...")
    try:
        response = requests.get(f"{base_url}/stock/000001/comprehensive-analysis")
        if response.status_code == 200:
            print("   ✅ 成功")
            comprehensive_data = response.json()
            print(f"   分析类型: {comprehensive_data.get('analysis_type', 'N/A')}")
            print(f"   状态: {comprehensive_data.get('status', 'N/A')}")
        else:
            print(f"   ❌ 失败，状态码: {response.status_code}")
            if response.status_code == 500:
                print(f"   错误详情: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print()
    print("=" * 50)
    print("✅ API连接性测试完成")

if __name__ == "__main__":
    test_api_connectivity()