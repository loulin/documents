#!/usr/bin/env python3
"""
增强版中式个性化营养建议系统 V2.0
集成29道中式菜谱，覆盖八大菜系和健康食谱
基于《中国居民膳食指南(2022)》和国际营养学会疾病营养指南
采用循证医学方法，提供科学的营养建议
"""

import json
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

# 导入扩展菜谱数据库
from expanded_chinese_recipes import (
    ExpandedChineseRecipeDatabase,
    ExtendedChineseDish,
    CuisineType,
    CookingMethod
)

class ActivityLevel(Enum):
    SEDENTARY = "久坐"
    LIGHT = "轻度活动"
    MODERATE = "中等活动"
    ACTIVE = "活跃"
    VERY_ACTIVE = "非常活跃"

class HealthGoal(Enum):
    WEIGHT_LOSS = "减重"
    WEIGHT_GAIN = "增重"
    MAINTAIN_WEIGHT = "维持体重"
    MUSCLE_GAIN = "增肌"
    DIABETES_CONTROL = "血糖控制"
    BLOOD_PRESSURE_CONTROL = "血压控制"
    CHOLESTEROL_CONTROL = "血脂控制"

class DietaryRestriction(Enum):
    NONE = "无限制"
    VEGETARIAN = "素食"
    VEGAN = "纯素食"
    GLUTEN_FREE = "无麸质"
    LOW_SODIUM = "低钠"
    LOW_CARB = "低碳水"
    DIABETIC = "糖尿病饮食"

class DiseaseType(Enum):
    HEALTHY = "健康人群"
    TYPE2_DIABETES = "2型糖尿病"
    HYPERTENSION = "高血压"
    DYSLIPIDEMIA = "血脂异常"
    METABOLIC_SYNDROME = "代谢综合征"

@dataclass
class UserProfile:
    """用户档案"""
    name: str
    age: int
    gender: str  # "男" or "女"
    height: float  # cm
    weight: float  # kg
    activity_level: ActivityLevel
    health_goals: List[HealthGoal]
    dietary_restrictions: List[DietaryRestriction]

    # 实验室检查指标
    blood_glucose: Optional[float] = None  # mmol/L
    hba1c: Optional[float] = None  # %
    blood_pressure_systolic: Optional[int] = None  # mmHg
    blood_pressure_diastolic: Optional[int] = None  # mmHg
    cholesterol_total: Optional[float] = None  # mmol/L
    cholesterol_ldl: Optional[float] = None  # mmol/L
    cholesterol_hdl: Optional[float] = None  # mmol/L
    triglycerides: Optional[float] = None  # mmol/L

    # 个人偏好
    preferred_cuisines: List[str] = None  # 偏好菜系
    disliked_foods: List[str] = None  # 不喜欢的食物
    food_allergies: List[str] = None  # 食物过敏

    def __post_init__(self):
        if self.preferred_cuisines is None:
            self.preferred_cuisines = []
        if self.disliked_foods is None:
            self.disliked_foods = []
        if self.food_allergies is None:
            self.food_allergies = []

@dataclass
class NutritionInfo:
    """营养信息"""
    calories: float  # 千卡/100g
    protein: float  # 蛋白质 g/100g
    carbs: float  # 碳水化合物 g/100g
    fat: float  # 脂肪 g/100g
    fiber: float  # 膳食纤维 g/100g
    sodium: float  # 钠 mg/100g
    sugar: float = 0  # 糖 g/100g

@dataclass
class ChineseFood:
    """中式食物信息"""
    name: str
    category: str
    nutrition_per_100g: NutritionInfo
    glycemic_index: Optional[int] = None
    allergens: List[str] = None

    def __post_init__(self):
        if self.allergens is None:
            self.allergens = []

