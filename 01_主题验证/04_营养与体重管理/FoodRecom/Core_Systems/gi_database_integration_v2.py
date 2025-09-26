#!/usr/bin/env python3
"""
血糖指数(GI)数据库集成系统 v2.0
扩充版 - 95种食物完整数据库
为糖尿病患者提供科学的血糖管理支持
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math

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
class FoodGIData:
    """食物血糖指数数据"""
    name: str
    gi_value: int                    # 血糖指数值
    gi_level: GILevel               # GI等级
    portion_size_g: int             # 标准份量(克)
    carb_per_portion: float         # 每份碳水化合物(克)
    gl_value: float                 # 血糖负荷值 = GI × 碳水/100
    gl_level: GLLevel               # GL等级
    category: str                   # 食物分类
    preparation_notes: str = ""      # 制备说明
    diabetes_recommendation: str = "" # 糖尿病建议

@dataclass
class PatientProfile:
    """患者档案 - 支持饮食偏好"""
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
    preferred_cuisines: List[str] = None     # 偏好菜系
    disliked_foods: List[str] = None         # 不喜欢的食物
    dietary_restrictions: List[str] = None    # 饮食限制
    spice_tolerance: str = "中等"            # 辣度承受
    cooking_preferences: List[str] = None     # 烹饪偏好

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

class GIDatabaseSystemV2:
    """血糖指数数据库系统 v2.0 - 扩充版"""

    def __init__(self):
        self.gi_database = self._initialize_expanded_gi_database()
        print(f"🩺 血糖指数数据库 v2.0 已加载")
        print(f"📊 收录食物: {len(self.gi_database)} 种")

        # 统计各等级食物数量
        low_gi_count = len([f for f in self.gi_database.values() if f.gi_level == GILevel.LOW])
        medium_gi_count = len([f for f in self.gi_database.values() if f.gi_level == GILevel.MEDIUM])
        high_gi_count = len([f for f in self.gi_database.values() if f.gi_level == GILevel.HIGH])

        print(f"🟢 低GI食物: {low_gi_count}种 ({low_gi_count/len(self.gi_database)*100:.1f}%)")
        print(f"🟡 中GI食物: {medium_gi_count}种 ({medium_gi_count/len(self.gi_database)*100:.1f}%)")
        print(f"🔴 高GI食物: {high_gi_count}种 ({high_gi_count/len(self.gi_database)*100:.1f}%)")

    def _initialize_expanded_gi_database(self) -> Dict[str, FoodGIData]:
        """初始化扩充版GI数据库 - 95种食物"""
        gi_foods = {}

        # 谷物类 (15种)
        gi_foods["大米(白米)"] = FoodGIData("大米(白米)", 83, GILevel.HIGH, 150, 35.0, 29.1, GLLevel.HIGH, "谷物", "煮熟的白米饭", "限制摄入，用糙米替代")
        gi_foods["糙米"] = FoodGIData("糙米", 50, GILevel.LOW, 150, 33.0, 16.5, GLLevel.MEDIUM, "谷物", "煮熟的糙米饭", "推荐糖尿病患者主食")
        gi_foods["燕麦(即食)"] = FoodGIData("燕麦(即食)", 55, GILevel.LOW, 40, 24.0, 13.2, GLLevel.MEDIUM, "谷物", "即食燕麦片", "早餐首选，含β-葡聚糖")
        gi_foods["燕麦片(生)"] = FoodGIData("燕麦片(生)", 40, GILevel.LOW, 40, 24.0, 9.6, GLLevel.LOW, "谷物", "需煮制的燕麦", "需煮制，GI更低")
        gi_foods["荞麦面"] = FoodGIData("荞麦面", 45, GILevel.LOW, 150, 30.0, 13.5, GLLevel.MEDIUM, "谷物", "煮熟的荞麦面条", "优秀低GI主食，富含芦丁")
        gi_foods["全麦面包"] = FoodGIData("全麦面包", 51, GILevel.LOW, 50, 13.0, 6.6, GLLevel.LOW, "谷物", "100%全麦面包", "比白面包更适合")
        gi_foods["白面包"] = FoodGIData("白面包", 75, GILevel.HIGH, 50, 15.0, 11.3, GLLevel.MEDIUM, "谷物", "精制白面包", "应避免或限制摄入")
        gi_foods["薏米"] = FoodGIData("薏米", 54, GILevel.LOW, 150, 23.0, 12.4, GLLevel.MEDIUM, "谷物", "煮熟的薏米", "健脾利湿，适合糖尿病患者")
        gi_foods["黑米"] = FoodGIData("黑米", 42, GILevel.LOW, 150, 43.3, 18.2, GLLevel.MEDIUM, "谷物", "煮熟的黑米饭", "花青素丰富，抗氧化强")
        gi_foods["藜麦"] = FoodGIData("藜麦", 35, GILevel.LOW, 150, 30.6, 10.7, GLLevel.MEDIUM, "谷物", "煮熟的藜麦", "完全蛋白质，营养价值高")
        gi_foods["小米"] = FoodGIData("小米", 52, GILevel.LOW, 150, 30.0, 15.6, GLLevel.MEDIUM, "谷物", "小米粥", "易消化，适合老年患者")
        gi_foods["青稞"] = FoodGIData("青稞", 48, GILevel.LOW, 150, 30.2, 14.5, GLLevel.MEDIUM, "谷物", "煮熟的青稞", "高原谷物，β-葡聚糖含量高")
        gi_foods["玉米"] = FoodGIData("玉米", 60, GILevel.MEDIUM, 150, 16.0, 9.6, GLLevel.LOW, "谷物", "煮熟的玉米", "膳食纤维丰富，控制分量")
        gi_foods["意大利面"] = FoodGIData("意大利面", 58, GILevel.MEDIUM, 150, 40.0, 23.2, GLLevel.HIGH, "谷物", "煮熟的意面", "比精制面条好，但仍需控制")
        gi_foods["玉米片"] = FoodGIData("玉米片", 81, GILevel.HIGH, 30, 25.0, 20.3, GLLevel.HIGH, "谷物", "早餐玉米片", "应避免，用燕麦片替代")

        # 薯类 (6种)
        gi_foods["甘薯(蒸)"] = FoodGIData("甘薯(蒸)", 54, GILevel.LOW, 150, 24.0, 12.8, GLLevel.MEDIUM, "薯类", "蒸制甘薯", "富含β-胡萝卜素")
        gi_foods["紫薯"] = FoodGIData("紫薯", 47, GILevel.LOW, 150, 24.0, 11.2, GLLevel.MEDIUM, "薯类", "蒸制紫薯", "花青素丰富，抗氧化")
        gi_foods["山药"] = FoodGIData("山药", 51, GILevel.LOW, 150, 26.0, 13.3, GLLevel.MEDIUM, "薯类", "蒸制山药", "药食同源，益气养阴")
        gi_foods["芋头"] = FoodGIData("芋头", 53, GILevel.LOW, 150, 24.0, 12.7, GLLevel.MEDIUM, "薯类", "蒸制芋头", "钾含量高，适合高血压合并糖尿病")
        gi_foods["马铃薯(煮)"] = FoodGIData("马铃薯(煮)", 78, GILevel.HIGH, 150, 20.0, 15.6, GLLevel.MEDIUM, "薯类", "水煮土豆", "建议用甘薯、山药替代")
        gi_foods["红薯(烤)"] = FoodGIData("红薯(烤)", 63, GILevel.MEDIUM, 150, 27.0, 17.1, GLLevel.MEDIUM, "薯类", "烤制红薯", "比蒸制GI稍高，注意分量")

        # 豆类 (12种)
        gi_foods["绿豆"] = FoodGIData("绿豆", 25, GILevel.LOW, 150, 25.0, 6.2, GLLevel.LOW, "豆类", "煮熟的绿豆", "清热解毒，极低GI")
        gi_foods["红豆"] = FoodGIData("红豆", 29, GILevel.LOW, 150, 22.0, 6.4, GLLevel.LOW, "豆类", "煮熟的红豆", "补血养心，膳食纤维丰富")
        gi_foods["黄豆"] = FoodGIData("黄豆", 18, GILevel.LOW, 100, 11.0, 2.0, GLLevel.LOW, "豆类", "煮熟的黄豆", "优质蛋白，异黄酮丰富")
        gi_foods["黑豆"] = FoodGIData("黑豆", 30, GILevel.LOW, 150, 18.0, 5.4, GLLevel.LOW, "豆类", "煮熟的黑豆", "补肾益阴，花青素丰富")
        gi_foods["扁豆"] = FoodGIData("扁豆", 38, GILevel.LOW, 150, 23.5, 8.9, GLLevel.LOW, "豆类", "煮熟的扁豆", "健脾化湿，B族维生素丰富")
        gi_foods["鹰嘴豆"] = FoodGIData("鹰嘴豆", 33, GILevel.LOW, 150, 24.0, 8.0, GLLevel.LOW, "豆类", "煮熟的鹰嘴豆", "地中海饮食，蛋白质含量高")
        gi_foods["豌豆"] = FoodGIData("豌豆", 45, GILevel.LOW, 150, 21.0, 9.5, GLLevel.LOW, "豆类", "煮熟的豌豆", "维生素K丰富，有助骨骼健康")
        gi_foods["蚕豆"] = FoodGIData("蚕豆", 40, GILevel.LOW, 150, 18.0, 7.2, GLLevel.LOW, "豆类", "煮熟的蚕豆", "叶酸含量高，适合孕期糖尿病")
        gi_foods["四季豆"] = FoodGIData("四季豆", 30, GILevel.LOW, 150, 7.0, 2.1, GLLevel.LOW, "豆类", "炒制四季豆", "极低GL，可自由摄入")
        gi_foods["豆腐"] = FoodGIData("豆腐", 15, GILevel.LOW, 100, 6.0, 0.9, GLLevel.LOW, "豆类", "新鲜豆腐", "优质植物蛋白，低碳水化合物")
        gi_foods["豆浆"] = FoodGIData("豆浆", 30, GILevel.LOW, 250, 3.5, 1.1, GLLevel.LOW, "豆类", "无糖豆浆", "植物蛋白饮品，无糖版本")
        gi_foods["花生"] = FoodGIData("花生", 15, GILevel.LOW, 30, 5.0, 0.8, GLLevel.LOW, "豆类", "生花生或水煮", "健康脂肪，适量摄入")

        # 蔬菜类 (18种)
        gi_foods["西兰花"] = FoodGIData("西兰花", 10, GILevel.LOW, 150, 5.2, 0.8, GLLevel.LOW, "蔬菜", "水煮或蒸制", "抗癌蔬菜之王，自由摄入")
        gi_foods["菠菜"] = FoodGIData("菠菜", 15, GILevel.LOW, 150, 6.0, 0.9, GLLevel.LOW, "蔬菜", "焯水后烹饪", "叶酸、铁含量高")
        gi_foods["白菜"] = FoodGIData("白菜", 25, GILevel.LOW, 150, 4.8, 1.2, GLLevel.LOW, "蔬菜", "炒制或煮汤", "水分含量高，维生素C丰富")
        gi_foods["芹菜"] = FoodGIData("芹菜", 35, GILevel.LOW, 150, 4.0, 1.4, GLLevel.LOW, "蔬菜", "炒制或凉拌", "降血压，膳食纤维丰富")
        gi_foods["生菜"] = FoodGIData("生菜", 20, GILevel.LOW, 150, 2.5, 0.5, GLLevel.LOW, "蔬菜", "生食为主", "生食佳品，热量极低")
        gi_foods["黄瓜"] = FoodGIData("黄瓜", 15, GILevel.LOW, 150, 4.6, 0.7, GLLevel.LOW, "蔬菜", "生食或凉拌", "利尿消肿，含硅元素美容")
        gi_foods["番茄"] = FoodGIData("番茄", 30, GILevel.LOW, 150, 7.7, 2.3, GLLevel.LOW, "蔬菜", "生食或熟制", "番茄红素丰富，抗氧化")
        gi_foods["茄子"] = FoodGIData("茄子", 25, GILevel.LOW, 150, 11.2, 2.8, GLLevel.LOW, "蔬菜", "蒸制或炒制", "膳食纤维丰富，有助控糖")
        gi_foods["青椒"] = FoodGIData("青椒", 40, GILevel.LOW, 150, 6.0, 2.4, GLLevel.LOW, "蔬菜", "炒制或生食", "维生素C含量极高")
        gi_foods["胡萝卜(生)"] = FoodGIData("胡萝卜(生)", 35, GILevel.LOW, 150, 8.0, 2.8, GLLevel.LOW, "蔬菜", "生食胡萝卜", "β-胡萝卜素丰富")
        gi_foods["胡萝卜(煮)"] = FoodGIData("胡萝卜(煮)", 85, GILevel.HIGH, 150, 8.0, 6.8, GLLevel.LOW, "蔬菜", "煮熟的胡萝卜", "建议生食或轻微加热")
        gi_foods["洋葱"] = FoodGIData("洋葱", 25, GILevel.LOW, 150, 12.4, 3.1, GLLevel.LOW, "蔬菜", "炒制或生食", "含硫化合物，调节血糖")
        gi_foods["大蒜"] = FoodGIData("大蒜", 30, GILevel.LOW, 10, 4.0, 1.0, GLLevel.LOW, "蔬菜", "调味使用", "抗菌消炎，调节血脂")
        gi_foods["韭菜"] = FoodGIData("韭菜", 25, GILevel.LOW, 150, 6.0, 1.5, GLLevel.LOW, "蔬菜", "炒制或包饺子", "补肾壮阳，膳食纤维丰富")
        gi_foods["苦瓜"] = FoodGIData("苦瓜", 24, GILevel.LOW, 150, 5.6, 1.4, GLLevel.LOW, "蔬菜", "炒制或凉拌", "苦瓜素有助降血糖")
        gi_foods["冬瓜"] = FoodGIData("冬瓜", 15, GILevel.LOW, 150, 5.4, 0.8, GLLevel.LOW, "蔬菜", "煮汤或清炒", "利水消肿，钾含量高")
        gi_foods["丝瓜"] = FoodGIData("丝瓜", 20, GILevel.LOW, 150, 7.4, 1.1, GLLevel.LOW, "蔬菜", "清炒或煮汤", "清热化痰，维生素C丰富")
        gi_foods["萝卜"] = FoodGIData("萝卜", 35, GILevel.LOW, 150, 6.0, 2.1, GLLevel.LOW, "蔬菜", "生食或煮汤", "消食化痰，维生素C丰富")

        # 水果类 (15种)
        gi_foods["草莓"] = FoodGIData("草莓", 40, GILevel.LOW, 150, 7.7, 3.1, GLLevel.LOW, "水果", "新鲜草莓", "维生素C丰富，抗氧化")
        gi_foods["蓝莓"] = FoodGIData("蓝莓", 53, GILevel.LOW, 150, 9.6, 5.1, GLLevel.LOW, "水果", "新鲜蓝莓", "花青素之王，护眼明目")
        gi_foods["樱桃"] = FoodGIData("樱桃", 22, GILevel.LOW, 150, 16.8, 3.7, GLLevel.LOW, "水果", "新鲜樱桃", "花青素丰富，抗炎作用")
        gi_foods["柚子"] = FoodGIData("柚子", 25, GILevel.LOW, 150, 11.2, 2.8, GLLevel.LOW, "水果", "新鲜柚子", "维生素C高，柚皮苷有助控糖")
        gi_foods["橙子"] = FoodGIData("橙子", 45, GILevel.LOW, 150, 9.8, 4.4, GLLevel.LOW, "水果", "新鲜橙子", "维生素C、叶酸丰富")
        gi_foods["苹果"] = FoodGIData("苹果", 36, GILevel.LOW, 150, 14.4, 5.2, GLLevel.LOW, "水果", "新鲜苹果", "果胶丰富，有助控制血糖")
        gi_foods["梨"] = FoodGIData("梨", 38, GILevel.LOW, 150, 10.6, 4.0, GLLevel.LOW, "水果", "新鲜梨", "润燥清肺，膳食纤维丰富")
        gi_foods["桃子"] = FoodGIData("桃子", 35, GILevel.LOW, 150, 10.5, 3.7, GLLevel.LOW, "水果", "新鲜桃子", "维生素A丰富，低热量")
        gi_foods["李子"] = FoodGIData("李子", 24, GILevel.LOW, 150, 11.2, 2.7, GLLevel.LOW, "水果", "新鲜李子", "有机酸丰富，助消化")
        gi_foods["猕猴桃"] = FoodGIData("猕猴桃", 50, GILevel.LOW, 150, 12.4, 6.2, GLLevel.LOW, "水果", "新鲜猕猴桃", "维生素C极高，膳食纤维丰富")
        gi_foods["柠檬"] = FoodGIData("柠檬", 25, GILevel.LOW, 100, 6.0, 1.5, GLLevel.LOW, "水果", "新鲜柠檬", "维生素C高，柠檬酸有助代谢")
        gi_foods["牛油果"] = FoodGIData("牛油果", 15, GILevel.LOW, 100, 6.0, 0.9, GLLevel.LOW, "水果", "新鲜牛油果", "单不饱和脂肪酸丰富")
        gi_foods["西瓜"] = FoodGIData("西瓜", 72, GILevel.HIGH, 150, 5.5, 4.0, GLLevel.LOW, "水果", "新鲜西瓜", "虽然GI高但GL低，可少量食用")
        gi_foods["香蕉(成熟)"] = FoodGIData("香蕉(成熟)", 60, GILevel.MEDIUM, 120, 20.3, 12.2, GLLevel.MEDIUM, "水果", "成熟香蕉", "富含钾元素，适量食用")
        gi_foods["葡萄"] = FoodGIData("葡萄", 62, GILevel.MEDIUM, 120, 15.5, 9.6, GLLevel.LOW, "水果", "新鲜葡萄", "白藜芦醇丰富，但糖分较高")

        # 奶制品 (6种)
        gi_foods["牛奶(全脂)"] = FoodGIData("牛奶(全脂)", 30, GILevel.LOW, 250, 12.3, 3.7, GLLevel.LOW, "奶制品", "常温或加热", "优质蛋白和钙质")
        gi_foods["酸奶(无糖)"] = FoodGIData("酸奶(无糖)", 35, GILevel.LOW, 200, 8.8, 3.1, GLLevel.LOW, "奶制品", "无添加糖酸奶", "益生菌丰富，改善肠道健康")
        gi_foods["酸奶(希腊式)"] = FoodGIData("酸奶(希腊式)", 11, GILevel.LOW, 200, 10.5, 1.9, GLLevel.LOW, "奶制品", "希腊式酸奶", "蛋白质含量更高，饱腹感强")
        gi_foods["奶酪(切达)"] = FoodGIData("奶酪(切达)", 25, GILevel.LOW, 30, 1.2, 0.4, GLLevel.LOW, "奶制品", "天然奶酪", "高蛋白低碳水")
        gi_foods["茅屋奶酪"] = FoodGIData("茅屋奶酪", 45, GILevel.LOW, 100, 4.0, 1.8, GLLevel.LOW, "奶制品", "新鲜茅屋奶酪", "低脂高蛋白，减重期选择")
        gi_foods["酸牛奶"] = FoodGIData("酸牛奶", 31, GILevel.LOW, 250, 11.0, 3.4, GLLevel.LOW, "奶制品", "传统酸奶", "传统发酵，营养易吸收")

        # 坚果种子 (8种)
        gi_foods["核桃"] = FoodGIData("核桃", 15, GILevel.LOW, 30, 1.2, 0.4, GLLevel.LOW, "坚果", "生核桃仁", "ω-3脂肪酸丰富，护心益脑")
        gi_foods["杏仁"] = FoodGIData("杏仁", 15, GILevel.LOW, 30, 3.0, 0.9, GLLevel.LOW, "坚果", "生杏仁", "维生素E高，抗氧化强")
        gi_foods["腰果"] = FoodGIData("腰果", 25, GILevel.LOW, 30, 12.0, 3.0, GLLevel.LOW, "坚果", "生腰果", "镁含量高，有助血糖控制")
        gi_foods["榛子"] = FoodGIData("榛子", 15, GILevel.LOW, 30, 2.8, 0.7, GLLevel.LOW, "坚果", "生榛子", "单不饱和脂肪酸丰富")
        gi_foods["开心果"] = FoodGIData("开心果", 15, GILevel.LOW, 30, 1.0, 0.3, GLLevel.LOW, "坚果", "带壳开心果", "膳食纤维高，饱腹感强")
        gi_foods["南瓜子"] = FoodGIData("南瓜子", 25, GILevel.LOW, 30, 5.6, 1.4, GLLevel.LOW, "种子", "生南瓜子", "锌含量高，增强免疫力")
        gi_foods["芝麻"] = FoodGIData("芝麻", 35, GILevel.LOW, 20, 3.2, 1.1, GLLevel.LOW, "种子", "生芝麻", "钙质丰富，芝麻素有益健康")
        gi_foods["亚麻籽"] = FoodGIData("亚麻籽", 35, GILevel.LOW, 20, 0.6, 0.2, GLLevel.LOW, "种子", "磨碎食用", "ω-3含量极高，抗炎作用")

        # 肉类 (5种) - GI=0
        gi_foods["鸡胸肉"] = FoodGIData("鸡胸肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "去皮烹饪", "无碳水化合物，高蛋白低脂")
        gi_foods["瘦猪肉"] = FoodGIData("瘦猪肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "瘦肉部位", "B族维生素丰富，适量摄入")
        gi_foods["牛瘦肉"] = FoodGIData("牛瘦肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "瘦牛肉", "血红素铁高，预防贫血")
        gi_foods["羊肉"] = FoodGIData("羊肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "瘦羊肉", "温补性质，冬季食用佳")
        gi_foods["鸭胸肉"] = FoodGIData("鸭胸肉", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "肉类", "去皮鸭胸", "不饱和脂肪酸含量高")

        # 鱼类 (6种) - GI=0
        gi_foods["三文鱼"] = FoodGIData("三文鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "清蒸或水煮", "ω-3脂肪酸极高，护心健脑")
        gi_foods["鲫鱼"] = FoodGIData("鲫鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "清蒸或煮汤", "蛋白质优质，易消化吸收")
        gi_foods["带鱼"] = FoodGIData("带鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "清蒸或红烧", "DHA含量高，益智健脑")
        gi_foods["鲈鱼"] = FoodGIData("鲈鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "清蒸为主", "低脂高蛋白，肉质鲜嫩")
        gi_foods["鳕鱼"] = FoodGIData("鳕鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "清蒸或水煮", "维生素D丰富，助钙吸收")
        gi_foods["沙丁鱼"] = FoodGIData("沙丁鱼", 0, GILevel.LOW, 100, 0, 0, GLLevel.LOW, "鱼类", "清蒸或罐头", "小型鱼类，汞含量低")

        # 蛋类 (2种) - GI=0
        gi_foods["鸡蛋"] = FoodGIData("鸡蛋", 0, GILevel.LOW, 50, 0, 0, GLLevel.LOW, "蛋类", "水煮或蒸制", "完全蛋白质，营养价值高")
        gi_foods["鸭蛋"] = FoodGIData("鸭蛋", 0, GILevel.LOW, 50, 0, 0, GLLevel.LOW, "蛋类", "水煮为主", "维生素B12含量高")

        # 油脂类 (2种) - GI=0
        gi_foods["橄榄油"] = FoodGIData("橄榄油", 0, GILevel.LOW, 10, 0, 0, GLLevel.LOW, "油脂", "特级初榨", "单不饱和脂肪酸高，地中海饮食核心")
        gi_foods["椰子油"] = FoodGIData("椰子油", 0, GILevel.LOW, 10, 0, 0, GLLevel.LOW, "油脂", "初榨椰子油", "中链脂肪酸，易被人体利用")

        return gi_foods

    def get_food_gi_info(self, food_name: str) -> Optional[FoodGIData]:
        """获取食物GI信息"""
        return self.gi_database.get(food_name)

    def search_by_gi_level(self, gi_level: GILevel) -> List[FoodGIData]:
        """按GI等级搜索食物"""
        return [food for food in self.gi_database.values() if food.gi_level == gi_level]

    def search_by_category(self, category: str) -> List[FoodGIData]:
        """按食物分类搜索"""
        return [food for food in self.gi_database.values() if food.category == category]

    def get_low_gi_foods(self) -> List[FoodGIData]:
        """获取所有低GI食物"""
        return self.search_by_gi_level(GILevel.LOW)

    def get_diabetes_friendly_foods(self) -> List[FoodGIData]:
        """获取糖尿病友好食物(低GI + 低GL)"""
        return [food for food in self.gi_database.values()
                if food.gi_level == GILevel.LOW and food.gl_level == GLLevel.LOW]

    def calculate_meal_gi_gl(self, meal_composition: List[Tuple[str, float]]) -> Tuple[float, float]:
        """
        计算混合餐食的加权平均GI和总GL
        meal_composition: [(食物名称, 重量g), ...]
        返回: (加权平均GI, 总GL)
        """
        if not meal_composition:
            return 0.0, 0.0

        total_carbs = 0.0
        weighted_gi_sum = 0.0
        total_gl = 0.0

        for food_name, weight_g in meal_composition:
            food_data = self.get_food_gi_info(food_name)
            if not food_data:
                continue

            # 计算该食物的碳水化合物量
            carb_ratio = weight_g / food_data.portion_size_g
            food_carbs = food_data.carb_per_portion * carb_ratio
            food_gl = (food_data.gi_value * food_carbs) / 100

            total_carbs += food_carbs
            weighted_gi_sum += food_data.gi_value * food_carbs
            total_gl += food_gl

        # 计算加权平均GI
        average_gi = weighted_gi_sum / total_carbs if total_carbs > 0 else 0

        return round(average_gi, 1), round(total_gl, 1)

    def generate_diabetes_meal_plan(self, target_gl: float = 15.0, patient: Optional[PatientProfile] = None) -> Dict[str, List[str]]:
        """生成基于饮食偏好的糖尿病患者餐食计划"""
        low_gi_foods = self.get_low_gi_foods()

        meal_plan = {
            "主食类": [],
            "蛋白质类": [],
            "蔬菜类": [],
            "水果类": [],
            "个性化说明": []
        }

        # 过滤掉过敏和不喜欢的食物
        avoid_foods = []
        if patient:
            if patient.allergies:
                avoid_foods.extend(patient.allergies)
            if patient.disliked_foods:
                avoid_foods.extend(patient.disliked_foods)

        for food in low_gi_foods:
            if food.gl_value <= target_gl:
                # 检查是否为过敏或不喜欢的食物
                if any(avoid_food in food.name for avoid_food in avoid_foods):
                    continue

                # 素食限制检查
                if patient and patient.dietary_restrictions and "素食" in patient.dietary_restrictions:
                    if food.category in ["肉类", "鱼类"] or any(meat in food.name for meat in ["鱼", "肉", "鸡", "鸭", "猪", "牛", "羊"]):
                        continue

                # 分类推荐
                if food.category in ["谷物", "薯类"]:
                    meal_plan["主食类"].append(f"{food.name} (GI:{food.gi_value}, GL:{food.gl_value:.1f})")
                elif food.category in ["肉类", "鱼类", "蛋类", "豆类"]:
                    meal_plan["蛋白质类"].append(f"{food.name} (GI:{food.gi_value}, GL:{food.gl_value:.1f})")
                elif food.category == "蔬菜":
                    meal_plan["蔬菜类"].append(f"{food.name} (GI:{food.gi_value}, GL:{food.gl_value:.1f})")
                elif food.category == "水果":
                    meal_plan["水果类"].append(f"{food.name} (GI:{food.gi_value}, GL:{food.gl_value:.1f})")

        # 添加个性化说明
        if patient:
            notes = []
            if patient.preferred_cuisines:
                notes.append(f"考虑{'/'.join(patient.preferred_cuisines)}口味偏好")
            if patient.dietary_restrictions:
                notes.append(f"遵循{'/'.join(patient.dietary_restrictions)}饮食要求")
            if avoid_foods:
                notes.append(f"已排除过敏/不喜食物: {'/'.join(avoid_foods)}")
            if patient.spice_tolerance != "中等":
                notes.append(f"适配{patient.spice_tolerance}口味")

            meal_plan["个性化说明"] = notes

        return meal_plan

    def generate_personalized_gi_recommendations(self, patient: PatientProfile) -> Dict[str, any]:
        """为患者生成个性化GI推荐"""
        recommendations = {
            "患者信息": {
                "姓名": patient.name,
                "BMI": f"{patient.bmi:.1f} ({patient.bmi_category})",
                "疾病": patient.diagnosed_diseases,
                "饮食偏好": {
                    "偏好菜系": patient.preferred_cuisines,
                    "不喜食物": patient.disliked_foods,
                    "饮食限制": patient.dietary_restrictions,
                    "辣度承受": patient.spice_tolerance
                }
            }
        }

        # 生成个性化餐食计划
        meal_plan = self.generate_diabetes_meal_plan(target_gl=10.0, patient=patient)
        recommendations["低GL餐食推荐"] = meal_plan

        # 特别推荐的低GI食物
        diabetes_friendly = self.get_diabetes_friendly_foods()
        avoid_foods = (patient.allergies or []) + (patient.disliked_foods or [])

        safe_foods = []
        for food in diabetes_friendly[:10]:  # 取前10个最佳选择
            if not any(avoid_food in food.name for avoid_food in avoid_foods):
                safe_foods.append(f"{food.name} (GI:{food.gi_value}, GL:{food.gl_value:.1f})")

        recommendations["最佳选择食物"] = safe_foods

        # 饮食建议
        advice = []
        if "糖尿病" in patient.diagnosed_diseases:
            advice.append("严格控制高GI食物，优选GL≤10的食物")
        if "高血压" in patient.diagnosed_diseases:
            advice.append("减少钠盐摄入，选择天然调味方式")
        if patient.bmi >= 28:
            advice.append("控制总热量，选择高纤维低GL食物增加饱腹感")

        if patient.dietary_restrictions:
            if "素食" in patient.dietary_restrictions:
                advice.append("重点关注豆类蛋白质，确保营养均衡")
            if "低盐" in patient.dietary_restrictions:
                advice.append("使用天然香料调味，避免加工食品")

        recommendations["专业建议"] = advice

        return recommendations

    def print_database_summary(self):
        """打印数据库摘要"""
        print("\n" + "="*60)
        print("📊 GI数据库 v2.0 摘要统计")
        print("="*60)

        categories = {}
        gi_levels = {GILevel.LOW: 0, GILevel.MEDIUM: 0, GILevel.HIGH: 0}

        for food in self.gi_database.values():
            # 按分类统计
            if food.category not in categories:
                categories[food.category] = 0
            categories[food.category] += 1

            # 按GI等级统计
            gi_levels[food.gi_level] += 1

        print(f"总食物数量: {len(self.gi_database)} 种")
        print("\n📈 GI等级分布:")
        for level, count in gi_levels.items():
            percentage = (count / len(self.gi_database)) * 100
            print(f"  {level.value}: {count}种 ({percentage:.1f}%)")

        print("\n🗂️ 食物分类分布:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}种")

# 使用示例
if __name__ == "__main__":
    # 初始化系统
    gi_system = GIDatabaseSystemV2()

    # 打印摘要
    gi_system.print_database_summary()

    # 测试功能
    print("\n" + "="*60)
    print("🔍 功能测试示例")
    print("="*60)

    # 1. 查询特定食物
    food_info = gi_system.get_food_gi_info("糙米")
    if food_info:
        print(f"\n1. 食物查询 - {food_info.name}:")
        print(f"   GI值: {food_info.gi_value} ({food_info.gi_level.value})")
        print(f"   GL值: {food_info.gl_value:.1f} ({food_info.gl_level.value})")
        print(f"   建议: {food_info.diabetes_recommendation}")

    # 2. 获取低GI食物数量
    low_gi_foods = gi_system.get_low_gi_foods()
    print(f"\n2. 低GI食物总数: {len(low_gi_foods)}种")

    # 3. 计算混合餐食GI/GL
    meal = [("糙米", 100), ("鸡胸肉", 100), ("西兰花", 150)]
    avg_gi, total_gl = gi_system.calculate_meal_gi_gl(meal)
    print(f"\n3. 健康餐食分析:")
    print(f"   组成: 糙米100g + 鸡胸肉100g + 西兰花150g")
    print(f"   平均GI: {avg_gi}")
    print(f"   总GL: {total_gl}")

    # 4. 生成餐食计划
    meal_plan = gi_system.generate_diabetes_meal_plan(target_gl=10.0)
    print(f"\n4. 低GL餐食推荐 (GL≤10):")
    for category, foods in meal_plan.items():
        if foods:
            print(f"   {category}: {len(foods)}种选择")

    print("\n🎉 GI数据库系统测试完成！")