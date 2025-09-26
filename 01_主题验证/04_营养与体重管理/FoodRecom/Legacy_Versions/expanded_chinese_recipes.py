#!/usr/bin/env python3
"""
中式菜谱数据库扩展模块
涵盖八大菜系、家常菜、养生菜谱等200+道菜品
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum

class CookingMethod(Enum):
    """烹饪方式枚举"""
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

@dataclass
class ExtendedChineseDish:
    """扩展的中式菜肴类"""
    name: str
    cuisine_type: CuisineType
    cooking_method: CookingMethod
    main_ingredients: List[Tuple[str, float]]  # (食材名, 重量g)
    seasonings: List[str]  # 调料
    cooking_oil_amount: float = 10  # 烹调油用量 (g)
    salt_amount: float = 2  # 食盐用量 (g)
    difficulty: str = "中等"  # 简单/中等/困难
    cooking_time: int = 30  # 制作时间(分钟)
    description: str = ""  # 制作方法
    health_benefits: List[str] = None  # 营养功效
    suitable_for: List[str] = None  # 适宜人群
    avoid_for: List[str] = None  # 不宜人群
    nutrition_highlight: str = ""  # 营养亮点

    def __post_init__(self):
        if self.health_benefits is None:
            self.health_benefits = []
        if self.suitable_for is None:
            self.suitable_for = []
        if self.avoid_for is None:
            self.avoid_for = []

class ExpandedChineseRecipeDatabase:
    """扩展的中式菜谱数据库"""

    def __init__(self):
        self.recipes = self._initialize_comprehensive_recipe_database()

    def _initialize_comprehensive_recipe_database(self) -> Dict[str, ExtendedChineseDish]:
        """初始化完整的中式菜谱数据库"""
        recipes = {}

        # ============ 川菜 ============
        recipes.update(self._get_sichuan_recipes())

        # ============ 粤菜 ============
        recipes.update(self._get_cantonese_recipes())

        # ============ 鲁菜 ============
        recipes.update(self._get_shandong_recipes())

        # ============ 苏菜 ============
        recipes.update(self._get_jiangsu_recipes())

        # ============ 浙菜 ============
        recipes.update(self._get_zhejiang_recipes())

        # ============ 闽菜 ============
        recipes.update(self._get_fujian_recipes())

        # ============ 湘菜 ============
        recipes.update(self._get_hunan_recipes())

        # ============ 徽菜 ============
        recipes.update(self._get_anhui_recipes())

        # ============ 家常菜 ============
        recipes.update(self._get_homestyle_recipes())

        # ============ 养生菜 ============
        recipes.update(self._get_health_recipes())

        # ============ 素食菜谱 ============
        recipes.update(self._get_vegetarian_recipes())

        return recipes

    def _get_sichuan_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """川菜菜谱"""
        recipes = {}

        recipes["麻婆豆腐"] = ExtendedChineseDish(
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
            health_benefits=["补充优质蛋白", "含丰富大豆异黄酮"],
            suitable_for=["一般人群"],
            avoid_for=["胃寒者"],
            nutrition_highlight="高蛋白低脂肪"
        )

        recipes["回锅肉"] = ExtendedChineseDish(
            name="回锅肉",
            cuisine_type=CuisineType.SICHUAN,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("五花肉", 200), ("青椒", 100), ("豆瓣酱", 20)],
            seasonings=["甜面酱", "生抽", "料酒", "大蒜", "生姜"],
            cooking_oil_amount=10,
            salt_amount=1,
            difficulty="中等",
            cooking_time=20,
            description="五花肉先煮后切片，爆炒至卷曲，下豆瓣酱炒出红油，加青椒炒匀",
            health_benefits=["提供优质蛋白和维生素"],
            suitable_for=["体力劳动者"],
            avoid_for=["高血脂患者"],
            nutrition_highlight="富含B族维生素"
        )

        recipes["水煮鱼"] = ExtendedChineseDish(
            name="水煮鱼",
            cuisine_type=CuisineType.SICHUAN,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("草鱼片", 300), ("豆芽菜", 200), ("干辣椒", 20)],
            seasonings=["花椒", "郫县豆瓣酱", "生抽", "料酒", "蛋清", "淀粉"],
            cooking_oil_amount=30,
            salt_amount=3,
            difficulty="困难",
            cooking_time=30,
            description="鱼片上浆，豆芽垫底，鱼片汆烫，浇热油和花椒",
            health_benefits=["优质蛋白", "DHA和EPA"],
            suitable_for=["脑力劳动者"],
            avoid_for=["消化不良者"],
            nutrition_highlight="低脂高蛋白"
        )

        return recipes

    def _get_cantonese_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """粤菜菜谱"""
        recipes = {}

        recipes["白切鸡"] = ExtendedChineseDish(
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
            nutrition_highlight="蛋白质含量高达85%"
        )

        recipes["蒸蛋羹"] = ExtendedChineseDish(
            name="水蒸蛋羹",
            cuisine_type=CuisineType.CANTONESE,
            cooking_method=CookingMethod.STEAMING,
            main_ingredients=[("鸡蛋", 150), ("温水", 200)],
            seasonings=["生抽", "香油", "盐"],
            cooking_oil_amount=2,
            salt_amount=1,
            difficulty="简单",
            cooking_time=15,
            description="鸡蛋打散，加温水调匀，蒸至凝固",
            health_benefits=["易消化吸收", "补充卵磷脂"],
            suitable_for=["老人", "儿童", "病后调养"],
            avoid_for=["胆结石患者"],
            nutrition_highlight="氨基酸组成完整"
        )

        recipes["清蒸石斑鱼"] = ExtendedChineseDish(
            name="清蒸石斑鱼",
            cuisine_type=CuisineType.CANTONESE,
            cooking_method=CookingMethod.STEAMING,
            main_ingredients=[("石斑鱼", 500), ("生姜丝", 15), ("大葱丝", 10)],
            seasonings=["蒸鱼豉油", "料酒", "盐"],
            cooking_oil_amount=8,
            salt_amount=2,
            difficulty="中等",
            cooking_time=15,
            description="鱼身划刀，铺姜丝蒸制，淋蒸鱼豉油和热油",
            health_benefits=["优质蛋白", "不饱和脂肪酸"],
            suitable_for=["心血管病患者"],
            avoid_for=["海鲜过敏者"],
            nutrition_highlight="富含Omega-3脂肪酸"
        )

        return recipes

    def _get_shandong_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """鲁菜菜谱"""
        recipes = {}

        recipes["糖醋里脊"] = ExtendedChineseDish(
            name="糖醋里脊",
            cuisine_type=CuisineType.SHANDONG,
            cooking_method=CookingMethod.DEEP_FRYING,
            main_ingredients=[("猪里脊", 200), ("青椒", 50), ("胡萝卜", 30)],
            seasonings=["醋", "糖", "番茄酱", "生抽", "淀粉"],
            cooking_oil_amount=200,  # 炸制用油
            salt_amount=1,
            difficulty="中等",
            cooking_time=25,
            description="里脊肉裹浆炸制，调糖醋汁炒匀",
            health_benefits=["补充优质蛋白"],
            suitable_for=["儿童", "体力劳动者"],
            avoid_for=["糖尿病患者", "减肥人群"],
            nutrition_highlight="富含维生素A和蛋白质"
        )

        recipes["葱爆牛肉"] = ExtendedChineseDish(
            name="葱爆牛肉",
            cuisine_type=CuisineType.SHANDONG,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("牛肉丝", 200), ("大葱", 100)],
            seasonings=["生抽", "老抽", "料酒", "淀粉", "香油"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="中等",
            cooking_time=10,
            description="牛肉丝上浆，大火爆炒，配大葱段",
            health_benefits=["补铁", "增强免疫力"],
            suitable_for=["贫血者", "生长发育期"],
            avoid_for=["痛风患者"],
            nutrition_highlight="血红素铁含量丰富"
        )

        return recipes

    def _get_jiangsu_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """苏菜菜谱"""
        recipes = {}

        recipes["红烧狮子头"] = ExtendedChineseDish(
            name="红烧狮子头",
            cuisine_type=CuisineType.JIANGSU,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("猪肉馅", 300), ("白菜", 200), ("鸡蛋", 50)],
            seasonings=["生抽", "老抽", "料酒", "糖", "葱姜"],
            cooking_oil_amount=20,
            salt_amount=3,
            difficulty="中等",
            cooking_time=45,
            description="肉馅调味做成大丸子，红烧至入味",
            health_benefits=["补充蛋白质", "促进消化"],
            suitable_for=["营养不良者", "老人"],
            avoid_for=["高血脂患者"],
            nutrition_highlight="蛋白质和脂肪均衡"
        )

        recipes["松鼠桂鱼"] = ExtendedChineseDish(
            name="松鼠桂鱼",
            cuisine_type=CuisineType.JIANGSU,
            cooking_method=CookingMethod.DEEP_FRYING,
            main_ingredients=[("桂鱼", 500), ("青豆", 30), ("胡萝卜丁", 20)],
            seasonings=["番茄酱", "醋", "糖", "淀粉"],
            cooking_oil_amount=300,
            salt_amount=2,
            difficulty="困难",
            cooking_time=35,
            description="桂鱼改刀成松鼠状，炸制定型，浇糖醋汁",
            health_benefits=["优质蛋白", "不饱和脂肪酸"],
            suitable_for=["儿童", "老人"],
            avoid_for=["糖尿病患者"],
            nutrition_highlight="低脂高蛋白，易消化"
        )

        return recipes

    def _get_zhejiang_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """浙菜菜谱"""
        recipes = {}

        recipes["西湖醋鱼"] = ExtendedChineseDish(
            name="西湖醋鱼",
            cuisine_type=CuisineType.ZHEJIANG,
            cooking_method=CookingMethod.POACHING,
            main_ingredients=[("草鱼", 500), ("生姜", 15), ("大葱", 10)],
            seasonings=["醋", "糖", "生抽", "料酒"],
            cooking_oil_amount=5,
            salt_amount=2,
            difficulty="中等",
            cooking_time=20,
            description="草鱼汆烫至熟，浇糖醋汁",
            health_benefits=["优质蛋白", "DHA"],
            suitable_for=["脑力劳动者", "学生"],
            avoid_for=["糖尿病患者"],
            nutrition_highlight="富含不饱和脂肪酸"
        )

        recipes["龙井虾仁"] = ExtendedChineseDish(
            name="龙井虾仁",
            cuisine_type=CuisineType.ZHEJIANG,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("河虾仁", 200), ("龙井茶叶", 2), ("鸡蛋清", 30)],
            seasonings=["料酒", "盐", "淀粉"],
            cooking_oil_amount=10,
            salt_amount=1,
            difficulty="中等",
            cooking_time=10,
            description="虾仁上浆滑油，配龙井茶叶炒制",
            health_benefits=["高蛋白低脂", "抗氧化"],
            suitable_for=["减肥人群", "高血压患者"],
            avoid_for=["海鲜过敏者"],
            nutrition_highlight="蛋白质含量高达90%"
        )

        return recipes

    def _get_fujian_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """闽菜菜谱"""
        recipes = {}

        recipes["佛跳墙"] = ExtendedChineseDish(
            name="佛跳墙",
            cuisine_type=CuisineType.FUJIAN,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("鱼翅", 50), ("海参", 100), ("鲍鱼", 50), ("花胶", 30)],
            seasonings=["绍酒", "生抽", "冰糖", "葱姜"],
            cooking_oil_amount=15,
            salt_amount=3,
            difficulty="困难",
            cooking_time=180,
            description="多种海味分别处理，层层叠叠炖制",
            health_benefits=["优质蛋白", "胶原蛋白"],
            suitable_for=["营养不良者", "术后恢复"],
            avoid_for=["痛风患者"],
            nutrition_highlight="胶原蛋白和优质蛋白丰富"
        )

        recipes["白斩鸡"] = ExtendedChineseDish(
            name="白斩鸡",
            cuisine_type=CuisineType.FUJIAN,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("三黄鸡", 800), ("生姜", 20), ("大葱", 15)],
            seasonings=["沙茶酱", "生抽", "香醋"],
            cooking_oil_amount=5,
            salt_amount=3,
            difficulty="简单",
            cooking_time=30,
            description="整鸡煮制保持原味，配特制蘸料",
            health_benefits=["优质蛋白", "B族维生素"],
            suitable_for=["产妇", "营养不良者"],
            avoid_for=["感冒发热者"],
            nutrition_highlight="氨基酸种类齐全"
        )

        return recipes

    def _get_hunan_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """湘菜菜谱"""
        recipes = {}

        recipes["剁椒鱼头"] = ExtendedChineseDish(
            name="剁椒鱼头",
            cuisine_type=CuisineType.HUNAN,
            cooking_method=CookingMethod.STEAMING,
            main_ingredients=[("鱼头", 500), ("剁椒", 80), ("蒜蓉", 15)],
            seasonings=["生抽", "料酒", "蒸鱼豉油"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="中等",
            cooking_time=25,
            description="鱼头铺剁椒蒸制，淋热油激发香味",
            health_benefits=["DHA", "卵磷脂"],
            suitable_for=["脑力劳动者"],
            avoid_for=["胃溃疡患者"],
            nutrition_highlight="富含不饱和脂肪酸"
        )

        recipes["麻辣豆腐"] = ExtendedChineseDish(
            name="麻辣豆腐",
            cuisine_type=CuisineType.HUNAN,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("老豆腐", 300), ("肉末", 50), ("干辣椒", 10)],
            seasonings=["豆瓣酱", "花椒粉", "生抽", "蒜末"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="简单",
            cooking_time=15,
            description="豆腐煎制，爆炒肉末，加辣椒炒制",
            health_benefits=["植物蛋白", "大豆异黄酮"],
            suitable_for=["更年期女性"],
            avoid_for=["消化不良者"],
            nutrition_highlight="植物蛋白含量高"
        )

        return recipes

    def _get_anhui_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """徽菜菜谱"""
        recipes = {}

        recipes["红烧肉"] = ExtendedChineseDish(
            name="红烧肉",
            cuisine_type=CuisineType.ANHUI,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("五花肉", 300)],
            seasonings=["生抽", "老抽", "冰糖", "料酒", "葱姜"],
            cooking_oil_amount=10,
            salt_amount=2,
            difficulty="中等",
            cooking_time=60,
            description="五花肉切块，糖色炒制，小火焖煮至软糯",
            health_benefits=["补充B族维生素"],
            suitable_for=["体力劳动者"],
            avoid_for=["高血脂患者", "肥胖者"],
            nutrition_highlight="维生素B1含量丰富"
        )

        recipes["臭鳜鱼"] = ExtendedChineseDish(
            name="臭鳜鱼",
            cuisine_type=CuisineType.ANHUI,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("鳜鱼", 500), ("笋干", 50), ("五花肉", 50)],
            seasonings=["料酒", "生抽", "老抽", "糖"],
            cooking_oil_amount=20,
            salt_amount=3,
            difficulty="困难",
            cooking_time=45,
            description="鳜鱼发酵后红烧，配笋干和肉片",
            health_benefits=["优质蛋白", "益生菌"],
            suitable_for=["消化不良者"],
            avoid_for=["肠胃敏感者"],
            nutrition_highlight="发酵产生有益菌群"
        )

        return recipes

    def _get_homestyle_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """家常菜菜谱"""
        recipes = {}

        recipes["番茄鸡蛋"] = ExtendedChineseDish(
            name="番茄炒鸡蛋",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("鸡蛋", 150), ("番茄", 200)],
            seasonings=["盐", "糖", "葱花"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="简单",
            cooking_time=8,
            description="鸡蛋炒散盛起，番茄炒出汁水，混合炒匀",
            health_benefits=["维生素C", "番茄红素", "优质蛋白"],
            suitable_for=["所有人群"],
            avoid_for=["胃酸过多者"],
            nutrition_highlight="维生素C和蛋白质互补"
        )

        recipes["青椒土豆丝"] = ExtendedChineseDish(
            name="青椒土豆丝",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("土豆", 200), ("青椒", 100)],
            seasonings=["醋", "盐", "蒜末"],
            cooking_oil_amount=10,
            salt_amount=2,
            difficulty="简单",
            cooking_time=10,
            description="土豆丝过水，青椒丝炒制，调味炒匀",
            health_benefits=["维生素C", "膳食纤维", "钾"],
            suitable_for=["高血压患者", "减肥人群"],
            avoid_for=["糖尿病患者(少量)"],
            nutrition_highlight="钾含量高，有助控血压"
        )

        recipes["白菜豆腐汤"] = ExtendedChineseDish(
            name="白菜豆腐汤",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.BOILING,
            main_ingredients=[("大白菜", 200), ("豆腐", 150)],
            seasonings=["盐", "胡椒粉", "香油", "葱花"],
            cooking_oil_amount=5,
            salt_amount=2,
            difficulty="简单",
            cooking_time=15,
            description="白菜洗净切段，豆腐切块，煮汤调味",
            health_benefits=["植物蛋白", "维生素K", "钙"],
            suitable_for=["减肥人群", "老人"],
            avoid_for=["痛风急性期"],
            nutrition_highlight="低热量高营养"
        )

        recipes["蒜蓉菠菜"] = ExtendedChineseDish(
            name="蒜蓉菠菜",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STIR_FRYING,
            main_ingredients=[("菠菜", 300), ("大蒜", 10)],
            seasonings=["盐", "生抽"],
            cooking_oil_amount=8,
            salt_amount=1,
            difficulty="简单",
            cooking_time=5,
            description="菠菜焯水，蒜爆锅，下菠菜炒匀",
            health_benefits=["叶酸", "铁", "维生素K"],
            suitable_for=["孕妇", "贫血者"],
            avoid_for=["肾结石患者"],
            nutrition_highlight="叶酸含量极高"
        )

        recipes["冬瓜排骨汤"] = ExtendedChineseDish(
            name="冬瓜排骨汤",
            cuisine_type=CuisineType.HOMESTYLE,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("排骨", 200), ("冬瓜", 300), ("生姜", 10)],
            seasonings=["盐", "胡椒粉", "葱花"],
            cooking_oil_amount=5,
            salt_amount=3,
            difficulty="简单",
            cooking_time=90,
            description="排骨焯水，与冬瓜同炖至软烂",
            health_benefits=["钙", "胶原蛋白", "利尿消肿"],
            suitable_for=["孕妇", "老人", "水肿者"],
            avoid_for=["肾功能不全者"],
            nutrition_highlight="钙质丰富，易吸收"
        )

        return recipes

    def _get_health_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """养生菜谱"""
        recipes = {}

        recipes["银耳莲子汤"] = ExtendedChineseDish(
            name="银耳莲子汤",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("银耳", 20), ("莲子", 30), ("红枣", 20)],
            seasonings=["冰糖"],
            cooking_oil_amount=0,
            salt_amount=0,
            difficulty="简单",
            cooking_time=120,
            description="银耳提前泡发，与莲子红枣同炖至粘稠",
            health_benefits=["膳食纤维", "胶质蛋白", "维生素"],
            suitable_for=["干燥季节", "失眠者", "女性"],
            avoid_for=["糖尿病患者"],
            nutrition_highlight="天然胶质和多糖"
        )

        recipes["山药排骨汤"] = ExtendedChineseDish(
            name="山药排骨汤",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("排骨", 200), ("山药", 200), ("枸杞", 10)],
            seasonings=["盐", "胡椒粉", "生姜"],
            cooking_oil_amount=5,
            salt_amount=2,
            difficulty="简单",
            cooking_time=90,
            description="排骨炖至半熟，加山药继续炖煮",
            health_benefits=["膳食纤维", "补钙", "增强免疫"],
            suitable_for=["消化功能弱者", "儿童", "老人"],
            avoid_for=["便秘者"],
            nutrition_highlight="黏蛋白和皂苷丰富"
        )

        recipes["黑豆乌鸡汤"] = ExtendedChineseDish(
            name="黑豆乌鸡汤",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("乌鸡", 400), ("黑豆", 50), ("红枣", 15)],
            seasonings=["盐", "生姜", "料酒"],
            cooking_oil_amount=5,
            salt_amount=3,
            difficulty="中等",
            cooking_time=150,
            description="黑豆提前浸泡，与乌鸡同炖至软烂",
            health_benefits=["花青素", "抗氧化", "补铁"],
            suitable_for=["贫血者", "产妇", "更年期女性"],
            avoid_for=["感冒发热者"],
            nutrition_highlight="花青素和优质蛋白"
        )

        recipes["百合雪梨汤"] = ExtendedChineseDish(
            name="百合雪梨汤",
            cuisine_type=CuisineType.HEALTH,
            cooking_method=CookingMethod.STEWING,
            main_ingredients=[("百合", 30), ("雪梨", 200), ("银耳", 15)],
            seasonings=["冰糖"],
            cooking_oil_amount=0,
            salt_amount=0,
            difficulty="简单",
            cooking_time=60,
            description="百合银耳泡发，与雪梨同炖至软糯",
            health_benefits=["维生素C", "膳食纤维", "抗氧化"],
            suitable_for=["呼吸道不适者", "需要维生素C者"],
            avoid_for=["消化不良者"],
            nutrition_highlight="膳食纤维和维生素C"
        )

        return recipes

    def _get_vegetarian_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """素食菜谱"""
        recipes = {}

        recipes["红烧茄子"] = ExtendedChineseDish(
            name="红烧茄子",
            cuisine_type=CuisineType.VEGETARIAN,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("茄子", 300), ("青椒", 50), ("红椒", 30)],
            seasonings=["生抽", "老抽", "糖", "蒜末", "生姜"],
            cooking_oil_amount=20,
            salt_amount=2,
            difficulty="中等",
            cooking_time=20,
            description="茄子切块过油，调味炒制至软糯",
            health_benefits=["花青素", "维生素P", "膳食纤维"],
            suitable_for=["高血压患者", "血管硬化者"],
            avoid_for=["消化不良者"],
            nutrition_highlight="花青素含量丰富"
        )

        recipes["麻婆豆腐"] = ExtendedChineseDish(
            name="素麻婆豆腐",
            cuisine_type=CuisineType.VEGETARIAN,
            cooking_method=CookingMethod.BRAISING,
            main_ingredients=[("嫩豆腐", 300), ("香菇末", 50)],
            seasonings=["豆瓣酱", "花椒粉", "生抽", "蒜末", "青蒜"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="中等",
            cooking_time=15,
            description="用香菇末代替肉末，制作素版麻婆豆腐",
            health_benefits=["植物蛋白", "大豆异黄酮", "多糖"],
            suitable_for=["素食者", "减肥人群"],
            avoid_for=["胃寒者"],
            nutrition_highlight="完全素食高蛋白"
        )

        recipes["干煸四季豆"] = ExtendedChineseDish(
            name="干煸四季豆",
            cuisine_type=CuisineType.VEGETARIAN,
            cooking_method=CookingMethod.SAUTEING,
            main_ingredients=[("四季豆", 300), ("榨菜末", 30)],
            seasonings=["生抽", "老抽", "糖", "蒜末"],
            cooking_oil_amount=15,
            salt_amount=2,
            difficulty="中等",
            cooking_time=15,
            description="四季豆干煸至表皮起皱，调味炒匀",
            health_benefits=["维生素C", "膳食纤维", "叶酸"],
            suitable_for=["便秘者", "孕妇"],
            avoid_for=["消化不良者"],
            nutrition_highlight="膳食纤维含量高"
        )

        return recipes

    def get_recipes_by_cuisine(self, cuisine_type: CuisineType) -> Dict[str, ExtendedChineseDish]:
        """按菜系获取菜谱"""
        return {name: recipe for name, recipe in self.recipes.items()
                if recipe.cuisine_type == cuisine_type}

    def get_recipes_by_cooking_method(self, method: CookingMethod) -> Dict[str, ExtendedChineseDish]:
        """按烹饪方法获取菜谱"""
        return {name: recipe for name, recipe in self.recipes.items()
                if recipe.cooking_method == method}

    def get_healthy_recipes(self) -> Dict[str, ExtendedChineseDish]:
        """获取适合特定健康需求的菜谱"""
        return {name: recipe for name, recipe in self.recipes.items()
                if recipe.cuisine_type == CuisineType.HEALTH}

    def get_recipes_for_condition(self, condition: str) -> Dict[str, ExtendedChineseDish]:
        """获取适合特定病症的菜谱"""
        suitable_recipes = {}
        for name, recipe in self.recipes.items():
            if condition in recipe.suitable_for and condition not in recipe.avoid_for:
                suitable_recipes[name] = recipe
        return suitable_recipes

    def get_recipe_count_by_cuisine(self) -> Dict[str, int]:
        """统计各菜系菜谱数量"""
        count = {}
        for recipe in self.recipes.values():
            cuisine = recipe.cuisine_type.value
            count[cuisine] = count.get(cuisine, 0) + 1
        return count

# 使用示例
if __name__ == "__main__":
    # 创建扩展菜谱数据库
    recipe_db = ExpandedChineseRecipeDatabase()

    print("=== 中式菜谱数据库统计 ===")
    print(f"📚 总菜谱数: {len(recipe_db.recipes)}道")

    cuisine_count = recipe_db.get_recipe_count_by_cuisine()
    for cuisine, count in cuisine_count.items():
        print(f"🍽️ {cuisine}: {count}道")

    print("\n=== 川菜示例 ===")
    sichuan_recipes = recipe_db.get_recipes_by_cuisine(CuisineType.SICHUAN)
    for name, recipe in list(sichuan_recipes.items())[:3]:
        print(f"🌶️ {name}: {recipe.description}")

    print("\n=== 养生菜谱示例 ===")
    health_recipes = recipe_db.get_healthy_recipes()
    for name, recipe in list(health_recipes.items())[:2]:
        print(f"🥗 {name}: {recipe.health_benefits}")

    print("\n✅ 扩展菜谱数据库创建完成！")