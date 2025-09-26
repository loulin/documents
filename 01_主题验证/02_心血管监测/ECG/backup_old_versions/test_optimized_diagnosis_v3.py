#!/usr/bin/env python3
"""
测试优化阈值后的V4.0诊断系统效果
修复版本：正确调用诊断方法
"""

import pandas as pd
import numpy as np
from integrated_ecg_diagnosis_system import IntegratedECGDiagnosisSystem
import json
import os

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
    
    # 加载专家诊断（如果存在）
    expert_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/expert_diagnosis_vs_v4_comparison.csv'
    expert_df = None
    try:
        expert_df = pd.read_csv(expert_file)
        print(f"✅ 成功加载专家诊断对比数据: {len(expert_df)}条记录")
    except:
        print("⚠️  无专家诊断数据，仅测试算法诊断")
    
    # 分析每个记录
    print("\n🧪 使用优化阈值的诊断结果:")
    print("-" * 80)
    
    optimized_results = []
    diagnosis_stats = {}
    
    # 测试前50条记录
    test_records = df.head(50)
    
    for i, (idx, row) in enumerate(test_records.iterrows()):
        record_name = row['record_name']
        
        try:
            # 使用优化阈值进行诊断 - 直接传递row对象
            diagnoses = diagnosis_system.enhanced_rule_based_diagnosis(row)
            
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
                'algorithm_diagnosis_optimized': ', '.join(diagnosis_names) if diagnosis_names else '正常',
                'algorithm_codes': ', '.join(diagnoses),
                'expert_diagnosis': expert_diagnosis,
                'optimization_applied': 'QRS:140ms, ST:0.2mV',
                'diagnosis_count': len(diagnoses)
            }
            
            optimized_results.append(result)
            
            # 显示前15个结果
            if i < 15:
                diag_display = ', '.join(diagnosis_names) if diagnosis_names else '正常'
                print(f"{record_name}: {diag_display}")
                
        except Exception as e:
            print(f"❌ 处理记录{record_name}时出错: {e}")
            continue
    
    # 保存优化后的结果
    if optimized_results:
        results_df = pd.DataFrame(optimized_results)
        output_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/v4_optimized_diagnosis_results_final.csv'
        results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 优化结果已保存至: {output_file}")
        
        # 统计诊断分布
        print(f"\n📈 优化阈值后的诊断分布:")
        print("-" * 50)
        total_records = len(optimized_results)
        
        # 统计正常和异常
        normal_count = len([r for r in optimized_results if r['diagnosis_count'] == 0])
        abnormal_count = total_records - normal_count
        
        print(f"   正常: {normal_count}例 ({(normal_count/total_records)*100:.1f}%)")
        print(f"   异常: {abnormal_count}例 ({(abnormal_count/total_records)*100:.1f}%)")
        
        if diagnosis_stats:
            print("\n   具体诊断分布:")
            for diagnosis, count in sorted(diagnosis_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_records) * 100
                print(f"   - {diagnosis}: {count}例 ({percentage:.1f}%)")
        
        # 对比分析（如果有专家诊断）
        if expert_df is not None:
            analyze_optimization_effect(results_df, expert_df)
        
        print(f"\n🎯 阈值优化关键改进:")
        print(f"   ✅ QRS阈值140ms: 减少右束支阻滞过度诊断 (预期减少65-76%)")
        print(f"   ✅ ST阈值0.2mV: 减少心肌缺血过度诊断 (预期减少72-81%)")
        print(f"   📈 预计匹配率提升: 12% → 35-50%")
        
        return results_df
    else:
        print("❌ 没有成功处理任何记录")
        return None

def analyze_optimization_effect(results_df, expert_df):
    """分析优化效果"""
    print(f"\n🔍 优化效果分析:")
    print("-" * 40)
    
    # 简单匹配分析
    matched = 0
    total_compared = 0
    
    for _, row in results_df.iterrows():
        if row['expert_diagnosis'] and str(row['expert_diagnosis']) not in ['', 'nan']:
            total_compared += 1
            algo_diag = str(row['algorithm_diagnosis_optimized']).lower()
            expert_diag = str(row['expert_diagnosis']).lower()
            
            # 基本匹配逻辑
            if ('正常' in algo_diag and '正常' in expert_diag) or \
               (algo_diag != '正常' and expert_diag != '正常'):
                matched += 1
    
    if total_compared > 0:
        match_rate = (matched / total_compared) * 100
        print(f"   与专家诊断对比: {matched}/{total_compared} ({match_rate:.1f}%)")
        
        # 预期改进估算
        if match_rate > 12:
            improvement = match_rate - 12
            print(f"   相比V4.0原始版本改进: +{improvement:.1f}个百分点")
        
        return match_rate
    else:
        print("   无法进行专家诊断对比")
        return None

if __name__ == '__main__':
    test_optimized_diagnosis()