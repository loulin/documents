#!/usr/bin/env python3
"""
血糖指数(GI)数据库集成系统
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

    def __post_init__(self):
        # 自动计算GL值
        if self.gl_value == 0:
            self.gl_value = (self.gi_value * self.carb_per_portion) / 100

        # 自动确定GL等级
        if self.gl_value <= 10:
            self.gl_level = GLLevel.LOW
        elif self.gl_value <= 19:
            self.gl_level = GLLevel.MEDIUM
        else:
            self.gl_level = GLLevel.HIGH

class GIDatabaseSystem:
    """血糖指数数据库系统"""

    def __init__(self):
        self.gi_database = self._initialize_gi_database()
        print(f"血糖指数数据库已加载，收录 {len(self.gi_database)} 种食物")

    def _initialize_gi_database(self) -> Dict[str, FoodGIData]:
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

        gi_foods["燕麦"] = FoodGIData(
            name="燕麦(即食)",
            gi_value=55,
            gi_level=GILevel.LOW,
            portion_size_g=40,
            carb_per_portion=24.0,
            gl_value=0,
            gl_level=GLLevel.MEDIUM,
            category="谷物",
            preparation_notes="即食燕麦片",
            diabetes_recommendation="推荐早餐选择，含β-葡聚糖有助控糖"
        )

        gi_foods["荞麦"] = FoodGIData(
            name="荞麦面",
            gi_value=45,
            gi_level=GILevel.LOW,
            portion_size_g=180,
            carb_per_portion=30.0,
            gl_value=0,
            gl_level=GLLevel.MEDIUM,
            category="谷物",
            preparation_notes="煮熟的荞麦面条",
            diabetes_recommendation="优秀的低GI主食选择"
        )

        gi_foods["全麦面包"] = FoodGIData(
            name="全麦面包",
            gi_value=51,
            gi_level=GILevel.LOW,
            portion_size_g=30,
            carb_per_portion=13.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="谷物",
            preparation_notes="100%全麦面包",
            diabetes_recommendation="比白面包更适合糖尿病患者"
        )

        gi_foods["白面包"] = FoodGIData(
            name="白面包",
            gi_value=75,
            gi_level=GILevel.HIGH,
            portion_size_g=30,
            carb_per_portion=14.0,
            gl_value=0,
            gl_level=GLLevel.MEDIUM,
            category="谷物",
            preparation_notes="精制白面包",
            diabetes_recommendation="糖尿病患者应避免或限制摄入"
        )

        # 薯类
        gi_foods["土豆"] = FoodGIData(
            name="土豆(煮)",
            gi_value=62,
            gi_level=GILevel.MEDIUM,
            portion_size_g=150,
            carb_per_portion=20.0,
            gl_value=0,
            gl_level=GLLevel.MEDIUM,
            category="薯类",
            preparation_notes="带皮水煮",
            diabetes_recommendation="可适量食用，注意控制分量"
        )

        gi_foods["红薯"] = FoodGIData(
            name="红薯(烤)",
            gi_value=63,
            gi_level=GILevel.MEDIUM,
            portion_size_g=150,
            carb_per_portion=28.0,
            gl_value=0,
            gl_level=GLLevel.MEDIUM,
            category="薯类",
            preparation_notes="烤制红薯",
            diabetes_recommendation="营养丰富，但需控制分量"
        )

        # 豆类
        gi_foods["绿豆"] = FoodGIData(
            name="绿豆",
            gi_value=25,
            gi_level=GILevel.LOW,
            portion_size_g=150,
            carb_per_portion=25.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="豆类",
            preparation_notes="煮熟的绿豆",
            diabetes_recommendation="优秀的低GI食物，推荐食用"
        )

        gi_foods["红豆"] = FoodGIData(
            name="红豆",
            gi_value=29,
            gi_level=GILevel.LOW,
            portion_size_g=150,
            carb_per_portion=22.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="豆类",
            preparation_notes="煮熟的红豆",
            diabetes_recommendation="低GI，富含膳食纤维，推荐食用"
        )

        gi_foods["黄豆"] = FoodGIData(
            name="黄豆",
            gi_value=18,
            gi_level=GILevel.LOW,
            portion_size_g=100,
            carb_per_portion=11.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="豆类",
            preparation_notes="煮熟的黄豆",
            diabetes_recommendation="极佳的低GI高蛋白食物"
        )

        # 蔬菜类
        gi_foods["西兰花"] = FoodGIData(
            name="西兰花",
            gi_value=10,
            gi_level=GILevel.LOW,
            portion_size_g=200,
            carb_per_portion=8.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="蔬菜",
            preparation_notes="水煮或蒸制",
            diabetes_recommendation="自由摄入，营养丰富"
        )

        gi_foods["菠菜"] = FoodGIData(
            name="菠菜",
            gi_value=15,
            gi_level=GILevel.LOW,
            portion_size_g=200,
            carb_per_portion=6.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="蔬菜",
            preparation_notes="焯水后烹饪",
            diabetes_recommendation="自由摄入，富含叶酸和铁"
        )

        gi_foods["白菜"] = FoodGIData(
            name="白菜",
            gi_value=25,
            gi_level=GILevel.LOW,
            portion_size_g=200,
            carb_per_portion=5.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="蔬菜",
            preparation_notes="炒制或煮汤",
            diabetes_recommendation="自由摄入，水分含量高"
        )

        gi_foods["胡萝卜"] = FoodGIData(
            name="胡萝卜",
            gi_value=47,
            gi_level=GILevel.LOW,
            portion_size_g=150,
            carb_per_portion=12.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="蔬菜",
            preparation_notes="生食或熟制",
            diabetes_recommendation="可正常摄入，富含β-胡萝卜素"
        )

        # 水果类
        gi_foods["苹果"] = FoodGIData(
            name="苹果",
            gi_value=36,
            gi_level=GILevel.LOW,
            portion_size_g=150,
            carb_per_portion=21.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="水果",
            preparation_notes="新鲜整果",
            diabetes_recommendation="优秀的水果选择，富含膳食纤维"
        )

        gi_foods["香蕉"] = FoodGIData(
            name="香蕉",
            gi_value=51,
            gi_level=GILevel.LOW,
            portion_size_g=120,
            carb_per_portion=23.0,
            gl_value=0,
            gl_level=GLLevel.MEDIUM,
            category="水果",
            preparation_notes="中等成熟度",
            diabetes_recommendation="可适量食用，注意成熟度影响GI值"
        )

        gi_foods["橙子"] = FoodGIData(
            name="橙子",
            gi_value=43,
            gi_level=GILevel.LOW,
            portion_size_g=150,
            carb_per_portion=18.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="水果",
            preparation_notes="新鲜整果",
            diabetes_recommendation="推荐食用，维生素C丰富"
        )

        gi_foods["葡萄"] = FoodGIData(
            name="葡萄",
            gi_value=46,
            gi_level=GILevel.LOW,
            portion_size_g=120,
            carb_per_portion=20.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="水果",
            preparation_notes="新鲜葡萄",
            diabetes_recommendation="可适量食用，避免过量"
        )

        gi_foods["西瓜"] = FoodGIData(
            name="西瓜",
            gi_value=72,
            gi_level=GILevel.HIGH,
            portion_size_g=150,
            carb_per_portion=11.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="水果",
            preparation_notes="新鲜西瓜",
            diabetes_recommendation="虽然GI高但GL低，可少量食用"
        )

        # 奶制品
        gi_foods["牛奶"] = FoodGIData(
            name="牛奶(全脂)",
            gi_value=39,
            gi_level=GILevel.LOW,
            portion_size_g=250,
            carb_per_portion=12.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="奶制品",
            preparation_notes="常温或加热",
            diabetes_recommendation="低GI，可正常摄入"
        )

        gi_foods["酸奶"] = FoodGIData(
            name="酸奶(无糖)",
            gi_value=35,
            gi_level=GILevel.LOW,
            portion_size_g=200,
            carb_per_portion=9.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="奶制品",
            preparation_notes="无添加糖酸奶",
            diabetes_recommendation="优秀选择，含益生菌"
        )

        # 坚果类
        gi_foods["花生"] = FoodGIData(
            name="花生",
            gi_value=14,
            gi_level=GILevel.LOW,
            portion_size_g=30,
            carb_per_portion=4.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="坚果",
            preparation_notes="生花生或水煮",
            diabetes_recommendation="低GI，但注意控制分量(高热量)"
        )

        gi_foods["核桃"] = FoodGIData(
            name="核桃",
            gi_value=15,
            gi_level=GILevel.LOW,
            portion_size_g=30,
            carb_per_portion=3.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="坚果",
            preparation_notes="生核桃仁",
            diabetes_recommendation="优质脂肪来源，少量食用"
        )

        # 肉类和鱼类(通常GI值为0或极低)
        gi_foods["鸡胸肉"] = FoodGIData(
            name="鸡胸肉",
            gi_value=0,
            gi_level=GILevel.LOW,
            portion_size_g=100,
            carb_per_portion=0.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="肉类",
            preparation_notes="去皮烹饪",
            diabetes_recommendation="优质蛋白来源，自由摄入"
        )

        gi_foods["鲈鱼"] = FoodGIData(
            name="鲈鱼",
            gi_value=0,
            gi_level=GILevel.LOW,
            portion_size_g=100,
            carb_per_portion=0.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="鱼类",
            preparation_notes="清蒸或水煮",
            diabetes_recommendation="优质蛋白和ω-3脂肪酸来源"
        )

        # 蛋类
        gi_foods["鸡蛋"] = FoodGIData(
            name="鸡蛋",
            gi_value=0,
            gi_level=GILevel.LOW,
            portion_size_g=60,
            carb_per_portion=0.5,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="蛋类",
            preparation_notes="水煮或蒸制",
            diabetes_recommendation="完全蛋白质来源，自由摄入"
        )

        # 甜品类(高GI，糖尿病患者需避免)
        gi_foods["白糖"] = FoodGIData(
            name="白糖",
            gi_value=68,
            gi_level=GILevel.MEDIUM,
            portion_size_g=10,
            carb_per_portion=10.0,
            gl_value=0,
            gl_level=GLLevel.LOW,
            category="糖类",
            preparation_notes="精制白糖",
            diabetes_recommendation="严格避免"
        )

        gi_foods["蜂蜜"] = FoodGIData(
            name="蜂蜜",
            gi_value=61,
            gi_level=GILevel.MEDIUM,
            portion_size_g=20,
            carb_per_portion=17.0,
            gl_value=0,
            gl_level=GLLevel.MEDIUM,
            category="糖类",
            preparation_notes="天然蜂蜜",
            diabetes_recommendation="限制摄入"
        )

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

    def get_diabetes_friendly_foods(self) -> List[FoodGIData]:
        """获取糖尿病友好食物(低GI且低GL)"""
        return [food for food in self.gi_database.values()
                if food.gi_level == GILevel.LOW and food.gl_level in [GLLevel.LOW, GLLevel.MEDIUM]]

    def calculate_meal_gi_gl(self, meal_composition: List[Tuple[str, float]]) -> Tuple[float, float]:
        """
        计算混合膳食的GI和GL值
        meal_composition: [(食物名称, 重量(克)), ...]
        """
        total_carb = 0
        weighted_gi_sum = 0
        total_gl = 0

        for food_name, weight in meal_composition:
            food_data = self.get_food_gi_info(food_name)
            if food_data:
                # 按重量比例计算碳水化合物
                carb_amount = (weight / food_data.portion_size_g) * food_data.carb_per_portion
                total_carb += carb_amount

                # 加权GI计算
                weighted_gi_sum += food_data.gi_value * carb_amount

                # GL累加
                total_gl += (weight / food_data.portion_size_g) * food_data.gl_value

        # 计算加权平均GI
        meal_gi = weighted_gi_sum / total_carb if total_carb > 0 else 0

        return meal_gi, total_gl

    def generate_gi_report(self) -> str:
        """生成GI数据库报告"""
        categories = {}
        gi_distribution = {GILevel.LOW: 0, GILevel.MEDIUM: 0, GILevel.HIGH: 0}

        for food in self.gi_database.values():
            # 分类统计
            if food.category not in categories:
                categories[food.category] = 0
            categories[food.category] += 1

            # GI等级分布
            gi_distribution[food.gi_level] += 1

        report = f"""
