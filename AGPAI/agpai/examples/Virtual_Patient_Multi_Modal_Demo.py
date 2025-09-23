#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
虚拟患者多模态整合分析演示
Virtual Patient Multi-Modal Integration Analysis Demo

基于真实临床场景创建虚拟患者数据，演示多模态生理信号整合分析系统
Creates realistic virtual patient data to demonstrate multi-modal physiological signal integration analysis

患者背景：
- 姓名：李明华（虚拟）
- 年龄：52岁
- 诊断：2型糖尿病合并高血压
- 病程：糖尿病8年，高血压3年
- 当前治疗：二甲双胍 + 格列美脲 + 氨氯地平
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class VirtualPatientDataGenerator:
    """虚拟患者数据生成器"""
    
    def __init__(self):
        self.patient_info = {
            'name': '李明华',
            'age': 52,
            'gender': 'M',
            'diagnosis': '2型糖尿病合并高血压',
            'diabetes_duration': 8,  # 年
            'hypertension_duration': 3,  # 年
            'medications': ['二甲双胍 1000mg bid', '格列美脲 2mg qd', '氨氯地平 5mg qd']
        }
        
        # 设定24小时监测时间
        self.start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.end_time = self.start_time + timedelta(hours=24)
    
    def generate_cgm_data(self):
        """生成CGM数据 - 模拟不良控制的2型糖尿病患者"""
        # 24小时，每分钟一个数据点
        time_points = pd.date_range(self.start_time, self.end_time, freq='1min')[:-1]
        n_points = len(time_points)
        
        # 基础血糖波动模式
        base_glucose = 180  # mg/dL, 基础偏高
        
        # 餐后血糖峰值模拟 (早7点、中12点、晚6点)
        meal_effects = np.zeros(n_points)
        for i, time_point in enumerate(time_points):
            hour = time_point.hour
            minute = time_point.minute
            
            # 早餐后血糖峰值 (7-10点)
            if 7 <= hour <= 10:
                peak_time = 8.5  # 8:30达峰
                time_from_peak = abs(hour + minute/60 - peak_time)
                meal_effects[i] += 120 * np.exp(-time_from_peak**2 / 2)
            
            # 午餐后血糖峰值 (12-15点)
            elif 12 <= hour <= 15:
                peak_time = 13.5  # 13:30达峰
                time_from_peak = abs(hour + minute/60 - peak_time)
                meal_effects[i] += 100 * np.exp(-time_from_peak**2 / 2)
            
            # 晚餐后血糖峰值 (18-22点)
            elif 18 <= hour <= 22:
                peak_time = 19.5  # 19:30达峰
                time_from_peak = abs(hour + minute/60 - peak_time)
                meal_effects[i] += 110 * np.exp(-time_from_peak**2 / 2)
        
        # 黎明现象 (凌晨4-8点血糖上升)
        dawn_effect = np.zeros(n_points)
        for i, time_point in enumerate(time_points):
            hour = time_point.hour + time_point.minute/60
            if 4 <= hour <= 8:
                dawn_effect[i] = 40 * np.sin((hour - 4) / 4 * np.pi)
        
        # 药物效应（格列美脲早晨服用，持续约8-10小时）
        drug_effect = np.zeros(n_points)
        for i, time_point in enumerate(time_points):
            hours_since_morning = (time_point - self.start_time.replace(hour=7)).total_seconds() / 3600
            if hours_since_morning > 0:
                # 药物降糖效应，8小时后逐渐减弱
                drug_effect[i] = -30 * np.exp(-max(0, hours_since_morning-1)/8) * (hours_since_morning > 0)
        
        # 基础变异性和噪声
        baseline_variation = np.random.normal(0, 15, n_points)  # 较高的变异性
        measurement_noise = np.random.normal(0, 5, n_points)
        
        # 合成最终血糖值
        glucose_values = (base_glucose + meal_effects + dawn_effect + 
                         drug_effect + baseline_variation + measurement_noise)
        
        # 确保血糖值在合理范围内
        glucose_values = np.clip(glucose_values, 40, 400)
        
        # 添加一些低血糖事件（夜间和下午）
        for i, time_point in enumerate(time_points):
            hour = time_point.hour
            # 夜间低血糖风险（凌晨2-4点）
            if 2 <= hour <= 4 and np.random.random() < 0.3:
                glucose_values[i:i+30] = np.maximum(glucose_values[i:i+30] - 40, 50)
            # 下午低血糖风险（15-17点，午餐后药物作用）
            elif 15 <= hour <= 17 and np.random.random() < 0.2:
                glucose_values[i:i+20] = np.maximum(glucose_values[i:i+20] - 30, 60)
        
        cgm_data = pd.DataFrame({
            'timestamp': time_points,
            'glucose_mg_dl': glucose_values,
            'sensor_id': 'CGM_001'
        })
        
        return cgm_data
    
    def generate_ecg_data(self):
        """生成ECG数据 - 模拟有轻度心律不齐的患者"""
        # 24小时心电数据，每秒采样
        time_points = pd.date_range(self.start_time, self.end_time, freq='1s')[:-1]
        n_points = len(time_points)
        
        # 基础心率模式（昼夜节律）
        base_hr = np.zeros(n_points)
        for i, time_point in enumerate(time_points):
            hour = time_point.hour + time_point.minute/60 + time_point.second/3600
            # 正常昼夜节律：白天高，夜间低
            circadian_hr = 75 + 15 * np.sin(2 * np.pi * (hour - 6) / 24)
            base_hr[i] = circadian_hr
        
        # 糖尿病相关的心率变异性降低
        hr_variability = np.random.normal(0, 3, n_points)  # 较低的HRV
        
        # 血糖影响心率（高血糖时心率略快）
        glucose_effect = np.zeros(n_points)
        # 简化：假设每分钟的血糖值影响该分钟内的心率
        for i in range(0, n_points, 60):  # 每分钟
            glucose_idx = i // 60
            if glucose_idx < len(self.cgm_data):
                glucose = self.cgm_data.iloc[glucose_idx]['glucose_mg_dl']
                if glucose > 180:  # 高血糖
                    hr_increase = (glucose - 180) / 10  # 每10mg/dL增加1bpm
                    glucose_effect[i:i+60] = min(hr_increase, 20)
        
        # 活动影响（简化模拟）
        activity_effect = np.zeros(n_points)
        # 白天活动时心率增加
        for i, time_point in enumerate(time_points):
            hour = time_point.hour
            if 8 <= hour <= 22:  # 白天活动时间
                if np.random.random() < 0.1:  # 10%概率有活动
                    activity_duration = np.random.randint(60, 300)  # 1-5分钟活动
                    end_idx = min(i + activity_duration, n_points)
                    activity_effect[i:end_idx] += np.random.randint(20, 50)
        
        # 合成心率
        heart_rate = base_hr + hr_variability + glucose_effect + activity_effect
        heart_rate = np.clip(heart_rate, 45, 150)  # 合理范围
        
        # 添加一些房性早搏（糖尿病常见）
        rr_intervals = 60000 / heart_rate  # 转换为RR间期(ms)
        for i in range(len(rr_intervals)):
            if np.random.random() < 0.05:  # 5%概率出现房性早搏
                if i > 0:
                    rr_intervals[i] *= 0.8  # 早搏RR间期缩短
                if i < len(rr_intervals) - 1:
                    rr_intervals[i+1] *= 1.3  # 代偿性间歇
        
        ecg_data = pd.DataFrame({
            'timestamp': time_points,
            'heart_rate_bpm': 60000 / rr_intervals,
            'rr_interval_ms': rr_intervals,
            'lead': 'Lead_II'
        })
        
        return ecg_data
    
    def generate_hrv_data(self):
        """基于ECG数据生成HRV数据"""
        # 从ECG数据中提取RR间期计算HRV指标
        rr_intervals = self.ecg_data['rr_interval_ms'].values
        
        # 每5分钟计算一次HRV指标
        hrv_data = []
        window_size = 300  # 5分钟窗口
        
        for i in range(0, len(rr_intervals), window_size):
            window_rr = rr_intervals[i:i+window_size]
            if len(window_rr) < 100:  # 数据太少跳过
                continue
                
            timestamp = self.ecg_data['timestamp'].iloc[i]
            
            # 时域指标
            rmssd = np.sqrt(np.mean(np.diff(window_rr)**2))
            sdnn = np.std(window_rr)
            pnn50 = np.sum(np.abs(np.diff(window_rr)) > 50) / len(np.diff(window_rr)) * 100
            
            # 简化的频域指标（模拟）
            lf_power = np.random.normal(200, 50)  # 低频功率
            hf_power = np.random.normal(100, 30)  # 高频功率
            lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0
            
            # 糖尿病患者HRV普遍降低
            diabetes_factor = 0.7  # 整体降低30%
            
            hrv_data.append({
                'timestamp': timestamp,
                'rmssd_ms': rmssd * diabetes_factor,
                'sdnn_ms': sdnn * diabetes_factor,
                'pnn50_percent': pnn50 * diabetes_factor,
                'lf_power': lf_power * diabetes_factor,
                'hf_power': hf_power * diabetes_factor,
                'lf_hf_ratio': lf_hf_ratio * 1.2  # 交感神经相对亢进
            })
        
        return pd.DataFrame(hrv_data)
    
    def generate_abpm_data(self):
        """生成ABPM数据 - 模拟控制不佳的高血压合并糖尿病"""
        # 24小时血压监测，每30分钟一次
        time_points = pd.date_range(self.start_time, self.end_time, freq='30min')[:-1]
        n_points = len(time_points)
        
        abpm_data = []
        
        for i, time_point in enumerate(time_points):
            hour = time_point.hour + time_point.minute/60
            
            # 基础血压模式（昼夜节律）
            if 6 <= hour <= 22:  # 白天
                base_sbp = 145  # 收缩压偏高
                base_dbp = 90   # 舒张压偏高
            else:  # 夜间
                base_sbp = 135  # 夜间血压下降不足（非杓型）
                base_dbp = 85
            
            # 血糖对血压的影响
            glucose_idx = min(i * 30, len(self.cgm_data) - 1)  # 对应的血糖数据
            current_glucose = self.cgm_data.iloc[glucose_idx]['glucose_mg_dl']
            
            # 高血糖时血压升高
            glucose_effect_sbp = 0
            glucose_effect_dbp = 0
            if current_glucose > 200:
                glucose_effect_sbp = (current_glucose - 200) / 10
                glucose_effect_dbp = (current_glucose - 200) / 20
            
            # 白大衣效应和变异性
            measurement_variation_sbp = np.random.normal(0, 8)
            measurement_variation_dbp = np.random.normal(0, 5)
            
            # 最终血压值
            sbp = base_sbp + glucose_effect_sbp + measurement_variation_sbp
            dbp = base_dbp + glucose_effect_dbp + measurement_variation_dbp
            
            # 确保合理范围
            sbp = np.clip(sbp, 90, 200)
            dbp = np.clip(dbp, 50, 120)
            
            # 确保SBP > DBP
            if sbp <= dbp:
                sbp = dbp + 20
            
            pulse_pressure = sbp - dbp
            map_bp = dbp + pulse_pressure / 3
            
            abpm_data.append({
                'timestamp': time_point,
                'sbp_mmhg': round(sbp, 1),
                'dbp_mmhg': round(dbp, 1),
                'pulse_pressure': round(pulse_pressure, 1),
                'map_mmhg': round(map_bp, 1),
                'measurement_type': 'daytime' if 6 <= hour <= 22 else 'nighttime'
            })
        
        return pd.DataFrame(abpm_data)
    
    def generate_all_data(self):
        """生成所有虚拟患者数据"""
        print("=== 虚拟患者数据生成 ===")
        print(f"患者：{self.patient_info['name']}")
        print(f"年龄：{self.patient_info['age']}岁")
        print(f"诊断：{self.patient_info['diagnosis']}")
        print(f"监测时间：{self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%Y-%m-%d %H:%M')}")
        print()
        
        print("生成CGM数据...")
        self.cgm_data = self.generate_cgm_data()
        
        print("生成ECG数据...")
        self.ecg_data = self.generate_ecg_data()
        
        print("生成HRV数据...")
        self.hrv_data = self.generate_hrv_data()
        
        print("生成ABPM数据...")
        self.abpm_data = self.generate_abpm_data()
        
        print("✓ 所有数据生成完成！")
        
        return {
            'cgm': self.cgm_data,
            'ecg': self.ecg_data,
            'hrv': self.hrv_data,
            'abpm': self.abpm_data
        }

