#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试使用DeepSeek进行深度分析
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('test_with_deepseek')

def test_deepseek_analysis(stock_code):
    """
    测试使用DeepSeek进行深度分析
    """
    logger.info(f"开始测试使用DeepSeek分析股票 {stock_code}")
    
    try:
        # 使用DeepSeek配置
        from tradingagents.api.main_api import get_comprehensive_stock_analysis
        
        # 保存原始配置
        original_provider = os.getenv("DEFAULT_LLM_PROVIDER", "modelscope")
        original_deep_model = os.getenv("DEEP_THINK_LLM", "ZhipuAI/GLM-4.6")
        original_quick_model = os.getenv("QUICK_THINK_LLM", "ZhipuAI/GLM-4.6")
        
        # 设置DeepSeek配置
        os.environ["DEFAULT_LLM_PROVIDER"] = "deepseek"
        os.environ["DEEP_THINK_LLM"] = "deepseek-chat"
        os.environ["QUICK_THINK_LLM"] = "deepseek-chat"
        
        logger.info("已切换到DeepSeek配置")
        logger.info(f"DEEPSEEK_API_KEY: {os.getenv('DEEPSEEK_API_KEY', '未设置')[:10]}...")
        
        # 执行分析
        report = get_comprehensive_stock_analysis(stock_code)
        
        # 恢复原始配置
        os.environ["DEFAULT_LLM_PROVIDER"] = original_provider
        os.environ["DEEP_THINK_LLM"] = original_deep_model
        os.environ["QUICK_THINK_LLM"] = original_quick_model
        
        if 'error' in report:
            logger.error(f"❌ 股票 {stock_code} 分析失败: {report['error']}")
            return report
        else:
            logger.info(f"✅ 股票 {stock_code} 分析完成")
            analysis_type = report.get('analysis_type', 'unknown')
            logger.info(f"   分析类型: {analysis_type}")
            
            return report
    
    except Exception as e:
        logger.error(f"❌ 分析股票 {stock_code} 时发生异常: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return {'error': str(e)}

if __name__ == "__main__":
    test_stock = '000001'
    logger.info("🚀 开始测试使用DeepSeek进行深度分析")
    result = test_deepseek_analysis(test_stock)
    logger.info("🏁 DeepSeek深度分析测试完成")