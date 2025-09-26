#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于CGM数据的孕妇血糖分型和不良事件风险分层工具

作者: G+ Medical Platform
日期: 2025-01-09
版本: 1.0.0

功能:
1. CGM数据预处理和指标计算
2. 血糖分型分析
3. 多维度风险评估
4. 不良事件风险预测
5. 临床管理建议生成
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')


@dataclass
class CGMMetrics:
    """CGM指标数据类"""
    TIR: float  # 目标范围内时间百分比 (3.5-7.8 mmol/L)
    GMI: float  # 血糖管理指标
    CV: float   # 变异系数
    MAGE: float # 平均血糖变化幅度
    TAR_L1: float  # >7.8 mmol/L时间百分比
    TAR_L2: float  # >10.0 mmol/L时间百分比
    TBR_L1: float  # <3.9 mmol/L时间百分比
    TBR_L2: float  # <3.0 mmol/L时间百分比
    night_abnormal_pct: float  # 夜间血糖异常百分比
    rhythm_disruption: str     # 节律紊乱程度: "轻微", "中度", "严重"


@dataclass
class PatientFactors:
    """患者基础风险因素"""
    previous_gdm: bool = False      # 既往GDM史
    obesity: bool = False           # 肥胖(BMI≥28)
    advanced_age: bool = False      # 高龄(≥35岁)
    family_history: bool = False    # 家族史
    pcos: bool = False             # 多囊卵巢综合征
    hypertension: bool = False     # 高血压史


@dataclass
class RiskScores:
    """风险评分结果"""
    total_score: float
    control_score: float
    variability_score: float
    acute_score: float
    longterm_score: float
    risk_level: str
    risk_multiplier: float


