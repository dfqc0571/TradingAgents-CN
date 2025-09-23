# API 增强功能实现方案

## 1. 错误处理增强

### 1.1 技术分析API错误处理改进

在 [technical_analysis_api.py](file://d:\TradingAgents-CN\tradingagents\api\technical_analysis_api.py#L0-L299) 中增强错误处理机制：

```python
try:
    # 现有代码
    stock_data = get_china_stock_data_unified(stock_code, start_date, end_date)
    if not stock_data or "error" in stock_data:
        logger.error(f"获取股票数据失败: {stock_code}")
        return {
            "error": "股票数据获取失败",
            "code": stock_code,
            "suggestion": "请检查股票代码或稍后重试"
        }
    
    # 增强stockstats处理错误捕获
    try:
        stock = stockstats.StockDataFrame.retype(stock_data)
        # ... 技术指标计算逻辑
    except Exception as e:
        logger.error(f"技术指标计算失败: {str(e)}")
        return {
            "error": f"技术指标计算失败: {str(e)}",
            "code": stock_code,
            "suggestion": "数据格式可能不兼容，请联系技术支持"
        }
        
except Exception as e:
    logger.error(f"技术分析过程中发生未预期错误: {str(e)}")
    return {
        "error": f"技术分析失败: {str(e)}",
        "code": stock_code,
        "suggestion": "系统内部错误，请稍后重试"
    }
```

### 1.2 预测API错误处理改进

在 [prediction_api.py](file://d:\TradingAgents-CN\tradingagents\api\prediction_api.py#L0-L236) 中增强错误处理：

```python
try:
    # 获取股票数据
    from tradingagents.utils.stock_utils import StockUtils
    if StockUtils.is_china_stock(stock_code):
        stock_data = get_china_stock_data_unified(stock_code, start_date, end_date)
        if isinstance(stock_data, dict) and 'error' in stock_data:
            logger.error(f"预测API获取股票数据失败: {stock_data['error']}")
            return stock_data
    
    # 预测逻辑
    # ...
    
except Exception as e:
    logger.error(f"预测股票趋势时发生错误: {e}")
    return {
        'error': f'预测股票趋势失败: {str(e)}',
        'code': stock_code,
        'suggestion': '请检查股票代码和数据源'
    }
```

### 1.3 风险评估API错误处理改进

在 [risk_assessment_api.py](file://d:\TradingAgents-CN\tradingagents\api\risk_assessment_api.py#L0-L306) 中增强错误处理：

```python
try:
    # 获取股票市场信息
    market_info = StockUtils.get_market_info(stock_code)
    
    # 风险评估逻辑
    # ...
    
except Exception as e:
    logger.error(f"评估市场风险时发生错误: {e}")
    return {
        'error': f'评估市场风险失败: {str(e)}',
        'code': stock_code,
        'suggestion': '请检查股票代码'
    }
```

## 2. 性能优化（缓存机制）

### 2.1 缓存实现方案

引入Redis作为缓存存储，为API添加缓存机制：

```python
# 在 utils/cache_utils.py 中实现缓存工具
import redis
import json
import hashlib
from typing import Any, Optional
from tradingagents.utils.logging_init import get_logger

logger = get_logger('utils.cache')

class CacheManager:
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            self.enabled = True
        except Exception as e:
            logger.warning(f"Redis连接失败，缓存功能将禁用: {e}")
            self.enabled = False
    
    def _generate_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        key_str = f"{prefix}:{':'.join(map(str, args))}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if not self.enabled:
            return None
            
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"获取缓存数据失败: {e}")
        return None
    
    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """设置缓存数据"""
        if not self.enabled:
            return False
            
        try:
            self.redis_client.setex(key, expire, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"设置缓存数据失败: {e}")
            return False

# 全局缓存管理器实例
cache_manager = CacheManager()
```

### 2.2 在API中使用缓存

在技术分析API中添加缓存：

```python
# 在 calculate_technical_indicators 函数中
def calculate_technical_indicators(stock_code: str, indicators: List[str] = None) -> Dict[str, Any]:
    # 生成缓存键
    cache_key = cache_manager._generate_key("technical_indicators", stock_code, str(indicators))
    
    # 尝试从缓存获取数据
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        logger.info(f"从缓存获取技术指标数据: {stock_code}")
        return cached_result
    
    # ... 现有逻辑 ...
    
    # 保存结果到缓存
    cache_manager.set(cache_key, result, expire=300)  # 5分钟缓存
    return result
```

## 3. 安全加固

### 3.1 API认证机制

为FastAPI添加JWT认证：

```python
# 在 api/web_api.py 中
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

# JWT配置
SECRET_KEY = "your-secret-key"  # 应该从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict):
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证访问令牌"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 为需要认证的路由添加依赖
@app.get("/stock/{stock_code}/technical-analysis")
def technical_analysis(
    stock_code: str, 
    indicators: Optional[str] = None,
    payload: dict = Depends(verify_token)  # 添加认证依赖
):
    """获取股票技术分析（需要认证）"""
    # ... 现有逻辑 ...
```

### 3.2 API密钥管理

添加API密钥配置：

```python
# 在 config/api_config.py 中
import os
from typing import List

class APIConfig:
    # JWT配置
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API密钥白名单
    ALLOWED_API_KEYS = os.getenv("ALLOWED_API_KEYS", "").split(",")
    
    # 请求频率限制
    RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))  # 每分钟请求数
    RATE_LIMIT_WINDOW = 60  # 秒

api_config = APIConfig()
```

## 4. 实施建议

### 4.1 分阶段实施

1. **第一阶段：错误处理增强**
   - 完善各API模块的异常处理
   - 统一错误响应格式
   - 增强日志记录

2. **第二阶段：性能优化**
   - 实现缓存管理器
   - 为高频API添加缓存机制
   - 监控缓存命中率和性能提升

3. **第三阶段：安全加固**
   - 实现JWT认证机制
   - 添加API密钥管理
   - 实施请求频率限制

### 4.2 测试验证

每个阶段完成后都需要进行充分测试：

```python
# 测试错误处理
def test_error_handling():
    # 测试无效股票代码
    result = calculate_technical_indicators("INVALID")
    assert "error" in result
    
    # 测试网络异常情况
    # ...

# 测试缓存功能
def test_caching():
    # 第一次调用
    result1 = calculate_technical_indicators("000001")
    
    # 第二次调用应该从缓存获取
    result2 = calculate_technical_indicators("000001")
    
    assert result1 == result2

# 测试安全认证
def test_authentication():
    # 测试无认证访问被拒绝
    # 测试有效令牌访问成功
    # ...
```

## 5. 配置要求

### 5.1 环境变量配置

```
# .env 文件配置示例
SECRET_KEY=your-very-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_API_KEYS=key1,key2,key3
API_RATE_LIMIT=100

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 5.2 依赖包更新

在 `pyproject.toml` 中添加必要依赖：

```toml
[dependencies]
# 现有依赖...
redis = "^4.0.0"
PyJWT = "^2.0.0"
```

## 6. 总结

这些API增强功能将显著提升系统的稳定性、性能和安全性。通过分阶段实施，可以确保每个改进都经过充分测试，不会对现有功能产生负面影响。Web端将从这些改进中直接受益，获得更好的用户体验。