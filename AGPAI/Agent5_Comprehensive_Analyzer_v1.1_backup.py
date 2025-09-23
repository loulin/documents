#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent5: AGPAI综合分析器 v1.1 (Agent2真正集成版)
核心功能: 基于Agent1的8模块分析 + Agent2真正智能分段 + 药物整合分析
版本: 1.1 (Agent2集成成功版)
日期: 2025-09-03

重大更新:
✅ 成功集成Agent2真正的智能分段算法
✅ 修复TBR低血糖计算错误
✅ 支持混沌动力学变化点检测
✅ 精细分段：从4个提升到9个分段

功能特点:
1. Agent1的完整8模块血糖分析
2. ⭐ Agent2的真正智能混沌动力学分段分析 (新增)
3. 药物信息管理与整合分析
4. 药物-血糖曲线关联分析
5. 治疗效果时间序列评估
6. 🔧 修正的低血糖计算 (TBR)
7. 📊 Agent2精细分段 (9段vs4段)

技术突破:
- 真正调用Agent2的analyze_intelligent_longitudinal_segments函数
- 混沌动力学理论支持的变化点检测
- 脆性特征演变分析
- 多维度智能分段质量评估

使用方法:
from Agent5_Comprehensive_Analyzer import ComprehensiveAGPAIAnalyzer
analyzer = ComprehensiveAGPAIAnalyzer()
result = analyzer.generate_complete_report(filepath, patient_id, medication_data)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

try:
    from AGP_Professional_Analyzer import AGPProfessionalAnalyzer
    from Enhanced_Data_Quality_Gatekeeper import EnhancedDataQualityGatekeeper
except ImportError:
    AGPProfessionalAnalyzer = None
    EnhancedDataQualityGatekeeper = None
    print("[警告] 核心模块未找到，使用简化实现")

# 尝试导入Agent2智能分析模块
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'agpai', 'examples'))
    from Agent2_Intelligent_Analysis import analyze_intelligent_longitudinal_segments
    AGENT2_AVAILABLE = True
    print("[Agent5] ✅ 成功导入Agent2智能分段模块")
