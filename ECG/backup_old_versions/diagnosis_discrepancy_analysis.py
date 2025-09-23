#!/usr/bin/env python3
"""
医师诊断vs数据驱动诊断差异根本原因分析
深入探讨两种诊断方法的本质差异
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import ast
import re

class DiagnosisDiscrepancyAnalyzer:
    def __init__(self):
        """初始化差异分析器"""
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 疾病分类体系
        self.disease_categories = {
            # 形态学依赖的疾病（需要看波形）
            'morphology_dependent': {
                '59118001': '右束支阻滞',    # 需要QRS形态
                '429622005': '左束支阻滞',   # 需要QRS形态  
                '428750005': '左前分支阻滞', # 需要电轴分析
                '17338001': '左心室肥厚',    # 需要电压标准
                '251173003': 'T波异常',     # 需要T波形态
                '251199005': 'ST段异常',    # 需要ST段分析
                '251146004': '心电轴偏移',   # 需要向量分析
                '270492004': '一度房室阻滞', # 需要PR间期
                '698252002': '二度房室阻滞', # 需要P-QRS关系
                '164865005': '完全性房室阻滞' # 需要房室分离分析
            },
            
            # 节律依赖的疾病（可用HRV分析）
            'rhythm_dependent': {
                '426177001': '窦性心动过缓',  # 心率+规律性
                '426783006': '窦性心律',     # 心率+规律性
                '427084000': '心房颤动',     # 完全不规律
                '164889003': '心律不齐',     # 不规律程度
                '164890007': '室性心律失常', # 严重不规律
                '284470004': '心房早搏',     # 偶发不规律
                '39732003': '室性早搏',      # 偶发不规律
                '59931005': '房室交界性心律' # 特殊节律
            },
            
            # 功能性疾病（HRV敏感）
            'functional_dependent': {
                '55827005': '心肌缺血',     # 自主神经功能异常
                '233917008': '主动脉瓣狭窄', # 血流动力学改变
                '164909002': '左心房扩大',   # 压力负荷
                '164912004': '右心房扩大',   # 压力负荷
                '164917005': '双房扩大'      # 双侧负荷
            },
            
            # 非特异性异常
            'nonspecific': {
                '164934002': '心电图异常'    # 泛指各种异常
            }
        }
    
    def analyze_diagnostic_paradigms(self, csv_file):
        """分析两种诊断范式的差异"""
        print("🔍 分析医师诊断vs数据驱动诊断的根本差异...")
        
        # 读取原始数据和诊断结果
        original_df = pd.read_csv('enhanced_ecg_analysis_results.csv')
        comparison_df = pd.read_csv('ecg_diagnosis_comparison.csv')
        
        analysis_results = {
            'paradigm_differences': self._analyze_paradigm_differences(original_df, comparison_df),
            'information_gap': self._analyze_information_gap(original_df),
            'diagnostic_focus': self._analyze_diagnostic_focus(comparison_df),
            'accuracy_by_category': self._analyze_accuracy_by_category(comparison_df),
            'methodological_limitations': self._analyze_methodological_limitations(original_df)
        }
        
        return analysis_results
    
    def _analyze_paradigm_differences(self, original_df, comparison_df):
        """分析诊断范式差异"""
        print("\n📊 诊断范式对比分析:")
        print("=" * 60)
        
        paradigm_analysis = {
            '医师诊断特点': {
                '信息来源': '完整12导联ECG波形图',
                '分析方法': '形态学+节律学+临床经验',
                '诊断依据': 'QRS波形、ST-T变化、PR间期、电轴',
                '优势': '全面、准确、符合医学标准',
                '局限': '主观性、经验依赖、无法量化HRV'
            },
            
            '数据驱动诊断特点': {
                '信息来源': 'R峰时间序列+HRV统计指标',  
                '分析方法': '数值阈值判断+统计学分析',
                '诊断依据': '心率、HRV指标、信号质量、一致性',
                '优势': '客观、量化、自动化、HRV敏感',
                '局限': '缺少形态学信息、经验不足'
            }
        }
        
        print("🏥 医师诊断范式:")
        for key, value in paradigm_analysis['医师诊断特点'].items():
            print(f"  {key}: {value}")
        
        print("\n🤖 数据驱动诊断范式:")  
        for key, value in paradigm_analysis['数据驱动诊断特点'].items():
            print(f"  {key}: {value}")
            
        return paradigm_analysis
    
    def _analyze_information_gap(self, df):
        """分析信息缺失造成的诊断差异"""
        print(f"\n🔍 信息缺失分析:")
        print("-" * 40)
        
        # 统计每个疾病类别的出现频次
        all_diagnoses = []
        for _, row in df.iterrows():
            diagnosis = row['diagnosis']
            if pd.notna(diagnosis):
                codes = diagnosis.split(',')
                all_diagnoses.extend([code.strip() for code in codes])
        
        diagnosis_counts = Counter(all_diagnoses)
        
        # 按疾病类别分组分析
        category_stats = {}
        for category, diseases in self.disease_categories.items():
            category_count = sum(diagnosis_counts.get(code, 0) for code in diseases.keys())
            category_stats[category] = {
                'count': category_count,
                'percentage': category_count / len(all_diagnoses) * 100,
                'diseases': diseases
            }
        
        print("按疾病特征分类统计:")
        for category, stats in category_stats.items():
            category_name = {
                'morphology_dependent': '形态学依赖疾病',
                'rhythm_dependent': '节律依赖疾病', 
                'functional_dependent': '功能性疾病',
                'nonspecific': '非特异性异常'
            }.get(category, category)
            
            print(f"  {category_name}: {stats['count']}次 ({stats['percentage']:.1f}%)")
            
            # 显示具体疾病
            for code, name in stats['diseases'].items():
                count = diagnosis_counts.get(code, 0)
                if count > 0:
                    print(f"    - {name}: {count}次")
        
        # 分析信息缺失的影响
        morphology_ratio = category_stats['morphology_dependent']['percentage']
        rhythm_ratio = category_stats['rhythm_dependent']['percentage']
        
        info_gap_analysis = {
            'morphology_loss': f"形态学疾病占{morphology_ratio:.1f}%，但HRV分析无法识别",
            'rhythm_advantage': f"节律疾病占{rhythm_ratio:.1f}%，HRV分析有优势",
            'detection_capability': {
                'high': '节律依赖疾病（心房颤动、心律不齐）',
                'medium': '功能性疾病（心肌缺血、心动过缓）',
                'low': '形态学疾病（传导阻滞、心肌损伤）'
            }
        }
        
        print(f"\n关键发现:")
        print(f"  - {info_gap_analysis['morphology_loss']}")
        print(f"  - {info_gap_analysis['rhythm_advantage']}")
        
        return category_stats, info_gap_analysis
    
    def _analyze_diagnostic_focus(self, comparison_df):
        """分析两种诊断方法的关注点差异"""
        print(f"\n🎯 诊断关注点差异分析:")
        print("-" * 40)
        
        # 统计原始诊断和预测诊断的分布
        orig_diagnoses = []
        pred_diagnoses = []
        
        for _, row in comparison_df.iterrows():
            if pd.notna(row['original_diagnosis']):
                orig_codes = row['original_diagnosis'].split(',')
                orig_diagnoses.extend([code.strip() for code in orig_codes])
            
            if pd.notna(row['predicted_diagnosis']):
                pred_codes = row['predicted_diagnosis'].split(',')
                pred_diagnoses.extend([code.strip() for code in pred_codes])
        
        orig_counter = Counter(orig_diagnoses)
        pred_counter = Counter(pred_diagnoses)
        
        # 找出诊断关注点的差异
        focus_differences = {
            '医师关注但算法忽略': [],
            '算法关注但医师较少': [],
            '双方都关注': []
        }
        
        all_codes = set(orig_counter.keys()) | set(pred_counter.keys())
        
        for code in all_codes:
            orig_count = orig_counter.get(code, 0)
            pred_count = pred_counter.get(code, 0)
            
            if orig_count >= 5 and pred_count < orig_count * 0.3:
                focus_differences['医师关注但算法忽略'].append((code, orig_count, pred_count))
            elif pred_count >= 5 and orig_count < pred_count * 0.3:
                focus_differences['算法关注但医师较少'].append((code, orig_count, pred_count))
            elif orig_count >= 3 and pred_count >= 3:
                focus_differences['双方都关注'].append((code, orig_count, pred_count))
        
        # 转换为中文名称并显示
        code_to_name = {}
        for category in self.disease_categories.values():
            code_to_name.update(category)
        
        for focus_type, codes_list in focus_differences.items():
            print(f"\n{focus_type}:")
            for code, orig_count, pred_count in codes_list:
                name = code_to_name.get(code, f"未知({code})")
                print(f"  - {name}: 医师{orig_count}次, 算法{pred_count}次")
        
        return focus_differences, orig_counter, pred_counter
    
    def _analyze_accuracy_by_category(self, comparison_df):
        """按疾病类别分析诊断准确性"""
        print(f"\n📈 分疾病类别准确性分析:")
        print("-" * 40)
        
        category_accuracy = {}
        
        for category_name, diseases in self.disease_categories.items():
            category_results = {
                'total_cases': 0,
                'correct_detections': 0,
                'missed_detections': 0,
                'false_positives': 0,
                'accuracy_rate': 0
            }
            
            for _, row in comparison_df.iterrows():
                orig_codes = set(row['original_diagnosis'].split(',')) if pd.notna(row['original_diagnosis']) else set()
                pred_codes = set(row['predicted_diagnosis'].split(',')) if pd.notna(row['predicted_diagnosis']) else set()
                
                # 该类别在原始诊断中的疾病
                orig_category_codes = orig_codes & diseases.keys()
                pred_category_codes = pred_codes & diseases.keys()
                
                if orig_category_codes:  # 原始诊断包含该类别疾病
                    category_results['total_cases'] += 1
                    
                    # 计算正确检出、漏检
                    correctly_detected = len(orig_category_codes & pred_category_codes)
                    missed = len(orig_category_codes - pred_category_codes)
                    
                    if correctly_detected > 0:
                        category_results['correct_detections'] += 1
                    if missed > 0:
                        category_results['missed_detections'] += 1
                
                # 误诊检测
                false_positive_codes = pred_category_codes - orig_codes
                if false_positive_codes:
                    category_results['false_positives'] += len(false_positive_codes)
            
            # 计算准确率
            if category_results['total_cases'] > 0:
                category_results['accuracy_rate'] = category_results['correct_detections'] / category_results['total_cases']
            
            category_accuracy[category_name] = category_results
        
        # 显示结果
        category_names = {
            'morphology_dependent': '形态学依赖疾病',
            'rhythm_dependent': '节律依赖疾病',
            'functional_dependent': '功能性疾病', 
            'nonspecific': '非特异性异常'
        }
        
        for category, results in category_accuracy.items():
            if results['total_cases'] > 0:
                name = category_names.get(category, category)
                print(f"\n{name}:")
                print(f"  总病例: {results['total_cases']}")
                print(f"  正确检出: {results['correct_detections']} ({results['accuracy_rate']:.1%})")
                print(f"  漏检: {results['missed_detections']}")
                print(f"  误检: {results['false_positives']}")
        
        return category_accuracy
    
    def _analyze_methodological_limitations(self, df):
        """分析方法学局限性"""
        print(f"\n⚠️  方法学局限性分析:")
        print("-" * 40)
        
        limitations = {
            'HRV方法局限性': {
                '形态学盲区': '无法分析QRS、P波、T波形态',
                '间期测量缺失': '无法测量PR、QT、QRS间期',
                '电轴分析缺失': '无法进行心电轴计算',
                '导联间关系': '缺少导联间ST-T对应分析',
                '动态变化': '仅10秒静态分析，缺少动态监测'
            },
            
            '医师诊断优势': {
                '形态学专业性': '训练有素的波形识别能力',
                '临床相关性': '结合患者症状、病史、体征',
                '经验积累': '大量病例积累的模式识别',
                '动态判断': '可结合多时间点ECG变化',
                '质量控制': '能识别伪差、干扰等技术问题'
            },
            
            'HRV分析优势': {
                '量化精确': '提供精确的数值化指标',
                '自主神经': '敏感检测自主神经功能状态',
                '客观性': '避免主观判断差异',
                '批量处理': '可自动分析大量数据',
                '隐藏信息': '发现肉眼难以察觉的微小变化'
            }
        }
        
        for category, items in limitations.items():
            print(f"\n{category}:")
            for key, value in items.items():
                print(f"  - {key}: {value}")
        
        # 数据质量影响分析
        print(f"\n📊 数据质量对诊断的影响:")
        quality_stats = self._analyze_data_quality_impact(df)
        
        return limitations, quality_stats
    
    def _analyze_data_quality_impact(self, df):
        """分析数据质量对诊断准确性的影响"""
        quality_impact = {}
        
        # 解析信号质量数据
        snr_values = []
        for _, row in df.iterrows():
            quality_str = row.get('quality', '{}')
            try:
                quality_str = str(quality_str).replace("'", '"')
                quality_str = re.sub(r'np\.float64\((.*?)\)', r'\1', quality_str)
                quality_dict = ast.literal_eval(quality_str)
                snr = quality_dict.get('snr_db', np.nan)
                if not pd.isna(snr):
                    snr_values.append(snr)
            except:
                continue
        
        if snr_values:
            quality_impact = {
                'snr_mean': np.mean(snr_values),
                'snr_std': np.std(snr_values),
                'snr_min': np.min(snr_values),
                'snr_max': np.max(snr_values),
                'poor_quality_ratio': np.sum(np.array(snr_values) < 10) / len(snr_values)
            }
            
            print(f"  信号质量统计 (SNR):")
            print(f"    平均: {quality_impact['snr_mean']:.1f} dB")
            print(f"    范围: {quality_impact['snr_min']:.1f} - {quality_impact['snr_max']:.1f} dB")
            print(f"    质量差占比: {quality_impact['poor_quality_ratio']:.1%} (SNR < 10dB)")
        
        return quality_impact
    
    def generate_comprehensive_report(self, csv_file):
        """生成综合差异分析报告"""
        analysis_results = self.analyze_diagnostic_paradigms(csv_file)
        
        # 生成结论
        print(f"\n🎯 差异根本原因总结:")
        print("=" * 60)
        
        conclusions = [
            "1. 信息维度差异：医师看'形态'，算法算'节律'",
            "2. 专业知识差异：医师有临床经验，算法依赖统计规律", 
            "3. 诊断标准差异：医师遵循医学指南，算法基于数值阈值",
            "4. 应用场景差异：医师适合确诊，算法适合筛查",
            "5. 互补价值：结合使用可提供更全面的心电评估"
        ]
        
        for conclusion in conclusions:
            print(f"  {conclusion}")
        
        return analysis_results

def main():
    analyzer = DiagnosisDiscrepancyAnalyzer()
    results = analyzer.generate_comprehensive_report('enhanced_ecg_analysis_results.csv')
    return analyzer, results

if __name__ == '__main__':
    analyzer, results = main()