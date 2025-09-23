#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
循证医学建议系统 - 为AGP分析建议添加明确的来源和依据
"""

from typing import Dict, List, Optional
from enum import Enum

class EvidenceLevel(Enum):
    """证据等级"""
    HIGH = "高"           # 权威指南、大型RCT研究
    MODERATE = "中"       # 观察性研究、小型RCT
    LOW = "低"           # 专家意见、经验性设定
    EXPERT = "专家共识"   # 专家共识但缺乏RCT
    UNVERIFIED = "待验证" # 系统内部设定，缺乏外部验证

class ClinicalGuideline:
    """临床指南来源"""
    ADA_2025 = "ADA Standards of Care 2025"
    ATTD_2023 = "ATTD International Consensus 2023"
    IDF_2021 = "IDF Global Guideline 2021"
    EASD_2024 = "EASD Position Statement 2024"
    CDS_2024 = "中华医学会糖尿病学分会指南 2024"

class EvidenceBasedRecommendations:
    """循证医学建议生成器"""
    
    def __init__(self):
        self.evidence_database = self._initialize_evidence_database()
    
    def _initialize_evidence_database(self) -> Dict:
        """初始化循证医学证据数据库"""
        return {
            # TIR相关建议 - 高质量证据
            'tir_low': {
                'condition': 'TIR < 70%',
                'recommendation': '优化血糖管理策略提高目标范围内时间',
                'evidence_source': ClinicalGuideline.ADA_2025,
                'evidence_level': EvidenceLevel.HIGH,
                'reference': 'ADA Standards of Care 2025, Section 7.1.3',
                'clinical_basis': 'TIR>70%与微血管并发症风险降低显著相关',
                'patient_population': '成人T1DM和T2DM患者',
                'safety_notes': '需要评估低血糖风险'
            },
            
            # 血糖变异性建议 - 高质量证据
            'high_glucose_cv': {
                'condition': 'CV > 36%',
                'recommendation': '降低血糖变异性至36%以下',
                'evidence_source': ClinicalGuideline.ADA_2025 + ', ' + ClinicalGuideline.ATTD_2023,
                'evidence_level': EvidenceLevel.HIGH,
                'reference': 'ATTD Consensus 2023; ADA Standards 2025',
                'clinical_basis': 'CV>36%与糖尿病并发症风险增加相关',
                'patient_population': '所有CGM使用者',
                'safety_notes': '需要平衡变异性控制与低血糖风险'
            },
            
            # 低血糖建议 - 高质量证据
            'severe_hypoglycemia': {
                'condition': '血糖 < 3.0 mmol/L',
                'recommendation': '立即评估并调整治疗方案预防严重低血糖',
                'evidence_source': ClinicalGuideline.ADA_2025,
                'evidence_level': EvidenceLevel.HIGH,
                'reference': 'ADA Standards of Care 2025, Section 6',
                'clinical_basis': '严重低血糖与心血管事件和死亡率增加相关',
                'patient_population': '所有糖尿病患者',
                'safety_notes': '需要紧急医学评估'
            },
            
            # 黎明现象建议 - 中等质量证据
            'dawn_phenomenon': {
                'condition': '黎明血糖上升 > 1.0 mmol/L/h',
                'recommendation': '考虑调整基础胰岛素时间或剂量',
                'evidence_source': '临床观察研究',
                'evidence_level': EvidenceLevel.MODERATE,
                'reference': 'Monnier L, et al. Diabetes Care 2013',
                'clinical_basis': '黎明现象与基础胰岛素作用不足相关',
                'patient_population': '胰岛素治疗患者',
                'safety_notes': '调整需要监测低血糖风险'
            },
            
            # 分位数带变异性建议 - 低质量证据（经验性）
            'temporal_variability': {
                'condition': '分位数带CV > 40%',
                'recommendation': '建立规律生活作息改善血糖昼夜节律',
                'evidence_source': '系统内部设定',
                'evidence_level': EvidenceLevel.UNVERIFIED,
                'reference': 'AGPAI内部算法，缺乏外部验证',
                'clinical_basis': '理论上昼夜节律稳定有助于血糖管理',
                'patient_population': '所有患者',
                'safety_notes': '建议作为辅助参考，非主要治疗依据'
            },
            
            # 餐后血糖建议 - 中等质量证据
            'postprandial_high': {
                'condition': '餐后血糖峰值 > 10.0 mmol/L',
                'recommendation': '优化餐时胰岛素管理',
                'evidence_source': ClinicalGuideline.IDF_2021,
                'evidence_level': EvidenceLevel.MODERATE,
                'reference': 'IDF Guideline 2021, Postprandial Glucose',
                'clinical_basis': '餐后高血糖与大血管并发症相关',
                'patient_population': '餐时胰岛素使用者',
                'safety_notes': '需要考虑胰岛素剂量调整的低血糖风险'
            }
        }
    
    def generate_evidence_based_recommendation(self, condition_key: str, 
                                            value: float = None) -> Dict:
        """生成有循证依据的建议"""
        
        if condition_key not in self.evidence_database:
            return self._generate_unverified_recommendation(condition_key)
        
        evidence = self.evidence_database[condition_key]
        
        return {
            'category': self._get_category_from_condition(condition_key),
            'recommendation': evidence['recommendation'],
            'evidence_level': evidence['evidence_level'].value,
            'evidence_source': evidence['evidence_source'],
            'reference': evidence['reference'],
            'clinical_basis': evidence['clinical_basis'],
            'patient_population': evidence['patient_population'],
            'safety_notes': evidence['safety_notes'],
            'priority': self._determine_priority(evidence['evidence_level']),
            'follow_up': self._generate_follow_up(condition_key),
            'current_value': value
        }
    
    def _generate_unverified_recommendation(self, condition_key: str) -> Dict:
        """为缺乏证据的条件生成标记"""
        return {
            'category': 'unverified_analysis',
            'recommendation': f'基于{condition_key}的分析结果，建议咨询专业医生',
            'evidence_level': EvidenceLevel.UNVERIFIED.value,
            'evidence_source': 'AGPAI系统分析',
            'reference': '无外部验证',
            'clinical_basis': '系统算法分析，临床意义待验证',
            'patient_population': '需要专业医生评估',
            'safety_notes': '⚠️ 此建议缺乏循证医学依据，仅作参考',
            'priority': 'low',
            'follow_up': '建议与医护团队讨论'
        }
    
    def _get_category_from_condition(self, condition_key: str) -> str:
        """根据条件确定建议类别"""
        category_mapping = {
            'tir_low': 'glucose_management',
            'high_glucose_cv': 'variability_control', 
            'severe_hypoglycemia': 'safety_critical',
            'dawn_phenomenon': 'insulin_timing',
            'temporal_variability': 'lifestyle_optimization',
            'postprandial_high': 'meal_management'
        }
        return category_mapping.get(condition_key, 'general')
    
    def _determine_priority(self, evidence_level: EvidenceLevel) -> str:
        """根据证据等级确定优先级"""
        priority_mapping = {
            EvidenceLevel.HIGH: 'high',
            EvidenceLevel.MODERATE: 'medium',
            EvidenceLevel.LOW: 'low',
            EvidenceLevel.EXPERT: 'medium',
            EvidenceLevel.UNVERIFIED: 'low'
        }
        return priority_mapping.get(evidence_level, 'low')
    
    def _generate_follow_up(self, condition_key: str) -> str:
        """生成随访建议"""
        follow_up_mapping = {
            'tir_low': '2-4周后复查CGM数据评估改善情况',
            'high_glucose_cv': '1-2周后评估变异性改善',
            'severe_hypoglycemia': '立即医学评估，24-48小时内复查',
            'dawn_phenomenon': '1周后评估基础胰岛素调整效果',
            'temporal_variability': '2-3周后评估生活规律改善效果',
            'postprandial_high': '1-2周后评估餐时管理改善'
        }
        return follow_up_mapping.get(condition_key, '根据具体情况确定复查时间')
    
    def generate_evidence_summary_report(self, recommendations: List[Dict]) -> str:
        """生成证据等级汇总报告"""
        
        evidence_counts = {level.value: 0 for level in EvidenceLevel}
        
        for rec in recommendations:
            evidence_level = rec.get('evidence_level', '未知')
            evidence_counts[evidence_level] = evidence_counts.get(evidence_level, 0) + 1
        
        total_recs = len(recommendations)
        
        report = f"""
