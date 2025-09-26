#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能时间分段分析器
基于数据驱动的多维度变化点检测和阶段识别
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from scipy import stats
from scipy.signal import find_peaks, savgol_filter
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class IntelligentSegmentationAnalyzer:
    """智能分段分析器"""
    
    def __init__(self, min_segment_days: int = 2, max_segments: int = 6):
        self.min_segment_days = min_segment_days
        self.max_segments = max_segments
        self.window_hours = 12  # 滑动窗口大小
        
    def analyze_intelligent_segments(self, df: pd.DataFrame, glucose_values: np.ndarray, total_days: int) -> Dict:
        """智能分段主函数"""
        
        print("[智能分段] 开始多维度变化点检测...")
        
        # 1. 数据预处理
        df_processed = self._preprocess_data(df.copy())
        
        # 2. 多维度指标计算
        indicators = self._calculate_sliding_indicators(df_processed, glucose_values)
        
        # 3. 多种变化点检测方法
        change_points = self._detect_change_points_comprehensive(indicators, df_processed)
        
        # 4. 变化点融合和筛选
        final_segments = self._merge_and_filter_segments(change_points, df_processed, total_days)
        
        # 5. 段间差异分析
        segment_analysis = self._analyze_segment_differences(final_segments, df_processed, glucose_values)
        
        # 6. 生成智能分段报告
        intelligent_report = {
            "分段方法": "基于数据驱动的多维度变化点检测",
            "检测维度": ["血糖控制质量", "脆性特征", "变异模式", "治疗反应"],
            "变化点检测结果": change_points,
            "最终分段": final_segments,
            "段间差异分析": segment_analysis,
            "分段评估": self._evaluate_segmentation_quality(segment_analysis)
        }
        
        return intelligent_report
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据预处理"""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 添加时间特征
        df['hour'] = df['timestamp'].dt.hour
        df['day_from_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
        df['hours_from_start'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds() / 3600
        
        return df
    
    def _calculate_sliding_indicators(self, df: pd.DataFrame, glucose_values: np.ndarray) -> Dict:
        """计算滑动窗口指标"""
        
        print("[智能分段] 计算滑动窗口指标...")
        
        timestamps = df['timestamp'].values
        hours_from_start = df['hours_from_start'].values
        
        # 滑动窗口参数
        window_size = int(len(glucose_values) * 0.1)  # 10%的数据作为窗口
        step_size = max(1, window_size // 4)  # 25%重叠
        
        indicators = {
            'timestamps': [],
            'hours': [],
            'mean_glucose': [],
            'cv': [],
            'tir': [],
            'gmi': [],
            'brittleness_score': [],
            'variability_index': [],
            'stability_score': [],
            'trend_strength': []
        }
        
        for i in range(0, len(glucose_values) - window_size + 1, step_size):
            window_glucose = glucose_values[i:i+window_size]
            window_hours = hours_from_start[i:i+window_size]
            
            if len(window_glucose) < self.window_hours:
                continue
            
            # 中心时间点
            center_idx = i + window_size // 2
            indicators['timestamps'].append(timestamps[center_idx])
            indicators['hours'].append(hours_from_start[center_idx])
            
            # 基础指标
            mean_glucose = np.mean(window_glucose)
            std_glucose = np.std(window_glucose)
            cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0
            tir = np.mean((window_glucose >= 3.9) & (window_glucose <= 10.0)) * 100
            
            # GMI计算
            mean_glucose_mgdl = mean_glucose * 18.018
            gmi = 3.31 + 0.02392 * mean_glucose_mgdl
            
            indicators['mean_glucose'].append(mean_glucose)
            indicators['cv'].append(cv)
            indicators['tir'].append(tir)
            indicators['gmi'].append(gmi)
            
            # 脆性评分
            brittleness = self._calculate_brittleness_score(window_glucose, cv, tir)
            indicators['brittleness_score'].append(brittleness)
            
            # 变异性指数
            glucose_diff = np.diff(window_glucose)
            variability_index = np.std(glucose_diff) if len(glucose_diff) > 0 else 0
            indicators['variability_index'].append(variability_index)
            
            # 稳定性评分
            stability = self._calculate_stability_score(window_glucose, cv, mean_glucose)
            indicators['stability_score'].append(stability)
            
            # 趋势强度
            if len(window_glucose) > 5:
                x = np.arange(len(window_glucose))
                slope, _, r_value, _, _ = stats.linregress(x, window_glucose)
                trend_strength = abs(r_value) * 100  # R²转换为百分比
            else:
                trend_strength = 0
            indicators['trend_strength'].append(trend_strength)
        
        # 转换为numpy数组
        for key in indicators:
            indicators[key] = np.array(indicators[key])
        
        return indicators
    
    def _calculate_brittleness_score(self, glucose_data: np.ndarray, cv: float, tir: float) -> float:
        """计算脆性评分"""
        brittleness_score = 0
        
        # CV贡献
        if cv > 50:
            brittleness_score += 40
        elif cv > 36:
            brittleness_score += 30
        elif cv > 25:
            brittleness_score += 20
        else:
            brittleness_score += 10
        
        # TIR贡献（反向）
        if tir < 50:
            brittleness_score += 30
        elif tir < 70:
            brittleness_score += 20
        elif tir < 80:
            brittleness_score += 10
        
        # 极值贡献
        extreme_high = np.sum(glucose_data > 15) / len(glucose_data) * 100
        extreme_low = np.sum(glucose_data < 3.0) / len(glucose_data) * 100
        
        brittleness_score += extreme_high * 2 + extreme_low * 3
        
        return min(100, brittleness_score)
    
    def _calculate_stability_score(self, glucose_data: np.ndarray, cv: float, mean_glucose: float) -> float:
        """计算稳定性评分"""
        stability_score = 100
        
        # CV惩罚
        stability_score -= cv * 1.5
        
        # 平均血糖偏离惩罚
        target_glucose = 7.0  # 理想血糖
        glucose_deviation = abs(mean_glucose - target_glucose)
        stability_score -= glucose_deviation * 5
        
        # 波动惩罚
        glucose_ranges = np.max(glucose_data) - np.min(glucose_data)
        stability_score -= glucose_ranges * 2
        
        return max(0, min(100, stability_score))
    
    def _detect_change_points_comprehensive(self, indicators: Dict, df: pd.DataFrame) -> Dict:
        """综合变化点检测"""
        
        print("[智能分段] 进行多维度变化点检测...")
        
        change_points = {
            'statistical_changes': [],
            'clustering_changes': [],
            'gradient_changes': [],
            'brittleness_changes': [],
            'composite_score': []
        }
        
        hours = indicators['hours']
        
        # 1. 统计显著性变化检测
        for metric in ['mean_glucose', 'cv', 'tir']:
            changes = self._detect_statistical_changes(indicators[metric], hours)
            change_points['statistical_changes'].extend(changes)
        
        # 2. 聚类变化点检测
        clustering_changes = self._detect_clustering_changes(indicators, hours)
        change_points['clustering_changes'] = clustering_changes
        
        # 3. 梯度变化检测
        for metric in ['brittleness_score', 'stability_score']:
            gradient_changes = self._detect_gradient_changes(indicators[metric], hours)
            change_points['gradient_changes'].extend(gradient_changes)
        
        # 4. 脆性阶段变化检测
        brittleness_changes = self._detect_brittleness_phase_changes(indicators, hours)
        change_points['brittleness_changes'] = brittleness_changes
        
        # 5. 计算综合变化点评分
        composite_changes = self._calculate_composite_change_score(change_points, hours)
        change_points['composite_score'] = composite_changes
        
        return change_points
    
    def _detect_statistical_changes(self, values: np.ndarray, hours: np.ndarray, 
                                  window_size: int = 10, threshold: float = 2.0) -> List[Dict]:
        """统计显著性变化检测"""
        changes = []
        
        if len(values) < window_size * 2:
            return changes
        
        for i in range(window_size, len(values) - window_size):
            before_window = values[i-window_size:i]
            after_window = values[i:i+window_size]
            
            # t检验
            try:
                t_stat, p_value = stats.ttest_ind(before_window, after_window)
                
                if p_value < 0.05 and abs(t_stat) > threshold:
                    change_magnitude = abs(np.mean(after_window) - np.mean(before_window))
                    
                    changes.append({
                        'hour': hours[i],
                        'change_type': 'statistical',
                        'magnitude': change_magnitude,
                        'p_value': p_value,
                        't_statistic': t_stat,
                        'direction': 'increase' if np.mean(after_window) > np.mean(before_window) else 'decrease'
                    })
            except:
                continue
        
        return changes
    
    def _detect_clustering_changes(self, indicators: Dict, hours: np.ndarray) -> List[Dict]:
        """基于聚类的变化点检测"""
        
        # 构建特征矩阵
        feature_names = ['mean_glucose', 'cv', 'tir', 'brittleness_score']
        features = np.column_stack([indicators[name] for name in feature_names])
        
        if len(features) < 6:  # 至少需要6个点进行聚类
            return []
        
        # 标准化特征
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        changes = []
        
        # 尝试不同的聚类数
        for n_clusters in range(2, min(6, len(features) // 3)):
            try:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(features_scaled)
                
                # 查找聚类标签变化点
                label_changes = np.where(np.diff(labels) != 0)[0]
                
                for change_idx in label_changes:
                    if change_idx > 0 and change_idx < len(hours) - 1:
                        # 计算变化强度
                        before_features = features[max(0, change_idx-2):change_idx+1]
                        after_features = features[change_idx+1:min(len(features), change_idx+4)]
                        
                        if len(before_features) > 0 and len(after_features) > 0:
                            change_magnitude = np.linalg.norm(
                                np.mean(after_features, axis=0) - np.mean(before_features, axis=0)
                            )
                            
                            changes.append({
                                'hour': hours[change_idx],
                                'change_type': 'clustering',
                                'magnitude': change_magnitude,
                                'n_clusters': n_clusters,
                                'from_cluster': labels[change_idx],
                                'to_cluster': labels[change_idx + 1]
                            })
            except:
                continue
        
        return changes
    
    def _detect_gradient_changes(self, values: np.ndarray, hours: np.ndarray, 
                               window_size: int = 5) -> List[Dict]:
        """梯度变化检测"""
        changes = []
        
        if len(values) < window_size * 2:
            return changes
        
        # 计算平滑梯度
        smoothed_values = savgol_filter(values, min(11, len(values)//2*2+1), 3)
        gradient = np.gradient(smoothed_values)
        
        # 检测梯度显著变化
        gradient_change = np.abs(np.diff(gradient))
        threshold = np.percentile(gradient_change, 75)  # 75%分位数作为阈值
        
        significant_changes = np.where(gradient_change > threshold)[0]
        
        for change_idx in significant_changes:
            if change_idx < len(hours) - 1:
                changes.append({
                    'hour': hours[change_idx],
                    'change_type': 'gradient',
                    'magnitude': gradient_change[change_idx],
                    'gradient_before': gradient[change_idx],
                    'gradient_after': gradient[change_idx + 1]
                })
        
        return changes
    
    def _detect_brittleness_phase_changes(self, indicators: Dict, hours: np.ndarray) -> List[Dict]:
        """脆性阶段变化检测"""
        brittleness_scores = indicators['brittleness_score']
        stability_scores = indicators['stability_score']
        
        changes = []
        
        # 定义脆性等级
        def classify_brittleness(score):
            if score > 75:
                return 'high'
            elif score > 50:
                return 'moderate'
            elif score > 25:
                return 'low'
            else:
                return 'stable'
        
        # 滑动窗口检测阶段变化
        window_size = max(3, len(brittleness_scores) // 10)
        
        for i in range(window_size, len(brittleness_scores) - window_size):
            before_phase = [classify_brittleness(score) 
                          for score in brittleness_scores[i-window_size:i]]
            after_phase = [classify_brittleness(score) 
                         for score in brittleness_scores[i:i+window_size]]
            
            before_dominant = max(set(before_phase), key=before_phase.count)
            after_dominant = max(set(after_phase), key=after_phase.count)
            
            if before_dominant != after_dominant:
                # 计算相对变化强度
                before_avg = np.mean(brittleness_scores[i-window_size:i])
                after_avg = np.mean(brittleness_scores[i:i+window_size])
                
                changes.append({
                    'hour': hours[i],
                    'change_type': 'brittleness_phase',
                    'from_phase': before_dominant,
                    'to_phase': after_dominant,
                    'magnitude': abs(after_avg - before_avg),
                    'direction': 'improvement' if after_avg < before_avg else 'deterioration'
                })
        
        return changes
    
    def _calculate_composite_change_score(self, change_points: Dict, hours: np.ndarray) -> List[Dict]:
        """计算综合变化点评分"""
        
        # 将所有变化点按时间排序
        all_changes = []
        
        for change_type, changes in change_points.items():
            if change_type == 'composite_score':  # 跳过自身
                continue
            
            for change in changes:
                all_changes.append({
                    'hour': change['hour'],
                    'type': change_type,
                    'magnitude': change.get('magnitude', 0)
                })
        
        if not all_changes:
            return []
        
        # 按时间排序
        all_changes.sort(key=lambda x: x['hour'])
        
        # 计算时间窗口内的变化点密度
        window_hours = 24  # 24小时窗口
        composite_changes = []
        
        for hour in np.arange(0, hours.max(), 6):  # 每6小时检查一次
            window_changes = [c for c in all_changes 
                            if abs(c['hour'] - hour) <= window_hours/2]
            
            if len(window_changes) >= 2:  # 至少需要2个变化点才认为是显著变化
                total_magnitude = sum(c['magnitude'] for c in window_changes)
                change_density = len(window_changes) / window_hours
                
                composite_score = total_magnitude * change_density
                
                composite_changes.append({
                    'hour': hour,
                    'change_type': 'composite',
                    'magnitude': total_magnitude,
                    'density': change_density,
                    'score': composite_score,
                    'contributing_changes': len(window_changes)
                })
        
        # 排序并选择最显著的变化点
        composite_changes.sort(key=lambda x: x['score'], reverse=True)
        
        return composite_changes[:self.max_segments-1]  # 最多返回max_segments-1个分割点
    
    def _merge_and_filter_segments(self, change_points: Dict, df: pd.DataFrame, total_days: int) -> List[Dict]:
        """合并和筛选分段"""
        
        print("[智能分段] 合并和筛选变化点...")
        
        # 收集所有有意义的变化点
        significant_changes = []
        
        # 1. 使用综合评分最高的变化点
        composite_changes = change_points.get('composite_score', [])
        for change in composite_changes[:3]:  # 最多3个综合变化点
            significant_changes.append(change['hour'])
        
        # 2. 添加统计显著性最高的变化点
        stat_changes = change_points.get('statistical_changes', [])
        stat_changes.sort(key=lambda x: abs(x.get('t_statistic', 0)), reverse=True)
        for change in stat_changes[:2]:  # 最多2个统计变化点
            hour = change['hour']
            if not any(abs(hour - existing) < 24 for existing in significant_changes):
                significant_changes.append(hour)
        
        # 3. 添加脆性阶段变化最显著的点
        brittleness_changes = change_points.get('brittleness_changes', [])
        brittleness_changes.sort(key=lambda x: x.get('magnitude', 0), reverse=True)
        for change in brittleness_changes[:2]:  # 最多2个脆性变化点
            hour = change['hour']
            if not any(abs(hour - existing) < 24 for existing in significant_changes):
                significant_changes.append(hour)
        
        # 排序变化点
        significant_changes.sort()
        
        # 确保最小段长度
        min_hours = self.min_segment_days * 24
        filtered_changes = []
        last_change = -min_hours
        
        for change_hour in significant_changes:
            if change_hour - last_change >= min_hours:
                filtered_changes.append(change_hour)
                last_change = change_hour
        
        # 生成最终分段
        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()
        total_hours = (end_time - start_time).total_seconds() / 3600
        
        segments = []
        current_start = 0
        
        for i, change_hour in enumerate(filtered_changes):
            segment_start = start_time + timedelta(hours=current_start)
            segment_end = start_time + timedelta(hours=change_hour)
            
            segments.append({
                'segment_id': i + 1,
                'start_time': segment_start,
                'end_time': segment_end,
                'start_hour': current_start,
                'end_hour': change_hour,
                'duration_hours': change_hour - current_start,
                'duration_days': (change_hour - current_start) / 24
            })
            
            current_start = change_hour
        
        # 最后一段
        if current_start < total_hours:
            segments.append({
                'segment_id': len(segments) + 1,
                'start_time': start_time + timedelta(hours=current_start),
                'end_time': end_time,
                'start_hour': current_start,
                'end_hour': total_hours,
                'duration_hours': total_hours - current_start,
                'duration_days': (total_hours - current_start) / 24
            })
        
        return segments
    
    def _analyze_segment_differences(self, segments: List[Dict], df: pd.DataFrame, 
                                   glucose_values: np.ndarray) -> Dict:
        """分析段间差异"""
        
        print("[智能分段] 分析段间差异...")
        
        segment_analysis = {}
        
        for segment in segments:
            # 提取段内数据
            mask = ((df['timestamp'] >= segment['start_time']) & 
                   (df['timestamp'] <= segment['end_time']))
            segment_data = df[mask]['glucose'].values
            
            if len(segment_data) < 5:
                continue
            
            # 计算段内指标
            analysis = self._analyze_single_segment(segment_data, segment)
            
            segment_name = f"第{segment['segment_id']}段({segment['start_time'].strftime('%m-%d %H:%M')}至{segment['end_time'].strftime('%m-%d %H:%M')})"
            segment_analysis[segment_name] = analysis
        
        # 计算段间差异统计
        if len(segment_analysis) >= 2:
            segment_comparison = self._compare_segments(segment_analysis)
            segment_analysis['段间差异统计'] = segment_comparison
        
        return segment_analysis
    
    def _analyze_single_segment(self, glucose_data: np.ndarray, segment: Dict) -> Dict:
        """分析单个段的特征"""
        
        mean_glucose = np.mean(glucose_data)
        std_glucose = np.std(glucose_data)
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0
        
        tir = np.mean((glucose_data >= 3.9) & (glucose_data <= 10.0)) * 100
        time_above = np.mean(glucose_data > 10.0) * 100
        time_below = np.mean(glucose_data < 3.9) * 100
        
        # GMI计算
        mean_glucose_mgdl = mean_glucose * 18.018
        gmi = 3.31 + 0.02392 * mean_glucose_mgdl
        
        # 脆性评分
        brittleness_score = self._calculate_brittleness_score(glucose_data, cv, tir)
        
        # 稳定性评分
        stability_score = self._calculate_stability_score(glucose_data, cv, mean_glucose)
        
        # 控制质量评级
        if mean_glucose <= 8.0 and tir >= 70 and cv <= 25:
            control_grade = "优秀"
        elif mean_glucose <= 10.0 and tir >= 50 and cv <= 35:
            control_grade = "良好"
        elif mean_glucose <= 12.0 and tir >= 30 and cv <= 50:
            control_grade = "需改善"
        else:
            control_grade = "较差"
        
        # 脆性分级
        if brittleness_score > 75:
            brittleness_grade = "高脆性"
        elif brittleness_score > 50:
            brittleness_grade = "中等脆性"
        elif brittleness_score > 25:
            brittleness_grade = "低脆性"
        else:
            brittleness_grade = "稳定"
        
        return {
            "段基本信息": {
                "持续时间": f"{segment['duration_days']:.1f}天",
                "数据点数": len(glucose_data),
                "时间范围": f"{segment['start_time'].strftime('%m-%d %H:%M')} 至 {segment['end_time'].strftime('%m-%d %H:%M')}"
            },
            "血糖控制指标": {
                "平均血糖": f"{mean_glucose:.1f} mmol/L",
                "血糖标准差": f"{std_glucose:.1f} mmol/L",
                "变异系数": f"{cv:.1f}%",
                "GMI": f"{gmi:.1f}%",
                "血糖范围": f"{glucose_data.min():.1f}-{glucose_data.max():.1f} mmol/L"
            },
            "时间分布指标": {
                "目标范围时间": f"{tir:.1f}%",
                "高血糖时间": f"{time_above:.1f}%",
                "低血糖时间": f"{time_below:.1f}%"
            },
            "脆性与稳定性": {
                "脆性评分": f"{brittleness_score:.1f}/100",
                "脆性等级": brittleness_grade,
                "稳定性评分": f"{stability_score:.1f}/100",
                "控制质量": control_grade
            },
            # 用于比较的原始数值
            "_raw_metrics": {
                "mean_glucose": mean_glucose,
                "cv": cv,
                "tir": tir,
                "brittleness_score": brittleness_score,
                "stability_score": stability_score
            }
        }
    
    def _compare_segments(self, segment_analysis: Dict) -> Dict:
        """比较段间差异"""
        
        segments = [seg for seg in segment_analysis.keys() if seg != '段间差异统计']
        
        if len(segments) < 2:
            return {"error": "段数不足，无法进行比较"}
        
        # 提取各段指标
        metrics = {
            'mean_glucose': [],
            'cv': [],
            'tir': [],
            'brittleness_score': [],
            'stability_score': []
        }
        
        for seg_name in segments:
            raw_metrics = segment_analysis[seg_name]['_raw_metrics']
            for metric in metrics.keys():
                metrics[metric].append(raw_metrics[metric])
        
        # 计算变化趋势
        trends = {}
        for metric, values in metrics.items():
            if len(values) >= 2:
                first_val = values[0]
                last_val = values[-1]
                change = last_val - first_val
                change_percent = (change / first_val * 100) if first_val != 0 else 0
                
                if metric in ['cv', 'brittleness_score']:  # 这些指标越低越好
                    direction = "改善" if change < 0 else "恶化" if change > 0 else "稳定"
                elif metric in ['tir', 'stability_score']:  # 这些指标越高越好
                    direction = "改善" if change > 0 else "恶化" if change < 0 else "稳定"
                else:  # mean_glucose
                    target = 7.5
                    first_deviation = abs(first_val - target)
                    last_deviation = abs(last_val - target)
                    direction = "改善" if last_deviation < first_deviation else "恶化" if last_deviation > first_deviation else "稳定"
                
                trends[metric] = {
                    "变化值": f"{change:+.1f}",
                    "变化百分比": f"{change_percent:+.1f}%",
                    "趋势": direction,
                    "首段值": f"{first_val:.1f}",
                    "末段值": f"{last_val:.1f}"
                }
        
        # 识别最显著变化
        max_improvement = None
        max_deterioration = None
        
        for metric, trend in trends.items():
            change_magnitude = abs(float(trend["变化百分比"].replace('+', '').replace('%', '')))
            
            if trend["趋势"] == "改善" and (max_improvement is None or change_magnitude > max_improvement[1]):
                max_improvement = (metric, change_magnitude, trend)
            elif trend["趋势"] == "恶化" and (max_deterioration is None or change_magnitude > max_deterioration[1]):
                max_deterioration = (metric, change_magnitude, trend)
        
        # 生成总体评估
        improvement_count = sum(1 for t in trends.values() if t["趋势"] == "改善")
        deterioration_count = sum(1 for t in trends.values() if t["趋势"] == "恶化")
        
        if improvement_count > deterioration_count:
            overall_trend = "整体改善"
        elif deterioration_count > improvement_count:
            overall_trend = "整体恶化"
        else:
            overall_trend = "整体稳定"
        
        return {
            "总体趋势": overall_trend,
            "各指标变化趋势": trends,
            "最显著改善": {
                "指标": max_improvement[0],
                "改善幅度": f"{max_improvement[1]:.1f}%",
                "详情": max_improvement[2]
            } if max_improvement else "无显著改善",
            "最显著恶化": {
                "指标": max_deterioration[0],
                "恶化幅度": f"{max_deterioration[1]:.1f}%",
                "详情": max_deterioration[2]
            } if max_deterioration else "无显著恶化",
            "改善指标数": improvement_count,
            "恶化指标数": deterioration_count,
            "稳定指标数": len(trends) - improvement_count - deterioration_count
        }
    
    def _evaluate_segmentation_quality(self, segment_analysis: Dict) -> Dict:
        """评估分段质量"""
        
        segments = [seg for seg in segment_analysis.keys() if seg != '段间差异统计']
        
        if len(segments) < 2:
            return {"quality": "无法评估", "reason": "段数不足"}
        
        # 计算段内一致性
        consistency_scores = []
        for seg_name in segments:
            raw_metrics = segment_analysis[seg_name]['_raw_metrics']
            cv = raw_metrics['cv']
            brittleness = raw_metrics['brittleness_score']
            
            # 一致性评分：CV和脆性评分都低表示段内一致性好
            consistency = max(0, 100 - cv - brittleness * 0.5)
            consistency_scores.append(consistency)
        
        avg_consistency = np.mean(consistency_scores)
        
        # 计算段间差异性
        if '段间差异统计' in segment_analysis:
            diff_stats = segment_analysis['段间差异统计']
            improvement_count = diff_stats.get('改善指标数', 0)
            deterioration_count = diff_stats.get('恶化指标数', 0)
            
            # 差异性评分：有变化趋势表示分段有意义
            differentiation = (improvement_count + deterioration_count) / len(segments) * 20
        else:
            differentiation = 0
        
        # 综合质量评分
        quality_score = (avg_consistency * 0.6 + differentiation * 0.4)
        
        if quality_score > 70:
            quality_grade = "优秀"
            quality_desc = "分段合理，段内一致性高，段间差异明显"
        elif quality_score > 50:
            quality_grade = "良好"
            quality_desc = "分段较为合理，存在一定的时间演变特征"
        elif quality_score > 30:
            quality_grade = "一般"
            quality_desc = "分段部分合理，但段间差异不够显著"
        else:
            quality_grade = "较差"
            quality_desc = "分段效果不理想，可能需要调整分段策略"
        
        return {
            "分段质量评分": f"{quality_score:.1f}/100",
            "质量等级": quality_grade,
            "质量描述": quality_desc,
            "段数": len(segments),
            "平均段内一致性": f"{avg_consistency:.1f}/100",
            "段间差异性": f"{differentiation:.1f}/100",
            "建议": self._generate_segmentation_recommendations(quality_score, len(segments))
        }
    
    def _generate_segmentation_recommendations(self, quality_score: float, num_segments: int) -> List[str]:
        """生成分段建议"""
        recommendations = []
        
        if quality_score < 30:
            recommendations.append("当前分段效果不佳，建议调整分段策略")
            if num_segments > 4:
                recommendations.append("可考虑减少分段数，寻找更显著的变化点")
            else:
                recommendations.append("可考虑增加监测时间长度以获得更多数据")
        
        if num_segments < 2:
            recommendations.append("分段数过少，无法体现时间演变特征")
        elif num_segments > 6:
            recommendations.append("分段数过多，可能造成过度分割")
        
        if quality_score > 70:
            recommendations.append("分段质量优秀，可用于精准的时间演变分析")
            recommendations.append("建议基于此分段进行个体化治疗策略调整")
        
        return recommendations if recommendations else ["分段合理，可进行后续分析"]


# 测试函数
def test_intelligent_segmentation():
    """测试智能分段功能"""
    import sys
    
    # 使用真实数据进行测试
    filepath = "/Users/williamsun/Documents/gplus/docs/AGPAI/demodata/胰腺外科/上官李军-253124-1MH011R56MM.xlsx"
    
    # 加载数据
    df = pd.read_excel(filepath)
    if 'glucose' in df.columns:
        df = df.rename(columns={'glucose': 'glucose'})
    elif '值' in df.columns:
        df = df.rename(columns={'值': 'glucose', '时间': 'timestamp'})
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    glucose_values = df['glucose'].dropna().values
    total_days = (df['timestamp'].max() - df['timestamp'].min()).days + 1
    
    print(f"数据加载完成: {len(glucose_values)}个数据点, {total_days}天")
    
    # 创建智能分段分析器
    analyzer = IntelligentSegmentationAnalyzer(min_segment_days=2, max_segments=5)
    
    # 进行智能分段分析
    result = analyzer.analyze_intelligent_segments(df, glucose_values, total_days)
    
    # 保存结果
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Intelligent_Segmentation_Analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"智能分段分析完成，结果已保存: {filename}")
    
    # 打印简要结果
    print("\n=== 智能分段结果概览 ===")
    print(f"检测到 {len(result['最终分段'])} 个智能分段:")
    
    for segment in result['最终分段']:
        print(f"第{segment['segment_id']}段: {segment['duration_days']:.1f}天 ({segment['start_time'].strftime('%m-%d %H:%M')} ~ {segment['end_time'].strftime('%m-%d %H:%M')})")
    
    quality = result['分段评估']
    print(f"\n分段质量: {quality['质量等级']} ({quality['分段质量评分']})")
    print(f"分段描述: {quality['质量描述']}")


if __name__ == "__main__":
    test_intelligent_segmentation()