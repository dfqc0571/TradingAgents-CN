# Trading Agents API 文档

## 概述

Trading Agents API 提供了完整的股票分析和交易决策支持功能。该API基于FastAPI构建，提供RESTful接口，支持多种股票市场（A股、港股、美股）的分析功能。

## API基础信息

- **基础URL**: `http://localhost:8000` (默认)
- **API文档**: `http://localhost:8000/docs` (Swagger UI)
- **API文档**: `http://localhost:8000/redoc` (ReDoc)

## 认证

当前版本API无需认证，但在生产环境中建议添加API密钥认证机制。

## 错误处理

API使用标准HTTP状态码来表示请求结果：
- `200`: 请求成功
- `404`: 请求的资源未找到
- `500`: 服务器内部错误
- `503`: 服务不可用

## API端点

### 1. 健康检查

#### GET `/health`
检查API服务健康状态

**响应示例**:
```json
{
  "healthy": true,
  "service_status": {
    "database": "connected",
    "data_service": "available"
  },
  "data_service_status": "All data sources available",
  "checked_at": "2023-01-01T00:00:00"
}
```

### 2. 市场概览

#### GET `/market/overview`
获取市场概览信息

**响应示例**:
```json
{
  "generated_at": "2023-01-01T00:00:00",
  "market_summary": {
    "total_stocks": 1000,
    "shanghai_composite": 3000.0,
    "shenzhen_component": 11000.0,
    "growth_stocks": 600,
    "decline_stocks": 400
  },
  "service_status": {
    "database": "connected",
    "data_service": "available"
  },
  "status": "success"
}
```

### 3. 股票基础信息

#### GET `/stock/{stock_code}/basic-info`
获取指定股票的基础信息

**路径参数**:
- `stock_code` (string, required): 股票代码，如 "000001"

**响应示例**:
```json
{
  "code": "000001",
  "name": "平安银行",
  "market": "A股",
  "currency": "CNY",
  "status": "success"
}
```

### 4. 技术分析

#### GET `/stock/{stock_code}/technical-analysis`
获取股票技术指标分析

**路径参数**:
- `stock_code` (string, required): 股票代码

**查询参数**:
- `indicators` (string, optional): 指标列表，用逗号分隔，如 "rsi_14,macd"

**响应示例**:
```json
{
  "code": "000001",
  "date": "2023-01-01",
  "rsi_14": 55.5,
  "macd": 0.25,
  "boll_ub": 15.5,
  "boll_lb": 14.2,
  "close_20_sma": 14.8,
  "status": "success"
}
```

### 5. 交易信号

#### GET `/stock/{stock_code}/trading-signals`
获取股票交易信号

**路径参数**:
- `stock_code` (string, required): 股票代码

**响应示例**:
```json
{
  "code": "000001",
  "date": "2023-01-01",
  "signals": [
    {
      "name": "MACD Signal",
      "value": "BUY",
      "strength": 0.8
    },
    {
      "name": "RSI Signal",
      "value": "HOLD",
      "strength": 0.6
    }
  ],
  "overall_signal": "BUY",
  "confidence": 0.75,
  "status": "success"
}
```

### 6. 趋势预测

#### GET `/stock/{stock_code}/prediction`
获取股票趋势预测

**路径参数**:
- `stock_code` (string, required): 股票代码

**查询参数**:
- `days` (integer, optional, default=5): 预测天数

**响应示例**:
```json
{
  "code": "000001",
  "current_date": "2023-01-01",
  "prediction_period": "5天",
  "predictions": [
    {
      "date": "2023-01-02",
      "price": 15.2,
      "change_percent": 2.5,
      "confidence": 0.8
    }
  ],
  "overall_trend": "MODERATE_UP",
  "recommendation": "HOLD",
  "avg_change_percent": 1.2,
  "confidence": 0.75,
  "status": "success"
}
```

### 7. 投资建议

#### GET `/stock/{stock_code}/investment-suggestion`
获取股票投资建议

**路径参数**:
- `stock_code` (string, required): 股票代码

**响应示例**:
```json
{
  "code": "000001",
  "date": "2023-01-01",
  "action": "BUY",
  "reasons": [
    "技术指标显示买入信号",
    "基本面分析良好"
  ],
  "risk_level": "MODERATE",
  "target_price": 16.5,
  "stop_loss": 14.0,
  "confidence": 0.8,
  "status": "success"
}
```