class EnhancedChineseFoodRecommenderV2:
    """增强版中国本土化个性化饮食推荐系统 V2.0"""

    def __init__(self):
        self.food_database = self._initialize_food_database()
        self.recipe_database = ExpandedChineseRecipeDatabase()
        self.disease_protocols = self._initialize_disease_protocols()
        self.activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.375,
            ActivityLevel.MODERATE: 1.55,
            ActivityLevel.ACTIVE: 1.725,
            ActivityLevel.VERY_ACTIVE: 1.9
        }

    def _initialize_food_database(self) -> Dict[str, ChineseFood]:
        """初始化中式食物数据库"""
        foods = {}

        # 主食类
        foods["白米饭"] = ChineseFood(
            name="白米饭", category="主食",
            nutrition_per_100g=NutritionInfo(116, 2.6, 25.9, 0.3, 0.3, 147),
            glycemic_index=87
        )

        foods["糙米饭"] = ChineseFood(
            name="糙米饭", category="主食",
            nutrition_per_100g=NutritionInfo(112, 2.1, 23.0, 0.9, 1.8, 5),
            glycemic_index=50
        )

        foods["燕麦片"] = ChineseFood(
            name="燕麦片", category="主食",
            nutrition_per_100g=NutritionInfo(389, 16.9, 66.3, 6.9, 10.6, 20),
            glycemic_index=42
        )

        foods["荞麦面"] = ChineseFood(
            name="荞麦面", category="主食",
            nutrition_per_100g=NutritionInfo(335, 11.7, 71.5, 1.3, 6.5, 18),
            glycemic_index=45
        )

        # 蛋白质类
        foods["鸡蛋"] = ChineseFood(
            name="鸡蛋", category="蛋类",
            nutrition_per_100g=NutritionInfo(155, 13.0, 1.1, 11.0, 0, 131)
        )

        foods["鸡胸肉"] = ChineseFood(
            name="鸡胸肉", category="禽肉",
            nutrition_per_100g=NutritionInfo(165, 31.0, 0, 3.6, 0, 74)
        )

        foods["三文鱼"] = ChineseFood(
            name="三文鱼", category="鱼类",
            nutrition_per_100g=NutritionInfo(208, 20.0, 0, 13.0, 0, 49)
        )

        foods["鲫鱼"] = ChineseFood(
            name="鲫鱼", category="鱼类",
            nutrition_per_100g=NutritionInfo(108, 17.1, 0, 2.7, 0, 51)
        )

        foods["豆腐"] = ChineseFood(
            name="豆腐", category="豆制品",
            nutrition_per_100g=NutritionInfo(98, 8.1, 4.2, 4.8, 0.4, 7)
        )

        # 蔬菜类
        foods["西兰花"] = ChineseFood(
            name="西兰花", category="蔬菜",
            nutrition_per_100g=NutritionInfo(34, 2.8, 7.0, 0.4, 3.7, 33)
        )

        foods["小白菜"] = ChineseFood(
            name="小白菜", category="蔬菜",
            nutrition_per_100g=NutritionInfo(15, 1.5, 3.0, 0.3, 1.1, 73)
        )

        foods["菠菜"] = ChineseFood(
            name="菠菜", category="蔬菜",
            nutrition_per_100g=NutritionInfo(28, 2.6, 4.5, 0.4, 1.7, 85)
        )

        foods["胡萝卜"] = ChineseFood(
            name="胡萝卜", category="蔬菜",
            nutrition_per_100g=NutritionInfo(37, 1.0, 8.8, 0.2, 3.2, 25)
        )

        foods["番茄"] = ChineseFood(
            name="番茄", category="蔬菜",
            nutrition_per_100g=NutritionInfo(18, 0.9, 3.9, 0.2, 1.4, 5)
        )

        foods["黄瓜"] = ChineseFood(
            name="黄瓜", category="蔬菜",
            nutrition_per_100g=NutritionInfo(16, 0.7, 4.0, 0.1, 0.5, 6)
        )

        # 水果类
        foods["苹果"] = ChineseFood(
            name="苹果", category="水果",
            nutrition_per_100g=NutritionInfo(52, 0.3, 14.0, 0.2, 2.4, 1),
            glycemic_index=36
        )

        foods["香蕉"] = ChineseFood(
            name="香蕉", category="水果",
            nutrition_per_100g=NutritionInfo(93, 1.0, 22.0, 0.2, 1.7, 1),
            glycemic_index=52
        )

        # 奶制品
        foods["牛奶"] = ChineseFood(
            name="牛奶", category="奶制品",
            nutrition_per_100g=NutritionInfo(54, 3.0, 3.4, 3.2, 0, 37)
        )

        foods["酸奶"] = ChineseFood(
            name="酸奶", category="奶制品",
            nutrition_per_100g=NutritionInfo(59, 3.2, 4.5, 3.3, 0, 47)
        )

        # 坚果类
        foods["核桃"] = ChineseFood(
            name="核桃", category="坚果",
            nutrition_per_100g=NutritionInfo(654, 14.9, 13.7, 65.2, 9.6, 2)
        )

        # 调料
        foods["橄榄油"] = ChineseFood(
            name="橄榄油", category="油脂",
            nutrition_per_100g=NutritionInfo(884, 0, 0, 100, 0, 2)
        )

        foods["大蒜"] = ChineseFood(
            name="大蒜", category="调料",
            nutrition_per_100g=NutritionInfo(126, 4.5, 27.6, 0.2, 1.1, 12)
        )

        foods["生姜"] = ChineseFood(
            name="生姜", category="调料",
            nutrition_per_100g=NutritionInfo(41, 1.3, 8.8, 0.3, 2.0, 27)
        )

        return foods

    def _initialize_disease_protocols(self) -> Dict[DiseaseType, Dict]:
        """初始化疾病营养方案"""
        protocols = {}

        protocols[DiseaseType.TYPE2_DIABETES] = {
            "carb_percentage": (0.40, 0.50),
            "protein_percentage": (0.15, 0.25),
            "fat_percentage": (0.25, 0.40),
            "fiber_target": 35,
            "sodium_limit": 2300,
            "glycemic_index_preference": "low",
            "preferred_cuisines": [CuisineType.HEALTH, CuisineType.CANTONESE],
            "cooking_methods": [CookingMethod.STEAMING, CookingMethod.BOILING, CookingMethod.STEWING]
        }

        protocols[DiseaseType.HYPERTENSION] = {
            "carb_percentage": (0.50, 0.60),
            "protein_percentage": (0.15, 0.20),
            "fat_percentage": (0.25, 0.30),
            "sodium_limit": 1500,
            "potassium_target": 3500,
            "preferred_cuisines": [CuisineType.HEALTH, CuisineType.CANTONESE],
            "cooking_methods": [CookingMethod.STEAMING, CookingMethod.COLD_MIXING, CookingMethod.BOILING]
        }

        return protocols

    def analyze_disease_risk(self, user: UserProfile) -> List[DiseaseType]:
        """分析疾病风险"""
        diseases = []

        # 糖尿病判断
        if (user.blood_glucose and user.blood_glucose >= 7.0) or \
           (user.hba1c and user.hba1c >= 6.5):
            diseases.append(DiseaseType.TYPE2_DIABETES)

        # 高血压判断
        if (user.blood_pressure_systolic and user.blood_pressure_systolic >= 140) or \
           (user.blood_pressure_diastolic and user.blood_pressure_diastolic >= 90):
            diseases.append(DiseaseType.HYPERTENSION)

        # 血脂异常判断
        if (user.cholesterol_total and user.cholesterol_total >= 6.2) or \
           (user.cholesterol_ldl and user.cholesterol_ldl >= 4.1) or \
           (user.triglycerides and user.triglycerides >= 2.3):
            diseases.append(DiseaseType.DYSLIPIDEMIA)

        if not diseases:
            diseases.append(DiseaseType.HEALTHY)

        return diseases

    def generate_enhanced_meal_plan_v2(self, user: UserProfile) -> Dict:
        """生成增强版膳食计划 V2.0"""
        diseases = self.analyze_disease_risk(user)
        primary_disease = diseases[0]

        # 计算营养需求
        bmr = self.calculate_bmr(user)
        tdee = self.calculate_tdee(user)
        target_calories = self._calculate_target_calories(user, tdee)

        # 获取适合的菜谱
        suitable_recipes = self._get_suitable_recipes(user, primary_disease)

        # 生成四餐计划
        meal_plan = {
            "breakfast": self._create_enhanced_breakfast(target_calories * 0.25, suitable_recipes, user),
            "lunch": self._create_enhanced_lunch(target_calories * 0.35, suitable_recipes, user),
            "dinner": self._create_enhanced_dinner(target_calories * 0.30, suitable_recipes, user),
            "snack": self._create_enhanced_snack(target_calories * 0.10, suitable_recipes, user)
        }

        return {
            "user_info": user,
            "diseases": diseases,
            "nutrition_targets": {
                "bmr": bmr,
                "tdee": tdee,
                "target_calories": target_calories
            },
            "meal_plan": meal_plan,
            "total_recipes_available": len(suitable_recipes)
        }

    def _get_suitable_recipes(self, user: UserProfile, disease: DiseaseType) -> Dict[str, ExtendedChineseDish]:
        """获取适合的菜谱"""
        all_recipes = self.recipe_database.recipes
        suitable_recipes = {}

        # 基于疾病类型筛选
        if disease in self.disease_protocols:
            protocol = self.disease_protocols[disease]
            preferred_cuisines = protocol.get("preferred_cuisines", [])
            preferred_methods = protocol.get("cooking_methods", [])

            for name, recipe in all_recipes.items():
                # 检查菜系偏好
                if preferred_cuisines and recipe.cuisine_type not in preferred_cuisines:
                    # 但仍保留一些家常菜和健康菜
                    if recipe.cuisine_type not in [CuisineType.HOMESTYLE, CuisineType.HEALTH]:
                        continue

                # 检查烹饪方法
                if preferred_methods and recipe.cooking_method not in preferred_methods:
                    # 对于疾病患者，严格限制油炸等不健康烹饪方法
                    if recipe.cooking_method == CookingMethod.DEEP_FRYING and disease != DiseaseType.HEALTHY:
                        continue

                # 检查适宜人群
                disease_chinese = disease.value
                if disease_chinese in recipe.avoid_for:
                    continue

                suitable_recipes[name] = recipe
        else:
            # 健康人群可以选择所有菜谱
            suitable_recipes = all_recipes.copy()

        # 基于用户偏好进一步筛选
        if user.preferred_cuisines:
            filtered_recipes = {}
            for name, recipe in suitable_recipes.items():
                if any(cuisine in recipe.cuisine_type.value for cuisine in user.preferred_cuisines):
                    filtered_recipes[name] = recipe
            if filtered_recipes:  # 如果有匹配的偏好菜谱
                suitable_recipes = filtered_recipes

        return suitable_recipes

    def _create_enhanced_breakfast(self, target_calories: float, recipes: Dict, user: UserProfile) -> Dict:
        """创建增强版早餐"""
        breakfast_recipes = {name: recipe for name, recipe in recipes.items()
                           if recipe.difficulty == "简单" and recipe.cooking_time <= 20}

        if not breakfast_recipes:
            breakfast_recipes = recipes

        # 随机选择一道适合早餐的菜
        suitable_breakfast = [name for name, recipe in breakfast_recipes.items()
                            if any(ingredient[0] in ["鸡蛋", "牛奶", "燕麦片"]
                                 for ingredient in recipe.main_ingredients)]

        if suitable_breakfast:
            selected_recipe_name = random.choice(suitable_breakfast)
            selected_recipe = breakfast_recipes[selected_recipe_name]
        else:
            # 默认早餐
            selected_recipe_name = "蒸蛋羹"
            selected_recipe = None

        return {
            "recipe_name": selected_recipe_name,
            "recipe": selected_recipe,
            "estimated_calories": target_calories,
            "description": f"精选{selected_recipe_name}作为健康早餐"
        }

    def _create_enhanced_lunch(self, target_calories: float, recipes: Dict, user: UserProfile) -> Dict:
        """创建增强版午餐"""
        # 偏好有蛋白质和蔬菜的菜谱
        lunch_recipes = {name: recipe for name, recipe in recipes.items()
                        if recipe.cooking_time <= 45}

        # 选择有荤有素的搭配
        protein_dishes = [name for name, recipe in lunch_recipes.items()
                         if any(ingredient[0] in ["鸡胸肉", "鱼", "豆腐", "牛肉", "猪肉"]
                              for ingredient in recipe.main_ingredients)]

        if protein_dishes:
            selected_recipe_name = random.choice(protein_dishes)
            selected_recipe = lunch_recipes[selected_recipe_name]
        else:
            selected_recipe_name = list(lunch_recipes.keys())[0] if lunch_recipes else "清炒小白菜"
            selected_recipe = lunch_recipes.get(selected_recipe_name)

        return {
            "recipe_name": selected_recipe_name,
            "recipe": selected_recipe,
            "estimated_calories": target_calories,
            "description": f"营养丰富的{selected_recipe_name}，搭配主食"
        }

    def _create_enhanced_dinner(self, target_calories: float, recipes: Dict, user: UserProfile) -> Dict:
        """创建增强版晚餐"""
        # 晚餐选择清淡一些的菜谱
        dinner_recipes = {name: recipe for name, recipe in recipes.items()
                         if recipe.cooking_method in [CookingMethod.STEAMING, CookingMethod.BOILING,
                                                     CookingMethod.STIR_FRYING, CookingMethod.COLD_MIXING]}

        # 优先选择蔬菜类和汤类
        light_dishes = [name for name, recipe in dinner_recipes.items()
                       if "汤" in name or any(ingredient[0] in ["蔬菜", "豆腐", "鱼"]
                                           for ingredient in recipe.main_ingredients)]

        if light_dishes:
            selected_recipe_name = random.choice(light_dishes)
            selected_recipe = dinner_recipes[selected_recipe_name]
        else:
            selected_recipe_name = list(dinner_recipes.keys())[0] if dinner_recipes else "清蒸鲫鱼"
            selected_recipe = dinner_recipes.get(selected_recipe_name)

        return {
            "recipe_name": selected_recipe_name,
            "recipe": selected_recipe,
            "estimated_calories": target_calories,
            "description": f"清淡营养的{selected_recipe_name}"
        }

    def _create_enhanced_snack(self, target_calories: float, recipes: Dict, user: UserProfile) -> Dict:
        """创建增强版加餐"""
        # 加餐选择简单的健康食品
        health_recipes = self.recipe_database.get_healthy_recipes()

        if health_recipes:
            selected_recipe_name = random.choice(list(health_recipes.keys()))
            selected_recipe = health_recipes[selected_recipe_name]
        else:
            selected_recipe_name = "核桃酸奶"
            selected_recipe = None

        return {
            "recipe_name": selected_recipe_name,
            "recipe": selected_recipe,
            "estimated_calories": target_calories,
            "description": f"健康养生的{selected_recipe_name}"
        }

    def generate_comprehensive_report_v2(self, user: UserProfile) -> str:
        """生成全面报告 V2.0"""
        meal_plan_data = self.generate_enhanced_meal_plan_v2(user)

        report = f"""# {user.name} 个性化中式营养方案报告 V2.0

*基于29道中式菜谱的智能推荐系统*
*涵盖八大菜系、家常菜、健康食谱*
*遵循现代营养学和循证医学原则*

## 📋 基本信息
- **姓名**: {user.name}
- **年龄**: {user.age}岁
- **性别**: {user.gender}
- **身高**: {user.height}cm
- **体重**: {user.weight}kg
- **BMI**: {user.weight / ((user.height / 100) ** 2):.1f}
- **活动水平**: {user.activity_level.value}

## 🏥 健康状况评估
"""

        diseases = meal_plan_data["diseases"]
        for disease in diseases:
            if disease != DiseaseType.HEALTHY:
                report += f"- **{disease.value}**: 需要特殊营养管理\n"

        nutrition_targets = meal_plan_data["nutrition_targets"]
        report += f"""
## 🎯 营养目标
- **基础代谢率**: {nutrition_targets['bmr']:.0f} 千卡
- **总日消耗**: {nutrition_targets['tdee']:.0f} 千卡
- **目标摄入**: {nutrition_targets['target_calories']:.0f} 千卡
- **可选菜谱**: {meal_plan_data['total_recipes_available']}道

## 🍽️ 个性化中式菜谱推荐

### 早餐
**推荐菜品**: {meal_plan_data['meal_plan']['breakfast']['recipe_name']}
- **预估热量**: {meal_plan_data['meal_plan']['breakfast']['estimated_calories']:.0f} 千卡
- **推荐理由**: {meal_plan_data['meal_plan']['breakfast']['description']}
"""

        breakfast_recipe = meal_plan_data['meal_plan']['breakfast']['recipe']
        if breakfast_recipe:
            report += f"""
**制作方法**: {breakfast_recipe.description}
**烹饪时间**: {breakfast_recipe.cooking_time}分钟
**难度等级**: {breakfast_recipe.difficulty}
"""
            if breakfast_recipe.health_benefits:
                report += f"**营养功效**: {', '.join(breakfast_recipe.health_benefits)}\n"

        report += f"""
### 午餐
**推荐菜品**: {meal_plan_data['meal_plan']['lunch']['recipe_name']}
- **预估热量**: {meal_plan_data['meal_plan']['lunch']['estimated_calories']:.0f} 千卡
- **推荐理由**: {meal_plan_data['meal_plan']['lunch']['description']}
"""

        lunch_recipe = meal_plan_data['meal_plan']['lunch']['recipe']
        if lunch_recipe:
            report += f"""
**制作方法**: {lunch_recipe.description}
**菜系**: {lunch_recipe.cuisine_type.value}
**烹饪方法**: {lunch_recipe.cooking_method.value}
"""
            if lunch_recipe.health_benefits:
                report += f"**营养功效**: {', '.join(lunch_recipe.health_benefits)}\n"

        report += f"""
### 晚餐
**推荐菜品**: {meal_plan_data['meal_plan']['dinner']['recipe_name']}
- **预估热量**: {meal_plan_data['meal_plan']['dinner']['estimated_calories']:.0f} 千卡
- **推荐理由**: {meal_plan_data['meal_plan']['dinner']['description']}
"""

        dinner_recipe = meal_plan_data['meal_plan']['dinner']['recipe']
        if dinner_recipe:
            report += f"""
**制作方法**: {dinner_recipe.description}
**菜系**: {dinner_recipe.cuisine_type.value}
**烹饪方法**: {dinner_recipe.cooking_method.value}
"""
            if dinner_recipe.health_benefits:
                report += f"**营养功效**: {', '.join(dinner_recipe.health_benefits)}\n"

        report += f"""
### 加餐
**推荐菜品**: {meal_plan_data['meal_plan']['snack']['recipe_name']}
- **预估热量**: {meal_plan_data['meal_plan']['snack']['estimated_calories']:.0f} 千卡
- **推荐理由**: {meal_plan_data['meal_plan']['snack']['description']}

## 🏮 中式菜谱数据库统计
"""

        # 添加菜谱数据库统计
        cuisine_count = self.recipe_database.get_recipe_count_by_cuisine()
        for cuisine, count in cuisine_count.items():
            report += f"- **{cuisine}**: {count}道菜谱\n"

        report += f"""
## 💡 个性化建议

### 🍽️ 菜系搭配建议
基于您的健康状况，推荐以下菜系：
"""

        primary_disease = diseases[0]
        if primary_disease == DiseaseType.TYPE2_DIABETES:
            report += """
- **粤菜**: 清淡少油，适合血糖控制
- **健康食谱**: 营养均衡，科学搭配
- **家常菜**: 制作简便，营养丰富
"""
        elif primary_disease == DiseaseType.HYPERTENSION:
            report += """
- **粤菜**: 少盐清蒸，保护心血管
- **素食菜**: 富含钾元素，有助降血压
- **家常菜**: 控制调料，健康美味
"""
        else:
            report += """
- **八大菜系**: 营养丰富，口味多样
- **家常菜**: 制作简便，适合日常
- **健康食谱**: 预防疾病，增强体质
"""

        report += f"""
### 🔄 菜谱轮换建议
- 每周更换3-4道新菜谱
- 保持菜系多样性
- 根据季节调整食材
- 注意营养均衡搭配

### ⚠️ 注意事项
- 严格控制烹饪用油量
- 注意食物过敏原
- 遵循疾病饮食限制
- 定期监测健康指标

---
*报告生成时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}*
*本报告基于29道中式菜谱智能匹配生成*
*遵循现代营养学和循证医学原则*
*具体饮食方案请咨询专业营养师*
"""

        return report

    def calculate_bmr(self, user: UserProfile) -> float:
        """计算基础代谢率"""
        if user.gender == "男":
            bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
        else:
            bmr = 447.593 + (9.247 * user.weight) + (3.098 * user.height) - (4.330 * user.age)
        return bmr

    def calculate_tdee(self, user: UserProfile) -> float:
        """计算总日能量消耗"""
        bmr = self.calculate_bmr(user)
        return bmr * self.activity_multipliers[user.activity_level]

    def _calculate_target_calories(self, user: UserProfile, tdee: float) -> float:
        """计算目标热量摄入"""
        if HealthGoal.WEIGHT_LOSS in user.health_goals:
            return tdee * 0.8  # 减重：减少20%热量
        elif HealthGoal.WEIGHT_GAIN in user.health_goals:
            return tdee * 1.2  # 增重：增加20%热量
        else:
            return tdee  # 维持体重

