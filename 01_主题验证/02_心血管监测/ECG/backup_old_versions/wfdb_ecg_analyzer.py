#!/usr/bin/env python3
"""
WFDB ECG数据分析器
专门用于分析PhysioNet WFDB格式的12导联ECG数据
支持批量分析和详细心电图特征提取
"""

import wfdb
import neurokit2 as nk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def analyze_single_ecg_record(record_name, data_dir):
    """
    分析单个ECG记录
    """
    try:
        print(f"\n=== 分析记录: {record_name} ===")
        
        # 读取WFDB格式数据
        record_path = os.path.join(data_dir, record_name)
        record = wfdb.rdrecord(record_path)
        
        # 获取基本信息
        sampling_rate = record.fs
        duration = len(record.p_signal) / sampling_rate
        leads = record.sig_name
        
        print(f"采样率: {sampling_rate} Hz")
        print(f"时长: {duration:.1f} 秒")
        print(f"导联: {leads}")
        
        # 读取患者信息
        patient_info = {}
        if hasattr(record, 'comments'):
            for comment in record.comments:
                if comment.startswith('#Age:'):
                    patient_info['age'] = comment.split(': ')[1]
                elif comment.startswith('#Sex:'):
                    patient_info['sex'] = comment.split(': ')[1]
                elif comment.startswith('#Dx:'):
                    patient_info['diagnosis'] = comment.split(': ')[1]
        
        print(f"患者信息: {patient_info}")
        
        # 选择Lead II进行分析（标准导联）
        if 'II' in leads:
            lead_idx = leads.index('II')
            ecg_signal = record.p_signal[:, lead_idx]
            print("使用导联 II 进行分析")
        else:
            # 如果没有Lead II，使用第一个导联
            ecg_signal = record.p_signal[:, 0]
            print(f"使用导联 {leads[0]} 进行分析")
        
        # ECG信号处理和分析
        print("开始ECG信号分析...")
        signals, info = nk.ecg_process(ecg_signal, sampling_rate=sampling_rate)
        
        # 检查R峰检测结果
        r_peaks = info.get('ECG_R_Peaks', [])
        if len(r_peaks) < 3:
            print(f"⚠️  警告: 检测到的R峰数量过少 ({len(r_peaks)}个)")
            return None
        
        print(f"检测到 {len(r_peaks)} 个R峰")
        
        # 计算心率统计
        rr_intervals = np.diff(r_peaks) / sampling_rate * 1000  # 转换为毫秒
        heart_rate = 60000 / rr_intervals  # BPM
        
        basic_stats = {
            'record_name': record_name,
            'duration_sec': duration,
            'sampling_rate': sampling_rate,
            'r_peaks_count': len(r_peaks),
            'mean_hr': np.mean(heart_rate),
            'std_hr': np.std(heart_rate),
            'min_hr': np.min(heart_rate),
            'max_hr': np.max(heart_rate),
            'mean_rr': np.mean(rr_intervals),
            'std_rr': np.std(rr_intervals),
            **patient_info
        }
        
        # HRV分析
        try:
            hrv_metrics = nk.hrv(r_peaks, sampling_rate=sampling_rate, show=False)
            if not hrv_metrics.empty:
                # 添加主要HRV指标到结果中
                basic_stats.update({
                    'RMSSD': hrv_metrics.iloc[0].get('HRV_RMSSD', np.nan),
                    'SDNN': hrv_metrics.iloc[0].get('HRV_SDNN', np.nan),
                    'pNN50': hrv_metrics.iloc[0].get('HRV_pNN50', np.nan),
                    'HF_power': hrv_metrics.iloc[0].get('HRV_HF', np.nan),
                    'LF_power': hrv_metrics.iloc[0].get('HRV_LF', np.nan),
                })
                print("✅ HRV分析完成")
            else:
                print("⚠️  HRV分析失败")
        except Exception as e:
            print(f"⚠️  HRV分析错误: {e}")
        
        return basic_stats
        
    except Exception as e:
        print(f"❌ 分析记录 {record_name} 时出错: {e}")
        return None

