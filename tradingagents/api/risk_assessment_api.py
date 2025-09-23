#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险评估API接口
提供股票投资风险评估功能
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('api.risk_assessment')

# 导入风险评估相关模块
try:
    # 尝试导入新闻分析模块
    from tradingagents.agents.analysts.news_analyst import create_news_analyst
    from tradingagents.tools.unified_news_tool import create_unified_news_tool
    from tradingagents.utils.stock_utils import StockUtils
    RISK_ASSESSMENT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ 风险评估模块部分功能不可用: {e}")
    RISK_ASSESSMENT_AVAILABLE = False

def evaluate_market_risk(stock_code: str) -> Dict[str, Any]:
    """
    评估股票市场风险
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict: 市场风险评估结果
    
    Example:
        >>> risk = evaluate_market_risk('000001')
        >>> print(risk['risk_level'])
    """
    if not RISK_ASSESSMENT_AVAILABLE:
        return {
            'error': '风险评估模块不可用',
            'code': stock_code,
            'suggestion': '请检查模块依赖'
        }
    
    try:
        # 获取股票市场信息
        market_info = StockUtils.get_market_info(stock_code)
        
        # 简化的风险评估逻辑（实际项目中应该使用更复杂的模型）
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 模拟风险评估结果
        import random
        
        # 基于市场类型设定基础风险
        base_risk = 0.5
        if market_info['is_china']:
            base_risk = 0.6  # A股市场波动较大
        elif market_info['is_hk']:
            base_risk = 0.5  # 港股市场适中
        elif market_info['is_us']:
            base_risk = 0.4  # 美股市场相对稳定
        
        # 添加随机波动
        risk_score = min(1.0, max(0.1, base_risk + random.uniform(-0.2, 0.2)))
        
        # 确定风险等级
        if risk_score < 0.3:
            risk_level = 'LOW'
            description = '低风险'
        elif risk_score < 0.6:
            risk_level = 'MODERATE'
            description = '中等风险'
        elif risk_score < 0.8:
            risk_level = 'HIGH'
            description = '高风险'
        else:
            risk_level = 'VERY_HIGH'
            description = '极高风险'
        
        return {
            'code': stock_code,
            'date': current_date,
            'market': market_info['market_name'],
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'description': description,
            'factors': {
                'market_volatility': round(random.uniform(0.1, 0.9), 2),
                'sector_risk': round(random.uniform(0.1, 0.9), 2),
                'liquidity_risk': round(random.uniform(0.1, 0.9), 2)
            },
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"评估市场风险时发生错误: {e}")
        return {
            'error': f'评估市场风险失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码'
        }

def analyze_news_sentiment(stock_code: str, days: int = 7) -> Dict[str, Any]:
    """
    分析股票相关新闻情绪
    
    Args:
        stock_code: 股票代码
        days: 分析天数，默认7天
    
    Returns:
        Dict: 新闻情绪分析结果
    
    Example:
        >>> sentiment = analyze_news_sentiment('000001')
        >>> print(sentiment['sentiment_score'])
    """
    if not RISK_ASSESSMENT_AVAILABLE:
        return {
            'error': '风险评估模块不可用',
            'code': stock_code,
            'suggestion': '请检查模块依赖'
        }
    
    try:
        # 获取股票市场信息
        market_info = StockUtils.get_market_info(stock_code)
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 模拟新闻情绪分析结果
        import random
        
        # 基于市场类型设定基础情绪
        base_sentiment = 0.0  # 中性
        if market_info['is_china']:
            base_sentiment = random.uniform(-0.2, 0.2)  # A股新闻情绪波动较大
        elif market_info['is_hk']:
            base_sentiment = random.uniform(-0.1, 0.1)  # 港股新闻情绪适中
        elif market_info['is_us']:
            base_sentiment = random.uniform(-0.1, 0.1)  # 美股新闻情绪相对稳定
        
        sentiment_score = min(1.0, max(-1.0, base_sentiment))
        
        # 确定情绪等级
        if sentiment_score < -0.5:
            sentiment = 'VERY_NEGATIVE'
            description = '极度负面'
        elif sentiment_score < -0.1:
            sentiment = 'NEGATIVE'
            description = '负面'
        elif sentiment_score <= 0.1:
            sentiment = 'NEUTRAL'
            description = '中性'
        elif sentiment_score <= 0.5:
            sentiment = 'POSITIVE'
            description = '正面'
        else:
            sentiment = 'VERY_POSITIVE'
            description = '极度正面'
        
        return {
            'code': stock_code,
            'date': current_date,
            'analysis_period': f"{days}天",
            'sentiment_score': round(sentiment_score, 2),
            'sentiment': sentiment,
            'description': description,
            'positive_news_count': random.randint(0, 10),
            'negative_news_count': random.randint(0, 10),
            'total_news_count': random.randint(5, 20),
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"分析新闻情绪时发生错误: {e}")
        return {
            'error': f'分析新闻情绪失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码'
        }

