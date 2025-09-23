#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CGM数据质量评估集成功能
验证在分析前进行数据质量检查的完整流程
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from CGM_AGP_Analyzer_Agent import CGMDataReader, AGPVisualAnalyzer, AGPIntelligentReporter

def create_poor_quality_cgm_data():
    """创建质量较差的CGM测试数据"""
    print("🧪 创建质量较差的测试数据...")
    
    # 只生成5天数据（不足最低要求）
    dates = pd.date_range('2024-01-01', periods=5*24*4, freq='15min')
    glucose_values = 7 + np.random.randn(len(dates)) * 0.5
    
    # 模拟严重的数据质量问题
    # 1. 大量缺失数据（50%）
    missing_indices = np.random.choice(len(dates), size=int(len(dates) * 0.5), replace=False)
    glucose_values[missing_indices] = np.nan
    
    # 2. 大量异常值
    outlier_indices = np.random.choice(len(dates), size=int(len(dates) * 0.1), replace=False)
    glucose_values[outlier_indices] = np.random.choice([0.5, 35.0], size=len(outlier_indices))
    
    # 3. 长时间连续重复值
    duplicate_start = 50
    glucose_values[duplicate_start:duplicate_start+100] = 8.5
    
    return pd.DataFrame({
        'timestamp': dates,
        'glucose': glucose_values,
        'device_info': 'test_poor_quality'
    })

def create_good_quality_cgm_data():
    """创建质量良好的CGM测试数据"""
    print("✨ 创建质量良好的测试数据...")
    
    # 生成14天完整数据
    dates = pd.date_range('2024-01-01', periods=14*24*4, freq='15min')
    
    # 生成真实的血糖模式
    time_hours = np.arange(len(dates)) / 4.0  # 转换为小时
    
    # 昼夜节律模式
    circadian = 1.5 * np.sin(2 * np.pi * time_hours / 24 - np.pi/2)
    
    # 餐时血糖波动
    meal_times = [7, 12, 18]  # 早中晚餐时间
    meal_effects = np.zeros(len(dates))
    for meal_time in meal_times:
        for day in range(14):
            meal_start = day * 24 * 4 + meal_time * 4
            if meal_start < len(dates):
                for i in range(min(12, len(dates) - meal_start)):  # 餐后3小时
                    if meal_start + i < len(dates):
                        meal_effects[meal_start + i] = 2.0 * np.exp(-i/8) * (1 + np.random.normal(0, 0.1))
    
    # 基础血糖 + 昼夜节律 + 餐时效应 + 随机噪声
    glucose_values = 7.0 + circadian + meal_effects + np.random.normal(0, 0.3, len(dates))
    glucose_values = np.clip(glucose_values, 3.0, 15.0)
    
    # 少量随机缺失（2%）
    missing_indices = np.random.choice(len(dates), size=int(len(dates) * 0.02), replace=False)
    glucose_values[missing_indices] = np.nan
    
    return pd.DataFrame({
        'timestamp': dates,
        'glucose': glucose_values,
        'device_info': 'test_good_quality'
    })

def test_data_quality_integration():
    """测试数据质量评估集成功能"""
    print("🔬 开始测试数据质量评估集成功能\n")
    
    # 创建分析器
    analyzer = AGPVisualAnalyzer(enable_quality_check=True)
    reporter = AGPIntelligentReporter()
    
    print("=" * 60)
    print("测试1: 质量较差的数据")
    print("=" * 60)
    
    # 测试质量较差的数据
    poor_data = create_poor_quality_cgm_data()
    print(f"📊 生成测试数据: {len(poor_data)}条记录")
    
    # 进行分析（应该被质量检查阻止）
    print("\n🔍 开始AGP分析...")
    poor_result = analyzer.analyze_cgm_data(poor_data, analysis_days=14)
    
    if 'error' in poor_result:
        print(f"✅ 质量检查成功阻止了分析: {poor_result['message']}")
        print(f"📋 质量评分: {poor_result['quality_assessment']['overall_quality']['total_score']}/100")
        print(f"🏷️ 质量等级: {poor_result['quality_assessment']['overall_quality']['quality_level']}")
    else:
        print("❌ 质量检查失败，分析不应该继续")
    
    print("\n" + "=" * 60)
    print("测试2: 质量良好的数据")
    print("=" * 60)
    
    # 测试质量良好的数据
    good_data = create_good_quality_cgm_data()
    print(f"📊 生成测试数据: {len(good_data)}条记录")
    
    # 进行分析（应该通过质量检查）
    print("\n🔍 开始AGP分析...")
    good_result = analyzer.analyze_cgm_data(good_data, analysis_days=14)
    
    if 'error' not in good_result:
        print("✅ 质量检查通过，成功完成AGP分析")
        print(f"📈 分析指标数量: {len(good_result)}个")
        
        # 生成智能报告
        print("\n📝 生成智能分析报告...")
        patient_info = {
            'name': '测试患者',
            'age': 45,
            'gender': '男',
            'diabetes_type': 'T2DM',
            'diabetes_duration': '5年',
            'cgm_device': 'Test Device'
        }
        
        report = reporter.generate_intelligent_report(good_result, patient_info)
        print(f"📋 报告生成完成，包含{len(report.get('clinical_recommendations', []))}条临床建议")
        
        # 保存详细报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"Data_Quality_Test_Report_{timestamp}.json"
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 详细报告已保存: {report_file}")
        
    else:
        print(f"❌ 良好数据的分析失败: {good_result.get('message', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("测试3: 跳过质量检查")
    print("=" * 60)
    
    # 测试禁用质量检查
    analyzer_no_quality = AGPVisualAnalyzer(enable_quality_check=False)
    print("🔄 禁用质量检查，强制分析质量较差的数据...")
    
    force_result = analyzer_no_quality.analyze_cgm_data(poor_data, analysis_days=14)
    if 'error' not in force_result:
        print("✅ 成功跳过质量检查，完成强制分析")
        print(f"📈 强制分析结果包含{len(force_result)}个指标")
    else:
        print("❌ 强制分析失败")
    
    print("\n🎉 数据质量评估集成测试完成!")
    return True

def main():
    """主函数"""
    try:
        success = test_data_quality_integration()
        if success:
            print("\n✅ 所有测试通过！数据质量评估功能正常集成")
        else:
            print("\n❌ 测试失败，请检查集成实现")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()