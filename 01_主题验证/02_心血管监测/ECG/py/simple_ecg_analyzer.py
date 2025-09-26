#!/usr/bin/env python3
"""
简化版ECG数据分析器
用于分析PhysioNet WFDB格式的ECG数据，只使用基本Python库
"""

import struct
import os
import pandas as pd
import numpy as np
import argparse
from pathlib import Path

def parse_header_file(header_path):
    """
    解析.hea头文件获取记录信息
    """
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
        
        # 解析导联信息
        for i in range(1, info['num_leads'] + 1):
            lead_line = lines[i].strip().split()
            lead_name = lead_line[-1]  # 导联名称在最后
            leads.append(lead_name)
        
        info['leads'] = leads
        
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
    """
    读取.mat二进制数据文件
    """
    try:
        # WFDB格式通常使用16位有符号整数
        with open(mat_path, 'rb') as f:
            data = f.read()
        
        # 解析为16位整数
        num_values = len(data) // 2
        values = struct.unpack(f'<{num_values}h', data)  # 小端序16位有符号整数
        
        expected_values = num_leads * num_samples
        
        # 处理数据维度，可能有额外的头信息
        if num_values == expected_values:
            # 完全匹配
            signal_data = np.array(values).reshape(num_samples, num_leads)
        elif num_values > expected_values:
            # 有额外数据，可能是头信息，跳过开头的额外数据
            extra = num_values - expected_values
            print(f"跳过 {extra} 个额外值（可能是文件头）")
            signal_values = values[extra:]  # 跳过开头的额外数据
            if len(signal_values) == expected_values:
                signal_data = np.array(signal_values).reshape(num_samples, num_leads)
            else:
                print(f"跳过额外数据后仍不匹配: 期望 {expected_values}, 实际 {len(signal_values)}")
                return None
        else:
            print(f"数据不足: 期望 {expected_values}, 实际 {num_values}")
            return None
        
        return signal_data
        
    except Exception as e:
        print(f"读取数据文件错误: {e}")
        return None

def simple_r_peak_detection(ecg_signal, sampling_rate):
    """
    简单的R峰检测算法
    """
    try:
        # 简单的阈值检测
        signal = np.array(ecg_signal, dtype=float)
        
        # 去除基线漂移（移动平均）
        window_size = int(sampling_rate * 0.2)  # 200ms窗口
        baseline = np.convolve(signal, np.ones(window_size)/window_size, mode='same')
        signal_filtered = signal - baseline
        
        # 找到峰值
        threshold = np.std(signal_filtered) * 2.0
        peaks = []
        
        min_distance = int(sampling_rate * 0.3)  # 最小间距300ms
        
        for i in range(min_distance, len(signal_filtered) - min_distance):
            if (signal_filtered[i] > threshold and 
                signal_filtered[i] > signal_filtered[i-1] and 
                signal_filtered[i] > signal_filtered[i+1]):
                
                # 检查最小间距
                if not peaks or (i - peaks[-1]) >= min_distance:
                    peaks.append(i)
        
        return peaks
        
    except Exception as e:
        print(f"R峰检测错误: {e}")
        return []

def calculate_hrv_metrics(r_peaks, sampling_rate):
    """
    计算基本HRV指标
    """
    if len(r_peaks) < 3:
        return {}
    
    # 计算RR间期（毫秒）
    rr_intervals = np.diff(r_peaks) / sampling_rate * 1000
    
    # 基本统计指标
    metrics = {
        'mean_rr': np.mean(rr_intervals),
        'std_rr': np.std(rr_intervals),  # SDNN
        'min_rr': np.min(rr_intervals),
        'max_rr': np.max(rr_intervals),
        'mean_hr': 60000 / np.mean(rr_intervals),
        'std_hr': np.std(60000 / rr_intervals)
    }
    
    # RMSSD (相邻RR间期差值的均方根)
    if len(rr_intervals) > 1:
        diff_rr = np.diff(rr_intervals)
        metrics['rmssd'] = np.sqrt(np.mean(diff_rr ** 2))
        
        # pNN50 (相邻RR间期差值>50ms的比例)
        nn50 = np.sum(np.abs(diff_rr) > 50)
        metrics['pnn50'] = (nn50 / len(diff_rr)) * 100
    
    return metrics

