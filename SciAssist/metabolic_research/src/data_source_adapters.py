from abc import ABC, abstractmethod
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os
from urllib.parse import urlencode
import json
import xml.etree.ElementTree as ET

class DataSourceAdapter(ABC):
    """数据源适配器基类"""
    
    @abstractmethod
    async def search(self, query: str, **params) -> Dict[str, Any]:
        """搜索数据"""
        pass
        
    @abstractmethod
    async def fetch(self, id: str, **params) -> Dict[str, Any]:
        """获取具体数据"""
        pass

class PubMedAdapter(DataSourceAdapter):
    """PubMed适配器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = api_key or os.getenv("NCBI_API_KEY")
        self.logger = logging.getLogger("PubMedAdapter")
        
    async def search(self, query: str, **params) -> Dict[str, Any]:
        """搜索PubMed文献"""
        try:
            async with aiohttp.ClientSession() as session:
                # 构建搜索URL
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": params.get("max_results", 20),
                    "retmode": "json",
                    "sort": params.get("sort", "relevance")
                }
                if self.api_key:
                    search_params["api_key"] = self.api_key
                    
                url = f"{self.base_url}esearch.fcgi?{urlencode(search_params)}"
                
                # 执行搜索
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"PubMed搜索失败: {response.status}")
                        
                    data = await response.json()
                    id_list = data["esearchresult"]["idlist"]
                    
                    # 获取详细信息
                    results = await self.fetch_details(session, id_list)
                    return {"status": "success", "results": results}
                    
        except Exception as e:
            self.logger.error(f"PubMed搜索错误: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def fetch_details(self, session: aiohttp.ClientSession, 
                          id_list: List[str]) -> List[Dict[str, Any]]:
        """获取文献详细信息"""
        if not id_list:
            return []
            
        try:
            # 构建详情URL
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            if self.api_key:
                fetch_params["api_key"] = self.api_key
                
            url = f"{self.base_url}efetch.fcgi?{urlencode(fetch_params)}"
            
            # 获取详情
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"获取PubMed详情失败: {response.status}")
                    
                xml_data = await response.text()
                return self._parse_pubmed_xml(xml_data)
                
        except Exception as e:
            self.logger.error(f"获取PubMed详情错误: {str(e)}")
            return []
            
    def _parse_pubmed_xml(self, xml_data: str) -> List[Dict[str, Any]]:
        """解析PubMed XML响应"""
        results = []
        try:
            root = ET.fromstring(xml_data)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    # 提取文章信息
                    article_data = {
                        "pmid": article.find(".//PMID").text,
                        "title": article.find(".//ArticleTitle").text,
                        "abstract": "",
                        "authors": [],
                        "journal": "",
                        "pub_date": "",
                        "keywords": []
                    }
                    
                    # 提取摘要
                    abstract = article.find(".//Abstract/AbstractText")
                    if abstract is not None:
                        article_data["abstract"] = abstract.text
                        
                    # 提取作者
                    authors = article.findall(".//Author")
                    for author in authors:
                        last_name = author.find("LastName")
                        fore_name = author.find("ForeName")
                        if last_name is not None and fore_name is not None:
                            article_data["authors"].append(
                                f"{fore_name.text} {last_name.text}"
                            )
                            
                    # 提取期刊信息
                    journal = article.find(".//Journal/Title")
                    if journal is not None:
                        article_data["journal"] = journal.text
                        
                    # 提取发布日期
                    pub_date = article.find(".//PubDate")
                    if pub_date is not None:
                        year = pub_date.find("Year")
                        month = pub_date.find("Month")
                        if year is not None:
                            article_data["pub_date"] = year.text
                            if month is not None:
                                article_data["pub_date"] = f"{month.text} {year.text}"
                                
                    # 提取关键词
                    keywords = article.findall(".//Keyword")
                    article_data["keywords"] = [k.text for k in keywords if k.text]
                    
                    results.append(article_data)
                    
                except Exception as e:
                    self.logger.error(f"解析文章错误: {str(e)}")
                    continue
                    
            return results
            
        except Exception as e:
            self.logger.error(f"解析XML错误: {str(e)}")
            return []
            
    async def fetch(self, id: str, **params) -> Dict[str, Any]:
        """获取单篇文献详情"""
        try:
            async with aiohttp.ClientSession() as session:
                details = await self.fetch_details(session, [id])
                return details[0] if details else None
                
        except Exception as e:
            self.logger.error(f"获取文献详情错误: {str(e)}")
            return None

class ClinicalTrialsAdapter(DataSourceAdapter):
    """ClinicalTrials.gov适配器"""
    
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api"
        self.logger = logging.getLogger("ClinicalTrialsAdapter")
        
    async def search(self, query: str, **params) -> Dict[str, Any]:
        """搜索临床试验"""
        try:
            async with aiohttp.ClientSession() as session:
                # 构建搜索参数
                search_params = {
                    "expr": query,
                    "fmt": "json",
                    "max_rnk": params.get("max_results", 20)
                }
                
                url = f"{self.base_url}/query/study_fields?{urlencode(search_params)}"
                
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"临床试验搜索失败: {response.status}")
                        
                    data = await response.json()
                    return {"status": "success", "results": self._parse_trials(data)}
                    
        except Exception as e:
            self.logger.error(f"临床试验搜索错误: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def _parse_trials(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析临床试验数据"""
        results = []
        try:
            studies = data.get("StudyFieldsResponse", {}).get("StudyFields", [])
            
            for study in studies:
                try:
                    trial_data = {
                        "nct_id": study.get("NCTId", [None])[0],
                        "title": study.get("BriefTitle", [None])[0],
                        "status": study.get("OverallStatus", [None])[0],
                        "phase": study.get("Phase", [None])[0],
                        "conditions": study.get("Condition", []),
                        "interventions": study.get("InterventionName", []),
                        "locations": study.get("LocationFacility", []),
                        "url": f"https://clinicaltrials.gov/ct2/show/{study.get('NCTId', [None])[0]}"
                    }
                    results.append(trial_data)
                    
                except Exception as e:
                    self.logger.error(f"解析试验数据错误: {str(e)}")
                    continue
                    
            return results
            
        except Exception as e:
            self.logger.error(f"解析试验列表错误: {str(e)}")
            return []
            
    async def fetch(self, id: str, **params) -> Dict[str, Any]:
        """获取单个临床试验详情"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/query/full_studies?expr={id}&fmt=json"
                
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"获取试验详情失败: {response.status}")
                        
                    data = await response.json()
                    studies = data.get("FullStudiesResponse", {}).get("FullStudies", [])
                    return studies[0] if studies else None
                    
        except Exception as e:
            self.logger.error(f"获取试验详情错误: {str(e)}")
            return None

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self.adapters = {
            "pubmed": PubMedAdapter(),
            "clinical_trials": ClinicalTrialsAdapter()
        }
        self.logger = logging.getLogger("DataSourceManager")
        
    async def search_all(self, query: str, sources: List[str] = None, 
                        **params) -> Dict[str, Any]:
        """搜索所有或指定数据源"""
        results = {}
        sources = sources or list(self.adapters.keys())
        
        tasks = []
        for source in sources:
            if source in self.adapters:
                task = self.adapters[source].search(query, **params)
                tasks.append((source, task))
                
        # 并行执行所有搜索
        for source, task in tasks:
            try:
                results[source] = await task
            except Exception as e:
                self.logger.error(f"{source}搜索错误: {str(e)}")
                results[source] = {"status": "error", "message": str(e)}
                
        return results
        
    async def fetch_details(self, source: str, id: str, **params) -> Dict[str, Any]:
        """获取指定数据源的详细信息"""
        if source not in self.adapters:
            raise ValueError(f"未知数据源: {source}")
            
        return await self.adapters[source].fetch(id, **params)

async def main():
    """示例用法"""
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建数据源管理器
    manager = DataSourceManager()
    
    # 示例查询
    query = "GLP-1 receptor agonists diabetes"
    
    # 搜索所有数据源
    results = await manager.search_all(query, max_results=5)
    
    # 打印结果
    for source, data in results.items():
        print(f"\n{source.upper()} 结果:")
        if data["status"] == "success":
            for item in data["results"][:3]:  # 只显示前3条
                print(f"\n  - {item.get('title', 'No title')}")
        else:
            print(f"  错误: {data['message']}")

if __name__ == "__main__":
    asyncio.run(main())
