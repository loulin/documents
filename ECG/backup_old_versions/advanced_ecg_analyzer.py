#!/usr/bin/env python3
"""
高级ECG数据分析器
改进版本：既支持专业库也支持基础环境
专门用于分析PhysioNet WFDB格式的12导联ECG数据
支持批量分析和详细心电图特征提取
"""

import struct
import os
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import warnings
import math
from scipy import signal
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

def parse_header_file(header_path):
    """解析.hea头文件获取记录信息"""
    info = {}
    leads = []
    
    try:
        with open(header_path, 'r') as f:
            lines = f.readlines()
        
        # 第一行包含基本信息
        first_line = lines[0].strip().split()
        info['record_name'] = first_line[0]
        info['num_leads'] = int(first_line[1])
        info['sampling_rate'] = int(first_line[2])
        info['num_samples'] = int(first_line[3])
        
        # 解析导联信息和增益
        gains = []
        baselines = []
        for i in range(1, info['num_leads'] + 1):
            lead_line = lines[i].strip().split()
            lead_name = lead_line[-1]  # 导联名称在最后
            gain_str = lead_line[2]  # 增益信息 "1000/mV"
            gain = float(gain_str.split('/')[0])
            baseline = int(lead_line[4]) if len(lead_line) > 4 else 0
            
            leads.append(lead_name)
            gains.append(gain)
            baselines.append(baseline)
        
        info['leads'] = leads
        info['gains'] = gains
        info['baselines'] = baselines
        
        # 解析患者信息
        for line in lines:
            line = line.strip()
            if line.startswith('#Age:'):
                info['age'] = line.split(': ')[1]
            elif line.startswith('#Sex:'):
                info['sex'] = line.split(': ')[1]
            elif line.startswith('#Dx:'):
                info['diagnosis'] = line.split(': ')[1]
        
        return info
        
    except Exception as e:
        print(f"解析头文件错误: {e}")
        return None

def read_mat_file(mat_path, num_leads, num_samples):
    """读取.mat二进制数据文件"""
    try:
        with open(mat_path, 'rb') as f:
            data = f.read()
        
        num_values = len(data) // 2
        values = struct.unpack(f'<{num_values}h', data)
        
        expected_values = num_leads * num_samples
        
        if num_values > expected_values:
            extra = num_values - expected_values
            print(f"跳过 {extra} 个额外值（文件头）")
            signal_values = values[extra:]
            if len(signal_values) == expected_values:
                signal_data = np.array(signal_values).reshape(num_samples, num_leads)
            else:
                return None
        else:
            signal_data = np.array(values).reshape(num_samples, num_leads)
        
        return signal_data
        
    except Exception as e:
        print(f"读取数据文件错误: {e}")
        return None

def convert_to_physical_units(signal_data, gains, baselines):
    """将数字信号转换为物理单位(mV)"""
    try:
        physical_data = np.zeros_like(signal_data, dtype=float)
        for i in range(len(gains)):
            # 转换公式: physical = (digital - baseline) / gain
            physical_data[:, i] = (signal_data[:, i] - baselines[i]) / gains[i]
        return physical_data
    except Exception as e:
        print(f"单位转换错误: {e}")
        return signal_data.astype(float)

