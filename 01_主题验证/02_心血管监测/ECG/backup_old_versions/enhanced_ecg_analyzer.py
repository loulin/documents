#!/usr/bin/env python3
"""
增强版ECG数据分析器 v3.0
集成neurokit2等价的专业HRV指标和频域分析
专门用于分析PhysioNet WFDB格式的12导联ECG数据
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
from scipy.stats import entropy
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
        print(f"高级R峰检测错误: {e}")
        return []

def calculate_comprehensive_hrv_metrics(r_peaks, sampling_rate):
    """计算全面的HRV指标（等价neurokit2功能）"""
    if len(r_peaks) < 5:  # 需要至少5个R峰
        return {}
    
    # RR间期（毫秒）
    rr_intervals = np.diff(r_peaks) / sampling_rate * 1000
    
    if len(rr_intervals) < 4:
        return {}
    
    # === 时域指标 ===
    metrics = {}
    
    # 基础时域指标
    metrics['mean_rr'] = np.mean(rr_intervals)
    metrics['std_rr'] = np.std(rr_intervals, ddof=1)  # SDNN
    metrics['min_rr'] = np.min(rr_intervals)
    metrics['max_rr'] = np.max(rr_intervals)
    metrics['mean_hr'] = 60000 / metrics['mean_rr']
    metrics['std_hr'] = np.std(60000 / rr_intervals, ddof=1)
    
    # 高级时域指标
    diff_rr = np.diff(rr_intervals)
    if len(diff_rr) > 0:
        # RMSSD - 相邻RR间期差值的均方根
        metrics['rmssd'] = np.sqrt(np.mean(diff_rr ** 2))
        
        # pNNx指标
        metrics['pnn50'] = (np.sum(np.abs(diff_rr) > 50) / len(diff_rr)) * 100
        metrics['pnn20'] = (np.sum(np.abs(diff_rr) > 20) / len(diff_rr)) * 100
        metrics['pnn10'] = (np.sum(np.abs(diff_rr) > 10) / len(diff_rr)) * 100
        
        # SDSD - 相邻RR间期差值的标准差
        metrics['sdsd'] = np.std(diff_rr, ddof=1)
        
        # 高级统计指标
        metrics['cv'] = (metrics['std_rr'] / metrics['mean_rr']) * 100  # 变异系数
        metrics['median_rr'] = np.median(rr_intervals)
        metrics['mad_rr'] = np.median(np.abs(rr_intervals - metrics['median_rr']))  # 中位数绝对偏差
        
        # 范围和四分位数
        metrics['range_rr'] = metrics['max_rr'] - metrics['min_rr']
        metrics['iqr_rr'] = np.percentile(rr_intervals, 75) - np.percentile(rr_intervals, 25)
        
        # === 几何指标 ===
        # 三角指数（近似）
        hist, bin_edges = np.histogram(rr_intervals, bins=32)
        metrics['triangular_index'] = len(rr_intervals) / np.max(hist) if np.max(hist) > 0 else np.nan
        
        # TINN - 三角插值基线宽度
        metrics['tinn'] = np.max(rr_intervals) - np.min(rr_intervals)
        
        # 几何均值
        metrics['geometric_mean_rr'] = np.exp(np.mean(np.log(rr_intervals)))
        
        # === 频域指标（简化版本）===
        try:
            # 重采样到均匀时间间隔（4Hz）
            time_rr = np.cumsum(rr_intervals) / 1000  # 转换为秒
            time_uniform = np.arange(0, time_rr[-1], 0.25)  # 4Hz采样
            
            if len(time_uniform) > 10:  # 需要足够的采样点
                # 线性插值
                rr_interpolated = np.interp(time_uniform, time_rr, rr_intervals)
                
                # 去趋势
                rr_detrended = rr_interpolated - np.mean(rr_interpolated)
                
                # 功率谱密度
                freqs, psd = signal.welch(rr_detrended, fs=4.0, nperseg=min(256, len(rr_detrended)))
                
                # 频域指标
                vlf_band = (freqs >= 0.0033) & (freqs < 0.04)  # VLF: 0.0033-0.04 Hz
                lf_band = (freqs >= 0.04) & (freqs < 0.15)     # LF: 0.04-0.15 Hz  
                hf_band = (freqs >= 0.15) & (freqs < 0.4)      # HF: 0.15-0.4 Hz
                
                metrics['vlf_power'] = np.trapz(psd[vlf_band], freqs[vlf_band]) if np.any(vlf_band) else 0
                metrics['lf_power'] = np.trapz(psd[lf_band], freqs[lf_band]) if np.any(lf_band) else 0
                metrics['hf_power'] = np.trapz(psd[hf_band], freqs[hf_band]) if np.any(hf_band) else 0
                
                # 总功率
                metrics['total_power'] = metrics['vlf_power'] + metrics['lf_power'] + metrics['hf_power']
                
                # 相对功率
                if metrics['total_power'] > 0:
                    metrics['vlf_relative'] = metrics['vlf_power'] / metrics['total_power'] * 100
                    metrics['lf_relative'] = metrics['lf_power'] / metrics['total_power'] * 100
                    metrics['hf_relative'] = metrics['hf_power'] / metrics['total_power'] * 100
                
                # LF/HF比值
                metrics['lf_hf_ratio'] = metrics['lf_power'] / metrics['hf_power'] if metrics['hf_power'] > 0 else np.nan
                
                # 峰频率
                if np.any(lf_band):
                    lf_peak_idx = np.argmax(psd[lf_band])
                    metrics['lf_peak'] = freqs[lf_band][lf_peak_idx]
                
                if np.any(hf_band):
                    hf_peak_idx = np.argmax(psd[hf_band])
                    metrics['hf_peak'] = freqs[hf_band][hf_peak_idx]
            
        except Exception as e:
            print(f"频域分析错误: {e}")
            # 如果频域分析失败，设置默认值
            for key in ['vlf_power', 'lf_power', 'hf_power', 'total_power', 
                       'vlf_relative', 'lf_relative', 'hf_relative', 'lf_hf_ratio',
                       'lf_peak', 'hf_peak']:
                metrics[key] = np.nan
        
        # === 非线性指标 ===
        # 样本熵（简化版本）
        try:
            # Poincaré图指标
            rr1 = rr_intervals[:-1]  # RRn
            rr2 = rr_intervals[1:]   # RRn+1
            
            # SD1 - 短期变异性
            metrics['sd1'] = np.std(rr1 - rr2, ddof=1) / np.sqrt(2)
            
            # SD2 - 长期变异性  
            metrics['sd2'] = np.sqrt(2 * np.var(rr_intervals, ddof=1) - np.var(rr1 - rr2, ddof=1))
            
            # SD1/SD2比值
            metrics['sd1_sd2_ratio'] = metrics['sd1'] / metrics['sd2'] if metrics['sd2'] > 0 else np.nan
            
            # 椭圆面积
            metrics['csi'] = metrics['sd2'] / metrics['sd1'] if metrics['sd1'] > 0 else np.nan  # 心脏交感指数
            metrics['cvi'] = np.log10(metrics['sd1'] * metrics['sd2']) if (metrics['sd1'] > 0 and metrics['sd2'] > 0) else np.nan  # 心脏迷走指数
            
        except Exception as e:
            print(f"非线性分析错误: {e}")
            for key in ['sd1', 'sd2', 'sd1_sd2_ratio', 'csi', 'cvi']:
                metrics[key] = np.nan
        
        # === 统计形状指标 ===
        # 偏度和峰度
        from scipy.stats import skew, kurtosis
        metrics['skewness'] = skew(rr_intervals)
        metrics['kurtosis'] = kurtosis(rr_intervals)
        
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

def analyze_single_record_enhanced(record_name, data_dir):
    """增强版分析单个ECG记录"""
    print(f"\n=== 增强版分析记录: {record_name} ===")
    
    header_path = os.path.join(data_dir, f"{record_name}.hea")
    mat_path = os.path.join(data_dir, f"{record_name}.mat")
    
    # 解析头文件
    header_info = parse_header_file(header_path)
    if not header_info:
        return None
    
    print(f"导联数: {header_info['num_leads']}")
    print(f"采样率: {header_info['sampling_rate']} Hz")
    print(f"时长: {header_info['num_samples'] / header_info['sampling_rate']:.1f}秒")
    
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
        
        # 全面HRV分析
        hrv_metrics = calculate_comprehensive_hrv_metrics(r_peaks, header_info['sampling_rate'])
        
        lead_analyses[lead_name] = {
            'r_peaks_count': len(r_peaks),
            'quality': quality,
            **hrv_metrics
        }
        
        print(f"导联 {lead_name}: {len(r_peaks)}个R峰, SNR: {quality.get('snr_db', 0):.1f}dB")
    
    # 选择最佳导联进行主要分析
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
    
    print("✅ 增强版分析完成")
    return result

def analyze_directory_enhanced(data_dir, output_file=None):
    """批量增强版分析"""
    print(f"🔍 增强版分析目录: {data_dir}")
    
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
        result = analyze_single_record_enhanced(record_name, data_dir)
        
        if result:
            results.append(result)
            successful += 1
    
    if results:
        df = pd.DataFrame(results)
        
        if output_file is None:
            output_file = os.path.join(data_dir, 'enhanced_ecg_analysis_results.csv')
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n📊 增强版分析结果已保存到: {output_file}")
        print(f"✅ 成功分析: {successful}/{len(record_names)} 个记录")
        
        # 显示统计摘要
        print(f"\n📈 增强版分析摘要:")
        
        # 基础指标
        numeric_cols = ['mean_hr', 'std_rr', 'rmssd', 'lf_power', 'hf_power', 'lf_hf_ratio', 'sd1', 'sd2']
        for col in numeric_cols:
            if col in df.columns:
                values = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(values) > 0:
                    print(f"{col}: {values.mean():.2f} ± {values.std():.2f}")
        
        # 信号质量
        if 'quality' in df.columns:
            try:
                import ast
                snr_values = []
                for quality_str in df['quality']:
                    try:
                        quality_dict = ast.literal_eval(str(quality_str))
                        snr = quality_dict.get('snr_db', np.nan)
                        if not np.isnan(snr):
                            snr_values.append(snr)
                    except:
                        continue
                
                if snr_values:
                    print(f"平均SNR: {np.mean(snr_values):.1f} ± {np.std(snr_values):.1f} dB")
            except Exception as e:
                print(f"SNR统计错误: {e}")
        
        return df
    else:
        print("❌ 没有成功分析的记录")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="增强版ECG数据分析器")
    parser.add_argument("data_dir", help="ECG数据目录路径")
    parser.add_argument("--output", "-o", help="输出CSV文件路径")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"❌ 目录不存在: {args.data_dir}")
        exit(1)
    
    # 检查scipy是否可用
    try:
        from scipy import signal
        from scipy.stats import skew, kurtosis
        print("🎯 使用完整的信号处理和统计功能")
    except ImportError:
        print("⚠️  部分功能可能受限，建议安装scipy")
    
    analyze_directory_enhanced(args.data_dir, args.output)