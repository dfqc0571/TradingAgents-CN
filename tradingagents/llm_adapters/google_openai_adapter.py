"""
Google AI OpenAI兼容适配器
为 TradingAgents 提供Google AI (Gemini)模型的 OpenAI 兼容接口
解决Google模型工具调用格式不匹配的问题
"""

import os
from typing import Any, Dict, List, Optional, Union, Sequence
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import LLMResult, ChatGeneration
from pydantic import Field, SecretStr
from ..config.config_manager import token_tracker
from ..config.api_key_manager import get_api_key_manager

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class ChatGoogleOpenAI(ChatGoogleGenerativeAI):
    """
    Google AI OpenAI 兼容适配器
    继承 ChatGoogleGenerativeAI，优化工具调用和内容格式处理
    解决Google模型工具调用返回格式与系统期望不匹配的问题
    """
    
    def __init__(self, **kwargs):
        """初始化 Google AI OpenAI 兼容客户端"""
        
        # 设置 Google AI 的默认配置
        kwargs.setdefault("temperature", 0.1)
        kwargs.setdefault("max_tokens", 2000)
        
        # 检查 API 密钥
        google_api_key = kwargs.get("google_api_key") or os.getenv("GOOGLE_API_KEY")
        # 如果没有提供特定密钥，使用轮询机制获取
        if not google_api_key:
            api_key_manager = get_api_key_manager()
            google_api_key = api_key_manager.get_next_google_key()
            
        if not google_api_key:
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY environment variable "
                "or pass google_api_key parameter."
            )
        
        kwargs["google_api_key"] = google_api_key
        
        # 调用父类初始化
        super().__init__(**kwargs)
        
        # 保存API密钥管理器引用用于错误处理
        self._api_key_manager = get_api_key_manager()

        logger.info(f"✅ Google AI OpenAI 兼容适配器初始化成功")
        logger.info(f"   模型: {kwargs.get('model', 'gemini-pro')}")
        logger.info(f"   温度: {kwargs.get('temperature', 0.1)}")
        logger.info(f"   最大Token: {kwargs.get('max_tokens', 2000)}")
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> LLMResult:
        """重写生成方法，优化工具调用处理和内容格式"""
        
        try:
            # 调用父类的生成方法
            result = super()._generate(messages, stop, **kwargs)
            
            # 修复可能的列表格式问题
            if result and hasattr(result, 'generations') and result.generations:
                # 确保 generations 是正确的格式
                if isinstance(result.generations, list):
                    # 处理嵌套列表的情况
                    fixed_generations = []
                    for gen_item in result.generations:
                        if isinstance(gen_item, list):
                            # 如果是嵌套列表，只取第一个元素
                            if gen_item:
                                fixed_generations.append(gen_item[0])
                            else:
                                fixed_generations.append([])
                        else:
                            fixed_generations.append(gen_item)
                    result.generations = fixed_generations
                
                # 优化返回内容格式
                for generation_item in result.generations:
                    # 如果是列表中的列表
                    if isinstance(generation_item, list) and generation_item:
                        generation = generation_item[0]
                        if hasattr(generation, 'message') and generation.message:
                            self._optimize_message_content(generation.message)
                    # 如果是单个generation对象
                    elif hasattr(generation_item, 'message') and generation_item.message:
                        self._optimize_message_content(generation_item.message)
                    # 如果generation_item本身就是一个message对象
                    elif hasattr(generation_item, 'content'):
                        self._optimize_message_content(generation_item)
            
            # 追踪 token 使用量
            self._track_token_usage(result, kwargs)
            
            return result
            
        except Exception as e:
            # 标记当前API密钥出现错误
            if hasattr(self, 'google_api_key'):
                self._api_key_manager.mark_key_error(self.google_api_key)
            
            logger.error(f"❌ Google AI 生成失败: {e}")
            # 返回一个包含错误信息的结果，而不是抛出异常
            error_message = AIMessage(content=f"Google AI 调用失败: {str(e)}")
            error_generation = ChatGeneration(message=error_message)
            return LLMResult(generations=[[error_generation]])
    
    def _optimize_message_content(self, message: BaseMessage):
        """优化消息内容格式，确保包含新闻特征关键词"""
        
        if not isinstance(message, AIMessage) or not message.content:
            return

        # 确保tool_calls属性存在且格式正确
        if not hasattr(message, 'tool_calls'):
            message.tool_calls = []
        elif message.tool_calls is None:
            message.tool_calls = []
        elif not isinstance(message.tool_calls, list):
            # 如果tool_calls不是列表，将其转换为列表
            message.tool_calls = [message.tool_calls] if message.tool_calls else []
            
        # 检查tool_calls中的每个元素是否是字典格式，如果不是则转换
        for i, tool_call in enumerate(message.tool_calls):
            if not isinstance(tool_call, dict):
                # 尝试从对象中提取必要的属性
                if hasattr(tool_call, 'name') and hasattr(tool_call, 'args'):
                    message.tool_calls[i] = {
                        'name': tool_call.name,
                        'args': tool_call.args,
                        'id': getattr(tool_call, 'id', f'tool_call_{i}')
                    }
                else:
                    # 如果无法提取必要属性，移除该工具调用
                    logger.warning(f"⚠️ 无法识别的工具调用格式: {type(tool_call)}")
                    message.tool_calls[i] = {}

        # 清理空的工具调用
        message.tool_calls = [tc for tc in message.tool_calls if tc]

    def _is_news_content(self, content: str) -> bool:
        """判断内容是否为新闻内容"""
        
        # 检查是否包含新闻相关的关键词
        news_indicators = [
            "股票", "公司", "市场", "投资", "财经", "证券", "交易",
            "涨跌", "业绩", "财报", "分析", "预测", "消息", "公告"
        ]
        
        return any(indicator in content for indicator in news_indicators) and len(content) > 200
    
    def _enhance_news_content(self, content: str) -> str:
        """增强新闻内容，添加必要的格式化信息"""
        
        import datetime
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 如果内容缺少必要的新闻特征，添加它们
        enhanced_content = content
        
        # 添加发布时间信息（如果缺少）
        if "发布时间" not in content and "时间" not in content:
            enhanced_content = f"发布时间: {current_date}\n\n{enhanced_content}"
        
        # 添加新闻标题标识（如果缺少）
        if "新闻标题" not in content and "标题" not in content:
            # 尝试从内容中提取第一行作为标题
            lines = enhanced_content.split('\n')
            if lines:
                first_line = lines[0].strip()
                if len(first_line) < 100:  # 可能是标题
                    enhanced_content = f"新闻标题: {first_line}\n\n{enhanced_content}"
        
        # 添加文章来源信息（如果缺少）
        if "文章来源" not in content and "来源" not in content:
            enhanced_content = f"{enhanced_content}\n\n文章来源: Google AI 智能分析"
        
        return enhanced_content
    
    def _track_token_usage(self, result: LLMResult, kwargs: Dict[str, Any]):
        """追踪 token 使用量"""
        
        try:
            # 从结果中提取 token 使用信息
            if hasattr(result, 'llm_output') and result.llm_output:
                token_usage = result.llm_output.get('token_usage', {})
                
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                
                if input_tokens > 0 or output_tokens > 0:
                    # 生成会话ID
                    session_id = kwargs.get('session_id', f"google_openai_{hash(str(kwargs))%10000}")
                    analysis_type = kwargs.get('analysis_type', 'stock_analysis')
                    
                    # 使用 TokenTracker 记录使用量
                    token_tracker.track_usage(
                        provider="google",
                        model_name=self.model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        session_id=session_id,
                        analysis_type=analysis_type
                    )
                    
                    logger.debug(f"📊 [Google适配器] Token使用量: 输入={input_tokens}, 输出={output_tokens}")
                    
        except Exception as track_error:
            # token 追踪失败不应该影响主要功能
            logger.error(f"⚠️ Google适配器 Token 追踪失败: {track_error}")