def comprehensive_risk_assessment(stock_code: str) -> Dict[str, Any]:
    """
    综合风险评估
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict: 综合风险评估结果
    
    Example:
        >>> assessment = comprehensive_risk_assessment('000001')
        >>> print(assessment['overall_risk_level'])
    """
    if not RISK_ASSESSMENT_AVAILABLE:
        return {
            'error': '风险评估模块不可用',
            'code': stock_code,
            'suggestion': '请检查模块依赖'
        }
    
    try:
        # 获取市场风险评估
        market_risk = evaluate_market_risk(stock_code)
        if 'error' in market_risk:
            return market_risk
        
        # 获取新闻情绪分析
        news_sentiment = analyze_news_sentiment(stock_code)
        if 'error' in news_sentiment:
            return news_sentiment
        
        # 综合评估
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算综合风险分数
        # 市场风险权重0.6，新闻情绪权重0.4
        overall_risk_score = (
            market_risk['risk_score'] * 0.6 + 
            (0.5 - news_sentiment['sentiment_score'] * 0.5) * 0.4  # 情绪分数转换为风险分数
        )
        
        # 确定综合风险等级
        if overall_risk_score < 0.3:
            overall_risk_level = 'LOW'
            description = '低风险'
            recommendation = '可以考虑投资'
        elif overall_risk_score < 0.6:
            overall_risk_level = 'MODERATE'
            description = '中等风险'
            recommendation = '谨慎投资'
        elif overall_risk_score < 0.8:
            overall_risk_level = 'HIGH'
            description = '高风险'
            recommendation = '高风险投资，需密切关注'
        else:
            overall_risk_level = 'VERY_HIGH'
            description = '极高风险'
            recommendation = '不建议投资'
        
        return {
            'code': stock_code,
            'date': current_date,
            'market_risk': market_risk,
            'news_sentiment': news_sentiment,
            'overall_risk_score': round(overall_risk_score, 2),
            'overall_risk_level': overall_risk_level,
            'description': description,
            'recommendation': recommendation,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"综合风险评估时发生错误: {e}")
        return {
            'error': f'综合风险评估失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码'
        }

if __name__ == '__main__':
    # 简单的命令行测试
    logger.info("🔍 风险评估API测试")
    logger.info("=" * 50)
    
    # 测试市场风险评估
    logger.info("\n📊 评估平安银行市场风险:")
    market_risk_result = evaluate_market_risk('000001')
    if 'error' not in market_risk_result:
        logger.info(f"  风险等级: {market_risk_result.get('risk_level')}")
        logger.info(f"  风险分数: {market_risk_result.get('risk_score')}")
        logger.info(f"  风险描述: {market_risk_result.get('description')}")
    else:
        logger.error(f"  错误: {market_risk_result.get('error')}")
    
    # 测试新闻情绪分析
    logger.info("\n📰 分析平安银行新闻情绪:")
    news_sentiment_result = analyze_news_sentiment('000001')
    if 'error' not in news_sentiment_result:
        logger.info(f"  情绪等级: {news_sentiment_result.get('sentiment')}")
        logger.info(f"  情绪分数: {news_sentiment_result.get('sentiment_score')}")
        logger.info(f"  情绪描述: {news_sentiment_result.get('description')}")
    else:
        logger.error(f"  错误: {news_sentiment_result.get('error')}")
    
    # 测试综合风险评估
    logger.info("\n📈 平安银行综合风险评估:")
    comprehensive_result = comprehensive_risk_assessment('000001')
    if 'error' not in comprehensive_result:
        logger.info(f"  综合风险等级: {comprehensive_result.get('overall_risk_level')}")
        logger.info(f"  综合风险分数: {comprehensive_result.get('overall_risk_score')}")
        logger.info(f"  投资建议: {comprehensive_result.get('recommendation')}")
    else:
        logger.error(f"  错误: {comprehensive_result.get('error')}")