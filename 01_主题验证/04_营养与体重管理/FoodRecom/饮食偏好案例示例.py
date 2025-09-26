#!/usr/bin/env python3
"""
饮食偏好案例示例
展示如何在营养管理系统中设置和使用饮食偏好
"""

import sys
import os
sys.path.append('Core_Systems')

from integrated_nutrition_system_v2 import IntegratedNutritionSystemV2, PatientProfile

def create_preference_examples():
    """创建不同饮食偏好的患者案例"""

    print("=== 饮食偏好案例示例 ===\n")

    # 案例1: 川菜爱好者，重辣偏好
    patient1 = PatientProfile(
        name="张先生",
        age=42,
        gender="男",
        height=175,
        weight=70,
        diagnosed_diseases=["高血压"],

        # 饮食偏好设置
        preferred_cuisines=["川菜"],           # 偏好川菜
        disliked_foods=["海鲜", "羊肉"],       # 不喜欢海鲜和羊肉
        dietary_restrictions=[],               # 无特殊饮食限制
        spice_tolerance="重辣",                # 重辣偏好
        cooking_preferences=["炒", "煮", "蒸"], # 偏好炒煮蒸
        allergies=["虾"]                       # 对虾过敏
    )

    # 案例2: 粤菜爱好者，清淡饮食
    patient2 = PatientProfile(
        name="李女士",
        age=38,
        gender="女",
        height=162,
        weight=58,
        diagnosed_diseases=["糖尿病"],

        # 饮食偏好设置
        preferred_cuisines=["粤菜"],           # 偏好粤菜
        disliked_foods=["动物内脏"],           # 不喜欢内脏
        dietary_restrictions=["低盐"],         # 低盐饮食
        spice_tolerance="微辣",                # 微辣偏好
        cooking_preferences=["蒸", "煮"],       # 偏好清蒸水煮
        allergies=[]                           # 无过敏
    )

    # 案例3: 素食主义者
    patient3 = PatientProfile(
        name="王女士",
        age=35,
        gender="女",
        height=168,
        weight=60,
        diagnosed_diseases=[],

        # 饮食偏好设置
        preferred_cuisines=["清淡"],           # 偏好清淡
        disliked_foods=[],                     # 无特别不喜欢
        dietary_restrictions=["素食"],         # 素食主义
        spice_tolerance="中等",                # 中等辣度
        cooking_preferences=["蒸", "煮", "炖"], # 偏好健康烹饪
        allergies=["花生"]                     # 花生过敏
    )

    return [patient1, patient2, patient3]

def demonstrate_preference_integration():
    """演示饮食偏好如何集成到营养推荐中"""

    # 创建系统实例
    system = IntegratedNutritionSystemV2()

    # 获取案例患者
    patients = create_preference_examples()

    for i, patient in enumerate(patients, 1):
        print(f"📋 案例 {i}: {patient.name} - 饮食偏好分析")
        print("="*50)

        # 显示患者饮食偏好
        print("👤 患者信息:")
        print(f"   年龄: {patient.age}岁, 性别: {patient.gender}")
        print(f"   BMI: {patient.bmi:.1f} ({patient.bmi_category})")
        print(f"   疾病: {', '.join(patient.diagnosed_diseases) if patient.diagnosed_diseases else '无'}")

        print("\n🍽️ 饮食偏好:")
        print(f"   偏好菜系: {', '.join(patient.preferred_cuisines) if patient.preferred_cuisines else '无偏好'}")
        print(f"   不喜食物: {', '.join(patient.disliked_foods) if patient.disliked_foods else '无'}")
        print(f"   饮食限制: {', '.join(patient.dietary_restrictions) if patient.dietary_restrictions else '无'}")
        print(f"   辣度承受: {patient.spice_tolerance}")
        print(f"   烹饪偏好: {', '.join(patient.cooking_preferences) if patient.cooking_preferences else '无'}")
        print(f"   过敏食物: {', '.join(patient.allergies) if patient.allergies else '无'}")

        # 生成个性化推荐
        print("\n🎯 个性化菜谱推荐:")
        recommendations = system._recommend_recipes(patient)

        for meal_type, recipes in recommendations.items():
            if meal_type not in ["个性化说明", "注意事项"]:
                print(f"   {meal_type}: {recipes[0] if recipes else '暂无推荐'}")

        # 显示个性化说明
        if "个性化说明" in recommendations:
            print(f"\n💡 {recommendations['个性化说明']}")

        if "注意事项" in recommendations:
            print(f"⚠️ {recommendations['注意事项']}")

        print("\n" + "-"*50 + "\n")

def show_preference_form_template():
    """展示饮食偏好采集表单模板"""

    print("📝 饮食偏好采集表单模板")
    print("="*40)

    form_template = {
        "基本信息": {
            "姓名": "患者姓名",
            "年龄": "数字",
            "性别": "男/女",
            "身高": "厘米",
            "体重": "公斤"
        },

        "健康状况": {
            "确诊疾病": ["糖尿病", "高血压", "血脂异常", "其他"],
            "服用药物": "药物名称列表",
            "过敏史": "过敏物质列表"
        },

        "饮食偏好": {
            "偏好菜系": {
                "选项": ["川菜", "粤菜", "鲁菜", "苏菜", "浙菜", "闽菜", "湘菜", "徽菜", "清淡", "其他"],
                "说明": "可多选，影响菜谱推荐风味"
            },
            "不喜食物": {
                "说明": "请列出不喜欢的具体食物",
                "示例": ["海鲜", "动物内脏", "羊肉", "某些蔬菜"]
            },
            "饮食限制": {
                "选项": ["素食", "清真", "低盐", "低脂", "无糖", "无麸质", "其他"],
                "说明": "宗教、健康或个人原因的饮食限制"
            },
            "辣度承受": {
                "选项": ["不能吃辣", "微辣", "中等", "重辣"],
                "说明": "影响调料和烹饪方式推荐"
            },
            "烹饪偏好": {
                "选项": ["蒸", "煮", "炒", "炖", "烤", "凉拌", "其他"],
                "说明": "偏好的烹饪方式，可多选"
            }
        },

        "特殊需求": {
            "食物过敏": {
                "常见过敏原": ["花生", "海鲜", "鸡蛋", "牛奶", "坚果", "其他"],
                "说明": "严重影响食谱推荐，必须准确填写"
            },
            "其他备注": "其他特殊饮食需求或说明"
        }
    }

    for category, fields in form_template.items():
        print(f"\n📋 {category}:")
        for field, details in fields.items():
            if isinstance(details, dict):
                print(f"   {field}:")
                if "选项" in details:
                    print(f"      选项: {', '.join(details['选项'])}")
                if "说明" in details:
                    print(f"      说明: {details['说明']}")
                if "示例" in details:
                    print(f"      示例: {', '.join(details['示例'])}")
            else:
                print(f"   {field}: {details}")

if __name__ == "__main__":
    print("🍽️ 饮食偏好集成演示\n")

    # 1. 演示饮食偏好集成
    demonstrate_preference_integration()

    # 2. 显示表单模板
    show_preference_form_template()

    print("\n" + "="*60)
    print("💡 使用建议:")
    print("1. 在患者初诊时收集完整的饮食偏好信息")
    print("2. 定期更新患者偏好，特别是饮食限制变化")
    print("3. 结合营养需求和个人偏好制定可执行的方案")
    print("4. 重视过敏信息，确保饮食安全")
    print("5. 考虑文化背景和地域饮食习惯")
    print("="*60)