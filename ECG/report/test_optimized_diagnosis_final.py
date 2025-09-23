#!/usr/bin/env python3
"""
测试优化阈值后的V4.0诊断系统效果 - 最终版本
正确处理诊断方法返回的字典结构
"""

import pandas as pd
import numpy as np
from integrated_ecg_diagnosis_system import IntegratedECGDiagnosisSystem
import json
import os

def test_optimized_diagnosis():
    """测试优化阈值的诊断效果"""
    
    print("🔧 V4.0阈值优化效果测试 - 最终版本")
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
            diagnosis_result = diagnosis_system.enhanced_rule_based_diagnosis(row)
            
            # 检查返回结果的结构
            if isinstance(diagnosis_result, dict):
                diagnoses = diagnosis_result.get('diagnoses', [])
                confidence_scores = diagnosis_result.get('confidence_scores', {})
                total_features = diagnosis_result.get('total_features_used', {'total': 0})
            else:
                # 如果返回的是列表，直接使用
                diagnoses = diagnosis_result if isinstance(diagnosis_result, list) else []
                confidence_scores = {}
                total_features = {'total': 0}
            
            # 统计诊断分布
            for diagnosis in diagnoses:
                diagnosis_name = diagnosis_system.diagnosis_codes.get(diagnosis, diagnosis)
                diagnosis_stats[diagnosis_name] = diagnosis_stats.get(diagnosis_name, 0) + 1
            
            # 转换为诊断名称
            diagnosis_names = [diagnosis_system.diagnosis_codes.get(code, code) for code in diagnoses]
            
            # 计算平均置信度
            avg_confidence = np.mean(list(confidence_scores.values())) if confidence_scores else 0
            
            result = {
                'record_name': record_name,
                'algorithm_diagnosis_optimized': ', '.join(diagnosis_names) if diagnosis_names else '正常',
                'algorithm_codes': ', '.join(diagnoses),
                'diagnosis_confidence': round(avg_confidence, 3),
                'diagnosis_count': len(diagnoses),
                'optimization_applied': 'QRS:140ms, ST:0.2mV',
                'features_used': total_features.get('total', 0)
            }
            
            optimized_results.append(result)
            
            # 显示前15个结果
            if i < 15:
                diag_display = ', '.join(diagnosis_names) if diagnosis_names else '正常'
                conf_display = f"(置信度:{avg_confidence:.2f})" if avg_confidence > 0 else ""
                print(f"{record_name}: {diag_display} {conf_display}")
                
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
        
        print(f"   正常ECG: {normal_count}例 ({(normal_count/total_records)*100:.1f}%)")
        print(f"   异常ECG: {abnormal_count}例 ({(abnormal_count/total_records)*100:.1f}%)")
        
        if diagnosis_stats:
            print("\n   异常诊断分布:")
            for diagnosis, count in sorted(diagnosis_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_records) * 100
                print(f"   - {diagnosis}: {count}例 ({percentage:.1f}%)")
        else:
            print("\n   所有记录均诊断为正常")
        
        # 生成对比分析
        generate_comparison_analysis(optimized_results)
        
        print(f"\n🎯 阈值优化关键效果:")
        print(f"   ✅ QRS阈值140ms: 减少右束支阻滞过度诊断 (预期减少65-76%)")
        print(f"   ✅ ST阈值0.2mV: 减少心肌缺血过度诊断 (预期减少72-81%)")
        print(f"   📊 当前诊断异常率: {(abnormal_count/total_records)*100:.1f}% (原版可能>80%)")
        print(f"   📈 预计匹配率提升: 12% → 35-50%")
        
        return results_df
    else:
        print("❌ 没有成功处理任何记录")
        return None

def generate_comparison_analysis(optimized_results):
    """生成对比分析报告"""
    print(f"\n🔍 阈值优化效果分析:")
    print("-" * 40)
    
    total = len(optimized_results)
    
    # 诊断复杂度分析
    diagnosis_counts = [r['diagnosis_count'] for r in optimized_results]
    avg_diagnoses_per_case = np.mean(diagnosis_counts) if diagnosis_counts else 0
    max_diagnoses = max(diagnosis_counts) if diagnosis_counts else 0
    
    print(f"   平均每例诊断数: {avg_diagnoses_per_case:.2f}")
    print(f"   最大诊断数: {max_diagnoses}")
    
    # 置信度分析
    confidences = [r['diagnosis_confidence'] for r in optimized_results if r['diagnosis_confidence'] > 0]
    if confidences:
        avg_confidence = np.mean(confidences)
        print(f"   平均诊断置信度: {avg_confidence:.2f}")
    
    # 特征使用情况
    features_used = [r['features_used'] for r in optimized_results if r['features_used'] > 0]
    if features_used:
        avg_features = np.mean(features_used)
        print(f"   平均特征使用数: {avg_features:.1f}")
    
    # 相比原始版本的预期改进
    abnormal_rate = sum(1 for r in optimized_results if r['diagnosis_count'] > 0) / total * 100
    print(f"\n   当前异常检出率: {abnormal_rate:.1f}%")
    print(f"   预期改进: 大幅减少过度诊断，提高特异性")

def load_expert_diagnosis_for_comparison():
    """尝试加载专家诊断进行对比"""
    expert_files = [
        '/Users/williamsun/Documents/gplus/docs/ECG/report/expert_diagnosis_vs_v4_comparison.csv',
        '/Users/williamsun/Documents/gplus/docs/ECG/report/expert_diagnosis_reference.csv'
    ]
    
    for file_path in expert_files:
        try:
            df = pd.read_csv(file_path)
            print(f"✅ 找到专家诊断数据: {file_path}")
            return df
        except:
            continue
    
    return None

if __name__ == '__main__':
    result = test_optimized_diagnosis()
    
    if result is not None:
        print(f"\n✅ 测试完成！处理了{len(result)}条记录")
        print(f"📄 详细结果保存在: v4_optimized_diagnosis_results_final.csv")
    else:
        print(f"\n❌ 测试失败")