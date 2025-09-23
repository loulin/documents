#!/usr/bin/env python3
"""
临床智慧集成系统 - 将专家临床经验融入算法
解决V4.0缺乏临床判断能力的问题
"""

import numpy as np
from typing import Dict, List, Tuple, Optional

class ClinicalWisdomEngine:
    """临床智慧引擎 - 集成专家经验"""
    
    def __init__(self):
        # 年龄相关的诊断调整规则
        self.age_adjustment_rules = {
            'elderly_threshold': 65,
            'young_threshold': 18,
            
            # 老年人特殊考虑
            'elderly_adjustments': {
                'st_tolerance': 1.3,  # ST段异常阈值放宽30%
                'qrs_tolerance': 1.1,  # QRS增宽阈值放宽10%
                'arrhythmia_significance': 0.8,  # 心律失常重要性降低20%
                'common_findings': ['窦性心动过缓', '束支阻滞']  # 老年人常见
            },
            
            # 年轻人特殊考虑
            'young_adjustments': {
                'st_tolerance': 0.8,  # ST段异常阈值更严格
                'qrs_tolerance': 0.9,  # QRS增宽阈值更严格
                'arrhythmia_significance': 1.2,  # 心律失常更重要
                'rare_findings': ['束支阻滞', '心房颤动']  # 年轻人少见，需高置信度
            }
        }
        
        # 性别相关的诊断调整
        self.gender_adjustment_rules = {
            'male_patterns': {
                'rbbb_prevalence': 1.2,  # 男性右束支阻滞更常见
                'mi_risk_factor': 1.1,   # 男性心梗风险稍高
            },
            'female_patterns': {
                'qt_prolongation': 1.1,  # 女性QT间期延长更常见
                'functional_changes': 1.2  # 功能性改变更常见
            }
        }
        
        # 多导联一致性验证规则
        self.multi_lead_validation = {
            'critical_diagnoses': ['心肌缺血', '急性心梗', '左束支阻滞'],
            'required_lead_agreement': {
                '心肌缺血': 0.75,  # 需要75%导联一致
                '右束支阻滞': 0.6,   # 需要60%导联一致
                '左束支阻滞': 0.8,   # 需要80%导联一致
                '心房颤动': 0.5      # 心房颤动可能导联差异大
            },
            'lead_groups': {
                'inferior': ['II', 'III', 'aVF'],
                'lateral': ['I', 'aVL', 'V5', 'V6'],
                'anterior': ['V1', 'V2', 'V3', 'V4'],
                'septal': ['V1', 'V2']
            }
        }
        
        # 临床context优先级规则
        self.clinical_priority_rules = {
            # 高优先级：需要立即关注
            'high_priority': {
                'diagnoses': ['急性心梗', '心房颤动', '室性心动过速', '完全性房室阻滞'],
                'confidence_boost': 0.1,  # 提高10%置信度
                'specificity_requirement': 0.95  # 需要95%特异性
            },
            
            # 中等优先级：需要进一步评估
            'medium_priority': {
                'diagnoses': ['心肌缺血', '左束支阻滞', '房性心律失常'],
                'confidence_boost': 0.05,
                'specificity_requirement': 0.85
            },
            
            # 低优先级：可能良性
            'low_priority': {
                'diagnoses': ['窦性心动过缓', '心电图异常', '右束支阻滞'],
                'confidence_boost': 0.0,
                'specificity_requirement': 0.75
            }
        }
    
    def apply_age_gender_adjustment(self, 
                                   diagnosis: str, 
                                   confidence: float,
                                   age: Optional[int] = None,
                                   gender: Optional[str] = None) -> Tuple[float, str]:
        """应用年龄性别调整"""
        adjusted_confidence = confidence
        adjustment_reason = ""
        
        if age is not None:
            if age >= self.age_adjustment_rules['elderly_threshold']:
                # 老年人调整
                elderly_adj = self.age_adjustment_rules['elderly_adjustments']
                
                if diagnosis in elderly_adj['common_findings']:
                    adjusted_confidence *= 1.1  # 常见诊断提高置信度
                    adjustment_reason += f"老年人常见({diagnosis}); "
                
                if diagnosis == '心肌缺血':
                    adjusted_confidence *= 0.9  # 老年人ST改变可能非特异性
                    adjustment_reason += "老年人ST改变特异性降低; "
                    
            elif age <= self.age_adjustment_rules['young_threshold']:
                # 年轻人调整
                young_adj = self.age_adjustment_rules['young_adjustments']
                
                if diagnosis in young_adj['rare_findings']:
                    adjusted_confidence *= 0.8  # 罕见诊断降低置信度
                    adjustment_reason += f"年轻人罕见({diagnosis}); "
        
        if gender:
            if gender.lower() in ['male', 'm', '男']:
                if diagnosis == '右束支阻滞':
                    adjusted_confidence *= self.gender_adjustment_rules['male_patterns']['rbbb_prevalence']
                    adjustment_reason += "男性RBBB患病率调整; "
                    
            elif gender.lower() in ['female', 'f', '女']:
                if '功能性' in diagnosis or diagnosis == '心电图异常':
                    adjusted_confidence *= self.gender_adjustment_rules['female_patterns']['functional_changes']
                    adjustment_reason += "女性功能性改变倾向; "
        
        return min(adjusted_confidence, 1.0), adjustment_reason
    
    def validate_multi_lead_consistency(self, 
                                      diagnosis: str,
                                      lead_findings: Dict[str, bool],
                                      lead_values: Dict[str, float]) -> Tuple[bool, float, str]:
        """多导联一致性验证"""
        
        if diagnosis not in self.multi_lead_validation['required_lead_agreement']:
            return True, 1.0, "无需多导联验证"
        
        required_agreement = self.multi_lead_validation['required_lead_agreement'][diagnosis]
        
        # 计算支持该诊断的导联比例
        supporting_leads = sum(1 for finding in lead_findings.values() if finding)
        total_leads = len(lead_findings)
        agreement_ratio = supporting_leads / total_leads if total_leads > 0 else 0
        
        is_consistent = agreement_ratio >= required_agreement
        
        # 特殊规则：某些诊断需要特定导联组合
        special_validation = self._apply_special_lead_rules(diagnosis, lead_findings, lead_values)
        
        validation_msg = f"导联一致性: {agreement_ratio:.2f} (需要: {required_agreement:.2f})"
        if special_validation['applied']:
            validation_msg += f"; {special_validation['message']}"
            is_consistent = is_consistent and special_validation['passed']
        
        return is_consistent, agreement_ratio, validation_msg
    
    def _apply_special_lead_rules(self, 
                                 diagnosis: str,
                                 lead_findings: Dict[str, bool],
                                 lead_values: Dict[str, float]) -> Dict:
        """应用特殊导联规则"""
        result = {'applied': False, 'passed': True, 'message': ''}
        
        if diagnosis == '下壁心肌缺血':
            # 下壁缺血必须在II, III, aVF中体现
            inferior_leads = self.multi_lead_validation['lead_groups']['inferior']
            inferior_positive = sum(1 for lead in inferior_leads 
                                  if lead in lead_findings and lead_findings[lead])
            
            if inferior_positive >= 2:  # 至少2个下壁导联阳性
                result = {'applied': True, 'passed': True, 'message': '下壁导联确认'}
            else:
                result = {'applied': True, 'passed': False, 'message': '下壁导联不支持'}
                
        elif diagnosis == '前壁心肌缺血':
            # 前壁缺血必须在V1-V4中体现
            anterior_leads = self.multi_lead_validation['lead_groups']['anterior']
            anterior_positive = sum(1 for lead in anterior_leads 
                                  if lead in lead_findings and lead_findings[lead])
            
            if anterior_positive >= 2:
                result = {'applied': True, 'passed': True, 'message': '前壁导联确认'}
            else:
                result = {'applied': True, 'passed': False, 'message': '前壁导联不支持'}
        
        return result
    
    def apply_clinical_priority_weighting(self, 
                                        diagnoses: List[str],
                                        confidences: List[float]) -> Tuple[List[str], List[float]]:
        """应用临床优先级加权"""
        
        adjusted_diagnoses = []
        adjusted_confidences = []
        
        for diagnosis, confidence in zip(diagnoses, confidences):
            # 确定诊断优先级
            priority_level = self._get_diagnosis_priority(diagnosis)
            
            # 应用优先级调整
            if priority_level in self.clinical_priority_rules:
                rules = self.clinical_priority_rules[priority_level]
                boost = rules['confidence_boost']
                min_specificity = rules['specificity_requirement']
                
                adjusted_confidence = confidence + boost
                
                # 检查是否满足特异性要求
                if adjusted_confidence >= min_specificity:
                    adjusted_diagnoses.append(diagnosis)
                    adjusted_confidences.append(min(adjusted_confidence, 1.0))
                else:
                    # 置信度不够，降级或移除
                    if priority_level == 'high_priority':
                        # 高优先级诊断降级为疑似
                        adjusted_diagnoses.append(f"疑似{diagnosis}")
                        adjusted_confidences.append(adjusted_confidence)
                    # 其他优先级诊断移除
            else:
                adjusted_diagnoses.append(diagnosis)
                adjusted_confidences.append(confidence)
        
        return adjusted_diagnoses, adjusted_confidences
    
    def _get_diagnosis_priority(self, diagnosis: str) -> str:
        """获取诊断优先级"""
        for priority, rules in self.clinical_priority_rules.items():
            if diagnosis in rules['diagnoses']:
                return priority
        return 'low_priority'  # 默认低优先级
    
    def generate_clinical_interpretation(self,
                                       diagnoses: List[str],
                                       confidences: List[float],
                                       patient_info: Dict = None) -> Dict:
        """生成临床解释"""
        
        age = patient_info.get('age') if patient_info else None
        gender = patient_info.get('gender') if patient_info else None
        
        interpretation = {
            'primary_diagnoses': [],
            'secondary_findings': [],
            'clinical_recommendations': [],
            'confidence_summary': {},
            'adjustments_applied': []
        }
        
        # 按临床重要性分类
        for diagnosis, confidence in zip(diagnoses, confidences):
            priority = self._get_diagnosis_priority(diagnosis)
            
            if priority == 'high_priority' and confidence >= 0.8:
                interpretation['primary_diagnoses'].append({
                    'diagnosis': diagnosis,
                    'confidence': confidence,
                    'clinical_significance': '需要立即关注'
                })
            else:
                interpretation['secondary_findings'].append({
                    'diagnosis': diagnosis,
                    'confidence': confidence,
                    'clinical_significance': f'{priority}优先级'
                })
        
        # 生成临床建议
        if interpretation['primary_diagnoses']:
            interpretation['clinical_recommendations'].append("建议进一步心电图检查或心脏专科会诊")
        
        if age and age >= 65 and any('心律失常' in d['diagnosis'] for d in interpretation['secondary_findings']):
            interpretation['clinical_recommendations'].append("老年患者心律失常，建议动态心电图监测")
        
        # 置信度摘要
        interpretation['confidence_summary'] = {
            'mean_confidence': np.mean(confidences),
            'high_confidence_count': sum(1 for c in confidences if c >= 0.8),
            'total_diagnoses': len(diagnoses)
        }
        
        return interpretation

