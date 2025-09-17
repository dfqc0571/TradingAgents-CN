"""
魔搭社区 (ModelScope) 适配器
为 TradingAgents 提供魔搭社区大模型的 LangChain 兼容接口
"""

import os
from typing import Optional, Sequence, Union, Dict, Any, List
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

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
        
        # 保存模型名称以供后续使用
        self.model_name = model

        logger.info(f"✅ [魔搭社区] 已配置魔搭社区端点")

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, BaseTool]],
        **kwargs: Any,
    ):
        """绑定工具到模型，但检查模型是否支持工具调用"""
        # 检查模型是否支持工具调用
        from .openai_compatible_base import OPENAI_COMPATIBLE_PROVIDERS
        models_config = OPENAI_COMPATIBLE_PROVIDERS.get("modelscope", {}).get("models", {})
        model_info = models_config.get(self.model_name, {})
        supports_function_calling = model_info.get("supports_function_calling", False)
        
        if not supports_function_calling:
            logger.warning(f"⚠️ 模型 {self.model_name} 不支持工具调用，将使用模拟工具调用")
            # 返回一个带有模拟工具调用功能的实例
            return self._create_mock_tool_binding(tools)
        
        # 模型支持工具调用，正常绑定
        return self.llm.bind_tools(tools, **kwargs)
    
    def _create_mock_tool_binding(self, tools: Sequence[Union[Dict[str, Any], type, BaseTool]]):
        """为不支持工具调用的模型创建模拟工具绑定"""
        # 创建工具描述列表
        tool_descriptions = []
        for tool in tools:
            if hasattr(tool, "name") and hasattr(tool, "description"):
                tool_descriptions.append({
                    "name": tool.name,
                    "description": tool.description
                })
            elif isinstance(tool, dict) and "name" in tool and "description" in tool:
                tool_descriptions.append({
                    "name": tool["name"],
                    "description": tool["description"]
                })
        
        # 保存工具信息
        self._tool_descriptions = tool_descriptions
        return self

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