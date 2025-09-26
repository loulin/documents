#!/usr/bin/env python3
"""
简化版EDF ECG文件分析器 - 专注于混沌动力学和脆性分析
绕过复杂的分段分析，直接进行脆性评估
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime
import json

try:
    import mne
    from scipy.signal import find_peaks
    from scipy import stats
except ImportError:
    print("需要安装依赖: pip install mne scipy")
    sys.exit(1)

class SimplifiedECGAnalyzer:
    def __init__(self, sampling_rate=1000.0):
        self.sampling_rate = sampling_rate
    
    def calculate_lyapunov_exponent(self, data, m=3, delay=1):
        """计算Lyapunov指数"""
        try:
            N = len(data)
            if N < 100:
                return 0.0
            
            # 简化计算
            data = np.array(data)
            diffs = []
            
            for i in range(N - m * delay):
                # 构造相空间向量
                xi = data[i:i + m * delay:delay]
                
                # 寻找最近邻
                min_dist = float('inf')
                for j in range(i + 10, min(i + 50, N - m * delay)):
                    xj = data[j:j + m * delay:delay]
                    dist = np.linalg.norm(xi - xj)
                    if dist < min_dist and dist > 0:
                        min_dist = dist
                
                if min_dist != float('inf') and min_dist > 0:
                    diffs.append(np.log(min_dist))
            
            if len(diffs) > 1:
                # 线性拟合斜率作为Lyapunov指数估计
                x = np.arange(len(diffs))
                slope, _, _, _, _ = stats.linregress(x, diffs)
                return max(0, slope * self.sampling_rate)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def calculate_approximate_entropy(self, data, m=2, r=None):
        """计算近似熵"""
        try:
            N = len(data)
            if N < 20:
                return 0.0
            
            if r is None:
                r = 0.2 * np.std(data)
            
            def _maxdist(xi, xj, m):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def _phi(m):
                patterns = np.array([data[i:i + m] for i in range(N - m + 1)])
                C = np.zeros(N - m + 1)
                
                for i in range(N - m + 1):
                    template_i = patterns[i]
                    matches = sum([1 for j in range(N - m + 1) 
                                 if _maxdist(template_i, patterns[j], m) <= r])
                    C[i] = matches / float(N - m + 1)
                
                phi = (N - m + 1) ** (-1) * sum([np.log(c) for c in C if c > 0])
                return phi
            
            return _phi(m) - _phi(m + 1)
            
        except Exception:
            return 0.0
    
    def calculate_heart_rate_statistics(self, ecg_data):
        """计算心率统计信息"""
        try:
            # 简单R波检测
            # 标准化数据
            normalized = (ecg_data - np.mean(ecg_data)) / np.std(ecg_data)
            
            # 寻找峰值
            peaks, _ = find_peaks(normalized, height=1.0, distance=int(0.4 * self.sampling_rate))
            
            if len(peaks) < 2:
                return {
                    'mean_hr': 0,
                    'hr_cv': 0,
                    'rr_mean': 0,
                    'rr_std': 0,
                    'detected_beats': 0
                }
            
            # 计算RR间期
            rr_intervals = np.diff(peaks) / self.sampling_rate * 1000  # ms
            
            # 过滤异常值
            rr_mean = np.mean(rr_intervals)
            rr_intervals = rr_intervals[(rr_intervals > 0.3 * rr_mean) & 
                                      (rr_intervals < 3.0 * rr_mean)]
            
            if len(rr_intervals) < 2:
                return {
                    'mean_hr': 0,
                    'hr_cv': 0,
                    'rr_mean': 0,
                    'rr_std': 0,
                    'detected_beats': 0
                }
            
            # 心率统计
            rr_mean = np.mean(rr_intervals)
            rr_std = np.std(rr_intervals)
            mean_hr = 60000.0 / rr_mean  # bpm
            hr_cv = (rr_std / rr_mean) * 100  # %
            
            return {
                'mean_hr': float(mean_hr),
                'hr_cv': float(hr_cv),
                'rr_mean': float(rr_mean),
                'rr_std': float(rr_std),
                'detected_beats': len(peaks),
                'rr_intervals': rr_intervals.tolist()
            }
            
        except Exception as e:
            print(f"心率计算错误: {e}")
            return {
                'mean_hr': 0,
                'hr_cv': 0,
                'rr_mean': 0,
                'rr_std': 0,
                'detected_beats': 0
            }
    
    def classify_brittleness(self, chaos_indicators, hr_stats):
        """ECG脆性分型"""
        
        # 提取指标
        lyapunov = chaos_indicators['lyapunov_exponent']
        approx_entropy = chaos_indicators['approximate_entropy']
        hr_cv = hr_stats['hr_cv']
        mean_hr = hr_stats['mean_hr']
        
        # 脆性评分计算
        brittleness_score = 0
        risk_factors = []
        
        # Lyapunov指数评分
        if lyapunov > 0.1:
            brittleness_score += 25
            risk_factors.append("高混沌度")
        elif lyapunov > 0.05:
            brittleness_score += 15
        elif lyapunov > 0.01:
            brittleness_score += 10
        
        # 近似熵评分
        if approx_entropy > 1.5:
            brittleness_score += 20
            risk_factors.append("高复杂性")
        elif approx_entropy > 1.0:
            brittleness_score += 12
        elif approx_entropy > 0.5:
            brittleness_score += 8
        
        # 心率变异评分
        if hr_cv > 40:
            brittleness_score += 30
            risk_factors.append("极高心率变异")
        elif hr_cv > 25:
            brittleness_score += 20
            risk_factors.append("高心率变异")
        elif hr_cv > 15:
            brittleness_score += 10
        
        # 心率范围评分
        if mean_hr > 180 or mean_hr < 60:
            brittleness_score += 15
            risk_factors.append("异常心率范围")
        elif mean_hr > 160 or mean_hr < 80:
            brittleness_score += 8
        
        # 脆性分型
        if brittleness_score >= 85:
            brittleness_type = "V型极度危险型"
            risk_level = "极高风险"
        elif brittleness_score >= 70:
            brittleness_type = "IV型重度脆弱型"
            risk_level = "高风险"
        elif brittleness_score >= 50:
            brittleness_type = "III型中度易损型"
            risk_level = "中等风险"
        elif brittleness_score >= 30:
            brittleness_type = "II型轻度不稳定型"
            risk_level = "低风险"
        else:
            brittleness_type = "I型正常稳定型"
            risk_level = "正常"
        
        return {
            "脆性分型": brittleness_type,
            "脆性评分": int(brittleness_score),
            "风险等级": risk_level,
            "主要风险因子": risk_factors,
            "详细评分": {
                "混沌度评分": min(25, lyapunov * 250),
                "复杂性评分": min(20, approx_entropy * 13.33),
                "变异性评分": min(30, hr_cv * 0.75),
                "心率评分": 15 if (mean_hr > 180 or mean_hr < 60) else 8 if (mean_hr > 160 or mean_hr < 80) else 0
            }
        }
    
    def analyze_ecg_channel(self, ecg_data, channel_name):
        """分析单个ECG通道"""
        
        print(f"  - 计算混沌动力学指标...")
        
        # 混沌动力学指标
        chaos_indicators = {
            'lyapunov_exponent': self.calculate_lyapunov_exponent(ecg_data),
            'approximate_entropy': self.calculate_approximate_entropy(ecg_data)
        }
        
        print(f"  - 计算心率统计...")
        
        # 心率统计
        hr_stats = self.calculate_heart_rate_statistics(ecg_data)
        
        print(f"  - 进行脆性分型...")
        
        # 脆性分型
        brittleness = self.classify_brittleness(chaos_indicators, hr_stats)
        
        return {
            "通道名称": channel_name,
            "混沌动力学指标": chaos_indicators,
            "心率统计": hr_stats,
            "脆性评估": brittleness,
            "数据质量": "良好" if hr_stats['detected_beats'] > 10 else "较差"
        }

def main():
    """主函数"""
    
    edf_file = "/Users/williamsun/Documents/gplus/docs/ECG/abdominal-and-direct-fetal-ecg-database-1.0.0/r01.edf"
    
    print("开始简化版胎儿ECG分析...")
    print("专注于混沌动力学和脆性评估")
    
    # 读取EDF文件
    print(f"\n读取EDF文件: {edf_file}")
    raw = mne.io.read_raw_edf(edf_file, preload=True, verbose=False)
    
    info = {
        'sampling_rate': raw.info['sfreq'],
        'channels': raw.ch_names,
        'duration': raw.times[-1],
        'n_samples': len(raw.times)
    }
    
    print(f"采样频率: {info['sampling_rate']} Hz")
    print(f"通道数: {len(info['channels'])}")
    print(f"记录时长: {info['duration']:.1f} 秒")
    
    # 创建分析器
    analyzer = SimplifiedECGAnalyzer(sampling_rate=info['sampling_rate'])
    
    # 分析结果
    results = {}
    
    # 分析每个通道
    ecg_data = raw.get_data()
    
    for i, channel_name in enumerate(info['channels']):
        print(f"\n=== 分析通道: {channel_name} ===")
        
        channel_data = ecg_data[i, :]
        
        # 数据质量检查
        if np.std(channel_data) < 1e-6:
            print(f"  跳过：信号变化太小")
            continue
        
        # 执行分析
        try:
            result = analyzer.analyze_ecg_channel(channel_data, channel_name)
            results[channel_name] = result
            
            # 显示关键结果
            brittleness = result['脆性评估']
            hr_stats = result['心率统计']
            
            print(f"  脆性分型: {brittleness['脆性分型']}")
            print(f"  脆性评分: {brittleness['脆性评分']}")
            print(f"  风险等级: {brittleness['风险等级']}")
            print(f"  平均心率: {hr_stats['mean_hr']:.1f} bpm")
            print(f"  心率变异: {hr_stats['hr_cv']:.1f}%")
            print(f"  检测心拍: {hr_stats['detected_beats']} 次")
            
        except Exception as e:
            print(f"  分析失败: {e}")
    
    # 生成综合报告
    print("\n" + "="*60)
    print("              胎儿ECG脆性分析报告")
    print("="*60)
    
    print(f"数据文件: r01.edf")
    print(f"分析方法: 混沌动力学 + 脆性分型")
    print(f"成功分析: {len(results)} 个通道")
    
    if results:
        print(f"\n{'通道':<12} {'脆性分型':<15} {'评分':<6} {'心率':<8} {'变异':<8} {'风险等级'}")
        print("-" * 70)
        
        for channel, result in results.items():
            brittleness = result['脆性评估']
            hr_stats = result['心率统计']
            
            print(f"{channel:<12} {brittleness['脆性分型'][:13]:<15} "
                  f"{brittleness['脆性评分']:<6} "
                  f"{hr_stats['mean_hr']:.0f}bpm {hr_stats['hr_cv']:.1f}%   "
                  f"{brittleness['风险等级']}")
    
    print("\n" + "="*60)
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/Users/williamsun/Documents/gplus/docs/HuaShan/fetal_ecg_simplified_analysis_r01_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_info': {
                'file': 'r01.edf',
                'method': 'SimplifiedECG-Agent2',
                'timestamp': timestamp,
                'edf_info': info
            },
            'results': results
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n详细结果已保存到: {output_file}")

if __name__ == "__main__":
    main()