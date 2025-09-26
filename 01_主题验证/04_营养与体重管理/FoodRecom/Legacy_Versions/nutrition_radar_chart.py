#!/usr/bin/env python3
"""
食物营养雷达图生成系统
提供食物营养成分的可视化分析
"""

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import math

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

@dataclass
class FoodNutrition:
    """食物营养数据"""
    name: str
    # 每100g的营养成分
    calories: float          # 热量 (千卡)
    protein: float          # 蛋白质 (g)
    carbs: float           # 碳水化合物 (g)
    fat: float             # 脂肪 (g)
    fiber: float           # 膳食纤维 (g)
    vitamin_c: float       # 维生素C (mg)
    calcium: float         # 钙 (mg)
    iron: float           # 铁 (mg)
    sodium: float         # 钠 (mg)
    potassium: float      # 钾 (mg)

class NutritionRadarChart:
    """营养雷达图生成器"""

    def __init__(self):
        self.nutrition_database = self._initialize_nutrition_database()
        print("营养雷达图系统已初始化")

    def _initialize_nutrition_database(self) -> Dict[str, FoodNutrition]:
        """初始化营养数据库"""
        foods = {}

        # 谷物类
        foods["大米"] = FoodNutrition(
            name="大米(白米)",
            calories=346, protein=7.4, carbs=77.9, fat=0.8,
            fiber=0.7, vitamin_c=0, calcium=13, iron=2.3,
            sodium=5, potassium=103
        )

        foods["糙米"] = FoodNutrition(
            name="糙米",
            calories=348, protein=7.7, carbs=77.2, fat=1.8,
            fiber=1.8, vitamin_c=0, calcium=16, iron=1.6,
            sodium=5, potassium=154
        )

        foods["燕麦"] = FoodNutrition(
            name="燕麦",
            calories=367, protein=15.0, carbs=61.0, fat=7.0,
            fiber=10.1, vitamin_c=0, calcium=52, iron=4.2,
            sodium=6, potassium=358
        )

        # 蛋白质类
        foods["鸡胸肉"] = FoodNutrition(
            name="鸡胸肉",
            calories=133, protein=28.9, carbs=0, fat=1.9,
            fiber=0, vitamin_c=1.6, calcium=6, iron=0.4,
            sodium=63, potassium=358
        )

        foods["鲈鱼"] = FoodNutrition(
            name="鲈鱼",
            calories=105, protein=20.0, carbs=0, fat=2.5,
            fiber=0, vitamin_c=0, calcium=138, iron=2.0,
            sodium=60, potassium=278
        )

        foods["鸡蛋"] = FoodNutrition(
            name="鸡蛋",
            calories=144, protein=13.3, carbs=2.8, fat=8.8,
            fiber=0, vitamin_c=0, calcium=56, iron=2.0,
            sodium=131, potassium=154
        )

        foods["牛奶"] = FoodNutrition(
            name="牛奶",
            calories=54, protein=3.0, carbs=3.4, fat=3.2,
            fiber=0, vitamin_c=1, calcium=104, iron=0.3,
            sodium=37, potassium=109
        )

        # 蔬菜类
        foods["西兰花"] = FoodNutrition(
            name="西兰花",
            calories=22, protein=4.1, carbs=4.3, fat=0.6,
            fiber=1.6, vitamin_c=51, calcium=67, iron=1.0,
            sodium=18, potassium=17
        )

        foods["菠菜"] = FoodNutrition(
            name="菠菜",
            calories=24, protein=2.6, carbs=4.5, fat=0.6,
            fiber=1.7, vitamin_c=32, calcium=66, iron=2.9,
            sodium=85, potassium=502
        )

        foods["胡萝卜"] = FoodNutrition(
            name="胡萝卜",
            calories=25, protein=1.0, carbs=6.0, fat=0.2,
            fiber=2.8, vitamin_c=13, calcium=32, iron=1.0,
            sodium=25, potassium=119
        )

        # 水果类
        foods["苹果"] = FoodNutrition(
            name="苹果",
            calories=54, protein=0.2, carbs=14.2, fat=0.2,
            fiber=1.2, vitamin_c=1, calcium=11, iron=0.6,
            sodium=1, potassium=119
        )

        foods["香蕉"] = FoodNutrition(
            name="香蕉",
            calories=93, protein=1.4, carbs=22.0, fat=0.2,
            fiber=1.2, vitamin_c=16, calcium=28, iron=1.9,
            sodium=8, potassium=256
        )

        foods["橙子"] = FoodNutrition(
            name="橙子",
            calories=48, protein=0.8, carbs=12.0, fat=0.2,
            fiber=1.8, vitamin_c=35, calcium=40, iron=0.4,
            sodium=1, potassium=154
        )

        # 坚果类
        foods["核桃"] = FoodNutrition(
            name="核桃",
            calories=646, protein=14.9, carbs=19.1, fat=58.8,
            fiber=9.5, vitamin_c=1, calcium=56, iron=2.2,
            sodium=6, potassium=385
        )

        foods["杏仁"] = FoodNutrition(
            name="杏仁",
            calories=578, protein=19.0, carbs=22.0, fat=50.6,
            fiber=11.8, vitamin_c=0, calcium=248, iron=4.2,
            sodium=7, potassium=728
        )

        # 豆类
        foods["黄豆"] = FoodNutrition(
            name="黄豆",
            calories=359, protein=35.0, carbs=18.0, fat=16.0,
            fiber=15.5, vitamin_c=0, calcium=191, iron=8.2,
            sodium=2, potassium=1503
        )

        foods["豆腐"] = FoodNutrition(
            name="豆腐",
            calories=98, protein=8.1, carbs=4.2, fat=6.6,
            fiber=0.4, vitamin_c=0, calcium=164, iron=1.9,
            sodium=7, potassium=125
        )

        return foods

    def get_food_nutrition(self, food_name: str) -> Optional[FoodNutrition]:
        """获取食物营养信息"""
        return self.nutrition_database.get(food_name)

    def create_single_food_radar(self, food_name: str, portion_g: float = 100) -> plt.Figure:
        """创建单个食物的营养雷达图"""
        food = self.get_food_nutrition(food_name)
        if not food:
            raise ValueError(f"未找到食物 {food_name} 的营养数据")

        # 按分量调整营养数据
        ratio = portion_g / 100

        # 定义营养指标和对应的每日推荐值(用于标准化)
        nutrients = {
            '蛋白质': (food.protein * ratio, 60),      # DRV: 60g
            '碳水化合物': (food.carbs * ratio, 300),    # DRV: 300g
            '脂肪': (food.fat * ratio, 60),           # DRV: 60g
            '膳食纤维': (food.fiber * ratio, 30),      # DRV: 30g
            '维生素C': (food.vitamin_c * ratio, 100),  # DRV: 100mg
            '钙': (food.calcium * ratio, 800),        # DRV: 800mg
            '铁': (food.iron * ratio, 15),           # DRV: 15mg
            '钾': (food.potassium * ratio, 2000),     # DRV: 2000mg
        }

        # 计算相对于DRV的百分比(限制在0-150%范围内)
        labels = list(nutrients.keys())
        values = [min(nutrients[label][0] / nutrients[label][1] * 100, 150)
                 for label in labels]

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形

        values += values[:1]  # 闭合数据

        # 绘制雷达图
        ax.plot(angles, values, 'o-', linewidth=2, label=f'{food.name} ({portion_g}g)')
        ax.fill(angles, values, alpha=0.25)

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)

        # 设置径向轴
        ax.set_ylim(0, 150)
        ax.set_yticks([25, 50, 75, 100, 125, 150])
        ax.set_yticklabels(['25%', '50%', '75%', '100%', '125%', '150%'], fontsize=10)

        # 添加网格线
        ax.grid(True)

        # 添加标题和图例
        plt.title(f'{food.name} 营养成分雷达图\n(每{portion_g}g，相对于每日推荐值的百分比)',
                 fontsize=16, fontweight='bold', pad=20)

        # 添加热量信息
        calories_per_portion = food.calories * ratio
        plt.figtext(0.02, 0.02, f'热量: {calories_per_portion:.0f} 千卡/{portion_g}g',
                   fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.tight_layout()

        return fig

    def create_food_comparison_radar(self, foods_portions: List[Tuple[str, float]]) -> plt.Figure:
        """创建多个食物的营养对比雷达图"""
        if len(foods_portions) > 5:
            raise ValueError("最多支持5个食物的对比")

        # 颜色列表
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

        # 营养指标标准值
        drv_values = {
            '蛋白质': 60, '碳水化合物': 300, '脂肪': 60, '膳食纤维': 30,
            '维生素C': 100, '钙': 800, '铁': 15, '钾': 2000
        }

        labels = list(drv_values.keys())

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        # 为每个食物绘制雷达图
        for i, (food_name, portion) in enumerate(foods_portions):
            food = self.get_food_nutrition(food_name)
            if not food:
                print(f"警告: 未找到食物 {food_name} 的营养数据，跳过")
                continue

            ratio = portion / 100

            # 计算营养值相对于DRV的百分比
            values = [
                min(food.protein * ratio / drv_values['蛋白质'] * 100, 150),
                min(food.carbs * ratio / drv_values['碳水化合物'] * 100, 150),
                min(food.fat * ratio / drv_values['脂肪'] * 100, 150),
                min(food.fiber * ratio / drv_values['膳食纤维'] * 100, 150),
                min(food.vitamin_c * ratio / drv_values['维生素C'] * 100, 150),
                min(food.calcium * ratio / drv_values['钙'] * 100, 150),
                min(food.iron * ratio / drv_values['铁'] * 100, 150),
                min(food.potassium * ratio / drv_values['钾'] * 100, 150),
            ]
            values += values[:1]

            # 绘制线条和填充
            ax.plot(angles, values, 'o-', linewidth=2,
                   color=colors[i], label=f'{food.name} ({portion}g)')
            ax.fill(angles, values, alpha=0.1, color=colors[i])

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)

        # 设置径向轴
        ax.set_ylim(0, 150)
        ax.set_yticks([25, 50, 75, 100, 125, 150])
        ax.set_yticklabels(['25%', '50%', '75%', '100%', '125%', '150%'], fontsize=10)

        # 添加网格线
        ax.grid(True)

        # 添加标题和图例
        plt.title('食物营养成分对比雷达图\n(相对于每日推荐值的百分比)',
                 fontsize=16, fontweight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        plt.tight_layout()

        return fig

    def create_meal_nutrition_radar(self, meal_composition: List[Tuple[str, float]],
                                  meal_name: str = "膳食") -> plt.Figure:
        """创建整餐营养雷达图"""
        # 累计营养成分
        total_nutrition = {
            'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0,
            'vitamin_c': 0, 'calcium': 0, 'iron': 0, 'potassium': 0,
            'calories': 0
        }

        meal_details = []

        for food_name, portion in meal_composition:
            food = self.get_food_nutrition(food_name)
            if not food:
                print(f"警告: 未找到食物 {food_name} 的营养数据，跳过")
                continue

            ratio = portion / 100
            total_nutrition['protein'] += food.protein * ratio
            total_nutrition['carbs'] += food.carbs * ratio
            total_nutrition['fat'] += food.fat * ratio
            total_nutrition['fiber'] += food.fiber * ratio
            total_nutrition['vitamin_c'] += food.vitamin_c * ratio
            total_nutrition['calcium'] += food.calcium * ratio
            total_nutrition['iron'] += food.iron * ratio
            total_nutrition['potassium'] += food.potassium * ratio
            total_nutrition['calories'] += food.calories * ratio

            meal_details.append(f"{food.name} {portion}g")

        # 营养指标标准值
        drv_values = {
            '蛋白质': 60, '碳水化合物': 300, '脂肪': 60, '膳食纤维': 30,
            '维生素C': 100, '钙': 800, '铁': 15, '钾': 2000
        }

        labels = list(drv_values.keys())

        # 计算相对于DRV的百分比
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

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        values += values[:1]

        # 绘制雷达图
        ax.plot(angles, values, 'o-', linewidth=3, color='#FF6B6B')
        ax.fill(angles, values, alpha=0.3, color='#FF6B6B')

        # 添加100%参考线
        ref_values = [100] * (len(labels) + 1)
        ax.plot(angles, ref_values, '--', linewidth=1, color='green', alpha=0.7,
               label='每日推荐值(100%)')

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)

        # 设置径向轴
        ax.set_ylim(0, 200)
        ax.set_yticks([50, 100, 150, 200])
        ax.set_yticklabels(['50%', '100%', '150%', '200%'], fontsize=10)

        # 添加网格线
        ax.grid(True)

        # 添加标题
        plt.title(f'{meal_name} 营养成分雷达图\n(相对于每日推荐值的百分比)',
                 fontsize=16, fontweight='bold', pad=20)

        # 添加膳食组成信息
        meal_info = f"膳食组成: {', '.join(meal_details)}\n总热量: {total_nutrition['calories']:.0f} 千卡"
        plt.figtext(0.02, 0.02, meal_info, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))

        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        plt.tight_layout()

        return fig

    def generate_nutrition_report_with_radar(self, foods_portions: List[Tuple[str, float]],
                                           save_path: str = None) -> str:
        """生成包含雷达图的营养分析报告"""
        report = "# 食物营养分析报告\n\n"

        for food_name, portion in foods_portions:
            food = self.get_food_nutrition(food_name)
            if not food:
                continue

            ratio = portion / 100

            report += f"## {food.name} ({portion}g)\n\n"
            report += f"- **热量**: {food.calories * ratio:.1f} 千卡\n"
            report += f"- **蛋白质**: {food.protein * ratio:.1f} g\n"
            report += f"- **碳水化合物**: {food.carbs * ratio:.1f} g\n"
            report += f"- **脂肪**: {food.fat * ratio:.1f} g\n"
            report += f"- **膳食纤维**: {food.fiber * ratio:.1f} g\n"
            report += f"- **维生素C**: {food.vitamin_c * ratio:.1f} mg\n"
            report += f"- **钙**: {food.calcium * ratio:.1f} mg\n"
            report += f"- **铁**: {food.iron * ratio:.1f} mg\n"
            report += f"- **钾**: {food.potassium * ratio:.1f} mg\n\n"

        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)

        return report

    def get_available_foods(self) -> List[str]:
        """获取可用食物列表"""
        return list(self.nutrition_database.keys())

