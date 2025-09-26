#!/usr/bin/env python3
"""
测试优化阈值后的V4.0诊断系统效果
对比调整前后的诊断结果与专家诊断
"""

import pandas as pd
import numpy as np
from integrated_ecg_diagnosis_system import IntegratedECGDiagnosisSystem
import json
import os

def load_expert_diagnosis():
    """加载专家诊断数据"""
    expert_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/expert_diagnosis_reference.csv'
    try:
        df = pd.read_csv(expert_file)
        return df
    except Exception as e:
        print(f"无法加载专家诊断: {e}")
        return None

def test_optimized_diagnosis():
    """测试优化阈值的诊断效果"""
    
    print("🔧 V4.0阈值优化效果测试")
    print("=" * 60)
    
    # 初始化诊断系统（已包含优化阈值）
    diagnosis_system = IntegratedECGDiagnosisSystem()
    
    # 显示当前阈值设置
    print("\n📊 当前优化后的阈值设置:")
    print(f"   - QRS宽度阈值: {diagnosis_system.thresholds['qrs_wide_threshold']}ms (原120ms) ✅")
    print(f"   - ST抬高阈值: {diagnosis_system.thresholds['st_elevation_threshold']}mV (原0.1mV) ✅")  
    print(f"   - ST压低阈值: {diagnosis_system.thresholds['st_depression_threshold']}mV (原-0.1mV) ✅")
    
    # 加载ECG分析结果
    ecg_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/enhanced_ecg_analysis_results.csv'
    
    try:
        df = pd.read_csv(ecg_file)
        print(f"\n✅ 成功加载ECG数据: {len(df)}条记录")
    except Exception as e:
        print(f"❌ 加载ECG数据失败: {e}")
        return
    
    # 加载专家诊断
    expert_df = load_expert_diagnosis()
    if expert_df is None:
        print("⚠️  无专家诊断数据，仅测试算法诊断")
    
    # 分析每个记录
    print("\n🧪 使用优化阈值的诊断结果:")
    print("-" * 80)
    
    optimized_results = []
    diagnosis_stats = {}
    
    for i, row in df.head(50).iterrows():  # 测试前50条记录
        record_name = row['record_name']
        
        # 提取ECG特征
        features = {
            'mean_hr': row.get('mean_hr', 70),
            'std_hr': row.get('std_hr', 5),
            'rmssd': row.get('rmssd', 30),
            'pnn50': row.get('pnn50', 10),
            'qrs_duration_mean': row.get('qrs_duration_mean', 100),
            'st_deviation_mean': row.get('st_deviation_mean', 0),
            'r_wave_amplitude_mean': row.get('r_wave_amplitude_mean', 1.0),
            't_wave_amplitude_mean': row.get('t_wave_amplitude_mean', 0.3),
            'wide_qrs_ratio': row.get('wide_qrs_ratio', 0),
            'st_elevation_ratio': row.get('st_elevation_ratio', 0), 
            'st_depression_ratio': row.get('st_depression_ratio', 0)
        }
        
        # 使用优化阈值进行诊断
        diagnoses = diagnosis_system.enhanced_rule_based_diagnosis(features)
        
        # 统计诊断分布
        for diagnosis in diagnoses:
            diagnosis_name = diagnosis_system.diagnosis_codes.get(diagnosis, diagnosis)
            diagnosis_stats[diagnosis_name] = diagnosis_stats.get(diagnosis_name, 0) + 1
        
        # 转换为诊断名称
        diagnosis_names = [diagnosis_system.diagnosis_codes.get(code, code) for code in diagnoses]
        
        # 获取专家诊断（如果有）
        expert_diagnosis = ""
        if expert_df is not None:
            expert_row = expert_df[expert_df['record_name'] == record_name]
            if not expert_row.empty:
                expert_diagnosis = expert_row.iloc[0].get('expert_diagnosis', '')
        
        result = {
            'record_name': record_name,
            'algorithm_diagnosis_optimized': ', '.join(diagnosis_names),
            'algorithm_codes': ', '.join(diagnoses),
            'expert_diagnosis': expert_diagnosis,
            'optimization_applied': 'QRS:140ms, ST:0.2mV',
            'features_count': len([f for f in features.values() if f != 0])
        }
        
        optimized_results.append(result)
        
        # 显示前10个结果
        if i < 10:
            print(f"{record_name}: {', '.join(diagnosis_names) if diagnosis_names else '正常'}")
    
    # 保存优化后的结果
    results_df = pd.DataFrame(optimized_results)
    output_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/v4_optimized_diagnosis_results.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 优化结果已保存至: {output_file}")
    
    # 统计诊断分布
    print(f"\n📈 优化阈值后的诊断分布:")
    print("-" * 50)
    total_records = len(optimized_results)
    for diagnosis, count in sorted(diagnosis_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_records) * 100
        print(f"   {diagnosis}: {count}例 ({percentage:.1f}%)")
    
    # 对比分析（如果有专家诊断）
    if expert_df is not None:
        analyze_optimization_effect(results_df)
    
    print(f"\n🎯 阈值优化预期效果:")
    print(f"   ✅ QRS阈值140ms: 减少右束支阻滞过度诊断")
    print(f"   ✅ ST阈值0.2mV: 减少心肌缺血过度诊断")
    print(f"   📈 预计匹配率提升: 12% → 35-50%")
    
    return results_df

def analyze_optimization_effect(results_df):
    """分析优化效果"""
    print(f"\n🔍 优化效果分析:")
    print("-" * 40)
    
    # 统计与专家诊断的匹配情况
    matched = 0
    total_with_expert = 0
    
    for _, row in results_df.iterrows():
        if row['expert_diagnosis'] and str(row['expert_diagnosis']) != 'nan':
            total_with_expert += 1
            algo_diag = str(row['algorithm_diagnosis_optimized']).lower()
            expert_diag = str(row['expert_diagnosis']).lower()
            
            # 简单的匹配逻辑
            if algo_diag in expert_diag or expert_diag in algo_diag:
                matched += 1
    
    if total_with_expert > 0:
        match_rate = (matched / total_with_expert) * 100
        print(f"   匹配率: {matched}/{total_with_expert} ({match_rate:.1f}%)")
        print(f"   改进预期: 从12%提升至{match_rate:.1f}%")

if __name__ == '__main__':
    test_optimized_diagnosis()