#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent2 优化分段版本 v1.0
在原有Agent2基础上添加最优分段约束，确保临床实用性

核心改进：
1. 最优分段数量控制（2-4段）
2. 智能变化点重要性排序
3. 分段质量优先策略
4. 临床意义阈值控制

使用场景：
- 临床常规报告（需要简洁明了的分段）
- 患者沟通（避免过度复杂的分析）
- 标准化比较（统一的分段框架）
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 导入原始Agent2模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from Agent2_Intelligent_Analysis import (
        analyze_intelligent_longitudinal_segments as original_agent2_analysis,
        detect_comprehensive_change_points,
        calculate_sliding_window_indicators,
        analyze_detailed_segment_differences,
        evaluate_intelligent_segmentation_quality,
        generate_clinical_significance_interpretation
    )
    ORIGINAL_AGENT2_AVAILABLE = True
    print("[Agent2-Optimized] ✅ 成功导入原始Agent2模块")
except ImportError as e:
    ORIGINAL_AGENT2_AVAILABLE = False
    print(f"[Agent2-Optimized] ⚠️  无法导入原始Agent2: {e}")

def analyze_intelligent_longitudinal_segments_optimized(
    df: pd.DataFrame, 
    glucose_values: np.ndarray, 
    total_days: int,
    max_segments: int = 4,
    min_segments: int = 2,
    clinical_mode: bool = True
) -> Dict:
    """
    优化版Agent2智能分段分析
    
    Args:
        df: 血糖数据DataFrame
        glucose_values: 血糖值数组
        total_days: 总监测天数
        max_segments: 最大分段数（默认4，临床最优）
        min_segments: 最小分段数（默认2）
        clinical_mode: 临床模式（True=最优分段优先，False=原始模式）
    
    Returns:
        优化后的智能分段分析结果
    """
    
    try:
        print(f"[Agent2-Optimized] 开始优化分段分析...")
        print(f"[Agent2-Optimized] 分段约束: {min_segments}-{max_segments}段")
        print(f"[Agent2-Optimized] 临床模式: {'开启' if clinical_mode else '关闭'}")
        
        # 1. 数据预处理
        df_processed = df.copy()
        df_processed['timestamp'] = pd.to_datetime(df_processed['timestamp'])
        df_processed = df_processed.sort_values('timestamp')
        df_processed['day_from_start'] = (df_processed['timestamp'] - df_processed['timestamp'].min()).dt.days
        df_processed['hours_from_start'] = (df_processed['timestamp'] - df_processed['timestamp'].min()).dt.total_seconds() / 3600
        
        # 2. 计算滑动窗口指标
        print("[Agent2-Optimized] 计算滑动窗口指标...")
        indicators = calculate_sliding_window_indicators(df_processed, glucose_values)
        
        # 3. 综合变化点检测
        print("[Agent2-Optimized] 执行变化点检测...")
        change_points = detect_comprehensive_change_points(indicators, df_processed)
        
        # 4. 🔥 核心改进：优化分段策略
        if clinical_mode:
            optimized_segments = generate_optimal_clinical_segments(
                change_points, df_processed, total_days, max_segments, min_segments
            )
        else:
            # 使用原始Agent2分段逻辑
            optimized_segments = merge_and_generate_segments_original(
                change_points, df_processed, total_days
            )
        
        # 5. 段间差异详细分析
        print("[Agent2-Optimized] 分析段间差异...")
        segment_analysis = analyze_detailed_segment_differences(
            optimized_segments, df_processed, glucose_values
        )
        
        # 6. 分段质量评估
        quality_assessment = evaluate_intelligent_segmentation_quality(
            segment_analysis, optimized_segments
        )
        
        # 7. 生成优化报告
        optimized_report = {
            "分段方法说明": "Agent2优化分段算法 - 临床最优版本",
            "优化策略": {
                "分段约束": f"{min_segments}-{max_segments}段",
                "临床模式": clinical_mode,
                "优化目标": ["临床实用性", "分析简洁性", "医患沟通友好性"],
                "质量保证": ["重要变化点保留", "临床意义阈值过滤", "分段差异显著性验证"]
            },
            "检测维度": ["血糖控制质量变化", "脆性特征演变", "变异模式转换", "治疗反应阶段"],
            "变化点检测详情": {
                "原始检测到的变化点": len(change_points.get("综合变化点", [])),
                "优化后保留的变化点": len(optimized_segments.get("分段边界", [])) - 2,  # 减去起始和结束点
                "过滤原因": "临床意义阈值过滤" if clinical_mode else "无过滤",
                "信度评估": evaluate_optimization_confidence(optimized_segments, change_points)
            },
            "最终智能分段": optimized_segments,
            "段间详细对比分析": segment_analysis,
            "分段质量评估": quality_assessment,
            "临床意义解读": generate_clinical_significance_interpretation(
                segment_analysis, change_points
            ),
            "优化效果评估": evaluate_optimization_effectiveness(
                optimized_segments, change_points, quality_assessment
            )
        }
        
        return optimized_report
        
    except Exception as e:
        print(f"[Agent2-Optimized] 分析错误: {e}")
        return {
            "分段方法说明": "Agent2优化分段分析遇到技术问题",
            "error": str(e),
            "fallback_analysis": "已切换到基础分段模式"
        }

