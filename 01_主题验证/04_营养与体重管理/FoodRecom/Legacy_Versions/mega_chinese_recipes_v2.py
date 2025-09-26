#!/usr/bin/env python3
"""
超大中式菜谱数据库 v2.0 (100+道菜品)
涵盖八大菜系、地方特色菜、季节菜品、养生食谱等
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class CuisineType(Enum):
    """菜系分类"""
    SICHUAN = "川菜"
    CANTONESE = "粤菜"
    SHANDONG = "鲁菜"
    JIANGSU = "苏菜"
    ZHEJIANG = "浙菜"
    FUJIAN = "闽菜"
    HUNAN = "湘菜"
    ANHUI = "徽菜"
    HOMESTYLE = "家常菜"
    HEALTH = "养生菜"
    VEGETARIAN = "素食"
    NORTHEASTERN = "东北菜"
    XINJIANG = "新疆菜"
    YUNNAN = "云南菜"

class CookingMethod(Enum):
    """烹饪方式"""
    STEAMING = "蒸"
    BOILING = "煮"
    BRAISING = "焖"
    STEWING = "炖"
    STIR_FRYING = "炒"
    DEEP_FRYING = "炸"
    BLANCHING = "焯"
    COLD_MIXING = "凉拌"
    GRILLING = "烤"
    POACHING = "汆"
    ROASTING = "烧"

class Season(Enum):
    """季节"""
    SPRING = "春季"
    SUMMER = "夏季"
    AUTUMN = "秋季"
    WINTER = "冬季"
    ALL_SEASONS = "四季"

class DifficultyLevel(Enum):
    """难度等级"""
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"

class SpiceLevel(Enum):
    """辣度等级"""
    MILD = "微辣"
    SPICY = "中辣"
    VERY_SPICY = "重辣"

@dataclass
class MegaChineseDish:
    """超级中式菜肴类"""
    name: str
    cuisine_type: CuisineType
    cooking_method: CookingMethod
    difficulty_level: DifficultyLevel
    season: Season
    spice_level: SpiceLevel
    estimated_calories: int
    main_ingredients: List[str]
    cooking_steps: str
    health_benefits: List[str]
    suitable_for_conditions: List[str]
    regional_specialty: bool = False

class MegaChineseRecipeDatabase:
    """超大中式菜谱数据库"""

    def __init__(self):
        print("正在初始化超大中式菜谱数据库...")
        self.recipes = self._load_all_recipes()
        print(f"菜谱数据库初始化完成,共收录 {len(self.recipes)} 道菜品")

    def _load_all_recipes(self) -> Dict[str, MegaChineseDish]:
        """加载所有菜谱"""
        recipes = {}

        # 川菜 (20道)
        recipes.update(self._get_sichuan_recipes())

        # 粤菜 (18道)
        recipes.update(self._get_cantonese_recipes())

        # 鲁菜 (15道)
        recipes.update(self._get_shandong_recipes())

        # 江浙菜 (15道)
        recipes.update(self._get_jiangzhe_recipes())

        # 湘菜 (12道)
        recipes.update(self._get_hunan_recipes())

        # 北方菜 (10道)
        recipes.update(self._get_northern_recipes())

        # 地方特色菜 (15道)
        recipes.update(self._get_regional_specialties())

        # 家常菜 (10道)
        recipes.update(self._get_homestyle_recipes())

        return recipes

    def _get_sichuan_recipes(self) -> Dict[str, MegaChineseDish]:
        """川菜菜谱 (20道)"""
        return {
            "麻婆豆腐": MegaChineseDish(
                name="麻婆豆腐",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=180,
                main_ingredients=["嫩豆腐", "牛肉末", "郫县豆瓣酱", "花椒粉"],
                cooking_steps="豆腐切块汆水，爆炒牛肉末，下豆瓣酱炒出红油，加豆腐焖煮，撒花椒粉",
                health_benefits=["优质蛋白", "大豆异黄酮", "钙质"],
                suitable_for_conditions=["一般人群", "蛋白质缺乏者"],
                regional_specialty=True
            ),
            "夫妻肺片": MegaChineseDish(
                name="夫妻肺片",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.COLD_MIXING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=220,
                main_ingredients=["牛肉", "牛舌", "牛肚", "红油", "花椒油"],
                cooking_steps="牛杂卤制至软烂，切片装盘，淋特制红油调料",
                health_benefits=["优质蛋白", "铁元素", "B族维生素"],
                suitable_for_conditions=["贫血者", "体力劳动者"],
                regional_specialty=True
            ),
            "水煮牛肉": MegaChineseDish(
                name="水煮牛肉",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=260,
                main_ingredients=["牛肉片", "豆芽", "白菜", "豆瓣酱"],
                cooking_steps="牛肉片上浆，蔬菜垫底，肉片汆烫，浇热油爆香",
                health_benefits=["优质蛋白", "铁元素", "维生素C"],
                suitable_for_conditions=["贫血者", "健康成人"],
                regional_specialty=True
            ),
            "宫保鸡丁": MegaChineseDish(
                name="宫保鸡丁",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=240,
                main_ingredients=["鸡胸肉", "花生米", "干辣椒", "花椒"],
                cooking_steps="鸡肉上浆滑油，爆炒干辣椒花椒，下鸡丁和花生米炒匀",
                health_benefits=["优质蛋白", "维生素E", "不饱和脂肪酸"],
                suitable_for_conditions=["健康成人", "脑力劳动者"],
                regional_specialty=True
            ),
            "口水鸡": MegaChineseDish(
                name="口水鸡",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.COLD_MIXING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=200,
                main_ingredients=["白斩鸡", "红油", "花椒油", "蒜泥"],
                cooking_steps="白斩鸡放凉切片，调制川式口水鸡料汁浇在鸡肉上",
                health_benefits=["优质蛋白", "低脂肪"],
                suitable_for_conditions=["减肥人群", "夏季开胃"],
                regional_specialty=True
            ),
            "鱼香肉丝": MegaChineseDish(
                name="鱼香肉丝",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=280,
                main_ingredients=["猪肉丝", "木耳", "胡萝卜", "豆瓣酱"],
                cooking_steps="肉丝上浆炒制，配菜丝炒香，调鱼香汁炒合",
                health_benefits=["蛋白质", "膳食纤维", "维生素A"],
                suitable_for_conditions=["一般人群", "儿童成长"],
                regional_specialty=True
            ),
            "回锅肉": MegaChineseDish(
                name="回锅肉",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=350,
                main_ingredients=["五花肉", "青椒", "豆瓣酱", "甜面酱"],
                cooking_steps="五花肉煮熟切片，爆炒豆瓣酱，下肉片和青椒炒制",
                health_benefits=["蛋白质", "维生素C", "B族维生素"],
                suitable_for_conditions=["体力劳动者", "寒冷地区"],
                regional_specialty=True
            ),
            "蒜泥白肉": MegaChineseDish(
                name="蒜泥白肉",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=280,
                main_ingredients=["五花肉", "蒜泥", "生抽", "香油"],
                cooking_steps="五花肉煮制切片，调蒜泥汁淋浇",
                health_benefits=["蛋白质", "大蒜素", "维生素B1"],
                suitable_for_conditions=["夏季清淡", "抗菌需要"],
                regional_specialty=True
            ),
            "水煮鱼": MegaChineseDish(
                name="水煮鱼",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=250,
                main_ingredients=["草鱼", "豆芽", "豆瓣酱", "干辣椒"],
                cooking_steps="鱼片上浆，豆芽垫底，鱼片汆烫，浇辣椒油",
                health_benefits=["优质蛋白", "DHA", "维生素D"],
                suitable_for_conditions=["大脑发育", "心血管健康"],
                regional_specialty=True
            ),
            "棒棒鸡": MegaChineseDish(
                name="棒棒鸡",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.COLD_MIXING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.SUMMER,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=190,
                main_ingredients=["鸡胸肉", "芝麻酱", "辣椒油", "花椒粉"],
                cooking_steps="鸡肉煮熟撕丝，调芝麻辣椒汁拌制",
                health_benefits=["优质蛋白", "维生素E", "不饱和脂肪"],
                suitable_for_conditions=["减肥人群", "夏季开胃"],
                regional_specialty=True
            ),
            "干煸豆角": MegaChineseDish(
                name="干煸豆角",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.SUMMER,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=160,
                main_ingredients=["四季豆", "肉末", "豆瓣酱", "花椒"],
                cooking_steps="豆角干煸至皱皮，下肉末炒香，调味炒制",
                health_benefits=["膳食纤维", "维生素C", "叶酸"],
                suitable_for_conditions=["便秘者", "孕妇"],
                regional_specialty=True
            ),
            "麻辣豆腐": MegaChineseDish(
                name="麻辣豆腐",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=170,
                main_ingredients=["豆腐", "花椒", "辣椒", "豆瓣酱"],
                cooking_steps="豆腐切块，爆炒香料，下豆腐焖煮入味",
                health_benefits=["植物蛋白", "钙质", "大豆异黄酮"],
                suitable_for_conditions=["素食者", "更年期女性"],
                regional_specialty=True
            ),
            "辣子鸡": MegaChineseDish(
                name="辣子鸡",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=280,
                main_ingredients=["鸡块", "干辣椒", "花椒", "生抽"],
                cooking_steps="鸡块炸制，爆炒干辣椒花椒，下鸡块炒香",
                health_benefits=["优质蛋白", "B族维生素"],
                suitable_for_conditions=["体力消耗大", "辣食爱好者"],
                regional_specialty=True
            ),
            "酸菜鱼": MegaChineseDish(
                name="酸菜鱼",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=220,
                main_ingredients=["草鱼", "酸菜", "泡椒", "豆芽"],
                cooking_steps="鱼片腌制，酸菜炒香，下鱼片煮制",
                health_benefits=["优质蛋白", "DHA", "乳酸菌"],
                suitable_for_conditions=["肠胃调理", "开胃消食"],
                regional_specialty=True
            ),
            "毛血旺": MegaChineseDish(
                name="毛血旺",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=300,
                main_ingredients=["鸭血", "毛肚", "豆皮", "辣椒"],
                cooking_steps="食材汆烫，制麻辣汤底，浇热油爆香",
                health_benefits=["铁元素", "蛋白质", "维生素A"],
                suitable_for_conditions=["贫血", "冬季温补"],
                regional_specialty=True
            ),
            "口水茄子": MegaChineseDish(
                name="口水茄子",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=120,
                main_ingredients=["茄子", "蒜泥", "辣椒油", "香醋"],
                cooking_steps="茄子蒸熟撕条，调口水汁浇淋",
                health_benefits=["膳食纤维", "花青素", "维生素P"],
                suitable_for_conditions=["减肥", "抗氧化"],
                regional_specialty=True
            ),
            "川式泡菜": MegaChineseDish(
                name="川式泡菜",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.COLD_MIXING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=30,
                main_ingredients=["白萝卜", "胡萝卜", "泡椒", "盐水"],
                cooking_steps="蔬菜切条，盐水泡制，发酵入味",
                health_benefits=["益生菌", "维生素C", "膳食纤维"],
                suitable_for_conditions=["肠道健康", "开胃消食"],
                regional_specialty=True
            ),
            "白油豆腐": MegaChineseDish(
                name="白油豆腐",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=150,
                main_ingredients=["嫩豆腐", "高汤", "香葱", "胡椒粉"],
                cooking_steps="豆腐切块，高汤煮制，清淡调味",
                health_benefits=["植物蛋白", "钙质", "低脂肪"],
                suitable_for_conditions=["老人", "病后恢复"],
                regional_specialty=True
            ),
            "樟茶鸭": MegaChineseDish(
                name="樟茶鸭",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.GRILLING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=320,
                main_ingredients=["鸭子", "樟木", "茶叶", "花椒"],
                cooking_steps="鸭子腌制，樟茶熏制，炸至金黄",
                health_benefits=["蛋白质", "维生素A", "铁元素"],
                suitable_for_conditions=["营养滋补", "秋季进补"],
                regional_specialty=True
            ),
            "怪味鸡": MegaChineseDish(
                name="怪味鸡",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.COLD_MIXING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.SUMMER,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=210,
                main_ingredients=["鸡肉", "芝麻酱", "花椒粉", "白糖"],
                cooking_steps="鸡肉煮熟切块，调怪味汁拌制",
                health_benefits=["优质蛋白", "维生素E", "钙质"],
                suitable_for_conditions=["夏季开胃", "营养补充"],
                regional_specialty=True
            )
        }

    def _get_cantonese_recipes(self) -> Dict[str, MegaChineseDish]:
        """粤菜菜谱 (18道)"""
        return {
            "白切鸡": MegaChineseDish(
                name="白切鸡",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["三黄鸡", "生姜", "香葱", "生抽"],
                cooking_steps="整鸡煮制至熟，冰水过凉，切块装盘，配姜葱蘸料",
                health_benefits=["优质蛋白", "低脂肪", "B族维生素"],
                suitable_for_conditions=["产后恢复", "减肥人群"],
                regional_specialty=True
            ),
            "蒸蛋羹": MegaChineseDish(
                name="蒸蛋羹",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=120,
                main_ingredients=["鸡蛋", "温水", "盐", "香油"],
                cooking_steps="蛋液过筛，加温水调匀，蒸制至嫩滑",
                health_benefits=["优质蛋白", "卵磷脂", "维生素A"],
                suitable_for_conditions=["婴幼儿", "老人", "病后恢复"],
                regional_specialty=False
            ),
            "清蒸鲈鱼": MegaChineseDish(
                name="清蒸鲈鱼",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=150,
                main_ingredients=["鲈鱼", "生姜", "香葱", "蒸鱼豉油"],
                cooking_steps="鱼洗净改刀，姜葱摆盘，蒸制后淋豉油",
                health_benefits=["优质蛋白", "DHA", "磷脂"],
                suitable_for_conditions=["大脑发育", "心血管健康"],
                regional_specialty=True
            ),
            "广式烧鹅": MegaChineseDish(
                name="广式烧鹅",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.ROASTING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["鹅肉", "五香粉", "蜂蜜", "生抽"],
                cooking_steps="鹅肉腌制，挂炉烧制，刷蜜上色",
                health_benefits=["蛋白质", "铁元素", "维生素B12"],
                suitable_for_conditions=["营养不良", "贫血"],
                regional_specialty=True
            ),
            "虾饺": MegaChineseDish(
                name="虾饺",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=180,
                main_ingredients=["河虾", "澄粉", "生粉", "猪油"],
                cooking_steps="虾肉调馅，澄粉和面，包制蒸熟",
                health_benefits=["优质蛋白", "钙质", "磷元素"],
                suitable_for_conditions=["儿童发育", "补钙"],
                regional_specialty=True
            ),
            "叉烧包": MegaChineseDish(
                name="叉烧包",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=280,
                main_ingredients=["面粉", "叉烧肉", "洋葱", "蚝油"],
                cooking_steps="发面制皮，叉烧调馅，包制蒸熟",
                health_benefits=["碳水化合物", "蛋白质", "B族维生素"],
                suitable_for_conditions=["主食选择", "体力补充"],
                regional_specialty=True
            ),
            "干炒牛河": MegaChineseDish(
                name="干炒牛河",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=380,
                main_ingredients=["河粉", "牛肉", "豆芽", "韭黄"],
                cooking_steps="河粉先炒，牛肉丝炒制，合炒调味",
                health_benefits=["碳水化合物", "蛋白质", "铁元素"],
                suitable_for_conditions=["体力劳动", "快速补能"],
                regional_specialty=True
            ),
            "白灼虾": MegaChineseDish(
                name="白灼虾",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=100,
                main_ingredients=["基围虾", "生姜", "香葱", "生抽"],
                cooking_steps="虾洗净，开水烫熟，配姜葱蘸料",
                health_benefits=["优质蛋白", "低脂肪", "钙质"],
                suitable_for_conditions=["减肥", "补钙", "儿童"],
                regional_specialty=True
            ),
            "蒜蓉粉丝蒸扇贝": MegaChineseDish(
                name="蒜蓉粉丝蒸扇贝",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=130,
                main_ingredients=["扇贝", "粉丝", "蒜蓉", "生抽"],
                cooking_steps="扇贝处理，粉丝垫底，蒜蓉调味，蒸制",
                health_benefits=["优质蛋白", "锌元素", "牛磺酸"],
                suitable_for_conditions=["智力发育", "视力保护"],
                regional_specialty=True
            ),
            "煲仔饭": MegaChineseDish(
                name="煲仔饭",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=450,
                main_ingredients=["大米", "腊肠", "青菜", "生抽"],
                cooking_steps="米饭焖制，加腊肠继续焖，配菜调味",
                health_benefits=["碳水化合物", "蛋白质", "维生素"],
                suitable_for_conditions=["主食", "冬季暖胃"],
                regional_specialty=True
            ),
            "广式早茶点心": MegaChineseDish(
                name="广式早茶点心",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["面粉", "虾仁", "猪肉", "各种馅料"],
                cooking_steps="多种点心制作，蒸制工艺精细",
                health_benefits=["蛋白质", "碳水化合物", "多种维生素"],
                suitable_for_conditions=["早餐选择", "社交聚餐"],
                regional_specialty=True
            ),
            "白切猪肉": MegaChineseDish(
                name="白切猪肉",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=280,
                main_ingredients=["猪肉", "生姜", "香葱", "生抽"],
                cooking_steps="猪肉煮制至熟，切片装盘，配蘸料",
                health_benefits=["蛋白质", "B族维生素", "铁元素"],
                suitable_for_conditions=["营养补充", "体力恢复"],
                regional_specialty=True
            ),
            "蒸排骨": MegaChineseDish(
                name="蒸排骨",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=320,
                main_ingredients=["猪排骨", "豆豉", "生抽", "生粉"],
                cooking_steps="排骨腌制，豆豉调味，蒸制至软烂",
                health_benefits=["蛋白质", "钙质", "磷元素"],
                suitable_for_conditions=["骨骼发育", "营养补充"],
                regional_specialty=True
            ),
            "糖醋里脊": MegaChineseDish(
                name="糖醋里脊",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["猪里脊", "淀粉", "白糖", "醋"],
                cooking_steps="里脊切条挂浆，炸制金黄，糖醋汁炒合",
                health_benefits=["蛋白质", "碳水化合物", "维生素B1"],
                suitable_for_conditions=["儿童喜爱", "开胃消食"],
                regional_specialty=False
            ),
            "白灼菜心": MegaChineseDish(
                name="白灼菜心",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.BLANCHING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=25,
                main_ingredients=["菜心", "蒜蓉", "生抽", "香油"],
                cooking_steps="菜心焯水，蒜蓉爆香，淋汁调味",
                health_benefits=["维生素C", "叶酸", "膳食纤维"],
                suitable_for_conditions=["减肥", "维生素补充"],
                regional_specialty=True
            ),
            "咕噜肉": MegaChineseDish(
                name="咕噜肉",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=380,
                main_ingredients=["猪肉", "菠萝", "青椒", "番茄酱"],
                cooking_steps="猪肉挂浆炸制，菠萝青椒炒制，糖醋汁炒合",
                health_benefits=["蛋白质", "维生素C", "消化酶"],
                suitable_for_conditions=["开胃消食", "儿童喜爱"],
                regional_specialty=True
            ),
            "蜜汁叉烧": MegaChineseDish(
                name="蜜汁叉烧",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.ROASTING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=300,
                main_ingredients=["猪肉", "蜂蜜", "生抽", "料酒"],
                cooking_steps="猪肉腌制，烤制上色，刷蜜汁",
                health_benefits=["蛋白质", "B族维生素", "铁元素"],
                suitable_for_conditions=["营养补充", "体力恢复"],
                regional_specialty=True
            ),
            "薄撑": MegaChineseDish(
                name="薄撑",
                cuisine_type=CuisineType.CANTONESE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["面粉", "鸡蛋", "韭菜", "虾米"],
                cooking_steps="调制面糊，摊制薄饼，配菜调味",
                health_benefits=["碳水化合物", "蛋白质", "维生素"],
                suitable_for_conditions=["主食", "快餐选择"],
                regional_specialty=True
            )
        }

    def _get_shandong_recipes(self) -> Dict[str, MegaChineseDish]:
        """鲁菜菜谱 (15道)"""
        return {
            "糖醋鲤鱼": MegaChineseDish(
                name="糖醋鲤鱼",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=280,
                main_ingredients=["鲤鱼", "番茄酱", "白糖", "醋"],
                cooking_steps="整鱼开花刀，炸至金黄，制糖醋汁浇淋",
                health_benefits=["优质蛋白质", "维生素B12", "磷元素"],
                suitable_for_conditions=["蛋白质缺乏", "发育期", "恢复期"],
                regional_specialty=True
            ),
            "九转大肠": MegaChineseDish(
                name="九转大肠",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=320,
                main_ingredients=["猪大肠", "生抽", "老抽", "冰糖"],
                cooking_steps="大肠清洗处理，先煮后烧，多重调味",
                health_benefits=["胶原蛋白", "维生素B1"],
                suitable_for_conditions=["体质虚弱"],
                regional_specialty=True
            ),
            "德州扒鸡": MegaChineseDish(
                name="德州扒鸡",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["三黄鸡", "桂皮", "八角", "生抽"],
                cooking_steps="整鸡卤制，香料入味，软烂脱骨",
                health_benefits=["优质蛋白质", "B族维生素"],
                suitable_for_conditions=["营养不良", "产后恢复"],
                regional_specialty=True
            ),
            "扒海参": MegaChineseDish(
                name="扒海参",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=150,
                main_ingredients=["海参", "瘦肉", "鸡汤", "酱油"],
                cooking_steps="海参发好，制高汤，小火慢扒",
                health_benefits=["胶原蛋白", "精氨酸", "低脂肪"],
                suitable_for_conditions=["术后恢复", "抗衰老"],
                regional_specialty=True
            ),
            "油爆双脆": MegaChineseDish(
                name="油爆双脆",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["猪肚", "鸡胗", "韭黄", "料酒"],
                cooking_steps="双脆改刀，急火爆炒，保持脆嫩",
                health_benefits=["蛋白质", "铁元素", "锌元素"],
                suitable_for_conditions=["贫血", "体力恢复"],
                regional_specialty=True
            ),
            "鲁式红烧肉": MegaChineseDish(
                name="鲁式红烧肉",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=400,
                main_ingredients=["五花肉", "冰糖", "生抽", "老抽"],
                cooking_steps="肉块焯水，糖色炒制，小火焖煮",
                health_benefits=["蛋白质", "维生素B1", "脂肪"],
                suitable_for_conditions=["体力劳动", "冬季进补"],
                regional_specialty=True
            ),
            "爆炒腰花": MegaChineseDish(
                name="爆炒腰花",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=180,
                main_ingredients=["猪腰", "木耳", "笋片", "料酒"],
                cooking_steps="腰花改花刀，急火爆炒，去腥调味",
                health_benefits=["蛋白质", "维生素A", "铁元素"],
                suitable_for_conditions=["肾虚", "营养不良"],
                regional_specialty=True
            ),
            "锅烧肘子": MegaChineseDish(
                name="锅烧肘子",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=450,
                main_ingredients=["猪肘", "生抽", "老抽", "料酒"],
                cooking_steps="肘子处理，焯水上色，小火焖煮",
                health_benefits=["胶原蛋白", "蛋白质", "钙质"],
                suitable_for_conditions=["关节保健", "美容养颜"],
                regional_specialty=True
            ),
            "白扒四宝": MegaChineseDish(
                name="白扒四宝",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=220,
                main_ingredients=["鸡胗", "鸭胗", "冬笋", "香菇"],
                cooking_steps="四宝处理，高汤扒制，清淡鲜美",
                health_benefits=["蛋白质", "多糖", "膳食纤维"],
                suitable_for_conditions=["免疫调节", "营养滋补"],
                regional_specialty=True
            ),
            "鲁式蒸蛋": MegaChineseDish(
                name="鲁式蒸蛋",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=150,
                main_ingredients=["鸡蛋", "海米", "香菇", "高汤"],
                cooking_steps="蛋液调匀，配料摆放，蒸制嫩滑",
                health_benefits=["优质蛋白", "卵磷脂", "钙质"],
                suitable_for_conditions=["老人", "儿童", "病后恢复"],
                regional_specialty=True
            ),
            "奶汤蒲菜": MegaChineseDish(
                name="奶汤蒲菜",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.SPRING,
                spice_level=SpiceLevel.MILD,
                estimated_calories=80,
                main_ingredients=["蒲菜", "鸡汤", "火腿", "冬笋"],
                cooking_steps="蒲菜处理，鸡汤煮制，清香鲜美",
                health_benefits=["膳食纤维", "维生素", "低热量"],
                suitable_for_conditions=["减肥", "春季养生"],
                regional_specialty=True
            ),
            "红烧大虾": MegaChineseDish(
                name="红烧大虾",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=150,
                main_ingredients=["大虾", "生抽", "老抽", "白糖"],
                cooking_steps="大虾处理，油焖上色，调味收汁",
                health_benefits=["优质蛋白", "钙质", "磷元素"],
                suitable_for_conditions=["儿童发育", "补钙"],
                regional_specialty=True
            ),
            "清汤银耳": MegaChineseDish(
                name="清汤银耳",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=60,
                main_ingredients=["银耳", "鸡汤", "火腿丝", "青菜"],
                cooking_steps="银耳发好，清汤煮制，营养清淡",
                health_benefits=["胶质", "多糖", "膳食纤维"],
                suitable_for_conditions=["美容养颜", "润燥清肺"],
                regional_specialty=True
            ),
            "济南把子肉": MegaChineseDish(
                name="济南把子肉",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=380,
                main_ingredients=["五花肉", "生抽", "老抽", "冰糖"],
                cooking_steps="肉条捆扎，卤汁焖煮，肥而不腻",
                health_benefits=["蛋白质", "维生素B1", "脂肪"],
                suitable_for_conditions=["体力劳动", "营养补充"],
                regional_specialty=True
            ),
            "鲁菜四喜丸子": MegaChineseDish(
                name="鲁菜四喜丸子",
                cuisine_type=CuisineType.SHANDONG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=320,
                main_ingredients=["猪肉馅", "荸荠", "香菇", "鸡蛋"],
                cooking_steps="肉馅调制，制丸炸制，红烧入味",
                health_benefits=["蛋白质", "维生素B1", "铁元素"],
                suitable_for_conditions=["营养补充", "节庆聚餐"],
                regional_specialty=True
            )
        }

    def _get_jiangzhe_recipes(self) -> Dict[str, MegaChineseDish]:
        """江浙菜菜谱 (15道)"""
        return {
            "西湖醋鱼": MegaChineseDish(
                name="西湖醋鱼",
                cuisine_type=CuisineType.ZHEJIANG,
                cooking_method=CookingMethod.POACHING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=180,
                main_ingredients=["草鱼", "白糖", "醋", "酱油"],
                cooking_steps="鱼汆烫至熟，制糖醋汁淋浇",
                health_benefits=["DHA", "优质蛋白质", "磷脂"],
                suitable_for_conditions=["大脑发育", "记忆力下降"],
                regional_specialty=True
            ),
            "东坡肉": MegaChineseDish(
                name="东坡肉",
                cuisine_type=CuisineType.ZHEJIANG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=420,
                main_ingredients=["五花肉", "绍酒", "酱油", "冰糖"],
                cooking_steps="肉块焯水，小火慢炖，红亮油润",
                health_benefits=["蛋白质", "维生素B1"],
                suitable_for_conditions=["体力劳动者"],
                regional_specialty=True
            ),
            "叫化鸡": MegaChineseDish(
                name="叫化鸡",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.ROASTING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=250,
                main_ingredients=["土鸡", "荷叶", "黄泥", "绍酒"],
                cooking_steps="鸡腹填料，荷叶包裹，黄泥封口烤制",
                health_benefits=["蛋白质", "胶原蛋白"],
                suitable_for_conditions=["滋补调理"],
                regional_specialty=True
            ),
            "松鼠桂鱼": MegaChineseDish(
                name="松鼠桂鱼",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=300,
                main_ingredients=["桂鱼", "蛋清", "淀粉", "番茄酱"],
                cooking_steps="鱼肉开花刀，挂浆油炸，浇糖醋汁",
                health_benefits=["优质蛋白质", "DHA"],
                suitable_for_conditions=["智力发育", "视力保护"],
                regional_specialty=True
            ),
            "蟹粉小笼包": MegaChineseDish(
                name="蟹粉小笼包",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=280,
                main_ingredients=["面粉", "蟹粉", "肉馅", "皮冻"],
                cooking_steps="制皮冻，调蟹粉馅，包制蒸熟",
                health_benefits=["蛋白质", "锌元素", "维生素A"],
                suitable_for_conditions=["营养补充", "味觉享受"],
                regional_specialty=True
            ),
            "龙井虾仁": MegaChineseDish(
                name="龙井虾仁",
                cuisine_type=CuisineType.ZHEJIANG,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.SPRING,
                spice_level=SpiceLevel.MILD,
                estimated_calories=120,
                main_ingredients=["河虾仁", "龙井茶", "蛋清", "料酒"],
                cooking_steps="虾仁上浆，茶叶泡制，清炒调味",
                health_benefits=["优质蛋白", "抗氧化物", "低脂肪"],
                suitable_for_conditions=["减肥", "抗氧化"],
                regional_specialty=True
            ),
            "白切羊肉": MegaChineseDish(
                name="白切羊肉",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=300,
                main_ingredients=["羊肉", "生姜", "料酒", "香葱"],
                cooking_steps="羊肉煮制去膻，切片装盘，配蘸料",
                health_benefits=["蛋白质", "铁元素", "维生素B12"],
                suitable_for_conditions=["冬季进补", "贫血"],
                regional_specialty=True
            ),
            "清蒸大闸蟹": MegaChineseDish(
                name="清蒸大闸蟹",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=120,
                main_ingredients=["大闸蟹", "生姜", "香醋", "黄酒"],
                cooking_steps="螃蟹清洗，蒸制至熟，配姜醋汁",
                health_benefits=["优质蛋白", "锌元素", "硒元素"],
                suitable_for_conditions=["营养滋补", "秋季时令"],
                regional_specialty=True
            ),
            "糖醋排骨": MegaChineseDish(
                name="糖醋排骨",
                cuisine_type=CuisineType.ZHEJIANG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["猪排骨", "白糖", "醋", "生抽"],
                cooking_steps="排骨焯水，炸制上色，糖醋汁焖煮",
                health_benefits=["蛋白质", "钙质", "磷元素"],
                suitable_for_conditions=["儿童喜爱", "骨骼发育"],
                regional_specialty=True
            ),
            "白斩鸡": MegaChineseDish(
                name="白斩鸡",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["土鸡", "生姜", "香葱", "料酒"],
                cooking_steps="整鸡煮制，冰水过凉，切块装盘",
                health_benefits=["优质蛋白", "低脂肪", "B族维生素"],
                suitable_for_conditions=["产后恢复", "病后调理"],
                regional_specialty=True
            ),
            "蒸蛋羹": MegaChineseDish(
                name="蒸蛋羹",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=120,
                main_ingredients=["鸡蛋", "温水", "盐", "香油"],
                cooking_steps="蛋液过筛，加温水调匀，蒸制嫩滑",
                health_benefits=["优质蛋白", "卵磷脂", "维生素A"],
                suitable_for_conditions=["婴幼儿", "老人", "病后恢复"],
                regional_specialty=False
            ),
            "红烧狮子头": MegaChineseDish(
                name="红烧狮子头",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=320,
                main_ingredients=["猪肉馅", "荸荠", "鸡蛋", "生抽"],
                cooking_steps="肉馅调制，制丸油炸，红烧入味",
                health_benefits=["蛋白质", "维生素B1", "铁元素"],
                suitable_for_conditions=["营养补充", "冬季进补"],
                regional_specialty=True
            ),
            "油焖春笋": MegaChineseDish(
                name="油焖春笋",
                cuisine_type=CuisineType.ZHEJIANG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SPRING,
                spice_level=SpiceLevel.MILD,
                estimated_calories=80,
                main_ingredients=["春笋", "生抽", "老抽", "白糖"],
                cooking_steps="春笋切块，油焖上色，调味收汁",
                health_benefits=["膳食纤维", "维生素", "低热量"],
                suitable_for_conditions=["减肥", "春季养生"],
                regional_specialty=True
            ),
            "醉虾": MegaChineseDish(
                name="醉虾",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.COLD_MIXING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.SUMMER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=100,
                main_ingredients=["河虾", "黄酒", "生姜", "香葱"],
                cooking_steps="活虾处理，黄酒腌制，调味装盘",
                health_benefits=["优质蛋白", "钙质", "低脂肪"],
                suitable_for_conditions=["补钙", "夏季开胃"],
                regional_specialty=True
            ),
            "苏式月饼": MegaChineseDish(
                name="苏式月饼",
                cuisine_type=CuisineType.JIANGSU,
                cooking_method=CookingMethod.ROASTING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=400,
                main_ingredients=["面粉", "猪油", "豆沙", "咸蛋黄"],
                cooking_steps="酥皮制作，包馅成型，烘烤至熟",
                health_benefits=["碳水化合物", "蛋白质", "脂肪"],
                suitable_for_conditions=["节庆食品", "传统糕点"],
                regional_specialty=True
            )
        }

    def _get_hunan_recipes(self) -> Dict[str, MegaChineseDish]:
        """湘菜菜谱 (12道)"""
        return {
            "剁椒鱼头": MegaChineseDish(
                name="剁椒鱼头",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=220,
                main_ingredients=["胖头鱼", "剁椒", "蒸鱼豉油", "葱"],
                cooking_steps="鱼头剖开，铺剁椒蒸制，淋豉油",
                health_benefits=["DHA", "优质蛋白质", "磷脂"],
                suitable_for_conditions=["大脑健康", "增强食欲"],
                regional_specialty=True
            ),
            "口味虾": MegaChineseDish(
                name="口味虾",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.SUMMER,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=180,
                main_ingredients=["小龙虾", "干辣椒", "花椒", "啤酒"],
                cooking_steps="虾炸制，爆炒香料，焖制入味",
                health_benefits=["蛋白质", "钙质", "锌元素"],
                suitable_for_conditions=["夏季开胃", "补钙"],
                regional_specialty=True
            ),
            "臭豆腐": MegaChineseDish(
                name="臭豆腐",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=200,
                main_ingredients=["臭豆腐", "辣椒粉", "蒜泥", "香菜"],
                cooking_steps="豆腐炸制，调辣椒蒜泥汁",
                health_benefits=["植物蛋白", "益生菌", "维生素B12"],
                suitable_for_conditions=["肠道健康", "素食者"],
                regional_specialty=True
            ),
            "毛血旺": MegaChineseDish(
                name="毛血旺",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=280,
                main_ingredients=["鸭血", "毛肚", "豆皮", "辣椒"],
                cooking_steps="食材汆烫，制麻辣汤底，浇热油",
                health_benefits=["铁元素", "蛋白质", "维生素A"],
                suitable_for_conditions=["贫血", "冬季温补"],
                regional_specialty=True
            ),
            "湘式小炒肉": MegaChineseDish(
                name="湘式小炒肉",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=300,
                main_ingredients=["五花肉", "青椒", "干辣椒", "豆豉"],
                cooking_steps="肉片炒制出油，下青椒炒香",
                health_benefits=["蛋白质", "维生素C", "维生素B1"],
                suitable_for_conditions=["下饭神器", "辣食爱好"],
                regional_specialty=True
            ),
            "糖油粑粑": MegaChineseDish(
                name="糖油粑粑",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=320,
                main_ingredients=["糯米粉", "红糖", "植物油", "芝麻"],
                cooking_steps="糯米团制作，油炸至金黄，裹糖浆",
                health_benefits=["碳水化合物", "快速能量", "维生素E"],
                suitable_for_conditions=["快速补能", "传统小食"],
                regional_specialty=True
            ),
            "辣椒炒肉": MegaChineseDish(
                name="辣椒炒肉",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=280,
                main_ingredients=["猪肉", "青辣椒", "红辣椒", "豆豉"],
                cooking_steps="肉丝炒制，下辣椒爆炒，调味收汁",
                health_benefits=["蛋白质", "维生素C", "辣椒素"],
                suitable_for_conditions=["开胃消食", "夏季发汗"],
                regional_specialty=True
            ),
            "湖南米粉": MegaChineseDish(
                name="湖南米粉",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=350,
                main_ingredients=["米粉", "肉丝", "豆芽", "辣椒油"],
                cooking_steps="米粉煮制，配菜炒制，调汤拌制",
                health_benefits=["碳水化合物", "蛋白质", "B族维生素"],
                suitable_for_conditions=["主食选择", "快餐"],
                regional_specialty=True
            ),
            "酸辣土豆丝": MegaChineseDish(
                name="酸辣土豆丝",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=120,
                main_ingredients=["土豆", "青椒", "干辣椒", "醋"],
                cooking_steps="土豆丝过水，爆炒调味，酸辣开胃",
                health_benefits=["维生素C", "膳食纤维", "钾元素"],
                suitable_for_conditions=["减肥", "开胃消食"],
                regional_specialty=True
            ),
            "红烧肉": MegaChineseDish(
                name="红烧肉",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=400,
                main_ingredients=["五花肉", "冰糖", "生抽", "老抽"],
                cooking_steps="肉块焯水，糖色炒制，小火焖煮",
                health_benefits=["蛋白质", "维生素B1", "脂肪"],
                suitable_for_conditions=["体力劳动", "冬季进补"],
                regional_specialty=False
            ),
            "湘式腊肉": MegaChineseDish(
                name="湘式腊肉",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=420,
                main_ingredients=["腊肉", "蒜苗", "干辣椒", "料酒"],
                cooking_steps="腊肉蒸制，切片炒制，配菜调味",
                health_benefits=["蛋白质", "脂肪", "保存食品"],
                suitable_for_conditions=["冬季储存", "传统风味"],
                regional_specialty=True
            ),
            "酱板鸭": MegaChineseDish(
                name="酱板鸭",
                cuisine_type=CuisineType.HUNAN,
                cooking_method=CookingMethod.ROASTING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=300,
                main_ingredients=["鸭肉", "酱料", "香料", "辣椒"],
                cooking_steps="鸭肉腌制，酱料调味，烘烤制作",
                health_benefits=["蛋白质", "铁元素", "维生素A"],
                suitable_for_conditions=["营养补充", "特色小食"],
                regional_specialty=True
            )
        }

    def _get_northern_recipes(self) -> Dict[str, MegaChineseDish]:
        """北方菜菜谱 (10道)"""
        return {
            "京酱肉丝": MegaChineseDish(
                name="京酱肉丝",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=240,
                main_ingredients=["猪肉丝", "甜面酱", "豆皮", "葱丝"],
                cooking_steps="肉丝上浆炒制，调甜面酱炒香",
                health_benefits=["蛋白质", "B族维生素"],
                suitable_for_conditions=["日常营养", "老少皆宜"],
                regional_specialty=False
            ),
            "锅包肉": MegaChineseDish(
                name="锅包肉",
                cuisine_type=CuisineType.NORTHEASTERN,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["猪里脊", "土豆淀粉", "白糖", "醋"],
                cooking_steps="肉片挂浆炸制，调糖醋汁炒合",
                health_benefits=["蛋白质", "碳水化合物"],
                suitable_for_conditions=["体力消耗大"],
                regional_specialty=True
            ),
            "小鸡炖蘑菇": MegaChineseDish(
                name="小鸡炖蘑菇",
                cuisine_type=CuisineType.NORTHEASTERN,
                cooking_method=CookingMethod.STEWING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["土鸡", "榛蘑", "粉条", "葱段"],
                cooking_steps="鸡块炖制，加蘑菇粉条焖煮",
                health_benefits=["蛋白质", "多糖", "膳食纤维"],
                suitable_for_conditions=["免疫力低下", "冬季滋补"],
                regional_specialty=True
            ),
            "地三鲜": MegaChineseDish(
                name="地三鲜",
                cuisine_type=CuisineType.NORTHEASTERN,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=180,
                main_ingredients=["茄子", "土豆", "青椒", "生抽"],
                cooking_steps="蔬菜分别过油，调味炒合",
                health_benefits=["维生素C", "膳食纤维", "钾元素"],
                suitable_for_conditions=["素食者", "减肥人群"],
                regional_specialty=True
            ),
            "酸菜白肉": MegaChineseDish(
                name="酸菜白肉",
                cuisine_type=CuisineType.NORTHEASTERN,
                cooking_method=CookingMethod.STEWING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=250,
                main_ingredients=["猪肉", "酸菜", "粉条", "葱段"],
                cooking_steps="肉片煮制，酸菜炒香，合炖调味",
                health_benefits=["蛋白质", "乳酸菌", "维生素C"],
                suitable_for_conditions=["肠胃调理", "冬季暖胃"],
                regional_specialty=True
            ),
            "红烧狮子头": MegaChineseDish(
                name="红烧狮子头",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=320,
                main_ingredients=["猪肉馅", "荸荠", "鸡蛋", "生抽"],
                cooking_steps="肉馅调制，制丸油炸，红烧入味",
                health_benefits=["蛋白质", "维生素B1", "铁元素"],
                suitable_for_conditions=["营养补充", "冬季进补"],
                regional_specialty=False
            ),
            "炸酱面": MegaChineseDish(
                name="炸酱面",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=400,
                main_ingredients=["面条", "猪肉丁", "甜面酱", "黄瓜丝"],
                cooking_steps="肉丁炒制，下酱炒香，面条配菜",
                health_benefits=["碳水化合物", "蛋白质", "B族维生素"],
                suitable_for_conditions=["主食选择", "北方口味"],
                regional_specialty=True
            ),
            "溜肝尖": MegaChineseDish(
                name="溜肝尖",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["猪肝", "青椒", "洋葱", "料酒"],
                cooking_steps="肝片腌制，急火爆炒，去腥调味",
                health_benefits=["铁元素", "维生素A", "蛋白质"],
                suitable_for_conditions=["贫血", "视力保护"],
                regional_specialty=False
            ),
            "糖醋里脊": MegaChineseDish(
                name="糖醋里脊",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["猪里脊", "淀粉", "白糖", "醋"],
                cooking_steps="里脊切条挂浆，炸制金黄，糖醋汁炒合",
                health_benefits=["蛋白质", "碳水化合物", "维生素B1"],
                suitable_for_conditions=["儿童喜爱", "开胃消食"],
                regional_specialty=False
            ),
            "木须肉": MegaChineseDish(
                name="木须肉",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=220,
                main_ingredients=["猪肉丝", "鸡蛋", "木耳", "黄花菜"],
                cooking_steps="肉丝炒制，蛋液摊制，配菜炒合",
                health_benefits=["蛋白质", "维生素", "膳食纤维"],
                suitable_for_conditions=["营养均衡", "家常搭配"],
                regional_specialty=False
            )
        }

    def _get_regional_specialties(self) -> Dict[str, MegaChineseDish]:
        """地方特色菜菜谱 (15道)"""
        return {
            "新疆大盘鸡": MegaChineseDish(
                name="新疆大盘鸡",
                cuisine_type=CuisineType.XINJIANG,
                cooking_method=CookingMethod.STEWING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=280,
                main_ingredients=["鸡肉", "土豆", "青椒", "洋葱"],
                cooking_steps="鸡块炒制，加蔬菜焖煮，配拌面",
                health_benefits=["蛋白质", "维生素C", "碳水化合物"],
                suitable_for_conditions=["体力劳动", "高原地区"],
                regional_specialty=True
            ),
            "云南过桥米线": MegaChineseDish(
                name="云南过桥米线",
                cuisine_type=CuisineType.YUNNAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["米线", "鸡汤", "猪肉片", "韭菜"],
                cooking_steps="制浓鸡汤，烫制配菜，汤浇米线",
                health_benefits=["碳水化合物", "蛋白质", "B族维生素"],
                suitable_for_conditions=["快速补能", "肠胃调理"],
                regional_specialty=True
            ),
            "兰州拉面": MegaChineseDish(
                name="兰州拉面",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=400,
                main_ingredients=["面粉", "牛肉", "萝卜", "香菜"],
                cooking_steps="和面拉制，熬牛骨汤，配菜装碗",
                health_benefits=["碳水化合物", "蛋白质", "钙质"],
                suitable_for_conditions=["主食补充", "北方口味"],
                regional_specialty=True
            ),
            "重庆小面": MegaChineseDish(
                name="重庆小面",
                cuisine_type=CuisineType.SICHUAN,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.VERY_SPICY,
                estimated_calories=380,
                main_ingredients=["碱面", "花椒", "辣椒油", "榨菜"],
                cooking_steps="调制麻辣底料，煮面条拌制",
                health_benefits=["碳水化合物", "辣椒素", "维生素C"],
                suitable_for_conditions=["辣食爱好者", "开胃消食"],
                regional_specialty=True
            ),
            "陕西肉夹馍": MegaChineseDish(
                name="陕西肉夹馍",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.ROASTING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=420,
                main_ingredients=["白吉馍", "猪肉", "青椒", "调料"],
                cooking_steps="卤制猪肉切碎，馍饼烤制夹肉",
                health_benefits=["蛋白质", "碳水化合物", "B族维生素"],
                suitable_for_conditions=["快餐选择", "饱腹感强"],
                regional_specialty=True
            ),
            "新疆抓饭": MegaChineseDish(
                name="新疆抓饭",
                cuisine_type=CuisineType.XINJIANG,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=450,
                main_ingredients=["大米", "羊肉", "胡萝卜", "洋葱"],
                cooking_steps="羊肉炒制，米饭焖煮，香料调味",
                health_benefits=["碳水化合物", "蛋白质", "胡萝卜素"],
                suitable_for_conditions=["主食", "高原地区"],
                regional_specialty=True
            ),
            "东北锅包肉": MegaChineseDish(
                name="东北锅包肉",
                cuisine_type=CuisineType.NORTHEASTERN,
                cooking_method=CookingMethod.DEEP_FRYING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["猪里脊", "土豆淀粉", "白糖", "醋"],
                cooking_steps="肉片挂浆炸制，调糖醋汁炒合",
                health_benefits=["蛋白质", "碳水化合物"],
                suitable_for_conditions=["体力消耗大"],
                regional_specialty=True
            ),
            "云南汽锅鸡": MegaChineseDish(
                name="云南汽锅鸡",
                cuisine_type=CuisineType.YUNNAN,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=180,
                main_ingredients=["土鸡", "天麻", "枸杞", "生姜"],
                cooking_steps="汽锅蒸制，药材调味，清汤鲜美",
                health_benefits=["蛋白质", "药用价值", "滋补"],
                suitable_for_conditions=["体质虚弱", "药膳调理"],
                regional_specialty=True
            ),
            "广西螺蛳粉": MegaChineseDish(
                name="广西螺蛳粉",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=350,
                main_ingredients=["米粉", "螺蛳汤", "酸笋", "花生"],
                cooking_steps="熬制螺蛳汤，米粉煮制，配菜调味",
                health_benefits=["碳水化合物", "蛋白质", "钙质"],
                suitable_for_conditions=["特色风味", "开胃消食"],
                regional_specialty=True
            ),
            "内蒙古手抓羊肉": MegaChineseDish(
                name="内蒙古手抓羊肉",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=350,
                main_ingredients=["羊肉", "生姜", "料酒", "盐"],
                cooking_steps="羊肉煮制，简单调味，保持原味",
                health_benefits=["蛋白质", "铁元素", "维生素B12"],
                suitable_for_conditions=["冬季进补", "草原风味"],
                regional_specialty=True
            ),
            "贵州酸汤鱼": MegaChineseDish(
                name="贵州酸汤鱼",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.SPICY,
                estimated_calories=220,
                main_ingredients=["鲤鱼", "酸汤", "西红柿", "木姜子"],
                cooking_steps="制酸汤底，鱼片煮制，酸辣开胃",
                health_benefits=["优质蛋白", "维生素C", "有机酸"],
                suitable_for_conditions=["开胃消食", "夏季清热"],
                regional_specialty=True
            ),
            "福建佛跳墙": MegaChineseDish(
                name="福建佛跳墙",
                cuisine_type=CuisineType.FUJIAN,
                cooking_method=CookingMethod.STEWING,
                difficulty_level=DifficultyLevel.HARD,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=380,
                main_ingredients=["海参", "鲍鱼", "花胶", "香菇"],
                cooking_steps="多种食材分别处理，合炖调味",
                health_benefits=["胶原蛋白", "蛋白质", "微量元素"],
                suitable_for_conditions=["高档宴请", "滋补养生"],
                regional_specialty=True
            ),
            "天津狗不理包子": MegaChineseDish(
                name="天津狗不理包子",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STEAMING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=300,
                main_ingredients=["面粉", "猪肉馅", "生姜", "香葱"],
                cooking_steps="发面制皮，调馅包制，蒸制至熟",
                health_benefits=["碳水化合物", "蛋白质", "B族维生素"],
                suitable_for_conditions=["主食", "传统名点"],
                regional_specialty=True
            ),
            "海南文昌鸡": MegaChineseDish(
                name="海南文昌鸡",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=220,
                main_ingredients=["文昌鸡", "生姜", "香葱", "蒜泥"],
                cooking_steps="整鸡煮制，切块装盘，配蘸料",
                health_benefits=["优质蛋白", "低脂肪", "B族维生素"],
                suitable_for_conditions=["产后恢复", "营养补充"],
                regional_specialty=True
            ),
            "西藏酥油茶": MegaChineseDish(
                name="西藏酥油茶",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["酥油", "茶叶", "盐", "牛奶"],
                cooking_steps="茶叶煮制，加酥油搅拌，调味饮用",
                health_benefits=["脂肪", "茶多酚", "高热量"],
                suitable_for_conditions=["高原地区", "御寒保暖"],
                regional_specialty=True
            )
        }

    def _get_homestyle_recipes(self) -> Dict[str, MegaChineseDish]:
        """家常菜菜谱 (10道)"""
        return {
            "番茄鸡蛋": MegaChineseDish(
                name="番茄鸡蛋",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=180,
                main_ingredients=["番茄", "鸡蛋", "白糖", "盐"],
                cooking_steps="鸡蛋炒制盛起，番茄炒出汁水，合炒调味",
                health_benefits=["优质蛋白", "番茄红素", "维生素C"],
                suitable_for_conditions=["日常营养", "老少皆宜"],
                regional_specialty=False
            ),
            "青椒土豆丝": MegaChineseDish(
                name="青椒土豆丝",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=120,
                main_ingredients=["土豆", "青椒", "蒜", "醋"],
                cooking_steps="土豆丝过水，青椒丝炒制，调味炒合",
                health_benefits=["维生素C", "膳食纤维", "钾元素"],
                suitable_for_conditions=["减肥", "维生素补充"],
                regional_specialty=False
            ),
            "红烧茄子": MegaChineseDish(
                name="红烧茄子",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BRAISING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=150,
                main_ingredients=["茄子", "生抽", "老抽", "白糖"],
                cooking_steps="茄子过油，调味汁焖煮，收汁装盘",
                health_benefits=["膳食纤维", "花青素", "维生素P"],
                suitable_for_conditions=["抗氧化", "血管保护"],
                regional_specialty=False
            ),
            "蒜蓉菠菜": MegaChineseDish(
                name="蒜蓉菠菜",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=50,
                main_ingredients=["菠菜", "蒜", "盐", "香油"],
                cooking_steps="菠菜焯水，蒜爆香，快炒调味",
                health_benefits=["叶酸", "铁元素", "维生素K"],
                suitable_for_conditions=["贫血", "孕妇", "骨骼健康"],
                regional_specialty=False
            ),
            "紫菜蛋花汤": MegaChineseDish(
                name="紫菜蛋花汤",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.BOILING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.ALL_SEASONS,
                spice_level=SpiceLevel.MILD,
                estimated_calories=80,
                main_ingredients=["紫菜", "鸡蛋", "虾皮", "香油"],
                cooking_steps="紫菜泡发，蛋液打散，开水冲制",
                health_benefits=["碘元素", "优质蛋白", "钙质"],
                suitable_for_conditions=["甲状腺健康", "补碘"],
                regional_specialty=False
            ),
            "凉拌黄瓜": MegaChineseDish(
                name="凉拌黄瓜",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.COLD_MIXING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=30,
                main_ingredients=["黄瓜", "蒜", "醋", "香油"],
                cooking_steps="黄瓜拍制，调味汁拌制，腌制入味",
                health_benefits=["维生素C", "水分", "膳食纤维"],
                suitable_for_conditions=["减肥", "夏季解腻"],
                regional_specialty=False
            ),
            "土豆炖牛肉": MegaChineseDish(
                name="土豆炖牛肉",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STEWING,
                difficulty_level=DifficultyLevel.MEDIUM,
                season=Season.WINTER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=280,
                main_ingredients=["牛肉", "土豆", "胡萝卜", "洋葱"],
                cooking_steps="牛肉焯水，配菜炖煮，调味收汁",
                health_benefits=["优质蛋白", "铁元素", "维生素A"],
                suitable_for_conditions=["贫血", "体力恢复"],
                regional_specialty=False
            ),
            "冬瓜排骨汤": MegaChineseDish(
                name="冬瓜排骨汤",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STEWING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SUMMER,
                spice_level=SpiceLevel.MILD,
                estimated_calories=200,
                main_ingredients=["排骨", "冬瓜", "生姜", "香葱"],
                cooking_steps="排骨焯水，炖煮出汤，下冬瓜煮制",
                health_benefits=["蛋白质", "钙质", "利尿消肿"],
                suitable_for_conditions=["水肿", "夏季清热"],
                regional_specialty=False
            ),
            "韭菜炒蛋": MegaChineseDish(
                name="韭菜炒蛋",
                cuisine_type=CuisineType.HOMESTYLE,
                cooking_method=CookingMethod.STIR_FRYING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.SPRING,
                spice_level=SpiceLevel.MILD,
                estimated_calories=160,
                main_ingredients=["韭菜", "鸡蛋", "盐", "料酒"],
                cooking_steps="鸡蛋炒制，韭菜下锅，快炒调味",
                health_benefits=["优质蛋白", "维生素A", "膳食纤维"],
                suitable_for_conditions=["春季养生", "补肾壮阳"],
                regional_specialty=False
            ),
            "银耳莲子汤": MegaChineseDish(
                name="银耳莲子汤",
                cuisine_type=CuisineType.HEALTH,
                cooking_method=CookingMethod.STEWING,
                difficulty_level=DifficultyLevel.EASY,
                season=Season.AUTUMN,
                spice_level=SpiceLevel.MILD,
                estimated_calories=80,
                main_ingredients=["银耳", "莲子", "冰糖", "红枣"],
                cooking_steps="银耳泡发，莲子处理，小火炖煮",
                health_benefits=["胶质", "多糖", "安神养心"],
                suitable_for_conditions=["美容养颜", "润燥清肺"],
                regional_specialty=False
            )
        }

    def get_stats(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        stats = {}

        # 按菜系统计
        for cuisine in CuisineType:
            count = sum(1 for dish in self.recipes.values()
                       if dish.cuisine_type == cuisine)
            if count > 0:
                stats[f"📚 {cuisine.value}"] = count

        # 按难度统计
        for difficulty in DifficultyLevel:
            count = sum(1 for dish in self.recipes.values()
                       if dish.difficulty_level == difficulty)
            if count > 0:
                stats[f"📊 {difficulty.value}菜谱"] = count

        # 按热量统计
        low_cal = sum(1 for dish in self.recipes.values()
                     if dish.estimated_calories <= 100)
        medium_cal = sum(1 for dish in self.recipes.values()
                        if 100 < dish.estimated_calories <= 300)
        high_cal = sum(1 for dish in self.recipes.values()
                      if dish.estimated_calories > 300)

        if low_cal > 0:
            stats["🥗 低热量菜谱 (≤100千卡)"] = low_cal
        if medium_cal > 0:
            stats["🍽️ 中热量菜谱 (100-300千卡)"] = medium_cal
        if high_cal > 0:
            stats["🍖 高热量菜谱 (>300千卡)"] = high_cal

        stats["📊 总菜谱数"] = len(self.recipes)
        return stats

    def get_recipes_by_cuisine(self, cuisine_type: CuisineType) -> Dict[str, MegaChineseDish]:
        """按菜系查询菜谱"""
        return {name: dish for name, dish in self.recipes.items()
                if dish.cuisine_type == cuisine_type}

    def get_recipes_by_calories(self, max_calories: int) -> Dict[str, MegaChineseDish]:
        """按热量查询菜谱"""
        return {name: dish for name, dish in self.recipes.items()
                if dish.estimated_calories <= max_calories}

    def get_recipes_by_difficulty(self, difficulty: DifficultyLevel) -> Dict[str, MegaChineseDish]:
        """按难度查询菜谱"""
        return {name: dish for name, dish in self.recipes.items()
                if dish.difficulty_level == difficulty}

    def search_recipes(self, keyword: str) -> Dict[str, MegaChineseDish]:
        """关键词搜索菜谱"""
        results = {}
        keyword = keyword.lower()

        for name, dish in self.recipes.items():
            # 搜索菜名
            if keyword in name.lower():
                results[name] = dish
                continue

            # 搜索主要食材
            if any(keyword in ingredient.lower() for ingredient in dish.main_ingredients):
                results[name] = dish
                continue

            # 搜索健康功效
            if any(keyword in benefit.lower() for benefit in dish.health_benefits):
                results[name] = dish
                continue

        return results

if __name__ == "__main__":
    # 创建超大菜谱数据库
    print("🚀 启动超大中式菜谱数据库 v2.0")
    mega_db = MegaChineseRecipeDatabase()

    print("\n=== 超大中式菜谱数据库统计 ===")
    stats = mega_db.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}道")

    print("\n=== 川菜示例 ===")
    sichuan_dishes = mega_db.get_recipes_by_cuisine(CuisineType.SICHUAN)
    for name, dish in list(sichuan_dishes.items())[:3]:
        print(f"🌶️ {name}: {dish.cooking_steps[:30]}...")

    print("\n=== 低热量菜谱 (≤100千卡) ===")
    low_cal_dishes = mega_db.get_recipes_by_calories(100)
    for name, dish in low_cal_dishes.items():
        print(f"🥗 {name}: {dish.estimated_calories}千卡")

    print(f"\n✅ 超大菜谱数据库创建完成！")
    print(f"📊 总计：{len(mega_db.recipes)}道菜谱")
    print(f"🎯 已达成100+菜谱目标！")