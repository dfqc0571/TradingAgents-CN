#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主API服务模块
整合所有API功能，提供统一访问入口
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('api.main')

# 导入所有API模块
try:
    from tradingagents.api.stock_api import (
        get_stock_info, 
        get_all_stocks, 
        get_stock_data, 
        search_stocks, 
        get_market_summary,
        check_service_status
    )
    from tradingagents.api.technical_analysis_api import (
        calculate_technical_indicators,
        get_trading_signals
    )
    from tradingagents.api.prediction_api import (
        predict_stock_trend,
        get_investment_suggestion
    )
    from tradingagents.api.risk_assessment_api import (
        evaluate_market_risk,
        analyze_news_sentiment,
        comprehensive_risk_assessment
    )
    API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ 部分API模块不可用: {e}")
    API_AVAILABLE = False

def get_comprehensive_stock_analysis(stock_code: str) -> Dict[str, Any]:
    """
    获取股票综合分析报告
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict: 股票综合分析报告
    
    Example:
        >>> report = get_comprehensive_stock_analysis('000001')
        >>> print(report['basic_info']['name'])
    """
    if not API_AVAILABLE:
        return {
            'error': 'API服务不可用',
            'code': stock_code,
            'suggestion': '请检查服务配置'
        }
    
    try:
        logger.info(f"开始生成股票 {stock_code} 的综合分析报告")
        
        # 尝试使用智能体框架进行深度分析
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG
            
            # 创建默认配置
            config = DEFAULT_CONFIG.copy()
            config["llm_provider"] = os.getenv("DEFAULT_LLM_PROVIDER", "modelscope")
            config["deep_think_llm"] = os.getenv("DEEP_THINK_LLM", "ZhipuAI/GLM-4.6")
            config["quick_think_llm"] = os.getenv("QUICK_THINK_LLM", "ZhipuAI/GLM-4.6")
            
            logger.info(f"使用LLM提供商: {config['llm_provider']}")
            logger.info(f"使用深度思考模型: {config['deep_think_llm']}")
            logger.info(f"使用快速思考模型: {config['quick_think_llm']}")
            
            # 初始化智能体图
            graph = TradingAgentsGraph(
                selected_analysts=["market", "social", "news", "fundamentals"],
                config=config
            )
            
            # 执行分析
            analysis_date = datetime.now().strftime('%Y-%m-%d')
            state, decision = graph.propagate(stock_code, analysis_date)
            
            # 构建深度分析报告
            deep_analysis_report = {
                'code': stock_code,
                'generated_at': datetime.now().isoformat(),
                'basic_info': get_stock_info(stock_code),
                'market_report': state.get('market_report', ''),
                'news_report': state.get('news_report', ''),
                'fundamentals_report': state.get('fundamentals_report', ''),
                'sentiment_report': state.get('sentiment_report', ''),
                'investment_debate_state': state.get('investment_debate_state', {}),
                'risk_debate_state': state.get('risk_debate_state', {}),
                'final_trade_decision': state.get('final_trade_decision', ''),
                'technical_analysis': calculate_technical_indicators(stock_code),
                'trading_signals': get_trading_signals(stock_code),
                'trend_prediction': predict_stock_trend(stock_code, days=5),
                'investment_suggestion': get_investment_suggestion(stock_code),
                'risk_assessment': comprehensive_risk_assessment(stock_code),
                'status': 'success',
                'analysis_type': 'deep_analysis'
            }
            
            logger.info(f"股票 {stock_code} 的深度综合分析报告生成完成")
            return deep_analysis_report
            
        except Exception as graph_error:
            logger.error(f"深度分析失败: {graph_error}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            # 回退到传统分析方法
            return _get_traditional_comprehensive_analysis(stock_code)
        
    except Exception as e:
        logger.error(f"生成综合分析报告时发生错误: {e}")
        return {
            'error': f'生成综合分析报告失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码和服务状态'
        }


def _get_traditional_comprehensive_analysis(stock_code: str) -> Dict[str, Any]:
    """
    传统的综合分析方法（作为备选方案）
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict: 股票综合分析报告
    """
    # 1. 获取基础信息
    basic_info = get_stock_info(stock_code)
    if 'error' in basic_info:
        return basic_info
    
    # 2. 获取技术指标
    technical_indicators = calculate_technical_indicators(stock_code)
    if 'error' in technical_indicators:
        technical_indicators = {'error': '技术指标计算失败'}
    
    # 3. 获取交易信号
    trading_signals = get_trading_signals(stock_code)
    if 'error' in trading_signals:
        trading_signals = {'error': '交易信号生成失败'}
    
    # 4. 获取趋势预测
    trend_prediction = predict_stock_trend(stock_code, days=5)
    if 'error' in trend_prediction:
        trend_prediction = {'error': '趋势预测失败'}
    
    # 5. 获取投资建议
    investment_suggestion = get_investment_suggestion(stock_code)
    if 'error' in investment_suggestion:
        investment_suggestion = {'error': '投资建议生成失败'}
    
    # 6. 获取风险评估
    risk_assessment = comprehensive_risk_assessment(stock_code)
    if 'error' in risk_assessment:
        risk_assessment = {'error': '风险评估失败'}
    
    # 组合报告
    report = {
        'code': stock_code,
        'generated_at': datetime.now().isoformat(),
        'basic_info': basic_info,
        'technical_analysis': technical_indicators,
        'trading_signals': trading_signals,
        'trend_prediction': trend_prediction,
        'investment_suggestion': investment_suggestion,
        'risk_assessment': risk_assessment,
        'status': 'success',
        'analysis_type': 'traditional'
    }
    
    return report

def get_market_overview() -> Dict[str, Any]:
    """
    获取市场概览
    
    Returns:
        Dict: 市场概览信息
    
    Example:
        >>> overview = get_market_overview()
        >>> print(overview['total_stocks'])
    """
    if not API_AVAILABLE:
        return {
            'error': 'API服务不可用',
            'suggestion': '请检查服务配置'
        }
    
    try:
        logger.info("开始生成市场概览")
        
        # 获取市场汇总信息
        market_summary = get_market_summary()
        if 'error' in market_summary:
            return market_summary
        
        # 获取服务状态
        service_status = check_service_status()
        
        # 组合市场概览
        overview = {
            'generated_at': datetime.now().isoformat(),
            'market_summary': market_summary,
            'service_status': service_status,
            'status': 'success'
        }
        
        logger.info("市场概览生成完成")
        return overview
        
    except Exception as e:
        logger.error(f"生成市场概览时发生错误: {e}")
        return {
            'error': f'生成市场概览失败: {str(e)}',
            'suggestion': '请检查服务状态'
        }

def search_stocks_with_analysis(keyword: str) -> List[Dict[str, Any]]:
    """
    搜索股票并提供简要分析
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        List[Dict]: 匹配股票的简要分析列表
    
    Example:
        >>> results = search_stocks_with_analysis('平安')
        >>> print(len(results))
    """
    if not API_AVAILABLE:
        return [{
            'error': 'API服务不可用',
            'suggestion': '请检查服务配置'
        }]
    
    try:
        logger.info(f"开始搜索关键词: {keyword}")
        
        # 搜索股票
        search_results = search_stocks(keyword)
        if not search_results or ('error' in search_results[0]):
            return search_results
        
        # 为每个股票生成简要分析
        analyzed_results = []
        for stock in search_results[:10]:  # 限制前10个结果
            if 'error' in stock:
                continue
                
            stock_code = stock.get('code')
            if not stock_code:
                continue
            
            # 获取简要技术信号
            signals = get_trading_signals(stock_code)
            
            # 获取简要投资建议
            suggestion = get_investment_suggestion(stock_code)
            
            analyzed_stock = {
                'basic_info': stock,
                'trading_signals': signals if 'error' not in signals else {'recommendation': 'N/A'},
                'investment_suggestion': suggestion if 'error' not in suggestion else {'action': 'N/A'},
                'status': 'success'
            }
            
            analyzed_results.append(analyzed_stock)
        
        logger.info(f"搜索完成，共找到 {len(analyzed_results)} 个匹配股票")
        return analyzed_results
        
    except Exception as e:
        logger.error(f"搜索股票时发生错误: {e}")
        return [{
            'error': f'搜索股票失败: {str(e)}',
            'keyword': keyword,
            'suggestion': '请检查服务状态'
        }]

def health_check() -> Dict[str, Any]:
    """
    健康检查
    
    Returns:
        Dict: 服务健康状态
    
    Example:
        >>> status = health_check()
        >>> print(status['healthy'])
    """
    if not API_AVAILABLE:
        return {
            'healthy': False,
            'error': 'API服务不可用',
            'suggestion': '请检查服务配置'
        }
    
    try:
        # 检查服务状态
        service_status = check_service_status()
        
        # 检查数据服务
        market_overview = get_market_summary()
        
        healthy = (
            service_status.get('service_available', False) and
            'error' not in market_overview
        )
        
        return {
            'healthy': healthy,
            'service_status': service_status,
            'data_service_status': 'available' if 'error' not in market_overview else 'unavailable',
            'checked_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"健康检查时发生错误: {e}")
        return {
            'healthy': False,
            'error': f'健康检查失败: {str(e)}',
            'suggestion': '请检查服务状态'
        }

# 新增：为定时任务提供接口
def generate_daily_reports(stock_codes: List[str]) -> List[Dict[str, Any]]:
    """
    为定时任务生成多个股票的分析报告
    
    Args:
        stock_codes: 股票代码列表
    
    Returns:
        List[Dict]: 股票分析报告列表
    """
    reports = []
    for stock_code in stock_codes:
        report = get_comprehensive_stock_analysis(stock_code)
        reports.append(report)
    return reports

if __name__ == '__main__':
    # 简单的命令行测试
    logger.info("🔍 主API服务测试")
    logger.info("=" * 50)
    
    # 测试健康检查
    logger.info("\n🩺 服务健康检查:")
    health_result = health_check()
    logger.info(f"  健康状态: {'正常' if health_result.get('healthy') else '异常'}")
    logger.info(f"  数据服务: {health_result.get('data_service_status')}")
    
    # 测试市场概览
    logger.info("\n📊 市场概览:")
    overview_result = get_market_overview()
    if 'error' not in overview_result:
        summary = overview_result.get('market_summary', {})
        logger.info(f"  总股票数: {summary.get('total_count', 'N/A')}")
        logger.info(f"  沪市股票: {summary.get('shanghai_count', 'N/A')}")
        logger.info(f"  深市股票: {summary.get('shenzhen_count', 'N/A')}")
    else:
        logger.error(f"  错误: {overview_result.get('error')}")
    
    # 测试综合分析
    logger.info("\n📈 平安银行综合分析:")
    analysis_result = get_comprehensive_stock_analysis('000001')
    if 'error' not in analysis_result:
        basic_info = analysis_result.get('basic_info', {})
        logger.info(f"  股票名称: {basic_info.get('name', 'N/A')}")
        logger.info(f"  股票代码: {basic_info.get('code', 'N/A')}")
        
        investment_suggestion = analysis_result.get('investment_suggestion', {})
        logger.info(f"  投资建议: {investment_suggestion.get('action', 'N/A')}")
        logger.info(f"  建议理由: {investment_suggestion.get('reason', 'N/A')}")
    else:
        logger.error(f"  错误: {analysis_result.get('error')}")
    
    # 测试股票搜索
    logger.info("\n🔍 搜索'平安'相关股票:")
    search_result = search_stocks_with_analysis('平安')
    if search_result and 'error' not in search_result[0]:
        logger.info(f"  找到 {len(search_result)} 只相关股票")
        for i, stock in enumerate(search_result[:3]):  # 显示前3个结果
            basic_info = stock.get('basic_info', {})
            suggestion = stock.get('investment_suggestion', {})
            logger.info(f"  {i+1}. {basic_info.get('code', 'N/A')} {basic_info.get('name', 'N/A')}"
                       f" - 建议: {suggestion.get('action', 'N/A')}")
    else:
        logger.error(f"  错误: {search_result[0].get('error') if search_result else '未知错误'}")