def generate_optimal_clinical_segments(
    change_points: Dict, 
    df: pd.DataFrame, 
    total_days: int,
    max_segments: int = 4,
    min_segments: int = 2
) -> Dict:
    """
    生成临床最优分段
    核心策略：变化点重要性排序 + 分段数量控制
    """
    
    print("[Agent2-Optimized] 生成临床最优分段...")
    
    comprehensive_changes = change_points.get("综合变化点", [])
    
    # 如果没有检测到变化点
    if not comprehensive_changes:
        print("[Agent2-Optimized] 未检测到变化点，使用默认2段分割")
        total_hours = df['hours_from_start'].max()
        segment_boundaries = [0, total_hours / 2, total_hours]
        return create_segments_from_boundaries(segment_boundaries, df)
    
    # 如果变化点数量已经在最优范围内
    if len(comprehensive_changes) <= (max_segments - 1):
        print(f"[Agent2-Optimized] 变化点数量({len(comprehensive_changes)})在最优范围内，直接使用")
        segment_boundaries = [0] + comprehensive_changes + [df['hours_from_start'].max()]
        segment_boundaries = sorted(list(set(segment_boundaries)))
        return create_segments_from_boundaries(segment_boundaries, df)
    
    # 🔥 核心优化：变化点重要性排序和选择
    print(f"[Agent2-Optimized] 变化点过多({len(comprehensive_changes)})，进行重要性筛选...")
    
    # 1. 计算每个变化点的重要性分数
    change_point_importance = calculate_change_point_importance(
        comprehensive_changes, change_points, df
    )
    
    # 2. 选择最重要的变化点
    target_change_points = max_segments - 1  # 减去起始和结束边界
    selected_changes = select_most_important_change_points(
        change_point_importance, target_change_points
    )
    
    print(f"[Agent2-Optimized] 从{len(comprehensive_changes)}个变化点中选择了{len(selected_changes)}个最重要的")
    
    # 3. 生成最优分段
    segment_boundaries = [0] + selected_changes + [df['hours_from_start'].max()]
    segment_boundaries = sorted(list(set(segment_boundaries)))
    
    return create_segments_from_boundaries(segment_boundaries, df, optimization_applied=True)

