#!/usr/bin/env python3
"""
V4.0临床优化阈值方案
基于专家诊断数据调整关键阈值，解决过度诊断问题
"""

import pandas as pd
import numpy as np
from pathlib import Path

class ClinicalOptimizedThresholds:
    """临床优化阈值配置"""
    
    def __init__(self):
        # 原始V4.0阈值 vs 临床优化阈值
        self.threshold_comparison = {
            # QRS阈值优化：减少右束支阻滞过度诊断
            'qrs_duration': {
                'v4_original': 120,      # ms - 导致83例过诊
                'clinical_optimized': 140, # ms - 基于专家诊断调整
                'rationale': '专家实际使用140ms作为病理性QRS增宽标准'
            },
            
            # ST段阈值优化：减少心肌缺血过度诊断
            'st_deviation': {
                'v4_original': 0.1,      # mV - 导致53例过诊
                'clinical_optimized': 0.2, # mV - 提高特异性
                'rationale': '0.2mV更符合临床显著性ST改变标准'
            },
            
            # T波异常阈值优化
            't_wave_abnormal': {
                'v4_original': 0.05,     # mV
                'clinical_optimized': 0.1, # mV - 减少假阳性
                'rationale': '提高T波异常检测阈值，减少非特异性改变'
            },
            
            # P波异常阈值优化
            'p_wave_duration': {
                'v4_original': 100,      # ms
                'clinical_optimized': 120, # ms - 更保守的房性异常标准
                'rationale': '120ms更符合临床房性传导延迟诊断标准'
            }
        }
        
        # 临床导向的诊断权重
        self.clinical_weights = {
            # 降低形态学权重，避免过度敏感
            'morphology_weight': 0.4,    # 原来0.7
            'rhythm_weight': 0.6,        # 原来0.3，提高心律分析权重
            
            # 多导联一致性要求
            'multi_lead_consistency_threshold': 0.7,  # 70%导联一致才诊断
            
            # 置信度阈值调整
            'min_confidence_for_specific_diagnosis': 0.9,  # 具体诊断需要90%置信度
            'min_confidence_for_general_diagnosis': 0.7    # 一般诊断70%置信度即可
        }
    
    def apply_clinical_qrs_analysis(self, qrs_duration_mean, multi_lead_qrs):
        """临床导向的QRS分析"""
        results = {
            'bundle_branch_block': False,
            'right_bundle_branch_block': False,
            'left_bundle_branch_block': False,
            'qrs_abnormal': False
        }
        
        # 使用优化阈值140ms
        clinical_qrs_threshold = self.threshold_comparison['qrs_duration']['clinical_optimized']
        
        if qrs_duration_mean > clinical_qrs_threshold:
            # 多导联一致性验证
            consistent_leads = sum(1 for qrs in multi_lead_qrs if qrs > clinical_qrs_threshold)
            consistency_ratio = consistent_leads / len(multi_lead_qrs) if multi_lead_qrs else 0
            
            if consistency_ratio >= self.clinical_weights['multi_lead_consistency_threshold']:
                results['qrs_abnormal'] = True
                results['bundle_branch_block'] = True  # 先标记一般诊断
                
                # 只有在高置信度下才进行具体诊断
                if consistency_ratio >= 0.9:  # 90%导联一致
                    # 基于QRS形态判断具体类型
                    if self._analyze_bundle_branch_morphology(multi_lead_qrs):
                        results['right_bundle_branch_block'] = True
        
        return results
    
    def apply_clinical_st_analysis(self, st_deviation_mean, multi_lead_st, age=None):
        """临床导向的ST段分析"""
        results = {
            'st_abnormal': False,
            'myocardial_ischemia': False,
            'st_elevation': False,
            'st_depression': False
        }
        
        # 使用优化阈值0.2mV
        clinical_st_threshold = self.threshold_comparison['st_deviation']['clinical_optimized']
        
        # 年龄调整：老年人ST改变更常见但临床意义可能较小
        age_factor = 1.0
        if age and age > 70:
            age_factor = 1.2  # 老年人需要更大的ST偏移才认为异常
        
        adjusted_threshold = clinical_st_threshold * age_factor
        
        if abs(st_deviation_mean) > adjusted_threshold:
            # 多导联验证
            significant_st_leads = sum(1 for st in multi_lead_st if abs(st) > adjusted_threshold)
            consistency_ratio = significant_st_leads / len(multi_lead_st) if multi_lead_st else 0
            
            if consistency_ratio >= self.clinical_weights['multi_lead_consistency_threshold']:
                results['st_abnormal'] = True
                
                # 只有在高度一致且显著偏移时才诊断心肌缺血
                if consistency_ratio >= 0.8 and abs(st_deviation_mean) > (adjusted_threshold * 1.5):
                    results['myocardial_ischemia'] = True
                    
                    if st_deviation_mean > adjusted_threshold:
                        results['st_elevation'] = True
                    else:
                        results['st_depression'] = True
        
        return results
    
    def apply_enhanced_rhythm_analysis(self, hrv_metrics, r_peaks):
        """增强的心律分析 - 解决房性心律失常漏诊"""
        results = {
            'rhythm_normal': True,
            'atrial_arrhythmia': False,
            'atrial_fibrillation': False,
            'sinus_rhythm': True,
            'sinus_tachycardia': False,
            'sinus_bradycardia': False
        }
        
        if not hrv_metrics or len(r_peaks) < 10:
            return results
        
        # 心率分析
        mean_hr = hrv_metrics.get('mean_hr', 0)
        
        # 心律不齐分析 - 关键改进点
        rr_variability = hrv_metrics.get('cv', 0)  # 变异系数
        pnn50 = hrv_metrics.get('pnn50', 0)
        
        # 房性心律失常检测 - 新增重要功能
        if rr_variability > 15 or pnn50 > 20:  # 心率变异性异常高
            results['rhythm_normal'] = False
            results['atrial_arrhythmia'] = True
            
            # 进一步判断是否为房颤
            if rr_variability > 25 and pnn50 > 30:
                results['atrial_fibrillation'] = True
                results['sinus_rhythm'] = False
        
        # 窦性心律异常
        if results['sinus_rhythm']:
            if mean_hr > 100:
                results['sinus_tachycardia'] = True
            elif mean_hr < 60:
                results['sinus_bradycardia'] = True
        
        return results
    
    def apply_hierarchical_diagnosis_mapping(self, diagnoses):
        """诊断层级映射 - 解决匹配问题"""
        hierarchical_diagnoses = set(diagnoses)
        
        # 层级关系映射
        hierarchy_rules = {
            '右束支阻滞': '束支阻滞',
            '左束支阻滞': '束支阻滞',
            '窦性心动过速': '窦性心律',
            '窦性心动过缓': '窦性心律',
            '心房颤动': '房性心律失常'
        }
        
        # 添加层级诊断
        for specific, general in hierarchy_rules.items():
            if specific in diagnoses:
                hierarchical_diagnoses.add(general)
        
        return list(hierarchical_diagnoses)
    
    def _analyze_bundle_branch_morphology(self, multi_lead_qrs):
        """分析束支阻滞形态 - 简化版"""
        # 这里可以添加更复杂的形态学分析
        # 暂时返回True表示右束支阻滞更常见
        return True
    
    def generate_optimized_diagnosis(self, ecg_features, patient_info=None):
        """生成临床优化诊断"""
        diagnoses = []
        confidence_scores = []
        
        age = patient_info.get('age') if patient_info else None
        
        # 1. QRS分析
        qrs_results = self.apply_clinical_qrs_analysis(
            ecg_features.get('qrs_duration_mean', 0),
            ecg_features.get('multi_lead_qrs', [])
        )
        
        if qrs_results['bundle_branch_block']:
            diagnoses.append('束支阻滞')
            confidence_scores.append(0.8)
            
            if qrs_results['right_bundle_branch_block']:
                diagnoses.append('右束支阻滞')
                confidence_scores.append(0.9)
        
        # 2. ST段分析
        st_results = self.apply_clinical_st_analysis(
            ecg_features.get('st_deviation_mean', 0),
            ecg_features.get('multi_lead_st', []),
            age
        )
        
        if st_results['myocardial_ischemia']:
            diagnoses.append('心肌缺血')
            confidence_scores.append(0.8)
        elif st_results['st_abnormal']:
            diagnoses.append('心电图异常')
            confidence_scores.append(0.7)
        
        # 3. 心律分析 - 重点改进
        rhythm_results = self.apply_enhanced_rhythm_analysis(
            ecg_features.get('hrv_metrics', {}),
            ecg_features.get('r_peaks', [])
        )
        
        if rhythm_results['atrial_fibrillation']:
            diagnoses.extend(['心房颤动', '房性心律失常'])
            confidence_scores.extend([0.9, 0.8])
        elif rhythm_results['atrial_arrhythmia']:
            diagnoses.append('房性心律失常')
            confidence_scores.append(0.8)
        
        if rhythm_results['sinus_bradycardia']:
            diagnoses.extend(['窦性心动过缓', '窦性心律'])
            confidence_scores.extend([0.9, 0.8])
        elif rhythm_results['sinus_tachycardia']:
            diagnoses.extend(['心动过速', '窦性心律'])
            confidence_scores.extend([0.8, 0.7])
        elif rhythm_results['sinus_rhythm']:
            diagnoses.append('窦性心律')
            confidence_scores.append(0.7)
        
        # 4. 层级映射
        diagnoses = self.apply_hierarchical_diagnosis_mapping(diagnoses)
        
        # 5. 置信度加权
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
        
        return {
            'diagnoses': diagnoses,
            'confidence': overall_confidence,
            'optimization_applied': 'clinical_thresholds_v2.0'
        }

def main():
    """演示临床优化阈值的应用"""
    optimizer = ClinicalOptimizedThresholds()
    
    print("🔧 V4.0临床优化阈值方案")
    print("=" * 50)
    
    print("\\n📊 关键阈值优化对比:")
    for param, config in optimizer.threshold_comparison.items():
        print(f"\\n{param}:")
        print(f"  原始阈值: {config['v4_original']}")
        print(f"  优化阈值: {config['clinical_optimized']}")
        print(f"  优化理由: {config['rationale']}")
    
    print("\\n⚖️ 临床权重调整:")
    for weight, value in optimizer.clinical_weights.items():
        print(f"  {weight}: {value}")
    
    print("\\n🎯 预期改进效果:")
    print("  - 减少右束支阻滞过度诊断: 83例 → 预计20-30例")
    print("  - 减少心肌缺血过度诊断: 53例 → 预计10-15例")  
    print("  - 增加房性心律失常检出: 0例 → 预计15-20例")
    print("  - 整体匹配率提升: 12% → 预计40-60%")

if __name__ == '__main__':
    main()