#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试深度分析功能
用于验证是否能正确使用智能体进行股票分析
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
logger = get_logger('test_deep_analysis')

# 导入API模块
try:
    from tradingagents.api.main_api import get_comprehensive_stock_analysis
    API_AVAILABLE = True
    logger.info("✅ API模块导入成功")
except ImportError as e:
    logger.error(f"❌ API模块导入失败: {e}")
    API_AVAILABLE = False

def test_deep_analysis(stock_code):
    """
    测试深度分析功能
    
    Args:
        stock_code: 股票代码
    """
    if not API_AVAILABLE:
        logger.error("❌ API服务不可用，无法进行测试")
        return
    
    logger.info(f"开始测试股票 {stock_code} 的深度分析功能")
    
    try:
        # 执行综合分析
        report = get_comprehensive_stock_analysis(stock_code)
        
        if 'error' in report:
            logger.error(f"❌ 股票 {stock_code} 分析失败: {report['error']}")
            return report
        else:
            logger.info(f"✅ 股票 {stock_code} 分析完成")
            analysis_type = report.get('analysis_type', 'unknown')
            logger.info(f"   分析类型: {analysis_type}")
            
            # 检查是否包含深度分析特有的字段
            investment_debate = report.get('investment_debate_state', {})
            risk_debate = report.get('risk_debate_state', {})
            market_report = report.get('market_report', '')
            news_report = report.get('news_report', '')
            fundamentals_report = report.get('fundamentals_report', '')
            
            logger.info(f"   投资辩论状态: {'存在' if investment_debate else '缺失'}")
            logger.info(f"   风险辩论状态: {'存在' if risk_debate else '缺失'}")
            logger.info(f"   市场报告: {'存在' if market_report else '缺失'}")
            logger.info(f"   新闻报告: {'存在' if news_report else '缺失'}")
            logger.info(f"   基本面报告: {'存在' if fundamentals_report else '缺失'}")
            
            # 保存报告到文件
            output_file = os.path.join(project_root, f'test_deep_analysis_{stock_code}.json')
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                logger.info(f"📝 分析报告已保存到: {output_file}")
            except Exception as e:
                logger.error(f"❌ 保存报告失败: {e}")
            
            return report
    
    except Exception as e:
        logger.error(f"❌ 分析股票 {stock_code} 时发生异常: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return {'error': str(e)}

if __name__ == "__main__":
    # 测试一只股票的深度分析
    test_stock = '000001'  # 平安银行
    logger.info("🚀 开始测试深度分析功能")
    result = test_deep_analysis(test_stock)
    logger.info("🏁 深度分析测试完成")
    
    if result and 'error' not in result:
        print("\n分析报告摘要:")
        print(f"股票代码: {result.get('code', 'N/A')}")
        print(f"分析类型: {result.get('analysis_type', 'N/A')}")
        print(f"投资建议: {result.get('investment_suggestion', {}).get('action', 'N/A')}")
        print(f"风险等级: {result.get('risk_assessment', {}).get('overall_risk_level', 'N/A')}")