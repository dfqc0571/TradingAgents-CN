#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术分析API接口
提供股票技术指标计算和分析功能
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import io

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('api.technical_analysis')

# 导入技术分析工具
try:
    from tradingagents.dataflows.stockstats_utils import StockstatsUtils
    from tradingagents.dataflows.interface import get_china_stock_data_unified
    TECHNICAL_ANALYSIS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ 技术分析模块不可用: {e}")
    TECHNICAL_ANALYSIS_AVAILABLE = False

def calculate_technical_indicators(
    stock_code: str, 
    indicators: List[str] = None,
    date: str = None,
    data_dir: str = None
) -> Dict[str, Any]:
    """
    计算股票技术指标
    
    Args:
        stock_code: 股票代码
        indicators: 需要计算的技术指标列表，默认为常用的指标
        date: 计算指标的日期，默认为今天
        data_dir: 数据目录路径
    
    Returns:
        Dict: 技术指标计算结果
    
    Example:
        >>> result = calculate_technical_indicators('000001', ['rsi_14', 'macd'])
        >>> print(result['rsi_14'])
    """
    if not TECHNICAL_ANALYSIS_AVAILABLE:
        return {
            'error': '技术分析模块不可用',
            'code': stock_code,
            'suggestion': '请检查模块依赖'
        }
    
    try:
        # 默认指标
        if indicators is None:
            indicators = ['rsi_14', 'macd', 'boll_ub', 'boll_lb', 'close_20_sma']
        
        # 默认日期为今天
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
        
        # 如果是中国股票，使用统一数据接口
        from tradingagents.utils.stock_utils import StockUtils
        if StockUtils.is_china_stock(stock_code):
            # 获取中国股票数据
            stock_data_str = get_china_stock_data_unified(stock_code, start_date, end_date)
            if isinstance(stock_data_str, dict) and 'error' in stock_data_str:
                return stock_data_str
            
            # 解析数据为DataFrame
            try:
                # 将字符串转换为DataFrame
                lines = stock_data_str.strip().split('\n')
                # 跳过标题行，找到数据开始的位置
                data_lines = []
                for line in lines:
                    if line.strip() and not line.startswith('日期') and not line.startswith('='):
                        # 假设数据行包含日期格式
                        if '-' in line and ':' not in line:  # 排除时间行
                            data_lines.append(line)
                
                if not data_lines:
                    return {
                        'error': '无法解析股票数据',
                        'code': stock_code,
                        'suggestion': '数据格式不正确'
                    }
                
                # 构造CSV格式数据
                csv_data = "Date,Open,High,Low,Close,Volume\n"
                for line in data_lines:
                    parts = line.split()
                    if len(parts) >= 6:
                        # 重新组织数据格式
                        csv_data += f"{parts[0]},{parts[1]},{parts[2]},{parts[3]},{parts[4]},{parts[5]}\n"
                
                # 读取为DataFrame
                stock_data = pd.read_csv(io.StringIO(csv_data))
                
            except Exception as parse_error:
                logger.error(f"解析股票数据时发生错误: {parse_error}")
                return {
                    'error': f'解析股票数据失败: {str(parse_error)}',
                    'code': stock_code,
                    'suggestion': '请检查数据源'
                }
            
            # 保存数据到临时CSV文件
            if data_dir is None:
                data_dir = os.path.join(project_root, 'data')
                os.makedirs(data_dir, exist_ok=True)
            
            temp_file = os.path.join(data_dir, f'{stock_code}_temp.csv')
            stock_data.to_csv(temp_file, index=False)
            
            # 计算技术指标
            results = {}
            for indicator in indicators:
                try:
                    value = StockstatsUtils.get_stock_stats(
                        symbol=stock_code,
                        indicator=indicator,
                        curr_date=date,
                        data_dir=data_dir,
                        online=False
                    )
                    results[indicator] = value
                except Exception as e:
                    logger.warning(f"计算指标 {indicator} 失败: {e}")
                    results[indicator] = None
            
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return {
                'code': stock_code,
                'date': date,
                'indicators': results,
                'status': 'success'
            }
        else:
            # 其他市场股票使用在线数据
            results = {}
            for indicator in indicators:
                try:
                    value = StockstatsUtils.get_stock_stats(
                        symbol=stock_code,
                        indicator=indicator,
                        curr_date=date,
                        data_dir=data_dir or '.',
                        online=True
                    )
                    results[indicator] = value
                except Exception as e:
                    logger.warning(f"计算指标 {indicator} 失败: {e}")
                    results[indicator] = None
            
            return {
                'code': stock_code,
                'date': date,
                'indicators': results,
                'status': 'success'
            }
            
    except Exception as e:
        logger.error(f"计算技术指标时发生错误: {e}")
        return {
            'error': f'计算技术指标失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码和数据源'
        }

