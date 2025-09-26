#!/usr/bin/env python3
"""
基于HRV参数的ECG自动诊断系统
与SNOMED-CT预标注诊断进行对比分析
"""

import pandas as pd
import numpy as np
import ast
import re
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class ECGAutoDiagnosisSystem:
    def __init__(self):
        """初始化诊断系统"""
        # SNOMED编码到中文诊断的映射
        self.snomed_to_chinese = {
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
            '233917008': '主动脉瓣狭窄',
            '270492004': '一度房室阻滞',
            '164909002': '左心房扩大',
            '164912004': '右心房扩大',
            '164917005': '双房扩大',
            '251173003': 'T波异常',
            '251199005': 'ST段异常',
            '251146004': '心电轴偏移',
            '284470004': '心房早搏',
            '39732003': '室性早搏',
            '59931005': '房室交界性心律',
            '47665007': '多形性室性心动过速',
            '698252002': '二度房室阻滞',
            '164865005': '完全性房室阻滞'
        }
    
    def parse_quality_field(self, quality_str):
        """解析质量字段"""
        try:
            if pd.isna(quality_str):
                return {'snr_db': np.nan, 'baseline_drift_ratio': np.nan, 
                       'saturation_ratio': np.nan, 'dynamic_range': np.nan}
            
            # 清理字符串格式
            quality_str = str(quality_str).replace("'", '"')
            quality_str = re.sub(r'np\.float64\((.*?)\)', r'\1', quality_str)
            quality_dict = ast.literal_eval(quality_str)
            return quality_dict
        except:
            return {'snr_db': np.nan, 'baseline_drift_ratio': np.nan, 
                   'saturation_ratio': np.nan, 'dynamic_range': np.nan}
    
    def rule_based_diagnosis(self, row):
        """基于规则的诊断算法"""
        diagnoses = []
        
        # 解析信号质量
        quality = self.parse_quality_field(row.get('quality', '{}'))
        snr = quality.get('snr_db', np.nan)
        
        # 如果信号质量太差，返回心电图异常
        if not pd.isna(snr) and snr < 5:
            diagnoses.append('164934002')  # 心电图异常
        
        # 获取关键参数
        mean_hr = row.get('mean_hr', np.nan)
        std_rr = row.get('std_rr', np.nan)  # SDNN
        rmssd = row.get('rmssd', np.nan)
        pnn50 = row.get('pnn50', np.nan)
        triangular_index = row.get('triangular_index', np.nan)
        r_peaks_consistency = row.get('r_peaks_consistency', np.nan)
        lf_hf_ratio = row.get('lf_hf_ratio', np.nan)
        cv = row.get('cv', np.nan)
        
        # 1. 心率基础诊断
        if not pd.isna(mean_hr):
            if mean_hr < 50:
                diagnoses.append('426177001')  # 窦性心动过缓
            elif mean_hr >= 50 and mean_hr <= 100 and r_peaks_consistency > 0.9:
                diagnoses.append('426783006')  # 窦性心律
        
        # 2. 心律失常诊断
        if not pd.isna(r_peaks_consistency) and r_peaks_consistency < 0.7:
            # R峰检测一致性低，提示严重心律失常
            if not pd.isna(pnn50) and pnn50 > 80:
                diagnoses.append('427084000')  # 心房颤动
            else:
                diagnoses.append('164889003')  # 心律不齐
        
        # 3. 心律不齐进一步分类
        elif not pd.isna(std_rr) and not pd.isna(triangular_index):
            if std_rr > 100 and triangular_index < 6:
                if not pd.isna(pnn50) and pnn50 > 50:
                    diagnoses.append('427084000')  # 房颤特征
                else:
                    diagnoses.append('164889003')  # 一般心律不齐
        
        # 4. 室性心律失常检测
        if (not pd.isna(std_rr) and std_rr > 200 and 
            not pd.isna(cv) and cv > 40 and
            not pd.isna(r_peaks_consistency) and r_peaks_consistency < 0.6):
            diagnoses.append('164890007')  # 室性心律失常
        
        # 5. 传导阻滞检测 (基于R峰一致性和心率变异性)
        if (not pd.isna(r_peaks_consistency) and r_peaks_consistency < 0.8 and
            not pd.isna(std_rr) and std_rr > 50 and std_rr < 150):
            diagnoses.append('59118001')  # 右束支阻滞 (最常见)
        
        # 6. 心肌缺血检测 (基于HRV频域分析)
        if not pd.isna(lf_hf_ratio) and (lf_hf_ratio < 0.5 or lf_hf_ratio > 4.0):
            diagnoses.append('55827005')  # 心肌缺血
        
        # 7. 自主神经功能异常
        if not pd.isna(rmssd):
            if rmssd < 15:
                # 副交感神经功能严重受损，可能合并其他异常
                if '164889003' not in diagnoses and '427084000' not in diagnoses:
                    diagnoses.append('164934002')  # 心电图异常
            elif rmssd > 200:
                # 极高的RMSSD可能提示病理性变异
                diagnoses.append('164889003')  # 心律不齐
        
        # 8. 如果没有明确诊断但有异常参数，标记为心电图异常
        if not diagnoses:
            # 检查是否有任何异常参数
            abnormal_params = 0
            if not pd.isna(mean_hr) and (mean_hr < 50 or mean_hr > 100):
                abnormal_params += 1
            if not pd.isna(std_rr) and std_rr > 100:
                abnormal_params += 1
            if not pd.isna(r_peaks_consistency) and r_peaks_consistency < 0.9:
                abnormal_params += 1
            
            if abnormal_params >= 2:
                diagnoses.append('164934002')  # 心电图异常
            else:
                diagnoses.append('426783006')  # 窦性心律(正常)
        
        return diagnoses
    
    def compare_diagnoses(self, original_diagnosis, predicted_diagnosis):
        """比较原始诊断和预测诊断"""
        # 解析原始诊断
        orig_codes = set(original_diagnosis.split(',')) if original_diagnosis else set()
        pred_codes = set(predicted_diagnosis)
        
        # 计算匹配情况
        exact_match = orig_codes == pred_codes
        partial_match = len(orig_codes & pred_codes) > 0
        missed_diagnoses = orig_codes - pred_codes
        extra_diagnoses = pred_codes - orig_codes
        
        return {
            'exact_match': exact_match,
            'partial_match': partial_match,
            'overlap_count': len(orig_codes & pred_codes),
            'missed_diagnoses': missed_diagnoses,
            'extra_diagnoses': extra_diagnoses,
            'jaccard_similarity': len(orig_codes & pred_codes) / len(orig_codes | pred_codes) if orig_codes | pred_codes else 0
        }
    
    def analyze_dataset(self, csv_file):
        """分析整个数据集"""
        print("🔍 加载ECG分析数据集...")
        df = pd.read_csv(csv_file)
        
        print(f"数据集大小: {len(df)} 个记录")
        
        # 对每个记录进行诊断
        results = []
        for idx, row in df.iterrows():
            record_name = row['record_name']
            original_diagnosis = row['diagnosis']
            
            # 自动诊断
            predicted_diagnosis = self.rule_based_diagnosis(row)
            
            # 比较诊断结果
            comparison = self.compare_diagnoses(original_diagnosis, predicted_diagnosis)
            
            result = {
                'record_name': record_name,
                'original_diagnosis': original_diagnosis,
                'predicted_diagnosis': ','.join(predicted_diagnosis),
                'original_chinese': self.get_chinese_diagnosis(original_diagnosis),
                'predicted_chinese': self.get_chinese_diagnosis(','.join(predicted_diagnosis)),
                **comparison
            }
            results.append(result)
        
        return pd.DataFrame(results), df
    
    def get_chinese_diagnosis(self, diagnosis_codes):
        """获取中文诊断"""
        if not diagnosis_codes:
            return "无诊断"
        
        codes = diagnosis_codes.split(',')
        chinese_names = []
        for code in codes:
            code = code.strip()
            if code in self.snomed_to_chinese:
                chinese_names.append(self.snomed_to_chinese[code])
            else:
                chinese_names.append(f"未知编码({code})")
        
        return ' + '.join(chinese_names)
    
    def generate_performance_report(self, results_df):
        """生成性能评估报告"""
        total_records = len(results_df)
        exact_matches = results_df['exact_match'].sum()
        partial_matches = results_df['partial_match'].sum()
        
        print("📊 诊断性能评估报告")
        print("=" * 50)
        print(f"总记录数: {total_records}")
        print(f"完全匹配: {exact_matches} ({exact_matches/total_records*100:.1f}%)")
        print(f"部分匹配: {partial_matches} ({partial_matches/total_records*100:.1f}%)")
        print(f"平均Jaccard相似度: {results_df['jaccard_similarity'].mean():.3f}")
        print(f"平均重叠诊断数: {results_df['overlap_count'].mean():.1f}")
        
        print("\n🎯 按诊断类别分析:")
        
        # 分析最常见的原始诊断
        orig_diag_counts = results_df['original_diagnosis'].value_counts().head(10)
        print("\n原始诊断Top 10:")
        for diag, count in orig_diag_counts.items():
            chinese = self.get_chinese_diagnosis(diag)
            print(f"  {chinese}: {count}次")
        
        # 分析预测诊断
        pred_diag_counts = results_df['predicted_diagnosis'].value_counts().head(10)
        print("\n预测诊断Top 10:")
        for diag, count in pred_diag_counts.items():
            chinese = self.get_chinese_diagnosis(diag)
            print(f"  {chinese}: {count}次")
        
        # 分析missed和extra诊断
        print("\n❌ 最常漏诊的疾病:")
        all_missed = []
        for missed_set in results_df['missed_diagnoses']:
            all_missed.extend(list(missed_set))
        
        if all_missed:
            missed_counts = pd.Series(all_missed).value_counts().head(5)
            for code, count in missed_counts.items():
                chinese = self.get_chinese_diagnosis(code)
                print(f"  {chinese} ({code}): 漏诊{count}次")
        else:
            print("  无明显漏诊模式")
        
        print("\n➕ 最常过诊的疾病:")
        all_extra = []
        for extra_set in results_df['extra_diagnoses']:
            all_extra.extend(list(extra_set))
        
        if all_extra:
            extra_counts = pd.Series(all_extra).value_counts().head(5)
            for code, count in extra_counts.items():
                chinese = self.get_chinese_diagnosis(code)
                print(f"  {chinese} ({code}): 过诊{count}次")
        else:
            print("  无明显过诊模式")
        
        return {
            'total_records': total_records,
            'exact_match_rate': exact_matches / total_records,
            'partial_match_rate': partial_matches / total_records,
            'avg_jaccard_similarity': results_df['jaccard_similarity'].mean(),
            'avg_overlap_count': results_df['overlap_count'].mean()
        }
    
    def generate_detailed_comparison(self, results_df, output_file=None):
        """生成详细的诊断对比表"""
        # 选择关键列进行输出
        comparison_df = results_df[[
            'record_name', 
            'original_chinese', 
            'predicted_chinese',
            'exact_match',
            'jaccard_similarity',
            'overlap_count'
        ]].copy()
        
        # 添加匹配状态列
        comparison_df['match_status'] = comparison_df.apply(lambda row: 
            '✅完全匹配' if row['exact_match'] 
            else f'🔶部分匹配({row["overlap_count"]}个)' if row['overlap_count'] > 0
            else '❌完全不匹配', axis=1)
        
        # 按相似度排序
        comparison_df = comparison_df.sort_values('jaccard_similarity', ascending=False)
        
        if output_file:
            comparison_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n📄 详细对比结果已保存到: {output_file}")
        
        return comparison_df

def main():
    """主函数"""
    diagnosis_system = ECGAutoDiagnosisSystem()
    
    # 分析数据集
    results_df, original_df = diagnosis_system.analyze_dataset('enhanced_ecg_analysis_results.csv')
    
    # 生成性能报告
    performance_metrics = diagnosis_system.generate_performance_report(results_df)
    
    # 生成详细对比
    detailed_comparison = diagnosis_system.generate_detailed_comparison(
        results_df, 
        'ecg_diagnosis_comparison.csv'
    )
    
    # 显示一些具体案例
    print("\n🔍 诊断对比案例 (Top 10):")
    print("-" * 100)
    for idx, row in detailed_comparison.head(10).iterrows():
        print(f"记录: {row['record_name']}")
        print(f"  原始诊断: {row['original_chinese']}")
        print(f"  预测诊断: {row['predicted_chinese']}")
        print(f"  匹配状态: {row['match_status']} (相似度: {row['jaccard_similarity']:.3f})")
        print()
    
    return diagnosis_system, results_df, detailed_comparison, performance_metrics

if __name__ == '__main__':
    diagnosis_system, results_df, detailed_comparison, performance_metrics = main()