# 示例使用
if __name__ == "__main__":
    # 创建增强版推荐系统
    recommender = EnhancedChineseFoodRecommenderV2()

    # 创建测试用户
    user1 = UserProfile(
        name="张女士",
        age=42,
        gender="女",
        height=162,
        weight=58,
        activity_level=ActivityLevel.MODERATE,
        health_goals=[HealthGoal.DIABETES_CONTROL],
        dietary_restrictions=[DietaryRestriction.DIABETIC],
        blood_glucose=7.8,
        hba1c=7.2,
        blood_pressure_systolic=125,
        preferred_cuisines=["粤菜", "养生菜"]
    )

    user2 = UserProfile(
        name="李先生",
        age=35,
        gender="男",
        height=175,
        weight=72,
        activity_level=ActivityLevel.ACTIVE,
        health_goals=[HealthGoal.MUSCLE_GAIN],
        dietary_restrictions=[DietaryRestriction.NONE],
        preferred_cuisines=["川菜", "湘菜"]
    )

    # 生成报告
    print("=== 生成增强版中式营养报告 ===")

    report1 = recommender.generate_comprehensive_report_v2(user1)
    with open("/Users/williamsun/Documents/gplus/docs/FoodRecom/中式营养方案_张女士_V2.md", "w", encoding="utf-8") as f:
        f.write(report1)

    report2 = recommender.generate_comprehensive_report_v2(user2)
    with open("/Users/williamsun/Documents/gplus/docs/FoodRecom/中式营养方案_李先生_V2.md", "w", encoding="utf-8") as f:
        f.write(report2)

    print(f"✅ V2.0系统测试完成")
    print(f"📚 总菜谱数: {len(recommender.recipe_database.recipes)}道")
    print(f"📄 生成报告: 中式营养方案_张女士_V2.md, 中式营养方案_李先生_V2.md")