class CGMProcessor:
    """CGM数据处理器"""
    
    @staticmethod
    def calculate_tir(glucose_values: List[float], 
                     target_range: Tuple[float, float] = (3.5, 7.8)) -> float:
        """计算目标范围内时间百分比"""
        if not glucose_values:
            return 0.0
        
        in_range = [target_range[0] <= val <= target_range[1] for val in glucose_values]
        return (sum(in_range) / len(glucose_values)) * 100
    
    @staticmethod
    def calculate_gmi(mean_glucose: float) -> float:
        """计算血糖管理指标 (GMI)"""
        # GMI(%) = 3.31 + 0.02392 × mean_glucose(mg/dL)
        # 转换mmol/L到mg/dL: mg/dL = mmol/L × 18.0182
        mean_glucose_mgdl = mean_glucose * 18.0182
        return 3.31 + 0.02392 * mean_glucose_mgdl
    
    @staticmethod
    def calculate_cv(glucose_values: List[float]) -> float:
        """计算变异系数"""
        if not glucose_values or len(glucose_values) < 2:
            return 0.0
        
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values, ddof=1)
        return (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0.0
    
    @staticmethod
    def calculate_mage(glucose_values: List[float], 
                      timestamps: List[datetime]) -> float:
        """计算平均血糖变化幅度 (MAGE)"""
        if len(glucose_values) < 3:
            return 0.0
        
        # 计算相邻血糖值的差值
        differences = []
        for i in range(1, len(glucose_values)):
            diff = abs(glucose_values[i] - glucose_values[i-1])
            differences.append(diff)
        
        if not differences:
            return 0.0
        
        # 计算标准差
        mean_diff = np.mean(differences)
        std_diff = np.std(differences, ddof=1)
        
        # MAGE: 大于1个标准差的血糖变化的平均值
        significant_changes = [diff for diff in differences if diff > std_diff]
        
        return np.mean(significant_changes) if significant_changes else 0.0
    
    @staticmethod
    def calculate_tar_tbr(glucose_values: List[float]) -> Dict[str, float]:
        """计算高血糖和低血糖时间百分比"""
        if not glucose_values:
            return {'TAR_L1': 0.0, 'TAR_L2': 0.0, 'TBR_L1': 0.0, 'TBR_L2': 0.0}
        
        total_points = len(glucose_values)
        
        # 高血糖时间
        tar_l1 = sum(1 for val in glucose_values if val > 7.8) / total_points * 100
        tar_l2 = sum(1 for val in glucose_values if val > 10.0) / total_points * 100
        
        # 低血糖时间
        tbr_l1 = sum(1 for val in glucose_values if val < 3.9) / total_points * 100
        tbr_l2 = sum(1 for val in glucose_values if val < 3.0) / total_points * 100
        
        return {
            'TAR_L1': tar_l1,
            'TAR_L2': tar_l2,
            'TBR_L1': tbr_l1,
            'TBR_L2': tbr_l2
        }
    
    @staticmethod
    def analyze_night_pattern(glucose_values: List[float], 
                            timestamps: List[datetime]) -> Tuple[float, str]:
        """分析夜间血糖模式"""
        if len(glucose_values) != len(timestamps):
            return 0.0, "轻微"
        
        # 夜间时间定义为22:00-06:00
        night_values = []
        for i, ts in enumerate(timestamps):
            hour = ts.hour
            if hour >= 22 or hour <= 6:
                night_values.append(glucose_values[i])
        
        if not night_values:
            return 0.0, "轻微"
        
        # 计算夜间血糖异常百分比 (超出3.9-7.8范围)
        abnormal_count = sum(1 for val in night_values 
                           if val < 3.9 or val > 7.8)
        abnormal_pct = (abnormal_count / len(night_values)) * 100
        
        # 判断节律紊乱程度
        if abnormal_pct < 5:
            rhythm_disruption = "轻微"
        elif abnormal_pct < 15:
            rhythm_disruption = "中度"
        else:
            rhythm_disruption = "严重"
        
        return abnormal_pct, rhythm_disruption
    
    def process_cgm_data(self, glucose_values: List[float], 
                        timestamps: List[datetime]) -> CGMMetrics:
        """处理CGM数据并计算所有指标"""
        if not glucose_values or not timestamps:
            raise ValueError("血糖数据和时间戳不能为空")
        
        if len(glucose_values) != len(timestamps):
            raise ValueError("血糖数据和时间戳长度不匹配")
        
        # 计算基础指标
        tir = self.calculate_tir(glucose_values)
        mean_glucose = np.mean(glucose_values)
        gmi = self.calculate_gmi(mean_glucose)
        cv = self.calculate_cv(glucose_values)
        mage = self.calculate_mage(glucose_values, timestamps)
        
        # 计算高低血糖时间
        tar_tbr = self.calculate_tar_tbr(glucose_values)
        
        # 分析夜间模式
        night_abnormal_pct, rhythm_disruption = self.analyze_night_pattern(
            glucose_values, timestamps)
        
        return CGMMetrics(
            TIR=tir,
            GMI=gmi,
            CV=cv,
            MAGE=mage,
            TAR_L1=tar_tbr['TAR_L1'],
            TAR_L2=tar_tbr['TAR_L2'],
            TBR_L1=tar_tbr['TBR_L1'],
            TBR_L2=tar_tbr['TBR_L2'],
            night_abnormal_pct=night_abnormal_pct,
            rhythm_disruption=rhythm_disruption
        )


class CGMClassifier:
    """CGM血糖分型器"""
    
    def classify_glucose_control(self, tir: float, gmi: float) -> Dict[str, Any]:
        """血糖控制质量分型"""
        if tir >= 80 and gmi < 6.0:
            return {
                'type': '理想控制型',
                'level': 'Optimal',
                'risk_level': '低风险',
                'description': '血糖稳定在目标范围'
            }
        elif tir >= 70 and gmi < 6.5:
            return {
                'type': '良好控制型',
                'level': 'Good',
                'risk_level': '低-中风险',
                'description': '轻微超标，整体可控'
            }
        elif tir >= 50 and gmi < 7.0:
            return {
                'type': '一般控制型',
                'level': 'Fair',
                'risk_level': '中风险',
                'description': '经常超出目标范围'
            }
        else:
            return {
                'type': '控制不佳型',
                'level': 'Poor',
                'risk_level': '高风险',
                'description': '大部分时间血糖异常'
            }
    
    def classify_variability(self, cv: float, mage: float) -> Dict[str, Any]:
        """血糖变异性分型"""
        if cv < 25 and mage < 3.0:
            return {
                'type': '稳定波动型',
                'level': 'Stable',
                'risk_level': '低风险',
                'description': '血糖波动小，稳定'
            }
        elif cv < 36 and mage < 4.5:
            return {
                'type': '中等波动型',
                'level': 'Moderate',
                'risk_level': '中风险',
                'description': '血糖有一定波动'
            }
        elif cv < 50 and mage < 6.0:
            return {
                'type': '高度波动型',
                'level': 'High',
                'risk_level': '高风险',
                'description': '血糖波动明显'
            }
        else:
            return {
                'type': '极不稳定型',
                'level': 'Unstable',
                'risk_level': '极高风险',
                'description': '血糖极不稳定'
            }
    
    def classify_hyperglycemia_pattern(self, tar_l1: float, tar_l2: float) -> Dict[str, Any]:
        """高血糖模式分型"""
        if tar_l1 > 15 and tar_l2 < 5:
            return {
                'type': '餐后高峰型',
                'level': 'Postprandial',
                'clinical_meaning': '胰岛素抵抗为主',
                'description': '主要为餐后血糖升高'
            }
        elif tar_l1 > 25 and tar_l2 > 10:
            return {
                'type': '持续高血糖型',
                'level': 'Sustained',
                'clinical_meaning': 'β细胞功能不足',
                'description': '持续性血糖升高'
            }
        elif tar_l1 > 10 and tar_l2 < 3:
            return {
                'type': '夜间高血糖型',
                'level': 'Nocturnal',
                'clinical_meaning': '基础胰岛素不足',
                'description': '夜间为主的血糖升高'
            }
        elif tar_l1 > 20 and tar_l2 > 5:
            return {
                'type': '混合高血糖型',
                'level': 'Mixed',
                'clinical_meaning': '综合性糖代谢异常',
                'description': '多时段血糖升高'
            }
        else:
            return {
                'type': '无明显高血糖型',
                'level': 'Normal',
                'clinical_meaning': '血糖控制良好',
                'description': '无明显高血糖模式'
            }
    
    def classify_hypoglycemia_risk(self, tbr_l1: float, tbr_l2: float) -> Dict[str, Any]:
        """低血糖风险分型"""
        if tbr_l1 < 1 and tbr_l2 < 0.1:
            return {
                'type': '无低血糖型',
                'level': 'None',
                'risk_level': '标准管理',
                'description': '很少低血糖'
            }
        elif tbr_l1 < 4 and tbr_l2 < 0.5:
            return {
                'type': '轻微低血糖型',
                'level': 'Mild',
                'risk_level': '饮食调整',
                'description': '偶发轻度低血糖'
            }
        elif tbr_l1 <= 4 and tbr_l2 < 1:
            return {
                'type': '中度低血糖型',
                'level': 'Moderate',
                'risk_level': '密切监测',
                'description': '明显低血糖风险'
            }
        else:
            return {
                'type': '高危低血糖型',
                'level': 'High-risk',
                'risk_level': '紧急干预',
                'description': '严重低血糖风险'
            }
    
    def get_comprehensive_classification(self, metrics: CGMMetrics) -> Dict[str, Any]:
        """综合分型评估"""
        control_class = self.classify_glucose_control(metrics.TIR, metrics.GMI)
        variability_class = self.classify_variability(metrics.CV, metrics.MAGE)
        hyper_class = self.classify_hyperglycemia_pattern(metrics.TAR_L1, metrics.TAR_L2)
        hypo_class = self.classify_hypoglycemia_risk(metrics.TBR_L1, metrics.TBR_L2)
        
        # 确定综合分型
        if (control_class['level'] == 'Optimal' and 
            variability_class['level'] == 'Stable'):
            comprehensive_type = 'A型-理想稳定'
            risk_level = '极低'
        elif (control_class['level'] == 'Good' and 
              variability_class['level'] in ['Stable', 'Moderate']):
            comprehensive_type = 'B型-良好控制'
            risk_level = '低'
        elif (control_class['level'] == 'Fair' and 
              hyper_class['level'] == 'Postprandial'):
            comprehensive_type = 'C型-餐后失控'
            risk_level = '中等'
        elif (control_class['level'] == 'Poor' and 
              hyper_class['level'] == 'Sustained'):
            comprehensive_type = 'D型-持续高血糖'
            risk_level = '高'
        elif hyper_class['level'] == 'Nocturnal':
            comprehensive_type = 'E型-夜间异常'
            risk_level = '中-高'
        elif variability_class['level'] == 'Unstable':
            comprehensive_type = 'F型-极不稳定'
            risk_level = '极高'
        else:
            comprehensive_type = 'B型-良好控制'  # 默认分型
            risk_level = '低'
        
        return {
            'comprehensive_type': comprehensive_type,
            'risk_level': risk_level,
            'control_classification': control_class,
            'variability_classification': variability_class,
            'hyperglycemia_classification': hyper_class,
            'hypoglycemia_classification': hypo_class
        }


class RiskAssessment:
    """风险评估器"""
    
    def normalize_glucose_control(self, tir: float, gmi: float) -> float:
        """血糖控制质量标准化 (35%权重)"""
        # TIR评分 (1-5分)
        if tir >= 80:
            tir_score = 1
        elif tir >= 70:
            tir_score = 2
        elif tir >= 50:
            tir_score = 3
        else:
            tir_score = 5
        
        # GMI评分 (1-5分)
        if gmi < 6.0:
            gmi_score = 1
        elif gmi < 6.5:
            gmi_score = 2
        elif gmi < 7.0:
            gmi_score = 3
        else:
            gmi_score = 5
        
        return (tir_score + gmi_score) / 2  # 1-5分
    
    def normalize_variability(self, cv: float, mage: float) -> float:
        """血糖变异性标准化 (30%权重)"""
        # CV评分
        if cv < 25:
            cv_score = 1
        elif cv < 36:
            cv_score = 2
        elif cv < 50:
            cv_score = 4
        else:
            cv_score = 6
        
        # MAGE评分
        if mage < 3.0:
            mage_score = 1
        elif mage < 4.5:
            mage_score = 2
        elif mage < 6.0:
            mage_score = 4
        else:
            mage_score = 6
        
        return (cv_score + mage_score) / 2  # 1-6分
    
    def normalize_acute_risk(self, tar_l1: float, tar_l2: float, 
                           tbr_l1: float, tbr_l2: float) -> float:
        """急性风险标准化 (25%权重)"""
        # 高血糖评分
        tar_total = tar_l1 + tar_l2
        if tar_total < 10:
            tar_score = 1
        elif tar_total < 25:
            tar_score = 2
        elif tar_total < 40:
            tar_score = 4
        else:
            tar_score = 6
        
        # 低血糖评分
        tbr_total = tbr_l1 + tbr_l2
        if tbr_total < 1:
            tbr_score = 1
        elif tbr_total < 4:
            tbr_score = 2
        elif tbr_total < 8:
            tbr_score = 4
        else:
            tbr_score = 6
        
        return max(tar_score, tbr_score)  # 取较高风险，1-6分
    
    def normalize_longterm_risk(self, night_abnormal_pct: float, 
                              rhythm_disruption: str) -> float:
        """长期风险标准化 (10%权重)"""
        if night_abnormal_pct < 5 and rhythm_disruption == "轻微":
            return 1
        elif night_abnormal_pct < 15 and rhythm_disruption == "中度":
            return 2
        else:
            return 3  # 1-3分
    
    def calculate_risk_scores(self, metrics: CGMMetrics) -> RiskScores:
        """计算风险评分"""
        # 各维度标准化评分
        control_score = self.normalize_glucose_control(metrics.TIR, metrics.GMI)
        variability_score = self.normalize_variability(metrics.CV, metrics.MAGE)
        acute_score = self.normalize_acute_risk(
            metrics.TAR_L1, metrics.TAR_L2, metrics.TBR_L1, metrics.TBR_L2)
        longterm_score = self.normalize_longterm_risk(
            metrics.night_abnormal_pct, metrics.rhythm_disruption)
        
        # 加权综合评分
        total_score = (control_score * 0.35 + 
                      variability_score * 0.30 + 
                      acute_score * 0.25 + 
                      longterm_score * 0.10)
        
        # 确定风险等级
        if total_score <= 2.5:
            risk_level = "绿级-低风险"
            risk_multiplier = 1.0
        elif total_score <= 4.5:
            risk_level = "黄级-中风险"
            risk_multiplier = 2.0
        elif total_score <= 6.0:
            risk_level = "橙级-高风险"
            risk_multiplier = 3.5
        else:
            risk_level = "红级-极高风险"
            risk_multiplier = 5.0
        
        return RiskScores(
            total_score=round(total_score, 2),
            control_score=control_score,
            variability_score=variability_score,
            acute_score=acute_score,
            longterm_score=longterm_score,
            risk_level=risk_level,
            risk_multiplier=risk_multiplier
        )
    
    def get_management_recommendations(self, risk_scores: RiskScores) -> Dict[str, str]:
        """获取管理建议"""
        risk_level = risk_scores.risk_level
        
        if risk_level == "绿级-低风险":
            return {
                '监测频率': '标准产检',
                '血糖监测': '每周2-3天CGM',
                '专科会诊': '不需要',
                '药物治疗': '生活方式干预',
                '分娩管理': '标准管理',
                '随访计划': '常规产后随访'
            }
        elif risk_level == "黄级-中风险":
            return {
                '监测频率': '每2周产检',
                '血糖监测': '连续CGM监测',
                '专科会诊': '内分泌科会诊',
                '药物治疗': '考虑胰岛素治疗',
                '分娩管理': '密切监护',
                '随访计划': '产后6周、3月、6月随访'
            }
        elif risk_level == "橙级-高风险":
            return {
                '监测频率': '每周产检',
                '血糖监测': '连续CGM+每日血糖',
                '专科会诊': '内分泌+产科联合管理',
                '药物治疗': '胰岛素强化治疗',
                '分娩管理': '提前入院，专人监护',
                '随访计划': '产后密切随访，长期代谢监测'
            }
        else:  # 红级-极高风险
            return {
                '监测频率': '每周2次或住院',
                '血糖监测': '实时CGM+频繁指血',
                '专科会诊': 'MDT多学科会诊',
                '药物治疗': '胰岛素泵或强化方案',
                '分娩管理': '住院管理，NICU准备',
                '随访计划': '产后住院观察，长期专科随访'
            }
    
    def predict_adverse_outcomes(self, risk_scores: RiskScores, 
                               patient_factors: Optional[PatientFactors] = None) -> Dict[str, float]:
        """预测不良事件风险"""
        base_multiplier = risk_scores.risk_multiplier
        
        # 基础风险调整因子
        adjustment_factor = 1.0
        if patient_factors:
            if patient_factors.previous_gdm:
                adjustment_factor *= 1.5
            if patient_factors.obesity:
                adjustment_factor *= 1.3
            if patient_factors.advanced_age:
                adjustment_factor *= 1.2
            if patient_factors.family_history:
                adjustment_factor *= 1.1
            if patient_factors.pcos:
                adjustment_factor *= 1.2
            if patient_factors.hypertension:
                adjustment_factor *= 1.1
        
        final_multiplier = base_multiplier * adjustment_factor
        
        # 各类不良事件风险预测 (基础风险 × 风险倍数)
        predictions = {
            '巨大儿风险': min(final_multiplier * 0.15, 0.85),
            '新生儿低血糖风险': min(final_multiplier * 0.10, 0.70),
            '剖宫产风险': min(final_multiplier * 0.25, 0.90),
            '产后糖尿病风险': min(final_multiplier * 0.08, 0.60),
            '妊娠高血压风险': min(final_multiplier * 0.12, 0.75),
            '子痫前期风险': min(final_multiplier * 0.06, 0.50),
            '新生儿NICU入住风险': min(final_multiplier * 0.12, 0.65),
            '新生儿黄疸风险': min(final_multiplier * 0.20, 0.80)
        }
        
        # 转换为百分比格式
        return {k: round(v * 100, 1) for k, v in predictions.items()}


class CGMRiskAssessmentTool:
    """CGM风险评估工具主类"""
    
    def __init__(self):
        self.processor = CGMProcessor()
        self.classifier = CGMClassifier()
        self.risk_assessor = RiskAssessment()
    
    def assess_patient(self, glucose_values: List[float], 
                      timestamps: List[datetime],
                      patient_factors: Optional[PatientFactors] = None) -> Dict[str, Any]:
        """完整的患者评估"""
        try:
            # 1. 处理CGM数据
            metrics = self.processor.process_cgm_data(glucose_values, timestamps)
            
            # 2. 血糖分型
            classification = self.classifier.get_comprehensive_classification(metrics)
            
            # 3. 风险评估
            risk_scores = self.risk_assessor.calculate_risk_scores(metrics)
            
            # 4. 管理建议
            management = self.risk_assessor.get_management_recommendations(risk_scores)
            
            # 5. 不良事件预测
            adverse_outcomes = self.risk_assessor.predict_adverse_outcomes(
                risk_scores, patient_factors)
            
            # 6. 生成报告
            report = self._generate_report(
                metrics, classification, risk_scores, management, adverse_outcomes)
            
            return {
                'success': True,
                'metrics': metrics.__dict__,
                'classification': classification,
                'risk_scores': risk_scores.__dict__,
                'management_recommendations': management,
                'adverse_outcome_predictions': adverse_outcomes,
                'report': report
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '评估过程中发生错误，请检查输入数据'
            }
    
    def _generate_report(self, metrics: CGMMetrics, classification: Dict,
                        risk_scores: RiskScores, management: Dict,
                        adverse_outcomes: Dict) -> str:
        """生成评估报告"""
        report = f"""
=== CGM血糖分型和风险评估报告 ===

【CGM指标】
• 目标范围内时间(TIR): {metrics.TIR:.1f}%
• 血糖管理指标(GMI): {metrics.GMI:.1f}%
• 变异系数(CV): {metrics.CV:.1f}%
• 平均血糖变化幅度(MAGE): {metrics.MAGE:.1f} mmol/L
• 高血糖时间(TAR L1/L2): {metrics.TAR_L1:.1f}% / {metrics.TAR_L2:.1f}%
• 低血糖时间(TBR L1/L2): {metrics.TBR_L1:.1f}% / {metrics.TBR_L2:.1f}%

【血糖分型】
• 综合分型: {classification['comprehensive_type']}
• 控制质量: {classification['control_classification']['type']}
• 变异性: {classification['variability_classification']['type']}
• 高血糖模式: {classification['hyperglycemia_classification']['type']}
• 低血糖风险: {classification['hypoglycemia_classification']['type']}

【风险评估】
• 总体风险评分: {risk_scores.total_score}分
• 风险等级: {risk_scores.risk_level}
• 血糖控制评分: {risk_scores.control_score}分 (权重35%)
• 变异性评分: {risk_scores.variability_score}分 (权重30%)
• 急性风险评分: {risk_scores.acute_score}分 (权重25%)
• 长期风险评分: {risk_scores.longterm_score}分 (权重10%)

【不良事件风险预测】
"""
        for outcome, risk in adverse_outcomes.items():
            report += f"• {outcome}: {risk}%\n"
        
        report += f"""
【管理建议】
"""
        for category, recommendation in management.items():
            report += f"• {category}: {recommendation}\n"
        
        report += f"""
【评估时间】{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report
    
    def batch_assess(self, patients_data: List[Dict]) -> List[Dict]:
        """批量评估多个患者"""
        results = []
        for i, patient_data in enumerate(patients_data):
            try:
                glucose_values = patient_data['glucose_values']
                timestamps = patient_data['timestamps']
                patient_factors = patient_data.get('patient_factors')
                
                result = self.assess_patient(glucose_values, timestamps, patient_factors)
                result['patient_id'] = patient_data.get('patient_id', f'Patient_{i+1}')
                results.append(result)
                
            except Exception as e:
                results.append({
                    'patient_id': patient_data.get('patient_id', f'Patient_{i+1}'),
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def export_results(self, results: Dict, format: str = 'json', 
                      filename: Optional[str] = None) -> str:
        """导出评估结果"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cgm_assessment_{timestamp}"
        
        if format.lower() == 'json':
            output_file = f"{filename}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        elif format.lower() == 'txt':
            output_file = f"{filename}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                if 'report' in results:
                    f.write(results['report'])
                else:
                    f.write(str(results))
        else:
            raise ValueError("支持的格式: 'json', 'txt'")
        
        return output_file


def demo_usage():
    """演示用法"""
    print("=== CGM血糖分型和风险评估工具演示 ===\n")
    
    # 创建工具实例
    tool = CGMRiskAssessmentTool()
    
    # 模拟CGM数据 (14天，每5分钟一个点)
    np.random.seed(42)
    total_points = 14 * 24 * 12  # 14天 × 24小时 × 12个点/小时
    
    # 生成模拟血糖数据 (mmol/L)
    base_glucose = 7.0
    glucose_values = []
    timestamps = []
    
    start_time = datetime(2025, 1, 1, 0, 0, 0)
    
    for i in range(total_points):
        # 模拟生理性血糖波动
        time_of_day = (i % (24 * 12)) / 12  # 小时
        
        # 基础波动
        daily_pattern = 1.0 + 0.3 * np.sin(2 * np.pi * time_of_day / 24)
        
        # 餐后血糖升高 (假设6点、12点、18点用餐)
        meal_times = [6, 12, 18]
        meal_effect = 0
        for meal_time in meal_times:
            time_since_meal = abs(time_of_day - meal_time)
            if time_since_meal < 2:  # 餐后2小时内
                meal_effect += 2.0 * np.exp(-time_since_meal)
        
        # 添加随机噪声
        noise = np.random.normal(0, 0.5)
        
        glucose = base_glucose * daily_pattern + meal_effect + noise
        glucose = max(3.0, min(15.0, glucose))  # 限制在合理范围内
        
        glucose_values.append(glucose)
        timestamps.append(start_time + timedelta(minutes=i*5))
    
    # 创建患者基础因素
    patient_factors = PatientFactors(
        previous_gdm=False,
        obesity=True,
        advanced_age=True,
        family_history=True,
        pcos=False,
        hypertension=False
    )
    
    # 执行评估
    print("正在处理CGM数据并进行风险评估...")
    result = tool.assess_patient(glucose_values, timestamps, patient_factors)
    
    if result['success']:
        print("评估完成！\n")
        print(result['report'])
        
        # 导出结果
        output_file = tool.export_results(result, 'json', 'demo_result')
        print(f"\n结果已导出到: {output_file}")
        
    else:
        print(f"评估失败: {result['error']}")


if __name__ == "__main__":
    demo_usage()