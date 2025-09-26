#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGPAI增强版智能标注系统 - 快速演示脚本
快速测试和演示智能标注功能
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_demo_cgm_data(days=14) -> pd.DataFrame:
    """
    创建演示用的CGM数据
    生成包含各种血糖模式的真实数据，用于测试标注功能
    """
    print("🔬 正在生成演示CGM数据...")
    
    # 设置随机种子确保可重复性
    np.random.seed(42)
    
    # 生成时间序列（每15分钟一个点）
    start_time = datetime.now() - timedelta(days=days)
    time_points = []
    glucose_values = []
    
    for day in range(days):
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                timestamp = start_time + timedelta(days=day, hours=hour, minutes=minute)
                time_points.append(timestamp)
                
                # 生成带有临床模式的血糖值
                glucose = generate_realistic_glucose(hour, minute, day)
                glucose_values.append(glucose)
    
    # 创建DataFrame
    cgm_data = pd.DataFrame({
        'timestamp': time_points,
        'glucose': glucose_values,
        'device_info': 'demo_enhanced'
    })
    
    print(f"✅ 生成{len(cgm_data)}个数据点，包含以下临床模式：")
    print("   📈 黎明现象 (4-8点血糖上升)")
    print("   🍽️ 餐后血糖峰值 (三餐后)")
    print("   ⚠️ 低血糖事件 (随机发生)")
    print("   📊 高血糖事件 (偶发)")
    print("   🌙 夜间血糖变异")
    print("   🔄 血糖变异性模式")
    
    return cgm_data

def generate_realistic_glucose(hour, minute, day):
    """生成真实的血糖值，包含各种临床模式"""
    
    # 基础血糖水平
    base_glucose = 7.0
    
    # 时间相关的小时值
    time_hour = hour + minute / 60.0
    
    # 1. 昼夜节律和黎明现象
    circadian = 1.0 * np.sin(2 * np.pi * (time_hour - 6) / 24)
    
    # 增强黎明现象 (4-8点)
    if 4 <= time_hour <= 8:
        dawn_effect = 2.5 * np.exp(-(time_hour - 6)**2 / 4) * (1 + 0.3 * np.sin(2 * np.pi * day / 7))
    else:
        dawn_effect = 0
    
    # 2. 餐后血糖峰值
    postprandial = 0
    
    # 早餐后峰值 (7-10点)
    if 7 <= time_hour <= 10:
        breakfast_peak = 4.5 * np.exp(-(time_hour - 8)**2 / 1.5)
        # 添加个体差异
        breakfast_peak *= (1 + 0.2 * np.sin(2 * np.pi * day / 3))
        postprandial += breakfast_peak
    
    # 午餐后峰值 (12-15点)
    if 12 <= time_hour <= 15:
        lunch_peak = 3.5 * np.exp(-(time_hour - 13)**2 / 1.0)
        postprandial += lunch_peak
    
    # 晚餐后峰值 (18-21点)
    if 18 <= time_hour <= 21:
        dinner_peak = 4.0 * np.exp(-(time_hour - 19)**2 / 1.2)
        postprandial += dinner_peak
    
    # 3. 胰岛素作用效果
    insulin_effect = 0
    
    # 餐时胰岛素作用
    if 8 <= time_hour <= 12:  # 早餐胰岛素
        insulin_effect += -1.8 * np.exp(-(time_hour - 10)**2 / 3)
    if 13 <= time_hour <= 17:  # 午餐胰岛素
        insulin_effect += -1.5 * np.exp(-(time_hour - 15)**2 / 3)
    if 19 <= time_hour <= 23:  # 晚餐胰岛素
        insulin_effect += -1.7 * np.exp(-(time_hour - 21)**2 / 3)
    
    # 基础胰岛素作用
    if time_hour <= 6 or time_hour >= 22:
        insulin_effect += -0.5
    
    # 4. 运动效应（随机发生）
    exercise_effect = 0
    if np.random.random() < 0.08:  # 8%概率运动
        exercise_effect = -2.0 * np.random.exponential(0.5)
    
    # 5. 应激反应（偶发）
    stress_effect = 0
    if np.random.random() < 0.03:  # 3%概率应激
        stress_effect = 3.0 * np.random.exponential(0.8)
    
    # 6. 低血糖事件（模拟过量胰岛素）
    hypoglycemia_risk = 0
    if np.random.random() < 0.015:  # 1.5%概率低血糖
        hypoglycemia_risk = -3.0 * np.random.exponential(0.7)
    
    # 7. 高血糖事件（模拟遗漏用药或高碳水）
    hyperglycemia_risk = 0
    if np.random.random() < 0.02:  # 2%概率高血糖
        hyperglycemia_risk = 6.0 * np.random.exponential(0.6)
    
    # 8. 夜间变异（模拟睡眠质量影响）
    nocturnal_variation = 0
    if 0 <= time_hour <= 6:
        if day % 3 == 0:  # 每3天有一次不良睡眠
            nocturnal_variation = 1.5 * np.random.normal(0, 0.8)
    
    # 9. 周末效应
    weekend_effect = 0
    if day % 7 >= 5:  # 周末
        weekend_effect = 0.8 * np.random.normal(0, 1.2)
        # 周末餐时可能不规律
        if 11 <= time_hour <= 14:  # 可能晚起+早午餐合并
            postprandial *= 1.4
    
    # 10. 传感器噪声
    sensor_noise = np.random.normal(0, 0.6)
    
    # 11. 设备特定的偏差
    device_bias = 0.1 * np.sin(2 * np.pi * time_hour / 24)
    
    # 综合血糖值计算
    glucose = (base_glucose + circadian + dawn_effect + postprandial + 
              insulin_effect + exercise_effect + stress_effect + 
              hypoglycemia_risk + hyperglycemia_risk + nocturnal_variation +
              weekend_effect + sensor_noise + device_bias)
    
    # 限制在生理范围内
    glucose = np.clip(glucose, 2.0, 25.0)
    
    return glucose