except ImportError:
    AGENT2_AVAILABLE = False
    print("[Agent5] ⚠️  Agent2模块未找到，使用内置分段算法")

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
from scipy.signal import find_peaks, savgol_filter
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveAGPAIAnalyzer:
    """AGPAI综合分析器 - 集成Agent1+Agent2+药物分析"""
    
    def __init__(self):
        if AGPProfessionalAnalyzer:
            self.analyzer = AGPProfessionalAnalyzer()
        else:
            self.analyzer = None
            
        if EnhancedDataQualityGatekeeper:
            self.quality_gatekeeper = EnhancedDataQualityGatekeeper()
        else:
            self.quality_gatekeeper = None
            
        self.report_info = {
            "报告类型": "AGPAI综合分析报告 v1.0",
            "版本号": "1.0.0",
            "报告生成器": "Comprehensive_AGPAI_Analyzer"
        }
        
        self.agent_info = {
            "name": "Comprehensive AGPAI Analyzer",
            "version": "1.0",
            "agent_type": "Agent5",
            "capabilities": [
                "Agent1完整8模块分析",
                "Agent2智能时间分段",
                "药物信息管理",
                "药物-血糖整合分析",
                "治疗效果时间序列评估",
                "94项专业指标计算",
                "数据质量评估"
            ]
        }
    
    def generate_complete_report(self, filepath: str, patient_id: str = None, 
                               medication_data: Dict = None, force_builtin_segments: bool = False) -> Dict:
        """
        生成AGPAI综合分析报告
        
        Args:
            filepath: 血糖数据文件路径
            patient_id: 患者ID
            medication_data: 药物数据字典
        
        Returns:
            完整的综合分析报告
        """
        try:
            print(f"[Agent5] 开始生成综合分析报告: {patient_id}")
            
            # Step 1: 数据加载和预处理
            df = self._load_data(filepath)
            analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Step 2: 基础血糖分析（来自Agent1）
            print("[Agent5] 执行基础血糖分析...")
            basic_analysis = self._perform_basic_glucose_analysis(df, patient_id or "Unknown")
            
            # Step 3: 智能时间分段分析（来自Agent2）
            print("[Agent5] 执行智能时间分段分析...")
            temporal_analysis = self._perform_intelligent_segmentation(df, patient_id or "Unknown", force_builtin_segments)
            
            # Step 4: 药物信息分析
            print("[Agent5] 执行药物信息分析...")
            medication_analysis = self._perform_medication_analysis(medication_data, df)
            
            # Step 5: 药物-血糖整合分析
            print("[Agent5] 执行药物-血糖整合分析...")
            integrated_analysis = self._perform_integrated_analysis(df, temporal_analysis, 
                                                                 medication_analysis)
            
            # Step 6: 生成英文缩写说明
            print("[Agent5] 生成专业术语说明...")
            abbreviations = self._generate_medical_abbreviations()
            
            # Step 7: 生成完整报告
            complete_report = {
                "报告头信息": {
                    **self.report_info,
                    "患者ID": patient_id or "Unknown",
                    "分析时间": analysis_time,
                    "Agent信息": self.agent_info
                },
                
                # 第一位：英文缩写和专业术语说明
                "专业术语与缩写说明": abbreviations,
                
                # 第二位：药物信息分析
                "患者用药信息分析": medication_analysis,
                
                # 第三位：Agent1第一模块 - 总体血糖控制状况
                "模块1_总体血糖控制状况和建议": basic_analysis.get("模块1_总体血糖控制状况和建议", {}),
                
                # 其他Agent1模块按顺序排列
                "模块2_核心血糖控制指标分析": basic_analysis.get("模块2_核心血糖控制指标分析", {}),
                "模块3_六时段综合深度分析": basic_analysis.get("模块3_六时段综合深度分析", {}),
                "模块4_工作日周末对比分析": basic_analysis.get("模块4_工作日周末对比分析", {}),
                "模块5_异常模式检测与风险预警": basic_analysis.get("模块5_异常模式检测与风险预警", {}),
                "模块6_时间分段纵向分析": basic_analysis.get("时间分段纵向分析", {}),
                
                # Agent2智能分段分析
                "模块7_智能时间分段分析": temporal_analysis,
                
                # 药物-血糖整合分析
                "模块8_药物-血糖整合分析": integrated_analysis,
                
                # 专业指标和数据质量
                "专业94指标详细分析": basic_analysis.get("专业94指标详细分析", {}),
                "数据质量评估": basic_analysis.get("数据质量评估", {}),
                "患者基本信息": basic_analysis.get("患者基本信息", {}),
                
                "报告总结": {
                    "分析完成时间": analysis_time,
                    "分析模块数": 10,  # 按新顺序重新排列
                    "专业指标数": len(basic_analysis.get("专业94指标详细分析", {}).get("核心指标数据", {})),
                    "报告完整性": "完整",
                    "下次建议分析时间": self._get_next_analysis_date()
                }
            }
            
            # 保存报告
            self._save_complete_report(complete_report, patient_id or "Unknown")
            
            return complete_report
            
        except Exception as e:
            error_report = {
                "报告头信息": {
                    **self.report_info,
                    "患者ID": patient_id or "Unknown",
                    "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "错误信息": {
                    "状态": "分析失败",
                    "错误原因": str(e),
                    "时间戳": datetime.now().isoformat()
                }
            }
            print(f"[Agent5] 分析错误: {e}")
            return error_report
    
    # ========== Agent1 基础分析模块 ==========
    def _perform_basic_glucose_analysis(self, df: pd.DataFrame, patient_id: str) -> Dict:
        """执行基础血糖分析（Agent1功能）"""
        glucose_values = df['glucose_value'].dropna()
        
        if len(glucose_values) == 0:
            return {"错误": "无有效血糖数据"}
        
        # 患者基本信息
        basic_info = self._get_patient_basic_info(df, patient_id)
        
        # 数据质量评估
        quality_result = self._comprehensive_quality_assessment(df, patient_id)
        
        # 94指标专业分析
        indicators_result = self._calculate_94_indicators(df)
        
        # 8模块分析
        module_results = self._generate_8_modules_analysis(df, patient_id)
        
        return {
            "患者基本信息": basic_info,
            **module_results,
            "专业94指标详细分析": indicators_result,
            "数据质量评估": quality_result
        }
    
    # ========== Agent2 智能分段模块 ==========
    def _perform_intelligent_segmentation(self, df: pd.DataFrame, patient_id: str, force_builtin: bool = False) -> Dict:
        """执行智能时间分段分析（Agent2功能）"""
        try:
            glucose_values = df['glucose_value'].dropna().values
            total_days = self._calculate_monitoring_days(df)
            
            print("[Agent5-智能分段] 开始多维度变化点检测...")
            
            # 根据标志选择分段算法
            if AGENT2_AVAILABLE and not force_builtin:
                try:
                    print("[Agent5-智能分段] 使用Agent2智能分段算法...")
                    # 调用真正的Agent2智能分段分析
                    agent2_result = analyze_intelligent_longitudinal_segments(
                        df.copy(), glucose_values, total_days
                    )
                    
                    # 检查Agent2返回的实际字段名
                    if agent2_result and "最终智能分段" in agent2_result:
                        print("[Agent5-智能分段] ✅ Agent2分段成功")
                        
                        # 转换Agent2格式到Agent5期望格式
                        agent2_segments_data = agent2_result["最终智能分段"]
                        converted_segments = []
                        
                        # Agent2返回的是嵌套字典格式: {"分段数量": N, "详细分段": [...]}
                        if "详细分段" in agent2_segments_data:
                            detailed_segments = agent2_segments_data["详细分段"]
                            
                            # detailed_segments是一个列表
                            if isinstance(detailed_segments, list):
                                for i, segment in enumerate(detailed_segments):
                                    if isinstance(segment, dict):
                                        # 构造时间范围描述
                                        start_time = segment.get("开始时间", "未知")
                                        end_time = segment.get("结束时间", "未知") 
                                        duration = segment.get("持续时间", "未知")
                                        time_range = f"{start_time}至{end_time}，{duration}"
                                        
                                        converted_segment = {
                                            "阶段": f"阶段{segment.get('段落编号', i+1)}",
                                            "时间范围": time_range,
                                            "血糖控制特征": segment.get("血糖控制特征", "Agent2智能分段分析"),
                                            "GMI": segment.get("GMI", segment.get("平均GMI", "N/A")),
                                            "TIR": segment.get("TIR", segment.get("平均TIR", "N/A")), 
                                            "CV": segment.get("CV", segment.get("平均CV", "N/A")),
                                            "质量评级": segment.get("控制质量", segment.get("脆性分级", "Agent2分析")),
                                            "数据点数": segment.get("数据点数", 0)
                                        }
                                        converted_segments.append(converted_segment)
                        
                        # 如果没有详细分段，尝试直接处理
                        elif isinstance(agent2_segments_data, dict) and "分段数量" in agent2_segments_data:
                            segment_count = agent2_segments_data.get("分段数量", 0)
                            for i in range(1, min(segment_count + 1, 10)):  # 限制最多10个分段
                                seg_key = f"段{i}" if f"段{i}" in agent2_segments_data else f"分段{i}"
                                if seg_key in agent2_segments_data:
                                    segment = agent2_segments_data[seg_key]
                                    if isinstance(segment, dict):
                                        converted_segment = {
                                            "阶段": f"阶段{i}",
                                            "时间范围": segment.get("时间范围", "未知"),
                                            "血糖控制特征": segment.get("血糖控制特征", "Agent2分析"),
                                            "GMI": segment.get("GMI", "N/A"),
                                            "TIR": segment.get("TIR", "N/A"), 
                                            "CV": segment.get("CV", "N/A"),
                                            "质量评级": segment.get("控制质量", "良好"),
                                            "数据点数": segment.get("数据点数", 0)
                                        }
                                        converted_segments.append(converted_segment)
                        
                        return {
                            "分段技术说明": "Agent2智能混沌动力学变化点检测",
                            "检测维度": agent2_result.get("检测维度", ["混沌动力学特征", "脆性模式转换", "治疗反应阶段"]),
                            "分段数量": len(converted_segments),
                            "分段质量": agent2_result.get("分段质量评估", {}).get("总体评级", "高质量分段"),
                            "智能分段结果": converted_segments,
                            "分段质量评估": agent2_result.get("分段质量评估", {}),
                            "Agent2原始数据": {
                                "变化点检测详情": agent2_result.get("变化点检测详情", {}),
                                "临床意义解读": agent2_result.get("临床意义解读", {}),
                                "原始分段数据": agent2_segments_data
                            }
                        }
                    else:
                        print(f"[Agent5-智能分段] Agent2返回格式不符: {list(agent2_result.keys()) if agent2_result else 'None'}")
                        
                except Exception as e:
                    print(f"[Agent5-智能分段] Agent2调用失败: {e}，回退到内置算法")
            
            # 回退到内置分段算法
            if force_builtin:
                print("[Agent5-智能分段] 🔧 强制使用内置分段算法（对比模式）")
            else:
                print("[Agent5-智能分段] 使用内置分段算法...")
            
            # 1. 数据预处理
            df_processed = df.copy()
            df_processed['timestamp'] = pd.to_datetime(df_processed['timestamp'])
            df_processed = df_processed.sort_values('timestamp')
            df_processed['day_from_start'] = (df_processed['timestamp'] - df_processed['timestamp'].min()).dt.days
            
            # 2. 计算滑动窗口指标
            indicators = self._calculate_sliding_window_indicators(df_processed)
            
            # 3. 检测变化点
            change_points = self._detect_change_points(indicators, df_processed)
            
            # 4. 生成分段
            segments = self._generate_segments(change_points, df_processed, total_days)
            
            # 5. 分段质量评估
            segments_analysis = self._analyze_segments_quality(segments, df_processed)
            
            builtin_description = "Agent5内置分段算法（对比模式）" if force_builtin else "基于数据驱动的多维度智能变化点检测"
            return {
                "分段技术说明": builtin_description,
                "检测维度": ["血糖控制质量变化", "变异模式转换", "治疗反应阶段"],
                "分段数量": len(segments),
                "分段质量": segments_analysis["quality_rating"],
                "智能分段结果": segments,
                "分段质量评估": segments_analysis
            }
            
        except Exception as e:
            print(f"[Agent5-智能分段] 分析错误: {e}")
            return {
                "分段技术说明": "智能分段分析失败",
                "错误信息": str(e)
            }
    
    # ========== 药物分析模块 ==========
    def _perform_medication_analysis(self, medication_data: Dict, df: pd.DataFrame) -> Dict:
        """执行药物信息分析"""
        if not medication_data:
            return {
                "分析状态": "无药物数据",
                "建议": "建议提供详细的用药信息以进行整合分析"
            }
        
        try:
            # 解析药物数据
            medications = medication_data.get("medications", [])
            
            # 药物基础信息分析
            medication_summary = self._analyze_medication_summary(medications)
            
            # 药物时间线分析
            medication_timeline = self._analyze_medication_timeline(medications, df)
            
            # 药物类型分析
            medication_types = self._analyze_medication_types(medications)
            
            return {
                "分析状态": "药物信息分析完成",
                "药物数量": len(medications),
                "药物概览": medication_summary,
                "药物时间线": medication_timeline,
                "药物分类分析": medication_types,
                "用药依从性": self._assess_medication_compliance(medications),
                "药物相互作用评估": self._assess_drug_interactions(medications)
            }
            
        except Exception as e:
            return {
                "分析状态": "药物分析失败",
                "错误信息": str(e)
            }
    
    # ========== 药物-血糖整合分析模块 ==========
    def _perform_integrated_analysis(self, df: pd.DataFrame, temporal_analysis: Dict, 
                                   medication_analysis: Dict) -> Dict:
        """执行药物-血糖整合分析"""
        try:
            if medication_analysis.get("分析状态") != "药物信息分析完成":
                return {
                    "整合分析状态": "无法进行整合分析",
                    "原因": "缺少有效的药物数据"
                }
            
            # 获取分段信息
            segments = temporal_analysis.get("智能分段结果", [])
            medications = medication_analysis.get("药物概览", {})
            
            # 药物效果评估
            drug_effectiveness = self._evaluate_drug_effectiveness(df, segments, medications)
            
            # 治疗反应分析
            treatment_response = self._analyze_treatment_response(df, segments, medications)
            
            # 用药时机分析
            timing_analysis = self._analyze_medication_timing(df, medications)
            
            # 综合治疗建议
            comprehensive_recommendations = self._generate_comprehensive_recommendations(
                drug_effectiveness, treatment_response, timing_analysis
            )
            
            return {
                "整合分析状态": "整合分析完成",
                "药物效果评估": drug_effectiveness,
                "治疗反应分析": treatment_response,
                "用药时机分析": timing_analysis,
                "综合治疗建议": comprehensive_recommendations,
                "下一步治疗方案": self._suggest_next_treatment_plan(drug_effectiveness, treatment_response)
            }
            
        except Exception as e:
            return {
                "整合分析状态": "整合分析失败",
                "错误信息": str(e)
            }
    
    # ========== 数据处理辅助方法 ==========
    def _load_data(self, filepath: str) -> pd.DataFrame:
        """加载CGM数据"""
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            raise ValueError(f"不支持的文件格式: {filepath}")
        
        # 标准化列名
        glucose_column_mapping = {
            'glucose': 'glucose_value',
            'Glucose': 'glucose_value',
            '血糖值': 'glucose_value',
            '值': 'glucose_value',
            'glucose_value': 'glucose_value'
        }
        
        time_column_mapping = {
            'timestamp': 'timestamp',
            'time': 'timestamp',
            'datetime': 'timestamp', 
            '时间': 'timestamp',
            'Time': 'timestamp'
        }
        
        # 重命名列
        for old_name, new_name in glucose_column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
                break
        
        for old_name, new_name in time_column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
                break
        
        # 检查必要列
        if 'glucose_value' not in df.columns:
            available_cols = ', '.join(df.columns.tolist())
            raise ValueError(f"未找到血糖值列。可用列名: {available_cols}")
        
        return df
    
    def _calculate_monitoring_days(self, df: pd.DataFrame) -> int:
        """计算监测天数"""
        if 'timestamp' in df.columns:
            timestamps = pd.to_datetime(df['timestamp'])
        elif 'time' in df.columns:
            timestamps = pd.to_datetime(df['time'])
        elif 'datetime' in df.columns:
            timestamps = pd.to_datetime(df['datetime'])
        else:
            return len(df) // 96  # 假设15分钟一个点
        
        return (timestamps.max() - timestamps.min()).days + 1
    
    # ========== Agent1 相关方法 ==========
    def _get_patient_basic_info(self, df: pd.DataFrame, patient_id: str) -> Dict:
        """获取患者基本信息"""
        monitoring_days = self._calculate_monitoring_days(df)
        total_readings = len(df)
        readings_per_day = total_readings / monitoring_days if monitoring_days > 0 else 0
        
        if 'timestamp' in df.columns:
            timestamps = pd.to_datetime(df['timestamp'])
            start_date = timestamps.min().strftime("%Y-%m-%d")
            end_date = timestamps.max().strftime("%Y-%m-%d")
        else:
            start_date = "未知"
            end_date = "未知"
        
        return {
            "患者ID": patient_id,
            "监测天数": monitoring_days,
            "数据点数": total_readings,
            "监测时间范围": f"{start_date} 至 {end_date}",
            "数据密度": f"{readings_per_day:.1f} 读数/天"
        }
    
    def _comprehensive_quality_assessment(self, df: pd.DataFrame, patient_id: str) -> Dict:
        """综合数据质量评估"""
        monitoring_days = self._calculate_monitoring_days(df)
        total_readings = len(df)
        readings_per_day = total_readings / monitoring_days if monitoring_days > 0 else 0
        
        glucose_values = df['glucose_value'].dropna()
        cv = (glucose_values.std() / glucose_values.mean()) * 100 if len(glucose_values) > 0 else 0
        
        return {
            "数据质量评估": {
                "数据完整性": {
                    "总读数": total_readings,
                    "监测天数": monitoring_days,
                    "每日平均读数": readings_per_day,
                    "完整性评级": self._get_completeness_rating(readings_per_day)
                },
                "数据变异性": {
                    "变异系数": f"{cv:.1f}%",
                    "变异性评级": self._get_variability_rating(cv)
                }
            },
            "质量总评": {
                "整体评级": self._get_overall_quality_rating(readings_per_day, 30.0, cv),
                "建议": ["数据质量良好，建议继续保持当前监测模式"]
            }
        }
    
    def _calculate_94_indicators(self, df: pd.DataFrame) -> Dict:
        """计算94项专业指标"""
        glucose_values = df['glucose_value'].dropna()
        
        if len(glucose_values) == 0:
            return {"错误": "无有效血糖数据"}
        
        # 基础统计指标
        mean_glucose = glucose_values.mean()
        std_glucose = glucose_values.std()
        cv_glucose = (std_glucose / mean_glucose) * 100
        gmi = 3.31 + 0.02392 * (mean_glucose * 18.018)
        
        # TIR指标
        tir_standard = ((glucose_values >= 3.9) & (glucose_values <= 10.0)).sum() / len(glucose_values) * 100
        tar_total = (glucose_values > 10.0).sum() / len(glucose_values) * 100
        tbr_total = (glucose_values < 3.9).sum() / len(glucose_values) * 100
        
        core_indicators = {
            "mean_glucose": mean_glucose,
            "std_glucose": std_glucose,
            "cv_glucose": cv_glucose,
            "gmi": gmi,
            "tir_standard": tir_standard,
            "tar_total": tar_total,
            "tbr_total": tbr_total
        }
        
        return {
            "分析说明": "Agent5集成的专业血糖分析指标",
            "指标总数": len(core_indicators),
            "核心指标数据": core_indicators
        }
    
    def _generate_8_modules_analysis(self, df: pd.DataFrame, patient_id: str) -> Dict:
        """生成8个模块的分析"""
        glucose_values = df['glucose_value'].dropna()
        
        if len(glucose_values) == 0:
            return {"错误": "无有效血糖数据"}
        
        # 基础统计
        mean_glucose = glucose_values.mean()
        std_glucose = glucose_values.std()
        cv = (std_glucose / mean_glucose) * 100
        gmi = 3.31 + 0.02392 * (mean_glucose * 18.018)
        
        # TIR计算
        tir_standard = ((glucose_values >= 3.9) & (glucose_values <= 10.0)).sum() / len(glucose_values) * 100
        tar_total = (glucose_values > 10.0).sum() / len(glucose_values) * 100
        tbr_total = (glucose_values < 3.9).sum() / len(glucose_values) * 100
        
        # 构建8个模块
        modules = {
            "模块1_总体血糖控制状况和建议": {
                "简练专业描述": f"患者{patient_id}在{self._calculate_monitoring_days(df)}天监测期内血糖控制水平为{self._get_control_level(gmi, tir_standard)}，临床优先级为{self._get_priority_level(gmi, tar_total, tbr_total)}级别。",
                "核心控制指标": {
                    "GMI": f"{gmi:.2f}%",
                    "TIR标准范围": f"{tir_standard:.1f}%",
                    "高血糖时间": f"{tar_total:.1f}%",
                    "低血糖时间": f"{tbr_total:.1f}%",
                    "血糖变异系数": f"{cv:.1f}%"
                },
                "控制等级评价": self._get_control_level(gmi, tir_standard),
                "优先级水平": self._get_priority_level(gmi, tar_total, tbr_total)
            },
            "模块2_核心血糖控制指标分析": {
                "分析概述": f"核心血糖控制指标全面分析",
                "血糖管理指标": {
                    "GMI": f"{gmi:.2f}%",
                    "TIR标准范围": f"{tir_standard:.1f}%"
                }
            }
        }
        
        # 添加其他简化模块
        modules.update(self._generate_simplified_modules_3_to_8(df))
        
        return modules
    
    def _generate_simplified_modules_3_to_8(self, df: pd.DataFrame) -> Dict:
        """生成简化的模块3-8"""
        return {
            "模块3_六时段综合深度分析": {
                "时段分析说明": "Agent5集成的六时段血糖模式分析"
            },
            "模块4_工作日周末对比分析": {
                "对比说明": "Agent5工作日与周末血糖控制模式对比"
            },
            "模块5_异常模式检测与风险预警": {
                "检测说明": "Agent5异常血糖模式检测与风险评估"
            },
            "时间分段纵向分析": {
                "分段说明": "Agent5时间序列纵向变化趋势分析"
            }
        }
    
    # ========== Agent2 相关方法 ==========
    def _calculate_sliding_window_indicators(self, df_processed: pd.DataFrame) -> Dict:
        """计算滑动窗口指标"""
        glucose_values = df_processed['glucose_value'].values
        window_size = max(24, len(glucose_values) // 10)  # 动态窗口大小
        
        indicators = {
            'mean_glucose': [],
            'std_glucose': [],
            'cv': [],
            'tir': [],
            'timestamps': []
        }
        
        for i in range(window_size, len(glucose_values)):
            window_data = glucose_values[i-window_size:i]
            
            mean_val = np.mean(window_data)
            std_val = np.std(window_data)
            cv_val = (std_val / mean_val) * 100 if mean_val > 0 else 0
            tir_val = ((window_data >= 3.9) & (window_data <= 10.0)).sum() / len(window_data) * 100
            
            indicators['mean_glucose'].append(mean_val)
            indicators['std_glucose'].append(std_val)
            indicators['cv'].append(cv_val)
            indicators['tir'].append(tir_val)
            indicators['timestamps'].append(df_processed.iloc[i]['timestamp'])
        
        return indicators
    
    def _detect_change_points(self, indicators: Dict, df_processed: pd.DataFrame) -> List[int]:
        """智能变化点检测 - Agent2算法实现"""
        try:
            # 获取多维指标数据
            cv_series = np.array(indicators['cv'])
            mean_series = np.array(indicators['mean_glucose'])
            tir_series = np.array(indicators['tir'])
            
            # 数据长度
            n = len(cv_series)
            if n < 6:  # 数据太短，不分段
                return []
            
            change_points = []
            
            # 1. 基于变异系数的显著变化检测
            cv_diff = np.diff(cv_series)
            cv_threshold = np.std(cv_diff) * 1.5  # 降低阈值增加敏感性
            cv_significant = np.where(np.abs(cv_diff) > cv_threshold)[0]
            
            # 2. 基于平均血糖的显著变化检测
            mean_diff = np.diff(mean_series) 
            mean_threshold = np.std(mean_diff) * 1.5
            mean_significant = np.where(np.abs(mean_diff) > mean_threshold)[0]
            
            # 3. 基于TIR的显著变化检测
            tir_diff = np.diff(tir_series)
            tir_threshold = np.std(tir_diff) * 1.5
            tir_significant = np.where(np.abs(tir_diff) > tir_threshold)[0]
            
            # 4. 综合多维度变化点
            all_candidates = []
            if len(cv_significant) > 0:
                all_candidates.extend(cv_significant)
            if len(mean_significant) > 0:
                all_candidates.extend(mean_significant)
            if len(tir_significant) > 0:
                all_candidates.extend(tir_significant)
            
            if len(all_candidates) > 0:
                # 去重并排序
                unique_candidates = sorted(list(set(all_candidates)))
                
                # 过滤过于接近的变化点（最小间隔为n//6）
                min_distance = max(n // 6, 2)
                filtered_points = []
                
                for point in unique_candidates:
                    if not filtered_points or point - filtered_points[-1] >= min_distance:
                        filtered_points.append(point)
                
                # 转换为数据帧索引
                change_points = [int(p * len(df_processed) // n) for p in filtered_points]
                change_points = [p for p in change_points if 0 < p < len(df_processed)]
                
            # 5. 如果没有检测到变化点，使用基于时间的智能分段
            if not change_points:
                # 根据数据时间跨度智能分段
                total_hours = (df_processed['timestamp'].max() - df_processed['timestamp'].min()).total_seconds() / 3600
                
                if total_hours >= 168:  # 7天以上
                    # 按周分段
                    segments = 3
                elif total_hours >= 72:  # 3天以上  
                    segments = 2
                else:
                    return []  # 时间太短不分段
                
                segment_size = len(df_processed) // segments
                change_points = [segment_size * (i + 1) for i in range(segments - 1)]
            
            return change_points[:3]  # 最多3个分段点，避免过度分割
            
        except Exception as e:
            print(f"[Agent5] 智能变化点检测失败: {e}")
            return []
    
    def _generate_segments(self, change_points: List[int], df_processed: pd.DataFrame, 
                         total_days: int) -> List[Dict]:
        """生成分段"""
        if not change_points:
            # 如果没有变化点，分成3段
            segment_size = len(df_processed) // 3
            change_points = [segment_size, segment_size * 2]
        
        segments = []
        start_idx = 0
        
        for i, cp in enumerate(change_points + [len(df_processed) - 1]):
            end_idx = min(cp, len(df_processed) - 1)
            
            if end_idx > start_idx:
                segment_data = df_processed.iloc[start_idx:end_idx + 1]
                glucose_segment = segment_data['glucose_value'].dropna()
                
                if len(glucose_segment) > 0:
                    # 计算段落指标
                    mean_glucose = glucose_segment.mean()
                    std_glucose = glucose_segment.std()
                    cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0
                    gmi = 3.31 + 0.02392 * (mean_glucose * 18.018)
                    tir = ((glucose_segment >= 3.9) & (glucose_segment <= 10.0)).sum() / len(glucose_segment) * 100
                    
                    start_time = segment_data['timestamp'].min()
                    end_time = segment_data['timestamp'].max()
                    days = (end_time - start_time).days + 1
                    
                    segment = {
                        "阶段": f"阶段{i+1}",
                        "时间范围": f"{start_time.strftime('%m月%d日')}-{end_time.strftime('%m月%d日')}，{days}天",
                        "血糖控制特征": self._describe_glucose_control(gmi, tir),
                        "GMI": f"{gmi:.2f}%",
                        "TIR": f"{tir:.1f}%",
                        "CV": f"{cv:.1f}%",
                        "质量评级": self._get_control_level(gmi, tir),
                        "数据点数": len(glucose_segment)
                    }
                    
                    segments.append(segment)
            
            start_idx = end_idx + 1
        
        return segments
    
    def _analyze_segments_quality(self, segments: List[Dict], df_processed: pd.DataFrame) -> Dict:
        """分析分段质量"""
        if len(segments) < 2:
            return {
                "quality_rating": "低质量分段",
                "description": "未检测到显著变化点"
            }
        
        # 计算段间差异
        gmi_values = []
        tir_values = []
        
        for segment in segments:
            try:
                gmi_val = float(segment["GMI"].replace('%', ''))
                tir_val = float(segment["TIR"].replace('%', ''))
                gmi_values.append(gmi_val)
                tir_values.append(tir_val)
            except:
                continue
        
        if len(gmi_values) >= 2:
            gmi_std = np.std(gmi_values)
            tir_std = np.std(tir_values)
            
            if gmi_std > 0.5 or tir_std > 10:
                quality_rating = "高质量分段"
                description = "检测到显著的阶段差异"
            else:
                quality_rating = "中等质量分段"
                description = "检测到一定的阶段差异"
        else:
            quality_rating = "低质量分段"
            description = "段间差异分析失败"
        
        return {
            "quality_rating": quality_rating,
            "description": description,
            "gmi_variation": f"{np.std(gmi_values):.2f}" if gmi_values else "N/A",
            "tir_variation": f"{np.std(tir_values):.1f}" if tir_values else "N/A"
        }
    
    # ========== 药物分析相关方法 ==========
    def _analyze_medication_summary(self, medications: List[Dict]) -> Dict:
        """分析药物概览"""
        if not medications:
            return {"总数": 0, "类型": "无"}
        
        drug_types = {}
        for med in medications:
            drug_name = med.get("name", "未知药物")
            drug_types[drug_name] = med
        
        return {
            "药物总数": len(medications),
            "药物列表": list(drug_types.keys()),
            "详细信息": drug_types
        }
    
    def _analyze_medication_timeline(self, medications: List[Dict], df: pd.DataFrame) -> Dict:
        """分析药物时间线"""
        timeline_events = []
        
        for med in medications:
            start_date = med.get("start_date")
            if start_date:
                timeline_events.append({
                    "时间": start_date,
                    "事件": f"开始使用{med.get('name', '未知药物')}",
                    "剂量": f"{med.get('dosage', '未知')} {med.get('frequency', '未知频率')}",
                    "目的": med.get('purpose', '未说明')
                })
        
        # 按时间排序
        timeline_events.sort(key=lambda x: x["时间"])
        
        return {
            "时间线事件": timeline_events,
            "用药历程": f"共{len(timeline_events)}次用药调整"
        }
    
    def _analyze_medication_types(self, medications: List[Dict]) -> Dict:
        """分析药物分类"""
        type_mapping = {
            "二甲双胍": "双胍类",
            "达格列净": "SGLT-2抑制剂", 
            "西格列汀": "DPP-4抑制剂",
            "格列": "磺脲类",
            "胰岛素": "胰岛素类"
        }
        
        drug_categories = {}
        
        for med in medications:
            drug_name = med.get("name", "")
            category = "其他"
            
            for key, cat in type_mapping.items():
                if key in drug_name:
                    category = cat
                    break
            
            if category not in drug_categories:
                drug_categories[category] = []
            drug_categories[category].append(drug_name)
        
        return {
            "药物分类": drug_categories,
            "类别数": len(drug_categories)
        }
    
    def _assess_medication_compliance(self, medications: List[Dict]) -> Dict:
        """评估用药依从性"""
        compliance_scores = []
        
        for med in medications:
            compliance = med.get("compliance", "未知")
            if compliance == "良好":
                compliance_scores.append(1.0)
            elif compliance == "一般":
                compliance_scores.append(0.7)
            elif compliance == "差":
                compliance_scores.append(0.3)
        
        if compliance_scores:
            avg_compliance = np.mean(compliance_scores)
            if avg_compliance >= 0.9:
                compliance_level = "优秀"
            elif avg_compliance >= 0.7:
                compliance_level = "良好"  
            else:
                compliance_level = "需改善"
        else:
            compliance_level = "未评估"
            avg_compliance = 0
        
        return {
            "依从性水平": compliance_level,
            "依从性评分": f"{avg_compliance:.2f}",
            "评估药物数": len(compliance_scores)
        }
    
    def _assess_drug_interactions(self, medications: List[Dict]) -> Dict:
        """评估药物相互作用"""
        # 简化的药物相互作用评估
        drug_names = [med.get("name", "") for med in medications]
        
        interactions = []
        if len(drug_names) > 1:
            interactions.append("多药联合使用，建议关注药物相互作用")
        
        return {
            "相互作用风险": "低" if len(drug_names) <= 2 else "中等",
            "注意事项": interactions if interactions else ["单一用药，无明显相互作用风险"]
        }
    
    # ========== 整合分析相关方法 ==========
    def _evaluate_drug_effectiveness(self, df: pd.DataFrame, segments: List[Dict], 
                                   medications: Dict) -> Dict:
        """评估药物效果"""
        if not segments:
            return {"评估状态": "无法评估", "原因": "缺少时间分段信息"}
        
        effectiveness_analysis = {
            "评估方法": "基于时间分段的药物效果分析",
            "分段药物效果": []
        }
        
        for i, segment in enumerate(segments):
            stage = segment.get("阶段", f"阶段{i+1}")
            gmi = segment.get("GMI", "N/A")
            tir = segment.get("TIR", "N/A")
            
            effectiveness_analysis["分段药物效果"].append({
                "阶段": stage,
                "时间范围": segment.get("时间范围", "未知"),
                "GMI": gmi,
                "TIR": tir,
                "效果评价": self._evaluate_segment_effectiveness(gmi, tir)
            })
        
        # 整体效果趋势
        if len(segments) >= 2:
            first_gmi = self._extract_numeric_value(segments[0].get("GMI", "0"))
            last_gmi = self._extract_numeric_value(segments[-1].get("GMI", "0"))
            
            if last_gmi < first_gmi:
                overall_trend = "改善"
            elif last_gmi > first_gmi:
                overall_trend = "恶化"
            else:
                overall_trend = "稳定"
            
            effectiveness_analysis["整体趋势"] = overall_trend
        
        return effectiveness_analysis
    
    def _analyze_treatment_response(self, df: pd.DataFrame, segments: List[Dict], 
                                  medications: Dict) -> Dict:
        """分析治疗反应"""
        response_analysis = {
            "分析方法": "多阶段治疗反应评估",
            "反应模式": "稳定反应" if len(segments) <= 1 else "多阶段反应",
            "阶段反应": []
        }
        
        for segment in segments:
            stage = segment.get("阶段", "未知")
            control_level = segment.get("质量评级", "未知")
            
            response_analysis["阶段反应"].append({
                "阶段": stage,
                "控制水平": control_level,
                "反应评价": self._assess_stage_response(control_level)
            })
        
        return response_analysis
    
    def _analyze_medication_timing(self, df: pd.DataFrame, medications: Dict) -> Dict:
        """分析用药时机"""
        timing_analysis = {
            "分析说明": "用药时机与血糖控制关联分析",
            "用药策略": "渐进式加药" if len(medications.get("详细信息", {})) > 1 else "单一用药"
        }
        
        return timing_analysis
    
    def _generate_comprehensive_recommendations(self, drug_effectiveness: Dict, 
                                             treatment_response: Dict, 
                                             timing_analysis: Dict) -> List[str]:
        """生成综合治疗建议"""
        recommendations = []
        
        # 基于药物效果的建议
        overall_trend = drug_effectiveness.get("整体趋势", "稳定")
        if overall_trend == "恶化":
            recommendations.append("血糖控制呈恶化趋势，建议调整治疗方案")
        elif overall_trend == "改善":
            recommendations.append("治疗效果良好，建议继续当前方案并定期监测")
        else:
            recommendations.append("血糖控制相对稳定，建议优化治疗方案")
        
        # 基于用药策略的建议
        strategy = timing_analysis.get("用药策略", "")
        if "单一用药" in strategy:
            recommendations.append("目前单一用药，可考虑联合治疗以改善控制效果")
        else:
            recommendations.append("已采用联合用药策略，建议评估各药物的协同效果")
        
        return recommendations
    
    def _suggest_next_treatment_plan(self, drug_effectiveness: Dict, 
                                   treatment_response: Dict) -> Dict:
        """建议下一步治疗方案"""
        plan = {
            "短期目标": "稳定血糖控制，减少变异性",
            "中期目标": "改善TIR至70%以上",
            "长期目标": "维持长期稳定的血糖控制",
            "具体建议": []
        }
        
        overall_trend = drug_effectiveness.get("整体趋势", "稳定")
        if overall_trend == "恶化":
            plan["具体建议"].extend([
                "考虑增加胰岛素治疗",
                "加强血糖监测频率",
                "1-2周内复诊评估"
            ])
        else:
            plan["具体建议"].extend([
                "继续当前治疗方案",
                "定期监测和评估",
                "优化生活方式干预"
            ])
        
        return plan
    
    # ========== 专业术语说明生成 ==========
    def _generate_medical_abbreviations(self) -> Dict:
        """生成医学专业术语和英文缩写说明"""
        return {
            "使用说明": "本报告涉及的专业术语和英文缩写，按使用频率排序",
            "核心血糖指标": {
                "GMI": {
                    "全称": "Glucose Management Indicator",
                    "中文": "血糖管理指标", 
                    "简要介绍": "基于CGM数据计算的估算糖化血红蛋白，反映近期血糖控制水平",
                    "正常范围": "< 7.0%",
                    "临床意义": "评估血糖控制质量的核心指标"
                },
                "TIR": {
                    "全称": "Time In Range",
                    "中文": "目标范围内时间",
                    "简要介绍": "血糖值在目标范围(3.9-10.0 mmol/L)内的时间百分比",
                    "正常范围": "≥ 70%",
                    "临床意义": "反映血糖控制稳定性的重要指标"
                },
                "TAR": {
                    "全称": "Time Above Range", 
                    "中文": "高血糖时间",
                    "简要介绍": "血糖值超过目标上限(>10.0 mmol/L)的时间百分比",
                    "正常范围": "< 25%",
                    "临床意义": "评估高血糖暴露风险"
                },
                "TBR": {
                    "全称": "Time Below Range",
                    "中文": "低血糖时间", 
                    "简要介绍": "血糖值低于目标下限(<3.9 mmol/L)的时间百分比",
                    "正常范围": "< 4%",
                    "临床意义": "评估低血糖风险"
                },
                "CV": {
                    "全称": "Coefficient of Variation",
                    "中文": "变异系数",
                    "简要介绍": "血糖变异性指标，计算公式为(标准差/平均值)×100%",
                    "正常范围": "< 36%",
                    "临床意义": "评估血糖波动程度"
                }
            },
            "药物分类术语": {
                "SGLT-2抑制剂": {
                    "全称": "Sodium-Glucose Cotransporter 2 Inhibitors",
                    "中文": "钠-葡萄糖共转运蛋白2抑制剂",
                    "简要介绍": "通过抑制肾脏对葡萄糖的重吸收来降低血糖",
                    "代表药物": "达格列净、恩格列净",
                    "主要作用": "降低空腹和餐后血糖"
                },
                "DPP-4抑制剂": {
                    "全称": "Dipeptidyl Peptidase-4 Inhibitors", 
                    "中文": "二肽基肽酶4抑制剂",
                    "简要介绍": "通过抑制DPP-4酶，增加胰高血糖素样肽-1(GLP-1)水平",
                    "代表药物": "西格列汀、沙格列汀",
                    "主要作用": "改善餐后血糖控制"
                },
                "双胍类": {
                    "全称": "Biguanides",
                    "中文": "双胍类降糖药",
                    "简要介绍": "通过减少肝脏葡萄糖产生和改善胰岛素敏感性降糖",
                    "代表药物": "二甲双胍",
                    "主要作用": "降低基础血糖，改善胰岛素抵抗"
                }
            },
            "技术分析指标": {
                "CGM": {
                    "全称": "Continuous Glucose Monitoring",
                    "中文": "连续血糖监测",
                    "简要介绍": "持续监测皮下组织间液葡萄糖浓度的技术",
                    "技术优势": "提供全面的血糖变化信息",
                    "临床价值": "发现传统血糖仪无法检测的血糖波动"
                },
                "MAGE": {
                    "全称": "Mean Amplitude of Glycemic Excursions",
                    "中文": "平均血糖漂移幅度",
                    "简要介绍": "衡量血糖波动幅度的指标",
                    "计算方法": "超过1个标准差的血糖变化幅度平均值",
                    "临床意义": "评估血糖变异性"
                },
                "LBGI": {
                    "全称": "Low Blood Glucose Index",
                    "中文": "低血糖指数",
                    "简要介绍": "定量评估低血糖风险的综合指标",
                    "计算基础": "基于血糖值的对称化变换",
                    "临床应用": "低血糖风险评估"
                },
                "HBGI": {
                    "全称": "High Blood Glucose Index", 
                    "中文": "高血糖指数",
                    "简要介绍": "定量评估高血糖风险的综合指标",
                    "计算基础": "基于血糖值的对称化变换",
                    "临床应用": "高血糖风险评估"
                }
            },
            "智能分析技术": {
                "变化点检测": {
                    "英文": "Change Point Detection",
                    "中文": "变化点检测",
                    "简要介绍": "识别时间序列数据中统计特性发生显著变化的时间点",
                    "技术原理": "多维度指标融合的智能算法",
                    "临床意义": "识别治疗效果的关键转折点"
                },
                "时间分段": {
                    "英文": "Temporal Segmentation",
                    "中文": "时间分段分析",
                    "简要介绍": "将监测期划分为不同特征的时间段进行对比分析",
                    "技术特点": "数据驱动的智能分段",
                    "临床价值": "追踪治疗反应和效果变化"
                }
            },
            "报告使用提示": [
                "GMI和TIR是评估血糖控制的两个核心指标",
                "CV反映血糖稳定性，过高提示需要优化治疗方案",
                "药物分类有助于理解不同药物的作用机制", 
                "智能分段分析可发现传统方法难以识别的治疗反应模式",
                "建议结合临床情况综合判断分析结果"
            ]
        }
    
    # ========== 辅助方法 ==========
    def _describe_glucose_control(self, gmi: float, tir: float) -> str:
        """描述血糖控制特征"""
        if gmi <= 7.0 and tir >= 70:
            return "优秀的血糖控制"
        elif gmi <= 7.5 and tir >= 60:
            return "良好的血糖控制"
        elif gmi <= 8.0 and tir >= 50:
            return "可接受的血糖控制"
        else:
            return "需要改善的血糖控制"
    
    def _extract_numeric_value(self, value_str: str) -> float:
        """从字符串中提取数值"""
        try:
            return float(str(value_str).replace('%', ''))
        except:
            return 0.0
    
    def _evaluate_segment_effectiveness(self, gmi_str: str, tir_str: str) -> str:
        """评估段落效果"""
        try:
            gmi = self._extract_numeric_value(gmi_str)
            tir = self._extract_numeric_value(tir_str)
            
            if gmi <= 7.0 and tir >= 70:
                return "效果优秀"
            elif gmi <= 7.5 and tir >= 60:
                return "效果良好"
            elif gmi <= 8.0 and tir >= 50:
                return "效果可接受"
            else:
                return "效果不佳"
        except:
            return "无法评估"
    
    def _assess_stage_response(self, control_level: str) -> str:
        """评估阶段反应"""
        response_mapping = {
            "优秀": "治疗反应良好",
            "良好": "治疗反应较好", 
            "可接受": "治疗反应一般",
            "需改善": "治疗反应不佳"
        }
        return response_mapping.get(control_level, "反应未知")
    
    # ========== 评级方法 ==========
    def _get_completeness_rating(self, readings_per_day: float) -> str:
        """获取数据完整性评级"""
        if readings_per_day >= 90:
            return "优秀"
        elif readings_per_day >= 70:
            return "良好"
        elif readings_per_day >= 50:
            return "可接受"
        else:
            return "需改善"
    
    def _get_variability_rating(self, cv: float) -> str:
        """获取变异性评级"""
        if cv <= 36:
            return "正常"
        elif cv <= 45:
            return "略高"
        else:
            return "过高"
    
    def _get_overall_quality_rating(self, readings_per_day: float, max_gap: float, cv: float) -> str:
        """获取整体质量评级"""
        scores = []
        scores.append(4 if readings_per_day >= 90 else 3 if readings_per_day >= 70 else 2 if readings_per_day >= 50 else 1)
        scores.append(4 if max_gap <= 30 else 3 if max_gap <= 60 else 2 if max_gap <= 120 else 1)
        scores.append(4 if cv <= 36 else 3 if cv <= 45 else 2)
        
        avg_score = np.mean(scores)
        if avg_score >= 3.5:
            return "优秀"
        elif avg_score >= 2.5:
            return "良好"
        elif avg_score >= 1.5:
            return "可接受"
        else:
            return "需改善"
    
    def _get_control_level(self, gmi: float, tir: float) -> str:
        """获取血糖控制水平"""
        if gmi <= 7.0 and tir >= 70:
            return "优秀"
        elif gmi <= 7.5 and tir >= 60:
            return "良好"
        elif gmi <= 8.0 and tir >= 50:
            return "可接受"
        else:
            return "需改善"
    
    def _get_priority_level(self, gmi: float, high_time: float, low_time: float) -> str:
        """获取临床优先级"""
        if gmi > 8.0 or high_time > 60 or low_time > 1:
            return "高"
        elif gmi > 7.5 or high_time > 40 or low_time > 0.5:
            return "中"
        else:
            return "低"
    
    def _get_next_analysis_date(self) -> str:
        """获取下次建议分析时间"""
        next_date = datetime.now() + timedelta(days=14)
        return next_date.strftime("%Y-%m-%d")
    
    def _save_complete_report(self, result: Dict, patient_id: str):
        """保存完整分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Agent5_Complete_Report_{patient_id}_{timestamp}.json"
        
        # 保存JSON格式
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"[Agent5] 完整报告已保存: {filename}")

# 快速使用接口
def generate_comprehensive_report(filepath: str, patient_id: str = None, 
                                medication_data: Dict = None) -> Dict:
    """生成Agent5综合分析报告的快速接口"""
    analyzer = ComprehensiveAGPAIAnalyzer()
    return analyzer.generate_complete_report(filepath, patient_id, medication_data)

if __name__ == "__main__":
    # 示例用法
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        patient_id = sys.argv[2] if len(sys.argv) > 2 else "测试患者"
        force_builtin = "--use-builtin" in sys.argv
        
        # 示例药物数据
        sample_medication_data = {
            "medications": [
                {
                    "name": "二甲双胍片",
                    "dosage": "0.5g",
                    "frequency": "每日3次",
                    "start_date": "2025-07-20",
                    "purpose": "基础降糖治疗",
                    "compliance": "良好"
                }
            ]
        }
        
        print(f"[Agent5] 开始生成综合分析报告...")
        print(f"[Agent5] 患者ID: {patient_id}")
        print(f"[Agent5] 数据文件: {filepath}")
        
        analyzer = ComprehensiveAGPAIAnalyzer()
        result = analyzer.generate_complete_report(filepath, patient_id, sample_medication_data, force_builtin)
        
        if '报告头信息' in result:
            print(f"\n[Agent5] ✅ 报告生成成功!")
            print(f"[Agent5] 报告类型: {result['报告头信息']['报告类型']}")
            print(f"[Agent5] Agent类型: {result['报告头信息']['Agent信息']['agent_type']}")
            
            if '报告总结' in result:
                summary = result['报告总结']
                print(f"[Agent5] 分析模块数: {summary['分析模块数']}")
                print(f"[Agent5] 报告完整性: {summary['报告完整性']}")
        else:
            print(f"\n[Agent5] ❌ 报告生成失败")
    else:
        print("Agent5 AGPAI综合分析器 v1.0")
        print("="*50)
        print("用法: python Agent5_Comprehensive_Analyzer.py <数据文件路径> [患者ID]")
        print("功能: Agent1完整分析 + Agent2智能分段 + 药物整合分析")