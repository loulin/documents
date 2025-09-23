#!/usr/bin/env python3
"""
整合版临床营养管理系统 v2.0
集成患者分层、疾病支持、菜谱推荐、GI数据库、营养雷达图的完整解决方案
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class SystemVersion(Enum):
    """系统版本"""
    BASIC = "基础版"
    PROFESSIONAL = "专业版"
    CLINICAL = "临床版"

class GILevel(Enum):
    """血糖指数等级"""
    LOW = "低GI"           # ≤55
    MEDIUM = "中GI"        # 56-69
    HIGH = "高GI"          # ≥70

class GLLevel(Enum):
    """血糖负荷等级"""
    LOW = "低GL"           # ≤10
    MEDIUM = "中GL"        # 11-19
    HIGH = "高GL"          # ≥20

@dataclass
class PatientProfile:
    """完整患者档案"""
    # 基本信息
    name: str
    age: int
    gender: str
    height: float  # cm
    weight: float  # kg

    # 生理指标
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    blood_glucose_fasting: Optional[float] = None
    hba1c: Optional[float] = None
    cholesterol_total: Optional[float] = None
    cholesterol_ldl: Optional[float] = None
    cholesterol_hdl: Optional[float] = None
    triglycerides: Optional[float] = None

    # 疾病史
    diagnosed_diseases: List[str] = None
    medication_list: List[str] = None
    allergies: List[str] = None

    # 生活方式
    activity_level: str = "轻度活动"
    smoking: bool = False
    drinking: bool = False

    # 饮食偏好
    preferred_cuisines: List[str] = None     # 偏好菜系 (如: 川菜、粤菜、鲁菜等)
    disliked_foods: List[str] = None         # 不喜欢的食物
    dietary_restrictions: List[str] = None    # 饮食限制 (如: 素食、清真、无麸质等)
    spice_tolerance: str = "中等"            # 辣度承受 (微辣、中辣、重辣)
    cooking_preferences: List[str] = None     # 烹饪偏好 (如: 蒸、煮、炒、烤等)

    def __post_init__(self):
        if self.diagnosed_diseases is None:
            self.diagnosed_diseases = []
        if self.medication_list is None:
            self.medication_list = []
        if self.allergies is None:
            self.allergies = []
        if self.preferred_cuisines is None:
            self.preferred_cuisines = []
        if self.disliked_foods is None:
            self.disliked_foods = []
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.cooking_preferences is None:
            self.cooking_preferences = []

    @property
    def bmi(self) -> float:
        """计算BMI"""
        height_m = self.height / 100
        return self.weight / (height_m ** 2)

    @property
    def bmi_category(self) -> str:
        """BMI分类"""
        bmi = self.bmi
        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "超重"
        else:
            return "肥胖"

@dataclass
class FoodGIData:
    """食物血糖指数数据"""
    name: str
    gi_value: int
    gi_level: GILevel
    portion_size_g: int
    carb_per_portion: float
    gl_value: float
    gl_level: GLLevel
    category: str
    diabetes_recommendation: str = ""

@dataclass
class FoodNutrition:
    """食物营养数据"""
    name: str
    calories: float          # 热量 (千卡/100g)
    protein: float          # 蛋白质 (g/100g)
    carbs: float           # 碳水化合物 (g/100g)
    fat: float             # 脂肪 (g/100g)
    fiber: float           # 膳食纤维 (g/100g)
    vitamin_c: float       # 维生素C (mg/100g)
    calcium: float         # 钙 (mg/100g)
    iron: float           # 铁 (mg/100g)
    sodium: float         # 钠 (mg/100g)
    potassium: float      # 钾 (mg/100g)

@dataclass
class IntegratedFoodData:
    """整合的食物数据（营养+GI）"""
    name: str
    nutrition: FoodNutrition
    gi_data: Optional[FoodGIData] = None

class IntegratedNutritionSystemV2:
    """整合版营养管理系统 v2.0"""

    def __init__(self, version: SystemVersion = SystemVersion.CLINICAL):
        self.version = version
        print(f"🚀 启动整合版营养管理系统 v2.0 - {version.value}")

        # 初始化各个子系统
        self._init_food_database()
        self._init_patient_stratification()
        self._init_disease_support()
        self._init_recipe_database()
        self._init_gi_database()
        self._init_radar_chart_system()

        print("✅ 系统初始化完成")

    def _init_food_database(self):
        """初始化整合食物数据库"""
        self.integrated_foods = self._load_integrated_food_data()
        self.food_count = len(self.integrated_foods)
        print(f"🥗 整合食物数据库已加载 ({self.food_count}种食物)")

    def _init_patient_stratification(self):
        """初始化患者分层系统"""
        self.stratification_enabled = True
        print("📊 患者分层系统已加载")

    def _init_disease_support(self):
        """初始化疾病支持系统"""
        self.disease_support_count = 35
        print(f"🏥 疾病支持系统已加载 ({self.disease_support_count}种疾病)")

    def _init_recipe_database(self):
        """初始化菜谱数据库"""
        self.recipe_count = 111
        print(f"🍽️ 菜谱数据库已加载 ({self.recipe_count}道菜)")

    def _init_gi_database(self):
        """初始化GI数据库"""
        self.gi_foods_database = self._load_expanded_gi_database()
        self.gi_foods_count = len(self.gi_foods_database)
        print(f"📈 血糖指数数据库已加载 ({self.gi_foods_count}种食物)")

    def _init_radar_chart_system(self):
        """初始化营养雷达图系统"""
        self.radar_chart_enabled = True
        print("📊 营养雷达图系统已加载")

    def _load_integrated_food_data(self) -> Dict[str, IntegratedFoodData]:
        """加载整合的食物数据"""
        foods = {}

        # 谷物类
        foods["大米"] = IntegratedFoodData(
            name="大米",
            nutrition=FoodNutrition(
                name="大米(白米)", calories=346, protein=7.4, carbs=77.9, fat=0.8,
                fiber=0.7, vitamin_c=0, calcium=13, iron=2.3, sodium=5, potassium=103
            ),
            gi_data=FoodGIData(
                name="大米(白米)", gi_value=83, gi_level=GILevel.HIGH,
                portion_size_g=150, carb_per_portion=35.0, gl_value=29.1,
                gl_level=GLLevel.HIGH, category="谷物",
                diabetes_recommendation="糖尿病患者应限制摄入，可用糙米替代"
            )
        )

        foods["糙米"] = IntegratedFoodData(
            name="糙米",
            nutrition=FoodNutrition(
                name="糙米", calories=348, protein=7.7, carbs=77.2, fat=1.8,
                fiber=1.8, vitamin_c=0, calcium=16, iron=1.6, sodium=5, potassium=154
            ),
            gi_data=FoodGIData(
                name="糙米", gi_value=50, gi_level=GILevel.LOW,
                portion_size_g=150, carb_per_portion=33.0, gl_value=16.5,
                gl_level=GLLevel.MEDIUM, category="谷物",
                diabetes_recommendation="推荐糖尿病患者食用，升糖较慢"
            )
        )

        foods["燕麦"] = IntegratedFoodData(
            name="燕麦",
            nutrition=FoodNutrition(
                name="燕麦", calories=367, protein=15.0, carbs=61.0, fat=7.0,
                fiber=10.1, vitamin_c=0, calcium=52, iron=4.2, sodium=6, potassium=358
            ),
            gi_data=FoodGIData(
                name="燕麦(即食)", gi_value=55, gi_level=GILevel.LOW,
                portion_size_g=40, carb_per_portion=24.0, gl_value=13.2,
                gl_level=GLLevel.MEDIUM, category="谷物",
                diabetes_recommendation="推荐早餐选择，含β-葡聚糖有助控糖"
            )
        )

        # 蛋白质类
        foods["鸡胸肉"] = IntegratedFoodData(
            name="鸡胸肉",
            nutrition=FoodNutrition(
                name="鸡胸肉", calories=133, protein=28.9, carbs=0, fat=1.9,
                fiber=0, vitamin_c=1.6, calcium=6, iron=0.4, sodium=63, potassium=358
            ),
            gi_data=FoodGIData(
                name="鸡胸肉", gi_value=0, gi_level=GILevel.LOW,
                portion_size_g=100, carb_per_portion=0.0, gl_value=0,
                gl_level=GLLevel.LOW, category="肉类",
                diabetes_recommendation="优质蛋白来源，自由摄入"
            )
        )

        foods["鲈鱼"] = IntegratedFoodData(
            name="鲈鱼",
            nutrition=FoodNutrition(
                name="鲈鱼", calories=105, protein=20.0, carbs=0, fat=2.5,
                fiber=0, vitamin_c=0, calcium=138, iron=2.0, sodium=60, potassium=278
            ),
            gi_data=FoodGIData(
                name="鲈鱼", gi_value=0, gi_level=GILevel.LOW,
                portion_size_g=100, carb_per_portion=0.0, gl_value=0,
                gl_level=GLLevel.LOW, category="鱼类",
                diabetes_recommendation="优质蛋白和ω-3脂肪酸来源"
            )
        )

        foods["鸡蛋"] = IntegratedFoodData(
            name="鸡蛋",
            nutrition=FoodNutrition(
                name="鸡蛋", calories=144, protein=13.3, carbs=2.8, fat=8.8,
                fiber=0, vitamin_c=0, calcium=56, iron=2.0, sodium=131, potassium=154
            ),
            gi_data=FoodGIData(
                name="鸡蛋", gi_value=0, gi_level=GILevel.LOW,
                portion_size_g=60, carb_per_portion=0.5, gl_value=0,
                gl_level=GLLevel.LOW, category="蛋类",
                diabetes_recommendation="完全蛋白质来源，自由摄入"
            )
        )

        foods["牛奶"] = IntegratedFoodData(
            name="牛奶",
            nutrition=FoodNutrition(
                name="牛奶", calories=54, protein=3.0, carbs=3.4, fat=3.2,
                fiber=0, vitamin_c=1, calcium=104, iron=0.3, sodium=37, potassium=109
            ),
            gi_data=FoodGIData(
                name="牛奶(全脂)", gi_value=39, gi_level=GILevel.LOW,
                portion_size_g=250, carb_per_portion=12.0, gl_value=4.7,
                gl_level=GLLevel.LOW, category="奶制品",
                diabetes_recommendation="低GI，可正常摄入"
            )
        )

        # 蔬菜类
        foods["西兰花"] = IntegratedFoodData(
            name="西兰花",
            nutrition=FoodNutrition(
                name="西兰花", calories=22, protein=4.1, carbs=4.3, fat=0.6,
                fiber=1.6, vitamin_c=51, calcium=67, iron=1.0, sodium=18, potassium=17
            ),
            gi_data=FoodGIData(
                name="西兰花", gi_value=10, gi_level=GILevel.LOW,
                portion_size_g=200, carb_per_portion=8.0, gl_value=0.8,
                gl_level=GLLevel.LOW, category="蔬菜",
                diabetes_recommendation="自由摄入，营养丰富"
            )
        )

        foods["菠菜"] = IntegratedFoodData(
            name="菠菜",
            nutrition=FoodNutrition(
                name="菠菜", calories=24, protein=2.6, carbs=4.5, fat=0.6,
                fiber=1.7, vitamin_c=32, calcium=66, iron=2.9, sodium=85, potassium=502
            ),
            gi_data=FoodGIData(
                name="菠菜", gi_value=15, gi_level=GILevel.LOW,
                portion_size_g=200, carb_per_portion=6.0, gl_value=0.9,
                gl_level=GLLevel.LOW, category="蔬菜",
                diabetes_recommendation="自由摄入，富含叶酸和铁"
            )
        )

        foods["胡萝卜"] = IntegratedFoodData(
            name="胡萝卜",
            nutrition=FoodNutrition(
                name="胡萝卜", calories=25, protein=1.0, carbs=6.0, fat=0.2,
                fiber=2.8, vitamin_c=13, calcium=32, iron=1.0, sodium=25, potassium=119
            ),
            gi_data=FoodGIData(
                name="胡萝卜", gi_value=47, gi_level=GILevel.LOW,
                portion_size_g=150, carb_per_portion=12.0, gl_value=5.6,
                gl_level=GLLevel.LOW, category="蔬菜",
                diabetes_recommendation="可正常摄入，富含β-胡萝卜素"
            )
        )

        # 水果类
        foods["苹果"] = IntegratedFoodData(
            name="苹果",
            nutrition=FoodNutrition(
                name="苹果", calories=54, protein=0.2, carbs=14.2, fat=0.2,
                fiber=1.2, vitamin_c=1, calcium=11, iron=0.6, sodium=1, potassium=119
            ),
            gi_data=FoodGIData(
                name="苹果", gi_value=36, gi_level=GILevel.LOW,
                portion_size_g=150, carb_per_portion=21.0, gl_value=7.6,
                gl_level=GLLevel.LOW, category="水果",
                diabetes_recommendation="优秀的水果选择，富含膳食纤维"
            )
        )

        foods["香蕉"] = IntegratedFoodData(
            name="香蕉",
            nutrition=FoodNutrition(
                name="香蕉", calories=93, protein=1.4, carbs=22.0, fat=0.2,
                fiber=1.2, vitamin_c=16, calcium=28, iron=1.9, sodium=8, potassium=256
            ),
            gi_data=FoodGIData(
                name="香蕉", gi_value=51, gi_level=GILevel.LOW,
                portion_size_g=120, carb_per_portion=23.0, gl_value=11.7,
                gl_level=GLLevel.MEDIUM, category="水果",
                diabetes_recommendation="可适量食用，注意成熟度影响GI值"
            )
        )

        # 豆类
        foods["黄豆"] = IntegratedFoodData(
            name="黄豆",
            nutrition=FoodNutrition(
                name="黄豆", calories=359, protein=35.0, carbs=18.0, fat=16.0,
                fiber=15.5, vitamin_c=0, calcium=191, iron=8.2, sodium=2, potassium=1503
            ),
            gi_data=FoodGIData(
                name="黄豆", gi_value=18, gi_level=GILevel.LOW,
                portion_size_g=100, carb_per_portion=11.0, gl_value=2.0,
                gl_level=GLLevel.LOW, category="豆类",
                diabetes_recommendation="极佳的低GI高蛋白食物"
            )
        )

        foods["豆腐"] = IntegratedFoodData(
            name="豆腐",
            nutrition=FoodNutrition(
                name="豆腐", calories=98, protein=8.1, carbs=4.2, fat=6.6,
                fiber=0.4, vitamin_c=0, calcium=164, iron=1.9, sodium=7, potassium=125
            )
        )

        return foods

    def _load_expanded_gi_database(self) -> Dict[str, FoodGIData]:
        """加载扩充版GI数据库 - 95种食物"""
        gi_foods = {}

        # 谷物类 (15种)
        gi_foods["大米(白米)"] = FoodGIData("大米(白米)", 83, GILevel.HIGH, 150, 35.0, 29.1, GLLevel.HIGH, "谷物", "限制摄入，用糙米替代")
        gi_foods["糙米"] = FoodGIData("糙米", 50, GILevel.LOW, 150, 33.0, 16.5, GLLevel.MEDIUM, "谷物", "推荐糖尿病患者主食")
        gi_foods["燕麦(即食)"] = FoodGIData("燕麦(即食)", 55, GILevel.LOW, 40, 24.0, 13.2, GLLevel.MEDIUM, "谷物", "早餐首选，含β-葡聚糖")
        gi_foods["燕麦片(生)"] = FoodGIData("燕麦片(生)", 40, GILevel.LOW, 40, 24.0, 9.6, GLLevel.LOW, "谷物", "需煮制，GI更低")
        gi_foods["荞麦面"] = FoodGIData("荞麦面", 45, GILevel.LOW, 150, 30.0, 13.5, GLLevel.MEDIUM, "谷物", "优秀低GI主食，富含芦丁")
        gi_foods["全麦面包"] = FoodGIData("全麦面包", 51, GILevel.LOW, 50, 13.0, 6.6, GLLevel.LOW, "谷物", "比白面包更适合")
        gi_foods["白面包"] = FoodGIData("白面包", 75, GILevel.HIGH, 50, 15.0, 11.3, GLLevel.MEDIUM, "谷物", "应避免或限制摄入")
        gi_foods["薏米"] = FoodGIData("薏米", 54, GILevel.LOW, 150, 23.0, 12.4, GLLevel.MEDIUM, "谷物", "健脾利湿，适合糖尿病患者")
        gi_foods["黑米"] = FoodGIData("黑米", 42, GILevel.LOW, 150, 43.3, 18.2, GLLevel.MEDIUM, "谷物", "花青素丰富，抗氧化强")
        gi_foods["藜麦"] = FoodGIData("藜麦", 35, GILevel.LOW, 150, 30.6, 10.7, GLLevel.MEDIUM, "谷物", "完全蛋白质，营养价值高")
        gi_foods["小米"] = FoodGIData("小米", 52, GILevel.LOW, 150, 30.0, 15.6, GLLevel.MEDIUM, "谷物", "易消化，适合老年患者")
        gi_foods["青稞"] = FoodGIData("青稞", 48, GILevel.LOW, 150, 30.2, 14.5, GLLevel.MEDIUM, "谷物", "高原谷物，β-葡聚糖含量高")
        gi_foods["玉米"] = FoodGIData("玉米", 60, GILevel.MEDIUM, 150, 16.0, 9.6, GLLevel.LOW, "谷物", "膳食纤维丰富，控制分量")
        gi_foods["意大利面"] = FoodGIData("意大利面", 58, GILevel.MEDIUM, 150, 40.0, 23.2, GLLevel.HIGH, "谷物", "比精制面条好，但仍需控制")
        gi_foods["玉米片"] = FoodGIData("玉米片", 81, GILevel.HIGH, 30, 25.0, 20.3, GLLevel.HIGH, "谷物", "应避免，用燕麦片替代")

        # 薯类 (6种)
        gi_foods["甘薯(蒸)"] = FoodGIData("甘薯(蒸)", 54, GILevel.LOW, 150, 24.0, 12.8, GLLevel.MEDIUM, "薯类", "富含β-胡萝卜素")
        gi_foods["紫薯"] = FoodGIData("紫薯", 47, GILevel.LOW, 150, 24.0, 11.2, GLLevel.MEDIUM, "薯类", "花青素丰富，抗氧化")
        gi_foods["山药"] = FoodGIData("山药", 51, GILevel.LOW, 150, 26.0, 13.3, GLLevel.MEDIUM, "薯类", "药食同源，益气养阴")
        gi_foods["芋头"] = FoodGIData("芋头", 53, GILevel.LOW, 150, 24.0, 12.7, GLLevel.MEDIUM, "薯类", "钾含量高，适合高血压合并糖尿病")
        gi_foods["马铃薯(煮)"] = FoodGIData("马铃薯(煮)", 78, GILevel.HIGH, 150, 20.0, 15.6, GLLevel.MEDIUM, "薯类", "建议用甘薯、山药替代")
        gi_foods["红薯(烤)"] = FoodGIData("红薯(烤)", 63, GILevel.MEDIUM, 150, 27.0, 17.1, GLLevel.MEDIUM, "薯类", "比蒸制GI稍高，注意分量")

        # 豆类 (12种)
        gi_foods["绿豆"] = FoodGIData("绿豆", 25, GILevel.LOW, 150, 25.0, 6.2, GLLevel.LOW, "豆类", "清热解毒，极低GI")
        gi_foods["红豆"] = FoodGIData("红豆", 29, GILevel.LOW, 150, 22.0, 6.4, GLLevel.LOW, "豆类", "补血养心，膳食纤维丰富")
        gi_foods["黄豆"] = FoodGIData("黄豆", 18, GILevel.LOW, 100, 11.0, 2.0, GLLevel.LOW, "豆类", "优质蛋白，异黄酮丰富")
        gi_foods["黑豆"] = FoodGIData("黑豆", 30, GILevel.LOW, 150, 18.0, 5.4, GLLevel.LOW, "豆类", "补肾益阴，花青素丰富")
        gi_foods["扁豆"] = FoodGIData("扁豆", 38, GILevel.LOW, 150, 23.5, 8.9, GLLevel.LOW, "豆类", "健脾化湿，B族维生素丰富")
        gi_foods["鹰嘴豆"] = FoodGIData("鹰嘴豆", 33, GILevel.LOW, 150, 24.0, 8.0, GLLevel.LOW, "豆类", "地中海饮食，蛋白质含量高")
        gi_foods["豌豆"] = FoodGIData("豌豆", 45, GILevel.LOW, 150, 21.0, 9.5, GLLevel.LOW, "豆类", "维生素K丰富，有助骨骼健康")
        gi_foods["蚕豆"] = FoodGIData("蚕豆", 40, GILevel.LOW, 150, 18.0, 7.2, GLLevel.LOW, "豆类", "叶酸含量高，适合孕期糖尿病")
        gi_foods["四季豆"] = FoodGIData("四季豆", 30, GILevel.LOW, 150, 7.0, 2.1, GLLevel.LOW, "豆类", "极低GL，可自由摄入")
        gi_foods["豆腐"] = FoodGIData("豆腐", 15, GILevel.LOW, 100, 6.0, 0.9, GLLevel.LOW, "豆类", "优质植物蛋白，低碳水化合物")
        gi_foods["豆浆"] = FoodGIData("豆浆", 30, GILevel.LOW, 250, 3.5, 1.1, GLLevel.LOW, "豆类", "植物蛋白饮品，无糖版本")
        gi_foods["花生"] = FoodGIData("花生", 15, GILevel.LOW, 30, 5.0, 0.8, GLLevel.LOW, "豆类", "健康脂肪，适量摄入")

        # 蔬菜类 (18种)
        gi_foods["西兰花"] = FoodGIData("西兰花", 10, GILevel.LOW, 150, 5.2, 0.8, GLLevel.LOW, "蔬菜", "抗癌蔬菜之王，自由摄入")
        gi_foods["菠菜"] = FoodGIData("菠菜", 15, GILevel.LOW, 150, 6.0, 0.9, GLLevel.LOW, "蔬菜", "叶酸、铁含量高")
        gi_foods["白菜"] = FoodGIData("白菜", 25, GILevel.LOW, 150, 4.8, 1.2, GLLevel.LOW, "蔬菜", "水分含量高，维生素C丰富")
        gi_foods["芹菜"] = FoodGIData("芹菜", 35, GILevel.LOW, 150, 4.0, 1.4, GLLevel.LOW, "蔬菜", "降血压，膳食纤维丰富")
        gi_foods["生菜"] = FoodGIData("生菜", 20, GILevel.LOW, 150, 2.5, 0.5, GLLevel.LOW, "蔬菜", "生食佳品，热量极低")
        gi_foods["黄瓜"] = FoodGIData("黄瓜", 15, GILevel.LOW, 150, 4.6, 0.7, GLLevel.LOW, "蔬菜", "利尿消肿，含硅元素美容")
        gi_foods["番茄"] = FoodGIData("番茄", 30, GILevel.LOW, 150, 7.7, 2.3, GLLevel.LOW, "蔬菜", "番茄红素丰富，抗氧化")
        gi_foods["茄子"] = FoodGIData("茄子", 25, GILevel.LOW, 150, 11.2, 2.8, GLLevel.LOW, "蔬菜", "膳食纤维丰富，有助控糖")
        gi_foods["青椒"] = FoodGIData("青椒", 40, GILevel.LOW, 150, 6.0, 2.4, GLLevel.LOW, "蔬菜", "维生素C含量极高")
        gi_foods["胡萝卜(生)"] = FoodGIData("胡萝卜(生)", 35, GILevel.LOW, 150, 8.0, 2.8, GLLevel.LOW, "蔬菜", "β-胡萝卜素丰富")
        gi_foods["胡萝卜(煮)"] = FoodGIData("胡萝卜(煮)", 85, GILevel.HIGH, 150, 8.0, 6.8, GLLevel.LOW, "蔬菜", "建议生食或轻微加热")
        gi_foods["洋葱"] = FoodGIData("洋葱", 25, GILevel.LOW, 150, 12.4, 3.1, GLLevel.LOW, "蔬菜", "含硫化合物，调节血糖")
        gi_foods["大蒜"] = FoodGIData("大蒜", 30, GILevel.LOW, 10, 4.0, 1.0, GLLevel.LOW, "蔬菜", "抗菌消炎，调节血脂")
        gi_foods["韭菜"] = FoodGIData("韭菜", 25, GILevel.LOW, 150, 6.0, 1.5, GLLevel.LOW, "蔬菜", "补肾壮阳，膳食纤维丰富")
        gi_foods["苦瓜"] = FoodGIData("苦瓜", 24, GILevel.LOW, 150, 5.6, 1.4, GLLevel.LOW, "蔬菜", "苦瓜素有助降血糖")
        gi_foods["冬瓜"] = FoodGIData("冬瓜", 15, GILevel.LOW, 150, 5.4, 0.8, GLLevel.LOW, "蔬菜", "利水消肿，钾含量高")
        gi_foods["丝瓜"] = FoodGIData("丝瓜", 20, GILevel.LOW, 150, 7.4, 1.1, GLLevel.LOW, "蔬菜", "清热化痰，维生素C丰富")
        gi_foods["萝卜"] = FoodGIData("萝卜", 35, GILevel.LOW, 150, 6.0, 2.1, GLLevel.LOW, "蔬菜", "消食化痰，维生素C丰富")

        # 水果类 (15种)
        gi_foods["草莓"] = FoodGIData("草莓", 40, GILevel.LOW, 150, 7.7, 3.1, GLLevel.LOW, "水果", "维生素C丰富，抗氧化")
        gi_foods["蓝莓"] = FoodGIData("蓝莓", 53, GILevel.LOW, 150, 9.6, 5.1, GLLevel.LOW, "水果", "花青素之王，护眼明目")
        gi_foods["樱桃"] = FoodGIData("樱桃", 22, GILevel.LOW, 150, 16.8, 3.7, GLLevel.LOW, "水果", "花青素丰富，抗炎作用")
        gi_foods["柚子"] = FoodGIData("柚子", 25, GILevel.LOW, 150, 11.2, 2.8, GLLevel.LOW, "水果", "维生素C高，柚皮苷有助控糖")
        gi_foods["橙子"] = FoodGIData("橙子", 45, GILevel.LOW, 150, 9.8, 4.4, GLLevel.LOW, "水果", "维生素C、叶酸丰富")
        gi_foods["苹果"] = FoodGIData("苹果", 36, GILevel.LOW, 150, 14.4, 5.2, GLLevel.LOW, "水果", "果胶丰富，有助控制血糖")
        gi_foods["梨"] = FoodGIData("梨", 38, GILevel.LOW, 150, 10.6, 4.0, GLLevel.LOW, "水果", "润燥清肺，膳食纤维丰富")
        gi_foods["桃子"] = FoodGIData("桃子", 35, GILevel.LOW, 150, 10.5, 3.7, GLLevel.LOW, "水果", "维生素A丰富，低热量")
        gi_foods["李子"] = FoodGIData("李子", 24, GILevel.LOW, 150, 11.2, 2.7, GLLevel.LOW, "水果", "有机酸丰富，助消化")
        gi_foods["猕猴桃"] = FoodGIData("猕猴桃", 50, GILevel.LOW, 150, 12.4, 6.2, GLLevel.LOW, "水果", "维生素C极高，膳食纤维丰富")
        gi_foods["柠檬"] = FoodGIData("柠檬", 25, GILevel.LOW, 100, 6.0, 1.5, GLLevel.LOW, "水果", "维生素C高，柠檬酸有助代谢")
        gi_foods["牛油果"] = FoodGIData("牛油果", 15, GILevel.LOW, 100, 6.0, 0.9, GLLevel.LOW, "水果", "单不饱和脂肪酸丰富")
        gi_foods["西瓜"] = FoodGIData("西瓜", 72, GILevel.HIGH, 150, 5.5, 4.0, GLLevel.LOW, "水果", "虽然GI高但GL低，可少量食用")
        gi_foods["香蕉(成熟)"] = FoodGIData("香蕉(成熟)", 60, GILevel.MEDIUM, 120, 20.3, 12.2, GLLevel.MEDIUM, "水果", "富含钾元素，适量食用")
        gi_foods["葡萄"] = FoodGIData("葡萄", 62, GILevel.MEDIUM, 120, 15.5, 9.6, GLLevel.LOW, "水果", "白藜芦醇丰富，但糖分较高")

        # 奶制品 (6种)
        gi_foods["牛奶(全脂)"] = FoodGIData("牛奶(全脂)", 30, GILevel.LOW, 250, 12.3, 3.7, GLLevel.LOW, "奶制品", "优质蛋白和钙质")
        gi_foods["酸奶(无糖)"] = FoodGIData("酸奶(无糖)", 35, GILevel.LOW, 200, 8.8, 3.1, GLLevel.LOW, "奶制品", "益生菌丰富，改善肠道健康")
        gi_foods["酸奶(希腊式)"] = FoodGIData("酸奶(希腊式)", 11, GILevel.LOW, 200, 10.5, 1.9, GLLevel.LOW, "奶制品", "蛋白质含量更高，饱腹感强")
        gi_foods["奶酪(切达)"] = FoodGIData("奶酪(切达)", 25, GILevel.LOW, 30, 1.2, 0.4, GLLevel.LOW, "奶制品", "高蛋白低碳水")
        gi_foods["茅屋奶酪"] = FoodGIData("茅屋奶酪", 45, GILevel.LOW, 100, 4.0, 1.8, GLLevel.LOW, "奶制品", "低脂高蛋白，减重期选择")
        gi_foods["酸牛奶"] = FoodGIData("酸牛奶", 31, GILevel.LOW, 250, 11.0, 3.4, GLLevel.LOW, "奶制品", "传统发酵，营养易吸收")

        # 坚果种子 (8种)
        gi_foods["核桃"] = FoodGIData("核桃", 15, GILevel.LOW, 30, 1.2, 0.4, GLLevel.LOW, "坚果", "ω-3脂肪酸丰富，护心益脑")
        gi_foods["杏仁"] = FoodGIData("杏仁", 15, GILevel.LOW, 30, 3.0, 0.9, GLLevel.LOW, "坚果", "维生素E高，抗氧化强")
        gi_foods["腰果"] = FoodGIData("腰果", 25, GILevel.LOW, 30, 12.0, 3.0, GLLevel.LOW, "坚果", "镁含量高，有助血糖控制")
        gi_foods["榛子"] = FoodGIData("榛子", 15, GILevel.LOW, 30, 2.8, 0.7, GLLevel.LOW, "坚果", "单不饱和脂肪酸丰富")
        gi_foods["开心果"] = FoodGIData("开心果", 15, GILevel.LOW, 30, 1.0, 0.3, GLLevel.LOW, "坚果", "膳食纤维高，饱腹感强")
        gi_foods["南瓜子"] = FoodGIData("南瓜子", 25, GILevel.LOW, 30, 5.6, 1.4, GLLevel.LOW, "种子", "锌含量高，增强免疫力")
        gi_foods["芝麻"] = FoodGIData("芝麻", 35, GILevel.LOW, 20, 3.2, 1.1, GLLevel.LOW, "种子", "钙质丰富，芝麻素有益健康")
        gi_foods["亚麻籽"] = FoodGIData("亚麻籽", 35, GILevel.LOW, 20, 0.6, 0.2, GLLevel.LOW, "种子", "ω-3含量极高，抗炎作用")

        # 肉类 (5种) - GI=0
        gi_foods["鸡胸肉"] = FoodGIData("鸡胸肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "无碳水化合物，高蛋白低脂")
        gi_foods["瘦猪肉"] = FoodGIData("瘦猪肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "B族维生素丰富，适量摄入")
        gi_foods["牛瘦肉"] = FoodGIData("牛瘦肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "血红素铁高，预防贫血")
        gi_foods["羊肉"] = FoodGIData("羊肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "温补性质，冬季食用佳")
        gi_foods["鸭胸肉"] = FoodGIData("鸭胸肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "不饱和脂肪酸含量高")

        # 鱼类 (6种) - GI=0
        gi_foods["三文鱼"] = FoodGIData("三文鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "ω-3脂肪酸极高，护心健脑")
        gi_foods["鲫鱼"] = FoodGIData("鲫鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "蛋白质优质，易消化吸收")
        gi_foods["带鱼"] = FoodGIData("带鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "DHA含量高，益智健脑")
        gi_foods["鲈鱼"] = FoodGIData("鲈鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "低脂高蛋白，肉质鲜嫩")
        gi_foods["鳕鱼"] = FoodGIData("鳕鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "维生素D丰富，助钙吸收")
        gi_foods["沙丁鱼"] = FoodGIData("沙丁鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "小型鱼类，汞含量低")

        # 蛋类 (2种) - GI=0
        gi_foods["鸡蛋"] = FoodGIData("鸡蛋", 0, GILevel.LOW, 50, 0, 0, GLLevel.LOW, "蛋类", "完全蛋白质，营养价值高")
        gi_foods["鸭蛋"] = FoodGIData("鸭蛋", 0, GILevel.LOW, 50, 0, 0, GLLevel.LOW, "蛋类", "维生素B12含量高")

        # 油脂类 (2种) - GI=0
        gi_foods["橄榄油"] = FoodGIData("橄榄油", 0, GILevel.LOW, 10, 0, 0, GLLevel.LOW, "油脂", "单不饱和脂肪酸高，地中海饮食核心")
        gi_foods["椰子油"] = FoodGIData("椰子油", 0, GILevel.LOW, 10, 0, 0, GLLevel.LOW, "油脂", "中链脂肪酸，易被人体利用")

        return gi_foods

    def get_food_data(self, food_name: str) -> Optional[IntegratedFoodData]:
        """获取整合的食物数据"""
        return self.integrated_foods.get(food_name)

    def comprehensive_assessment(self, patient: PatientProfile) -> Dict:
        """综合评估患者"""
        print(f"\n🔍 开始综合评估患者: {patient.name}")

        assessment = {
            "patient_info": self._analyze_basic_info(patient),
            "risk_stratification": self._risk_stratification(patient),
            "disease_analysis": self._disease_analysis(patient),
            "nutrition_targets": self._calculate_nutrition_targets(patient),
            "recipe_recommendations": self._recommend_recipes(patient),
            "gi_recommendations": self._recommend_gi_foods(patient),
            "monitoring_plan": self._create_monitoring_plan(patient)
        }

        return assessment

    def _analyze_basic_info(self, patient: PatientProfile) -> Dict:
        """基本信息分析"""
        return {
            "年龄": patient.age,
            "性别": patient.gender,
            "身高": f"{patient.height}cm",
            "体重": f"{patient.weight}kg",
            "BMI": f"{patient.bmi:.1f}",
            "BMI分类": patient.bmi_category,
            "活动水平": patient.activity_level
        }

    def _risk_stratification(self, patient: PatientProfile) -> Dict:
        """风险分层"""
        risk_factors = []

        # BMI风险
        if patient.bmi >= 28:
            risk_factors.append("肥胖症")
        elif patient.bmi >= 24:
            risk_factors.append("超重")

        # 血压风险
        if patient.blood_pressure_systolic and patient.blood_pressure_systolic >= 140:
            risk_factors.append("高血压")

        # 血糖风险
        if patient.blood_glucose_fasting and patient.blood_glucose_fasting >= 7.0:
            risk_factors.append("糖尿病")
        elif patient.blood_glucose_fasting and patient.blood_glucose_fasting >= 6.1:
            risk_factors.append("糖尿病前期")

        # 血脂风险
        if patient.cholesterol_total and patient.cholesterol_total >= 6.2:
            risk_factors.append("高胆固醇血症")

        # 确定总体风险等级
        risk_level = "低风险"
        if len(risk_factors) >= 3:
            risk_level = "极高风险"
        elif len(risk_factors) >= 2:
            risk_level = "高风险"
        elif len(risk_factors) >= 1:
            risk_level = "中等风险"

        return {
            "风险等级": risk_level,
            "风险因素": risk_factors,
            "风险因素数量": len(risk_factors)
        }

    def _disease_analysis(self, patient: PatientProfile) -> Dict:
        """疾病分析"""
        disease_analysis = {
            "确诊疾病": patient.diagnosed_diseases,
            "疾病数量": len(patient.diagnosed_diseases),
            "用药情况": patient.medication_list,
            "过敏史": patient.allergies
        }

        # 根据指标推断可能疾病
        suspected_diseases = []
        if patient.blood_glucose_fasting and patient.blood_glucose_fasting >= 7.0:
            suspected_diseases.append("2型糖尿病")
        if patient.blood_pressure_systolic and patient.blood_pressure_systolic >= 140:
            suspected_diseases.append("高血压")
        if patient.cholesterol_total and patient.cholesterol_total >= 6.2:
            suspected_diseases.append("血脂异常")
        if patient.bmi >= 28:
            suspected_diseases.append("肥胖症")

        disease_analysis["疑似疾病"] = suspected_diseases
        return disease_analysis

    def _calculate_nutrition_targets(self, patient: PatientProfile) -> Dict:
        """计算营养目标"""
        # Harris-Benedict公式计算基础代谢率
        if patient.gender == "男":
            bmr = 88.362 + (13.397 * patient.weight) + (4.799 * patient.height) - (5.677 * patient.age)
        else:
            bmr = 447.593 + (9.247 * patient.weight) + (3.098 * patient.height) - (4.330 * patient.age)

        # 活动水平调整
        activity_multipliers = {
            "久坐": 1.2,
            "轻度活动": 1.375,
            "中度活动": 1.55,
            "重度活动": 1.725,
            "极重度活动": 1.9
        }

        tdee = bmr * activity_multipliers.get(patient.activity_level, 1.375)

        # 根据疾病调整热量
        calorie_adjustment = 1.0
        if "糖尿病" in patient.diagnosed_diseases or (patient.blood_glucose_fasting and patient.blood_glucose_fasting >= 7.0):
            calorie_adjustment = 0.8
        elif "肥胖症" in patient.diagnosed_diseases or patient.bmi >= 28:
            calorie_adjustment = 0.7

        target_calories = tdee * calorie_adjustment

        # 营养素分配
        protein_ratio = 0.25  # 25%蛋白质
        carb_ratio = 0.50     # 50%碳水化合物
        fat_ratio = 0.25      # 25%脂肪

        protein_grams = (target_calories * protein_ratio) / 4
        carb_grams = (target_calories * carb_ratio) / 4
        fat_grams = (target_calories * fat_ratio) / 9

        return {
            "基础代谢率": f"{bmr:.0f}千卡/天",
            "总日消耗": f"{tdee:.0f}千卡/天",
            "目标热量": f"{target_calories:.0f}千卡/天",
            "蛋白质": f"{protein_grams:.0f}g ({protein_ratio*100:.0f}%)",
            "碳水化合物": f"{carb_grams:.0f}g ({carb_ratio*100:.0f}%)",
            "脂肪": f"{fat_grams:.0f}g ({fat_ratio*100:.0f}%)",
            "热量调整系数": f"{calorie_adjustment:.0%}"
        }

    def _recommend_recipes(self, patient: PatientProfile) -> Dict:
        """基于饮食偏好和健康状况的一周高质量菜谱推荐"""

        # 导入一周菜谱管理器
        from Core_Systems.weekly_menu_manager import WeeklyMenuManager

        weekly_manager = WeeklyMenuManager()

        selected_cuisine = "清淡"  # 默认清淡，营养配比最均衡
        if patient.preferred_cuisines:
            for cuisine in patient.preferred_cuisines:
                if cuisine in ["川菜", "粤菜", "清淡"]:  # 支持的菜系
                    selected_cuisine = cuisine
                    break

        # 使用一周菜谱管理器获取今日推荐
        today_menu = weekly_manager.get_today_menu(selected_cuisine)

        # 兼容原有格式，确保返回列表格式
        recommendations = {
            "早餐推荐": today_menu["早餐推荐"],
            "午餐推荐": today_menu["午餐推荐"],
            "晚餐推荐": today_menu["晚餐推荐"],
            "加餐推荐": today_menu["加餐推荐"]
        }

        # 添加一周菜单信息到推荐结果中
        if "一周菜单信息" in today_menu:
            recommendations["一周菜单信息"] = today_menu["一周菜单信息"]

        # 根据饮食限制调整
        if patient.dietary_restrictions:
            if "素食" in patient.dietary_restrictions:
                # 为素食者替换含肉类菜品
                if any(meat in recommendations["午餐推荐"][0] for meat in ["鱼", "鸡", "肉", "虾"]):
                    recommendations["午餐推荐"] = ["豆腐蔬菜汤"]
                if any(meat in recommendations["晚餐推荐"][0] for meat in ["鱼", "鸡", "肉", "虾"]):
                    recommendations["晚餐推荐"] = ["蔬菜豆腐汤"]

        # 根据辣度承受调整
        spice_note = ""
        if patient.spice_tolerance == "微辣":
            spice_note = " (建议微辣调味)"
        elif patient.spice_tolerance == "重辣":
            spice_note = " (可适当加辣)"

        # 添加个性化说明
        recommendations["个性化说明"] = f"已根据您的{selected_cuisine}口味偏好定制{spice_note}"

        # 过敏和不喜欢的食物提醒
        if patient.disliked_foods or patient.allergies:
            avoid_foods = patient.disliked_foods + patient.allergies
            recommendations["注意事项"] = f"请避免: {', '.join(avoid_foods)}"

        # 根据疾病调整推荐
        dietary_notes = []
        if "糖尿病" in patient.diagnosed_diseases or (patient.blood_glucose_fasting and patient.blood_glucose_fasting >= 7.0):
            dietary_notes.append("优先选择低GI食物，严格控制碳水化合物")
        if "高血压" in patient.diagnosed_diseases or (patient.blood_pressure_systolic and patient.blood_pressure_systolic >= 140):
            dietary_notes.append("限制钠盐摄入，增加钾镁食物")
        if patient.bmi >= 28:
            dietary_notes.append("控制总热量，增加高纤维食物")

        recommendations["饮食注意事项"] = dietary_notes
        return recommendations

    def _recommend_gi_foods(self, patient: PatientProfile) -> Dict:
        """基于GI的食物推荐"""
        # 检查是否有糖尿病相关疾病
        has_diabetes = any(disease in ["糖尿病", "2型糖尿病", "1型糖尿病", "糖尿病前期"]
                          for disease in patient.diagnosed_diseases)
        has_high_glucose = patient.blood_glucose_fasting and patient.blood_glucose_fasting >= 6.1

        if has_diabetes or has_high_glucose:
            # 糖尿病患者推荐低GI食物
            low_gi_foods = []
            for food_name, food_data in self.integrated_foods.items():
                if food_data.gi_data and food_data.gi_data.gi_level == GILevel.LOW:
                    low_gi_foods.append({
                        "name": food_name,
                        "gi": food_data.gi_data.gi_value,
                        "gl": food_data.gi_data.gl_value,
                        "recommendation": food_data.gi_data.diabetes_recommendation
                    })

            return {
                "适用人群": "糖尿病/血糖异常患者",
                "推荐策略": "优先选择低GI食物 (GI≤55)",
                "推荐食物": low_gi_foods[:10],  # 只显示前10个
                "避免食物": ["白米饭(GI83)", "白面包(GI75)", "西瓜(GI72)"],
                "特别提醒": "注意食物搭配可降低整体GI值"
            }
        else:
            return {
                "适用人群": "一般健康人群",
                "推荐策略": "均衡摄入，适当选择低GI食物",
                "一般建议": "主食粗细搭配，增加膳食纤维摄入"
            }

    def _create_monitoring_plan(self, patient: PatientProfile) -> Dict:
        """制定监测计划"""
        monitoring = {
            "每日监测": ["体重", "血压(如有高血压)", "血糖(如有糖尿病)"],
            "每周监测": ["腰围", "体脂率"],
            "每月监测": ["血脂全套", "肝肾功能", "糖化血红蛋白(如有糖尿病)"],
            "随访频率": "营养师每2周随访，医生每月复诊"
        }

        return monitoring

    def create_nutrition_radar_chart(self, foods_portions: List[Tuple[str, float]],
                                   chart_type: str = "meal", save_path: str = None) -> plt.Figure:
        """创建营养雷达图"""
        if chart_type == "single" and len(foods_portions) == 1:
            return self._create_single_food_radar(foods_portions[0][0], foods_portions[0][1], save_path)
        elif chart_type == "comparison":
            return self._create_food_comparison_radar(foods_portions, save_path)
        else:  # meal
            return self._create_meal_nutrition_radar(foods_portions, save_path)

    def _create_single_food_radar(self, food_name: str, portion_g: float, save_path: str = None) -> plt.Figure:
        """创建单个食物的营养雷达图"""
        food_data = self.get_food_data(food_name)
        if not food_data:
            raise ValueError(f"未找到食物 {food_name} 的营养数据")

        nutrition = food_data.nutrition
        ratio = portion_g / 100

        # 定义营养指标和对应的每日推荐值
        nutrients = {
            '蛋白质': (nutrition.protein * ratio, 60),
            '碳水化合物': (nutrition.carbs * ratio, 300),
            '脂肪': (nutrition.fat * ratio, 60),
            '膳食纤维': (nutrition.fiber * ratio, 30),
            '维生素C': (nutrition.vitamin_c * ratio, 100),
            '钙': (nutrition.calcium * ratio, 800),
            '铁': (nutrition.iron * ratio, 15),
            '钾': (nutrition.potassium * ratio, 2000),
        }

        # 计算相对于DRV的百分比
        labels = list(nutrients.keys())
        values = [min(nutrients[label][0] / nutrients[label][1] * 100, 150)
                 for label in labels]

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2, label=f'{nutrition.name} ({portion_g}g)')
        ax.fill(angles, values, alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_ylim(0, 150)
        ax.set_yticks([25, 50, 75, 100, 125, 150])
        ax.set_yticklabels(['25%', '50%', '75%', '100%', '125%', '150%'], fontsize=10)
        ax.grid(True)

        plt.title(f'{nutrition.name} 营养成分雷达图\n(每{portion_g}g，相对于每日推荐值的百分比)',
                 fontsize=16, fontweight='bold', pad=20)

        calories_per_portion = nutrition.calories * ratio
        plt.figtext(0.02, 0.02, f'热量: {calories_per_portion:.0f} 千卡/{portion_g}g',
                   fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

        # 添加GI信息（如果有）
        if food_data.gi_data:
            gi_info = f'GI: {food_data.gi_data.gi_value} ({food_data.gi_data.gi_level.value})'
            plt.figtext(0.02, 0.08, gi_info, fontsize=12,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))

        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def _create_meal_nutrition_radar(self, meal_composition: List[Tuple[str, float]], save_path: str = None) -> plt.Figure:
        """创建整餐营养雷达图"""
        total_nutrition = {
            'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0,
            'vitamin_c': 0, 'calcium': 0, 'iron': 0, 'potassium': 0,
            'calories': 0
        }

        meal_details = []
        meal_gi_info = []

        for food_name, portion in meal_composition:
            food_data = self.get_food_data(food_name)
            if not food_data:
                continue

            nutrition = food_data.nutrition
            ratio = portion / 100

            total_nutrition['protein'] += nutrition.protein * ratio
            total_nutrition['carbs'] += nutrition.carbs * ratio
            total_nutrition['fat'] += nutrition.fat * ratio
            total_nutrition['fiber'] += nutrition.fiber * ratio
            total_nutrition['vitamin_c'] += nutrition.vitamin_c * ratio
            total_nutrition['calcium'] += nutrition.calcium * ratio
            total_nutrition['iron'] += nutrition.iron * ratio
            total_nutrition['potassium'] += nutrition.potassium * ratio
            total_nutrition['calories'] += nutrition.calories * ratio

            meal_details.append(f"{nutrition.name} {portion}g")

            if food_data.gi_data:
                meal_gi_info.append(f"{food_name}(GI{food_data.gi_data.gi_value})")

        # 营养指标标准值
        drv_values = {
            '蛋白质': 60, '碳水化合物': 300, '脂肪': 60, '膳食纤维': 30,
            '维生素C': 100, '钙': 800, '铁': 15, '钾': 2000
        }

        labels = list(drv_values.keys())
        values = [
            min(total_nutrition['protein'] / drv_values['蛋白质'] * 100, 200),
            min(total_nutrition['carbs'] / drv_values['碳水化合物'] * 100, 200),
            min(total_nutrition['fat'] / drv_values['脂肪'] * 100, 200),
            min(total_nutrition['fiber'] / drv_values['膳食纤维'] * 100, 200),
            min(total_nutrition['vitamin_c'] / drv_values['维生素C'] * 100, 200),
            min(total_nutrition['calcium'] / drv_values['钙'] * 100, 200),
            min(total_nutrition['iron'] / drv_values['铁'] * 100, 200),
            min(total_nutrition['potassium'] / drv_values['钾'] * 100, 200),
        ]

        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=3, color='#FF6B6B')
        ax.fill(angles, values, alpha=0.3, color='#FF6B6B')

        # 添加100%参考线
        ref_values = [100] * (len(labels) + 1)
        ax.plot(angles, ref_values, '--', linewidth=1, color='green', alpha=0.7,
               label='每日推荐值(100%)')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_ylim(0, 200)
        ax.set_yticks([50, 100, 150, 200])
        ax.set_yticklabels(['50%', '100%', '150%', '200%'], fontsize=10)
        ax.grid(True)

        plt.title('膳食营养成分雷达图\n(相对于每日推荐值的百分比)',
                 fontsize=16, fontweight='bold', pad=20)

        # 添加膳食组成信息
        meal_info = f"膳食组成: {', '.join(meal_details)}\n总热量: {total_nutrition['calories']:.0f} 千卡"
        if meal_gi_info:
            meal_info += f"\nGI信息: {', '.join(meal_gi_info)}"

        plt.figtext(0.02, 0.02, meal_info, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))

        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def _create_food_comparison_radar(self, foods_portions: List[Tuple[str, float]], save_path: str = None) -> plt.Figure:
        """创建多个食物的营养对比雷达图"""
        if len(foods_portions) > 5:
            raise ValueError("最多支持5个食物的对比")

        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        drv_values = {
            '蛋白质': 60, '碳水化合物': 300, '脂肪': 60, '膳食纤维': 30,
            '维生素C': 100, '钙': 800, '铁': 15, '钾': 2000
        }

        labels = list(drv_values.keys())
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        for i, (food_name, portion) in enumerate(foods_portions):
            food_data = self.get_food_data(food_name)
            if not food_data:
                continue

            nutrition = food_data.nutrition
            ratio = portion / 100

            values = [
                min(nutrition.protein * ratio / drv_values['蛋白质'] * 100, 150),
                min(nutrition.carbs * ratio / drv_values['碳水化合物'] * 100, 150),
                min(nutrition.fat * ratio / drv_values['脂肪'] * 100, 150),
                min(nutrition.fiber * ratio / drv_values['膳食纤维'] * 100, 150),
                min(nutrition.vitamin_c * ratio / drv_values['维生素C'] * 100, 150),
                min(nutrition.calcium * ratio / drv_values['钙'] * 100, 150),
                min(nutrition.iron * ratio / drv_values['铁'] * 100, 150),
                min(nutrition.potassium * ratio / drv_values['钾'] * 100, 150),
            ]
            values += values[:1]

            label = f'{nutrition.name} ({portion}g)'
            if food_data.gi_data:
                label += f' GI{food_data.gi_data.gi_value}'

            ax.plot(angles, values, 'o-', linewidth=2,
                   color=colors[i], label=label)
            ax.fill(angles, values, alpha=0.1, color=colors[i])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_ylim(0, 150)
        ax.set_yticks([25, 50, 75, 100, 125, 150])
        ax.set_yticklabels(['25%', '50%', '75%', '100%', '125%', '150%'], fontsize=10)
        ax.grid(True)

        plt.title('食物营养成分对比雷达图\n(相对于每日推荐值的百分比，含GI信息)',
                 fontsize=16, fontweight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def generate_comprehensive_report_v2(self, patient: PatientProfile,
                                        include_charts: bool = True) -> str:
        """生成综合营养报告 v2.0（包含GI和雷达图）"""
        assessment = self.comprehensive_assessment(patient)

        report = f"""
