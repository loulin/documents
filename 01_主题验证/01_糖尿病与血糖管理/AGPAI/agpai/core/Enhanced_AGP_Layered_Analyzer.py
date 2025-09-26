#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced AGP Layered Analyzer
Agent 1 的增强分层分析模块
提供多层次、多时间尺度的AGP模式分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class TimeLayer(Enum):
    """时间层次"""
    ULTRA_SHORT = "15分钟"    # 超短期 - 餐后反应
    SHORT = "1小时"          # 短期 - 小时级模式
    MEDIUM = "4小时"         # 中期 - 时段模式  
    LONG = "24小时"          # 长期 - 日模式
    EXTENDED = "7天"         # 扩展 - 周模式

class AGPPattern(Enum):
    """AGP模式类型"""
    STABLE_OPTIMAL = "稳定最优型"
    STABLE_SUBOPTIMAL = "稳定次优型"
    VARIABLE_CONTROLLED = "可控变异型"
    VARIABLE_UNCONTROLLED = "失控变异型"
    HYPOGLYCEMIC_PRONE = "低血糖倾向型"
    HYPERGLYCEMIC_DOMINANT = "高血糖主导型"
    MIXED_PATTERN = "混合模式型"
    DAWN_PHENOMENON = "黎明现象型"
    POSTPRANDIAL_SPIKE = "餐后峰值型"

@dataclass
class LayeredAnalysisResult:
    """分层分析结果"""
    time_layer: TimeLayer
    pattern_type: AGPPattern
    key_metrics: Dict[str, float]
    clinical_interpretation: str
    recommendations: List[str]

@dataclass
class ComprehensiveAGPProfile:
    """综合AGP档案"""
    overall_pattern: AGPPattern
    layered_results: List[LayeredAnalysisResult]
    pattern_consistency: float
    temporal_stability: Dict[str, float]
    clinical_summary: str

