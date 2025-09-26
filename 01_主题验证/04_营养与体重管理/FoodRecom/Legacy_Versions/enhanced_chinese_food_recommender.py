#!/usr/bin/env python3
"""
中国本土化个性化饮食建议系统 (增强版)
基于《中国居民膳食指南(2022)》和美国营养学会疾病营养指南
结合中式菜谱和烹饪方式，生成专业的个性化饮食建议
"""

import json
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

class DiseaseType(Enum):
    """疾病类型枚举"""
    HEALTHY = "健康人群"
    TYPE2_DIABETES = "2型糖尿病"
    HYPERTENSION = "高血压"
    DYSLIPIDEMIA = "血脂异常"
    METABOLIC_SYNDROME = "代谢综合征"
    CHRONIC_KIDNEY_DISEASE = "慢性肾病"
    CARDIOVASCULAR_DISEASE = "心血管疾病"
    OBESITY = "肥胖症"

class CookingMethod(Enum):
    """烹饪方式枚举"""
    STEAMING = "蒸"
    BOILING = "煮"
    BRAISING = "焖"
    STEWING = "炖"
    STIR_FRYING = "炒"
    BLANCHING = "焯"
    COLD_MIXING = "凉拌"
    GRILLING = "烤"

@dataclass
class ChineseDietaryGuidelines:
    """中国居民膳食指南推荐量"""
    # 基于《中国居民膳食指南(2022)》

    # 每日推荐摄入量 (成年人)
    grains: Tuple[int, int] = (200, 300)  # 谷薯类 (g/天)
    vegetables: Tuple[int, int] = (300, 500)  # 蔬菜类 (g/天)
    fruits: Tuple[int, int] = (200, 350)  # 水果类 (g/天)
    livestock_poultry: Tuple[int, int] = (40, 75)  # 畜禽肉类 (g/天)
    aquatic_products: Tuple[int, int] = (40, 75)  # 水产品 (g/天)
    eggs: Tuple[int, int] = (40, 50)  # 蛋类 (g/天)
    dairy: Tuple[int, int] = (300, 500)  # 奶及奶制品 (g/天)
    soybeans_nuts: Tuple[int, int] = (25, 35)  # 大豆和坚果 (g/天)
    cooking_oil: Tuple[int, int] = (25, 30)  # 烹调油 (g/天)
    salt: int = 5  # 食盐 (g/天，最大值)

@dataclass
class AmericanNutritionGuidelines:
    """美国营养学会疾病营养指导"""
    # 基于ADA, AHA, AACE等组织指南

    diabetes_carb_range: Tuple[float, float] = (0.40, 0.50)  # 糖尿病碳水占比
    diabetes_protein_range: Tuple[float, float] = (0.15, 0.25)  # 糖尿病蛋白质占比
    diabetes_fat_range: Tuple[float, float] = (0.25, 0.40)  # 糖尿病脂肪占比

    hypertension_sodium_limit: int = 1500  # 高血压钠限制 (mg/天)
    hypertension_potassium_target: int = 3500  # 高血压钾目标 (mg/天)

    dyslipidemia_saturated_fat_limit: float = 0.07  # 血脂异常饱和脂肪限制
    dyslipidemia_fiber_target: int = 35  # 血脂异常纤维目标 (g/天)

@dataclass
class ChineseFood:
    """中式食物信息"""
    name: str
    category: str
    subcategory: str  # 细分类别
    nutrition_per_100g: 'NutritionInfo'
    glycemic_index: Optional[int] = None
    sodium_per_100g: float = 0  # 钠含量 (mg)
    potassium_per_100g: float = 0  # 钾含量 (mg)
    saturated_fat_per_100g: float = 0  # 饱和脂肪 (g)
    preferred_cooking: List[CookingMethod] = None
    regional_cuisine: List[str] = None  # 地方菜系
    allergens: List[str] = None

    def __post_init__(self):
        if self.preferred_cooking is None:
            self.preferred_cooking = []
        if self.regional_cuisine is None:
            self.regional_cuisine = []
        if self.allergens is None:
            self.allergens = []

@dataclass
class ChineseDish:
    """中式菜肴"""
    name: str
    cuisine_type: str  # 菜系 (川菜、粤菜、鲁菜等)
    cooking_method: CookingMethod
    ingredients: List[Tuple[ChineseFood, float]]  # (食材, 重量)
    cooking_oil_amount: float = 10  # 烹调油用量 (g)
    salt_amount: float = 2  # 食盐用量 (g)
    difficulty: str = "简单"  # 烹饪难度
    cooking_time: int = 20  # 制作时间 (分钟)
    description: str = ""  # 制作说明