class VirtualPatientMultiModalAnalyzer:
    """虚拟患者多模态整合分析器"""
    
    def __init__(self, patient_data):
        self.cgm_data = patient_data['cgm']
        self.ecg_data = patient_data['ecg']
        self.hrv_data = patient_data['hrv']
        self.abpm_data = patient_data['abpm']
        
        # 存储分析结果
        self.analysis_results = {}
    
    def run_comprehensive_analysis(self):
        """运行综合多模态分析"""
        print("\n=== 多模态整合分析开始 ===")
        
        # 1. 单模态基础分析
        print("1. 进行单模态基础分析...")
        self._analyze_glucose_metrics()
        self._analyze_cardiovascular_metrics()
        
        # 2. 多模态时间同步分析
        print("2. 进行多模态时间同步分析...")
        self._synchronize_and_correlate()
        
        # 3. 生理耦合分析
        print("3. 进行生理耦合分析...")
        self._analyze_physiological_coupling()
        
        # 4. 整合脆性评估
        print("4. 进行整合脆性评估...")
        self._calculate_integrated_brittleness()
        
        # 5. 临床决策支持
        print("5. 生成临床决策支持...")
        self._generate_clinical_recommendations()
        
        print("✓ 分析完成！")
        
        return self.analysis_results
    
    def _analyze_glucose_metrics(self):
        """血糖指标分析"""
        glucose_values = self.cgm_data['glucose_mg_dl'].values
        
        # 基础统计
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        cv_glucose = (std_glucose / mean_glucose) * 100
        
        # 时间范围分析
        tir_70_180 = np.sum((glucose_values >= 70) & (glucose_values <= 180)) / len(glucose_values) * 100
        tbr_below_70 = np.sum(glucose_values < 70) / len(glucose_values) * 100
        tar_above_180 = np.sum(glucose_values > 180) / len(glucose_values) * 100
        tar_above_250 = np.sum(glucose_values > 250) / len(glucose_values) * 100
        
        # 血糖变异性指标
        mage = self._calculate_mage(glucose_values)
        
        self.analysis_results['glucose_metrics'] = {
            'mean_glucose_mgdl': round(mean_glucose, 1),
            'std_glucose': round(std_glucose, 1),
            'cv_percent': round(cv_glucose, 1),
            'tir_70_180_percent': round(tir_70_180, 1),
            'tbr_below_70_percent': round(tbr_below_70, 1),
            'tar_above_180_percent': round(tar_above_180, 1),
            'tar_above_250_percent': round(tar_above_250, 1),
            'mage_mgdl': round(mage, 1),
            'glucose_risk_level': self._assess_glucose_risk(tir_70_180, cv_glucose, mage)
        }
    
    def _calculate_mage(self, glucose_values):
        """计算平均血糖漂移幅度(MAGE)"""
        # 简化的MAGE计算
        differences = np.abs(np.diff(glucose_values))
        mean_diff = np.mean(differences)
        sd_diff = np.std(differences)
        
        # 大于1个标准差的漂移
        significant_excursions = differences[differences > (mean_diff + sd_diff)]
        
        if len(significant_excursions) > 0:
            mage = np.mean(significant_excursions)
        else:
            mage = mean_diff
        
        return mage
    
    def _assess_glucose_risk(self, tir, cv, mage):
        """血糖风险评估"""
        if tir > 70 and cv < 36 and mage < 3.9:
            return "低风险"
        elif tir > 50 and cv < 50:
            return "中等风险"
        else:
            return "高风险"
    
    def _analyze_cardiovascular_metrics(self):
        """心血管指标分析"""
        # HRV分析
        hrv_mean = self.hrv_data.mean()
        
        # 血压分析
        bp_stats = {
            'mean_sbp': self.abpm_data['sbp_mmhg'].mean(),
            'mean_dbp': self.abpm_data['dbp_mmhg'].mean(),
            'sbp_cv': (self.abpm_data['sbp_mmhg'].std() / self.abpm_data['sbp_mmhg'].mean()) * 100,
            'dbp_cv': (self.abpm_data['dbp_mmhg'].std() / self.abpm_data['dbp_mmhg'].mean()) * 100
        }
        
        # 昼夜节律分析
        daytime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'daytime']
        nighttime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'nighttime']
        
        sbp_dip = ((daytime_bp['sbp_mmhg'].mean() - nighttime_bp['sbp_mmhg'].mean()) / 
                   daytime_bp['sbp_mmhg'].mean()) * 100
        
        self.analysis_results['cardiovascular_metrics'] = {
            'hrv_metrics': {
                'mean_rmssd': round(hrv_mean['rmssd_ms'], 1),
                'mean_sdnn': round(hrv_mean['sdnn_ms'], 1),
                'mean_pnn50': round(hrv_mean['pnn50_percent'], 1),
                'mean_lf_hf_ratio': round(hrv_mean['lf_hf_ratio'], 2)
            },
            'bp_metrics': {
                'mean_sbp': round(bp_stats['mean_sbp'], 1),
                'mean_dbp': round(bp_stats['mean_dbp'], 1),
                'sbp_variability': round(bp_stats['sbp_cv'], 1),
                'dbp_variability': round(bp_stats['dbp_cv'], 1),
                'sbp_dip_percent': round(sbp_dip, 1),
                'dipping_pattern': self._assess_dipping_pattern(sbp_dip)
            },
            'cv_risk_level': self._assess_cv_risk(hrv_mean, bp_stats, sbp_dip)
        }
    
    def _assess_dipping_pattern(self, dip_percent):
        """血压昼夜节律评估"""
        if dip_percent >= 10:
            return "杓型（正常）"
        elif 0 <= dip_percent < 10:
            return "非杓型"
        else:
            return "反杓型"
    
    def _assess_cv_risk(self, hrv_mean, bp_stats, sbp_dip):
        """心血管风险评估"""
        risk_factors = 0
        
        # HRV风险因子
        if hrv_mean['rmssd_ms'] < 20:
            risk_factors += 1
        if hrv_mean['sdnn_ms'] < 50:
            risk_factors += 1
        if hrv_mean['lf_hf_ratio'] > 2.5:
            risk_factors += 1
        
        # 血压风险因子
        if bp_stats['mean_sbp'] > 140 or bp_stats['mean_dbp'] > 90:
            risk_factors += 1
        if bp_stats['sbp_cv'] > 15:
            risk_factors += 1
        if sbp_dip < 10:
            risk_factors += 1
        
        if risk_factors <= 2:
            return "低-中等风险"
        elif risk_factors <= 4:
            return "中-高风险"
        else:
            return "高风险"
    
    def _synchronize_and_correlate(self):
        """时间同步和相关性分析"""
        # 将所有数据同步到30分钟窗口
        sync_data = []
        
        start_time = self.cgm_data['timestamp'].min()
        end_time = self.cgm_data['timestamp'].max()
        time_windows = pd.date_range(start_time, end_time, freq='30min')[:-1]
        
        for window_start in time_windows:
            window_end = window_start + timedelta(minutes=30)
            
            # CGM数据平均值
            cgm_window = self.cgm_data[
                (self.cgm_data['timestamp'] >= window_start) & 
                (self.cgm_data['timestamp'] < window_end)
            ]
            
            # HRV数据（最近的一个值）
            hrv_window = self.hrv_data[self.hrv_data['timestamp'] <= window_end]
            if not hrv_window.empty:
                hrv_latest = hrv_window.iloc[-1]
            else:
                continue
            
            # ABPM数据（最近的一个值）
            abpm_window = self.abpm_data[self.abpm_data['timestamp'] <= window_end]
            if not abpm_window.empty:
                abpm_latest = abpm_window.iloc[-1]
            else:
                continue
            
            if not cgm_window.empty:
                sync_data.append({
                    'timestamp': window_start,
                    'glucose': cgm_window['glucose_mg_dl'].mean(),
                    'rmssd': hrv_latest['rmssd_ms'],
                    'lf_hf_ratio': hrv_latest['lf_hf_ratio'],
                    'sbp': abpm_latest['sbp_mmhg'],
                    'dbp': abpm_latest['dbp_mmhg']
                })
        
        sync_df = pd.DataFrame(sync_data)
        
        if len(sync_df) > 10:  # 确保有足够数据计算相关性
            correlations = {
                'glucose_sbp_corr': sync_df['glucose'].corr(sync_df['sbp']),
                'glucose_rmssd_corr': sync_df['glucose'].corr(sync_df['rmssd']),
                'sbp_rmssd_corr': sync_df['sbp'].corr(sync_df['rmssd']),
                'glucose_lf_hf_corr': sync_df['glucose'].corr(sync_df['lf_hf_ratio'])
            }
            
            self.analysis_results['temporal_correlations'] = {
                'correlations': {k: round(v, 3) for k, v in correlations.items()},
                'coupling_strength': self._assess_coupling_strength(correlations)
            }
        
        self.sync_data = sync_df
    
    def _assess_coupling_strength(self, correlations):
        """评估生理耦合强度"""
        strong_correlations = sum(1 for corr in correlations.values() if abs(corr) > 0.5)
        moderate_correlations = sum(1 for corr in correlations.values() if 0.3 < abs(corr) <= 0.5)
        
        if strong_correlations >= 2:
            return "强耦合"
        elif strong_correlations + moderate_correlations >= 2:
            return "中等耦合"
        else:
            return "弱耦合"
    
    def _analyze_physiological_coupling(self):
        """生理耦合分析"""
        if not hasattr(self, 'sync_data') or self.sync_data.empty:
            return
        
        # 血糖-血压耦合强度
        glucose_bp_coupling = self._calculate_coupling_strength(
            self.sync_data['glucose'], self.sync_data['sbp']
        )
        
        # 血糖-HRV耦合强度
        glucose_hrv_coupling = self._calculate_coupling_strength(
            self.sync_data['glucose'], self.sync_data['rmssd']
        )
        
        # 血压-HRV耦合强度（压力感受器功能）
        bp_hrv_coupling = self._calculate_coupling_strength(
            self.sync_data['sbp'], self.sync_data['rmssd']
        )
        
        self.analysis_results['physiological_coupling'] = {
            'glucose_bp_coupling': round(glucose_bp_coupling, 3),
            'glucose_hrv_coupling': round(glucose_hrv_coupling, 3),
            'bp_hrv_coupling': round(bp_hrv_coupling, 3),
            'overall_coupling_status': self._assess_overall_coupling(
                glucose_bp_coupling, glucose_hrv_coupling, bp_hrv_coupling
            )
        }
    
    def _calculate_coupling_strength(self, signal1, signal2):
        """计算两信号间的耦合强度"""
        # 使用互信息的简化版本
        correlation = np.corrcoef(signal1, signal2)[0, 1]
        
        # 非线性耦合的简化评估
        signal1_norm = (signal1 - signal1.mean()) / signal1.std()
        signal2_norm = (signal2 - signal2.mean()) / signal2.std()
        
        # 计算延迟相关性（考虑生理延迟）
        max_corr = abs(correlation)
        for lag in range(1, min(5, len(signal1)//4)):  # 最多考虑4个时间点的延迟
            if lag < len(signal1):
                delayed_corr = abs(np.corrcoef(signal1[:-lag], signal2[lag:])[0, 1])
                max_corr = max(max_corr, delayed_corr)
        
        return max_corr
    
    def _assess_overall_coupling(self, gb_coupling, gh_coupling, bh_coupling):
        """评估整体耦合状态"""
        avg_coupling = (gb_coupling + gh_coupling + bh_coupling) / 3
        
        if avg_coupling > 0.6:
            return "耦合过强（病理性）"
        elif avg_coupling > 0.4:
            return "中等耦合（边界性）"
        elif avg_coupling > 0.2:
            return "正常耦合"
        else:
            return "耦合减弱（功能障碍）"
    
    def _calculate_integrated_brittleness(self):
        """计算整合脆性评分"""
        # 血糖脆性评分
        glucose_score = self._calculate_glucose_brittleness_score()
        
        # 心血管脆性评分
        cv_score = self._calculate_cv_brittleness_score()
        
        # 自主神经脆性评分
        autonomic_score = self._calculate_autonomic_brittleness_score()
        
        # 整合脆性评分（加权平均）
        integrated_score = (glucose_score * 0.4 + cv_score * 0.35 + autonomic_score * 0.25)
        
        # 脆性分型
        brittleness_type = self._classify_brittleness_type(integrated_score)
        
        self.analysis_results['integrated_brittleness'] = {
            'glucose_brittleness_score': round(glucose_score, 1),
            'cardiovascular_brittleness_score': round(cv_score, 1),
            'autonomic_brittleness_score': round(autonomic_score, 1),
            'integrated_brittleness_score': round(integrated_score, 1),
            'brittleness_type': brittleness_type,
            'risk_stratification': self._stratify_risk(integrated_score)
        }
    
    def _calculate_glucose_brittleness_score(self):
        """血糖脆性评分"""
        glucose_metrics = self.analysis_results['glucose_metrics']
        score = 0
        
        # TIR评分（40分）
        tir = glucose_metrics['tir_70_180_percent']
        if tir >= 70:
            score += 40
        elif tir >= 50:
            score += 30
        elif tir >= 25:
            score += 20
        else:
            score += 10
        
        # CV评分（30分）
        cv = glucose_metrics['cv_percent']
        if cv <= 36:
            score += 30
        elif cv <= 50:
            score += 20
        else:
            score += 10
        
        # TBR评分（30分）
        tbr = glucose_metrics['tbr_below_70_percent']
        if tbr < 4:
            score += 30
        elif tbr < 10:
            score += 20
        else:
            score += 10
        
        return score
    
    def _calculate_cv_brittleness_score(self):
        """心血管脆性评分"""
        cv_metrics = self.analysis_results['cardiovascular_metrics']
        score = 0
        
        # 血压控制（40分）
        sbp = cv_metrics['bp_metrics']['mean_sbp']
        dbp = cv_metrics['bp_metrics']['mean_dbp']
        if sbp < 140 and dbp < 90:
            score += 40
        elif sbp < 160 and dbp < 100:
            score += 25
        else:
            score += 10
        
        # 血压变异性（30分）
        sbp_cv = cv_metrics['bp_metrics']['sbp_variability']
        if sbp_cv < 10:
            score += 30
        elif sbp_cv < 15:
            score += 20
        else:
            score += 10
        
        # 昼夜节律（30分）
        dip_pattern = cv_metrics['bp_metrics']['dipping_pattern']
        if dip_pattern == "杓型（正常）":
            score += 30
        elif dip_pattern == "非杓型":
            score += 15
        else:
            score += 5
        
        return score
    
    def _calculate_autonomic_brittleness_score(self):
        """自主神经脆性评分"""
        hrv_metrics = self.analysis_results['cardiovascular_metrics']['hrv_metrics']
        score = 0
        
        # RMSSD评分（35分）
        rmssd = hrv_metrics['mean_rmssd']
        if rmssd >= 20:
            score += 35
        elif rmssd >= 15:
            score += 25
        else:
            score += 10
        
        # SDNN评分（35分）
        sdnn = hrv_metrics['mean_sdnn']
        if sdnn >= 50:
            score += 35
        elif sdnn >= 30:
            score += 25
        else:
            score += 10
        
        # LF/HF比值评分（30分）
        lf_hf = hrv_metrics['mean_lf_hf_ratio']
        if 0.5 <= lf_hf <= 2.0:
            score += 30
        elif 2.0 < lf_hf <= 3.0:
            score += 20
        else:
            score += 10
        
        return score
    
    def _classify_brittleness_type(self, score):
        """脆性分型"""
        if score >= 85:
            return "I型（稳定型）"
        elif score >= 70:
            return "II型（轻度不稳定型）"
        elif score >= 55:
            return "III型（中度不稳定型）"
        elif score >= 40:
            return "IV型（重度不稳定型）"
        elif score >= 25:
            return "V型（极重度不稳定型）"
        else:
            return "VI型（危重不稳定型）"
    
    def _stratify_risk(self, score):
        """风险分层"""
        if score >= 75:
            return "低风险"
        elif score >= 60:
            return "中等风险"
        elif score >= 45:
            return "高风险"
        else:
            return "极高风险"
    
    def _generate_clinical_recommendations(self):
        """生成临床决策支持建议"""
        brittleness = self.analysis_results['integrated_brittleness']
        glucose_metrics = self.analysis_results['glucose_metrics']
        cv_metrics = self.analysis_results['cardiovascular_metrics']
        
        recommendations = []
        
        # 血糖管理建议
        if glucose_metrics['tir_70_180_percent'] < 70:
            recommendations.append({
                'category': '血糖管理',
                'priority': '高',
                'recommendation': '调整降糖方案，目标TIR>70%，建议内分泌科会诊'
            })
        
        if glucose_metrics['cv_percent'] > 36:
            recommendations.append({
                'category': '血糖变异性',
                'priority': '中',
                'recommendation': '优化降糖药物时间分布，考虑CGM指导下的精准调药'
            })
        
        # 心血管管理建议
        if cv_metrics['bp_metrics']['mean_sbp'] > 140:
            recommendations.append({
                'category': '血压管理',
                'priority': '高',
                'recommendation': '加强降压治疗，目标<140/90mmHg，建议心内科评估'
            })
        
        if cv_metrics['bp_metrics']['dipping_pattern'] != "杓型（正常）":
            recommendations.append({
                'category': '昼夜节律',
                'priority': '中',
                'recommendation': '评估睡眠质量，考虑睡前给药调整血压昼夜节律'
            })
        
        # 自主神经功能建议
        if cv_metrics['hrv_metrics']['mean_rmssd'] < 15:
            recommendations.append({
                'category': '自主神经功能',
                'priority': '中',
                'recommendation': '评估糖尿病神经病变，建议神经科会诊及HRV监测'
            })
        
        # 综合管理建议
        risk_level = brittleness['risk_stratification']
        if risk_level in ['高风险', '极高风险']:
            recommendations.append({
                'category': '综合管理',
                'priority': '高',
                'recommendation': '多学科团队管理，增加随访频率，考虑住院调整治疗'
            })
        
        # 生活方式建议
        recommendations.append({
            'category': '生活方式',
            'priority': '中',
            'recommendation': '规律作息，适量运动，血压和血糖自我监测'
        })
        
        self.analysis_results['clinical_recommendations'] = recommendations
    
    def generate_report(self):
        """生成分析报告"""
        print("\n" + "="*60)
        print("虚拟患者多模态整合分析报告")
        print("="*60)
        
        # 患者基本信息
        print(f"\n患者信息：李明华，52岁男性")
        print(f"诊断：2型糖尿病合并高血压")
        print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 血糖分析结果
        print(f"\n【血糖分析结果】")
        glucose = self.analysis_results['glucose_metrics']
        print(f"平均血糖：{glucose['mean_glucose_mgdl']} mg/dL")
        print(f"血糖变异系数：{glucose['cv_percent']}%")
        print(f"目标范围内时间(TIR)：{glucose['tir_70_180_percent']}%")
        print(f"低血糖时间(TBR)：{glucose['tbr_below_70_percent']}%")
        print(f"高血糖时间(TAR)：{glucose['tar_above_180_percent']}%")
        print(f"MAGE：{glucose['mage_mgdl']} mg/dL")
        print(f"血糖风险等级：{glucose['glucose_risk_level']}")
        
        # 心血管分析结果
        print(f"\n【心血管分析结果】")
        cv = self.analysis_results['cardiovascular_metrics']
        print(f"平均收缩压：{cv['bp_metrics']['mean_sbp']} mmHg")
        print(f"平均舒张压：{cv['bp_metrics']['mean_dbp']} mmHg")
        print(f"血压变异性：{cv['bp_metrics']['sbp_variability']}%")
        print(f"昼夜节律：{cv['bp_metrics']['dipping_pattern']}")
        print(f"RMSSD：{cv['hrv_metrics']['mean_rmssd']} ms")
        print(f"SDNN：{cv['hrv_metrics']['mean_sdnn']} ms")
        print(f"LF/HF比值：{cv['hrv_metrics']['mean_lf_hf_ratio']}")
        print(f"心血管风险等级：{cv['cv_risk_level']}")
        
        # 生理耦合分析
        if 'physiological_coupling' in self.analysis_results:
            print(f"\n【生理耦合分析】")
            coupling = self.analysis_results['physiological_coupling']
            print(f"血糖-血压耦合强度：{coupling['glucose_bp_coupling']}")
            print(f"血糖-HRV耦合强度：{coupling['glucose_hrv_coupling']}")
            print(f"血压-HRV耦合强度：{coupling['bp_hrv_coupling']}")
            print(f"整体耦合状态：{coupling['overall_coupling_status']}")
        
        # 整合脆性评估
        print(f"\n【整合脆性评估】")
        brittleness = self.analysis_results['integrated_brittleness']
        print(f"血糖脆性评分：{brittleness['glucose_brittleness_score']}/100")
        print(f"心血管脆性评分：{brittleness['cardiovascular_brittleness_score']}/100")
        print(f"自主神经脆性评分：{brittleness['autonomic_brittleness_score']}/100")
        print(f"整合脆性评分：{brittleness['integrated_brittleness_score']}/100")
        print(f"脆性分型：{brittleness['brittleness_type']}")
        print(f"风险分层：{brittleness['risk_stratification']}")
        
        # 临床建议
        print(f"\n【临床决策支持建议】")
        recommendations = self.analysis_results['clinical_recommendations']
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. 【{rec['category']}】({rec['priority']}优先级)")
            print(f"   {rec['recommendation']}")
        
        print(f"\n" + "="*60)
        print("报告结束")
        print("="*60)

def main():
    """主函数：演示虚拟患者多模态分析"""
    
    # 1. 生成虚拟患者数据
    print("正在生成虚拟患者数据...")
    generator = VirtualPatientDataGenerator()
    patient_data = generator.generate_all_data()
    
    # 2. 运行多模态分析
    print("\n正在运行多模态整合分析...")
    analyzer = VirtualPatientMultiModalAnalyzer(patient_data)
    results = analyzer.run_comprehensive_analysis()
    
    # 3. 生成分析报告
    analyzer.generate_report()
    
    # 4. 保存数据和结果（可选）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存虚拟患者数据
    patient_data['cgm'].to_csv(f'virtual_patient_cgm_{timestamp}.csv', index=False)
    patient_data['hrv'].to_csv(f'virtual_patient_hrv_{timestamp}.csv', index=False)
    patient_data['abpm'].to_csv(f'virtual_patient_abpm_{timestamp}.csv', index=False)
    
    # 保存分析结果
    import json
    with open(f'virtual_patient_analysis_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据和分析结果已保存到文件 (时间戳: {timestamp})")
    
    return results

if __name__ == "__main__":
    results = main()