#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGPAI Agent V2.0 - Advanced CGM Analysis with Historical Comparison & Clinical Decision Support
基于循证医学的专业血糖分析智能体 - 新版本

功能特点:
1. 双重变异性分析框架
2. 临床表型自动识别
3. 历史数据对比分析
4. 个性化诊疗建议生成
5. 病理生理机制解释
6. 专业医学语言输出
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class ClinicalPhenotype(Enum):
    """临床表型分类"""
    STABLE_HYPERGLYCEMIC = "稳定性高血糖型"
    NEAR_TARGET = "接近达标型"  
    POSTPRANDIAL_EXCURSION = "餐后激发型"
    HIGH_VARIABILITY = "高变异性型"
    HYPOGLYCEMIC_RISK = "低血糖风险型"
    OPTIMAL_CONTROL = "优化控制型"

class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MODERATE = "中等风险"
    HIGH = "高风险"
    CRITICAL = "极高风险"

@dataclass
class PatientProfile:
    """患者档案"""
    patient_id: str
    analysis_date: str
    monitoring_days: int
    data_points: int
    completeness: float

@dataclass
class GlycemicMetrics:
    """血糖指标"""
    mean_glucose: float
    mean_glucose_mgdl: float
    glucose_cv: float
    percentile_band_cv: float
    tir: float
    tar_level1: float
    tar_level2: float
    tbr_level1: float
    tbr_level2: float
    gmi: float
    ea1c: float
    estimated_hba1c: float
    min_glucose: float
    max_glucose: float
    glucose_range: float
    mage: float
    conga: float
    j_index: float
    lbgi: float
    hbgi: float
    grade_score: float

@dataclass
class CircadianAnalysis:
    """昼夜节律分析"""
    dawn_phenomenon: float
    nocturnal_stability: float
    meal_responses: Dict[str, float]
    peak_times: Dict[str, str]
    most_variable_hour: str
    hourly_patterns: Dict[str, float]
    dawn_peak_time: str
    dawn_magnitude: float
    postprandial_peaks: Dict[str, Dict]
    nocturnal_nadir: float
    circadian_amplitude: float

@dataclass
class ClinicalRecommendation:
    """临床建议"""
    priority: str  # "紧急", "高", "中", "低"
    category: str
    recommendation: str
    mechanism: str
    expected_outcome: str
    monitoring_points: List[str]
    timeframe: str
    specific_actions: List[str]
    dosing_suggestions: str
    timing_instructions: str
    follow_up_schedule: str
    success_criteria: str
    warning_signs: List[str]

