#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent2_HRV_Brittleness_Analyzer.py

基于Agent2 v5.0血糖脆性分析架构的HRV脆性分析系统
适用于心率变异性的脆性评估、智能分段和自主神经功能分析

作者: AGPAI Team  
版本: v1.0
日期: 2025-08-28
"""

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import entropy
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class HRVBrittenessAnalyzer:
    """HRV脆性分析器 - 基于Agent2混沌动力学架构"""
    
    def __init__(self):
        self.brittleness_types = {
            1: "I型正常调节型",
            2: "II型轻度失调型",
            3: "III型中度失调型", 
            4: "IV型重度失调型",
            5: "V型极度刚性型"
        }
        
        # HRV正常参考范围 (基于年龄和性别)
        self.reference_ranges = {
            "RMSSD": {"normal": 50, "warning": 30, "risk": 15},
            "pNN50": {"normal": 15, "warning": 5, "risk": 2},
            "SDNN": {"normal": 100, "warning": 50, "risk": 30},
            "LF_HF_ratio": {"balanced_min": 1.0, "balanced_max": 2.5}
        }
    
    def preprocess_rr_data(self, rr_intervals):
        """RR间期数据预处理"""
        # 转换为numpy数组
        rr_data = np.array(rr_intervals, dtype=float)
        
        # 异常值过滤 (300-2000ms)
        valid_mask = (rr_data >= 300) & (rr_data <= 2000)
        rr_data = rr_data[valid_mask]
        
        # 移除极端异常值 (3σ原则)
        if len(rr_data) > 10:
            mean_rr = np.mean(rr_data)
            std_rr = np.std(rr_data)
            valid_mask = np.abs(rr_data - mean_rr) <= 3 * std_rr
            rr_data = rr_data[valid_mask]
        
        return rr_data
    
    def calculate_time_domain_hrv(self, rr_intervals):
        """计算HRV时域指标"""
        if len(rr_intervals) < 5:
            return {
                'RMSSD': 0, 'pNN50': 0, 'SDNN': 0, 'SDANN': 0,
                'mean_RR': 0, 'mean_HR': 0
            }
        
        # 基础统计
        mean_rr = np.mean(rr_intervals)
        mean_hr = 60000 / mean_rr if mean_rr > 0 else 0
        
        # RMSSD: 相邻RR间期差值的均方根
        rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
        
        # pNN50: 相邻RR间期差值>50ms的百分比
        nn50_count = np.sum(np.abs(np.diff(rr_intervals)) > 50)
        pnn50 = (nn50_count / (len(rr_intervals) - 1)) * 100
        
        # SDNN: RR间期标准差
        sdnn = np.std(rr_intervals)
        
        # SDANN: 5分钟段平均RR间期的标准差
        if len(rr_intervals) > 100:
            segment_size = len(rr_intervals) // 20  # 分为20段
            segment_means = []
            for i in range(0, len(rr_intervals) - segment_size, segment_size):
                segment = rr_intervals[i:i + segment_size]
                segment_means.append(np.mean(segment))
            sdann = np.std(segment_means) if len(segment_means) > 1 else 0
        else:
            sdann = 0
        
        return {
            'RMSSD': rmssd,
            'pNN50': pnn50,
            'SDNN': sdnn,
            'SDANN': sdann,
            'mean_RR': mean_rr,
            'mean_HR': mean_hr
        }
    
    def calculate_frequency_domain_hrv(self, rr_intervals, sampling_rate=4):
        """计算HRV频域指标"""
        try:
            if len(rr_intervals) < 50:
                return {'LF': 0, 'HF': 0, 'LF_HF_ratio': 0, 'total_power': 0}
            
            # RR间期插值到等间隔时间序列
            time_points = np.cumsum(rr_intervals) / 1000  # 转换为秒
            time_uniform = np.arange(0, time_points[-1], 1/sampling_rate)
            
            # 插值
            rr_interpolated = np.interp(time_uniform, time_points[:-1], rr_intervals[:-1])
            
            # 去趋势
            rr_detrended = signal.detrend(rr_interpolated)
            
            # 功率谱密度估计
            f, psd = signal.welch(rr_detrended, fs=sampling_rate, nperseg=min(256, len(rr_detrended)))
            
            # 频段功率计算
            vlf_mask = (f >= 0.003) & (f < 0.04)   # VLF: 0.003-0.04 Hz
            lf_mask = (f >= 0.04) & (f < 0.15)     # LF: 0.04-0.15 Hz  
            hf_mask = (f >= 0.15) & (f < 0.4)      # HF: 0.15-0.4 Hz
            
            vlf_power = np.sum(psd[vlf_mask])
            lf_power = np.sum(psd[lf_mask])
            hf_power = np.sum(psd[hf_mask])
            total_power = np.sum(psd)
            
            # LF/HF比值
            lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0
            
            return {
                'VLF': vlf_power,
                'LF': lf_power,
                'HF': hf_power,
                'LF_HF_ratio': lf_hf_ratio,
                'total_power': total_power
            }
        except:
            return {'LF': 0, 'HF': 0, 'LF_HF_ratio': 0, 'total_power': 0}
    
    def calculate_lyapunov_exponent(self, rr_intervals, embedding_dim=3, delay=1):
        """计算Lyapunov指数 - 混沌动力学核心指标"""
        try:
            if len(rr_intervals) < 100:
                return 0
            
            # 相空间重构
            N = len(rr_intervals)
            reconstructed = np.zeros((N - (embedding_dim - 1) * delay, embedding_dim))
            
            for i in range(embedding_dim):
                start_idx = i * delay
                end_idx = N - (embedding_dim - 1 - i) * delay
                reconstructed[:, i] = rr_intervals[start_idx:end_idx]
            
            # 计算平均对数散度
            divergences = []
            for i in range(1, len(reconstructed) - 1):
                # 寻找最近邻点
                distances = np.linalg.norm(reconstructed - reconstructed[i], axis=1)
                distances[i] = np.inf  # 排除自身
                nearest_idx = np.argmin(distances)
                
                # 计算演化后的距离
                if i + 1 < len(reconstructed) and nearest_idx + 1 < len(reconstructed):
                    initial_distance = distances[nearest_idx]
                    evolved_distance = np.linalg.norm(
                        reconstructed[i + 1] - reconstructed[nearest_idx + 1]
                    )
                    
                    if initial_distance > 0 and evolved_distance > 0:
                        divergence = np.log(evolved_distance / initial_distance)
                        divergences.append(divergence)
            
            lyapunov_exponent = np.mean(divergences) if divergences else 0
            return lyapunov_exponent
        except:
            return 0
    
    def calculate_approximate_entropy(self, rr_intervals, m=2, r=None):
        """计算近似熵"""
        try:
            N = len(rr_intervals)
            if N < 100 or r is None:
                r = 0.2 * np.std(rr_intervals) if N >= 10 else 1.0
            
            def maxdist(xi, xj):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def phi(m):
                patterns = np.array([rr_intervals[i:i + m] for i in range(N - m + 1)])
                C = np.zeros(N - m + 1)
                
                for i in range(N - m + 1):
                    template = patterns[i]
                    matches = 0
                    for j in range(N - m + 1):
                        if maxdist(template, patterns[j]) <= r:
                            matches += 1
                    C[i] = matches / (N - m + 1)
                
                phi_value = sum([np.log(c) if c > 0 else 0 for c in C]) / (N - m + 1)
                return phi_value
            
            approximate_entropy = phi(m) - phi(m + 1)
            return approximate_entropy
        except:
            return 0
    
    def calculate_hurst_exponent(self, rr_intervals):
        """计算Hurst指数"""
        try:
            N = len(rr_intervals)
            if N < 100:
                return 0.5
            
            # R/S分析
            lags = np.logspace(1, np.log10(N//4), 15).astype(int)
            rs_values = []
            
            for lag in lags:
                if lag >= N:
                    continue
                    
                sections = N // lag
                if sections == 0:
                    continue
                
                section_rs = []
                for i in range(sections):
                    start_idx = i * lag
                    end_idx = (i + 1) * lag
                    section_data = rr_intervals[start_idx:end_idx]
                    
                    # 计算累积偏差
                    mean_val = np.mean(section_data)
                    deviations = section_data - mean_val
                    cumsum_dev = np.cumsum(deviations)
                    
                    # R: 极差
                    R = np.max(cumsum_dev) - np.min(cumsum_dev)
                    
                    # S: 标准差
                    S = np.std(section_data)
                    
                    if S > 0:
                        section_rs.append(R / S)
                
                if len(section_rs) > 0:
                    rs_values.append(np.mean(section_rs))
            
            # 线性拟合计算Hurst指数
            if len(rs_values) >= 3:
                valid_lags = lags[:len(rs_values)]
                log_lags = np.log10(valid_lags)
                log_rs = np.log10(rs_values)
                
                # 过滤无效值
                valid_mask = ~(np.isinf(log_rs) | np.isnan(log_rs))
                if np.sum(valid_mask) >= 3:
                    hurst = np.polyfit(log_lags[valid_mask], log_rs[valid_mask], 1)[0]
                    return max(0, min(1, hurst))
            
            return 0.5
        except:
            return 0.5
    
    def calculate_sample_entropy(self, rr_intervals, m=2, r=None):
        """计算样本熵"""
        try:
            N = len(rr_intervals)
            if N < 50:
                return 0
            
            if r is None:
                r = 0.2 * np.std(rr_intervals)
            
            def chebyshev_distance(a, b):
                return max([abs(x - y) for x, y in zip(a, b)])
            
            A = 0.0  # m+1长度匹配数
            B = 0.0  # m长度匹配数
            
            for i in range(N - m):
                template_m = rr_intervals[i:i + m]
                if i + m + 1 <= N:
                    template_m_plus = rr_intervals[i:i + m + 1]
                else:
                    continue
                
                for j in range(i + 1, N - m):
                    if j + m <= N:
                        test_m = rr_intervals[j:j + m]
                        
                        # m长度匹配检查
                        if chebyshev_distance(template_m, test_m) <= r:
                            B += 1.0
                            
                            # m+1长度匹配检查
                            if j + m + 1 <= N:
                                test_m_plus = rr_intervals[j:j + m + 1]
                                if chebyshev_distance(template_m_plus, test_m_plus) <= r:
                                    A += 1.0
            
            sample_entropy = -np.log(A / B) if B > 0 else 0
            return sample_entropy
        except:
            return 0
    
    def calculate_poincare_analysis(self, rr_intervals):
        """Poincare散点图分析"""
        try:
            if len(rr_intervals) < 10:
                return {'SD1': 0, 'SD2': 0, 'SD1_SD2_ratio': 0}
            
            # RR(n) vs RR(n+1)
            rr1 = rr_intervals[:-1]  # RR(n)
            rr2 = rr_intervals[1:]   # RR(n+1)
            
            # 计算SD1和SD2
            # SD1: 短轴标准差 (快速变化)
            sd1 = np.std(rr1 - rr2) / np.sqrt(2)
            
            # SD2: 长轴标准差 (慢速变化)
            sd2 = np.std(rr1 + rr2) / np.sqrt(2)
            
            # SD1/SD2比值
            sd1_sd2_ratio = sd1 / sd2 if sd2 > 0 else 0
            
            return {
                'SD1': sd1,
                'SD2': sd2, 
                'SD1_SD2_ratio': sd1_sd2_ratio
            }
        except:
            return {'SD1': 0, 'SD2': 0, 'SD1_SD2_ratio': 0}
    
    def classify_hrv_brittleness(self, rr_intervals):
        """HRV脆性分型"""
        try:
            # 数据预处理
            clean_rr = self.preprocess_rr_data(rr_intervals)
            
            if len(clean_rr) < 50:
                return {"error": "RR间期数据不足，无法进行可靠分析"}
            
            # 时域分析
            time_domain = self.calculate_time_domain_hrv(clean_rr)
            
            # 频域分析
            freq_domain = self.calculate_frequency_domain_hrv(clean_rr)
            
            # 混沌动力学分析
            lyapunov = self.calculate_lyapunov_exponent(clean_rr)
            approx_entropy = self.calculate_approximate_entropy(clean_rr)
            hurst_exponent = self.calculate_hurst_exponent(clean_rr)
            sample_entropy = self.calculate_sample_entropy(clean_rr)
            
            # Poincare分析
            poincare = self.calculate_poincare_analysis(clean_rr)
            
            # HRV脆性评分
            brittleness_score = self.calculate_hrv_brittleness_score(
                time_domain, freq_domain, lyapunov, approx_entropy, hurst_exponent
            )
            
            # 脆性分型
            brittleness_type = self.determine_brittleness_type(brittleness_score)
            risk_level = self.assess_risk_level(brittleness_score)
            autonomic_balance = self.assess_autonomic_balance(freq_domain)
            
            return {
                "脆性分型": self.brittleness_types[brittleness_type],
                "脆性评分": f"{brittleness_score:.1f}/100",
                "风险等级": risk_level,
                "自主神经平衡": autonomic_balance,
                "时域HRV指标": {
                    "RMSSD": f"{time_domain['RMSSD']:.1f} ms",
                    "pNN50": f"{time_domain['pNN50']:.1f}%",
                    "SDNN": f"{time_domain['SDNN']:.1f} ms",
                    "平均心率": f"{time_domain['mean_HR']:.1f} bpm"
                },
                "频域HRV指标": {
                    "LF功率": f"{freq_domain['LF']:.2f} ms²",
                    "HF功率": f"{freq_domain['HF']:.2f} ms²",
                    "LF/HF比值": f"{freq_domain['LF_HF_ratio']:.2f}"
                },
                "混沌动力学指标": {
                    "Lyapunov指数": f"{lyapunov:.6f}",
                    "近似熵": f"{approx_entropy:.4f}",
                    "Hurst指数": f"{hurst_exponent:.4f}",
                    "样本熵": f"{sample_entropy:.4f}"
                },
                "Poincare分析": {
                    "SD1": f"{poincare['SD1']:.1f} ms",
                    "SD2": f"{poincare['SD2']:.1f} ms",
                    "SD1/SD2": f"{poincare['SD1_SD2_ratio']:.3f}"
                },
                "临床解读": self.generate_clinical_interpretation(
                    brittleness_type, autonomic_balance, time_domain
                )
            }
            
        except Exception as e:
            return {"error": f"HRV分析过程出错: {str(e)}"}
    
    def calculate_hrv_brittleness_score(self, time_domain, freq_domain, lyapunov, approx_entropy, hurst):
        """HRV脆性综合评分 (0-100)"""
        
        score = 0
        
        # 时域指标评分 (0-35分)
        # RMSSD评分
        if time_domain['RMSSD'] < self.reference_ranges['RMSSD']['risk']:
            score += 15
        elif time_domain['RMSSD'] < self.reference_ranges['RMSSD']['warning']:
            score += 8
        
        # pNN50评分
        if time_domain['pNN50'] < self.reference_ranges['pNN50']['risk']:
            score += 10
        elif time_domain['pNN50'] < self.reference_ranges['pNN50']['warning']:
            score += 5
        
        # SDNN评分
        if time_domain['SDNN'] < self.reference_ranges['SDNN']['risk']:
            score += 10
        elif time_domain['SDNN'] < self.reference_ranges['SDNN']['warning']:
            score += 5
        
        # 频域指标评分 (0-25分)
        lf_hf_ratio = freq_domain['LF_HF_ratio']
        if lf_hf_ratio > 4.0 or lf_hf_ratio < 0.5:  # 严重失衡
            score += 15
        elif lf_hf_ratio > 3.0 or lf_hf_ratio < 0.8:  # 中度失衡
            score += 10
        elif lf_hf_ratio > self.reference_ranges['LF_HF_ratio']['balanced_max'] or \
             lf_hf_ratio < self.reference_ranges['LF_HF_ratio']['balanced_min']:
            score += 5
        
        # 混沌动力学指标评分 (0-40分)
        # Lyapunov指数评分
        if abs(lyapunov) > 0.01:
            score += 10
        elif abs(lyapunov) > 0.005:
            score += 5
        
        # 近似熵评分
        if approx_entropy < 0.3 or approx_entropy > 2.0:
            score += 10
        elif approx_entropy < 0.5 or approx_entropy > 1.5:
            score += 5
        
        # Hurst指数评分
        if abs(hurst - 0.5) > 0.4:  # 严重偏离随机性
            score += 15
        elif abs(hurst - 0.5) > 0.3:
            score += 10
        elif abs(hurst - 0.5) > 0.2:
            score += 5
        
        return min(100, max(0, score))
    
    def determine_brittleness_type(self, score):
        """确定脆性分型"""
        if score <= 15:
            return 1  # I型正常调节型
        elif score <= 35:
            return 2  # II型轻度失调型
        elif score <= 55:
            return 3  # III型中度失调型
        elif score <= 75:
            return 4  # IV型重度失调型
        else:
            return 5  # V型极度刚性型
    
    def assess_risk_level(self, score):
        """评估风险等级"""
        if score <= 15:
            return "🟢 低风险"
        elif score <= 35:
            return "🟡 中低风险"
        elif score <= 55:
            return "🟠 中等风险"
        elif score <= 75:
            return "🔴 高风险"
        else:
            return "🔴 极高风险"
    
    def assess_autonomic_balance(self, freq_domain):
        """评估自主神经平衡"""
        lf_hf_ratio = freq_domain['LF_HF_ratio']
        
        if lf_hf_ratio > 3.0:
            return "交感神经过度激活"
        elif lf_hf_ratio > 2.5:
            return "交感神经优势"
        elif lf_hf_ratio >= 1.0:
            return "相对平衡"
        elif lf_hf_ratio >= 0.5:
            return "副交感神经优势"
        else:
            return "副交感神经过度激活"
    
    def generate_clinical_interpretation(self, brittleness_type, autonomic_balance, time_domain):
        """生成临床解读"""
        base_interpretations = {
            1: "自主神经功能正常，心率变异性良好，适应性调节能力强",
            2: "轻度自主神经功能失调，建议关注生活方式因素和压力管理",
            3: "中度自主神经功能异常，建议进一步评估心血管风险因素",
            4: "重度自主神经功能失调，心血管事件风险增加，建议专科会诊",
            5: "极度自主神经功能刚性，心脏猝死高风险，需要紧急医疗关注"
        }
        
        base_text = base_interpretations.get(brittleness_type, "需要专业评估")
        
        # 添加自主神经平衡信息
        balance_text = f"自主神经状态显示{autonomic_balance}"
        
        # 添加心率信息
        hr_text = ""
        if time_domain['mean_HR'] > 100:
            hr_text = "，伴有心动过速"
        elif time_domain['mean_HR'] < 50:
            hr_text = "，伴有心动过缓"
        
        return f"{base_text}。{balance_text}{hr_text}。"

def analyze_hrv_brittleness(rr_intervals, patient_id="Unknown"):
    """HRV脆性分析主函数"""
    
    print(f"💓 HRV脆性分析系统启动 - 患者ID: {patient_id}")
    print("="*60)
    
    # 初始化分析器
    analyzer = HRVBrittenessAnalyzer()
    
    # 执行分析
    result = analyzer.classify_hrv_brittleness(rr_intervals)
    
    # 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "报告头信息": {
            "报告类型": "HRV脆性分析报告 v1.0",
            "患者ID": patient_id,
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "分析方法": "混沌动力学 + 时频域HRV + 自主神经平衡分析",
            "数据质量": f"分析了 {len(rr_intervals)} 个RR间期"
        },
        "HRV脆性评估": result
    }
    
    # 保存报告
    filename = f"HRV_Brittleness_Analysis_{patient_id}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print("📊 HRV脆性分析完成")
    if "error" not in result:
        print(f"脆性分型: {result.get('脆性分型', 'N/A')}")
        print(f"脆性评分: {result.get('脆性评分', 'N/A')}")
        print(f"风险等级: {result.get('风险等级', 'N/A')}")
        print(f"自主神经平衡: {result.get('自主神经平衡', 'N/A')}")
    else:
        print(f"分析出错: {result['error']}")
    
    print(f"分析报告已保存: {filename}")
    
    return report

# 示例使用
if __name__ == "__main__":
    # 生成示例RR间期数据
    np.random.seed(42)
    
    # 模拟24小时RR间期数据
    # 正常成年人静息心率约60-80 bpm，RR间期约750-1000ms
    
    # 基础RR间期 (心率约72 bpm)
    base_rr = 833  # ms
    num_beats = 5000  # 大约1小时的数据
    
    # 添加生理性变异
    # 1. 呼吸性窦性心律不齐 (RSA) - 高频成分
    respiratory_freq = 0.25  # Hz (15次/分钟)
    time_points = np.arange(num_beats) * base_rr / 1000  # 秒
    rsa_variation = 30 * np.sin(2 * np.pi * respiratory_freq * time_points)
    
    # 2. 血压调节相关的低频变异
    lf_freq = 0.1  # Hz
    lf_variation = 20 * np.sin(2 * np.pi * lf_freq * time_points)
    
    # 3. 随机噪声
    random_variation = np.random.normal(0, 10, num_beats)
    
    # 4. 昼夜节律效应 (简化)
    circadian_variation = 50 * np.sin(2 * np.pi * time_points / (24 * 3600))
    
    # 合成RR间期
    rr_intervals = (base_rr + rsa_variation + lf_variation + 
                   random_variation + circadian_variation)
    
    # 确保RR间期在合理范围内
    rr_intervals = np.clip(rr_intervals, 400, 1500)
    
    print(f"生成了 {len(rr_intervals)} 个RR间期数据点")
    print(f"RR间期范围: {np.min(rr_intervals):.1f} - {np.max(rr_intervals):.1f} ms")
    print(f"平均心率: {60000 / np.mean(rr_intervals):.1f} bpm")
    
    # 执行分析
    result = analyze_hrv_brittleness(rr_intervals, "Demo_Patient_HRV")
    
    print("\n🎯 HRV演示分析完成！")