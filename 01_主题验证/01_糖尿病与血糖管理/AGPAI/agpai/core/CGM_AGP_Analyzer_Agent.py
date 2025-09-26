#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CGM数据读取和AGP分析智能体
基于AGP_Visual_Pattern_Analysis.csv的57种视觉指标实现
"""

import pandas as pd
import numpy as np
from scipy import signal, stats
from scipy.fft import fft, fftfreq
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import json
import logging

from ..config.config_manager import ConfigManager

class CGMDataReader:
    """CGM原始数据读取器 - 支持多种CGM设备格式"""
    
    def __init__(self):
        self.supported_formats = ['dexcom', 'freestyle', 'medtronic', 'generic_csv']
        
    def read_cgm_file(self, file_path: str, device_type: str = 'auto') -> pd.DataFrame:
        """
        读取CGM原始数据文件
        
        Args:
            file_path: CGM数据文件路径
            device_type: 设备类型 ('dexcom', 'freestyle', 'medtronic', 'generic_csv', 'auto')
            
        Returns:
            标准化的CGM数据DataFrame (timestamp, glucose, device_info)
        """
        if device_type == 'auto':
            device_type = self._detect_device_type(file_path)
            
        if device_type == 'dexcom':
            return self._read_dexcom(file_path)
        elif device_type == 'freestyle':
            return self._read_freestyle(file_path)
        elif device_type == 'medtronic':
            return self._read_medtronic(file_path)
        elif device_type == 'generic_csv':
            return self._read_generic_csv(file_path)
        else:
            raise ValueError(f"Unsupported device type: {device_type}")
    
    def _detect_device_type(self, file_path: str) -> str:
        """自动检测CGM设备类型"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                header = f.readline().lower()
                if 'dexcom' in header or 'glucose value' in header:
                    return 'dexcom'
                elif 'freestyle' in header or 'historic glucose' in header:
                    return 'freestyle'
                elif 'medtronic' in header or 'sensor glucose' in header:
                    return 'medtronic'
                else:
                    return 'generic_csv'
        except:
            return 'generic_csv'
    
    def _read_dexcom(self, file_path: str) -> pd.DataFrame:
        """读取Dexcom CGM数据"""
        df = pd.read_csv(file_path)
        
        # Dexcom格式标准化
        glucose_col = 'Glucose Value (mg/dL)' if 'Glucose Value (mg/dL)' in df.columns else 'glucose'
        timestamp_col = 'Timestamp (YYYY-MM-DDTHH:MM:SS)' if 'Timestamp (YYYY-MM-DDTHH:MM:SS)' in df.columns else 'timestamp'
        
        result = pd.DataFrame({
            'timestamp': pd.to_datetime(df[timestamp_col]),
            'glucose': df[glucose_col] * 0.0555 if df[glucose_col].max() > 50 else df[glucose_col],  # mg/dL to mmol/L
            'device_info': 'dexcom'
        })
        
        return result.dropna().reset_index(drop=True)
    
    def _read_freestyle(self, file_path: str) -> pd.DataFrame:
        """读取FreeStyle CGM数据"""
        df = pd.read_csv(file_path, skiprows=1)  # FreeStyle通常有标题行
        
        # FreeStyle格式标准化  
        result = pd.DataFrame({
            'timestamp': pd.to_datetime(df.iloc[:, 0]),  # 第一列通常是时间
            'glucose': pd.to_numeric(df.iloc[:, 1], errors='coerce'),  # 第二列是血糖值
            'device_info': 'freestyle'
        })
        
        # 单位转换 (如果需要)
        if result['glucose'].max() > 50:  # 可能是mg/dL
            result['glucose'] = result['glucose'] * 0.0555
            
        return result.dropna().reset_index(drop=True)
    
    def _read_medtronic(self, file_path: str) -> pd.DataFrame:
        """读取Medtronic CGM数据"""
        df = pd.read_csv(file_path)
        
        result = pd.DataFrame({
            'timestamp': pd.to_datetime(df['Date'] + ' ' + df['Time']),
            'glucose': df['Sensor Glucose (mmol/L)'],
            'device_info': 'medtronic'
        })
        
        return result.dropna().reset_index(drop=True)
    
    def _read_generic_csv(self, file_path: str) -> pd.DataFrame:
        """读取通用CSV格式CGM数据"""
        # 根据R002 V5.txt的格式进行修改：tab分隔，跳过前3行头部，无列名
        # 数据行格式为：ID\t时间\t记录类型\t葡萄糖历史记录（mmol/L）
        # 因此，时间在索引1，葡萄糖在索引3
        df = pd.read_csv(file_path, sep='\t', skiprows=3, header=None) 
        
        # 明确指定时间和血糖的列索引
        timestamp_col_index = 1
        glucose_col_index = 3
            
        result = pd.DataFrame({
            'timestamp': pd.to_datetime(df.iloc[:, timestamp_col_index], format='%Y/%m/%d %H:%M'), # 指定时间格式，提高鲁棒性
            'glucose': pd.to_numeric(df.iloc[:, glucose_col_index], errors='coerce'),
            'device_info': 'generic'
        })
        
        # 单位转换检查 (如果需要)
        # R002 V5.txt中的葡萄糖已经是mmol/L，所以这里max()不会大于50，不会进行转换
        if result['glucose'].max() > 50:
            result['glucose'] = result['glucose'] * 0.0555
            
        return result.dropna().reset_index(drop=True)


