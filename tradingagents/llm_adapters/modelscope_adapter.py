"""
魔搭社区 (ModelScope) 适配器
为 TradingAgents 提供魔搭社区大模型的 LangChain 兼容接口
"""

import os
from typing import Optional

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class ChatModelScope:
    """魔搭社区适配器"""
    
    def __init__(
        self,
        model: str = "Qwen/Qwen3-235B-A22B-Thinking-2507",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        # 从环境变量获取API密钥
        if api_key is None:
            api_key = os.getenv("MODELSCOPE_API_KEY")
            if not api_key:
                raise ValueError("使用魔搭社区需要设置MODELSCOPE_API_KEY环境变量")

        logger.info(f"🔧 [魔搭社区] 使用API密钥: {api_key[:20]}...")

        # 导入OpenAI兼容适配器
        from .openai_compatible_base import create_openai_compatible_llm
        
        # 创建OpenAI兼容的LLM实例
        self.llm = create_openai_compatible_llm(
            provider="modelscope",
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        logger.info(f"✅ [魔搭社区] 已配置魔搭社区端点")

    def __getattr__(self, name):
        """代理所有未定义的方法和属性到内部的LLM实例"""
        return getattr(self.llm, name)


def create_modelscope_llm(
    model: str = "Qwen/Qwen3-235B-A22B-Thinking-2507",
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatModelScope:
    """创建魔搭社区 LLM 实例的便捷函数"""
    
    return ChatModelScope(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )