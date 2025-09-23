#!/usr/bin/env python3
"""
V4.0文件夹整理计划
保留优化V4.0和支持文件，删除其他版本
"""

import os
import shutil
from pathlib import Path

def analyze_files():
    """分析文件并分类"""
    
    # 需要保留的核心V4.0文件
    keep_v4_files = [
        'enhanced_ecg_analyzer_v4.py',           # 核心V4.0分析器(优化版)
        'integrated_ecg_diagnosis_system.py',    # 集成诊断系统(优化版)
        'enhanced_ecg_analysis_results.csv',     # V4.0分析结果数据
    ]
    
    # 需要保留的支持和参考文件
    keep_support_files = [
        'README.md',                              # 项目说明
        'SNOMED_Diagnosis_Codes_Reference.md',   # 诊断代码参考
        'ECG_Data_Fields_Dictionary.md',         # 数据字典
        'v4_threshold_optimization_validation_report.md',  # V4.0优化验证报告
    ]
    
    # 需要保留的测试和验证文件
    keep_test_files = [
        'test_optimized_diagnosis_final.py',     # V4.0优化测试脚本
        'simple_matching_analysis.py',           # 匹配度分析
        'v4_optimized_diagnosis_results_final.csv',  # 优化结果
        'threshold_optimization_detailed_comparison.csv',  # 优化对比数据
    ]
    
    # 需要保留的高级功能文件（未来扩展用）
    keep_future_files = [
        'hierarchical_diagnosis_system.py',      # 诊断层级系统
        'clinical_wisdom_integration.py',        # 临床智慧集成
        'v4_clinical_optimized_thresholds.py',   # 临床优化阈值
        'v4_2_clinical_intelligent_system.py',   # V4.2系统（未来版本）
    ]
    
    # 所有需要保留的文件
    keep_files = keep_v4_files + keep_support_files + keep_test_files + keep_future_files
    
    print("📋 文件整理分析")
    print("=" * 50)
    
    # 分析当前目录的所有文件
    current_files = []
    for item in os.listdir('.'):
        if os.path.isfile(item):
            current_files.append(item)
    
    print(f"当前文件总数: {len(current_files)}")
    print(f"计划保留文件: {len(keep_files)}")
    
    # 分类显示
    print(f"\n✅ 需要保留的文件 ({len(keep_files)}个):")
    print("-" * 40)
    
    print("🔧 核心V4.0文件:")
    for f in keep_v4_files:
        if f in current_files:
            print(f"   ✓ {f}")
        else:
            print(f"   ❌ {f} (缺失)")
    
    print("\n📚 支持参考文件:")  
    for f in keep_support_files:
        if f in current_files:
            print(f"   ✓ {f}")
        else:
            print(f"   ❌ {f} (缺失)")
    
    print("\n🧪 测试验证文件:")
    for f in keep_test_files:
        if f in current_files:
            print(f"   ✓ {f}")
        else:
            print(f"   ❌ {f} (缺失)")
            
    print("\n🚀 高级功能文件:")
    for f in keep_future_files:
        if f in current_files:
            print(f"   ✓ {f}")
        else:
            print(f"   ❌ {f} (缺失)")
    
    # 需要删除的文件
    delete_files = [f for f in current_files if f not in keep_files and not f.startswith('.')]
    
    print(f"\n❌ 需要删除的文件 ({len(delete_files)}个):")
    print("-" * 40)
    for f in sorted(delete_files)[:20]:  # 只显示前20个
        print(f"   🗑️  {f}")
    if len(delete_files) > 20:
        print(f"   ... 还有 {len(delete_files) - 20} 个文件")
    
    return keep_files, delete_files

if __name__ == '__main__':
    keep_files, delete_files = analyze_files()
    
    print(f"\n📊 整理摘要:")
    print(f"   保留: {len(keep_files)} 个文件")
    print(f"   删除: {len(delete_files)} 个文件")
    print(f"   空间释放: 预计50-70%")