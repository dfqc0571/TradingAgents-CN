"""
TradingAgents-CN RESTful API
基于FastAPI的股票分析API服务
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('api')

# 导入环境变量
from dotenv import load_dotenv
load_dotenv(project_root / ".env", override=True)

# 导入自定义模块
from .n8n_integration import router as n8n_router
from tradingagents.graph.n8n_optimized_graph import create_n8n_optimized_graph

# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents-CN API",
    description="基于多智能体LLM的中文金融交易决策框架API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(n8n_router)

# 健康检查端点
@app.get("/api/health")
async def health_check():
    """
    健康检查端点
    
    Returns:
        健康状态信息
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TradingAgents-CN RESTful API"
    }

# 股票分析API端点
@app.get("/api/v1/analyze/{stock_code}")
async def analyze_stock(
    stock_code: str,
    analysis_date: Optional[str] = None,
    depth: int = 3,
    optimization_level: str = "medium"
):
    """
    分析单只股票的投资价值
    
    Args:
        stock_code: 股票代码
        analysis_date: 分析日期 (格式: YYYY-MM-DD)
        depth: 分析深度 (1-5)
        optimization_level: 优化级别 ("high", "medium", "low")
        
    Returns:
        分析结果
    """
    try:
        logger.info(f"🔍 开始分析股票 {stock_code}")
        
        # 创建优化版分析器
        analyzer = create_n8n_optimized_graph(optimization_level)
        
        # 执行分析
        result = analyzer.analyze_stock(
            stock_code=stock_code,
            depth=depth
        )
        
        return {
            "status": "completed",
            "analysis_id": f"analysis_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "recommendation": result.get("recommendation", "HOLD"),
            "confidence": result.get("confidence", 0.5),
            "target_price": result.get("target_price", 0),
            "risk_level": result.get("risk_level", "MEDIUM"),
            "alerts": result.get("alerts", []),
            "reports": result
        }
        
    except Exception as e:
        logger.error(f"❌ 分析股票 {stock_code} 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 实时监控API端点
@app.get("/api/v1/monitor/alerts/{stock_pool}")
async def monitor_alerts(
    stock_pool: str,
    alert_types: Optional[List[str]] = None
):
    """
    实时监控股票池中的风险警报
    
    Args:
        stock_pool: 股票池名称或股票代码列表
        alert_types: 警报类型过滤器
        
    Returns:
        检测到的警报列表
    """
    try:
        logger.info(f"🚨 开始监控股票池 {stock_pool}")
        
        # 解析股票池
        if "," in stock_pool:
            stocks = stock_pool.split(",")
        else:
            # 这里可以实现从预定义股票池获取股票列表的逻辑
            stocks = [stock_pool]
        
        # 模拟风险检测逻辑
        alerts = []
        for stock in stocks:
            # 这里应该实现实际的风险检测逻辑
            # 暂时返回模拟数据
            alerts.append({
                "type": "MAJOR_NEWS",
                "severity": "HIGH",
                "stock": stock,
                "message": f"检测到 {stock} 的重大新闻",
                "timestamp": datetime.now().isoformat()
            })
        
        # 根据警报类型过滤
        if alert_types:
            alerts = [alert for alert in alerts if alert["type"] in alert_types]
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"❌ 监控股票池 {stock_pool} 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 批量分析API端点
@app.post("/api/v1/batch-analyze")
async def batch_analyze(
    stock_pool: List[str],
    schedule: str = "daily",
    optimization_level: str = "medium",
    notification_webhook: Optional[str] = None
):
    """
    批量分析股票池
    
    Args:
        stock_pool: 股票代码列表
        schedule: 分析计划 ("daily", "weekly", "monthly")
        optimization_level: 优化级别 ("high", "medium", "low")
        notification_webhook: 通知Webhook URL
        
    Returns:
        批量分析结果
    """
    try:
        logger.info(f"📊 开始批量分析 {len(stock_pool)} 只股票")
        
        # 创建优化版分析器
        analyzer = create_n8n_optimized_graph(optimization_level)
        
        # 执行批量分析
        result = analyzer.batch_analyze(
            stock_pool=stock_pool,
            schedule=schedule
        )
        
        # 如果提供了通知Webhook，发送通知
        if notification_webhook:
            # 这里应该实现发送通知的逻辑
            logger.info(f"🔔 准备发送通知到 {notification_webhook}")
        
        return {
            "status": "completed",
            "analysis_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis_count": len(stock_pool),
            "schedule": schedule,
            "optimization_level": optimization_level,
            "results": result["results"]
        }
        
    except Exception as e:
        logger.error(f"❌ 批量分析时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )