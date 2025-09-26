# 医学研究智能助手快速入门指南

## 简介

医学研究智能助手是一个结合了 Gemini AI 和专业医学数据源的研究辅助系统。本指南将帮助你快速设置和开始使用系统。

## 快速开始

### 1. 环境准备

```bash
# 克隆代码库
git clone https://github.com/yourusername/medical-research-assistant.git
cd medical-research-assistant

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件：

```env
# .env
GEMINI_API_KEY=your_gemini_api_key_here
NCBI_API_KEY=your_pubmed_api_key_here
DRUGBANK_API_KEY=your_drugbank_api_key_here
```

### 3. 运行示例

```python
# example.py
from research_assistant import GeminiResearchAgent

async def main():
    # 初始化研究助手
    agent = GeminiResearchAgent()
    
    # 执行查询
    result = await agent.research(
        query="2型糖尿病最新治疗进展",
        domain="endocrinology"
    )
    
    # 打印结果
    print(result.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 基本用法

### 1. 文献搜索

```python
# 搜索最近的研究文献
result = await agent.search_literature(
    query="GLP-1受体激动剂",
    years=5,  # 最近5年
    sort="relevance"
)
```

### 2. 临床试验查询

```python
# 查询相关临床试验
trials = await agent.search_trials(
    condition="Type 2 Diabetes",
    status="Recruiting"
)
```

### 3. 生成研究报告

```python
# 生成综合报告
report = await agent.generate_report(
    topic="糖尿病新药研究进展",
    sections=[
        "current_status",
        "key_findings",
        "future_directions"
    ]
)
```

## 数据源配置

### 1. PubMed配置

```yaml
# sources/pubmed.yaml
api:
  base_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  rate_limit: 3  # 每秒请求数
  cache_ttl: 3600  # 缓存时间（秒）
```

### 2. ClinicalTrials.gov配置

```yaml
# sources/clinical_trials.yaml
api:
  base_url: https://clinicaltrials.gov/api/
  format: json
  max_results: 100
```

## 常见问题解答

### 1. API限制问题

Q: 如何处理API请求限制？
A: 系统内置了自动限流机制，会根据各数据源的限制自动调整请求频率。

### 2. 数据缓存

Q: 数据会被缓存多久？
A: 默认配置：
- PubMed数据：1小时
- 临床试验数据：24小时
- 药物数据：7天

### 3. 错误处理

Q: 如果数据源暂时不可用怎么办？
A: 系统会：
1. 尝试使用缓存数据
2. 切换到备用数据源
3. 返回部分结果

## 最佳实践

### 1. 查询优化

```python
# 优化查询以获得更好的结果
query = ResearchQuery(
    text="GLP-1受体激动剂在肥胖治疗中的应用",
    filters={
        "year": "2020-2025",
        "study_type": ["RCT", "Meta-Analysis"],
        "language": ["english", "chinese"]
    }
)
```

### 2. 缓存使用

```python
# 使用缓存加速重复查询
results = await agent.search_with_cache(
    query="糖尿病治疗新进展",
    cache_key="diabetes_treatment_2025",
    ttl=3600
)
```

### 3. 错误处理

```python
try:
    result = await agent.research(query)
except DataSourceError:
    # 使用备用数据源
    result = await agent.research_with_fallback(query)
except QuotaExceededError:
    # 等待并重试
    await asyncio.sleep(60)
    result = await agent.research(query)
```

## 高级功能

### 1. 自定义分析流程

```python
# 创建自定义分析流程
pipeline = AnalysisPipeline([
    DataCollector(),
    Preprocessor(),
    GeminiAnalyzer(),
    ReportGenerator()
])

result = await pipeline.run(query)
```

### 2. 导出功能

```python
# 导出研究结果
await agent.export_results(
    result,
    format="pdf",
    template="academic",
    output_path="research_report.pdf"
)
```

### 3. 批量处理

```python
# 批量处理多个查询
queries = [
    "糖尿病治疗进展",
    "高血压研究现状",
    "肥胖治疗新方法"
]

results = await agent.batch_research(queries)
```

## 监控和维护

### 1. 性能监控

```python
# 检查系统性能
stats = await agent.get_stats()
print(f"平均响应时间: {stats.avg_response_time}秒")
print(f"缓存命中率: {stats.cache_hit_ratio}%")
```

### 2. 健康检查

```python
# 检查所有数据源状态
status = await agent.check_health()
for source, is_healthy in status.items():
    print(f"{source}: {'健康' if is_healthy else '异常'}")
```

### 3. 日志查看

```python
# 查看最近的错误日志
logs = await agent.get_logs(
    level="ERROR",
    hours=24
)
```

## 更新日志

- 2025-08-18: 初始版本发布
- 2025-08-17: 添加数据源集成
- 2025-08-16: 添加Gemini集成

## 联系支持

- 技术支持：support@example.com
- 文档网��：https://docs.example.com
- GitHub仓库：https://github.com/example/medical-research-assistant