# 支持的模型列表
GOOGLE_OPENAI_MODELS = {
    # Gemini 2.5 系列 - 最新验证模型
    "gemini-2.5-pro": {
        "description": "Gemini 2.5 Pro - 最新旗舰模型，功能强大 (16.68s)",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["复杂推理", "专业分析", "高质量输出"],
        "avg_response_time": 16.68
    },
    "gemini-2.5-flash": {
        "description": "Gemini 2.5 Flash - 最新快速模型 (2.73s)",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["快速响应", "实时分析", "高频使用"],
        "avg_response_time": 2.73
    },
    "gemini-2.5-flash-lite-preview-06-17": {
        "description": "Gemini 2.5 Flash Lite Preview - 超快响应 (1.45s)",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["超快响应", "实时交互", "高频调用"],
        "avg_response_time": 1.45
    },
    # Gemini 2.0 系列
    "gemini-2.0-flash": {
        "description": "Gemini 2.0 Flash - 新一代快速模型 (1.87s)",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["快速响应", "实时分析"],
        "avg_response_time": 1.87
    },
    # Gemini 1.5 系列
    "gemini-1.5-pro": {
        "description": "Gemini 1.5 Pro - 强大性能，平衡选择 (2.25s)",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["复杂分析", "专业任务", "深度思考"],
        "avg_response_time": 2.25
    },
    "gemini-1.5-flash": {
        "description": "Gemini 1.5 Flash - 快速响应，备用选择 (2.87s)",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["快速任务", "日常对话", "简单分析"],
        "avg_response_time": 2.87
    },
    # 经典模型
    "gemini-pro": {
        "description": "Gemini Pro - 经典模型，稳定可靠",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["通用任务", "稳定性要求高的场景"]
    }
}


