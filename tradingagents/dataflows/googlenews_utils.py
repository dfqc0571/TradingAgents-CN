#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
谷歌新闻数据获取工具
支持中文新闻搜索和处理
"""

import sys
import os
import time
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('dataflows.googlenews')

# 尝试导入tenacity，如果不可用则使用简单重试机制
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type
    )
    TENACITY_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ tenacity库不可用，将使用简单重试机制")
    TENACITY_AVAILABLE = False

# 尝试导入Google News API
try:
    from GoogleNews import GoogleNews
    GOOGLE_NEWS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ GoogleNews库不可用")
    GOOGLE_NEWS_AVAILABLE = False

def getNewsData(stock_name: str, days: int = 30) -> List[Dict[str, str]]:
    """
    获取指定股票相关的新闻数据
    
    Args:
        stock_name: 股票名称
        days: 获取最近几天的新闻，默认30天
    
    Returns:
        List[Dict]: 新闻数据列表，每条新闻包含title、link、date等字段
    """
    if not GOOGLE_NEWS_AVAILABLE:
        logger.warning(f"❌ Google News API不可用，无法获取{stock_name}的新闻数据")
        return []
    
    try:
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 格式化日期
        start_date_str = start_date.strftime("%m/%d/%Y")
        end_date_str = end_date.strftime("%m/%d/%Y")
        
        logger.info(f"🔍 搜索{stock_name}的新闻，时间范围: {start_date_str} - {end_date_str}")
        
        # 创建GoogleNews实例
        googlenews = GoogleNews(lang='zh', start=start_date_str, end=end_date_str)
        googlenews.setencode('utf-8')
        
        # 搜索关键词
        search_query = f"{stock_name} 股票 OR 股价 OR 投资"
        logger.info(f"🔍 搜索关键词: {search_query}")
        
        # 根据是否有tenacity使用不同的重试机制
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=4, max=10),
                retry=retry_if_exception_type(Exception)
            )
            def _search_with_retry():
                googlenews.search(search_query)
                return googlenews.result()
            
            results = _search_with_retry()
        else:
            # 简单重试机制
            results = None
            for attempt in range(3):
                try:
                    googlenews.search(search_query)
                    results = googlenews.result()
                    break
                except Exception as e:
                    logger.warning(f"第{attempt+1}次尝试失败: {e}")
                    if attempt < 2:  # 不是最后一次尝试
                        time.sleep(2 ** attempt)  # 指数退避
                    else:
                        raise  # 最后一次尝试失败则抛出异常
        
        if not results:
            logger.info(f"🔍 未找到{stock_name}的相关新闻")
            return []
        
        # 处理结果
        news_list = []
        for item in results[:10]:  # 限制最多10条新闻
            news_item = {
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'date': item.get('date', ''),
                'desc': item.get('desc', ''),
                'source': item.get('media', '')
            }
            news_list.append(news_item)
        
        logger.info(f"✅ 成功获取{len(news_list)}条{stock_name}的新闻")
        return news_list
        
    except Exception as e:
        logger.error(f"❌ 获取{stock_name}新闻时发生错误: {e}")
        return []

# 测试函数
def test_news_fetch():
    """测试新闻获取功能"""
    print("🧪 测试新闻获取功能...")
    
    # 测试平安银行
    news = getNewsData("平安银行", 7)
    print(f"🔍 平安银行新闻数量: {len(news)}")
    
    if news:
        print("📝 最新新闻:")
        for i, item in enumerate(news[:3]):
            print(f"  {i+1}. {item['title']}")
            print(f"     日期: {item['date']}")
            print(f"     来源: {item['source']}")
            print()

if __name__ == "__main__":
    test_news_fetch()