#!/usr/bin/env python3
"""
治疗切点检测器
用于识别胰腺外科等场景下的断崖式治疗调整时间点
支持多种切点检测算法和分段脆性分析
"""

import numpy as np
import pandas as pd
from scipy import stats, signal
from scipy.optimize import minimize_scalar
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from typing import List, Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class TreatmentCutpointDetector:
    """
    治疗切点检测器
    专门用于识别胰腺外科患者的治疗方案调整时间点
    """
    
    def __init__(self):
        """初始化切点检测器"""
        self.detector_name = "Treatment Cutpoint Detector"
        self.version = "1.0.0"
        
        # 检测参数
        self.detection_params = {
            'min_segment_hours': 24,      # 最小片段长度（小时）
            'change_threshold': 0.3,      # 变化阈值
            'statistical_pvalue': 0.01,   # 统计显著性阈值
            'window_hours': 8,            # 滑动窗口（小时）
            'stability_hours': 12         # 稳定期长度（小时）
        }
        
        # 切点类型定义
        self.cutpoint_types = {
            'SURGICAL': '手术切点',
            'MEDICATION': '药物调整切点', 
            'NUTRITION': '营养方案切点',
            'STRESS': '应激反应切点',
            'INFECTION': '感染切点',
            'UNKNOWN': '未知切点'
        }
    
    def detect_cutpoints(self, 
                        glucose_data: np.ndarray,
                        timestamps: np.ndarray,
                        method: str = 'comprehensive') -> List[Dict]:
        """
        检测治疗切点
        
        Args:
            glucose_data: 血糖数据
            timestamps: 时间戳数组
            method: 检测方法 ('variance', 'mean', 'trend', 'comprehensive')
            
        Returns:
            切点信息列表
        """
        if len(glucose_data) < 100:  # 至少需要100个数据点
            return []
        
        cutpoints = []
        
        if method == 'comprehensive':
            # 综合多种方法
            variance_points = self._detect_variance_change(glucose_data, timestamps)
            mean_points = self._detect_mean_change(glucose_data, timestamps)
            trend_points = self._detect_trend_change(glucose_data, timestamps)
            
            # 合并和去重
            all_points = variance_points + mean_points + trend_points
            cutpoints = self._merge_nearby_cutpoints(all_points, timestamps)
            
        elif method == 'variance':
            cutpoints = self._detect_variance_change(glucose_data, timestamps)
        elif method == 'mean':
            cutpoints = self._detect_mean_change(glucose_data, timestamps)
        elif method == 'trend':
            cutpoints = self._detect_trend_change(glucose_data, timestamps)
        
        # 验证和优化切点
        validated_cutpoints = self._validate_cutpoints(cutpoints, glucose_data, timestamps)
        
        return validated_cutpoints
    
    def _detect_variance_change(self, glucose_data: np.ndarray, timestamps: np.ndarray) -> List[Dict]:
        """检测方差变化切点"""
        cutpoints = []
        window_size = max(20, len(glucose_data) // 20)  # 动态窗口大小
        
        # 计算滑动方差
        variances = []
        for i in range(window_size, len(glucose_data) - window_size):
            left_var = np.var(glucose_data[i-window_size:i])
            right_var = np.var(glucose_data[i:i+window_size])
            
            # 方差比值
            var_ratio = max(left_var, right_var) / (min(left_var, right_var) + 1e-6)
            variances.append((i, var_ratio, left_var, right_var))
        
        # 寻找显著的方差变化点
        var_ratios = [v[1] for v in variances]
        threshold = np.percentile(var_ratios, 95)  # 95分位数作为阈值
        
        for i, var_ratio, left_var, right_var in variances:
            if var_ratio > threshold and var_ratio > 2.0:  # 方差变化超过2倍
                cutpoints.append({
                    'index': i,
                    'timestamp': timestamps[i],
                    'method': 'variance_change',
                    'significance': var_ratio,
                    'left_variance': left_var,
                    'right_variance': right_var,
                    'type': 'UNKNOWN'
                })
        
        return cutpoints
    
    def _detect_mean_change(self, glucose_data: np.ndarray, timestamps: np.ndarray) -> List[Dict]:
        """检测均值变化切点"""
        cutpoints = []
        window_size = max(20, len(glucose_data) // 20)
        
        # 计算滑动均值差异
        for i in range(window_size, len(glucose_data) - window_size):
            left_mean = np.mean(glucose_data[i-window_size:i])
            right_mean = np.mean(glucose_data[i:i+window_size])
            
            # t检验
            left_segment = glucose_data[i-window_size:i]
            right_segment = glucose_data[i:i+window_size]
            
            try:
                t_stat, p_value = stats.ttest_ind(left_segment, right_segment)
                
                # 效应大小 (Cohen's d)
                pooled_std = np.sqrt(((len(left_segment)-1) * np.var(left_segment, ddof=1) + 
                                    (len(right_segment)-1) * np.var(right_segment, ddof=1)) / 
                                   (len(left_segment) + len(right_segment) - 2))
                cohens_d = abs(left_mean - right_mean) / (pooled_std + 1e-6)
                
                # 显著性检验
                if p_value < self.detection_params['statistical_pvalue'] and cohens_d > 0.5:
                    cutpoints.append({
                        'index': i,
                        'timestamp': timestamps[i],
                        'method': 'mean_change',
                        'significance': cohens_d,
                        'p_value': p_value,
                        'left_mean': left_mean,
                        'right_mean': right_mean,
                        'mean_change': right_mean - left_mean,
                        'type': self._classify_cutpoint_type(right_mean - left_mean, cohens_d)
                    })
                    
            except:
                continue
        
        return cutpoints
    
    def _detect_trend_change(self, glucose_data: np.ndarray, timestamps: np.ndarray) -> List[Dict]:
        """检测趋势变化切点"""
        cutpoints = []
        window_size = max(30, len(glucose_data) // 15)
        
        for i in range(window_size, len(glucose_data) - window_size):
            # 左侧趋势
            left_x = np.arange(window_size)
            left_y = glucose_data[i-window_size:i]
            left_slope, _, left_r, _, _ = stats.linregress(left_x, left_y)
            
            # 右侧趋势
            right_x = np.arange(window_size)
            right_y = glucose_data[i:i+window_size]
            right_slope, _, right_r, _, _ = stats.linregress(right_x, right_y)
            
            # 趋势变化检测
            slope_change = abs(right_slope - left_slope)
            trend_significance = abs(right_r) + abs(left_r)  # 两侧相关性之和
            
            # 显著趋势变化
            if slope_change > 0.1 and trend_significance > 0.5:
                cutpoints.append({
                    'index': i,
                    'timestamp': timestamps[i],
                    'method': 'trend_change',
                    'significance': slope_change,
                    'left_slope': left_slope,
                    'right_slope': right_slope,
                    'left_correlation': left_r,
                    'right_correlation': right_r,
                    'slope_change': right_slope - left_slope,
                    'type': self._classify_trend_type(left_slope, right_slope)
                })
        
        return cutpoints
    
    def _classify_cutpoint_type(self, mean_change: float, effect_size: float) -> str:
        """根据均值变化分类切点类型"""
        if abs(mean_change) > 4.0:  # 血糖变化超过4 mmol/L
            return 'SURGICAL'
        elif abs(mean_change) > 2.0 and effect_size > 1.0:
            return 'MEDICATION'
        elif mean_change > 1.0:
            return 'STRESS'
        else:
            return 'UNKNOWN'
    
    def _classify_trend_type(self, left_slope: float, right_slope: float) -> str:
        """根据趋势变化分类切点类型"""
        if left_slope < -0.2 and right_slope > 0.2:  # 从下降变为上升
            return 'MEDICATION'
        elif left_slope > 0.2 and right_slope < -0.2:  # 从上升变为下降
            return 'SURGICAL'
        elif abs(right_slope - left_slope) > 0.5:
            return 'STRESS'
        else:
            return 'UNKNOWN'
    
    def _merge_nearby_cutpoints(self, cutpoints: List[Dict], timestamps: np.ndarray) -> List[Dict]:
        """合并邻近的切点"""
        if not cutpoints:
            return []
        
        # 按时间排序
        cutpoints.sort(key=lambda x: x['index'])
        
        merged = []
        current_group = [cutpoints[0]]
        
        for i in range(1, len(cutpoints)):
            # 检查时间间隔（以小时为单位）
            time_diff_hours = (timestamps[cutpoints[i]['index']] - 
                             timestamps[current_group[-1]['index']]) / np.timedelta64(1, 'h')
            
            if time_diff_hours < self.detection_params['stability_hours']:
                current_group.append(cutpoints[i])
            else:
                # 处理当前组
                merged_point = self._merge_cutpoint_group(current_group)
                merged.append(merged_point)
                current_group = [cutpoints[i]]
        
        # 处理最后一组
        if current_group:
            merged_point = self._merge_cutpoint_group(current_group)
            merged.append(merged_point)
        
        return merged
    
    def _merge_cutpoint_group(self, group: List[Dict]) -> Dict:
        """合并一组切点"""
        if len(group) == 1:
            return group[0]
        
        # 选择显著性最高的切点作为代表
        best_point = max(group, key=lambda x: x.get('significance', 0))
        
        # 合并信息
        methods = list(set([p['method'] for p in group]))
        types = list(set([p['type'] for p in group]))
        
        best_point['methods'] = methods
        best_point['merged_types'] = types
        best_point['group_size'] = len(group)
        
        return best_point
    
    def _validate_cutpoints(self, cutpoints: List[Dict], 
                          glucose_data: np.ndarray, 
                          timestamps: np.ndarray) -> List[Dict]:
        """验证切点的有效性"""
        validated = []
        
        for cutpoint in cutpoints:
            idx = cutpoint['index']
            
            # 确保切点前后有足够的数据
            min_points = int(self.detection_params['min_segment_hours'] * 4)  # 假设15分钟一个点
            
            if idx < min_points or idx > len(glucose_data) - min_points:
                continue
            
            # 检查切点前后的稳定性
            pre_segment = glucose_data[idx-min_points:idx]
            post_segment = glucose_data[idx:idx+min_points]
            
            # 计算段内稳定性
            pre_stability = self._calculate_stability(pre_segment)
            post_stability = self._calculate_stability(post_segment)
            
            # 只保留稳定性合理的切点
            if pre_stability > 0.3 or post_stability > 0.3:  # 至少一段相对稳定
                cutpoint['pre_stability'] = pre_stability
                cutpoint['post_stability'] = post_stability
                cutpoint['validated'] = True
                validated.append(cutpoint)
        
        return validated
    
    def _calculate_stability(self, segment: np.ndarray) -> float:
        """计算段内稳定性评分 (0-1)"""
        if len(segment) < 10:
            return 0.0
        
        # 多个稳定性指标
        cv = np.std(segment) / (np.mean(segment) + 1e-6)  # 变异系数
        trend_strength = abs(stats.linregress(range(len(segment)), segment)[2])  # 趋势强度
        autocorr = np.corrcoef(segment[:-1], segment[1:])[0, 1] if len(segment) > 1 else 0
        
        # 综合稳定性评分
        stability = (1 / (1 + cv)) * 0.4 + (1 - trend_strength) * 0.3 + abs(autocorr) * 0.3
        
        return max(0, min(1, stability))
    
    def analyze_segments(self, glucose_data: np.ndarray, 
                        timestamps: np.ndarray,
                        cutpoints: List[Dict]) -> List[Dict]:
        """分析切点分割的各个片段"""
        if not cutpoints:
            # 无切点，整段分析
            return [{
                'segment_id': 0,
                'start_idx': 0,
                'end_idx': len(glucose_data),
                'start_time': timestamps[0],
                'end_time': timestamps[-1],
                'duration_hours': (timestamps[-1] - timestamps[0]) / np.timedelta64(1, 'h'),
                'glucose_data': glucose_data,
                'type': 'complete'
            }]
        
        segments = []
        
        # 添加切点索引，包含起始和结束
        cutpoint_indices = [0] + [cp['index'] for cp in cutpoints] + [len(glucose_data)]
        cutpoint_indices = sorted(list(set(cutpoint_indices)))  # 去重并排序
        
        for i in range(len(cutpoint_indices) - 1):
            start_idx = cutpoint_indices[i]
            end_idx = cutpoint_indices[i + 1]
            
            if end_idx - start_idx < 20:  # 片段太短
                continue
            
            segment_data = glucose_data[start_idx:end_idx]
            segment_timestamps = timestamps[start_idx:end_idx]
            
            duration = (segment_timestamps[-1] - segment_timestamps[0]) / np.timedelta64(1, 'h')
            
            # 分析片段特征
            segment_analysis = {
                'segment_id': i,
                'start_idx': start_idx,
                'end_idx': end_idx,
                'start_time': segment_timestamps[0],
                'end_time': segment_timestamps[-1],
                'duration_hours': duration,
                'glucose_data': segment_data,
                'mean_glucose': np.mean(segment_data),
                'glucose_std': np.std(segment_data),
                'cv': np.std(segment_data) / (np.mean(segment_data) + 1e-6) * 100,
                'min_glucose': np.min(segment_data),
                'max_glucose': np.max(segment_data),
                'glucose_range': np.max(segment_data) - np.min(segment_data)
            }
            
            # 确定片段类型
            if i == 0:
                segment_analysis['type'] = 'pre_treatment'
            elif i == len(cutpoint_indices) - 2:
                segment_analysis['type'] = 'post_treatment'
            else:
                segment_analysis['type'] = f'intermediate_{i}'
            
            # 添加对应的切点信息
            if i < len(cutpoints):
                segment_analysis['cutpoint_info'] = cutpoints[i]
            
            segments.append(segment_analysis)
        
        return segments
    
    def compare_segments(self, segments: List[Dict]) -> Dict:
        """比较不同片段的差异"""
        if len(segments) < 2:
            return {'error': '需要至少2个片段进行比较'}
        
        comparison = {
            'segment_count': len(segments),
            'total_duration': sum(s['duration_hours'] for s in segments),
            'comparisons': []
        }
        
        # 两两比较相邻片段
        for i in range(len(segments) - 1):
            pre_segment = segments[i]
            post_segment = segments[i + 1]
            
            # 统计显著性检验
            try:
                t_stat, p_value = stats.ttest_ind(
                    pre_segment['glucose_data'], 
                    post_segment['glucose_data']
                )
                
                # 效应大小
                cohens_d = abs(pre_segment['mean_glucose'] - post_segment['mean_glucose']) / \
                          np.sqrt((pre_segment['glucose_std']**2 + post_segment['glucose_std']**2) / 2)
                
            except:
                t_stat, p_value, cohens_d = 0, 1, 0
            
            segment_comparison = {
                'pre_segment_id': pre_segment['segment_id'],
                'post_segment_id': post_segment['segment_id'],
                'mean_change': post_segment['mean_glucose'] - pre_segment['mean_glucose'],
                'cv_change': post_segment['cv'] - pre_segment['cv'],
                'range_change': post_segment['glucose_range'] - pre_segment['glucose_range'],
                'statistical_significance': p_value,
                'effect_size': cohens_d,
                'significant': p_value < 0.05 and cohens_d > 0.3,
                'improvement': {
                    'mean_closer_to_target': abs(post_segment['mean_glucose'] - 7.0) < abs(pre_segment['mean_glucose'] - 7.0),
                    'variability_decreased': post_segment['cv'] < pre_segment['cv'],
                    'range_decreased': post_segment['glucose_range'] < pre_segment['glucose_range']
                }
            }
            
            comparison['comparisons'].append(segment_comparison)
        
        # 整体评估
        overall_improvement = {
            'mean_improvement': sum(1 for c in comparison['comparisons'] if c['improvement']['mean_closer_to_target']),
            'variability_improvement': sum(1 for c in comparison['comparisons'] if c['improvement']['variability_decreased']),
            'range_improvement': sum(1 for c in comparison['comparisons'] if c['improvement']['range_decreased']),
            'significant_changes': sum(1 for c in comparison['comparisons'] if c['significant'])
        }
        
        comparison['overall_assessment'] = overall_improvement
        
        return comparison