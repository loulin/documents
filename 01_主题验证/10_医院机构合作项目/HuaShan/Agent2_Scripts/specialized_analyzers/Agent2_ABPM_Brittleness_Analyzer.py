#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent2_ABPM_Brittleness_Analyzer.py

基于Agent2 v5.0血糖脆性分析架构的ABPM脆性分析系统
适用于24小时动态血压监测的脆性评估、昼夜节律分析和心血管风险预测

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

class ABPMBrittenessAnalyzer:
    """ABPM脆性分析器 - 基于Agent2混沌动力学架构"""
    
    def __init__(self):
        self.brittleness_types = {
            1: "I型正常调节型",
            2: "II型轻度失调型",
            3: "III型中度失调型",
            4: "IV型重度失调型",
            5: "V型极度不稳定型"
        }
        
        # ABPM参考标准 (基于国际指南)
        self.reference_standards = {
            "daytime_awake": {"SBP": 135, "DBP": 85},
            "nighttime_sleep": {"SBP": 120, "DBP": 70},
            "24h_overall": {"SBP": 130, "DBP": 80},
            "dipping_normal": {"min": 10, "max": 20},  # 正常夜间下降10-20%
            "variability_normal": {"cv_threshold": 15}   # CV<15%为正常变异性
        }
        
        # 血压脆性分型阈值
        self.brittleness_thresholds = {
            "dipping_ratio": {"normal": (10, 20), "abnormal": (-5, 5)},
            "cv_threshold": {"normal": 12, "warning": 15, "high": 20},
            "morning_surge": {"normal": 35, "warning": 45, "high": 55}
        }
    
    def preprocess_abpm_data(self, bp_data):
        """ABPM数据预处理"""
        try:
            # 转换为DataFrame格式
            if isinstance(bp_data, dict):
                df = pd.DataFrame(bp_data)
            else:
                df = bp_data.copy()
            
            # 确保有必要的列
            required_columns = ['timestamp', 'SBP', 'DBP']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必要列: {col}")
            
            # 时间戳处理
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp').reset_index(drop=True)
            
            # 异常值检测和过滤
            df = self.filter_bp_outliers(df)
            
            # 计算衍生参数
            df['pulse_pressure'] = df['SBP'] - df['DBP']
            df['mean_arterial_pressure'] = df['DBP'] + df['pulse_pressure'] / 3
            df['hour'] = df['timestamp'].dt.hour if 'timestamp' in df.columns else range(len(df))
            
            return df
            
        except Exception as e:
            print(f"数据预处理错误: {e}")
            return None
    
    def filter_bp_outliers(self, df):
        """血压异常值过滤"""
        # 血压合理范围
        sbp_valid = (df['SBP'] >= 70) & (df['SBP'] <= 250)
        dbp_valid = (df['DBP'] >= 40) & (df['DBP'] <= 150)
        
        # 脉压合理范围
        pulse_pressure = df['SBP'] - df['DBP']
        pp_valid = (pulse_pressure >= 20) & (pulse_pressure <= 100)
        
        # 组合筛选
        valid_mask = sbp_valid & dbp_valid & pp_valid
        
        print(f"数据过滤: {len(df)} -> {np.sum(valid_mask)} 个有效测量点")
        
        return df[valid_mask].reset_index(drop=True)
    
    def classify_day_night_periods(self, df):
        """昼夜时段分类"""
        try:
            # 基于时间分类昼夜
            if 'hour' in df.columns:
                daytime_mask = (df['hour'] >= 6) & (df['hour'] < 22)  # 6:00-22:00
                nighttime_mask = (df['hour'] >= 22) | (df['hour'] < 6)  # 22:00-6:00
            else:
                # 如果没有时间信息，按数据点比例分配
                total_points = len(df)
                daytime_mask = np.zeros(total_points, dtype=bool)
                nighttime_mask = np.zeros(total_points, dtype=bool)
                
                # 假设2/3时间为白天，1/3为夜间
                day_points = int(total_points * 0.67)
                daytime_mask[:day_points] = True
                nighttime_mask[day_points:] = True
            
            day_data = df[daytime_mask]
            night_data = df[nighttime_mask]
            
            return day_data, night_data
            
        except Exception as e:
            print(f"昼夜分类错误: {e}")
            # 返回空的DataFrame
            return pd.DataFrame(), pd.DataFrame()
    
    def calculate_circadian_rhythm(self, df):
        """计算昼夜节律指标"""
        try:
            day_data, night_data = self.classify_day_night_periods(df)
            
            if len(day_data) < 5 or len(night_data) < 5:
                return {
                    "dipping_ratio_sbp": 0,
                    "dipping_ratio_dbp": 0,
                    "dipping_pattern": "数据不足",
                    "day_night_difference": {"SBP": 0, "DBP": 0}
                }
            
            # 计算白天和夜间平均血压
            day_sbp_mean = day_data['SBP'].mean()
            day_dbp_mean = day_data['DBP'].mean()
            night_sbp_mean = night_data['SBP'].mean()
            night_dbp_mean = night_data['DBP'].mean()
            
            # 计算夜间下降率 (Dipping ratio)
            dipping_ratio_sbp = ((day_sbp_mean - night_sbp_mean) / day_sbp_mean) * 100
            dipping_ratio_dbp = ((day_dbp_mean - night_dbp_mean) / day_dbp_mean) * 100
            
            # 分类昼夜节律模式
            dipping_pattern = self.classify_dipping_pattern(dipping_ratio_sbp)
            
            return {
                "day_sbp_mean": day_sbp_mean,
                "day_dbp_mean": day_dbp_mean,
                "night_sbp_mean": night_sbp_mean,
                "night_dbp_mean": night_dbp_mean,
                "dipping_ratio_sbp": dipping_ratio_sbp,
                "dipping_ratio_dbp": dipping_ratio_dbp,
                "dipping_pattern": dipping_pattern,
                "day_night_difference": {
                    "SBP": day_sbp_mean - night_sbp_mean,
                    "DBP": day_dbp_mean - night_dbp_mean
                }
            }
            
        except Exception as e:
            print(f"昼夜节律计算错误: {e}")
            return {"dipping_ratio_sbp": 0, "dipping_pattern": "计算错误"}
    
    def classify_dipping_pattern(self, dipping_ratio):
        """分类昼夜节律模式"""
        if dipping_ratio >= 20:
            return "Extreme Dipper (过度下降型)"
        elif 10 <= dipping_ratio < 20:
            return "Normal Dipper (正常下降型)"
        elif 0 <= dipping_ratio < 10:
            return "Non-dipper (非下降型)"
        else:
            return "Riser (反转型)"
    
    def calculate_bp_variability(self, df):
        """计算血压变异性指标"""
        try:
            # 标准血压变异性指标
            sbp_cv = (df['SBP'].std() / df['SBP'].mean()) * 100
            dbp_cv = (df['DBP'].std() / df['DBP'].mean()) * 100
            
            # 平均实际变异性 (ARV)
            sbp_arv = df['SBP'].diff().abs().mean()
            dbp_arv = df['DBP'].diff().abs().mean()
            
            # 血压负荷 (BP Load) - 异常血压测量的百分比
            day_data, night_data = self.classify_day_night_periods(df)
            
            if len(day_data) > 0:
                day_sbp_load = (day_data['SBP'] > 135).mean() * 100
                day_dbp_load = (day_data['DBP'] > 85).mean() * 100
            else:
                day_sbp_load = day_dbp_load = 0
                
            if len(night_data) > 0:
                night_sbp_load = (night_data['SBP'] > 120).mean() * 100
                night_dbp_load = (night_data['DBP'] > 70).mean() * 100
            else:
                night_sbp_load = night_dbp_load = 0
            
            return {
                "SBP_CV": sbp_cv,
                "DBP_CV": dbp_cv,
                "SBP_ARV": sbp_arv,
                "DBP_ARV": dbp_arv,
                "day_SBP_load": day_sbp_load,
                "day_DBP_load": day_dbp_load,
                "night_SBP_load": night_sbp_load,
                "night_DBP_load": night_dbp_load
            }
            
        except Exception as e:
            print(f"血压变异性计算错误: {e}")
            return {"SBP_CV": 0, "DBP_CV": 0}
    
    def calculate_lyapunov_exponent(self, bp_values, embedding_dim=3, delay=1):
        """计算Lyapunov指数 - 混沌动力学核心指标"""
        try:
            if len(bp_values) < 50:
                return 0
            
            # 相空间重构
            N = len(bp_values)
            reconstructed = np.zeros((N - (embedding_dim - 1) * delay, embedding_dim))
            
            for i in range(embedding_dim):
                start_idx = i * delay
                end_idx = N - (embedding_dim - 1 - i) * delay
                reconstructed[:, i] = bp_values[start_idx:end_idx]
            
            # 计算Lyapunov指数
            lyapunov_values = []
            for i in range(1, min(len(reconstructed) - 1, 200)):  # 限制计算量
                # 寻找最近邻点
                distances = np.linalg.norm(reconstructed - reconstructed[i], axis=1)
                distances[i] = np.inf  # 排除自身
                nearest_idx = np.argmin(distances)
                
                # 计算演化散度
                if i + 1 < len(reconstructed) and nearest_idx + 1 < len(reconstructed):
                    initial_distance = distances[nearest_idx]
                    evolved_distance = np.linalg.norm(
                        reconstructed[i + 1] - reconstructed[nearest_idx + 1]
                    )
                    
                    if initial_distance > 0 and evolved_distance > 0:
                        divergence = np.log(evolved_distance / initial_distance)
                        lyapunov_values.append(divergence)
            
            lyapunov_exponent = np.mean(lyapunov_values) if lyapunov_values else 0
            return lyapunov_exponent
            
        except Exception as e:
            print(f"Lyapunov指数计算错误: {e}")
            return 0
    
    def calculate_approximate_entropy(self, bp_values, m=2, r=None):
        """计算近似熵"""
        try:
            N = len(bp_values)
            if N < 20:
                return 0
                
            if r is None:
                r = 0.2 * np.std(bp_values)
            
            def maxdist(xi, xj):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def phi(m):
                patterns = np.array([bp_values[i:i + m] for i in range(N - m + 1)])
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
            
        except Exception as e:
            print(f"近似熵计算错误: {e}")
            return 0
    
    def calculate_hurst_exponent(self, bp_values):
        """计算Hurst指数"""
        try:
            N = len(bp_values)
            if N < 20:
                return 0.5
            
            # R/S分析
            lags = np.logspace(1, np.log10(N//3), 10).astype(int)
            rs_values = []
            
            for lag in lags:
                if lag >= N:
                    continue
                    
                sections = N // lag
                section_rs = []
                
                for i in range(sections):
                    start_idx = i * lag
                    end_idx = (i + 1) * lag
                    section_data = bp_values[start_idx:end_idx]
                    
                    if len(section_data) < 3:
                        continue
                    
                    # 计算累积偏差
                    mean_val = np.mean(section_data)
                    deviations = section_data - mean_val
                    cumsum_dev = np.cumsum(deviations)
                    
                    # R: 极差，S: 标准差
                    R = np.max(cumsum_dev) - np.min(cumsum_dev)
                    S = np.std(section_data)
                    
                    if S > 0:
                        section_rs.append(R / S)
                
                if len(section_rs) > 0:
                    rs_values.append(np.mean(section_rs))
            
            # 线性拟合
            if len(rs_values) >= 3:
                valid_lags = lags[:len(rs_values)]
                log_lags = np.log10(valid_lags)
                log_rs = np.log10(rs_values)
                
                valid_mask = ~(np.isinf(log_rs) | np.isnan(log_rs))
                if np.sum(valid_mask) >= 3:
                    hurst = np.polyfit(log_lags[valid_mask], log_rs[valid_mask], 1)[0]
                    return max(0, min(1, hurst))
            
            return 0.5
            
        except Exception as e:
            print(f"Hurst指数计算错误: {e}")
            return 0.5
    
    def calculate_morning_surge(self, df):
        """计算晨起血压高峰"""
        try:
            if 'hour' not in df.columns or len(df) < 20:
                return {"morning_surge_sbp": 0, "morning_surge_dbp": 0}
            
            # 定义时间段
            morning_mask = (df['hour'] >= 6) & (df['hour'] <= 10)  # 晨起6-10点
            night_mask = (df['hour'] >= 0) & (df['hour'] <= 6)     # 夜间0-6点
            
            morning_data = df[morning_mask]
            night_data = df[night_mask]
            
            if len(morning_data) < 3 or len(night_data) < 3:
                return {"morning_surge_sbp": 0, "morning_surge_dbp": 0}
            
            # 计算晨起血压高峰 (晨起平均值 - 夜间最低值)
            morning_sbp_mean = morning_data['SBP'].mean()
            morning_dbp_mean = morning_data['DBP'].mean()
            night_sbp_min = night_data['SBP'].min()
            night_dbp_min = night_data['DBP'].min()
            
            morning_surge_sbp = morning_sbp_mean - night_sbp_min
            morning_surge_dbp = morning_dbp_mean - night_dbp_min
            
            return {
                "morning_surge_sbp": morning_surge_sbp,
                "morning_surge_dbp": morning_surge_dbp,
                "morning_sbp_mean": morning_sbp_mean,
                "morning_dbp_mean": morning_dbp_mean,
                "night_sbp_min": night_sbp_min,
                "night_dbp_min": night_dbp_min
            }
            
        except Exception as e:
            print(f"晨起血压高峰计算错误: {e}")
            return {"morning_surge_sbp": 0, "morning_surge_dbp": 0}
    
    def classify_abpm_brittleness(self, bp_data):
        """ABPM脆性分型"""
        try:
            # 数据预处理
            df = self.preprocess_abpm_data(bp_data)
            if df is None or len(df) < 10:
                return {"error": "ABPM数据不足或格式错误"}
            
            print(f"分析 {len(df)} 个血压测量点")
            
            # 基础统计
            basic_stats = {
                "mean_SBP": df['SBP'].mean(),
                "mean_DBP": df['DBP'].mean(), 
                "mean_pulse_pressure": df['pulse_pressure'].mean(),
                "mean_MAP": df['mean_arterial_pressure'].mean()
            }
            
            # 昼夜节律分析
            circadian_rhythm = self.calculate_circadian_rhythm(df)
            
            # 血压变异性
            bp_variability = self.calculate_bp_variability(df)
            
            # 晨起血压高峰
            morning_surge = self.calculate_morning_surge(df)
            
            # 混沌动力学分析
            lyapunov_sbp = self.calculate_lyapunov_exponent(df['SBP'].values)
            lyapunov_dbp = self.calculate_lyapunov_exponent(df['DBP'].values)
            approx_entropy_sbp = self.calculate_approximate_entropy(df['SBP'].values)
            hurst_sbp = self.calculate_hurst_exponent(df['SBP'].values)
            
            # ABPM脆性综合评分
            brittleness_score = self.calculate_abpm_brittleness_score(
                circadian_rhythm, bp_variability, morning_surge,
                lyapunov_sbp, approx_entropy_sbp, hurst_sbp
            )
            
            # 脆性分型和风险评估
            brittleness_type = self.determine_brittleness_type(brittleness_score)
            risk_level = self.assess_cardiovascular_risk(brittleness_score)
            hypertension_pattern = self.classify_hypertension_pattern(basic_stats, circadian_rhythm)
            
            return {
                "脆性分型": self.brittleness_types[brittleness_type],
                "脆性评分": f"{brittleness_score:.1f}/100",
                "心血管风险等级": risk_level,
                "高血压模式": hypertension_pattern,
                "基础血压指标": {
                    "24小时平均收缩压": f"{basic_stats['mean_SBP']:.1f} mmHg",
                    "24小时平均舒张压": f"{basic_stats['mean_DBP']:.1f} mmHg",
                    "平均脉压": f"{basic_stats['mean_pulse_pressure']:.1f} mmHg",
                    "平均动脉压": f"{basic_stats['mean_MAP']:.1f} mmHg"
                },
                "昼夜节律分析": {
                    "白天平均收缩压": f"{circadian_rhythm.get('day_sbp_mean', 0):.1f} mmHg",
                    "夜间平均收缩压": f"{circadian_rhythm.get('night_sbp_mean', 0):.1f} mmHg",
                    "夜间下降率": f"{circadian_rhythm.get('dipping_ratio_sbp', 0):.1f}%",
                    "昼夜节律模式": circadian_rhythm.get('dipping_pattern', '未知')
                },
                "血压变异性": {
                    "收缩压变异系数": f"{bp_variability.get('SBP_CV', 0):.1f}%",
                    "舒张压变异系数": f"{bp_variability.get('DBP_CV', 0):.1f}%",
                    "白天收缩压负荷": f"{bp_variability.get('day_SBP_load', 0):.1f}%",
                    "夜间收缩压负荷": f"{bp_variability.get('night_SBP_load', 0):.1f}%"
                },
                "晨起血压高峰": {
                    "收缩压晨峰": f"{morning_surge.get('morning_surge_sbp', 0):.1f} mmHg",
                    "舒张压晨峰": f"{morning_surge.get('morning_surge_dbp', 0):.1f} mmHg"
                },
                "混沌动力学指标": {
                    "收缩压Lyapunov指数": f"{lyapunov_sbp:.6f}",
                    "收缩压近似熵": f"{approx_entropy_sbp:.4f}",
                    "收缩压Hurst指数": f"{hurst_sbp:.4f}"
                },
                "临床解读": self.generate_clinical_interpretation(
                    brittleness_type, circadian_rhythm, bp_variability, risk_level
                )
            }
            
        except Exception as e:
            print(f"ABPM脆性分析错误: {e}")
            return {"error": f"ABPM分析过程出错: {str(e)}"}
    
    def calculate_abpm_brittleness_score(self, circadian, variability, morning_surge, 
                                       lyapunov, approx_entropy, hurst):
        """ABPM脆性综合评分 (0-100)"""
        score = 0
        
        # 昼夜节律评分 (0-30分)
        dipping_ratio = circadian.get('dipping_ratio_sbp', 10)
        if dipping_ratio < 0:  # Riser模式
            score += 30
        elif dipping_ratio < 5:  # Non-dipper
            score += 20
        elif dipping_ratio > 25:  # Extreme dipper
            score += 15
        elif dipping_ratio < 10:  # 轻度异常
            score += 10
        
        # 血压变异性评分 (0-25分)
        sbp_cv = variability.get('SBP_CV', 10)
        if sbp_cv > 20:
            score += 15
        elif sbp_cv > 15:
            score += 10
        elif sbp_cv > 12:
            score += 5
        
        # 血压负荷评分
        day_load = variability.get('day_SBP_load', 0)
        night_load = variability.get('night_SBP_load', 0)
        if day_load > 50 or night_load > 30:
            score += 10
        
        # 晨起血压高峰评分 (0-20分)
        morning_sbp_surge = morning_surge.get('morning_surge_sbp', 30)
        if morning_sbp_surge > 55:
            score += 20
        elif morning_sbp_surge > 45:
            score += 15
        elif morning_sbp_surge > 35:
            score += 8
        
        # 混沌动力学评分 (0-25分)
        if abs(lyapunov) > 0.01:
            score += 10
        if approx_entropy < 0.5 or approx_entropy > 2.0:
            score += 8
        if abs(hurst - 0.5) > 0.3:
            score += 7
        
        return min(100, max(0, score))
    
    def determine_brittleness_type(self, score):
        """确定脆性分型"""
        if score <= 20:
            return 1  # I型正常调节型
        elif score <= 40:
            return 2  # II型轻度失调型
        elif score <= 60:
            return 3  # III型中度失调型
        elif score <= 80:
            return 4  # IV型重度失调型
        else:
            return 5  # V型极度不稳定型
    
    def assess_cardiovascular_risk(self, score):
        """评估心血管风险等级"""
        if score <= 20:
            return "🟢 低风险"
        elif score <= 40:
            return "🟡 中等风险"
        elif score <= 60:
            return "🟠 中高风险"
        elif score <= 80:
            return "🔴 高风险"
        else:
            return "🔴 极高风险"
    
    def classify_hypertension_pattern(self, basic_stats, circadian):
        """分类高血压模式"""
        mean_sbp = basic_stats['mean_SBP']
        mean_dbp = basic_stats['mean_DBP']
        dipping_pattern = circadian.get('dipping_pattern', '')
        
        # 血压水平分类
        if mean_sbp >= 140 or mean_dbp >= 90:
            bp_level = "高血压"
        elif mean_sbp >= 130 or mean_dbp >= 80:
            bp_level = "血压偏高"
        else:
            bp_level = "血压正常"
        
        # 结合昼夜节律模式
        if "Non-dipper" in dipping_pattern:
            pattern = f"{bp_level} + 非杓型"
        elif "Riser" in dipping_pattern:
            pattern = f"{bp_level} + 反杓型"
        elif "Extreme" in dipping_pattern:
            pattern = f"{bp_level} + 超杓型"
        else:
            pattern = f"{bp_level} + 杓型"
        
        return pattern
    
    def generate_clinical_interpretation(self, brittleness_type, circadian, variability, risk_level):
        """生成临床解读"""
        base_interpretations = {
            1: "血压调节功能正常，昼夜节律良好，心血管风险较低",
            2: "轻度血压调节异常，建议生活方式干预和定期监测",
            3: "中度血压脆性增加，存在心血管事件风险，建议药物治疗",
            4: "重度血压调节失衡，心血管风险显著增加，需要积极治疗",
            5: "极度血压不稳定，存在急性心血管事件高风险，需紧急处理"
        }
        
        base_text = base_interpretations.get(brittleness_type, "需要专业评估")
        
        # 添加昼夜节律信息
        dipping_pattern = circadian.get('dipping_pattern', '')
        if "Non-dipper" in dipping_pattern:
            rhythm_text = "，夜间血压下降不足，增加靶器官损害风险"
        elif "Riser" in dipping_pattern:
            rhythm_text = "，夜间血压反而升高，心血管风险极大增加"
        else:
            rhythm_text = "，昼夜节律相对正常"
        
        # 添加变异性信息
        sbp_cv = variability.get('SBP_CV', 0)
        if sbp_cv > 15:
            variability_text = "，血压变异性增大"
        else:
            variability_text = ""
        
        return f"{base_text}{rhythm_text}{variability_text}。"

def analyze_abpm_brittleness(bp_data, patient_id="Unknown"):
    """ABPM脆性分析主函数"""
    
    print(f"🩺 ABPM脆性分析系统启动 - 患者ID: {patient_id}")
    print("="*60)
    
    # 初始化分析器
    analyzer = ABPMBrittenessAnalyzer()
    
    # 执行分析
    result = analyzer.classify_abmp_brittleness(bp_data)
    
    # 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "报告头信息": {
            "报告类型": "ABPM脆性分析报告 v1.0",
            "患者ID": patient_id,
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "分析方法": "混沌动力学 + 昼夜节律 + 血压变异性 + 脆性分型分析"
        },
        "ABPM脆性评估": result
    }
    
    # 保存报告
    filename = f"ABPM_Brittleness_Analysis_{patient_id}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print("📊 ABMP脆性分析完成")
    if "error" not in result:
        print(f"脆性分型: {result.get('脆性分型', 'N/A')}")
        print(f"脆性评分: {result.get('脆性评分', 'N/A')}")
        print(f"心血管风险: {result.get('心血管风险等级', 'N/A')}")
        print(f"高血压模式: {result.get('高血压模式', 'N/A')}")
    else:
        print(f"分析出错: {result['error']}")
    
    print(f"分析报告已保存: {filename}")
    
    return report