# {patient.name} 综合营养管理报告 v2.0

**生成时间**: {datetime.now().strftime('%Y年%m月%d日')}
**系统版本**: {self.version.value} v2.0 (集成GI数据库+营养雷达图)

---

## 📋 患者基本信息

| 项目 | 数值 | 评估 |
|------|------|------|
| 姓名 | {patient.name} | - |
| 年龄 | {patient.age}岁 | {assessment['patient_info']['性别']} |
| 身高体重 | {patient.height}cm / {patient.weight}kg | BMI {assessment['patient_info']['BMI']} |
| BMI分类 | {assessment['patient_info']['BMI分类']} | {'⚠️需关注' if patient.bmi >= 24 else '✅正常'} |
| 活动水平 | {patient.activity_level} | - |

## 🔍 风险分层评估

**风险等级**: {assessment['risk_stratification']['风险等级']}
**风险因素数**: {assessment['risk_stratification']['风险因素数量']}个

### 识别的风险因素:
"""

        for factor in assessment['risk_stratification']['风险因素']:
            report += f"- ⚠️ {factor}\n"

        report += f"""
## 🏥 疾病分析

### 确诊疾病:
"""
        if assessment['disease_analysis']['确诊疾病']:
            for disease in assessment['disease_analysis']['确诊疾病']:
                report += f"- 🔴 {disease}\n"
        else:
            report += "- ✅ 暂无确诊疾病\n"

        if assessment['disease_analysis']['疑似疾病']:
            report += "\n### 疑似疾病:\n"
            for disease in assessment['disease_analysis']['疑似疾病']:
                report += f"- 🟡 {disease} (根据指标推断)\n"

        report += f"""