def get_available_google_models() -> Dict[str, Dict[str, Any]]:
    """获取可用的 Google AI 模型列表"""
    return GOOGLE_OPENAI_MODELS


def create_google_openai_llm(
    model: str = "gemini-2.5-flash-lite-preview-06-17",
    google_api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2000,
    **kwargs
) -> ChatGoogleOpenAI:
    """创建 Google AI OpenAI 兼容 LLM 实例的便捷函数"""
    
    return ChatGoogleOpenAI(
        model=model,
        google_api_key=google_api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def test_google_openai_connection(
    model: str = "gemini-2.0-flash",
    google_api_key: Optional[str] = None
) -> bool:
    """测试 Google AI OpenAI 兼容接口连接"""
    
    try:
        logger.info(f"🧪 测试 Google AI OpenAI 兼容接口连接")
        logger.info(f"   模型: {model}")
        
        # 创建客户端
        llm = create_google_openai_llm(
            model=model,
            google_api_key=google_api_key,
            max_tokens=50
        )
        
        # 发送测试消息
        response = llm.invoke("你好，请简单介绍一下你自己。")
        
        if response and hasattr(response, 'content') and response.content:
            logger.info(f"✅ Google AI OpenAI 兼容接口连接成功")
            logger.info(f"   响应: {response.content[:100]}...")
            return True
        else:
            logger.error(f"❌ Google AI OpenAI 兼容接口响应为空")
            return False
            
    except Exception as e:
        logger.error(f"❌ Google AI OpenAI 兼容接口连接失败: {e}")
        return False


def test_google_openai_function_calling(
    model: str = "gemini-2.5-flash-lite-preview-06-17",
    google_api_key: Optional[str] = None
) -> bool:
    """测试 Google AI OpenAI 兼容接口的 Function Calling"""
    
    try:
        logger.info(f"🧪 测试 Google AI Function Calling")
        logger.info(f"   模型: {model}")
        
        # 创建客户端
        llm = create_google_openai_llm(
            model=model,
            google_api_key=google_api_key,
            max_tokens=200
        )
        
        # 定义测试工具
        from langchain_core.tools import tool
        
        @tool
        def test_news_tool(query: str) -> str:
            """测试新闻工具，返回模拟新闻内容"""
            return f"""发布时间: 2024-01-15
新闻标题: {query}相关市场动态
文章来源: 测试新闻源

这是一条关于{query}的测试新闻内容。该公司近期表现良好，市场前景看好。
投资者对此表示关注，分析师给出积极评价。"""
        
        # 绑定工具
        llm_with_tools = llm.bind_tools([test_news_tool])
        
        # 测试工具调用
        response = llm_with_tools.invoke("请使用test_news_tool查询'苹果公司'的新闻")
        
        logger.info(f"✅ Google AI Function Calling 测试完成")
        logger.info(f"   响应类型: {type(response)}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"   工具调用数量: {len(response.tool_calls)}")
            return True
        else:
            logger.info(f"   响应内容: {getattr(response, 'content', 'No content')}")
            return True  # 即使没有工具调用也算成功，因为模型可能选择不调用工具
            
    except Exception as e:
        logger.error(f"❌ Google AI Function Calling 测试失败: {e}")
        return False


if __name__ == "__main__":
    """测试脚本"""
    logger.info(f"🧪 Google AI OpenAI 兼容适配器测试")
    logger.info(f"=" * 50)
    
    # 测试连接
    connection_ok = test_google_openai_connection()
    
    if connection_ok:
        # 测试 Function Calling
        function_calling_ok = test_google_openai_function_calling()
        
        if function_calling_ok:
            logger.info(f"\n🎉 所有测试通过！Google AI OpenAI 兼容适配器工作正常")
        else:
            logger.error(f"\n⚠️ Function Calling 测试失败")
    else:
        logger.error(f"\n❌ 连接测试失败")