#!/usr/bin/env python3
"""
综合诊断分析：ECG内置诊断 vs v4.0算法诊断
"""

import os
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

def extract_built_in_diagnoses(data_dir):
    """提取所有ECG文件的内置SNOMED-CT诊断"""
    
    # SNOMED-CT代码到中文名称的完整映射
    snomed_to_chinese = {
        '164889003': '房性心律失常',
        '59118001': '右束支阻滞',
        '164934002': '心房颤动',
        '426177001': '束支阻滞',
        '164890007': '室性心律失常',
        '429622005': '左前分支阻滞',
        '428750005': '左束支阻滞',
        '251146004': '左束支阻滞',
        '39732003': '左心室肥厚',
        '164909002': '左轴偏转',
        '427393009': '窦性心动过缓',
        '426783006': '窦性心律',
        '164917005': '心律不齐',
        '413444003': '心肌缺血',
        '164931005': '一度房室阻滞',
        '164884008': '心电图异常',
        '426627000': '心动过速',
        '445118002': '左心房扩大',
        '428417006': '下壁心肌梗死',
        '164865005': '二度房室阻滞',
        '164873001': '窦性停搏',
        '164895008': '窦房传导阻滞',
        '418818005': '房性期前收缩',
        '428750005': '左束支传导阻滞',
        '17338001': '室性期前收缩'
    }
    
    built_in_diagnoses = []
    
    # 获取所有.hea文件
    hea_files = [f for f in os.listdir(data_dir) if f.endswith('.hea')]
    hea_files.sort()
    
    print(f"🔍 分析 {len(hea_files)} 个ECG记录的内置诊断...")
    
    for hea_file in hea_files:
        record_name = hea_file.replace('.hea', '')
        file_path = os.path.join(data_dir, hea_file)
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # 解析患者信息
            age = 'Unknown'
            sex = 'Unknown'
            diagnosis_codes = []
            
            for line in content.split('\\n'):
                line = line.strip()
                if line.startswith('#Age:'):
                    age = line.split(': ')[1]
                elif line.startswith('#Sex:'):
                    sex = line.split(': ')[1]
                elif line.startswith('#Dx:'):
                    dx_part = line.split(': ')[1]
                    diagnosis_codes = [code.strip() for code in dx_part.split(',') if code.strip()]
            
            # 转换为中文诊断
            chinese_diagnoses = []
            for code in diagnosis_codes:
                if code in snomed_to_chinese:
                    chinese_diagnoses.append(snomed_to_chinese[code])
                else:
                    chinese_diagnoses.append(f"未知诊断({code})")
            
            built_in_diagnoses.append({
                'record_name': record_name,
                'age': age,
                'sex': sex,
                'snomed_codes': ','.join(diagnosis_codes),
                'chinese_diagnosis': ' + '.join(chinese_diagnoses) if chinese_diagnoses else '无诊断',
                'diagnosis_count': len(diagnosis_codes)
            })
            
        except Exception as e:
            print(f"解析 {hea_file} 时出错: {e}")
            continue
    
    return pd.DataFrame(built_in_diagnoses)

def load_algorithm_results():
    """加载v4.0算法诊断结果"""
    
    # SNOMED-CT代码到中文名称的映射
    code_to_chinese = {
        '426627000': '心动过速',
        '426177001': '束支阻滞', 
        '164889003': '房性心律失常',
        '59118001': '右束支阻滞',
        '164934002': '心房颤动',
        '251146004': '左束支阻滞',
        '39732003': '左心室肥厚',
        '164909002': '左轴偏转',
        '427393009': '窦性心动过缓',
        '426783006': '窦性心律',
        '164917005': '心律不齐',
        '413444003': '心肌缺血',
        '164931005': '一度房室阻滞',
        '164884008': '心电图异常'
    }
    
    try:
        # 读取v4.0算法结果
        algo_df = pd.read_csv('/Users/williamsun/Documents/gplus/docs/ECG/report/v4_diagnosis_results/integrated_algorithm_diagnosis_v4.csv')
        
        # 转换算法诊断为中文
        algorithm_results = []
        
        for idx, row in algo_df.iterrows():
            algo_codes = row['algorithm_diagnosis'].split(',') if row['algorithm_diagnosis'] else []
            algo_chinese = []
            
            for code in algo_codes:
                chinese_name = code_to_chinese.get(code.strip(), f"未知代码({code.strip()})")
                algo_chinese.append(chinese_name)
            
            algorithm_results.append({
                'record_name': row['record_name'],
                'algorithm_codes': row['algorithm_diagnosis'],
                'algorithm_chinese': ' + '.join(algo_chinese) if algo_chinese else '无诊断',
                'confidence': row['diagnosis_confidence'],
                'features_total': row['features_used_total'],
                'features_morphology': row['features_used_morphology']
            })
        
        return pd.DataFrame(algorithm_results)
        
    except Exception as e:
        print(f"加载算法结果时出错: {e}")
        return None

