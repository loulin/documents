#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学文献和临床试验API集成示例
Medical Literature and Clinical Trial API Integration Example
"""

import asyncio
import aiohttp
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalDataAPI:
    """医学数据API集成类"""

    def __init__(self):
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.clinicaltrials_base_url = "https://clinicaltrials.gov/api/v2"
        self.your_email = "your_email@hospital.com"  # NCBI要求提供邮箱
        self.api_key = "YOUR_NCBI_API_KEY"  # 申请NCBI API key

    async def search_pubmed(self, query: str, max_results: int = 20):
        """
        搜索PubMed文献

        Args:
            query: 搜索关键词
            max_results: 最大结果数
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: 搜索获取PMID列表
                search_params = {
                    'db': 'pubmed',
                    'term': query,
                    'retmax': max_results,
                    'tool': 'SciAssist',
                    'email': self.your_email,
                    'api_key': self.api_key
                }

                search_url = f"{self.pubmed_base_url}/esearch.fcgi"
                async with session.get(search_url, params=search_params) as response:
                    search_xml = await response.text()

                # 解析搜索结果获取PMID列表
                root = ET.fromstring(search_xml)
                pmid_list = [id_elem.text for id_elem in root.findall('.//Id')]

                if not pmid_list:
                    return []

                # Step 2: 获取文献详细信息
                fetch_params = {
                    'db': 'pubmed',
                    'id': ','.join(pmid_list),
                    'retmode': 'xml',
                    'tool': 'SciAssist',
                    'email': self.your_email,
                    'api_key': self.api_key
                }

                fetch_url = f"{self.pubmed_base_url}/efetch.fcgi"
                async with session.get(fetch_url, params=fetch_params) as response:
                    fetch_xml = await response.text()

                # 解析文献详情
                articles = self._parse_pubmed_xml(fetch_xml)

                logger.info(f"成功获取 {len(articles)} 篇PubMed文献")
                return articles

        except Exception as e:
            logger.error(f"PubMed搜索失败: {str(e)}")
            return []

    def _parse_pubmed_xml(self, xml_content: str):
        """解析PubMed XML响应"""
        articles = []

        try:
            root = ET.fromstring(xml_content)

            for article_elem in root.findall('.//PubmedArticle'):
                article = {}

                # 基本信息
                pmid_elem = article_elem.find('.//PMID')
                article['pmid'] = pmid_elem.text if pmid_elem is not None else ''

                # 标题
                title_elem = article_elem.find('.//ArticleTitle')
                article['title'] = title_elem.text if title_elem is not None else ''

                # 摘要
                abstract_elem = article_elem.find('.//AbstractText')
                article['abstract'] = abstract_elem.text if abstract_elem is not None else ''

                # 作者
                authors = []
                for author_elem in article_elem.findall('.//Author'):
                    last_name = author_elem.find('LastName')
                    first_name = author_elem.find('ForeName')
                    if last_name is not None and first_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
                article['authors'] = authors

                # 期刊
                journal_elem = article_elem.find('.//Title')
                article['journal'] = journal_elem.text if journal_elem is not None else ''

                # 发表日期
                pub_date_elem = article_elem.find('.//PubDate')
                if pub_date_elem is not None:
                    year = pub_date_elem.find('Year')
                    month = pub_date_elem.find('Month')
                    article['publication_date'] = f"{year.text if year is not None else ''}-{month.text if month is not None else ''}"

                articles.append(article)

        except ET.ParseError as e:
            logger.error(f"XML解析错误: {str(e)}")

        return articles

    async def search_clinical_trials(self, condition: str, max_studies: int = 20):
        """
        搜索临床试验

        Args:
            condition: 疾病条件
            max_studies: 最大结果数
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'query.cond': condition,
                    'countTotal': True,
                    'pageSize': max_studies,
                    'format': 'json'
                }

                url = f"{self.clinicaltrials_base_url}/studies"
                async with session.get(url, params=params) as response:
                    data = await response.json()

                trials = []
                studies = data.get('studies', [])

                for study in studies:
                    protocol_section = study.get('protocolSection', {})
                    identification_module = protocol_section.get('identificationModule', {})
                    status_module = protocol_section.get('statusModule', {})
                    design_module = protocol_section.get('designModule', {})
                    conditions_module = protocol_section.get('conditionsModule', {})

                    trial = {
                        'nct_id': identification_module.get('nctId', ''),
                        'title': identification_module.get('briefTitle', ''),
                        'status': status_module.get('overallStatus', ''),
                        'phase': design_module.get('phases', []),
                        'conditions': conditions_module.get('conditions', []),
                        'brief_summary': identification_module.get('briefSummary', ''),
                        'start_date': status_module.get('startDateStruct', {}).get('date', ''),
                        'completion_date': status_module.get('completionDateStruct', {}).get('date', ''),
                    }
                    trials.append(trial)

                logger.info(f"成功获取 {len(trials)} 个临床试验")
                return trials

        except Exception as e:
            logger.error(f"临床试验搜索失败: {str(e)}")
            return []

    async def get_semantic_scholar_alternative(self, query: str, max_papers: int = 20):
        """
        使用Semantic Scholar作为Google Scholar的替代

        Args:
            query: 搜索关键词
            max_papers: 最大结果数
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.semanticscholar.org/graph/v1/paper/search"
                params = {
                    'query': query,
                    'limit': max_papers,
                    'fields': 'paperId,title,abstract,authors,year,citationCount,journal,url'
                }

                headers = {
                    'User-Agent': 'SciAssist-Medical-Research-Tool'
                }

                async with session.get(url, params=params, headers=headers) as response:
                    data = await response.json()

                papers = []
                for paper_data in data.get('data', []):
                    paper = {
                        'id': paper_data.get('paperId', ''),
                        'title': paper_data.get('title', ''),
                        'abstract': paper_data.get('abstract', ''),
                        'authors': [author.get('name', '') for author in paper_data.get('authors', [])],
                        'year': paper_data.get('year', ''),
                        'citation_count': paper_data.get('citationCount', 0),
                        'journal': paper_data.get('journal', {}).get('name', '') if paper_data.get('journal') else '',
                        'url': paper_data.get('url', '')
                    }
                    papers.append(paper)

                logger.info(f"成功获取 {len(papers)} 篇Semantic Scholar论文")
                return papers

        except Exception as e:
            logger.error(f"Semantic Scholar搜索失败: {str(e)}")
            return []

