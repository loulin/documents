#!/usr/bin/env python3
"""
个性化饮食建议系统
基于用户体格、实验室检查、个人偏好等因素生成个性化食谱
输出markdown格式的饮食建议报告
"""

import json
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

class ActivityLevel(Enum):
    """活动水平枚举"""
    SEDENTARY = "久坐"      # 1.2
    LIGHT = "轻度活动"       # 1.375
    MODERATE = "中等活动"    # 1.55
    ACTIVE = "活跃"         # 1.725
    VERY_ACTIVE = "非常活跃"  # 1.9

class HealthGoal(Enum):
    """健康目标枚举"""
    WEIGHT_LOSS = "减重"
    WEIGHT_GAIN = "增重"
    MAINTAIN = "维持体重"
    MUSCLE_GAIN = "增肌"
    DIABETES_CONTROL = "血糖控制"
    HYPERTENSION_CONTROL = "血压控制"
    LIPID_CONTROL = "血脂控制"

class DietaryRestriction(Enum):
    """饮食限制枚举"""
    NONE = "无限制"
    VEGETARIAN = "素食"
    VEGAN = "纯素食"
    GLUTEN_FREE = "无麸质"
    LOW_SODIUM = "低钠"
    LOW_CARB = "低碳水"
    DIABETIC = "糖尿病饮食"

@dataclass
class UserProfile:
    """用户档案"""
    # 基本信息
    name: str
    age: int
    gender: str  # "男" or "女"
    height: float  # cm
    weight: float  # kg
    activity_level: ActivityLevel

    # 健康目标
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
    calories: float  # 千卡
    protein: float   # 克
    carbs: float     # 克
    fat: float       # 克
    fiber: float     # 克
    sodium: float    # 毫克
    sugar: float     # 克

@dataclass
class Food:
    """食物信息"""
    name: str
    category: str
    nutrition_per_100g: NutritionInfo
    glycemic_index: Optional[int] = None
    allergens: List[str] = None

    def __post_init__(self):
        if self.allergens is None:
            self.allergens = []

@dataclass
class Meal:
    """餐食信息"""
    name: str
    foods: List[Tuple[Food, float]]  # (食物, 重量克数)
    meal_type: str  # 早餐/午餐/晚餐/加餐

    def calculate_nutrition(self) -> NutritionInfo:
        """计算餐食总营养"""
        total_nutrition = NutritionInfo(0, 0, 0, 0, 0, 0, 0)

        for food, weight in self.foods:
            factor = weight / 100  # 转换为100g倍数
            total_nutrition.calories += food.nutrition_per_100g.calories * factor
            total_nutrition.protein += food.nutrition_per_100g.protein * factor
            total_nutrition.carbs += food.nutrition_per_100g.carbs * factor
            total_nutrition.fat += food.nutrition_per_100g.fat * factor
            total_nutrition.fiber += food.nutrition_per_100g.fiber * factor
            total_nutrition.sodium += food.nutrition_per_100g.sodium * factor
            total_nutrition.sugar += food.nutrition_per_100g.sugar * factor

        return total_nutrition