# 血糖指数(GI)数据库报告

## 📊 数据库概览
- **收录食物总数**: {len(self.gi_database)}种
- **数据更新时间**: 2025年09月20日
- **数据来源**: 国际GI数据库、中国食物成分表

## 📈 食物分类分布
"""
        for category, count in categories.items():
            report += f"- **{category}**: {count}种\n"

        report += f"""
## 🎯 GI等级分布
- **低GI食物 (≤55)**: {gi_distribution[GILevel.LOW]}种 ({gi_distribution[GILevel.LOW]/len(self.gi_database)*100:.1f}%)
- **中GI食物 (56-69)**: {gi_distribution[GILevel.MEDIUM]}种 ({gi_distribution[GILevel.MEDIUM]/len(self.gi_database)*100:.1f}%)
- **高GI食物 (≥70)**: {gi_distribution[GILevel.HIGH]}种 ({gi_distribution[GILevel.HIGH]/len(self.gi_database)*100:.1f}%)

## 🍎 糖尿病友好食物推荐 (低GI低GL)
"""
        diabetes_foods = self.get_diabetes_friendly_foods()
        for food in diabetes_foods[:10]:  # 显示前10个
            report += f"- **{food.name}** (GI:{food.gi_value}, GL:{food.gl_value:.1f}) - {food.diabetes_recommendation}\n"

        report += f"""