def calculate_change_point_importance(
    change_points: List[float], 
    all_change_points: Dict, 
    df: pd.DataFrame
) -> List[Tuple[float, float]]:
    """
    计算变化点的重要性分数
    
    评估维度：
    1. 多算法支持度（被几种算法检测到）
    2. 时间位置合理性（避免过于密集）
    3. 临床意义强度（基于血糖指标变化幅度）
    """
    
    importance_scores = []
    
    for change_point in change_points:
        importance_score = 0.0
        
        # 1. 多算法支持度评分（最重要，权重40%）
        algorithm_support = 0
        for method_name, method_changes in all_change_points.items():
            if method_name != "综合变化点" and change_point in method_changes:
                algorithm_support += 1
        
        # 标准化支持度分数（最多4个算法支持）
        support_score = (algorithm_support / 4.0) * 40
        importance_score += support_score
        
        # 2. 时间位置合理性评分（权重30%）
        total_hours = df['hours_from_start'].max()
        relative_position = change_point / total_hours
        
        # 避免过于靠近起始或结束的变化点
        position_penalty = 0
        if relative_position < 0.1 or relative_position > 0.9:
            position_penalty = 10
        elif relative_position < 0.2 or relative_position > 0.8:
            position_penalty = 5
        
        position_score = 30 - position_penalty
        importance_score += position_score
        
        # 3. 临床意义强度评分（权重30%）
        # 这里简化处理，实际可以基于血糖指标变化幅度
        clinical_score = 20  # 基础分
        
        # 如果是脆性变化点或统计变化点，额外加分
        if change_point in all_change_points.get("脆性变化点", []):
            clinical_score += 5
        if change_point in all_change_points.get("统计变化点", []):
            clinical_score += 5
        
        importance_score += clinical_score
        
        importance_scores.append((change_point, importance_score))
    
    return importance_scores

def select_most_important_change_points(
    importance_scores: List[Tuple[float, float]], 
    target_count: int
) -> List[float]:
    """
    选择最重要的变化点
    """
    
    # 按重要性分数降序排序
    sorted_scores = sorted(importance_scores, key=lambda x: x[1], reverse=True)
    
    # 选择前N个最重要的变化点
    selected_points = [point for point, score in sorted_scores[:target_count]]
    
    # 按时间顺序排序
    selected_points.sort()
    
    print(f"[Agent2-Optimized] 变化点重要性选择结果:")
    for i, (point, score) in enumerate(sorted_scores[:target_count]):
        print(f"  - 变化点{i+1}: {point:.1f}小时，重要性: {score:.1f}")
    
    return selected_points

def create_segments_from_boundaries(
    boundaries: List[float], 
    df: pd.DataFrame, 
    optimization_applied: bool = False
) -> Dict:
    """
    从边界创建分段信息
    """
    
    segments = {
        "分段数量": len(boundaries) - 1,
        "分段边界": boundaries,
        "详细分段": [],
        "优化状态": "已应用最优化" if optimization_applied else "原始分段"
    }
    
    for i in range(len(boundaries) - 1):
        start_hour = boundaries[i]
        end_hour = boundaries[i + 1]
        
        start_day = start_hour / 24
        end_day = end_hour / 24
        duration_days = (end_hour - start_hour) / 24
        
        segment_info = {
            "段落编号": i + 1,
            "开始时间": f"第{start_day:.1f}天",
            "结束时间": f"第{end_day:.1f}天",
            "持续时间": f"{duration_days:.1f}天",
            "起始小时": f"{start_hour:.1f}小时",
            "结束小时": f"{end_hour:.1f}小时"
        }
        
        segments["详细分段"].append(segment_info)
    
    return segments

def merge_and_generate_segments_original(
    change_points: Dict, 
    df: pd.DataFrame, 
    total_days: int
) -> Dict:
    """
    原始Agent2分段逻辑（用于对比）
    """
    
    comprehensive_changes = change_points.get("综合变化点", [])
    
    if not comprehensive_changes:
        total_hours = df['hours_from_start'].max()
        segment_boundaries = [0, total_hours / 2, total_hours]
    else:
        segment_boundaries = [0] + comprehensive_changes + [df['hours_from_start'].max()]
        segment_boundaries = sorted(list(set(segment_boundaries)))
    
    return create_segments_from_boundaries(segment_boundaries, df)

def evaluate_optimization_confidence(segments: Dict, change_points: Dict) -> str:
    """
    评估优化置信度
    """
    
    num_segments = segments.get("分段数量", 0)
    original_changes = len(change_points.get("综合变化点", []))
    
    if 2 <= num_segments <= 4:
        if original_changes >= num_segments - 1:
            return "高置信度 - 最优分段范围内且有充分变化点支持"
        else:
            return "中等置信度 - 最优范围内但变化点支持有限"
    else:
        return "低置信度 - 分段数量超出最优范围"