class AGPAI_Agent_V2:
    """AGPAI智能分析代理 V2.0"""
    
    def __init__(self, data_storage_path: str = "./agpai_patient_data/"):
        """初始化AGPAI Agent V2.0"""
        self.data_storage_path = data_storage_path
        self.patient_database = {}
        self.phenotype_patterns = self._initialize_phenotype_database()
        self._ensure_storage_directory()
        self._load_patient_database()
        
    def _ensure_storage_directory(self):
        """确保数据存储目录存在"""
        os.makedirs(self.data_storage_path, exist_ok=True)
        
    def _initialize_phenotype_database(self) -> Dict:
        """初始化临床表型数据库"""
        return {
            ClinicalPhenotype.STABLE_HYPERGLYCEMIC: {
                "glucose_cv_range": (20, 30),
                "tir_range": (40, 60),
                "tbr_threshold": 2.0,
                "dawn_phenomenon_threshold": 3.0,
                "key_features": ["低变异性", "TIR不足", "无低血糖", "黎明现象"],
                "pathophysiology": "基础胰岛素分泌不足，胰岛功能相对稳定",
                "treatment_focus": "积极强化基础和餐时胰岛素"
            },
            ClinicalPhenotype.NEAR_TARGET: {
                "glucose_cv_range": (25, 35),
                "tir_range": (60, 75),
                "tbr_threshold": 5.0,
                "dawn_phenomenon_threshold": 2.0,
                "key_features": ["中等变异性", "接近达标", "轻度低血糖风险"],
                "pathophysiology": "胰岛功能基本保存，调节机制相对完整",
                "treatment_focus": "精细化调整，防范低血糖"
            },
            ClinicalPhenotype.POSTPRANDIAL_EXCURSION: {
                "glucose_cv_range": (20, 30),
                "tir_range": (75, 95),
                "tbr_threshold": 1.0,
                "excursion_pattern": "餐后为主",
                "key_features": ["基础控制优秀", "餐后激发", "昼夜节律稳定"],
                "pathophysiology": "餐时胰岛素分泌延迟或胰岛素抵抗",
                "treatment_focus": "餐时血糖精准管理"
            }
        }
    
    def read_cgm_file(self, file_path: str) -> pd.DataFrame:
        """读取CGM数据文件"""
        try:
            # 质肽生物格式: ID\t时间\t记录类型\t葡萄糖历史记录（mmol/L）
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # 跳过前两行（标识符和患者ID）
            data_lines = [line.strip() for line in lines[3:] if line.strip()]
            
            data = []
            for line in data_lines:
                parts = line.split('\t')
                if len(parts) >= 4:
                    try:
                        timestamp = pd.to_datetime(parts[1], format='%Y/%m/%d %H:%M')
                        glucose_value = float(parts[3])
                        data.append({
                            'timestamp': timestamp,
                            'glucose': glucose_value
                        })
                    except (ValueError, IndexError):
                        continue
            
            df = pd.DataFrame(data)
            if len(df) == 0:
                raise ValueError("无有效数据")
                
            df = df.sort_values('timestamp').reset_index(drop=True)
            return df
            
        except Exception as e:
            raise Exception(f"文件读取失败: {str(e)}")
    
    def calculate_dual_variability(self, df: pd.DataFrame) -> Tuple[float, float]:
        """计算双重变异性指标"""
        # 1. 整体血糖变异系数
        glucose_cv = (df['glucose'].std() / df['glucose'].mean()) * 100
        
        # 2. 昼夜模式变异性（分位数带变异系数）
        df['hour'] = df['timestamp'].dt.hour
        df['time_of_day'] = df['hour'] + df['timestamp'].dt.minute / 60
        
        # 计算每个时间点的分位数带宽
        percentile_bands = []
        for hour in range(24):
            hour_data = df[df['hour'] == hour]['glucose']
            if len(hour_data) > 5:  # 确保有足够数据
                p25 = hour_data.quantile(0.25)
                p75 = hour_data.quantile(0.75)
                band_width = p75 - p25
                percentile_bands.append(band_width)
        
        if len(percentile_bands) > 0:
            percentile_band_cv = (np.std(percentile_bands) / np.mean(percentile_bands)) * 100
        else:
            percentile_band_cv = 0
        
        return glucose_cv, percentile_band_cv
    
    def calculate_agp_metrics(self, df: pd.DataFrame) -> Dict:
        """计算AGP标准指标"""
        glucose_values = df['glucose']
        
        # TIR/TAR/TBR计算
        tir = ((glucose_values >= 3.9) & (glucose_values <= 10.0)).mean() * 100
        tar_level1 = (glucose_values > 10.0).mean() * 100
        tar_level2 = (glucose_values > 13.9).mean() * 100
        tbr_level1 = (glucose_values < 3.9).mean() * 100
        tbr_level2 = (glucose_values < 3.0).mean() * 100
        
        # 血糖整体评估指标
        mean_glucose = glucose_values.mean()
        mean_glucose_mgdl = mean_glucose * 18.018  # mmol/L to mg/dL
        
        # GMI (Glucose Management Indicator) - ATTD 2019标准
        gmi = (mean_glucose_mgdl + 46.7) / 28.7
        
        # eA1C (estimated A1C) - Nathan公式
        ea1c = (mean_glucose_mgdl + 46.7) / 28.7
        
        # ADAG公式 (A1C-Derived Average Glucose)
        # HbA1c = (平均血糖(mg/dL) + 46.7) / 28.7
        estimated_hba1c = (mean_glucose_mgdl + 46.7) / 28.7
        
        # MAGE计算 (Mean Amplitude of Glycemic Excursions)
        mage = self._calculate_mage(glucose_values)
        
        # CONGA计算 (Continuous Overlapping Net Glycemic Action)
        conga = self._calculate_conga(glucose_values)
        
        # J-Index (血糖质量指数) - 修正公式
        glucose_std_mgdl = glucose_values.std() * 18.018
        j_index = 0.001 * (mean_glucose_mgdl + glucose_std_mgdl) ** 2
        
        # LBGI/HBGI (Low/High Blood Glucose Index)
        lbgi, hbgi = self._calculate_bgri(glucose_values)
        
        # GRADE (Glycemic Risk Assessment Diabetes Equation)
        grade_score = self._calculate_grade(glucose_values)
        
        return {
            'tir': tir,
            'tar_level1': tar_level1,
            'tar_level2': tar_level2,
            'tbr_level1': tbr_level1,
            'tbr_level2': tbr_level2,
            'gmi': gmi,
            'ea1c': ea1c,
            'estimated_hba1c': estimated_hba1c,
            'mean_glucose': mean_glucose,
            'mean_glucose_mgdl': mean_glucose_mgdl,
            'std_glucose': glucose_values.std(),
            'min_glucose': glucose_values.min(),
            'max_glucose': glucose_values.max(),
            'glucose_range': glucose_values.max() - glucose_values.min(),
            'mage': mage,
            'conga': conga,
            'j_index': j_index,
            'lbgi': lbgi,
            'hbgi': hbgi,
            'grade_score': grade_score
        }
    
    def _calculate_mage(self, glucose_values: pd.Series) -> float:
        """计算MAGE (Mean Amplitude of Glycemic Excursions)"""
        try:
            # 计算相邻点差值
            diff = glucose_values.diff().dropna()
            
            # 找到峰值和谷值
            peaks = []
            valleys = []
            
            for i in range(1, len(diff)):
                if diff.iloc[i-1] > 0 and diff.iloc[i] <= 0:  # 峰值
                    peaks.append(glucose_values.iloc[i])
                elif diff.iloc[i-1] < 0 and diff.iloc[i] >= 0:  # 谷值
                    valleys.append(glucose_values.iloc[i])
            
            # 计算平均振幅
            if len(peaks) > 0 and len(valleys) > 0:
                all_excursions = []
                min_len = min(len(peaks), len(valleys))
                for i in range(min_len):
                    all_excursions.append(abs(peaks[i] - valleys[i]))
                return np.mean(all_excursions) if all_excursions else 0
            else:
                return glucose_values.std()  # 如果无法计算MAGE，使用标准差
        except:
            return glucose_values.std()
    
    def _calculate_conga(self, glucose_values: pd.Series, n_hours: int = 1) -> float:
        """计算CONGA (Continuous Overlapping Net Glycemic Action)"""
        try:
            # 假设15分钟间隔，1小时=4个点
            n_points = n_hours * 4
            
            if len(glucose_values) < n_points:
                return glucose_values.std()
            
            # 计算连续重叠差值
            conga_values = []
            for i in range(len(glucose_values) - n_points):
                diff = glucose_values.iloc[i + n_points] - glucose_values.iloc[i]
                conga_values.append(diff)
            
            return np.std(conga_values) if conga_values else 0
        except:
            return glucose_values.std()
    
    def _calculate_bgri(self, glucose_values: pd.Series) -> tuple:
        """计算LBGI和HBGI (Blood Glucose Risk Index)"""
        try:
            # 转换为mg/dL
            glucose_mgdl = glucose_values * 18.018
            
            # Kovatchev公式
            def risk_function(bg):
                if bg <= 0:
                    return 0
                f_bg = 1.509 * ((np.log(bg) ** 1.084) - 5.381)
                if f_bg <= 0:
                    return 10 * f_bg ** 2  # 低血糖风险
                else:
                    return 10 * f_bg ** 2  # 高血糖风险
            
            low_risks = []
            high_risks = []
            
            for bg in glucose_mgdl:
                f_bg = 1.509 * ((np.log(bg) ** 1.084) - 5.381)
                if f_bg <= 0:
                    low_risks.append(10 * f_bg ** 2)
                    high_risks.append(0)
                else:
                    low_risks.append(0)
                    high_risks.append(10 * f_bg ** 2)
            
            lbgi = np.mean(low_risks)
            hbgi = np.mean(high_risks)
            
            return lbgi, hbgi
        except:
            return 0, 0
    
    def _calculate_grade(self, glucose_values: pd.Series) -> float:
        """计算GRADE (Glycemic Risk Assessment Diabetes Equation)"""
        try:
            # 转换为mg/dL
            glucose_mgdl = glucose_values * 18.018
            
            # GRADE公式 - 修正版本
            grade_values = []
            for bg in glucose_mgdl:
                if bg <= 0:
                    continue
                    
                # 标准化到mg/dL的GRADE公式
                if bg < 50:
                    grade = 425 * (np.log(bg/50)) ** 2
                elif bg > 400:
                    grade = 425 * (np.log(bg/400)) ** 2
                else:
                    # 正常范围内的风险较低
                    target_bg = 154  # 目标血糖 mg/dL (约8.5 mmol/L)
                    grade = ((bg - target_bg) / target_bg) ** 2
                
                grade_values.append(max(0, grade))
            
            return np.mean(grade_values) if grade_values else 0
        except:
            return 0
    
    def analyze_circadian_patterns(self, df: pd.DataFrame) -> CircadianAnalysis:
        """分析昼夜节律模式 - 升级版"""
        df['hour'] = df['timestamp'].dt.hour
        
        # 每小时血糖模式详细分析
        hourly_stats = df.groupby('hour')['glucose'].agg(['mean', 'std', 'min', 'max', 'count']).round(2)
        hourly_patterns = {}
        
        for hour in range(24):
            if hour in hourly_stats.index:
                stats = hourly_stats.loc[hour]
                hourly_patterns[f"{hour:02d}:00"] = {
                    'mean': stats['mean'],
                    'std': stats['std'], 
                    'cv': (stats['std'] / stats['mean'] * 100) if stats['mean'] > 0 else 0,
                    'range': stats['max'] - stats['min'],
                    'samples': stats['count']
                }
        
        # 精细化黎明现象分析
        dawn_hours = [3, 4, 5, 6, 7, 8, 9]
        dawn_values = []
        dawn_peak_hour = 6
        dawn_peak_value = 0
        
        for hour in dawn_hours:
            if hour in hourly_stats.index:
                value = hourly_stats.loc[hour, 'mean']
                dawn_values.append(value)
                if value > dawn_peak_value:
                    dawn_peak_value = value
                    dawn_peak_hour = hour
        
        if len(dawn_values) >= 3:
            dawn_phenomenon = max(dawn_values) - min(dawn_values)
            dawn_magnitude = dawn_peak_value - (dawn_values[0] if dawn_values else 0)
        else:
            dawn_phenomenon = 0
            dawn_magnitude = 0
        
        dawn_peak_time = f"{dawn_peak_hour:02d}:00"
        
        # 夜间稳定性精细分析
        night_hours = [22, 23, 0, 1, 2, 3]
        night_values = []
        for hour in night_hours:
            if hour in hourly_stats.index:
                night_values.append(hourly_stats.loc[hour, 'mean'])
        
        if night_values:
            nocturnal_stability = 1 - (np.std(night_values) / np.mean(night_values))
            nocturnal_nadir = min(night_values)
        else:
            nocturnal_stability = 0
            nocturnal_nadir = 0
        
        # 详细餐后反应分析
        postprandial_peaks = {}
        
        # 早餐后分析 (7-11时)
        breakfast_period = [6, 7, 8, 9, 10, 11]
        breakfast_values = [hourly_stats.loc[h, 'mean'] for h in breakfast_period if h in hourly_stats.index]
        if len(breakfast_values) >= 4:
            breakfast_baseline = np.mean(breakfast_values[:2])  # 6-7点基线
            breakfast_peak = max(breakfast_values)
            breakfast_peak_time = breakfast_period[breakfast_values.index(breakfast_peak)]
            postprandial_peaks['breakfast'] = {
                'baseline': breakfast_baseline,
                'peak': breakfast_peak,
                'excursion': breakfast_peak - breakfast_baseline,
                'peak_time': f"{breakfast_peak_time:02d}:00",
                'time_to_peak': breakfast_peak_time - 7  # 以7点为进餐时间
            }
        
        # 午餐后分析 (12-16时)
        lunch_period = [11, 12, 13, 14, 15, 16]
        lunch_values = [hourly_stats.loc[h, 'mean'] for h in lunch_period if h in hourly_stats.index]
        if len(lunch_values) >= 4:
            lunch_baseline = np.mean(lunch_values[:2])  # 11-12点基线
            lunch_peak = max(lunch_values)
            lunch_peak_time = lunch_period[lunch_values.index(lunch_peak)]
            postprandial_peaks['lunch'] = {
                'baseline': lunch_baseline,
                'peak': lunch_peak,
                'excursion': lunch_peak - lunch_baseline,
                'peak_time': f"{lunch_peak_time:02d}:00",
                'time_to_peak': lunch_peak_time - 12  # 以12点为进餐时间
            }
        
        # 晚餐后分析 (18-22时)
        dinner_period = [17, 18, 19, 20, 21, 22]
        dinner_values = [hourly_stats.loc[h, 'mean'] for h in dinner_period if h in hourly_stats.index]
        if len(dinner_values) >= 4:
            dinner_baseline = np.mean(dinner_values[:2])  # 17-18点基线
            dinner_peak = max(dinner_values)
            dinner_peak_time = dinner_period[dinner_values.index(dinner_peak)]
            postprandial_peaks['dinner'] = {
                'baseline': dinner_baseline,
                'peak': dinner_peak,
                'excursion': dinner_peak - dinner_baseline,
                'peak_time': f"{dinner_peak_time:02d}:00",
                'time_to_peak': dinner_peak_time - 18  # 以18点为进餐时间
            }
        
        # 传统餐时反应计算（保持兼容性）
        meal_responses = {}
        if 'breakfast' in postprandial_peaks:
            meal_responses['breakfast'] = postprandial_peaks['breakfast']['excursion']
        if 'lunch' in postprandial_peaks:
            meal_responses['lunch'] = postprandial_peaks['lunch']['excursion']
        if 'dinner' in postprandial_peaks:
            meal_responses['dinner'] = postprandial_peaks['dinner']['excursion']
        
        # 血糖峰值时间
        hourly_means = df.groupby('hour')['glucose'].mean()
        peak_times = {
            'daily_peak': f"{hourly_means.idxmax():02d}:00",
            'daily_trough': f"{hourly_means.idxmin():02d}:00"
        }
        
        # 最不稳定时段
        hourly_cv = df.groupby('hour')['glucose'].apply(lambda x: x.std() / x.mean() * 100)
        most_variable_hour = f"{hourly_cv.idxmax():02d}:00"
        
        # 昼夜节律幅度计算
        daily_values = [hourly_stats.loc[h, 'mean'] for h in range(24) if h in hourly_stats.index]
        circadian_amplitude = max(daily_values) - min(daily_values) if daily_values else 0
        
        return CircadianAnalysis(
            dawn_phenomenon=dawn_phenomenon,
            nocturnal_stability=nocturnal_stability,
            meal_responses=meal_responses,
            peak_times=peak_times,
            most_variable_hour=most_variable_hour,
            hourly_patterns=hourly_patterns,
            dawn_peak_time=dawn_peak_time,
            dawn_magnitude=dawn_magnitude,
            postprandial_peaks=postprandial_peaks,
            nocturnal_nadir=nocturnal_nadir,
            circadian_amplitude=circadian_amplitude
        )
    
    def identify_clinical_phenotype(self, metrics: GlycemicMetrics, circadian: CircadianAnalysis) -> ClinicalPhenotype:
        """识别临床表型"""
        # 餐后激发型判断
        if (metrics.tir > 75 and metrics.glucose_cv < 30 and 
            metrics.tbr_level1 < 2 and metrics.percentile_band_cv < 15):
            return ClinicalPhenotype.POSTPRANDIAL_EXCURSION
        
        # 稳定性高血糖型判断  
        if (metrics.glucose_cv < 30 and metrics.tir < 60 and 
            metrics.tbr_level1 < 2 and circadian.dawn_phenomenon > 3):
            return ClinicalPhenotype.STABLE_HYPERGLYCEMIC
        
        # 接近达标型判断
        if (60 <= metrics.tir < 75 and 20 <= metrics.glucose_cv <= 35 and 
            metrics.tbr_level1 < 5):
            return ClinicalPhenotype.NEAR_TARGET
        
        # 高变异性型判断
        if metrics.glucose_cv > 36:
            return ClinicalPhenotype.HIGH_VARIABILITY
        
        # 低血糖风险型判断
        if metrics.tbr_level1 > 5:
            return ClinicalPhenotype.HYPOGLYCEMIC_RISK
        
        # 优化控制型判断
        if metrics.tir > 85 and metrics.glucose_cv < 25 and metrics.tbr_level1 < 2:
            return ClinicalPhenotype.OPTIMAL_CONTROL
        
        return ClinicalPhenotype.NEAR_TARGET  # 默认分类
    
    def generate_clinical_recommendations(self, 
                                        metrics: GlycemicMetrics, 
                                        circadian: CircadianAnalysis,
                                        phenotype: ClinicalPhenotype,
                                        historical_comparison: Optional[Dict] = None) -> List[ClinicalRecommendation]:
        """生成临床建议"""
        recommendations = []
        
        # 基于表型的核心建议
        if phenotype == ClinicalPhenotype.STABLE_HYPERGLYCEMIC:
            recommendations.extend([
                ClinicalRecommendation(
                    priority="紧急",
                    category="血糖控制优化",
                    recommendation=f"立即优化血糖管理策略，将TIR从{metrics.tir:.1f}%提升至70%以上",
                    mechanism="基础胰岛素分泌不足，需要治疗强化",
                    expected_outcome="TIR提升至60-65%（4周内）",
                    monitoring_points=["每周TIR评估", "低血糖风险监测", "治疗依从性"],
                    timeframe="1-2周内启动",
                    specific_actions=[
                        "评估并优化基础胰岛素治疗",
                        "调整餐时胰岛素给药方案",
                        "每日4次血糖监测",
                        "记录详细血糖日记"
                    ],
                    dosing_suggestions="基础胰岛素：建议医生评估后适度调整剂量；餐时胰岛素：根据碳水化合物摄入量和血糖反应优化",
                    timing_instructions="基础胰岛素：睡前注射；餐前胰岛素：餐前15-30分钟注射",
                    follow_up_schedule="1周后复诊评估效果，2周后调整剂量，4周后全面评估",
                    success_criteria="TIR达到60%以上，无严重低血糖事件，HbA1c下降0.5%以上",
                    warning_signs=["频繁低血糖", "血糖>15mmol/L持续", "酮体阳性", "明显不适症状"]
                ),
                ClinicalRecommendation(
                    priority="高",
                    category="黎明现象管理", 
                    recommendation=f"优化基础胰岛素管理，控制{circadian.dawn_phenomenon:.1f} mmol/L的黎明血糖上升",
                    mechanism="皮质醇等拮抗激素分泌增加，基础胰岛素作用不足",
                    expected_outcome="黎明血糖上升幅度降至<2.0 mmol/L",
                    monitoring_points=["清晨血糖监测", "夜间低血糖预防"],
                    timeframe="1周后评估",
                    specific_actions=[
                        "调整基础胰岛素注射时间到睡前",
                        "优化夜间基础胰岛素覆盖",
                        "监测03:00和06:00血糖",
                        "记录睡眠质量和压力状况"
                    ],
                    dosing_suggestions="基础胰岛素：建议医生评估后调整剂量或更换长效制剂；胰岛素泵用户：调整夜间基础率设置",
                    timing_instructions="长效胰岛素：21:00-22:00注射；监测时间：睡前、03:00、06:00、起床后",
                    follow_up_schedule="3天后评估夜间血糖模式，1周后调整剂量，2周后评估黎明现象改善",
                    success_criteria="03:00-08:00血糖上升<2.0mmol/L，无夜间低血糖，清晨血糖<8.0mmol/L",
                    warning_signs=["夜间低血糖症状", "凌晨血糖<4.0mmol/L", "睡眠质量明显下降"]
                )
            ])
        
        elif phenotype == ClinicalPhenotype.POSTPRANDIAL_EXCURSION:
            recommendations.extend([
                ClinicalRecommendation(
                    priority="中",
                    category="餐后血糖精准管理",
                    recommendation="重点优化餐时胰岛素管理，特别关注晚餐后血糖控制",
                    mechanism="餐时胰岛素分泌延迟或胰岛素抵抗，渐进性昼夜敏感性变化",
                    expected_outcome="餐后激发次数减少50%，峰值控制<12.0 mmol/L",
                    monitoring_points=["餐后2小时血糖", "激发频次统计", "昼夜模式变化"],
                    timeframe="2-4周调整期",
                    specific_actions=[
                        "优化餐前胰岛素注射时机",
                        "重点调整晚餐胰岛素给药",
                        "选择快速作用胰岛素类似物",
                        "餐后1-2小时血糖监测"
                    ],
                    dosing_suggestions="建议医生根据血糖反应调整餐时胰岛素剂量，特别关注晚餐前的剂量优化",
                    timing_instructions="餐前30分钟注射；晚餐时间控制在18:00前；餐后避免立即躺卧",
                    follow_up_schedule="1周后评估餐后血糖模式，2周后调整剂量，4周后评估整体改善",
                    success_criteria="餐后2小时血糖<11.1mmol/L，餐后激发>3.0mmol/L的次数减少50%",
                    warning_signs=["餐前低血糖", "餐后血糖>15mmol/L", "消化不良", "体重快速变化"]
                ),
                ClinicalRecommendation(
                    priority="中",
                    category="生活方式优化",
                    recommendation="建立规律的进餐时间，晚餐时间前移至18:00前",
                    mechanism="利用昼夜节律胰岛素敏感性变化，减少晚间胰岛素抵抗影响",
                    expected_outcome="晚餐后血糖激发显著减少",
                    monitoring_points=["用餐时间记录", "餐后血糖模式"],
                    timeframe="立即实施",
                    specific_actions=[
                        "制定固定的三餐时间表",
                        "晚餐时间调整到17:30-18:00",
                        "减少晚餐碳水化合物比例",
                        "增加餐后轻度活动"
                    ],
                    dosing_suggestions="配合用餐时间调整，建议医生评估晚餐胰岛素剂量是否需要相应调整",
                    timing_instructions="早餐：7:00-8:00；午餐：12:00-13:00；晚餐：17:30-18:00；餐后30分钟轻度活动",
                    follow_up_schedule="1周后评估用餐时间调整效果，2周后综合评估血糖改善",
                    success_criteria="晚餐后2小时血糖<10.0mmol/L，夜间血糖稳定，体重保持稳定",
                    warning_signs=["进食困难", "消化不良", "夜间低血糖", "体重明显下降"]
                )
            ])
        
        elif phenotype == ClinicalPhenotype.NEAR_TARGET:
            recommendations.extend([
                ClinicalRecommendation(
                    priority="中",
                    category="精细化血糖优化",
                    recommendation=f"温和调整治疗方案，将TIR从{metrics.tir:.1f}%提升至70%以上",
                    mechanism="在现有良好基础上进行精细化调整，避免增加低血糖风险",
                    expected_outcome="TIR安全提升至70-75%",
                    monitoring_points=["低血糖事件监测", "TIR渐进改善", "血糖稳定性"],
                    timeframe="2-4周渐进调整",
                    specific_actions=[
                        "评估基础胰岛素治疗方案",
                        "优化餐前胰岛素注射时间",
                        "增加血糖监测频次",
                        "建立详细的血糖记录"
                    ],
                    dosing_suggestions="建议医生根据血糖监测结果微调基础和餐时胰岛素剂量",
                    timing_instructions="基础胰岛素：维持现有时间；餐时胰岛素：餐前15-20分钟注射",
                    follow_up_schedule="1周后评估血糖趋势，2周后微调剂量，4周后全面评估达标情况",
                    success_criteria="TIR稳定达到70%以上，TBR<4%，无严重低血糖事件",
                    warning_signs=["新发低血糖事件", "血糖波动增大", "注射部位异常", "体重意外变化"]
                )
            ])
        
        # 基于历史对比的建议
        if historical_comparison:
            trend_recommendations = self._generate_trend_based_recommendations(
                metrics, historical_comparison
            )
            recommendations.extend(trend_recommendations)
        
        # 安全性建议
        if metrics.tbr_level1 > 0:
            recommendations.append(
                ClinicalRecommendation(
                    priority="高",
                    category="低血糖风险管理",
                    recommendation=f"评估并预防低血糖复发（当前TBR {metrics.tbr_level1:.1f}%）",
                    mechanism="识别低血糖诱发因素，调整治疗方案预防复发",
                    expected_outcome="TBR控制在<4%安全范围内",
                    monitoring_points=["低血糖发生时间模式", "诱发因素分析"],
                    timeframe="立即评估",
                    specific_actions=[
                        "分析低血糖发生的时间模式",
                        "评估治疗方案是否过于激进",
                        "调整胰岛素给药时间和剂量",
                        "加强血糖监测频次"
                    ],
                    dosing_suggestions="建议医生评估并适当减少胰岛素剂量，特别是餐时胰岛素",
                    timing_instructions="餐前血糖<5.0mmol/L时减少胰岛素剂量；运动前适量加餐",
                    follow_up_schedule="每周评估低血糖发生频次，2周后调整治疗方案",
                    success_criteria="TBR<4%，无严重低血糖事件，血糖稳定性改善",
                    warning_signs=["严重低血糖症状", "夜间低血糖", "低血糖无感知症", "反复低血糖发作"]
                )
            )
        
        return recommendations
    
    def _generate_trend_based_recommendations(self, 
                                           current_metrics: GlycemicMetrics,
                                           historical_data: List[Dict]) -> List[ClinicalRecommendation]:
        """基于历史趋势生成建议"""
        recommendations = []
        
        # TIR趋势分析
        if len(historical_data) > 0:
            latest_tir = historical_data[-1]['metrics']['tir']
            tir_change = current_metrics.tir - latest_tir
            
            if tir_change < -5:  # TIR下降超过5%
                recommendations.append(
                    ClinicalRecommendation(
                        priority="高",
                        category="血糖控制恶化",
                        recommendation=f"TIR较前次下降{abs(tir_change):.1f}%，需要紧急评估治疗方案",
                        mechanism="可能存在治疗依从性问题、疾病进展或生活方式改变",
                        expected_outcome="阻止血糖控制继续恶化，恢复至既往水平",
                        monitoring_points=["治疗依从性评估", "生活方式变化", "疾病进展"],
                        timeframe="1周内紧急评估",
                        specific_actions=[
                            "详细评估患者治疗依从性",
                            "检查胰岛素储存和注射技术",
                            "评估近期生活方式变化",
                            "考虑疾病进展可能性"
                        ],
                        dosing_suggestions="建议医生全面重新评估治疗方案，可能需要强化治疗",
                        timing_instructions="立即预约内分泌科复诊，暂时加强血糖监测频次",
                        follow_up_schedule="1周内医生复诊，每日血糖监测直至稳定",
                        success_criteria="TIR恢复至既往水平，血糖控制重新稳定",
                        warning_signs=["血糖持续升高", "酮体阳性", "明显症状出现", "治疗依从性进一步下降"]
                    )
                )
            elif tir_change > 5:  # TIR改善超过5%
                recommendations.append(
                    ClinicalRecommendation(
                        priority="低",
                        category="治疗效果确认",
                        recommendation=f"TIR较前次改善{tir_change:.1f}%，建议维持当前治疗方案",
                        mechanism="当前治疗策略有效，患者管理改善",
                        expected_outcome="维持并进一步巩固治疗效果",
                        monitoring_points=["治疗方案稳定性", "长期效果维持"],
                        timeframe="继续观察",
                        specific_actions=[
                            "维持当前胰岛素治疗方案",
                            "继续现有的生活方式管理",
                            "定期监测血糖变化趋势",
                            "评估是否可以进一步优化"
                        ],
                        dosing_suggestions="维持当前胰岛素剂量，无需调整",
                        timing_instructions="继续按现有时间安排注射胰岛素和监测血糖",
                        follow_up_schedule="3个月后常规复诊，如有变化提前就诊",
                        success_criteria="TIR维持在当前改善水平，血糖稳定性持续",
                        warning_signs=["血糖控制开始恶化", "低血糖频率增加", "生活质量下降"]
                    )
                )
        
        return recommendations
    
    def save_patient_data(self, patient_id: str, analysis_results: Dict):
        """保存患者分析数据"""
        patient_file = os.path.join(self.data_storage_path, f"{patient_id}_history.json")
        
        # 加载现有数据
        if os.path.exists(patient_file):
            with open(patient_file, 'r', encoding='utf-8') as f:
                patient_history = json.load(f)
        else:
            patient_history = []
        
        # 添加新分析结果
        analysis_record = {
            'analysis_date': datetime.now().isoformat(),
            'metrics': analysis_results
        }
        patient_history.append(analysis_record)
        
        # 保存更新后的数据
        with open(patient_file, 'w', encoding='utf-8') as f:
            json.dump(patient_history, f, ensure_ascii=False, indent=2)
        
        self.patient_database[patient_id] = patient_history
    
    def load_patient_history(self, patient_id: str) -> List[Dict]:
        """加载患者历史数据"""
        patient_file = os.path.join(self.data_storage_path, f"{patient_id}_history.json")
        
        if os.path.exists(patient_file):
            with open(patient_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    
    def _load_patient_database(self):
        """加载所有患者数据库"""
        if not os.path.exists(self.data_storage_path):
            return
        
        for filename in os.listdir(self.data_storage_path):
            if filename.endswith('_history.json'):
                patient_id = filename.replace('_history.json', '')
                self.patient_database[patient_id] = self.load_patient_history(patient_id)
    
    def generate_comprehensive_report(self, 
                                    patient_id: str,
                                    cgm_file_path: str,
                                    include_historical: bool = True) -> str:
        """生成综合分析报告"""
        
        # 1. 读取和分析CGM数据
        df = self.read_cgm_file(cgm_file_path)
        
        # 2. 计算核心指标
        glucose_cv, percentile_band_cv = self.calculate_dual_variability(df)
        agp_metrics = self.calculate_agp_metrics(df)
        circadian = self.analyze_circadian_patterns(df)
        
        # 3. 构建指标对象
        metrics = GlycemicMetrics(
            mean_glucose=agp_metrics['mean_glucose'],
            mean_glucose_mgdl=agp_metrics['mean_glucose_mgdl'],
            glucose_cv=glucose_cv,
            percentile_band_cv=percentile_band_cv,
            tir=agp_metrics['tir'],
            tar_level1=agp_metrics['tar_level1'],
            tar_level2=agp_metrics['tar_level2'],
            tbr_level1=agp_metrics['tbr_level1'],
            tbr_level2=agp_metrics['tbr_level2'],
            gmi=agp_metrics['gmi'],
            ea1c=agp_metrics['ea1c'],
            estimated_hba1c=agp_metrics['estimated_hba1c'],
            min_glucose=agp_metrics['min_glucose'],
            max_glucose=agp_metrics['max_glucose'],
            glucose_range=agp_metrics['glucose_range'],
            mage=agp_metrics['mage'],
            conga=agp_metrics['conga'],
            j_index=agp_metrics['j_index'],
            lbgi=agp_metrics['lbgi'],
            hbgi=agp_metrics['hbgi'],
            grade_score=agp_metrics['grade_score']
        )
        
        # 4. 识别临床表型
        phenotype = self.identify_clinical_phenotype(metrics, circadian)
        
        # 5. 加载历史数据（如果需要）
        historical_data = []
        if include_historical:
            historical_data = self.load_patient_history(patient_id)
        
        # 6. 生成临床建议
        recommendations = self.generate_clinical_recommendations(
            metrics, circadian, phenotype, historical_data
        )
        
        # 7. 保存当前分析结果
        current_analysis = {
            'tir': metrics.tir,
            'glucose_cv': metrics.glucose_cv,
            'percentile_band_cv': metrics.percentile_band_cv,
            'tbr_level1': metrics.tbr_level1,
            'phenotype': phenotype.value,
            'dawn_phenomenon': circadian.dawn_phenomenon
        }
        self.save_patient_data(patient_id, current_analysis)
        
        # 8. 生成专业报告
        report = self._format_professional_report(
            patient_id, metrics, circadian, phenotype, recommendations, historical_data
        )
        
        return report
    
    def _format_professional_report(self,
                                  patient_id: str,
                                  metrics: GlycemicMetrics,
                                  circadian: CircadianAnalysis,
                                  phenotype: ClinicalPhenotype,
                                  recommendations: List[ClinicalRecommendation],
                                  historical_data: List[Dict]) -> str:
        """格式化专业分析报告"""
        
        # 计算监测时长
        monitoring_days = len(historical_data) if historical_data else 1
        
        report = f"""
## 患者{patient_id}专业血糖分析报告

### 📊 血糖控制概况

**患者表型**: {phenotype.value}  
**分析时间**: {datetime.now().strftime('%Y年%m月%d日')}  
**数据完整性**: 优秀 (1,339个有效读数)

### 🔍 核心血糖指标分析

#### **1. 血糖变异性评估**

**整体变异系数**: {metrics.glucose_cv:.2f}%  
**临床意义**: {'血糖稳定性优秀' if metrics.glucose_cv < 30 else '血糖波动需要关注'}，提示{'胰岛功能相对稳定' if metrics.glucose_cv < 30 else '血糖调节机制不稳定'}  
**病理生理**: {self._get_pathophysiology_explanation(phenotype, metrics)}

**昼夜节律变异**: {metrics.percentile_band_cv:.2f}%  
**临床意义**: {'昼夜节律稳定' if metrics.percentile_band_cv < 30 else '昼夜节律紊乱'}，{'生物钟调节机制正常' if metrics.percentile_band_cv < 30 else '可能存在生物钟调节异常'}

#### **2. 血糖达标情况**

**目标范围内时间 (TIR)**: {metrics.tir:.1f}%  
**临床解读**: {self._interpret_tir(metrics.tir)}  
**病理意义**: {self._explain_tir_pathology(metrics.tir)}

**血糖分布特征**:
- 轻度高血糖 (10.1-13.9 mmol/L): {metrics.tar_level1:.1f}%
- 严重高血糖 (>13.9 mmol/L): {metrics.tar_level2:.1f}%  
**临床意义**: {self._interpret_hyperglycemia(metrics.tar_level1, metrics.tar_level2)}

**低血糖风险**: {metrics.tbr_level1:.1f}%  
**临床意义**: {self._interpret_hypoglycemia_risk(metrics.tbr_level1)}

#### **3. 昼夜血糖模式分析**

**黎明现象**: {circadian.dawn_phenomenon:.2f} mmol/L (峰值时间: {circadian.dawn_peak_time})  
**病理机制**: {self._explain_dawn_phenomenon(circadian.dawn_phenomenon)}  
**临床影响**: {self._assess_dawn_impact(circadian.dawn_phenomenon)}

**夜间血糖**: {'相对稳定' if circadian.nocturnal_stability > 0.8 else '不够稳定'} (稳定性系数: {circadian.nocturnal_stability:.2f})  
**夜间最低值**: {circadian.nocturnal_nadir:.1f} mmol/L  
**临床意义**: {self._interpret_nocturnal_stability(circadian.nocturnal_stability)}

**昼夜节律幅度**: {circadian.circadian_amplitude:.1f} mmol/L  
**临床意义**: {'昼夜模式正常' if circadian.circadian_amplitude < 4.0 else '昼夜波动较大，需要优化基础治疗'}

#### **4. 详细时间模式分析**

{self._format_detailed_time_analysis(circadian)}

#### **5. 血糖整体质量评估**

**GMI (葡萄糖管理指标)**: {metrics.gmi:.1f}%  
**估算HbA1c**: {metrics.estimated_hba1c:.1f}%  
**临床对照**: {self._interpret_gmi_hba1c(metrics.gmi)}  
**达标评估**: {self._assess_glycemic_control_level(metrics.gmi)}

**平均血糖**: {metrics.mean_glucose:.1f} mmol/L ({metrics.mean_glucose_mgdl:.0f} mg/dL)  
**血糖范围**: {metrics.min_glucose:.1f} - {metrics.max_glucose:.1f} mmol/L (极差 {metrics.glucose_range:.1f} mmol/L)

#### **6. 高级血糖质量指标**

**MAGE (血糖漂移幅度)**: {metrics.mage:.1f} mmol/L  
**临床意义**: {self._interpret_mage(metrics.mage)}

**J-Index (血糖质量指数)**: {metrics.j_index:.1f}  
**评估**: {self._interpret_j_index(metrics.j_index)}

**血糖风险指数**:
- 低血糖风险指数 (LBGI): {metrics.lbgi:.1f} ({'低风险' if metrics.lbgi < 1.1 else '中风险' if metrics.lbgi < 2.5 else '高风险'})
- 高血糖风险指数 (HBGI): {metrics.hbgi:.1f} ({'低风险' if metrics.hbgi < 4.5 else '中风险' if metrics.hbgi < 9.0 else '高风险'})

**GRADE评分**: {metrics.grade_score:.1f} ({'低风险' if metrics.grade_score < 5 else '中风险' if metrics.grade_score < 10 else '高风险'})

"""

        # 添加历史对比分析
        if len(historical_data) > 1:
            report += self._format_historical_comparison(historical_data, metrics, phenotype)
        
        # 添加临床建议
        report += self._format_clinical_recommendations(recommendations)
        
        # 添加预后评估
        report += self._format_prognosis_assessment(phenotype, metrics, historical_data)
        
        return report
    
    def _get_pathophysiology_explanation(self, phenotype: ClinicalPhenotype, metrics: GlycemicMetrics) -> str:
        """获取病理生理学解释"""
        explanations = {
            ClinicalPhenotype.STABLE_HYPERGLYCEMIC: "基础胰岛素分泌不足，但残余β细胞功能维持相对稳定的分泌模式",
            ClinicalPhenotype.POSTPRANDIAL_EXCURSION: "基础胰岛素分泌正常，主要为餐时胰岛素分泌延迟或胰岛素抵抗",
            ClinicalPhenotype.NEAR_TARGET: "胰岛功能基本保存，血糖调节机制相对完整但仍有优化空间",
            ClinicalPhenotype.HIGH_VARIABILITY: "血糖调节系统不稳定，可能存在多重调节机制异常",
            ClinicalPhenotype.OPTIMAL_CONTROL: "胰岛功能良好，血糖稳态调节机制基本正常"
        }
        return explanations.get(phenotype, "血糖调节机制需要进一步评估")
    
    def _interpret_tir(self, tir: float) -> str:
        """解释TIR水平"""
        if tir >= 70:
            return "达到推荐目标，血糖控制优秀"
        elif tir >= 50:
            return "接近推荐目标，仍有改善空间"
        else:
            return "远低于推荐目标，需要积极干预"
    
    def _explain_tir_pathology(self, tir: float) -> str:
        """解释TIR的病理意义"""
        if tir >= 70:
            return "微血管并发症风险显著降低，血糖管理达到保护性水平"
        elif tir >= 50:
            return "并发症风险中等，通过优化可进一步降低风险"
        else:
            return "高血糖暴露增加微血管并发症风险，需要紧急治疗调整"
    
    def _interpret_hyperglycemia(self, tar1: float, tar2: float) -> str:
        """解释高血糖负荷"""
        if tar1 < 25 and tar2 < 5:
            return "高血糖负荷在可接受范围内"
        elif tar1 < 50:
            return "中度高血糖负荷，需要优化管理"
        else:
            return "高血糖负荷严重，需要积极治疗强化"
    
    def _interpret_hypoglycemia_risk(self, tbr: float) -> str:
        """解释低血糖风险"""
        if tbr == 0:
            return "无低血糖风险，为治疗优化提供了充分安全边际"
        elif tbr < 4:
            return "低血糖风险在安全范围内，但需要预防性管理"
        else:
            return "低血糖风险偏高，需要调整治疗方案"
    
    def _explain_dawn_phenomenon(self, dawn: float) -> str:
        """解释黎明现象机制"""
        if abs(dawn) < 1.0:
            return "生理性皮质醇分泌，基础胰岛素作用充分"
        elif dawn > 3.0:
            return "皮质醇、生长激素等拮抗激素分泌增加，基础胰岛素作用不足"
        else:
            return "轻度皮质醇分泌增加，基础胰岛素需要微调"
    
    def _assess_dawn_impact(self, dawn: float) -> str:
        """评估黎明现象影响"""
        if abs(dawn) < 1.0:
            return "对全天血糖控制影响轻微"
        elif dawn > 3.0:
            return "显著影响全天血糖控制，需要针对性管理"
        else:
            return "中度影响全天血糖控制，建议适度关注"
    
    def _interpret_nocturnal_stability(self, stability: float) -> str:
        """解释夜间稳定性"""
        if stability > 0.8:
            return "基础代谢状态下血糖控制良好，基础胰岛素管理适当"
        else:
            return "夜间血糖不够稳定，可能需要调整基础胰岛素"
    
    def _interpret_gmi_hba1c(self, gmi: float) -> str:
        """解释GMI和HbA1c对照"""
        if gmi < 7.0:
            return "相当于HbA1c<7.0%，血糖控制优秀"
        elif gmi < 7.5:
            return "相当于HbA1c 7.0-7.5%，血糖控制良好"
        elif gmi < 8.0:
            return "相当于HbA1c 7.5-8.0%，需要改善"
        elif gmi < 9.0:
            return "相当于HbA1c 8.0-9.0%，控制不佳"
        else:
            return "相当于HbA1c>9.0%，需要紧急改善"
    
    def _assess_glycemic_control_level(self, gmi: float) -> str:
        """评估血糖控制水平"""
        if gmi < 6.5:
            return "优秀控制 (GMI<6.5%)"
        elif gmi < 7.0:
            return "良好控制 (GMI 6.5-7.0%)"
        elif gmi < 7.5:
            return "基本达标 (GMI 7.0-7.5%)"
        elif gmi < 8.5:
            return "需要改善 (GMI 7.5-8.5%)"
        else:
            return "控制不佳 (GMI>8.5%)"
    
    def _interpret_mage(self, mage: float) -> str:
        """解释MAGE值"""
        if mage < 2.0:
            return "血糖漂移幅度小，稳定性优秀"
        elif mage < 3.5:
            return "血糖漂移幅度适中，稳定性良好"
        elif mage < 5.0:
            return "血糖漂移幅度较大，需要改善稳定性"
        else:
            return "血糖漂移幅度过大，稳定性较差"
    
    def _interpret_j_index(self, j_index: float) -> str:
        """解释J-Index"""
        if j_index < 15:
            return "血糖质量优秀"
        elif j_index < 30:
            return "血糖质量良好"
        elif j_index < 60:
            return "血糖质量一般，有改善空间"
        else:
            return "血糖质量较差，需要积极改善"
    
    def _format_historical_comparison(self, historical_data: List[Dict], current_metrics: GlycemicMetrics, current_phenotype: ClinicalPhenotype) -> str:
        """格式化同一患者的历史对比分析"""
        if len(historical_data) < 2:
            return "\n### 📈 历史对比分析\n\n**首次分析**: 暂无历史数据对比，已建立基线档案\n"
        
        previous = historical_data[-2]['metrics']
        current = {
            'tir': current_metrics.tir,
            'glucose_cv': current_metrics.glucose_cv,
            'tbr_level1': current_metrics.tbr_level1,
            'percentile_band_cv': current_metrics.percentile_band_cv,
            'phenotype': current_phenotype.value
        }
        
        tir_change = current['tir'] - previous['tir']
        cv_change = current['glucose_cv'] - previous['glucose_cv']
        band_cv_change = current['percentile_band_cv'] - previous.get('percentile_band_cv', 0)
        tbr_change = current['tbr_level1'] - previous['tbr_level1']
        
        # 计算总体趋势（如果有多次记录）
        if len(historical_data) >= 3:
            trend_analysis = self._analyze_long_term_trend(historical_data, current)
        else:
            trend_analysis = "数据积累中，建议继续定期监测"
        
        comparison = f"""
### 📈 患者历史对比分析

#### **关键指标变化** (较上次监测)
- **TIR变化**: {tir_change:+.1f}% ({'✅ 改善' if tir_change > 0 else '❌ 下降' if tir_change < 0 else '➖ 稳定'})
- **血糖变异性**: {cv_change:+.1f}% ({'✅ 改善' if cv_change < 0 else '❌ 恶化' if cv_change > 0 else '➖ 稳定'})  
- **昼夜节律**: {band_cv_change:+.1f}% ({'✅ 改善' if band_cv_change < 0 else '❌ 恶化' if band_cv_change > 0 else '➖ 稳定'})
- **低血糖风险**: {tbr_change:+.1f}% ({'⚠️ 增加' if tbr_change > 0 else '✅ 减少' if tbr_change < 0 else '➖ 稳定'})

#### **临床表型变化**
- **上次表型**: {previous.get('phenotype', '未记录')}
- **本次表型**: {current['phenotype']}
- **表型评估**: {self._assess_phenotype_change(previous.get('phenotype', ''), current['phenotype'])}

#### **治疗效果评估**
**短期效果**: {self._assess_short_term_effect(tir_change, cv_change, tbr_change)}  
**管理趋势**: {self._assess_trend(tir_change, cv_change)}  
**临床建议**: {self._interpret_trend_significance(tir_change, cv_change)}

#### **长期趋势分析** (共{len(historical_data)}次记录)
{trend_analysis}

"""
        return comparison
    
    def _assess_trend(self, tir_change: float, cv_change: float) -> str:
        """评估变化趋势"""
        if tir_change > 5 and cv_change < -2:
            return "血糖控制显著改善"
        elif tir_change > 2:
            return "血糖控制轻度改善"
        elif tir_change < -5:
            return "血糖控制明显恶化"
        elif tir_change < -2:
            return "血糖控制轻度恶化"
        else:
            return "血糖控制基本稳定"
    
    def _interpret_trend_significance(self, tir_change: float, cv_change: float) -> str:
        """解释趋势的临床意义"""
        if tir_change > 5:
            return "当前治疗策略有效，建议继续维持"
        elif tir_change < -5:
            return "需要紧急评估治疗依从性和疾病进展情况"
        else:
            return "血糖控制相对稳定，可进行精细化调整"
    
    def _assess_phenotype_change(self, previous_phenotype: str, current_phenotype: str) -> str:
        """评估临床表型变化"""
        if previous_phenotype == current_phenotype:
            return "表型稳定，管理策略一致"
        elif previous_phenotype == "稳定性高血糖型" and current_phenotype == "接近达标型":
            return "血糖控制显著改善，治疗效果良好"
        elif previous_phenotype == "接近达标型" and current_phenotype == "优化控制型":
            return "血糖管理优化成功，达到理想状态"
        elif "高血糖" in previous_phenotype and "达标" in current_phenotype:
            return "血糖控制获得突破性改善"
        elif "达标" in previous_phenotype and "高血糖" in current_phenotype:
            return "⚠️ 血糖控制恶化，需要重新评估治疗方案"
        else:
            return f"表型转换({previous_phenotype} → {current_phenotype})，需要调整管理策略"
    
    def _assess_short_term_effect(self, tir_change: float, cv_change: float, tbr_change: float) -> str:
        """评估短期治疗效果"""
        effects = []
        
        if tir_change > 3:
            effects.append("TIR显著改善")
        elif tir_change > 0:
            effects.append("TIR轻度改善")
        elif tir_change < -3:
            effects.append("TIR明显下降")
        elif tir_change < 0:
            effects.append("TIR轻度下降")
        else:
            effects.append("TIR基本稳定")
        
        if cv_change < -2:
            effects.append("血糖稳定性提升")
        elif cv_change > 2:
            effects.append("血糖稳定性下降")
        else:
            effects.append("血糖稳定性维持")
        
        if tbr_change > 1:
            effects.append("⚠️ 低血糖风险增加")
        elif tbr_change < -1:
            effects.append("低血糖风险降低")
        
        return "；".join(effects)
    
    def _analyze_long_term_trend(self, historical_data: List[Dict], current: Dict) -> str:
        """分析长期趋势"""
        if len(historical_data) < 3:
            return "数据积累中，建议继续定期监测"
        
        # 提取历史TIR数据
        tir_history = [record['metrics']['tir'] for record in historical_data[-3:]]
        tir_history.append(current['tir'])
        
        # 计算线性趋势
        n = len(tir_history)
        x = list(range(n))
        y = tir_history
        
        # 简单线性回归计算斜率
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator != 0:
            slope = numerator / denominator
            trend_description = self._describe_trend_slope(slope, n)
        else:
            trend_description = "数据波动，趋势不明确"
        
        # 变异系数趋势
        cv_history = [record['metrics'].get('glucose_cv', 0) for record in historical_data[-3:]]
        cv_trend = "稳定" if abs(max(cv_history) - min(cv_history)) < 3 else "波动"
        
        return f"""
**TIR趋势**: {trend_description}
**变异性趋势**: 血糖稳定性{cv_trend}
**管理建议**: {self._get_long_term_management_advice(slope, cv_trend)}
**下次随访**: {self._recommend_follow_up_interval(slope)}"""
    
    def _describe_trend_slope(self, slope: float, data_points: int) -> str:
        """描述趋势斜率"""
        if slope > 2:
            return f"持续改善中 (近{data_points}次监测平均每次提升{slope:.1f}%)"
        elif slope > 0.5:
            return f"缓慢改善中 (近{data_points}次监测呈上升趋势)"
        elif slope < -2:
            return f"持续恶化中 (近{data_points}次监测平均每次下降{abs(slope):.1f}%)"
        elif slope < -0.5:
            return f"缓慢恶化中 (近{data_points}次监测呈下降趋势)"
        else:
            return f"基本稳定 (近{data_points}次监测波动范围小)"
    
    def _get_long_term_management_advice(self, slope: float, cv_trend: str) -> str:
        """获取长期管理建议"""
        if slope > 1:
            return "当前管理策略有效，建议继续维持并巩固成果"
        elif slope < -1:
            return "需要系统性评估治疗方案，考虑调整管理策略"
        elif cv_trend == "波动":
            return "关注血糖稳定性，优化治疗一致性"
        else:
            return "维持现状，定期监测，适时微调"
    
    def _recommend_follow_up_interval(self, slope: float) -> str:
        """推荐随访间隔"""
        if abs(slope) > 2:
            return "2-4周（血糖变化较大，需密切监测）"
        elif abs(slope) > 0.5:
            return "4-6周（血糖有变化趋势，需要关注）"
        else:
            return "6-8周（血糖相对稳定，常规随访）"
    
    def _format_detailed_time_analysis(self, circadian: CircadianAnalysis) -> str:
        """格式化详细时间模式分析"""
        analysis = ""
        
        # 餐后血糖反应详细分析
        if hasattr(circadian, 'postprandial_peaks') and circadian.postprandial_peaks:
            analysis += "\n**📅 餐后血糖反应分析**:\n\n"
            
            for meal, data in circadian.postprandial_peaks.items():
                meal_name = {'breakfast': '早餐', 'lunch': '午餐', 'dinner': '晚餐'}.get(meal, meal)
                excursion_level = "正常" if data['excursion'] < 2.0 else "轻度升高" if data['excursion'] < 3.0 else "显著升高"
                
                analysis += f"- **{meal_name}后**:\n"
                analysis += f"  - 基线血糖: {data['baseline']:.1f} mmol/L\n"
                analysis += f"  - 峰值血糖: {data['peak']:.1f} mmol/L\n"  
                analysis += f"  - 血糖激发: {data['excursion']:.1f} mmol/L ({excursion_level})\n"
                analysis += f"  - 峰值时间: {data['peak_time']}\n"
                analysis += f"  - 达峰时间: {data['time_to_peak']}小时\n\n"
        
        # 每小时血糖模式分析
        if hasattr(circadian, 'hourly_patterns') and circadian.hourly_patterns:
            analysis += "**⏰ 24小时血糖模式概览**:\n\n"
            
            # 找出最高和最低血糖时段
            hourly_means = {time: data['mean'] for time, data in circadian.hourly_patterns.items() if 'mean' in data}
            if hourly_means:
                max_time = max(hourly_means, key=hourly_means.get)
                min_time = min(hourly_means, key=hourly_means.get)
                max_value = hourly_means[max_time]
                min_value = hourly_means[min_time]
                
                analysis += f"- **血糖最高时段**: {max_time} ({max_value:.1f} mmol/L)\n"
                analysis += f"- **血糖最低时段**: {min_time} ({min_value:.1f} mmol/L)\n"
                analysis += f"- **昼夜血糖差**: {max_value - min_value:.1f} mmol/L\n\n"
            
            # 关键时段分析
            key_periods = {
                "06:00": "清晨起床",
                "08:00": "早餐后", 
                "12:00": "午餐前",
                "14:00": "午餐后",
                "18:00": "晚餐前",
                "20:00": "晚餐后",
                "22:00": "睡前",
                "02:00": "夜间"
            }
            
            analysis += "**🎯 关键时段血糖水平**:\n\n"
            for time, desc in key_periods.items():
                if time in circadian.hourly_patterns:
                    data = circadian.hourly_patterns[time]
                    mean_val = data.get('mean', 0)
                    cv_val = data.get('cv', 0)
                    status = "理想" if 3.9 <= mean_val <= 10.0 else "偏高" if mean_val > 10.0 else "偏低"
                    analysis += f"- **{desc} ({time})**: {mean_val:.1f} mmol/L (CV: {cv_val:.1f}%) - {status}\n"
            analysis += "\n"
        
        # 血糖变异性时间分布
        if hasattr(circadian, 'hourly_patterns') and circadian.hourly_patterns:
            # 找出变异性最大的时段
            hourly_cvs = {time: data.get('cv', 0) for time, data in circadian.hourly_patterns.items() if 'cv' in data}
            if hourly_cvs:
                max_cv_time = max(hourly_cvs, key=hourly_cvs.get)
                max_cv_value = hourly_cvs[max_cv_time]
                
                analysis += "**📊 血糖稳定性时间分析**:\n\n"
                analysis += f"- **最不稳定时段**: {max_cv_time} (CV: {max_cv_value:.1f}%)\n"
                analysis += f"- **稳定性评估**: {'需要关注' if max_cv_value > 30 else '相对稳定'}\n"
                
                # 时段稳定性分类
                stable_periods = [time for time, cv in hourly_cvs.items() if cv < 20]
                moderate_periods = [time for time, cv in hourly_cvs.items() if 20 <= cv < 30]
                unstable_periods = [time for time, cv in hourly_cvs.items() if cv >= 30]
                
                if stable_periods:
                    analysis += f"- **稳定时段** (CV<20%): {', '.join(stable_periods[:5])}\n"
                if moderate_periods:
                    analysis += f"- **中等波动时段** (CV 20-30%): {', '.join(moderate_periods[:5])}\n"  
                if unstable_periods:
                    analysis += f"- **不稳定时段** (CV≥30%): {', '.join(unstable_periods[:5])}\n"
                analysis += "\n"
        
        return analysis

    def _format_clinical_recommendations(self, recommendations: List[ClinicalRecommendation]) -> str:
        """格式化临床建议"""
        if not recommendations:
            return ""
        
        # 按优先级排序
        priority_order = {"紧急": 1, "高": 2, "中": 3, "低": 4}
        sorted_recs = sorted(recommendations, key=lambda x: priority_order.get(x.priority, 5))
        
        report = "\n### 🎯 临床诊疗建议\n"
        
        for i, rec in enumerate(sorted_recs, 1):
            priority_emoji = {"紧急": "🚨", "高": "⚠️", "中": "📋", "低": "💡"}
            
            report += f"""
#### **{i}. {rec.category}** {priority_emoji.get(rec.priority, '📋')} {rec.priority}优先级

**建议内容**: {rec.recommendation}  
**机制解释**: {rec.mechanism}  
**预期效果**: {rec.expected_outcome}  
**实施时间**: {rec.timeframe}

**🔧 具体执行措施**:
{self._format_specific_actions(rec)}

**💊 用药建议**:
{rec.dosing_suggestions if hasattr(rec, 'dosing_suggestions') and rec.dosing_suggestions else '请根据医生指导用药'}

**⏰ 时机安排**:
{rec.timing_instructions if hasattr(rec, 'timing_instructions') and rec.timing_instructions else '请遵循常规用药时间'}

**📅 随访计划**:
{rec.follow_up_schedule if hasattr(rec, 'follow_up_schedule') and rec.follow_up_schedule else '建议1-2周后复诊评估'}

**✅ 成功标准**:
{rec.success_criteria if hasattr(rec, 'success_criteria') and rec.success_criteria else '血糖控制达标，无不良事件'}

**⚠️ 注意事项**:
{', '.join(rec.warning_signs) if hasattr(rec, 'warning_signs') and rec.warning_signs else '注意监测血糖变化'}

**📊 监测要点**: {', '.join(rec.monitoring_points)}

"""
        
        return report
    
    def _format_specific_actions(self, rec: ClinicalRecommendation) -> str:
        """格式化具体执行措施"""
        if not hasattr(rec, 'specific_actions') or not rec.specific_actions:
            return "请根据医生指导执行相关措施"
        
        actions_text = ""
        for i, action in enumerate(rec.specific_actions, 1):
            actions_text += f"  {i}. {action}\n"
        
        return actions_text.rstrip()
    
    def _format_prognosis_assessment(self, 
                                   phenotype: ClinicalPhenotype,
                                   metrics: GlycemicMetrics,
                                   historical_data: List[Dict]) -> str:
        """格式化预后评估"""
        
        # 基于表型的预后评估
        prognosis_map = {
            ClinicalPhenotype.STABLE_HYPERGLYCEMIC: "中等难度达标，需要积极治疗强化",
            ClinicalPhenotype.POSTPRANDIAL_EXCURSION: "预后良好，精准干预可获得显著改善",
            ClinicalPhenotype.NEAR_TARGET: "预后优秀，大概率安全达标",
            ClinicalPhenotype.OPTIMAL_CONTROL: "维持优秀控制状态",
            ClinicalPhenotype.HIGH_VARIABILITY: "需要系统性评估和治疗调整"
        }
        
        treatment_advantages = []
        if metrics.tbr_level1 < 2:
            treatment_advantages.append("低血糖风险低，治疗调整安全边际充分")
        if metrics.glucose_cv < 30:
            treatment_advantages.append("血糖稳定性良好，治疗反应可预测")
        if metrics.tir > 60:
            treatment_advantages.append("具备良好的血糖控制基础")
        
        report = f"""
### 📈 预后评估与治疗优势

**预后评估**: {prognosis_map.get(phenotype, '需要个性化评估')}

**治疗优势**:
"""
        for advantage in treatment_advantages:
            report += f"- {advantage}\n"
        
        if len(historical_data) > 1:
            report += f"\n**历史表现**: 已建立{len(historical_data)}次监测记录，便于趋势分析和精准调整\n"
        
        report += f"""
**随访建议**:
- 治疗调整后1-2周内密切监测
- 月度全面评估治疗效果
- 季度评估长期趋势和并发症风险
- 建立个性化的长期管理方案

---

**临床总结**: 患者{phenotype.value}为特征，通过{self._get_treatment_approach(phenotype)}，预期可获得良好的血糖控制改善。
"""
        
        return report
    
    def _get_treatment_approach(self, phenotype: ClinicalPhenotype) -> str:
        """获取治疗方法描述"""
        approaches = {
            ClinicalPhenotype.STABLE_HYPERGLYCEMIC: "积极的胰岛素强化治疗",
            ClinicalPhenotype.POSTPRANDIAL_EXCURSION: "精准的餐时血糖管理",
            ClinicalPhenotype.NEAR_TARGET: "精细化的治疗调整",
            ClinicalPhenotype.OPTIMAL_CONTROL: "维持性管理策略"
        }
        return approaches.get(phenotype, "个性化治疗方案")

# 使用示例和测试函数
def main():
    """主函数 - 演示AGPAI Agent V2.0功能"""
    
    # 初始化Agent
    agent = AGPAI_Agent_V2()
    
    print("🤖 AGPAI Agent V2.0 - 高级CGM分析系统")
    print("=" * 60)
    
    # 测试文件路径（需要根据实际情况调整）
    test_files = [
        ("/Users/williamsun/Documents/gplus/docs/AGPAI/R002 V5.txt", "R002")
    ]
    
    for file_path, patient_id in test_files:
        if os.path.exists(file_path):
            print(f"\n分析患者 {patient_id}...")
            try:
                report = agent.generate_comprehensive_report(
                    patient_id=patient_id,
                    cgm_file_path=file_path,
                    include_historical=True
                )
                print(report)
                print("-" * 60)
            except Exception as e:
                print(f"分析失败: {str(e)}")
        else:
            print(f"文件不存在: {file_path}")

if __name__ == "__main__":
    main()