def analyze_ecg_directory(data_dir, output_file=None):
    """
    批量分析目录中的所有ECG记录
    """
    print(f"🔍 分析目录: {data_dir}")
    
    # 读取RECORDS文件获取记录列表
    records_file = os.path.join(data_dir, 'RECORDS')
    if not os.path.exists(records_file):
        print("❌ 未找到RECORDS文件")
        return
    
    # 读取记录名称列表
    with open(records_file, 'r') as f:
        record_names = [line.strip() for line in f if line.strip()]
    
    print(f"找到 {len(record_names)} 个ECG记录")
    
    # 分析所有记录
    results = []
    successful_analyses = 0
    
    for i, record_name in enumerate(record_names, 1):
        print(f"\n进度: {i}/{len(record_names)}")
        result = analyze_single_ecg_record(record_name, data_dir)
        
        if result:
            results.append(result)
            successful_analyses += 1
            print("✅ 分析成功")
        else:
            print("❌ 分析失败")
    
    # 保存结果到CSV
    if results:
        df = pd.DataFrame(results)
        
        if output_file is None:
            output_file = os.path.join(data_dir, 'ecg_analysis_results.csv')
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n📊 分析结果已保存到: {output_file}")
        print(f"✅ 成功分析: {successful_analyses}/{len(record_names)} 个记录")
        
        # 显示基本统计信息
        print("\n📈 总体统计:")
        print(f"平均心率: {df['mean_hr'].mean():.1f} ± {df['mean_hr'].std():.1f} BPM")
        print(f"平均RR间期: {df['mean_rr'].mean():.1f} ± {df['mean_rr'].std():.1f} ms")
        
        if 'RMSSD' in df.columns:
            rmssd_mean = df['RMSSD'].mean()
            if not np.isnan(rmssd_mean):
                print(f"平均RMSSD: {rmssd_mean:.1f} ms")
        
        # 年龄分布
        if 'age' in df.columns:
            ages = pd.to_numeric(df['age'], errors='coerce').dropna()
            if len(ages) > 0:
                print(f"年龄范围: {ages.min():.0f}-{ages.max():.0f} 岁 (平均: {ages.mean():.1f}岁)")
        
        # 性别分布
        if 'sex' in df.columns:
            sex_counts = df['sex'].value_counts()
            print(f"性别分布: {dict(sex_counts)}")
        
        return df
    else:
        print("❌ 没有成功分析的记录")
        return None

def plot_sample_ecg(data_dir, record_name, save_path=None):
    """
    绘制示例ECG信号
    """
    try:
        record_path = os.path.join(data_dir, record_name)
        record = wfdb.rdrecord(record_path)
        
        # 创建多子图显示所有导联
        fig, axes = plt.subplots(4, 3, figsize=(15, 12))
        fig.suptitle(f'ECG Record: {record_name}', fontsize=16)
        
        for i, (ax, lead_name) in enumerate(zip(axes.flat, record.sig_name)):
            if i < len(record.sig_name):
                time_axis = np.arange(len(record.p_signal)) / record.fs
                ax.plot(time_axis, record.p_signal[:, i], 'b-', linewidth=0.8)
                ax.set_title(f'Lead {lead_name}')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Amplitude (mV)')
                ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"ECG图表已保存到: {save_path}")
        
        return fig
        
    except Exception as e:
        print(f"绘制ECG图表时出错: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="分析WFDB格式的ECG数据")
    parser.add_argument("data_dir", help="包含ECG数据的目录路径")
    parser.add_argument("--output", "-o", help="输出CSV文件路径")
    parser.add_argument("--plot-sample", help="绘制指定记录的ECG图表")
    parser.add_argument("--plot-save", help="ECG图表保存路径")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"❌ 目录不存在: {args.data_dir}")
        exit(1)
    
    # 执行批量分析
    df = analyze_ecg_directory(args.data_dir, args.output)
    
    # 如果指定了绘图参数，绘制示例ECG
    if args.plot_sample and df is not None:
        plot_sample_ecg(args.data_dir, args.plot_sample, args.plot_save)