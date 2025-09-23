#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent协调器
统一管理和协调三个专业化Agent的工作流程
实现Agent间的数据共享、结果整合和协同分析
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum

# 导入三个Agent
from .AGP_Professional_Analyzer import AGPProfessionalAnalyzer
from .Brittleness_Clinical_Advisor import BrittlenessClinicalAdvisor
from .Comprehensive_Intelligence_Analyzer import ComprehensiveIntelligenceAnalyzer

class AnalysisMode(Enum):
    """分析模式"""
    SEQUENTIAL = "顺序分析"      # 按顺序执行
    PARALLEL = "并行分析"        # 并行执行
    INTEGRATED = "整合分析"      # 深度整合
    CUSTOM = "自定义分析"        # 自定义流程

class ReportLevel(Enum):
    """报告级别"""
    BASIC = "基础报告"           # 仅核心结果
    DETAILED = "详细报告"        # 完整分析
    COMPREHENSIVE = "综合报告"   # 全面分析+AI洞察
    CLINICAL = "临床报告"        # 医疗级报告

@dataclass
class AnalysisRequest:
    """分析请求"""
    data_path: str
    patient_id: str
    patient_info: Dict[str, Any] = None
    analysis_mode: AnalysisMode = AnalysisMode.INTEGRATED
    report_level: ReportLevel = ReportLevel.COMPREHENSIVE
    enable_agents: List[str] = None  # None表示启用所有Agent
    custom_parameters: Dict[str, Any] = None

@dataclass
class AgentResult:
    """Agent结果"""
    agent_name: str
    success: bool
    result: Dict[str, Any] = None
    error_message: str = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None