### 8. 市场风险评估

#### GET `/stock/{stock_code}/market-risk`
评估股票市场风险

**路径参数**:
- `stock_code` (string, required): 股票代码

**响应示例**:
```json
{
  "code": "000001",
  "date": "2023-01-01",
  "market": "A股",
  "risk_score": 0.6,
  "risk_level": "MODERATE",
  "description": "中等风险",
  "factors": {
    "market_volatility": 0.7,
    "sector_risk": 0.5,
    "liquidity_risk": 0.4
  },
  "status": "success"
}
```

### 9. 新闻情绪分析

#### GET `/stock/{stock_code}/news-sentiment`
分析股票相关新闻情绪

**路径参数**:
- `stock_code` (string, required): 股票代码

**查询参数**:
- `days` (integer, optional, default=7): 分析天数

**响应示例**:
```json
{
  "code": "000001",
  "date": "2023-01-01",
  "market": "A股",
  "sentiment_score": 0.2,
  "sentiment_label": "POSITIVE",
  "description": "积极情绪",
  "news_count": 15,
  "positive_news": 9,
  "negative_news": 3,
  "neutral_news": 3,
  "key_topics": [
    "业绩增长",
    "行业政策"
  ],
  "status": "success"
}
```

### 10. 综合风险评估

#### GET `/stock/{stock_code}/comprehensive-risk`
获取股票综合风险评估

**路径参数**:
- `stock_code` (string, required): 股票代码

**响应示例**:
```json
{
  "code": "000001",
  "date": "2023-01-01",
  "market_risk": {
    "risk_score": 0.6,
    "risk_level": "MODERATE"
  },
  "news_sentiment": {
    "sentiment_score": 0.2,
    "sentiment_label": "POSITIVE"
  },
  "overall_risk": "MODERATE",
  "recommendation": "可以考虑投资，但需注意风险控制",
  "status": "success"
}
```

### 11. 综合股票分析

#### GET `/stock/{stock_code}/comprehensive-analysis`
获取股票综合分析报告

**路径参数**:
- `stock_code` (string, required): 股票代码

**响应示例**:
```json
{
  "code": "000001",
  "generated_at": "2023-01-01T00:00:00",
  "basic_info": {
    "code": "000001",
    "name": "平安银行",
    "market": "A股",
    "currency": "CNY",
    "status": "success"
  },
  "technical_analysis": {
    // 技术分析结果
  },
  "trading_signals": {
    // 交易信号结果
  },
  "trend_prediction": {
    // 趋势预测结果
  },
  "investment_suggestion": {
    // 投资建议结果
  },
  "risk_assessment": {
    // 风险评估结果
  },
  "status": "success"
}
```

## 数据源优先级

API使用统一的数据接口获取股票数据，数据源优先级如下：

### A股数据源优先级
1. **AKShare** (第一优先级)
2. **Tushare** (第二优先级)
3. **BaoStock** (第三优先级)
4. **TDX** (第四优先级)

### 港股数据源优先级
1. **AKShare** (优先) - 国内数据源，港股支持更好
2. **Yahoo Finance** (备用) - 国际数据源
3. **默认格式** (降级) - 确保可用性

## 错误响应格式

所有错误响应都遵循以下格式：

```json
{
  "error": "错误描述",
  "code": "股票代码(如果适用)",
  "suggestion": "建议解决方案"
}
```

## 性能优化

API实现了以下性能优化措施：
1. **数据缓存**: 对频繁访问的数据进行缓存，提高响应速度
2. **连接池**: 数据库连接使用连接池管理，减少连接开销
3. **异步处理**: 支持异步处理长时间运行的任务

## 安全考虑

在生产环境中，建议实施以下安全措施：
1. **API密钥认证**: 为API访问添加认证机制
2. **速率限制**: 防止API被恶意滥用
3. **输入验证**: 对所有输入参数进行严格验证
4. **日志审计**: 记录所有API访问日志，便于安全审计

## 使用示例

### Python示例
```python
import requests

# 获取股票综合分析报告
response = requests.get("http://localhost:8000/stock/000001/comprehensive-analysis")
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"请求失败: {response.status_code}")
```

### JavaScript示例
```javascript
// 获取股票技术分析
fetch('http://localhost:8000/stock/000001/technical-analysis')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```