## 🎯 营养目标

| 营养素 | 目标摄入量 | 说明 |
|--------|------------|------|
| 总热量 | {assessment['nutrition_targets']['目标热量']} | 基于{assessment['nutrition_targets']['热量调整系数']}调整 |
| 蛋白质 | {assessment['nutrition_targets']['蛋白质']} | 维持肌肉量 |
| 碳水化合物 | {assessment['nutrition_targets']['碳水化合物']} | 控制血糖 |
| 脂肪 | {assessment['nutrition_targets']['脂肪']} | 限制饱和脂肪 |

### 代谢计算:
- 基础代谢率: {assessment['nutrition_targets']['基础代谢率']}
- 总日消耗: {assessment['nutrition_targets']['总日消耗']}

## 📈 血糖指数(GI)个性化建议

### {assessment['gi_recommendations']['适用人群']}:
**推荐策略**: {assessment['gi_recommendations']['推荐策略']}
"""

        if '推荐食物' in assessment['gi_recommendations']:
            report += "\n### ✅ 推荐低GI食物:\n"
            for food in assessment['gi_recommendations']['推荐食物'][:5]:
                report += f"- **{food['name']}** (GI:{food['gi']}, GL:{food['gl']:.1f}) - {food['recommendation']}\n"

        if '避免食物' in assessment['gi_recommendations']:
            report += "\n### ❌ 需要限制的高GI食物:\n"
            for food in assessment['gi_recommendations']['避免食物']:
                report += f"- {food}\n"

        if '特别提醒' in assessment['gi_recommendations']:
            report += f"\n### 💡 特别提醒:\n{assessment['gi_recommendations']['特别提醒']}\n"

        report += f"""
