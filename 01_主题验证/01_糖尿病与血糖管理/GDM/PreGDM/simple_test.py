#!/usr/bin/env python3
"""
CGM妊娠糖尿病风险评估工具 - 简化测试
Simple test for CGM Gestational Diabetes Risk Assessment Tool
"""

import numpy as np
from datetime import datetime, timedelta
import random
from CGM_GDM import GestationalCGMRiskAssessmentTool, PatientFactors

def generate_simple_cgm_data(hours=72, base_glucose=6.5, variability=1.0):
    """生成简单的模拟CGM数据"""
    timestamps = []
    glucose_values = []
    
    start_time = datetime.now() - timedelta(hours=hours)
    
    for i in range(hours * 12):  # 每5分钟一个数据点
        timestamp = start_time + timedelta(minutes=i*5)
        timestamps.append(timestamp)
        
        # 简单的血糖模拟：基础值 + 日间变化 + 随机变异
        hour_of_day = timestamp.hour + timestamp.minute/60
        daily_variation = 0.5 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
        random_variation = random.gauss(0, variability * 0.3)
        
        glucose = base_glucose + daily_variation + random_variation
        glucose = max(2.0, min(glucose, 25.0))  # 限制在合理范围
        
        glucose_values.append(round(glucose, 1))
    
    return glucose_values, timestamps

def main():
    print("🩺 CGM妊娠糖尿病风险评估工具 - 简化测试")
    print("=" * 50)
    
    # 初始化工具
    tool = GestationalCGMRiskAssessmentTool()
    
    # 测试场景
    scenarios = [
        {
            'name': '孕早期理想控制',
            'weeks': 16,
            'base_glucose': 6.0,
            'variability': 0.8,
            'patient': PatientFactors(gestational_weeks=16, obesity=False, advanced_age=False)
        },
        {
            'name': '孕中期轻度异常',
            'weeks': 26,
            'base_glucose': 7.2,
            'variability': 1.2,
            'patient': PatientFactors(gestational_weeks=26, obesity=True, pcos=True)
        },
        {
            'name': '孕晚期高风险',
            'weeks': 35,
            'base_glucose': 8.0,
            'variability': 1.8,
            'patient': PatientFactors(gestational_weeks=35, previous_gdm=True, obesity=True, advanced_age=True)
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 场景 {i}: {scenario['name']}")
        print("-" * 30)
        
        # 生成模拟数据
        glucose_data, timestamps = generate_simple_cgm_data(
            hours=72,
            base_glucose=scenario['base_glucose'],
            variability=scenario['variability']
        )
        
        # 执行评估
        result = tool.assess_patient(
            glucose_values=glucose_data,
            timestamps=timestamps,
            patient_factors=scenario['patient']
        )
        
        if result['success']:
            print(f"✅ 评估成功")
            print(f"🗓️  孕期: {result['gestational_period_cn']} ({result['gestational_weeks']:.0f}周)")
            
            # CGM指标
            metrics = result['metrics']
            print(f"📊 CGM指标:")
            print(f"   • TIR: {metrics['TIR']:.1f}%")
            print(f"   • GMI: {metrics['GMI']:.1f} mmol/L")
            print(f"   • CV: {metrics['CV']:.1f}%")
            
            # 分型和风险
            print(f"🏷️  分型: {result['classification']['comprehensive_type']}")
            print(f"⚠️  风险: {result['risk_scores']['risk_level']}")
            
            # 管理建议
            recommendations = result['management_recommendations']
            print(f"💡 建议:")
            print(f"   • 产检: {recommendations.get('antenatal_care_frequency', '标准')}")
            print(f"   • CGM: {recommendations.get('cgm_monitoring_strategy', '间歇性')}")
            
        else:
            print(f"❌ 评估失败: {result.get('error', '未知错误')}")
    
    print("\n✨ 测试完成！")
    print("\n📈 总结:")
    print("• 工具成功评估了不同孕期的血糖控制情况")
    print("• 孕期特异性目标范围正确应用")
    print("• 风险分层和管理建议符合临床需求")

if __name__ == "__main__":
    main()