class MedicalResearchService:
    """医学研究服务"""

    def __init__(self):
        self.api = MedicalDataAPI()

    async def comprehensive_research(self, topic: str, doctor_specialty: str = None):
        """
        综合研究：同时搜索文献和临床试验

        Args:
            topic: 研究主题
            doctor_specialty: 医生专科（用于个性化推荐）
        """
        results = {
            'topic': topic,
            'search_time': datetime.now().isoformat(),
            'pubmed_articles': [],
            'clinical_trials': [],
            'semantic_scholar_papers': [],
            'summary': {}
        }

        # 并发执行多个搜索
        tasks = [
            self.api.search_pubmed(topic, max_results=10),
            self.api.search_clinical_trials(topic, max_studies=10),
            self.api.get_semantic_scholar_alternative(topic, max_papers=10)
        ]

        try:
            pubmed_results, trial_results, scholar_results = await asyncio.gather(*tasks)

            results['pubmed_articles'] = pubmed_results
            results['clinical_trials'] = trial_results
            results['semantic_scholar_papers'] = scholar_results

            # 生成摘要
            results['summary'] = {
                'total_pubmed_articles': len(pubmed_results),
                'total_clinical_trials': len(trial_results),
                'total_scholar_papers': len(scholar_results),
                'active_trials': len([t for t in trial_results if t['status'] in ['Recruiting', 'Active, not recruiting']]),
                'recent_papers': len([p for p in pubmed_results if '2024' in str(p.get('publication_date', '')) or '2025' in str(p.get('publication_date', ''))])
            }

        except Exception as e:
            logger.error(f"综合研究失败: {str(e)}")

        return results

# 使用示例
async def demo_medical_research():
    """演示医学研究API的使用"""

    service = MedicalResearchService()

    # 模拟内分泌医生的研究需求
    research_topics = [
        "GLP-1 receptor agonists diabetes",
        "thyroid cancer treatment",
        "insulin resistance PCOS",
        "diabetic nephropathy"
    ]

    for topic in research_topics:
        print(f"\n🔍 正在研究: {topic}")
        print("-" * 50)

        results = await service.comprehensive_research(topic, doctor_specialty="endocrinology")

        print(f"📚 PubMed文献: {results['summary']['total_pubmed_articles']} 篇")
        print(f"🧪 临床试验: {results['summary']['total_clinical_trials']} 个")
        print(f"📖 学术论文: {results['summary']['total_scholar_papers']} 篇")
        print(f"🏃 进行中试验: {results['summary']['active_trials']} 个")
        print(f"🆕 近期论文: {results['summary']['recent_papers']} 篇")

        # 显示前3个结果示例
        if results['pubmed_articles']:
            print(f"\n📰 最新PubMed文献:")
            for i, article in enumerate(results['pubmed_articles'][:3], 1):
                print(f"{i}. {article['title'][:100]}...")

        if results['clinical_trials']:
            print(f"\n🧪 相关临床试验:")
            for i, trial in enumerate(results['clinical_trials'][:3], 1):
                print(f"{i}. {trial['title'][:80]}... [Status: {trial['status']}]")

if __name__ == "__main__":
    print("🏥 医学文献与临床试验API集成演示")
    print("=" * 60)

    # 运行演示
    asyncio.run(demo_medical_research())