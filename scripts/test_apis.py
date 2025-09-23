#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
用于测试所有封装的API功能
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('scripts.test_apis')

def test_stock_api():
    """测试股票数据API"""
    logger.info("🔍 测试股票数据API")
    
    try:
        from tradingagents.api import (
            get_stock_info,
            get_all_stocks,
            search_stocks,
            get_market_summary,
            check_service_status
        )
        
        # 测试服务状态
        logger.info("  📊 检查服务状态...")
        status = check_service_status()
        logger.info(f"    服务可用: {status.get('service_available', 'N/A')}")
        
        # 测试获取单个股票信息
        logger.info("  🏢 获取平安银行信息...")
        stock_info = get_stock_info('000001')
        if 'error' not in stock_info:
            logger.info(f"    股票名称: {stock_info.get('name', 'N/A')}")
            logger.info(f"    股票代码: {stock_info.get('code', 'N/A')}")
        else:
            logger.warning(f"    错误: {stock_info.get('error')}")
        
        # 测试搜索功能
        logger.info("  🔍 搜索'平安'相关股票...")
        search_results = search_stocks('平安')
        if search_results and 'error' not in search_results[0]:
            logger.info(f"    找到 {len(search_results)} 只相关股票")
        else:
            logger.warning(f"    搜索失败: {search_results[0].get('error') if search_results else '未知错误'}")
        
        # 测试市场概览
        logger.info("  📈 获取市场概览...")
        market_summary = get_market_summary()
        if 'error' not in market_summary:
            logger.info(f"    总股票数: {market_summary.get('total_count', 'N/A')}")
            logger.info(f"    沪市股票: {market_summary.get('shanghai_count', 'N/A')}")
        else:
            logger.warning(f"    获取失败: {market_summary.get('error')}")
            
        logger.info("✅ 股票数据API测试完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 股票数据API测试失败: {e}")
        return False

def test_technical_analysis_api():
    """测试技术分析API"""
    logger.info("🔍 测试技术分析API")
    
    try:
        from tradingagents.api import (
            calculate_technical_indicators,
            get_trading_signals
        )
        
        # 测试技术指标计算
        logger.info("  📊 计算平安银行技术指标...")
        indicators = calculate_technical_indicators('000001', ['rsi_14', 'macd'])
        if 'error' not in indicators:
            rsi = indicators['indicators'].get('rsi_14', 'N/A')
            macd = indicators['indicators'].get('macd', 'N/A')
            logger.info(f"    RSI(14): {rsi}")
            logger.info(f"    MACD: {macd}")
        else:
            logger.warning(f"    计算失败: {indicators.get('error')}")
        
        # 测试交易信号生成
        logger.info("  📈 生成平安银行交易信号...")
        signals = get_trading_signals('000001')
        if 'error' not in signals:
            recommendation = signals.get('recommendation', 'N/A')
            confidence = signals.get('confidence', 'N/A')
            logger.info(f"    推荐操作: {recommendation}")
            logger.info(f"    置信度: {confidence}")
        else:
            logger.warning(f"    生成失败: {signals.get('error')}")
            
        logger.info("✅ 技术分析API测试完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 技术分析API测试失败: {e}")
        return False

def test_prediction_api():
    """测试预测API"""
    logger.info("🔍 测试预测API")
    
    try:
        from tradingagents.api import (
            predict_stock_trend,
            get_investment_suggestion
        )
        
        # 测试趋势预测
        logger.info("  📈 预测平安银行趋势...")
        prediction = predict_stock_trend('000001', days=3)
        if 'error' not in prediction:
            trend = prediction.get('overall_trend', 'N/A')
            recommendation = prediction.get('recommendation', 'N/A')
            logger.info(f"    总体趋势: {trend}")
            logger.info(f"    推荐操作: {recommendation}")
        else:
            logger.warning(f"    预测失败: {prediction.get('error')}")
        
        # 测试投资建议
        logger.info("  💡 获取平安银行投资建议...")
        suggestion = get_investment_suggestion('000001')
        if 'error' not in suggestion:
            action = suggestion.get('action', 'N/A')
            reason = suggestion.get('reason', 'N/A')
            logger.info(f"    操作建议: {action}")
            logger.info(f"    建议理由: {reason}")
        else:
            logger.warning(f"    获取失败: {suggestion.get('error')}")
            
        logger.info("✅ 预测API测试完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 预测API测试失败: {e}")
        return False

