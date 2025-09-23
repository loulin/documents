#!/usr/bin/env python3
"""
CGM妊娠糖尿病风险评估工具 - 模拟数据测试脚本
Test script for CGM Gestational Diabetes Risk Assessment Tool with simulated data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from CGM_GDM import GestationalCGMRiskAssessmentTool, PatientFactors

def generate_cgm_data(hours=72, base_glucose=6.5, variability=1.5, trend=0, noise_level=0.3):
    """
    生成模拟CGM数据
    
    Parameters:
    - hours: 监测小时数
    - base_glucose: 基础血糖水平 (mmol/L)
    - variability: 血糖变异性
    - trend: 血糖趋势 (正值表示升高趋势)
    - noise_level: 噪声水平
    """
    timestamps = []
    glucose_values = []
    
    start_time = datetime.now() - timedelta(hours=hours)
    
    for i in range(hours * 12):  # 每5分钟一个数据点
        timestamp = start_time + timedelta(minutes=i*5)
        timestamps.append(timestamp)
        
        # 基础血糖 + 日间变化 + 餐后波动 + 趋势 + 噪声
        hour_of_day = timestamp.hour + timestamp.minute/60
        
        # 日间节律 (早晨较高，夜间较低)
        circadian = 0.5 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
        
        # 餐后波动 (假设7点、12点、18点进餐)
        meal_effect = 0
        for meal_time in [7, 12, 18]:
            time_since_meal = abs(hour_of_day - meal_time)
            if time_since_meal < 3:  # 餐后3小时内
                meal_effect += (3 - time_since_meal) * variability * 0.8
        
        # 长期趋势
        trend_effect = trend * i / (hours * 12)
        
        # 随机噪声
        noise = random.gauss(0, noise_level)
        
        glucose = base_glucose + circadian + meal_effect + trend_effect + noise
        glucose = max(2.0, min(glucose, 25.0))  # 限制在合理范围内
        
        glucose_values.append(round(glucose, 1))
    
    return glucose_values, timestamps

def create_test_scenarios():
    """创建不同的测试场景"""
    
    scenarios = []
    
    # 场景1: 孕早期，理想控制
    print("=== 场景1: 孕早期理想控制 ===")
    glucose_data1, timestamps1 = generate_cgm_data(
        hours=72, 
        base_glucose=6.0, 
        variability=0.8, 
        trend=0, 
        noise_level=0.2
    )
    patient1 = PatientFactors(
        gestational_weeks=16,
        previous_gdm=False,
        obesity=False,
        advanced_age=False
    )
    scenarios.append({
        'name': '孕早期理想控制',
        'glucose_data': glucose_data1,
        'timestamps': timestamps1,
        'patient_factors': patient1
    })
    
    # 场景2: 孕中期，轻度控制不佳
    print("=== 场景2: 孕中期轻度控制不佳 ===")
    glucose_data2, timestamps2 = generate_cgm_data(
        hours=72,
        base_glucose=7.2,
        variability=1.5,
        trend=0.1,
        noise_level=0.4
    )
    patient2 = PatientFactors(
        gestational_weeks=26,
        previous_gdm=False,
        obesity=True,
        advanced_age=False,
        pcos=True
    )
    scenarios.append({
        'name': '孕中期轻度控制不佳',
        'glucose_data': glucose_data2,
        'timestamps': timestamps2,
        'patient_factors': patient2
    })
    
    # 场景3: 孕晚期，高风险多重因素
    print("=== 场景3: 孕晚期高风险 ===")
    glucose_data3, timestamps3 = generate_cgm_data(
        hours=72,
        base_glucose=8.5,
        variability=2.5,
        trend=0.2,
        noise_level=0.6
    )
    patient3 = PatientFactors(
        gestational_weeks=35,
        previous_gdm=True,
        obesity=True,
        advanced_age=True,
        family_history=True,
        hypertension=True
    )
    scenarios.append({
        'name': '孕晚期高风险',
        'glucose_data': glucose_data3,
        'timestamps': timestamps3,
        'patient_factors': patient3
    })
    
    # 场景4: 孕中期，血糖变异性极高
    print("=== 场景4: 孕中期血糖变异性极高 ===")
    glucose_data4, timestamps4 = generate_cgm_data(
        hours=72,
        base_glucose=7.0,
        variability=3.0,
        trend=0,
        noise_level=0.8
    )
    patient4 = PatientFactors(
        gestational_weeks=28,
        previous_gdm=True,
        obesity=False,
        advanced_age=True,
        pcos=True
    )
    scenarios.append({
        'name': '孕中期血糖变异性极高',
        'glucose_data': glucose_data4,
        'timestamps': timestamps4,
        'patient_factors': patient4
    })
    
    return scenarios

def run_comprehensive_test():
    """运行综合测试"""
    
    print("🩺 CGM妊娠糖尿病风险评估工具 - 模拟数据测试")
    print("=" * 60)
    
    # 初始化工具
    tool = GestationalCGMRiskAssessmentTool()
    
    # 创建测试场景
    scenarios = create_test_scenarios()
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🔍 正在评估场景 {i}: {scenario['name']}")
        print("-" * 40)
        
        try:
            # 执行评估
            result = tool.assess_patient(
                glucose_values=scenario['glucose_data'],
                timestamps=scenario['timestamps'],
                patient_factors=scenario['patient_factors']
            )
            
            if result['success']:
                # 显示关键结果
                print(f"✅ 评估成功")
                print(f"📅 孕期阶段: {result['gestational_period_cn']} ({result['gestational_weeks']}周)")
                print(f"🎯 目标血糖范围: {result['target_glucose_range'][0]}-{result['target_glucose_range'][1]} mmol/L")
                
                # CGM指标
                metrics = result['metrics']
                print(f"📊 CGM指标:")
                print(f"   • TIR: {metrics['TIR']:.1f}%")
                print(f"   • GMI: {metrics['GMI']:.1f} mmol/L")
                print(f"   • CV: {metrics['CV']:.1f}%")
                print(f"   • MAGE: {metrics['MAGE']:.1f} mmol/L")
                
                # 分型结果
                classification = result['classification']
                print(f"🏷️  血糖分型:")
                print(f"   • 综合分型: {classification['comprehensive_type']}")
                
                # 风险评分
                risk_scores = result['risk_scores']
                print(f"⚠️  风险评估:")
                print(f"   • 风险等级: {risk_scores['risk_level']}")
                print(f"   • 综合评分: {risk_scores['composite_score']:.2f}")
                print(f"   • 主要风险: {risk_scores['primary_risk_score']:.2f}")
                
                # 不良事件预测
                predictions = result['adverse_outcome_predictions']
                print(f"🔮 不良事件预测:")
                for event, prob in predictions.items():
                    if isinstance(prob, (int, float)):
                        print(f"   • {event}: {prob:.1f}%")
                
                # 管理建议
                recommendations = result['management_recommendations']
                print(f"💡 管理建议:")
                print(f"   • 产检频率: {recommendations.get('antenatal_care_frequency', 'N/A')}")
                print(f"   • CGM策略: {recommendations.get('cgm_monitoring_strategy', 'N/A')}")
                print(f"   • 专科会诊: {recommendations.get('specialist_consultation', 'N/A')}")
                
                results.append(result)
                
            else:
                print(f"❌ 评估失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 程序错误: {str(e)}")
    
    # 结果汇总
    print("\n📋 测试结果汇总")
    print("=" * 60)
    
    if results:
        print(f"总共评估: {len(results)} 个场景")
        
        # 风险等级分布
        risk_levels = [r['risk_scores']['risk_level'] for r in results]
        level_counts = {}
        for level in risk_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print("风险等级分布:")
        for level, count in level_counts.items():
            print(f"  • {level}: {count} 例")
        
        # 分型分布
        types = [r['classification']['comprehensive_type'] for r in results]
        type_counts = {}
        for type_name in types:
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        print("分型分布:")
        for type_name, count in type_counts.items():
            print(f"  • {type_name}: {count} 例")
    
    print("\n✨ 测试完成！")
    return results

def batch_test_demo():
    """批量评估演示"""
    
    print("\n🔄 批量评估演示")
    print("=" * 40)
    
    tool = GestationalCGMRiskAssessmentTool()
    scenarios = create_test_scenarios()
    
    # 准备批量数据
    batch_data = []
    for i, scenario in enumerate(scenarios):
        batch_data.append({
            'patient_id': f'TEST_{i+1:03d}',
            'glucose_values': scenario['glucose_data'],
            'timestamps': scenario['timestamps'],
            'patient_factors': scenario['patient_factors']
        })
    
    # 执行批量评估
    batch_results = tool.batch_assess(batch_data)
    
    print(f"批量评估完成，共处理 {len(batch_results)} 个患者")
    
    # 显示简要结果
    for result in batch_results:
        if result['success']:
            patient_id = result.get('patient_id', 'Unknown')
            risk_level = result['risk_scores']['risk_level']
            comp_type = result['classification']['comprehensive_type']
            print(f"  • {patient_id}: {risk_level} - {comp_type}")
        else:
            print(f"  • {result.get('patient_id', 'Unknown')}: 评估失败")
    
    return batch_results

def export_demo(results):
    """导出功能演示"""
    
    if not results:
        print("没有结果可导出")
        return
    
    print("\n💾 导出功能演示")
    print("=" * 40)
    
    tool = GestationalCGMRiskAssessmentTool()
    
    # 导出第一个结果
    result = results[0]
    
    try:
        # 导出JSON
        json_file = tool.export_results(result, 'json', 'test_assessment')
        print(f"✅ JSON导出成功: {json_file}")
        
        # 导出文本报告
        txt_file = tool.export_results(result, 'txt', 'test_report')
        print(f"✅ 文本报告导出成功: {txt_file}")
        
    except Exception as e:
        print(f"❌ 导出失败: {str(e)}")

if __name__ == "__main__":
    print("开始CGM妊娠糖尿病风险评估工具测试...")
    
    # 运行综合测试
    test_results = run_comprehensive_test()
    
    # 批量评估演示
    batch_results = batch_test_demo()
    
    # 导出演示
    export_demo(test_results)
    
    print("\n🎉 所有测试完成！")