class EnhancedChineseFoodRecommender:
    """增强版中国本土化饮食推荐系统"""

    def __init__(self):
        self.chinese_guidelines = ChineseDietaryGuidelines()
        self.american_guidelines = AmericanNutritionGuidelines()
        self.food_database = self._initialize_chinese_food_database()
        self.dish_database = self._initialize_chinese_dish_database()
        self.disease_nutrition_protocols = self._initialize_disease_protocols()

    def _initialize_chinese_food_database(self) -> Dict[str, ChineseFood]:
        """初始化中式食物数据库"""
        foods = {
            # 谷薯类
            "大米": ChineseFood("大米", "谷薯类", "精制谷物",
                             NutritionInfo(346, 7.4, 77.9, 0.8, 0.7, 2.5, 0.7),
                             glycemic_index=83, sodium_per_100g=5, potassium_per_100g=103),
            "糙米": ChineseFood("糙米", "谷薯类", "全谷物",
                             NutritionInfo(348, 7.7, 77.0, 2.7, 4.7, 1.2, 0.5),
                             glycemic_index=47, sodium_per_100g=5, potassium_per_100g=223),
            "小米": ChineseFood("小米", "谷薯类", "全谷物",
                             NutritionInfo(358, 9.0, 75.1, 3.1, 1.6, 0.4, 0.6),
                             glycemic_index=71, sodium_per_100g=4, potassium_per_100g=284),
            "燕麦": ChineseFood("燕麦", "谷薯类", "全谷物",
                             NutritionInfo(338, 15.0, 61.0, 7.0, 5.0, 1.0, 1.2),
                             glycemic_index=40, sodium_per_100g=6, potassium_per_100g=214),
            "荞麦": ChineseFood("荞麦", "谷薯类", "全谷物",
                             NutritionInfo(324, 9.3, 71.5, 2.1, 17.6, 0.1, 0.4),
                             glycemic_index=45, sodium_per_100g=18, potassium_per_100g=401),
            "红薯": ChineseFood("红薯", "谷薯类", "薯类",
                             NutritionInfo(99, 1.1, 24.7, 0.1, 1.6, 16.8, 0.2),
                             glycemic_index=54, sodium_per_100g=28, potassium_per_100g=130),
            "紫薯": ChineseFood("紫薯", "谷薯类", "薯类",
                             NutritionInfo(82, 1.3, 20.1, 0.2, 1.4, 14.5, 0.1),
                             glycemic_index=47, sodium_per_100g=23, potassium_per_100g=271),

            # 蔬菜类 - 叶菜类
            "小白菜": ChineseFood("小白菜", "蔬菜类", "叶菜类",
                               NutritionInfo(15, 1.5, 3.0, 0.3, 1.1, 0.9, 0.1),
                               glycemic_index=15, sodium_per_100g=73, potassium_per_100g=178,
                               preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.BLANCHING]),
            "菠菜": ChineseFood("菠菜", "蔬菜类", "叶菜类",
                             NutritionInfo(24, 2.6, 4.5, 0.3, 1.7, 0.4, 0.1),
                             glycemic_index=15, sodium_per_100g=85, potassium_per_100g=311,
                             preferred_cooking=[CookingMethod.BLANCHING, CookingMethod.STIR_FRYING]),
            "韭菜": ChineseFood("韭菜", "蔬菜类", "叶菜类",
                             NutritionInfo(22, 2.4, 4.6, 0.4, 1.4, 0.8, 0.1),
                             glycemic_index=15, sodium_per_100g=5, potassium_per_100g=247,
                             preferred_cooking=[CookingMethod.STIR_FRYING]),
            "芹菜": ChineseFood("芹菜", "蔬菜类", "叶菜类",
                             NutritionInfo(20, 2.2, 4.6, 0.3, 1.4, 1.8, 0.1),
                             glycemic_index=15, sodium_per_100g=159, potassium_per_100g=154,
                             preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.COLD_MIXING]),

            # 蔬菜类 - 瓜茄类
            "黄瓜": ChineseFood("黄瓜", "蔬菜类", "瓜茄类",
                             NutritionInfo(15, 0.8, 3.6, 0.2, 0.9, 1.5, 0.0),
                             glycemic_index=15, sodium_per_100g=4, potassium_per_100g=102,
                             preferred_cooking=[CookingMethod.COLD_MIXING, CookingMethod.STIR_FRYING]),
            "番茄": ChineseFood("番茄", "蔬菜类", "瓜茄类",
                             NutritionInfo(15, 0.9, 3.3, 0.2, 0.5, 2.5, 0.0),
                             glycemic_index=15, sodium_per_100g=5, potassium_per_100g=179,
                             preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.STEWING]),
            "茄子": ChineseFood("茄子", "蔬菜类", "瓜茄类",
                             NutritionInfo(23, 1.1, 5.1, 0.2, 1.3, 2.5, 0.0),
                             glycemic_index=15, sodium_per_100g=1, potassium_per_100g=142,
                             preferred_cooking=[CookingMethod.BRAISING, CookingMethod.STEAMING]),
            "冬瓜": ChineseFood("冬瓜", "蔬菜类", "瓜茄类",
                             NutritionInfo(12, 0.4, 2.9, 0.2, 0.7, 1.8, 0.0),
                             glycemic_index=15, sodium_per_100g=1, potassium_per_100g=78,
                             preferred_cooking=[CookingMethod.STEWING, CookingMethod.BRAISING]),

            # 蔬菜类 - 根茎类
            "胡萝卜": ChineseFood("胡萝卜", "蔬菜类", "根茎类",
                               NutritionInfo(25, 1.0, 6.0, 0.2, 3.2, 4.0, 0.0),
                               glycemic_index=47, sodium_per_100g=25, potassium_per_100g=119,
                               preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.STEWING]),
            "白萝卜": ChineseFood("白萝卜", "蔬菜类", "根茎类",
                               NutritionInfo(16, 0.9, 4.0, 0.1, 1.0, 2.6, 0.0),
                               glycemic_index=25, sodium_per_100g=61, potassium_per_100g=173,
                               preferred_cooking=[CookingMethod.STEWING, CookingMethod.COLD_MIXING]),
            "莲藕": ChineseFood("莲藕", "蔬菜类", "根茎类",
                             NutritionInfo(73, 2.0, 16.4, 0.2, 2.2, 0.5, 0.0),
                             glycemic_index=38, sodium_per_100g=5, potassium_per_100g=243,
                             preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.BRAISING]),

            # 蔬菜类 - 十字花科
            "大白菜": ChineseFood("大白菜", "蔬菜类", "十字花科",
                               NutritionInfo(17, 1.5, 3.6, 0.3, 1.1, 1.5, 0.1),
                               glycemic_index=15, sodium_per_100g=57, potassium_per_100g=130,
                               preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.STEWING]),
            "西兰花": ChineseFood("西兰花", "蔬菜类", "十字花科",
                               NutritionInfo(36, 4.1, 7.1, 0.6, 1.6, 1.5, 0.1),
                               glycemic_index=15, sodium_per_100g=18, potassium_per_100g=17,
                               preferred_cooking=[CookingMethod.BLANCHING, CookingMethod.STIR_FRYING]),
            "花菜": ChineseFood("花菜", "蔬菜类", "十字花科",
                             NutritionInfo(24, 2.0, 4.9, 0.2, 1.2, 2.1, 0.0),
                             glycemic_index=15, sodium_per_100g=31, potassium_per_100g=200,
                             preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.BLANCHING]),

            # 畜禽肉类
            "瘦猪肉": ChineseFood("瘦猪肉", "畜禽肉类", "猪肉",
                               NutritionInfo(143, 20.3, 1.0, 6.2, 0.0, 0.0, 2.4),
                               sodium_per_100g=65, potassium_per_100g=305, saturated_fat_per_100g=2.4,
                               preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.BRAISING]),
            "瘦牛肉": ChineseFood("瘦牛肉", "畜禽肉类", "牛肉",
                               NutritionInfo(125, 19.9, 2.0, 4.2, 0.0, 0.0, 1.6),
                               sodium_per_100g=84, potassium_per_100g=284, saturated_fat_per_100g=1.6,
                               preferred_cooking=[CookingMethod.BRAISING, CookingMethod.STIR_FRYING]),
            "鸡胸肉": ChineseFood("鸡胸肉", "畜禽肉类", "鸡肉",
                               NutritionInfo(133, 19.4, 2.5, 5.0, 0.0, 0.0, 1.4),
                               sodium_per_100g=63, potassium_per_100g=251, saturated_fat_per_100g=1.4,
                               preferred_cooking=[CookingMethod.STEAMING, CookingMethod.STIR_FRYING]),

            # 水产品类
            "草鱼": ChineseFood("草鱼", "水产品类", "淡水鱼",
                             NutritionInfo(113, 16.6, 0.0, 5.2, 0.0, 0.0, 1.4),
                             sodium_per_100g=54, potassium_per_100g=312, saturated_fat_per_100g=1.4,
                             preferred_cooking=[CookingMethod.STEAMING, CookingMethod.BRAISING]),
            "鲫鱼": ChineseFood("鲫鱼", "水产品类", "淡水鱼",
                             NutritionInfo(108, 17.1, 0.0, 2.7, 0.0, 0.0, 0.7),
                             sodium_per_100g=41, potassium_per_100g=290, saturated_fat_per_100g=0.7,
                             preferred_cooking=[CookingMethod.STEWING, CookingMethod.STEAMING]),
            "带鱼": ChineseFood("带鱼", "水产品类", "海水鱼",
                             NutritionInfo(127, 17.7, 0.0, 5.6, 0.0, 0.0, 1.4),
                             sodium_per_100g=150, potassium_per_100g=280, saturated_fat_per_100g=1.4,
                             preferred_cooking=[CookingMethod.BRAISING, CookingMethod.STEAMING]),
            "虾": ChineseFood("虾", "水产品类", "甲壳类",
                           NutritionInfo(87, 16.4, 2.0, 1.2, 0.0, 0.0, 0.3),
                           sodium_per_100g=165, potassium_per_100g=215, saturated_fat_per_100g=0.3,
                           preferred_cooking=[CookingMethod.STIR_FRYING, CookingMethod.STEAMING]),

            # 蛋类
            "鸡蛋": ChineseFood("鸡蛋", "蛋类", "鸡蛋",
                             NutritionInfo(144, 13.3, 2.8, 8.8, 0.0, 0.2, 2.7),
                             sodium_per_100g=131, potassium_per_100g=154, saturated_fat_per_100g=2.7,
                             preferred_cooking=[CookingMethod.BOILING, CookingMethod.STEAMING]),

            # 奶类
            "牛奶": ChineseFood("牛奶", "奶类", "液态奶",
                             NutritionInfo(54, 3.0, 3.4, 3.2, 0.0, 3.4, 2.1),
                             sodium_per_100g=37, potassium_per_100g=109, saturated_fat_per_100g=2.1),
            "酸奶": ChineseFood("酸奶", "奶类", "发酵奶",
                             NutritionInfo(72, 2.5, 9.3, 2.7, 0.0, 7.4, 1.8),
                             sodium_per_100g=39, potassium_per_100g=150, saturated_fat_per_100g=1.8),

            # 大豆坚果类
            "黄豆": ChineseFood("黄豆", "大豆坚果类", "大豆",
                             NutritionInfo(359, 35.0, 34.2, 16.0, 15.5, 11.9, 2.4),
                             sodium_per_100g=2, potassium_per_100g=1503, saturated_fat_per_100g=2.4),
            "豆腐": ChineseFood("豆腐", "大豆坚果类", "豆制品",
                             NutritionInfo(81, 8.1, 4.2, 3.7, 0.4, 1.2, 0.5),
                             sodium_per_100g=7, potassium_per_100g=125, saturated_fat_per_100g=0.5,
                             preferred_cooking=[CookingMethod.STEAMING, CookingMethod.BRAISING]),
            "核桃": ChineseFood("核桃", "大豆坚果类", "坚果",
                             NutritionInfo(646, 15.4, 19.1, 58.8, 9.5, 3.2, 5.6),
                             sodium_per_100g=6, potassium_per_100g=385, saturated_fat_per_100g=5.6),
            "花生": ChineseFood("花生", "大豆坚果类", "坚果",
                             NutritionInfo(313, 21.7, 23.8, 25.4, 6.3, 5.7, 5.3),
                             sodium_per_100g=34, potassium_per_100g=563, saturated_fat_per_100g=5.3),

            # 水果类
            "苹果": ChineseFood("苹果", "水果类", "仁果类",
                             NutritionInfo(54, 0.2, 13.5, 0.2, 1.2, 10.3, 0.1),
                             glycemic_index=36, sodium_per_100g=1, potassium_per_100g=119),
            "香蕉": ChineseFood("香蕉", "水果类", "热带水果",
                             NutritionInfo(91, 1.4, 22.0, 0.2, 1.2, 12.2, 0.1),
                             glycemic_index=52, sodium_per_100g=1, potassium_per_100g=256),
            "橙子": ChineseFood("橙子", "水果类", "柑橘类",
                             NutritionInfo(48, 0.8, 12.1, 0.2, 1.4, 9.0, 0.0),
                             glycemic_index=45, sodium_per_100g=1, potassium_per_100g=154),
            "梨": ChineseFood("梨", "水果类", "仁果类",
                           NutritionInfo(51, 0.1, 13.3, 0.1, 3.1, 8.8, 0.0),
                           glycemic_index=38, sodium_per_100g=2, potassium_per_100g=92),

            # 调料类
            "生姜": ChineseFood("生姜", "调料类", "香辛料",
                             NutritionInfo(19, 1.3, 4.0, 0.3, 2.7, 0.8, 0.1),
                             sodium_per_100g=27, potassium_per_100g=295),
            "大蒜": ChineseFood("大蒜", "调料类", "香辛料",
                             NutritionInfo(126, 4.5, 27.6, 0.2, 1.1, 0.5, 0.1),
                             sodium_per_100g=5, potassium_per_100g=302),
        }

        return foods

    def _initialize_chinese_dish_database(self) -> Dict[str, ChineseDish]:
        """初始化中式菜肴数据库"""
        dishes = {}

        # 家常菜
        dishes["蒸蛋羹"] = ChineseDish(
            name="蒸蛋羹",
            cuisine_type="家常菜",
            cooking_method=CookingMethod.STEAMING,
            ingredients=[
                (self.food_database["鸡蛋"], 100),
                (self.food_database["牛奶"], 50)
            ],
            cooking_oil_amount=2,
            salt_amount=1,
            difficulty="简单",
            cooking_time=15,
            description="鸡蛋打散，加入牛奶和少量盐，蒸10-15分钟至凝固"
        )

        dishes["清炒小白菜"] = ChineseDish(
            name="清炒小白菜",
            cuisine_type="家常菜",
            cooking_method=CookingMethod.STIR_FRYING,
            ingredients=[
                (self.food_database["小白菜"], 200),
                (self.food_database["大蒜"], 5)
            ],
            cooking_oil_amount=8,
            salt_amount=2,
            difficulty="简单",
            cooking_time=5,
            description="蒜爆锅，下小白菜大火快炒，调味即可"
        )

        dishes["清蒸鲫鱼"] = ChineseDish(
            name="清蒸鲫鱼",
            cuisine_type="粤菜",
            cooking_method=CookingMethod.STEAMING,
            ingredients=[
                (self.food_database["鲫鱼"], 300),
                (self.food_database["生姜"], 10)
            ],
            cooking_oil_amount=5,
            salt_amount=2,
            difficulty="中等",
            cooking_time=20,
            description="鲫鱼洗净，姜丝摆放，蒸15-20分钟，浇蒸鱼豉油"
        )

        return dishes

    def _initialize_disease_protocols(self) -> Dict[DiseaseType, Dict]:
        """初始化疾病营养方案"""
        protocols = {}

        # 2型糖尿病营养方案 (基于ADA 2023指南)
        protocols[DiseaseType.TYPE2_DIABETES] = {
            "carb_percentage": (0.40, 0.50),  # 碳水化合物40-50%
            "protein_percentage": (0.15, 0.25),  # 蛋白质15-25%
            "fat_percentage": (0.25, 0.40),  # 脂肪25-40%
            "fiber_target": 35,  # 纤维素35g/天
            "sodium_limit": 2300,  # 钠限制2300mg/天
            "glycemic_index_preference": "low",  # 优选低GI食物
            "meal_distribution": (0.20, 0.30, 0.30, 0.20),  # 早午晚加餐热量分配
            "specific_recommendations": [
                "选择低升糖指数的主食",
                "增加膳食纤维摄入",
                "控制单次进餐碳水化合物含量",
                "定时定量进餐",
                "监测餐后血糖"
            ]
        }

        # 高血压营养方案 (基于DASH饮食)
        protocols[DiseaseType.HYPERTENSION] = {
            "carb_percentage": (0.50, 0.60),
            "protein_percentage": (0.15, 0.20),
            "fat_percentage": (0.25, 0.30),
            "sodium_limit": 1500,  # 钠限制1500mg/天
            "potassium_target": 3500,  # 钾目标3500mg/天
            "calcium_target": 1200,  # 钙目标1200mg/天
            "magnesium_target": 500,  # 镁目标500mg/天
            "specific_recommendations": [
                "严格限制钠盐摄入",
                "增加富含钾的食物",
                "多吃深色蔬菜和水果",
                "选择低脂乳制品",
                "限制饱和脂肪摄入"
            ]
        }

        # 血脂异常营养方案 (基于ATP III指南)
        protocols[DiseaseType.DYSLIPIDEMIA] = {
            "carb_percentage": (0.50, 0.60),
            "protein_percentage": (0.15, 0.20),
            "fat_percentage": (0.25, 0.30),
            "saturated_fat_limit": 0.07,  # 饱和脂肪<7%
            "cholesterol_limit": 200,  # 胆固醇<200mg/天
            "fiber_target": 35,  # 纤维素35g/天
            "omega3_target": 2,  # ω-3脂肪酸2g/天
            "specific_recommendations": [
                "限制饱和脂肪和反式脂肪",
                "增加不饱和脂肪摄入",
                "多吃富含水溶性纤维的食物",
                "适量摄入植物甾醇",
                "选择深海鱼类"
            ]
        }

        return protocols

    def analyze_disease_risk(self, user: 'UserProfile') -> List[DiseaseType]:
        """基于用户指标分析疾病风险"""
        diseases = []

        # BMI计算
        bmi = user.weight / ((user.height / 100) ** 2)

        # 糖尿病风险
        if (user.blood_glucose and user.blood_glucose >= 7.0) or \
           (user.hba1c and user.hba1c >= 6.5):
            diseases.append(DiseaseType.TYPE2_DIABETES)

        # 高血压风险
        if (user.blood_pressure_systolic and user.blood_pressure_systolic >= 140) or \
           (user.blood_pressure_diastolic and user.blood_pressure_diastolic >= 90):
            diseases.append(DiseaseType.HYPERTENSION)

        # 血脂异常风险
        if (user.cholesterol_total and user.cholesterol_total >= 6.2) or \
           (user.cholesterol_ldl and user.cholesterol_ldl >= 4.1) or \
           (user.triglycerides and user.triglycerides >= 2.3):
            diseases.append(DiseaseType.DYSLIPIDEMIA)

        # 肥胖症
        if bmi >= 28:
            diseases.append(DiseaseType.OBESITY)

        # 代谢综合征 (需满足多个条件)
        metabolic_criteria = 0
        if bmi >= 25: metabolic_criteria += 1
        if user.blood_glucose and user.blood_glucose >= 6.1: metabolic_criteria += 1
        if user.blood_pressure_systolic and user.blood_pressure_systolic >= 130: metabolic_criteria += 1
        if user.triglycerides and user.triglycerides >= 1.7: metabolic_criteria += 1

        if metabolic_criteria >= 3:
            diseases.append(DiseaseType.METABOLIC_SYNDROME)

        return diseases if diseases else [DiseaseType.HEALTHY]

    def calculate_chinese_dietary_targets(self, user: 'UserProfile', diseases: List[DiseaseType]) -> Dict:
        """基于中国膳食指南计算个性化目标"""
        targets = {}

        # 基础热量需求
        bmr = self.calculate_bmr(user)
        tdee = self.calculate_tdee(user)

        # 根据疾病调整热量
        if DiseaseType.OBESITY in diseases or DiseaseType.TYPE2_DIABETES in diseases:
            target_calories = int(tdee - 500)  # 减重
        elif user.weight / ((user.height / 100) ** 2) < 18.5:
            target_calories = int(tdee + 300)  # 增重
        else:
            target_calories = int(tdee)

        # 根据疾病确定营养素分配
        primary_disease = diseases[0] if diseases else DiseaseType.HEALTHY

        if primary_disease in self.disease_nutrition_protocols:
            protocol = self.disease_nutrition_protocols[primary_disease]
            carb_range = protocol["carb_percentage"]
            protein_range = protocol["protein_percentage"]
            fat_range = protocol["fat_percentage"]

            # 选择范围中值
            carb_ratio = (carb_range[0] + carb_range[1]) / 2
            protein_ratio = (protein_range[0] + protein_range[1]) / 2
            fat_ratio = (fat_range[0] + fat_range[1]) / 2
        else:
            # 健康人群使用中国膳食指南推荐
            carb_ratio = 0.55
            protein_ratio = 0.15
            fat_ratio = 0.30

        targets.update({
            "target_calories": target_calories,
            "carb_grams": target_calories * carb_ratio / 4,
            "protein_grams": target_calories * protein_ratio / 4,
            "fat_grams": target_calories * fat_ratio / 9,
            "carb_ratio": carb_ratio,
            "protein_ratio": protein_ratio,
            "fat_ratio": fat_ratio
        })

        # 中国膳食指南推荐量调整
        guidelines = self.chinese_guidelines

        # 根据疾病调整推荐量
        if primary_disease == DiseaseType.TYPE2_DIABETES:
            targets["grains_target"] = guidelines.grains[0]  # 选择下限
            targets["vegetables_target"] = guidelines.vegetables[1]  # 选择上限
            targets["fruits_target"] = guidelines.fruits[0]  # 选择下限
        elif primary_disease == DiseaseType.HYPERTENSION:
            targets["vegetables_target"] = guidelines.vegetables[1]  # 增加蔬菜
            targets["dairy_target"] = guidelines.dairy[1]  # 增加奶类
        else:
            targets["grains_target"] = sum(guidelines.grains) / 2
            targets["vegetables_target"] = sum(guidelines.vegetables) / 2
            targets["fruits_target"] = sum(guidelines.fruits) / 2

        return targets

    def generate_chinese_meal_plan(self, user: 'UserProfile', diseases: List[DiseaseType]) -> List:
        """生成中式营养餐谱"""
        targets = self.calculate_chinese_dietary_targets(user, diseases)
        primary_disease = diseases[0] if diseases else DiseaseType.HEALTHY

        # 热量分配 (根据中国人饮食习惯)
        if primary_disease == DiseaseType.TYPE2_DIABETES:
            # 糖尿病患者：少量多餐
            meal_distribution = (0.20, 0.30, 0.25, 0.15, 0.10)  # 早午晚上下午加餐
        else:
            meal_distribution = (0.25, 0.35, 0.30, 0.10)  # 早午晚加餐

        meals = []
        total_calories = targets["target_calories"]

        # 生成早餐
        breakfast_calories = total_calories * meal_distribution[0]
        breakfast = self._create_chinese_breakfast(breakfast_calories, primary_disease, user)
        meals.append(breakfast)

        # 生成午餐
        lunch_calories = total_calories * meal_distribution[1]
        lunch = self._create_chinese_lunch(lunch_calories, primary_disease, user)
        meals.append(lunch)

        # 生成晚餐
        dinner_calories = total_calories * meal_distribution[2]
        dinner = self._create_chinese_dinner(dinner_calories, primary_disease, user)
        meals.append(dinner)

        # 生成加餐
        snack_calories = total_calories * meal_distribution[3]
        snack = self._create_chinese_snack(snack_calories, primary_disease, user)
        meals.append(snack)

        return meals

    def _create_chinese_breakfast(self, calories: float, disease: DiseaseType, user: 'UserProfile') -> Dict:
        """创建中式早餐"""
        breakfast = {
            "meal_name": "早餐",
            "target_calories": calories,
            "dishes": [],
            "cooking_suggestions": []
        }

        if disease == DiseaseType.TYPE2_DIABETES:
            # 糖尿病早餐：低GI主食 + 优质蛋白 + 蔬菜
            breakfast["dishes"] = [
                {
                    "dish_name": "燕麦小米粥",
                    "ingredients": [
                        {"food": "燕麦", "amount": 30, "unit": "克"},
                        {"food": "小米", "amount": 20, "unit": "克"}
                    ],
                    "cooking_method": "煮",
                    "cooking_time": "30分钟",
                    "nutrition_highlight": "低升糖指数，富含β-葡聚糖"
                },
                {
                    "dish_name": "蒸蛋羹",
                    "ingredients": [
                        {"food": "鸡蛋", "amount": 60, "unit": "克"},
                        {"food": "牛奶", "amount": 50, "unit": "毫升"}
                    ],
                    "cooking_method": "蒸",
                    "cooking_time": "15分钟",
                    "nutrition_highlight": "优质蛋白，易消化"
                },
                {
                    "dish_name": "凉拌黄瓜",
                    "ingredients": [
                        {"food": "黄瓜", "amount": 100, "unit": "克"}
                    ],
                    "cooking_method": "凉拌",
                    "cooking_time": "5分钟",
                    "nutrition_highlight": "低热量，增加饱腹感"
                }
            ]
            breakfast["cooking_suggestions"] = [
                "粥品煮制时间充分，利于营养释放",
                "蒸蛋羹火候要温和，保持嫩滑",
                "凉拌菜可在前一晚准备"
            ]

        elif disease == DiseaseType.HYPERTENSION:
            # 高血压早餐：低钠 + 高钾
            breakfast["dishes"] = [
                {
                    "dish_name": "紫薯粥",
                    "ingredients": [
                        {"food": "紫薯", "amount": 80, "unit": "克"},
                        {"food": "大米", "amount": 30, "unit": "克"}
                    ],
                    "cooking_method": "煮",
                    "cooking_time": "25分钟",
                    "nutrition_highlight": "富含钾和花青素"
                },
                {
                    "dish_name": "蒸蛋羹",
                    "ingredients": [
                        {"food": "鸡蛋", "amount": 60, "unit": "克"}
                    ],
                    "cooking_method": "蒸",
                    "cooking_time": "15分钟",
                    "nutrition_highlight": "减少盐的使用"
                }
            ]

        return breakfast

    def _create_chinese_lunch(self, calories: float, disease: DiseaseType, user: 'UserProfile') -> Dict:
        """创建中式午餐"""
        lunch = {
            "meal_name": "午餐",
            "target_calories": calories,
            "dishes": [],
            "cooking_suggestions": []
        }

        # 基础搭配：主食 + 荤菜 + 素菜 + 汤
        if disease == DiseaseType.TYPE2_DIABETES:
            lunch["dishes"] = [
                {
                    "dish_name": "糙米饭",
                    "ingredients": [
                        {"food": "糙米", "amount": 60, "unit": "克(生重)"}
                    ],
                    "cooking_method": "蒸煮",
                    "nutrition_highlight": "全谷物，膳食纤维丰富"
                },
                {
                    "dish_name": "清蒸鲫鱼",
                    "ingredients": [
                        {"food": "鲫鱼", "amount": 120, "unit": "克"},
                        {"food": "生姜", "amount": 5, "unit": "克"}
                    ],
                    "cooking_method": "清蒸",
                    "cooking_time": "20分钟",
                    "nutrition_highlight": "优质蛋白，少油烹调"
                },
                {
                    "dish_name": "清炒西兰花",
                    "ingredients": [
                        {"food": "西兰花", "amount": 150, "unit": "克"},
                        {"food": "大蒜", "amount": 5, "unit": "克"}
                    ],
                    "cooking_method": "清炒",
                    "cooking_time": "5分钟",
                    "nutrition_highlight": "富含维生素C和膳食纤维"
                },
                {
                    "dish_name": "冬瓜汤",
                    "ingredients": [
                        {"food": "冬瓜", "amount": 100, "unit": "克"}
                    ],
                    "cooking_method": "煮汤",
                    "nutrition_highlight": "低热量，清热利水"
                }
            ]

        return lunch

    def _create_chinese_dinner(self, calories: float, disease: DiseaseType, user: 'UserProfile') -> Dict:
        """创建中式晚餐"""
        dinner = {
            "meal_name": "晚餐",
            "target_calories": calories,
            "dishes": [],
            "cooking_suggestions": ["晚餐宜清淡，避免过饱", "睡前2-3小时完成用餐"]
        }

        # 晚餐相对简单，热量较低
        if disease == DiseaseType.TYPE2_DIABETES:
            dinner["dishes"] = [
                {
                    "dish_name": "荞麦面条",
                    "ingredients": [
                        {"food": "荞麦", "amount": 40, "unit": "克(干重)"}
                    ],
                    "cooking_method": "煮面",
                    "nutrition_highlight": "低GI主食"
                },
                {
                    "dish_name": "清炒小白菜",
                    "ingredients": [
                        {"food": "小白菜", "amount": 200, "unit": "克"}
                    ],
                    "cooking_method": "清炒",
                    "nutrition_highlight": "高纤维，促进消化"
                },
                {
                    "dish_name": "豆腐汤",
                    "ingredients": [
                        {"food": "豆腐", "amount": 80, "unit": "克"}
                    ],
                    "cooking_method": "煮汤",
                    "nutrition_highlight": "植物蛋白，易消化"
                }
            ]

        return dinner

    def _create_chinese_snack(self, calories: float, disease: DiseaseType, user: 'UserProfile') -> Dict:
        """创建中式加餐"""
        snack = {
            "meal_name": "加餐",
            "target_calories": calories,
            "dishes": [],
            "suggestions": []
        }

        if disease == DiseaseType.TYPE2_DIABETES:
            snack["dishes"] = [
                {
                    "dish_name": "坚果组合",
                    "ingredients": [
                        {"food": "核桃", "amount": 10, "unit": "克"},
                        {"food": "花生", "amount": 10, "unit": "克"}
                    ],
                    "nutrition_highlight": "健康脂肪，控制血糖"
                }
            ]
            snack["suggestions"] = [
                "上午10点或下午3点食用",
                "避免临近正餐时间",
                "可配合适量水果"
            ]

        return snack

    def generate_enhanced_chinese_report(self, user: 'UserProfile') -> str:
        """生成增强版中国本土化营养报告"""
        diseases = self.analyze_disease_risk(user)
        targets = self.calculate_chinese_dietary_targets(user, diseases)
        meal_plan = self.generate_chinese_meal_plan(user, diseases)

        # 生成报告
        report = f"""# {user.name} 中国本土化个性化营养建议报告

*基于《中国居民膳食指南(2022)》和国际疾病营养指南*

## 📋 基本信息

| 项目 | 数值 | 评估 |
|------|------|------|
| 姓名 | {user.name} | - |
| 年龄 | {user.age}岁 | - |
| 性别 | {user.gender} | - |
| 身高 | {user.height}cm | - |
| 体重 | {user.weight}kg | - |
| BMI | {user.weight / ((user.height / 100) ** 2):.1f} | {self._get_bmi_status(user.weight / ((user.height / 100) ** 2))} |
| 活动水平 | {user.activity_level.value} | - |

## 🏥 健康风险评估

### 疾病风险分析
"""

        # 添加健康指标分析
        if user.blood_glucose:
            glucose_status = self._get_glucose_status(user.blood_glucose)
            report += f"- **空腹血糖**: {user.blood_glucose:.1f} mmol/L ({glucose_status})\n"

        if user.hba1c:
            hba1c_status = self._get_hba1c_status(user.hba1c)
            report += f"- **糖化血红蛋白**: {user.hba1c:.1f}% ({hba1c_status})\n"

        if user.blood_pressure_systolic and user.blood_pressure_diastolic:
            bp_status = self._get_bp_status(user.blood_pressure_systolic, user.blood_pressure_diastolic)
            report += f"- **血压**: {user.blood_pressure_systolic}/{user.blood_pressure_diastolic} mmHg ({bp_status})\n"

        # 疾病风险
        report += f"\n### 识别的健康风险\n"
        for disease in diseases:
            if disease != DiseaseType.HEALTHY:
                protocol = self.disease_nutrition_protocols.get(disease, {})
                report += f"- **{disease.value}**: 需要专业营养干预\n"

        # 营养目标
        report += f"""
## 🎯 个性化营养目标

### 基于中国膳食指南的推荐量

| 食物类别 | 每日推荐量 | 本方案目标 | 说明 |
|----------|------------|------------|------|
| 谷薯类 | {self.chinese_guidelines.grains[0]}-{self.chinese_guidelines.grains[1]}g | {targets.get('grains_target', 250):.0f}g | 以全谷物为主 |
| 蔬菜类 | {self.chinese_guidelines.vegetables[0]}-{self.chinese_guidelines.vegetables[1]}g | {targets.get('vegetables_target', 400):.0f}g | 深色蔬菜占一半 |
| 水果类 | {self.chinese_guidelines.fruits[0]}-{self.chinese_guidelines.fruits[1]}g | {targets.get('fruits_target', 250):.0f}g | 新鲜水果为主 |
| 畜禽肉 | {self.chinese_guidelines.livestock_poultry[0]}-{self.chinese_guidelines.livestock_poultry[1]}g | 60g | 优选瘦肉 |
| 水产品 | {self.chinese_guidelines.aquatic_products[0]}-{self.chinese_guidelines.aquatic_products[1]}g | 60g | 每周2-3次 |
| 蛋类 | {self.chinese_guidelines.eggs[0]}-{self.chinese_guidelines.eggs[1]}g | 50g | 每日1个 |
| 奶类 | {self.chinese_guidelines.dairy[0]}-{self.chinese_guidelines.dairy[1]}g | {targets.get('dairy_target', 300):.0f}g | 低脂为主 |
| 烹调油 | ≤{self.chinese_guidelines.cooking_oil[1]}g | 25g | 多样化用油 |
| 食盐 | ≤{self.chinese_guidelines.salt}g | <5g | 控制钠摄入 |

### 热量与宏量营养素目标

| 营养素 | 目标值 | 占比 | 基于指南 |
|--------|--------|------|----------|
| 总热量 | {targets['target_calories']}千卡 | 100% | 个体化计算 |
| 碳水化合物 | {targets['carb_grams']:.0f}g | {targets['carb_ratio']*100:.0f}% | 疾病调整后 |
| 蛋白质 | {targets['protein_grams']:.0f}g | {targets['protein_ratio']*100:.0f}% | 优质蛋白为主 |
| 脂肪 | {targets['fat_grams']:.0f}g | {targets['fat_ratio']*100:.0f}% | 不饱和脂肪为主 |

## 🍽️ 中式个性化食谱

"""

        # 添加每餐详情
        total_daily_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0, "sodium": 0}

        for meal in meal_plan:
            report += f"### {meal['meal_name']} ({meal['target_calories']:.0f}千卡)\n\n"

            for dish in meal["dishes"]:
                report += f"#### {dish['dish_name']}\n\n"
                report += "**食材配比**:\n"

                for ingredient in dish["ingredients"]:
                    report += f"- {ingredient['food']} {ingredient['amount']}{ingredient['unit']}\n"

                if "cooking_method" in dish:
                    report += f"\n**烹饪方法**: {dish['cooking_method']}\n"

                if "cooking_time" in dish:
                    report += f"**制作时间**: {dish['cooking_time']}\n"

                if "nutrition_highlight" in dish:
                    report += f"**营养特点**: {dish['nutrition_highlight']}\n"

                report += "\n"

            if "cooking_suggestions" in meal:
                report += "**烹饪建议**:\n"
                for suggestion in meal["cooking_suggestions"]:
                    report += f"- {suggestion}\n"
                report += "\n"

        # 添加专业营养建议
        report += """## 💡 专业营养建议

### 🥗 中国膳食指南核心推荐

1. **食物多样，合理搭配**
   - 平均每天摄入12种以上食物，每周25种以上
   - 谷类为主，粗细搭配，全谷物和杂豆类占1/3

2. **吃动平衡，健康体重**
   - 各年龄段人群都应天天运动、保持健康体重
   - 坚持日常身体活动，每周至少进行5天中等强度身体活动

3. **多吃蔬果、奶类、大豆**
   - 蔬菜水果是平衡膳食的重要组成部分
   - 奶类富含钙，大豆类富含优质蛋白质

4. **适量吃鱼、禽、蛋、瘦肉**
   - 鱼、禽、蛋和瘦肉摄入要适量
   - 少吃肥肉、烟熏和腌制肉制品

5. **少盐少油，控糖限酒**
   - 培养清淡饮食习惯，少吃高盐和油炸食品
   - 控制添加糖的摄入量，每天摄入不超过50g

6. **杜绝浪费，兴新食尚**
   - 珍惜食物，按需备餐，提倡分餐不浪费
   - 选择新鲜卫生的食物和适宜的烹调方式

### 🍳 中式烹饪建议

#### 健康烹调方法优先级
1. **蒸、煮、炖、焖**: 保持食物原味，营养损失少
2. **凉拌、蘸食**: 清爽开胃，适合蔬菜类
3. **快炒、爆炒**: 时间短，保持蔬菜脆嫩
4. **烤、煎**: 适度使用，控制油量

#### 调味料使用原则
- **盐**: 推荐使用低钠盐，逐步减量
- **油**: 轮换使用不同种类植物油
- **糖**: 尽量减少添加糖使用
- **醋**: 可适量使用，有助控制血糖

### 🏥 疾病特殊建议

"""

        # 添加针对性疾病建议
        for disease in diseases:
            if disease in self.disease_nutrition_protocols:
                protocol = self.disease_nutrition_protocols[disease]
                report += f"#### {disease.value}营养管理\n\n"
                for rec in protocol.get("specific_recommendations", []):
                    report += f"- {rec}\n"
                report += "\n"

        # 添加中医药膳建议
        report += """### 🌿 中医药膳调理建议

#### 体质调理
- **气虚体质**: 适合山药、红枣、黄芪等补气食物
- **阳虚体质**: 适合生姜、桂圆、羊肉等温阳食物
- **阴虚体质**: 适合百合、银耳、梨等滋阴食物
- **痰湿体质**: 适合薏米、冬瓜、茯苓等化湿食物

#### 四季饮食调理
- **春季**: 养肝为主，多吃绿色蔬菜，如菠菜、韭菜
- **夏季**: 清热解暑，多吃瓜类，如冬瓜、黄瓜
- **秋季**: 润燥养肺，多吃白色食物，如梨、银耳
- **冬季**: 温补肾阳，适量进补，如羊肉、核桃

## ⚠️ 注意事项与监测

### 饮食监测指标
"""

        # 添加监测建议
        if DiseaseType.TYPE2_DIABETES in diseases:
            report += """
#### 糖尿病监测
- **血糖监测**: 餐前、餐后2小时血糖
- **糖化血红蛋白**: 每3个月检测一次
- **体重**: 每周同一时间测量
- **血压**: 每日监测，记录变化趋势
"""

        if DiseaseType.HYPERTENSION in diseases:
            report += """
#### 高血压监测
- **血压**: 每日早晚各测一次
- **体重**: 控制在理想范围内
- **钠摄入**: 记录每日用盐量
- **运动**: 记录运动类型和时长
"""

        report += f"""
### 复查建议
- **营养评估**: 建议1-3个月复查一次
- **实验室检查**: 根据疾病类型定期检查
- **体重管理**: 每周测量，记录变化
- **饮食日记**: 前2周详细记录，便于调整

### 特殊情况处理
1. **血糖异常**: 立即调整饮食，必要时就医
2. **血压波动**: 监测钠摄入，调整用药
3. **体重快速变化**: 及时咨询营养师
4. **消化不良**: 调整食物质地和烹调方法

---

**免责声明**: 本报告基于中国居民膳食指南和国际营养学会标准制定，仅供参考。具体实施前请咨询注册营养师或临床医生。

*报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}*
*基于: 《中国居民膳食指南(2022)》、美国糖尿病学会、美国心脏协会等权威指南*
"""

        return report

    def _get_bmi_status(self, bmi: float) -> str:
        """BMI状态评估"""
        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "超重"
        else:
            return "肥胖"

    def _get_glucose_status(self, glucose: float) -> str:
        """血糖状态评估"""
        if glucose < 3.9:
            return "偏低"
        elif glucose <= 6.1:
            return "正常"
        elif glucose <= 7.0:
            return "糖耐量异常"
        else:
            return "糖尿病范围"

    def _get_hba1c_status(self, hba1c: float) -> str:
        """糖化血红蛋白状态评估"""
        if hba1c < 6.0:
            return "正常"
        elif hba1c < 6.5:
            return "糖耐量异常"
        else:
            return "糖尿病范围"

    def _get_bp_status(self, systolic: int, diastolic: int) -> str:
        """血压状态评估"""
        if systolic < 120 and diastolic < 80:
            return "正常"
        elif systolic < 140 or diastolic < 90:
            return "高血压前期"
        else:
            return "高血压"

    def calculate_bmr(self, user: 'UserProfile') -> float:
        """计算基础代谢率"""
        if user.gender == "男":
            bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
        else:
            bmr = 447.593 + (9.247 * user.weight) + (3.098 * user.height) - (4.330 * user.age)
        return bmr

    def calculate_tdee(self, user: 'UserProfile') -> float:
        """计算总日能量消耗"""
        bmr = self.calculate_bmr(user)
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.375,
            ActivityLevel.MODERATE: 1.55,
            ActivityLevel.ACTIVE: 1.725,
            ActivityLevel.VERY_ACTIVE: 1.9
        }
        return bmr * activity_multipliers[user.activity_level]

