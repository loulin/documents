from typing import List, Dict, Any, Optional
import google.generativeai as genai
import os
from datetime import datetime
import json
import logging
from dataclasses import dataclass
import yaml

@dataclass
class ResearchQuery:
    query: str
    domain: str
    context: Optional[str] = None
    max_results: int = 10

@dataclass
class ResearchResult:
    content: str
    sources: List[Dict[str, str]]
    confidence: float
    timestamp: datetime

class GeminiResearchAgent:
    def __init__(self, api_key: str, config_path: str):
        """初始化Gemini研究助手"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # 加载域配置
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GeminiResearchAgent')
        
        # 初始化模型
        self.model = genai.GenerativeModel('gemini-pro')
        
    def _build_prompt(self, query: ResearchQuery) -> str:
        """构建研究提示"""
        domain_config = self.config['domains'].get(query.domain, {})
        
        prompt_parts = [
            f"作为一个专业的{query.domain}领域研究助手，请帮助分析以下问题：\n{query.query}\n\n",
            "请考虑以下关键方面：\n"
        ]
        
        # 添加领域特定的搜索词
        if 'search_terms' in domain_config:
            terms = '\n'.join(f"- {term}" for term in domain_config['search_terms'])
            prompt_parts.append(f"相关搜索词：\n{terms}\n")
            
        # 添加重要期刊
        if 'journals' in domain_config:
            journals = '\n'.join(f"- {journal}" for journal in domain_config['journals'])
            prompt_parts.append(f"重点期刊：\n{journals}\n")
        
        # 添加上下文（如果有）
        if query.context:
            prompt_parts.append(f"\n考虑以下背景信息：\n{query.context}\n")
            
        prompt_parts.append("\n请提供：\n1. 详细分析\n2. 相关研究证据\n3. 关键发现\n4. 建议方向")
        
        return ''.join(prompt_parts)
        
    async def research(self, query: ResearchQuery) -> ResearchResult:
        """执行研究查询"""
        try:
            # 1. 从数据源获取原始数据
            data_manager = DataSourceManager()
            raw_data = await data_manager.search_all(
                query=query.query,
                sources=self._get_relevant_sources(query.domain),
                max_results=query.max_results
            )
            
            # 2. 构建增强的提示
            prompt = self._build_enhanced_prompt(query, raw_data)
            
            # 3. 使用Gemini生成分析
            response = await self.model.generate_content_async(prompt)
            
            # 4. 处理并验证结果
            analysis = response.text
            
            # 5. 提取和验证引用
            sources = self._extract_and_verify_sources(raw_data)
            
            # 6. 生成最终结果
            result = ResearchResult(
                content=analysis,
                sources=sources,
                confidence=self._calculate_confidence(response, raw_data),
                timestamp=datetime.now(),
                raw_data=raw_data  # 保存原始数据供后续使用
            )
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise
            
    def _extract_sources(self, response: Any) -> List[Dict[str, str]]:
        """从响应中提取源引用"""
        # 这里需要根据实际的API响应结构来实现
        # 临时返回空列表
        return []
        
    def _calculate_confidence(self, response: Any) -> float:
        """计算结果的置信度"""
        # 这里需要根据实际的API响应特征来实现
        # 临时返回固定值
        return 0.8
        
    def save_result(self, query: ResearchQuery, result: ResearchResult, 
                   output_dir: str):
        """保存研究结果"""
        timestamp = result.timestamp.strftime('%Y%m%d_%H%M%S')
        filename = f"research_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        data = {
            "query": {
                "text": query.query,
                "domain": query.domain,
                "context": query.context,
            },
            "result": {
                "content": result.content,
                "sources": result.sources,
                "confidence": result.confidence,
                "timestamp": result.timestamp.isoformat()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Saved result to {filepath}")
        
async def main():
    # 配置
    api_key = os.getenv("GEMINI_API_KEY")
    config_path = "domains/domain_source_mapping.yaml"
    output_dir = "research_results"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化代理
    agent = GeminiResearchAgent(api_key, config_path)
    
    # 示例查询
    query = ResearchQuery(
        query="2型糖尿病患者中GLP-1受体激动剂的最新研究进展是什么？",
        domain="endocrinology",
        context="特别关注心血管获益和减重效果"
    )
    
    # 执行研究
    result = await agent.research(query)
    
    # 保存结果
    agent.save_result(query, result, output_dir)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