def analyze_single_record(record_name, data_dir):
    """
    分析单个ECG记录
    """
    print(f"\n=== 分析记录: {record_name} ===")
    
    header_path = os.path.join(data_dir, f"{record_name}.hea")
    mat_path = os.path.join(data_dir, f"{record_name}.mat")
    
    # 解析头文件
    header_info = parse_header_file(header_path)
    if not header_info:
        return None
    
    print(f"导联数: {header_info['num_leads']}")
    print(f"采样率: {header_info['sampling_rate']} Hz")
    print(f"样本数: {header_info['num_samples']}")
    print(f"导联: {header_info['leads']}")
    
    # 读取数据
    signal_data = read_mat_file(mat_path, header_info['num_leads'], header_info['num_samples'])
    if signal_data is None:
        return None
    
    # 选择导联II进行分析（如果存在）
    if 'II' in header_info['leads']:
        lead_idx = header_info['leads'].index('II')
        ecg_signal = signal_data[:, lead_idx]
        analysis_lead = 'II'
    else:
        # 使用第一个导联
        ecg_signal = signal_data[:, 0]
        analysis_lead = header_info['leads'][0]
    
    print(f"使用导联 {analysis_lead} 进行分析")
    
    # R峰检测
    r_peaks = simple_r_peak_detection(ecg_signal, header_info['sampling_rate'])
    print(f"检测到 {len(r_peaks)} 个R峰")
    
    if len(r_peaks) < 3:
        print("⚠️ R峰数量不足，无法进行可靠分析")
        return None
    
    # 计算HRV指标
    hrv_metrics = calculate_hrv_metrics(r_peaks, header_info['sampling_rate'])
    
    # 整合结果
    result = {
        'record_name': record_name,
        'num_leads': header_info['num_leads'],
        'sampling_rate': header_info['sampling_rate'],
        'duration_sec': header_info['num_samples'] / header_info['sampling_rate'],
        'analysis_lead': analysis_lead,
        'r_peaks_count': len(r_peaks),
        **hrv_metrics,
        **{k: v for k, v in header_info.items() if k in ['age', 'sex', 'diagnosis']}
    }
    
    print("✅ 分析完成")
    return result

def analyze_directory(data_dir, output_file=None):
    """
    批量分析目录中的所有ECG记录
    """
    print(f"🔍 分析目录: {data_dir}")
    
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
        result = analyze_single_record(record_name, data_dir)
        
        if result:
            results.append(result)
            successful += 1
    
    if results:
        df = pd.DataFrame(results)
        
        if output_file is None:
            output_file = os.path.join(data_dir, 'ecg_analysis_results.csv')
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n📊 结果已保存到: {output_file}")
        print(f"✅ 成功分析: {successful}/{len(record_names)} 个记录")
        
        # 显示统计摘要
        print(f"\n📈 分析摘要:")
        print(f"平均心率: {df['mean_hr'].mean():.1f} ± {df['mean_hr'].std():.1f} BPM")
        print(f"平均SDNN: {df['std_rr'].mean():.1f} ± {df['std_rr'].std():.1f} ms")
        if 'rmssd' in df.columns:
            print(f"平均RMSSD: {df['rmssd'].mean():.1f} ± {df['rmssd'].std():.1f} ms")
        
        if 'age' in df.columns:
            ages = pd.to_numeric(df['age'], errors='coerce').dropna()
            if len(ages) > 0:
                print(f"年龄范围: {ages.min():.0f}-{ages.max():.0f} 岁")
        
        if 'sex' in df.columns:
            print(f"性别分布: {dict(df['sex'].value_counts())}")
        
        return df
    else:
        print("❌ 没有成功分析的记录")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="简化版ECG数据分析器")
    parser.add_argument("data_dir", help="ECG数据目录路径")
    parser.add_argument("--output", "-o", help="输出CSV文件路径")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"❌ 目录不存在: {args.data_dir}")
        exit(1)
    
    analyze_directory(args.data_dir, args.output)