def get_trading_signals(stock_code: str, date: str = None) -> Dict[str, Any]:
    """
    根据技术指标生成交易信号
    
    Args:
        stock_code: 股票代码
        date: 分析日期，默认为今天
    
    Returns:
        Dict: 交易信号和建议
    
    Example:
        >>> signals = get_trading_signals('000001')
        >>> print(signals['recommendation'])
    """
    if not TECHNICAL_ANALYSIS_AVAILABLE:
        return {
            'error': '技术分析模块不可用',
            'code': stock_code,
            'suggestion': '请检查模块依赖'
        }
    
    try:
        # 默认日期为今天
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算关键指标
        indicators_result = calculate_technical_indicators(
            stock_code=stock_code,
            indicators=['rsi_14', 'macd', 'boll_ub', 'boll_lb', 'close_20_sma'],
            date=date
        )
        
        if 'error' in indicators_result:
            return indicators_result
        
        indicators = indicators_result['indicators']
        
        # 解析指标值
        rsi = indicators.get('rsi_14')
        macd_line = indicators.get('macd')
        # 简化处理，实际应用中需要更复杂的逻辑
        
        # 生成交易信号
        signals = {
            'code': stock_code,
            'date': date,
            'rsi': rsi,
            'macd': macd_line,
            'signals': {},
            'recommendation': 'HOLD',  # 默认持有
            'confidence': 0.5
        }
        
        # RSI信号
        if isinstance(rsi, (int, float)):
            if rsi < 30:
                signals['signals']['rsi'] = 'OVERSOLD'
                signals['recommendation'] = 'BUY'
                signals['confidence'] = 0.8
            elif rsi > 70:
                signals['signals']['rsi'] = 'OVERBOUGHT'
                signals['recommendation'] = 'SELL'
                signals['confidence'] = 0.8
            else:
                signals['signals']['rsi'] = 'NEUTRAL'
        
        # MACD信号
        if isinstance(macd_line, (int, float)):
            if macd_line > 0:
                signals['signals']['macd'] = 'BULLISH'
                if signals['recommendation'] == 'BUY':
                    signals['confidence'] = 0.9
            elif macd_line < 0:
                signals['signals']['macd'] = 'BEARISH'
                if signals['recommendation'] == 'SELL':
                    signals['confidence'] = 0.9
        
        return signals
        
    except Exception as e:
        logger.error(f"生成交易信号时发生错误: {e}")
        return {
            'error': f'生成交易信号失败: {str(e)}',
            'code': stock_code,
            'suggestion': '请检查股票代码和数据源'
        }

if __name__ == '__main__':
    # 简单的命令行测试
    logger.info("🔍 技术分析API测试")
    logger.info("=" * 50)
    
    # 测试计算技术指标
    logger.info("\n📊 计算平安银行技术指标:")
    indicators_result = calculate_technical_indicators('000001', ['rsi_14', 'macd'])
    if 'error' not in indicators_result:
        for indicator, value in indicators_result['indicators'].items():
            logger.info(f"  {indicator}: {value}")
    else:
        logger.error(f"  错误: {indicators_result.get('error')}")
    
    # 测试生成交易信号
    logger.info("\n📈 生成平安银行交易信号:")
    signals_result = get_trading_signals('000001')
    if 'error' not in signals_result:
        logger.info(f"  推荐操作: {signals_result.get('recommendation')}")
        logger.info(f"  置信度: {signals_result.get('confidence')}")
        logger.info(f"  RSI: {signals_result.get('rsi')}")
        logger.info(f"  MACD: {signals_result.get('macd')}")
    else:
        logger.error(f"  错误: {signals_result.get('error')}")