#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试患者纵向分析功能 - 模拟同一患者的多次监测
演示历史对比和趋势分析功能
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from AGPAI_Agent_V2 import AGPAI_Agent_V2

def create_simulated_cgm_data(patient_id: str, base_tir: float, base_cv: float, visit_number: int):
    """创建模拟的CGM数据文件，显示治疗进展"""
    
    # 根据随访次数模拟治疗效果
    tir_improvement = (visit_number - 1) * 5  # 每次随访TIR提升5%
    cv_improvement = (visit_number - 1) * -2  # 每次随访CV降低2%
    
    current_tir = min(base_tir + tir_improvement, 85)  # TIR最高85%
    current_cv = max(base_cv + cv_improvement, 20)     # CV最低20%
    
    # 基于目标TIR和CV生成模拟数据
    mean_glucose = 7.5 + (1 - current_tir/100) * 3  # TIR越低，平均血糖越高
    glucose_std = mean_glucose * current_cv / 100
    
    # 生成14天的CGM数据
    start_date = datetime(2024, 6, 10) + timedelta(days=(visit_number-1)*30)
    data_points = []
    
    for day in range(14):
        for hour in range(24):
            for minute_interval in [0, 15, 30, 45]:
                timestamp = start_date + timedelta(days=day, hours=hour, minutes=minute_interval)
                
                # 添加昼夜节律
                hour_factor = 1 + 0.3 * np.sin((hour - 6) * np.pi / 12)  # 6点最低，18点最高
                
                # 添加餐后效应
                meal_effect = 0
                if hour in [8, 9, 10]:  # 早餐后
                    meal_effect = 2
                elif hour in [13, 14, 15]:  # 午餐后
                    meal_effect = 1.5
                elif hour in [19, 20, 21]:  # 晚餐后
                    meal_effect = 2.5
                
                # 生成血糖值
                base_glucose = np.random.normal(mean_glucose * hour_factor + meal_effect, glucose_std)
                glucose_value = max(3.5, min(base_glucose, 20.0))  # 限制在合理范围内
                
                data_points.append({
                    'id': len(data_points) + 100000,
                    'timestamp': timestamp.strftime('%Y/%m/%d %H:%M'),
                    'glucose': round(glucose_value, 1)
                })
    
    # 写入文件
    filename = f"simulated_{patient_id}_v{visit_number}.txt"
    file_path = os.path.join("./test_data/", filename)
    
    os.makedirs("./test_data/", exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("CGXI\n")
        f.write(f"# {patient_id}\n")
        f.write("ID\t时间\t记录类型\t葡萄糖历史记录（mmol/L）\n")
        
        for point in data_points:
            f.write(f"{point['id']}\t{point['timestamp']}\t0\t{point['glucose']}\n")
    
    return file_path

def demonstrate_longitudinal_analysis():
    """演示患者纵向分析功能"""
    
    print("🔬 AGPAI Agent V2.0 - 患者纵向分析演示")
    print("=" * 80)
    
    # 初始化Agent
    agent = AGPAI_Agent_V2()
    
    # 模拟患者的治疗历程
    patient_id = "P001_Demo"
    base_tir = 45.0  # 基线TIR
    base_cv = 32.0   # 基线CV
    
    # 模拟4次随访
    visits = [
        {"visit": 1, "description": "基线评估"},
        {"visit": 2, "description": "治疗调整后4周"},
        {"visit": 3, "description": "治疗调整后8周"},
        {"visit": 4, "description": "治疗调整后12周"}
    ]
    
    reports = []
    
    for visit_info in visits:
        visit_num = visit_info["visit"]
        description = visit_info["description"]
        
        print(f"\n📅 第{visit_num}次随访 - {description}")
        print("-" * 60)
        
        # 创建模拟数据
        file_path = create_simulated_cgm_data(patient_id, base_tir, base_cv, visit_num)
        
        # 分析CGM数据
        try:
            report = agent.generate_comprehensive_report(
                patient_id=patient_id,
                cgm_file_path=file_path,
                include_historical=True
            )
            
            reports.append({
                'visit': visit_num,
                'description': description,
                'report': report
            })
            
            # 提取并显示关键指标
            df = agent.read_cgm_file(file_path)
            glucose_cv, percentile_band_cv = agent.calculate_dual_variability(df)
            agp_metrics = agent.calculate_agp_metrics(df)
            
            print(f"📊 关键指标:")
            print(f"   TIR: {agp_metrics['tir']:.1f}%")
            print(f"   血糖CV: {glucose_cv:.1f}%")
            print(f"   昼夜CV: {percentile_band_cv:.1f}%")
            print(f"   TBR: {agp_metrics['tbr_level1']:.1f}%")
            
            # 显示历史对比部分（从第2次随访开始）
            if visit_num > 1:
                lines = report.split('\n')
                in_historical_section = False
                historical_lines = []
                
                for line in lines:
                    if '### 📈 患者历史对比分析' in line:
                        in_historical_section = True
                    elif in_historical_section and line.startswith('###') and '历史对比' not in line:
                        break
                    elif in_historical_section:
                        historical_lines.append(line)
                
                if historical_lines:
                    print("\n".join(historical_lines[:15]))  # 显示历史对比的前15行
                    print("...")
            
            # 清理临时文件
            os.remove(file_path)
            
        except Exception as e:
            print(f"❌ 分析失败: {str(e)}")
    
    # 生成总结分析
    print(f"\n\n📈 患者{patient_id}治疗历程总结")
    print("=" * 80)
    
    # 查看患者数据库中的历史记录
    if patient_id in agent.patient_database:
        history = agent.patient_database[patient_id]
        
        print(f"📊 历史记录数量: {len(history)}")
        print("\n🔍 TIR变化趋势:")
        
        for i, record in enumerate(history, 1):
            metrics = record['metrics']
            tir = metrics['tir']
            cv = metrics['glucose_cv']
            phenotype = metrics.get('phenotype', '未分类')
            
            change_indicator = ""
            if i > 1:
                prev_tir = history[i-2]['metrics']['tir']
                tir_change = tir - prev_tir
                change_indicator = f" ({tir_change:+.1f}%)"
            
            print(f"   第{i}次: TIR {tir:.1f}%{change_indicator}, CV {cv:.1f}%, 表型: {phenotype}")
        
        # 计算总体改善
        if len(history) >= 2:
            initial_tir = history[0]['metrics']['tir']
            final_tir = history[-1]['metrics']['tir']
            total_improvement = final_tir - initial_tir
            
            print(f"\n🎯 总体治疗效果:")
            print(f"   TIR改善: {total_improvement:+.1f}% (从{initial_tir:.1f}%到{final_tir:.1f}%)")
            
            if total_improvement > 10:
                print("   ✅ 治疗效果显著，管理策略成功")
            elif total_improvement > 5:
                print("   📈 治疗效果良好，继续当前策略")
            elif total_improvement > 0:
                print("   📊 治疗效果轻度，可考虑进一步优化")
            else:
                print("   ⚠️ 需要重新评估治疗方案")
    
    # 清理测试数据目录
    if os.path.exists("./test_data/"):
        import shutil
        shutil.rmtree("./test_data/")
    
    print(f"\n✨ 演示完成！患者纵向分析功能展示了AGPAI Agent V2.0的强大历史对比能力。")

def demonstrate_phenotype_transition():
    """演示临床表型转换的识别"""
    
    print("\n\n🔄 临床表型转换演示")
    print("=" * 60)
    
    agent = AGPAI_Agent_V2()
    
    # 模拟不同的表型转换场景
    transitions = [
        {
            "from": {"tir": 45, "cv": 28, "phenotype": "稳定性高血糖型"},
            "to": {"tir": 68, "cv": 26, "phenotype": "接近达标型"},
            "scenario": "治疗强化成功"
        },
        {
            "from": {"tir": 68, "cv": 26, "phenotype": "接近达标型"},
            "to": {"tir": 87, "cv": 22, "phenotype": "优化控制型"},
            "scenario": "精细化管理成功"
        },
        {
            "from": {"tir": 72, "cv": 25, "phenotype": "接近达标型"},
            "to": {"tir": 58, "cv": 31, "phenotype": "接近达标型"},
            "scenario": "治疗依从性下降"
        }
    ]
    
    for i, transition in enumerate(transitions, 1):
        print(f"\n场景{i}: {transition['scenario']}")
        print(f"   表型变化: {transition['from']['phenotype']} → {transition['to']['phenotype']}")
        print(f"   TIR变化: {transition['from']['tir']:.1f}% → {transition['to']['tir']:.1f}%")
        print(f"   CV变化: {transition['from']['cv']:.1f}% → {transition['to']['cv']:.1f}%")
        
        # 使用Agent的表型变化评估函数
        assessment = agent._assess_phenotype_change(
            transition['from']['phenotype'], 
            transition['to']['phenotype']
        )
        print(f"   系统评估: {assessment}")

if __name__ == "__main__":
    try:
        demonstrate_longitudinal_analysis()
        demonstrate_phenotype_transition()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断演示")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()