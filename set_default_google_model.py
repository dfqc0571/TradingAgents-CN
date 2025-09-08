#!/usr/bin/env python3
"""
设置默认Google AI模型的脚本
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def set_default_google_model():
    """设置默认Google AI模型为gemini-2.5-flash"""
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    print("🔧 设置默认Google AI模型")
    print("=" * 50)
    
    # 检查.env文件是否存在
    if not env_file.exists():
        print("❌ .env文件不存在")
        return False
    
    # 读取.env文件内容
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找是否已存在默认模型设置
    default_model_line = None
    for i, line in enumerate(lines):
        if line.startswith("DEFAULT_GOOGLE_MODEL="):
            default_model_line = i
            break
    
    # 设置默认模型
    new_model_line = "DEFAULT_GOOGLE_MODEL=gemini-2.5-flash\n"
    
    if default_model_line is not None:
        # 更新现有行
        lines[default_model_line] = new_model_line
        print("🔄 更新默认Google AI模型设置")
    else:
        # 添加新行
        lines.append(f"\n# 默认Google AI模型\n{new_model_line}")
        print("➕ 添加默认Google AI模型设置")
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ 默认Google AI模型已设置为: gemini-2.5-flash")
    print(f"📁 配置文件: {env_file}")
    
    return True

if __name__ == "__main__":
    success = set_default_google_model()
    if success:
        print("\n💡 请重启Web应用使配置生效")
    else:
        print("\n💥 设置默认Google AI模型失败")