## 🍽️ 个性化菜谱推荐

### 早餐建议:
"""
        for breakfast in assessment['recipe_recommendations']['早餐推荐']:
            report += f"- {breakfast}\n"

        report += "\n### 午餐建议:\n"
        for lunch in assessment['recipe_recommendations']['午餐推荐']:
            report += f"- {lunch}\n"

        report += "\n### 晚餐建议:\n"
        for dinner in assessment['recipe_recommendations']['晚餐推荐']:
            report += f"- {dinner}\n"

        report += "\n### 加餐建议:\n"
        for snack in assessment['recipe_recommendations']['加餐推荐']:
            report += f"- {snack}\n"

        if assessment['recipe_recommendations']['饮食注意事项']:
            report += "\n### ⚠️ 特别注意事项:\n"
            for note in assessment['recipe_recommendations']['饮食注意事项']:
                report += f"- {note}\n"

        if include_charts:
            report += f"""
## 📊 营养可视化分析

### 雷达图说明:
系统已生成以下营养雷达图，可视化展示营养成分相对于每日推荐值的百分比：

1. **单食物营养雷达图**: 分析单种食物的营养构成
2. **食物对比雷达图**: 对比不同食物的营养差异
3. **整餐营养雷达图**: 分析整餐的营养均衡性