class PersonalizedFoodRecommender:
    """个性化饮食推荐系统"""

    def __init__(self):
        self.food_database = self._initialize_food_database()

    def _initialize_food_database(self) -> Dict[str, Food]:
        """初始化食物数据库"""
        foods = {
            # 主食类
            "糙米饭": Food("糙米饭", "主食", NutritionInfo(112, 2.6, 23.0, 0.9, 1.8, 5, 0.2), glycemic_index=50),
            "白米饭": Food("白米饭", "主食", NutritionInfo(130, 2.7, 28.0, 0.3, 0.4, 1, 0.1), glycemic_index=73),
            "燕麦片": Food("燕麦片", "主食", NutritionInfo(389, 16.9, 66.3, 6.9, 10.6, 2, 0.99), glycemic_index=40),
            "全麦面包": Food("全麦面包", "主食", NutritionInfo(247, 13.0, 41.0, 4.2, 7.0, 500, 6.0), glycemic_index=51),
            "荞麦面": Food("荞麦面", "主食", NutritionInfo(335, 11.7, 71.5, 1.3, 6.5, 18, 2.4), glycemic_index=45),

            # 蛋白质类
            "鸡胸肉": Food("鸡胸肉", "蛋白质", NutritionInfo(165, 31.0, 0, 3.6, 0, 74, 0)),
            "瘦牛肉": Food("瘦牛肉", "蛋白质", NutritionInfo(250, 26.0, 0, 15.0, 0, 72, 0)),
            "三文鱼": Food("三文鱼", "蛋白质", NutritionInfo(208, 20.0, 0, 13.0, 0, 59, 0)),
            "鸡蛋": Food("鸡蛋", "蛋白质", NutritionInfo(155, 13.0, 1.1, 11.0, 0, 124, 0.6)),
            "豆腐": Food("豆腐", "蛋白质", NutritionInfo(76, 8.1, 1.9, 4.8, 0.4, 7, 0.6)),
            "瘦猪肉": Food("瘦猪肉", "蛋白质", NutritionInfo(143, 20.9, 0, 6.2, 0, 48, 0)),

            # 蔬菜类
            "西兰花": Food("西兰花", "蔬菜", NutritionInfo(34, 2.8, 7.0, 0.4, 2.6, 33, 1.5), glycemic_index=15),
            "菠菜": Food("菠菜", "蔬菜", NutritionInfo(23, 2.9, 3.6, 0.4, 2.2, 79, 0.4), glycemic_index=15),
            "胡萝卜": Food("胡萝卜", "蔬菜", NutritionInfo(41, 0.9, 10.0, 0.2, 2.8, 69, 4.7), glycemic_index=47),
            "黄瓜": Food("黄瓜", "蔬菜", NutritionInfo(16, 0.7, 4.0, 0.1, 0.5, 2, 1.7), glycemic_index=15),
            "番茄": Food("番茄", "蔬菜", NutritionInfo(18, 0.9, 3.9, 0.2, 1.2, 5, 2.6), glycemic_index=10),
            "白萝卜": Food("白萝卜", "蔬菜", NutritionInfo(16, 0.9, 3.4, 0.1, 1.6, 61, 1.9), glycemic_index=25),

            # 水果类
            "苹果": Food("苹果", "水果", NutritionInfo(52, 0.3, 14.0, 0.2, 2.4, 1, 10.4), glycemic_index=36),
            "香蕉": Food("香蕉", "水果", NutritionInfo(89, 1.1, 23.0, 0.3, 2.6, 1, 12.2), glycemic_index=51),
            "橙子": Food("橙子", "水果", NutritionInfo(47, 0.9, 12.0, 0.1, 2.4, 0, 9.4), glycemic_index=45),
            "蓝莓": Food("蓝莓", "水果", NutritionInfo(57, 0.7, 14.0, 0.3, 2.4, 1, 10.0), glycemic_index=53),

            # 坚果类
            "核桃": Food("核桃", "坚果", NutritionInfo(654, 15.0, 14.0, 65.0, 6.7, 2, 2.6)),
            "杏仁": Food("杏仁", "坚果", NutritionInfo(579, 21.0, 22.0, 50.0, 12.5, 1, 4.4)),

            # 油脂类
            "橄榄油": Food("橄榄油", "油脂", NutritionInfo(884, 0, 0, 100.0, 0, 2, 0)),
            "茶籽油": Food("茶籽油", "油脂", NutritionInfo(884, 0, 0, 100.0, 0, 0, 0)),

            # 乳制品
            "脱脂牛奶": Food("脱脂牛奶", "乳制品", NutritionInfo(34, 3.4, 5.0, 0.1, 0, 52, 5.0), glycemic_index=32),
            "酸奶": Food("酸奶", "乳制品", NutritionInfo(59, 3.2, 4.5, 3.3, 0, 36, 4.7), glycemic_index=35),
        }

        return foods

    def calculate_bmr(self, user: UserProfile) -> float:
        """计算基础代谢率 (BMR) - Harris-Benedict公式"""
        if user.gender == "男":
            bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
        else:
            bmr = 447.593 + (9.247 * user.weight) + (3.098 * user.height) - (4.330 * user.age)
        return bmr

    def calculate_tdee(self, user: UserProfile) -> float:
        """计算总日能量消耗 (TDEE)"""
        bmr = self.calculate_bmr(user)
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.375,
            ActivityLevel.MODERATE: 1.55,
            ActivityLevel.ACTIVE: 1.725,
            ActivityLevel.VERY_ACTIVE: 1.9
        }
        return bmr * activity_multipliers[user.activity_level]

    def calculate_target_calories(self, user: UserProfile) -> int:
        """计算目标热量"""
        tdee = self.calculate_tdee(user)

        # 根据健康目标调整
        if HealthGoal.WEIGHT_LOSS in user.health_goals:
            return int(tdee - 500)  # 每天减少500卡路里
        elif HealthGoal.WEIGHT_GAIN in user.health_goals:
            return int(tdee + 500)  # 每天增加500卡路里
        elif HealthGoal.MUSCLE_GAIN in user.health_goals:
            return int(tdee + 300)  # 适度增加热量
        else:
            return int(tdee)

    def calculate_macros(self, user: UserProfile, target_calories: int) -> Dict[str, float]:
        """计算宏量营养素分配"""
        # 基础分配比例
        if HealthGoal.DIABETES_CONTROL in user.health_goals:
            # 糖尿病饮食：低碳水，高蛋白
            carb_ratio = 0.40
            protein_ratio = 0.25
            fat_ratio = 0.35
        elif HealthGoal.WEIGHT_LOSS in user.health_goals:
            # 减重饮食：中等碳水，高蛋白
            carb_ratio = 0.35
            protein_ratio = 0.30
            fat_ratio = 0.35
        elif HealthGoal.MUSCLE_GAIN in user.health_goals:
            # 增肌饮食：高碳水，高蛋白
            carb_ratio = 0.45
            protein_ratio = 0.30
            fat_ratio = 0.25
        else:
            # 标准分配
            carb_ratio = 0.50
            protein_ratio = 0.20
            fat_ratio = 0.30

        return {
            "carbs": (target_calories * carb_ratio) / 4,  # 1g碳水 = 4卡
            "protein": (target_calories * protein_ratio) / 4,  # 1g蛋白质 = 4卡
            "fat": (target_calories * fat_ratio) / 9,  # 1g脂肪 = 9卡
            "carb_ratio": carb_ratio,
            "protein_ratio": protein_ratio,
            "fat_ratio": fat_ratio
        }

    def filter_foods_by_restrictions(self, user: UserProfile) -> Dict[str, Food]:
        """根据饮食限制筛选食物"""
        filtered_foods = {}

        for name, food in self.food_database.items():
            # 检查过敏原
            if any(allergen in food.allergens for allergen in user.food_allergies):
                continue

            # 检查不喜欢的食物
            if name in user.disliked_foods:
                continue

            # 检查饮食限制
            skip_food = False
            for restriction in user.dietary_restrictions:
                if restriction == DietaryRestriction.VEGETARIAN:
                    if food.category == "蛋白质" and name in ["瘦牛肉", "瘦猪肉", "鸡胸肉", "三文鱼"]:
                        skip_food = True
                        break
                elif restriction == DietaryRestriction.VEGAN:
                    if food.category in ["蛋白质", "乳制品"] and name not in ["豆腐"]:
                        skip_food = True
                        break
                elif restriction == DietaryRestriction.LOW_SODIUM:
                    if food.nutrition_per_100g.sodium > 200:  # 限制高钠食物
                        skip_food = True
                        break
                elif restriction == DietaryRestriction.LOW_CARB:
                    if food.category == "主食" or food.nutrition_per_100g.carbs > 20:
                        skip_food = True
                        break

            if not skip_food:
                filtered_foods[name] = food

        return filtered_foods

    def generate_meal_plan(self, user: UserProfile) -> List[Meal]:
        """生成个性化餐食计划"""
        target_calories = self.calculate_target_calories(user)
        macros = self.calculate_macros(user, target_calories)
        available_foods = self.filter_foods_by_restrictions(user)

        # 热量分配：早餐25%，午餐35%，晚餐30%，加餐10%
        breakfast_calories = target_calories * 0.25
        lunch_calories = target_calories * 0.35
        dinner_calories = target_calories * 0.30
        snack_calories = target_calories * 0.10

        meals = []

        # 生成早餐
        breakfast = self._create_meal("早餐", breakfast_calories, macros, available_foods, user)
        meals.append(breakfast)

        # 生成午餐
        lunch = self._create_meal("午餐", lunch_calories, macros, available_foods, user)
        meals.append(lunch)

        # 生成晚餐
        dinner = self._create_meal("晚餐", dinner_calories, macros, available_foods, user)
        meals.append(dinner)

        # 生成加餐
        snack = self._create_meal("加餐", snack_calories, macros, available_foods, user)
        meals.append(snack)

        return meals

    def _create_meal(self, meal_type: str, target_calories: float, macros: Dict[str, float],
                     available_foods: Dict[str, Food], user: UserProfile) -> Meal:
        """创建单餐"""
        meal_foods = []

        if meal_type == "早餐":
            # 早餐：主食 + 蛋白质 + 少量水果
            if "燕麦片" in available_foods:
                meal_foods.append((available_foods["燕麦片"], 40))
            elif "全麦面包" in available_foods:
                meal_foods.append((available_foods["全麦面包"], 50))

            if "鸡蛋" in available_foods:
                meal_foods.append((available_foods["鸡蛋"], 60))  # 1个鸡蛋约60g
            elif "脱脂牛奶" in available_foods:
                meal_foods.append((available_foods["脱脂牛奶"], 200))

            if "苹果" in available_foods:
                meal_foods.append((available_foods["苹果"], 100))

        elif meal_type == "午餐":
            # 午餐：主食 + 蛋白质 + 蔬菜 + 少量油脂
            if "糙米饭" in available_foods:
                meal_foods.append((available_foods["糙米饭"], 80))
            elif "白米饭" in available_foods:
                meal_foods.append((available_foods["白米饭"], 70))

            if "鸡胸肉" in available_foods:
                meal_foods.append((available_foods["鸡胸肉"], 100))
            elif "瘦牛肉" in available_foods:
                meal_foods.append((available_foods["瘦牛肉"], 80))
            elif "豆腐" in available_foods:
                meal_foods.append((available_foods["豆腐"], 150))

            if "西兰花" in available_foods:
                meal_foods.append((available_foods["西兰花"], 150))
            elif "菠菜" in available_foods:
                meal_foods.append((available_foods["菠菜"], 100))

            if "橄榄油" in available_foods:
                meal_foods.append((available_foods["橄榄油"], 10))

        elif meal_type == "晚餐":
            # 晚餐：少量主食 + 蛋白质 + 大量蔬菜
            if "荞麦面" in available_foods:
                meal_foods.append((available_foods["荞麦面"], 60))
            elif "糙米饭" in available_foods:
                meal_foods.append((available_foods["糙米饭"], 60))

            if "三文鱼" in available_foods:
                meal_foods.append((available_foods["三文鱼"], 100))
            elif "瘦猪肉" in available_foods:
                meal_foods.append((available_foods["瘦猪肉"], 80))

            if "黄瓜" in available_foods:
                meal_foods.append((available_foods["黄瓜"], 100))
            if "番茄" in available_foods:
                meal_foods.append((available_foods["番茄"], 150))

        else:  # 加餐
            if "酸奶" in available_foods:
                meal_foods.append((available_foods["酸奶"], 100))
            if "核桃" in available_foods:
                meal_foods.append((available_foods["核桃"], 15))

        return Meal(f"{user.name}的{meal_type}", meal_foods, meal_type)

    def generate_health_analysis(self, user: UserProfile) -> Dict[str, str]:
        """生成健康分析"""
        analysis = {}

        # BMI分析
        bmi = user.weight / ((user.height / 100) ** 2)
        if bmi < 18.5:
            bmi_status = "偏瘦"
        elif bmi < 24:
            bmi_status = "正常"
        elif bmi < 28:
            bmi_status = "超重"
        else:
            bmi_status = "肥胖"

        analysis["BMI分析"] = f"BMI: {bmi:.1f} ({bmi_status})"

        # 血糖分析
        if user.blood_glucose:
            if user.blood_glucose < 3.9:
                glucose_status = "偏低"
            elif user.blood_glucose <= 6.1:
                glucose_status = "正常"
            elif user.blood_glucose <= 7.0:
                glucose_status = "糖耐量异常"
            else:
                glucose_status = "糖尿病范围"
            analysis["血糖分析"] = f"空腹血糖: {user.blood_glucose:.1f} mmol/L ({glucose_status})"

        # 血压分析
        if user.blood_pressure_systolic and user.blood_pressure_diastolic:
            if user.blood_pressure_systolic < 120 and user.blood_pressure_diastolic < 80:
                bp_status = "正常"
            elif user.blood_pressure_systolic < 140 or user.blood_pressure_diastolic < 90:
                bp_status = "高血压前期"
            else:
                bp_status = "高血压"
            analysis["血压分析"] = f"血压: {user.blood_pressure_systolic}/{user.blood_pressure_diastolic} mmHg ({bp_status})"

        return analysis

    def generate_markdown_report(self, user: UserProfile) -> str:
        """生成markdown格式的个性化饮食报告"""
        target_calories = self.calculate_target_calories(user)
        macros = self.calculate_macros(user, target_calories)
        meal_plan = self.generate_meal_plan(user)
        health_analysis = self.generate_health_analysis(user)

        # 生成报告
        report = f"""# {user.name} 个性化饮食建议报告

## 基本信息
- **姓名**: {user.name}
- **年龄**: {user.age}岁
- **性别**: {user.gender}
- **身高**: {user.height} cm
- **体重**: {user.weight} kg
- **活动水平**: {user.activity_level.value}

## 健康分析
"""

        for key, value in health_analysis.items():
            report += f"- **{key}**: {value}\n"

        report += f"""
## 健康目标
{', '.join([goal.value for goal in user.health_goals])}

## 饮食限制
{', '.join([restriction.value for restriction in user.dietary_restrictions]) if user.dietary_restrictions else '无特殊限制'}

## 营养目标

### 每日热量需求
- **基础代谢率**: {self.calculate_bmr(user):.0f} 千卡
- **总日消耗**: {self.calculate_tdee(user):.0f} 千卡
- **目标摄入**: {target_calories} 千卡

### 宏量营养素分配
- **碳水化合物**: {macros['carbs']:.0f}克 ({macros['carb_ratio']*100:.0f}%)
- **蛋白质**: {macros['protein']:.0f}克 ({macros['protein_ratio']*100:.0f}%)
- **脂肪**: {macros['fat']:.0f}克 ({macros['fat_ratio']*100:.0f}%)

## 个性化食谱

"""

        # 添加每餐详情
        total_nutrition = NutritionInfo(0, 0, 0, 0, 0, 0, 0)

        for meal in meal_plan:
            meal_nutrition = meal.calculate_nutrition()
            total_nutrition.calories += meal_nutrition.calories
            total_nutrition.protein += meal_nutrition.protein
            total_nutrition.carbs += meal_nutrition.carbs
            total_nutrition.fat += meal_nutrition.fat
            total_nutrition.fiber += meal_nutrition.fiber
            total_nutrition.sodium += meal_nutrition.sodium
            total_nutrition.sugar += meal_nutrition.sugar

            report += f"### {meal.meal_type}\n\n"
            report += "| 食物 | 重量 | 热量 | 蛋白质 | 碳水 | 脂肪 |\n"
            report += "|------|------|------|--------|------|------|\n"

            for food, weight in meal.foods:
                factor = weight / 100
                calories = food.nutrition_per_100g.calories * factor
                protein = food.nutrition_per_100g.protein * factor
                carbs = food.nutrition_per_100g.carbs * factor
                fat = food.nutrition_per_100g.fat * factor

                report += f"| {food.name} | {weight}g | {calories:.0f}千卡 | {protein:.1f}g | {carbs:.1f}g | {fat:.1f}g |\n"

            report += f"\n**{meal.meal_type}营养合计**: {meal_nutrition.calories:.0f}千卡, 蛋白质{meal_nutrition.protein:.1f}g, 碳水{meal_nutrition.carbs:.1f}g, 脂肪{meal_nutrition.fat:.1f}g\n\n"

        # 添加营养总结
        report += f"""## 全天营养总结

| 营养素 | 实际摄入 | 目标摄入 | 达成率 |
|--------|----------|----------|--------|
| 热量 | {total_nutrition.calories:.0f}千卡 | {target_calories}千卡 | {total_nutrition.calories/target_calories*100:.1f}% |
| 蛋白质 | {total_nutrition.protein:.1f}g | {macros['protein']:.0f}g | {total_nutrition.protein/macros['protein']*100:.1f}% |
| 碳水化合物 | {total_nutrition.carbs:.1f}g | {macros['carbs']:.0f}g | {total_nutrition.carbs/macros['carbs']*100:.1f}% |
| 脂肪 | {total_nutrition.fat:.1f}g | {macros['fat']:.0f}g | {total_nutrition.fat/macros['fat']*100:.1f}% |
| 膳食纤维 | {total_nutrition.fiber:.1f}g | 25-35g | {'✓' if total_nutrition.fiber >= 25 else '需增加'} |
| 钠 | {total_nutrition.sodium:.0f}mg | <2300mg | {'✓' if total_nutrition.sodium < 2300 else '超标'} |

## 饮食建议

### 🍽️ 用餐建议
1. **定时定量**: 三餐时间固定，避免暴饮暴食
2. **细嚼慢咽**: 每餐用时20-30分钟，充分咀嚼
3. **先菜后饭**: 先吃蔬菜，再吃蛋白质，最后吃主食
4. **适量饮水**: 每日1500-2000ml，餐前半小时饮水

### 🥗 食物选择
1. **优质蛋白**: 瘦肉、鱼类、蛋类、豆制品
2. **复合碳水**: 全谷物、薯类、豆类
3. **健康脂肪**: 坚果、橄榄油、深海鱼
4. **丰富蔬果**: 深色蔬菜、低糖水果

### ⚠️ 注意事项
"""

        # 根据健康目标添加特殊建议
        if HealthGoal.DIABETES_CONTROL in user.health_goals:
            report += "- **血糖控制**: 选择低升糖指数食物，餐后适量运动\n"
        if HealthGoal.WEIGHT_LOSS in user.health_goals:
            report += "- **减重建议**: 控制总热量，增加蛋白质摄入，多吃高纤维食物\n"
        if HealthGoal.HYPERTENSION_CONTROL in user.health_goals:
            report += "- **血压控制**: 限制钠盐摄入(<2300mg/天)，多吃富含钾的食物\n"
        if HealthGoal.LIPID_CONTROL in user.health_goals:
            report += "- **血脂控制**: 限制饱和脂肪，增加不饱和脂肪，多吃富含纤维的食物\n"

        report += f"""
---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*本报告仅供参考，具体饮食方案请咨询专业营养师*
"""

        return report

