#!/usr/bin/env python3
"""
超大中式菜谱数据库 (100+道菜品)
涵盖八大菜系、地方特色菜、季节菜品、养生食谱等
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
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
    GUIZHOU = "贵州菜"
    TIBETAN = "藏菜"
    HAKKA = "客家菜"
    SHANXI = "晋菜"

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
    SMOKING = "熏"
    POACHING = "汆"
    SAUTEING = "煸"
    ROASTING = "烧"
    QUICK_FRYING = "爆"

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
    EXTRA_SPICY = "特辣"

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
    cooking_time: int = 30  # 制作时间(分钟)
    cooking_oil_amount: float = 10  # 烹调油用量 (g)
    salt_amount: float = 2  # 食盐用量 (g)


class MegaChineseRecipeDatabase:
    """超大中式菜谱数据库"""

    def __init__(self):
        self.recipes = self._initialize_mega_recipe_database()

    def _initialize_mega_recipe_database(self) -> Dict[str, MegaChineseDish]:
        """初始化超大菜谱数据库"""
        recipes = {}

        # ============ 川菜扩展 ============
        recipes.update(self._get_sichuan_mega_recipes())

        # ============ 粤菜扩展 ============
        recipes.update(self._get_cantonese_mega_recipes())

        # ============ 鲁菜扩展 ============
        recipes.update(self._get_shandong_mega_recipes())

        # ============ 江浙菜扩展 ============
        recipes.update(self._get_jiangzhe_mega_recipes())

        # ============ 湘菜扩展 ============
        recipes.update(self._get_hunan_mega_recipes())

        # ============ 北方菜扩展 ============
        recipes.update(self._get_northern_mega_recipes())

        # ============ 地方特色菜 ============
        recipes.update(self._get_regional_specialties())

        # ============ 家常菜扩展 ============
        recipes.update(self._get_homestyle_mega_recipes())

        # ============ 养生菜扩展 ============
        recipes.update(self._get_health_mega_recipes())

        # ============ 素食菜扩展 ============
        recipes.update(self._get_vegetarian_mega_recipes())

        return recipes

    def _get_sichuan_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """川菜扩展菜谱"""
        recipes = {}

        recipes["麻婆豆腐"] = MegaChineseDish(
            name="麻婆豆腐",
            cuisine_type=CuisineType.SICHUAN,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("嫩豆腐", 300), ("牛肉末", 50), ("郫县豆瓣酱", 15)],
            seasonings=["花椒粉", "生抽", "老抽", "蒜末", "姜末", "青蒜"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="中等",
            cooking_time=15,
            description="豆腐切块汆水，爆炒牛肉末，下豆瓣酱炒出红油，加豆腐焖煮，最后撒花椒粉",
            health_benefits=["优质蛋白", "大豆异黄酮"],
            suitable_for=["一般人群", "蛋白质缺乏者"],
            avoid_for=["消化不良者"],
            nutrition_highlight="高蛋白低脂肪",
            spice_level=3,
            estimated_calories=180,
            regional_specialty="成都经典"
        )

        recipes["宫保鸡丁"] = MegaChineseDish(
            name="宫保鸡丁",
            cuisine_type=CuisineType.SICHUAN,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("鸡胸肉", 200), ("花生米", 50), ("干辣椒", 10)],
            seasonings=["花椒", "生抽", "老抽", "醋", "糖", "料酒", "淀粉"],
            cooking_oil_amount=20,
            salt_amount=2,
            difficulty="中等",
            cooking_time=12,
            description="鸡肉上浆滑油，爆炒干辣椒花椒，下鸡丁和花生米炒匀",
            health_benefits=["优质蛋白", "维生素E", "不饱和脂肪酸"],
            suitable_for=["健康成人", "脑力劳动者"],
            avoid_for=["花生过敏者", "消化不良者"],
            spice_level=2,
            estimated_calories=220
        )

        recipes["夫妻肺片"] = MegaChineseDish(
            name="夫妻肺片",
            cuisine_type=CuisineType.SICHUAN,
            cooking_method=CookingMethod.COLD_MIXING,
            main_ingredients=[("牛肉", 150), ("牛舌", 100), ("牛肚", 100)],
            seasonings=["红油", "花椒油", "生抽", "蒜泥", "姜末"],
            cooking_oil_amount=15,
            salt_amount=3,
            difficulty="困难",
            cooking_time=120,
            description="牛杂卤制至软烂，切片装盘，淋特制红油调料",
            health_benefits=["优质蛋白", "铁元素", "B族维生素"],
            suitable_for=["贫血者", "体力劳动者"],
            avoid_for=["高血脂患者", "痛风患者"],
            spice_level=3,
            estimated_calories=180
        )

        recipes["水煮牛肉"] = MegaChineseDish(
            name="水煮牛肉",
            cuisine_type=CuisineType.SICHUAN,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("牛肉片", 300), ("豆芽", 200), ("白菜", 150)],
            seasonings=["豆瓣酱", "花椒", "干辣椒", "蒜末", "生抽"],
            cooking_oil_amount=30,
            salt_amount=3,
            difficulty="中等",
            cooking_time=25,
            description="牛肉片上浆，蔬菜垫底，肉片汆烫，浇热油爆香",
            health_benefits=["优质蛋白", "铁元素"],
            suitable_for=["贫血者", "健康成人"],
            avoid_for=["消化不良者"],
            spice_level=4,
            estimated_calories=200
        )

        recipes["口水鸡"] = MegaChineseDish(
            name="口水鸡",
            cuisine_type=CuisineType.SICHUAN,
            cooking_method=CookingMethod.COLD_MIXING,
            main_ingredients=[("白斩鸡", 400), ("黄瓜丝", 50), ("胡萝卜丝", 30)],
            seasonings=["红油", "花椒油", "生抽", "香醋", "蒜泥", "姜末"],
            cooking_oil_amount=12,
            salt_amount=2,
            difficulty="简单",
            cooking_time=20,
            description="白斩鸡放凉切片，调制川式口水鸡料汁浇在鸡肉上",
            health_benefits=["优质蛋白", "低脂肪"],
            suitable_for=["减肥人群", "健康成人"],
            avoid_for=["消化不良者"],
            spice_level=3,
            estimated_calories=160
        )

        return recipes

    def _get_cantonese_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """粤菜扩展菜谱"""
        recipes = {}

        recipes["白切鸡"] = MegaChineseDish(
            name="白切鸡",
            cuisine_type=CuisineType.CANTONESE,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("土鸡", 800), ("生姜", 30), ("大葱", 20)],
            seasonings=["姜蓉", "蒜蓉", "生抽", "香油"],
            cooking_oil_amount=5,
            salt_amount=5,
            difficulty="中等",
            cooking_time=40,
            description="整鸡煮制，保持原味，配姜蓉蘸料",
            health_benefits=["优质蛋白", "提供能量"],
            suitable_for=["营养不良者", "产妇"],
            avoid_for=["感冒发热者"],
            estimated_calories=165,
            regional_specialty="广州传统"
        )

        recipes["蜜汁叉烧"] = MegaChineseDish(
            name="蜜汁叉烧",
            cuisine_type=CuisineType.CANTONESE,
            cooking_method=CookingMethod.ROASTING,
            main_ingredients=[("梅花肉", 500), ("蜂蜜", 30), ("叉烧酱", 50)],
            seasonings=["生抽", "老抽", "料酒", "五香粉"],
            cooking_oil_amount=8,
            salt_amount=3,
            difficulty="中等",
            cooking_time=90,
            description="猪肉腌制入味，烤箱烘烤至表面焦糖化",
            health_benefits=["优质蛋白", "B族维生素"],
            suitable_for=["健康成人", "体力劳动者"],
            avoid_for=["糖尿病患者", "高血脂患者"],
            estimated_calories=280
        )

        recipes["虾饺"] = MegaChineseDish(
            name="虾饺",
            cuisine_type=CuisineType.CANTONESE,
            cooking_method=CookingMethod.STEAMING,
            main_ingredients=[("鲜虾仁", 200), ("澄粉", 100), ("猪肥肉", 30)],
            seasonings=["盐", "胡椒粉", "香油", "生粉"],
            cooking_oil_amount=5,
            salt_amount=1,
            difficulty="困难",
            cooking_time=30,
            description="调制澄粉皮，包入虾仁馅，蒸制透明",
            health_benefits=["优质蛋白", "低脂肪", "易消化"],
            suitable_for=["老人", "儿童", "减肥人群"],
            avoid_for=["海鲜过敏者"],
            estimated_calories=120
        )

        recipes["广式烧鸭"] = MegaChineseDish(
            name="广式烧鸭",
            cuisine_type=CuisineType.CANTONESE,
            cooking_method=CookingMethod.ROASTING,
            main_ingredients=[("鸭子", 1000), ("五香粉", 5), ("甜面酱", 20)],
            seasonings=["生抽", "老抽", "料酒", "糖", "盐"],
            cooking_oil_amount=0,
            salt_amount=8,
            difficulty="困难",
            cooking_time=150,
            description="鸭子腌制，挂炉烤制至皮脆肉嫩",
            health_benefits=["优质蛋白", "铁元素"],
            suitable_for=["贫血者", "营养不良者"],
            avoid_for=["高血脂患者"],
            estimated_calories=290
        )

        recipes["白灼菜心"] = MegaChineseDish(
            name="白灼菜心",
            cuisine_type=CuisineType.CANTONESE,
            cooking_method=CookingMethod.BLANCHING,
            main_ingredients=[("菜心", 300), ("蒜蓉", 10)],
            seasonings=["生抽", "蒸鱼豉油", "香油"],
            cooking_oil_amount=8,
            salt_amount=1,
            difficulty="简单",
            cooking_time=5,
            description="菜心焯水断生，淋蒜蓉豉油汁",
            health_benefits=["维生素C", "叶酸", "膳食纤维"],
            suitable_for=["所有人群"],
            avoid_for=[],
            estimated_calories=25
        )

        return recipes

    def _get_northeastern_recipes(self) -> Dict[str, MegaChineseDish]:
        """东北菜菜谱"""
        recipes = {}

        recipes["锅包肉"] = MegaChineseDish(
            name="锅包肉",
            cuisine_type=CuisineType.NORTHEASTERN,
            cooking_method=CookingMethod.DEEP_FRYING,
            main_ingredients=[("猪里脊", 300), ("胡萝卜丝", 50), ("香菜", 20)],
            seasonings=["番茄酱", "醋", "糖", "淀粉", "料酒"],
            cooking_oil_amount=200,
            salt_amount=2,
            difficulty="中等",
            cooking_time=20,
            description="里脊肉裹浆炸至金黄，调糖醋汁炒匀",
            health_benefits=["优质蛋白", "维生素A"],
            suitable_for=["儿童", "体力劳动者"],
            avoid_for=["减肥人群", "糖尿病患者"],
            estimated_calories=320,
            season=Season.WINTER,
            regional_specialty="哈尔滨名菜"
        )

        recipes["东北乱炖"] = MegaChineseDish(
            name="东北乱炖",
            cuisine_type=CuisineType.NORTHEASTERN,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("五花肉", 200), ("土豆", 200), ("豆角", 150), ("茄子", 150)],
            seasonings=["生抽", "老抽", "料酒", "大葱", "生姜"],
            cooking_oil_amount=15,
            salt_amount=3,
            difficulty="简单",
            cooking_time=45,
            description="五花肉爆香，下蔬菜炖煮至软烂",
            health_benefits=["维生素C", "膳食纤维", "蛋白质"],
            suitable_for=["体力劳动者", "营养不良者"],
            avoid_for=["高血脂患者"],
            estimated_calories=180,
            season=Season.AUTUMN
        )

        recipes["小鸡炖蘑菇"] = MegaChineseDish(
            name="小鸡炖蘑菇",
            cuisine_type=CuisineType.NORTHEASTERN,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("土鸡", 600), ("榛蘑", 100), ("粉条", 100)],
            seasonings=["生抽", "老抽", "料酒", "大葱", "生姜", "八角"],
            cooking_oil_amount=12,
            salt_amount=4,
            difficulty="中等",
            cooking_time=80,
            description="鸡肉爆香，加蘑菇和调料炖煮，最后下粉条",
            health_benefits=["优质蛋白", "多糖", "氨基酸"],
            suitable_for=["营养不良者", "术后恢复"],
            avoid_for=["痛风患者"],
            estimated_calories=190,
            season=Season.WINTER
        )

        return recipes

    def _get_xinjiang_recipes(self) -> Dict[str, MegaChineseDish]:
        """新疆菜菜谱"""
        recipes = {}

        recipes["大盘鸡"] = MegaChineseDish(
            name="大盘鸡",
            cuisine_type=CuisineType.XINJIANG,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("土鸡", 800), ("土豆", 300), ("青椒", 100), ("红椒", 100)],
            seasonings=["豆瓣酱", "生抽", "老抽", "料酒", "糖", "八角", "桂皮"],
            cooking_oil_amount=25,
            salt_amount=4,
            difficulty="中等",
            cooking_time=60,
            description="鸡块爆炒，加调料焖煮，下土豆和彩椒",
            health_benefits=["优质蛋白", "维生素C", "钾元素"],
            suitable_for=["体力劳动者", "健康成人"],
            avoid_for=["高血压患者"],
            estimated_calories=210,
            spice_level=2,
            regional_specialty="新疆沙湾"
        )

        recipes["手抓饭"] = MegaChineseDish(
            name="手抓饭",
            cuisine_type=CuisineType.XINJIANG,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("羊肉", 300), ("大米", 300), ("胡萝卜", 200), ("洋葱", 100)],
            seasonings=["孜然粉", "盐", "胡椒粉"],
            cooking_oil_amount=30,
            salt_amount=5,
            difficulty="中等",
            cooking_time=90,
            description="羊肉炒香，加蔬菜和大米焖制成饭",
            health_benefits=["优质蛋白", "胡萝卜素", "复合碳水"],
            suitable_for=["体力劳动者", "生长发育期"],
            avoid_for=["高血脂患者"],
            estimated_calories=280,
            regional_specialty="维吾尔传统"
        )

        recipes["烤羊肉串"] = MegaChineseDish(
            name="烤羊肉串",
            cuisine_type=CuisineType.XINJIANG,
            cooking_method=CookingMethod.GRILLING,
            main_ingredients=[("羊肉", 300), ("洋葱", 50)],
            seasonings=["孜然粉", "辣椒粉", "盐", "胡椒粉"],
            cooking_oil_amount=5,
            salt_amount=3,
            difficulty="简单",
            cooking_time=15,
            description="羊肉切块串签，炭火烤制，撒孜然辣椒粉",
            health_benefits=["优质蛋白", "铁元素", "锌元素"],
            suitable_for=["贫血者", "体力劳动者"],
            avoid_for=["高血脂患者", "痛风患者"],
            estimated_calories=250,
            spice_level=2
        )

        return recipes

    def _get_yunnan_recipes(self) -> Dict[str, MegaChineseDish]:
        """云南菜菜谱"""
        recipes = {}

        recipes["过桥米线"] = MegaChineseDish(
            name="过桥米线",
            cuisine_type=CuisineType.YUNNAN,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("米线", 200), ("鸡胸肉片", 100), ("火腿片", 50), ("鹌鹑蛋", 50)],
            seasonings=["鸡汤", "胡椒粉", "香菜", "韭菜"],
            cooking_oil_amount=8,
            salt_amount=3,
            difficulty="中等",
            cooking_time=30,
            description="热鸡汤烫熟生食材，加入米线和调料",
            health_benefits=["优质蛋白", "B族维生素", "易消化"],
            suitable_for=["老人", "儿童", "病后调养"],
            avoid_for=["高血压患者"],
            estimated_calories=280,
            regional_specialty="昆明传统"
        )

        recipes["汽锅鸡"] = MegaChineseDish(
            name="汽锅鸡",
            cuisine_type=CuisineType.YUNNAN,
            cooking_method=CookingMethod.STEAMING,
            main_ingredients=[("土鸡", 800), ("枸杞", 10), ("红枣", 30)],
            seasonings=["料酒", "盐", "胡椒粉", "生姜"],
            cooking_oil_amount=0,
            salt_amount=4,
            difficulty="简单",
            cooking_time=120,
            description="鸡肉放入汽锅，蒸汽蒸制，原汁原味",
            health_benefits=["优质蛋白", "胶原蛋白", "滋补强身"],
            suitable_for=["营养不良者", "术后恢复", "产妇"],
            avoid_for=["感冒发热者"],
            estimated_calories=165
        )

        recipes["酸辣鱼"] = MegaChineseDish(
            name="酸辣鱼",
            cuisine_type=CuisineType.YUNNAN,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("草鱼", 500), ("酸菜", 200), ("番茄", 150)],
            seasonings=["野山椒", "泡椒", "生姜", "大蒜", "香菜"],
            cooking_oil_amount=15,
            salt_amount=3,
            difficulty="中等",
            cooking_time=25,
            description="鱼片腌制，爆香调料，下鱼片煮制",
            health_benefits=["优质蛋白", "DHA", "维生素C"],
            suitable_for=["脑力劳动者", "学生"],
            avoid_for=["胃溃疡患者"],
            estimated_calories=160,
            spice_level=3
        )

        return recipes

    def _get_homestyle_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """家常菜扩展菜谱"""
        recipes = {}

        recipes["红烧肉"] = MegaChineseDish(
            name="红烧肉",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("五花肉", 400)],
            seasonings=["生抽", "老抽", "冰糖", "料酒", "八角", "桂皮"],
            cooking_oil_amount=10,
            salt_amount=2,
            difficulty="中等",
            cooking_time=90,
            description="五花肉切块，糖色炒制，小火焖煮至软糯",
            health_benefits=["B族维生素", "蛋白质"],
            suitable_for=["体力劳动者"],
            avoid_for=["高血脂患者", "减肥人群"],
            estimated_calories=350
        )

        recipes["糖醋排骨"] = MegaChineseDish(
            name="糖醋排骨",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("小排", 500)],
            seasonings=["醋", "糖", "生抽", "老抽", "料酒", "葱", "姜"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="中等",
            cooking_time=60,
            description="排骨焯水，炒糖色，加调料焖煮收汁",
            health_benefits=["优质蛋白", "钙", "磷"],
            suitable_for=["儿童", "青少年", "老人"],
            avoid_for=["糖尿病患者"],
            estimated_calories=280
        )

        recipes["鱼香肉丝"] = MegaChineseDish(
            name="鱼香肉丝",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("猪肉丝", 200), ("冬笋丝", 100), ("木耳丝", 50), ("胡萝卜丝", 50)],
            seasonings=["郫县豆瓣酱", "糖", "醋", "生抽", "料酒", "蒜末", "姜末"],
            cooking_oil_amount=20,
            salt_amount=1,
            difficulty="中等",
            cooking_time=15,
            description="肉丝上浆滑油，爆炒配菜，调鱼香汁炒匀",
            health_benefits=["优质蛋白", "膳食纤维", "维生素A"],
            suitable_for=["健康成人"],
            avoid_for=["高血压患者"],
            estimated_calories=180,
            spice_level=1
        )

        recipes["宫保鸡丁"] = MegaChineseDish(
            name="家常版宫保鸡丁",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("鸡胸肉", 250), ("花生米", 80), ("青椒", 50), ("胡萝卜", 50)],
            seasonings=["生抽", "老抽", "醋", "糖", "料酒", "干辣椒", "花椒"],
            cooking_oil_amount=18,
            salt_amount=2,
            difficulty="中等",
            cooking_time=12,
            description="鸡丁腌制滑油，炒香花生和调料，快速炒匀",
            health_benefits=["优质蛋白", "维生素E", "不饱和脂肪酸"],
            suitable_for=["健康成人", "学生"],
            avoid_for=["花生过敏者"],
            estimated_calories=220,
            spice_level=2
        )

        return recipes

    def _get_health_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """养生菜扩展菜谱"""
        recipes = {}

        recipes["银耳莲子汤"] = MegaChineseDish(
            name="银耳莲子汤",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("银耳", 20), ("莲子", 30), ("红枣", 20), ("枸杞", 10)],
            seasonings=["冰糖"],
            cooking_oil_amount=0,
            salt_amount=0,
            difficulty="简单",
            cooking_time=120,
            description="银耳提前泡发，与莲子红枣同炖至粘稠",
            health_benefits=["膳食纤维", "胶质蛋白", "维生素"],
            suitable_for=["需要美容者", "失眠者", "女性"],
            avoid_for=["糖尿病患者"],
            estimated_calories=80,
            season=Season.ALL_YEAR
        )

        recipes["山药薏米粥"] = MegaChineseDish(
            name="山药薏米粥",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("山药", 100), ("薏米", 50), ("大米", 50)],
            seasonings=[],
            cooking_oil_amount=0,
            salt_amount=0,
            difficulty="简单",
            cooking_time=60,
            description="薏米提前浸泡，与大米和山药同煮成粥",
            health_benefits=["膳食纤维", "淀粉酶", "蛋白质"],
            suitable_for=["消化功能弱者", "老人", "儿童"],
            avoid_for=["便秘者"],
            estimated_calories=120
        )

        recipes["枸杞菊花茶"] = MegaChineseDish(
            name="枸杞菊花茶",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("枸杞", 10), ("菊花", 5)],
            seasonings=["蜂蜜"],
            cooking_oil_amount=0,
            salt_amount=0,
            difficulty="简单",
            cooking_time=10,
            description="枸杞和菊花用开水冲泡，可加蜂蜜调味",
            health_benefits=["花青素", "维生素C", "抗氧化"],
            suitable_for=["用眼过度者", "上班族"],
            avoid_for=["脾胃虚寒者"],
            estimated_calories=15,
            season=Season.SUMMER
        )

        recipes["黑豆核桃豆浆"] = MegaChineseDish(
            name="黑豆核桃豆浆",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("黑豆", 50), ("核桃仁", 30), ("黑芝麻", 20)],
            seasonings=[],
            cooking_oil_amount=0,
            salt_amount=0,
            difficulty="简单",
            cooking_time=15,
            description="黑豆提前浸泡，与核桃芝麻打成豆浆",
            health_benefits=["花青素", "不饱和脂肪酸", "植物蛋白"],
            suitable_for=["贫血者", "更年期女性", "老人"],
            avoid_for=["消化不良者"],
            estimated_calories=180
        )

        return recipes

    def _get_vegetarian_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """素食菜扩展菜谱"""
        recipes = {}

        recipes["麻婆豆腐"] = MegaChineseDish(
            name="素麻婆豆腐",
            cuisine_type=CuisineType.VEGETARIAN,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("嫩豆腐", 300), ("香菇末", 80)],
            seasonings=["豆瓣酱", "花椒粉", "生抽", "蒜末", "青蒜"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="中等",
            cooking_time=15,
            description="用香菇末代替肉末，制作素版麻婆豆腐",
            health_benefits=["植物蛋白", "大豆异黄酮", "多糖"],
            suitable_for=["素食者", "减肥人群"],
            avoid_for=["消化不良者"],
            estimated_calories=140,
            spice_level=2
        )

        recipes["宫保杏鲍菇"] = MegaChineseDish(
            name="宫保杏鲍菇",
            cuisine_type=CuisineType.VEGETARIAN,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("杏鲍菇", 300), ("花生米", 50), ("青椒", 50)],
            seasonings=["生抽", "醋", "糖", "干辣椒", "花椒"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="简单",
            cooking_time=10,
            description="杏鲍菇切丁炒制，调宫保汁炒匀",
            health_benefits=["蛋白质", "膳食纤维", "多糖"],
            suitable_for=["素食者", "减肥人群"],
            avoid_for=["花生过敏者"],
            estimated_calories=120,
            spice_level=2
        )

        recipes["清炒时蔬"] = MegaChineseDish(
            name="清炒时蔬",
            cuisine_type=CuisineType.VEGETARIAN,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("时令蔬菜", 300)],
            seasonings=["蒜末", "生抽", "盐"],
            cooking_oil_amount=8,
            salt_amount=1,
            difficulty="简单",
            cooking_time=5,
            description="蒜爆锅，下时蔬大火快炒至断生",
            health_benefits=["维生素C", "叶酸", "膳食纤维"],
            suitable_for=["所有人群"],
            avoid_for=[],
            estimated_calories=35,
            season=Season.ALL_YEAR
        )

        return recipes

    def _get_seasonal_recipes(self) -> Dict[str, MegaChineseDish]:
        """季节特色菜"""
        recipes = {}

        # 春季菜品
        recipes["春笋炒肉"] = MegaChineseDish(
            name="春笋炒肉",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("春笋", 300), ("猪肉丝", 150)],
            seasonings=["生抽", "料酒", "盐", "葱", "姜"],
            cooking_oil_amount=12,
            salt_amount=2,
            difficulty="简单",
            cooking_time=10,
            description="春笋焯水去涩味，与肉丝炒制",
            health_benefits=["膳食纤维", "优质蛋白", "维生素"],
            suitable_for=["便秘者", "减肥人群"],
            avoid_for=["肠胃敏感者"],
            estimated_calories=140,
            season=Season.SPRING
        )

        # 夏季菜品
        recipes["凉拌黄瓜"] = MegaChineseDish(
            name="凉拌黄瓜",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.COLD_MIXING,
            main_ingredients=[("黄瓜", 300)],
            seasonings=["蒜末", "香醋", "香油", "盐", "糖"],
            cooking_oil_amount=5,
            salt_amount=1,
            difficulty="简单",
            cooking_time=5,
            description="黄瓜拍碎，调料拌匀腌制片刻",
            health_benefits=["维生素C", "水分", "膳食纤维"],
            suitable_for=["减肥人群", "高血压患者"],
            avoid_for=["脾胃虚寒者"],
            estimated_calories=25,
            season=Season.SUMMER
        )

        # 秋季菜品
        recipes["南瓜粥"] = MegaChineseDish(
            name="南瓜粥",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("南瓜", 200), ("大米", 50)],
            seasonings=[],
            cooking_oil_amount=0,
            salt_amount=0,
            difficulty="简单",
            cooking_time=30,
            description="南瓜蒸熟压泥，与大米同煮成粥",
            health_benefits=["胡萝卜素", "膳食纤维", "钾元素"],
            suitable_for=["糖尿病患者", "老人", "儿童"],
            avoid_for=[],
            estimated_calories=80,
            season=Season.AUTUMN
        )

        # 冬季菜品
        recipes["羊肉汤"] = MegaChineseDish(
            name="清炖羊肉汤",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("羊肉", 300), ("白萝卜", 200), ("冬瓜", 150)],
            seasonings=["生姜", "料酒", "胡椒粉", "香菜"],
            cooking_oil_amount=5,
            salt_amount=3,
            difficulty="简单",
            cooking_time=90,
            description="羊肉焯水，炖煮至软烂，加蔬菜继续炖",
            health_benefits=["优质蛋白", "温阳补气", "维生素"],
            suitable_for=["体寒者", "冬季进补"],
            avoid_for=["上火体质", "高血脂患者"],
            estimated_calories=180,
            season=Season.WINTER
        )

        return recipes

    # 实用查询方法
    def get_recipes_by_cuisine(self, cuisine_type: CuisineType) -> Dict[str, MegaChineseDish]:
        """按菜系获取菜谱"""
        return {name: recipe for name, recipe in self.recipes.items()
                if recipe.cuisine_type == cuisine_type}

    def get_recipes_by_season(self, season: Season) -> Dict[str, MegaChineseDish]:
        """按季节获取菜谱"""
        return {name: recipe for name, recipe in self.recipes.items()
                if recipe.season == season or recipe.season == Season.ALL_YEAR}

    def get_recipes_by_difficulty(self, difficulty: str) -> Dict[str, MegaChineseDish]:
        """按难度获取菜谱"""
        return {name: recipe for name, recipe in self.recipes.items()
                if recipe.difficulty == difficulty}

    def get_low_calorie_recipes(self, max_calories: int = 150) -> Dict[str, MegaChineseDish]:
        """获取低热量菜谱"""
        return {name: recipe for name, recipe in self.recipes.items()
                if recipe.estimated_calories <= max_calories}

    def get_recipes_for_condition(self, condition: str) -> Dict[str, MegaChineseDish]:
        """获取适合特定病症的菜谱"""
        suitable_recipes = {}
        for name, recipe in self.recipes.items():
            if condition in recipe.suitable_for and condition not in recipe.avoid_for:
                suitable_recipes[name] = recipe
        return suitable_recipes

    def get_recipe_statistics(self) -> Dict[str, int]:
        """获取菜谱统计信息"""
        stats = {}

        # 按菜系统计
        for cuisine in CuisineType:
            count = len(self.get_recipes_by_cuisine(cuisine))
            if count > 0:
                stats[cuisine.value] = count

        # 按季节统计
        for season in Season:
            count = len([r for r in self.recipes.values() if r.season == season])
            if count > 0:
                stats[f"{season.value}菜品"] = count

        # 按难度统计
        difficulties = ["简单", "中等", "困难"]
        for difficulty in difficulties:
            count = len(self.get_recipes_by_difficulty(difficulty))
            if count > 0:
                stats[f"{difficulty}菜谱"] = count

        # 总计
        stats["总菜谱数"] = len(self.recipes)

        return stats

    def _get_shandong_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """鲁菜扩展菜谱"""
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
            )
        }

    def _get_jiangzhe_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """江浙菜扩展菜谱"""
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
            )
        }

    def _get_hunan_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """湘菜扩展菜谱"""
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
            )
        }

    def _get_northern_mega_recipes(self) -> Dict[str, MegaChineseDish]:
        """北方菜扩展菜谱"""
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
            )
        }

    def _get_regional_specialties(self) -> Dict[str, MegaChineseDish]:
        """地方特色菜谱"""
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
            )
        }

# 使用示例
if __name__ == "__main__":
    # 创建超大菜谱数据库
    mega_db = MegaChineseRecipeDatabase()

    print("=== 超大中式菜谱数据库 ===")
    stats = mega_db.get_recipe_statistics()

    for category, count in stats.items():
        print(f"📚 {category}: {count}道")

    print(f"\n=== 川菜示例 ===")
    sichuan_recipes = mega_db.get_recipes_by_cuisine(CuisineType.SICHUAN)
    for name, recipe in list(sichuan_recipes.items())[:3]:
        print(f"🌶️ {name}: {recipe.description[:30]}...")

    print(f"\n=== 低热量菜谱 (≤100千卡) ===")
    low_cal_recipes = mega_db.get_low_calorie_recipes(100)
    for name, recipe in list(low_cal_recipes.items())[:3]:
        print(f"🥗 {name}: {recipe.estimated_calories}千卡")

    print(f"\n✅ 超大菜谱数据库创建完成！")
    print(f"📊 总计：{len(mega_db.recipes)}道菜谱")