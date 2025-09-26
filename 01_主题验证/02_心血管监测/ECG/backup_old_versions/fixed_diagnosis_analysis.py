#!/usr/bin/env python3
"""
修复版诊断分析：ECG内置诊断 vs v4.0算法诊断
"""

import os
import pandas as pd
import numpy as np
from collections import Counter

def extract_built_in_diagnoses_fixed(data_dir):
    """修复版：提取所有ECG文件的内置SNOMED-CT诊断"""
    
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
                lines = f.readlines()
            
            # 解析患者信息
            age = 'Unknown'
            sex = 'Unknown'
            diagnosis_codes = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('#Age:'):
                    age = line.split(': ')[1] if ': ' in line else 'Unknown'
                elif line.startswith('#Sex:'):
                    sex = line.split(': ')[1] if ': ' in line else 'Unknown'
                elif line.startswith('#Dx:'):
                    dx_part = line.split(': ')[1] if ': ' in line else ''
                    if dx_part:
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
                'diagnosis_count': len(diagnosis_codes),
                'raw_codes': diagnosis_codes  # 保留原始代码用于调试
            })
            
        except Exception as e:
            print(f"解析 {hea_file} 时出错: {e}")
            continue
    
    return pd.DataFrame(built_in_diagnoses)

def load_algorithm_results_fixed():
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