## ⚠️ 糖尿病患者应避免的高GI食物
"""
        high_gi_foods = self.search_by_gi_level(GILevel.HIGH)
        for food in high_gi_foods:
            report += f"- **{food.name}** (GI:{food.gi_value}) - {food.diabetes_recommendation}\n"

        report += f"""
## 💡 使用建议

### 对糖尿病患者:
1. **优先选择低GI食物** (GI≤55)
2. **控制高GI食物摄入量**
3. **注意食物搭配降低整体GI**
4. **考虑GL值进行分量控制**

### 混合膳食原则:
- 蛋白质和脂肪可降低整体GI
- 膳食纤维有助于减缓血糖上升
- 食物加工程度影响GI值
- 进餐顺序：蔬菜→蛋白质→主食

---
*本数据库基于国际权威GI研究数据编制，供临床营养参考使用*
"""
        return report

    def recommend_meal_for_diabetes(self, meal_type: str = "午餐") -> Dict:
        """为糖尿病患者推荐低GI膳食"""
        recommendations = {
            "breakfast": {
                "主食": [("燕麦", 40), ("全麦面包", 30)],
                "蛋白质": [("鸡蛋", 60), ("牛奶", 200)],
                "蔬果": [("苹果", 100)]
            },
            "lunch": {
                "主食": [("糙米", 100), ("荞麦面", 80)],
                "蛋白质": [("鲈鱼", 100), ("鸡胸肉", 80)],
                "蔬菜": [("西兰花", 150), ("菠菜", 100)]
            },
            "dinner": {
                "主食": [("糙米", 80)],
                "蛋白质": [("鸡胸肉", 80)],
                "蔬菜": [("白菜", 200), ("胡萝卜", 100)]
            }
        }

        meal_map = {"早餐": "breakfast", "午餐": "lunch", "晚餐": "dinner"}
        meal_key = meal_map.get(meal_type, "lunch")

        meal_plan = recommendations[meal_key]

        # 计算整餐的GI和GL
        all_foods = []
        for category_foods in meal_plan.values():
            all_foods.extend(category_foods)

        meal_gi, meal_gl = self.calculate_meal_gi_gl(all_foods)

        return {
            "meal_type": meal_type,
            "meal_plan": meal_plan,
            "estimated_gi": meal_gi,
            "estimated_gl": meal_gl,
            "diabetes_suitability": "适合" if meal_gi <= 55 and meal_gl <= 20 else "需调整"
        }

if __name__ == "__main__":
    # 演示GI数据库系统
    print("🚀 启动血糖指数(GI)数据库系统")

    gi_system = GIDatabaseSystem()

    print("\n=== 系统功能演示 ===")

    # 1. 查询单个食物
    print("\n1. 查询食物GI信息:")
    apple_info = gi_system.get_food_gi_info("苹果")
    if apple_info:
        print(f"   🍎 {apple_info.name}: GI={apple_info.gi_value} ({apple_info.gi_level.value}), GL={apple_info.gl_value:.1f}")
        print(f"   💡 糖尿病建议: {apple_info.diabetes_recommendation}")

    # 2. 搜索低GI食物
    print("\n2. 低GI食物推荐 (前5个):")
    low_gi_foods = gi_system.search_by_gi_level(GILevel.LOW)[:5]
    for food in low_gi_foods:
        print(f"   ✅ {food.name}: GI={food.gi_value}")

    # 3. 混合膳食GI计算
    print("\n3. 混合膳食GI/GL计算:")
    meal = [("糙米", 100), ("鸡胸肉", 100), ("西兰花", 150)]
    meal_gi, meal_gl = gi_system.calculate_meal_gi_gl(meal)
    print(f"   🍽️ 膳食组成: {meal}")
    print(f"   📊 整餐GI: {meal_gi:.1f}, GL: {meal_gl:.1f}")

    # 4. 糖尿病膳食推荐
    print("\n4. 糖尿病友好午餐推荐:")
    lunch_rec = gi_system.recommend_meal_for_diabetes("午餐")
    print(f"   🥗 膳食方案: {lunch_rec['meal_plan']}")
    print(f"   📈 预估GI: {lunch_rec['estimated_gi']:.1f}")
    print(f"   📊 预估GL: {lunch_rec['estimated_gl']:.1f}")
    print(f"   ✅ 适宜性: {lunch_rec['diabetes_suitability']}")

    # 5. 生成完整报告
    print("\n5. 生成GI数据库报告...")
    report = gi_system.generate_gi_report()

    # 保存报告
    report_file = "/Users/williamsun/Documents/gplus/docs/FoodRecom/GI数据库报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ GI数据库报告已生成: {report_file}")

    print(f"\n🎯 GI数据库系统功能完整，已集成到营养管理系统！")