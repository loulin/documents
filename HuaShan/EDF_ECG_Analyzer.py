#!/usr/bin/env python3
"""
EDF ECG文件分析器 - 基于ECG-Agent2系统
专门用于分析EDF格式的胎儿心电数据
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

# 添加ECG-Agent2分析器路径
sys.path.append('/Users/williamsun/Documents/gplus/docs/HuaShan')

try:
    import mne  # 用于读取EDF文件
except ImportError:
    print("需要安装MNE库: pip install mne")
    sys.exit(1)

def read_edf_file(edf_path):
    """
    读取EDF文件并提取ECG数据
    """
    try:
        print(f"正在读取EDF文件: {edf_path}")
        
        # 使用MNE读取EDF文件
        raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
        
        # 获取基本信息
        info = {
            'sampling_rate': raw.info['sfreq'],
            'channels': raw.ch_names,
            'duration': raw.times[-1],
            'n_samples': len(raw.times)
        }
        
        print(f"采样频率: {info['sampling_rate']} Hz")
        print(f"通道数: {len(info['channels'])}")
        print(f"通道名称: {info['channels']}")
        print(f"记录时长: {info['duration']:.2f} 秒")
        print(f"数据点数: {info['n_samples']}")
        
        # 提取ECG数据
        ecg_data = raw.get_data()
        timestamps = raw.times
        
        return {
            'data': ecg_data,
            'timestamps': timestamps,
            'info': info,
            'raw': raw
        }
        
    except Exception as e:
        print(f"读取EDF文件失败: {e}")
        return None

def analyze_fetal_ecg(edf_data):
    """
    使用ECG-Agent2系统分析胎儿心电数据
    """
    try:
        # 导入ECG-Agent2分析器
        from ECG_Agent2_Intelligent_Analyzer import ECGAgent2Analyzer
        
        # 创建分析器实例
        analyzer = ECGAgent2Analyzer(
            sampling_rate=edf_data['info']['sampling_rate']
        )
        
        # 对每个通道进行分析
        analysis_results = {}
        
        for i, channel_name in enumerate(edf_data['info']['channels']):
            print(f"\n=== 分析通道: {channel_name} ===")
            
            # 获取单通道数据
            channel_data = edf_data['data'][i, :]
            timestamps = edf_data['timestamps']
            
            # 数据质量检查
            if np.std(channel_data) < 1e-6:
                print(f"通道 {channel_name} 数据变化太小，跳过分析")
                continue
                
            if np.any(np.isnan(channel_data)) or np.any(np.isinf(channel_data)):
                print(f"通道 {channel_name} 包含无效数据，进行清理")
                channel_data = np.nan_to_num(channel_data, nan=0.0, posinf=0.0, neginf=0.0)
            
            try:
                # 执行ECG智能分析
                result = analyzer.analyze_ecg_intelligence(
                    channel_data, 
                    timestamps, 
                    patient_id=f"r01_fetal_{channel_name}"
                )
                
                analysis_results[channel_name] = result
                
                # 打印关键结果
                if 'ECG脆性评估' in result:
                    brittleness = result['ECG脆性评估']
                    print(f"脆性分型: {brittleness.get('脆性分型', 'N/A')}")
                    print(f"脆性评分: {brittleness.get('脆性评分', 'N/A')}")
                    print(f"心血管风险: {brittleness.get('心血管风险评估', 'N/A')}")
                
            except Exception as e:
                print(f"通道 {channel_name} 分析失败: {e}")
                continue
        
        return analysis_results
        
    except ImportError:
        print("ECG-Agent2分析器未找到，执行基础分析")
        return analyze_basic_ecg(edf_data)

def analyze_basic_ecg(edf_data):
    """
    基础ECG分析（当ECG-Agent2不可用时）
    """
    results = {}
    
    for i, channel_name in enumerate(edf_data['info']['channels']):
        channel_data = edf_data['data'][i, :]
        
        # 基础统计分析
        basic_stats = {
            'mean': float(np.mean(channel_data)),
            'std': float(np.std(channel_data)),
            'min': float(np.min(channel_data)),
            'max': float(np.max(channel_data)),
            'range': float(np.ptp(channel_data)),
            'rms': float(np.sqrt(np.mean(channel_data**2)))
        }
        
        # 估算心率（简单峰值检测）
        try:
            from scipy.signal import find_peaks
            
            # 标准化数据
            normalized_data = (channel_data - np.mean(channel_data)) / np.std(channel_data)
            
            # 寻找R波峰值
            peaks, _ = find_peaks(normalized_data, height=1.5, distance=int(0.4 * edf_data['info']['sampling_rate']))
            
            if len(peaks) > 1:
                rr_intervals = np.diff(peaks) / edf_data['info']['sampling_rate']
                heart_rate = 60.0 / np.mean(rr_intervals)
                heart_rate_var = np.std(rr_intervals) * 1000  # ms
                
                basic_stats.update({
                    'estimated_heart_rate': float(heart_rate),
                    'heart_rate_variability': float(heart_rate_var),
                    'detected_beats': len(peaks)
                })
            
        except ImportError:
            print("SciPy未安装，跳过心率分析")
        
        results[channel_name] = {
            'basic_statistics': basic_stats,
            'channel_quality': 'good' if basic_stats['std'] > 1e-6 else 'poor'
        }
    
    return results

def save_analysis_results(results, output_path):
    """
    保存分析结果
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存JSON格式结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n分析结果已保存到: {output_path}")
        
    except Exception as e:
        print(f"保存结果失败: {e}")

