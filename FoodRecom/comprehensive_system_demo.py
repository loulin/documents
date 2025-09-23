#!/usr/bin/env python3
"""
综合营养管理系统演示
展示完整的饮食偏好、GI数据库、营养雷达图集成功能
"""

import sys
import os
sys.path.append('Core_Systems')

from integrated_nutrition_system_v2 import IntegratedNutritionSystemV2, PatientProfile
from gi_database_integration_v2 import GIDatabaseSystemV2

def create_comprehensive_demo():
    """创建完整的系统演示"""

    print("🏥 综合营养管理系统完整演示")
    print("="*60)

    # 初始化系统
    nutrition_system = IntegratedNutritionSystemV2()
    gi_system = GIDatabaseSystemV2()

    print(f"✅ 营养系统初始化完成 - 包含 {nutrition_system.food_count} 种食物")
    print(f"✅ GI数据库初始化完成 - 包含 {len(gi_system.gi_database)} 种食物")
    print()

    # 创建测试患者 - 糖尿病患者，川菜爱好者
    test_patient = PatientProfile(
        name="赵大爷",
        age=65,
        gender="男",
        height=172,
        weight=78,
        diagnosed_diseases=["糖尿病", "高血压"],

        # 饮食偏好设置
        preferred_cuisines=["川菜", "清淡"],      # 偏好川菜和清淡
        disliked_foods=["海鲜", "动物内脏"],      # 不喜欢海鲜和内脏
        dietary_restrictions=["低盐", "低糖"],    # 低盐低糖饮食
        spice_tolerance="微辣",                   # 微辣偏好
        cooking_preferences=["蒸", "煮", "炖"],    # 偏好健康烹饪
        allergies=["虾", "蟹"]                    # 甲壳类过敏
    )

    print("👤 测试患者信息:")
    print(f"   姓名: {test_patient.name}")
    print(f"   年龄: {test_patient.age}岁, 性别: {test_patient.gender}")
    print(f"   身高: {test_patient.height}cm, 体重: {test_patient.weight}kg")
    print(f"   BMI: {test_patient.bmi:.1f} ({test_patient.bmi_category})")
    print(f"   疾病: {', '.join(test_patient.diagnosed_diseases)}")
    print()

    print("🍽️ 患者饮食偏好:")
    print(f"   偏好菜系: {', '.join(test_patient.preferred_cuisines)}")
    print(f"   不喜食物: {', '.join(test_patient.disliked_foods)}")
    print(f"   饮食限制: {', '.join(test_patient.dietary_restrictions)}")
    print(f"   辣度承受: {test_patient.spice_tolerance}")
    print(f"   烹饪偏好: {', '.join(test_patient.cooking_preferences)}")
    print(f"   过敏史: {', '.join(test_patient.allergies)}")
    print()

    # 1. 营养系统个性化推荐
    print("🎯 营养系统个性化推荐:")
    print("-" * 40)

    recommendations = nutrition_system._recommend_recipes(test_patient)

    for meal_type, recipes in recommendations.items():
        if meal_type not in ["个性化说明", "注意事项"]:
            print(f"   {meal_type}: {recipes[0] if recipes else '暂无推荐'}")

    if "个性化说明" in recommendations:
        print(f"\n💡 {recommendations['个性化说明']}")

    if "注意事项" in recommendations:
        print(f"⚠️ {recommendations['注意事项']}")

    print()

    # 2. GI数据库个性化推荐
    print("🍚 GI数据库个性化推荐:")
    print("-" * 40)

    gi_recommendations = gi_system.generate_personalized_gi_recommendations(test_patient)

    for category, items in gi_recommendations.items():
        if isinstance(items, list) and items:
            print(f"   {category}: {items[0]}")
        elif isinstance(items, str):
            print(f"   {category}: {items}")

    print()

    # 3. 糖尿病专用膳食计划
    print("📋 糖尿病专用膳食计划 (低血糖负荷):")
    print("-" * 40)

    diabetes_plan = gi_system.generate_diabetes_meal_plan(target_gl=12.0, patient=test_patient)

    for category, foods in diabetes_plan.items():
        if category not in ["个性化说明"]:
            if isinstance(foods, list) and foods:
                print(f"   {category}: {foods[0]}")
            elif isinstance(foods, str):
                print(f"   {category}: {foods}")

    if "个性化说明" in diabetes_plan and diabetes_plan["个性化说明"]:
        print(f"\n   个性化说明: {diabetes_plan['个性化说明'][0]}")
    print()

    # 4. 营养雷达图生成
    print("📊 营养雷达图分析:")
    print("-" * 40)

    try:
        # 选择川菜中适合糖尿病的菜品
        test_food = "麻婆豆腐"

        chart_file = nutrition_system.create_nutrition_radar_chart(
            [(test_food, 100.0)],
            chart_type="single",
            save_path="Charts/"
        )

        if chart_file:
            print(f"   ✅ 已生成 {test_food} 的营养雷达图: {chart_file}")
        else:
            print(f"   ❌ 未找到 {test_food} 的营养数据")

    except Exception as e:
        print(f"   ⚠️ 雷达图生成遇到问题: {e}")

    print()

    # 5. 完整营养报告
    print("📄 完整营养分析报告:")
    print("-" * 40)

    full_report = nutrition_system.generate_comprehensive_report_v2(test_patient)

    # 显示报告的关键部分
    report_lines = full_report.split('\n')
    key_sections = []
    current_section = []

    for line in report_lines:
        if line.startswith('##') or line.startswith('#'):
            if current_section:
                key_sections.append('\n'.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        key_sections.append('\n'.join(current_section))

    # 显示前几个关键部分
    for i, section in enumerate(key_sections[:3]):
        if section.strip():
            print(section[:300] + "..." if len(section) > 300 else section)
            print()

    return test_patient, recommendations, gi_recommendations, diabetes_plan

def demonstrate_preference_variations():
    """演示不同饮食偏好的效果对比"""

    print("\n" + "="*60)
    print("🔄 饮食偏好效果对比演示")
    print("="*60)

    # 基础患者信息（去除name字段）
    base_info = {
        "age": 50,
        "gender": "女",
        "height": 165,
        "weight": 65,
        "diagnosed_diseases": ["高血压"]
    }

    # 创建不同偏好的患者
    patients = [
        PatientProfile(
            name="川菜爱好者",
            **base_info,
            preferred_cuisines=["川菜"],
            spice_tolerance="重辣",
            cooking_preferences=["炒", "煮"]
        ),
        PatientProfile(
            name="粤菜爱好者",
            **base_info,
            preferred_cuisines=["粤菜"],
            spice_tolerance="不能吃辣",
            cooking_preferences=["蒸", "煲"]
        ),
        PatientProfile(
            name="素食主义者",
            **base_info,
            preferred_cuisines=["清淡"],
            dietary_restrictions=["素食"],
            spice_tolerance="微辣",
            cooking_preferences=["蒸", "煮", "炖"]
        )
    ]

    system = IntegratedNutritionSystemV2()

    for patient in patients:
        print(f"\n👤 {patient.name} 的推荐:")
        print(f"   偏好: {patient.preferred_cuisines[0]}, {patient.spice_tolerance}")
        if patient.dietary_restrictions:
            print(f"   限制: {', '.join(patient.dietary_restrictions)}")

        recommendations = system._recommend_recipes(patient)

        print("   推荐菜品:")
        for meal_type, recipes in recommendations.items():
            if meal_type not in ["个性化说明", "注意事项"] and recipes:
                print(f"     {meal_type}: {recipes[0]}")

def show_system_capabilities():
    """显示系统完整能力"""

    print("\n" + "="*60)
    print("🏆 系统能力总览")
    print("="*60)

    capabilities = {
        "🎯 个性化推荐": [
            "基于8大菜系的菜谱推荐",
            "考虑饮食偏好和限制",
            "根据疾病调整推荐",
            "过敏食物安全筛选"
        ],
        "🍚 GI血糖管理": [
            "95种食物GI数据库",
            "血糖负荷计算",
            "糖尿病膳食规划",
            "个性化GI推荐"
        ],
        "📊 可视化分析": [
            "营养成分雷达图",
            "疾病适宜性分析",
            "营养密度可视化",
            "健康指标对比"
        ],
        "📋 临床应用": [
            "35种疾病支持",
            "患者风险分层",
            "完整营养报告",
            "临床决策支持"
        ],
        "🔧 系统特性": [
            "完全独立运行",
            "中文界面支持",
            "模块化设计",
            "易于集成扩展"
        ]
    }

    for category, features in capabilities.items():
        print(f"\n{category}:")
        for feature in features:
            print(f"   ✅ {feature}")

    print(f"\n📈 系统规模:")
    system = IntegratedNutritionSystemV2()
    gi_system = GIDatabaseSystemV2()

    print(f"   • 菜谱数据库: {system.food_count} 种菜品")
    print(f"   • GI数据库: {len(gi_system.gi_database)} 种食物")
    print(f"   • 支持疾病: 35+ 种")
    print(f"   • 菜系覆盖: 8大菜系 + 地方特色")
    print(f"   • 偏好维度: 6个主要维度")

if __name__ == "__main__":
    print("🌟 综合营养管理系统 - 完整功能演示")
    print("包含: 饮食偏好 + GI数据库 + 营养雷达图 + 临床应用")
    print()

    try:
        # 1. 主要功能演示
        patient, recommendations, gi_recs, diabetes_plan = create_comprehensive_demo()

        # 2. 偏好对比演示
        demonstrate_preference_variations()

        # 3. 系统能力展示
        show_system_capabilities()

        print("\n" + "="*60)
        print("✅ 演示完成！系统功能完整，运行正常。")
        print("💡 建议: 根据实际需求选择对应的功能模块使用。")
        print("="*60)

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保 Core_Systems 目录中的文件完整")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        print("请检查系统配置和依赖")