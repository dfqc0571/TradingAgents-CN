"""
N8N集成API端点
提供专为N8N工作流优化的API接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import asyncio
import uuid
from datetime import datetime

from tradingagents.graph.n8n_optimized_graph import create_n8n_optimized_graph
from tradingagents.utils.logging_manager import get_logger
from .monitoring import get_black_swan_monitor

logger = get_logger(__name__)

# 创建API路由
router = APIRouter(prefix="/n8n", tags=["N8N Integration"])

class StockAnalysisRequest(BaseModel):
    """股票分析请求模型"""
    stock_code: str
    depth: int = 3
    analysis_date: Optional[str] = None
    optimization_level: str = "medium"

class BatchAnalysisRequest(BaseModel):
    """批量分析请求模型"""
    stock_pool: List[str]
    schedule: str = "daily"
    optimization_level: str = "medium"
    notification_webhook: Optional[str] = None

class AnalysisResponse(BaseModel):
    """分析响应模型"""
    status: str
    analysis_id: str
    timestamp: str
    result: Dict[str, Any]

class MonitorRequest(BaseModel):
    """监控请求模型"""
    stock_pool: List[str]
    alert_types: Optional[List[str]] = None

class MonitorResponse(BaseModel):
    """监控响应模型"""
    status: str
    timestamp: str
    alerts: List[Dict[str, Any]]

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """
    分析单只股票的投资价值（N8N优化版）
    
    Args:
        request: 股票分析请求
        
    Returns:
        分析结果
    """
    analysis_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        logger.info(f"🔍 [N8N API] 开始分析股票 {request.stock_code}")
        
        # 创建优化版分析器
        analyzer = create_n8n_optimized_graph(request.optimization_level)
        
        # 执行分析
        result = analyzer.analyze_stock(
            stock_code=request.stock_code,
            depth=request.depth
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [N8N API] 股票 {request.stock_code} 分析完成，耗时 {processing_time:.2f} 秒")
        
        return AnalysisResponse(
            status="completed",
            analysis_id=analysis_id,
            timestamp=datetime.now().isoformat(),
            result=result
        )
        
    except Exception as e:
        logger.error(f"❌ [N8N API] 分析股票 {request.stock_code} 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-analyze", response_model=AnalysisResponse)
async def batch_analyze(request: BatchAnalysisRequest):
    """
    批量分析股票池（N8N优化版）
    
    Args:
        request: 批量分析请求
        
    Returns:
        批量分析结果
    """
    analysis_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        logger.info(f"📊 [N8N API] 开始批量分析 {len(request.stock_pool)} 只股票")
        
        # 创建优化版分析器
        analyzer = create_n8n_optimized_graph(request.optimization_level)
        
        # 执行批量分析
        result = analyzer.batch_analyze(
            stock_pool=request.stock_pool,
            schedule=request.schedule
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [N8N API] 批量分析完成，耗时 {processing_time:.2f} 秒")
        
        return AnalysisResponse(
            status="completed",
            analysis_id=analysis_id,
            timestamp=datetime.now().isoformat(),
            result=result
        )
        
    except Exception as e:
        logger.error(f"❌ [N8N API] 批量分析时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitor", response_model=MonitorResponse)
async def monitor_stocks(request: MonitorRequest):
    """
    实时监控股票池中的风险警报
    
    Args:
        request: 监控请求
        
    Returns:
        检测到的警报列表
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"🚨 [N8N API] 开始监控股票池 {len(request.stock_pool)} 只股票")
        
        # 获取监控器实例
        monitor = get_black_swan_monitor()
        
        # 并发监控所有股票
        tasks = [monitor.monitor_stock(stock) for stock in request.stock_pool]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并所有警报
        all_alerts = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ 监控过程中发生异常: {result}")
            elif isinstance(result, list):
                all_alerts.extend(result)
        
        # 根据警报类型过滤
        if request.alert_types:
            all_alerts = [alert for alert in all_alerts if alert["type"] in request.alert_types]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [N8N API] 监控完成，检测到 {len(all_alerts)} 个警报，耗时 {processing_time:.2f} 秒")
        
        return MonitorResponse(
            status="completed",
            timestamp=datetime.now().isoformat(),
            alerts=all_alerts
        )
        
    except Exception as e:
        logger.error(f"❌ [N8N API] 监控时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    Returns:
        健康状态信息
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TradingAgents-CN N8N Integration API"
    }