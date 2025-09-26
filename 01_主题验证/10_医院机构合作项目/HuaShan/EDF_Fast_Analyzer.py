#!/usr/bin/env python3
"""
快速EDF ECG分析器 - 优化版本
专注于核心脆性指标的快速计算
"""

import sys
import os
import numpy as np
from datetime import datetime
import json

try:
    import mne
    from scipy.signal import find_peaks
except ImportError:
    print("需要安装依赖: pip install mne scipy")
    sys.exit(1)

class FastECGAnalyzer:
    def __init__(self, sampling_rate=1000.0):
        self.sampling_rate = sampling_rate
    
    def calculate_simple_chaos_indicators(self, data, max_samples=10000):
        """快速混沌指标计算"""
        
        # 降采样以加快计算
        if len(data) > max_samples:
            step = len(data) // max_samples
            data = data[::step]
        
        try:
            # 简化Lyapunov指数估计
            diffs = np.abs(np.diff(data))
            lyapunov_proxy = np.mean(diffs) / np.std(data) if np.std(data) > 0 else 0
            
            # 简化近似熵估计
            data_diff = np.diff(data)
            entropy_proxy = -np.sum(data_diff**2) / len(data_diff) if len(data_diff) > 0 else 0
            entropy_proxy = abs(entropy_proxy) / (np.var(data) + 1e-10)
            
            return {
                'lyapunov_proxy': float(lyapunov_proxy),
                'entropy_proxy': float(entropy_proxy),
                'signal_complexity': float(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-10))
            }
            
        except Exception:
            return {
                'lyapunov_proxy': 0.0,
                'entropy_proxy': 0.0,
                'signal_complexity': 0.0
            }
    
    def calculate_heart_rate_fast(self, ecg_data, max_samples=50000):
        """快速心率计算"""
        
        # 降采样以加快峰值检测
        if len(ecg_data) > max_samples:
            step = len(ecg_data) // max_samples
            ecg_data = ecg_data[::step]
            effective_sr = self.sampling_rate / step
        else:
            effective_sr = self.sampling_rate
        
        try:
            # 简单标准化
            ecg_normalized = (ecg_data - np.mean(ecg_data))
            ecg_std = np.std(ecg_normalized)
            
            if ecg_std < 1e-10:
                return self._empty_hr_result()
            
            ecg_normalized /= ecg_std
            
            # 快速峰值检测
            min_distance = int(0.3 * effective_sr)  # 200 bpm最大
            peaks, _ = find_peaks(ecg_normalized, height=0.5, distance=min_distance)
            
            if len(peaks) < 3:
                return self._empty_hr_result()
            
            # RR间期计算
            rr_intervals = np.diff(peaks) / effective_sr * 1000  # ms
            
            # 简单异常值过滤
            rr_mean = np.median(rr_intervals)
            valid_rr = rr_intervals[(rr_intervals > 0.5 * rr_mean) & 
                                   (rr_intervals < 2.0 * rr_mean)]
            
            if len(valid_rr) < 2:
                return self._empty_hr_result()
            
            # 统计计算
            rr_mean = np.mean(valid_rr)
            rr_std = np.std(valid_rr)
            mean_hr = 60000.0 / rr_mean
            hr_cv = (rr_std / rr_mean) * 100
            
            return {
                'mean_hr': float(mean_hr),
                'hr_cv': float(hr_cv),
                'rr_mean': float(rr_mean),
                'rr_std': float(rr_std),
                'detected_beats': len(peaks)
            }
            
        except Exception as e:
            print(f"    心率计算错误: {e}")
            return self._empty_hr_result()
    
    def _empty_hr_result(self):
        """空心率结果"""
        return {
            'mean_hr': 0,
            'hr_cv': 0,
            'rr_mean': 0,
            'rr_std': 0,
            'detected_beats': 0
        }
    
    def classify_fast_brittleness(self, chaos_indicators, hr_stats):
        """快速脆性分型"""
        
        # 提取指标
        lyapunov_proxy = chaos_indicators['lyapunov_proxy']
        entropy_proxy = chaos_indicators['entropy_proxy']
        signal_complexity = chaos_indicators['signal_complexity']
        hr_cv = hr_stats['hr_cv']
        mean_hr = hr_stats['mean_hr']
        
        # 快速评分
        score = 0
        risks = []
        
        # 混沌度评分
        if lyapunov_proxy > 1.0:
            score += 25
            risks.append("高混沌度")
        elif lyapunov_proxy > 0.5:
            score += 15
        
        # 复杂性评分
        if entropy_proxy > 0.1:
            score += 20
            risks.append("高熵值")
        elif entropy_proxy > 0.05:
            score += 10
        
        # 信号复杂性
        if signal_complexity > 2.0:
            score += 15
            risks.append("高信号复杂性")
        
        # 心率变异评分
        if hr_cv > 30:
            score += 30
            risks.append("极高心率变异")
        elif hr_cv > 20:
            score += 20
        elif hr_cv > 10:
            score += 10
        
        # 心率范围评分
        if mean_hr > 180 or mean_hr < 60:
            score += 10
            risks.append("异常心率")
        
        # 分型判断
        if score >= 80:
            btype = "V型极度危险"
        elif score >= 60:
            btype = "IV型重度脆弱"
        elif score >= 40:
            btype = "III型中度易损"
        elif score >= 20:
            btype = "II型轻度不稳定"
        else:
            btype = "I型正常稳定"
        
        return {
            "脆性分型": btype,
            "脆性评分": int(score),
            "主要风险": risks
        }
    
    def analyze_channel_fast(self, ecg_data, channel_name):
        """快速通道分析"""
        
        print(f"  - 信号预处理...")
        
        # 基本统计
        signal_stats = {
            'mean': float(np.mean(ecg_data)),
            'std': float(np.std(ecg_data)),
            'range': float(np.ptp(ecg_data))
        }
        
        # 信号质量检查
        if signal_stats['std'] < 1e-6:
            return {
                "通道名称": channel_name,
                "状态": "信号质量差",
                "脆性评估": {"脆性分型": "无法分析", "脆性评分": 0, "主要风险": []},
                "信号统计": signal_stats
            }
        
        print(f"  - 计算混沌指标...")
        chaos_indicators = self.calculate_simple_chaos_indicators(ecg_data)
        
        print(f"  - 心率分析...")
        hr_stats = self.calculate_heart_rate_fast(ecg_data)
        
        print(f"  - 脆性分型...")
        brittleness = self.classify_fast_brittleness(chaos_indicators, hr_stats)
        
        return {
            "通道名称": channel_name,
            "状态": "分析完成",
            "混沌指标": chaos_indicators,
            "心率统计": hr_stats,
            "脆性评估": brittleness,
            "信号统计": signal_stats
        }

