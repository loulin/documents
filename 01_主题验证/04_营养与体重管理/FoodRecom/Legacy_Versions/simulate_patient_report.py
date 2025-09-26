#!/usr/bin/env python3
"""
模拟患者营养建议报告生成
患者信息：58岁男性，血脂血压高，肥胖
"""

import sys
import os
sys.path.append('/Users/williamsun/Documents/gplus/docs/FoodRecom')

from enhanced_food_recommender_v2 import (
    EnhancedChineseFoodRecommenderV2,
    UserProfile,
    ActivityLevel,
    HealthGoal,
    DietaryRestriction
)

def create_simulation_patient():
    """创建模拟患者档案"""

    # 58岁男性，血脂血压高，肥胖
    # 假设身高170cm，体重85kg (BMI=29.4，属于肥胖)
    patient = UserProfile(
        name="王先生",
        age=58,
        gender="男",
        height=170,  # cm
        weight=85,   # kg (BMI = 29.4)
        activity_level=ActivityLevel.LIGHT,  # 轻度活动

        # 健康目标：减重和血脂血压控制
        health_goals=[
            HealthGoal.WEIGHT_LOSS,
            HealthGoal.BLOOD_PRESSURE_CONTROL,
            HealthGoal.CHOLESTEROL_CONTROL
        ],

        # 饮食限制：低钠、低脂
        dietary_restrictions=[
            DietaryRestriction.LOW_SODIUM,
            DietaryRestriction.NONE
        ],

        # 实验室检查指标（模拟高血脂高血压）
        blood_glucose=5.8,  # 正常范围
        hba1c=5.9,  # 正常范围
        blood_pressure_systolic=155,  # 高血压2期
        blood_pressure_diastolic=95,   # 高血压2期
        cholesterol_total=6.8,  # 高胆固醇 (正常<5.2)
        cholesterol_ldl=4.5,    # 高LDL (正常<3.4)
        cholesterol_hdl=0.9,    # 低HDL (正常>1.0)
        triglycerides=2.8,      # 高甘油三酯 (正常<1.7)

        # 个人偏好
        preferred_cuisines=["家常菜", "粤菜"],
        disliked_foods=["内脏", "肥肉"],
        food_allergies=[]
    )

    return patient

def generate_patient_report():
    """生成患者营养建议报告"""

    print("=== 正在为模拟患者生成营养建议报告 ===")

    # 创建患者档案
    patient = create_simulation_patient()

    # 打印患者基本信息
    bmi = patient.weight / ((patient.height / 100) ** 2)
    print(f"患者信息：{patient.name}，{patient.age}岁，男性")
    print(f"身高：{patient.height}cm，体重：{patient.weight}kg")
    print(f"BMI：{bmi:.1f} (肥胖)")
    print(f"血压：{patient.blood_pressure_systolic}/{patient.blood_pressure_diastolic} mmHg (高血压2期)")
    print(f"总胆固醇：{patient.cholesterol_total} mmol/L (高)")
    print(f"LDL胆固醇：{patient.cholesterol_ldl} mmol/L (高)")
    print(f"HDL胆固醇：{patient.cholesterol_hdl} mmol/L (低)")
    print(f"甘油三酯：{patient.triglycerides} mmol/L (高)")

    # 创建营养建议系统
    recommender = EnhancedChineseFoodRecommenderV2()

    # 生成个性化报告
    report = recommender.generate_comprehensive_report_v2(patient)

    # 保存报告
    report_filename = "/Users/williamsun/Documents/gplus/docs/FoodRecom/营养建议报告_王先生_58岁_三高肥胖.md"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ 报告生成完成")
    print(f"📄 保存位置：{report_filename}")

    return report

if __name__ == "__main__":
    # 生成模拟患者报告
    report = generate_patient_report()

    # 显示报告片段
    print("\n=== 报告预览 ===")
    lines = report.split('\n')
    for i, line in enumerate(lines[:50]):  # 显示前50行
        print(line)

    if len(lines) > 50:
        print("...")
        print(f"[完整报告共{len(lines)}行，已保存到文件]")