"""
API密钥管理器
支持多API密钥轮询和主备提供商自动切换
"""

import os
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from ..utils.logging_manager import get_logger

logger = get_logger(__name__)


@dataclass
class APIKeyInfo:
    """API密钥信息"""
    key: str
    provider: str  # google, dashscope, openai, etc.
    is_active: bool = True
    usage_count: int = 0
    error_count: int = 0


class APIKeyManager:
    """API密钥管理器，支持轮询和主备切换"""
    
    def __init__(self):
        self.google_keys: List[APIKeyInfo] = []
        self.backup_keys: Dict[str, APIKeyInfo] = {}
        self.current_google_index = 0
        self._load_api_keys()
    
    def _load_api_keys(self):
        """加载所有配置的API密钥"""
        # 加载主Google API密钥
        main_key = os.getenv("GOOGLE_API_KEY")
        if main_key:
            self.google_keys.append(APIKeyInfo(key=main_key, provider="google"))
            logger.info("✅ 加载主Google API密钥")
        
        # 加载备用Google API密钥 (最多10个)
        for i in range(1, 11):
            key_name = f"GOOGLE_API_KEY_{i}"
            key_value = os.getenv(key_name)
            if key_value:
                self.google_keys.append(APIKeyInfo(key=key_value, provider="google"))
                logger.info(f"✅ 加载备用Google API密钥 {i}")
        
        # 加载阿里百炼备用密钥
        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        if dashscope_key:
            self.backup_keys["dashscope"] = APIKeyInfo(key=dashscope_key, provider="dashscope")
            logger.info("✅ 加载阿里百炼备用密钥")
        
        # 加载其他备用密钥
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.backup_keys["openai"] = APIKeyInfo(key=openai_key, provider="openai")
        
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.backup_keys["deepseek"] = APIKeyInfo(key=deepseek_key, provider="deepseek")
        
        logger.info(f"🔑 总共加载 {len(self.google_keys)} 个Google API密钥和 {len(self.backup_keys)} 个备用密钥")
    
    def get_next_google_key(self) -> Optional[str]:
        """获取下一个可用的Google API密钥（轮询方式）"""
        if not self.google_keys:
            return None
        
        # 使用轮询方式选择下一个密钥
        start_index = self.current_google_index
        while True:
            key_info = self.google_keys[self.current_google_index]
            self.current_google_index = (self.current_google_index + 1) % len(self.google_keys)
            
            # 如果密钥有效，返回它
            if key_info.is_active:
                key_info.usage_count += 1
                logger.debug(f"🔄 使用Google API密钥 {self.current_google_index} (总计使用{key_info.usage_count}次)")
                return key_info.key
            
            # 如果遍历完所有密钥都没找到有效的，返回None
            if self.current_google_index == start_index:
                logger.warning("⚠️ 没有可用的Google API密钥")
                return None
    
    def mark_key_error(self, key: str):
        """标记密钥出现错误"""
        # 查找对应的密钥并增加错误计数
        for key_info in self.google_keys:
            if key_info.key == key:
                key_info.error_count += 1
                logger.warning(f"❌ Google API密钥错误计数: {key_info.error_count}")
                # 如果错误次数过多，暂时标记为非活跃
                if key_info.error_count > 5:
                    key_info.is_active = False
                    logger.warning(f"🚫 Google API密钥因错误过多被禁用")
                break
    
    def get_backup_key(self, provider: str = "dashscope") -> Optional[str]:
        """获取备用提供商的API密钥"""
        if provider in self.backup_keys and self.backup_keys[provider].is_active:
            key_info = self.backup_keys[provider]
            key_info.usage_count += 1
            logger.info(f"🔄 切换到备用提供商 {provider}")
            return key_info.key
        return None
    
    def reset_key_status(self):
        """重置所有密钥的状态（例如每天重置）"""
        for key_info in self.google_keys:
            key_info.is_active = True
            key_info.error_count = 0
        for key_info in self.backup_keys.values():
            key_info.is_active = True
            key_info.error_count = 0
        logger.info("🔄 所有API密钥状态已重置")


# 全局API密钥管理器实例
api_key_manager = APIKeyManager()


def get_api_key_manager() -> APIKeyManager:
    """获取全局API密钥管理器实例"""
    return api_key_manager