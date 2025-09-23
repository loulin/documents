#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版CGM AGP分析智能体演示
展示全部57种视觉指标和高级分析功能
"""

import pandas as pd
import numpy as np
from scipy import signal, stats
from scipy.fft import fft, fftfreq
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import json
import logging

# 导入完整版分析器
from CGM_AGP_Analyzer_Agent import CGMDataReader, AGPVisualAnalyzer, AGPIntelligentReporter

def create_realistic_cgm_data(days=14, noise_level=0.8) -> pd.DataFrame:
    """
    创建更真实的CGM演示数据，包含各种血糖模式
    """
    np.random.seed(42)  # 确保可重复性
    
    dates = pd.date_range('2024-01-01', periods=days*24*4, freq='15min')
    glucose_values = []
    
    for i, timestamp in enumerate(dates):
        hour = timestamp.hour + timestamp.minute / 60.0
        day_of_week = timestamp.dayofweek
        
        # 基础血糖 (7.0 mmol/L)
        base_glucose = 7.0
        
        # 昼夜节律和黎明现象
        circadian = 1.2 * np.sin(2 * np.pi * (hour - 6) / 24)
        dawn_phenomenon = 1.8 if 4 <= hour <= 8 else 0
        
        # 餐后血糖峰值
        postprandial = 0
        if 7 <= hour <= 9:  # 早餐后
            meal_effect = 4.5 * np.exp(-(hour - 7.5)**2 / 0.8)
            postprandial += meal_effect
        elif 12 <= hour <= 14:  # 午餐后
            meal_effect = 3.8 * np.exp(-(hour - 12.5)**2 / 0.6)
            postprandial += meal_effect
        elif 18 <= hour <= 21:  # 晚餐后
            meal_effect = 4.2 * np.exp(-(hour - 18.8)**2 / 0.9)
            postprandial += meal_effect
        
        # 周末效应
        weekend_effect = 0
        if day_of_week >= 5:  # 周末
            weekend_effect = 0.8 * np.random.normal(0, 1)
            # 周末用餐时间不规律
            if np.random.random() < 0.3:
                postprandial *= np.random.uniform(0.7, 1.4)
        
        # 运动效应（模拟随机运动）
        exercise_effect = 0
        if np.random.random() < 0.15:  # 15%概率运动
            exercise_effect = -2.5 * np.random.exponential(0.5)
        
        # 应激效应（模拟生活压力）
        stress_effect = 0
        if np.random.random() < 0.05:  # 5%概率应激
            stress_effect = 2.0 * np.random.exponential(1.0)
        
        # 胰岛素作用模拟
        insulin_effect = 0
        # 模拟胰岛素的作用曲线
        if 7.5 <= hour <= 11:  # 早餐胰岛素作用期
            insulin_effect = -1.5 * np.exp(-(hour - 9)**2 / 2.0)
        elif 12.5 <= hour <= 16:  # 午餐胰岛素作用期
            insulin_effect = -1.2 * np.exp(-(hour - 14)**2 / 2.0)
        elif 19 <= hour <= 23:  # 晚餐胰岛素作用期
            insulin_effect = -1.4 * np.exp(-(hour - 21)**2 / 2.0)
        
        # 夜间基础胰岛素
        if hour <= 6 or hour >= 22:
            insulin_effect += -0.3
        
        # 血糖传感器噪声
        sensor_noise = np.random.normal(0, noise_level)
        
        # 综合血糖值
        glucose = (base_glucose + circadian + dawn_phenomenon + postprandial + 
                  weekend_effect + exercise_effect + stress_effect + 
                  insulin_effect + sensor_noise)
        
        # 限制在生理范围内
        glucose = np.clip(glucose, 2.5, 25.0)
        glucose_values.append(glucose)
    
    return pd.DataFrame({
        'timestamp': dates,
        'glucose': glucose_values,
        'device_info': 'realistic_demo'
    })

def analyze_and_display_results(cgm_data: pd.DataFrame, patient_info: Dict):
    """
    完整的AGP分析和结果展示
    """
    print("=== 完整版CGM AGP智能分析 ===\n")
    
    # 初始化分析器
    analyzer = AGPVisualAnalyzer()
    reporter = AGPIntelligentReporter()
    
    print("🔍 正在进行57种视觉指标分析...")
    analysis_results = analyzer.analyze_cgm_data(cgm_data, analysis_days=14)
    
    print("📊 正在生成智能医学报告...")
    intelligent_report = reporter.generate_intelligent_report(analysis_results, patient_info)
    
    # 显示整体评估
    overall = intelligent_report['overall_assessment']
    print(f"\n🎯 【整体评估】")
    print(f"   控制水平: {overall['level']} ({overall['overall_score']}分)")
    print(f"   评估说明: {overall['description']}")
    print(f"   数据质量: {overall['data_quality']}")
    
    # 显示关键发现
    findings = intelligent_report['key_findings']
    if findings:
        print(f"\n🔍 【关键发现】")
        for i, finding in enumerate(findings, 1):
            severity_icon = {'severe': '🔴', 'moderate': '🟡', 'mild': '🟢'}.get(finding.get('severity'), '📋')
            print(f"   {i}. {severity_icon} {finding['description']}")
            print(f"      临床意义: {finding['clinical_significance']}")
    
    # 显示风险警报
    alerts = intelligent_report['risk_alerts']
    if alerts:
        print(f"\n⚠️  【风险警报】")
        for alert in alerts:
            urgency_icon = {'high': '🚨', 'medium': '⚠️', 'low': '💡'}.get(alert['urgency'], '📋')
            print(f"   {urgency_icon} [{alert['urgency'].upper()}] {alert['message']}")
            print(f"      建议行动: {alert['action_required']}")
    
    # 显示临床建议
    recommendations = intelligent_report['clinical_recommendations']
    if recommendations:
        print(f"\n💡 【临床建议】")
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '📋')
            print(f"   {i}. {priority_icon} [{rec['category'].upper()}] {rec['recommendation']}")
            print(f"      依据: {rec['rationale']}")
            print(f"      随访: {rec['follow_up']}")
    
    # 显示详细分析
    detailed = intelligent_report['detailed_analysis']
    print(f"\n📈 【详细技术分析】")
    
    # 曲线形态分析
    morphology = detailed['curve_morphology']
    print(f"   曲线形态:")
    print(f"   ├─ 平滑度: {morphology['smoothness']:.3f}")
    print(f"   ├─ 对称性: {morphology['symmetry']:.3f}")  
    print(f"   ├─ 复杂度: {morphology['complexity']:.3f}")
    print(f"   └─ 解读: {morphology['interpretation']}")
    
    # 时间模式分析
    time_patterns = detailed['time_patterns']
    print(f"   时间模式:")
    print(f"   ├─ 黎明现象: {time_patterns['dawn_phenomenon']:.2f} mmol/L/h")
    print(f"   ├─ 早餐峰值: {time_patterns['postprandial_response']['morning']:.2f} mmol/L")
    print(f"   ├─ 餐后一致性: {time_patterns['postprandial_response']['consistency']:.3f}")
    print(f"   ├─ 夜间稳定性: {time_patterns['nocturnal_stability']:.3f}")
    print(f"   └─ 解读: {time_patterns['interpretation']}")
    
    # 变异性分析
    variability = detailed['variability_analysis']
    print(f"   变异性分析:")
    print(f"   ├─ 分位数变异: {variability['percentile_spread']:.1f}%")
    print(f"   ├─ 振荡幅度: {variability['oscillation_amplitude']:.2f} mmol/L")
    print(f"   └─ 解读: {variability['interpretation']}")
    
    # 显示患者教育内容
    education = intelligent_report['patient_education']
    if education:
        print(f"\n📚 【患者教育要点】")
        for edu in education:
            print(f"   📖 {edu['topic']}:")
            for content in edu['content']:
                print(f"      • {content}")
            print(f"      行动要点:")
            for action in edu['action_items']:
                print(f"        ✓ {action}")
    
    # 显示核心指标汇总
    print(f"\n📊 【核心指标汇总】")
    key_metrics = [
        ('tir_percentage', 'TIR目标范围内时间', '%'),
        ('tbr_percentage', 'TBR低血糖时间', '%'),
        ('tar_percentage', 'TAR高血糖时间', '%'),
        ('median_curve_smoothness', '曲线平滑度', ''),
        ('curve_symmetry_index', '对称性指数', ''),
        ('dawn_curve_slope', '黎明现象斜率', 'mmol/L/h'),
        ('morning_peak_height', '早晨峰值高度', 'mmol/L'),
        ('nocturnal_curve_flatness', '夜间稳定性', ''),
        ('percentile_spread_variability', '血糖变异性', '%'),
        ('comprehensive_smoothness_score', '综合平滑度', ''),
        ('curve_elegance_score', '曲线优雅度', ''),
        ('visual_complexity_index', '视觉复杂度', ''),
        ('fractal_dimension', '分形维数', ''),
        ('approximate_entropy', '近似熵', ''),
        ('target_range_coverage', '目标范围覆盖', '%'),
        ('hypoglycemia_zone_depth', '低血糖深度', 'mmol/L'),
        ('hyperglycemia_zone_height', '高血糖高度', 'mmol/L')
    ]
    
    for key, desc, unit in key_metrics:
        if key in analysis_results:
            value = analysis_results[key]
            if isinstance(value, bool):
                value_str = "是" if value else "否"
            elif isinstance(value, (int, float)):
                if unit == '%':
                    value_str = f"{value:.1f}{unit}"
                elif 'mmol/L' in unit:
                    value_str = f"{value:.2f} {unit}"
                else:
                    value_str = f"{value:.3f}{unit}"
            else:
                value_str = str(value)
            print(f"   {desc}: {value_str}")
    
    return intelligent_report

def main():
    """主程序演示"""
    
    # 生成真实的CGM演示数据
    print("🔬 正在生成真实CGM演示数据...")
    cgm_data = create_realistic_cgm_data(days=14, noise_level=0.6)
    
    print(f"✅ 生成完成：{len(cgm_data)}个数据点")
    print(f"   时间范围：{cgm_data['timestamp'].min()} 到 {cgm_data['timestamp'].max()}")
    print(f"   血糖范围：{cgm_data['glucose'].min():.1f} - {cgm_data['glucose'].max():.1f} mmol/L")
    print(f"   平均血糖：{cgm_data['glucose'].mean():.1f} mmol/L")
    
    # 患者信息
    patient_info = {
        'name': '李明',
        'age': 52,
        'gender': '男',
        'diabetes_type': 'T2DM',
        'diabetes_duration': '10年',
        'cgm_device': 'Dexcom G6',
        'current_treatment': '基础-餐时胰岛素方案'
    }
    
    # 进行完整分析并展示结果
    report = analyze_and_display_results(cgm_data, patient_info)
    
    # 保存完整报告
    report_filename = f"Complete_AGP_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 完整分析报告已保存至: {report_filename}")
    
    # 数据质量统计
    print(f"\n📈 【数据质量统计】")
    print(f"   数据完整性: {len(cgm_data)/1344*100:.1f}% (期望1344个点)")
    print(f"   TIR达标: {'✅' if report['technical_metrics'].get('tir_percentage', 0) >= 70 else '❌'}")
    print(f"   低血糖风险: {'⚠️' if report['technical_metrics'].get('tbr_percentage', 0) > 4 else '✅'}")
    print(f"   血糖稳定性: {'✅' if report['technical_metrics'].get('comprehensive_smoothness_score', 0) > 0.7 else '❌'}")
    
    print(f"\n🎯 分析完成！这就是基于57种视觉指标的完整AGP智能分析系统。")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.WARNING)  # 减少日志输出
    
    # 运行演示
    main()