def comprehensive_comparison_analysis(built_in_df, algorithm_df):
    """综合对比分析"""
    
    # 合并数据
    merged_df = pd.merge(built_in_df, algorithm_df, on='record_name', how='inner')
    
    print(f"\n📊 数据概览:")
    print(f"   - 内置诊断记录数: {len(built_in_df)}")
    print(f"   - 算法诊断记录数: {len(algorithm_df)}")
    print(f"   - 成功匹配记录数: {len(merged_df)}")
    
    # 统计分析
    analysis_results = {
        'total_records': len(merged_df),
        'exact_matches': 0,
        'partial_matches': 0,
        'no_matches': 0,
        'jaccard_scores': [],
        'precision_scores': [],
        'recall_scores': []
    }
    
    detailed_results = []
    
    print(f"\\n🔍 详细诊断对比 (前15个):")
    print("=" * 120)
    
    for idx, row in merged_df.head(15).iterrows():
        # 解析诊断
        builtin_diagnoses = set(row['chinese_diagnosis'].split(' + ')) if row['chinese_diagnosis'] != '无诊断' else set()
        algorithm_diagnoses = set(row['algorithm_chinese'].split(' + ')) if row['algorithm_chinese'] != '无诊断' else set()
        
        # 计算相似度指标
        intersection = builtin_diagnoses.intersection(algorithm_diagnoses)
        union = builtin_diagnoses.union(algorithm_diagnoses)
        
        exact_match = builtin_diagnoses == algorithm_diagnoses
        jaccard = len(intersection) / len(union) if union else 0
        precision = len(intersection) / len(algorithm_diagnoses) if algorithm_diagnoses else 0
        recall = len(intersection) / len(builtin_diagnoses) if builtin_diagnoses else 0
        
        # 统计
        if exact_match:
            analysis_results['exact_matches'] += 1
            match_status = "✅ 完全匹配"
        elif len(intersection) > 0:
            analysis_results['partial_matches'] += 1
            match_status = f"🔶 部分匹配({len(intersection)}个)"
        else:
            analysis_results['no_matches'] += 1
            match_status = "❌ 无匹配"
        
        analysis_results['jaccard_scores'].append(jaccard)
        analysis_results['precision_scores'].append(precision)
        analysis_results['recall_scores'].append(recall)
        
        # 显示结果
        print(f"记录 {row['record_name']} ({row['age']}岁 {row['sex']})")
        print(f"  📋 内置诊断: {row['chinese_diagnosis']}")
        print(f"  🤖 算法诊断: {row['algorithm_chinese']}")
        print(f"  📊 结果评估: {match_status}")
        print(f"  📈 相似度指标: Jaccard={jaccard:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")
        print(f"  🔧 特征使用: 总{row['features_total']}个 (形态学{row['features_morphology']}个), 置信度{row['confidence']:.3f}")
        print()
        
        detailed_results.append({
            'record_name': row['record_name'],
            'builtin_diagnosis': row['chinese_diagnosis'],
            'algorithm_diagnosis': row['algorithm_chinese'],
            'exact_match': exact_match,
            'jaccard_similarity': jaccard,
            'precision': precision,
            'recall': recall,
            'match_status': match_status,
            'confidence': row['confidence'],
            'features_total': row['features_total'],
            'features_morphology': row['features_morphology']
        })
    
    # 计算总体统计
    total_records = analysis_results['total_records']
    exact_match_rate = (analysis_results['exact_matches'] / total_records) * 100
    partial_match_rate = (analysis_results['partial_matches'] / total_records) * 100
    total_match_rate = ((analysis_results['exact_matches'] + analysis_results['partial_matches']) / total_records) * 100
    
    avg_jaccard = np.mean(analysis_results['jaccard_scores'])
    avg_precision = np.mean(analysis_results['precision_scores'])
    avg_recall = np.mean(analysis_results['recall_scores'])
    avg_f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
    
    print("=" * 80)
    print("🎯 综合诊断分析结果")
    print("=" * 80)
    print(f"总分析病例数: {total_records}")
    print(f"完全匹配: {analysis_results['exact_matches']} 例 ({exact_match_rate:.2f}%)")
    print(f"部分匹配: {analysis_results['partial_matches']} 例 ({partial_match_rate:.2f}%)")
    print(f"无匹配: {analysis_results['no_matches']} 例 ({(analysis_results['no_matches']/total_records)*100:.2f}%)")
    print(f"总体有效匹配率: {exact_match_rate + partial_match_rate:.2f}%")
    print()
    print(f"📊 平均性能指标:")
    print(f"   - Jaccard相似度: {avg_jaccard:.3f}")
    print(f"   - 精确率 (Precision): {avg_precision:.3f}")
    print(f"   - 召回率 (Recall): {avg_recall:.3f}")
    print(f"   - F1分数: {avg_f1:.3f}")
    print()
    print(f"🆕 v4.0系统特征:")
    print(f"   - 平均置信度: {merged_df['confidence'].mean():.3f}")
    print(f"   - 平均特征使用数: {merged_df['features_total'].mean():.1f}")
    print(f"   - 平均形态学特征数: {merged_df['features_morphology'].mean():.1f}")
    
    # 诊断类型分析
    print(f"\\n🔍 诊断类型分析:")
    builtin_all_diagnoses = []
    algorithm_all_diagnoses = []
    
    for _, row in merged_df.iterrows():
        if row['chinese_diagnosis'] != '无诊断':
            builtin_all_diagnoses.extend(row['chinese_diagnosis'].split(' + '))
        if row['algorithm_chinese'] != '无诊断':
            algorithm_all_diagnoses.extend(row['algorithm_chinese'].split(' + '))
    
    builtin_counter = Counter(builtin_all_diagnoses)
    algorithm_counter = Counter(algorithm_all_diagnoses)
    
    print("   内置诊断分布 (前10):")
    for diagnosis, count in builtin_counter.most_common(10):
        print(f"     {diagnosis}: {count} 例 ({count/len(merged_df)*100:.1f}%)")
    
    print("   算法诊断分布 (前10):")
    for diagnosis, count in algorithm_counter.most_common(10):
        print(f"     {diagnosis}: {count} 例 ({count/len(merged_df)*100:.1f}%)")
    
    return {
        'summary': analysis_results,
        'detailed_results': detailed_results,
        'merged_data': merged_df,
        'performance_metrics': {
            'exact_match_rate': exact_match_rate,
            'partial_match_rate': partial_match_rate,
            'total_match_rate': total_match_rate,
            'avg_jaccard': avg_jaccard,
            'avg_precision': avg_precision,
            'avg_recall': avg_recall,
            'avg_f1': avg_f1
        }
    }