if __name__ == "__main__":
    # 演示营养雷达图系统
    print("🚀 启动食物营养雷达图系统")

    radar_system = NutritionRadarChart()

    print(f"📊 已加载 {len(radar_system.nutrition_database)} 种食物的营养数据")
    print("可用食物:", ", ".join(radar_system.get_available_foods()))

    # 1. 创建单个食物雷达图
    print("\n1. 生成单个食物雷达图 - 鸡胸肉(100g)")
    fig1 = radar_system.create_single_food_radar("鸡胸肉", 100)
    fig1.savefig("/Users/williamsun/Documents/gplus/docs/FoodRecom/鸡胸肉营养雷达图.png",
                dpi=300, bbox_inches='tight')
    plt.close(fig1)

    # 2. 创建食物对比雷达图
    print("\n2. 生成食物对比雷达图")
    comparison_foods = [("鸡胸肉", 100), ("鲈鱼", 100), ("牛奶", 250)]
    fig2 = radar_system.create_food_comparison_radar(comparison_foods)
    fig2.savefig("/Users/williamsun/Documents/gplus/docs/FoodRecom/蛋白质食物对比雷达图.png",
                dpi=300, bbox_inches='tight')
    plt.close(fig2)

    # 3. 创建整餐营养雷达图
    print("\n3. 生成整餐营养雷达图")
    meal = [("糙米", 100), ("鸡胸肉", 100), ("西兰花", 150), ("胡萝卜", 100)]
    fig3 = radar_system.create_meal_nutrition_radar(meal, "健康午餐")
    fig3.savefig("/Users/williamsun/Documents/gplus/docs/FoodRecom/健康午餐营养雷达图.png",
                dpi=300, bbox_inches='tight')
    plt.close(fig3)

    # 4. 生成营养分析报告
    print("\n4. 生成营养分析报告")
    report = radar_system.generate_nutrition_report_with_radar(
        meal, "/Users/williamsun/Documents/gplus/docs/FoodRecom/膳食营养分析报告.md")

    print("✅ 营养雷达图系统演示完成！")
    print("📁 生成的文件:")
    print("   - 鸡胸肉营养雷达图.png")
    print("   - 蛋白质食物对比雷达图.png")
    print("   - 健康午餐营养雷达图.png")
    print("   - 膳食营养分析报告.md")