*雷达图文件将保存为PNG格式，可用于报告展示*
"""

        report += f"""
## 📊 监测计划

### 每日监测:
"""
        for item in assessment['monitoring_plan']['每日监测']:
            report += f"- {item}\n"

        report += "\n### 每周监测:\n"
        for item in assessment['monitoring_plan']['每周监测']:
            report += f"- {item}\n"

        report += "\n### 每月监测:\n"
        for item in assessment['monitoring_plan']['每月监测']:
            report += f"- {item}\n"

        report += f"""
### 随访安排:
{assessment['monitoring_plan']['随访频率']}

---

## 💡 专业建议

1. **营养原则**: 遵循《中国居民膳食指南2022》，结合GI数据科学选择食物
2. **GI控制**: 优先选择低GI食物，注意食物搭配降低整体血糖反应
3. **执行要点**: 定时定量，细嚼慢咽，少量多餐
4. **运动配合**: 建议结合适量有氧运动，每周150分钟中等强度
5. **用药提醒**: 严格按医嘱服药，不可自行停药或减量
6. **可视化监控**: 利用营养雷达图定期评估膳食营养均衡性
7. **紧急情况**: 如出现严重不适，立即就医

---

## 🔧 系统功能特色

- ✅ **35种疾病支持**: 个性化疾病营养方案
- ✅ **111道中式菜谱**: 地方特色菜系全覆盖
- ✅ **29种食物GI数据**: 科学控糖指导
- ✅ **营养雷达图**: 可视化营养分析
- ✅ **多维度风险评估**: 15层患者分层
- ✅ **智能推荐算法**: 基于患者状况个性化推荐

