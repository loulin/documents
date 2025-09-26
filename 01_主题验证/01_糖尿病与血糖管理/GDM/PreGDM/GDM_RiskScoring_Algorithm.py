#!/usr/bin/env python3
"""
GDM风险评分算法实现
基于多维度评估的妊娠糖尿病风险预测模型
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import math
import json

class GDM_RiskScoringAlgorithm:
    """GDM风险评分算法主类"""
    
    def __init__(self):
        """初始化风险评分系统"""
        
        # 风险因子权重配置
        self.risk_weights = {
            'demographic': {
                'age': 0.15,           # 年龄
                'ethnicity': 0.08,     # 种族
                'socioeconomic': 0.03  # 社会经济状态
            },
            'anthropometric': {
                'pre_pregnancy_bmi': 0.20,     # 孕前BMI
                'weight_gain': 0.10,           # 孕期体重增长
                'body_composition': 0.05       # 体成分
            },
            'obstetric_history': {
                'previous_gdm': 0.25,          # 既往GDM史
                'macrosomia_history': 0.15,    # 巨大儿史
                'pregnancy_loss': 0.08,        # 妊娠丢失史
                'parity': 0.05                 # 产次
            },
            'family_history': {
                'diabetes_family': 0.18,       # 糖尿病家族史
                'gdm_family': 0.12             # GDM家族史
            },
            'medical_history': {
                'pcos': 0.15,                  # 多囊卵巢综合征
                'metabolic_syndrome': 0.18,    # 代谢综合征
                'hypertension': 0.10,          # 高血压
                'cardiovascular': 0.08         # 心血管疾病
            },
            'biochemical': {
                'fasting_glucose': 0.25,       # 空腹血糖
                'hba1c': 0.20,                # 糖化血红蛋白
                'insulin_resistance': 0.18,    # 胰岛素抵抗
                'lipid_profile': 0.08,         # 血脂谱
                'inflammatory_markers': 0.06   # 炎症标志物
            },
            'lifestyle': {
                'physical_activity': 0.12,     # 体力活动
                'diet_quality': 0.10,          # 饮食质量
                'smoking': 0.08,               # 吸烟史
                'sleep_quality': 0.05          # 睡眠质量
            },
            'current_pregnancy': {
                'gestational_age': 0.10,       # 孕周
                'multiple_pregnancy': 0.15,    # 多胎妊娠
                'fetal_growth': 0.12,          # 胎儿生长
                'pregnancy_complications': 0.08 # 妊娠并发症
            }
        }
        
        # 风险分层阈值
        self.risk_thresholds = {
            'low': (0, 25),
            'moderate': (26, 45),
            'high': (46, 65),
            'very_high': (66, 100)
        }
        
        # 诊断标准和参考值
        self.reference_values = {
            'glucose': {
                'fasting_normal': 5.1,        # mmol/L
                'fasting_impaired': 5.6,
                'random_normal': 7.8,
                'ogtt_1h': 10.0,
                'ogtt_2h': 8.5
            },
            'hba1c': {
                'normal': 5.7,                # %
                'prediabetes': 6.0,
                'diabetes': 6.5
            },
            'insulin': {
                'normal_range': (2.6, 24.9),  # mIU/L
                'resistance_threshold': 15.0
            },
            'bmi': {
                'normal': (18.5, 24.9),
                'overweight': (25.0, 29.9),
                'obese': (30.0, 34.9),
                'severely_obese': (35.0, float('inf'))
            }
        }
    
    def calculate_comprehensive_risk(self, patient_data: Dict) -> Dict:
        """
        计算综合GDM风险评分
        
        Args:
            patient_data: 患者完整数据字典
            
        Returns:
            风险评估结果字典
        """
        
        print(f"🔍 开始GDM综合风险评估...")
        print(f"患者ID: {patient_data.get('patient_id', 'Unknown')}")
        
        # 各维度风险评分
        dimension_scores = {}
        
        # 1. 人口学特征评分
        dimension_scores['demographic'] = self._score_demographic_factors(
            patient_data.get('demographic', {})
        )
        
        # 2. 体格测量评分
        dimension_scores['anthropometric'] = self._score_anthropometric_factors(
            patient_data.get('anthropometric', {})
        )
        
        # 3. 产科史评分
        dimension_scores['obstetric_history'] = self._score_obstetric_history(
            patient_data.get('obstetric_history', {})
        )
        
        # 4. 家族史评分
        dimension_scores['family_history'] = self._score_family_history(
            patient_data.get('family_history', {})
        )
        
        # 5. 既往病史评分
        dimension_scores['medical_history'] = self._score_medical_history(
            patient_data.get('medical_history', {})
        )
        
        # 6. 生化指标评分
        dimension_scores['biochemical'] = self._score_biochemical_markers(
            patient_data.get('biochemical', {})
        )
        
        # 7. 生活方式评分
        dimension_scores['lifestyle'] = self._score_lifestyle_factors(
            patient_data.get('lifestyle', {})
        )
        
        # 8. 当前妊娠评分
        dimension_scores['current_pregnancy'] = self._score_current_pregnancy(
            patient_data.get('current_pregnancy', {})
        )
        
        # 计算加权总分
        total_score = self._calculate_weighted_total_score(dimension_scores)
        
        # 风险分层
        risk_level = self._classify_risk_level(total_score)
        
        # 时间风险预测
        time_based_risks = self._calculate_time_based_risks(total_score, patient_data)
        
        # 生成风险报告
        risk_report = self._generate_risk_report(
            dimension_scores, total_score, risk_level, time_based_risks, patient_data
        )
        
        return {
            'patient_id': patient_data.get('patient_id'),
            'assessment_date': datetime.now().isoformat(),
            'total_score': total_score,
            'risk_level': risk_level,
            'dimension_scores': dimension_scores,
            'time_based_risks': time_based_risks,
            'recommendations': self._generate_recommendations(risk_level, dimension_scores),
            'follow_up_schedule': self._create_follow_up_schedule(risk_level, patient_data),
            'risk_report': risk_report
        }
    
    def _score_demographic_factors(self, demographic: Dict) -> Dict:
        """评分人口学因素"""
        
        scores = {}
        
        # 年龄评分
        age = demographic.get('age', 25)
        if age < 25:
            scores['age'] = 0
        elif age < 30:
            scores['age'] = 5
        elif age < 35:
            scores['age'] = 10
        elif age < 40:
            scores['age'] = 15
        else:
            scores['age'] = 20
        
        # 种族评分
        ethnicity = demographic.get('ethnicity', 'other')
        high_risk_ethnicities = ['asian', 'hispanic', 'african_american', 'native_american']
        scores['ethnicity'] = 10 if ethnicity in high_risk_ethnicities else 0
        
        # 社会经济状态
        socioeconomic_status = demographic.get('socioeconomic_status', 'middle')
        scores['socioeconomic'] = 5 if socioeconomic_status == 'low' else 0
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 35,
            'percentage': sum(scores.values()) / 35 * 100
        }
    
    def _score_anthropometric_factors(self, anthropometric: Dict) -> Dict:
        """评分体格测量因素"""
        
        scores = {}
        
        # 孕前BMI评分
        pre_pregnancy_bmi = anthropometric.get('pre_pregnancy_bmi', 22)
        if pre_pregnancy_bmi < 18.5:
            scores['pre_pregnancy_bmi'] = 2  # 低体重也有风险
        elif pre_pregnancy_bmi < 25:
            scores['pre_pregnancy_bmi'] = 0
        elif pre_pregnancy_bmi < 30:
            scores['pre_pregnancy_bmi'] = 10
        elif pre_pregnancy_bmi < 35:
            scores['pre_pregnancy_bmi'] = 20
        else:
            scores['pre_pregnancy_bmi'] = 25
        
        # 孕期体重增长评分
        weight_gain = anthropometric.get('gestational_weight_gain', 0)
        expected_gain = self._calculate_expected_weight_gain(
            pre_pregnancy_bmi, 
            anthropometric.get('gestational_weeks', 20)
        )
        
        gain_ratio = weight_gain / expected_gain if expected_gain > 0 else 0
        if gain_ratio < 0.8:
            scores['weight_gain'] = 2  # 增重不足
        elif gain_ratio <= 1.2:
            scores['weight_gain'] = 0  # 正常增重
        elif gain_ratio <= 1.5:
            scores['weight_gain'] = 8  # 增重过多
        else:
            scores['weight_gain'] = 15  # 严重增重过多
        
        # 体成分评分（腰围、腰臀比等）
        waist_circumference = anthropometric.get('waist_circumference', 80)
        scores['body_composition'] = 5 if waist_circumference > 88 else 0  # 女性腰围>88cm
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 45,
            'percentage': sum(scores.values()) / 45 * 100
        }
    
    def _score_obstetric_history(self, obstetric: Dict) -> Dict:
        """评分产科史"""
        
        scores = {}
        
        # 既往GDM史 - 最重要的风险因素
        previous_gdm = obstetric.get('previous_gdm', False)
        scores['previous_gdm'] = 25 if previous_gdm else 0
        
        # 巨大儿史
        macrosomia_history = obstetric.get('macrosomia_history', False)
        scores['macrosomia_history'] = 15 if macrosomia_history else 0
        
        # 妊娠丢失史
        pregnancy_losses = obstetric.get('pregnancy_losses', 0)
        if pregnancy_losses >= 3:
            scores['pregnancy_loss'] = 10
        elif pregnancy_losses >= 1:
            scores['pregnancy_loss'] = 5
        else:
            scores['pregnancy_loss'] = 0
        
        # 产次
        parity = obstetric.get('parity', 0)
        scores['parity'] = 5 if parity >= 4 else 0  # 经产妇风险
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 55,
            'percentage': sum(scores.values()) / 55 * 100
        }
    
    def _score_family_history(self, family: Dict) -> Dict:
        """评分家族史"""
        
        scores = {}
        
        # 糖尿病家族史
        diabetes_family = family.get('diabetes_family_history', 'none')
        if diabetes_family == 'first_degree':
            scores['diabetes_family'] = 20
        elif diabetes_family == 'second_degree':
            scores['diabetes_family'] = 10
        else:
            scores['diabetes_family'] = 0
        
        # GDM家族史
        gdm_family = family.get('gdm_family_history', False)
        scores['gdm_family'] = 15 if gdm_family else 0
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 35,
            'percentage': sum(scores.values()) / 35 * 100
        }
    
    def _score_medical_history(self, medical: Dict) -> Dict:
        """评分既往病史"""
        
        scores = {}
        
        # PCOS
        pcos = medical.get('pcos', False)
        scores['pcos'] = 15 if pcos else 0
        
        # 代谢综合征
        metabolic_syndrome = medical.get('metabolic_syndrome', False)
        scores['metabolic_syndrome'] = 20 if metabolic_syndrome else 0
        
        # 高血压
        hypertension = medical.get('hypertension', False)
        scores['hypertension'] = 10 if hypertension else 0
        
        # 心血管疾病
        cardiovascular = medical.get('cardiovascular_disease', False)
        scores['cardiovascular'] = 10 if cardiovascular else 0
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 55,
            'percentage': sum(scores.values()) / 55 * 100
        }
    
    def _score_biochemical_markers(self, biochemical: Dict) -> Dict:
        """评分生化指标"""
        
        scores = {}
        
        # 空腹血糖评分
        fasting_glucose = biochemical.get('fasting_glucose', 4.5)  # mmol/L
        if fasting_glucose >= 7.0:
            scores['fasting_glucose'] = 25  # 糖尿病范围
        elif fasting_glucose >= 6.1:
            scores['fasting_glucose'] = 20  # 空腹血糖受损
        elif fasting_glucose >= 5.6:
            scores['fasting_glucose'] = 15  # 空腹血糖异常
        elif fasting_glucose >= 5.1:
            scores['fasting_glucose'] = 10  # GDM诊断阈值
        else:
            scores['fasting_glucose'] = 0
        
        # HbA1c评分
        hba1c = biochemical.get('hba1c', 5.0)  # %
        if hba1c >= 6.5:
            scores['hba1c'] = 25
        elif hba1c >= 6.0:
            scores['hba1c'] = 20
        elif hba1c >= 5.7:
            scores['hba1c'] = 15
        else:
            scores['hba1c'] = 0
        
        # 胰岛素抵抗评分
        homa_ir = biochemical.get('homa_ir', 1.0)
        if homa_ir >= 3.5:
            scores['insulin_resistance'] = 20
        elif homa_ir >= 2.5:
            scores['insulin_resistance'] = 15
        elif homa_ir >= 2.0:
            scores['insulin_resistance'] = 10
        else:
            scores['insulin_resistance'] = 0
        
        # 血脂谱评分
        triglycerides = biochemical.get('triglycerides', 1.0)  # mmol/L
        hdl = biochemical.get('hdl_cholesterol', 1.5)  # mmol/L
        
        lipid_score = 0
        if triglycerides >= 2.3:
            lipid_score += 5
        if hdl < 1.3:  # 女性
            lipid_score += 5
        scores['lipid_profile'] = lipid_score
        
        # 炎症标志物
        crp = biochemical.get('crp', 1.0)  # mg/L
        scores['inflammatory_markers'] = 5 if crp >= 3.0 else 0
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 85,
            'percentage': sum(scores.values()) / 85 * 100
        }
    
    def _score_lifestyle_factors(self, lifestyle: Dict) -> Dict:
        """评分生活方式因素"""
        
        scores = {}
        
        # 体力活动评分
        physical_activity = lifestyle.get('physical_activity', 'moderate')
        activity_mapping = {
            'sedentary': 15,
            'low': 10,
            'moderate': 5,
            'high': 0
        }
        scores['physical_activity'] = activity_mapping.get(physical_activity, 5)
        
        # 饮食质量评分
        diet_quality = lifestyle.get('diet_quality', 'average')
        diet_mapping = {
            'poor': 10,
            'average': 5,
            'good': 0,
            'excellent': 0
        }
        scores['diet_quality'] = diet_mapping.get(diet_quality, 5)
        
        # 吸烟史评分
        smoking_status = lifestyle.get('smoking_status', 'never')
        if smoking_status in ['current', 'recent']:
            scores['smoking'] = 10
        elif smoking_status == 'former':
            scores['smoking'] = 5
        else:
            scores['smoking'] = 0
        
        # 睡眠质量评分
        sleep_hours = lifestyle.get('sleep_hours_per_night', 7)
        if sleep_hours < 6 or sleep_hours > 9:
            scores['sleep_quality'] = 5
        else:
            scores['sleep_quality'] = 0
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 40,
            'percentage': sum(scores.values()) / 40 * 100
        }
    
    def _score_current_pregnancy(self, pregnancy: Dict) -> Dict:
        """评分当前妊娠因素"""
        
        scores = {}
        
        # 孕周评分
        gestational_weeks = pregnancy.get('gestational_weeks', 20)
        if gestational_weeks >= 24:  # 胰岛素抵抗高峰期
            scores['gestational_age'] = 10
        elif gestational_weeks >= 20:
            scores['gestational_age'] = 5
        else:
            scores['gestational_age'] = 0
        
        # 多胎妊娠
        multiple_pregnancy = pregnancy.get('multiple_pregnancy', False)
        scores['multiple_pregnancy'] = 15 if multiple_pregnancy else 0
        
        # 胎儿生长评估
        estimated_fetal_weight_percentile = pregnancy.get('estimated_fetal_weight_percentile', 50)
        if estimated_fetal_weight_percentile >= 90:
            scores['fetal_growth'] = 15
        elif estimated_fetal_weight_percentile >= 75:
            scores['fetal_growth'] = 10
        else:
            scores['fetal_growth'] = 0
        
        # 妊娠并发症
        complications = pregnancy.get('pregnancy_complications', [])
        complication_score = 0
        high_risk_complications = ['hypertension', 'preeclampsia', 'polyhydramnios']
        for complication in complications:
            if complication in high_risk_complications:
                complication_score += 5
        scores['pregnancy_complications'] = min(complication_score, 15)
        
        return {
            'scores': scores,
            'total': sum(scores.values()),
            'max_possible': 55,
            'percentage': sum(scores.values()) / 55 * 100
        }
    
    def _calculate_weighted_total_score(self, dimension_scores: Dict) -> float:
        """计算加权总分"""
        
        total_weighted_score = 0
        
        for dimension, scores in dimension_scores.items():
            if dimension in self.risk_weights:
                dimension_weight = sum(self.risk_weights[dimension].values())
                dimension_percentage = scores['percentage']
                weighted_contribution = dimension_percentage * dimension_weight
                total_weighted_score += weighted_contribution
        
        return min(100, total_weighted_score)  # 确保不超过100分
    
    def _classify_risk_level(self, total_score: float) -> str:
        """分类风险等级"""
        
        for risk_level, (min_score, max_score) in self.risk_thresholds.items():
            if min_score <= total_score <= max_score:
                return risk_level
        
        return 'very_high'  # 默认最高风险
    
    def _calculate_time_based_risks(self, total_score: float, patient_data: Dict) -> Dict:
        """计算基于时间的风险预测"""
        
        # 基础风险概率（基于评分）
        base_risk = min(total_score / 100, 0.8)  # 最高80%风险
        
        # 孕周调整因子
        gestational_weeks = patient_data.get('current_pregnancy', {}).get('gestational_weeks', 20)
        
        if gestational_weeks < 20:
            week_factor = 0.5  # 早孕期风险较低
        elif gestational_weeks < 28:
            week_factor = 1.0  # 中孕期标准风险
        else:
            week_factor = 1.5  # 晚孕期风险增加
        
        adjusted_risk = min(base_risk * week_factor, 0.9)
        
        # 时间窗口风险预测
        time_risks = {
            'current_pregnancy': {
                'probability': adjusted_risk,
                'confidence_interval': (max(0, adjusted_risk - 0.1), min(1, adjusted_risk + 0.1))
            },
            'next_pregnancy': {
                'probability': max(0.1, adjusted_risk * 0.7),  # 下次妊娠风险
                'confidence_interval': (max(0, adjusted_risk * 0.6), min(1, adjusted_risk * 0.8))
            },
            'long_term_t2dm': {
                'probability': max(0.05, adjusted_risk * 0.4),  # 远期2型糖尿病风险
                'confidence_interval': (max(0, adjusted_risk * 0.3), min(1, adjusted_risk * 0.5))
            }
        }
        
        return time_risks
    
    def _calculate_expected_weight_gain(self, pre_pregnancy_bmi: float, gestational_weeks: int) -> float:
        """计算预期体重增长"""
        
        # IOM推荐的孕期体重增长指南
        if pre_pregnancy_bmi < 18.5:
            total_gain = 16  # kg
        elif pre_pregnancy_bmi < 25:
            total_gain = 13
        elif pre_pregnancy_bmi < 30:
            total_gain = 9
        else:
            total_gain = 7
        
        # 按孕周分配
        if gestational_weeks <= 13:
            return total_gain * 0.1  # 早孕期增重较少
        elif gestational_weeks <= 27:
            return total_gain * 0.4  # 中孕期
        else:
            return total_gain * (gestational_weeks - 13) / 27  # 线性增长
    
    def _generate_recommendations(self, risk_level: str, dimension_scores: Dict) -> List[str]:
        """生成风险管理建议"""
        
        recommendations = []
        
        # 基于风险等级的基础建议
        if risk_level == 'very_high':
            recommendations.extend([
                "立即转诊内分泌科专家评估",
                "孕早期开始血糖监测",
                "考虑CGM连续血糖监测",
                "营养师制定个体化饮食方案",
                "每1-2周专科随访"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "内分泌科会诊评估",
                "提前至孕16-20周进行OGTT筛查",
                "强化生活方式干预",
                "营养师指导",
                "每2-3周随访"
            ])
        elif risk_level == 'moderate':
            recommendations.extend([
                "标准孕24-28周OGTT筛查",
                "生活方式指导",
                "控制体重增长",
                "每月随访评估"
            ])
        else:  # low risk
            recommendations.extend([
                "维持健康生活方式",
                "按时产检",
                "标准孕期筛查"
            ])
        
        # 基于具体风险因素的针对性建议
        for dimension, scores in dimension_scores.items():
            if scores['percentage'] > 50:  # 该维度风险较高
                recommendations.extend(self._get_dimension_specific_recommendations(dimension, scores))
        
        return list(set(recommendations))  # 去重
    
    def _get_dimension_specific_recommendations(self, dimension: str, scores: Dict) -> List[str]:
        """获取特定维度的建议"""
        
        recommendations = []
        
        if dimension == 'anthropometric':
            recommendations.extend([
                "严格控制孕期体重增长",
                "营养师制定低血糖指数饮食方案",
                "每周监测体重变化"
            ])
        elif dimension == 'biochemical':
            recommendations.extend([
                "定期监测血糖和HbA1c",
                "评估胰岛素抵抗状态",
                "监测血脂和炎症指标"
            ])
        elif dimension == 'lifestyle':
            recommendations.extend([
                "制定孕期运动计划",
                "改善饮食结构",
                "戒烟和改善睡眠质量"
            ])
        elif dimension == 'obstetric_history':
            recommendations.extend([
                "密切监测胎儿生长发育",
                "加强产前检查频次",
                "准备应对妊娠并发症"
            ])
        
        return recommendations
    
    def _create_follow_up_schedule(self, risk_level: str, patient_data: Dict) -> Dict:
        """创建随访计划"""
        
        gestational_weeks = patient_data.get('current_pregnancy', {}).get('gestational_weeks', 20)
        
        schedule = {
            'initial_assessment': {
                'timing': 'immediate',
                'tests': ['OGTT', 'HbA1c', 'lipid_profile']
            }
        }
        
        if risk_level in ['high', 'very_high']:
            schedule['frequent_monitoring'] = {
                'frequency': '1-2 weeks',
                'tests': ['fasting_glucose', 'weight', 'blood_pressure'],
                'until': 'delivery'
            }
            
            if gestational_weeks < 20:
                schedule['early_screening'] = {
                    'timing': '16-20 weeks',
                    'tests': ['OGTT', 'HbA1c']
                }
        else:
            schedule['standard_monitoring'] = {
                'frequency': '4 weeks',
                'tests': ['routine_prenatal'],
                'until': 'delivery'
            }
        
        schedule['standard_screening'] = {
            'timing': '24-28 weeks',
            'tests': ['OGTT']
        }
        
        schedule['postpartum_follow_up'] = {
            'timing': '6-12 weeks postpartum',
            'tests': ['OGTT', 'HbA1c'],
            'annual_screening': True
        }
        
        return schedule
    
    def _generate_risk_report(self, dimension_scores: Dict, total_score: float, 
                             risk_level: str, time_based_risks: Dict, patient_data: Dict) -> str:
        """生成风险评估报告"""
        
        patient_id = patient_data.get('patient_id', 'Unknown')
        gestational_weeks = patient_data.get('current_pregnancy', {}).get('gestational_weeks', 'Unknown')
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        GDM风险评估报告                                        ║
║                   Gestational Diabetes Risk Assessment                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

👤 患者信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   患者ID: {patient_id}
   评估日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   孕周: {gestational_weeks} 周

🎯 风险评估结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   综合风险评分: {total_score:.1f}/100
   风险等级: {risk_level.upper()}
   
   当前妊娠GDM风险: {time_based_risks['current_pregnancy']['probability']*100:.1f}%
   下次妊娠风险: {time_based_risks['next_pregnancy']['probability']*100:.1f}%
   远期T2DM风险: {time_based_risks['long_term_t2dm']['probability']*100:.1f}%

📊 各维度风险分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        dimension_names = {
            'demographic': '人口学特征',
            'anthropometric': '体格测量',
            'obstetric_history': '产科史',
            'family_history': '家族史',
            'medical_history': '既往病史',
            'biochemical': '生化指标',
            'lifestyle': '生活方式',
            'current_pregnancy': '当前妊娠'
        }
        
        for dimension, scores in dimension_scores.items():
            name = dimension_names.get(dimension, dimension)
            percentage = scores['percentage']
            risk_indicator = '🔴' if percentage > 60 else '🟡' if percentage > 30 else '🟢'
            report += f"\n   {risk_indicator} {name}: {percentage:.1f}% ({scores['total']}/{scores['max_possible']})"
        
        report += f"""

