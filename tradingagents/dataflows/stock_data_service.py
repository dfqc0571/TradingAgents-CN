#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的股票数据获取服务
实现MongoDB -> Tushare数据接口的完整降级机制
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

try:
    from tradingagents.config.database_manager import get_database_manager
    DATABASE_MANAGER_AVAILABLE = True
except ImportError:
    DATABASE_MANAGER_AVAILABLE = False

try:
    from .tdx_utils import get_tdx_provider, TongDaXinDataProvider
    TDX_AVAILABLE = True
except ImportError:
    TDX_AVAILABLE = False

try:
    from .akshare_utils import get_akshare_provider, AKShareProvider
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import sys
    import os
    # 添加utils目录到路径
    utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'utils')
    if utils_path not in sys.path:
        sys.path.append(utils_path)
    from enhanced_stock_list_fetcher import enhanced_fetch_stock_list
    ENHANCED_FETCHER_AVAILABLE = True
except ImportError:
    ENHANCED_FETCHER_AVAILABLE = False

logger = logging.getLogger(__name__)

class StockDataService:
    """
    统一的股票数据获取服务
    实现完整的降级机制：MongoDB -> Tushare数据接口 -> 缓存 -> 错误处理
    """
    
    def __init__(self):
        self.db_manager = None
        self.tdx_provider = None
        self.akshare_provider = None
        self._init_services()
    
    def _init_services(self):
        """初始化服务"""
        # 尝试初始化数据库管理器
        if DATABASE_MANAGER_AVAILABLE:
            try:
                self.db_manager = get_database_manager()
                if self.db_manager.is_mongodb_available():
                    logger.info(f"✅ MongoDB连接成功")
                else:
                    logger.error(f"⚠️ MongoDB连接失败，将使用Tushare数据接口")
            except Exception as e:
                logger.error(f"⚠️ 数据库管理器初始化失败: {e}")
                self.db_manager = None
        
        # 尝试初始化通达信提供器
        if TDX_AVAILABLE:
            try:
                self.tdx_provider = get_tdx_provider()
                logger.info(f"✅ Tushare数据接口初始化成功")
            except Exception as e:
                logger.error(f"⚠️ Tushare数据接口初始化失败: {e}")
                self.tdx_provider = None
        
        # 尝试初始化AKShare提供器
        if AKSHARE_AVAILABLE:
            try:
                self.akshare_provider = get_akshare_provider()
                logger.info(f"✅ AKShare数据接口初始化成功")
            except Exception as e:
                logger.error(f"⚠️ AKShare数据接口初始化失败: {e}")
                self.akshare_provider = None
    
    def get_stock_basic_info(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """
        获取股票基础信息（单个股票或全部股票）
        
        Args:
            stock_code: 股票代码，如果为None则返回所有股票
        
        Returns:
            Dict: 股票基础信息
        """
        logger.info(f"📊 获取股票基础信息: {stock_code or '全部股票'}")
        
        # 1. 优先从MongoDB获取
        if self.db_manager and self.db_manager.is_mongodb_available():
            try:
                result = self._get_from_mongodb(stock_code)
                if result:
                    logger.info(f"✅ 从MongoDB获取成功: {len(result) if isinstance(result, list) else 1}条记录")
                    return result
            except Exception as e:
                logger.error(f"⚠️ MongoDB查询失败: {e}")
        
        # 2. 优先使用AKShare（如果可用且配置为默认数据源）
        logger.info(f"🔄 MongoDB不可用，检查是否使用AKShare")
        if self.akshare_provider is not None and os.getenv('DEFAULT_CHINA_DATA_SOURCE', '').lower() == 'akshare':
            try:
                result = self._get_from_akshare(stock_code)
                if result:
                    logger.info(f"✅ 从AKShare获取成功: {len(result) if isinstance(result, list) else 1}条记录")
                    # 尝试缓存到MongoDB（如果可用）
                    self._cache_to_mongodb(result)
                    return result
            except Exception as e:
                logger.error(f"⚠️ AKShare查询失败: {e}")
        else:
            logger.info(f"🔄 AKShare不可用或未配置为默认数据源")
        
        # 3. 降级到Tushare数据接口
        logger.info(f"🔄 降级到Tushare数据接口")
        if self.tdx_provider is not None:
            try:
                result = self._get_from_tdx_api(stock_code)
                if result:
                    logger.info(f"✅ 从Tushare数据接口获取成功: {len(result) if isinstance(result, list) else 1}条记录")
                    # 尝试缓存到MongoDB（如果可用）
                    self._cache_to_mongodb(result)
                    return result
            except Exception as e:
                logger.error(f"⚠️ Tushare数据接口查询失败: {e}")
        
        # 4. 最后的降级方案
        logger.error(f"❌ 所有数据源都不可用")
        return self._get_fallback_data(stock_code)
    
    def _get_from_mongodb(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """从MongoDB获取数据"""
        try:
            mongodb_client = self.db_manager.get_mongodb_client()
            if not mongodb_client:
                return None

            db = mongodb_client[self.db_manager.mongodb_config["database"]]
            collection = db['stock_basic_info']

            if stock_code:
                # 获取单个股票
                result = collection.find_one({'code': stock_code})
                return result if result else None
            else:
                # 获取所有股票
                cursor = collection.find({})
                results = list(cursor)
                return results if results else None

        except Exception as e:
            logger.error(f"MongoDB查询失败: {e}")
            return None
    
    def _get_from_tdx_api(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """从Tushare数据接口获取数据"""
        try:
            if stock_code:
                # 获取单个股票信息
                if self.tdx_provider:
                    # 使用现有的股票名称获取方法
                    stock_name = self.tdx_provider._get_stock_name(stock_code)
                    return {
                        'code': stock_code,
                        'name': stock_name,
                        'market': self._get_market_name(stock_code),
                        'category': self._get_stock_category(stock_code),
                        'source': 'tdx_api',
                        'updated_at': datetime.now().isoformat()
                    }
            else:
                # 获取所有股票列表
                stock_df = enhanced_fetch_stock_list(
                    type_='stock',
                    enable_server_failover=True,
                    max_retries=3
                )
                
                if stock_df is not None and not stock_df.empty:
                    # 转换为字典列表
                    results = []
                    for _, row in stock_df.iterrows():
                        results.append({
                            'code': row.get('code', ''),
                            'name': row.get('name', ''),
                            'market': row.get('market', ''),
                            'category': row.get('category', ''),
                            'source': 'tdx_api',
                            'updated_at': datetime.now().isoformat()
                        })
                    return results
                    
        except Exception as e:
            logger.error(f"Tushare数据接口查询失败: {e}")
            return None

    def _get_from_akshare(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """从AKShare获取数据"""
        try:
            if stock_code:
                # 获取单个股票信息
                if self.akshare_provider:
                    stock_info = self.akshare_provider.get_stock_info(stock_code)
                    if stock_info:
                        return {
                            'code': stock_code,
                            'name': stock_info.get('name', f'股票{stock_code}'),
                            'market': self._get_market_name(stock_code),
                            'category': self._get_stock_category(stock_code),
                            'source': 'akshare',
                            'updated_at': datetime.now().isoformat()
                        }
            else:
                # 获取所有股票列表
                # 注意：AKShare没有直接获取所有股票列表的API，所以我们降级到Tushare
                stock_df = enhanced_fetch_stock_list(
                    type_='stock',
                    enable_server_failover=True,
                    max_retries=3
                )
                
                if stock_df is not None and not stock_df.empty:
                    # 转换为字典列表
                    results = []
                    for _, row in stock_df.iterrows():
                        results.append({
                            'code': row.get('code', ''),
                            'name': row.get('name', ''),
                            'market': row.get('market', ''),
                            'category': row.get('category', ''),
                            'source': 'akshare_enhanced',
                            'updated_at': datetime.now().isoformat()
                        })
                    return results
                    
        except Exception as e:
            logger.error(f"AKShare查询失败: {e}")
            return None
    
    def _cache_to_mongodb(self, data: Any) -> bool:
        """将数据缓存到MongoDB"""
        if not self.db_manager or not self.db_manager.get_mongodb_client():
            return False
        
        try:
            mongodb_client = self.db_manager.get_mongodb_client()
            if not mongodb_client:
                return False
                
            db = mongodb_client[self.db_manager.mongodb_config["database"]]
            collection = db['stock_basic_info']
            
            if isinstance(data, list):
                # 批量插入
                for item in data:
                    collection.update_one(
                        {'code': item['code']},
                        {'$set': item},
                        upsert=True
                    )
                logger.info(f"💾 已缓存{len(data)}条记录到MongoDB")
            elif isinstance(data, dict):
                # 单条插入
                collection.update_one(
                    {'code': data['code']},
                    {'$set': data},
                    upsert=True
                )
                logger.info(f"💾 已缓存股票{data['code']}到MongoDB")
            
            return True
            
        except Exception as e:
            logger.error(f"缓存到MongoDB失败: {e}")
            return False
    
    def _get_fallback_data(self, stock_code: str = None) -> Dict[str, Any]:
        """最后的降级数据"""
        if stock_code:
            return {
                'code': stock_code,
                'name': f'股票{stock_code}',
                'market': self._get_market_name(stock_code),
                'category': '未知',
                'source': 'fallback',
                'updated_at': datetime.now().isoformat(),
                'error': '所有数据源都不可用'
            }
        else:
            return {
                'error': '无法获取股票列表，请检查网络连接和数据库配置',
                'suggestion': '请确保MongoDB已配置或网络连接正常以访问Tushare数据接口'
            }
    
    def _get_market_name(self, stock_code: str) -> str:
        """根据股票代码判断市场"""
        if stock_code.startswith(('60', '68', '90')):
            return '上海'
        elif stock_code.startswith(('00', '30', '20')):
            return '深圳'
        else:
            return '未知'
    
    def _get_stock_category(self, stock_code: str) -> str:
        """根据股票代码判断类别"""
        if stock_code.startswith('60'):
            return '沪市主板'
        elif stock_code.startswith('68'):
            return '科创板'
        elif stock_code.startswith('00'):
            return '深市主板'
        elif stock_code.startswith('30'):
            return '创业板'
        elif stock_code.startswith('20'):
            return '深市B股'
        else:
            return '其他'
    
    def get_stock_data_with_fallback(self, stock_code: str, start_date: str, end_date: str) -> str:
        """
        获取股票数据（带降级机制）
        这是对现有get_china_stock_data函数的增强
        """
        logger.info(f"📊 获取股票数据: {stock_code} ({start_date} 到 {end_date})")
        
        # 首先确保股票基础信息可用
        stock_info = self.get_stock_basic_info(stock_code)
        if stock_info and 'error' in stock_info:
            return f"❌ 无法获取股票{stock_code}的基础信息: {stock_info.get('error', '未知错误')}"
        
        # 优先使用AKShare获取数据（如果配置为默认数据源）
        if AKSHARE_AVAILABLE and os.getenv('DEFAULT_CHINA_DATA_SOURCE', '').lower() == 'akshare':
            try:
                if self.akshare_provider:
                    # 使用AKShare获取股票数据
                    data = self.akshare_provider.get_stock_data(stock_code, start_date, end_date)
                    if data is not None and not data.empty:
                        # 格式化数据为字符串
                        return self._format_akshare_stock_data(stock_code, data, start_date, end_date)
            except Exception as e:
                logger.warning(f"⚠️ AKShare获取股票数据失败: {e}")
        
        # 调用现有的get_china_stock_data函数
        try:
            from .tdx_utils import get_china_stock_data

            return get_china_stock_data(stock_code, start_date, end_date)
        except Exception as e:
            return f"❌ 获取股票数据失败: {str(e)}\n\n💡 建议：\n1. 检查网络连接\n2. 确认股票代码格式正确\n3. 检查MongoDB配置"

    def _format_akshare_stock_data(self, stock_code: str, data: pd.DataFrame, start_date: str, end_date: str) -> str:
        """
        格式化AKShare股票数据为文本格式
        
        Args:
            stock_code: 股票代码
            data: 股票数据DataFrame
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            str: 格式化的股票数据文本
        """
        if data is None or data.empty:
            return f"❌ 无法获取股票 {stock_code} 的AKShare数据"

        try:
            # 获取股票基本信息
            stock_name = f'股票{stock_code}'  # 默认名称
            if self.akshare_provider:
                stock_info = self.akshare_provider.get_stock_info(stock_code)
                stock_name = stock_info.get('name', f'股票{stock_code}')
            
            # 计算统计信息
            latest_price = data['收盘'].iloc[-1]
            price_change = data['收盘'].iloc[-1] - data['收盘'].iloc[0]
            price_change_pct = (price_change / data['收盘'].iloc[0]) * 100

            avg_volume = data['成交量'].mean() if '成交量' in data.columns else 0
            max_price = data['最高'].max()
            min_price = data['最低'].min()

            # 格式化输出
            formatted_text = f"""
📊 股票数据报告 (AKShare)
================

股票信息:
- 代码: {stock_code}
- 名称: {stock_name}
- 市场: {self._get_market_name(stock_code)}

价格信息:
- 最新价格: ¥{latest_price:.2f}
- 期间涨跌: ¥{price_change:+.2f} ({price_change_pct:+.2f}%)
- 期间最高: ¥{max_price:.2f}
- 期间最低: ¥{min_price:.2f}

交易信息:
- 数据期间: {start_date} 至 {end_date}
- 交易天数: {len(data)}天
- 平均成交量: {avg_volume:,.0f}股

最近5个交易日:
"""

            # 添加最近5天的数据
            recent_data = data.tail(5)
            for _, row in recent_data.iterrows():
                formatted_text += f"- {row['日期']}: 开盘¥{row['开盘']:.2f}, 收盘¥{row['收盘']:.2f}, 成交量{row['成交量']:,.0f}\n"

            formatted_text += f"\n数据来源: AKShare\n"

            return formatted_text

        except Exception as e:
            logger.error(f"❌ 格式化AKShare股票数据失败: {e}")
            return f"❌ AKShare股票数据格式化失败: {stock_code}"

# 全局服务实例
_stock_data_service = None

def get_stock_data_service() -> StockDataService:
    """获取股票数据服务实例（单例模式）"""
    global _stock_data_service
    if _stock_data_service is None:
        _stock_data_service = StockDataService()
    return _stock_data_service