# 示例使用
if __name__ == "__main__":
    # 生成示例24小时ABPM数据
    np.random.seed(42)
    
    print("生成示例24小时ABPM数据...")
    
    # 模拟24小时血压数据 (每15分钟测量一次)
    hours = 24
    measurements_per_hour = 4
    total_measurements = hours * measurements_per_hour
    
    # 生成时间序列
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    timestamps = [start_time + timedelta(minutes=i*15) for i in range(total_measurements)]
    
    # 模拟血压昼夜变化
    sbp_values = []
    dbp_values = []
    
    for i in range(total_measurements):
        hour = timestamps[i].hour
        
        # 基础血压 (模拟轻度高血压患者)
        if 6 <= hour <= 22:  # 白天
            base_sbp = 145 + 10 * np.sin((hour - 6) / 16 * 2 * np.pi)  # 白天血压较高
            base_dbp = 90 + 5 * np.sin((hour - 6) / 16 * 2 * np.pi)
        else:  # 夜间
            base_sbp = 125 + 5 * np.random.normal(0, 1)  # 夜间血压下降
            base_dbp = 75 + 3 * np.random.normal(0, 1)
        
        # 添加随机变异 (模拟血压变异性)
        sbp_variation = np.random.normal(0, 12)  # 较大变异性
        dbp_variation = np.random.normal(0, 8)
        
        # 模拟晨起血压高峰
        if 6 <= hour <= 9:
            morning_surge = 15 * (1 - abs(hour - 7.5) / 1.5)  # 7:30左右最高
            base_sbp += morning_surge
            base_dbp += morning_surge * 0.6
        
        final_sbp = base_sbp + sbp_variation
        final_dbp = base_dbp + dbp_variation
        
        # 确保合理范围
        final_sbp = max(90, min(200, final_sbp))
        final_dbp = max(50, min(120, final_dbp))
        
        # 确保收缩压>舒张压
        if final_sbp <= final_dbp:
            final_sbp = final_dbp + 20
        
        sbp_values.append(final_sbp)
        dbp_values.append(final_dbp)
    
    # 构建ABPM数据
    abpm_data = {
        'timestamp': timestamps,
        'SBP': sbp_values,
        'DBP': dbp_values
    }
    
    print(f"生成了 {len(timestamps)} 个血压测量点")
    print(f"收缩压范围: {min(sbp_values):.1f} - {max(sbp_values):.1f} mmHg")
    print(f"舒张压范围: {min(dbp_values):.1f} - {max(dbp_values):.1f} mmHg")
    print(f"平均血压: {np.mean(sbp_values):.1f}/{np.mean(dbp_values):.1f} mmHg")
    
    # 执行分析
    result = analyze_abmp_brittleness(abpm_data, "Demo_Patient_ABPM")
    
    print("\n🎯 ABPM演示分析完成！")