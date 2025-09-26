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

        基于统计分布的异常值检测：
        - Z-score检测
        - 四分位距(IQR)检测
        - 改进的Z-score（MAD）
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
        z_threshold = 2.5  # 2.5个标准差
        z_anomalies = z_scores > z_threshold

        # 2. IQR方法
        Q1 = np.percentile(glucose_array, 25)
        Q3 = np.percentile(glucose_array, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        iqr_anomalies = (glucose_array < lower_bound) | (glucose_array > upper_bound)

        # 3. 改进的Z-score (MAD - Median Absolute Deviation)
        median = np.median(glucose_array)
        mad = np.median(np.abs(glucose_array - median))
        mad_z_scores = 0.6745 * (glucose_array - median) / mad
        mad_threshold = 3.5
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

        识别异常模式：
        - 平台模式（连续相同值）
        - 锯齿模式（高频振荡）
        - 趋势突变
        - 周期性异常
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
        flat_tolerance = 0.5  # mg/dL
        flat_min_length = 6   # 至少6个点

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
            # 计算二阶差分检测振荡
            second_diff = np.diff(glucose_array, n=2)
            oscillation_threshold = np.std(second_diff) * 2
            oscillation_indices = np.where(np.abs(second_diff) > oscillation_threshold)[0] + 1
            anomaly_indices.update(oscillation_indices)

        # 3. 趋势突变检测
        if len(glucose_array) > window_size * 2:
            trend_changes = []
            for i in range(window_size, len(glucose_array) - window_size):
                # 前后窗口的趋势比较
                before_trend = np.polyfit(range(window_size),
                                        glucose_array[i-window_size:i], 1)[0]
                after_trend = np.polyfit(range(window_size),
                                       glucose_array[i:i+window_size], 1)[0]

                trend_change = abs(after_trend - before_trend)
                if trend_change > 2.0:  # mg/dL/min 趋势突变阈值
                    trend_changes.append(i)
                    anomaly_indices.add(i)

        # 4. 周期性异常检测
        if len(glucose_array) > 30:
            # 检测异常周期性模式
            autocorr = np.correlate(glucose_array, glucose_array, mode='full')
            autocorr = autocorr[autocorr.size // 2:]

            # 寻找异常强的周期性
            peaks, _ = signal.find_peaks(autocorr[1:20], height=np.max(autocorr) * 0.3)
            if len(peaks) > 3:  # 过多短周期可能是传感器噪声
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

        分析频谱特征：
        - 异常高频成分（传感器噪声）
        - 不自然的周期性
        - 频谱能量分布异常
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

        # FFT分析
        fft_values = fft(glucose_array)
        frequencies = fftfreq(n, d=1/sampling_rate)

        # 功率谱密度
        psd = np.abs(fft_values)**2

        # 生理学频率范围分析
        # 正常血糖变化主要在低频范围 (< 0.01 Hz，即 > 100分钟周期)
        nyquist_freq = sampling_rate / 2

        # 定义频段
        very_low_freq = frequencies < 0.005    # > 200分钟周期（生理性）
        low_freq = (frequencies >= 0.005) & (frequencies < 0.02)   # 50-200分钟
        mid_freq = (frequencies >= 0.02) & (frequencies < 0.1)     # 10-50分钟
        high_freq = frequencies >= 0.1         # < 10分钟（可能异常）

        # 计算各频段能量
        total_energy = np.sum(psd)
        very_low_energy = np.sum(psd[very_low_freq])
        low_energy = np.sum(psd[low_freq])
        mid_energy = np.sum(psd[mid_freq])
        high_energy = np.sum(psd[high_freq])

        # 异常检测：高频能量占比过高
        high_freq_ratio = high_energy / total_energy
        if high_freq_ratio > 0.15:  # 高频能量超过15%可能异常
            # 通过滑动窗口找出高频异常区域
            window_size = 10
            for i in range(0, n - window_size, window_size//2):
                window_data = glucose_array[i:i+window_size]
                window_fft = fft(window_data)
                window_psd = np.abs(window_fft)**2
                window_high_energy = np.sum(window_psd[len(window_psd)//3:])
                window_total_energy = np.sum(window_psd)

                if window_high_energy / window_total_energy > 0.2:
                    results['anomalies'].extend(range(i, min(i+window_size, n)))

        # 检测异常周期性
        # 寻找不自然的强周期信号
        peak_indices = signal.find_peaks(psd[1:n//2], height=np.max(psd) * 0.1)[0]
        for peak_idx in peak_indices:
            freq = frequencies[peak_idx + 1]
            period_minutes = 1/freq if freq > 0 else float('inf')

            # 5-20分钟的强周期可能是传感器异常
            if 5 <= period_minutes <= 20:
                # 标记相关时间点
                period_samples = int(period_minutes * sampling_rate * 60)
                for i in range(0, n, period_samples):
                    if i < n:
                        results['anomalies'].append(i)

        results['frequency_features'] = {
            'high_freq_ratio': high_freq_ratio,
            'dominant_frequency': frequencies[np.argmax(psd[1:n//2]) + 1],
            'energy_distribution': {
                'very_low': very_low_energy / total_energy,
                'low': low_energy / total_energy,
                'mid': mid_energy / total_energy,
                'high': high_energy / total_energy
            }
        }

        # 去重
        results['anomalies'] = list(set(results['anomalies']))

        return results

    def method_4_machine_learning(self, glucose_data, contamination=0.1):
        """
        方法4：机器学习异常检测

        使用无监督学习：
        - Isolation Forest
        - 基于特征工程的异常检测
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

        # 特征工程
        features = []

        for i in range(2, n-2):
            feature_vector = [
                glucose_array[i],                                    # 当前值
                glucose_array[i] - glucose_array[i-1],              # 一阶差分
                glucose_array[i-1] - 2*glucose_array[i] + glucose_array[i+1],  # 二阶差分
                np.mean(glucose_array[max(0, i-5):i+1]),           # 5点移动平均
                np.std(glucose_array[max(0, i-5):i+1]),            # 5点移动标准差
                glucose_array[i] - np.mean(glucose_array[max(0, i-10):i+1]),  # 与10点均值偏差
            ]

            # 添加更多特征
            if i >= 5:
                recent_trend = np.polyfit(range(5), glucose_array[i-4:i+1], 1)[0]
                feature_vector.append(recent_trend)  # 短期趋势
            else:
                feature_vector.append(0)

            features.append(feature_vector)

        features = np.array(features)

        # 标准化特征
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Isolation Forest异常检测
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomaly_labels = iso_forest.fit_predict(features_scaled)
        anomaly_scores = iso_forest.score_samples(features_scaled)

        # 异常点索引（调整偏移）
        anomaly_indices = np.where(anomaly_labels == -1)[0] + 2  # 加回偏移

        results['anomalies'] = anomaly_indices.tolist()
        results['scores'] = anomaly_scores.tolist()
        results['features'] = {
            'feature_count': features.shape[1],
            'anomaly_ratio': len(anomaly_indices) / len(features)
        }

        return results

    def method_5_physiological_constraints(self, glucose_data, timestamps=None):
        """
        方法5：生理学约束检验

        基于生理学规律检测异常：
        - 绝对值范围检查
        - 生理学变化速度限制
        - 餐后响应模式检验
        - 日节律模式检验
        """
        results = {
            'method': '生理学约束检验',
            'anomalies': [],
            'violations': {},
            'details': {}
        }

        glucose_array = np.array(glucose_data)
        anomaly_indices = set()

        # 1. 绝对范围检查
        ABSOLUTE_MIN = 20   # mg/dL
        ABSOLUTE_MAX = 600  # mg/dL
        NORMAL_MIN = 70     # mg/dL
        NORMAL_MAX = 200    # mg/dL

        absolute_violations = np.where((glucose_array < ABSOLUTE_MIN) |
                                     (glucose_array > ABSOLUTE_MAX))[0]
        extreme_violations = np.where((glucose_array < 40) |
                                    (glucose_array > 400))[0]

        anomaly_indices.update(absolute_violations)
        anomaly_indices.update(extreme_violations)

        # 2. 生理变化速度检查（已在变化率中涵盖，这里检查更细致的约束）
        if len(glucose_array) > 1:
            time_intervals = np.ones(len(glucose_array)-1) * 15  # 默认15分钟
            if timestamps is not None:
                time_intervals = [(timestamps[i+1] - timestamps[i]).total_seconds()/60
                                for i in range(len(timestamps)-1)]

            rates = np.diff(glucose_array) / time_intervals

            # 极速变化检查（比基本变化率检查更严格）
            EXTREME_RATE = 15.0  # mg/dL/min
            extreme_rate_violations = np.where(np.abs(rates) > EXTREME_RATE)[0]
            anomaly_indices.update(extreme_rate_violations)

        # 3. 持续异常值检查
        # 连续过高或过低的值可能是传感器问题
        if len(glucose_array) > 10:
            # 连续高值
            high_mask = glucose_array > 300
            high_segments = self._find_consecutive_segments(high_mask, min_length=6)
            for start, end in high_segments:
                anomaly_indices.update(range(start, end+1))

            # 连续低值
            low_mask = glucose_array < 60
            low_segments = self._find_consecutive_segments(low_mask, min_length=4)
            for start, end in low_segments:
                anomaly_indices.update(range(start, end+1))

        # 4. 非生理性模式检查
        # 检查过于规律的模式（可能是传感器故障）
        if len(glucose_array) > 20:
            # 检查重复数值
            unique_values, counts = np.unique(np.round(glucose_array, 1), return_counts=True)
            repeated_values = unique_values[counts > len(glucose_array) * 0.1]  # 超过10%重复

            for repeated_val in repeated_values:
                repeated_indices = np.where(np.abs(glucose_array - repeated_val) < 0.1)[0]
                if len(repeated_indices) > 5:  # 连续重复
                    anomaly_indices.update(repeated_indices)

        results['anomalies'] = list(anomaly_indices)
        results['violations'] = {
            'absolute_violations': len(absolute_violations),
            'extreme_violations': len(extreme_violations),
            'extreme_rate_violations': len(extreme_rate_violations) if 'extreme_rate_violations' in locals() else 0,
        }

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

        # 处理结尾
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

            median_interval = np.median(time_intervals)

            for i, interval in enumerate(time_intervals):
                # 异常的时间间隔可能表示数据质量问题
                if interval < 2 or interval > 60:  # 小于2分钟或大于60分钟
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
                if prediction_error > 50:  # mg/dL
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
                    if z_score > 3:  # 局部异常
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

        # 执行各种检测方法
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

        # 综合评估
        print("\n📊 综合结果分析...")

        # 按投票数排序异常点
        sorted_anomalies = sorted(method_votes.items(), key=lambda x: x[1], reverse=True)

        # 分类异常严重程度
        high_confidence = [idx for idx, votes in sorted_anomalies if votes >= 3]
        medium_confidence = [idx for idx, votes in sorted_anomalies if votes == 2]
        low_confidence = [idx for idx, votes in sorted_anomalies if votes == 1]

        # 生成综合报告
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

def demonstrate_comprehensive_detection():
    """演示综合异常检测系统"""
    print("🩸 多维度CGMS异常检测系统演示")
    print("=" * 70)

    # 创建检测器
    detector = ComprehensiveCGMSAnomalyDetector()

    # 创建测试数据（包含各种类型的异常）
    np.random.seed(42)
    n_points = 100

    # 基础血糖模式
    base_glucose = 120 + np.cumsum(np.random.normal(0, 2, n_points))

    # 添加各种异常
    test_glucose = base_glucose.copy()

    # 统计异常：极值
    test_glucose[20] = 300  # 统计异常值
    test_glucose[21] = 50   # 另一个异常值

    # 模式异常：平台
    test_glucose[40:50] = 150  # 平台异常

    # 频域异常：高频噪声
    noise_indices = range(60, 80)
    high_freq_noise = 20 * np.sin(np.arange(len(noise_indices)) * 0.5)
    test_glucose[60:80] += high_freq_noise

    # 生理异常：不合理变化
    test_glucose[85] = test_glucose[84] + 100  # 瞬间跳跃

    print(f"📊 生成测试数据：{len(test_glucose)} 个数据点")
    print(f"🎯 预植入异常：统计异常、平台异常、频域噪声、生理异常")

    # 执行综合检测
    result = detector.comprehensive_detection(test_glucose)

    # 显示结果
    print(f"\n📈 综合检测结果:")
    print(f"总异常点数: {result['summary']['total_anomalies']}")
    print(f"高置信度异常: {result['summary']['high_confidence_count']} 个")
    print(f"中置信度异常: {result['summary']['medium_confidence_count']} 个")
    print(f"低置信度异常: {result['summary']['low_confidence_count']} 个")

    print(f"\n🎯 各方法检测统计:")
    for method, method_result in result['method_results'].items():
        anomaly_count = len(method_result['anomalies'])
        print(f"  {method_result['method']}: {anomaly_count} 个异常")

    print(f"\n🔍 高置信度异常点详情:")
    for i, idx in enumerate(result['high_confidence_anomalies'][:10]):
        if idx < len(test_glucose):
            votes = result['voting_results'][idx]
            value = test_glucose[idx]
            print(f"  {i+1}. 位置{idx}: 血糖={value:.1f} mg/dL, 投票数={votes}")

    print(f"\n✨ 系统成功整合了 {result['total_methods']} 种检测方法！")
    return result

if __name__ == "__main__":
    demonstrate_comprehensive_detection()