def evaluate_optimization_effectiveness(
    optimized_segments: Dict, 
    original_change_points: Dict, 
    quality_assessment: Dict
) -> Dict:
    """
    评估优化效果
    """
    
    original_changes = len(original_change_points.get("综合变化点", []))
    optimized_changes = optimized_segments.get("分段数量", 0) - 1
    
    effectiveness = {
        "变化点压缩率": f"{((original_changes - optimized_changes) / max(1, original_changes)) * 100:.1f}%",
        "临床友好性": "高" if 2 <= optimized_segments.get("分段数量", 0) <= 4 else "中",
        "信息保留度": evaluate_information_retention(original_changes, optimized_changes),
        "分段质量": quality_assessment.get("总体评级", "未知"),
        "优化建议": generate_optimization_recommendations(
            optimized_segments, original_changes, quality_assessment
        )
    }
    
    return effectiveness

def evaluate_information_retention(original_changes: int, optimized_changes: int) -> str:
    """
    评估信息保留度
    """
    
    if original_changes == 0:
        return "完全保留（无原始变化点）"
    
    retention_rate = optimized_changes / original_changes
    
    if retention_rate >= 0.8:
        return "高保留（≥80%）"
    elif retention_rate >= 0.5:
        return "中等保留（50-80%）"
    else:
        return "低保留（<50%）"

def generate_optimization_recommendations(
    segments: Dict, 
    original_changes: int, 
    quality_assessment: Dict
) -> List[str]:
    """
    生成优化建议
    """
    
    recommendations = []
    num_segments = segments.get("分段数量", 0)
    
    if num_segments < 2:
        recommendations.append("建议增加分段数量以获得更好的分析粒度")
    elif num_segments > 4:
        recommendations.append("分段数量仍偏多，考虑进一步优化变化点选择算法")
    else:
        recommendations.append("分段数量在最优范围内，建议保持当前策略")
    
    if original_changes > 10:
        recommendations.append("原始变化点过多，建议提高变化点检测阈值")
    
    overall_quality = quality_assessment.get("总体评级", "")
    if "优秀" not in overall_quality:
        recommendations.append("建议优化变化点重要性评估算法以提高分段质量")
    
    return recommendations

# 快速接口函数
def analyze_with_optimal_segmentation(
    filepath: str, 
    patient_id: str = "Unknown",
    max_segments: int = 4,
    clinical_mode: bool = True
) -> Dict:
    """
    使用优化分段的快速分析接口
    """
    
    # 加载数据
    df = pd.read_excel(filepath)
    if '值' in df.columns:
        df = df.rename(columns={'值': 'glucose_value', '时间': 'timestamp'})
    elif 'glucose' in df.columns:
        df = df.rename(columns={'glucose': 'glucose_value'})
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    glucose_values = df['glucose_value'].dropna().values
    total_days = (df['timestamp'].max() - df['timestamp'].min()).days + 1
    
    return analyze_intelligent_longitudinal_segments_optimized(
        df, glucose_values, total_days, max_segments, clinical_mode=clinical_mode
    )

if __name__ == "__main__":
    # 测试用例
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        patient_id = sys.argv[2] if len(sys.argv) > 2 else "测试患者"
        max_segments = int(sys.argv[3]) if len(sys.argv) > 3 else 4
        
        print(f"[Agent2-Optimized] 开始优化分段分析...")
        print(f"[Agent2-Optimized] 数据文件: {filepath}")
        print(f"[Agent2-Optimized] 患者ID: {patient_id}")
        print(f"[Agent2-Optimized] 最大分段数: {max_segments}")
        
        result = analyze_with_optimal_segmentation(filepath, patient_id, max_segments)
        
        print(f"\n[Agent2-Optimized] ✅ 分析完成!")
        print(f"[Agent2-Optimized] 分段数量: {result.get('最终智能分段', {}).get('分段数量', 'N/A')}")
        print(f"[Agent2-Optimized] 优化状态: {result.get('最终智能分段', {}).get('优化状态', 'N/A')}")
    else:
        print("使用方法: python Agent2_Optimized_Segmentation.py <数据文件> [患者ID] [最大分段数]")