def advanced_r_peak_detection(ecg_signal, sampling_rate):
    """改进的R峰检测算法"""
    try:
        # 1. 带通滤波 (5-15Hz，突出QRS复合波)
        nyquist = sampling_rate / 2
        low_cutoff = 5 / nyquist
        high_cutoff = 15 / nyquist
        
        # 使用Butterworth滤波器
        b, a = signal.butter(4, [low_cutoff, high_cutoff], btype='band')
        filtered_signal = signal.filtfilt(b, a, ecg_signal)
        
        # 2. 微分操作（突出QRS斜率）
        diff_signal = np.diff(filtered_signal)
        
        # 3. 平方操作（放大大的变化）
        squared_signal = diff_signal ** 2
        
        # 4. 移动窗口积分
        window_size = int(sampling_rate * 0.08)  # 80ms窗口
        integrated_signal = np.convolve(squared_signal, np.ones(window_size), mode='same')
        
        # 5. 自适应阈值检测
        threshold = np.mean(integrated_signal) + 2 * np.std(integrated_signal)
        
        # 6. 峰值检测
        peaks = []
        min_distance = int(sampling_rate * 0.4)  # 最小RR间期400ms
        
        for i in range(min_distance, len(integrated_signal) - min_distance):
            if (integrated_signal[i] > threshold and
                integrated_signal[i] == np.max(integrated_signal[i-min_distance//2:i+min_distance//2])):
                # 在原始信号中精确定位R峰
                search_window = slice(max(0, i-20), min(len(ecg_signal), i+20))
                local_peak = i - 20 + np.argmax(np.abs(ecg_signal[search_window]))
                
                if not peaks or (local_peak - peaks[-1]) >= min_distance:
                    peaks.append(local_peak)
        
        return peaks
        
    except Exception as e:
        print(f"高级R峰检测错误，使用简单算法: {e}")
        return simple_r_peak_detection(ecg_signal, sampling_rate)

def simple_r_peak_detection(ecg_signal, sampling_rate):
    """简单的R峰检测算法（备用）"""
    try:
        signal_array = np.array(ecg_signal, dtype=float)
        
        # 去除基线漂移
        window_size = int(sampling_rate * 0.2)
        baseline = np.convolve(signal_array, np.ones(window_size)/window_size, mode='same')
        signal_filtered = signal_array - baseline
        
        # 阈值检测
        threshold = np.std(signal_filtered) * 2.0
        peaks = []
        min_distance = int(sampling_rate * 0.3)
        
        for i in range(min_distance, len(signal_filtered) - min_distance):
            if (signal_filtered[i] > threshold and 
                signal_filtered[i] > signal_filtered[i-1] and 
                signal_filtered[i] > signal_filtered[i+1]):
                
                if not peaks or (i - peaks[-1]) >= min_distance:
                    peaks.append(i)
        
        return peaks
        
    except Exception as e:
        print(f"简单R峰检测错误: {e}")
        return []

def calculate_advanced_hrv_metrics(r_peaks, sampling_rate):
    """计算高级HRV指标"""
    if len(r_peaks) < 3:
        return {}
    
    # RR间期（毫秒）
    rr_intervals = np.diff(r_peaks) / sampling_rate * 1000
    
    # 时域指标
    metrics = {
        'mean_rr': np.mean(rr_intervals),
        'std_rr': np.std(rr_intervals),  # SDNN
        'min_rr': np.min(rr_intervals),
        'max_rr': np.max(rr_intervals),
        'mean_hr': 60000 / np.mean(rr_intervals),
        'std_hr': np.std(60000 / rr_intervals)
    }
    
    # 高级时域指标
    if len(rr_intervals) > 1:
        diff_rr = np.diff(rr_intervals)
        metrics['rmssd'] = np.sqrt(np.mean(diff_rr ** 2))
        
        # pNN50 和 pNN20
        nn50 = np.sum(np.abs(diff_rr) > 50)
        nn20 = np.sum(np.abs(diff_rr) > 20)
        metrics['pnn50'] = (nn50 / len(diff_rr)) * 100
        metrics['pnn20'] = (nn20 / len(diff_rr)) * 100
        
        # 三角指数（近似）
        hist, _ = np.histogram(rr_intervals, bins=32)
        metrics['triangular_index'] = len(rr_intervals) / np.max(hist) if np.max(hist) > 0 else 0
        
        # TINN（近似）
        metrics['tinn'] = np.max(rr_intervals) - np.min(rr_intervals)
    
    # 几何指标
    metrics['cv'] = (metrics['std_rr'] / metrics['mean_rr']) * 100  # 变异系数
    
    return metrics

def analyze_signal_quality(ecg_signal, sampling_rate):
    """分析信号质量"""
    try:
        # 信噪比估计
        signal_power = np.mean(ecg_signal ** 2)
        noise_estimate = np.mean(np.diff(ecg_signal) ** 2)  # 简单噪声估计
        snr = 10 * np.log10(signal_power / noise_estimate) if noise_estimate > 0 else float('inf')
        
        # 基线漂移检测
        low_freq_content = np.mean(np.abs(ecg_signal[:int(sampling_rate)]))
        baseline_drift = low_freq_content / np.mean(np.abs(ecg_signal))
        
        # 饱和度检测
        max_val = np.max(np.abs(ecg_signal))
        saturation = np.sum(np.abs(ecg_signal) > 0.95 * max_val) / len(ecg_signal)
        
        quality = {
            'snr_db': snr,
            'baseline_drift_ratio': baseline_drift,
            'saturation_ratio': saturation * 100,
            'dynamic_range': np.max(ecg_signal) - np.min(ecg_signal)
        }
        
        return quality
        
    except Exception as e:
        print(f"信号质量分析错误: {e}")
        return {}

def analyze_single_record_advanced(record_name, data_dir):
    """高级分析单个ECG记录"""
    print(f"\n=== 高级分析记录: {record_name} ===")
    
    header_path = os.path.join(data_dir, f"{record_name}.hea")
    mat_path = os.path.join(data_dir, f"{record_name}.mat")
    
    # 解析头文件
    header_info = parse_header_file(header_path)
    if not header_info:
        return None
    
    print(f"导联数: {header_info['num_leads']}")
    print(f"采样率: {header_info['sampling_rate']} Hz")
    print(f"时长: {header_info['num_samples'] / header_info['sampling_rate']:.1f}秒")
    print(f"导联: {header_info['leads']}")
    
    # 读取数据
    signal_data = read_mat_file(mat_path, header_info['num_leads'], header_info['num_samples'])
    if signal_data is None:
        return None
    
    # 转换为物理单位
    physical_data = convert_to_physical_units(signal_data, header_info['gains'], header_info['baselines'])
    
    # 分析所有导联
    lead_analyses = {}
    for i, lead_name in enumerate(header_info['leads']):
        ecg_signal = physical_data[:, i]
        
        # 信号质量分析
        quality = analyze_signal_quality(ecg_signal, header_info['sampling_rate'])
        
        # R峰检测
        r_peaks = advanced_r_peak_detection(ecg_signal, header_info['sampling_rate'])
        
        # HRV分析
        hrv_metrics = calculate_advanced_hrv_metrics(r_peaks, header_info['sampling_rate'])
        
        lead_analyses[lead_name] = {
            'r_peaks_count': len(r_peaks),
            'quality': quality,
            **hrv_metrics
        }
        
        print(f"导联 {lead_name}: {len(r_peaks)}个R峰, SNR: {quality.get('snr_db', 0):.1f}dB")
    
    # 选择最佳导联进行主要分析（基于信号质量）
    best_lead = max(lead_analyses.keys(), 
                   key=lambda x: lead_analyses[x]['quality'].get('snr_db', 0))
    
    print(f"最佳分析导联: {best_lead}")
    
    # 整合结果
    result = {
        'record_name': record_name,
        'num_leads': header_info['num_leads'],
        'sampling_rate': header_info['sampling_rate'],
        'duration_sec': header_info['num_samples'] / header_info['sampling_rate'],
        'best_lead': best_lead,
        **{k: v for k, v in header_info.items() if k in ['age', 'sex', 'diagnosis']},
        **lead_analyses[best_lead]
    }
    
    # 添加多导联统计
    all_r_peaks = [lead_analyses[lead]['r_peaks_count'] for lead in header_info['leads']]
    result['mean_r_peaks_across_leads'] = np.mean(all_r_peaks)
    result['r_peaks_consistency'] = 1 - (np.std(all_r_peaks) / np.mean(all_r_peaks)) if np.mean(all_r_peaks) > 0 else 0
    
    print("✅ 高级分析完成")
    return result

def analyze_directory_advanced(data_dir, output_file=None):
    """批量高级分析目录中的所有ECG记录"""
    print(f"🔍 高级分析目录: {data_dir}")
    
    # 读取RECORDS文件
    records_file = os.path.join(data_dir, 'RECORDS')
    if not os.path.exists(records_file):
        print("❌ 未找到RECORDS文件")
        return None
    
    with open(records_file, 'r') as f:
        record_names = [line.strip() for line in f if line.strip()]
    
    print(f"找到 {len(record_names)} 个记录")
    
    # 分析所有记录
    results = []
    successful = 0
    
    for i, record_name in enumerate(record_names, 1):
        print(f"\n进度: {i}/{len(record_names)}")
        result = analyze_single_record_advanced(record_name, data_dir)
        
        if result:
            results.append(result)
            successful += 1
    
    if results:
        df = pd.DataFrame(results)
        
        if output_file is None:
            output_file = os.path.join(data_dir, 'advanced_ecg_analysis_results.csv')
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n📊 高级分析结果已保存到: {output_file}")
        print(f"✅ 成功分析: {successful}/{len(record_names)} 个记录")
        
        # 高级统计摘要
        print(f"\n📈 高级分析摘要:")
        print(f"平均心率: {df['mean_hr'].mean():.1f} ± {df['mean_hr'].std():.1f} BPM")
        print(f"平均SDNN: {df['std_rr'].mean():.1f} ± {df['std_rr'].std():.1f} ms")
        print(f"平均RMSSD: {df['rmssd'].mean():.1f} ± {df['rmssd'].std():.1f} ms")
        print(f"平均信噪比: {df['snr_db'].mean():.1f} ± {df['snr_db'].std():.1f} dB")
        print(f"R峰检测一致性: {df['r_peaks_consistency'].mean():.3f}")
        
        if 'triangular_index' in df.columns:
            print(f"平均三角指数: {df['triangular_index'].mean():.1f}")
        
        # 最佳导联统计
        best_leads = df['best_lead'].value_counts()
        print(f"最佳分析导联分布: {dict(best_leads)}")
        
        return df
    else:
        print("❌ 没有成功分析的记录")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="高级ECG数据分析器")
    parser.add_argument("data_dir", help="ECG数据目录路径")
    parser.add_argument("--output", "-o", help="输出CSV文件路径")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"❌ 目录不存在: {args.data_dir}")
        exit(1)
    
    # 检查scipy是否可用
    try:
        from scipy import signal
        print("🎯 使用高级信号处理功能")
    except ImportError:
        print("⚠️  未安装scipy，将使用基础算法")
    
    analyze_directory_advanced(args.data_dir, args.output)