def main():
    """主函数 - 示例用法"""

    # 创建推荐系统
    recommender = PersonalizedFoodRecommender()

    # 示例用户1：糖尿病患者
    user1 = UserProfile(
        name="张先生",
        age=45,
        gender="男",
        height=175,
        weight=75,
        activity_level=ActivityLevel.LIGHT,
        health_goals=[HealthGoal.DIABETES_CONTROL, HealthGoal.WEIGHT_LOSS],
        dietary_restrictions=[DietaryRestriction.DIABETIC],
        blood_glucose=8.5,
        hba1c=7.8,
        blood_pressure_systolic=130,
        blood_pressure_diastolic=85,
        preferred_cuisines=["中餐", "清淡菜"],
        disliked_foods=["内脏"],
        food_allergies=[]
    )

    # 生成报告
    report1 = recommender.generate_markdown_report(user1)

    # 保存报告
    with open("/Users/williamsun/Documents/gplus/docs/FoodRecom/糖尿病患者饮食建议_张先生.md", "w", encoding="utf-8") as f:
        f.write(report1)

    # 示例用户2：减重人群
    user2 = UserProfile(
        name="李女士",
        age=32,
        gender="女",
        height=160,
        weight=68,
        activity_level=ActivityLevel.MODERATE,
        health_goals=[HealthGoal.WEIGHT_LOSS],
        dietary_restrictions=[DietaryRestriction.NONE],
        blood_pressure_systolic=115,
        blood_pressure_diastolic=75,
        preferred_cuisines=["轻食", "健康餐"],
        disliked_foods=["肥肉"],
        food_allergies=["花生"]
    )

    report2 = recommender.generate_markdown_report(user2)

    with open("/Users/williamsun/Documents/gplus/docs/FoodRecom/减重饮食建议_李女士.md", "w", encoding="utf-8") as f:
        f.write(report2)

    print("✅ 个性化饮食建议报告生成完成")
    print("📁 报告保存位置: docs/FoodRecom/")

if __name__ == "__main__":
    main()