📋 建议证据等级汇总报告

总建议数: {total_recs}

证据等级分布:
• 🟢 高质量证据: {evidence_counts['高']} 项 ({evidence_counts['高']/total_recs*100:.1f}%)
• 🟡 中等质量证据: {evidence_counts['中']} 项 ({evidence_counts['中']/total_recs*100:.1f}%)
• 🟠 专家共识: {evidence_counts['专家共识']} 项 ({evidence_counts['专家共识']/total_recs*100:.1f}%)
• 🔴 低质量/待验证: {evidence_counts['低'] + evidence_counts['待验证']} 项 ({(evidence_counts['低'] + evidence_counts['待验证'])/total_recs*100:.1f}%)

⚠️ 注意事项:
- 高质量证据建议可直接参考
- 中等质量证据建议需要临床判断
- 待验证建议仅作参考，需要专业医生评估
"""
        
        return report

def main():
    """测试循证建议系统"""
    
    recommender = EvidenceBasedRecommendations()
    
    # 测试各种建议生成
    test_conditions = [
        ('tir_low', 65.0),
        ('high_glucose_cv', 42.0),
        ('severe_hypoglycemia', 2.3),
        ('temporal_variability', 48.5),
        ('unknown_condition', None)
    ]
    
    print("🔬 循证医学建议系统测试")
    print("="*60)
    
    recommendations = []
    
    for condition, value in test_conditions:
        rec = recommender.generate_evidence_based_recommendation(condition, value)
        recommendations.append(rec)
        
        print(f"\n📋 条件: {condition}")
        print(f"   建议: {rec['recommendation']}")
        print(f"   证据等级: {rec['evidence_level']}")
        print(f"   依据来源: {rec['evidence_source']}")
        print(f"   优先级: {rec['priority']}")
        
        if rec['evidence_level'] == '待验证':
            print(f"   ⚠️ 警告: {rec['safety_notes']}")
    
    # 生成汇总报告
    summary = recommender.generate_evidence_summary_report(recommendations)
    print(summary)

if __name__ == "__main__":
    main()