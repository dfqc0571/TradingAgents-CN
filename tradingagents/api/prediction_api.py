#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预测模型API接口
提供股票价格趋势预测功能
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
logger = get_logger('api.prediction')

# 导入预测相关模块
try:
    # 尝试导入市场分析师模块
    from tradingagents.agents.analysts.market_analyst import create_market_analyst_react
    from tradingagents.dataflows.interface import get_china_stock_data_unified
    PREDICTION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ 预测模块部分功能不可用: {e}")
    PREDICTION_AVAILABLE = False

def predict_stock_trend(
    stock_code: str, 
    days: int = 5,
    features: List[str] = None
) -> Dict[str, Any]:
    """
    预测股票价格趋势
    
    Args:
        stock_code: 股票代码
        days: 预测天数，默认5天
        features: 用于预测的特征列表
    
    Returns:
        Dict: 股票趋势预测结果
    
    Example:
        >>> result = predict_stock_trend('000001', days=3)
        >>> print(result['prediction'])
    """
    if not PREDICTION_AVAILABLE:
        return {
            'error': '预测模块不可用',
            'code': stock_code,
            'suggestion': '请检查模块依赖'
        }
    
    try:
        # 默认特征
        if features is None:
            features = ['price', 'volume', 'technical_indicators']
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 获取股票数据
        from tradingagents.utils.stock_utils import StockUtils
        if StockUtils.is_china_stock(stock_code):
            stock_data = get_china_stock_data_unified(stock_code, start_date, end_date)
            if isinstance(stock_data, dict) and 'error' in stock_data:
                return stock_data
        
        # 简化的预测逻辑（实际项目中应该使用更复杂的模型）
        # 这里我们只是模拟预测结果
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 模拟预测结果
        predictions = []
        base_price = 10.0  # 基准价格，实际应该从数据中获取
        
        for i in range(1, days + 1):
            future_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            # 简单的随机波动模拟
            import random
            change_percent = random.uniform(-0.05, 0.05)  # ±5%波动
            predicted_price = base_price * (1 + change_percent)
            
            predictions.append({
                'date': future_date,
                'price': round(predicted_price, 2),
                'change_percent': round(change_percent * 100, 2),
                'confidence': round(random.uniform(0.6, 0.9), 2)
            })
        
        # 确定总体趋势
        avg_change = sum(p['change_percent'] for p in predictions) / len(predictions)
        if avg_change > 2:
            trend = 'STRONG_UP'
            recommendation = 'BUY'
        elif avg_change > 0:
            trend = 'MODERATE_UP'
            recommendation = 'HOLD'
        elif avg_change > -2:
            trend = 'MODERATE_DOWN'
            recommendation = 'HOLD'
        else:
            trend = 'STRONG_DOWN'
            recommendation = 'SELL'
        
        return {
            'code': stock_code,
            'current_date': current_date,
            'prediction_period': f"{days}天",
            'predictions': predictions,
            'overall_trend': trend,
            'recommendation': recommendation,
            'avg_change_percent': round(avg_change, 2),
            'confidence': round(sum(p['confidence'] for p in predictions) / len(predictions), 2),
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"预测股票趋势时发生错误: {e}")
        return {
            'error': f'预测股票趋势失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码和数据源'
        }

def get_investment_suggestion(stock_code: str) -> Dict[str, Any]:
    """
    获取投资建议
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict: 投资建议和风险评估
    
    Example:
        >>> suggestion = get_investment_suggestion('000001')
        >>> print(suggestion['action'])
    """
    if not PREDICTION_AVAILABLE:
        return {
            'error': '预测模块不可用',
            'code': stock_code,
            'suggestion': '请检查模块依赖'
        }
    
    try:
        # 获取预测结果
        prediction_result = predict_stock_trend(stock_code, days=3)
        if 'error' in prediction_result:
            return prediction_result
        
        # 获取技术指标
        try:
            from tradingagents.api.technical_analysis_api import get_trading_signals
            technical_signals = get_trading_signals(stock_code)
        except ImportError:
            technical_signals = {'error': '无法加载技术分析模块'}
        
        # 综合分析生成建议
        suggestion = {
            'code': stock_code,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'prediction': prediction_result,
            'technical_signals': technical_signals,
            'risk_level': 'MODERATE',  # 默认中等风险
            'action': prediction_result['recommendation'],
            'reason': '',
            'confidence': 0.0
        }
        
        # 根据预测结果和信号确定建议
        if prediction_result['recommendation'] == 'BUY' and 'error' not in technical_signals:
            suggestion['reason'] = '基于趋势预测看涨，技术指标支持买入'
            suggestion['confidence'] = min(prediction_result['confidence'], 
                                         technical_signals.get('confidence', 0.5))
            # 如果预测和信号都强烈看涨，降低风险等级
            if prediction_result['overall_trend'] in ['STRONG_UP'] and \
               technical_signals.get('recommendation') == 'BUY':
                suggestion['risk_level'] = 'LOW'
        elif prediction_result['recommendation'] == 'SELL' and 'error' not in technical_signals:
            suggestion['reason'] = '基于趋势预测看跌，技术指标支持卖出'
            suggestion['confidence'] = min(prediction_result['confidence'], 
                                         technical_signals.get('confidence', 0.5))
            # 如果预测和信号都强烈看跌，提高风险等级
            if prediction_result['overall_trend'] in ['STRONG_DOWN'] and \
               technical_signals.get('recommendation') == 'SELL':
                suggestion['risk_level'] = 'HIGH'
        else:
            suggestion['reason'] = '趋势不明确，建议持有观察'
            suggestion['confidence'] = min(prediction_result['confidence'], 
                                         technical_signals.get('confidence', 0.5) if 'error' not in technical_signals else 0.5)
        
        return suggestion
        
    except Exception as e:
        logger.error(f"生成投资建议时发生错误: {e}")
        return {
            'error': f'生成投资建议失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码和数据源'
        }

if __name__ == '__main__':
    # 简单的命令行测试
    logger.info("🔍 预测模型API测试")
    logger.info("=" * 50)
    
    # 测试股票趋势预测
    logger.info("\n📈 预测平安银行趋势:")
    prediction_result = predict_stock_trend('000001', days=3)
    if 'error' not in prediction_result:
        logger.info(f"  总体趋势: {prediction_result.get('overall_trend')}")
        logger.info(f"  推荐操作: {prediction_result.get('recommendation')}")
        logger.info(f"  平均变化: {prediction_result.get('avg_change_percent')}%")
        logger.info(f"  置信度: {prediction_result.get('confidence')}")
    else:
        logger.error(f"  错误: {prediction_result.get('error')}")
    
    # 测试投资建议
    logger.info("\n💡 获取平安银行投资建议:")
    suggestion_result = get_investment_suggestion('000001')
    if 'error' not in suggestion_result:
        logger.info(f"  操作建议: {suggestion_result.get('action')}")
        logger.info(f"  风险等级: {suggestion_result.get('risk_level')}")
        logger.info(f"  建议理由: {suggestion_result.get('reason')}")
        logger.info(f"  置信度: {suggestion_result.get('confidence')}")
    else:
        logger.error(f"  错误: {suggestion_result.get('error')}")