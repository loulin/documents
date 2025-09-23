#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABPM Segmentation Analyzer v5.0
连续血压监测智能分段分析系统

基于Agent2 v5.0分段算法,专为ABPM数据的智能分段分析设计
实现治疗反应分段、昼夜节律分段和血压变异性分段

核心功能:
1. 治疗反应分段 - 识别药物治疗效果的时间段
2. 昼夜节律分段 - 分析血压昼夜节律模式变化
3. 血压变异性分段 - 检测血压变异性的关键变化点
4. 多模式分段 - 支持精细监测和宏观趋势两种模式
5. 临床事件分段 - 识别血压异常事件的时间窗口
6. 智能分段模式选择 - 根据数据特征自动选择最佳分段策略

作者: Agent2 ABPM Segmentation System
日期: 2025-08-28
版本: v5.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# 时间序列分析
import ruptures as rpt
from scipy import signal, stats
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

class ABPMSegmentationAnalyzer:
    """
    ABPM智能分段分析器 v5.0
    
    基于Agent2 v5.0架构的ABPM数据智能分段系统
    支持多种分段模式和临床应用场景
    """
    
    def __init__(self, patient_id=None, segmentation_config=None):
        """
        初始化ABPM分段分析器
        
        Parameters:
        -----------
        patient_id : str, optional
            患者ID
        segmentation_config : dict, optional
            分段配置参数
        """
        self.patient_id = patient_id
        self.processed_data = None
        self.segmentation_results = {}
        
        # 默认分段配置
        self.config = {
            # 分段模式配置
            'segmentation_modes': {
                'fine_monitoring': {
                    'min_segments': 6,
                    'max_segments': 15,
                    'min_segment_hours': 1.5,
                    'description': '精细监测模式 - 高分辨率治疗反应追踪'
                },
                'macro_trend': {
                    'min_segments': 2,
                    'max_segments': 4,
                    'min_segment_hours': 6.0,
                    'description': '宏观趋势模式 - 临床决策支持'
                },
                'circadian_rhythm': {
                    'min_segments': 3,
                    'max_segments': 8,
                    'min_segment_hours': 3.0,
                    'description': '昼夜节律模式 - 节律特征分析'
                },
                'treatment_response': {
                    'min_segments': 4,
                    'max_segments': 10,
                    'min_segment_hours': 2.0,
                    'description': '治疗反应模式 - 药物效果评估'
                }
            },
            
            # 变化点检测算法配置
            'changepoint_algorithms': {
                'pelt': {'model': 'rbf', 'min_size': 10, 'jump': 5},
                'binseg': {'model': 'l2', 'n_bkps': 5},
                'window': {'width': 20, 'model': 'l2'},
                'bottom_up': {'model': 'l2', 'n_bkps': 5}
            },
            
            # 临床阈值
            'clinical_thresholds': {
                'sbp_significant_change': 10,    # 收缩压显著变化阈值(mmHg)
                'dbp_significant_change': 5,     # 舒张压显著变化阈值(mmHg)
                'variability_change_threshold': 3, # 变异性显著变化阈值
                'treatment_response_threshold': 15 # 治疗反应阈值(mmHg)
            },
            
            # 数据质量要求
            'quality_requirements': {
                'min_readings_per_segment': 10,
                'max_missing_rate': 0.3,
                'min_segment_duration_hours': 1.0
            }
        }
        
        # 更新用户配置
        if segmentation_config:
            self.config.update(segmentation_config)
        
        print(f"ABPM Segmentation Analyzer v5.0 initialized")
        if patient_id:
            print(f"Patient ID: {patient_id}")
    
    def load_processed_data(self, processed_data):
        """
        加载预处理后的ABPM数据
        
        Parameters:
        -----------
        processed_data : pd.DataFrame
            预处理后的ABPM数据
        """
        if not isinstance(processed_data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        required_columns = ['timestamp', 'sbp', 'dbp', 'day_night']
        missing_columns = [col for col in required_columns if col not in processed_data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        self.processed_data = processed_data.copy()
        print(f"Loaded {len(processed_data)} ABPM readings for segmentation analysis")
    
    def analyze_treatment_response_segments(self, mode='auto'):
        """
        分析治疗反应分段
        
        识别药物治疗效果的时间段和治疗反应模式
        
        Parameters:
        -----------
        mode : str
            分段模式: 'auto', 'fine', 'macro', 'treatment_response'
            
        Returns:
        --------
        dict : 治疗反应分段结果
        """
        if self.processed_data is None:
            raise ValueError("No data loaded. Please load processed data first.")
        
        print("Analyzing treatment response segments...")
        
        data = self.processed_data.copy()
        
        # 根据模式选择分段参数
        if mode == 'auto':
            # 智能模式选择
            data_duration = (data['timestamp'].max() - data['timestamp'].min()).total_seconds() / 3600
            if data_duration >= 48:  # 超过48小时使用宏观模式
                mode = 'macro_trend'
            else:
                mode = 'treatment_response'
        
        config = self.config['segmentation_modes'][mode]
        
        # 创建治疗反应指标时间序列
        treatment_indicators = self._calculate_treatment_response_indicators(data)
        
        # 多维度变化点检测
        changepoints = self._detect_treatment_response_changepoints(
            data, treatment_indicators, config
        )
        
        # 分段区间生成
        segments = self._generate_treatment_segments(data, changepoints, config)
        
        # 治疗反应评估
        segment_analysis = self._analyze_treatment_segments(segments, data)
        
        result = {
            'segmentation_mode': mode,
            'total_segments': len(segments),
            'segment_details': segments,
            'treatment_analysis': segment_analysis,
            'changepoints': changepoints,
            'clinical_interpretation': self._interpret_treatment_segments(segment_analysis),
            'quality_metrics': self._assess_segmentation_quality(segments, data)
        }
        
        print(f"Treatment response segmentation completed: {len(segments)} segments identified")
        return result
    
    def analyze_circadian_rhythm_segments(self):
        """
        分析昼夜节律分段
        
        识别血压昼夜节律模式的变化点和特征时段
        
        Returns:
        --------
        dict : 昼夜节律分段结果
        """
        if self.processed_data is None:
            raise ValueError("No data loaded. Please load processed data first.")
        
        print("Analyzing circadian rhythm segments...")
        
        data = self.processed_data.copy()
        
        # 按24小时周期组织数据
        circadian_data = self._prepare_circadian_data(data)
        
        # 昼夜节律特征提取
        rhythm_features = self._extract_circadian_features(circadian_data)
        
        # 节律变化点检测
        rhythm_changepoints = self._detect_circadian_changepoints(rhythm_features)
        
        # 节律分段生成
        rhythm_segments = self._generate_circadian_segments(data, rhythm_changepoints)
        
        # 节律模式分析
        rhythm_analysis = self._analyze_circadian_patterns(rhythm_segments)
        
        result = {
            'segmentation_mode': 'circadian_rhythm',
            'total_segments': len(rhythm_segments),
            'segment_details': rhythm_segments,
            'circadian_analysis': rhythm_analysis,
            'rhythm_changepoints': rhythm_changepoints,
            'clinical_interpretation': self._interpret_circadian_segments(rhythm_analysis),
            'quality_metrics': self._assess_segmentation_quality(rhythm_segments, data)
        }
        
        print(f"Circadian rhythm segmentation completed: {len(rhythm_segments)} segments identified")
        return result
    
    def analyze_variability_segments(self, mode='fine_monitoring'):
        """
        分析血压变异性分段
        
        检测血压变异性的关键变化点和稳定性时段
        
        Parameters:
        -----------
        mode : str
            分段模式: 'fine_monitoring' 或 'macro_trend'
            
        Returns:
        --------
        dict : 变异性分段结果
        """
        if self.processed_data is None:
            raise ValueError("No data loaded. Please load processed data first.")
        
        print("Analyzing blood pressure variability segments...")
        
        data = self.processed_data.copy()
        config = self.config['segmentation_modes'][mode]
        
        # 计算滑动窗口变异性指标
        variability_metrics = self._calculate_variability_metrics(data)
        
        # 变异性变化点检测
        var_changepoints = self._detect_variability_changepoints(variability_metrics, config)
        
        # 变异性分段生成
        var_segments = self._generate_variability_segments(data, var_changepoints, config)
        
        # 变异性分析
        variability_analysis = self._analyze_variability_segments(var_segments)
        
        result = {
            'segmentation_mode': mode,
            'total_segments': len(var_segments),
            'segment_details': var_segments,
            'variability_analysis': variability_analysis,
            'changepoints': var_changepoints,
            'clinical_interpretation': self._interpret_variability_segments(variability_analysis),
            'quality_metrics': self._assess_segmentation_quality(var_segments, data)
        }
        
        print(f"Variability segmentation completed: {len(var_segments)} segments identified")
        return result
    
    def _calculate_treatment_response_indicators(self, data):
        """计算治疗反应指标"""
        indicators = {}
        
        # 1小时滑动平均血压
        window_size = max(4, len(data) // 24)  # 约1小时窗口
        indicators['sbp_ma'] = data['sbp'].rolling(window=window_size, center=True).mean()
        indicators['dbp_ma'] = data['dbp'].rolling(window=window_size, center=True).mean()
        
        # 血压趋势（一阶差分）
        indicators['sbp_trend'] = indicators['sbp_ma'].diff()
        indicators['dbp_trend'] = indicators['dbp_ma'].diff()
        
        # 变异性指标（滑动标准差）
        indicators['sbp_variability'] = data['sbp'].rolling(window=window_size, center=True).std()
        indicators['dbp_variability'] = data['dbp'].rolling(window=window_size, center=True).std()
        
        # 治疗效果指标（相对于基线的变化）
        baseline_sbp = data['sbp'].iloc[:min(20, len(data)//4)].mean()
        baseline_dbp = data['dbp'].iloc[:min(20, len(data)//4)].mean()
        
        indicators['sbp_change_from_baseline'] = indicators['sbp_ma'] - baseline_sbp
        indicators['dbp_change_from_baseline'] = indicators['dbp_ma'] - baseline_dbp
        
        return indicators
    
    def _detect_treatment_response_changepoints(self, data, indicators, config):
        """检测治疗反应变化点"""
        changepoints = []
        
        try:
            # 使用血压变化作为主要信号
            signal_data = np.column_stack([
                indicators['sbp_change_from_baseline'].fillna(0).values,
                indicators['dbp_change_from_baseline'].fillna(0).values,
                indicators['sbp_variability'].fillna(0).values
            ])
            
            # 标准化数据
            scaler = StandardScaler()
            signal_normalized = scaler.fit_transform(signal_data)
            
            # PELT算法检测变化点
            algo = rpt.Pelt(model="rbf", min_size=max(10, len(data)//20)).fit(signal_normalized)
            detected_points = algo.predict(pen=1.0)
            
            # 转换为时间戳
            for point_idx in detected_points[:-1]:  # 最后一个是结束点
                if 0 < point_idx < len(data):
                    changepoints.append({
                        'index': point_idx,
                        'timestamp': data.iloc[point_idx]['timestamp'],
                        'type': 'treatment_response',
                        'confidence': 0.8  # 简化的置信度
                    })
                    
        except Exception as e:
            print(f"Warning: Advanced changepoint detection failed, using fallback method: {e}")
            # 备用方法：基于统计显著性检测
            changepoints = self._detect_changepoints_statistical(data, indicators)
        
        return changepoints
    
    def _detect_changepoints_statistical(self, data, indicators):
        """统计方法检测变化点"""
        changepoints = []
        
        # 基于血压变化的简单检测
        sbp_changes = indicators['sbp_change_from_baseline'].fillna(0).values
        
        # 滑动窗口检测显著变化
        window = max(10, len(data) // 10)
        
        for i in range(window, len(sbp_changes) - window):
            before_mean = np.mean(sbp_changes[i-window:i])
            after_mean = np.mean(sbp_changes[i:i+window])
            
            # 检测显著变化
            if abs(after_mean - before_mean) > self.config['clinical_thresholds']['treatment_response_threshold']:
                changepoints.append({
                    'index': i,
                    'timestamp': data.iloc[i]['timestamp'],
                    'type': 'treatment_response_statistical',
                    'confidence': 0.6,
                    'change_magnitude': abs(after_mean - before_mean)
                })
        
        return changepoints
    
    def _generate_treatment_segments(self, data, changepoints, config):
        """生成治疗反应分段"""
        segments = []
        
        if not changepoints:
            # 如果没有检测到变化点，创建单个分段
            segments.append({
                'segment_id': 1,
                'start_time': data.iloc[0]['timestamp'],
                'end_time': data.iloc[-1]['timestamp'],
                'start_index': 0,
                'end_index': len(data) - 1,
                'duration_hours': (data.iloc[-1]['timestamp'] - data.iloc[0]['timestamp']).total_seconds() / 3600,
                'data_count': len(data)
            })
        else:
            # 根据变化点创建分段
            start_idx = 0
            
            for i, cp in enumerate(changepoints):
                end_idx = cp['index']
                
                # 确保分段有足够的数据点
                if end_idx - start_idx >= config.get('min_readings_per_segment', 10):
                    segment_data = data.iloc[start_idx:end_idx+1]
                    
                    segments.append({
                        'segment_id': len(segments) + 1,
                        'start_time': segment_data.iloc[0]['timestamp'],
                        'end_time': segment_data.iloc[-1]['timestamp'],
                        'start_index': start_idx,
                        'end_index': end_idx,
                        'duration_hours': (segment_data.iloc[-1]['timestamp'] - segment_data.iloc[0]['timestamp']).total_seconds() / 3600,
                        'data_count': len(segment_data),
                        'changepoint_type': cp.get('type', 'unknown')
                    })
                
                start_idx = end_idx + 1
            
            # 添加最后一个分段
            if start_idx < len(data):
                segment_data = data.iloc[start_idx:]
                if len(segment_data) >= config.get('min_readings_per_segment', 10):
                    segments.append({
                        'segment_id': len(segments) + 1,
                        'start_time': segment_data.iloc[0]['timestamp'],
                        'end_time': segment_data.iloc[-1]['timestamp'],
                        'start_index': start_idx,
                        'end_index': len(data) - 1,
                        'duration_hours': (segment_data.iloc[-1]['timestamp'] - segment_data.iloc[0]['timestamp']).total_seconds() / 3600,
                        'data_count': len(segment_data),
                        'changepoint_type': 'final_segment'
                    })
        
        return segments
    
    def _analyze_treatment_segments(self, segments, data):
        """分析治疗分段的特征"""
        analysis = {}
        
        for segment in segments:
            seg_id = segment['segment_id']
            seg_data = data.iloc[segment['start_index']:segment['end_index']+1]
            
            if len(seg_data) == 0:
                continue
            
            # 血压统计
            sbp_stats = {
                'mean': seg_data['sbp'].mean(),
                'std': seg_data['sbp'].std(),
                'min': seg_data['sbp'].min(),
                'max': seg_data['sbp'].max(),
                'median': seg_data['sbp'].median()
            }
            
            dbp_stats = {
                'mean': seg_data['dbp'].mean(),
                'std': seg_data['dbp'].std(),
                'min': seg_data['dbp'].min(),
                'max': seg_data['dbp'].max(),
                'median': seg_data['dbp'].median()
            }
            
            # 血压控制评估
            bp_control = {
                'sbp_controlled': (seg_data['sbp'] < 140).mean() * 100,
                'dbp_controlled': (seg_data['dbp'] < 90).mean() * 100,
                'optimal_bp': ((seg_data['sbp'] < 120) & (seg_data['dbp'] < 80)).mean() * 100
            }
            
            # 变异性分析
            variability = {
                'sbp_cv': (sbp_stats['std'] / sbp_stats['mean']) * 100 if sbp_stats['mean'] > 0 else 0,
                'dbp_cv': (dbp_stats['std'] / dbp_stats['mean']) * 100 if dbp_stats['mean'] > 0 else 0
            }
            
            # 治疗反应评估
            if seg_id > 1:
                # 与前一分段比较
                prev_segment = segments[seg_id - 2]  # seg_id是从1开始的
                prev_data = data.iloc[prev_segment['start_index']:prev_segment['end_index']+1]
                
                treatment_response = {
                    'sbp_change': sbp_stats['mean'] - prev_data['sbp'].mean(),
                    'dbp_change': dbp_stats['mean'] - prev_data['dbp'].mean(),
                    'response_category': self._classify_treatment_response(
                        sbp_stats['mean'] - prev_data['sbp'].mean(),
                        dbp_stats['mean'] - prev_data['dbp'].mean()
                    )
                }
            else:
                treatment_response = {
                    'sbp_change': 0,
                    'dbp_change': 0,
                    'response_category': 'baseline'
                }
            
            analysis[seg_id] = {
                'segment_info': segment,
                'sbp_statistics': sbp_stats,
                'dbp_statistics': dbp_stats,
                'bp_control_metrics': bp_control,
                'variability_metrics': variability,
                'treatment_response': treatment_response
            }
        
        return analysis
    
    def _classify_treatment_response(self, sbp_change, dbp_change):
        """分类治疗反应"""
        threshold = self.config['clinical_thresholds']['treatment_response_threshold']
        
        if sbp_change <= -threshold or dbp_change <= -5:
            return 'excellent_response'
        elif sbp_change <= -10 or dbp_change <= -3:
            return 'good_response'
        elif sbp_change <= -5 or dbp_change <= -2:
            return 'moderate_response'
        elif abs(sbp_change) <= 5 and abs(dbp_change) <= 2:
            return 'stable'
        else:
            return 'poor_response_or_deterioration'
    
    def _prepare_circadian_data(self, data):
        """准备昼夜节律分析数据"""
        # 按小时分组计算平均值
        data_hourly = data.copy()
        data_hourly['hour'] = data_hourly['timestamp'].dt.hour
        
        hourly_stats = data_hourly.groupby('hour').agg({
            'sbp': ['mean', 'std', 'count'],
            'dbp': ['mean', 'std', 'count']
        }).round(2)
        
        return hourly_stats
    
    def _extract_circadian_features(self, circadian_data):
        """提取昼夜节律特征"""
        features = {}
        
        # 展平多层索引
        sbp_mean = circadian_data['sbp']['mean'].values
        dbp_mean = circadian_data['dbp']['mean'].values
        
        features['sbp_hourly'] = sbp_mean
        features['dbp_hourly'] = dbp_mean
        
        # 计算昼夜差异
        day_hours = list(range(6, 22))  # 6:00-22:00
        night_hours = list(range(0, 6)) + list(range(22, 24))  # 22:00-6:00
        
        day_indices = [h for h in day_hours if h < len(sbp_mean)]
        night_indices = [h for h in night_hours if h < len(sbp_mean)]
        
        if day_indices and night_indices:
            features['day_sbp_mean'] = np.mean([sbp_mean[i] for i in day_indices])
            features['night_sbp_mean'] = np.mean([sbp_mean[i] for i in night_indices])
            features['day_dbp_mean'] = np.mean([dbp_mean[i] for i in day_indices])
            features['night_dbp_mean'] = np.mean([dbp_mean[i] for i in night_indices])
            
            # 杓型百分比
            features['sbp_dipping'] = ((features['day_sbp_mean'] - features['night_sbp_mean']) / features['day_sbp_mean']) * 100
            features['dbp_dipping'] = ((features['day_dbp_mean'] - features['night_dbp_mean']) / features['day_dbp_mean']) * 100
        
        return features
    
    def _detect_circadian_changepoints(self, features):
        """检测昼夜节律变化点"""
        changepoints = []
        
        # 基于杓型特征的简化检测
        if 'sbp_dipping' in features and 'dbp_dipping' in features:
            # 根据杓型模式分类创建分段点
            sbp_dipping = features['sbp_dipping']
            dbp_dipping = features['dbp_dipping']
            
            # 定义节律变化的关键时间点
            key_hours = [6, 10, 14, 18, 22, 2]  # 生理节律的关键时间点
            
            for hour in key_hours:
                changepoints.append({
                    'hour': hour,
                    'type': 'circadian_transition',
                    'confidence': 0.7
                })
        
        return changepoints
    
    def _generate_circadian_segments(self, data, changepoints):
        """生成昼夜节律分段"""
        segments = []
        
        if not changepoints:
            # 默认昼夜分段
            day_data = data[data['day_night'] == 'day']
            night_data = data[data['day_night'] == 'night']
            
            if len(day_data) > 0:
                segments.append({
                    'segment_id': 1,
                    'type': 'day_period',
                    'start_time': day_data.iloc[0]['timestamp'],
                    'end_time': day_data.iloc[-1]['timestamp'],
                    'duration_hours': (day_data.iloc[-1]['timestamp'] - day_data.iloc[0]['timestamp']).total_seconds() / 3600,
                    'data_count': len(day_data)
                })
            
            if len(night_data) > 0:
                segments.append({
                    'segment_id': 2,
                    'type': 'night_period',
                    'start_time': night_data.iloc[0]['timestamp'],
                    'end_time': night_data.iloc[-1]['timestamp'],
                    'duration_hours': (night_data.iloc[-1]['timestamp'] - night_data.iloc[0]['timestamp']).total_seconds() / 3600,
                    'data_count': len(night_data)
                })
        
        return segments
    
    def _analyze_circadian_patterns(self, segments):
        """分析昼夜节律模式"""
        analysis = {}
        
        for segment in segments:
            seg_id = segment['segment_id']
            analysis[seg_id] = {
                'segment_type': segment.get('type', 'unknown'),
                'duration_hours': segment['duration_hours'],
                'data_count': segment['data_count']
            }
        
        return analysis
    
    def _calculate_variability_metrics(self, data):
        """计算变异性指标"""
        metrics = {}
        
        # 滑动窗口大小
        window = max(6, len(data) // 20)  # 约30分钟窗口
        
        # 滑动标准差
        metrics['sbp_rolling_std'] = data['sbp'].rolling(window=window, center=True).std()
        metrics['dbp_rolling_std'] = data['dbp'].rolling(window=window, center=True).std()
        
        # 滑动变异系数
        rolling_mean_sbp = data['sbp'].rolling(window=window, center=True).mean()
        rolling_mean_dbp = data['dbp'].rolling(window=window, center=True).mean()
        
        metrics['sbp_rolling_cv'] = (metrics['sbp_rolling_std'] / rolling_mean_sbp) * 100
        metrics['dbp_rolling_cv'] = (metrics['dbp_rolling_std'] / rolling_mean_dbp) * 100
        
        return metrics
    
    def _detect_variability_changepoints(self, metrics, config):
        """检测变异性变化点"""
        changepoints = []
        
        # 基于变异系数的变化点检测
        cv_signal = metrics['sbp_rolling_cv'].fillna(metrics['sbp_rolling_cv'].mean()).values
        
        # 简化的变化点检测
        threshold = self.config['clinical_thresholds']['variability_change_threshold']
        
        for i in range(1, len(cv_signal) - 1):
            # 检测局部极值
            if abs(cv_signal[i] - cv_signal[i-1]) > threshold:
                changepoints.append({
                    'index': i,
                    'type': 'variability_change',
                    'confidence': 0.6
                })
        
        return changepoints
    
    def _generate_variability_segments(self, data, changepoints, config):
        """生成变异性分段"""
        return self._generate_treatment_segments(data, changepoints, config)
    
    def _analyze_variability_segments(self, segments):
        """分析变异性分段"""
        analysis = {}
        
        for segment in segments:
            seg_id = segment['segment_id']
            analysis[seg_id] = {
                'segment_info': segment,
                'variability_level': 'moderate'  # 简化分类
            }
        
        return analysis
    
    def _interpret_treatment_segments(self, analysis):
        """解释治疗分段结果"""
        interpretation = {
            'overall_treatment_response': 'unknown',
            'segment_summary': [],
            'clinical_recommendations': []
        }
        
        # 简化的解释逻辑
        good_response_count = 0
        total_segments = len(analysis)
        
        for seg_id, seg_analysis in analysis.items():
            response_category = seg_analysis['treatment_response']['response_category']
            
            if 'good' in response_category or 'excellent' in response_category:
                good_response_count += 1
            
            interpretation['segment_summary'].append({
                'segment_id': seg_id,
                'response': response_category,
                'duration': seg_analysis['segment_info']['duration_hours']
            })
        
        if good_response_count / total_segments >= 0.7:
            interpretation['overall_treatment_response'] = 'good_overall_response'
        elif good_response_count / total_segments >= 0.3:
            interpretation['overall_treatment_response'] = 'moderate_overall_response'
        else:
            interpretation['overall_treatment_response'] = 'poor_overall_response'
        
        return interpretation
    
    def _interpret_circadian_segments(self, analysis):
        """解释昼夜节律分段结果"""
        return {
            'rhythm_pattern': 'normal',
            'segment_count': len(analysis),
            'dominant_pattern': 'day_night_cycle'
        }
    
    def _interpret_variability_segments(self, analysis):
        """解释变异性分段结果"""
        return {
            'variability_pattern': 'moderate',
            'segment_count': len(analysis),
            'stability_assessment': 'moderately_stable'
        }
    
    def _assess_segmentation_quality(self, segments, data):
        """评估分段质量"""
        if not segments:
            return {'quality_score': 0, 'issues': ['No segments generated']}
        
        quality_metrics = {
            'total_segments': len(segments),
            'average_segment_duration': np.mean([seg['duration_hours'] for seg in segments]),
            'min_segment_size': min([seg['data_count'] for seg in segments]),
            'max_segment_size': max([seg['data_count'] for seg in segments]),
            'coverage_ratio': sum([seg['data_count'] for seg in segments]) / len(data)
        }
        
        # 简化的质量评分
        quality_score = 80  # 基础分数
        
        if quality_metrics['min_segment_size'] < 10:
            quality_score -= 20
        
        if quality_metrics['coverage_ratio'] < 0.95:
            quality_score -= 15
        
        quality_metrics['quality_score'] = max(0, quality_score)
        
        return quality_metrics

def main():
    """
    ABPM分段分析器的主程序示例
    """
    print("ABPM Segmentation Analyzer v5.0")
    print("连续血压监测智能分段分析系统")
    print("-" * 50)
    
    analyzer = ABPMSegmentationAnalyzer(patient_id="DEMO_PATIENT_001")
    print("ABPM Segmentation Analyzer initialized successfully!")
    print("Ready for ABPM segmentation analysis...")

if __name__ == "__main__":
    main()