#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Temporal Pattern Analyzer
动态时间段模式分析器
考虑患者血糖模式在不同时间段的变化和演进
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.signal import savgol_filter
import warnings
warnings.filterwarnings('ignore')

class TemporalWindow(Enum):
    """时间窗口类型"""
    SLIDING_3DAY = "3天滑动窗口"
    SLIDING_7DAY = "7天滑动窗口"
    FIXED_WEEKLY = "固定周窗口"
    ADAPTIVE = "自适应窗口"
    TREATMENT_PHASE = "治疗阶段窗口"

class PatternEvolution(Enum):
    """模式演进类型"""
    STABLE = "稳定型"               # 模式保持稳定
    IMPROVING = "改善型"            # 模式逐渐改善
    DETERIORATING = "恶化型"        # 模式逐渐恶化
    FLUCTUATING = "波动型"          # 模式反复波动
    PHASE_TRANSITION = "阶段转换型"  # 明显的阶段性转换
    CYCLICAL = "周期性"             # 周期性变化模式

class TreatmentPhase(Enum):
    """治疗阶段"""
    BASELINE = "基线期"
    ADJUSTMENT = "调整期"
    STABILIZATION = "稳定期"
    OPTIMIZATION = "优化期"
    MAINTENANCE = "维持期"

@dataclass
class TemporalPatternSegment:
    """时间段模式片段"""
    start_date: datetime
    end_date: datetime
    duration_days: int
    pattern_type: str
    key_metrics: Dict[str, float]
    stability_score: float
    clinical_phase: Optional[TreatmentPhase] = None
    change_points: List[datetime] = field(default_factory=list)

@dataclass
class PatternTransition:
    """模式转换"""
    from_pattern: str
    to_pattern: str
    transition_date: datetime
    transition_strength: float  # 转换强度 0-1
    likely_cause: str
    clinical_significance: str

@dataclass
class DynamicTemporalProfile:
    """动态时间模式档案"""
    analysis_period: Tuple[datetime, datetime]
    pattern_segments: List[TemporalPatternSegment]
    pattern_transitions: List[PatternTransition]
    overall_evolution: PatternEvolution
    dominant_pattern: str
    pattern_stability: float
    trend_analysis: Dict[str, float]
    clinical_insights: List[str]

