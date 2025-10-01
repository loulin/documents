#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多维度CGMS异常检测系统
整合多种检测方法，全面识别传感器异常
"""

import numpy as np
import pandas as pd
from scipy import signal, stats
from scipy.fft import fft, fftfreq
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings

from config import Config  # 导入统一配置

warnings.filterwarnings('ignore')

class ComprehensiveCGMSAnomalyDetector:
    """综合CGMS异常检测器 - 多维度方法"""

    def __init__(self):
        self.methods = {
            'rate_based': True,      # 基于变化率（已有）
            'statistical': True,     # 统计学方法
            'pattern_based': True,   # 模式识别
            'frequency': True,       # 频域分析
            'ml_based': True,        # 机器学习
            'physiological': True,   # 生理学约束
            'temporal': True,        # 时间序列分析
            'context_aware': True    # 上下文感知
        }

    def method_1_statistical_outliers(self, glucose_data, contamination=0.1):
        """
        方法1：统计学异常检测
        """
        results = {
            'method': '统计学异常检测',
            'anomalies': [],
            'scores': [],
            'details': {}
        }

        glucose_array = np.array(glucose_data)

        # 1. Z-score检测
        z_scores = np.abs(stats.zscore(glucose_array))
        z_threshold = Config.Statistical.Z_SCORE_THRESHOLD
        z_anomalies = z_scores > z_threshold

        # 2. IQR方法
        Q1 = np.percentile(glucose_array, 25)
        Q3 = np.percentile(glucose_array, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - Config.Statistical.IQR_MULTIPLIER * IQR
        upper_bound = Q3 + Config.Statistical.IQR_MULTIPLIER * IQR
        iqr_anomalies = (glucose_array < lower_bound) | (glucose_array > upper_bound)

        # 3. 改进的Z-score (MAD - Median Absolute Deviation)
        median = np.median(glucose_array)
        mad = np.median(np.abs(glucose_array - median))
        mad_z_scores = 0.6745 * (glucose_array - median) / mad
        mad_threshold = Config.Statistical.MAD_THRESHOLD
        mad_anomalies = np.abs(mad_z_scores) > mad_threshold

        # 综合评分
        anomaly_indices = np.where(z_anomalies | iqr_anomalies | mad_anomalies)[0]

        results['anomalies'] = anomaly_indices.tolist()
        results['scores'] = z_scores.tolist()
        results['details'] = {
            'z_score_anomalies': np.sum(z_anomalies),
            'iqr_anomalies': np.sum(iqr_anomalies),
            'mad_anomalies': np.sum(mad_anomalies),
            'bounds': {'lower': lower_bound, 'upper': upper_bound},
            'mad_threshold': mad_threshold
        }

        return results

    def method_2_pattern_recognition(self, glucose_data, window_size=15):
        """
        方法2：模式识别异常检测
        """
        results = {
            'method': '模式识别异常检测',
            'anomalies': [],
            'patterns': {},
            'details': {}
        }

        glucose_array = np.array(glucose_data)
        anomaly_indices = set()

        # 1. 平台检测（平坦信号）
        flat_tolerance = Config.Pattern.FLAT_TOLERANCE
        flat_min_length = Config.Pattern.FLAT_MIN_LENGTH

        flat_segments = []
        current_flat_start = None

        for i in range(1, len(glucose_array)):
            if abs(glucose_array[i] - glucose_array[i-1]) < flat_tolerance:
                if current_flat_start is None:
                    current_flat_start = i-1
            else:
                if current_flat_start is not None:
                    length = i - current_flat_start
                    if length >= flat_min_length:
                        flat_segments.append((current_flat_start, i-1, length))
                        anomaly_indices.update(range(current_flat_start, i))
                    current_flat_start = None

        # 2. 锯齿模式检测（高频振荡）
        if len(glucose_array) > 10:
            second_diff = np.diff(glucose_array, n=2)
            oscillation_threshold = np.std(second_diff) * Config.Pattern.OSCILLATION_STD_MULTIPLIER
            oscillation_indices = np.where(np.abs(second_diff) > oscillation_threshold)[0] + 1
            anomaly_indices.update(oscillation_indices)

        # 3. 趋势突变检测
        if len(glucose_array) > window_size * 2:
            trend_changes = []
            for i in range(window_size, len(glucose_array) - window_size):
                before_trend = np.polyfit(range(window_size), glucose_array[i-window_size:i], 1)[0]
                after_trend = np.polyfit(range(window_size), glucose_array[i:i+window_size], 1)[0]

                trend_change = abs(after_trend - before_trend)
                if trend_change > Config.Pattern.TREND_CHANGE_THRESHOLD:
                    trend_changes.append(i)
                    anomaly_indices.add(i)

        # 4. 周期性异常检测
        if len(glucose_array) > 30:
            autocorr = np.correlate(glucose_array, glucose_array, mode='full')
            autocorr = autocorr[autocorr.size // 2:]

            peaks, _ = signal.find_peaks(autocorr[1:20], height=np.max(autocorr) * Config.Pattern.AUTOCORR_PEAK_HEIGHT_RATIO)
            if len(peaks) > Config.Pattern.AUTOCORR_MAX_PEAKS:
                anomaly_indices.update(peaks + len(glucose_array) // 2)

        results['anomalies'] = list(anomaly_indices)
        results['patterns'] = {
            'flat_segments': flat_segments,
            'trend_changes': len([i for i in anomaly_indices if i in trend_changes]) if 'trend_changes' in locals() else 0,
            'oscillations': len(oscillation_indices) if 'oscillation_indices' in locals() else 0
        }

        return results

    def method_3_frequency_analysis(self, glucose_data, sampling_rate=1/15):
        """
        方法3：频域分析异常检测
        """
        results = {
            'method': '频域分析异常检测',
            'anomalies': [],
            'frequency_features': {},
            'details': {}
        }

        glucose_array = np.array(glucose_data)
        n = len(glucose_array)

        if n < 10:
            return results

        fft_values = fft(glucose_array)
        frequencies = fftfreq(n, d=1/sampling_rate)
        psd = np.abs(fft_values)**2

        high_freq = frequencies >= 0.1
        total_energy = np.sum(psd)
        high_energy = np.sum(psd[high_freq])

        high_freq_ratio = high_energy / total_energy
        if high_freq_ratio > Config.Frequency.HIGH_FREQ_ENERGY_RATIO:
            window_size = 10
            for i in range(0, n - window_size, window_size//2):
                window_data = glucose_array[i:i+window_size]
                window_fft = fft(window_data)
                window_psd = np.abs(window_fft)**2
                window_high_energy = np.sum(window_psd[len(window_psd)//3:])
                window_total_energy = np.sum(window_psd)

                if window_total_energy > 0 and (window_high_energy / window_total_energy) > Config.Frequency.WINDOW_HIGH_FREQ_RATIO:
                    results['anomalies'].extend(range(i, min(i+window_size, n)))

        peak_indices = signal.find_peaks(psd[1:n//2], height=np.max(psd) * Config.Frequency.PEAK_HEIGHT_RATIO)[0]
        for peak_idx in peak_indices:
            freq = frequencies[peak_idx + 1]
            period_minutes = 1/freq if freq > 0 else float('inf')

            if Config.Frequency.PERIODIC_ANOMALY_MIN_MINUTES <= period_minutes <= Config.Frequency.PERIODIC_ANOMALY_MAX_MINUTES:
                period_samples = int(period_minutes * sampling_rate * 60)
                for i in range(0, n, period_samples):
                    if i < n:
                        results['anomalies'].append(i)

        results['anomalies'] = list(set(results['anomalies']))
        return results

    def method_4_machine_learning(self, glucose_data, contamination=Config.MachineLearning.CONTAMINATION):
        """
        方法4：机器学习异常检测
        """
        results = {
            'method': '机器学习异常检测',
            'anomalies': [],
            'scores': [],
            'features': {}
        }

        glucose_array = np.array(glucose_data)
        n = len(glucose_array)

        if n < 20:
            return results

        features = []
        for i in range(2, n-2):
            feature_vector = [
                glucose_array[i],
                glucose_array[i] - glucose_array[i-1],
                glucose_array[i-1] - 2*glucose_array[i] + glucose_array[i+1],
                np.mean(glucose_array[max(0, i-5):i+1]),
                np.std(glucose_array[max(0, i-5):i+1]),
                glucose_array[i] - np.mean(glucose_array[max(0, i-10):i+1]),
            ]
            features.append(feature_vector)

        features = np.array(features)
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        iso_forest = IsolationForest(contamination=contamination, random_state=Config.General.RANDOM_STATE)
        anomaly_labels = iso_forest.fit_predict(features_scaled)
        anomaly_indices = np.where(anomaly_labels == -1)[0] + 2

        results['anomalies'] = anomaly_indices.tolist()
        return results

    def method_5_physiological_constraints(self, glucose_data, timestamps=None):
        """
        方法5：生理学约束检验
        """
        results = {
            'method': '生理学约束检验',
            'anomalies': [],
            'violations': {},
            'details': {}
        }

        glucose_array = np.array(glucose_data)
        anomaly_indices = set()

        absolute_violations = np.where((glucose_array < Config.Physiological.ABSOLUTE_MIN_GLUCOSE) | 
                                     (glucose_array > Config.Physiological.ABSOLUTE_MAX_GLUCOSE))[0]
        extreme_violations = np.where((glucose_array < Config.Physiological.EXTREME_MIN_GLUCOSE) | 
                                    (glucose_array > Config.Physiological.EXTREME_MAX_GLUCOSE))[0]

        anomaly_indices.update(absolute_violations)
        anomaly_indices.update(extreme_violations)

        if len(glucose_array) > 1:
            time_intervals = np.ones(len(glucose_array)-1) * 15
            if timestamps is not None:
                time_intervals = [(timestamps[i+1] - timestamps[i]).total_seconds()/60 for i in range(len(timestamps)-1)]
            rates = np.diff(glucose_array) / time_intervals
            extreme_rate_violations = np.where(np.abs(rates) > Config.Physiological.EXTREME_RATE_OF_CHANGE)[0]
            anomaly_indices.update(extreme_rate_violations)

        if len(glucose_array) > 10:
            high_mask = glucose_array > Config.Physiological.SUSTAINED_HIGH_GLUCOSE
            high_segments = self._find_consecutive_segments(high_mask, min_length=Config.Physiological.SUSTAINED_HIGH_MIN_LENGTH)
            for start, end in high_segments:
                anomaly_indices.update(range(start, end+1))

            low_mask = glucose_array < Config.Physiological.SUSTAINED_LOW_GLUCOSE
            low_segments = self._find_consecutive_segments(low_mask, min_length=Config.Physiological.SUSTAINED_LOW_MIN_LENGTH)
            for start, end in low_segments:
                anomaly_indices.update(range(start, end+1))

        if len(glucose_array) > 20:
            unique_values, counts = np.unique(np.round(glucose_array, 1), return_counts=True)
            repeated_values = unique_values[counts > len(glucose_array) * Config.Physiological.REPEATED_VALUE_RATIO]
            for repeated_val in repeated_values:
                repeated_indices = np.where(np.abs(glucose_array - repeated_val) < 0.1)[0]
                if len(repeated_indices) > 5:
                    anomaly_indices.update(repeated_indices)

        results['anomalies'] = list(anomaly_indices)
        return results

    def _find_consecutive_segments(self, boolean_mask, min_length=3):
        """查找连续的True段落"""
        segments = []
        start = None
        for i, val in enumerate(boolean_mask):
            if val and start is None:
                start = i
            elif not val and start is not None:
                if i - start >= min_length:
                    segments.append((start, i-1))
                start = None
        if start is not None and len(boolean_mask) - start >= min_length:
            segments.append((start, len(boolean_mask)-1))
        return segments

    def method_6_temporal_analysis(self, glucose_data, timestamps=None):
        """
        方法6：时间序列分析

        时间相关异常检测：
        - 时间间隔异常
        - 时序预测偏差
        - 季节性异常
        """
        results = {
            'method': '时间序列分析',
            'anomalies': [],
            'temporal_features': {},
            'details': {}
        }

        glucose_array = np.array(glucose_data)
        anomaly_indices = set()

        # 1. 时间间隔异常
        if timestamps is not None:
            time_intervals = [(timestamps[i+1] - timestamps[i]).total_seconds()/60
                            for i in range(len(timestamps)-1)]

            for i, interval in enumerate(time_intervals):
                # 异常的时间间隔可能表示数据质量问题
                if not (Config.Temporal.MIN_INTERVAL_MINUTES <= interval <= Config.Temporal.MAX_INTERVAL_MINUTES):
                    anomaly_indices.add(i)
                    anomaly_indices.add(i+1)

        # 2. 简单时序预测偏差
        if len(glucose_array) > 10:
            # 使用移动平均作为简单预测
            window_size = 5
            for i in range(window_size, len(glucose_array)):
                predicted = np.mean(glucose_array[i-window_size:i])
                actual = glucose_array[i]
                prediction_error = abs(actual - predicted)

                # 如果预测误差过大，可能是异常
                if prediction_error > Config.Temporal.PREDICTION_ERROR_THRESHOLD:
                    anomaly_indices.add(i)

        # 3. 局部异常检测（基于局部密度）
        if len(glucose_array) > 15:
            window_size = 7
            for i in range(window_size, len(glucose_array) - window_size):
                local_window = glucose_array[i-window_size:i+window_size+1]
                center_value = glucose_array[i]

                # 计算局部统计
                local_mean = np.mean(local_window)
                local_std = np.std(local_window)

                if local_std > 0:
                    z_score = abs(center_value - local_mean) / local_std
                    if z_score > Config.Temporal.LOCAL_Z_SCORE_THRESHOLD:  # 局部异常
                        anomaly_indices.add(i)

        results['anomalies'] = list(anomaly_indices)
        results['temporal_features'] = {
            'time_interval_anomalies': len([i for i in anomaly_indices if i < len(glucose_array)-1]) if timestamps else 0,
            'prediction_anomalies': len(anomaly_indices),
        }

        return results

    def comprehensive_detection(self, glucose_data, timestamps=None, methods=None):
        """
        综合异常检测：整合所有方法
        """
        if methods is None:
            methods = self.methods

        print("🔍 开始综合异常检测...")
        print("=" * 50)

        all_results = {}
        all_anomalies = set()
        method_votes = {}

        # ... (method execution loop remains the same)

        if methods.get('statistical', True):
            print("📊 统计学异常检测...")
            result = self.method_1_statistical_outliers(glucose_data)
            all_results['statistical'] = result
            for idx in result['anomalies']:
                method_votes[idx] = method_votes.get(idx, 0) + 1
            all_anomalies.update(result['anomalies'])

        if methods.get('pattern_based', True):
            print("🔍 模式识别异常检测...")
            result = self.method_2_pattern_recognition(glucose_data)
            all_results['pattern_based'] = result
            for idx in result['anomalies']:
                method_votes[idx] = method_votes.get(idx, 0) + 1
            all_anomalies.update(result['anomalies'])

        if methods.get('frequency', True):
            print("📈 频域分析异常检测...")
            result = self.method_3_frequency_analysis(glucose_data)
            all_results['frequency'] = result
            for idx in result['anomalies']:
                method_votes[idx] = method_votes.get(idx, 0) + 1
            all_anomalies.update(result['anomalies'])

        if methods.get('ml_based', True):
            print("🤖 机器学习异常检测...")
            result = self.method_4_machine_learning(glucose_data)
            all_results['ml_based'] = result
            for idx in result['anomalies']:
                method_votes[idx] = method_votes.get(idx, 0) + 1
            all_anomalies.update(result['anomalies'])

        if methods.get('physiological', True):
            print("🧬 生理学约束检验...")
            result = self.method_5_physiological_constraints(glucose_data, timestamps)
            all_results['physiological'] = result
            for idx in result['anomalies']:
                method_votes[idx] = method_votes.get(idx, 0) + 1
            all_anomalies.update(result['anomalies'])

        if methods.get('temporal', True):
            print("⏰ 时间序列分析...")
            result = self.method_6_temporal_analysis(glucose_data, timestamps)
            all_results['temporal'] = result
            for idx in result['anomalies']:
                method_votes[idx] = method_votes.get(idx, 0) + 1
            all_anomalies.update(result['anomalies'])

        print("\n📊 综合结果分析...")

        sorted_anomalies = sorted(method_votes.items(), key=lambda x: x[1], reverse=True)

        high_confidence = [idx for idx, votes in sorted_anomalies if votes >= Config.Ensemble.HIGH_CONFIDENCE_VOTES]
        medium_confidence = [idx for idx, votes in sorted_anomalies if votes == Config.Ensemble.MEDIUM_CONFIDENCE_VOTES]
        low_confidence = [idx for idx, votes in sorted_anomalies if votes == 1]

        comprehensive_result = {
            'total_methods': len([k for k, v in methods.items() if v]),
            'all_anomalies': list(all_anomalies),
            'high_confidence_anomalies': high_confidence,
            'medium_confidence_anomalies': medium_confidence,
            'low_confidence_anomalies': low_confidence,
            'method_results': all_results,
            'voting_results': method_votes,
            'summary': {
                'total_anomalies': len(all_anomalies),
                'high_confidence_count': len(high_confidence),
                'medium_confidence_count': len(medium_confidence),
                'low_confidence_count': len(low_confidence)
            }
        }

        return comprehensive_result

if __name__ == "__main__":
    # The demonstration function can remain as is, or be updated to use Config as well.
    # For now, we focus on the core class logic.
    pass