def demonstrate_clinical_wisdom():
    """演示临床智慧引擎"""
    engine = ClinicalWisdomEngine()
    
    print("🧠 临床智慧引擎演示")
    print("=" * 50)
    
    # 示例：年龄性别调整
    print("\\n📊 年龄性别调整示例")
    adjusted_conf, reason = engine.apply_age_gender_adjustment(
        '右束支阻滞', 0.75, age=25, gender='male'
    )
    print(f"原始置信度: 0.75")
    print(f"调整后置信度: {adjusted_conf:.3f}")
    print(f"调整原因: {reason}")
    
    # 示例：多导联验证
    print("\\n📊 多导联一致性验证示例")
    lead_findings = {'I': True, 'II': True, 'III': False, 'V1': True, 'V4': False}
    lead_values = {'I': 0.15, 'II': 0.12, 'III': 0.05, 'V1': 0.18, 'V4': 0.08}
    
    is_consistent, ratio, msg = engine.validate_multi_lead_consistency(
        '心肌缺血', lead_findings, lead_values
    )
    print(f"一致性验证: {is_consistent}")
    print(f"一致性比率: {ratio:.3f}")
    print(f"验证信息: {msg}")
    
    # 示例：临床解释
    print("\\n📊 临床解释示例")
    diagnoses = ['心房颤动', '右束支阻滞', '窦性心律']
    confidences = [0.89, 0.76, 0.65]
    patient_info = {'age': 72, 'gender': 'male'}
    
    interpretation = engine.generate_clinical_interpretation(
        diagnoses, confidences, patient_info
    )
    
    print("主要诊断:")
    for diag in interpretation['primary_diagnoses']:
        print(f"  - {diag['diagnosis']} (置信度: {diag['confidence']:.3f}) - {diag['clinical_significance']}")
    
    print("次要发现:")
    for finding in interpretation['secondary_findings']:
        print(f"  - {finding['diagnosis']} (置信度: {finding['confidence']:.3f}) - {finding['clinical_significance']}")
    
    print("临床建议:")
    for rec in interpretation['clinical_recommendations']:
        print(f"  - {rec}")

if __name__ == '__main__':
    demonstrate_clinical_wisdom()