def comprehensive_comparison_analysis_fixed(built_in_df, algorithm_df):
    """修复版综合对比分析"""
    
    # 合并数据
    merged_df = pd.merge(built_in_df, algorithm_df, on='record_name', how='inner')
    
    print(f"\\n📊 数据概览:")
    print(f"   - 内置诊断记录数: {len(built_in_df)}")
    print(f"   - 算法诊断记录数: {len(algorithm_df)}")
    print(f"   - 成功匹配记录数: {len(merged_df)}")
    
    # 检查内置诊断是否被正确解析
    valid_diagnoses = merged_df[merged_df['chinese_diagnosis'] != '无诊断']
    print(f"   - 有内置诊断的记录数: {len(valid_diagnoses)}")
    print(f"   - 无内置诊断的记录数: {len(merged_df) - len(valid_diagnoses)}")
    
    # 统计分析
    analysis_results = {
        'total_records': len(merged_df),
        'records_with_builtin_dx': len(valid_diagnoses),
        'exact_matches': 0,
        'partial_matches': 0,
        'no_matches': 0,
        'jaccard_scores': [],
        'precision_scores': [],
        'recall_scores': []
    }
    
    detailed_results = []
    
    # 为所有100个记录生成详细结果
    print(f"\\n📊 生成完整的{len(merged_df)}个记录详细对比数据...")
    for idx, row in merged_df.iterrows():
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
        
        # 匹配状态
        if exact_match:
            match_status = "✅ 完全匹配"
        elif len(intersection) > 0:
            match_status = f"🔶 部分匹配({len(intersection)}个)"
        else:
            match_status = "❌ 无匹配"
        
        detailed_results.append({
            'record_name': row['record_name'],
            'age': row['age'],
            'sex': row['sex'],
            'builtin_snomed': row['snomed_codes'],
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
    
    print(f"✅ 已生成{len(detailed_results)}个记录的详细对比数据")
    
    print(f"\\n🔍 内置诊断示例 (前10个有诊断的记录):")
    print("=" * 120)
    
    # 显示前10个有内置诊断的记录
    records_to_show = valid_diagnoses.head(10) if len(valid_diagnoses) > 0 else merged_df.head(10)
    
    print(f"🔍 内置诊断示例 (前10个有诊断的记录):")
    print("=" * 120)
    
    for idx, row in records_to_show.iterrows():
        # 解析诊断
        builtin_diagnoses = set(row['chinese_diagnosis'].split(' + ')) if row['chinese_diagnosis'] != '无诊断' else set()
        algorithm_diagnoses = set(row['algorithm_chinese'].split(' + ')) if row['algorithm_chinese'] != '无诊断' else set()
        
        # 计算相似度指标
        intersection = builtin_diagnoses.intersection(algorithm_diagnoses)
        union = builtin_diagnoses.union(algorithm_diagnoses)
        
        exact_match = builtin_diagnoses == algorithm_diagnoses and len(builtin_diagnoses) > 0
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
        print(f"  📋 内置SNOMED: {row['snomed_codes']}")
        print(f"  📋 内置诊断: {row['chinese_diagnosis']}")
        print(f"  🤖 算法诊断: {row['algorithm_chinese']}")
        print(f"  📊 结果评估: {match_status}")
        print(f"  📈 相似度指标: Jaccard={jaccard:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")
        print(f"  🔧 算法特征: 总{row['features_total']}个 (形态学{row['features_morphology']}个), 置信度{row['confidence']:.3f}")
        print()
    
    # 计算统计仅基于有内置诊断的记录
    if len(valid_diagnoses) > 0:
        # 重新计算基于有效记录的统计
        valid_analysis = []
        for idx, row in valid_diagnoses.iterrows():
            builtin_diagnoses = set(row['chinese_diagnosis'].split(' + '))
            algorithm_diagnoses = set(row['algorithm_chinese'].split(' + ')) if row['algorithm_chinese'] != '无诊断' else set()
            
            intersection = builtin_diagnoses.intersection(algorithm_diagnoses)
            union = builtin_diagnoses.union(algorithm_diagnoses)
            
            jaccard = len(intersection) / len(union) if union else 0
            precision = len(intersection) / len(algorithm_diagnoses) if algorithm_diagnoses else 0
            recall = len(intersection) / len(builtin_diagnoses) if builtin_diagnoses else 0
            
            valid_analysis.append({
                'exact_match': builtin_diagnoses == algorithm_diagnoses,
                'has_intersection': len(intersection) > 0,
                'jaccard': jaccard,
                'precision': precision,
                'recall': recall
            })
        
        valid_df = pd.DataFrame(valid_analysis)
        valid_exact_matches = valid_df['exact_match'].sum()
        valid_partial_matches = valid_df['has_intersection'].sum() - valid_exact_matches
        
        exact_match_rate = (valid_exact_matches / len(valid_diagnoses)) * 100
        partial_match_rate = (valid_partial_matches / len(valid_diagnoses)) * 100
        total_match_rate = ((valid_exact_matches + valid_partial_matches) / len(valid_diagnoses)) * 100
        
        avg_jaccard = valid_df['jaccard'].mean()
        avg_precision = valid_df['precision'].mean()
        avg_recall = valid_df['recall'].mean()
        avg_f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
        
    else:
        exact_match_rate = partial_match_rate = total_match_rate = 0
        avg_jaccard = avg_precision = avg_recall = avg_f1 = 0
    
    print("=" * 80)
    print("🎯 修复版综合诊断分析结果")
    print("=" * 80)
    print(f"总ECG记录数: {len(merged_df)}")
    print(f"有内置诊断记录数: {len(valid_diagnoses)}")
    
    if len(valid_diagnoses) > 0:
        print(f"\\n基于有内置诊断的{len(valid_diagnoses)}个记录的分析:")
        print(f"完全匹配: {valid_exact_matches} 例 ({exact_match_rate:.2f}%)")
        print(f"部分匹配: {valid_partial_matches} 例 ({partial_match_rate:.2f}%)")
        print(f"总体有效匹配率: {total_match_rate:.2f}%")
        print()
        print(f"📊 平均性能指标:")
        print(f"   - Jaccard相似度: {avg_jaccard:.3f}")
        print(f"   - 精确率 (Precision): {avg_precision:.3f}")
        print(f"   - 召回率 (Recall): {avg_recall:.3f}")
        print(f"   - F1分数: {avg_f1:.3f}")
        
        # 诊断类型分析
        print(f"\\n🔍 内置诊断分布分析:")
        builtin_all_diagnoses = []
        
        for _, row in valid_diagnoses.iterrows():
            if row['chinese_diagnosis'] != '无诊断':
                builtin_all_diagnoses.extend(row['chinese_diagnosis'].split(' + '))
        
        builtin_counter = Counter(builtin_all_diagnoses)
        print("   内置诊断分布:")
        for diagnosis, count in builtin_counter.most_common(10):
            print(f"     {diagnosis}: {count} 例 ({count/len(valid_diagnoses)*100:.1f}%)")
            
    else:
        print("⚠️  所有记录都显示无内置诊断，可能是数据格式问题")
    
    print(f"\\n🆕 v4.0算法诊断分布:")
    algorithm_all_diagnoses = []
    for _, row in merged_df.iterrows():
        if row['algorithm_chinese'] != '无诊断':
            algorithm_all_diagnoses.extend(row['algorithm_chinese'].split(' + '))
    
    algorithm_counter = Counter(algorithm_all_diagnoses)
    for diagnosis, count in algorithm_counter.most_common(10):
        print(f"     {diagnosis}: {count} 例 ({count/len(merged_df)*100:.1f}%)")
    
    return {
        'summary': analysis_results,
        'detailed_results': detailed_results,
        'merged_data': merged_df,
        'valid_diagnoses_count': len(valid_diagnoses),
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

if __name__ == '__main__':
    data_dir = '/Users/williamsun/Documents/gplus/docs/ECG/ECG_demodata/01/010'
    
    print("🚀 启动修复版ECG诊断分析")
    print("🔍 分析目标: ECG内置诊断 vs v4.0算法诊断 (修复版)")
    print("=" * 60)
    
    # 1. 提取内置诊断
    print("\\n步骤1: 提取ECG文件内置诊断...")
    built_in_df = extract_built_in_diagnoses_fixed(data_dir)
    
    # 2. 加载算法结果
    print("\\n步骤2: 加载v4.0算法诊断结果...")
    algorithm_df = load_algorithm_results_fixed()
    
    if algorithm_df is None:
        print("❌ 无法加载算法结果，请先运行v4.0诊断系统")
        exit(1)
    
    # 3. 综合对比分析
    print("\\n步骤3: 执行修复版综合对比分析...")
    results = comprehensive_comparison_analysis_fixed(built_in_df, algorithm_df)
    
    # 4. 保存结果
    if results['detailed_results']:
        output_path = '/Users/williamsun/Documents/gplus/docs/ECG/report/fixed_comprehensive_diagnosis_comparison.csv'
        detailed_df = pd.DataFrame(results['detailed_results'])
        detailed_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\\n💾 详细对比结果已保存至: {output_path}")
    
    print("\\n✅ 修复版分析完成!")
    
    if results['valid_diagnoses_count'] > 0:
        print(f"🎯 关键发现: 在{results['valid_diagnoses_count']}个有内置诊断的记录中，v4.0系统达到 {results['performance_metrics']['total_match_rate']:.1f}% 的总体匹配率")
        
        if results['performance_metrics']['exact_match_rate'] > 10:
            print("🎉 优秀表现! 算法诊断与内置诊断有很好的一致性")
        elif results['performance_metrics']['total_match_rate'] > 30:
            print("👍 良好表现! 算法能够识别大部分主要诊断")
        else:
            print("⚠️  仍有改进空间，建议进一步优化诊断规则")
    else:
        print("⚠️  检测到数据解析问题，建议检查ECG文件格式")