class MultiAgentCoordinator:
    """
    多Agent协调器
    统一管理AGP分析、脆性评估和综合智能分析
    """
    
    def __init__(self):
        """初始化多Agent协调器"""
        self.coordinator_name = "Multi-Agent Coordinator"
        self.version = "1.0.0"
        self.description = "统一协调管理三个专业化CGM分析Agent"
        
        # 初始化三个Agent
        self.agents = {
            'agp_analyzer': AGPProfessionalAnalyzer(),
            'brittleness_advisor': BrittlenessClinicalAdvisor(),
            'intelligence_analyzer': ComprehensiveIntelligenceAnalyzer()
        }
        
        # Agent依赖关系定义
        self.agent_dependencies = {
            'agp_analyzer': [],  # 无依赖，可独立运行
            'brittleness_advisor': [],  # 无依赖，可独立运行
            'intelligence_analyzer': ['agp_analyzer']  # 依赖AGP分析结果
        }
        
        # 数据共享缓存
        self.shared_data_cache = {}
        
        # 执行统计
        self.execution_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'average_execution_time': 0.0
        }
    
    def analyze_patient(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        执行患者血糖数据的多Agent分析
        """
        print(f"🎯 {self.coordinator_name} 开始多Agent分析...")
        print(f"📊 分析模式: {request.analysis_mode.value}")
        print(f"📋 报告级别: {request.report_level.value}")
        
        start_time = datetime.now()
        
        try:
            # 1. 数据预处理
            glucose_data, timestamps = self._preprocess_data(request.data_path)
            if glucose_data is None:
                raise ValueError("数据预处理失败")
            
            # 2. 确定启用的Agent
            enabled_agents = self._determine_enabled_agents(request.enable_agents)
            
            # 3. 执行分析
            if request.analysis_mode == AnalysisMode.PARALLEL:
                agent_results = self._execute_parallel_analysis(
                    glucose_data, timestamps, request, enabled_agents
                )
            elif request.analysis_mode == AnalysisMode.SEQUENTIAL:
                agent_results = self._execute_sequential_analysis(
                    glucose_data, timestamps, request, enabled_agents
                )
            elif request.analysis_mode == AnalysisMode.INTEGRATED:
                agent_results = self._execute_integrated_analysis(
                    glucose_data, timestamps, request, enabled_agents
                )
            else:  # CUSTOM
                agent_results = self._execute_custom_analysis(
                    glucose_data, timestamps, request, enabled_agents
                )
            
            # 4. 结果整合
            integrated_report = self._integrate_results(
                agent_results, request, glucose_data, timestamps
            )
            
            # 5. 生成最终报告
            final_report = self._generate_final_report(
                integrated_report, request, agent_results
            )
            
            # 6. 更新统计信息
            self._update_execution_stats(start_time, success=True)
            
            print(f"✅ 多Agent分析完成，耗时: {(datetime.now() - start_time).total_seconds():.2f}秒")
            return final_report
            
        except Exception as e:
            self._update_execution_stats(start_time, success=False)
            error_report = self._generate_error_report(request, str(e))
            print(f"❌ 多Agent分析失败: {e}")
            return error_report
    
    def _preprocess_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """数据预处理"""
        try:
            # 支持多种数据格式
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            elif data_path.endswith('.xlsx'):
                df = pd.read_excel(data_path)
            else:
                raise ValueError(f"不支持的文件格式: {data_path}")
            
            # 标准化列名
            if 'LBDTC' in df.columns and 'LBORRES' in df.columns:
                df = df.rename(columns={'LBDTC': 'timestamp', 'LBORRES': 'glucose'})
            elif '时间' in df.columns and '值' in df.columns:
                df = df.rename(columns={'时间': 'timestamp', '值': 'glucose'})
            
            # 数据清洗
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['glucose'] = pd.to_numeric(df['glucose'], errors='coerce')
            df = df.dropna().sort_values('timestamp').reset_index(drop=True)
            
            glucose_data = df['glucose'].values
            timestamps = df['timestamp'].values
            
            # 缓存原始数据
            self.shared_data_cache['original_data'] = {
                'glucose_data': glucose_data,
                'timestamps': timestamps,
                'dataframe': df
            }
            
            print(f"✅ 数据预处理完成: {len(glucose_data)} 条记录")
            return glucose_data, timestamps
            
        except Exception as e:
            print(f"❌ 数据预处理失败: {e}")
            return None, None
    
    def _determine_enabled_agents(self, enable_agents: List[str] = None) -> List[str]:
        """确定启用的Agent"""
        if enable_agents is None:
            return list(self.agents.keys())
        
        # 验证Agent名称
        valid_agents = []
        for agent_name in enable_agents:
            if agent_name in self.agents:
                valid_agents.append(agent_name)
            else:
                print(f"⚠️  未知的Agent: {agent_name}")
        
        return valid_agents
    
    def _execute_parallel_analysis(self, glucose_data: np.ndarray, 
                                 timestamps: np.ndarray,
                                 request: AnalysisRequest,
                                 enabled_agents: List[str]) -> Dict[str, AgentResult]:
        """并行执行分析"""
        print("🔄 开始并行分析...")
        
        agent_results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            for agent_name in enabled_agents:
                future = executor.submit(
                    self._execute_single_agent,
                    agent_name, glucose_data, timestamps, request
                )
                futures[agent_name] = future
            
            # 收集结果
            for agent_name, future in futures.items():
                try:
                    result = future.result(timeout=300)  # 5分钟超时
                    agent_results[agent_name] = result
                except Exception as e:
                    agent_results[agent_name] = AgentResult(
                        agent_name=agent_name,
                        success=False,
                        error_message=str(e)
                    )
        
        return agent_results
    
    def _execute_sequential_analysis(self, glucose_data: np.ndarray,
                                   timestamps: np.ndarray,
                                   request: AnalysisRequest,
                                   enabled_agents: List[str]) -> Dict[str, AgentResult]:
        """顺序执行分析"""
        print("📈 开始顺序分析...")
        
        agent_results = {}
        
        # 按依赖关系排序
        ordered_agents = self._sort_agents_by_dependency(enabled_agents)
        
        for agent_name in ordered_agents:
            print(f"🔄 执行 {agent_name}...")
            
            result = self._execute_single_agent(
                agent_name, glucose_data, timestamps, request
            )
            agent_results[agent_name] = result
            
            # 如果关键Agent失败，可能影响后续分析
            if not result.success and agent_name == 'agp_analyzer':
                print(f"⚠️  关键Agent {agent_name} 失败，继续执行其他Agent")
        
        return agent_results
    
    def _execute_integrated_analysis(self, glucose_data: np.ndarray,
                                   timestamps: np.ndarray,
                                   request: AnalysisRequest,
                                   enabled_agents: List[str]) -> Dict[str, AgentResult]:
        """整合分析执行"""
        print("🔗 开始整合分析...")
        
        agent_results = {}
        
        # 第一阶段：基础分析 (AGP + 脆性)
        phase1_agents = ['agp_analyzer', 'brittleness_advisor']
        phase1_enabled = [a for a in phase1_agents if a in enabled_agents]
        
        if phase1_enabled:
            print("📊 第一阶段：基础分析")
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    agent_name: executor.submit(
                        self._execute_single_agent,
                        agent_name, glucose_data, timestamps, request
                    )
                    for agent_name in phase1_enabled
                }
                
                for agent_name, future in futures.items():
                    agent_results[agent_name] = future.result()
        
        # 第二阶段：综合智能分析 (利用第一阶段结果)
        if 'intelligence_analyzer' in enabled_agents:
            print("🧠 第二阶段：综合智能分析")
            
            # 传递第一阶段结果给智能分析器
            phase1_results = {k: v.result for k, v in agent_results.items() if v.success}
            request_with_context = request
            request_with_context.custom_parameters = {
                **(request.custom_parameters or {}),
                'phase1_results': phase1_results
            }
            
            result = self._execute_single_agent(
                'intelligence_analyzer', glucose_data, timestamps, request_with_context
            )
            agent_results['intelligence_analyzer'] = result
        
        return agent_results
    
    def _execute_custom_analysis(self, glucose_data: np.ndarray,
                                timestamps: np.ndarray,
                                request: AnalysisRequest,
                                enabled_agents: List[str]) -> Dict[str, AgentResult]:
        """自定义分析执行"""
        print("⚙️  开始自定义分析...")
        
        # 自定义逻辑可以根据具体需求实现
        # 这里提供一个灵活的框架
        
        custom_params = request.custom_parameters or {}
        execution_order = custom_params.get('execution_order', enabled_agents)
        parallel_groups = custom_params.get('parallel_groups', [])
        
        agent_results = {}
        
        # 处理并行组
        for group in parallel_groups:
            group_agents = [a for a in group if a in enabled_agents]
            if group_agents:
                with ThreadPoolExecutor(max_workers=len(group_agents)) as executor:
                    futures = {
                        agent_name: executor.submit(
                            self._execute_single_agent,
                            agent_name, glucose_data, timestamps, request
                        )
                        for agent_name in group_agents
                    }
                    
                    for agent_name, future in futures.items():
                        agent_results[agent_name] = future.result()
        
        # 处理剩余的顺序执行Agent
        remaining_agents = [a for a in execution_order 
                          if a in enabled_agents and a not in agent_results]
        
        for agent_name in remaining_agents:
            result = self._execute_single_agent(
                agent_name, glucose_data, timestamps, request
            )
            agent_results[agent_name] = result
        
        return agent_results
    
    def _execute_single_agent(self, agent_name: str, 
                            glucose_data: np.ndarray,
                            timestamps: np.ndarray,
                            request: AnalysisRequest) -> AgentResult:
        """执行单个Agent分析"""
        start_time = datetime.now()
        
        try:
            agent = self.agents[agent_name]
            
            if agent_name == 'agp_analyzer':
                result = agent.generate_professional_agp_report(
                    request.data_path, request.patient_id
                )
            elif agent_name == 'brittleness_advisor':
                result = agent.generate_brittleness_report(
                    glucose_data, request.patient_id, request.patient_info
                )
            elif agent_name == 'intelligence_analyzer':
                result = agent.generate_comprehensive_report(
                    glucose_data, request.patient_id, request.patient_info
                )
            else:
                raise ValueError(f"未知的Agent: {agent_name}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResult(
                agent_name=agent_name,
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    'data_points': len(glucose_data),
                    'analysis_time': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return AgentResult(
                agent_name=agent_name,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _integrate_results(self, agent_results: Dict[str, AgentResult],
                         request: AnalysisRequest,
                         glucose_data: np.ndarray,
                         timestamps: np.ndarray) -> Dict[str, Any]:
        """整合Agent结果"""
        print("🔗 开始结果整合...")
        
        integrated_data = {
            'analysis_overview': {
                'patient_id': request.patient_id,
                'analysis_mode': request.analysis_mode.value,
                'report_level': request.report_level.value,
                'data_summary': {
                    'total_readings': len(glucose_data),
                    'time_range': f"{timestamps[0]} - {timestamps[-1]}" if len(timestamps) > 0 else "N/A",
                    'glucose_range': f"{np.min(glucose_data):.1f} - {np.max(glucose_data):.1f} mmol/L"
                }
            },
            'agent_results': {},
            'cross_agent_insights': [],
            'consensus_findings': {},
            'conflicting_assessments': []
        }
        
        # 收集成功的Agent结果
        successful_results = {}
        for agent_name, result in agent_results.items():
            if result.success:
                successful_results[agent_name] = result.result
                integrated_data['agent_results'][agent_name] = {
                    'status': 'success',
                    'execution_time': result.execution_time,
                    'key_findings': self._extract_key_findings(result.result, agent_name)
                }
            else:
                integrated_data['agent_results'][agent_name] = {
                    'status': 'failed',
                    'error': result.error_message,
                    'execution_time': result.execution_time
                }
        
        # 跨Agent洞察分析
        if len(successful_results) >= 2:
            cross_insights = self._generate_cross_agent_insights(successful_results)
            integrated_data['cross_agent_insights'] = cross_insights
        
        # 共识发现
        consensus = self._identify_consensus_findings(successful_results)
        integrated_data['consensus_findings'] = consensus
        
        # 冲突评估识别
        conflicts = self._identify_conflicting_assessments(successful_results)
        integrated_data['conflicting_assessments'] = conflicts
        
        return integrated_data
    
    def _generate_final_report(self, integrated_data: Dict[str, Any],
                             request: AnalysisRequest,
                             agent_results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """生成最终报告"""
        print("📋 生成最终综合报告...")
        
        final_report = {
            'coordinator_info': {
                'name': self.coordinator_name,
                'version': self.version,
                'analysis_time': datetime.now().isoformat(),
                'report_level': request.report_level.value
            },
            'executive_summary': self._generate_executive_summary(integrated_data, agent_results),
            'detailed_results': integrated_data,
            'clinical_recommendations': self._synthesize_clinical_recommendations(integrated_data),
            'quality_assessment': self._assess_analysis_quality(agent_results),
            'next_actions': self._generate_next_actions(integrated_data, request)
        }
        
        # 根据报告级别调整内容详细程度
        if request.report_level == ReportLevel.BASIC:
            final_report = self._simplify_report_for_basic_level(final_report)
        elif request.report_level == ReportLevel.CLINICAL:
            final_report = self._enhance_report_for_clinical_level(final_report, integrated_data)
        
        return final_report
    
    def _generate_executive_summary(self, integrated_data: Dict[str, Any],
                                  agent_results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """生成执行摘要"""
        successful_agents = sum(1 for r in agent_results.values() if r.success)
        total_agents = len(agent_results)
        
        # 提取关键指标
        key_metrics = {}
        if 'agp_analyzer' in integrated_data['agent_results']:
            agp_findings = integrated_data['agent_results']['agp_analyzer'].get('key_findings', {})
            key_metrics.update(agp_findings)
        
        return {
            'analysis_success_rate': f"{successful_agents}/{total_agents}",
            'key_metrics': key_metrics,
            'overall_assessment': self._determine_overall_assessment(integrated_data),
            'priority_concerns': self._identify_priority_concerns(integrated_data),
            'confidence_level': self._calculate_analysis_confidence(agent_results)
        }
    
    def _synthesize_clinical_recommendations(self, integrated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """合成临床建议"""
        all_recommendations = []
        
        # 从各Agent收集建议
        for agent_name, agent_data in integrated_data['agent_results'].items():
            if agent_data['status'] == 'success' and 'key_findings' in agent_data:
                agent_recs = agent_data['key_findings'].get('recommendations', [])
                for rec in agent_recs:
                    rec['source_agent'] = agent_name
                    all_recommendations.append(rec)
        
        # 去重和优先级排序
        synthesized_recommendations = self._deduplicate_and_prioritize_recommendations(
            all_recommendations
        )
        
        return synthesized_recommendations
    
    # 辅助方法实现
    def _sort_agents_by_dependency(self, enabled_agents: List[str]) -> List[str]:
        """按依赖关系排序Agent"""
        sorted_agents = []
        remaining_agents = enabled_agents.copy()
        
        while remaining_agents:
            # 找到没有未满足依赖的Agent
            ready_agents = []
            for agent in remaining_agents:
                dependencies = self.agent_dependencies.get(agent, [])
                if all(dep in sorted_agents or dep not in enabled_agents for dep in dependencies):
                    ready_agents.append(agent)
            
            if not ready_agents:
                # 处理循环依赖或未解决的依赖
                ready_agents = remaining_agents
            
            sorted_agents.extend(ready_agents)
            for agent in ready_agents:
                remaining_agents.remove(agent)
        
        return sorted_agents
    
    def _extract_key_findings(self, result: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """提取Agent关键发现"""
        key_findings = {}
        
        if agent_name == 'agp_analyzer':
            key_findings = {
                'tir': result.get('94_indicators', {}).get('target_standard_range', 'N/A'),
                'cv': result.get('94_indicators', {}).get('cv_glucose', 'N/A'),
                'control_quality': result.get('agp_interpretation', {}).get('overall_control', 'N/A'),
                'recommendations': result.get('clinical_recommendations', [])
            }
        elif agent_name == 'brittleness_advisor':
            key_findings = {
                'brittleness_type': result.get('brittleness_profile', {}).get('type', 'N/A'),
                'severity_score': result.get('brittleness_profile', {}).get('severity_score', 'N/A'),
                'risk_level': result.get('brittleness_profile', {}).get('risk_level', 'N/A'),
                'recommendations': result.get('clinical_recommendations', [])
            }
        elif agent_name == 'intelligence_analyzer':
            key_findings = {
                'health_status': result.get('comprehensive_health_assessment', {}).get('health_status', 'N/A'),
                'overall_score': result.get('comprehensive_health_assessment', {}).get('overall_score', 'N/A'),
                'ai_insights': result.get('ai_insights', []),
                'recommendations': result.get('intelligent_recommendations', [])
            }
        
        return key_findings
    
    def _generate_cross_agent_insights(self, successful_results: Dict[str, Dict[str, Any]]) -> List[str]:
        """生成跨Agent洞察"""
        insights = []
        
        # AGP + 脆性分析的交叉洞察
        if 'agp_analyzer' in successful_results and 'brittleness_advisor' in successful_results:
            agp_cv = successful_results['agp_analyzer'].get('94_indicators', {}).get('cv_glucose', 0)
            brittleness_type = successful_results['brittleness_advisor'].get('brittleness_profile', {}).get('type', '')
            
            if agp_cv > 50 and '混沌' in brittleness_type:
                insights.append("AGP高变异性与混沌脆性一致，建议采用保守治疗策略")
        
        # 其他交叉分析...
        
        return insights
    
    def _identify_consensus_findings(self, successful_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """识别共识发现"""
        consensus = {}
        
        # 收集各Agent对血糖控制质量的评估
        control_assessments = []
        for agent_name, result in successful_results.items():
            if agent_name == 'agp_analyzer':
                assessment = result.get('agp_interpretation', {}).get('overall_control', '')
                if assessment:
                    control_assessments.append(assessment)
        
        if control_assessments:
            consensus['glucose_control_consensus'] = max(set(control_assessments), 
                                                       key=control_assessments.count)
        
        return consensus
    
    def _identify_conflicting_assessments(self, successful_results: Dict[str, Dict[str, Any]]) -> List[str]:
        """识别冲突评估"""
        conflicts = []
        
        # 检查不同Agent之间的评估冲突
        # 这里可以添加具体的冲突检测逻辑
        
        return conflicts
    
    def _determine_overall_assessment(self, integrated_data: Dict[str, Any]) -> str:
        """确定总体评估"""
        # 基于各Agent结果确定总体评估
        return "需要进一步评估"  # 简化实现
    
    def _identify_priority_concerns(self, integrated_data: Dict[str, Any]) -> List[str]:
        """识别优先关注点"""
        concerns = []
        
        # 基于各Agent结果识别优先关注点
        for agent_name, agent_data in integrated_data['agent_results'].items():
            if agent_data['status'] == 'success':
                # 提取高优先级关注点
                pass
        
        return concerns
    
    def _calculate_analysis_confidence(self, agent_results: Dict[str, AgentResult]) -> float:
        """计算分析置信度"""
        successful_count = sum(1 for r in agent_results.values() if r.success)
        total_count = len(agent_results)
        
        if total_count == 0:
            return 0.0
        
        base_confidence = successful_count / total_count
        
        # 根据Agent重要性调整权重
        weights = {
            'agp_analyzer': 0.4,
            'brittleness_advisor': 0.3,
            'intelligence_analyzer': 0.3
        }
        
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for agent_name, result in agent_results.items():
            weight = weights.get(agent_name, 0.1)
            total_weight += weight
            if result.success:
                weighted_confidence += weight
        
        if total_weight > 0:
            return weighted_confidence / total_weight
        else:
            return base_confidence
    
    def _deduplicate_and_prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重和优先级排序建议"""
        # 简化实现：按优先级排序
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        
        return sorted(recommendations, 
                     key=lambda x: priority_order.get(x.get('priority', 'MEDIUM'), 2))
    
    def _assess_analysis_quality(self, agent_results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """评估分析质量"""
        quality_metrics = {
            'completeness': sum(1 for r in agent_results.values() if r.success) / len(agent_results),
            'execution_time': {
                agent_name: result.execution_time 
                for agent_name, result in agent_results.items()
            },
            'data_quality_issues': [],  # 可以添加数据质量检查
            'analysis_reliability': self._calculate_analysis_confidence(agent_results)
        }
        
        return quality_metrics
    
    def _generate_next_actions(self, integrated_data: Dict[str, Any], 
                             request: AnalysisRequest) -> List[str]:
        """生成下一步行动建议"""
        actions = []
        
        # 基于分析结果生成行动建议
        if integrated_data['consensus_findings']:
            actions.append("基于共识发现，建议执行相应的临床干预")
        
        if integrated_data['conflicting_assessments']:
            actions.append("存在评估冲突，建议进一步评估和专家会诊")
        
        actions.append("建议4-6周后重新评估治疗效果")
        
        return actions
    
    def _simplify_report_for_basic_level(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """为基础级别简化报告"""
        # 保留关键信息，移除详细分析
        simplified = {
            'coordinator_info': report['coordinator_info'],
            'executive_summary': report['executive_summary'],
            'key_recommendations': report['clinical_recommendations'][:3],  # 只保留前3个建议
            'next_actions': report['next_actions']
        }
        return simplified
    
    def _enhance_report_for_clinical_level(self, report: Dict[str, Any], 
                                         integrated_data: Dict[str, Any]) -> Dict[str, Any]:
        """为临床级别增强报告"""
        # 添加临床专用信息
        report['clinical_summary'] = {
            'diagnosis_support': self._generate_diagnosis_support(integrated_data),
            'treatment_pathway': self._generate_treatment_pathway(integrated_data),
            'risk_stratification': self._generate_risk_stratification(integrated_data),
            'monitoring_recommendations': self._generate_monitoring_recommendations(integrated_data)
        }
        
        return report
    
    def _generate_diagnosis_support(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成诊断支持信息"""
        return {'status': 'placeholder'}  # 简化实现
    
    def _generate_treatment_pathway(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成治疗路径建议"""
        return {'status': 'placeholder'}  # 简化实现
    
    def _generate_risk_stratification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成风险分层"""
        return {'status': 'placeholder'}  # 简化实现
    
    def _generate_monitoring_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成监测建议"""
        return {'status': 'placeholder'}  # 简化实现
    
    def _generate_error_report(self, request: AnalysisRequest, error_message: str) -> Dict[str, Any]:
        """生成错误报告"""
        return {
            'coordinator_info': {
                'name': self.coordinator_name,
                'version': self.version,
                'analysis_time': datetime.now().isoformat(),
                'status': 'ERROR'
            },
            'error_details': {
                'message': error_message,
                'patient_id': request.patient_id,
                'analysis_mode': request.analysis_mode.value
            },
            'suggested_actions': [
                "检查数据格式和完整性",
                "验证文件路径是否正确",
                "联系技术支持获取帮助"
            ]
        }
    
    def _update_execution_stats(self, start_time: datetime, success: bool):
        """更新执行统计"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        self.execution_stats['total_analyses'] += 1
        if success:
            self.execution_stats['successful_analyses'] += 1
        else:
            self.execution_stats['failed_analyses'] += 1
        
        # 更新平均执行时间
        total = self.execution_stats['total_analyses']
        current_avg = self.execution_stats['average_execution_time']
        self.execution_stats['average_execution_time'] = (
            (current_avg * (total - 1) + execution_time) / total
        )
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        return {
            'coordinator_info': {
                'name': self.coordinator_name,
                'version': self.version,
                'active_agents': len(self.agents)
            },
            'execution_stats': self.execution_stats,
            'available_agents': list(self.agents.keys()),
            'cache_status': {
                'cached_datasets': len(self.shared_data_cache)
            }
        }

# 便捷函数
def create_analysis_request(data_path: str, 
                          patient_id: str,
                          analysis_mode: str = "integrated",
                          report_level: str = "comprehensive",
                          **kwargs) -> AnalysisRequest:
    """创建分析请求的便捷函数"""
    mode_map = {
        "sequential": AnalysisMode.SEQUENTIAL,
        "parallel": AnalysisMode.PARALLEL,
        "integrated": AnalysisMode.INTEGRATED,
        "custom": AnalysisMode.CUSTOM
    }
    
    level_map = {
        "basic": ReportLevel.BASIC,
        "detailed": ReportLevel.DETAILED,
        "comprehensive": ReportLevel.COMPREHENSIVE,
        "clinical": ReportLevel.CLINICAL
    }
    
    return AnalysisRequest(
        data_path=data_path,
        patient_id=patient_id,
        analysis_mode=mode_map.get(analysis_mode.lower(), AnalysisMode.INTEGRATED),
        report_level=level_map.get(report_level.lower(), ReportLevel.COMPREHENSIVE),
        **kwargs
    )

if __name__ == "__main__":
    # 测试代码
    coordinator = MultiAgentCoordinator()
    print(f"✅ {coordinator.coordinator_name} 初始化完成")
    print(f"🎯 管理 {len(coordinator.agents)} 个专业化Agent")
    print(f"📊 支持多种分析模式和报告级别")
    
    # 显示协调器状态
    status = coordinator.get_coordinator_status()
    print(f"📈 协调器状态: {json.dumps(status, indent=2, ensure_ascii=False)}")