def run_quick_demo():
    """运行快速演示"""
    
    print("🚀 AGPAI增强版智能标注系统 - 快速演示")
    print("="*60)
    
    try:
        # 1. 生成演示数据
        cgm_data = create_demo_cgm_data(days=14)
        
        # 保存演示数据
        demo_file = "demo_cgm_data.csv"
        cgm_data.to_csv(demo_file, index=False)
        print(f"💾 演示数据已保存: {demo_file}")
        
        # 2. 导入增强版AGPAI系统
        print("\n📦 正在导入AGPAI增强版系统...")
        try:
            from AGP_Intelligent_Annotation_System import EnhancedAGPAISystem
            print("✅ 成功导入AGPAI增强版系统")
        except ImportError as e:
            print(f"❌ 导入失败: {e}")
            print("请确保CGM_AGP_Analyzer_Agent.py文件在同一目录下")
            return
        
        # 3. 创建系统实例
        print("\n🔧 正在初始化增强版AGPAI系统...")
        enhanced_agpai = EnhancedAGPAISystem()
        
        # 4. 设置患者信息
        patient_info = {
            'name': '演示患者',
            'age': 45,
            'gender': '男',
            'diabetes_type': 'T2DM',
            'diabetes_duration': '8年',
            'cgm_device': 'Demo Enhanced CGM'
        }
        
        # 5. 执行完整分析
        print("\n🔍 正在执行增强版智能标注分析...")
        print("   • 57种视觉指标分析")
        print("   • AGP智能标注生成")
        print("   • 每日曲线标注生成")
        print("   • 临床解读报告生成")
        
        results = enhanced_agpai.comprehensive_analysis_with_annotations(
            cgm_file_path=demo_file,
            patient_info=patient_info,
            output_dir="./demo_output"
        )
        
        # 6. 显示结果
        print(f"\n🎯 演示完成！生成的文件:")
        print(f"   📊 AGP智能标注图表: {results['agp_chart_path']}")
        print(f"   📈 每日曲线标注图表: {results['daily_chart_path']}")
        print(f"   📄 完整分析报告: {results['report_path']}")
        
        # 7. 显示关键发现
        findings = results['intelligent_report']['key_findings']
        if findings:
            print(f"\n🔍 检测到的临床模式 ({len(findings)}项):")
            for i, finding in enumerate(findings, 1):
                severity_icon = {'severe': '🔴', 'moderate': '🟡', 'mild': '🟢'}.get(finding.get('severity'), '📋')
                print(f"   {i}. {severity_icon} {finding['description']}")
        
        # 8. 显示推荐建议
        recommendations = results['intelligent_report']['clinical_recommendations']
        if recommendations:
            print(f"\n💡 临床建议 ({len(recommendations)}项):")
            for i, rec in enumerate(recommendations, 1):
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '📋')
                print(f"   {i}. {priority_icon} {rec['recommendation']}")
        
        print(f"\n✨ 演示数据特点:")
        tir = results['analysis_results'].get('target_range_coverage', 0)
        cv = results['analysis_results'].get('glucose_coefficient_of_variation', 0)
        dawn_slope = results['analysis_results'].get('dawn_curve_slope', 0)
        print(f"   • TIR (目标范围): {tir:.1f}%")
        print(f"   • 血糖变异系数: {cv:.1f}%")
        print(f"   • 黎明现象斜率: {dawn_slope:.2f} mmol/L/h")
        
        # 9. 使用提示
        print(f"\n📖 使用提示:")
        print(f"   1. 查看生成的PNG图表文件，观察智能标注效果")
        print(f"   2. 打开JSON报告文件，查看详细分析数据")
        print(f"   3. 参考AGPAI_Enhanced_Usage_Guide.md了解更多功能")
        print(f"   4. 查看Clinical_Annotation_Standards.md了解标注规则")
        
        # 10. 可选：显示图表
        show_charts = input(f"\n🖼️  是否显示生成的图表？(y/n): ").lower().strip()
        if show_charts == 'y':
            print("正在显示图表...")
            plt.show()
        
        print(f"\n🎉 AGPAI增强版智能标注演示完成！")
        
        return results
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 创建输出目录
    os.makedirs("demo_output", exist_ok=True)
    
    # 运行演示
    demo_results = run_quick_demo()
    
    if demo_results:
        print(f"\n🔗 相关文件:")
        print(f"   📚 使用指南: AGPAI_Enhanced_Usage_Guide.md")
        print(f"   📋 标注标准: Clinical_Annotation_Standards.md")
        print(f"   🔧 源代码: AGP_Intelligent_Annotation_System.py")