⚠️  主要风险因素
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        # 识别主要风险因素
        high_risk_dimensions = [
            (dimension_names.get(dim, dim), scores['percentage'])
            for dim, scores in dimension_scores.items()
            if scores['percentage'] > 40
        ]
        
        high_risk_dimensions.sort(key=lambda x: x[1], reverse=True)
        
        for i, (dim_name, percentage) in enumerate(high_risk_dimensions[:5], 1):
            report += f"\n   {i}. {dim_name} (风险度: {percentage:.1f}%)"
        
        if not high_risk_dimensions:
            report += "\n   未发现显著风险因素"
        
        report += f"""

💡 管理建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        recommendations = self._generate_recommendations(risk_level, dimension_scores)
        for i, rec in enumerate(recommendations[:8], 1):  # 限制显示数量
            report += f"\n   {i}. {rec}"
        
        report += f"""

📅 随访计划
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   下次评估: {self._get_next_assessment_timing(risk_level)}
   筛查频率: {self._get_screening_frequency(risk_level)}
   专科随访: {self._get_specialist_follow_up(risk_level)}

⚡ 预警阈值
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   空腹血糖 ≥ 5.1 mmol/L: 立即就诊
   随机血糖 ≥ 11.1 mmol/L: 急诊评估
   体重增长过快 > 0.5kg/周: 营养咨询
   胎动异常: 立即产科检查