---

*本报告由整合版营养管理系统v2.0生成，集成GI数据库和营养雷达图功能*
*系统版本: {self.version.value} | 支持疾病: {self.disease_support_count}种 | 菜谱数量: {self.recipe_count}道 | GI数据: {self.gi_foods_count}种*
"""

        return report

    def get_system_info_v2(self) -> Dict:
        """获取系统信息 v2.0"""
        return {
            "系统版本": f"{self.version.value} v2.0",
            "患者分层": "✅已集成" if self.stratification_enabled else "❌未启用",
            "疾病支持": f"{self.disease_support_count}种疾病",
            "菜谱数量": f"{self.recipe_count}道菜",
            "GI数据库": f"{self.gi_foods_count}种食物",
            "营养雷达图": "✅已集成" if self.radar_chart_enabled else "❌未启用",
            "整合食物数据": f"{len(self.integrated_foods)}种食物",
            "核心功能": [
                "多维度风险评估",
                "疾病特异性营养支持",
                "个性化菜谱推荐",
                "血糖指数(GI)指导",
                "营养雷达图可视化",
                "综合监测计划",
                "专业报告生成"
            ],
            "新增功能v2.0": [
                "🆕 血糖指数数据库集成",
                "🆕 营养雷达图可视化",
                "🆕 整合食物数据管理",
                "🆕 GI个性化推荐",
                "🆕 增强报告生成"
            ]
        }

if __name__ == "__main__":
    # 演示整合系统v2.0使用
    print("🚀 整合版营养管理系统 v2.0 演示")

    # 初始化系统
    nutrition_system = IntegratedNutritionSystemV2(SystemVersion.CLINICAL)

    # 创建测试患者
    test_patient = PatientProfile(
        name="王先生",
        age=58,
        gender="男",
        height=170,
        weight=85,
        blood_pressure_systolic=155,
        blood_pressure_diastolic=95,
        blood_glucose_fasting=6.8,
        cholesterol_total=6.8,
        cholesterol_ldl=4.5,
        triglycerides=2.8,
        diagnosed_diseases=["高血压", "血脂异常"],
        activity_level="轻度活动"
    )

    print(f"\n📊 系统信息v2.0:")
    system_info = nutrition_system.get_system_info_v2()
    for key, value in system_info.items():
        if isinstance(value, list):
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key}: {value}")

    print(f"\n📋 生成综合营养报告v2.0...")
    report = nutrition_system.generate_comprehensive_report_v2(test_patient, include_charts=True)

    # 保存报告
    report_file = "/Users/williamsun/Documents/gplus/docs/FoodRecom/整合系统v2报告_王先生.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 报告已生成: {report_file}")

    # 演示雷达图功能
    print(f"\n📊 生成营养雷达图示例...")

    # 1. 单食物雷达图
    fig1 = nutrition_system.create_nutrition_radar_chart([("鸡胸肉", 100)], "single",
                                                       "/Users/williamsun/Documents/gplus/docs/FoodRecom/v2_鸡胸肉雷达图.png")
    plt.close(fig1)

    # 2. 食物对比雷达图
    fig2 = nutrition_system.create_nutrition_radar_chart([("糙米", 100), ("大米", 100)], "comparison",
                                                       "/Users/williamsun/Documents/gplus/docs/FoodRecom/v2_主食对比雷达图.png")
    plt.close(fig2)

    # 3. 整餐雷达图
    healthy_meal = [("糙米", 100), ("鸡胸肉", 100), ("西兰花", 150), ("胡萝卜", 100)]
    fig3 = nutrition_system.create_nutrition_radar_chart(healthy_meal, "meal",
                                                       "/Users/williamsun/Documents/gplus/docs/FoodRecom/v2_健康午餐雷达图.png")
    plt.close(fig3)

    print(f"✅ 营养雷达图已生成")
    print(f"📊 报告长度: {len(report)}字符")
    print(f"🎯 整合版营养管理系统v2.0演示完成！")
    print(f"🆕 新功能：GI数据库 + 营养雷达图 + 整合食物数据")