def save_detailed_results(results, output_path):
    """保存详细对比结果"""
    detailed_df = pd.DataFrame(results['detailed_results'])
    detailed_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\\n💾 详细对比结果已保存至: {output_path}")

if __name__ == '__main__':
    data_dir = '/Users/williamsun/Documents/gplus/docs/ECG/ECG_demodata/01/010'
    
    print("🚀 启动综合ECG诊断分析")
    print("🔍 分析目标: ECG内置诊断 vs v4.0算法诊断")
    print("=" * 60)
    
    # 1. 提取内置诊断
    print("\\n步骤1: 提取ECG文件内置诊断...")
    built_in_df = extract_built_in_diagnoses(data_dir)
    
    # 2. 加载算法结果
    print("\\n步骤2: 加载v4.0算法诊断结果...")
    algorithm_df = load_algorithm_results()
    
    if algorithm_df is None:
        print("❌ 无法加载算法结果，请先运行v4.0诊断系统")
        exit(1)
    
    # 3. 综合对比分析
    print("\\n步骤3: 执行综合对比分析...")
    results = comprehensive_comparison_analysis(built_in_df, algorithm_df)
    
    # 4. 保存结果
    output_path = '/Users/williamsun/Documents/gplus/docs/ECG/report/comprehensive_diagnosis_comparison.csv'
    save_detailed_results(results, output_path)
    
    print("\\n✅ 综合分析完成!")
    print(f"🎯 关键发现: v4.0系统在与ECG内置诊断对比中达到 {results['performance_metrics']['total_match_rate']:.1f}% 的总体匹配率")
    
    if results['performance_metrics']['exact_match_rate'] > 10:
        print("🎉 优秀表现! 算法诊断与内置诊断有很好的一致性")
    elif results['performance_metrics']['total_match_rate'] > 30:
        print("👍 良好表现! 算法能够识别大部分主要诊断")
    else:
        print("⚠️  仍有改进空间，建议进一步优化诊断规则")