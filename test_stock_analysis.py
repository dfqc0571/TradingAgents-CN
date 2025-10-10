#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票分析功能
用于验证股票分析是否能正常运行并输出正确结果
"""

import sys
import os
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('test_stock_analysis')

# 导入API模块
try:
    from tradingagents.api.main_api import get_comprehensive_stock_analysis
    API_AVAILABLE = True
    logger.info("✅ API模块导入成功")
except ImportError as e:
    logger.error(f"❌ API模块导入失败: {e}")
    API_AVAILABLE = False

def test_stock_analysis(stock_codes):
    """
    测试股票分析功能
    
    Args:
        stock_codes: 股票代码列表
    """
    if not API_AVAILABLE:
        logger.error("❌ API服务不可用，无法进行测试")
        return
    
    logger.info(f"开始测试股票分析功能，测试股票: {stock_codes}")
    
    reports = []
    for stock_code in stock_codes:
        logger.info(f"🔄 正在分析股票: {stock_code}")
        try:
            report = get_comprehensive_stock_analysis(stock_code)
            reports.append(report)
            
            if 'error' in report:
                logger.error(f"❌ 股票 {stock_code} 分析失败: {report['error']}")
            else:
                logger.info(f"✅ 股票 {stock_code} 分析完成")
                # 输出关键信息
                basic_info = report.get('basic_info', {})
                logger.info(f"   股票名称: {basic_info.get('name', 'N/A')}")
                logger.info(f"   股票代码: {report.get('code', 'N/A')}")
                logger.info(f"   最新价格: {basic_info.get('price', 'N/A')}")
                logger.info(f"   分析类型: {report.get('analysis_type', 'N/A')}")
                
                # 检查关键分析内容是否存在
                market_report = report.get('market_report', '')
                news_report = report.get('news_report', '')
                fundamentals_report = report.get('fundamentals_report', '')
                final_trade_decision = report.get('final_trade_decision', '')
                
                logger.info(f"   市场报告: {'存在' if market_report else '缺失'}")
                logger.info(f"   新闻报告: {'存在' if news_report else '缺失'}")
                logger.info(f"   基本面报告: {'存在' if fundamentals_report else '缺失'}")
                logger.info(f"   交易决策: {'存在' if final_trade_decision else '缺失'}")
                
        except Exception as e:
            logger.error(f"❌ 分析股票 {stock_code} 时发生异常: {e}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
    
    # 保存报告到文件
    output_file = os.path.join(project_root, 'test_analysis_report.json')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        logger.info(f"📝 分析报告已保存到: {output_file}")
    except Exception as e:
        logger.error(f"❌ 保存报告失败: {e}")
    
    return reports

if __name__ == "__main__":
    # 测试两只股票的分析
    test_stocks = ['000001', '000002']  # 平安银行和万科A
    logger.info("🚀 开始测试股票分析功能")
    test_stock_analysis(test_stocks)
    logger.info("🏁 股票分析测试完成")