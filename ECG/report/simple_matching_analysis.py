#!/usr/bin/env python3
"""
简单匹配度分析：算法诊断 vs 内置诊断
"""

import pandas as pd
import numpy as np

def calculate_matching_rate():
    """计算算法诊断与内置诊断的匹配度"""
    
    print("📊 算法诊断与内置诊断匹配度分析")
    print("=" * 50)
    
    # 加载数据
    original_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/v4_diagnosis_detailed_comparison.csv'
    optimized_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/v4_optimized_diagnosis_results_final.csv'
    
    try:
        original_df = pd.read_csv(original_file)
        optimized_df = pd.read_csv(optimized_file)
        print(f"✅ 数据加载成功")
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return
    
    # 获取重叠记录
    common_records = list(set(original_df['record_name']).intersection(set(optimized_df['record_name'])))
    common_records.sort()
    
    print(f"\n🔍 分析记录数: {len(common_records)}条")
    print("-" * 50)
    
    # 原始V4.0匹配情况
    print("📋 原始V4.0算法 vs 内置诊断:")
    original_matches = 0
    for record in common_records:
        orig_row = original_df[original_df['record_name'] == record].iloc[0]
        builtin = str(orig_row['builtin_diagnosis']).lower()
        algorithm = str(orig_row['v4_algorithm_diagnosis']).lower()
        
        # 简单匹配判断
        if has_overlap(builtin, algorithm):
            original_matches += 1
    
    original_rate = (original_matches / len(common_records)) * 100
    print(f"   匹配数: {original_matches}/{len(common_records)}")
    print(f"   匹配率: {original_rate:.1f}%")
    
    # 优化后V4.0匹配情况
    print(f"\n📋 优化V4.0算法 vs 内置诊断:")
    optimized_matches = 0
    for record in common_records:
        orig_row = original_df[original_df['record_name'] == record].iloc[0]
        opt_row = optimized_df[optimized_df['record_name'] == record].iloc[0]
        
        builtin = str(orig_row['builtin_diagnosis']).lower()
        algorithm_opt = str(opt_row['algorithm_diagnosis_optimized']).lower()
        
        # 简单匹配判断
        if has_overlap(builtin, algorithm_opt):
            optimized_matches += 1
    
    optimized_rate = (optimized_matches / len(common_records)) * 100
    print(f"   匹配数: {optimized_matches}/{len(common_records)}")
    print(f"   匹配率: {optimized_rate:.1f}%")
    
    # 对比改进
    improvement = optimized_rate - original_rate
    print(f"\n🎯 匹配度改进:")
    print(f"   改进幅度: {improvement:+.1f}个百分点")
    if improvement > 0:
        print(f"   ✅ 匹配度有所提升")
    elif improvement < 0:
        print(f"   ⚠️  匹配度有所下降")
    else:
        print(f"   ➖ 匹配度无变化")
    
    # 显示几个具体例子
    print(f"\n📝 具体对比示例 (前10例):")
    print("-" * 70)
    for i, record in enumerate(common_records[:10]):
        orig_row = original_df[original_df['record_name'] == record].iloc[0]
        opt_row = optimized_df[optimized_df['record_name'] == record].iloc[0]
        
        builtin = orig_row['builtin_diagnosis']
        orig_algo = orig_row['v4_algorithm_diagnosis'] 
        opt_algo = opt_row['algorithm_diagnosis_optimized']
        
        print(f"{record}:")
        print(f"  内置: {builtin}")
        print(f"  原版: {orig_algo}")
        print(f"  优化: {opt_algo}")
        print()
    
    return {
        'original_rate': original_rate,
        'optimized_rate': optimized_rate,
        'improvement': improvement,
        'total_records': len(common_records)
    }

def has_overlap(str1, str2):
    """简单判断两个诊断字符串是否有重叠"""
    if pd.isna(str1) or pd.isna(str2):
        return False
    
    # 关键词匹配
    keywords1 = set([word.strip() for word in str1.replace(',', ' ').split() if len(word.strip()) > 1])
    keywords2 = set([word.strip() for word in str2.replace(',', ' ').split() if len(word.strip()) > 1])
    
    # 检查是否有交集
    return len(keywords1.intersection(keywords2)) > 0

if __name__ == '__main__':
    result = calculate_matching_rate()
    
    if result:
        print(f"✅ 匹配度分析完成")
        print(f"📊 关键结论: 匹配率从{result['original_rate']:.1f}%变化至{result['optimized_rate']:.1f}%")