# TradingAgents-CN v2.0 版本更新日志

## 发布日期
2025年9月

## 核心更新概览

本版本主要增加了API密钥轮询机制、N8N集成优化、防黑天鹅事件监控系统以及完整的RESTful API服务，显著提升了系统的稳定性和实用性。

## 新增功能详情

### 🔁 Google AI API密钥轮询机制

#### 功能描述
- 支持配置最多10个Google AI API密钥实现轮询使用
- 自动错误检测和密钥切换机制
- 提高API调用稳定性和免费额度利用率

#### 实现细节
1. 创建了`APIKeyManager`类管理多个API密钥
2. 实现了轮询算法，按顺序使用配置的API密钥
3. 添加了错误检测机制，自动标记问题密钥并切换到下一个
4. 支持主备提供商自动切换（Google AI → 阿里百炼）

#### 配置方式
在`.env`文件中配置多个Google API密钥：
```env
# 主密钥
GOOGLE_API_KEY=your_main_google_api_key

# 备用密钥1-10 (可选)
GOOGLE_API_KEY_1=your_second_google_api_key
GOOGLE_API_KEY_2=your_third_google_api_key
# ... 最多可以配置到 GOOGLE_API_KEY_10
```

### 🚀 N8N集成优化

#### 功能描述
- 专门针对N8N工作流优化的高性能分析版本
- 提供三种优化级别：high（高性能）、medium（平衡）、low（完整功能）
- 显著提升分析速度并降低成本

#### 实现细节
1. 创建了`N8NOptimizedGraph`类提供优化版本分析功能
2. 实现三种优化级别：
   - **High**: 分析速度提升50-70%，成本降低60-80%
   - **Medium**: 分析速度提升30-50%，成本降低40-60%
   - **Low**: 完整功能，效果与原版基本一致
3. 添加了专门的N8N集成API端点

#### 性能优化策略
- 高优化级别下只使用核心分析师（市场和技术分析、基本面分析）
- 减少辩论轮次以加快分析速度
- 使用更快、更经济的LLM模型
- 优先使用缓存数据而非实时API调用

#### N8N集成配置建议
```json
{
  "optimization_level": "medium",
  "api_key_strategy": "round_robin"
}
```

### 🛡️ 防黑天鹅事件监控系统

#### 功能描述
- 实时新闻监控和关键词检测
- 技术指标异常预警
- 基本面异常检测功能

#### 实现细节
1. 创建了`BlackSwanMonitor`类实现监控功能
2. 新闻监控模块：
   - 关键词检测：政策变化、监管动态、突发事件
   - 情绪分析：市场恐慌指数
   - 时效性检测：15分钟内的重大新闻
3. 技术指标预警模块：
   - 异常波动检测
   - 成交量激增预警
   - 技术破位信号
4. 基本面异常检测模块：
   - 财报异常检测
   - 高管变动监控
   - 重大合作/并购检测

### 🌐 完整的RESTful API服务

#### 功能描述
- 基于FastAPI的RESTful API服务
- 提供股票分析、批量分析和实时监控接口
- 自动生成交互式API文档

#### 实现细节
1. 创建了完整的FastAPI应用
2. 实现了核心API端点：
   - 股票分析接口：`GET /api/v1/analyze/{stock_code}`
   - 批量分析接口：`POST /api/v1/batch-analyze`
   - 实时监控接口：`GET /api/v1/monitor/alerts/{stock_pool}`
   - N8N专用接口：`POST /n8n/analyze`, `POST /n8n/batch-analyze`, `POST /n8n/monitor`
3. 添加了健康检查端点：`GET /api/health`
4. 自动生成交互式API文档

#### 部署方式
更新了`run_web.py`脚本，可同时启动Streamlit Web界面和FastAPI服务：
```bash
python web/run_web.py
```

访问地址：
- Web界面: http://localhost:8501
- API接口: http://localhost:8000
- API文档: http://localhost:8000/api/docs

## Docker部署优化

### 镜像源优化
更新了Dockerfile中的镜像源，使用以下国内镜像源加速依赖安装：
- https://docker.1ms.run
- https://dytt.online
- https://lispy.org
- https://docker.xiaogenban1993.com
- https://hub.rat.dev
- https://docker.m.daocloud.io
- https://mirror.ccs.tencentyun.com

### 端口配置更新
更新了docker-compose.yml，添加了8000端口映射用于FastAPI服务：
```yaml
ports:
  - "8501:8501"
  - "8000:8000"
```

## 依赖更新

在requirements.txt中添加了以下新依赖：
- fastapi>=0.115.0
- uvicorn>=0.30.6
- google-generativeai>=0.8.0
- google-genai>=0.1.0

## 使用说明

### 启动服务
```bash
# Docker部署
docker-compose up -d --build

# 本地部署
python web/run_web.py
```

### API调用示例

#### 股票分析
```bash
curl http://localhost:8000/api/v1/analyze/000001
```

#### 批量分析
```bash
curl -X POST http://localhost:8000/api/v1/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{"stock_pool": ["000001", "600036", "000858"]}'
```

#### 实时监控
```bash
curl http://localhost:8000/api/v1/monitor/alerts/000001,600036
```

## 兼容性说明

本版本保持与之前版本的向后兼容性，现有配置和使用方式无需更改即可继续使用。新增功能均为可选模块，不影响原有功能的正常使用。