#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HRV_Segmentation_Analyzer.py

HRV智能分段分析器 - 基于Agent2 v5.0智能分段架构
专门用于HRV数据的训练阶段识别、恢复状态分段和自主神经功能演变分析

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

class HRVDataStatus(Enum):
    """HRV数据状态"""
    TRAINING = "training"          # 训练监测数据
    RECOVERY = "recovery"          # 恢复监测数据
    CLINICAL = "clinical"          # 临床监测数据
    RESEARCH = "research"          # 科研数据
    REALTIME = "realtime"          # 实时监测

class HRVSegmentationAnalyzer:
    """HRV智能分段分析器"""
    
    def __init__(self):
        self.segmentation_modes = {
            'auto': '智能自动选择',
            'training_phases': '训练阶段分段',
            'recovery_monitoring': '恢复监测分段',
            'circadian_rhythm': '昼夜节律分段',
            'autonomic_balance': '自主神经平衡分段',
            'dual': '双模式分析'
        }
        
        # HRV变化显著性阈值
        self.change_thresholds = {
            'RMSSD': 15,      # ms
            'LF_HF_ratio': 0.5,
            'heart_rate': 10   # bpm
        }
    
    def detect_data_status(self, rr_intervals, timestamps=None, context_info=None):
        """智能检测HRV数据状态"""
        try:
            duration_hours = len(rr_intervals) * np.mean(rr_intervals) / 1000 / 3600
            mean_hr = 60000 / np.mean(rr_intervals)
            
            # 基于上下文信息判断
            if context_info:
                if 'training' in context_info.lower() or 'exercise' in context_info.lower():
                    data_status = HRVDataStatus.TRAINING
                elif 'recovery' in context_info.lower() or 'rest' in context_info.lower():
                    data_status = HRVDataStatus.RECOVERY
                elif 'clinical' in context_info.lower() or 'patient' in context_info.lower():
                    data_status = HRVDataStatus.CLINICAL
                else:
                    data_status = HRVDataStatus.RESEARCH
            else:
                # 基于数据特征自动判断
                if duration_hours < 2 and mean_hr > 90:
                    data_status = HRVDataStatus.TRAINING
                elif duration_hours < 8 and mean_hr < 70:
                    data_status = HRVDataStatus.RECOVERY
                elif duration_hours >= 20:
                    data_status = HRVDataStatus.CLINICAL
                else:
                    data_status = HRVDataStatus.RESEARCH
            
            return {
                "数据状态": data_status.value,
                "数据时长": f"{duration_hours:.1f}小时",
                "数据点数": len(rr_intervals),
                "平均心率": f"{mean_hr:.1f} bpm",
                "推荐分段模式": self.recommend_segmentation_mode(data_status)
            }
        except:
            return {
                "数据状态": HRVDataStatus.RESEARCH.value,
                "推荐分段模式": "autonomic_balance"
            }
    
    def recommend_segmentation_mode(self, data_status):
        """根据数据状态推荐分段模式"""
        recommendations = {
            HRVDataStatus.TRAINING: "training_phases",      # 训练数据关注训练阶段
            HRVDataStatus.RECOVERY: "recovery_monitoring",  # 恢复数据关注恢复阶段
            HRVDataStatus.CLINICAL: "circadian_rhythm",     # 临床数据关注昼夜节律
            HRVDataStatus.RESEARCH: "autonomic_balance",    # 科研数据关注自主神经
            HRVDataStatus.REALTIME: "dual"                  # 实时数据双模式分析
        }
        return recommendations.get(data_status, "autonomic_balance")
    
    def extract_hrv_features_windowed(self, rr_intervals, window_size_minutes=5):
        """提取滑动窗口HRV特征"""
        window_size_beats = int(window_size_minutes * 60 / (np.mean(rr_intervals) / 1000))
        window_size_beats = max(50, min(window_size_beats, len(rr_intervals) // 10))
        
        features = []
        
        for i in range(0, len(rr_intervals) - window_size_beats, window_size_beats // 4):
            window_rr = rr_intervals[i:i + window_size_beats]
            
            if len(window_rr) < 20:
                continue
            
            # 时域HRV指标
            rmssd = np.sqrt(np.mean(np.diff(window_rr) ** 2))
            sdnn = np.std(window_rr)
            pnn50 = (np.sum(np.abs(np.diff(window_rr)) > 50) / (len(window_rr) - 1)) * 100
            mean_hr = 60000 / np.mean(window_rr)
            
            # 频域HRV指标 (简化版本)
            try:
                # 插值到等间隔时间序列
                time_points = np.cumsum(window_rr) / 1000
                time_uniform = np.arange(0, time_points[-1], 0.25)  # 4Hz采样
                rr_interpolated = np.interp(time_uniform, time_points[:-1], window_rr[:-1])
                
                # 功率谱密度
                f, psd = signal.welch(signal.detrend(rr_interpolated), fs=4, nperseg=min(64, len(rr_interpolated)))
                
                lf_mask = (f >= 0.04) & (f < 0.15)
                hf_mask = (f >= 0.15) & (f < 0.4)
                
                lf_power = np.sum(psd[lf_mask])
                hf_power = np.sum(psd[hf_mask])
                lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0
            except:
                lf_hf_ratio = 0
            
            # 复杂性指标
            complexity = self.calculate_simple_complexity(window_rr)
            
            feature_dict = {
                'start_beat': i,
                'window_center_time_min': (i + window_size_beats // 2) * np.mean(rr_intervals) / 1000 / 60,
                'RMSSD': rmssd,
                'SDNN': sdnn,
                'pNN50': pnn50,
                'mean_HR': mean_hr,
                'LF_HF_ratio': lf_hf_ratio,
                'complexity': complexity
            }
            
            features.append(feature_dict)
        
        return features
    
    def calculate_simple_complexity(self, rr_intervals):
        """计算简单的复杂性指标"""
        try:
            if len(rr_intervals) < 10:
                return 0
            
            # 基于相邻RR间期差值的变异性
            diff_rr = np.diff(rr_intervals)
            complexity = np.std(diff_rr) / np.mean(rr_intervals) if np.mean(rr_intervals) > 0 else 0
            return complexity
        except:
            return 0
    
    def detect_hrv_change_points(self, features, method='multi_parameter'):
        """HRV变化点检测"""
        change_points = []
        
        if len(features) < 6:
            return change_points
        
        if method == 'multi_parameter':
            change_points = self.multi_parameter_change_detection(features)
        elif method == 'autonomic_balance':
            change_points = self.autonomic_balance_change_detection(features)
        else:
            change_points = self.training_phase_detection(features)
        
        return change_points
    
    def multi_parameter_change_detection(self, features):
        """多参数HRV变化点检测"""
        change_points = []
        
        # 提取关键参数序列
        rmssd_series = [f['RMSSD'] for f in features]
        hr_series = [f['mean_HR'] for f in features]
        lf_hf_series = [f['LF_HF_ratio'] for f in features]
        
        # 滑动窗口统计检验
        window_size = 5
        for i in range(window_size, len(features) - window_size):
            
            # RMSSD变化检测
            before_rmssd = np.mean(rmssd_series[i-window_size:i])
            after_rmssd = np.mean(rmssd_series[i:i+window_size])
            rmssd_change = abs(after_rmssd - before_rmssd)
            
            # 心率变化检测
            before_hr = np.mean(hr_series[i-window_size:i])
            after_hr = np.mean(hr_series[i:i+window_size])
            hr_change = abs(after_hr - before_hr)
            
            # LF/HF比值变化检测
            before_lf_hf = np.mean(lf_hf_series[i-window_size:i])
            after_lf_hf = np.mean(lf_hf_series[i:i+window_size])
            lf_hf_change = abs(after_lf_hf - before_lf_hf)
            
            # 判断是否为显著变化点
            significant_changes = 0
            change_details = []
            
            if rmssd_change > self.change_thresholds['RMSSD']:
                significant_changes += 1
                change_details.append(f"RMSSD变化{rmssd_change:.1f}ms")
            
            if hr_change > self.change_thresholds['heart_rate']:
                significant_changes += 1
                change_details.append(f"心率变化{hr_change:.1f}bpm")
            
            if lf_hf_change > self.change_thresholds['LF_HF_ratio']:
                significant_changes += 1
                change_details.append(f"LF/HF变化{lf_hf_change:.2f}")
            
            if significant_changes >= 2:
                change_point = {
                    'feature_index': i,
                    'time_minutes': features[i]['window_center_time_min'],
                    'significance_score': significant_changes,
                    'change_type': self.classify_hrv_change_type(features[i-1], features[i]),
                    'change_details': change_details
                }
                change_points.append(change_point)
        
        return change_points
    
    def classify_hrv_change_type(self, before_features, after_features):
        """分类HRV变化类型"""
        hr_change = after_features['mean_HR'] - before_features['mean_HR']
        rmssd_change = after_features['RMSSD'] - before_features['RMSSD']
        lf_hf_change = after_features['LF_HF_ratio'] - before_features['LF_HF_ratio']
        
        if hr_change > 20:
            return "心率上升阶段"
        elif hr_change < -20:
            return "心率下降阶段"
        elif rmssd_change > 15:
            return "副交感激活"
        elif rmssd_change < -15:
            return "副交感抑制"
        elif lf_hf_change > 1.0:
            return "交感神经激活"
        elif lf_hf_change < -1.0:
            return "交感神经抑制"
        else:
            return "综合调节变化"
    
    def analyze_training_phases(self, rr_intervals, change_points):
        """训练阶段分段分析"""
        if not change_points:
            # 默认训练三阶段：热身-主训练-恢复
            segments = self.create_training_default_segments(rr_intervals)
        else:
            segments = self.create_training_adaptive_segments(rr_intervals, change_points)
        
        return {
            "分段模式": "训练阶段分段",
            "分段数量": len(segments),
            "分段详情": segments,
            "临床应用": "适用于运动员训练监测和运动处方制定"
        }
    
    def create_training_default_segments(self, rr_intervals):
        """创建默认训练阶段分段"""
        total_duration_min = len(rr_intervals) * np.mean(rr_intervals) / 1000 / 60
        
        segments = []
        
        if total_duration_min <= 30:  # 短时训练
            # 热身 (前20%)，主训练 (中60%)，恢复 (后20%)
            boundaries = [0, int(0.2 * len(rr_intervals)), 
                         int(0.8 * len(rr_intervals)), len(rr_intervals)]
            phase_names = ["热身阶段", "主训练阶段", "即时恢复"]
        elif total_duration_min <= 90:  # 中等训练
            # 热身，主训练1，主训练2，恢复
            boundaries = [0, int(0.15 * len(rr_intervals)), int(0.5 * len(rr_intervals)),
                         int(0.8 * len(rr_intervals)), len(rr_intervals)]
            phase_names = ["热身阶段", "主训练阶段1", "主训练阶段2", "恢复阶段"]
        else:  # 长时训练
            # 更详细的分段
            boundaries = [0, int(0.1 * len(rr_intervals)), int(0.3 * len(rr_intervals)),
                         int(0.7 * len(rr_intervals)), int(0.9 * len(rr_intervals)), len(rr_intervals)]
            phase_names = ["热身", "训练强化1", "训练强化2", "训练维持", "恢复"]
        
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            segment_rr = rr_intervals[start_idx:end_idx]
            
            segments.append({
                "阶段编号": i + 1,
                "阶段名称": phase_names[i] if i < len(phase_names) else f"阶段{i+1}",
                "开始时间": f"{start_idx * np.mean(rr_intervals) / 1000 / 60:.1f}分钟",
                "持续时间": f"{len(segment_rr) * np.mean(segment_rr) / 1000 / 60:.1f}分钟",
                "训练特征": self.analyze_training_segment(segment_rr)
            })
        
        return segments
    
    def analyze_training_segment(self, segment_rr):
        """分析训练分段特征"""
        try:
            mean_hr = 60000 / np.mean(segment_rr)
            rmssd = np.sqrt(np.mean(np.diff(segment_rr) ** 2))
            
            # 训练强度评估
            if mean_hr >= 150:
                intensity = "高强度"
                zone = "无氧阈以上"
            elif mean_hr >= 130:
                intensity = "中高强度"
                zone = "有氧-无氧混合区"
            elif mean_hr >= 110:
                intensity = "中等强度"
                zone = "有氧区"
            elif mean_hr >= 90:
                intensity = "低中强度"
                zone = "脂肪燃烧区"
            else:
                intensity = "低强度"
                zone = "恢复区"
            
            # 自主神经状态
            if rmssd >= 40:
                autonomic_state = "副交感主导"
            elif rmssd >= 20:
                autonomic_state = "平衡状态"
            else:
                autonomic_state = "交感主导"
            
            return {
                "平均心率": f"{mean_hr:.1f} bpm",
                "训练强度": intensity,
                "心率区间": zone,
                "HRV(RMSSD)": f"{rmssd:.1f} ms",
                "自主神经状态": autonomic_state,
                "训练适应性": self.assess_training_adaptation(mean_hr, rmssd)
            }
        except:
            return {"评估": "数据不足"}
    
    def assess_training_adaptation(self, mean_hr, rmssd):
        """评估训练适应性"""
        # 基于心率和HRV的简化评估
        if mean_hr < 70 and rmssd > 50:
            return "优秀适应性"
        elif mean_hr < 80 and rmssd > 35:
            return "良好适应性"
        elif mean_hr < 90 and rmssd > 25:
            return "一般适应性"
        elif mean_hr > 100 and rmssd < 15:
            return "疲劳状态"
        else:
            return "需要评估"
    
    def analyze_recovery_monitoring(self, rr_intervals, change_points):
        """恢复监测分段分析"""
        segments = self.create_recovery_segments(rr_intervals, change_points)
        
        return {
            "分段模式": "恢复监测分段",
            "分段数量": len(segments),
            "分段详情": segments,
            "临床应用": "适用于运动恢复监测和疲劳评估"
        }
    
    def create_recovery_segments(self, rr_intervals, change_points):
        """创建恢复阶段分段"""
        total_duration_min = len(rr_intervals) * np.mean(rr_intervals) / 1000 / 60
        
        if not change_points or total_duration_min < 60:
            # 默认恢复阶段：即时恢复-快速恢复-慢速恢复-稳定期
            if total_duration_min <= 30:
                boundaries = [0, len(rr_intervals) // 3, 2 * len(rr_intervals) // 3, len(rr_intervals)]
                phase_names = ["即时恢复", "快速恢复", "趋向稳定"]
            else:
                boundaries = [0, len(rr_intervals) // 4, len(rr_intervals) // 2, 
                             3 * len(rr_intervals) // 4, len(rr_intervals)]
                phase_names = ["即时恢复", "快速恢复", "慢速恢复", "稳定期"]
        else:
            # 基于变化点的自适应分段
            boundaries = [0] + [cp['feature_index'] * 4 for cp in change_points if cp['feature_index'] * 4 < len(rr_intervals)] + [len(rr_intervals)]
            boundaries = sorted(list(set(boundaries)))
            phase_names = [f"恢复阶段{i+1}" for i in range(len(boundaries)-1)]
        
        segments = []
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            segment_rr = rr_intervals[start_idx:end_idx]
            
            segments.append({
                "恢复阶段": i + 1,
                "阶段名称": phase_names[i] if i < len(phase_names) else f"恢复{i+1}",
                "开始时间": f"{start_idx * np.mean(rr_intervals) / 1000 / 60:.1f}分钟",
                "持续时间": f"{len(segment_rr) * np.mean(segment_rr) / 1000 / 60:.1f}分钟",
                "恢复特征": self.analyze_recovery_segment(segment_rr)
            })
        
        return segments
    
    def analyze_recovery_segment(self, segment_rr):
        """分析恢复分段特征"""
        try:
            mean_hr = 60000 / np.mean(segment_rr)
            rmssd = np.sqrt(np.mean(np.diff(segment_rr) ** 2))
            hrv_trend = self.calculate_hrv_trend(segment_rr)
            
            # 恢复质量评估
            if mean_hr <= 70 and rmssd >= 40:
                recovery_quality = "优秀恢复"
            elif mean_hr <= 80 and rmssd >= 30:
                recovery_quality = "良好恢复"
            elif mean_hr <= 90 and rmssd >= 20:
                recovery_quality = "一般恢复"
            elif mean_hr > 100 or rmssd < 15:
                recovery_quality = "恢复不足"
            else:
                recovery_quality = "需要评估"
            
            return {
                "平均心率": f"{mean_hr:.1f} bpm",
                "HRV(RMSSD)": f"{rmssd:.1f} ms", 
                "HRV趋势": hrv_trend,
                "恢复质量": recovery_quality,
                "建议": self.generate_recovery_recommendation(mean_hr, rmssd, recovery_quality)
            }
        except:
            return {"评估": "数据不足"}
    
    def calculate_hrv_trend(self, segment_rr):
        """计算HRV趋势"""
        if len(segment_rr) < 100:
            return "数据不足"
        
        # 分为前半段和后半段比较
        mid_point = len(segment_rr) // 2
        first_half_rmssd = np.sqrt(np.mean(np.diff(segment_rr[:mid_point]) ** 2))
        second_half_rmssd = np.sqrt(np.mean(np.diff(segment_rr[mid_point:]) ** 2))
        
        rmssd_change = second_half_rmssd - first_half_rmssd
        
        if rmssd_change > 5:
            return "HRV上升"
        elif rmssd_change < -5:
            return "HRV下降"
        else:
            return "HRV稳定"
    
    def generate_recovery_recommendation(self, mean_hr, rmssd, recovery_quality):
        """生成恢复建议"""
        if recovery_quality == "优秀恢复":
            return "恢复充分，可进行下一阶段训练"
        elif recovery_quality == "良好恢复":
            return "恢复良好，建议适度训练"
        elif recovery_quality == "一般恢复":
            return "恢复一般，建议降低训练强度"
        else:
            return "恢复不足，建议延长休息时间"

def analyze_hrv_segmentation(rr_intervals, patient_id="Unknown", mode="auto", context_info=None):
    """HRV智能分段分析主函数"""
    
    print(f"💓 HRV智能分段分析启动 - 患者ID: {patient_id}")
    print(f"🔧 分段模式: {mode}")
    if context_info:
        print(f"📝 上下文信息: {context_info}")
    print("="*60)
    
    # 初始化分析器
    analyzer = HRVSegmentationAnalyzer()
    
    # 检测数据状态
    data_status = analyzer.detect_data_status(rr_intervals, context_info=context_info)
    print(f"📊 数据状态: {data_status['数据状态']}")
    print(f"⏱️  数据时长: {data_status['数据时长']}")
    print(f"💗 平均心率: {data_status['平均心率']}")
    
    # 智能模式选择
    if mode == "auto":
        mode = data_status['推荐分段模式']
        print(f"🧠 智能推荐模式: {mode}")
    
    # 提取HRV特征
    hrv_features = analyzer.extract_hrv_features_windowed(rr_intervals)
    print(f"📈 提取了 {len(hrv_features)} 个HRV特征窗口")
    
    # 检测变化点
    change_points = analyzer.detect_hrv_change_points(hrv_features)
    print(f"🎯 检测到变化点: {len(change_points)}个")
    
    # 执行分段分析
    if mode == "training_phases":
        segmentation_result = analyzer.analyze_training_phases(rr_intervals, change_points)
    elif mode == "recovery_monitoring":
        segmentation_result = analyzer.analyze_recovery_monitoring(rr_intervals, change_points)
    else:
        # 默认使用训练阶段分析
        segmentation_result = analyzer.analyze_training_phases(rr_intervals, change_points)
    
    # 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "报告头信息": {
            "报告类型": "HRV智能分段分析报告 v1.0",
            "患者ID": patient_id,
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "分段模式": analyzer.segmentation_modes.get(mode, mode),
            "上下文信息": context_info or "无"
        },
        "数据状态分析": data_status,
        "HRV特征分析": {
            "特征窗口数": len(hrv_features),
            "平均RMSSD": f"{np.mean([f['RMSSD'] for f in hrv_features]):.1f} ms",
            "平均心率": f"{np.mean([f['mean_HR'] for f in hrv_features]):.1f} bpm"
        },
        "变化点检测": {
            "检测到的变化点": len(change_points),
            "变化点详情": change_points
        },
        "智能分段结果": segmentation_result
    }
    
    # 保存报告
    filename = f"HRV_Segmentation_Analysis_{patient_id}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print("📊 HRV智能分段分析完成")
    print(f"📝 分段数量: {segmentation_result['分段数量']}")
    print(f"📄 分析报告已保存: {filename}")
    
    return report

# 示例使用
if __name__ == "__main__":
    # 生成示例训练HRV数据
    np.random.seed(42)
    
    # 模拟60分钟训练的RR间期数据
    # 热身(0-10min) -> 主训练(10-45min) -> 恢复(45-60min)
    
    total_minutes = 60
    avg_beats_per_minute = 80  # 平均心率约80bpm
    total_beats = total_minutes * avg_beats_per_minute
    
    rr_intervals = []
    
    for minute in range(total_minutes):
        if minute < 10:  # 热身阶段
            target_hr = 70 + minute * 2  # 70-88 bpm
            base_rr = 60000 / target_hr
            # 较高的HRV (副交感神经还有活性)
            rr_variation = np.random.normal(0, 40, avg_beats_per_minute)
        elif minute < 45:  # 主训练阶段
            progress = (minute - 10) / 35
            target_hr = 90 + progress * 40  # 90-130 bpm
            base_rr = 60000 / target_hr
            # 低HRV (交感神经主导)
            rr_variation = np.random.normal(0, 15, avg_beats_per_minute)
        else:  # 恢复阶段
            recovery_progress = (minute - 45) / 15
            target_hr = 130 - recovery_progress * 40  # 130降到90 bpm
            base_rr = 60000 / target_hr
            # 逐渐增加的HRV (副交感神经恢复)
            rr_var_std = 15 + recovery_progress * 25  # 15增加到40
            rr_variation = np.random.normal(0, rr_var_std, avg_beats_per_minute)
        
        # 生成该分钟的RR间期
        minute_rr = base_rr + rr_variation
        minute_rr = np.clip(minute_rr, 400, 1500)  # 限制在合理范围
        rr_intervals.extend(minute_rr)
    
    rr_intervals = np.array(rr_intervals[:total_beats])  # 确保总数据点数正确
    
    print(f"生成了 {len(rr_intervals)} 个训练RR间期数据")
    print(f"训练时长: {len(rr_intervals) * np.mean(rr_intervals) / 1000 / 60:.1f} 分钟")
    print(f"平均心率: {60000 / np.mean(rr_intervals):.1f} bpm")
    print(f"心率范围: {60000 / np.max(rr_intervals):.1f} - {60000 / np.min(rr_intervals):.1f} bpm")
    
    # 执行分析
    result = analyze_hrv_segmentation(
        rr_intervals, 
        "Demo_Athlete_001", 
        "auto",
        "运动员间歇训练监测"
    )
    
    print("\n🎯 HRV训练分段演示分析完成！")