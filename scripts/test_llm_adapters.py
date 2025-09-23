#!/usr/bin/env python3
"""
测试LLM适配器的脚本
验证各种LLM适配器是否能正确初始化和调用
"""

import os
import sys
from typing import Optional

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_core.messages import HumanMessage
from tradingagents.llm_adapters import (
    create_openai_compatible_llm,
    create_modelscope_llm,
    ChatDashScope
)

# 尝试导入SiliconFlow适配器
try:
    from tradingagents.llm_adapters import ChatSiliconFlow
    SILICONFLOW_AVAILABLE = True
except ImportError:
    SILICONFLOW_AVAILABLE = False


def getenv_stripped(key: str) -> Optional[str]:
    """获取环境变量并去除首尾空格"""
    val = os.getenv(key)
    return val.strip() if isinstance(val, str) else val


def test_modelscope_adapter():
    """测试魔搭ModelScope适配器"""
    print("==== 测试魔搭ModelScope适配器 ====")
    
    api_key = getenv_stripped("MODELSCOPE_API_KEY")
    base_url = getenv_stripped("MODELSCOPE_BASE_URL") or "https://api.moerscan.io/v1"
    model = getenv_stripped("MODELSCOPE_MODEL") or "qwen/Qwen2-7B-Instruct"
    
    print(f"Model           : {model}")
    print(f"API Key set     : {'YES' if api_key else 'NO'}")
    print(f"Base URL        : {base_url}")
    
    if not api_key:
        print("[WARNING] MODELSCOPE_API_KEY未设置，跳过测试")
        return 0
    
    try:
        # 测试新适配器
        llm = create_modelscope_llm(
            model=model,
            temperature=0.1,
            max_tokens=100
        )
        print("[OK] 新适配器实例化成功")
    except Exception as e:
        print(f"[ERROR] 新适配器实例化失败: {e}")
        return 1
    
    try:
        # 测试调用
        prompt = "请只回复：连接成功"
        print("发送测试请求到ModelScope ...")
        resp = llm.invoke([HumanMessage(content=prompt)])
        
        # 获取响应内容
        content = getattr(resp, "content", str(resp))
        trimmed = content[:100] if isinstance(content, str) else str(content)[:100]
        print("[OK] 收到响应:")
        print(trimmed)
        return 0
    except Exception as e:
        print(f"[ERROR] 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return 2


def test_siliconflow_adapter():
    """测试硅基流动SiliconFlow适配器"""
    print("\n==== 测试硅基流动SiliconFlow适配器 ====")
    
    if not SILICONFLOW_AVAILABLE:
        print("[WARNING] SiliconFlow适配器不可用，跳过测试")
        return 0
    
    api_key = getenv_stripped("SILICONFLOW_API_KEY")
    model = getenv_stripped("SILICONFLOW_MODEL") or "siliconflow/Qwen/Qwen2-7B-Instruct"
    
    print(f"Model           : {model}")
    print(f"API Key set     : {'YES' if api_key else 'NO'}")
    
    if not api_key:
        print("[WARNING] SILICONFLOW_API_KEY未设置，跳过测试")
        return 0
    
    try:
        # 测试新适配器
        llm = create_openai_compatible_llm(
            provider="siliconflow",
            model=model,
            temperature=0.1,
            max_tokens=100
        )
        print("[OK] 新适配器实例化成功")
    except Exception as e:
        print(f"[ERROR] 新适配器实例化失败: {e}")
        return 1
    
    try:
        # 测试调用
        prompt = "请只回复：连接成功"
        print("发送测试请求到SiliconFlow ...")
        resp = llm.invoke([HumanMessage(content=prompt)])
        
        # 获取响应内容
        content = getattr(resp, "content", str(resp))
        trimmed = content[:100] if isinstance(content, str) else str(content)[:100]
        print("[OK] 收到响应:")
        print(trimmed)
        return 0
    except Exception as e:
        print(f"[ERROR] 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return 2


def test_dashscope_adapter():
    """测试阿里百炼DashScope适配器"""
    print("\n==== 测试阿里百炼DashScope适配器 ====")
    
    api_key = getenv_stripped("DASHSCOPE_API_KEY")
    model = getenv_stripped("DASHSCOPE_MODEL") or "qwen-turbo"
    
    print(f"Model           : {model}")
    print(f"API Key set     : {'YES' if api_key else 'NO'}")
    
    if not api_key:
        print("[WARNING] DASHSCOPE_API_KEY未设置，跳过测试")
        return 0
    
    try:
        # 测试新适配器
        llm = create_openai_compatible_llm(
            provider="dashscope",
            model=model,
            temperature=0.1,
            max_tokens=100
        )
        print("[OK] 新适配器实例化成功")
    except Exception as e:
        print(f"[ERROR] 新适配器实例化失败: {e}")
        return 1
    
    try:
        # 测试调用
        prompt = "请只回复：连接成功"
        print("发送测试请求到DashScope ...")
        resp = llm.invoke([HumanMessage(content=prompt)])
        
        # 获取响应内容
        content = getattr(resp, "content", str(resp))
        trimmed = content[:100] if isinstance(content, str) else str(content)[:100]
        print("[OK] 收到响应:")
        print(trimmed)
        return 0
    except Exception as e:
        print(f"[ERROR] 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return 2


def main() -> int:
    """主测试函数"""
    print("LLM适配器测试脚本")
    print("=" * 50)
    
    results = []
    
    # 测试各种适配器
    results.append(test_modelscope_adapter())
    results.append(test_siliconflow_adapter())
    results.append(test_dashscope_adapter())
    
    # 统计结果
    success_count = sum(1 for r in results if r == 0)
    total_count = len(results)
    
    print(f"\n{'='*50}")
    print(f"测试完成: {success_count}/{total_count} 个适配器测试成功")
    
    if success_count == total_count:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")
        return 1


if __name__ == "__main__":
    sys.exit(main())