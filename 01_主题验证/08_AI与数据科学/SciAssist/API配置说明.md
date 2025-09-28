# API配置使用说明

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install aiohttp asyncio xml

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 2. API密钥申请

#### PubMed API Key 申请
1. 访问: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
2. 填写邮箱和机构信息
3. 获取API Key后更新配置:
```python
# 在 api_integration_example.py 中修改:
self.your_email = "your_email@hospital.com"    # 替换为实际邮箱
self.api_key = "YOUR_NCBI_API_KEY"              # 替换为实际API Key
```

#### ClinicalTrials.gov
- 无需API Key，直接使用

#### Semantic Scholar
- 无需API Key，但建议添加User-Agent标识

### 3. 运行测试

```bash
cd /Users/williamsun/Downloads/documents/01_主题验证/08_AI与数据科学/SciAssist/
python3 api_integration_example.py
```

## 配置文件模板

### config.json
```json
{
  "apis": {
    "pubmed": {
      "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
      "email": "your_email@hospital.com",
      "api_key": "YOUR_NCBI_API_KEY",
      "tool_name": "SciAssist",
      "rate_limit": 10,
      "timeout": 30
    },
    "clinicaltrials": {
      "base_url": "https://clinicaltrials.gov/api/v2",
      "timeout": 30
    },
    "semantic_scholar": {
      "base_url": "https://api.semanticscholar.org/graph/v1",
      "user_agent": "SciAssist-Medical-Research-Tool",
      "timeout": 30
    }
  },
  "cache": {
    "redis": {
      "host": "localhost",
      "port": 6379,
      "db": 0,
      "expire_time": 3600
    },
    "memory": {
      "max_size": 1000,
      "expire_time": 600
    }
  },
  "logging": {
    "level": "INFO",
    "file": "logs/api_integration.log"
  }
}
```

## API使用限制

### PubMed (NCBI E-utilities)
- **无API Key**: 3请求/秒，最多连续查询
- **有API Key**: 10请求/秒
- **建议时间**: 工作日晚9点-早5点，周末全天
- **必需参数**: tool, email

### ClinicalTrials.gov
- **速率限制**: 无严格限制，建议合理使用
- **分页支持**: pageSize参数控制每页结果数
- **最大结果**: 默认1000条/查询

### Semantic Scholar
- **速率限制**: 合理使用策略，具体未公开
- **建议**: 添加合理延时，避免过于频繁请求
- **User-Agent**: 必须设置标识应用

## 错误处理

### 常见错误及解决方案

```python
# 1. API限流
except aiohttp.ClientResponseError as e:
    if e.status == 429:  # Too Many Requests
        await asyncio.sleep(1)  # 等待后重试

# 2. 网络超时
except asyncio.TimeoutError:
    logger.warning("API调用超时，尝试重连")

# 3. 数据解析错误
except (json.JSONDecodeError, ET.ParseError) as e:
    logger.error(f"数据解析失败: {e}")
```

### 重试机制配置
```python
@retry(max_attempts=3, backoff_factor=2)
async def api_call_with_retry(self, url, params):
    """带重试的API调用"""
    pass
```

## 性能优化建议

### 1. 批量查询
```python
# 好的做法：批量获取多个PMID
pmids = "12345678,23456789,34567890"
params = {'db': 'pubmed', 'id': pmids}

# 避免：逐个查询
for pmid in pmids:
    params = {'db': 'pubmed', 'id': pmid}  # 低效
```

### 2. 缓存策略
```python
# Redis缓存示例
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

async def cached_search(self, query):
    cache_key = f"pubmed:{hashlib.md5(query.encode()).hexdigest()}"
    cached_result = r.get(cache_key)

    if cached_result:
        return json.loads(cached_result)

    result = await self.search_pubmed(query)
    r.setex(cache_key, 3600, json.dumps(result))  # 缓存1小时
    return result
```

### 3. 并发控制
```python
# 使用信号量控制并发数
semaphore = asyncio.Semaphore(5)  # 最多5个并发请求

async def controlled_request(self, url, params):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()
```

## 监控和日志

### 日志配置
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/api_integration.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 监控指标
```python
# 性能监控示例
class APIMonitor:
    def __init__(self):
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'response_times': []
        }

    async def track_request(self, api_name, start_time, success):
        self.stats['total_requests'] += 1
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1

        response_time = time.time() - start_time
        self.stats['response_times'].append(response_time)
```

## 部署建议

### Docker配置
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "api_integration_example.py"]
```

### 环境变量
```bash
# .env 文件
NCBI_EMAIL=your_email@hospital.com
NCBI_API_KEY=your_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=INFO
```

## 安全注意事项

### 1. API Key保护
- 使用环境变量存储敏感信息
- 不要在代码中硬编码API Key
- 定期轮换API Key

### 2. 数据合规
- 遵循HIPAA等医疗数据保护法规
- 不存储患者敏感信息
- 实施数据加密传输

### 3. 访问控制
- 实施API访问日志记录
- 设置访问频率限制
- 监控异常访问模式

## 常见问题解答

**Q: PubMed API返回空结果怎么办？**
A: 检查查询词拼写，尝试更通用的关键词，确认数据库中存在相关文献。

**Q: ClinicalTrials.gov API响应慢怎么办？**
A: 减小pageSize参数，使用缓存，考虑分页获取数据。

**Q: 如何处理API服务临时不可用？**
A: 实施重试机制，提供降级服务，使用缓存数据作为备选。

**Q: 如何优化大量医生并发查询？**
A: 使用Redis缓存热门查询，实施请求队列，考虑CDN加速。

---

*最后更新: 2025年9月*