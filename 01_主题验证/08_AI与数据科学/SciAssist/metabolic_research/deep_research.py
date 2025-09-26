"""
Deep Research Agent 客户端
提供与DRA API交互的标准接口
"""

import os
import json
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import datetime

@dataclass
class APIConfig:
    """API配置"""
    api_key: str
    base_url: str = "https://api.deepresearch.ai/v1"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1

class DeepResearchClient:
    """Deep Research Agent API客户端"""
    
    def __init__(self, api_key: str, config: Dict = None):
        """初始化客户端
        
        Args:
            api_key: API密钥
            config: 额外配置
        """
        self.config = APIConfig(
            api_key=api_key,
            **(config or {})
        )
        self._session = None
        
    async def _ensure_session(self):
        """确保aiohttp会话存在"""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
            )
    
    async def _request(self, 
                      method: str, 
                      endpoint: str, 
                      data: Dict = None) -> Any:
        """发送API请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            
        Returns:
            API响应
        """
        await self._ensure_session()
        
        url = f"{self.config.base_url}/{endpoint}"
        attempts = 0
        
        while attempts < self.config.max_retries:
            try:
                async with self._session.request(
                    method, 
                    url,
                    json=data,
                    timeout=self.config.timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                attempts += 1
                if attempts == self.config.max_retries:
                    raise
                await asyncio.sleep(self.config.retry_delay * attempts)
                
    async def search_literature(self, query: str) -> List[Dict]:
        """搜索文献
        
        Args:
            query: 搜索查询
            
        Returns:
            List[Dict]: 文献列表
        """
        return await self._request(
            "POST",
            "literature/search",
            {"query": query}
        )
        
    async def search_clinical_data(self, query: Dict) -> List[Dict]:
        """搜索临床数据
        
        Args:
            query: 搜索条件
            
        Returns:
            List[Dict]: 临床数据列表
        """
        return await self._request(
            "POST",
            "clinical/search",
            query
        )
        
    async def analyze_risk(self, data: Dict) -> Dict:
        """分析风险
        
        Args:
            data: 风险分析数据
            
        Returns:
            Dict: 风险分析结果
        """
        return await self._request(
            "POST",
            "risk/analyze",
            data
        )
        
    async def get_clinical_history(self, patient_id: str) -> Dict:
        """获取临床病史
        
        Args:
            patient_id: 患者ID
            
        Returns:
            Dict: 临床病史
        """
        return await self._request(
            "GET",
            f"clinical/history/{patient_id}"
        )
        
    async def get_patient_metrics(self, patient_id: str) -> Dict:
        """获取患者指标
        
        Args:
            patient_id: 患者ID
            
        Returns:
            Dict: 患者指标
        """
        return await self._request(
            "GET",
            f"patients/{patient_id}/metrics"
        )
        
    async def get_research_insights(self, data: Dict) -> List[Dict]:
        """获取研究洞察
        
        Args:
            data: 研究数据
            
        Returns:
            List[Dict]: 研究洞察列表
        """
        return await self._request(
            "POST",
            "research/insights",
            data
        )
        
    async def generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """生成建议
        
        Args:
            analysis: 分析结果
            
        Returns:
            List[Dict]: 建议列表
        """
        return await self._request(
            "POST",
            "recommendations/generate",
            analysis
        )
        
    async def create_monitoring_plan(self, analysis: Dict) -> Dict:
        """创建监测计划
        
        Args:
            analysis: 分析结果
            
        Returns:
            Dict: 监测计划
        """
        return await self._request(
            "POST",
            "monitoring/create",
            analysis
        )
        
    async def get_domain_knowledge(self, domain: str) -> Dict:
        """获取领域知识
        
        Args:
            domain: 领域
            
        Returns:
            Dict: 领域知识
        """
        return await self._request(
            "GET",
            f"knowledge/{domain}"
        )
        
    async def query_knowledge(self, query: Dict) -> List[Dict]:
        """查询知识
        
        Args:
            query: 查询条件
            
        Returns:
            List[Dict]: 查询结果
        """
        return await self._request(
            "POST",
            "knowledge/query",
            query
        )
        
    async def update_knowledge(self, data: Dict) -> bool:
        """更新知识
        
        Args:
            data: 更新数据
            
        Returns:
            bool: 是否成功
        """
        response = await self._request(
            "POST",
            "knowledge/update",
            data
        )
        return response.get("success", False)
        
    async def get_knowledge_updates(self) -> List[Dict]:
        """获取知识更新
        
        Returns:
            List[Dict]: 更新列表
        """
        return await self._request(
            "GET",
            "knowledge/updates"
        )
        
    async def sync_research_context(self, context: Dict) -> Dict:
        """同步研究上下文
        
        Args:
            context: 研究上下文
            
        Returns:
            Dict: 同步结果
        """
        return await self._request(
            "POST",
            "research/sync",
            context
        )
        
    async def generate_report(self, data: Dict) -> Dict:
        """生成报告
        
        Args:
            data: 报告数据
            
        Returns:
            Dict: 研究报告
        """
        return await self._request(
            "POST",
            "reports/generate",
            data
        )
        
    async def close(self):
        """关闭客户端"""
        if self._session:
            await self._session.close()
            self._session = None
            
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        """异步上下文管理器退出"""
        await self.close()
