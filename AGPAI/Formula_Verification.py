#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公式验证工具 - 检查AGP分析中的数学公式和算法正确性
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import stats
import json

def load_real_cgm_data():
    """加载真实CGM数据进行验证"""
    file_path = "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT-002最终版/40mg-v11-CGM导出原始数据-20240621/R006.txt"
    
    print("📁 读取真实CGM数据进行公式验证...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到数据开始行
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('ID\t时间\t记录类型'):
            data_start = i + 1
            break
    
    # 解析数据
    data_rows = []
    for line in lines[data_start:]:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split('\t')
        if len(parts) >= 4:
            try:
                timestamp_str = parts[1]
                glucose_value = float(parts[3])
                timestamp = pd.to_datetime(timestamp_str, format='%Y/%m/%d %H:%M')
                
                data_rows.append({
                    'timestamp': timestamp,
                    'glucose': glucose_value
                })
            except (ValueError, IndexError):
                continue
    
    cgm_data = pd.DataFrame(data_rows)
    cgm_data = cgm_data.sort_values('timestamp').reset_index(drop=True)
    
    print(f"✅ 读取了 {len(cgm_data)} 个数据点")
    print(f"📊 血糖范围: {cgm_data['glucose'].min():.1f} - {cgm_data['glucose'].max():.1f} mmol/L")
    
    return cgm_data

def verify_coefficient_of_variation(glucose_values):
    """验证变异系数(CV)计算"""
    print("\n🔍 验证变异系数(CV)计算:")
    print("="*50)
    
    # 移除缺失值
    clean_glucose = glucose_values.dropna()
    
    # 标准CV计算公式: CV = (标准偏差/均值) × 100%
    mean_glucose = clean_glucose.mean()
    std_glucose = clean_glucose.std()
    cv_correct = (std_glucose / mean_glucose) * 100
    
    print(f"📊 基础统计:")
    print(f"   数据点数: {len(clean_glucose)}")
    print(f"   均值 (Mean): {mean_glucose:.3f} mmol/L")
    print(f"   标准偏差 (SD): {std_glucose:.3f} mmol/L")
    
    print(f"\n🧮 变异系数计算:")
    print(f"   公式: CV = (SD / Mean) × 100%")
    print(f"   计算: CV = ({std_glucose:.3f} / {mean_glucose:.3f}) × 100%")
    print(f"   结果: CV = {cv_correct:.1f}%")
    
    # 检查其他可能的计算方法
    cv_numpy = (np.std(clean_glucose, ddof=1) / np.mean(clean_glucose)) * 100
    cv_pandas = (clean_glucose.std() / clean_glucose.mean()) * 100
    
    print(f"\n🔄 不同计算方法验证:")
    print(f"   NumPy方法: {cv_numpy:.1f}%")
    print(f"   Pandas方法: {cv_pandas:.1f}%")
    print(f"   手工计算: {cv_correct:.1f}%")
    
    # 临床参考范围
    print(f"\n📋 临床评估:")
    if cv_correct < 36:
        assessment = "✅ 正常 (CV < 36%)"
    elif cv_correct < 50:
        assessment = "⚠️ 偏高 (36% ≤ CV < 50%)"
    else:
        assessment = "🔴 过高 (CV ≥ 50%)"
    
    print(f"   变异系数评估: {assessment}")
    print(f"   ADA推荐目标: CV < 36%")
    
    return cv_correct

def verify_ada_metrics(glucose_values):
    """验证ADA标准指标计算"""
    print("\n🔍 验证ADA标准指标:")
    print("="*50)
    
    clean_glucose = glucose_values.dropna()
    
    # TIR (Time in Range) 3.9-10.0 mmol/L
    tir_count = len(clean_glucose[(clean_glucose >= 3.9) & (clean_glucose <= 10.0)])
    tir_percentage = (tir_count / len(clean_glucose)) * 100
    
    # TBR (Time Below Range)
    tbr_level1_count = len(clean_glucose[(clean_glucose >= 3.0) & (clean_glucose < 3.9)])  # Level 1: 3.0-3.9
    tbr_level2_count = len(clean_glucose[clean_glucose < 3.0])  # Level 2: <3.0
    tbr_level1_percentage = (tbr_level1_count / len(clean_glucose)) * 100
    tbr_level2_percentage = (tbr_level2_count / len(clean_glucose)) * 100
    
    # TAR (Time Above Range)
    tar_level1_count = len(clean_glucose[(clean_glucose > 10.0) & (clean_glucose <= 13.9)])  # Level 1: 10.1-13.9
    tar_level2_count = len(clean_glucose[clean_glucose > 13.9])  # Level 2: >13.9
    tar_level1_percentage = (tar_level1_count / len(clean_glucose)) * 100
    tar_level2_percentage = (tar_level2_count / len(clean_glucose)) * 100
    
    # GMI (Glucose Management Indicator)
    mean_glucose_mgdl = clean_glucose.mean() * 18.018  # 转换为mg/dL
    gmi = 3.31 + (0.02392 * mean_glucose_mgdl)
    
    print(f"📊 ADA核心指标:")
    print(f"   TIR (3.9-10.0 mmol/L): {tir_percentage:.1f}% (目标 >70%)")
    print(f"   TBR Level 1 (3.0-3.9): {tbr_level1_percentage:.1f}% (目标 <4%)")
    print(f"   TBR Level 2 (<3.0): {tbr_level2_percentage:.1f}% (目标 <1%)")
    print(f"   TAR Level 1 (10.1-13.9): {tar_level1_percentage:.1f}% (目标 <25%)")
    print(f"   TAR Level 2 (>13.9): {tar_level2_percentage:.1f}% (目标 <5%)")
    print(f"   GMI: {gmi:.1f}% (估计HbA1c)")
    
    # 评估
    assessments = []
    if tir_percentage >= 70:
        assessments.append("✅ TIR达标")
    else:
        assessments.append(f"❌ TIR未达标 (差{70-tir_percentage:.1f}%)")
    
    if tbr_level1_percentage <= 4:
        assessments.append("✅ TBR-L1达标")
    else:
        assessments.append(f"❌ TBR-L1超标 (超{tbr_level1_percentage-4:.1f}%)")
    
    if tbr_level2_percentage <= 1:
        assessments.append("✅ TBR-L2达标")
    else:
        assessments.append(f"❌ TBR-L2超标 (超{tbr_level2_percentage-1:.1f}%)")
    
    print(f"\n📋 ADA标准评估:")
    for assessment in assessments:
        print(f"   {assessment}")
    
    return {
        'TIR': tir_percentage,
        'TBR_L1': tbr_level1_percentage,
        'TBR_L2': tbr_level2_percentage,
        'TAR_L1': tar_level1_percentage,
        'TAR_L2': tar_level2_percentage,
        'GMI': gmi
    }

def verify_mage_calculation(glucose_values):
    """验证MAGE(平均血糖波动幅度)计算"""
    print("\n🔍 验证MAGE计算:")
    print("="*50)
    
    clean_glucose = glucose_values.dropna()
    
    # MAGE计算步骤:
    # 1. 计算标准偏差
    std_glucose = clean_glucose.std()
    
    # 2. 识别超过1个标准偏差的血糖变化
    glucose_diff = clean_glucose.diff().dropna()
    
    # 3. 找到峰值和谷值
    peaks = []
    valleys = []
    
    for i in range(1, len(clean_glucose)-1):
        if (clean_glucose.iloc[i] > clean_glucose.iloc[i-1] and 
            clean_glucose.iloc[i] > clean_glucose.iloc[i+1]):
            peaks.append(clean_glucose.iloc[i])
        elif (clean_glucose.iloc[i] < clean_glucose.iloc[i-1] and 
              clean_glucose.iloc[i] < clean_glucose.iloc[i+1]):
            valleys.append(clean_glucose.iloc[i])
    
    # 4. 计算有效的血糖波动(>1SD)
    valid_excursions = []
    
    # 简化的MAGE计算: 使用峰值和谷值之间的差异
    all_extremes = sorted(peaks + valleys)
    for i in range(len(all_extremes)-1):
        excursion = abs(all_extremes[i+1] - all_extremes[i])
        if excursion > std_glucose:
            valid_excursions.append(excursion)
    
    mage = np.mean(valid_excursions) if valid_excursions else 0
    
    print(f"📊 MAGE计算详情:")
    print(f"   血糖标准偏差: {std_glucose:.3f} mmol/L")
    print(f"   识别峰值数量: {len(peaks)}")
    print(f"   识别谷值数量: {len(valleys)}")
    print(f"   有效波动数量: {len(valid_excursions)}")
    print(f"   MAGE值: {mage:.3f} mmol/L")
    
    print(f"\n📋 MAGE评估:")
    if mage < 3.0:
        assessment = "✅ 良好 (MAGE < 3.0)"
    elif mage < 5.0:
        assessment = "⚠️ 中等 (3.0 ≤ MAGE < 5.0)"
    else:
        assessment = "🔴 较高 (MAGE ≥ 5.0)"
    
    print(f"   血糖波动评估: {assessment}")
    
    return mage

def verify_time_patterns(cgm_data):
    """验证时间模式分析"""
    print("\n🔍 验证时间模式分析:")
    print("="*50)
    
    # 添加时间特征
    cgm_data['hour'] = cgm_data['timestamp'].dt.hour
    cgm_data['date'] = cgm_data['timestamp'].dt.date
    
    # 1. 黎明现象分析 (凌晨4-8点血糖上升)
    dawn_hours = cgm_data[cgm_data['hour'].isin([4, 5, 6, 7, 8])]
    if len(dawn_hours) > 0:
        dawn_slope = np.polyfit(dawn_hours['hour'], dawn_hours['glucose'], 1)[0]
    else:
        dawn_slope = 0
    
    # 2. 餐后血糖分析 (假设餐时为7点、12点、18点)
    meal_times = [7, 12, 18]
    postprandial_peaks = []
    
    for meal_time in meal_times:
        # 餐后2小时血糖
        post_meal = cgm_data[cgm_data['hour'].isin([meal_time+1, meal_time+2])]
        pre_meal = cgm_data[cgm_data['hour'] == meal_time]
        
        if len(post_meal) > 0 and len(pre_meal) > 0:
            peak_increase = post_meal['glucose'].max() - pre_meal['glucose'].mean()
            postprandial_peaks.append(peak_increase)
    
    avg_postprandial_peak = np.mean(postprandial_peaks) if postprandial_peaks else 0
    
    # 3. 夜间稳定性 (22点-6点血糖变异系数)
    nocturnal_hours = cgm_data[cgm_data['hour'].isin([22, 23, 0, 1, 2, 3, 4, 5, 6])]
    if len(nocturnal_hours) > 10:
        nocturnal_cv = (nocturnal_hours['glucose'].std() / nocturnal_hours['glucose'].mean()) * 100
        nocturnal_stability = max(0, 1 - nocturnal_cv / 100)  # 转换为稳定性指数
    else:
        nocturnal_stability = 0
    
    print(f"📊 时间模式分析:")
    print(f"   黎明现象斜率: {dawn_slope:.3f} mmol/L/h")
    print(f"   平均餐后峰值: {avg_postprandial_peak:.3f} mmol/L")
    print(f"   夜间稳定性指数: {nocturnal_stability:.3f}")
    
    print(f"\n📋 时间模式评估:")
    
    # 黎明现象评估
    if abs(dawn_slope) < 0.5:
        dawn_assessment = "✅ 正常"
    elif abs(dawn_slope) < 1.0:
        dawn_assessment = "⚠️ 轻度"
    else:
        dawn_assessment = "🔴 明显"
    
    print(f"   黎明现象: {dawn_assessment}")
    
    # 餐后血糖评估
    if avg_postprandial_peak < 2.0:
        meal_assessment = "✅ 良好"
    elif avg_postprandial_peak < 3.0:
        meal_assessment = "⚠️ 中等"
    else:
        meal_assessment = "🔴 偏高"
    
    print(f"   餐后血糖控制: {meal_assessment}")
    
    # 夜间稳定性评估
    if nocturnal_stability > 0.8:
        night_assessment = "✅ 稳定"
    elif nocturnal_stability > 0.6:
        night_assessment = "⚠️ 一般"
    else:
        night_assessment = "🔴 不稳定"
    
    print(f"   夜间稳定性: {night_assessment}")
    
    return {
        'dawn_slope': dawn_slope,
        'postprandial_peak': avg_postprandial_peak,
        'nocturnal_stability': nocturnal_stability
    }

def compare_with_agp_analyzer(cgm_data):
    """与AGP分析器结果对比"""
    print("\n🔍 与AGP分析器结果对比:")
    print("="*50)
    
    # 导入AGP分析器
    try:
        from CGM_AGP_Analyzer_Agent import AGPVisualAnalyzer
        analyzer = AGPVisualAnalyzer(enable_quality_check=False)  # 跳过质量检查
        
        # 标准化数据格式
        standard_data = pd.DataFrame({
            'timestamp': cgm_data['timestamp'],
            'glucose': cgm_data['glucose'],
            'device_info': 'verification'
        })
        
        # 进行分析
        results = analyzer.analyze_cgm_data(standard_data, analysis_days=13)
        
        if 'error' not in results:
            print(f"📊 AGP分析器结果:")
            
            # 提取关键指标进行对比
            agp_metrics = {
                'smoothness': results.get('median_curve_smoothness', 0),
                'target_coverage': results.get('target_range_coverage', 0),
                'dawn_slope': results.get('dawn_curve_slope', 0),
                'nocturnal_flatness': results.get('nocturnal_curve_flatness', 0),
                'percentile_spread': results.get('percentile_spread_variability', 0)
            }
            
            for key, value in agp_metrics.items():
                print(f"   {key}: {value}")
            
            return agp_metrics
        else:
            print("❌ AGP分析器执行失败")
            return None
            
    except ImportError:
        print("❌ 无法导入AGP分析器")
        return None

def main():
    """主验证函数"""
    print("🔬 开始公式和算法验证")
    print("="*60)
    
    # 1. 加载真实数据
    cgm_data = load_real_cgm_data()
    
    # 2. 验证变异系数
    cv_result = verify_coefficient_of_variation(cgm_data['glucose'])
    
    # 3. 验证ADA指标
    ada_results = verify_ada_metrics(cgm_data['glucose'])
    
    # 4. 验证MAGE计算
    mage_result = verify_mage_calculation(cgm_data['glucose'])
    
    # 5. 验证时间模式
    time_patterns = verify_time_patterns(cgm_data)
    
    # 6. 与AGP分析器对比
    agp_comparison = compare_with_agp_analyzer(cgm_data)
    
    # 7. 生成验证报告
    verification_report = {
        'verification_timestamp': datetime.now().isoformat(),
        'data_summary': {
            'total_points': len(cgm_data),
            'glucose_range': [cgm_data['glucose'].min(), cgm_data['glucose'].max()],
            'mean_glucose': cgm_data['glucose'].mean(),
            'std_glucose': cgm_data['glucose'].std()
        },
        'manual_calculations': {
            'coefficient_of_variation': cv_result,
            'ada_metrics': ada_results,
            'mage': mage_result,
            'time_patterns': time_patterns
        },
        'agp_analyzer_results': agp_comparison
    }
    
    # 保存验证报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"/Users/williamsun/Documents/gplus/docs/AGPAI/Formula_Verification_Report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(verification_report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 验证报告已保存: {report_file}")
    
    # 8. 总结发现的问题
    print(f"\n📋 验证总结:")
    print(f"="*60)
    print(f"✅ 变异系数 (CV): {cv_result:.1f}%")
    print(f"✅ TIR: {ada_results['TIR']:.1f}%")
    print(f"✅ MAGE: {mage_result:.3f} mmol/L")
    print(f"✅ 黎明现象斜率: {time_patterns['dawn_slope']:.3f}")
    
    if agp_comparison:
        print(f"\n🔄 AGP分析器对比:")
        if 'percentile_spread' in agp_comparison:
            agp_cv = agp_comparison['percentile_spread']
            print(f"   手工CV: {cv_result:.1f}% vs AGP CV: {agp_cv:.1f}%")
            if abs(cv_result - agp_cv) > 5:
                print(f"   ⚠️ CV计算差异较大: {abs(cv_result - agp_cv):.1f}%")
            else:
                print(f"   ✅ CV计算基本一致")

if __name__ == "__main__":
    main()