def test_risk_assessment_api():
    """测试风险评估API"""
    logger.info("🔍 测试风险评估API")
    
    try:
        from tradingagents.api import (
            evaluate_market_risk,
            analyze_news_sentiment,
            comprehensive_risk_assessment
        )
        
        # 测试市场风险评估
        logger.info("  📊 评估平安银行市场风险...")
        market_risk = evaluate_market_risk('000001')
        if 'error' not in market_risk:
            risk_level = market_risk.get('risk_level', 'N/A')
            risk_score = market_risk.get('risk_score', 'N/A')
            logger.info(f"    风险等级: {risk_level}")
            logger.info(f"    风险分数: {risk_score}")
        else:
            logger.warning(f"    评估失败: {market_risk.get('error')}")
        
        # 测试新闻情绪分析
        logger.info("  📰 分析平安银行新闻情绪...")
        sentiment = analyze_news_sentiment('000001')
        if 'error' not in sentiment:
            sentiment_level = sentiment.get('sentiment', 'N/A')
            sentiment_score = sentiment.get('sentiment_score', 'N/A')
            logger.info(f"    情绪等级: {sentiment_level}")
            logger.info(f"    情绪分数: {sentiment_score}")
        else:
            logger.warning(f"    分析失败: {sentiment.get('error')}")
        
        # 测试综合风险评估
        logger.info("  📈 平安银行综合风险评估...")
        comprehensive = comprehensive_risk_assessment('000001')
        if 'error' not in comprehensive:
            overall_risk_level = comprehensive.get('overall_risk_level', 'N/A')
            overall_risk_score = comprehensive.get('overall_risk_score', 'N/A')
            logger.info(f"    综合风险等级: {overall_risk_level}")
            logger.info(f"    综合风险分数: {overall_risk_score}")
        else:
            logger.warning(f"    评估失败: {comprehensive.get('error')}")
            
        logger.info("✅ 风险评估API测试完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 风险评估API测试失败: {e}")
        return False

def test_main_api():
    """测试主API服务"""
    logger.info("🔍 测试主API服务")
    
    try:
        from tradingagents.api import (
            get_comprehensive_stock_analysis,
            get_market_overview,
            search_stocks_with_analysis,
            health_check
        )
        
        # 测试健康检查
        logger.info("  🩺 服务健康检查...")
        health = health_check()
        healthy = health.get('healthy', False)
        logger.info(f"    健康状态: {'正常' if healthy else '异常'}")
        
        # 测试市场概览
        logger.info("  📊 获取市场概览...")
        overview = get_market_overview()
        if 'error' not in overview:
            logger.info(f"    概览生成时间: {overview.get('generated_at', 'N/A')}")
        else:
            logger.warning(f"    获取失败: {overview.get('error')}")
        
        # 测试综合分析
        logger.info("  📈 获取平安银行综合分析...")
        comprehensive_analysis = get_comprehensive_stock_analysis('000001')
        if 'error' not in comprehensive_analysis:
            logger.info(f"    报告生成时间: {comprehensive_analysis.get('generated_at', 'N/A')}")
        else:
            logger.warning(f"    获取失败: {comprehensive_analysis.get('error')}")
        
        # 测试股票搜索与分析
        logger.info("  🔍 搜索并分析'平安'相关股票...")
        search_analysis = search_stocks_with_analysis('平安')
        if search_analysis and 'error' not in search_analysis[0]:
            logger.info(f"    找到并分析了 {len(search_analysis)} 只相关股票")
        else:
            logger.warning(f"    搜索失败: {search_analysis[0].get('error') if search_analysis else '未知错误'}")
            
        logger.info("✅ 主API服务测试完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 主API服务测试失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Trading Agents API测试脚本')
    parser.add_argument('--module', choices=['stock', 'technical', 'prediction', 'risk', 'main', 'all'], 
                       default='all', help='指定要测试的模块')
    
    args = parser.parse_args()
    
    logger.info("🚀 开始测试Trading Agents API")
    logger.info("=" * 60)
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"测试模块: {args.module}")
    logger.info("")
    
    test_results = []
    
    # 根据参数测试相应模块
    if args.module in ['stock', 'all']:
        test_results.append(('股票数据API', test_stock_api()))
    
    if args.module in ['technical', 'all']:
        test_results.append(('技术分析API', test_technical_analysis_api()))
    
    if args.module in ['prediction', 'all']:
        test_results.append(('预测API', test_prediction_api()))
    
    if args.module in ['risk', 'all']:
        test_results.append(('风险评估API', test_risk_assessment_api()))
    
    if args.module in ['main', 'all']:
        test_results.append(('主API服务', test_main_api()))
    
    # 输出测试总结
    logger.info("=" * 60)
    logger.info("📋 测试总结")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    
    for module_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{module_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("")
    logger.info(f"总计: {len(test_results)} 个模块")
    logger.info(f"通过: {passed} 个模块")
    logger.info(f"失败: {failed} 个模块")
    logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed == 0:
        logger.info("🎉 所有测试通过!")
        return 0
    else:
        logger.error("💥 部分测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())