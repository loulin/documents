#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent2_ECG_Brittleness_Analyzer.py

基于Agent2 v5.0血糖脆性分析架构的ECG脆性分析系统
适用于心电图信号的脆性评估、智能分段和临床预警

作者: AGPAI Team
版本: v1.0
日期: 2025-08-28
"""

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import entropy
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ECGBrittenessAnalyzer:
    """ECG脆性分析器 - 基于Agent2混沌动力学架构"""
    
    def __init__(self, sampling_rate=500):
        self.sampling_rate = sampling_rate
        self.brittleness_types = {
            1: "I型正常稳定型",
            2: "II型轻度不稳定型", 
            3: "III型中度易损型",
            4: "IV型重度脆弱型",
            5: "V型极度危险型"
        }
    
    def preprocess_ecg_data(self, raw_ecg):
        """ECG数据预处理"""
        # 带通滤波 (0.5-40Hz)
        nyquist = self.sampling_rate / 2
        low = 0.5 / nyquist
        high = 40 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered_ecg = signal.filtfilt(b, a, raw_ecg)
        
        # 基线校正 (高通滤波去除基线漂移)
        b_high, a_high = signal.butter(4, 0.5/nyquist, btype='high')
        baseline_corrected = signal.filtfilt(b_high, a_high, filtered_ecg)
        
        return baseline_corrected
    
    def detect_r_peaks(self, ecg_signal):
        """R波检测"""
        # 使用Pan-Tompkins算法检测R波
        # 简化版本，实际应用中可使用更精确的算法
        peaks, _ = signal.find_peaks(ecg_signal, 
                                   height=np.max(ecg_signal) * 0.6,
                                   distance=self.sampling_rate * 0.6)  # 最小间隔0.6秒
        return peaks
    
    def calculate_rr_intervals(self, r_peaks):
        """计算RR间期"""
        rr_intervals = np.diff(r_peaks) / self.sampling_rate * 1000  # 转换为毫秒
        # 异常值过滤 (300-2000ms)
        rr_intervals = rr_intervals[(rr_intervals >= 300) & (rr_intervals <= 2000)]
        return rr_intervals
    
    def calculate_lyapunov_exponent(self, signal_data, embedding_dim=3, delay=1):
        """计算Lyapunov指数 - 混沌动力学核心指标"""
        try:
            # 相空间重构
            N = len(signal_data)
            reconstructed = np.zeros((N - (embedding_dim - 1) * delay, embedding_dim))
            
            for i in range(embedding_dim):
                reconstructed[:, i] = signal_data[i * delay:N - (embedding_dim - 1 - i) * delay]
            
            # 计算Lyapunov指数
            lyapunov_values = []
            for i in range(1, len(reconstructed) - 1):
                if i + 1 < len(reconstructed):
                    distance = np.linalg.norm(reconstructed[i + 1] - reconstructed[i])
                    if distance > 0:
                        lyapunov_values.append(np.log(distance))
            
            if len(lyapunov_values) > 0:
                lyapunov_exponent = np.mean(np.diff(lyapunov_values))
            else:
                lyapunov_exponent = 0
                
            return lyapunov_exponent
        except:
            return 0
    
    def calculate_approximate_entropy(self, signal_data, m=2, r=None):
        """计算近似熵"""
        try:
            N = len(signal_data)
            if r is None:
                r = 0.2 * np.std(signal_data)
            
            def maxdist(xi, xj, N):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def phi(m):
                patterns = np.array([signal_data[i:i + m] for i in range(N - m + 1)])
                C = np.zeros(N - m + 1)
                for i in range(N - m + 1):
                    template = patterns[i]
                    matches = sum([1 for j in range(N - m + 1) if maxdist(template, patterns[j], m) <= r])
                    if matches > 0:
                        C[i] = matches / (N - m + 1)
                
                phi = sum([np.log(c) if c > 0 else 0 for c in C]) / (N - m + 1)
                return phi
            
            approximate_entropy = phi(m) - phi(m + 1)
            return approximate_entropy
        except:
            return 0
    
    def calculate_hurst_exponent(self, signal_data):
        """计算Hurst指数"""
        try:
            N = len(signal_data)
            if N < 100:
                return 0.5
                
            # R/S分析
            lags = np.logspace(1, np.log10(N//4), 20).astype(int)
            rs = []
            
            for lag in lags:
                sections = N // lag
                if sections == 0:
                    continue
                    
                section_data = signal_data[:sections*lag].reshape(sections, lag)
                
                rs_values = []
                for section in section_data:
                    mean_val = np.mean(section)
                    deviations = section - mean_val
                    cumsum_dev = np.cumsum(deviations)
                    
                    R = np.max(cumsum_dev) - np.min(cumsum_dev)
                    S = np.std(section)
                    
                    if S > 0:
                        rs_values.append(R / S)
                
                if len(rs_values) > 0:
                    rs.append(np.mean(rs_values))
            
            if len(rs) > 2 and len(lags) > 2:
                # 线性拟合
                log_lags = np.log10(lags[:len(rs)])
                log_rs = np.log10(rs)
                
                valid_indices = ~(np.isinf(log_rs) | np.isnan(log_rs))
                if np.sum(valid_indices) > 2:
                    hurst = np.polyfit(log_lags[valid_indices], log_rs[valid_indices], 1)[0]
                    return hurst
            
            return 0.5
        except:
            return 0.5
    
    def calculate_sample_entropy(self, signal_data, m=2, r=None):
        """计算样本熵"""
        try:
            N = len(signal_data)
            if r is None:
                r = 0.2 * np.std(signal_data)
            
            def chebyshev_distance(a, b):
                return max(abs(a - b))
            
            # 计算模板匹配
            A = 0.0  # m+1长度匹配数
            B = 0.0  # m长度匹配数
            
            for i in range(N - m):
                template_m = signal_data[i:i + m]
                template_m_plus = signal_data[i:i + m + 1] if i + m + 1 <= N else None
                
                for j in range(i + 1, N - m):
                    if j + m <= N:
                        test_m = signal_data[j:j + m]
                        
                        # m长度匹配
                        if max([chebyshev_distance(template_m[k], test_m[k]) for k in range(m)]) <= r:
                            B += 1.0
                            
                            # m+1长度匹配
                            if (template_m_plus is not None and 
                                j + m + 1 <= N and 
                                chebyshev_distance(template_m_plus[m], signal_data[j + m]) <= r):
                                A += 1.0
            
            if B > 0:
                sample_entropy = -np.log(A / B)
            else:
                sample_entropy = 0
                
            return sample_entropy
        except:
            return 0
    
    def calculate_hrv_time_domain(self, rr_intervals):
        """计算HRV时域指标"""
        if len(rr_intervals) < 2:
            return {'RMSSD': 0, 'pNN50': 0, 'SDNN': 0}
            
        # RMSSD: 相邻RR间期差值的均方根
        rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
        
        # pNN50: 相邻RR间期差值>50ms的百分比
        nn50 = np.sum(np.abs(np.diff(rr_intervals)) > 50)
        pnn50 = nn50 / len(rr_intervals) * 100
        
        # SDNN: RR间期的标准差
        sdnn = np.std(rr_intervals)
        
        return {
            'RMSSD': rmssd,
            'pNN50': pnn50,
            'SDNN': sdnn
        }
    
    def calculate_qt_variability(self, ecg_signal, r_peaks):
        """计算QT变异性"""
        try:
            qt_intervals = []
            
            for i in range(len(r_peaks) - 1):
                # 简化的QT间期检测 (实际应用中需要更精确的T波检测)
                qrs_start = r_peaks[i]
                next_qrs = r_peaks[i + 1]
                
                # 在RR间期的后70%区域寻找T波结束点
                search_start = int(qrs_start + (next_qrs - qrs_start) * 0.3)
                search_end = int(qrs_start + (next_qrs - qrs_start) * 0.8)
                
                if search_end < len(ecg_signal):
                    # 寻找T波结束点 (最小二阶导数点)
                    search_region = ecg_signal[search_start:search_end]
                    second_derivative = np.gradient(np.gradient(search_region))
                    t_end_relative = np.argmin(np.abs(second_derivative))
                    
                    qt_interval = (search_start + t_end_relative - qrs_start) / self.sampling_rate * 1000
                    
                    if 300 <= qt_interval <= 600:  # 合理的QT间期范围
                        qt_intervals.append(qt_interval)
            
            if len(qt_intervals) > 1:
                qt_variability = np.std(qt_intervals)
            else:
                qt_variability = 0
                
            return qt_variability
        except:
            return 0
    
    def classify_ecg_brittleness(self, ecg_data):
        """ECG脆性分型"""
        try:
            # 预处理
            clean_ecg = self.preprocess_ecg_data(ecg_data)
            
            # R波检测
            r_peaks = self.detect_r_peaks(clean_ecg)
            rr_intervals = self.calculate_rr_intervals(r_peaks)
            
            # 混沌动力学指标
            lyapunov = self.calculate_lyapunov_exponent(rr_intervals)
            approx_entropy = self.calculate_approximate_entropy(rr_intervals)
            hurst_exponent = self.calculate_hurst_exponent(rr_intervals)
            sample_entropy = self.calculate_sample_entropy(rr_intervals)
            
            # HRV指标
            hrv_metrics = self.calculate_hrv_time_domain(rr_intervals)
            
            # QT变异性
            qt_variability = self.calculate_qt_variability(clean_ecg, r_peaks)
            
            # ECG脆性评分计算
            brittleness_score = self.calculate_ecg_brittleness_score(
                lyapunov, approx_entropy, hurst_exponent, hrv_metrics, qt_variability
            )
            
            # 脆性分型
            brittleness_type = self.determine_brittleness_type(brittleness_score)
            risk_level = self.assess_risk_level(brittleness_score)
            
            return {
                "脆性分型": self.brittleness_types[brittleness_type],
                "脆性评分": f"{brittleness_score:.1f}/100",
                "风险等级": risk_level,
                "混沌动力学指标": {
                    "Lyapunov指数": f"{lyapunov:.6f}",
                    "近似熵": f"{approx_entropy:.4f}",
                    "Hurst指数": f"{hurst_exponent:.4f}",
                    "样本熵": f"{sample_entropy:.4f}"
                },
                "心率变异性": hrv_metrics,
                "QT变异性": f"{qt_variability:.2f}ms",
                "临床解读": self.generate_clinical_interpretation(
                    brittleness_type, brittleness_score, hrv_metrics
                )
            }
            
        except Exception as e:
            return {"error": f"分析过程出错: {str(e)}"}
    
    def calculate_ecg_brittleness_score(self, lyapunov, approx_entropy, hurst, hrv_metrics, qt_var):
        """ECG脆性综合评分 (0-100)"""
        
        # 混沌动力学评分 (0-40分)
        chaos_score = 0
        
        # Lyapunov指数评分
        if lyapunov > 0.001:
            chaos_score += min(15, abs(lyapunov) * 10000)
        
        # 熵值评分 
        if approx_entropy < 0.5:
            chaos_score += 10
        elif approx_entropy > 1.5:
            chaos_score += 5
        
        # Hurst指数评分
        if abs(hurst - 0.5) > 0.3:
            chaos_score += 15
        
        # HRV评分 (0-35分)
        hrv_score = 0
        if hrv_metrics['RMSSD'] < 20:  # 低HRV
            hrv_score += 15
        if hrv_metrics['pNN50'] < 5:   # 低变异性
            hrv_score += 10  
        if hrv_metrics['SDNN'] < 30:   # 低总变异性
            hrv_score += 10
        
        # QT变异性评分 (0-25分)
        qt_score = 0
        if qt_var > 30:  # 高QT变异性
            qt_score += min(25, qt_var * 0.5)
        
        total_score = chaos_score + hrv_score + qt_score
        return min(100, max(0, total_score))
    
    def determine_brittleness_type(self, score):
        """确定脆性分型"""
        if score <= 20:
            return 1  # I型正常稳定型
        elif score <= 40:
            return 2  # II型轻度不稳定型
        elif score <= 60:
            return 3  # III型中度易损型
        elif score <= 80:
            return 4  # IV型重度脆弱型
        else:
            return 5  # V型极度危险型
    
    def assess_risk_level(self, score):
        """评估风险等级"""
        if score <= 20:
            return "🟢 低风险"
        elif score <= 40:
            return "🟡 中低风险"
        elif score <= 60:
            return "🟠 中等风险"
        elif score <= 80:
            return "🔴 高风险"
        else:
            return "🔴 极高风险"
    
    def generate_clinical_interpretation(self, brittleness_type, score, hrv_metrics):
        """生成临床解读"""
        interpretations = {
            1: "心律稳定，自主神经功能正常，心脏电活动规律性良好",
            2: "轻度心律不稳定，建议定期监测，注意生活方式调整",
            3: "中度心电不稳定，建议进一步心电图检查，评估潜在心律失常",
            4: "重度心电脆性，存在恶性心律失常风险，建议紧急心内科会诊",
            5: "极度危险心电状态，心脏猝死高风险，需要立即医疗干预"
        }
        
        return interpretations.get(brittleness_type, "需要专业医师进一步评估")

def analyze_ecg_brittleness(ecg_data, patient_id="Unknown", sampling_rate=500):
    """ECG脆性分析主函数"""
    
    print(f"🫀 ECG脆性分析系统启动 - 患者ID: {patient_id}")
    print("="*60)
    
    # 初始化分析器
    analyzer = ECGBrittenessAnalyzer(sampling_rate=sampling_rate)
    
    # 执行分析
    result = analyzer.classify_ecg_brittleness(ecg_data)
    
    # 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "报告头信息": {
            "报告类型": "ECG脆性分析报告 v1.0",
            "患者ID": patient_id,
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "分析方法": "混沌动力学 + HRV + QT变异性分析"
        },
        "ECG脆性评估": result
    }
    
    # 保存报告
    filename = f"ECG_Brittleness_Analysis_{patient_id}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print("📊 ECG脆性分析完成")
    print(f"脆性分型: {result.get('脆性分型', 'N/A')}")
    print(f"脆性评分: {result.get('脆性评分', 'N/A')}")
    print(f"风险等级: {result.get('风险等级', 'N/A')}")
    print(f"分析报告已保存: {filename}")
    
    return report

# 示例使用
if __name__ == "__main__":
    # 生成示例ECG数据 (实际使用时替换为真实数据)
    import matplotlib.pyplot as plt
    
    # 模拟ECG信号 (窦性心律 + 噪声)
    duration = 30  # 30秒
    sampling_rate = 500
    t = np.linspace(0, duration, duration * sampling_rate)
    
    # 基础窦性心律 (心率约70bpm)
    heart_rate = 70
    ecg_signal = np.zeros_like(t)
    
    # 添加QRS波群
    rr_interval = 60 / heart_rate
    for beat_time in np.arange(0, duration, rr_interval):
        beat_idx = int(beat_time * sampling_rate)
        if beat_idx < len(ecg_signal) - 100:
            # 简化的QRS波形
            qrs_duration = int(0.1 * sampling_rate)  # 100ms
            qrs_wave = signal.gaussian(qrs_duration, std=qrs_duration//8)
            end_idx = min(beat_idx + qrs_duration, len(ecg_signal))
            ecg_signal[beat_idx:end_idx] += qrs_wave[:end_idx-beat_idx]
    
    # 添加噪声和变异性
    noise = np.random.normal(0, 0.1, len(ecg_signal))
    ecg_signal += noise
    
    # 执行分析
    result = analyze_ecg_brittleness(ecg_signal, "Demo_Patient_001", sampling_rate)
    
    print("\n🎯 演示分析完成！")