def generate_summary_report(results, edf_info):
    """
    生成分析摘要报告
    """
    print("\n" + "="*60)
    print("           胎儿ECG数据分析摘要报告")
    print("="*60)
    
    print(f"数据文件: r01.edf")
    print(f"采样频率: {edf_info['sampling_rate']} Hz")
    print(f"记录时长: {edf_info['duration']:.1f} 秒 ({edf_info['duration']/60:.1f} 分钟)")
    print(f"分析通道: {len(results)} 个")
    
    print(f"\n{'通道名称':<15} {'分析状态':<10} {'关键指标':<30}")
    print("-" * 60)
    
    for channel, result in results.items():
        if 'ECG脆性评估' in result:
            # ECG-Agent2分析结果
            brittleness = result['ECG脆性评估']
            status = "完整分析"
            key_metric = f"脆性: {brittleness.get('脆性分型', 'N/A')}"
        elif 'basic_statistics' in result:
            # 基础分析结果
            stats = result['basic_statistics']
            status = "基础分析"
            if 'estimated_heart_rate' in stats:
                key_metric = f"心率: {stats['estimated_heart_rate']:.1f} bpm"
            else:
                key_metric = f"信号强度: {stats['std']:.2f}"
        else:
            status = "分析失败"
            key_metric = "N/A"
        
        print(f"{channel:<15} {status:<10} {key_metric:<30}")
    
    print("\n" + "="*60)

def main():
    """
    主函数
    """
    edf_file = "/Users/williamsun/Documents/gplus/docs/ECG/abdominal-and-direct-fetal-ecg-database-1.0.0/r01.edf"
    
    if not os.path.exists(edf_file):
        print(f"EDF文件不存在: {edf_file}")
        return
    
    print("开始分析胎儿ECG数据...")
    print("使用ECG-Agent2智能分析系统")
    
    # 读取EDF文件
    edf_data = read_edf_file(edf_file)
    if not edf_data:
        return
    
    # 执行ECG分析
    print(f"\n开始ECG智能分析...")
    analysis_results = analyze_fetal_ecg(edf_data)
    
    # 生成报告
    generate_summary_report(analysis_results, edf_data['info'])
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/Users/williamsun/Documents/gplus/docs/HuaShan/fetal_ecg_analysis_r01_{timestamp}.json"
    save_analysis_results({
        'analysis_info': {
            'file': 'r01.edf',
            'analysis_time': timestamp,
            'analyzer': 'ECG-Agent2',
            'edf_info': edf_data['info']
        },
        'channel_results': analysis_results
    }, output_file)

if __name__ == "__main__":
    main()