#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web API服务
使用FastAPI提供RESTful API接口
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger('api.web')

# 导入所有API功能
try:
    from tradingagents.api.main_api import (
        get_comprehensive_stock_analysis,
        get_market_overview,
        search_stocks_with_analysis,
        health_check
    )
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
    # 导入定时任务模块
    from tradingagents.scheduled_tasks.daily_report import run_scheduler
    
    WEB_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Web API模块部分功能不可用: {e}")
    WEB_API_AVAILABLE = False

# 初始化FastAPI应用
app = FastAPI(
    title="Trading Agents API",
    description="股票分析和交易决策支持系统的API接口",
    version="1.0.0"
)

# 定义数据模型
class StockAnalysisResponse(BaseModel):
    code: str
    generated_at: str
    basic_info: dict
    technical_analysis: dict
    trading_signals: dict
    trend_prediction: dict
    investment_suggestion: dict
    risk_assessment: dict
    status: str

class MarketOverviewResponse(BaseModel):
    generated_at: str
    market_summary: dict
    service_status: dict
    status: str

class HealthCheckResponse(BaseModel):
    healthy: bool
    service_status: dict
    data_service_status: str
    checked_at: str

# API路由定义
@app.get("/")
def read_root():
    """根路径，返回API信息"""
    return {
        "message": "Trading Agents API",
        "version": "1.0.0",
        "description": "股票分析和交易决策支持系统的API接口"
    }

@app.get("/health", response_model=HealthCheckResponse)
def health():
    """健康检查接口"""
    result = health_check()
    if not result.get('healthy', False):
        raise HTTPException(status_code=503, detail=result.get('error', 'Service unavailable'))
    return result

@app.get("/market/overview", response_model=MarketOverviewResponse)
def market_overview():
    """获取市场概览"""
    result = get_market_overview()
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    return result

@app.get("/stock/{stock_code}/basic-info")
def stock_basic_info(stock_code: str):
    """获取股票基础信息"""
    result = get_stock_info(stock_code)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return result

@app.get("/stock/{stock_code}/technical-analysis")
def technical_analysis(stock_code: str, indicators: Optional[str] = None):
    """获取股票技术分析"""
    indicator_list = indicators.split(',') if indicators else None
    result = calculate_technical_indicators(stock_code, indicator_list)
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    return result

@app.get("/stock/{stock_code}/trading-signals")
def trading_signals(stock_code: str):
    """获取股票交易信号"""
    result = get_trading_signals(stock_code)
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    return result

@app.get("/stock/{stock_code}/prediction")
def stock_prediction(stock_code: str, days: int = 5):
    """获取股票趋势预测"""
    result = predict_stock_trend(stock_code, days)
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    return result

@app.get("/stock/{stock_code}/investment-suggestion")
def investment_suggestion(stock_code: str):
    """获取投资建议"""
    result = get_investment_suggestion(stock_code)
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    return result

@app.get("/stock/{stock_code}/risk-assessment")
def risk_assessment(stock_code: str):
    """获取风险评估"""
    result = comprehensive_risk_assessment(stock_code)
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    return result

@app.get("/stock/{stock_code}/comprehensive-analysis", response_model=StockAnalysisResponse)
def comprehensive_analysis(stock_code: str):
    """获取股票综合分析报告"""
    result = get_comprehensive_stock_analysis(stock_code)
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    return result

@app.get("/stock/search")
def search_stock(keyword: str = Query(..., min_length=1, max_length=50)):
    """搜索股票"""
    result = search_stocks_with_analysis(keyword)
    if result and 'error' in result[0]:
        raise HTTPException(status_code=500, detail=result[0]['error'])
    return result

@app.get("/stock/list")
def list_all_stocks():
    """获取所有股票列表"""
    result = get_all_stocks()
    if result and 'error' in result[0]:
        raise HTTPException(status_code=500, detail=result[0]['error'])
    return result

@app.post("/scheduler/start")
def start_scheduler():
    """启动定时任务调度器"""
    try:
        scheduler_thread = run_scheduler()
        return {"message": "定时任务调度器已启动", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """启动API服务器"""
    logger.info(f"🚀 启动Trading Agents API服务器 - http://{host}:{port}")
    uvicorn.run("tradingagents.api.web_api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    # 启动API服务器
    start_server()