"""
实时监控模块
实现防黑天鹅功能，包括新闻监控、技术指标预警和基本面异常检测
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re

from tradingagents.utils.logging_manager import get_logger
from tradingagents.dataflows.interface import get_stock_news, get_stock_data

logger = get_logger(__name__)

class BlackSwanMonitor:
    """黑天鹅事件监控器"""
    
    def __init__(self):
        # 关键词列表
        self.policy_keywords = [
            "政策", "监管", "法规", "禁令", "限制", "补贴", "税收", "关税"
        ]
        
        self.emergency_keywords = [
            "突发事件", "紧急", "危机", "灾难", "事故", "召回", "诉讼"
        ]
        
        self.market_sentiment_keywords = [
            "恐慌", "暴跌", "崩盘", "抄底", "抄底", "爆仓", "熔断"
        ]
        
        # 技术指标阈值
        self.volatility_threshold = 0.05  # 波动率阈值 5%
        self.volume_spike_threshold = 2.0  # 成交量激增阈值 2倍
        self.breakdown_threshold = 0.03    # 技术破位阈值 3%
    
    async def monitor_news(self, stock_code: str) -> List[Dict[str, Any]]:
        """
        监控股票相关新闻
        
        Args:
            stock_code: 股票代码
            
        Returns:
            检测到的新闻警报列表
        """
        alerts = []
        try:
            # 获取最近15分钟内的新闻
            news_list = await get_stock_news(
                stock_code, 
                start_date=(datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d")
            )
            
            for news in news_list:
                alert = self._analyze_news(news, stock_code)
                if alert:
                    alerts.append(alert)
                    
        except Exception as e:
            logger.error(f"❌ 监控股票 {stock_code} 新闻时出错: {e}")
            
        return alerts
    
    def _analyze_news(self, news: Dict[str, Any], stock_code: str) -> Optional[Dict[str, Any]]:
        """
        分析单条新闻是否包含风险信号
        
        Args:
            news: 新闻数据
            stock_code: 股票代码
            
        Returns:
            警报信息或None
        """
        title = news.get("title", "").lower()
        content = news.get("content", "").lower()
        publish_time = news.get("publish_time", "")
        
        # 检查是否包含政策关键词
        for keyword in self.policy_keywords:
            if keyword in title or keyword in content:
                return {
                    "type": "POLICY_CHANGE",
                    "severity": "HIGH",
                    "stock": stock_code,
                    "message": f"检测到政策相关消息: {keyword}",
                    "timestamp": publish_time,
                    "source": news.get("source", ""),
                    "url": news.get("url", "")
                }
        
        # 检查是否包含紧急事件关键词
        for keyword in self.emergency_keywords:
            if keyword in title or keyword in content:
                return {
                    "type": "EMERGENCY_EVENT",
                    "severity": "CRITICAL",
                    "stock": stock_code,
                    "message": f"检测到紧急事件: {keyword}",
                    "timestamp": publish_time,
                    "source": news.get("source", ""),
                    "url": news.get("url", "")
                }
        
        # 检查市场恐慌情绪
        for keyword in self.market_sentiment_keywords:
            if keyword in title or keyword in content:
                return {
                    "type": "MARKET_PANIC",
                    "severity": "HIGH",
                    "stock": stock_code,
                    "message": f"检测到市场恐慌情绪: {keyword}",
                    "timestamp": publish_time,
                    "source": news.get("source", ""),
                    "url": news.get("url", "")
                }
        
        return None
    
    async def monitor_technical_indicators(self, stock_code: str) -> List[Dict[str, Any]]:
        """
        监控技术指标异常
        
        Args:
            stock_code: 股票代码
            
        Returns:
            检测到的技术指标警报列表
        """
        alerts = []
        try:
            # 获取股票数据
            stock_data = await get_stock_data(stock_code, period="5d")
            if len(stock_data) < 2:
                return alerts
                
            # 计算波动率
            volatility = self._calculate_volatility(stock_data)
            if volatility > self.volatility_threshold:
                alerts.append({
                    "type": "HIGH_VOLATILITY",
                    "severity": "MEDIUM",
                    "stock": stock_code,
                    "message": f"检测到异常波动，波动率: {volatility:.2%}",
                    "timestamp": datetime.now().isoformat(),
                    "value": volatility
                })
            
            # 检查成交量激增
            volume_spike = self._check_volume_spike(stock_data)
            if volume_spike > self.volume_spike_threshold:
                alerts.append({
                    "type": "VOLUME_SPIKE",
                    "severity": "MEDIUM",
                    "stock": stock_code,
                    "message": f"检测到成交量激增 {volume_spike:.1f} 倍",
                    "timestamp": datetime.now().isoformat(),
                    "value": volume_spike
                })
            
            # 检查技术破位
            breakdown = self._check_technical_breakdown(stock_data)
            if breakdown < -self.breakdown_threshold:
                alerts.append({
                    "type": "TECHNICAL_BREAKDOWN",
                    "severity": "HIGH",
                    "stock": stock_code,
                    "message": f"检测到技术破位，跌幅: {abs(breakdown):.2%}",
                    "timestamp": datetime.now().isoformat(),
                    "value": breakdown
                })
                
        except Exception as e:
            logger.error(f"❌ 监控股票 {stock_code} 技术指标时出错: {e}")
            
        return alerts
    
    def _calculate_volatility(self, stock_data: List[Dict[str, Any]]) -> float:
        """计算波动率"""
        if len(stock_data) < 2:
            return 0
            
        # 计算每日收益率
        returns = []
        for i in range(1, len(stock_data)):
            prev_close = stock_data[i-1]["close"]
            curr_close = stock_data[i]["close"]
            if prev_close > 0:
                returns.append((curr_close - prev_close) / prev_close)
        
        if not returns:
            return 0
            
        # 计算标准差作为波动率
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        return variance ** 0.5
    
    def _check_volume_spike(self, stock_data: List[Dict[str, Any]]) -> float:
        """检查成交量激增"""
        if len(stock_data) < 2:
            return 0
            
        current_volume = stock_data[-1]["volume"]
        previous_volume = stock_data[-2]["volume"]
        
        if previous_volume > 0:
            return current_volume / previous_volume
        return 0
    
    def _check_technical_breakdown(self, stock_data: List[Dict[str, Any]]) -> float:
        """检查技术破位"""
        if len(stock_data) < 2:
            return 0
            
        current_close = stock_data[-1]["close"]
        previous_close = stock_data[-2]["close"]
        
        if previous_close > 0:
            return (current_close - previous_close) / previous_close
        return 0
    
    async def monitor_fundamentals(self, stock_code: str) -> List[Dict[str, Any]]:
        """
        监控基本面异常
        
        Args:
            stock_code: 股票代码
            
        Returns:
            检测到的基本面警报列表
        """
        alerts = []
        try:
            # 这里应该实现实际的基本面监控逻辑
            # 例如检查财报异常、高管变动、重大合作等
            # 暂时返回模拟数据
            
            # 模拟财报异常检测
            alerts.append({
                "type": "FINANCIAL_REPORT",
                "severity": "MEDIUM",
                "stock": stock_code,
                "message": "检测到财报发布，建议关注",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ 监控股票 {stock_code} 基本面时出错: {e}")
            
        return alerts
    
    async def monitor_stock(self, stock_code: str) -> List[Dict[str, Any]]:
        """
        综合监控单只股票的所有风险
        
        Args:
            stock_code: 股票代码
            
        Returns:
            所有检测到的警报列表
        """
        # 并发执行所有监控任务
        news_alerts, tech_alerts, fund_alerts = await asyncio.gather(
            self.monitor_news(stock_code),
            self.monitor_technical_indicators(stock_code),
            self.monitor_fundamentals(stock_code),
            return_exceptions=True
        )
        
        # 处理异常情况
        all_alerts = []
        for alerts in [news_alerts, tech_alerts, fund_alerts]:
            if isinstance(alerts, Exception):
                logger.error(f"❌ 监控过程中发生异常: {alerts}")
            elif isinstance(alerts, list):
                all_alerts.extend(alerts)
        
        return all_alerts


# 全局监控器实例
black_swan_monitor = BlackSwanMonitor()


def get_black_swan_monitor() -> BlackSwanMonitor:
    """获取全局黑天鹅监控器实例"""
    return black_swan_monitor