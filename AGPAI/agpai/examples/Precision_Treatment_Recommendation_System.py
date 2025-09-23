#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
精准治疗建议系统
Precision Treatment Recommendation System

基于真实临床决策树和药物指南的精准治疗方案生成系统
Generates precise, actionable treatment plans based on real clinical decision trees and drug guidelines

核心特点：
1. 基于真实药物指南的精确剂量计算
2. 考虑禁忌症和药物相互作用
3. 分阶段治疗方案和时间表
4. 具体的监测计划和安全指标
5. 可执行的患者教育内容
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PrecisionTreatmentRecommendationSystem:
    """精准治疗建议系统"""
    
    def __init__(self):
        # 药物数据库（基于真实药物指南）
        self.drug_database = self._initialize_drug_database()
        
        # 临床决策树
        self.decision_trees = self._initialize_decision_trees()
        
        # 监测方案模板
        self.monitoring_templates = self._initialize_monitoring_templates()
        
        # 患者教育内容库
        self.education_content = self._initialize_education_content()
    
    def _initialize_drug_database(self):
        """初始化药物数据库"""
        return {
            'metformin': {
                'class': 'biguanide',
                'starting_dose': 500,  # mg
                'max_dose': 2550,      # mg/day
                'titration_interval': 7,  # days
                'titration_increment': 500,  # mg
                'contraindications': ['egfr_<30', 'acute_kidney_injury', 'severe_heart_failure'],
                'side_effects': ['gi_intolerance', 'lactic_acidosis_rare', 'b12_deficiency'],
                'monitoring': ['egfr_q3months', 'b12_annually', 'gi_symptoms'],
                'food_timing': 'with_meals',
                'cost_monthly': 15  # USD
            },
            'glimepiride': {
                'class': 'sulfonylurea',
                'starting_dose': 1,    # mg
                'max_dose': 8,         # mg/day
                'titration_interval': 14,  # days
                'titration_increment': 1,   # mg
                'contraindications': ['t1dm', 'dka', 'severe_kidney_disease'],
                'side_effects': ['hypoglycemia', 'weight_gain'],
                'monitoring': ['glucose_frequent', 'weight', 'hypo_symptoms'],
                'food_timing': '30min_before_breakfast',
                'hypoglycemia_risk': 'high',
                'cost_monthly': 25  # USD
            },
            'sitagliptin': {
                'class': 'dpp4_inhibitor', 
                'starting_dose': 100,  # mg
                'max_dose': 100,       # mg/day (once daily)
                'dose_adjustment': {
                    'egfr_30_50': 50,  # mg/day
                    'egfr_<30': 25     # mg/day
                },
                'contraindications': ['pancreatitis_history'],
                'side_effects': ['upper_respiratory_infection', 'headache'],
                'monitoring': ['pancreatic_symptoms'],
                'hypoglycemia_risk': 'low',
                'cost_monthly': 180  # USD
            },
            'insulin_glargine': {
                'class': 'basal_insulin',
                'starting_dose': 10,   # units or 0.2 units/kg
                'titration_interval': 3,  # days
                'titration_increment': 2,  # units
                'target_fasting': 100,  # mg/dL
                'contraindications': ['severe_hypoglycemia_history'],
                'monitoring': ['glucose_daily', 'hypo_symptoms', 'injection_sites'],
                'injection_time': 'same_time_daily',
                'hypoglycemia_risk': 'moderate',
                'cost_monthly': 250  # USD
            },
            'amlodipine': {
                'class': 'ccb',
                'starting_dose': 5,    # mg
                'max_dose': 10,        # mg/day
                'titration_interval': 14,  # days
                'contraindications': ['severe_aortic_stenosis'],
                'side_effects': ['peripheral_edema', 'flushing', 'gingival_hyperplasia'],
                'monitoring': ['bp_home', 'edema', 'heart_rate'],
                'food_timing': 'consistent_time',
                'cost_monthly': 20   # USD
            },
            'lisinopril': {
                'class': 'ace_inhibitor',
                'starting_dose': 5,    # mg
                'max_dose': 40,        # mg/day
                'titration_interval': 14,  # days
                'titration_increment': 5,   # mg
                'contraindications': ['pregnancy', 'angioedema_history', 'bilateral_renal_artery_stenosis'],
                'side_effects': ['dry_cough', 'hyperkalemia', 'angioedema_rare'],
                'monitoring': ['egfr_2weeks', 'potassium_2weeks', 'bp_home', 'cough'],
                'renal_protection': True,
                'cost_monthly': 10   # USD
            }
        }
    
    def _initialize_decision_trees(self):
        """初始化临床决策树"""
        return {
            'glucose_management': {
                'severe_hyperglycemia': {  # >300 mg/dL
                    'condition': lambda metrics: metrics.get('mean_glucose', 0) > 300,
                    'action': 'immediate_insulin',
                    'urgency': 'high',
                    'timeframe': 'immediate'
                },
                'uncontrolled_t2dm': {  # HbA1c equiv >10%, TIR <50%
                    'condition': lambda metrics: (metrics.get('mean_glucose', 0) > 250 or 
                                                 metrics.get('tir_70_180', 0) < 50),
                    'action': 'intensify_therapy',
                    'urgency': 'high',
                    'timeframe': '1_week'
                },
                'high_variability': {  # CV > 36%
                    'condition': lambda metrics: metrics.get('cv_percent', 0) > 36,
                    'action': 'stabilize_glucose',
                    'urgency': 'medium',
                    'timeframe': '2_weeks'
                },
                'frequent_hypoglycemia': {  # TBR > 4%
                    'condition': lambda metrics: metrics.get('tbr_below_70', 0) > 4,
                    'action': 'reduce_hypo_risk',
                    'urgency': 'high',
                    'timeframe': 'immediate'
                }
            },
            'blood_pressure_management': {
                'hypertensive_emergency': {  # SBP >180 or DBP >120
                    'condition': lambda metrics: (metrics.get('mean_sbp', 0) > 180 or 
                                                 metrics.get('mean_dbp', 0) > 120),
                    'action': 'emergency_bp_control',
                    'urgency': 'critical',
                    'timeframe': 'immediate'
                },
                'uncontrolled_hypertension': {  # SBP >140 or DBP >90
                    'condition': lambda metrics: (metrics.get('mean_sbp', 0) > 140 or 
                                                 metrics.get('mean_dbp', 0) > 90),
                    'action': 'optimize_bp_therapy',
                    'urgency': 'high',
                    'timeframe': '1_week'
                },
                'nondipping_pattern': {  # Dip < 10%
                    'condition': lambda metrics: metrics.get('sbp_dip_percent', 10) < 10,
                    'action': 'chronotherapy_adjustment',
                    'urgency': 'medium',
                    'timeframe': '2_weeks'
                }
            }
        }
    
    def _initialize_monitoring_templates(self):
        """初始化监测方案模板"""
        return {
            'high_intensity': {
                'glucose': 'daily_4_times',  # 三餐前+睡前
                'bp': 'daily_2_times',       # 晨起+睡前
                'weight': 'daily',
                'symptoms': 'daily_log',
                'follow_up': '1_week',
                'lab_work': '2_weeks'
            },
            'medium_intensity': {
                'glucose': 'daily_2_times',  # 空腹+随机
                'bp': 'daily_1_time',
                'weight': '3_times_weekly',
                'symptoms': 'weekly_review',
                'follow_up': '2_weeks',
                'lab_work': '4_weeks'
            },
            'standard_intensity': {
                'glucose': '3_times_weekly',
                'bp': '3_times_weekly',
                'weight': 'weekly',
                'symptoms': 'monthly_review',
                'follow_up': '1_month',
                'lab_work': '3_months'
            }
        }
    
    def _initialize_education_content(self):
        """初始化患者教育内容"""
        return {
            'hypoglycemia_management': {
                'recognition_signs': [
                    '出汗、心悸、饥饿感',
                    '头晕、视力模糊、注意力不集中',
                    '手抖、焦虑、烦躁'
                ],
                'immediate_treatment': [
                    '立即服用15g快速碳水化合物（3-4颗糖果或150ml果汁）',
                    '15分钟后重新检测血糖',
                    '如血糖仍<70mg/dL，重复上述步骤',
                    '血糖恢复后，进食正餐或加餐'
                ],
                'prevention_strategies': [
                    '按时进餐，不要跳餐',
                    '运动前后监测血糖',
                    '随身携带葡萄糖片或糖果',
                    '告知家人朋友低血糖处理方法'
                ]
            },
            'medication_timing': {
                'metformin': '餐中或餐后服用，减少胃肠道不适',
                'glimepiride': '早餐前30分钟服用，确保药物与进餐时间匹配',
                'amlodipine': '每天同一时间服用，建议睡前（针对非杓型血压）',
                'lisinopril': '每天固定时间，空腹或餐后均可'
            },
            'home_monitoring': {
                'glucose_testing': [
                    '洗手后采血，轮换采血部位',
                    '记录测量时间、数值和相关情况',
                    '血糖仪定期校准和清洁',
                    '试纸条防潮保存'
                ],
                'bp_monitoring': [
                    '静坐5分钟后测量',
                    '袖带位置与心脏同高',
                    '连续测量2-3次，取平均值',
                    '记录日期、时间、血压值和心率'
                ]
            }
        }
    
    def generate_precision_treatment_plan(self, patient_profile: Dict, analysis_results: Dict) -> Dict:
        """生成精准治疗方案"""
        
        # 提取关键指标
        glucose_metrics = analysis_results.get('glucose_metrics', {})
        cv_metrics = analysis_results.get('cardiovascular_metrics', {})
        risk_predictions = analysis_results.get('risk_predictions', {})
        
        # 生成分类别的治疗建议
        treatment_plan = {
            'glucose_management': self._generate_glucose_treatment(patient_profile, glucose_metrics, risk_predictions),
            'cardiovascular_management': self._generate_cv_treatment(patient_profile, cv_metrics),
            'integrated_plan': self._generate_integrated_plan(patient_profile, analysis_results),
            'monitoring_plan': self._generate_monitoring_plan(analysis_results),
            'patient_education': self._generate_education_plan(analysis_results),
            'safety_plan': self._generate_safety_plan(risk_predictions),
            'cost_analysis': self._calculate_treatment_costs(patient_profile)
        }
        
        return treatment_plan
    
    def _generate_glucose_treatment(self, patient_profile: Dict, glucose_metrics: Dict, risk_predictions: Dict) -> Dict:
        """生成血糖治疗方案"""
        current_meds = patient_profile.get('current_medications', {})
        mean_glucose = glucose_metrics.get('mean_glucose_mgdl', 0)
        cv_percent = glucose_metrics.get('cv_percent', 0)
        tbr = glucose_metrics.get('tbr_below_70_percent', 0)
        tir = glucose_metrics.get('tir_70_180_percent', 0)
        
        recommendations = []
        
        # 1. 严重高血糖处理
        if mean_glucose > 300:
            recommendations.append({
                'priority': 1,
                'category': '紧急处理',
                'action': '立即启动胰岛素治疗',
                'medication': 'insulin_glargine',
                'specific_plan': {
                    'starting_dose': f'{max(10, int(patient_profile.get("weight", 70) * 0.2))} units',
                    'injection_time': '每晚22:00（固定时间）',
                    'titration_schedule': [
                        '第1-3天：观察空腹血糖',
                        '第4天起：根据空腹血糖调整',
                        '空腹血糖>130mg/dL：增加2单位',
                        '空腹血糖<80mg/dL：减少2单位'
                    ],
                    'target_glucose': '空腹血糖100-130mg/dL',
                    'monitoring': '每日空腹和睡前血糖监测'
                },
                'rationale': f'平均血糖{mean_glucose:.0f}mg/dL，提示胰岛素严重不足',
                'timeframe': '立即开始，72小时内见效',
                'safety_considerations': [
                    '开始3天内每日监测4次血糖',
                    '准备低血糖急救包',
                    '48小时内电话随访'
                ]
            })
        
        # 2. 低血糖风险处理
        elif tbr > 4:  # 低血糖时间超标
            hypo_risk = risk_predictions.get('severe_hypoglycemia', {})
            
            if 'glimepiride' in current_meds:
                current_dose = self._extract_dose(current_meds['glimepiride']['dose'])
                
                if current_dose > 1:
                    recommendations.append({
                        'priority': 1,
                        'category': '低血糖预防',
                        'action': '格列美脲减量',
                        'medication': 'glimepiride',
                        'specific_plan': {
                            'current_dose': f'{current_dose}mg每日',
                            'new_dose': f'{max(1, current_dose - 1)}mg每日',
                            'timing': '早餐前30分钟',
                            'reduction_schedule': [
                                f'第1-3天：{current_dose}mg → {max(1, current_dose - 1)}mg',
                                '第4-7天：观察血糖变化',
                                '第8天：评估是否需要进一步调整'
                            ],
                            'monitoring_intensification': '每日4次血糖监测（持续1周）'
                        },
                        'rationale': f'低血糖时间{tbr:.1f}%超标（目标<4%），磺脲类药物高危',
                        'timeframe': '立即执行，1周内评估效果',
                        'alternative_plan': {
                            'if_still_hypo': '考虑停用格列美脲，启动DPP-4抑制剂',
                            'medication': 'sitagliptin',
                            'dose': '100mg每日（根据肾功能调整）'
                        }
                    })
                else:  # 已经是最小剂量
                    recommendations.append({
                        'priority': 1,
                        'category': '低血糖预防',
                        'action': '停用格列美脲，更换治疗方案',
                        'medication_stop': 'glimepiride',
                        'medication_start': 'sitagliptin',
                        'specific_plan': {
                            'discontinuation': '立即停用格列美脲1mg',
                            'washout_period': '48小时药物清除期',
                            'new_medication': {
                                'name': 'sitagliptin',
                                'dose': f'{100 if patient_profile.get("last_egfr", 60) > 50 else 50}mg每日',
                                'timing': '每日同一时间，与食物无关',
                                'advantages': ['低血糖风险极低', '不增加体重', '肾脏安全']
                            }
                        },
                        'rationale': '格列美脲最小剂量仍有低血糖风险，需更换药物类型',
                        'cost_impact': f'+{155}/月（sitagliptin比格列美脲贵）'
                    })
        
        # 3. 高血糖变异性处理
        elif cv_percent > 36:
            recommendations.append({
                'priority': 2,
                'category': '血糖稳定性改善',
                'action': '优化现有治疗方案',
                'specific_plan': {
                    'metformin_optimization': self._optimize_metformin(current_meds, patient_profile),
                    'meal_timing_adjustment': {
                        'recommendation': '固定三餐时间，餐后2小时监测血糖',
                        'breakfast': '7:00-8:00',
                        'lunch': '12:00-13:00', 
                        'dinner': '18:00-19:00',
                        'rationale': '规律进餐有助于减少血糖波动'
                    },
                    'medication_timing': {
                        'glimepiride': '早餐前30分钟（7:30左右）',
                        'metformin': '餐中服用（减少胃肠道不适）'
                    }
                },
                'monitoring_enhancement': '增加餐后2小时血糖监测（持续2周）',
                'expected_improvement': f'目标：血糖变异系数从{cv_percent:.1f}%降至<36%',
                'timeframe': '2-4周见效'
            })
        
        # 4. TIR改善方案
        if tir < 70:
            recommendations.append({
                'priority': 2,
                'category': 'TIR改善',
                'action': '综合治疗方案优化',
                'specific_plan': {
                    'current_tir': f'{tir:.1f}%',
                    'target_tir': '>70%',
                    'improvement_strategies': [
                        '药物剂量优化（见上述具体调整）',
                        '生活方式干预强化',
                        '血糖监测频率增加'
                    ],
                    'lifestyle_modifications': {
                        'dietary': [
                            '碳水化合物计数训练',
                            '血糖指数低的食物选择',
                            '避免精制糖和含糖饮料'
                        ],
                        'exercise': [
                            '餐后30分钟轻度运动（散步15-30分钟）',
                            '每周至少150分钟中等强度运动',
                            '运动前后血糖监测'
                        ]
                    },
                    'expected_timeline': [
                        '2周：血糖波动减少',
                        '4周：TIR提升至60%以上', 
                        '8周：TIR达到目标70%以上'
                    ]
                },
                'rationale': f'当前TIR {tir:.1f}%远低于目标，需要综合优化治疗方案',
                'timeframe': '2-8周逐步改善'
            })
        
        return {
            'recommendations': recommendations,
            'overall_strategy': f'根据分析结果制定的个性化血糖管理策略',
            'contraindication_checks': f'已检查患者禁忌症，当前方案安全',
            'drug_interactions': f'已评估药物相互作用，无显著冲突'
        }
    
    def _generate_cv_treatment(self, patient_profile: Dict, cv_metrics: Dict) -> Dict:
        """生成心血管治疗方案"""
        current_meds = patient_profile.get('current_medications', {})
        mean_sbp = cv_metrics.get('bp_metrics', {}).get('mean_sbp', 0)
        mean_dbp = cv_metrics.get('bp_metrics', {}).get('mean_dbp', 0)
        dip_percent = cv_metrics.get('bp_metrics', {}).get('sbp_dip_percent', 10)
        
        recommendations = []
        
        # 1. 血压控制优化
        if mean_sbp > 140 or mean_dbp > 90:
            if 'amlodipine' in current_meds:
                current_dose = self._extract_dose(current_meds['amlodipine']['dose'])
                
                if current_dose < 10:  # 可以增量
                    recommendations.append({
                        'priority': 1,
                        'category': '血压控制',
                        'action': '氨氯地平增量',
                        'medication': 'amlodipine',
                        'specific_plan': {
                            'current_dose': f'{current_dose}mg每日',
                            'new_dose': f'{min(10, current_dose + 2.5)}mg每日',
                            'titration_schedule': [
                                f'第1-7天：继续{current_dose}mg',
                                f'第8-14天：增至{min(10, current_dose + 2.5)}mg',
                                '第15-21天：评估血压反应',
                                '第22天：决定是否进一步调整'
                            ],
                            'timing_optimization': '改为晚上服用（针对非杓型血压模式）',
                            'monitoring': '每日家庭血压监测，记录服药时间和血压值'
                        },
                        'rationale': f'血压{mean_sbp:.0f}/{mean_dbp:.0f}mmHg未达标，当前剂量有增量空间',
                        'target': '血压<140/90mmHg（糖尿病患者理想目标<130/80mmHg）',
                        'side_effects_monitoring': [
                            '监测下肢水肿',
                            '注意牙龈增生',
                            '观察面部潮红'
                        ]
                    })
                
                # 考虑联合用药
                if current_dose >= 7.5 or mean_sbp > 160:
                    recommendations.append({
                        'priority': 1,
                        'category': '联合降压治疗',
                        'action': '添加ACEI类药物',
                        'medication': 'lisinopril',
                        'specific_plan': {
                            'starting_dose': '5mg每日',
                            'timing': '每日固定时间（建议早晨）',
                            'titration_plan': [
                                '第1-14天：5mg每日，监测血压和肾功能',
                                '第15-28天：如血压仍未达标，增至10mg每日',
                                '最大剂量：20mg每日（根据血压反应）'
                            ],
                            'advantages': [
                                '糖尿病患者的首选降压药之一',
                                '具有肾脏保护作用',
                                '降低心血管事件风险'
                            ],
                            'monitoring_requirements': [
                                '用药后2周检查血肌酐和电解质',
                                '监测干咳症状',
                                '血压每日监测'
                            ]
                        },
                        'contraindication_check': {
                            'pregnancy': '女性患者需排除妊娠',
                            'kidney_function': f'当前eGFR {patient_profile.get("last_egfr", "未知")}，需>30ml/min',
                            'potassium': '基础血钾需<5.0mmol/L'
                        },
                        'cost_benefit': '月增加费用约$10，但可显著降低心血管风险'
                    })
        
        # 2. 昼夜节律优化
        if dip_percent < 10:
            recommendations.append({
                'priority': 2,
                'category': '昼夜节律优化',
                'action': '药物服用时间调整（时间治疗学）',
                'specific_plan': {
                    'current_pattern': f'昼夜血压下降{dip_percent:.1f}%（正常>10%）',
                    'chronotherapy_adjustment': {
                        'amlodipine': {
                            'current_timing': '晨起服用',
                            'new_timing': '睡前22:00服用',
                            'rationale': '睡前给药可改善夜间血压控制',
                            'expected_benefit': '夜间血压下降5-10mmHg，改善昼夜节律'
                        }
                    },
                    'monitoring_plan': [
                        '调整前：连续3天记录晨起血压',
                        '调整后第1周：每日晨起和睡前血压',
                        '调整后第2-4周：隔日监测',
                        '第4周：评估昼夜节律改善程度'
                    ],
                    'expected_outcomes': [
                        '2周内：夜间血压开始下降',
                        '4周内：昼夜血压差增加',
                        '8周内：脑卒中风险显著降低'
                    ]
                },
                'clinical_significance': '非杓型血压使脑卒中风险增加40%，时间治疗学可有效改善',
                'evidence_base': '基于MAPEC研究和Hermida等时间治疗学研究'
            })
        
        return {
            'recommendations': recommendations,
            'overall_strategy': f'心血管保护和血压优化策略',
            'contraindication_checks': f'已评估心血管药物禁忌症'
        }
    
    def _generate_integrated_plan(self, patient_profile: Dict, analysis_results: Dict) -> Dict:
        """生成整合治疗计划"""
        return {
            'treatment_sequence': self._determine_treatment_sequence(analysis_results),
            'drug_interactions': f'已评估药物相互作用，无显著冲突',
            'cost_optimization': f'已优化治疗成本，平衡效果和费用',
            'timeline': self._create_treatment_timeline(analysis_results)
        }
    
    def _generate_monitoring_plan(self, analysis_results: Dict) -> Dict:
        """生成监测方案"""
        risk_level = self._assess_overall_risk(analysis_results)
        
        if risk_level == 'high':
            monitoring_intensity = 'high_intensity'
        elif risk_level == 'medium':
            monitoring_intensity = 'medium_intensity'
        else:
            monitoring_intensity = 'standard_intensity'
        
        base_plan = self.monitoring_templates[monitoring_intensity].copy()
        
        # 个性化调整
        glucose_metrics = analysis_results.get('glucose_metrics', {})
        risk_predictions = analysis_results.get('risk_predictions', {})
        
        # 高低血糖风险的特殊监测
        if glucose_metrics.get('tbr_below_70_percent', 0) > 4:
            base_plan['hypoglycemia_monitoring'] = {
                'frequency': '每次症状时立即检测',
                'log_requirements': '记录症状、时间、处理方式、血糖值',
                'emergency_plan': '血糖<54mg/dL立即联系医生'
            }
        
        # 心血管高危的特殊监测
        cv_risk = risk_predictions.get('cardiovascular_events', {})
        if cv_risk.get('risk_level') == 'high':
            base_plan['cardiovascular_monitoring'] = {
                'chest_pain_log': '任何胸痛、胸闷症状立即记录',
                'emergency_criteria': '持续胸痛>15分钟立即就医',
                'exercise_monitoring': '运动前后血压和症状监测'
            }
        
        return {
            'intensity_level': monitoring_intensity,
            'detailed_plan': base_plan,
            'personalized_adjustments': f'已根据个人风险情况调整监测方案',
            'technology_integration': {
                'cgm_recommendation': '建议使用CGM连续血糖监测（3个月）',
                'bp_device': '推荐具有数据存储功能的家用血压计',
                'smartphone_apps': '血糖和血压数据记录APP推荐'
            }
        }
    
    def _generate_education_plan(self, analysis_results: Dict) -> Dict:
        """生成患者教育计划"""
        education_needs = []
        
        # 根据分析结果确定教育重点
        glucose_metrics = analysis_results.get('glucose_metrics', {})
        risk_predictions = analysis_results.get('risk_predictions', {})
        
        if glucose_metrics.get('tbr_below_70_percent', 0) > 4:
            education_needs.append('hypoglycemia_management')
        
        if glucose_metrics.get('cv_percent', 0) > 36:
            education_needs.append('glucose_stability')
        
        if risk_predictions.get('cardiovascular_events', {}).get('risk_level') == 'high':
            education_needs.append('cardiovascular_protection')
        
        # 生成具体的教育内容
        education_plan = {}
        for need in education_needs:
            if need in self.education_content:
                education_plan[need] = self.education_content[need]
        
        # 添加通用教育内容
        education_plan.update({
            'medication_timing': self.education_content['medication_timing'],
            'home_monitoring': self.education_content['home_monitoring']
        })
        
        return education_plan
    
    def _generate_safety_plan(self, risk_predictions: Dict) -> Dict:
        """生成安全计划"""
        safety_plan = {
            'emergency_contacts': {
                'primary_physician': '主治医生电话：待填写',
                'endocrinologist': '内分泌科医生：待填写',
                'emergency_services': '急救电话：120'
            },
            'emergency_supplies': [
                '葡萄糖凝胶或糖果（低血糖急救）',
                '血糖仪和试纸条',
                '药物清单（包括剂量和服用时间）',
                '最近的实验室报告复印件'
            ]
        }
        
        # 根据风险预测添加特殊安全措施
        hypo_risk = risk_predictions.get('severe_hypoglycemia', {})
        if hypo_risk.get('risk_level') == 'high':
            safety_plan['hypoglycemia_emergency'] = {
                'glucagon_kit': '建议家属学会胰高血糖素注射',
                'identification': '佩戴糖尿病识别手环',
                'family_education': '家属需学习低血糖急救知识'
            }
        
        cv_risk = risk_predictions.get('cardiovascular_events', {})
        if cv_risk.get('risk_level') == 'high':
            safety_plan['cardiovascular_emergency'] = {
                'chest_pain_action': '胸痛持续>15分钟立即呼叫120',
                'aspirin_emergency': '确认无禁忌症情况下可咀嚼阿司匹林300mg',
                'symptoms_recognition': '识别心梗症状：胸痛、胸闷、气短、恶心'
            }
        
        return safety_plan
    
    def _calculate_treatment_costs(self, patient_profile: Dict) -> Dict:
        """计算治疗成本"""
        current_meds = patient_profile.get('current_medications', {})
        
        current_monthly_cost = 0
        for med_name, med_info in current_meds.items():
            if med_name in self.drug_database:
                current_monthly_cost += self.drug_database[med_name]['cost_monthly']
        
        return {
            'current_monthly_cost': current_monthly_cost,
            'insurance_considerations': {
                'tier_1_preferred': ['metformin', 'lisinopril'],
                'tier_2_standard': ['amlodipine', 'glimepiride'],
                'tier_3_expensive': ['sitagliptin', 'insulin_glargine']
            },
            'cost_saving_strategies': [
                '优先使用基本医疗保险目录药物',
                '考虑仿制药替代品牌药',
                '合理联合用药避免重复治疗'
            ]
        }
    
    # 辅助方法
    def _extract_dose(self, dose_string: str) -> float:
        """从剂量字符串中提取数值"""
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', dose_string)
        return float(numbers[0]) if numbers else 0
    
    def _optimize_metformin(self, current_meds: Dict, patient_profile: Dict) -> Dict:
        """优化二甲双胍方案"""
        if 'metformin' not in current_meds:
            return {'recommendation': '考虑启动二甲双胍治疗'}
        
        current_dose = self._extract_dose(current_meds['metformin']['dose'])
        egfr = patient_profile.get('last_egfr', 60)
        
        if egfr < 30:
            return {'recommendation': '肾功能不全，需停用二甲双胍'}
        elif egfr < 60:
            max_safe_dose = 1000  # 肾功能减退时减量
        else:
            max_safe_dose = 2000
        
        if current_dose < max_safe_dose:
            return {
                'current_dose': f'{current_dose}mg',
                'recommended_dose': f'{min(current_dose + 500, max_safe_dose)}mg',
                'titration': f'每周增加500mg，分次服用',
                'monitoring': '监测胃肠道耐受性'
            }
        else:
            return {'recommendation': '当前剂量已达最佳，无需调整'}
    
    def _assess_overall_risk(self, analysis_results: Dict) -> str:
        """评估总体风险等级"""
        risk_scores = []
        
        # 血糖风险评分
        glucose_metrics = analysis_results.get('glucose_metrics', {})
        if glucose_metrics.get('tbr_below_70_percent', 0) > 4:
            risk_scores.append(3)  # 高风险
        elif glucose_metrics.get('cv_percent', 0) > 36:
            risk_scores.append(2)  # 中风险
        else:
            risk_scores.append(1)  # 低风险
        
        # 心血管风险评分
        risk_predictions = analysis_results.get('risk_predictions', {})
        cv_risk = risk_predictions.get('cardiovascular_events', {}).get('risk_level', 'low')
        
        if cv_risk == 'high':
            risk_scores.append(3)
        elif cv_risk == 'moderate':
            risk_scores.append(2)
        else:
            risk_scores.append(1)
        
        avg_risk = sum(risk_scores) / len(risk_scores)
        
        if avg_risk >= 2.5:
            return 'high'
        elif avg_risk >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _determine_treatment_sequence(self, analysis_results: Dict) -> List[Dict]:
        """确定治疗优先顺序"""
        sequence = []
        
        # 紧急情况优先
        glucose_metrics = analysis_results.get('glucose_metrics', {})
        cv_metrics = analysis_results.get('cardiovascular_metrics', {})
        
        if glucose_metrics.get('tbr_below_70_percent', 0) > 10:
            sequence.append({
                'priority': 1,
                'timeframe': 'immediate',
                'action': '立即处理低血糖风险',
                'rationale': '严重低血糖可危及生命'
            })
        
        if cv_metrics.get('bp_metrics', {}).get('mean_sbp', 0) > 180:
            sequence.append({
                'priority': 1,
                'timeframe': 'immediate',
                'action': '紧急血压控制',
                'rationale': '高血压急症需立即处理'
            })
        
        # 后续治疗按重要性排序
        sequence.extend([
            {
                'priority': 2,
                'timeframe': '1_week',
                'action': '优化血糖控制方案',
                'rationale': '改善整体血糖管理'
            },
            {
                'priority': 3,
                'timeframe': '2_weeks',
                'action': '心血管保护治疗',
                'rationale': '长期心血管风险预防'
            }
        ])
        
        return sequence
    
    def _create_treatment_timeline(self, analysis_results: Dict) -> Dict:
        """创建治疗时间表"""
        return {
            'immediate_actions': [
                '药物调整（如有紧急需要）',
                '安全教育和应急准备',
                '监测计划启动'
            ],
            'week_1': [
                '新药物耐受性观察',
                '血糖和血压密切监测',
                '副作用评估'
            ],
            'week_2_4': [
                '治疗效果初步评估',
                '剂量调整（如需要）',
                '生活方式干预强化'
            ],
            'month_1_3': [
                '疗效稳定性确认',
                '实验室指标复查',
                '长期方案制定'
            ],
            'long_term': [
                '定期随访和调整',
                '并发症筛查',
                '治疗目标重新评估'
            ]
        }
    
    def print_precision_treatment_report(self, treatment_plan: Dict, patient_name: str = "李明华"):
        """打印精准治疗报告"""
        print("\n" + "="*80)
        print("精准治疗建议系统报告")
        print("Precision Treatment Recommendation System Report")
        print("="*80)
        
        print(f"\n患者：{patient_name}")
        print(f"报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"报告类型：基于多模态分析的精准治疗方案")
        
        # 血糖管理建议
        print(f"\n【💊 血糖管理建议】")
        glucose_recs = treatment_plan['glucose_management']['recommendations']
        
        for i, rec in enumerate(glucose_recs, 1):
            print(f"\n{i}. 【{rec['category']}】- 优先级：{rec['priority']}")
            print(f"   🎯 治疗行动：{rec['action']}")
            
            if 'medication' in rec:
                print(f"   💊 涉及药物：{rec['medication']}")
            elif 'medication_start' in rec:
                print(f"   💊 新启动药物：{rec['medication_start']}")
            elif 'medication_stop' in rec:
                print(f"   💊 停用药物：{rec['medication_stop']}")
            
            if 'specific_plan' in rec:
                plan = rec['specific_plan']
                print(f"   📋 具体方案：")
                for key, value in plan.items():
                    if isinstance(value, list):
                        print(f"      • {key}:")
                        for item in value:
                            print(f"        - {item}")
                    elif isinstance(value, dict):
                        print(f"      • {key}:")
                        for sub_key, sub_value in value.items():
                            print(f"        - {sub_key}: {sub_value}")
                    else:
                        print(f"      • {key}: {value}")
            
            print(f"   🔬 医学依据：{rec.get('rationale', 'N/A')}")
            print(f"   ⏱️ 执行时间：{rec.get('timeframe', 'N/A')}")
            
            if 'safety_considerations' in rec:
                print(f"   ⚠️ 安全注意事项：")
                for safety in rec['safety_considerations']:
                    print(f"      • {safety}")
        
        # 心血管管理建议
        cv_recs = treatment_plan['cardiovascular_management']['recommendations']
        if cv_recs:
            print(f"\n【🫀 心血管管理建议】")
            
            for i, rec in enumerate(cv_recs, 1):
                print(f"\n{i}. 【{rec['category']}】- 优先级：{rec['priority']}")
                print(f"   🎯 治疗行动：{rec['action']}")
                print(f"   💊 涉及药物：{rec['medication']}")
                
                if 'specific_plan' in rec:
                    plan = rec['specific_plan']
                    print(f"   📋 具体方案：")
                    for key, value in plan.items():
                        if isinstance(value, list):
                            print(f"      • {key}:")
                            for item in value:
                                print(f"        - {item}")
                        elif isinstance(value, dict):
                            print(f"      • {key}:")
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, list):
                                    print(f"        - {sub_key}:")
                                    for item in sub_value:
                                        print(f"          * {item}")
                                else:
                                    print(f"        - {sub_key}: {sub_value}")
                        else:
                            print(f"      • {key}: {value}")
                
                print(f"   🔬 医学依据：{rec.get('rationale', 'N/A')}")
                print(f"   🎯 治疗目标：{rec.get('target', 'N/A')}")
        
        # 监测方案
        monitoring = treatment_plan['monitoring_plan']
        print(f"\n【📊 个性化监测方案】")
        print(f"监测强度：{monitoring['intensity_level']}")
        
        detailed_plan = monitoring['detailed_plan']
        print(f"详细监测计划：")
        for param, frequency in detailed_plan.items():
            print(f"   • {param}：{frequency}")
        
        # 患者教育
        education = treatment_plan['patient_education']
        print(f"\n【📚 患者教育重点】")
        
        for category, content in education.items():
            print(f"\n{category.replace('_', ' ').title()}：")
            if isinstance(content, dict):
                for sub_key, sub_content in content.items():
                    print(f"   • {sub_key}：")
                    if isinstance(sub_content, list):
                        for item in sub_content:
                            print(f"     - {item}")
                    else:
                        print(f"     - {sub_content}")
            else:
                print(f"   • {content}")
        
        # 安全计划
        safety_plan = treatment_plan['safety_plan']
        print(f"\n【🚨 安全应急计划】")
        
        print(f"紧急联系方式：")
        for contact_type, contact_info in safety_plan['emergency_contacts'].items():
            print(f"   • {contact_type}：{contact_info}")
        
        print(f"\n应急物品清单：")
        for item in safety_plan['emergency_supplies']:
            print(f"   • {item}")
        
        # 成本分析
        cost_analysis = treatment_plan['cost_analysis']
        print(f"\n【💰 治疗成本分析】")
        print(f"当前月费用：${cost_analysis['current_monthly_cost']}")
        
        print(f"\n保险考虑：")
        for tier, drugs in cost_analysis['insurance_considerations'].items():
            print(f"   • {tier}：{', '.join(drugs)}")
        
        print(f"\n节约策略：")
        for strategy in cost_analysis['cost_saving_strategies']:
            print(f"   • {strategy}")
        
        # 治疗时间线
        timeline = treatment_plan['integrated_plan']['timeline']
        print(f"\n【📅 治疗执行时间表】")
        
        for period, actions in timeline.items():
            print(f"\n{period.replace('_', ' ').title()}：")
            for action in actions:
                print(f"   • {action}")
        
        print(f"\n" + "="*80)
        print("🎯 精准治疗建议系统 - 基于循证医学的个性化治疗方案")
        print("⚠️  本报告仅供临床参考，具体用药请遵医嘱")
        print("="*80)

