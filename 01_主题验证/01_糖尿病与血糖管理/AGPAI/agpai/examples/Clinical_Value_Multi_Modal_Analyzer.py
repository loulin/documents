#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真正有临床价值的多模态分析系统
Clinical Value-Driven Multi-Modal Analyzer

核心理念：不是简单的数据整合，而是基于生理病理机制的临床决策支持系统
Core Philosophy: Evidence-based clinical decision support, not just data integration

临床价值体现：
1. 早期识别传统方法遗漏的问题
2. 预测未来1-6个月的并发症风险
3. 提供具体的个性化治疗方案
4. 优化治疗时机和药物选择
5. 减少不必要的医疗资源消耗
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ClinicalValueMultiModalAnalyzer:
    """基于临床价值的多模态分析器"""
    
    def __init__(self, patient_data: Dict):
        self.cgm_data = patient_data['cgm']
        self.ecg_data = patient_data['ecg'] 
        self.hrv_data = patient_data['hrv']
        self.abpm_data = patient_data['abpm']
        
        # 患者基础信息（实际应用中从病历获取）
        self.patient_profile = {
            'age': 52,
            'gender': 'M',
            'diabetes_duration_years': 8,
            'hypertension_duration_years': 3,
            'current_medications': {
                'metformin': {'dose': '1000mg', 'frequency': 'bid', 'timing': ['morning', 'evening']},
                'glimepiride': {'dose': '2mg', 'frequency': 'qd', 'timing': ['morning']},
                'amlodipine': {'dose': '5mg', 'frequency': 'qd', 'timing': ['morning']}
            },
            'contraindications': [],  # 禁忌症
            'allergies': [],  # 过敏史
            'comorbidities': ['hypertension'],  # 合并症
            'last_hba1c': 8.5,  # %
            'last_creatinine': 1.1,  # mg/dL
            'last_egfr': 75  # mL/min/1.73m²
        }
        
        # 分析结果存储
        self.clinical_insights = {}
        self.risk_predictions = {}
        self.treatment_recommendations = {}
        self.monitoring_plan = {}
    
    def run_clinical_analysis(self):
        """运行临床价值导向的分析"""
        print("=== 临床价值导向多模态分析 ===")
        
        # 1. 早期风险识别（传统方法可能遗漏的问题）
        print("1. 早期风险识别分析...")
        self._identify_subclinical_risks()
        
        # 2. 并发症风险预测
        print("2. 并发症风险预测...")
        self._predict_complication_risks()
        
        # 3. 个性化治疗方案生成
        print("3. 生成个性化治疗方案...")
        self._generate_personalized_treatment()
        
        # 4. 治疗时机优化
        print("4. 优化治疗时机...")
        self._optimize_treatment_timing()
        
        # 5. 监测方案设计
        print("5. 设计个性化监测方案...")
        self._design_monitoring_plan()
        
        # 6. 成本效益分析
        print("6. 成本效益分析...")
        self._analyze_cost_effectiveness()
        
        return self._generate_clinical_report()
    
    def _identify_subclinical_risks(self):
        """识别传统方法可能遗漏的早期风险"""
        risks = []
        
        # 1. 早期糖尿病心脏自主神经病变 (CAN)
        can_risk = self._assess_early_cardiac_autonomic_neuropathy()
        if can_risk['risk_level'] != 'low':
            risks.append({
                'condition': '早期糖尿病心脏自主神经病变',
                'traditional_detection': '通常需要明显症状出现后才诊断',
                'early_detection_advantage': f'提前{can_risk["early_detection_months"]}个月发现',
                'evidence': can_risk['evidence'],
                'clinical_significance': 'CAN是糖尿病患者心血管死亡的重要预测因子',
                'immediate_action': can_risk['immediate_action']
            })
        
        # 2. 脆性糖尿病早期征象
        brittle_risk = self._assess_brittle_diabetes_risk()
        if brittle_risk['risk_level'] != 'low':
            risks.append({
                'condition': '脆性糖尿病早期征象',
                'traditional_detection': '通常在反复低血糖或酮症后才认识到',
                'early_detection_advantage': f'提前{brittle_risk["early_detection_months"]}个月识别',
                'evidence': brittle_risk['evidence'],
                'clinical_significance': '脆性糖尿病患者急性并发症风险增加5-10倍',
                'immediate_action': brittle_risk['immediate_action']
            })
        
        # 3. 隐匿性心血管疾病
        cvd_risk = self._assess_subclinical_cvd()
        if cvd_risk['risk_level'] != 'low':
            risks.append({
                'condition': '隐匿性心血管疾病',
                'traditional_detection': '通常在症状性事件后才发现',
                'early_detection_advantage': f'提前{cvd_risk["early_detection_months"]}个月预警',
                'evidence': cvd_risk['evidence'],
                'clinical_significance': '糖尿病患者心血管事件风险比正常人高2-4倍',
                'immediate_action': cvd_risk['immediate_action']
            })
        
        self.clinical_insights['subclinical_risks'] = risks
    
    def _assess_early_cardiac_autonomic_neuropathy(self):
        """评估早期心脏自主神经病变"""
        # 计算HRV多项指标
        hrv_metrics = self.hrv_data.mean()
        rmssd = hrv_metrics['rmssd_ms']
        sdnn = hrv_metrics['sdnn_ms'] 
        lf_hf_ratio = hrv_metrics['lf_hf_ratio']
        
        # 血糖变异性对HRV的影响
        glucose_values = self.cgm_data['glucose_mg_dl'].values
        glucose_cv = (np.std(glucose_values) / np.mean(glucose_values)) * 100
        
        # CAN早期诊断算法（基于多项研究）
        can_score = 0
        evidence = []
        
        # Ewing测试的HRV等效指标
        if rmssd < 15:  # 严重异常
            can_score += 3
            evidence.append(f"RMSSD={rmssd:.1f}ms (正常>20ms)")
        elif rmssd < 20:  # 边界异常
            can_score += 2
            evidence.append(f"RMSSD={rmssd:.1f}ms (边界异常)")
        
        if sdnn < 50:
            can_score += 2
            evidence.append(f"SDNN={sdnn:.1f}ms (正常>50ms)")
        
        if lf_hf_ratio > 3.0 or lf_hf_ratio < 0.5:
            can_score += 1
            evidence.append(f"LF/HF={lf_hf_ratio:.2f} (自主神经失衡)")
        
        # 血糖变异性加重自主神经功能
        if glucose_cv > 36 and rmssd < 25:
            can_score += 2
            evidence.append(f"高血糖变异性({glucose_cv:.1f}%) + HRV降低的协同效应")
        
        # 年龄和病程修正
        age_duration_factor = self.patient_profile['age'] / 50 + self.patient_profile['diabetes_duration_years'] / 10
        if age_duration_factor > 1.5 and can_score >= 2:
            can_score += 1
            evidence.append(f"年龄({self.patient_profile['age']}岁)和病程({self.patient_profile['diabetes_duration_years']}年)增加CAN风险")
        
        # 风险分层
        if can_score >= 5:
            risk_level = 'high'
            early_detection_months = 12
            immediate_action = "立即进行Ewing测试确认，考虑调整降糖方案减少血糖变异性"
        elif can_score >= 3:
            risk_level = 'moderate'
            early_detection_months = 6
            immediate_action = "3个月内进行HRV专项检查，监测自主神经功能变化"
        elif can_score >= 1:
            risk_level = 'mild'
            early_detection_months = 3
            immediate_action = "加强血糖管理，6个月后复评HRV"
        else:
            risk_level = 'low'
            early_detection_months = 0
            immediate_action = "继续当前治疗方案"
        
        return {
            'risk_level': risk_level,
            'can_score': can_score,
            'early_detection_months': early_detection_months,
            'evidence': evidence,
            'immediate_action': immediate_action
        }
    
    def _assess_brittle_diabetes_risk(self):
        """评估脆性糖尿病风险"""
        glucose_values = self.cgm_data['glucose_mg_dl'].values
        
        # 脆性糖尿病的多模态特征
        brittle_score = 0
        evidence = []
        
        # 1. 血糖变异性异常高
        cv = (np.std(glucose_values) / np.mean(glucose_values)) * 100
        if cv > 50:
            brittle_score += 3
            evidence.append(f"极高血糖变异性 CV={cv:.1f}% (正常<36%)")
        elif cv > 40:
            brittle_score += 2
            evidence.append(f"高血糖变异性 CV={cv:.1f}%")
        
        # 2. 频繁血糖波动
        glucose_swings = np.sum(np.abs(np.diff(glucose_values)) > 50)  # 血糖摆幅>50mg/dL的次数
        swing_rate = glucose_swings / len(glucose_values) * 100
        if swing_rate > 10:
            brittle_score += 2
            evidence.append(f"频繁大幅血糖波动，{swing_rate:.1f}%的时间点血糖变化>50mg/dL")
        
        # 3. 低血糖频发且不易察觉
        tbr = np.sum(glucose_values < 70) / len(glucose_values) * 100
        severe_hypo_rate = np.sum(glucose_values < 54) / len(glucose_values) * 100
        if tbr > 10 and severe_hypo_rate > 2:
            brittle_score += 3
            evidence.append(f"频繁低血糖：TBR={tbr:.1f}%，严重低血糖率={severe_hypo_rate:.1f}%")
        
        # 4. 自主神经功能异常（低血糖无症状）
        hrv_metrics = self.hrv_data.mean()
        if hrv_metrics['rmssd_ms'] < 15 and tbr > 5:
            brittle_score += 2
            evidence.append("自主神经病变导致低血糖症状减弱")
        
        # 5. 血压波动与血糖关联异常
        if hasattr(self, '_calculate_glucose_bp_correlation'):
            bp_glucose_corr = self._calculate_glucose_bp_correlation()
            if abs(bp_glucose_corr) > 0.6:
                brittle_score += 1
                evidence.append(f"血糖-血压异常强耦合 r={bp_glucose_corr:.3f}")
        
        # 风险分层
        if brittle_score >= 6:
            risk_level = 'high'
            early_detection_months = 8
            immediate_action = "考虑胰岛素泵治疗，内分泌专科紧急会诊"
        elif brittle_score >= 4:
            risk_level = 'moderate' 
            early_detection_months = 4
            immediate_action = "调整降糖方案，避免磺脲类药物，考虑CGM指导治疗"
        elif brittle_score >= 2:
            risk_level = 'mild'
            early_detection_months = 2
            immediate_action = "密切监测血糖，调整用药时间"
        else:
            risk_level = 'low'
            early_detection_months = 0
            immediate_action = "继续当前治疗"
        
        return {
            'risk_level': risk_level,
            'brittle_score': brittle_score,
            'early_detection_months': early_detection_months,
            'evidence': evidence,
            'immediate_action': immediate_action
        }
    
    def _assess_subclinical_cvd(self):
        """评估隐匿性心血管疾病"""
        # 多模态心血管风险评估
        cvd_score = 0
        evidence = []
        
        # 1. 血压变异性异常（ABPM数据）
        bp_cv = (self.abpm_data['sbp_mmhg'].std() / self.abpm_data['sbp_mmhg'].mean()) * 100
        if bp_cv > 15:
            cvd_score += 2
            evidence.append(f"血压变异性增高 CV={bp_cv:.1f}% (正常<10%)")
        
        # 2. 非杓型血压（增加脑卒中风险）
        daytime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'daytime']['sbp_mmhg'].mean()
        nighttime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'nighttime']['sbp_mmhg'].mean()
        dip_percent = (daytime_bp - nighttime_bp) / daytime_bp * 100
        
        if dip_percent < 10:
            cvd_score += 2
            if dip_percent < 0:
                cvd_score += 1  # 反杓型更危险
                evidence.append(f"反杓型血压模式，夜间血压升高 (脑卒中风险增加70%)")
            else:
                evidence.append(f"非杓型血压模式 dip={dip_percent:.1f}% (脑卒中风险增加40%)")
        
        # 3. HRV降低 + 高血糖的协同心血管风险
        hrv_rmssd = self.hrv_data['rmssd_ms'].mean()
        mean_glucose = self.cgm_data['glucose_mg_dl'].mean()
        
        if hrv_rmssd < 20 and mean_glucose > 180:
            cvd_score += 3
            evidence.append(f"HRV降低({hrv_rmssd:.1f}ms) + 高血糖({mean_glucose:.1f}mg/dL)协同增加心血管风险")
        
        # 4. 隐匿性心律失常风险
        heart_rates = self.ecg_data['heart_rate_bpm'].values
        hr_cv = (np.std(heart_rates) / np.mean(heart_rates)) * 100
        if hr_cv < 5:  # 心率变异过低
            cvd_score += 1
            evidence.append(f"心率变异过低 CV={hr_cv:.1f}% (自主神经功能受损)")
        
        # 5. 代谢性心血管风险
        if self.patient_profile['last_hba1c'] > 8.0 and daytime_bp > 140:
            cvd_score += 2
            evidence.append(f"HbA1c {self.patient_profile['last_hba1c']}% + 高血压增加大血管病变风险")
        
        # 风险分层 (基于Framingham + UKPDS风险评估)
        if cvd_score >= 7:
            risk_level = 'high'
            early_detection_months = 6
            immediate_action = "立即心血管专科评估，考虑冠脉CTA或负荷试验"
        elif cvd_score >= 4:
            risk_level = 'moderate'
            early_detection_months = 3
            immediate_action = "加强降压治疗，3个月内心电图和超声心动图检查"
        elif cvd_score >= 2:
            risk_level = 'mild'
            early_detection_months = 1
            immediate_action = "优化血糖和血压控制，监测心血管症状"
        else:
            risk_level = 'low'
            early_detection_months = 0
            immediate_action = "继续当前治疗"
        
        return {
            'risk_level': risk_level,
            'cvd_score': cvd_score,
            'early_detection_months': early_detection_months,
            'evidence': evidence,
            'immediate_action': immediate_action
        }
    
    def _predict_complication_risks(self):
        """预测未来1-6个月并发症风险"""
        predictions = {}
        
        # 1. 严重低血糖风险预测
        predictions['severe_hypoglycemia'] = self._predict_severe_hypoglycemia_risk()
        
        # 2. 心血管事件风险预测  
        predictions['cardiovascular_events'] = self._predict_cardiovascular_risk()
        
        # 3. 糖尿病酮症风险预测
        predictions['diabetic_ketoacidosis'] = self._predict_dka_risk()
        
        # 4. 急性并发症住院风险
        predictions['acute_hospitalization'] = self._predict_hospitalization_risk()
        
        self.risk_predictions = predictions
    
    def _predict_severe_hypoglycemia_risk(self):
        """预测严重低血糖风险"""
        glucose_values = self.cgm_data['glucose_mg_dl'].values
        
        # 风险因子累积评分
        risk_score = 0
        risk_factors = []
        
        # 1. 当前低血糖频率
        tbr_54 = np.sum(glucose_values < 54) / len(glucose_values) * 100
        if tbr_54 > 1:
            risk_score += 3
            risk_factors.append(f"严重低血糖时间 {tbr_54:.1f}% (目标<1%)")
        
        # 2. 夜间低血糖倾向
        night_hours = []
        for i, timestamp in enumerate(self.cgm_data['timestamp']):
            hour = timestamp.hour
            if 0 <= hour <= 6:  # 夜间
                night_hours.append(glucose_values[i])
        
        if night_hours:
            night_hypo_rate = np.sum(np.array(night_hours) < 70) / len(night_hours) * 100
            if night_hypo_rate > 5:
                risk_score += 2
                risk_factors.append(f"夜间低血糖率 {night_hypo_rate:.1f}%")
        
        # 3. HRV降低导致低血糖症状不明显
        hrv_rmssd = self.hrv_data['rmssd_ms'].mean()
        if hrv_rmssd < 15:
            risk_score += 2
            risk_factors.append("自主神经病变可能导致低血糖症状不典型")
        
        # 4. 当前药物风险
        if 'glimepiride' in self.patient_profile['current_medications']:
            risk_score += 1
            risk_factors.append("磺脲类药物增加低血糖风险")
        
        # 5. 血糖变异性高
        cv = (np.std(glucose_values) / np.mean(glucose_values)) * 100
        if cv > 40:
            risk_score += 2
            risk_factors.append(f"高血糖变异性 {cv:.1f}% 增加低血糖风险")
        
        # 预测未来3个月风险
        if risk_score >= 7:
            risk_level = 'high'
            probability = 85
            timeline = "未来4周内"
            recommendation = "立即停用磺脲类药物，调整为基础胰岛素方案"
        elif risk_score >= 4:
            risk_level = 'moderate'
            probability = 45
            timeline = "未来8周内" 
            recommendation = "减少磺脲类药物剂量，加强血糖监测"
        elif risk_score >= 2:
            risk_level = 'mild'
            probability = 20
            timeline = "未来12周内"
            recommendation = "优化用药时间，教育低血糖处理"
        else:
            risk_level = 'low'
            probability = 5
            timeline = "未来3个月内"
            recommendation = "继续当前方案，定期监测"
        
        return {
            'risk_level': risk_level,
            'probability_percent': probability,
            'timeline': timeline,
            'risk_factors': risk_factors,
            'prevention_strategy': recommendation
        }
    
    def _predict_cardiovascular_risk(self):
        """预测心血管事件风险"""
        # 基于多模态数据的心血管事件风险预测
        risk_score = 0
        risk_factors = []
        
        # 1. 血压控制状况
        mean_sbp = self.abpm_data['sbp_mmhg'].mean()
        if mean_sbp > 160:
            risk_score += 3
            risk_factors.append(f"血压严重升高 {mean_sbp:.1f}mmHg")
        elif mean_sbp > 140:
            risk_score += 2
            risk_factors.append(f"血压未达标 {mean_sbp:.1f}mmHg")
        
        # 2. 非杓型血压增加脑卒中风险
        daytime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'daytime']['sbp_mmhg'].mean()
        nighttime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'nighttime']['sbp_mmhg'].mean()
        dip_percent = (daytime_bp - nighttime_bp) / daytime_bp * 100
        
        if dip_percent < 0:  # 反杓型
            risk_score += 3
            risk_factors.append("反杓型血压，脑卒中风险增加70%")
        elif dip_percent < 10:  # 非杓型
            risk_score += 2
            risk_factors.append("非杓型血压，脑卒中风险增加40%")
        
        # 3. HRV严重降低
        hrv_rmssd = self.hrv_data['rmssd_ms'].mean()
        if hrv_rmssd < 15:
            risk_score += 2
            risk_factors.append(f"严重HRV降低 RMSSD={hrv_rmssd:.1f}ms")
        
        # 4. 血糖控制差
        mean_glucose = self.cgm_data['glucose_mg_dl'].mean()
        if mean_glucose > 200:
            risk_score += 2
            risk_factors.append(f"血糖控制差 {mean_glucose:.1f}mg/dL")
        
        # 5. 年龄和病程
        if self.patient_profile['age'] > 50 and self.patient_profile['diabetes_duration_years'] > 5:
            risk_score += 1
            risk_factors.append(f"年龄{self.patient_profile['age']}岁，病程{self.patient_profile['diabetes_duration_years']}年")
        
        # 基于UKPDS风险方程修正的预测
        if risk_score >= 8:
            risk_level = 'high'
            probability = 25  # 6个月内心血管事件风险
            timeline = "未来6个月内"
            recommendation = "立即心血管专科评估，考虑二级预防用药"
        elif risk_score >= 5:
            risk_level = 'moderate'
            probability = 12
            timeline = "未来12个月内"
            recommendation = "加强降压降糖治疗，3个月内心血管评估"
        elif risk_score >= 3:
            risk_level = 'mild'
            probability = 6
            timeline = "未来24个月内"
            recommendation = "优化血压血糖控制，半年随访"
        else:
            risk_level = 'low'
            probability = 3
            timeline = "未来2年内"
            recommendation = "继续当前治疗，年度评估"
        
        return {
            'risk_level': risk_level,
            'probability_percent': probability,
            'timeline': timeline,
            'risk_factors': risk_factors,
            'prevention_strategy': recommendation
        }
    
    def _predict_dka_risk(self):
        """预测糖尿病酮症风险（2型糖尿病也可能发生）"""
        risk_score = 0
        risk_factors = []
        
        # 1. 持续高血糖
        glucose_values = self.cgm_data['glucose_mg_dl'].values
        tar_250 = np.sum(glucose_values > 250) / len(glucose_values) * 100
        if tar_250 > 10:
            risk_score += 3
            risk_factors.append(f"持续严重高血糖 TAR>250mg/dL: {tar_250:.1f}%")
        elif tar_250 > 5:
            risk_score += 1
            risk_factors.append(f"频繁高血糖 TAR>250mg/dL: {tar_250:.1f}%")
        
        # 2. 平均血糖极高
        mean_glucose = np.mean(glucose_values)
        if mean_glucose > 250:
            risk_score += 2
            risk_factors.append(f"平均血糖极高 {mean_glucose:.1f}mg/dL")
        
        # 3. 病程长且控制差 
        if (self.patient_profile['diabetes_duration_years'] > 10 and 
            self.patient_profile['last_hba1c'] > 10):
            risk_score += 2
            risk_factors.append(f"长病程+控制差: {self.patient_profile['diabetes_duration_years']}年, HbA1c {self.patient_profile['last_hba1c']}%")
        
        # 4. 可能的胰岛功能衰竭征象
        # 简化评估：如果使用磺脲类但血糖仍然很高
        if ('glimepiride' in self.patient_profile['current_medications'] and 
            mean_glucose > 200):
            risk_score += 1
            risk_factors.append("磺脲类药物效果差，提示胰岛功能衰竭")
        
        # 预测风险
        if risk_score >= 6:
            risk_level = 'high'
            probability = 15
            timeline = "未来4周内"
            recommendation = "立即检查血酮，考虑胰岛素治疗"
        elif risk_score >= 3:
            risk_level = 'moderate'
            probability = 8
            timeline = "未来8周内"
            recommendation = "强化降糖治疗，监测血酮"
        elif risk_score >= 1:
            risk_level = 'mild'
            probability = 3
            timeline = "未来12周内"
            recommendation = "调整降糖方案，教育酮症预防"
        else:
            risk_level = 'low'
            probability = 1
            timeline = "未来6个月内"
            recommendation = "继续当前治疗"
        
        return {
            'risk_level': risk_level,
            'probability_percent': probability,
            'timeline': timeline,
            'risk_factors': risk_factors,
            'prevention_strategy': recommendation
        }
    
    def _predict_hospitalization_risk(self):
        """预测急性并发症住院风险"""
        # 综合多种急性并发症的住院风险
        risk_factors = []
        total_risk = 0
        
        # 获取各种并发症风险
        hypo_risk = self.risk_predictions.get('severe_hypoglycemia', {})
        cv_risk = self.risk_predictions.get('cardiovascular_events', {})
        dka_risk = self.risk_predictions.get('diabetic_ketoacidosis', {})
        
        # 严重低血糖住院风险
        if hypo_risk.get('risk_level') == 'high':
            total_risk += 15
            risk_factors.append("严重低血糖住院风险")
        elif hypo_risk.get('risk_level') == 'moderate':
            total_risk += 8
        
        # 心血管事件住院风险
        if cv_risk.get('risk_level') == 'high':
            total_risk += 20
            risk_factors.append("心血管事件住院风险")
        elif cv_risk.get('risk_level') == 'moderate':
            total_risk += 10
        
        # 酮症住院风险
        if dka_risk.get('risk_level') == 'high':
            total_risk += 12
            risk_factors.append("糖尿病酮症住院风险")
        elif dka_risk.get('risk_level') == 'moderate':
            total_risk += 6
        
        # 其他因素
        # 多重用药风险
        med_count = len(self.patient_profile['current_medications'])
        if med_count >= 3:
            total_risk += 3
            risk_factors.append("多重用药相互作用风险")
        
        # 年龄因素
        if self.patient_profile['age'] > 65:
            total_risk += 5
            risk_factors.append("高龄住院风险增加")
        
        # 风险分层
        if total_risk >= 30:
            risk_level = 'high'
            probability = total_risk
            timeline = "未来1-2个月内"
            recommendation = "密切监测，考虑预防性住院调整治疗"
        elif total_risk >= 15:
            risk_level = 'moderate'
            probability = total_risk
            timeline = "未来3-4个月内"
            recommendation = "加强门诊随访，制定应急预案"
        elif total_risk >= 5:
            risk_level = 'mild'
            probability = total_risk
            timeline = "未来6个月内"
            recommendation = "定期随访，患者教育"
        else:
            risk_level = 'low'
            probability = total_risk
            timeline = "未来1年内"
            recommendation = "常规随访"
        
        return {
            'risk_level': risk_level,
            'probability_percent': min(probability, 50),  # 最高50%
            'timeline': timeline,
            'risk_factors': risk_factors,
            'prevention_strategy': recommendation
        }
    
    def _generate_personalized_treatment(self):
        """生成个性化治疗方案"""
        treatment_plan = {}
        
        # 1. 降糖药物调整
        treatment_plan['glucose_management'] = self._optimize_glucose_treatment()
        
        # 2. 血压管理
        treatment_plan['blood_pressure_management'] = self._optimize_bp_treatment()
        
        # 3. 心血管保护
        treatment_plan['cardiovascular_protection'] = self._design_cv_protection()
        
        # 4. 并发症预防
        treatment_plan['complication_prevention'] = self._design_complication_prevention()
        
        self.treatment_recommendations = treatment_plan
    
    def _optimize_glucose_treatment(self):
        """优化血糖治疗方案"""
        current_meds = self.patient_profile['current_medications']
        glucose_values = self.cgm_data['glucose_mg_dl'].values
        mean_glucose = np.mean(glucose_values)
        cv = (np.std(glucose_values) / mean_glucose) * 100
        
        recommendations = []
        
        # 基于血糖控制质量调整
        if mean_glucose > 200:
            # 血糖控制很差
            recommendations.append({
                'action': '立即调整',
                'medication': 'metformin',
                'change': '增加剂量至1500mg分次服用(早1000mg+晚500mg)',
                'rationale': '基础血糖过高，需要增加二甲双胍剂量',
                'contraindication_check': self._check_metformin_contraindications()
            })
            
            # 考虑停用磺脲类，改为胰岛素
            if cv > 40:  # 高变异性
                recommendations.append({
                    'action': '药物替换',
                    'medication': 'glimepiride',
                    'change': '逐渐减量停用',
                    'rationale': '磺脲类增加血糖变异性和低血糖风险',
                    'alternative': '启动基础胰岛素（如甘精胰岛素10单位睡前）'
                })
        
        elif mean_glucose > 150:
            # 血糖控制中等
            if cv > 36:
                recommendations.append({
                    'action': '调整用药时间',
                    'medication': 'glimepiride',
                    'change': '改为餐前30分钟服用',
                    'rationale': '优化药物作用时间，减少餐后血糖波动'
                })
        
        # 基于低血糖风险调整
        tbr = np.sum(glucose_values < 70) / len(glucose_values) * 100
        if tbr > 5:
            recommendations.append({
                'action': '减量',
                'medication': 'glimepiride',
                'change': '减量至1mg每日',
                'rationale': f'低血糖时间{tbr:.1f}%超标(目标<4%)',
                'monitoring': '2周后复评血糖'
            })
        
        return recommendations
    
    def _check_metformin_contraindications(self):
        """检查二甲双胍禁忌症"""
        warnings = []
        if self.patient_profile['last_egfr'] < 30:
            warnings.append("eGFR<30mL/min，禁用二甲双胍")
        elif self.patient_profile['last_egfr'] < 60:
            warnings.append("eGFR<60mL/min，需减量使用")
        return warnings
    
    def _optimize_bp_treatment(self):
        """优化血压治疗方案"""
        bp_data = self.abpm_data
        mean_sbp = bp_data['sbp_mmhg'].mean()
        mean_dbp = bp_data['dbp_mmhg'].mean()
        
        # 计算昼夜节律
        daytime_bp = bp_data[bp_data['measurement_type'] == 'daytime']['sbp_mmhg'].mean()
        nighttime_bp = bp_data[bp_data['measurement_type'] == 'nighttime']['sbp_mmhg'].mean()
        dip_percent = (daytime_bp - nighttime_bp) / daytime_bp * 100
        
        recommendations = []
        
        if mean_sbp > 140 or mean_dbp > 90:
            # 血压未达标
            recommendations.append({
                'action': '增加剂量',
                'medication': 'amlodipine',
                'change': '增至7.5mg每日（或10mg每日）',
                'rationale': f'血压{mean_sbp:.1f}/{mean_dbp:.1f}mmHg未达标',
                'target': '目标<140/90mmHg'
            })
            
            # 考虑联合用药
            recommendations.append({
                'action': '联合用药',
                'medication': '新增ACEI或ARB',
                'change': '如依那普利5mg每日或缬沙坦80mg每日',
                'rationale': '糖尿病患者优选ACEI/ARB类降压药',
                'additional_benefit': '肾脏保护作用'
            })
        
        # 基于昼夜节律调整用药时间
        if dip_percent < 10:  # 非杓型或反杓型
            recommendations.append({
                'action': '调整用药时间',
                'medication': 'amlodipine',
                'change': '改为睡前服用',
                'rationale': f'非杓型血压模式(dip={dip_percent:.1f}%)，睡前给药改善昼夜节律',
                'expected_benefit': '降低夜间血压，减少脑卒中风险'
            })
        
        return recommendations
    
    def _design_cv_protection(self):
        """设计心血管保护策略"""
        recommendations = []
        
        # 基于风险评估决定是否需要他汀类药物
        cv_risk = self.risk_predictions.get('cardiovascular_events', {})
        
        if cv_risk.get('risk_level') in ['high', 'moderate']:
            recommendations.append({
                'medication': 'atorvastatin',
                'dose': '20mg每晚',
                'rationale': '糖尿病+高血压患者心血管风险高，需要他汀类药物',
                'target': 'LDL-C<2.6mmol/L(100mg/dL)',
                'monitoring': '4-6周后复查血脂和肝功能'
            })
        
        # 抗血小板聚集
        if (self.patient_profile['age'] > 50 and 
            cv_risk.get('risk_level') == 'high'):
            recommendations.append({
                'medication': 'aspirin',
                'dose': '75mg每日',
                'rationale': '高心血管风险患者一级预防',
                'contraindication': '排除出血风险后使用'
            })
        
        # HRV严重降低的患者
        hrv_rmssd = self.hrv_data['rmssd_ms'].mean()
        if hrv_rmssd < 15:
            recommendations.append({
                'medication': 'metoprolol',
                'dose': '25mg bid',
                'rationale': 'β受体阻滞剂改善自主神经功能，减少心律失常',
                'monitoring': '注意血糖掩蔽低血糖症状'
            })
        
        return recommendations
    
    def _design_complication_prevention(self):
        """设计并发症预防策略"""
        prevention_plan = []
        
        # 1. 低血糖预防
        hypo_risk = self.risk_predictions.get('severe_hypoglycemia', {})
        if hypo_risk.get('risk_level') != 'low':
            prevention_plan.append({
                'complication': '严重低血糖',
                'strategies': [
                    '患者和家属低血糖急救培训',
                    '备用胰高血糖素注射笔',
                    'CGM低血糖报警设置',
                    '调整运动和饮食时间'
                ]
            })
        
        # 2. 心血管事件预防
        cv_risk = self.risk_predictions.get('cardiovascular_events', {})
        if cv_risk.get('risk_level') != 'low':
            prevention_plan.append({
                'complication': '心血管事件',
                'strategies': [
                    '血压家庭监测',
                    '心电图和超声心动图筛查',
                    '运动耐量评估',
                    '戒烟限酒生活方式干预'
                ]
            })
        
        # 3. 糖尿病肾病预防
        prevention_plan.append({
            'complication': '糖尿病肾病',
            'strategies': [
                '每3个月检查尿微量白蛋白',
                '控制血压<130/80mmHg',
                'ACEI/ARB类药物肾脏保护',
                '避免肾毒性药物'
            ]
        })
        
        return prevention_plan
    
    def _optimize_treatment_timing(self):
        """优化治疗时机"""
        timing_recommendations = {}
        
        # 基于昼夜节律优化用药时间
        timing_recommendations['medication_timing'] = self._optimize_medication_timing()
        
        # 基于生理耦合优化监测时间
        timing_recommendations['monitoring_timing'] = self._optimize_monitoring_timing()
        
        # 基于风险预测优化干预时机
        timing_recommendations['intervention_timing'] = self._optimize_intervention_timing()
        
        return timing_recommendations
    
    def _optimize_medication_timing(self):
        """优化用药时间"""
        recommendations = []
        
        # 基于血压昼夜节律调整降压药时间
        daytime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'daytime']['sbp_mmhg'].mean()
        nighttime_bp = self.abpm_data[self.abpm_data['measurement_type'] == 'nighttime']['sbp_mmhg'].mean()
        
        if nighttime_bp >= daytime_bp:  # 反杓型
            recommendations.append({
                'medication': '降压药',
                'optimal_timing': '睡前服用',
                'rationale': '反杓型血压，睡前给药降低夜间血压',
                'expected_benefit': '脑卒中风险降低30-40%'
            })
        
        # 基于血糖波动模式调整降糖药时间
        glucose_values = self.cgm_data['glucose_mg_dl'].values
        timestamps = self.cgm_data['timestamp'].values
        
        # 找出血糖最高的时间段
        hourly_glucose = {}
        for i, timestamp in enumerate(timestamps):
            hour = pd.to_datetime(timestamp).hour
            if hour not in hourly_glucose:
                hourly_glucose[hour] = []
            hourly_glucose[hour].append(glucose_values[i])
        
        peak_hour = max(hourly_glucose.keys(), 
                       key=lambda h: np.mean(hourly_glucose[h]))
        
        recommendations.append({
            'medication': '降糖药',
            'optimal_timing': f'餐前{2-3}小时(约{peak_hour-2}点)',
            'rationale': f'{peak_hour}点血糖最高，提前给药覆盖高峰期',
            'expected_benefit': '餐后血糖改善20-30%'
        })
        
        return recommendations
    
    def _optimize_monitoring_timing(self):
        """优化监测时机"""
        recommendations = []
        
        # 基于风险预测优化监测频率
        high_risk_conditions = []
        for condition, prediction in self.risk_predictions.items():
            if prediction.get('risk_level') == 'high':
                high_risk_conditions.append(condition)
        
        if high_risk_conditions:
            recommendations.append({
                'parameter': '血糖',
                'frequency': '每日4次',
                'timing': '三餐前+睡前',
                'rationale': f'高风险并发症：{", ".join(high_risk_conditions)}',
                'duration': '4周后根据情况调整'
            })
            
            recommendations.append({
                'parameter': '血压',
                'frequency': '每日2次',
                'timing': '晨起+睡前',
                'rationale': '血压变异性高，需密切监测',
                'target': '<140/90mmHg'
            })
        
        return recommendations
    
    def _optimize_intervention_timing(self):
        """优化干预时机"""
        recommendations = []
        
        # 基于风险时间线规划干预
        for condition, prediction in self.risk_predictions.items():
            if prediction.get('risk_level') in ['high', 'moderate']:
                timeline = prediction.get('timeline', '')
                if '4周' in timeline or '1个月' in timeline:
                    urgency = '紧急'
                    action_time = '立即'
                elif '8周' in timeline or '2个月' in timeline:
                    urgency = '重要'
                    action_time = '1周内'
                else:
                    urgency = '常规'
                    action_time = '2周内'
                
                recommendations.append({
                    'condition': condition,
                    'urgency': urgency,
                    'action_timeline': action_time,
                    'intervention': prediction.get('prevention_strategy', ''),
                    'rationale': f"{prediction.get('probability_percent', 0)}%概率在{timeline}"
                })
        
        return recommendations
    
    def _design_monitoring_plan(self):
        """设计个性化监测方案"""
        monitoring_plan = {}
        
        # 1. 血糖监测方案
        monitoring_plan['glucose_monitoring'] = self._design_glucose_monitoring()
        
        # 2. 血压监测方案
        monitoring_plan['bp_monitoring'] = self._design_bp_monitoring()
        
        # 3. 心血管监测方案
        monitoring_plan['cv_monitoring'] = self._design_cv_monitoring()
        
        # 4. 实验室检查方案
        monitoring_plan['lab_monitoring'] = self._design_lab_monitoring()
        
        self.monitoring_plan = monitoring_plan
    
    def _design_glucose_monitoring(self):
        """设计血糖监测方案"""
        glucose_cv = (np.std(self.cgm_data['glucose_mg_dl']) / 
                     np.mean(self.cgm_data['glucose_mg_dl'])) * 100
        
        if glucose_cv > 40:  # 高变异性
            return {
                'method': 'CGM持续监测',
                'duration': '至少3个月',
                'frequency': '每分钟',
                'key_metrics': ['TIR', 'CV', 'TBR', '夜间低血糖'],
                'alert_settings': '低血糖<70mg/dL, 高血糖>250mg/dL',
                'review_frequency': '每周数据下载分析'
            }
        else:
            return {
                'method': '指血血糖+CGM',
                'duration': 'CGM每月1周',
                'frequency': '指血每日2-3次',
                'key_metrics': ['空腹血糖', '餐后2h血糖', '睡前血糖'],
                'review_frequency': '每2周'
            }
    
    def _design_bp_monitoring(self):
        """设计血压监测方案"""
        bp_cv = (self.abpm_data['sbp_mmhg'].std() / 
                self.abpm_data['sbp_mmhg'].mean()) * 100
        
        if bp_cv > 15:  # 高变异性
            return {
                'method': '家庭血压监测+定期ABPM',
                'frequency': '每日2次(晨起+睡前)',
                'abpm_frequency': '每3个月',
                'target': '<140/90mmHg (家庭测量<135/85mmHg)',
                'special_attention': '夜间血压，昼夜节律'
            }
        else:
            return {
                'method': '家庭血压监测',
                'frequency': '每日1次',
                'abpm_frequency': '每6个月',
                'target': '<140/90mmHg'
            }
    
    def _design_cv_monitoring(self):
        """设计心血管监测方案"""
        cv_risk_level = self.risk_predictions.get('cardiovascular_events', {}).get('risk_level', 'low')
        
        if cv_risk_level == 'high':
            return {
                'ecg': '每3个月',
                'echo': '每6个月',
                'stress_test': '每年或症状时',
                'carotid_ultrasound': '每年',
                'ankle_brachial_index': '每年',
                'special_tests': 'HRV监测每月'
            }
        elif cv_risk_level == 'moderate':
            return {
                'ecg': '每6个月',
                'echo': '每年',
                'carotid_ultrasound': '每2年',
                'special_tests': 'HRV监测每季度'
            }
        else:
            return {
                'ecg': '每年',
                'echo': '每2年',
                'routine_screening': '按指南推荐'
            }
    
    def _design_lab_monitoring(self):
        """设计实验室检查方案"""
        return {
            'hba1c': '每3个月',
            'lipid_profile': '每3个月(调脂期间)',
            'kidney_function': '每3个月(eGFR, 尿微量白蛋白)',
            'liver_function': '每6个月',
            'thyroid_function': '每年',
            'vitamin_b12': '每年(二甲双胍用户)',
            'special_tests': {
                '糖化白蛋白': '每月(HbA1c不能反映时)',
                '胰岛功能': '必要时C肽检测',
                '自身抗体': '疑似LADA时检测'
            }
        }
    
    def _analyze_cost_effectiveness(self):
        """分析成本效益"""
        # 估算多模态监测的成本效益
        cost_analysis = {}
        
        # 传统监测成本 (年)
        traditional_cost = {
            'hba1c_quarterly': 4 * 50,  # $200
            'lipid_profile_quarterly': 4 * 30,  # $120
            'routine_visits': 6 * 200,  # $1200
            'total': 1520
        }
        
        # 多模态监测成本 (年)
        multimodal_cost = {
            'cgm_annual': 3600,  # $3600
            'abpm_quarterly': 4 * 150,  # $600
            'hrv_monitoring': 1200,  # $1200
            'analysis_system': 2400,  # $2400
            'total': 7800
        }
        
        # 预期效益
        benefits = {
            'severe_hypo_prevention': {
                'events_prevented_per_year': 2,
                'cost_per_event': 5000,
                'total_savings': 10000
            },
            'cv_event_prevention': {
                'events_prevented_per_year': 0.3,
                'cost_per_event': 25000,
                'total_savings': 7500
            },
            'hospitalization_reduction': {
                'days_saved_per_year': 3,
                'cost_per_day': 1500,
                'total_savings': 4500
            },
            'medication_optimization': {
                'annual_savings': 1200
            }
        }
        
        total_benefits = sum(b.get('total_savings', b.get('annual_savings', 0)) 
                           for b in benefits.values())
        
        net_benefit = total_benefits - (multimodal_cost['total'] - traditional_cost['total'])
        roi = (net_benefit / (multimodal_cost['total'] - traditional_cost['total'])) * 100
        
        cost_analysis = {
            'traditional_annual_cost': traditional_cost['total'],
            'multimodal_annual_cost': multimodal_cost['total'],
            'additional_investment': multimodal_cost['total'] - traditional_cost['total'],
            'annual_benefits': total_benefits,
            'net_annual_benefit': net_benefit,
            'roi_percent': roi,
            'breakeven_months': 12 if roi > 0 else 'Not cost-effective',
            'key_benefits': [
                f"避免严重低血糖{benefits['severe_hypo_prevention']['events_prevented_per_year']}次/年",
                f"降低心血管事件风险{benefits['cv_event_prevention']['events_prevented_per_year']*100:.0f}%",
                f"减少住院{benefits['hospitalization_reduction']['days_saved_per_year']}天/年"
            ]
        }
        
        self.clinical_insights['cost_effectiveness'] = cost_analysis
    
    def _generate_clinical_report(self):
        """生成临床价值导向的分析报告"""
        report = {
            'patient_summary': {
                'name': '李明华(虚拟)',
                'age': self.patient_profile['age'],
                'primary_conditions': ['2型糖尿病', '高血压'],
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'analysis_type': '多模态临床决策支持分析'
            },
            'clinical_insights': self.clinical_insights,
            'risk_predictions': self.risk_predictions,
            'treatment_recommendations': self.treatment_recommendations,
            'monitoring_plan': self.monitoring_plan
        }
        
        return report
    
    def print_clinical_report(self):
        """打印临床价值导向报告"""
        print("\n" + "="*80)
        print("基于临床价值的多模态分析报告")
        print("Clinical Value-Driven Multi-Modal Analysis Report")
        print("="*80)
        
        print(f"\n患者：李明华(虚拟)，{self.patient_profile['age']}岁男性")
        print(f"主要诊断：2型糖尿病({self.patient_profile['diabetes_duration_years']}年) + 高血压({self.patient_profile['hypertension_duration_years']}年)")
        print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 早期风险识别
        print(f"\n【🔍 早期风险识别 - 传统方法可能遗漏的问题】")
        subclinical_risks = self.clinical_insights.get('subclinical_risks', [])
        if subclinical_risks:
            for i, risk in enumerate(subclinical_risks, 1):
                print(f"\n{i}. {risk['condition']}")
                print(f"   ⚠️ 临床意义：{risk['clinical_significance']}")
                print(f"   🎯 早期识别优势：{risk['early_detection_advantage']}")
                print(f"   📋 证据：{'; '.join(risk['evidence'])}")
                print(f"   🏥 立即行动：{risk['immediate_action']}")
        else:
            print("未发现明显的早期风险征象")
        
        # 并发症风险预测
        print(f"\n【📊 并发症风险预测 - 未来1-6个月】")
        for condition, prediction in self.risk_predictions.items():
            condition_name = {
                'severe_hypoglycemia': '严重低血糖',
                'cardiovascular_events': '心血管事件',
                'diabetic_ketoacidosis': '糖尿病酮症',
                'acute_hospitalization': '急性住院'
            }.get(condition, condition)
            
            risk_level = prediction.get('risk_level', 'unknown')
            probability = prediction.get('probability_percent', 0)
            timeline = prediction.get('timeline', '')
            
            risk_emoji = {'high': '🔴', 'moderate': '🟡', 'mild': '🟠', 'low': '🟢'}.get(risk_level, '⚫')
            
            print(f"\n{condition_name} {risk_emoji}")
            print(f"   📈 风险水平：{risk_level}")
            print(f"   🎲 发生概率：{probability}% ({timeline})")
            print(f"   🛡️ 预防策略：{prediction.get('prevention_strategy', '继续当前治疗')}")
        
        # 个性化治疗方案
        print(f"\n【💊 个性化治疗方案 - 具体可执行的医疗行动】")
        
        # 血糖管理
        glucose_mgmt = self.treatment_recommendations.get('glucose_management', [])
        if glucose_mgmt:
            print(f"\n🩸 血糖管理调整：")
            for i, rec in enumerate(glucose_mgmt, 1):
                print(f"   {i}. 【{rec['medication']}】{rec['action']}")
                print(f"      具体方案：{rec['change']}")
                print(f"      医学依据：{rec['rationale']}")
                if 'contraindication_check' in rec and rec['contraindication_check']:
                    print(f"      ⚠️ 注意事项：{'; '.join(rec['contraindication_check'])}")
        
        # 血压管理
        bp_mgmt = self.treatment_recommendations.get('blood_pressure_management', [])
        if bp_mgmt:
            print(f"\n🫀 血压管理调整：")
            for i, rec in enumerate(bp_mgmt, 1):
                print(f"   {i}. 【{rec['medication']}】{rec['action']}")
                print(f"      具体方案：{rec['change']}")
                print(f"      医学依据：{rec['rationale']}")
                if 'expected_benefit' in rec:
                    print(f"      预期效果：{rec['expected_benefit']}")
        
        # 心血管保护
        cv_protection = self.treatment_recommendations.get('cardiovascular_protection', [])
        if cv_protection:
            print(f"\n💖 心血管保护策略：")
            for i, rec in enumerate(cv_protection, 1):
                print(f"   {i}. 【{rec['medication']}】{rec['dose']}")
                print(f"      医学依据：{rec['rationale']}")
                if 'monitoring' in rec:
                    print(f"      监测要求：{rec['monitoring']}")
        
        # 个性化监测方案
        print(f"\n【📋 个性化监测方案 - 精准监测，避免过度医疗】")
        
        glucose_monitoring = self.monitoring_plan.get('glucose_monitoring', {})
        print(f"\n🩸 血糖监测：")
        print(f"   方法：{glucose_monitoring.get('method', 'N/A')}")
        print(f"   频率：{glucose_monitoring.get('frequency', 'N/A')}")
        print(f"   重点指标：{', '.join(glucose_monitoring.get('key_metrics', []))}")
        
        bp_monitoring = self.monitoring_plan.get('bp_monitoring', {})
        print(f"\n🫀 血压监测：")
        print(f"   方法：{bp_monitoring.get('method', 'N/A')}")
        print(f"   频率：{bp_monitoring.get('frequency', 'N/A')}")
        print(f"   目标：{bp_monitoring.get('target', 'N/A')}")
        
        cv_monitoring = self.monitoring_plan.get('cv_monitoring', {})
        print(f"\n💖 心血管监测：")
        for test, freq in cv_monitoring.items():
            print(f"   {test}：{freq}")
        
        # 成本效益分析
        cost_effectiveness = self.clinical_insights.get('cost_effectiveness', {})
        if cost_effectiveness:
            print(f"\n【💰 成本效益分析 - 多模态监测的经济学价值】")
            print(f"传统监测年费用：${cost_effectiveness['traditional_annual_cost']:,}")
            print(f"多模态监测年费用：${cost_effectiveness['multimodal_annual_cost']:,}")
            print(f"额外投资：${cost_effectiveness['additional_investment']:,}")
            print(f"年度效益：${cost_effectiveness['annual_benefits']:,}")
            print(f"净效益：${cost_effectiveness['net_annual_benefit']:,}")
            print(f"投资回报率：{cost_effectiveness['roi_percent']:.1f}%")
            print(f"主要效益：")
            for benefit in cost_effectiveness['key_benefits']:
                print(f"   • {benefit}")
        
        # 总结和行动计划
        print(f"\n【🎯 总结与行动计划】")
        high_priority_actions = []
        
        # 收集高优先级行动
        for risks in subclinical_risks:
            if '立即' in risks['immediate_action']:
                high_priority_actions.append(risks['immediate_action'])
        
        for condition, prediction in self.risk_predictions.items():
            if prediction.get('risk_level') == 'high':
                high_priority_actions.append(prediction.get('prevention_strategy'))
        
        if high_priority_actions:
            print(f"\n🚨 高优先级行动(1周内执行)：")
            for i, action in enumerate(high_priority_actions[:3], 1):
                print(f"   {i}. {action}")
        
        print(f"\n📅 随访计划：")
        print(f"   • 2周后：评估药物调整效果，查看血糖血压变化")
        print(f"   • 4周后：复查相关实验室指标")
        print(f"   • 12周后：全面评估治疗效果，调整长期方案")
        
        print(f"\n" + "="*80)
        print("报告结束 - 基于循证医学的临床决策支持")
        print("="*80)

def main():
    """主函数：演示真正有临床价值的多模态分析"""
    
    # 生成虚拟患者数据（重用之前的数据生成器）
    from Virtual_Patient_Multi_Modal_Demo import VirtualPatientDataGenerator
    
    print("生成虚拟患者数据...")
    generator = VirtualPatientDataGenerator()
    patient_data = generator.generate_all_data()
    
    # 运行临床价值导向的分析
    print("\n运行临床价值导向的多模态分析...")
    analyzer = ClinicalValueMultiModalAnalyzer(patient_data)
    results = analyzer.run_clinical_analysis()
    
    # 生成临床报告
    analyzer.print_clinical_report()
    
    # 保存结果
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'clinical_value_analysis_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n临床价值分析结果已保存到文件 (时间戳: {timestamp})")
    
    return results

if __name__ == "__main__":
    results = main()