def main():
    """主函数"""
    
    edf_file = "/Users/williamsun/Documents/gplus/docs/ECG/abdominal-and-direct-fetal-ecg-database-1.0.0/r01.edf"
    
    print("快速胎儿ECG脆性分析")
    print("优化算法，专注核心指标\n")
    
    try:
        # 读取EDF文件
        print("读取EDF数据...")
        raw = mne.io.read_raw_edf(edf_file, preload=True, verbose=False)
        
        info = {
            'sampling_rate': raw.info['sfreq'],
            'channels': raw.ch_names,
            'duration': raw.times[-1]
        }
        
        print(f"文件信息:")
        print(f"  采样率: {info['sampling_rate']} Hz")
        print(f"  通道: {info['channels']}")
        print(f"  时长: {info['duration']:.1f} 秒")
        
        # 创建分析器
        analyzer = FastECGAnalyzer(sampling_rate=info['sampling_rate'])
        
        # 获取数据
        ecg_data = raw.get_data()
        results = {}
        
        # 分析每个通道
        for i, channel_name in enumerate(info['channels']):
            print(f"\n=== 分析通道 {i+1}/{len(info['channels'])}: {channel_name} ===")
            
            channel_data = ecg_data[i, :]
            result = analyzer.analyze_channel_fast(channel_data, channel_name)
            results[channel_name] = result
            
            # 显示结果
            if result['状态'] == '分析完成':
                brittleness = result['脆性评估']
                hr_stats = result['心率统计']
                
                print(f"  结果:")
                print(f"    脆性分型: {brittleness['脆性分型']}")
                print(f"    脆性评分: {brittleness['脆性评分']}")
                print(f"    心率: {hr_stats['mean_hr']:.1f} bpm")
                print(f"    心率变异: {hr_stats['hr_cv']:.1f}%")
                if brittleness['主要风险']:
                    print(f"    风险因子: {', '.join(brittleness['主要风险'])}")
            else:
                print(f"  状态: {result['状态']}")
        
        # 生成报告
        print("\n" + "="*60)
        print("              快速ECG脆性分析报告")
        print("="*60)
        
        successful_analyses = [r for r in results.values() if r['状态'] == '分析完成']
        
        if successful_analyses:
            print(f"\n成功分析 {len(successful_analyses)} 个通道:")
            print(f"{'通道':<12} {'脆性分型':<15} {'评分':<5} {'心率':<10} {'变异%':<8}")
            print("-" * 60)
            
            for result in successful_analyses:
                name = result['通道名称']
                brit = result['脆性评估']
                hr = result['心率统计']
                
                print(f"{name:<12} {brit['脆性分型']:<15} {brit['脆性评分']:<5} "
                      f"{hr['mean_hr']:.1f} bpm  {hr['hr_cv']:.1f}")
        
        print("\n" + "="*60)
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/Users/williamsun/Documents/gplus/docs/HuaShan/fetal_ecg_fast_analysis_r01_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'info': {
                    'file': 'r01.edf',
                    'analyzer': 'FastECG-Agent2',
                    'timestamp': timestamp,
                    'edf_info': info
                },
                'results': results
            }, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n结果已保存: {output_file}")
        
    except Exception as e:
        print(f"分析过程出错: {e}")

if __name__ == "__main__":
    main()