class DynamicTemporalPatternAnalyzer:
    """
    动态时间段模式分析器
    分析血糖模式在时间段内的变化和演进
    """
    
    def __init__(self, min_segment_days: int = 3, change_sensitivity: float = 0.15):
        self.analyzer_name = "Dynamic Temporal Pattern Analyzer"
        self.version = "1.0.0"
        self.min_segment_days = min_segment_days
        self.change_sensitivity = change_sensitivity
        
        # 模式识别阈值
        self.pattern_thresholds = {
            'excellent_tir': 85,
            'good_tir': 70,
            'acceptable_tir': 50,
            'poor_tir': 30,
            'excellent_cv': 25,
            'good_cv': 36,
            'acceptable_cv': 50,
            'poor_cv': 70
        }
        
        # 变化检测阈值
        self.change_thresholds = {
            'significant_tir_change': 10,    # TIR变化>10%为显著
            'significant_cv_change': 5,      # CV变化>5%为显著  
            'significant_mean_change': 1.0,  # 平均血糖变化>1.0 mmol/L为显著
            'trend_significance': 0.05       # p<0.05为显著趋势
        }
    
    def analyze_dynamic_patterns(self, glucose_data: np.ndarray,
                                timestamps: np.ndarray,
                                treatment_events: List[Dict] = None,
                                patient_info: Dict = None) -> DynamicTemporalProfile:
        """
        分析动态时间模式
        
        Args:
            glucose_data: 血糖数据
            timestamps: 时间戳
            treatment_events: 治疗事件列表 [{'date': datetime, 'event': str, 'description': str}]
            patient_info: 患者信息
        """
        print(f"🔄 {self.analyzer_name} 开始动态模式分析...")
        
        # 数据预处理
        df = self._prepare_temporal_dataframe(glucose_data, timestamps)
        
        # 1. 检测变化点
        change_points = self._detect_change_points(df)
        print(f"   🔍 检测到 {len(change_points)} 个显著变化点")
        
        # 2. 分割时间段
        segments = self._segment_temporal_periods(df, change_points, treatment_events)
        print(f"   📊 识别出 {len(segments)} 个模式段")
        
        # 3. 分析每个时间段的模式
        pattern_segments = []
        for i, (start_idx, end_idx) in enumerate(segments):
            segment_data = df.iloc[start_idx:end_idx]
            if len(segment_data) >= self.min_segment_days * 24:  # 至少3天数据
                pattern_segment = self._analyze_segment_pattern(segment_data, i+1)
                pattern_segments.append(pattern_segment)
        
        # 4. 识别模式转换
        pattern_transitions = self._identify_pattern_transitions(pattern_segments)
        
        # 5. 分析整体演进趋势
        overall_evolution = self._analyze_overall_evolution(pattern_segments, df)
        
        # 6. 计算趋势分析
        trend_analysis = self._calculate_trend_analysis(df)
        
        # 7. 生成临床洞察
        clinical_insights = self._generate_clinical_insights(
            pattern_segments, pattern_transitions, overall_evolution, treatment_events
        )
        
        # 确定主导模式
        dominant_pattern = self._determine_dominant_pattern(pattern_segments)
        
        # 计算整体稳定性
        pattern_stability = self._calculate_pattern_stability(pattern_segments)
        
        profile = DynamicTemporalProfile(
            analysis_period=(df['timestamp'].min(), df['timestamp'].max()),
            pattern_segments=pattern_segments,
            pattern_transitions=pattern_transitions,
            overall_evolution=overall_evolution,
            dominant_pattern=dominant_pattern,
            pattern_stability=pattern_stability,
            trend_analysis=trend_analysis,
            clinical_insights=clinical_insights
        )
        
        print(f"✅ 动态模式分析完成: {overall_evolution.value}")
        return profile
    
    def _prepare_temporal_dataframe(self, glucose_data: np.ndarray, 
                                  timestamps: np.ndarray) -> pd.DataFrame:
        """准备时间序列数据"""
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(timestamps),
            'glucose': glucose_data
        })
        
        df = df.sort_values('timestamp').reset_index(drop=True)
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        
        # 计算滑动统计指标
        window_size = min(288, len(df) // 10)  # 24小时窗口或1/10数据量
        if window_size >= 24:
            df['glucose_ma'] = df['glucose'].rolling(window=window_size, center=True).mean()
            df['glucose_std_ma'] = df['glucose'].rolling(window=window_size, center=True).std()
            df['cv_ma'] = df['glucose_std_ma'] / df['glucose_ma'] * 100
        
        return df
    
    def _detect_change_points(self, df: pd.DataFrame) -> List[int]:
        """检测显著变化点"""
        change_points = []
        
        if 'glucose_ma' not in df.columns:
            return change_points
        
        # 1. 基于移动平均的变化检测
        ma_values = df['glucose_ma'].dropna().values
        if len(ma_values) < 48:  # 少于2天数据
            return change_points
        
        # 计算一阶差分
        ma_diff = np.diff(ma_values)
        
        # 使用Savitzky-Golay滤波平滑差分
        if len(ma_diff) >= 5:
            smooth_diff = savgol_filter(ma_diff, min(21, len(ma_diff)//2*2-1), 2)
            
            # 检测显著变化点
            threshold = np.std(smooth_diff) * 2.0
            significant_changes = np.where(np.abs(smooth_diff) > threshold)[0]
            
            # 过滤太接近的变化点（至少间隔1天）
            filtered_changes = []
            for change_idx in significant_changes:
                if not filtered_changes or change_idx - filtered_changes[-1] > 24:
                    filtered_changes.append(change_idx)
            
            change_points.extend(filtered_changes)
        
        # 2. 基于日统计的变化检测
        daily_stats = df.groupby('date').agg({
            'glucose': ['mean', 'std', lambda x: np.sum((x >= 3.9) & (x <= 10.0)) / len(x) * 100]
        }).reset_index()
        daily_stats.columns = ['date', 'mean_glucose', 'std_glucose', 'tir']
        daily_stats['cv'] = daily_stats['std_glucose'] / daily_stats['mean_glucose'] * 100
        
        if len(daily_stats) >= 5:
            # TIR变化检测
            tir_changes = np.abs(np.diff(daily_stats['tir']))
            tir_change_points = np.where(tir_changes > self.change_thresholds['significant_tir_change'])[0]
            
            # 转换为原始数据索引
            for cp in tir_change_points:
                if cp < len(daily_stats) - 1:
                    date = daily_stats.iloc[cp+1]['date']
                    date_indices = df[df['date'] == date].index
                    if len(date_indices) > 0:
                        change_points.append(date_indices[0])
        
        # 排序并去重
        change_points = sorted(list(set(change_points)))
        
        return change_points
    
    def _segment_temporal_periods(self, df: pd.DataFrame, change_points: List[int],
                                treatment_events: List[Dict] = None) -> List[Tuple[int, int]]:
        """分割时间段"""
        segments = []
        
        # 添加治疗事件作为分割点
        if treatment_events:
            for event in treatment_events:
                event_date = pd.to_datetime(event['date']).date()
                event_indices = df[df['date'] == event_date].index
                if len(event_indices) > 0:
                    change_points.append(event_indices[0])
        
        # 排序分割点
        change_points = sorted(list(set([0] + change_points + [len(df)-1])))
        
        # 创建段
        for i in range(len(change_points)-1):
            start_idx = change_points[i]
            end_idx = change_points[i+1]
            
            # 确保段长度至少为最小天数
            segment_days = (df.iloc[end_idx]['timestamp'] - df.iloc[start_idx]['timestamp']).days
            if segment_days >= self.min_segment_days:
                segments.append((start_idx, end_idx))
        
        return segments
    
    def _analyze_segment_pattern(self, segment_data: pd.DataFrame, segment_id: int) -> TemporalPatternSegment:
        """分析单个时间段的模式"""
        start_date = segment_data['timestamp'].min()
        end_date = segment_data['timestamp'].max()
        duration_days = (end_date - start_date).days + 1
        
        # 计算关键指标
        glucose_values = segment_data['glucose'].values
        mean_glucose = np.mean(glucose_values)
        cv_glucose = np.std(glucose_values) / mean_glucose * 100
        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100
        tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
        
        # 高级指标
        glucose_range = np.max(glucose_values) - np.min(glucose_values)
        
        # Dawn现象检测
        if 'hour' in segment_data.columns:
            dawn_data = segment_data[segment_data['hour'].between(4, 8)]
            pre_dawn_data = segment_data[segment_data['hour'].between(2, 4)]
            if len(dawn_data) > 0 and len(pre_dawn_data) > 0:
                dawn_magnitude = dawn_data['glucose'].mean() - pre_dawn_data['glucose'].mean()
            else:
                dawn_magnitude = 0
        else:
            dawn_magnitude = 0
        
        key_metrics = {
            'mean_glucose': mean_glucose,
            'cv_glucose': cv_glucose,
            'tir': tir,
            'tbr': tbr,
            'tar': tar,
            'glucose_range': glucose_range,
            'dawn_magnitude': dawn_magnitude,
            'data_points': len(glucose_values)
        }
        
        # 模式分类
        pattern_type = self._classify_segment_pattern(key_metrics)
        
        # 计算稳定性评分
        stability_score = self._calculate_segment_stability(segment_data)
        
        # 检测变化点
        segment_change_points = []
        if len(segment_data) > 48:  # 至少2天数据
            segment_glucose = segment_data['glucose'].values
            if len(segment_glucose) >= 24:
                rolling_mean = pd.Series(segment_glucose).rolling(window=24).mean()
                rolling_std = pd.Series(segment_glucose).rolling(window=24).std()
                
                # 检测内部变化点
                for i in range(24, len(rolling_mean)-24):
                    if (abs(rolling_mean.iloc[i] - rolling_mean.iloc[i-12]) > 1.5 or
                        abs(rolling_std.iloc[i] - rolling_std.iloc[i-12]) > 1.0):
                        change_time = segment_data.iloc[i]['timestamp']
                        segment_change_points.append(change_time)
        
        return TemporalPatternSegment(
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            pattern_type=pattern_type,
            key_metrics=key_metrics,
            stability_score=stability_score,
            change_points=segment_change_points
        )
    
    def _classify_segment_pattern(self, metrics: Dict[str, float]) -> str:
        """分类时间段模式"""
        tir = metrics['tir']
        cv = metrics['cv_glucose']
        mean_glucose = metrics['mean_glucose']
        tbr = metrics['tbr']
        dawn_magnitude = metrics.get('dawn_magnitude', 0)
        
        # 优先检测特殊模式
        if tbr > 4:
            return "低血糖风险型"
        elif abs(dawn_magnitude) > 2.0:
            return "黎明现象型" if dawn_magnitude > 0 else "反向黎明现象型"
        elif mean_glucose > 12:
            return "高血糖主导型"
        
        # 基于TIR和CV的综合分类
        if tir >= self.pattern_thresholds['excellent_tir'] and cv <= self.pattern_thresholds['excellent_cv']:
            return "稳定最优型"
        elif tir >= self.pattern_thresholds['good_tir'] and cv <= self.pattern_thresholds['good_cv']:
            return "稳定良好型"
        elif tir >= self.pattern_thresholds['acceptable_tir'] and cv <= self.pattern_thresholds['acceptable_cv']:
            return "可接受控制型"
        elif cv > self.pattern_thresholds['poor_cv']:
            return "高变异不稳定型"
        elif tir < self.pattern_thresholds['poor_tir']:
            return "控制不佳型"
        else:
            return "中等控制型"
    
    def _calculate_segment_stability(self, segment_data: pd.DataFrame) -> float:
        """计算时间段稳定性"""
        glucose_values = segment_data['glucose'].values
        
        if len(glucose_values) < 24:
            return 0.5
        
        # 计算多个稳定性指标
        cv = np.std(glucose_values) / np.mean(glucose_values)
        
        # 滑动窗口稳定性
        window_size = min(24, len(glucose_values) // 4)
        if window_size >= 4:
            rolling_means = pd.Series(glucose_values).rolling(window=window_size).mean()
            rolling_stds = pd.Series(glucose_values).rolling(window=window_size).std()
            
            mean_stability = 1 - (rolling_means.std() / rolling_means.mean())
            std_stability = 1 - (rolling_stds.std() / rolling_stds.mean())
            
            # 综合稳定性评分
            stability_score = (
                0.4 * (1 - min(cv, 1.0)) +  # CV稳定性
                0.3 * max(0, mean_stability) +  # 均值稳定性
                0.3 * max(0, std_stability)     # 变异稳定性
            )
        else:
            stability_score = 1 - min(cv, 1.0)
        
        return max(0, min(1, stability_score))
    
    def _identify_pattern_transitions(self, segments: List[TemporalPatternSegment]) -> List[PatternTransition]:
        """识别模式转换"""
        transitions = []
        
        for i in range(len(segments) - 1):
            current_segment = segments[i]
            next_segment = segments[i + 1]
            
            if current_segment.pattern_type != next_segment.pattern_type:
                # 计算转换强度
                tir_change = abs(next_segment.key_metrics['tir'] - current_segment.key_metrics['tir'])
                cv_change = abs(next_segment.key_metrics['cv_glucose'] - current_segment.key_metrics['cv_glucose'])
                mean_change = abs(next_segment.key_metrics['mean_glucose'] - current_segment.key_metrics['mean_glucose'])
                
                # 归一化转换强度 (0-1)
                transition_strength = min(1.0, (tir_change/50 + cv_change/30 + mean_change/5) / 3)
                
                # 推断可能原因
                likely_cause = self._infer_transition_cause(current_segment, next_segment)
                
                # 临床意义
                clinical_significance = self._assess_transition_significance(
                    current_segment.pattern_type, next_segment.pattern_type, transition_strength
                )
                
                transition = PatternTransition(
                    from_pattern=current_segment.pattern_type,
                    to_pattern=next_segment.pattern_type,
                    transition_date=next_segment.start_date,
                    transition_strength=transition_strength,
                    likely_cause=likely_cause,
                    clinical_significance=clinical_significance
                )
                transitions.append(transition)
        
        return transitions
    
    def _infer_transition_cause(self, from_segment: TemporalPatternSegment, 
                              to_segment: TemporalPatternSegment) -> str:
        """推断转换原因"""
        tir_change = to_segment.key_metrics['tir'] - from_segment.key_metrics['tir']
        cv_change = to_segment.key_metrics['cv_glucose'] - from_segment.key_metrics['cv_glucose']
        mean_change = to_segment.key_metrics['mean_glucose'] - from_segment.key_metrics['mean_glucose']
        
        # 基于变化模式推断原因
        if tir_change > 15 and cv_change < -5:
            return "治疗方案优化生效"
        elif tir_change < -15 and cv_change > 5:
            return "血糖控制恶化"
        elif mean_change > 2:
            return "可能存在应激因素或感染"
        elif mean_change < -2:
            return "可能胰岛素剂量增加或饮食改善"
        elif cv_change > 10:
            return "生活方式不规律或药物依从性问题"
        elif cv_change < -10:
            return "血糖稳定性改善"
        else:
            return "自然波动或多因素影响"
    
    def _assess_transition_significance(self, from_pattern: str, to_pattern: str, 
                                      strength: float) -> str:
        """评估转换的临床意义"""
        # 定义模式优先级（数值越小越好）
        pattern_priority = {
            "稳定最优型": 1,
            "稳定良好型": 2,
            "可接受控制型": 3,
            "中等控制型": 4,
            "控制不佳型": 5,
            "高变异不稳定型": 6,
            "低血糖风险型": 7,
            "高血糖主导型": 8,
            "黎明现象型": 4,
            "反向黎明现象型": 5
        }
        
        from_priority = pattern_priority.get(from_pattern, 5)
        to_priority = pattern_priority.get(to_pattern, 5)
        
        if to_priority < from_priority:  # 改善
            if strength > 0.7:
                return "显著改善，治疗效果良好"
            elif strength > 0.4:
                return "轻度改善，继续观察"
            else:
                return "微小改善，保持现有方案"
        elif to_priority > from_priority:  # 恶化
            if strength > 0.7:
                return "显著恶化，需要紧急调整治疗"
            elif strength > 0.4:
                return "轻度恶化，需要评估原因"
            else:
                return "微小恶化，加强监测"
        else:  # 模式转换但不明确好坏
            if strength > 0.5:
                return "模式显著变化，需要深入分析"
            else:
                return "模式微调，正常范围内波动"
    
    def _analyze_overall_evolution(self, segments: List[TemporalPatternSegment], 
                                 df: pd.DataFrame) -> PatternEvolution:
        """分析整体演进趋势"""
        if len(segments) < 2:
            return PatternEvolution.STABLE
        
        # 计算TIR趋势
        tir_values = [seg.key_metrics['tir'] for seg in segments]
        cv_values = [seg.key_metrics['cv_glucose'] for seg in segments]
        mean_values = [seg.key_metrics['mean_glucose'] for seg in segments]
        
        # 趋势分析
        x = np.arange(len(tir_values))
        
        # TIR趋势
        tir_slope, _, tir_r_value, tir_p_value, _ = stats.linregress(x, tir_values)
        cv_slope, _, cv_r_value, cv_p_value, _ = stats.linregress(x, cv_values)
        
        # 判断演进类型
        significant_trend = tir_p_value < 0.1 or cv_p_value < 0.1
        
        if significant_trend:
            if tir_slope > 5 and cv_slope < -3:  # TIR增加，CV减少
                return PatternEvolution.IMPROVING
            elif tir_slope < -5 or cv_slope > 3:  # TIR减少或CV增加
                return PatternEvolution.DETERIORATING
        
        # 检查周期性
        pattern_types = [seg.pattern_type for seg in segments]
        unique_patterns = len(set(pattern_types))
        pattern_changes = sum(1 for i in range(1, len(pattern_types)) 
                            if pattern_types[i] != pattern_types[i-1])
        
        if pattern_changes > len(segments) // 2:
            return PatternEvolution.FLUCTUATING
        elif unique_patterns > len(segments) // 2:
            return PatternEvolution.PHASE_TRANSITION
        elif pattern_changes >= 2 and len(segments) >= 4:
            # 检查是否有周期性
            if self._detect_cyclical_pattern(tir_values) or self._detect_cyclical_pattern(cv_values):
                return PatternEvolution.CYCLICAL
        
        return PatternEvolution.STABLE
    
    def _detect_cyclical_pattern(self, values: List[float], min_cycles: int = 2) -> bool:
        """检测周期性模式"""
        if len(values) < 4:
            return False
        
        # 简化的周期性检测
        # 检查是否有重复的高低模式
        peaks = []
        valleys = []
        
        for i in range(1, len(values)-1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                peaks.append(i)
            elif values[i] < values[i-1] and values[i] < values[i+1]:
                valleys.append(i)
        
        # 如果有足够的峰谷，可能是周期性
        return len(peaks) >= min_cycles and len(valleys) >= min_cycles
    
    def _calculate_trend_analysis(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算趋势分析"""
        # 按日统计
        daily_stats = df.groupby('date').agg({
            'glucose': ['mean', 'std', lambda x: np.sum((x >= 3.9) & (x <= 10.0)) / len(x) * 100]
        }).reset_index()
        daily_stats.columns = ['date', 'mean_glucose', 'std_glucose', 'tir']
        daily_stats['cv'] = daily_stats['std_glucose'] / daily_stats['mean_glucose'] * 100
        
        x = np.arange(len(daily_stats))
        
        trends = {}
        
        # 各指标趋势
        for metric in ['mean_glucose', 'cv', 'tir']:
            if metric in daily_stats.columns:
                values = daily_stats[metric].values
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                trends[f'{metric}_slope'] = slope
                trends[f'{metric}_r_squared'] = r_value**2
                trends[f'{metric}_p_value'] = p_value
                trends[f'{metric}_trend_strength'] = abs(r_value) if p_value < 0.05 else 0
        
        return trends
    
    def _determine_dominant_pattern(self, segments: List[TemporalPatternSegment]) -> str:
        """确定主导模式"""
        if not segments:
            return "未知模式"
        
        # 按持续时间加权统计模式
        pattern_duration = {}
        for segment in segments:
            pattern = segment.pattern_type
            duration = segment.duration_days
            pattern_duration[pattern] = pattern_duration.get(pattern, 0) + duration
        
        return max(pattern_duration.items(), key=lambda x: x[1])[0]
    
    def _calculate_pattern_stability(self, segments: List[TemporalPatternSegment]) -> float:
        """计算模式稳定性"""
        if not segments:
            return 0.0
        
        # 方法1：基于模式变化频率
        pattern_changes = 0
        for i in range(1, len(segments)):
            if segments[i].pattern_type != segments[i-1].pattern_type:
                pattern_changes += 1
        
        change_stability = 1 - (pattern_changes / max(1, len(segments) - 1))
        
        # 方法2：基于各段内部稳定性
        avg_internal_stability = np.mean([seg.stability_score for seg in segments])
        
        # 综合稳定性
        overall_stability = 0.6 * change_stability + 0.4 * avg_internal_stability
        
        return overall_stability
    
    def _generate_clinical_insights(self, segments: List[TemporalPatternSegment],
                                  transitions: List[PatternTransition],
                                  evolution: PatternEvolution,
                                  treatment_events: List[Dict] = None) -> List[str]:
        """生成临床洞察"""
        insights = []
        
        # 1. 整体演进洞察
        if evolution == PatternEvolution.IMPROVING:
            insights.append("血糖控制呈现改善趋势，当前治疗方案有效")
        elif evolution == PatternEvolution.DETERIORATING:
            insights.append("血糖控制呈现恶化趋势，建议重新评估治疗方案")
        elif evolution == PatternEvolution.FLUCTUATING:
            insights.append("血糖模式反复波动，需要识别不稳定因素")
        elif evolution == PatternEvolution.PHASE_TRANSITION:
            insights.append("出现明显的阶段性转换，可能与治疗调整相关")
        elif evolution == PatternEvolution.CYCLICAL:
            insights.append("呈现周期性血糖模式，建议分析周期性因素")
        
        # 2. 关键转换洞察
        significant_transitions = [t for t in transitions if t.transition_strength > 0.5]
        if significant_transitions:
            insights.append(f"检测到{len(significant_transitions)}次显著模式转换")
            for trans in significant_transitions[:2]:  # 显示前2个
                insights.append(f"从{trans.from_pattern}转为{trans.to_pattern}: {trans.clinical_significance}")
        
        # 3. 模式分布洞察
        pattern_types = [seg.pattern_type for seg in segments]
        unique_patterns = set(pattern_types)
        if len(unique_patterns) == 1:
            insights.append(f"血糖模式高度一致，始终保持{list(unique_patterns)[0]}")
        elif len(unique_patterns) > len(segments) // 2:
            insights.append("血糖模式多样化，需要个性化管理策略")
        
        # 4. 稳定性洞察
        stability_scores = [seg.stability_score for seg in segments]
        avg_stability = np.mean(stability_scores)
        if avg_stability > 0.8:
            insights.append("各时间段内部稳定性良好")
        elif avg_stability < 0.5:
            insights.append("各时间段内部稳定性较差，存在显著波动")
        
        # 5. 治疗事件关联洞察
        if treatment_events and len(segments) > 1:
            for event in treatment_events:
                event_date = pd.to_datetime(event['date'])
                # 查找事件前后的模式变化
                for i, seg in enumerate(segments[1:], 1):
                    if abs((seg.start_date - event_date).days) <= 7:
                        prev_seg = segments[i-1]
                        if seg.pattern_type != prev_seg.pattern_type:
                            insights.append(f"{event['event']}后血糖模式发生变化")
                        break
        
        return insights[:8]  # 最多返回8条洞察

    def generate_dynamic_report(self, profile: DynamicTemporalProfile,
                              include_visualizations: bool = False) -> Dict:
        """生成动态模式分析报告"""
        
        report = {
            'analyzer_info': {
                'name': self.analyzer_name,
                'version': self.version,
                'analysis_time': datetime.now().isoformat()
            },
            'analysis_summary': {
                'analysis_period': {
                    'start': profile.analysis_period[0].isoformat(),
                    'end': profile.analysis_period[1].isoformat(),
                    'duration_days': (profile.analysis_period[1] - profile.analysis_period[0]).days
                },
                'overall_evolution': profile.overall_evolution.value,
                'dominant_pattern': profile.dominant_pattern,
                'pattern_stability': profile.pattern_stability,
                'segments_count': len(profile.pattern_segments),
                'transitions_count': len(profile.pattern_transitions)
            },
            'pattern_segments': [],
            'pattern_transitions': [],
            'trend_analysis': profile.trend_analysis,
            'clinical_insights': profile.clinical_insights
        }
        
        # 时间段详情
        for i, segment in enumerate(profile.pattern_segments):
            segment_report = {
                'segment_id': i + 1,
                'period': {
                    'start': segment.start_date.isoformat(),
                    'end': segment.end_date.isoformat(),
                    'duration_days': segment.duration_days
                },
                'pattern_type': segment.pattern_type,
                'key_metrics': segment.key_metrics,
                'stability_score': segment.stability_score,
                'change_points_count': len(segment.change_points)
            }
            report['pattern_segments'].append(segment_report)
        
        # 模式转换详情
        for transition in profile.pattern_transitions:
            transition_report = {
                'from_pattern': transition.from_pattern,
                'to_pattern': transition.to_pattern,
                'transition_date': transition.transition_date.isoformat(),
                'transition_strength': transition.transition_strength,
                'likely_cause': transition.likely_cause,
                'clinical_significance': transition.clinical_significance
            }
            report['pattern_transitions'].append(transition_report)
        
        return report

# 使用示例
if __name__ == "__main__":
    analyzer = DynamicTemporalPatternAnalyzer()
    print(f"✅ {analyzer.analyzer_name} v{analyzer.version} 初始化完成")
    print("🔄 支持动态血糖模式分析:")
    print("   • 自动检测血糖模式变化点")
    print("   • 分析不同时间段的模式特征") 
    print("   • 识别模式转换和演进趋势")
    print("   • 提供基于时间段的个性化建议")