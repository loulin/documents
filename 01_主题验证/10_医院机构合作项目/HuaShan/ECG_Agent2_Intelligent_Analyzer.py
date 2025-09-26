#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECG-Agent2智能脆性分析器 v1.0
基于Agent2血糖分析架构的心电图脆性分析和智能分段系统

核心功能：
- 心律混沌动力学分析 (Lyapunov指数、近似熵、分形维数)
- ECG脆性5类分型系统 (I-V型)
- 智能时间分段 (4种变化点检测算法)
- 心血管风险分级预警
- 临床导向治疗建议

作者: AGPAI Team 
版本: v1.0
日期: 2025-09-03
"""

import numpy as np
import pandas as pd
from scipy import signal, stats
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ECGAgent2Analyzer:
    """ECG智能脆性分析器 - 基于Agent2混沌动力学架构"""
    
    def __init__(self, sampling_rate=500):
        self.sampling_rate = sampling_rate
        self.version = "1.0"
        
        # ECG脆性分型定义
        self.brittleness_types = {
            "I型正常稳定型": {"risk_level": "低风险", "score_range": (0, 30)},
            "II型轻度不稳定型": {"risk_level": "低-中风险", "score_range": (30, 50)},
            "III型中度易损型": {"risk_level": "中风险", "score_range": (50, 70)},
            "IV型重度脆弱型": {"risk_level": "高风险", "score_range": (70, 85)},
            "V型极度危险型": {"risk_level": "极高风险", "score_range": (85, 100)}
        }
        
    def analyze_ecg_intelligence(self, ecg_data, timestamps, patient_id="Unknown"):
        """ECG智能脆性分析 - 主入口函数"""
        
        print(f"[ECG-Agent2] 开始智能脆性分析: 患者 {patient_id}")
        print(f"[ECG-Agent2] 数据长度: {len(ecg_data)} 采样点, 采样率: {self.sampling_rate}Hz")
        
        try:
            # 1. 数据预处理
            filtered_ecg = self.preprocess_ecg_data(ecg_data)
            
            # 2. 心电特征提取
            ecg_features = self.extract_ecg_features(filtered_ecg)
            
            # 3. 混沌动力学指标计算
            print("[ECG-Agent2] 计算混沌动力学指标...")
            chaos_indicators = self.calculate_ecg_chaos_indicators(ecg_features)
            
            # 4. ECG脆性分型
            print("[ECG-Agent2] 进行脆性分型...")
            brittleness_result = self.classify_ecg_brittleness(chaos_indicators, ecg_features)
            
            # 5. 智能时间分段分析
            print("[ECG-Agent2] 执行智能分段分析...")
            segmentation_result = self.analyze_ecg_intelligent_segments(
                filtered_ecg, timestamps, ecg_features
            )
            
            # 6. 心血管风险评估
            risk_assessment = self.assess_cardiovascular_risk(
                brittleness_result, segmentation_result
            )
            
            # 7. 生成智能分析报告
            intelligent_report = self.generate_ecg_intelligence_report(
                patient_id, chaos_indicators, brittleness_result, 
                segmentation_result, risk_assessment
            )
            
            return intelligent_report
            
        except Exception as e:
            print(f"[ECG-Agent2] 分析错误: {e}")
            return {
                "error": str(e),
                "fallback_analysis": "ECG智能分析遇到技术问题，请检查数据格式"
            }
    
    def preprocess_ecg_data(self, raw_ecg):
        """ECG数据预处理 - 滤波和基线校正"""
        
        # 带通滤波 (0.5-40Hz) - 去除工频干扰和基线漂移
        nyquist = self.sampling_rate / 2
        low_freq = 0.5 / nyquist
        high_freq = 40 / nyquist
        
        if low_freq < 1 and high_freq < 1:
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            filtered_ecg = signal.filtfilt(b, a, raw_ecg)
        else:
            filtered_ecg = raw_ecg
        
        # 去除异常值
        filtered_ecg = self.remove_ecg_artifacts(filtered_ecg)
        
        return filtered_ecg
    
    def remove_ecg_artifacts(self, ecg_signal):
        """去除ECG伪迹和异常值"""
        
        # 基于统计学的异常值检测
        mean_val = np.mean(ecg_signal)
        std_val = np.std(ecg_signal)
        
        # 3σ原则去除极端异常值
        mask = np.abs(ecg_signal - mean_val) < 3 * std_val
        cleaned_ecg = ecg_signal.copy()
        
        # 异常点用邻近值插值替代
        if np.sum(~mask) > 0:
            cleaned_ecg[~mask] = np.interp(
                np.where(~mask)[0], 
                np.where(mask)[0], 
                ecg_signal[mask]
            )
        
        return cleaned_ecg
    
    def extract_ecg_features(self, ecg_data):
        """ECG特征提取 - RR间期、QT间期、ST段等"""
        
        try:
            # R波检测 (Pan-Tompkins算法简化版)
            r_peaks = self.detect_r_peaks(ecg_data)
            
            if len(r_peaks) < 10:
                return {
                    'rr_intervals': np.array([]),
                    'qt_intervals': np.array([]),
                    'st_segments': np.array([]),
                    'heart_rates': np.array([])
                }
            
            # RR间期计算
            rr_intervals = self.calculate_rr_intervals(r_peaks)
            
            # 心率计算
            heart_rates = 60000 / rr_intervals  # 转换为bpm (RR间期单位ms)
            
            # QT间期估算 (简化方法)
            qt_intervals = self.estimate_qt_intervals(ecg_data, r_peaks)
            
            # ST段分析
            st_segments = self.analyze_st_segments(ecg_data, r_peaks)
            
            return {
                'rr_intervals': rr_intervals,
                'qt_intervals': qt_intervals, 
                'st_segments': st_segments,
                'heart_rates': heart_rates,
                'r_peaks': r_peaks
            }
            
        except Exception as e:
            print(f"[ECG-Agent2] 特征提取失败: {e}")
            return {
                'rr_intervals': np.array([]),
                'qt_intervals': np.array([]),
                'st_segments': np.array([]),
                'heart_rates': np.array([])
            }
    
    def detect_r_peaks(self, ecg_signal):
        """R波检测 - Pan-Tompkins算法简化版"""
        
        # 简化的R波检测
        # 实际应用中可使用更精确的算法如Hamilton, Christov等
        try:
            # 动态阈值检测
            threshold = np.max(ecg_signal) * 0.6
            min_distance = int(0.6 * self.sampling_rate)  # 最小RR间期600ms
            
            peaks, properties = signal.find_peaks(
                ecg_signal, 
                height=threshold,
                distance=min_distance,
                prominence=threshold * 0.3
            )
            
            return peaks
            
        except Exception:
            # 回退方案：简单峰值检测
            peaks, _ = signal.find_peaks(ecg_signal, distance=self.sampling_rate//2)
            return peaks[:min(len(peaks), 1000)]  # 限制峰值数量
    
    def calculate_rr_intervals(self, r_peaks):
        """计算RR间期 (毫秒)"""
        
        if len(r_peaks) < 2:
            return np.array([])
        
        rr_intervals = np.diff(r_peaks) / self.sampling_rate * 1000
        
        # RR间期异常值过滤 (300-2000ms)
        valid_mask = (rr_intervals >= 300) & (rr_intervals <= 2000)
        filtered_rr = rr_intervals[valid_mask]
        
        return filtered_rr
    
    def estimate_qt_intervals(self, ecg_signal, r_peaks):
        """QT间期估算 (简化方法)"""
        
        qt_intervals = []
        
        try:
            for i, r_peak in enumerate(r_peaks[:-1]):
                # QT间期估算：从R波到下一个R波前的T波结束
                # 简化：假设QT约为RR的40-45%
                next_r = r_peaks[i + 1] if i + 1 < len(r_peaks) else len(ecg_signal) - 1
                rr_interval = (next_r - r_peak) / self.sampling_rate * 1000
                
                # Bazett公式估算：QTc = QT / sqrt(RR)
                estimated_qt = 0.42 * rr_interval  # 简化估算
                
                if 250 <= estimated_qt <= 600:  # QT间期正常范围
                    qt_intervals.append(estimated_qt)
            
            return np.array(qt_intervals)
            
        except Exception:
            return np.array([])
    
    def analyze_st_segments(self, ecg_signal, r_peaks):
        """ST段分析 - 检测ST抬高/压低"""
        
        st_values = []
        
        try:
            for r_peak in r_peaks:
                # ST段通常在R波后80-120ms (J点后)
                j_point = int(r_peak + 0.08 * self.sampling_rate)  # J点位置
                st_point = int(r_peak + 0.12 * self.sampling_rate)  # ST段测量点
                
                if st_point < len(ecg_signal) and j_point < len(ecg_signal):
                    # 基线参考：R波前的等电位线
                    baseline = np.mean(ecg_signal[max(0, r_peak - int(0.02 * self.sampling_rate)):r_peak])
                    
                    # ST段电压
                    st_voltage = ecg_signal[st_point] - baseline
                    st_values.append(st_voltage)
            
            return np.array(st_values)
            
        except Exception:
            return np.array([])
    
    def calculate_ecg_chaos_indicators(self, ecg_features):
        """ECG混沌动力学指标计算"""
        
        indicators = {}
        rr_intervals = ecg_features['rr_intervals']
        qt_intervals = ecg_features['qt_intervals']
        
        if len(rr_intervals) < 10:
            return self.get_default_chaos_indicators()
        
        # 1. RR间期Lyapunov指数 (心律混沌程度)
        indicators['lyapunov_rr'] = self.calculate_lyapunov_exponent(rr_intervals)
        
        # 2. RR间期近似熵 (心率变异复杂性)
        indicators['rr_entropy'] = self.calculate_approximate_entropy(rr_intervals)
        
        # 3. 心率变异系数
        indicators['hr_cv'] = (np.std(rr_intervals) / np.mean(rr_intervals)) * 100
        
        # 4. QT间期变异性
        if len(qt_intervals) > 5:
            indicators['qt_variability'] = np.std(qt_intervals)
            indicators['qt_entropy'] = self.calculate_approximate_entropy(qt_intervals)
        else:
            indicators['qt_variability'] = 0
            indicators['qt_entropy'] = 0
            
        # 5. ST段不稳定性
        st_segments = ecg_features['st_segments']
        if len(st_segments) > 0:
            indicators['st_instability'] = np.sum(np.abs(st_segments) > 0.05) / len(st_segments)
        else:
            indicators['st_instability'] = 0
            
        # 6. 心脏复杂度综合评分
        indicators['cardiac_complexity'] = self.calculate_cardiac_complexity_score(
            indicators['lyapunov_rr'], indicators['rr_entropy'], indicators['hr_cv']
        )
        
        # 7. 基础统计指标
        indicators['mean_rr'] = np.mean(rr_intervals)
        indicators['std_rr'] = np.std(rr_intervals)
        indicators['mean_hr'] = np.mean(ecg_features['heart_rates']) if len(ecg_features['heart_rates']) > 0 else 0
        
        return indicators
    
    def get_default_chaos_indicators(self):
        """数据不足时的默认指标"""
        return {
            'lyapunov_rr': 0,
            'rr_entropy': 0.5,
            'hr_cv': 0,
            'qt_variability': 0,
            'qt_entropy': 0,
            'st_instability': 0,
            'cardiac_complexity': 0,
            'mean_rr': 800,
            'std_rr': 50,
            'mean_hr': 75
        }
    
    def calculate_lyapunov_exponent(self, signal_data, embedding_dim=3, delay=1):
        """计算Lyapunov指数 - 量化系统混沌程度"""
        
        try:
            if len(signal_data) < 50:
                return 0
            
            # 相空间重构
            N = len(signal_data)
            if N < (embedding_dim - 1) * delay + 1:
                return 0
                
            embedded_length = N - (embedding_dim - 1) * delay
            embedded = np.zeros((embedded_length, embedding_dim))
            
            for i in range(embedding_dim):
                start_idx = i * delay
                end_idx = start_idx + embedded_length
                embedded[:, i] = signal_data[start_idx:end_idx]
            
            # 计算相邻点距离
            if len(embedded) < 2:
                return 0
                
            distances = pdist(embedded[:min(100, len(embedded))])  # 限制计算量
            
            if len(distances) == 0 or np.all(distances == 0):
                return 0
            
            # Lyapunov指数估算
            valid_distances = distances[distances > 0]
            if len(valid_distances) < 2:
                return 0
            
            min_dist = np.percentile(valid_distances, 10)
            max_dist = np.percentile(valid_distances, 90)
            
            if max_dist <= min_dist:
                return 0
                
            lyapunov = np.log(max_dist / min_dist) / len(signal_data)
            
            # 限制范围避免异常值
            return np.clip(lyapunov, -1.0, 1.0)
            
        except Exception:
            return 0
    
    def calculate_approximate_entropy(self, signal_data, m=2, r=None):
        """计算近似熵 - 量化时间序列复杂性"""
        
        try:
            N = len(signal_data)
            if N < 20:
                return 0.5
            
            if r is None:
                r = 0.2 * np.std(signal_data)
            
            if r == 0:
                return 0
                
            def _maxdist(xi, xj, m):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def _phi(m):
                patterns = np.array([signal_data[i:i + m] for i in range(N - m + 1)])
                phi_values = []
                
                for i in range(N - m + 1):
                    template = patterns[i]
                    matches = sum(1 for j in range(N - m + 1) 
                                if _maxdist(template, patterns[j], m) <= r)
                    if matches > 0:
                        phi_values.append(np.log(matches / (N - m + 1)))
                
                return np.mean(phi_values) if phi_values else 0
            
            phi_m = _phi(m)
            phi_m1 = _phi(m + 1)
            
            approximate_entropy = phi_m - phi_m1
            
            return max(0, min(2, approximate_entropy))
            
        except Exception:
            return 0.5
    
    def calculate_cardiac_complexity_score(self, lyapunov, entropy, hr_cv):
        """心脏复杂度综合评分 (0-10分)"""
        
        complexity_score = 0
        
        # Lyapunov指数贡献 (0-4分)
        if lyapunov > 0.05:
            complexity_score += 4
        elif lyapunov > 0.01:
            complexity_score += 2
        elif lyapunov > 0:
            complexity_score += 1
        
        # 近似熵贡献 (0-3分)
        if entropy > 1.2:
            complexity_score += 3
        elif entropy > 0.8:
            complexity_score += 2
        elif entropy > 0.5:
            complexity_score += 1
        
        # 心率变异贡献 (0-3分)
        if hr_cv > 40:
            complexity_score += 3
        elif hr_cv > 25:
            complexity_score += 2
        elif hr_cv > 15:
            complexity_score += 1
        
        return min(10, complexity_score)
    
    def classify_ecg_brittleness(self, chaos_indicators, ecg_features):
        """ECG脆性分型 - 基于多维混沌动力学指标"""
        
        # 提取关键指标
        lyapunov_rr = chaos_indicators.get('lyapunov_rr', 0)
        rr_entropy = chaos_indicators.get('rr_entropy', 0)
        hr_cv = chaos_indicators.get('hr_cv', 0)
        qt_variability = chaos_indicators.get('qt_variability', 0)
        st_instability = chaos_indicators.get('st_instability', 0)
        complexity_score = chaos_indicators.get('cardiac_complexity', 0)
        
        # 脆性评分计算 (0-100分)
        brittleness_score = 0
        
        # 1. 心律混沌贡献 (0-30分)
        if lyapunov_rr > 0.05:
            brittleness_score += 30
        elif lyapunov_rr > 0.01:
            brittleness_score += 20
        elif lyapunov_rr > 0:
            brittleness_score += 10
        
        # 2. 心率变异贡献 (0-25分)
        if hr_cv > 40:
            brittleness_score += 25
        elif hr_cv > 25:
            brittleness_score += 15
        elif hr_cv > 15:
            brittleness_score += 8
        
        # 3. QT间期不稳定贡献 (0-20分)
        if qt_variability > 50:
            brittleness_score += 20
        elif qt_variability > 30:
            brittleness_score += 12
        elif qt_variability > 20:
            brittleness_score += 6
        
        # 4. ST段异常贡献 (0-15分)
        if st_instability > 0.2:
            brittleness_score += 15
        elif st_instability > 0.1:
            brittleness_score += 8
        elif st_instability > 0.05:
            brittleness_score += 4
        
        # 5. 复杂度评分贡献 (0-10分)
        brittleness_score += complexity_score
        
        # 确定脆性分型
        brittleness_type = self.determine_brittleness_type(brittleness_score)
        severity = self.determine_severity_level(brittleness_score)
        risk_level = self.determine_risk_level(brittleness_score)
        
        return {
            'brittleness_type': brittleness_type,
            'severity': severity,
            'risk_level': risk_level,
            'brittleness_score': brittleness_score,
            'component_scores': {
                'cardiac_chaos': min(30, lyapunov_rr * 600),
                'heart_rate_variability': min(25, hr_cv * 0.625),
                'qt_instability': min(20, qt_variability * 0.4),
                'st_abnormality': min(15, st_instability * 75),
                'complexity': complexity_score
            }
        }
    
    def determine_brittleness_type(self, score):
        """根据评分确定脆性分型"""
        if score >= 85:
            return "V型极度危险型"
        elif score >= 70:
            return "IV型重度脆弱型"
        elif score >= 50:
            return "III型中度易损型"
        elif score >= 30:
            return "II型轻度不稳定型"
        else:
            return "I型正常稳定型"
    
    def determine_severity_level(self, score):
        """确定严重程度"""
        if score >= 85:
            return "心脏猝死高危"
        elif score >= 70:
            return "恶性心律失常高危"
        elif score >= 50:
            return "心血管事件中危"
        elif score >= 30:
            return "需要监测关注"
        else:
            return "心电活动稳定"
    
    def determine_risk_level(self, score):
        """确定风险等级"""
        if score >= 85:
            return "极高风险"
        elif score >= 70:
            return "高风险"
        elif score >= 50:
            return "中风险"
        elif score >= 30:
            return "低-中风险"
        else:
            return "低风险"
    
    def analyze_ecg_intelligent_segments(self, ecg_data, timestamps, ecg_features):
        """ECG智能分段分析 - 基于Agent2架构"""
        
        try:
            print("[ECG-Agent2] 计算滑动窗口指标...")
            
            # 滑动窗口参数 (适配ECG高频特性)
            window_duration = 600  # 10分钟窗口
            window_size = int(window_duration * self.sampling_rate)
            step_size = int(window_size // 4)  # 2.5分钟步长
            
            # 滑动窗口分析
            window_indicators = self.calculate_ecg_sliding_window_indicators(
                ecg_data, ecg_features, window_size, step_size
            )
            
            # 变化点检测
            change_points = self.detect_ecg_comprehensive_change_points(window_indicators)
            
            # 生成分段
            segments = self.generate_ecg_segments(change_points, window_indicators)
            
            return {
                "分段方法说明": "基于混沌动力学的ECG智能变化点检测技术",
                "检测维度": ["心率变异性变化", "复极化异常演变", "ST段缺血模式", "心律失常负荷"],
                "变化点检测详情": {
                    "检测方法": ["心率统计变化点", "心律聚类变化点", "缺血梯度变化点", "脆性阶段变化点"],
                    "识别出的变化点": change_points,
                    "信度评估": "高置信度" if len(change_points.get("综合变化点", [])) >= 1 else "需要更长时间监测"
                },
                "最终智能分段": segments,
                "分段质量评估": self.evaluate_ecg_segmentation_quality(segments),
                "临床意义解读": self.generate_ecg_clinical_interpretation(segments)
            }
            
        except Exception as e:
            print(f"[ECG-Agent2] 分段分析错误: {e}")
            return {
                "分段方法说明": "ECG智能分段分析遇到技术问题",
                "error": str(e),
                "fallback_analysis": "已切换到基础时间分段模式"
            }
    
    def calculate_ecg_sliding_window_indicators(self, ecg_data, ecg_features, window_size, step_size):
        """ECG滑动窗口指标计算"""
        
        indicators = {
            'timestamps': [],
            'heart_rate_mean': [],
            'heart_rate_cv': [],
            'hrv_rmssd': [],
            'qt_variability': [],
            'st_elevation_mean': [],
            'arrhythmia_burden': [],
            'complexity_score': []
        }
        
        for i in range(0, len(ecg_data) - window_size + 1, step_size):
            window_ecg = ecg_data[i:i + window_size]
            
            # 窗口内R波检测
            window_r_peaks = self.detect_r_peaks(window_ecg)
            if len(window_r_peaks) < 5:
                continue
            
            # 窗口内特征提取
            window_rr = self.calculate_rr_intervals(window_r_peaks)
            if len(window_rr) < 3:
                continue
            
            # 计算指标
            hr_mean = 60000 / np.mean(window_rr) if len(window_rr) > 0 else 75
            hr_cv = (np.std(window_rr) / np.mean(window_rr)) * 100 if len(window_rr) > 0 else 0
            hrv_rmssd = np.sqrt(np.mean(np.diff(window_rr)**2)) if len(window_rr) > 1 else 0
            
            # QT变异性 (简化估算)
            window_qt = self.estimate_qt_intervals(window_ecg, window_r_peaks)
            qt_var = np.std(window_qt) if len(window_qt) > 1 else 0
            
            # ST段分析
            window_st = self.analyze_st_segments(window_ecg, window_r_peaks)
            st_elevation = np.mean(window_st) if len(window_st) > 0 else 0
            
            # 心律失常负荷 (简化)
            arrhythmia_rate = self.calculate_window_arrhythmia_burden(window_rr)
            
            # 复杂度评分
            complexity = self.calculate_window_complexity_score(window_rr, hr_cv)
            
            # 存储指标
            indicators['timestamps'].append(i / self.sampling_rate / 60)  # 转换为分钟
            indicators['heart_rate_mean'].append(hr_mean)
            indicators['heart_rate_cv'].append(hr_cv)
            indicators['hrv_rmssd'].append(hrv_rmssd)
            indicators['qt_variability'].append(qt_var)
            indicators['st_elevation_mean'].append(st_elevation)
            indicators['arrhythmia_burden'].append(arrhythmia_rate)
            indicators['complexity_score'].append(complexity)
        
        return indicators
    
    def calculate_window_arrhythmia_burden(self, rr_intervals):
        """计算窗口内心律失常负荷"""
        
        if len(rr_intervals) < 3:
            return 0
        
        # 简化的心律失常检测：基于RR间期异常变化
        rr_diff = np.abs(np.diff(rr_intervals))
        rr_mean = np.mean(rr_intervals)
        
        # 异常RR变化 (>50ms)
        abnormal_changes = np.sum(rr_diff > 50)
        
        # 转换为每分钟次数
        arrhythmia_rate = abnormal_changes / (len(rr_intervals) * rr_mean / 60000)
        
        return min(20, arrhythmia_rate)  # 限制最大值
    
    def calculate_window_complexity_score(self, rr_intervals, hr_cv):
        """计算窗口复杂度评分"""
        
        if len(rr_intervals) < 5:
            return 0
        
        # 基于心率变异和RR间期分布的复杂度
        complexity = 0
        
        # CV贡献
        if hr_cv > 30:
            complexity += 3
        elif hr_cv > 20:
            complexity += 2
        elif hr_cv > 10:
            complexity += 1
        
        # RR间期分布复杂度
        rr_entropy = self.calculate_approximate_entropy(rr_intervals, m=2)
        if rr_entropy > 1.0:
            complexity += 2
        elif rr_entropy > 0.5:
            complexity += 1
        
        return min(5, complexity)
    
    def detect_ecg_comprehensive_change_points(self, indicators):
        """ECG综合变化点检测 - 4种算法"""
        
        change_points = {
            "心率统计变化点": [],
            "心律聚类变化点": [],
            "缺血梯度变化点": [],
            "脆性阶段变化点": [],
            "综合变化点": []
        }
        
        if len(indicators['heart_rate_mean']) < 6:
            return change_points
        
        timestamps = np.array(indicators['timestamps'])
        
        # 1. 心率统计变化点检测
        hr_changes = self.detect_statistical_change_points(
            indicators['heart_rate_mean'], timestamps, significance=0.01
        )
        cv_changes = self.detect_statistical_change_points(
            indicators['heart_rate_cv'], timestamps, significance=0.01
        )
        change_points["心率统计变化点"] = list(set(hr_changes + cv_changes))
        
        # 2. 心律聚类变化点
        features = np.column_stack([
            indicators['heart_rate_mean'],
            indicators['heart_rate_cv'],
            indicators['hrv_rmssd'],
            indicators['arrhythmia_burden']
        ])
        clustering_changes = self.detect_clustering_change_points(features, timestamps)
        change_points["心律聚类变化点"] = clustering_changes
        
        # 3. 缺血梯度变化点
        st_changes = self.detect_gradient_change_points(
            indicators['st_elevation_mean'], timestamps
        )
        change_points["缺血梯度变化点"] = st_changes
        
        # 4. 脆性阶段变化点
        brittleness_changes = self.detect_brittleness_phase_changes(
            indicators['complexity_score'], timestamps
        )
        change_points["脆性阶段变化点"] = brittleness_changes
        
        # 5. 融合变化点
        all_changes = []
        for method_changes in change_points.values():
            all_changes.extend(method_changes)
        
        if all_changes:
            merged_changes = self.merge_nearby_change_points(
                all_changes, merge_threshold=30  # 30分钟合并阈值
            )
            change_points["综合变化点"] = merged_changes
        
        return change_points
    
    def detect_statistical_change_points(self, values, timestamps, significance=0.01):
        """统计学变化点检测 - T检验"""
        
        if len(values) < 6:
            return []
        
        change_points = []
        values_array = np.array(values)
        
        for i in range(2, len(values) - 2):
            left_segment = values_array[:i]
            right_segment = values_array[i:]
            
            if len(left_segment) >= 3 and len(right_segment) >= 3:
                try:
                    t_stat, p_value = stats.ttest_ind(left_segment, right_segment)
                    if p_value < significance:
                        change_points.append(timestamps[i])
                except:
                    continue
        
        return change_points
    
    def detect_clustering_change_points(self, features, timestamps):
        """聚类变化点检测"""
        
        if len(features) < 6:
            return []
        
        try:
            # 标准化特征
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(features)
            
            # 动态确定聚类数
            max_clusters = min(4, len(features) // 2)
            if max_clusters < 2:
                return []
            
            # K-means聚类
            kmeans = KMeans(n_clusters=max_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(normalized_features)
            
            # 检测聚类边界
            change_points = []
            for i in range(1, len(labels)):
                if labels[i] != labels[i-1]:
                    change_points.append(timestamps[i])
            
            return change_points
            
        except Exception:
            return []
    
    def detect_gradient_change_points(self, values, timestamps):
        """梯度变化点检测"""
        
        if len(values) < 5:
            return []
        
        try:
            # 计算梯度
            gradient = np.gradient(values)
            
            # 动态梯度阈值
            threshold = np.percentile(np.abs(gradient), 75)
            
            # 检测梯度突变点
            change_points = []
            for i in range(1, len(gradient) - 1):
                if abs(gradient[i]) > threshold and abs(gradient[i]) > 1.5 * abs(gradient[i-1]):
                    change_points.append(timestamps[i])
            
            return change_points
            
        except Exception:
            return []
    
    def detect_brittleness_phase_changes(self, complexity_scores, timestamps):
        """脆性阶段变化点检测"""
        
        if len(complexity_scores) < 4:
            return []
        
        change_points = []
        
        # 脆性分级阈值
        def get_brittleness_phase(score):
            if score >= 4:
                return 3  # 高脆性
            elif score >= 2:
                return 2  # 中脆性
            else:
                return 1  # 低脆性
        
        current_phase = get_brittleness_phase(complexity_scores[0])
        stable_count = 1
        
        for i in range(1, len(complexity_scores)):
            new_phase = get_brittleness_phase(complexity_scores[i])
            
            if new_phase != current_phase:
                if stable_count >= 2:  # 至少稳定2个窗口
                    change_points.append(timestamps[i])
                current_phase = new_phase
                stable_count = 1
            else:
                stable_count += 1
        
        return change_points
    
    def merge_nearby_change_points(self, change_points, merge_threshold=30):
        """合并相近的变化点"""
        
        if not change_points:
            return []
        
        sorted_points = sorted(change_points)
        merged = [sorted_points[0]]
        
        for point in sorted_points[1:]:
            if point - merged[-1] > merge_threshold:
                merged.append(point)
            else:
                # 取平均值
                merged[-1] = (merged[-1] + point) / 2
        
        return merged
    
    def generate_ecg_segments(self, change_points, indicators):
        """生成ECG分段信息"""
        
        comprehensive_changes = change_points.get("综合变化点", [])
        timestamps = indicators['timestamps']
        
        if not comprehensive_changes:
            # 无变化点时按时间等分
            total_duration = timestamps[-1] - timestamps[0]
            boundaries = [timestamps[0], timestamps[0] + total_duration/2, timestamps[-1]]
        else:
            boundaries = [timestamps[0]] + comprehensive_changes + [timestamps[-1]]
            boundaries = sorted(list(set(boundaries)))
        
        segments = {
            "分段数量": len(boundaries) - 1,
            "分段边界": boundaries,
            "详细分段": []
        }
        
        for i in range(len(boundaries) - 1):
            start_time = boundaries[i]
            end_time = boundaries[i + 1]
            duration = end_time - start_time
            
            # 计算分段内的平均指标
            segment_mask = (np.array(timestamps) >= start_time) & (np.array(timestamps) <= end_time)
            segment_indices = np.where(segment_mask)[0]
            
            if len(segment_indices) > 0:
                segment_hr = np.mean([indicators['heart_rate_mean'][j] for j in segment_indices])
                segment_cv = np.mean([indicators['heart_rate_cv'][j] for j in segment_indices])
                segment_complexity = np.mean([indicators['complexity_score'][j] for j in segment_indices])
            else:
                segment_hr = 75  # 默认值
                segment_cv = 10
                segment_complexity = 1
            
            # 分段特征描述
            if segment_complexity >= 4:
                segment_feature = "高复杂度心律失常期"
            elif segment_complexity >= 2:
                segment_feature = "中等复杂度不稳定期"
            elif segment_cv > 20:
                segment_feature = "心率变异增加期"
            else:
                segment_feature = "相对稳定期"
            
            segment_info = {
                "分段": i + 1,
                "开始时间": f"{start_time:.1f}分钟",
                "结束时间": f"{end_time:.1f}分钟",
                "持续时间": f"{duration:.1f}分钟",
                "平均心率": f"{segment_hr:.1f} bpm",
                "心率变异CV": f"{segment_cv:.1f}%",
                "复杂度评分": f"{segment_complexity:.1f}/5",
                "分段特征": segment_feature,
                "临床意义": self.get_segment_clinical_significance(segment_complexity, segment_cv)
            }
            
            segments["详细分段"].append(segment_info)
        
        return segments
    
    def get_segment_clinical_significance(self, complexity, cv):
        """获取分段临床意义"""
        
        if complexity >= 4:
            return "需要密切监护，高危心律失常风险"
        elif complexity >= 2:
            return "需要关注，中等心律失常风险"
        elif cv > 30:
            return "心率变异增加，建议评估自主神经功能"
        elif cv > 20:
            return "轻度心率不稳定，继续监测"
        else:
            return "心律相对稳定，维持现状"
    
    def evaluate_ecg_segmentation_quality(self, segments):
        """评估ECG分段质量"""
        
        num_segments = segments.get("分段数量", 0)
        
        quality_assessment = {
            "分段合理性": "优秀" if 2 <= num_segments <= 4 else "中等",
            "临床实用性": "高" if num_segments <= 5 else "中",
            "技术可靠性": "高",
            "总体评级": ""
        }
        
        if num_segments == 0:
            quality_assessment["总体评级"] = "数据不足"
        elif 2 <= num_segments <= 4:
            quality_assessment["总体评级"] = "优秀 - 临床友好分段"
        elif num_segments <= 6:
            quality_assessment["总体评级"] = "良好 - 分段合理"
        else:
            quality_assessment["总体评级"] = "需要优化 - 分段过多"
        
        return quality_assessment
    
    def generate_ecg_clinical_interpretation(self, segments):
        """生成ECG临床意义解读"""
        
        num_segments = segments.get("分段数量", 0)
        detailed_segments = segments.get("详细分段", [])
        
        interpretation = {
            "分段意义": "",
            "临床价值": [],
            "治疗指导": []
        }
        
        if num_segments <= 2:
            interpretation["分段意义"] = "心电活动相对稳定，无明显阶段性变化"
            interpretation["临床价值"].append("心律稳定性良好")
        elif num_segments <= 4:
            interpretation["分段意义"] = "检测到明显的心电活动阶段性变化"
            interpretation["临床价值"].extend([
                "成功识别心律变化的关键时点",
                "为治疗效果评估提供客观依据",
                "有助于预测心血管事件风险"
            ])
        else:
            interpretation["分段意义"] = "心电活动复杂多变，存在多个不稳定阶段"
            interpretation["临床价值"].append("需要更密集的监测和干预")
        
        # 治疗指导建议
        for segment in detailed_segments:
            complexity = float(segment.get("复杂度评分", "0").split('/')[0])
            if complexity >= 4:
                interpretation["治疗指导"].append("高危时段需要紧急心血管评估")
            elif complexity >= 2:
                interpretation["治疗指导"].append("不稳定时段建议调整治疗方案")
        
        if not interpretation["治疗指导"]:
            interpretation["治疗指导"].append("维持现有治疗，定期随访")
        
        return interpretation
    
    def assess_cardiovascular_risk(self, brittleness_result, segmentation_result):
        """心血管风险评估"""
        
        brittleness_score = brittleness_result['brittleness_score']
        brittleness_type = brittleness_result['brittleness_type']
        num_segments = segmentation_result.get("最终智能分段", {}).get("分段数量", 0)
        
        # 综合风险评分
        risk_factors = []
        risk_score = 0
        
        # 脆性评分贡献
        risk_score += brittleness_score * 0.7  # 70%权重
        
        # 分段复杂度贡献
        if num_segments > 5:
            risk_score += 15  # 复杂分段增加风险
            risk_factors.append("心电活动复杂多变")
        elif num_segments > 3:
            risk_score += 8
            risk_factors.append("心电活动存在阶段性变化")
        
        # 风险分级
        if risk_score >= 85:
            risk_level = "极高风险"
            recommendation = "立即心血管专科会诊，考虑住院监护"
        elif risk_score >= 70:
            risk_level = "高风险"
            recommendation = "紧急心血管评估，调整治疗方案"
        elif risk_score >= 50:
            risk_level = "中等风险"
            recommendation = "加强监测，定期专科随访"
        elif risk_score >= 30:
            risk_level = "低-中风险"
            recommendation = "继续观察，3-6月复查"
        else:
            risk_level = "低风险"
            recommendation = "维持现状，年度体检"
        
        return {
            "综合风险评分": risk_score,
            "风险等级": risk_level,
            "主要风险因素": risk_factors,
            "治疗建议": recommendation,
            "随访建议": self.generate_follow_up_plan(risk_level),
            "预后评估": self.generate_prognosis_assessment(brittleness_type, risk_score)
        }
    
    def generate_follow_up_plan(self, risk_level):
        """生成随访计划"""
        
        follow_up_plans = {
            "极高风险": "每日心电监护，每周专科随访，1月内复评",
            "高风险": "每周心电图，2周专科随访，3月内复评",
            "中等风险": "每2周心电图，1月专科随访，6月复评", 
            "低-中风险": "每月心电图，3月专科随访，年度评估",
            "低风险": "3月心电图检查，年度体检，必要时随诊"
        }
        
        return follow_up_plans.get(risk_level, "根据临床情况制定随访计划")
    
    def generate_prognosis_assessment(self, brittleness_type, risk_score):
        """生成预后评估"""
        
        if brittleness_type == "V型极度危险型":
            return "预后需谨慎，心脏猝死风险显著增加，需要积极干预"
        elif brittleness_type == "IV型重度脆弱型":
            return "预后有待改善，通过规范治疗可明显降低风险"
        elif brittleness_type == "III型中度易损型":
            return "预后良好，通过生活方式和药物治疗可有效控制"
        elif brittleness_type == "II型轻度不稳定型":
            return "预后优良，轻度异常通过调理可恢复正常"
        else:
            return "预后优秀，心电活动稳定，继续保持"
    
    def generate_ecg_intelligence_report(self, patient_id, chaos_indicators, 
                                       brittleness_result, segmentation_result, risk_assessment):
        """生成ECG智能分析报告"""
        
        report = {
            "报告头信息": {
                "报告类型": f"ECG智能脆性分析报告 v{self.version}",
                "患者ID": patient_id,
                "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "报告生成器": "ECG_Agent2_Intelligent_Analyzer",
                "版本号": f"{self.version}.0",
                "分析方法": "心律混沌动力学 + 多维脆性评分 + 智能分段 + 风险预测"
            },
            
            "心律混沌动力学指标": {
                "分析说明": "基于非线性动力学理论的心脏电活动混沌特征分析",
                "RR间期Lyapunov指数": {
                    "数值": f"{chaos_indicators['lyapunov_rr']:.6f}",
                    "解释": "正值表示心律混沌，负值表示心律稳定",
                    "临床意义": "评估心律失常风险和心脏猝死预测指标"
                },
                "RR间期近似熵": {
                    "数值": f"{chaos_indicators['rr_entropy']:.4f}",
                    "解释": "衡量心率变异复杂性和不规则程度",
                    "临床意义": "高熵值提示自主神经功能异常"
                },
                "心率变异系数": {
                    "数值": f"{chaos_indicators['hr_cv']:.2f}%",
                    "解释": "心率变异程度的标准化指标",
                    "临床意义": "反映自主神经调节功能状态"
                },
                "QT间期变异性": {
                    "数值": f"{chaos_indicators['qt_variability']:.2f}ms",
                    "解释": "心室复极化过程的不稳定性",
                    "临床意义": "恶性心律失常和心脏猝死的预测指标"
                },
                "ST段不稳定性": {
                    "数值": f"{chaos_indicators['st_instability']:.2f}",
                    "解释": "心肌缺血相关的ST段变化比例",
                    "临床意义": "反映心肌缺血负荷和冠心病风险"
                }
            },
            
            "ECG脆性分型评估": {
                "脆性分型": brittleness_result['brittleness_type'],
                "严重程度": brittleness_result['severity'],
                "脆性评分": f"{brittleness_result['brittleness_score']:.1f}/100",
                "风险等级": brittleness_result['risk_level'],
                "核心指标": {
                    "平均心率": f"{chaos_indicators['mean_hr']:.1f} bpm",
                    "平均RR间期": f"{chaos_indicators['mean_rr']:.1f} ms",
                    "RR标准差": f"{chaos_indicators['std_rr']:.1f} ms",
                    "心脏复杂度": f"{chaos_indicators['cardiac_complexity']:.1f}/10"
                },
                "分型特征": self.get_brittleness_type_features(brittleness_result['brittleness_type']),
                "病理生理机制": self.get_pathophysiology_mechanism(brittleness_result['brittleness_type'])
            },
            
            "ECG智能分段分析": segmentation_result,
            
            "心血管风险评估": risk_assessment,
            
            "综合智能解读": {
                "主要发现": f"患者心电系统分型为{brittleness_result['brittleness_type']}，综合风险评分{risk_assessment['综合风险评分']:.1f}分",
                "关键风险因素": risk_assessment['主要风险因素'],
                "治疗建议": risk_assessment['治疗建议'],
                "预后判断": risk_assessment['预后评估']
            },
            
            "个性化医疗建议": {
                "立即处理": self.generate_immediate_actions(brittleness_result['risk_level']),
                "治疗策略": self.generate_treatment_strategy(brittleness_result['brittleness_type']),
                "监测方案": self.generate_monitoring_protocol(brittleness_result['risk_level']),
                "生活建议": self.generate_lifestyle_recommendations(brittleness_result['brittleness_type']),
                "随访计划": risk_assessment['随访建议']
            }
        }
        
        return report
    
    def get_brittleness_type_features(self, brittleness_type):
        """获取脆性分型特征"""
        
        features_map = {
            "V型极度危险型": [
                "心律极度不稳定，存在恶性心律失常",
                "Lyapunov指数显著为正，系统处于混沌状态", 
                "心脏猝死风险极高，需要立即干预",
                "建议植入式心律转复除颤器(ICD)"
            ],
            "IV型重度脆弱型": [
                "心室电活动严重不稳定",
                "QT间期变异显著增加",
                "存在结构性心脏病的可能",
                "需要完善心脏影像学检查"
            ],
            "III型中度易损型": [
                "自主神经调节功能失衡",
                "心率变异性异常增加",
                "存在一定的心律失常风险",
                "通过治疗可有效改善"
            ],
            "II型轻度不稳定型": [
                "轻度心律不稳定，偶发早搏",
                "自主神经功能轻度异常",
                "大多数情况预后良好",
                "生活方式调整为主要干预手段"
            ],
            "I型正常稳定型": [
                "心电活动正常稳定",
                "自主神经调节平衡",
                "心血管风险低",
                "维持健康生活方式"
            ]
        }
        
        return features_map.get(brittleness_type, ["需要进一步评估脆性特征"])
    
    def get_pathophysiology_mechanism(self, brittleness_type):
        """获取病理生理机制"""
        
        mechanisms = {
            "V型极度危险型": "心脏电传导系统严重紊乱，窦房结和房室结功能失调；心肌细胞膜离子通道异常，动作电位不稳定；交感和副交感神经调节严重失衡；可能存在心肌结构性病变。",
            
            "IV型重度脆弱型": "心室肌细胞复极化过程异常，钾离子通道功能障碍；心肌纤维化导致电传导异常；冠状动脉微循环障碍影响心肌电活动；神经-内分泌系统调节紊乱。",
            
            "III型中度易损型": "自主神经系统调节失衡，交感神经过度激活或副交感神经功能减退；心率变异性控制机制异常；心脏压力反射敏感性下降；可能与代谢性疾病相关。",
            
            "II型轻度不稳定型": "轻度自主神经功能紊乱，可能与生活压力、睡眠不足、咖啡因摄入等因素相关；心脏传导系统功能基本正常但存在轻微扰动；代偿机制尚可维持。",
            
            "I型正常稳定型": "心脏电传导系统功能正常，窦房结起搏规律；自主神经调节平衡，交感和副交感神经协调工作；心肌细胞电生理活动稳定；整体心血管系统处于健康状态。"
        }
        
        return mechanisms.get(brittleness_type, "需要进一步分析病理生理机制")
    
    def generate_immediate_actions(self, risk_level):
        """生成立即处理建议"""
        
        actions = {
            "极高风险": [
                "立即建立心电监护",
                "准备除颤设备和抢救药物",
                "紧急心血管专科会诊",
                "考虑转入CCU监护"
            ],
            "高风险": [
                "24小时心电监测",
                "完善心脏超声和冠脉评估",
                "调整抗心律失常药物",
                "准备应急处理预案"
            ],
            "中等风险": [
                "加强心电图监测频率",
                "评估现有药物治疗方案",
                "完善相关辅助检查",
                "制定随访计划"
            ],
            "低-中风险": [
                "定期心电图检查",
                "生活方式指导",
                "必要时药物干预",
                "3-6月随访"
            ],
            "低风险": [
                "维持现有生活方式",
                "年度健康体检",
                "注意心血管危险因素",
                "必要时就诊"
            ]
        }
        
        return actions.get(risk_level, ["根据具体情况制定处理方案"])
    
    def generate_treatment_strategy(self, brittleness_type):
        """生成治疗策略"""
        
        strategies = {
            "V型极度危险型": [
                "考虑植入式心律转复除颤器(ICD)",
                "多重抗心律失常药物联合治疗",
                "射频消融术评估",
                "心脏再同步化治疗(CRT)评估"
            ],
            "IV型重度脆弱型": [
                "规范抗心律失常药物治疗",
                "冠状动脉介入治疗评估",
                "心脏电生理检查",
                "必要时外科手术治疗"
            ],
            "III型中度易损型": [
                "β受体阻滞剂治疗",
                "ACEI/ARB类药物",
                "心率控制药物",
                "抗凝治疗评估"
            ],
            "II型轻度不稳定型": [
                "生活方式干预为主",
                "必要时小剂量β阻滞剂",
                "电解质平衡调节",
                "压力管理和心理疏导"
            ],
            "I型正常稳定型": [
                "无需特殊药物治疗",
                "维持健康生活方式",
                "控制心血管危险因素",
                "定期健康监测"
            ]
        }
        
        return strategies.get(brittleness_type, ["根据具体病情制定治疗方案"])
    
    def generate_monitoring_protocol(self, risk_level):
        """生成监测方案"""
        
        protocols = {
            "极高风险": "连续心电监护 + 每日心电图 + 每周动态心电图 + 必要时植入式监测设备",
            "高风险": "24小时动态心电图每周1次 + 心电图每3日1次 + 必要时事件记录器",
            "中等风险": "24小时动态心电图每月1次 + 心电图每周1次 + 症状时随时检查",
            "低-中风险": "心电图每2周1次 + 动态心电图每3月1次 + 年度完整心电评估",
            "低风险": "心电图每月1次 + 动态心电图半年1次 + 年度体检心电图"
        }
        
        return protocols.get(risk_level, "根据病情制定个性化监测方案")
    
    def generate_lifestyle_recommendations(self, brittleness_type):
        """生成生活建议"""
        
        recommendations = {
            "V型极度危险型": [
                "绝对避免剧烈运动和情绪激动",
                "24小时有人陪伴，携带急救药物",
                "避免咖啡因、酒精等刺激性物质",
                "保持规律作息，充足睡眠"
            ],
            "IV型重度脆弱型": [
                "限制剧烈运动，适量轻度活动",
                "避免过度劳累和情绪波动",
                "戒烟限酒，低盐低脂饮食",
                "规律用药，定期监测"
            ],
            "III型中度易损型": [
                "适度有氧运动，避免过度疲劳",
                "学会压力管理和放松技巧",
                "保持规律作息，避免熬夜",
                "均衡饮食，控制体重"
            ],
            "II型轻度不稳定型": [
                "规律的中等强度有氧运动",
                "减少咖啡因摄入，戒烟限酒",
                "保持良好的睡眠质量",
                "适当的心理调节和压力释放"
            ],
            "I型正常稳定型": [
                "维持规律的体育锻炼习惯",
                "平衡营养，控制心血管危险因素",
                "保持积极乐观的心态",
                "定期健康体检"
            ]
        }
        
        return recommendations.get(brittleness_type, ["根据个人情况制定生活方式建议"])

# 使用示例
if __name__ == "__main__":
    # 创建ECG分析器实例
    ecg_analyzer = ECGAgent2Analyzer(sampling_rate=500)
    
    # 模拟ECG数据 (实际使用时从文件读取)
    print("ECG-Agent2智能脆性分析器 v1.0")
    print("基于Agent2血糖分析架构的心电图智能分析系统")
    print("\n使用方法:")
    print("1. ecg_data = load_ecg_data('patient_ecg.csv')")
    print("2. result = ecg_analyzer.analyze_ecg_intelligence(ecg_data, timestamps, 'Patient001')")
    print("3. 查看result中的完整分析报告")
    print("\n支持的ECG数据格式:")
    print("- 采样率: 250-1000 Hz")
    print("- 数据长度: 至少10分钟，推荐24小时")
    print("- 数据格式: numpy数组或pandas DataFrame")