# 保持原有的类定义兼容性
from personalized_food_recommender import UserProfile, ActivityLevel, HealthGoal, NutritionInfo

def main():
    """主函数 - 生成增强版示例报告"""

    # 创建增强版推荐系统
    recommender = EnhancedChineseFoodRecommender()

    # 示例用户1：糖尿病患者
    user1 = UserProfile(
        name="李先生",
        age=55,
        gender="男",
        height=172,
        weight=78,
        activity_level=ActivityLevel.LIGHT,
        health_goals=[HealthGoal.DIABETES_CONTROL, HealthGoal.WEIGHT_LOSS],
        dietary_restrictions=[],
        blood_glucose=9.2,
        hba1c=8.1,
        blood_pressure_systolic=138,
        blood_pressure_diastolic=88,
        cholesterol_total=5.8,
        triglycerides=2.1,
        preferred_cuisines=["川菜", "粤菜"],
        disliked_foods=["内脏", "海鲜"],
        food_allergies=[]
    )

    # 生成增强版报告
    report1 = recommender.generate_enhanced_chinese_report(user1)

    # 保存报告
    with open("/Users/williamsun/Documents/gplus/docs/FoodRecom/中式糖尿病营养方案_李先生.md", "w", encoding="utf-8") as f:
        f.write(report1)

    # 示例用户2：高血压患者
    user2 = UserProfile(
        name="王女士",
        age=48,
        gender="女",
        height=158,
        weight=65,
        activity_level=ActivityLevel.MODERATE,
        health_goals=[HealthGoal.HYPERTENSION_CONTROL],
        dietary_restrictions=[],
        blood_pressure_systolic=152,
        blood_pressure_diastolic=95,
        preferred_cuisines=["淮扬菜", "素食"],
        disliked_foods=["辛辣食物"],
        food_allergies=["花生"]
    )

    report2 = recommender.generate_enhanced_chinese_report(user2)

    with open("/Users/williamsun/Documents/gplus/docs/FoodRecom/中式高血压营养方案_王女士.md", "w", encoding="utf-8") as f:
        f.write(report2)

    print("✅ 增强版中国本土化个性化营养建议报告生成完成")
    print("📁 报告保存位置: docs/FoodRecom/")
    print("🔬 基于《中国居民膳食指南(2022)》和美国营养学会疾病指南")

if __name__ == "__main__":
    main()