class EnhancedAGPLayeredAnalyzer:
    """
    增强的AGP分层分析器
    在Agent 1基础上增加多层次分析能力
    """
    
    def __init__(self):
        self.analyzer_name = "Enhanced AGP Layered Analyzer"
        self.version = "1.0.0"
        
        # 时间分层定义
        self.time_layers = {
            TimeLayer.ULTRA_SHORT: 15,    # 15分钟
            TimeLayer.SHORT: 60,          # 1小时
            TimeLayer.MEDIUM: 240,        # 4小时
            TimeLayer.LONG: 1440,         # 24小时
            TimeLayer.EXTENDED: 10080     # 7天
        }
        
        # AGP模式阈值
        self.pattern_thresholds = {
            'optimal_tir': 70,
            'optimal_cv': 25,
            'suboptimal_tir': 50,
            'suboptimal_cv': 36,
            'high_variability_cv': 50,
            'hypoglycemia_threshold': 4,
            'hyperglycemia_mean': 12,
            'dawn_magnitude': 2.0
        }
        
    def analyze_layered_agp_patterns(self, glucose_data: np.ndarray,
                                   timestamps: np.ndarray,
                                   patient_info: Dict = None) -> ComprehensiveAGPProfile:
        """
        执行分层AGP模式分析
        """
        print(f"🔍 {self.analyzer_name} 开始分层分析...")
        
        # 数据预处理
        df = self._prepare_dataframe(glucose_data, timestamps)
        
        # 执行各层次分析
        layered_results = []
        
        # 1. 超短期分析 (15分钟层次)
        ultra_short_result = self._analyze_ultra_short_patterns(df)
        layered_results.append(ultra_short_result)
        
        # 2. 短期分析 (1小时层次)
        short_result = self._analyze_short_term_patterns(df)
        layered_results.append(short_result)
        
        # 3. 中期分析 (4小时层次)
        medium_result = self._analyze_medium_term_patterns(df)
        layered_results.append(medium_result)
        
        # 4. 长期分析 (24小时层次)
        long_result = self._analyze_long_term_patterns(df)
        layered_results.append(long_result)
        
        # 5. 扩展分析 (7天层次)
        extended_result = self._analyze_extended_patterns(df)
        layered_results.append(extended_result)
        
        # 确定整体模式
        overall_pattern = self._determine_overall_pattern(layered_results, df)
        
        # 计算模式一致性
        pattern_consistency = self._calculate_pattern_consistency(layered_results)
        
        # 时间稳定性分析
        temporal_stability = self._analyze_temporal_stability(df)
        
        # 生成临床总结
        clinical_summary = self._generate_clinical_summary(overall_pattern, layered_results)
        
        profile = ComprehensiveAGPProfile(
            overall_pattern=overall_pattern,
            layered_results=layered_results,
            pattern_consistency=pattern_consistency,
            temporal_stability=temporal_stability,
            clinical_summary=clinical_summary
        )
        
        print(f"✅ 分层分析完成: {overall_pattern.value}")
        return profile
    
    def _prepare_dataframe(self, glucose_data: np.ndarray, timestamps: np.ndarray) -> pd.DataFrame:
        """数据预处理"""
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(timestamps),
            'glucose': glucose_data
        })
        
        # 时间特征提取
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day'] = df['timestamp'].dt.date
        
        return df.sort_values('timestamp').reset_index(drop=True)
    
    def _analyze_ultra_short_patterns(self, df: pd.DataFrame) -> LayeredAnalysisResult:
        """超短期模式分析 (15分钟层次) - 餐后反应"""
        
        # 计算15分钟变化率
        df['glucose_change_15min'] = df['glucose'].diff()
        df['rate_of_change'] = df['glucose_change_15min'] / 0.25  # per hour
        
        metrics = {
            'max_rate_increase': df['rate_of_change'].max(),
            'max_rate_decrease': df['rate_of_change'].min(),
            'rapid_changes_count': len(df[np.abs(df['rate_of_change']) > 4]),  # >4 mmol/L/h
            'glucose_excursions': len(df[df['glucose_change_15min'].abs() > 1.5])  # >1.5 mmol/L
        }
        
        # 模式判断
        if metrics['rapid_changes_count'] > len(df) * 0.1:  # >10%快速变化
            pattern_type = AGPPattern.VARIABLE_UNCONTROLLED
            interpretation = "超短期血糖变化剧烈，餐后反应过强"
            recommendations = ["优化餐时胰岛素时机", "考虑预混胰岛素", "餐后监测加强"]
        elif metrics['max_rate_increase'] > 6:  # 升糖速率>6 mmol/L/h
            pattern_type = AGPPattern.POSTPRANDIAL_SPIKE
            interpretation = "餐后血糖峰值明显，需要优化餐时管理"
            recommendations = ["调整胰岛素剂量", "优化碳水化合物摄入", "餐前提前注射"]
        else:
            pattern_type = AGPPattern.STABLE_OPTIMAL
            interpretation = "超短期血糖变化平稳，餐后反应良好"
            recommendations = ["维持现有方案", "定期监测评估"]
        
        return LayeredAnalysisResult(
            time_layer=TimeLayer.ULTRA_SHORT,
            pattern_type=pattern_type,
            key_metrics=metrics,
            clinical_interpretation=interpretation,
            recommendations=recommendations
        )
    
    def _analyze_short_term_patterns(self, df: pd.DataFrame) -> LayeredAnalysisResult:
        """短期模式分析 (1小时层次) - 小时级模式"""
        
        # 按小时聚合
        hourly = df.groupby('hour')['glucose'].agg(['mean', 'std', 'min', 'max']).reset_index()
        
        metrics = {
            'hour_mean_cv': hourly['mean'].std() / hourly['mean'].mean() * 100,
            'hour_variability_avg': hourly['std'].mean(),
            'dawn_effect': hourly[hourly['hour'].between(4, 8)]['mean'].mean() - 
                          hourly[hourly['hour'].between(2, 4)]['mean'].mean(),
            'nocturnal_stability': hourly[hourly['hour'].between(22, 23) | 
                                        hourly['hour'].between(0, 6)]['std'].mean()
        }
        
        # 模式判断
        if metrics['dawn_effect'] > self.pattern_thresholds['dawn_magnitude']:
            pattern_type = AGPPattern.DAWN_PHENOMENON
            interpretation = f"明显黎明现象，升高{metrics['dawn_effect']:.1f} mmol/L"
            recommendations = ["调整基础胰岛素", "考虑长效胰岛素", "监测夜间血糖"]
        elif metrics['hour_mean_cv'] > 30:
            pattern_type = AGPPattern.VARIABLE_UNCONTROLLED
            interpretation = "小时级血糖模式不稳定，昼夜节律紊乱"
            recommendations = ["规律作息", "定时用药", "建立生活节律"]
        else:
            pattern_type = AGPPattern.STABLE_OPTIMAL
            interpretation = "小时级血糖模式稳定，昼夜节律良好"
            recommendations = ["维持现有生活模式", "继续规律监测"]
        
        return LayeredAnalysisResult(
            time_layer=TimeLayer.SHORT,
            pattern_type=pattern_type,
            key_metrics=metrics,
            clinical_interpretation=interpretation,
            recommendations=recommendations
        )
    
    def _analyze_medium_term_patterns(self, df: pd.DataFrame) -> LayeredAnalysisResult:
        """中期模式分析 (4小时层次) - 时段模式"""
        
        # 定义时段
        df['time_period'] = df['hour'].apply(self._classify_time_period)
        period_stats = df.groupby('time_period')['glucose'].agg(['mean', 'std', 'min', 'max'])
        
        metrics = {
            'breakfast_period_mean': period_stats.loc['早餐时段', 'mean'] if '早餐时段' in period_stats.index else 0,
            'lunch_period_mean': period_stats.loc['午餐时段', 'mean'] if '午餐时段' in period_stats.index else 0,
            'dinner_period_mean': period_stats.loc['晚餐时段', 'mean'] if '晚餐时段' in period_stats.index else 0,
            'night_period_stability': period_stats.loc['夜间时段', 'std'] if '夜间时段' in period_stats.index else 0,
            'period_consistency': period_stats['mean'].std() / period_stats['mean'].mean() * 100
        }
        
        # 识别主导时段问题
        problematic_periods = []
        if metrics['breakfast_period_mean'] > 10:
            problematic_periods.append('早餐')
        if metrics['lunch_period_mean'] > 10:
            problematic_periods.append('午餐')
        if metrics['dinner_period_mean'] > 10:
            problematic_periods.append('晚餐')
        
        # 模式判断
        if len(problematic_periods) >= 2:
            pattern_type = AGPPattern.HYPERGLYCEMIC_DOMINANT
            interpretation = f"多个时段血糖偏高: {', '.join(problematic_periods)}"
            recommendations = ["全面调整治疗方案", "优化饮食结构", "增加胰岛素剂量"]
        elif metrics['period_consistency'] > 25:
            pattern_type = AGPPattern.MIXED_PATTERN
            interpretation = "不同时段血糖模式差异较大，需要分时段管理"
            recommendations = ["制定分时段治疗方案", "个性化饮食计划", "分段血糖监测"]
        else:
            pattern_type = AGPPattern.STABLE_OPTIMAL
            interpretation = "各时段血糖控制均衡，整体稳定"
            recommendations = ["保持现有管理模式", "定期评估调整"]
        
        return LayeredAnalysisResult(
            time_layer=TimeLayer.MEDIUM,
            pattern_type=pattern_type,
            key_metrics=metrics,
            clinical_interpretation=interpretation,
            recommendations=recommendations
        )
    
    def _analyze_long_term_patterns(self, df: pd.DataFrame) -> LayeredAnalysisResult:
        """长期模式分析 (24小时层次) - 日模式"""
        
        # 按日分析
        daily_stats = df.groupby('day')['glucose'].agg(['mean', 'std', 'min', 'max'])
        daily_stats['cv'] = daily_stats['std'] / daily_stats['mean'] * 100
        daily_stats['tir'] = df.groupby('day').apply(
            lambda x: np.sum((x['glucose'] >= 3.9) & (x['glucose'] <= 10.0)) / len(x) * 100
        )
        
        metrics = {
            'daily_mean_avg': daily_stats['mean'].mean(),
            'daily_cv_avg': daily_stats['cv'].mean(),
            'daily_tir_avg': daily_stats['tir'].mean(),
            'daily_consistency': daily_stats['mean'].std() / daily_stats['mean'].mean() * 100,
            'best_day_tir': daily_stats['tir'].max(),
            'worst_day_tir': daily_stats['tir'].min()
        }
        
        # 模式判断
        if (metrics['daily_tir_avg'] >= self.pattern_thresholds['optimal_tir'] and 
            metrics['daily_cv_avg'] <= self.pattern_thresholds['optimal_cv']):
            pattern_type = AGPPattern.STABLE_OPTIMAL
            interpretation = f"日模式稳定最优，TIR {metrics['daily_tir_avg']:.1f}%"
            recommendations = ["维持现有治疗方案", "继续良好的自我管理"]
        elif (metrics['daily_tir_avg'] >= self.pattern_thresholds['suboptimal_tir'] and 
              metrics['daily_cv_avg'] <= self.pattern_thresholds['suboptimal_cv']):
            pattern_type = AGPPattern.STABLE_SUBOPTIMAL
            interpretation = f"日模式基本稳定但有改善空间，TIR {metrics['daily_tir_avg']:.1f}%"
            recommendations = ["适度优化治疗方案", "加强生活方式干预", "提高监测频率"]
        elif metrics['daily_consistency'] > 20:
            pattern_type = AGPPattern.VARIABLE_UNCONTROLLED
            interpretation = f"日间血糖控制不一致，变异性{metrics['daily_consistency']:.1f}%"
            recommendations = ["识别不稳定因素", "建立规律化管理", "强化教育指导"]
        else:
            pattern_type = AGPPattern.MIXED_PATTERN
            interpretation = "日模式呈现混合特征，需要综合评估"
            recommendations = ["详细分析变异原因", "个性化调整方案", "多学科协作管理"]
        
        return LayeredAnalysisResult(
            time_layer=TimeLayer.LONG,
            pattern_type=pattern_type,
            key_metrics=metrics,
            clinical_interpretation=interpretation,
            recommendations=recommendations
        )
    
    def _analyze_extended_patterns(self, df: pd.DataFrame) -> LayeredAnalysisResult:
        """扩展模式分析 (7天层次) - 周模式"""
        
        # 周模式分析
        df['week_day'] = df['day_of_week']
        weekly_stats = df.groupby('week_day')['glucose'].agg(['mean', 'std'])
        
        # 工作日vs周末
        weekdays = df[df['week_day'] < 5]['glucose']  # 周一到周五
        weekends = df[df['week_day'] >= 5]['glucose']  # 周六周日
        
        metrics = {
            'weekday_mean': weekdays.mean() if len(weekdays) > 0 else 0,
            'weekend_mean': weekends.mean() if len(weekends) > 0 else 0,
            'weekday_cv': weekdays.std() / weekdays.mean() * 100 if len(weekdays) > 0 else 0,
            'weekend_cv': weekends.std() / weekends.mean() * 100 if len(weekends) > 0 else 0,
            'week_pattern_stability': weekly_stats['mean'].std() / weekly_stats['mean'].mean() * 100,
            'weekend_deviation': abs(weekends.mean() - weekdays.mean()) if len(weekdays) > 0 and len(weekends) > 0 else 0
        }
        
        # 模式判断
        if metrics['weekend_deviation'] > 1.5:
            pattern_type = AGPPattern.MIXED_PATTERN
            interpretation = f"工作日与周末血糖模式差异显著，差值{metrics['weekend_deviation']:.1f} mmol/L"
            recommendations = ["建立周末血糖管理规范", "保持生活规律一致性", "调整周末用药方案"]
        elif metrics['week_pattern_stability'] > 15:
            pattern_type = AGPPattern.VARIABLE_CONTROLLED
            interpretation = "周间血糖模式有一定变化，但整体可控"
            recommendations = ["识别周间变异因素", "优化不稳定日期的管理", "保持整体治疗连续性"]
        else:
            pattern_type = AGPPattern.STABLE_OPTIMAL
            interpretation = "周模式高度稳定，生活规律良好"
            recommendations = ["维持现有生活模式", "继续优秀的自我管理", "定期复查评估"]
        
        return LayeredAnalysisResult(
            time_layer=TimeLayer.EXTENDED,
            pattern_type=pattern_type,
            key_metrics=metrics,
            clinical_interpretation=interpretation,
            recommendations=recommendations
        )
    
    def _classify_time_period(self, hour: int) -> str:
        """时段分类"""
        if 6 <= hour <= 10:
            return '早餐时段'
        elif 11 <= hour <= 15:
            return '午餐时段'
        elif 17 <= hour <= 21:
            return '晚餐时段'
        elif 22 <= hour <= 23 or 0 <= hour <= 5:
            return '夜间时段'
        else:
            return '其他时段'
    
    def _determine_overall_pattern(self, layered_results: List[LayeredAnalysisResult], 
                                 df: pd.DataFrame) -> AGPPattern:
        """确定整体AGP模式"""
        
        # 统计各层次的模式类型
        pattern_counts = {}
        for result in layered_results:
            pattern = result.pattern_type
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # 整体统计指标
        overall_tir = np.sum((df['glucose'] >= 3.9) & (df['glucose'] <= 10.0)) / len(df) * 100
        overall_cv = df['glucose'].std() / df['glucose'].mean() * 100
        overall_mean = df['glucose'].mean()
        low_time = np.sum(df['glucose'] < 3.9) / len(df) * 100
        
        # 决策逻辑
        if overall_tir >= 70 and overall_cv <= 25:
            return AGPPattern.STABLE_OPTIMAL
        elif overall_tir >= 50 and overall_cv <= 36:
            return AGPPattern.STABLE_SUBOPTIMAL
        elif low_time > 4:
            return AGPPattern.HYPOGLYCEMIC_PRONE
        elif overall_mean > 12:
            return AGPPattern.HYPERGLYCEMIC_DOMINANT
        elif overall_cv > 50:
            return AGPPattern.VARIABLE_UNCONTROLLED
        elif AGPPattern.DAWN_PHENOMENON in pattern_counts and pattern_counts[AGPPattern.DAWN_PHENOMENON] >= 2:
            return AGPPattern.DAWN_PHENOMENON
        elif AGPPattern.POSTPRANDIAL_SPIKE in pattern_counts and pattern_counts[AGPPattern.POSTPRANDIAL_SPIKE] >= 2:
            return AGPPattern.POSTPRANDIAL_SPIKE
        else:
            return AGPPattern.MIXED_PATTERN
    
    def _calculate_pattern_consistency(self, layered_results: List[LayeredAnalysisResult]) -> float:
        """计算模式一致性"""
        optimal_count = sum(1 for r in layered_results if r.pattern_type == AGPPattern.STABLE_OPTIMAL)
        return optimal_count / len(layered_results)
    
    def _analyze_temporal_stability(self, df: pd.DataFrame) -> Dict[str, float]:
        """时间稳定性分析"""
        return {
            'hourly_stability': 1 - (df.groupby('hour')['glucose'].std().std() / 
                                   df.groupby('hour')['glucose'].std().mean()),
            'daily_stability': 1 - (df.groupby('day')['glucose'].mean().std() / 
                                  df.groupby('day')['glucose'].mean().mean()),
            'weekly_stability': 1 - (df.groupby('day_of_week')['glucose'].mean().std() / 
                                   df.groupby('day_of_week')['glucose'].mean().mean())
        }
    
    def _generate_clinical_summary(self, overall_pattern: AGPPattern, 
                                 layered_results: List[LayeredAnalysisResult]) -> str:
        """生成临床总结"""
        
        summary_parts = [f"整体AGP模式: {overall_pattern.value}"]
        
        # 收集各层次关键发现
        key_findings = []
        for result in layered_results:
            if result.pattern_type != AGPPattern.STABLE_OPTIMAL:
                key_findings.append(f"{result.time_layer.value}层次: {result.clinical_interpretation}")
        
        if key_findings:
            summary_parts.append("关键发现: " + "; ".join(key_findings))
        else:
            summary_parts.append("各时间层次血糖控制均表现良好")
        
        return " | ".join(summary_parts)

    def generate_layered_report(self, profile: ComprehensiveAGPProfile) -> Dict:
        """生成分层分析报告"""
        
        report = {
            'analyzer_info': {
                'name': self.analyzer_name,
                'version': self.version,
                'analysis_time': datetime.now().isoformat()
            },
            'overall_assessment': {
                'pattern_type': profile.overall_pattern.value,
                'pattern_consistency': profile.pattern_consistency,
                'clinical_summary': profile.clinical_summary
            },
            'layered_analysis': [],
            'temporal_stability': profile.temporal_stability,
            'integrated_recommendations': []
        }
        
        # 各层次分析结果
        for result in profile.layered_results:
            layer_report = {
                'time_layer': result.time_layer.value,
                'pattern_type': result.pattern_type.value,
                'key_metrics': result.key_metrics,
                'clinical_interpretation': result.clinical_interpretation,
                'recommendations': result.recommendations
            }
            report['layered_analysis'].append(layer_report)
        
        # 综合建议
        all_recommendations = []
        for result in profile.layered_results:
            all_recommendations.extend(result.recommendations)
        
        # 去重并按优先级排序
        unique_recommendations = list(set(all_recommendations))
        report['integrated_recommendations'] = unique_recommendations[:5]  # 前5条
        
        return report

# 使用示例
if __name__ == "__main__":
    # 初始化增强分析器
    enhanced_analyzer = EnhancedAGPLayeredAnalyzer()
    print(f"✅ {enhanced_analyzer.analyzer_name} v{enhanced_analyzer.version} 初始化完成")
    print("🔍 支持5层时间尺度分析:")
    for layer in TimeLayer:
        print(f"   - {layer.value}")
    print("🎯 支持9种AGP模式识别:")
    for pattern in AGPPattern:
        print(f"   - {pattern.value}")