class AGPVisualAnalyzer:
    """AGP视觉模式分析器 - 实现57种视觉指标"""
    
    def __init__(self, enable_quality_check=True):
        self.indicators = {}
        self.enable_quality_check = enable_quality_check
        if enable_quality_check:
            try:
                from CGM_Data_Quality_Assessor import CGMDataQualityAssessor
                self.quality_assessor = CGMDataQualityAssessor()
            except ImportError:
                print("⚠️ 未找到数据质量评估模块，将跳过质量检查")
                self.enable_quality_check = False
        
    def analyze_cgm_data(self, cgm_data: pd.DataFrame, analysis_days: int = 14) -> Dict:
        """
        完整的CGM数据AGP视觉分析
        
        Args:
            cgm_data: 标准化CGM数据
            analysis_days: 分析天数
            
        Returns:
            包含57种视觉指标的分析结果
        """
        # 第一步：数据质量评估
        if self.enable_quality_check:
            print("🔍 正在进行数据质量评估...")
            quality_assessment = self.quality_assessor.assess_data_quality(cgm_data, analysis_days)
            
            if not quality_assessment['usable_for_analysis']:
                print("❌ 数据质量不合格，无法进行可靠的AGP分析")
                quality_report = self.quality_assessor.generate_quality_report(quality_assessment)
                print(quality_report)
                
                return {
                    'error': 'data_quality_insufficient',
                    'quality_assessment': quality_assessment,
                    'message': '数据质量不符合AGP分析要求，请改善数据质量后重试'
                }
            else:
                print(f"✅ 数据质量评估通过: {quality_assessment['overall_quality']['quality_level']} ({quality_assessment['overall_quality']['total_score']}/100)")
        
        # 数据预处理和验证
        processed_data = self._preprocess_data(cgm_data, analysis_days)
        
        # 计算各类视觉指标
        results = {}
        
        # 1. AGP曲线形态分析 (7个指标)
        results.update(self._analyze_curve_morphology(processed_data))
        
        # 2. 时间段分析 (6个指标)
        results.update(self._analyze_time_periods(processed_data))
        
        # 3. 分位数带分析 (5个指标)
        results.update(self._analyze_percentile_bands(processed_data))
        
        # 4. 异常模式识别 (5个指标)
        results.update(self._analyze_abnormal_patterns(processed_data))
        
        # 5. 餐时模式分析 (4个指标)
        results.update(self._analyze_meal_patterns(processed_data))
        
        # 6. 曲线复杂度分析 (5个指标)
        results.update(self._analyze_curve_complexity(processed_data))
        
        # 7. 目标范围分析 (4个指标)
        results.update(self._analyze_target_range(processed_data))
        
        # 8. 风险区域分析 (4个指标)
        results.update(self._analyze_risk_zones(processed_data))
        
        # 9. 日间变异分析 (4个指标)
        results.update(self._analyze_daily_variability(processed_data))
        
        # 10. 平滑度综合分析 (4个指标)
        results.update(self._analyze_comprehensive_smoothness(processed_data))
        
        # 11. 对称性分析 (4个指标)
        results.update(self._analyze_symmetry(processed_data))
        
        # 12. 图形美学分析 (3个指标)
        results.update(self._analyze_visual_aesthetics(processed_data))
        
        return results
    
    def _preprocess_data(self, cgm_data: pd.DataFrame, analysis_days: int) -> Dict:
        """数据预处理和AGP曲线生成"""
        # 取最近N天数据
        end_date = cgm_data['timestamp'].max()
        start_date = end_date - timedelta(days=analysis_days)
        data = cgm_data[cgm_data['timestamp'] >= start_date].copy()
        
        # 生成24小时AGP曲线
        data['hour'] = data['timestamp'].dt.hour + data['timestamp'].dt.minute / 60.0
        
        # 计算每小时的分位数
        hourly_stats = data.groupby('hour')['glucose'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
        
        agp_curve = {
            'hour': np.linspace(0, 24, 96),  # 15分钟间隔
            'p05': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['5%']),
            'p25': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['25%']),
            'p50': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['50%']),
            'p75': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['75%']),
            'p95': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['95%'])
        }
        
        return {
            'raw_data': data,
            'agp_curve': agp_curve,
            'analysis_period': analysis_days,
            'data_points': len(data)
        }
    
    def _analyze_curve_morphology(self, processed_data: Dict) -> Dict:
        """AGP曲线形态分析 (指标1-7)"""
        agp = processed_data['agp_curve']
        median_curve = agp['p50']
        
        results = {}
        
        # 1. 中位数曲线平滑度
        curvature = np.abs(np.diff(median_curve, n=2))
        results['median_curve_smoothness'] = 1 / (1 + np.mean(curvature))
        
        # 2. 25%-75%分位数带宽平均值
        band_width = agp['p75'] - agp['p25']
        results['percentile_band_width_avg'] = np.mean(band_width)
        
        # 3. 中位数曲线对称性指数
        first_half = median_curve[:48]
        second_half = median_curve[48:][::-1]  # 反转后半段
        results['curve_symmetry_index'] = np.corrcoef(first_half, second_half)[0,1]
        
        # 4. 24小时内曲线峰值数量
        peaks, _ = signal.find_peaks(median_curve, height=np.mean(median_curve))
        results['curve_peak_count'] = len(peaks)
        
        # 5. 24小时内曲线低谷数量
        valleys, _ = signal.find_peaks(-median_curve, height=-np.mean(median_curve))
        results['curve_valley_count'] = len(valleys)
        
        # 6. 一阶差分平滑度
        first_diff = np.diff(median_curve)
        results['first_order_smoothness'] = 1 - np.std(first_diff) / np.mean(np.abs(first_diff))
        
        # 7. 二阶差分平滑度
        second_diff = np.diff(median_curve, n=2)
        results['second_order_smoothness'] = 1 / (1 + np.var(second_diff))
        
        return results
    
    def _analyze_time_periods(self, processed_data: Dict) -> Dict:
        """时间段分析 (指标8-13)"""
        agp = processed_data['agp_curve']
        hours = agp['hour']
        median_curve = agp['p50']
        
        results = {}
        
        # 8. 黎明现象斜率 (4-8点)
        dawn_mask = (hours >= 4) & (hours <= 8)
        dawn_glucose = median_curve[dawn_mask]
        dawn_hours = hours[dawn_mask]
        results['dawn_curve_slope'] = np.polyfit(dawn_hours, dawn_glucose, 1)[0]
        
        # 9. 早晨峰值高度 (6-10点)
        morning_mask = (hours >= 6) & (hours <= 10)
        baseline = np.mean(median_curve[(hours >= 0) & (hours <= 6)])
        results['morning_peak_height'] = np.max(median_curve[morning_mask]) - baseline
        
        # 10. 早晨峰值持续时间
        morning_peak_idx = np.argmax(median_curve[morning_mask])
        peak_value = median_curve[morning_mask][morning_peak_idx]
        half_peak = (peak_value + baseline) / 2
        # 简化实现：估算半高宽
        results['morning_peak_width'] = 120  # 默认120分钟，实际需要更复杂的计算
        
        # 11. 午后曲线稳定性 (14-18点)
        afternoon_mask = (hours >= 14) & (hours <= 18)
        afternoon_glucose = median_curve[afternoon_mask]
        results['afternoon_curve_stability'] = 1 - (np.std(afternoon_glucose) / np.mean(afternoon_glucose))
        
        # 12. 晚间血糖升高幅度 (18-22点)
        evening_mask = (hours >= 18) & (hours <= 22)
        pre_evening_mask = (hours >= 17) & (hours <= 18)
        evening_max = np.max(median_curve[evening_mask])
        pre_evening_min = np.min(median_curve[pre_evening_mask])
        results['evening_surge_magnitude'] = evening_max - pre_evening_min
        
        # 13. 夜间曲线平坦度 (22-6点)
        night_mask = (hours >= 22) | (hours <= 6)
        night_glucose = median_curve[night_mask]
        results['nocturnal_curve_flatness'] = 1 - (np.std(night_glucose) / np.mean(night_glucose))
        
        return results
    
    def _analyze_percentile_bands(self, processed_data: Dict) -> Dict:
        """分位数带分析 (指标14-18)"""
        agp = processed_data['agp_curve']
        
        results = {}
        
        # 14. 25%分位线模式描述
        p25_stability = np.std(agp['p25']) / np.mean(agp['p25'])
        results['percentile_25_pattern'] = "平稳" if p25_stability < 0.3 else "波动"
        
        # 15. 75%分位线模式描述
        p75_trend = np.polyfit(agp['hour'], agp['p75'], 1)[0]
        results['percentile_75_pattern'] = "上升趋势" if p75_trend > 0.1 else "稳定"
        
        # 16. 分位数带宽变异系数 (重命名以避免与血糖CV混淆)
        band_width = agp['p75'] - agp['p25']
        results['percentile_band_cv'] = np.std(band_width) / np.mean(band_width) * 100
        
        # 新增: 真正的血糖变异系数(CV)
        raw_data = processed_data['raw_data']
        glucose_cv = (raw_data['glucose'].std() / raw_data['glucose'].mean()) * 100
        results['glucose_coefficient_of_variation'] = glucose_cv
        
        # 保持原来的分位数带宽变异性指标（有独立临床价值）
        results['percentile_spread_variability'] = results['percentile_band_cv']
        
        # 17. 目标范围内分位数带覆盖度
        target_mask = (agp['p25'] >= 3.9) & (agp['p75'] <= 10.0)
        results['target_range_coverage'] = np.sum(target_mask) / len(target_mask) * 100
        
        # 18. 分位数带平滑度
        iqr_width = agp['p75'] - agp['p25']
        results['quantile_band_smoothness'] = 1 - (np.var(iqr_width) / np.mean(iqr_width)**2)
        
        return results
    
    def _analyze_abnormal_patterns(self, processed_data: Dict) -> Dict:
        """异常模式识别 (指标19-23)"""
        raw_data = processed_data['raw_data']
        
        results = {}
        
        # 19. 急剧上升频率
        glucose_diff = raw_data['glucose'].diff()
        time_diff = raw_data['timestamp'].diff().dt.total_seconds() / 3600  # 小时
        spike_rate = glucose_diff / time_diff
        results['curve_spike_frequency'] = np.sum(spike_rate > 5) / processed_data['analysis_period']
        
        # 20. 急剧下降频率
        results['curve_drop_frequency'] = np.sum(spike_rate < -3) / processed_data['analysis_period']
        
        # 21. 高平台总时长
        high_glucose_mask = raw_data['glucose'] > 13
        time_diffs = raw_data['timestamp'].diff().dropna()
        sampling_interval = pd.Timedelta(np.median(time_diffs)).total_seconds() / 3600
        results['plateau_duration_total'] = np.sum(high_glucose_mask) * sampling_interval
        
        # 22. 血糖振荡幅度
        results['oscillation_amplitude'] = raw_data['glucose'].max() - raw_data['glucose'].min()
        
        # 23. 基线漂移斜率
        # 简化：使用线性回归检测总体趋势
        time_numeric = (raw_data['timestamp'] - raw_data['timestamp'].iloc[0]).dt.total_seconds() / 86400
        results['baseline_drift_slope'] = np.polyfit(time_numeric, raw_data['glucose'], 1)[0]
        
        return results
    
    def _analyze_meal_patterns(self, processed_data: Dict) -> Dict:
        """餐时模式分析 (指标24-27)"""
        agp = processed_data['agp_curve']
        hours = agp['hour']
        median_curve = agp['p50']
        
        results = {}
        
        # 24. 三餐峰值一致性评分
        breakfast_peak = np.max(median_curve[(hours >= 7) & (hours <= 9)])
        lunch_peak = np.max(median_curve[(hours >= 12) & (hours <= 14)])
        dinner_peak = np.max(median_curve[(hours >= 18) & (hours <= 20)])
        
        meal_peaks = [breakfast_peak, lunch_peak, dinner_peak]
        results['meal_peak_consistency'] = 1 - (np.std(meal_peaks) / np.mean(meal_peaks))
        
        # 25. 餐后恢复速率平均值
        # 简化实现：计算餐后2-4小时的下降速率
        post_breakfast = np.mean(np.diff(median_curve[(hours >= 9) & (hours <= 11)]))
        post_lunch = np.mean(np.diff(median_curve[(hours >= 14) & (hours <= 16)]))
        post_dinner = np.mean(np.diff(median_curve[(hours >= 20) & (hours <= 22)]))
        
        results['postprandial_recovery_rate'] = np.mean([post_breakfast, post_lunch, post_dinner])
        
        # 26. 餐前血糖下降模式
        pre_meal_dips = [
            np.min(median_curve[(hours >= 6.5) & (hours <= 7)]) < np.mean(median_curve[(hours >= 5) & (hours <= 6)]),
            np.min(median_curve[(hours >= 11.5) & (hours <= 12)]) < np.mean(median_curve[(hours >= 10) & (hours <= 11)]),
            np.min(median_curve[(hours >= 17.5) & (hours <= 18)]) < np.mean(median_curve[(hours >= 16) & (hours <= 17)])
        ]
        results['pre_meal_dip_pattern'] = np.sum(pre_meal_dips) >= 2
        
        # 27. 餐后反应变异系数
        meal_responses = [breakfast_peak - np.mean(median_curve[(hours >= 5) & (hours <= 7)]),
                         lunch_peak - np.mean(median_curve[(hours >= 10) & (hours <= 12)]),
                         dinner_peak - np.mean(median_curve[(hours >= 16) & (hours <= 18)])]
        results['meal_response_variability'] = np.std(meal_responses) / np.mean(meal_responses) * 100
        
        return results
    
    def _analyze_curve_complexity(self, processed_data: Dict) -> Dict:
        """曲线复杂度分析 (指标28-32)"""
        median_curve = processed_data['agp_curve']['p50']
        
        results = {}
        
        # 28. AGP曲线分形维数 (简化实现)
        # 使用盒子计数法的简化版本
        def box_count_dimension(curve, max_scale=10):
            scales = np.logspace(0, np.log10(max_scale), 10)
            counts = []
            for scale in scales:
                # 简化的盒子计数
                boxes = int(len(curve) / scale)
                count = len(np.unique((curve * boxes / np.max(curve)).astype(int)))
                counts.append(count)
            # 计算分形维数
            log_scales = np.log(1/scales)
            log_counts = np.log(counts)
            return -np.polyfit(log_scales, log_counts, 1)[0]
        
        results['fractal_dimension'] = box_count_dimension(median_curve)
        
        # 29. 曲线转折点频率
        def count_turning_points(curve):
            diff1 = np.diff(curve)
            diff_sign = np.sign(diff1)
            sign_changes = np.sum(np.diff(diff_sign) != 0)
            return sign_changes
        
        results['turning_point_frequency'] = count_turning_points(median_curve)
        
        # 30. 曲线粗糙度指数
        second_derivative = np.diff(median_curve, n=2)
        results['curve_roughness_index'] = np.mean(np.abs(second_derivative))
        
        # 31. 血糖自相关衰减系数
        autocorr = np.corrcoef(median_curve[:-1], median_curve[1:])[0,1]
        results['autocorrelation_decay'] = autocorr
        
        # 32. 近似熵
        def approximate_entropy(data, m=2, r=None):
            if r is None:
                r = 0.2 * np.std(data)
            
            def _maxdist(xi, xj, m):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def _phi(m):
                patterns = np.array([data[i:i+m] for i in range(len(data) - m + 1)])
                phi = 0
                for i in range(len(patterns)):
                    template = patterns[i]
                    matches = sum([1 for pattern in patterns if _maxdist(template, pattern, m) <= r])
                    if matches > 0:
                        phi += np.log(matches / len(patterns))
                return phi / len(patterns)
            
            return _phi(m) - _phi(m + 1)
        
        results['approximate_entropy'] = approximate_entropy(median_curve)
        
        return results
    
    def _analyze_target_range(self, processed_data: Dict) -> Dict:
        """目标范围分析 (指标33-36)"""
        raw_data = processed_data['raw_data']
        glucose = raw_data['glucose'].values
        
        results = {}
        
        # 33. 进入目标范围频率
        in_range = (glucose >= 3.9) & (glucose <= 10.0)
        entries = np.sum(np.diff(in_range.astype(int)) == 1)
        results['target_range_entry_frequency'] = entries / processed_data['analysis_period']
        
        # 34. 离开目标范围频率
        exits = np.sum(np.diff(in_range.astype(int)) == -1)
        results['target_range_exit_frequency'] = exits / processed_data['analysis_period']
        
        # 35. 目标范围内平均停留时间
        # 计算连续在目标范围内的时间段
        in_range_segments = []
        start = None
        for i, in_target in enumerate(in_range):
            if in_target and start is None:
                start = i
            elif not in_target and start is not None:
                in_range_segments.append(i - start)
                start = None
        
        if in_range_segments:
            time_diffs = raw_data['timestamp'].diff().dropna()
            avg_interval = pd.Timedelta(np.median(time_diffs)).total_seconds() / 60  # 分钟
            results['target_range_dwell_time_avg'] = np.mean(in_range_segments) * avg_interval
        else:
            results['target_range_dwell_time_avg'] = 0
        
        # 36. 范围转换平滑度
        # 简化：计算范围转换时的血糖变化平滑程度
        transition_points = np.where(np.diff(in_range.astype(int)) != 0)[0]
        if len(transition_points) > 0:
            transition_glucose = glucose[transition_points]
            smooth_transitions = signal.savgol_filter(transition_glucose, 
                                                    min(5, len(transition_glucose)), 1)
            results['range_transition_smoothness'] = 1 - np.mean(np.abs(transition_glucose - smooth_transitions))
        else:
            results['range_transition_smoothness'] = 1.0
        
        return results
    
    def _analyze_risk_zones(self, processed_data: Dict) -> Dict:
        """风险区域分析 (指标37-40)"""
        raw_data = processed_data['raw_data']
        glucose = raw_data['glucose'].values
        
        results = {}
        
        # 37. 低血糖区域最大深度
        hypo_glucose = glucose[glucose < 3.9]
        results['hypoglycemia_zone_depth'] = np.min(hypo_glucose) if len(hypo_glucose) > 0 else 3.9
        
        # 38. 高血糖区域最大高度
        hyper_glucose = glucose[glucose > 10.0]
        results['hyperglycemia_zone_height'] = np.max(hyper_glucose) if len(hyper_glucose) > 0 else 10.0
        
        # 39. 风险区域聚集数量
        risk_zones = (glucose < 3.9) | (glucose > 13.9)
        # 计算连续风险区域的数量
        risk_clusters = 0
        in_cluster = False
        for is_risk in risk_zones:
            if is_risk and not in_cluster:
                risk_clusters += 1
                in_cluster = True
            elif not is_risk:
                in_cluster = False
        results['risk_zone_cluster_count'] = risk_clusters
        
        # 40. 安全区域连续性
        safe_zones = (glucose >= 3.9) & (glucose <= 13.9)
        # 计算最长连续安全时间
        max_safe_duration = 0
        current_duration = 0
        for is_safe in safe_zones:
            if is_safe:
                current_duration += 1
            else:
                max_safe_duration = max(max_safe_duration, current_duration)
                current_duration = 0
        max_safe_duration = max(max_safe_duration, current_duration)
        results['safe_zone_continuity'] = max_safe_duration / len(safe_zones)
        
        return results
    
    def _analyze_daily_variability(self, processed_data: Dict) -> Dict:
        """日间变异分析 (指标41-44)"""
        raw_data = processed_data['raw_data']
        
        results = {}
        
        # 按日期分组分析
        raw_data['date'] = raw_data['timestamp'].dt.date
        daily_patterns = []
        
        for date, group in raw_data.groupby('date'):
            if len(group) >= 24:  # 确保有足够数据
                # 创建24小时模式
                group['hour'] = group['timestamp'].dt.hour + group['timestamp'].dt.minute / 60.0
                hourly_avg = group.groupby(group['hour'].round())['glucose'].mean()
                if len(hourly_avg) >= 20:  # 至少20小时数据
                    daily_patterns.append(hourly_avg.reindex(range(24), fill_value=np.nan))
        
        if len(daily_patterns) >= 2:
            daily_patterns_df = pd.DataFrame(daily_patterns)
            
            # 41. 日间模式相似度
            correlations = []
            for i in range(len(daily_patterns_df)):
                for j in range(i+1, len(daily_patterns_df)):
                    corr = daily_patterns_df.iloc[i].corr(daily_patterns_df.iloc[j])
                    if not np.isnan(corr):
                        correlations.append(corr)
            results['intraday_pattern_similarity'] = np.mean(correlations) if correlations else 0
            
            # 42. 清晨模式一致性 (6-10点)
            morning_patterns = daily_patterns_df.iloc[:, 6:11]
            morning_corr = morning_patterns.T.corr().values
            results['morning_pattern_consistency'] = np.mean(morning_corr[np.triu_indices_from(morning_corr, k=1)])
            
            # 43. 傍晚模式一致性 (17-21点)
            evening_patterns = daily_patterns_df.iloc[:, 17:22]
            evening_corr = evening_patterns.T.corr().values
            results['evening_pattern_consistency'] = np.mean(evening_corr[np.triu_indices_from(evening_corr, k=1)])
            
            # 44. 周末模式偏差度
            raw_data['is_weekend'] = raw_data['timestamp'].dt.dayofweek >= 5
            weekend_avg = raw_data[raw_data['is_weekend']]['glucose'].mean()
            weekday_avg = raw_data[~raw_data['is_weekend']]['glucose'].mean()
            results['weekend_pattern_deviation'] = abs(weekend_avg - weekday_avg)
        else:
            # 数据不足，使用默认值
            results.update({
                'intraday_pattern_similarity': 0.5,
                'morning_pattern_consistency': 0.5,
                'evening_pattern_consistency': 0.5,
                'weekend_pattern_deviation': 0
            })
        
        return results
    
    def _analyze_comprehensive_smoothness(self, processed_data: Dict) -> Dict:
        """平滑度综合分析 (指标45-48)"""
        median_curve = processed_data['agp_curve']['p50']
        
        results = {}
        
        # 45. 综合平滑度评分
        first_order = 1 - np.std(np.diff(median_curve)) / np.mean(np.abs(np.diff(median_curve)))
        second_order = 1 / (1 + np.var(np.diff(median_curve, n=2)))
        
        # 频域平滑度
        fft_vals = fft(median_curve)
        frequencies = fftfreq(len(median_curve))
        power_spectrum = np.abs(fft_vals)**2
        high_freq_power = np.sum(power_spectrum[np.abs(frequencies) > 0.1])
        total_power = np.sum(power_spectrum)
        freq_smoothness = 1 - high_freq_power / total_power
        
        results['comprehensive_smoothness_score'] = (0.4 * first_order + 
                                                   0.3 * second_order + 
                                                   0.3 * freq_smoothness)
        
        # 46. 移动平均平滑度
        window_size = max(3, len(median_curve) // 10)
        moving_avg = pd.Series(median_curve).rolling(window=window_size, center=True).mean().bfill().ffill()
        results['moving_average_smoothness'] = np.corrcoef(median_curve, moving_avg)[0,1]
        
        # 47. 频谱平滑度
        results['spectral_smoothness'] = 1 - high_freq_power / total_power
        
        # 48. 血糖平滑指数 (基于MAGE)
        # 简化的MAGE计算
        peaks, _ = signal.find_peaks(median_curve)
        valleys, _ = signal.find_peaks(-median_curve)
        all_extremes = np.sort(np.concatenate([peaks, valleys]))
        
        if len(all_extremes) >= 4:
            excursions = []
            for i in range(len(all_extremes)-1):
                excursion = abs(median_curve[all_extremes[i+1]] - median_curve[all_extremes[i]])
                if excursion >= np.std(median_curve):
                    excursions.append(excursion)
            mage = np.mean(excursions) if excursions else 0
        else:
            mage = 0
            
        results['glucose_smoothness_index'] = 1 - (mage / np.mean(median_curve)) if np.mean(median_curve) > 0 else 0
        
        return results
    
    def _analyze_symmetry(self, processed_data: Dict) -> Dict:
        """对称性分析 (指标49-52)"""
        median_curve = processed_data['agp_curve']['p50']
        hours = processed_data['agp_curve']['hour']
        
        results = {}
        
        # 49. 曲线对称性指数 (已在曲线形态中计算，这里再次计算以保持完整性)
        first_half = median_curve[:48]
        second_half = median_curve[48:][::-1]
        results['curve_symmetry_index'] = np.corrcoef(first_half, second_half)[0,1]
        
        # 50. 餐时对称性指数
        breakfast_pattern = median_curve[(hours >= 7) & (hours <= 9)]
        dinner_pattern = median_curve[(hours >= 19) & (hours <= 21)]
        if len(breakfast_pattern) == len(dinner_pattern):
            results['meal_symmetry_index'] = np.corrcoef(breakfast_pattern, dinner_pattern)[0,1]
        else:
            # 插值到相同长度
            breakfast_interp = np.interp(np.linspace(0, 1, 10), 
                                       np.linspace(0, 1, len(breakfast_pattern)), 
                                       breakfast_pattern)
            dinner_interp = np.interp(np.linspace(0, 1, 10), 
                                    np.linspace(0, 1, len(dinner_pattern)), 
                                    dinner_pattern)
            results['meal_symmetry_index'] = np.corrcoef(breakfast_interp, dinner_interp)[0,1]
        
        # 51. 周模式对称性指数 (简化实现)
        # 由于单次分析可能没有多周数据，使用AGP曲线的周期性
        results['weekly_symmetry_index'] = 0.7  # 默认值，实际需要多周数据
        
        # 52. 昼夜对称性指数
        morning_rise = median_curve[(hours >= 6) & (hours <= 10)]
        evening_fall = median_curve[(hours >= 20) & (hours <= 24)]
        
        # 计算上升和下降的对称性
        if len(morning_rise) > 0 and len(evening_fall) > 0:
            morning_slope = np.polyfit(range(len(morning_rise)), morning_rise, 1)[0]
            evening_slope = np.polyfit(range(len(evening_fall)), evening_fall, 1)[0]
            results['circadian_symmetry_index'] = 1 - abs(morning_slope + evening_slope) / max(abs(morning_slope), abs(evening_slope), 1)
        else:
            results['circadian_symmetry_index'] = 0.5
        
        return results
    
    def _analyze_visual_aesthetics(self, processed_data: Dict) -> Dict:
        """图形美学分析 (指标53-55)"""
        median_curve = processed_data['agp_curve']['p50']
        agp = processed_data['agp_curve']
        
        results = {}
        
        # 53. 曲线优雅度评分
        # 综合平滑性、对称性和简洁性
        smoothness = results.get('comprehensive_smoothness_score', 0.5)
        symmetry = results.get('curve_symmetry_index', 0.5)
        
        # 简洁性：转折点密度的倒数
        turning_points = results.get('turning_point_frequency', 10)
        simplicity = 1 / (1 + turning_points / 10)
        
        results['curve_elegance_score'] = (0.4 * smoothness + 0.3 * symmetry + 0.3 * simplicity)
        
        # 54. 视觉复杂度指数
        # 基于直方图熵和转折点密度
        hist, _ = np.histogram(median_curve, bins=20)
        hist = hist / np.sum(hist)  # 标准化
        entropy = -np.sum(hist * np.log(hist + 1e-10))
        turning_point_density = turning_points / len(median_curve)
        results['visual_complexity_index'] = 0.5 * entropy / np.log(20) + 0.5 * turning_point_density
        
        # 55. 颜色区域平衡度
        # 基于TIR, TAR, TBR的平衡性
        raw_data = processed_data['raw_data']
        glucose = raw_data['glucose']
        
        tir = np.sum((glucose >= 3.9) & (glucose <= 10.0)) / len(glucose)
        tbr = np.sum(glucose < 3.9) / len(glucose)
        tar = np.sum(glucose > 10.0) / len(glucose)
        
        # 理想分布：TIR=0.7, TAR=0.25, TBR=0.05
        ideal_dist = np.array([0.05, 0.7, 0.25])
        actual_dist = np.array([tbr, tir, tar])
        
        # 计算分布的均衡性（越接近理想分布越好）
        balance_score = 1 - np.sqrt(np.sum((ideal_dist - actual_dist)**2)) / np.sqrt(np.sum(ideal_dist**2))
        results['color_zone_balance'] = max(0, balance_score)
        
        return results


class AGPIntelligentReporter:
    """AGP智能报告生成器"""
    
    def __init__(self):
        self.analysis_results = None
        
    def generate_intelligent_report(self, analysis_results: Dict, patient_info: Dict = None) -> Dict:
        """
        生成智能AGP分析报告
        
        Args:
            analysis_results: AGP视觉分析结果
            patient_info: 患者信息
            
        Returns:
            结构化的智能分析报告
        """
        self.analysis_results = analysis_results
        
        report = {
            'patient_info': patient_info or {},
            'analysis_timestamp': datetime.now().isoformat(),
            'overall_assessment': self._generate_overall_assessment(),
            'key_findings': self._generate_key_findings(),
            'risk_alerts': self._generate_risk_alerts(),
            'clinical_recommendations': self._generate_clinical_recommendations(),
            'detailed_analysis': self._generate_detailed_analysis(),
            'trending': self._generate_trending_analysis(),
            'patient_education': self._generate_patient_education(),
            'technical_metrics': analysis_results
        }
        
        return report
    
    def _generate_overall_assessment(self) -> Dict:
        """生成整体评估"""
        # 基于多个指标生成综合评分
        smoothness_score = self.analysis_results.get('comprehensive_smoothness_score', 0.5)
        symmetry_score = self.analysis_results.get('curve_symmetry_index', 0.5)
        elegance_score = self.analysis_results.get('curve_elegance_score', 0.5)
        
        overall_score = (0.4 * smoothness_score + 0.3 * symmetry_score + 0.3 * elegance_score) * 100
        
        if overall_score >= 85:
            level = "优秀"
            description = "血糖控制稳定，AGP曲线优雅平滑"
        elif overall_score >= 70:
            level = "良好"  
            description = "血糖控制基本稳定，存在改善空间"
        elif overall_score >= 55:
            level = "一般"
            description = "血糖控制不够稳定，需要优化治疗"
        else:
            level = "需要改善"
            description = "血糖控制不佳，需要重新评估治疗方案"
        
        return {
            'overall_score': round(overall_score, 1),
            'level': level,
            'description': description,
            'data_quality': "优秀" if self.analysis_results.get('percentile_25_pattern') != "波动" else "良好"
        }
    
    def _generate_key_findings(self) -> List[Dict]:
        """生成关键发现"""
        findings = []
        
        # 黎明现象检测 (降低阈值以便更好检测)
        dawn_slope = self.analysis_results.get('dawn_curve_slope', 0)
        if abs(dawn_slope) > 0.5:  # 降低阈值
            if dawn_slope > 0.5:
                findings.append({
                    'type': 'dawn_phenomenon',
                    'severity': 'moderate' if dawn_slope < 1.5 else 'severe',
                    'description': f"检测到明显黎明现象，血糖上升速率{dawn_slope:.1f}mmol/L/h",
                    'clinical_significance': '提示基础胰岛素剂量或时机需要调整'
                })
            else:
                findings.append({
                    'type': 'reverse_dawn_phenomenon', 
                    'severity': 'moderate',
                    'description': f"检测到反向黎明现象，血糖下降速率{abs(dawn_slope):.1f}mmol/L/h",
                    'clinical_significance': '可能提示基础胰岛素过量或凌晨胰岛素敏感性增加'
                })
        
        # 餐后控制评估 (降低阈值)
        morning_peak = self.analysis_results.get('morning_peak_height', 0)
        if morning_peak > 3.0:  # 降低阈值
            findings.append({
                'type': 'postprandial_hyperglycemia',
                'severity': 'mild' if morning_peak < 5 else 'moderate' if morning_peak < 8 else 'severe',
                'description': f"早餐后血糖升高{morning_peak:.1f}mmol/L，控制需要改善",
                'clinical_significance': '建议优化速效胰岛素剂量或胰岛素碳水化合物比例'
            })
        
        # 夜间稳定性
        nocturnal_flatness = self.analysis_results.get('nocturnal_curve_flatness', 1.0)
        if nocturnal_flatness < 0.85:  # 稍微提高标准
            findings.append({
                'type': 'nocturnal_instability',
                'severity': 'mild' if nocturnal_flatness > 0.7 else 'moderate' if nocturnal_flatness > 0.5 else 'severe',
                'description': f"夜间血糖稳定性待改善，平坦度{nocturnal_flatness:.2f}",
                'clinical_significance': '可能存在夜间低血糖风险或基础胰岛素作用不足'
            })
        
        # 血糖变异性分析 (整体血糖稳定性)
        glucose_cv = self.analysis_results.get('glucose_coefficient_of_variation', 30)
        if glucose_cv > 36:  # ADA标准
            findings.append({
                'type': 'high_glucose_variability',
                'severity': 'mild' if glucose_cv < 50 else 'moderate' if glucose_cv < 70 else 'severe',
                'description': f"整体血糖变异性偏高，变异系数{glucose_cv:.1f}%",
                'clinical_significance': '提示血糖控制不够稳定，需评估治疗依从性和血糖管理策略'
            })
        
        # 时间模式变异性分析 (昼夜节律稳定性)
        band_cv = self.analysis_results.get('percentile_band_cv', 30)
        if band_cv > 40:  # 时间模式变异阈值
            findings.append({
                'type': 'temporal_pattern_variability',
                'severity': 'mild' if band_cv < 60 else 'moderate',
                'description': f"昼夜血糖模式变异较大，分位数带变异{band_cv:.1f}%",
                'clinical_significance': '提示血糖昼夜节律不够稳定，不同时段血糖分布差异较大'
            })
        
        # 增加TIR相关发现
        tir_percentage = self.analysis_results.get('target_range_coverage', 70)
        if tir_percentage < 70:
            findings.append({
                'type': 'low_tir',
                'severity': 'mild' if tir_percentage > 60 else 'moderate' if tir_percentage > 50 else 'severe',
                'description': f"目标范围内时间{tir_percentage:.1f}%，低于70%标准",
                'clinical_significance': 'ADA指南建议TIR应>70%，需要优化血糖管理策略'
            })
        
        # 曲线平滑度分析
        smoothness = self.analysis_results.get('median_curve_smoothness', 0.5)
        if smoothness < 0.6:
            findings.append({
                'type': 'curve_roughness',
                'severity': 'mild' if smoothness > 0.4 else 'moderate',
                'description': f"AGP曲线平滑度偏低，平滑指数{smoothness:.2f}",
                'clinical_significance': '血糖波动较大，提示需要改善血糖控制的稳定性'
            })
        
        # 对称性分析
        symmetry = self.analysis_results.get('curve_symmetry_index', 0.5)
        if abs(symmetry) < 0.3:  # 对称性太差
            findings.append({
                'type': 'asymmetric_pattern',
                'severity': 'mild',
                'description': f"血糖模式不对称，对称指数{symmetry:.2f}",
                'clinical_significance': '可能提示生活作息不规律或治疗方案需要个性化调整'
            })
        
        return findings
    
    def _generate_risk_alerts(self) -> List[Dict]:
        """生成风险警报"""
        alerts = []
        
        # 低血糖风险
        hypo_depth = self.analysis_results.get('hypoglycemia_zone_depth', 4.0)
        if hypo_depth < 3.0:
            alerts.append({
                'type': 'severe_hypoglycemia_risk',
                'urgency': 'high',
                'message': f"检测到严重低血糖，最低值{hypo_depth:.1f}mmol/L",
                'action_required': '立即评估胰岛素剂量，考虑减量'
            })
        elif hypo_depth < 3.5:
            alerts.append({
                'type': 'hypoglycemia_risk',
                'urgency': 'medium',
                'message': f"存在低血糖风险，最低值{hypo_depth:.1f}mmol/L",
                'action_required': '建议适当减少胰岛素剂量'
            })
        
        # 高血糖风险
        hyper_height = self.analysis_results.get('hyperglycemia_zone_height', 10.0)
        if hyper_height > 20:
            alerts.append({
                'type': 'severe_hyperglycemia_risk',
                'urgency': 'high',
                'message': f"检测到严重高血糖，最高值{hyper_height:.1f}mmol/L",
                'action_required': '立即评估治疗方案，考虑增加胰岛素剂量'
            })
        
        # 血糖突变风险
        spike_freq = self.analysis_results.get('curve_spike_frequency', 0)
        if spike_freq > 3:
            alerts.append({
                'type': 'glucose_instability',
                'urgency': 'medium',
                'message': f"血糖急剧变化频繁，每日{spike_freq:.1f}次",
                'action_required': '评估用药时机和剂量分配'
            })
        
        return alerts
    
    def _generate_clinical_recommendations(self) -> List[Dict]:
        """生成临床建议"""
        recommendations = []
        
        # 基于分析结果生成个性化建议
        dawn_slope = self.analysis_results.get('dawn_curve_slope', 0)
        if abs(dawn_slope) > 0.5:  # 降低阈值
            if dawn_slope > 0.5:
                recommendations.append({
                    'category': 'insulin_adjustment',
                    'priority': 'high' if dawn_slope > 1.0 else 'medium',
                    'recommendation': '建议调整基础胰岛素剂量或注射时间',
                    'rationale': f'黎明现象检测(斜率{dawn_slope:.1f}mmol/L/h)，可能需要优化基础胰岛素治疗',
                    'follow_up': '1-2周后复查AGP评估效果'
                })
            else:
                recommendations.append({
                    'category': 'insulin_adjustment', 
                    'priority': 'medium',
                    'recommendation': '建议评估基础胰岛素剂量，可能存在过量',
                    'rationale': f'检测到反向黎明现象(下降{abs(dawn_slope):.1f}mmol/L/h)，提示可能胰岛素过量',
                    'follow_up': '密切监测血糖变化，避免低血糖'
                })
        
        # TIR优化建议
        target_coverage = self.analysis_results.get('target_range_coverage', 80)
        if target_coverage < 70:
            recommendations.append({
                'category': 'treatment_optimization',
                'priority': 'high' if target_coverage < 50 else 'medium',
                'recommendation': '需要优化整体血糖管理策略提高TIR',
                'rationale': f'目标范围内时间{target_coverage:.1f}%低于ADA推荐的70%标准',
                'follow_up': '建议2-4周内重新评估，必要时调整治疗方案'
            })
        elif target_coverage < 85:
            recommendations.append({
                'category': 'treatment_optimization',
                'priority': 'low',
                'recommendation': '继续优化血糖管理，争取更高的TIR',
                'rationale': f'当前TIR{target_coverage:.1f}%已达标，但仍有提升空间',
                'follow_up': '保持现有治疗方案，定期监测'
            })
        
        # 餐后血糖建议
        morning_peak = self.analysis_results.get('morning_peak_height', 0)
        if morning_peak > 3.0:
            recommendations.append({
                'category': 'meal_management',
                'priority': 'medium' if morning_peak < 6 else 'high',
                'recommendation': '优化餐时胰岛素管理改善餐后血糖',
                'rationale': f'早餐后血糖升高{morning_peak:.1f}mmol/L，提示餐时管理需要改善',
                'follow_up': '建议营养师咨询，学习碳水化合物计数'
            })
        
        # 整体血糖变异性建议
        glucose_cv = self.analysis_results.get('glucose_coefficient_of_variation', 30)
        if glucose_cv > 36:
            recommendations.append({
                'category': 'glucose_control_optimization',
                'priority': 'medium',
                'recommendation': '优化整体血糖控制稳定性',
                'rationale': f'整体血糖变异系数{glucose_cv:.1f}%偏高，需要改善血糖控制质量',
                'follow_up': '评估治疗方案，加强血糖监测和管理'
            })
        
        # 时间模式变异性建议
        band_cv = self.analysis_results.get('percentile_band_cv', 30)
        if band_cv > 40:
            recommendations.append({
                'category': 'lifestyle_modification',
                'priority': 'medium',
                'recommendation': '建立规律的生活作息改善昼夜血糖节律',
                'rationale': f'昼夜血糖模式变异{band_cv:.1f}%偏高，提示生活节律不够规律',
                'follow_up': '固定作息时间，规律饮食和运动'
            })
        
        # 夜间管理建议
        nocturnal_flatness = self.analysis_results.get('nocturnal_curve_flatness', 1.0)
        if nocturnal_flatness < 0.8:
            recommendations.append({
                'category': 'insulin_adjustment',
                'priority': 'medium',
                'recommendation': '评估夜间基础胰岛素管理',
                'rationale': f'夜间血糖稳定性{nocturnal_flatness:.2f}待改善，可能影响睡眠质量',
                'follow_up': '记录夜间血糖和睡眠质量，必要时调整基础胰岛素'
            })
        
        # 曲线平滑度建议
        smoothness = self.analysis_results.get('median_curve_smoothness', 0.5)
        if smoothness < 0.6:
            recommendations.append({
                'category': 'comprehensive_management',
                'priority': 'medium',
                'recommendation': '综合改善血糖控制的平稳性',
                'rationale': f'AGP曲线平滑度{smoothness:.2f}偏低，血糖波动较大',
                'follow_up': '评估治疗依从性，考虑治疗方案调整'
            })
        
        # 如果没有生成任何建议，添加一般性建议
        if not recommendations:
            recommendations.append({
                'category': 'general_management',
                'priority': 'low',
                'recommendation': '维持当前血糖管理方案，继续定期监测',
                'rationale': '当前血糖模式相对稳定，未发现明显需要紧急调整的问题',
                'follow_up': '建议3个月后复查AGP，评估长期趋势'
            })
        
        return recommendations
    
    def _generate_detailed_analysis(self) -> Dict:
        """生成详细分析"""
        return {
            'curve_morphology': {
                'smoothness': self.analysis_results.get('median_curve_smoothness', 0),
                'symmetry': self.analysis_results.get('curve_symmetry_index', 0),
                'complexity': self.analysis_results.get('visual_complexity_index', 0),
                'interpretation': self._interpret_curve_morphology()
            },
            'time_patterns': {
                'dawn_phenomenon': self.analysis_results.get('dawn_curve_slope', 0),
                'postprandial_response': {
                    'morning': self.analysis_results.get('morning_peak_height', 0),
                    'consistency': self.analysis_results.get('meal_peak_consistency', 0)
                },
                'nocturnal_stability': self.analysis_results.get('nocturnal_curve_flatness', 0),
                'interpretation': self._interpret_time_patterns()
            },
            'variability_analysis': {
                'glucose_cv': self.analysis_results.get('glucose_coefficient_of_variation', 0),
                'percentile_band_cv': self.analysis_results.get('percentile_band_cv', 0),
                'oscillation_amplitude': self.analysis_results.get('oscillation_amplitude', 0),
                'interpretation': self._interpret_variability()
            }
        }
    
    def _interpret_curve_morphology(self) -> str:
        """解读曲线形态"""
        smoothness = self.analysis_results.get('median_curve_smoothness', 0.5)
        symmetry = self.analysis_results.get('curve_symmetry_index', 0.5)
        
        if smoothness > 0.8 and symmetry > 0.7:
            return "AGP曲线形态优秀，显示出良好的血糖控制稳定性和生活规律性"
        elif smoothness > 0.6 or symmetry > 0.5:
            return "AGP曲线基本稳定，但在平滑度或对称性方面存在改善空间"
        else:
            return "AGP曲线显示血糖控制不够稳定，建议重新评估治疗方案"
    
    def _interpret_time_patterns(self) -> str:
        """解读时间模式"""
        dawn_slope = self.analysis_results.get('dawn_curve_slope', 0)
        nocturnal_flatness = self.analysis_results.get('nocturnal_curve_flatness', 1.0)
        
        patterns = []
        if dawn_slope > 1.0:
            patterns.append("明显黎明现象")
        if nocturnal_flatness < 0.7:
            patterns.append("夜间血糖不够稳定")
            
        if not patterns:
            return "时间模式分析显示血糖昼夜节律基本正常"
        else:
            return f"时间模式分析发现：{', '.join(patterns)}，建议相应调整治疗方案"
    
    def _interpret_variability(self) -> str:
        """解读变异性（综合分析两种变异性）"""
        glucose_cv = self.analysis_results.get('glucose_coefficient_of_variation', 30)
        band_cv = self.analysis_results.get('percentile_band_cv', 30)
        
        # 整体血糖变异性评估
        if glucose_cv < 36:
            glucose_assessment = "整体血糖变异性良好"
        elif glucose_cv < 50:
            glucose_assessment = "整体血糖变异性中等"
        else:
            glucose_assessment = "整体血糖变异性偏高"
        
        # 时间模式变异性评估
        if band_cv < 30:
            pattern_assessment = "昼夜血糖节律稳定"
        elif band_cv < 50:
            pattern_assessment = "昼夜血糖节律有波动"
        else:
            pattern_assessment = "昼夜血糖节律不稳定"
        
        # 综合解读
        if glucose_cv < 36 and band_cv < 30:
            return f"{glucose_assessment}，{pattern_assessment}，血糖管理优秀"
        elif glucose_cv < 36:
            return f"{glucose_assessment}，但{pattern_assessment}，建议优化生活规律"
        elif band_cv < 30:
            return f"{pattern_assessment}，但{glucose_assessment}，建议优化血糖控制"
        else:
            return f"{glucose_assessment}且{pattern_assessment}，需要全面改善血糖管理"
    
    def _generate_trending_analysis(self) -> Dict:
        """生成趋势分析"""
        return {
            'baseline_trend': self.analysis_results.get('baseline_drift_slope', 0),
            'pattern_consistency': self.analysis_results.get('intraday_pattern_similarity', 0.5),
            'weekend_variation': self.analysis_results.get('weekend_pattern_deviation', 0),
            'interpretation': self._interpret_trending()
        }
    
    def _interpret_trending(self) -> str:
        """解读趋势"""
        drift = self.analysis_results.get('baseline_drift_slope', 0)
        consistency = self.analysis_results.get('intraday_pattern_similarity', 0.5)
        
        if abs(drift) < 0.05 and consistency > 0.7:
            return "血糖趋势稳定，日间模式一致性良好"
        elif abs(drift) > 0.1:
            direction = "上升" if drift > 0 else "下降" 
            return f"血糖基线呈{direction}趋势，需要关注长期控制"
        else:
            return "血糖模式存在一定变化，建议加强监测"
    
    def _generate_patient_education(self) -> List[Dict]:
        """生成患者教育内容"""
        education_points = []
        
        # 基于分析结果生成针对性教育内容
        dawn_slope = self.analysis_results.get('dawn_curve_slope', 0)
        if abs(dawn_slope) > 0.5:
            if dawn_slope > 0.5:
                education_points.append({
                    'topic': '黎明现象管理',
                    'content': [
                        '黎明现象是指清晨4-8点血糖自然上升的生理现象',
                        f'您的数据显示黎明现象比较明显(上升{dawn_slope:.1f}mmol/L/h)',
                        '这主要由生长激素、皮质醇等激素分泌增加引起',
                        '合理的基础胰岛素调整可以有效改善'
                    ],
                    'action_items': [
                        '记录连续一周的晨起血糖值(6:00-8:00)',
                        '确保长效胰岛素按医嘱时间注射',
                        '睡前避免高碳水化合物摄入',
                        '如持续晨起高血糖，及时联系医生调整方案'
                    ]
                })
            else:
                education_points.append({
                    'topic': '凌晨低血糖预防',
                    'content': [
                        f'您的血糖在凌晨时段有下降趋势(下降{abs(dawn_slope):.1f}mmol/L/h)',
                        '这可能提示基础胰岛素作用过强',
                        '凌晨低血糖容易引起反跳性高血糖',
                        '需要密切监测并适当调整治疗'
                    ],
                    'action_items': [
                        '注意夜间低血糖症状：出汗、心悸、噩梦',
                        '睡前血糖应维持在6-8mmol/L',
                        '必要时睡前适量加餐',
                        '发现异常立即联系医护团队'
                    ]
                })
        
        # TIR相关教育
        tir_percentage = self.analysis_results.get('target_range_coverage', 70)
        if tir_percentage < 70:
            education_points.append({
                'topic': 'TIR目标范围管理',
                'content': [
                    f'您的TIR(目标范围内时间)为{tir_percentage:.1f}%，低于推荐的70%',
                    'TIR是评估血糖控制质量的重要指标',
                    '提高TIR可以降低糖尿病并发症风险',
                    '需要通过综合管理来改善'
                ],
                'action_items': [
                    '严格按医嘱服药或注射胰岛素',
                    '保持规律的饮食和运动习惯',
                    '学习血糖自我监测技能',
                    '定期复查并调整治疗方案'
                ]
            })
        
        # 整体血糖变异性教育
        glucose_cv = self.analysis_results.get('glucose_coefficient_of_variation', 30)
        if glucose_cv > 36:
            education_points.append({
                'topic': '整体血糖稳定性改善',
                'content': [
                    f'您的整体血糖变异系数为{glucose_cv:.1f}%，超过ADA推荐的36%标准',
                    '血糖大幅波动比持续高血糖危害更大',
                    '稳定的血糖有助于预防急性和慢性并发症',
                    '需要从治疗方案和自我管理两方面入手改善'
                ],
                'action_items': [
                    '与医生讨论调整治疗方案的可能性',
                    '加强血糖自我监测频率',
                    '学习识别和处理血糖波动的诱因',
                    '建立规律的饮食和运动模式'
                ]
            })
        
        # 昼夜节律变异性教育
        band_cv = self.analysis_results.get('percentile_band_cv', 30)
        if band_cv > 40:
            education_points.append({
                'topic': '昼夜血糖节律优化',
                'content': [
                    f'您的昼夜血糖模式变异为{band_cv:.1f}%，提示不同时段差异较大',
                    '稳定的昼夜血糖节律有助于血糖管理',
                    '规律的生活作息是建立良好节律的基础',
                    '个体化的时间管理可以改善血糖模式'
                ],
                'action_items': [
                    '固定起床和就寝时间',
                    '三餐定时定量，避免夜间进食',
                    '根据AGP图谱识别问题时段',
                    '记录生活事件与血糖变化的关系'
                ]
            })
        
        # 餐后血糖教育
        morning_peak = self.analysis_results.get('morning_peak_height', 0)
        if morning_peak > 3.0:
            education_points.append({
                'topic': '餐后血糖管理',
                'content': [
                    f'您的早餐后血糖升高{morning_peak:.1f}mmol/L，需要改善',
                    '餐后2小时血糖应控制在10mmol/L以下',
                    '合理的餐时胰岛素管理是关键',
                    '饮食结构和进餐顺序也很重要'
                ],
                'action_items': [
                    '学习碳水化合物计数方法',
                    '餐前30分钟注射速效胰岛素',
                    '进餐顺序：蔬菜→蛋白质→主食',
                    '餐后适当活动，如散步15-30分钟'
                ]
            })
        
        # 夜间管理教育
        nocturnal_flatness = self.analysis_results.get('nocturnal_curve_flatness', 1.0)
        if nocturnal_flatness < 0.8:
            education_points.append({
                'topic': '夜间血糖管理',
                'content': [
                    f'您的夜间血糖稳定性{nocturnal_flatness:.2f}需要改善',
                    '良好的夜间血糖控制有助于改善睡眠质量',
                    '夜间血糖波动可能影响次日的血糖控制',
                    '需要优化基础胰岛素治疗'
                ],
                'action_items': [
                    '记录睡眠质量和夜间症状',
                    '睡前血糖控制在6-8mmol/L',
                    '避免睡前大量进食',
                    '必要时进行夜间血糖监测'
                ]
            })
        
        # 通用血糖管理教育
        education_points.append({
            'topic': 'CGM使用和血糖管理',
            'content': [
                'CGM为您提供连续的血糖信息，比传统血糖仪更全面',
                '关注血糖趋势箭头，及时调整治疗',
                '定期校准CGM确保数据准确性',
                'AGP报告能帮助您和医生制定更好的治疗方案'
            ],
            'action_items': [
                '每日查看CGM数据和趋势',
                '学会识别血糖模式',
                '记录饮食、运动和用药时间',
                '定期与医护团队分享AGP报告'
            ]
        })
        
        return education_points


# 主程序示例
def main():
    """主程序 - 演示CGM数据读取和AGP分析"""
    
    # 初始化组件
    cgm_reader = CGMDataReader()
    agp_analyzer = AGPVisualAnalyzer()
    report_generator = AGPIntelligentReporter()
    
    # 示例：处理CGM数据文件
    try:
        # 1. 读取CGM数据
        print("正在读取CGM数据...")
        # 请根据您的文件实际格式选择 device_type，如果文件是CSV格式，可以尝试 'generic_csv'
        # 如果是AGPAI_Agent_V2.py中那种tab分隔的格式，这个reader可能无法直接读取，需要调整
        cgm_file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/R002 V5.txt"
        cgm_data = cgm_reader.read_cgm_file(cgm_file_path, device_type='generic_csv') # 尝试使用通用CSV读取器
        
        print(f"成功读取{len(cgm_data)}个数据点，时间范围：{cgm_data['timestamp'].min()} 到 {cgm_data['timestamp'].max()}")
        
        # 2. 进行AGP视觉分析
        print("正在进行AGP视觉分析...")
        analysis_results = agp_analyzer.analyze_cgm_data(cgm_data, analysis_days=14)
        
        print(f"完成57种视觉指标分析")
        
        # 3. 生成智能报告
        print("正在生成智能分析报告...")
        patient_info = {
            'name': '张三',
            'age': 45,
            'gender': '男',
            'diabetes_type': 'T2DM',
            'diabetes_duration': '8年',
            'cgm_device': 'Dexcom G6'
        }
        
        intelligent_report = report_generator.generate_intelligent_report(analysis_results, patient_info)
        
        # 4. 输出报告摘要
        print("\n=== AGP智能分析报告 ===")
        overall = intelligent_report['overall_assessment']
        print(f"整体评估：{overall['level']} ({overall['overall_score']}分)")
        print(f"评估说明：{overall['description']}")
        
        print("\n主要发现：")
        for finding in intelligent_report['key_findings']:
            print(f"- {finding['description']}")
        
        print("\n风险警报：")
        for alert in intelligent_report['risk_alerts']:
            print(f"- [{alert['urgency'].upper()}] {alert['message']}")
        
        print("\n临床建议：")
        for rec in intelligent_report['clinical_recommendations']:
            print(f"- {rec['recommendation']}")
        
        # 5. 保存完整报告
        report_filename = f"AGP_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(intelligent_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n完整报告已保存至：{report_filename}")
        
        # 6. 显示关键指标
        print("\n=== 关键视觉指标 ===")
        key_indicators = [
            ('median_curve_smoothness', '中位数曲线平滑度'),
            ('curve_symmetry_index', '曲线对称性指数'),
            ('percentile_band_width_avg', '分位数带宽均值'),
            ('dawn_curve_slope', '黎明现象斜率'),
            ('morning_peak_height', '早晨峰值高度'),
            ('comprehensive_smoothness_score', '综合平滑度评分'),
            ('curve_elegance_score', '曲线优雅度评分')
        ]
        
        for key, desc in key_indicators:
            value = analysis_results.get(key, 0)
            print(f"{desc}: {value:.3f}")
        
        print("\n分析完成！")
        
    except Exception as e:
        print(f"处理过程中出现错误：{str(e)}")
        logging.exception("详细错误信息：")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 运行主程序
    main()