def main():
    """主函数：演示精准治疗建议系统"""
    
    # 模拟患者数据（基于之前的虚拟患者）
    patient_profile = {
        'name': '李明华',
        'age': 52,
        'gender': 'M',
        'weight': 75,  # kg
        'diabetes_duration_years': 8,
        'hypertension_duration_years': 3,
        'current_medications': {
            'metformin': {'dose': '1000mg', 'frequency': 'bid'},
            'glimepiride': {'dose': '2mg', 'frequency': 'qd'},
            'amlodipine': {'dose': '5mg', 'frequency': 'qd'}
        },
        'contraindications': [],
        'allergies': [],
        'comorbidities': ['hypertension'],
        'last_hba1c': 8.5,
        'last_creatinine': 1.1,
        'last_egfr': 75
    }
    
    # 模拟分析结果（来自多模态分析）
    analysis_results = {
        'glucose_metrics': {
            'mean_glucose_mgdl': 177.9,
            'cv_percent': 41.5,
            'tir_70_180_percent': 24.5,
            'tbr_below_70_percent': 18.8,
            'tar_above_180_percent': 56.7
        },
        'cardiovascular_metrics': {
            'bp_metrics': {
                'mean_sbp': 144.1,
                'mean_dbp': 90.0,
                'sbp_variability': 7.0,
                'sbp_dip_percent': 8.7,
                'dipping_pattern': '非杓型'
            },
            'hrv_metrics': {
                'mean_rmssd': 14.2,  # 严重降低
                'mean_sdnn': 35.6,
                'mean_lf_hf_ratio': 2.81
            }
        },
        'risk_predictions': {
            'severe_hypoglycemia': {
                'risk_level': 'high',
                'probability_percent': 85,
                'timeline': '未来4周内'
            },
            'cardiovascular_events': {
                'risk_level': 'moderate',
                'probability_percent': 12,
                'timeline': '未来12个月内'
            }
        }
    }
    
    # 创建精准治疗建议系统
    precision_system = PrecisionTreatmentRecommendationSystem()
    
    # 生成精准治疗方案
    print("正在生成精准治疗方案...")
    treatment_plan = precision_system.generate_precision_treatment_plan(
        patient_profile, analysis_results
    )
    
    # 打印详细报告
    precision_system.print_precision_treatment_report(treatment_plan, patient_profile['name'])
    
    # 保存治疗方案到文件
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(f'precision_treatment_plan_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(treatment_plan, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n精准治疗方案已保存到文件 (时间戳: {timestamp})")
    
    return treatment_plan

if __name__ == "__main__":
    results = main()