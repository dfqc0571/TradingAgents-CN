"""
Trading Agents API模块
提供股票分析和交易决策支持系统的API接口
"""

from .stock_api import (
    get_stock_info,
    get_all_stocks,
    get_stock_data,
    search_stocks,
    get_market_summary,
    check_service_status
)

from .technical_analysis_api import (
    calculate_technical_indicators,
    get_trading_signals
)

from .prediction_api import (
    predict_stock_trend,
    get_investment_suggestion
)

from .risk_assessment_api import (
    evaluate_market_risk,
    analyze_news_sentiment,
    comprehensive_risk_assessment
)

from .main_api import (
    get_comprehensive_stock_analysis,
    get_market_overview,
    search_stocks_with_analysis,
    health_check
)

__all__ = [
    # 基础股票数据API
    'get_stock_info',
    'get_all_stocks',
    'get_stock_data',
    'search_stocks',
    'get_market_summary',
    'check_service_status',
    
    # 技术分析API
    'calculate_technical_indicators',
    'get_trading_signals',
    
    # 预测API
    'predict_stock_trend',
    'get_investment_suggestion',
    
    # 风险评估API
    'evaluate_market_risk',
    'analyze_news_sentiment',
    'comprehensive_risk_assessment',
    
    # 综合API
    'get_comprehensive_stock_analysis',
    'get_market_overview',
    'search_stocks_with_analysis',
    'health_check'
]