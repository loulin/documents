#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ECG_Segmentation_Analyzer.py

ECG智能分段分析器 - 基于Agent2 v5.0智能分段架构
专门用于ECG信号的病理生理阶段识别和临床事件分段

作者: AGPAI Team
版本: v1.0
日期: 2025-08-28
"""

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import chi2_contingency
import json
from datetime import datetime, timedelta
from enum import Enum

class ECGDataStatus(Enum):
    """ECG数据状态"""
    REALTIME = "realtime"
    HISTORICAL = "historical"
    EMERGENCY = "emergency"
    MONITORING = "monitoring"

class ECGSegmentationAnalyzer:
    """ECG智能分段分析器"""
    
    def __init__(self, sampling_rate=500):
        self.sampling_rate = sampling_rate
        self.segmentation_modes = {
            'auto': '智能自动选择',
            'pathophysiologic': '病理生理分段',
            'clinical_event': '临床事件分段',
            'treatment_response': '治疗反应分段',
            'dual': '双模式分析'
        }
    
    def detect_data_status(self, ecg_data, timestamps=None):
        """智能检测ECG数据状态"""
        try:
            if timestamps is None:
                # 如果没有时间戳，默认为连续采样
                duration_hours = len(ecg_data) / self.sampling_rate / 3600
                data_status = ECGDataStatus.HISTORICAL if duration_hours > 1 else ECGDataStatus.REALTIME
            else:
                # 分析时间特征
                time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                current_time = datetime.now()
                time_since_last = (current_time - timestamps[-1]).total_seconds() / 3600
                
                if time_since_last < 0.1:  # 10分钟内
                    data_status = ECGDataStatus.REALTIME
                elif time_span < 2:  # 2小时内
                    data_status = ECGDataStatus.EMERGENCY
                else:
                    data_status = ECGDataStatus.HISTORICAL
            
            return {
                "数据状态": data_status.value,
                "数据时长": f"{len(ecg_data) / self.sampling_rate / 3600:.1f}小时",
                "数据密度": f"{self.sampling_rate}Hz",
                "推荐分段模式": self.recommend_segmentation_mode(data_status)
            }
        except:
            return {
                "数据状态": ECGDataStatus.HISTORICAL.value,
                "推荐分段模式": "pathophysiologic"
            }
    
    def recommend_segmentation_mode(self, data_status):
        """根据数据状态推荐分段模式"""
        recommendations = {
            ECGDataStatus.REALTIME: "clinical_event",      # 实时数据关注临床事件
            ECGDataStatus.EMERGENCY: "pathophysiologic",   # 急诊数据关注病理生理
            ECGDataStatus.HISTORICAL: "treatment_response", # 历史数据评估治疗反应
            ECGDataStatus.MONITORING: "dual"               # 监测数据双模式分析
        }
        return recommendations.get(data_status, "pathophysiologic")
    
    def detect_ecg_change_points(self, ecg_data, method='multi_dimensional'):
        """ECG变化点检测"""
        try:
            # 提取多维度ECG特征
            features = self.extract_ecg_features(ecg_data)
            
            if method == 'multi_dimensional':
                change_points = self.multi_dimensional_change_detection(features)
            elif method == 'statistical':
                change_points = self.statistical_change_detection(features)
            else:
                change_points = self.clinical_event_detection(ecg_data)
            
            return change_points
        except Exception as e:
            print(f"变化点检测出错: {e}")
            return []
    
    def extract_ecg_features(self, ecg_data, window_size_sec=60):
        """提取ECG多维度特征"""
        window_size = int(window_size_sec * self.sampling_rate)
        features = []
        
        for i in range(0, len(ecg_data) - window_size, window_size // 4):
            window = ecg_data[i:i + window_size]
            
            # R波检测
            r_peaks, _ = signal.find_peaks(window, 
                                         height=np.max(window) * 0.6,
                                         distance=self.sampling_rate * 0.6)
            
            if len(r_peaks) > 2:
                rr_intervals = np.diff(r_peaks) / self.sampling_rate * 1000
                
                feature_dict = {
                    'timestamp_idx': i,
                    'heart_rate_mean': 60000 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0,
                    'heart_rate_std': np.std(60000 / rr_intervals) if len(rr_intervals) > 1 else 0,
                    'rmssd': np.sqrt(np.mean(np.diff(rr_intervals) ** 2)) if len(rr_intervals) > 1 else 0,
                    'signal_amplitude_mean': np.mean(np.abs(window)),
                    'signal_amplitude_std': np.std(window),
                    'high_freq_power': self.calculate_high_frequency_power(window),
                    'morphology_complexity': self.calculate_morphology_complexity(window, r_peaks)
                }
            else:
                # 如果检测不到足够的R波，使用基本统计特征
                feature_dict = {
                    'timestamp_idx': i,
                    'heart_rate_mean': 0,
                    'heart_rate_std': 0,
                    'rmssd': 0,
                    'signal_amplitude_mean': np.mean(np.abs(window)),
                    'signal_amplitude_std': np.std(window),
                    'high_freq_power': 0,
                    'morphology_complexity': 0
                }
            
            features.append(feature_dict)
        
        return features
    
    def calculate_high_frequency_power(self, signal_window):
        """计算高频功率"""
        try:
            f, psd = signal.welch(signal_window, fs=self.sampling_rate, nperseg=min(256, len(signal_window)))
            high_freq_mask = (f >= 15) & (f <= 40)  # 15-40Hz
            high_freq_power = np.sum(psd[high_freq_mask])
            return high_freq_power
        except:
            return 0
    
    def calculate_morphology_complexity(self, signal_window, r_peaks):
        """计算波形复杂度"""
        try:
            if len(r_peaks) < 2:
                return 0
            
            # 提取心拍波形
            beat_morphologies = []
            for i in range(len(r_peaks) - 1):
                start = max(0, r_peaks[i] - int(0.2 * self.sampling_rate))
                end = min(len(signal_window), r_peaks[i] + int(0.4 * self.sampling_rate))
                beat = signal_window[start:end]
                if len(beat) > 10:
                    # 归一化
                    beat = (beat - np.mean(beat)) / (np.std(beat) + 1e-6)
                    beat_morphologies.append(beat)
            
            if len(beat_morphologies) < 2:
                return 0
            
            # 计算波形间相关性
            correlations = []
            min_length = min([len(beat) for beat in beat_morphologies])
            
            for i in range(len(beat_morphologies) - 1):
                beat1 = beat_morphologies[i][:min_length]
                beat2 = beat_morphologies[i+1][:min_length]
                correlation = np.corrcoef(beat1, beat2)[0, 1]
                if not np.isnan(correlation):
                    correlations.append(correlation)
            
            # 复杂度 = 1 - 平均相关性
            if len(correlations) > 0:
                complexity = 1 - np.mean(correlations)
                return max(0, min(1, complexity))
            else:
                return 0
        except:
            return 0
    
    def multi_dimensional_change_detection(self, features):
        """多维度变化点检测"""
        change_points = []
        
        if len(features) < 4:
            return change_points
        
        # 转换为数值矩阵
        feature_matrix = np.array([[f['heart_rate_mean'], f['rmssd'], 
                                   f['signal_amplitude_mean'], f['morphology_complexity']] 
                                  for f in features])
        
        # 滑动窗口检测显著变化
        window_size = 5
        for i in range(window_size, len(feature_matrix) - window_size):
            before_window = feature_matrix[i-window_size:i]
            after_window = feature_matrix[i:i+window_size]
            
            # 计算各维度的统计显著性
            significant_changes = 0
            
            for dim in range(feature_matrix.shape[1]):
                before_values = before_window[:, dim]
                after_values = after_window[:, dim]
                
                # 均值变化检测
                if len(before_values) > 2 and len(after_values) > 2:
                    before_mean = np.mean(before_values)
                    after_mean = np.mean(after_values)
                    before_std = np.std(before_values)
                    after_std = np.std(after_values)
                    
                    # 简化的t检验
                    pooled_std = np.sqrt((before_std**2 + after_std**2) / 2)
                    if pooled_std > 0:
                        t_stat = abs(before_mean - after_mean) / (pooled_std * np.sqrt(2/window_size))
                        if t_stat > 2.0:  # 简化的显著性阈值
                            significant_changes += 1
            
            # 如果多个维度同时发生显著变化，认为是变化点
            if significant_changes >= 2:
                change_point_info = {
                    'timestamp_idx': features[i]['timestamp_idx'],
                    'time_sec': features[i]['timestamp_idx'] / self.sampling_rate,
                    'significance_score': significant_changes,
                    'change_type': self.classify_change_type(features[i-1], features[i])
                }
                change_points.append(change_point_info)
        
        return change_points
    
    def classify_change_type(self, before_features, after_features):
        """分类变化类型"""
        hr_change = after_features['heart_rate_mean'] - before_features['heart_rate_mean']
        hrv_change = after_features['rmssd'] - before_features['rmssd']
        
        if hr_change > 20:
            return "心率上升"
        elif hr_change < -20:
            return "心率下降"
        elif hrv_change > 10:
            return "心率变异性增加"
        elif hrv_change < -10:
            return "心率变异性减少"
        else:
            return "综合变化"
    
    def analyze_pathophysiologic_segments(self, ecg_data, change_points):
        """病理生理分段分析"""
        if not change_points:
            # 如果没有检测到变化点，按固定时间分段
            duration_sec = len(ecg_data) / self.sampling_rate
            if duration_sec <= 3600:  # 1小时内
                segments = self.create_fixed_time_segments(ecg_data, num_segments=3)
            else:
                segments = self.create_fixed_time_segments(ecg_data, num_segments=6)
        else:
            segments = self.create_adaptive_segments(ecg_data, change_points)
        
        return {
            "分段模式": "病理生理分段",
            "分段数量": len(segments),
            "分段详情": segments,
            "临床应用": "适用于疾病进展监测和病理机制分析"
        }
    
    def analyze_clinical_event_segments(self, ecg_data, clinical_events=None):
        """临床事件分段分析"""
        # 检测关键临床事件
        detected_events = []
        
        # 心律失常检测
        arrhythmia_events = self.detect_arrhythmia_episodes(ecg_data)
        detected_events.extend(arrhythmia_events)
        
        # 心肌缺血检测
        ischemia_events = self.detect_ischemia_episodes(ecg_data)
        detected_events.extend(ischemia_events)
        
        # 基于事件创建分段
        if detected_events:
            segments = self.create_event_based_segments(ecg_data, detected_events)
        else:
            segments = self.create_fixed_time_segments(ecg_data, num_segments=4)
        
        return {
            "分段模式": "临床事件分段",
            "检测到的事件": len(detected_events),
            "分段数量": len(segments),
            "分段详情": segments,
            "临床应用": "适用于急性事件监测和实时预警"
        }
    
    def detect_arrhythmia_episodes(self, ecg_data):
        """检测心律失常发作"""
        events = []
        
        # 简化的心律失常检测
        # 实际应用中需要更复杂的算法
        
        # R波检测
        r_peaks, _ = signal.find_peaks(ecg_data, 
                                     height=np.max(ecg_data) * 0.6,
                                     distance=self.sampling_rate * 0.3)
        
        if len(r_peaks) > 2:
            rr_intervals = np.diff(r_peaks) / self.sampling_rate * 1000
            
            # 检测心律失常
            for i in range(1, len(rr_intervals)):
                # 房颤检测 (RR间期极不规律)
                if i >= 10:
                    recent_rr = rr_intervals[i-10:i]
                    rr_cv = np.std(recent_rr) / np.mean(recent_rr)
                    if rr_cv > 0.3:  # 变异系数>30%
                        events.append({
                            'type': '疑似房颤',
                            'start_idx': r_peaks[i-5],
                            'confidence': min(1.0, rr_cv)
                        })
                
                # 室性心动过速检测 (心率>150且规律)
                if rr_intervals[i] < 400:  # RR<400ms (HR>150)
                    consecutive_fast = 1
                    j = i + 1
                    while j < len(rr_intervals) and rr_intervals[j] < 400:
                        consecutive_fast += 1
                        j += 1
                    
                    if consecutive_fast >= 5:  # 连续5拍以上
                        events.append({
                            'type': '疑似室性心动过速',
                            'start_idx': r_peaks[i],
                            'duration_beats': consecutive_fast,
                            'confidence': 0.8
                        })
        
        return events
    
    def detect_ischemia_episodes(self, ecg_data):
        """检测心肌缺血发作"""
        events = []
        
        # ST段分析 (简化版本)
        try:
            # 高通滤波去除基线漂移
            b, a = signal.butter(4, 0.5/(self.sampling_rate/2), btype='high')
            filtered_ecg = signal.filtfilt(b, a, ecg_data)
            
            # 滑动窗口ST段分析
            window_size = int(10 * self.sampling_rate)  # 10秒窗口
            
            for i in range(0, len(filtered_ecg) - window_size, window_size // 2):
                window = filtered_ecg[i:i + window_size]
                
                # 简化的ST段提升检测
                # 实际应用中需要精确的QRS和ST段定位
                st_level = np.mean(window[len(window)//3:2*len(window)//3])  # 中间1/3作为ST段
                baseline_level = np.mean(window[:len(window)//5])  # 前1/5作为基线
                
                st_elevation = st_level - baseline_level
                
                # ST段抬高>1mm (0.1mV)
                if abs(st_elevation) > 0.1:
                    event_type = "ST段抬高" if st_elevation > 0 else "ST段压低"
                    events.append({
                        'type': event_type,
                        'start_idx': i,
                        'st_deviation': st_elevation,
                        'confidence': min(1.0, abs(st_elevation) / 0.2)
                    })
        except:
            pass
        
        return events
    
    def create_adaptive_segments(self, ecg_data, change_points):
        """基于变化点创建自适应分段"""
        segments = []
        
        # 添加起始点
        boundaries = [0] + [cp['timestamp_idx'] for cp in change_points] + [len(ecg_data)]
        boundaries = sorted(list(set(boundaries)))  # 去重并排序
        
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            
            segment_data = ecg_data[start_idx:end_idx]
            segment_features = self.analyze_segment_features(segment_data)
            
            segments.append({
                "段落编号": i + 1,
                "开始时间": f"{start_idx / self.sampling_rate:.1f}秒",
                "结束时间": f"{end_idx / self.sampling_rate:.1f}秒",
                "持续时间": f"{(end_idx - start_idx) / self.sampling_rate:.1f}秒",
                "段落特征": segment_features
            })
        
        return segments
    
    def create_fixed_time_segments(self, ecg_data, num_segments=4):
        """创建固定时间分段"""
        segments = []
        segment_length = len(ecg_data) // num_segments
        
        for i in range(num_segments):
            start_idx = i * segment_length
            end_idx = (i + 1) * segment_length if i < num_segments - 1 else len(ecg_data)
            
            segment_data = ecg_data[start_idx:end_idx]
            segment_features = self.analyze_segment_features(segment_data)
            
            segments.append({
                "段落编号": i + 1,
                "开始时间": f"{start_idx / self.sampling_rate:.1f}秒",
                "结束时间": f"{end_idx / self.sampling_rate:.1f}秒",
                "持续时间": f"{(end_idx - start_idx) / self.sampling_rate:.1f}秒",
                "段落特征": segment_features
            })
        
        return segments
    
    def analyze_segment_features(self, segment_data):
        """分析分段特征"""
        try:
            # R波检测
            r_peaks, _ = signal.find_peaks(segment_data, 
                                         height=np.max(segment_data) * 0.6,
                                         distance=self.sampling_rate * 0.4)
            
            if len(r_peaks) > 2:
                rr_intervals = np.diff(r_peaks) / self.sampling_rate * 1000
                mean_hr = 60000 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0
                rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2)) if len(rr_intervals) > 1 else 0
            else:
                mean_hr = 0
                rmssd = 0
            
            return {
                "平均心率": f"{mean_hr:.1f} bpm",
                "心率变异性(RMSSD)": f"{rmssd:.1f} ms",
                "信号质量": self.assess_signal_quality(segment_data),
                "节律规整性": self.assess_rhythm_regularity(rr_intervals) if len(r_peaks) > 2 else "无法评估"
            }
        except:
            return {
                "平均心率": "无法计算",
                "心率变异性": "无法计算", 
                "信号质量": "差",
                "节律规整性": "无法评估"
            }
    
    def assess_signal_quality(self, signal_data):
        """评估信号质量"""
        # 信噪比估计
        signal_power = np.var(signal_data)
        high_freq_noise = np.var(np.diff(signal_data))
        
        if high_freq_noise > 0:
            snr = signal_power / high_freq_noise
            if snr > 100:
                return "优秀"
            elif snr > 50:
                return "良好"
            elif snr > 20:
                return "一般"
            else:
                return "差"
        else:
            return "良好"
    
    def assess_rhythm_regularity(self, rr_intervals):
        """评估心律规整性"""
        if len(rr_intervals) < 5:
            return "数据不足"
        
        cv = np.std(rr_intervals) / np.mean(rr_intervals)
        
        if cv < 0.05:
            return "非常规整"
        elif cv < 0.10:
            return "规整"
        elif cv < 0.20:
            return "轻度不规整"
        elif cv < 0.30:
            return "中度不规整"
        else:
            return "严重不规整"

def analyze_ecg_segmentation(ecg_data, patient_id="Unknown", mode="auto", sampling_rate=500):
    """ECG智能分段分析主函数"""
    
    print(f"📈 ECG智能分段分析启动 - 患者ID: {patient_id}")
    print(f"🔧 分段模式: {mode}")
    print("="*60)
    
    # 初始化分析器
    analyzer = ECGSegmentationAnalyzer(sampling_rate=sampling_rate)
    
    # 检测数据状态
    data_status = analyzer.detect_data_status(ecg_data)
    print(f"📊 数据状态: {data_status['数据状态']}")
    print(f"⏱️  数据时长: {data_status['数据时长']}")
    
    # 智能模式选择
    if mode == "auto":
        mode = data_status['推荐分段模式']
        print(f"🧠 智能推荐模式: {mode}")
    
    # 检测变化点
    change_points = analyzer.detect_ecg_change_points(ecg_data)
    print(f"🎯 检测到变化点: {len(change_points)}个")
    
    # 执行分段分析
    if mode == "pathophysiologic":
        segmentation_result = analyzer.analyze_pathophysiologic_segments(ecg_data, change_points)
    elif mode == "clinical_event":
        segmentation_result = analyzer.analyze_clinical_event_segments(ecg_data)
    else:
        segmentation_result = analyzer.analyze_pathophysiologic_segments(ecg_data, change_points)
    
    # 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "报告头信息": {
            "报告类型": "ECG智能分段分析报告 v1.0",
            "患者ID": patient_id,
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "分段模式": analyzer.segmentation_modes.get(mode, mode),
            "采样率": f"{sampling_rate}Hz"
        },
        "数据状态分析": data_status,
        "变化点检测": {
            "检测到的变化点": len(change_points),
            "变化点详情": change_points
        },
        "智能分段结果": segmentation_result
    }
    
    # 保存报告
    filename = f"ECG_Segmentation_Analysis_{patient_id}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print("📊 ECG智能分段分析完成")
    print(f"📝 分段数量: {segmentation_result['分段数量']}")
    print(f"📄 分析报告已保存: {filename}")
    
    return report

# 示例使用
if __name__ == "__main__":
    # 生成示例ECG数据
    duration = 300  # 5分钟
    sampling_rate = 500
    t = np.linspace(0, duration, duration * sampling_rate)
    
    # 模拟包含心律失常的ECG信号
    ecg_signal = np.zeros_like(t)
    
    # 正常窦性心律阶段 (0-180秒)
    for beat_time in np.arange(0, 180, 0.857):  # 70 bpm
        beat_idx = int(beat_time * sampling_rate)
        if beat_idx < len(ecg_signal) - 100:
            qrs_duration = int(0.1 * sampling_rate)
            qrs_wave = signal.gaussian(qrs_duration, std=qrs_duration//8)
            end_idx = min(beat_idx + qrs_duration, len(ecg_signal))
            ecg_signal[beat_idx:end_idx] += qrs_wave[:end_idx-beat_idx]
    
    # 心动过速阶段 (180-240秒)  
    for beat_time in np.arange(180, 240, 0.5):  # 120 bpm
        beat_idx = int(beat_time * sampling_rate)
        if beat_idx < len(ecg_signal) - 100:
            qrs_duration = int(0.08 * sampling_rate)
            qrs_wave = signal.gaussian(qrs_duration, std=qrs_duration//10) * 1.2
            end_idx = min(beat_idx + qrs_duration, len(ecg_signal))
            ecg_signal[beat_idx:end_idx] += qrs_wave[:end_idx-beat_idx]
    
    # 恢复期 (240-300秒)
    for beat_time in np.arange(240, 300, 0.8):  # 75 bpm
        beat_idx = int(beat_time * sampling_rate)
        if beat_idx < len(ecg_signal) - 100:
            qrs_duration = int(0.1 * sampling_rate)
            qrs_wave = signal.gaussian(qrs_duration, std=qrs_duration//8) * 0.9
            end_idx = min(beat_idx + qrs_duration, len(ecg_signal))
            ecg_signal[beat_idx:end_idx] += qrs_wave[:end_idx-beat_idx]
    
    # 添加噪声
    noise = np.random.normal(0, 0.05, len(ecg_signal))
    ecg_signal += noise
    
    # 执行分析
    result = analyze_ecg_segmentation(ecg_signal, "Demo_Patient_ECG", "auto", sampling_rate)
    
    print("\n🎯 ECG分段演示分析完成！")