📋 备注
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • 本评估基于当前最佳证据和临床指南
   • 需要结合临床判断和其他检查结果
   • 建议与产科和内分泌科医生讨论
   • 风险评估应定期更新

报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本: GDM Risk Assessment v2.0
"""
        
        return report
    
    def _get_next_assessment_timing(self, risk_level: str) -> str:
        """获取下次评估时间"""
        timing_map = {
            'low': '4周后',
            'moderate': '2-3周后',
            'high': '1-2周后',
            'very_high': '1周内'
        }
        return timing_map.get(risk_level, '2周后')
    
    def _get_screening_frequency(self, risk_level: str) -> str:
        """获取筛查频率"""
        frequency_map = {
            'low': '标准产检',
            'moderate': '每月血糖检查',
            'high': '每2周血糖监测',
            'very_high': '每周血糖监测'
        }
        return frequency_map.get(risk_level, '每月')
    
    def _get_specialist_follow_up(self, risk_level: str) -> str:
        """获取专科随访建议"""
        specialist_map = {
            'low': '如有需要',
            'moderate': '内分泌科会诊',
            'high': '内分泌科定期随访',
            'very_high': '多学科团队管理'
        }
        return specialist_map.get(risk_level, '待定')

# 数据示例和使用演示
def create_sample_patient_data():
    """创建示例患者数据"""
    
    return {
        'patient_id': 'GDM_2024_001',
        'demographic': {
            'age': 32,
            'ethnicity': 'asian',
            'socioeconomic_status': 'middle'
        },
        'anthropometric': {
            'pre_pregnancy_bmi': 28.5,
            'gestational_weight_gain': 8.0,
            'gestational_weeks': 24,
            'waist_circumference': 92
        },
        'obstetric_history': {
            'previous_gdm': False,
            'macrosomia_history': True,
            'pregnancy_losses': 1,
            'parity': 1
        },
        'family_history': {
            'diabetes_family_history': 'first_degree',
            'gdm_family_history': True
        },
        'medical_history': {
            'pcos': True,
            'metabolic_syndrome': False,
            'hypertension': False,
            'cardiovascular_disease': False
        },
        'biochemical': {
            'fasting_glucose': 5.3,  # mmol/L
            'hba1c': 5.8,           # %
            'homa_ir': 3.2,
            'triglycerides': 2.1,    # mmol/L
            'hdl_cholesterol': 1.2,  # mmol/L
            'crp': 3.5               # mg/L
        },
        'lifestyle': {
            'physical_activity': 'low',
            'diet_quality': 'average',
            'smoking_status': 'never',
            'sleep_hours_per_night': 6.5
        },
        'current_pregnancy': {
            'gestational_weeks': 24,
            'multiple_pregnancy': False,
            'estimated_fetal_weight_percentile': 85,
            'pregnancy_complications': ['hypertension']
        }
    }

# 主函数
if __name__ == "__main__":
    print("🚀 启动GDM风险评分算法")
    print("=" * 80)
    
    # 创建风险评分器
    risk_scorer = GDM_RiskScoringAlgorithm()
    
    # 使用示例数据进行评估
    sample_patient = create_sample_patient_data()
    
    print(f"📋 评估患者: {sample_patient['patient_id']}")
    print(f"孕周: {sample_patient['current_pregnancy']['gestational_weeks']} 周")
    
    # 执行风险评估
    risk_result = risk_scorer.calculate_comprehensive_risk(sample_patient)
    
    # 显示评估结果
    print(f"\n{risk_result['risk_report']}")
    
    # 输出结构化结果
    print(f"\n📈 结构化评估结果:")
    print(f"   总分: {risk_result['total_score']:.1f}/100")
    print(f"   风险等级: {risk_result['risk_level']}")
    print(f"   当前妊娠GDM风险: {risk_result['time_based_risks']['current_pregnancy']['probability']*100:.1f}%")
    
    # 保存结果到JSON
    output_file = f"/Users/williamsun/Documents/gplus/docs/GDM/PreGDM/gdm_risk_assessment_{sample_patient['patient_id']}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(risk_result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 评估结果已保存至: {output_file}")
    print(f"✅ GDM风险评分算法演示完成")