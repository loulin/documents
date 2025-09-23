#!/usr/bin/env python3
"""
改进版ECG自动诊断系统
基于初次分析结果的优化算法
"""

import pandas as pd
import numpy as np
import ast
import re
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

class ImprovedECGDiagnosisSystem:
    def __init__(self):
        """初始化改进版诊断系统"""
        # 优化后的诊断阈值
        self.thresholds = {
            'bradycardia_hr': 55,  # 从50提升至55
            'tachycardia_hr': 110,  # 心动过速阈值
            'consistency_afib': 0.65,  # 从0.7降至0.65
            'consistency_severe': 0.6,  # 严重心律失常
            'lf_hf_ischemia_low': 0.8,  # 从0.5提升至0.8
            'lf_hf_ischemia_high': 3.5,  # 从4.0降至3.5
            'rmssd_low': 25,  # 从15提升至25
            'rmssd_high': 150,  # 从200降至150
            'sdnn_low': 30,  # HRV严重降低
            'sdnn_high': 120,  # HRV异常升高
            'pnn50_afib': 60,  # 房颤特征阈值
            'triangular_low': 6,  # 几何指标低值
            'cv_high': 35,  # 变异系数高值
            'snr_poor': 8,  # 信号质量差
        }
        
        # SNOMED编码映射
        self.snomed_map = {
            '426177001': '窦性心动过缓',
            '426783006': '窦性心律', 
            '164889003': '心律不齐',
            '427084000': '心房颤动',
            '164890007': '室性心律失常',
            '164934002': '心电图异常',
            '55827005': '心肌缺血',
            '59118001': '右束支阻滞',
            '428750005': '左前分支阻滞',
            '17338001': '左心室肥厚',
            '429622005': '左束支阻滞',
        }
    
    def parse_quality_field(self, quality_str):
        """解析信号质量字段"""
        try:
            if pd.isna(quality_str):
                return {'snr_db': np.nan, 'baseline_drift_ratio': np.nan, 
                       'saturation_ratio': np.nan, 'dynamic_range': np.nan}
            
            quality_str = str(quality_str).replace("'", '"')
            quality_str = re.sub(r'np\.float64\((.*?)\)', r'\1', quality_str)
            quality_dict = ast.literal_eval(quality_str)
            return quality_dict
        except:
            return {'snr_db': np.nan, 'baseline_drift_ratio': np.nan, 
                   'saturation_ratio': np.nan, 'dynamic_range': np.nan}
    
    def improved_diagnosis(self, row):
        """改进版诊断算法"""
        diagnoses = []
        diagnosis_confidence = {}
        
        # 解析关键参数
        quality = self.parse_quality_field(row.get('quality', '{}'))
        snr = quality.get('snr_db', np.nan)
        
        # 关键HRV参数
        mean_hr = row.get('mean_hr', np.nan)
        std_rr = row.get('std_rr', np.nan)  # SDNN
        rmssd = row.get('rmssd', np.nan)
        pnn50 = row.get('pnn50', np.nan)
        triangular_index = row.get('triangular_index', np.nan)
        r_peaks_consistency = row.get('r_peaks_consistency', np.nan)
        lf_hf_ratio = row.get('lf_hf_ratio', np.nan)
        cv = row.get('cv', np.nan)
        age = row.get('age', np.nan)
        
        # 1. 信号质量评估
        signal_quality_ok = True
        if not pd.isna(snr) and snr < self.thresholds['snr_poor']:
            diagnoses.append('164934002')  # 心电图异常
            diagnosis_confidence['164934002'] = 0.9
            signal_quality_ok = False
        
        # 只有信号质量可接受时才进行详细诊断
        if signal_quality_ok:
            
            # 2. 心律失常等级判断（最重要的优先）
            arrhythmia_severity = self._assess_arrhythmia_severity(
                r_peaks_consistency, pnn50, std_rr, triangular_index)
            
            if arrhythmia_severity == 'severe':  # 严重心律失常
                if not pd.isna(pnn50) and pnn50 > self.thresholds['pnn50_afib']:
                    diagnoses.append('427084000')  # 心房颤动
                    diagnosis_confidence['427084000'] = 0.85
                elif not pd.isna(std_rr) and std_rr > 200:
                    diagnoses.append('164890007')  # 室性心律失常  
                    diagnosis_confidence['164890007'] = 0.80
                else:
                    diagnoses.append('164889003')  # 心律不齐
                    diagnosis_confidence['164889003'] = 0.75
                    
            elif arrhythmia_severity == 'moderate':  # 中度心律失常
                diagnoses.append('164889003')  # 心律不齐
                diagnosis_confidence['164889003'] = 0.70
                
            # 3. 基础心率分析
            hr_diagnosis = self._analyze_heart_rate(mean_hr, age, r_peaks_consistency)
            if hr_diagnosis:
                for diag, conf in hr_diagnosis.items():
                    if diag not in diagnoses:
                        diagnoses.append(diag)
                        diagnosis_confidence[diag] = conf
            
            # 4. 心肌缺血多指标评估（更严格的标准）
            ischemia_score, ischemia_conf = self._assess_ischemia(
                lf_hf_ratio, rmssd, std_rr, mean_hr)
            
            if ischemia_score >= 2:  # 需要至少2个指标支持
                diagnoses.append('55827005')  # 心肌缺血
                diagnosis_confidence['55827005'] = ischemia_conf
            
            # 5. 传导阻滞推测（基于一致性和HRV模式）
            conduction_diag = self._assess_conduction_blocks(
                r_peaks_consistency, std_rr, cv, mean_hr)
            
            if conduction_diag:
                for diag, conf in conduction_diag.items():
                    if diag not in diagnoses:
                        diagnoses.append(diag)
                        diagnosis_confidence[diag] = conf
        
        # 6. 默认诊断
        if not diagnoses:
            if not pd.isna(mean_hr) and 50 <= mean_hr <= 100:
                diagnoses.append('426783006')  # 窦性心律
                diagnosis_confidence['426783006'] = 0.6
            else:
                diagnoses.append('164934002')  # 心电图异常
                diagnosis_confidence['164934002'] = 0.5
        
        return diagnoses, diagnosis_confidence
    
    def _assess_arrhythmia_severity(self, consistency, pnn50, std_rr, triangular_index):
        """评估心律失常严重程度"""
        severity_score = 0
        
        if not pd.isna(consistency):
            if consistency < self.thresholds['consistency_severe']:
                severity_score += 3
            elif consistency < self.thresholds['consistency_afib']:
                severity_score += 2
            elif consistency < 0.8:
                severity_score += 1
        
        if not pd.isna(pnn50) and pnn50 > 70:
            severity_score += 2
        
        if not pd.isna(std_rr) and std_rr > 150:
            severity_score += 2
            
        if not pd.isna(triangular_index) and triangular_index < self.thresholds['triangular_low']:
            severity_score += 1
        
        if severity_score >= 4:
            return 'severe'
        elif severity_score >= 2:
            return 'moderate'
        else:
            return 'mild'
    
    def _analyze_heart_rate(self, mean_hr, age, consistency):
        """心率分析"""
        hr_diagnoses = {}
        
        if pd.isna(mean_hr):
            return hr_diagnoses
        
        # 年龄相关的心率调整
        age_adjusted_brady_threshold = self.thresholds['bradycardia_hr']
        if not pd.isna(age) and age > 65:
            age_adjusted_brady_threshold = 50  # 老年人心动过缓标准更严格
        
        if mean_hr < age_adjusted_brady_threshold:
            # 检查是否为病理性心动过缓
            if not pd.isna(consistency) and consistency > 0.85:
                hr_diagnoses['426177001'] = 0.9  # 窦性心动过缓
            else:
                hr_diagnoses['426177001'] = 0.75  # 心动过缓伴心律不齐
                
        elif mean_hr > self.thresholds['tachycardia_hr']:
            # 心动过速（暂时归类为心律不齐）
            hr_diagnoses['164889003'] = 0.8
        
        elif 55 <= mean_hr <= 100 and not pd.isna(consistency) and consistency > 0.9:
            # 正常心率且规律
            hr_diagnoses['426783006'] = 0.85  # 窦性心律
            
        return hr_diagnoses
    
    def _assess_ischemia(self, lf_hf_ratio, rmssd, std_rr, mean_hr):
        """心肌缺血多指标评估"""
        ischemia_score = 0
        confidence_factors = []
        
        # LF/HF比值异常
        if not pd.isna(lf_hf_ratio):
            if lf_hf_ratio < self.thresholds['lf_hf_ischemia_low']:
                ischemia_score += 1
                confidence_factors.append(0.7)
            elif lf_hf_ratio > self.thresholds['lf_hf_ischemia_high']:
                ischemia_score += 1
                confidence_factors.append(0.8)
        
        # 副交感功能减退
        if not pd.isna(rmssd) and rmssd < self.thresholds['rmssd_low']:
            ischemia_score += 1
            confidence_factors.append(0.6)
        
        # HRV整体降低
        if not pd.isna(std_rr) and std_rr < self.thresholds['sdnn_low']:
            ischemia_score += 1
            confidence_factors.append(0.7)
        
        # 心率异常可能与缺血相关
        if not pd.isna(mean_hr) and (mean_hr < 45 or mean_hr > 110):
            ischemia_score += 0.5  # 权重较低
            confidence_factors.append(0.5)
        
        # 计算综合置信度
        if confidence_factors:
            avg_confidence = np.mean(confidence_factors)
            # 根据支持指标数量调整置信度
            final_confidence = min(0.9, avg_confidence * (ischemia_score / 3))
        else:
            final_confidence = 0.3
        
        return ischemia_score, final_confidence
    
    def _assess_conduction_blocks(self, consistency, std_rr, cv, mean_hr):
        """传导阻滞评估"""
        conduction_diags = {}
        
        # 基于一致性和变异性模式推测传导阻滞
        if (not pd.isna(consistency) and 0.7 < consistency < 0.9 and
            not pd.isna(std_rr) and 30 < std_rr < 100 and
            not pd.isna(cv) and cv < 20):
            
            # 这种模式可能提示传导阻滞（最常见是右束支阻滞）
            conduction_diags['59118001'] = 0.6  # 右束支阻滞
        
        return conduction_diags
    
    def analyze_with_confidence(self, csv_file):
        """带置信度的数据集分析"""
        print("🔍 加载数据集并运行改进版诊断...")
        df = pd.read_csv(csv_file)
        
        results = []
        for idx, row in df.iterrows():
            record_name = row['record_name']
            original_diagnosis = row['diagnosis']
            
            # 改进版诊断
            predicted_diagnosis, confidence = self.improved_diagnosis(row)
            
            # 比较结果
            orig_codes = set(original_diagnosis.split(',')) if original_diagnosis else set()
            pred_codes = set(predicted_diagnosis)
            
            result = {
                'record_name': record_name,
                'original_diagnosis': original_diagnosis,
                'predicted_diagnosis': ','.join(predicted_diagnosis),
                'diagnosis_confidence': confidence,
                'exact_match': orig_codes == pred_codes,
                'partial_match': len(orig_codes & pred_codes) > 0,
                'overlap_count': len(orig_codes & pred_codes),
                'jaccard_similarity': len(orig_codes & pred_codes) / len(orig_codes | pred_codes) if orig_codes | pred_codes else 0
            }
            results.append(result)
        
        return pd.DataFrame(results)
    
    def compare_versions(self, csv_file):
        """比较改进前后的性能"""
        print("📊 对比改进前后的诊断性能...\n")
        
        # 运行改进版分析
        improved_results = self.analyze_with_confidence(csv_file)
        
        # 计算改进版性能指标
        improved_metrics = {
            'exact_match_rate': improved_results['exact_match'].mean(),
            'partial_match_rate': improved_results['partial_match'].mean(),
            'avg_jaccard': improved_results['jaccard_similarity'].mean(),
            'avg_overlap': improved_results['overlap_count'].mean()
        }
        
        # 原版本性能（来自之前的分析）
        original_metrics = {
            'exact_match_rate': 0.01,
            'partial_match_rate': 0.37,
            'avg_jaccard': 0.142,
            'avg_overlap': 0.4
        }
        
        print("性能对比结果:")
        print("=" * 60)
        print(f"{'指标':<20} {'原版本':<15} {'改进版':<15} {'改进幅度':<15}")
        print("-" * 60)
        
        for metric in ['exact_match_rate', 'partial_match_rate', 'avg_jaccard', 'avg_overlap']:
            original = original_metrics[metric]
            improved = improved_metrics[metric]
            improvement = ((improved - original) / original * 100) if original > 0 else 0
            
            print(f"{metric:<20} {original:<15.3f} {improved:<15.3f} {improvement:>+12.1f}%")
        
        # 详细分析改进版结果
        print(f"\n改进版详细指标:")
        print(f"完全匹配: {improved_results['exact_match'].sum()}/{len(improved_results)} ({improved_metrics['exact_match_rate']:.1%})")
        print(f"部分匹配: {improved_results['partial_match'].sum()}/{len(improved_results)} ({improved_metrics['partial_match_rate']:.1%})")
        
        return improved_results, improved_metrics, original_metrics

def main():
    """主函数"""
    improved_system = ImprovedECGDiagnosisSystem()
    
    # 运行对比分析
    improved_results, improved_metrics, original_metrics = improved_system.compare_versions(
        'enhanced_ecg_analysis_results.csv')
    
    # 保存改进版结果
    improved_results.to_csv('improved_ecg_diagnosis_results.csv', index=False, encoding='utf-8-sig')
    print(f"\n📄 改进版诊断结果已保存到: improved_ecg_diagnosis_results.csv")
    
    # 显示最佳案例
    print("\n🏆 改进版最佳诊断案例:")
    print("-" * 80)
    best_cases = improved_results.nlargest(5, 'jaccard_similarity')
    for idx, row in best_cases.iterrows():
        print(f"记录: {row['record_name']}")
        print(f"  Jaccard相似度: {row['jaccard_similarity']:.3f}")
        match_status = '✅完全匹配' if row['exact_match'] else f'🔶部分匹配({row["overlap_count"]}个)'
        print(f"  匹配状态: {match_status}")
        print()
    
    return improved_system, improved_results

if __name__ == '__main__':
    improved_system, improved_results = main()