#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代谢研究助手示例代码
展示如何使用Deep Research Agent适配版的各个功能模块
"""

import asyncio
import datetime
from typing import Dict, List

from research_assistant import ResearchAssistant
from opportunity_evaluator import OpportunityEvaluator, ResearchOpportunity
from data_collector import DataCollector
from risk_analyzer import RiskAnalyzer
from knowledge_graph import KnowledgeGraph

async def demo_opportunity_evaluation():
    """演示研究机会评估功能"""
    print("\n=== 研究机会评估演示 ===")
    
    # 初始化评估器
    evaluator = OpportunityEvaluator("your-api-key")
    
    # 创建研究机会对象
    opportunity = ResearchOpportunity(
        id="",
        type="NEW_HYPOTHESIS",
        title="微血管病变预测模型",
        description="基于多组学数据的微血管病变预测",
        domain="endocrinology",
        potential_score=0.0,
        resource_requirements={
            "data": ["clinical_data", "genomics_data"],
            "computing": "high",
            "expertise": ["endocrinology", "bioinformatics"]
        },
        estimated_duration=24,  # 月
        risks=[],
        priority=0,
        created_at=datetime.datetime.now()
    )
    
    # 评估研究机会
    evaluation = await evaluator.evaluate_opportunity(opportunity)
    print(f"Research potential: {evaluation['potential']}")
    print(f"Feasibility: {evaluation['feasibility']}")
    print(f"Risk level: {evaluation['risks']}")
    print(f"Recommendations: {evaluation['recommendations']}")

async def demo_data_collection():
    """演示数据采集功能"""
    print("\n=== 数据采集演示 ===")
    
    # 初始化数据采集器
    collector = DataCollector("your-api-key")
    
    # 采集文献数据
    print("\n>> 文献采集:")
    literature = await collector.collect_literature(
        "早期糖尿病肾病biomarker"
    )
    for paper in literature[:3]:  # 显示前3篇
        print(f"\nTitle: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"Abstract: {paper.abstract[:200]}...")
    
    # 采集临床数据
    print("\n>> 临床数据采集:")
    clinical_data = await collector.collect_clinical_data({
        "condition": "diabetic_nephropathy",
        "stage": "early",
        "data_type": ["lab_results", "clinical_symptoms"]
    })
    print(f"Collected {len(clinical_data)} clinical records")

async def demo_risk_analysis():
    """演示风险分析功能"""
    print("\n=== 风险分析演示 ===")
    
    # 初始化风险分析器
    analyzer = RiskAnalyzer("your-api-key")
    
    # 准备示例患者数据
    patient_data = {
        "id": "12345",
        "age": 45,
        "gender": "female",
        "diagnosis": "type2_diabetes",
        "lab_results": {
            "hba1c": 7.2,
            "egfr": 85,
            "acr": 25
        }
    }
    
    # 个人风险分析
    print("\n>> 个人风险分析:")
    risk_profile = await analyzer.analyze_personal_risk(patient_data)
    print(f"Risk level: {risk_profile.risk_level}")
    print(f"Risk score: {risk_profile.risk_score}")
    print("\nKey factors:")
    for factor in risk_profile.key_factors:
        print(f"- {factor}")
    
    # 批量风险分析
    print("\n>> 批量风险分析:")
    patient_list = [
        patient_data,
        {**patient_data, "id": "12346", "age": 52, "lab_results": {"hba1c": 8.1}},
        {**patient_data, "id": "12347", "age": 38, "lab_results": {"hba1c": 6.5}}
    ]
    risk_profiles = await analyzer.analyze_batch_risks(patient_list)
    print(f"Analyzed {len(risk_profiles)} patients")

async def demo_knowledge_graph():
    """演示知识图谱功能"""
    print("\n=== 知识图谱演示 ===")
    
    # 初始化知识图谱
    kg = KnowledgeGraph("your-api-key")
    
    # 构建知识图谱
    print("\n>> 构建知识图谱:")
    graph = await kg.build_knowledge_graph("diabetic_complications")
    print(f"Nodes: {graph['metadata']['node_count']}")
    print(f"Edges: {graph['metadata']['edge_count']}")
    
    # 知识查询
    print("\n>> 知识查询:")
    results = await kg.query_knowledge(
        "微血管病变与HbA1c的关系"
    )
    for result in results[:3]:  # 显示前3个结果
        print(f"\nFound relationship:")
        print(f"- Source: {result['source']}")
        print(f"- Target: {result['target']}")
        print(f"- Confidence: {result['confidence']}")
    
    # 更新知识
    print("\n>> 更新知识:")
    success = await kg.update_knowledge({
        "type": "new_finding",
        "content": {
            "relation": "correlation",
            "source": "hba1c_level",
            "target": "microvascular_complications",
            "strength": 0.85
        }
    })
    print(f"Knowledge update {'successful' if success else 'failed'}")

async def demo_full_workflow():
    """演示完整工作流程"""
    print("\n=== 完整工作流程演示 ===")
    
    # 初始化研究助手
    assistant = ResearchAssistant("your-api-key")
    
    # 1. 创建研究上下文
    print("\n>> 创建研究上下文:")
    context = await assistant.create_research_context(
        title="2型糖尿病并发症预测研究",
        description="基于多中心数据的并发症风险预测模型研究",
        domain="endocrinology"
    )
    print(f"Created research context: {context.project_id}")
    
    # 2. 分析研究主题
    print("\n>> 分析研究主题:")
    results = await assistant.analyze_research_topic(
        context,
        "糖尿病肾病早期预测标志物"
    )
    print(f"Generated {len(results)} research results")
    
    # 3. 分析患者数据
    print("\n>> 分析患者数据:")
    patient_data = [
        {
            "id": "1",
            "age": 45,
            "diagnosis": "type2_diabetes",
            "lab_results": {"hba1c": 7.2}
        },
        {
            "id": "2",
            "age": 52,
            "diagnosis": "type2_diabetes",
            "lab_results": {"hba1c": 8.1}
        }
    ]
    patient_results = await assistant.analyze_patient_data(context, patient_data)
    print(f"Generated {len(patient_results)} patient analysis results")
    
    # 4. 生成研究报告
    print("\n>> 生成研究报告:")
    report = await assistant.generate_research_report(
        context,
        results + patient_results
    )
    print("Research report generated successfully")
    print(f"Report sections: {list(report.keys())}")

async def main():
    """主函数"""
    print("启动代谢研究助手示例...")
    
    try:
        # 演示各个功能模块
        await demo_opportunity_evaluation()
        await demo_data_collection()
        await demo_risk_analysis()
        await demo_knowledge_graph()
        
        # 演示完整工作流程
        await demo_full_workflow()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
