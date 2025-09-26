"""
简化菜谱管理模块
仅包含菜品名称和重量信息，大量菜谱数据库
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SimpleIngredient:
    """简化食材信息"""
    name: str                              # 食材名称
    weight: float                          # 重量(g)
    weight_type: str = "净重"              # 重量类型：净重/干重/生重

@dataclass
class SimpleRecipe:
    """简化菜谱"""
    name: str                              # 菜品名称
    ingredients: List[SimpleIngredient]    # 食材列表
    calories: float                        # 总热量
    protein: float                         # 蛋白质(g)
    disease_suitable: List[str]            # 适宜疾病

class SimpleRecipeManager:
    """简化菜谱管理器 - 大量菜谱数据库"""

    def __init__(self):
        self.recipes = self._load_recipes()

    def _load_recipes(self) -> Dict[str, Dict[str, List[SimpleRecipe]]]:
        """加载大量简化菜谱"""
        return {
            "清淡": {
                "早餐": [
                    SimpleRecipe("燕麦鸡蛋套餐", [
                        SimpleIngredient("燕麦片", 40, "干重"),
                        SimpleIngredient("鸡蛋", 60, "生重"),
                        SimpleIngredient("脱脂牛奶", 200, "净重")
                    ], 420, 25.2, ["糖尿病", "高血压"]),

                    SimpleRecipe("小米粥配蒸蛋", [
                        SimpleIngredient("小米", 30, "干重"),
                        SimpleIngredient("鸡蛋", 50, "生重"),
                        SimpleIngredient("青菜", 80, "净重")
                    ], 280, 18.5, ["胃病", "糖尿病"]),

                    SimpleRecipe("蒸蛋羹", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("温水", 150, "净重"),
                        SimpleIngredient("小葱", 5, "净重")
                    ], 185, 16.2, ["老年营养", "胃病"]),

                    SimpleRecipe("白粥配咸菜", [
                        SimpleIngredient("大米", 35, "干重"),
                        SimpleIngredient("萝卜丝", 60, "净重"),
                        SimpleIngredient("小菜", 20, "净重")
                    ], 245, 8.5, ["消化不良"]),

                    SimpleRecipe("豆浆配包子", [
                        SimpleIngredient("黄豆", 25, "干重"),
                        SimpleIngredient("素包子", 80, "净重")
                    ], 320, 18.6, ["素食", "糖尿病"]),

                    SimpleRecipe("牛奶麦片", [
                        SimpleIngredient("燕麦片", 35, "干重"),
                        SimpleIngredient("纯牛奶", 250, "净重")
                    ], 295, 16.8, ["骨质疏松"]),

                    SimpleRecipe("蒸蛋配青菜", [
                        SimpleIngredient("鸡蛋", 80, "生重"),
                        SimpleIngredient("小白菜", 100, "净重")
                    ], 155, 14.2, ["减重", "糖尿病"]),

                    SimpleRecipe("莲藕粥", [
                        SimpleIngredient("莲藕", 60, "净重"),
                        SimpleIngredient("大米", 30, "干重")
                    ], 195, 6.5, ["健脾"]),

                    SimpleRecipe("山药粥", [
                        SimpleIngredient("山药", 80, "净重"),
                        SimpleIngredient("大米", 30, "干重")
                    ], 215, 8.2, ["养胃"]),

                    SimpleRecipe("银耳粥", [
                        SimpleIngredient("银耳", 10, "干重"),
                        SimpleIngredient("大米", 35, "干重")
                    ], 225, 7.8, ["润燥"]),

                    SimpleRecipe("红枣粥", [
                        SimpleIngredient("红枣", 25, "净重"),
                        SimpleIngredient("小米", 30, "干重")
                    ], 235, 8.5, ["补血"]),

                    SimpleRecipe("绿豆粥", [
                        SimpleIngredient("绿豆", 25, "干重"),
                        SimpleIngredient("大米", 30, "干重")
                    ], 245, 9.8, ["清热"]),

                    SimpleRecipe("薏米粥", [
                        SimpleIngredient("薏米", 35, "干重"),
                        SimpleIngredient("红豆", 20, "干重")
                    ], 255, 10.5, ["祛湿"]),

                    SimpleRecipe("百合粥", [
                        SimpleIngredient("百合", 15, "干重"),
                        SimpleIngredient("大米", 35, "干重")
                    ], 235, 8.2, ["润肺"]),

                    SimpleRecipe("莲子粥", [
                        SimpleIngredient("莲子", 20, "干重"),
                        SimpleIngredient("大米", 35, "干重")
                    ], 245, 9.2, ["安神"]),

                    SimpleRecipe("核桃粥", [
                        SimpleIngredient("核桃仁", 15, "净重"),
                        SimpleIngredient("大米", 35, "干重")
                    ], 275, 9.8, ["健脑"]),

                    SimpleRecipe("南瓜粥", [
                        SimpleIngredient("南瓜", 100, "净重"),
                        SimpleIngredient("小米", 30, "干重")
                    ], 205, 7.5, ["护眼"]),

                    SimpleRecipe("玉米粥", [
                        SimpleIngredient("玉米粒", 60, "净重"),
                        SimpleIngredient("大米", 30, "干重")
                    ], 195, 6.8, ["粗粮"])
                ],
                "午餐": [
                    SimpleRecipe("清蒸鸡胸肉", [
                        SimpleIngredient("鸡胸肉", 120, "生重"),
                        SimpleIngredient("胡萝卜", 80, "净重"),
                        SimpleIngredient("西兰花", 100, "净重")
                    ], 285, 32.5, ["糖尿病", "减重"]),

                    SimpleRecipe("清蒸鲈鱼", [
                        SimpleIngredient("鲈鱼", 150, "净重"),
                        SimpleIngredient("生姜", 10, "净重"),
                        SimpleIngredient("小葱", 8, "净重")
                    ], 198, 28.6, ["心血管疾病"]),

                    SimpleRecipe("豆腐蔬菜汤", [
                        SimpleIngredient("嫩豆腐", 150, "净重"),
                        SimpleIngredient("冬瓜", 100, "净重"),
                        SimpleIngredient("紫菜", 5, "干重")
                    ], 145, 12.8, ["高血压", "肾病"]),

                    SimpleRecipe("蒸虾仁", [
                        SimpleIngredient("虾仁", 100, "净重"),
                        SimpleIngredient("鸡蛋白", 50, "生重"),
                        SimpleIngredient("嫩豌豆", 60, "净重")
                    ], 165, 24.8, ["高蛋白需求"]),

                    SimpleRecipe("白煮鸡蛋", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("小白菜", 120, "净重")
                    ], 185, 16.5, ["简单营养"]),

                    SimpleRecipe("清炖排骨", [
                        SimpleIngredient("排骨", 100, "生重"),
                        SimpleIngredient("白萝卜", 150, "净重"),
                        SimpleIngredient("胡萝卜", 50, "净重")
                    ], 245, 22.8, ["体质虚弱"]),

                    SimpleRecipe("蒸蛋羹配菜", [
                        SimpleIngredient("鸡蛋", 120, "生重"),
                        SimpleIngredient("青菜丁", 80, "净重"),
                        SimpleIngredient("香菇", 30, "净重")
                    ], 195, 18.5, ["营养均衡"]),

                    SimpleRecipe("白灼菜心", [
                        SimpleIngredient("菜心", 150, "净重"),
                        SimpleIngredient("蒜蓉", 5, "净重")
                    ], 65, 4.5, ["清淡蔬菜"]),

                    SimpleRecipe("清炖白萝卜", [
                        SimpleIngredient("白萝卜", 200, "净重"),
                        SimpleIngredient("瘦肉丝", 30, "净重")
                    ], 125, 8.5, ["消食"]),

                    SimpleRecipe("蒸南瓜", [
                        SimpleIngredient("南瓜", 200, "净重")
                    ], 95, 3.2, ["护眼"]),

                    SimpleRecipe("清蒸丝瓜", [
                        SimpleIngredient("丝瓜", 150, "净重"),
                        SimpleIngredient("蒜蓉", 5, "净重")
                    ], 45, 2.5, ["清热"]),

                    SimpleRecipe("白煮冬瓜", [
                        SimpleIngredient("冬瓜", 200, "净重"),
                        SimpleIngredient("虾皮", 8, "干重")
                    ], 55, 4.2, ["利水"]),

                    SimpleRecipe("蒸蛋羹", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("温水", 150, "净重"),
                        SimpleIngredient("小虾仁", 20, "净重")
                    ], 175, 16.8, ["嫩滑"]),

                    SimpleRecipe("清蒸山药", [
                        SimpleIngredient("山药", 150, "净重")
                    ], 125, 4.8, ["健脾"]),

                    SimpleRecipe("蒸蛋配菠菜", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("菠菜", 80, "净重")
                    ], 165, 15.2, ["补铁"]),

                    SimpleRecipe("清蒸茄子", [
                        SimpleIngredient("茄子", 150, "净重"),
                        SimpleIngredient("蒜蓉", 8, "净重")
                    ], 85, 3.5, ["低热量"]),

                    SimpleRecipe("白灼芥蓝", [
                        SimpleIngredient("芥蓝", 150, "净重")
                    ], 55, 4.8, ["补钙"]),

                    SimpleRecipe("清蒸莲藕", [
                        SimpleIngredient("莲藕", 150, "净重"),
                        SimpleIngredient("瘦肉丁", 25, "净重")
                    ], 145, 8.5, ["健脾"])
                ],
                "晚餐": [
                    SimpleRecipe("蔬菜豆腐汤", [
                        SimpleIngredient("嫩豆腐", 100, "净重"),
                        SimpleIngredient("小白菜", 80, "净重"),
                        SimpleIngredient("胡萝卜丝", 40, "净重")
                    ], 125, 9.8, ["晚餐清淡"]),

                    SimpleRecipe("紫菜蛋花汤", [
                        SimpleIngredient("紫菜", 5, "干重"),
                        SimpleIngredient("鸡蛋", 60, "生重"),
                        SimpleIngredient("小葱", 5, "净重")
                    ], 98, 8.5, ["补碘"]),

                    SimpleRecipe("冬瓜汤", [
                        SimpleIngredient("冬瓜", 200, "净重"),
                        SimpleIngredient("虾皮", 8, "干重")
                    ], 65, 5.2, ["水肿", "减重"]),

                    SimpleRecipe("蒸蛋羹", [
                        SimpleIngredient("鸡蛋", 80, "生重"),
                        SimpleIngredient("温水", 120, "净重")
                    ], 145, 12.8, ["易消化"]),

                    SimpleRecipe("青菜汤", [
                        SimpleIngredient("小青菜", 150, "净重"),
                        SimpleIngredient("豆腐丁", 50, "净重")
                    ], 85, 6.5, ["清热"]),

                    SimpleRecipe("萝卜丝汤", [
                        SimpleIngredient("白萝卜", 180, "净重"),
                        SimpleIngredient("香菇丝", 20, "净重")
                    ], 55, 3.8, ["消食"]),

                    SimpleRecipe("丝瓜蛋汤", [
                        SimpleIngredient("丝瓜", 120, "净重"),
                        SimpleIngredient("鸡蛋", 50, "生重")
                    ], 108, 8.2, ["清热润燥"])
                ],
                "加餐": [
                    SimpleRecipe("酸奶", [
                        SimpleIngredient("无糖酸奶", 150, "净重")
                    ], 95, 5.8, ["益生菌"]),

                    SimpleRecipe("水煮蛋", [
                        SimpleIngredient("鸡蛋", 60, "生重")
                    ], 85, 7.2, ["高蛋白"]),

                    SimpleRecipe("蒸蛋羹", [
                        SimpleIngredient("鸡蛋", 50, "生重"),
                        SimpleIngredient("温水", 80, "净重")
                    ], 75, 6.5, ["小份营养"]),

                    SimpleRecipe("豆浆", [
                        SimpleIngredient("黄豆", 20, "干重")
                    ], 125, 8.8, ["植物蛋白"]),

                    SimpleRecipe("牛奶", [
                        SimpleIngredient("纯牛奶", 200, "净重")
                    ], 125, 6.8, ["补钙"]),

                    SimpleRecipe("核桃仁", [
                        SimpleIngredient("核桃仁", 15, "净重")
                    ], 105, 2.5, ["健脑"]),

                    SimpleRecipe("苹果片", [
                        SimpleIngredient("苹果", 120, "净重")
                    ], 65, 0.5, ["维生素"]),

                    SimpleRecipe("蒸蛋羹小份", [
                        SimpleIngredient("鸡蛋", 40, "生重"),
                        SimpleIngredient("温水", 60, "净重")
                    ], 65, 5.2, ["小份营养"]),

                    SimpleRecipe("红枣", [
                        SimpleIngredient("红枣", 30, "净重")
                    ], 85, 1.2, ["补血"]),

                    SimpleRecipe("银耳汤", [
                        SimpleIngredient("银耳", 15, "干重"),
                        SimpleIngredient("冰糖", 5, "净重")
                    ], 75, 2.8, ["润燥"]),

                    SimpleRecipe("山楂片", [
                        SimpleIngredient("山楂", 50, "净重")
                    ], 45, 0.8, ["消食"]),

                    SimpleRecipe("柠檬蜂蜜水", [
                        SimpleIngredient("柠檬", 30, "净重"),
                        SimpleIngredient("蜂蜜", 8, "净重")
                    ], 55, 0.2, ["维C"]),

                    SimpleRecipe("绿豆汤", [
                        SimpleIngredient("绿豆", 25, "干重")
                    ], 95, 6.8, ["清热"]),

                    SimpleRecipe("黑芝麻糊", [
                        SimpleIngredient("黑芝麻粉", 20, "干重")
                    ], 125, 5.5, ["补肾"]),

                    SimpleRecipe("薏米水", [
                        SimpleIngredient("薏米", 20, "干重")
                    ], 85, 3.2, ["祛湿"]),

                    SimpleRecipe("枸杞茶", [
                        SimpleIngredient("枸杞", 8, "干重")
                    ], 35, 1.5, ["明目"]),

                    SimpleRecipe("莲子汤", [
                        SimpleIngredient("莲子", 25, "干重")
                    ], 95, 4.8, ["安神"]),

                    SimpleRecipe("白木耳", [
                        SimpleIngredient("白木耳", 20, "干重")
                    ], 65, 2.5, ["润肺"]),

                    SimpleRecipe("百合汤", [
                        SimpleIngredient("百合", 20, "干重")
                    ], 75, 3.2, ["润肺"]),

                    SimpleRecipe("花生米", [
                        SimpleIngredient("水煮花生", 20, "净重")
                    ], 115, 5.8, ["植物蛋白"]),

                    SimpleRecipe("瓜子仁", [
                        SimpleIngredient("葵花子仁", 12, "净重")
                    ], 75, 2.8, ["维E"])
                ]
            },

            "地中海": {
                "早餐": [
                    SimpleRecipe("希腊酸奶配坚果", [
                        SimpleIngredient("希腊酸奶", 150, "净重"),
                        SimpleIngredient("核桃仁", 15, "净重"),
                        SimpleIngredient("蓝莓", 80, "净重")
                    ], 285, 18.2, ["心血管"]),

                    SimpleRecipe("橄榄油吐司", [
                        SimpleIngredient("全麦面包", 60, "净重"),
                        SimpleIngredient("橄榄油", 8, "净重"),
                        SimpleIngredient("番茄片", 50, "净重")
                    ], 245, 8.5, ["地中海饮食"]),

                    SimpleRecipe("杏仁燕麦", [
                        SimpleIngredient("燕麦片", 40, "干重"),
                        SimpleIngredient("杏仁片", 12, "净重"),
                        SimpleIngredient("蜂蜜", 8, "净重")
                    ], 265, 9.8, ["抗氧化"]),

                    SimpleRecipe("无花果酸奶", [
                        SimpleIngredient("酸奶", 120, "净重"),
                        SimpleIngredient("无花果", 60, "净重"),
                        SimpleIngredient("坚果碎", 10, "净重")
                    ], 195, 8.5, ["纤维丰富"]),

                    SimpleRecipe("鳄梨吐司", [
                        SimpleIngredient("全麦面包", 50, "净重"),
                        SimpleIngredient("鳄梨", 80, "净重"),
                        SimpleIngredient("柠檬汁", 5, "净重")
                    ], 225, 6.8, ["健康脂肪"]),

                    SimpleRecipe("橄榄拼盘", [
                        SimpleIngredient("黑橄榄", 25, "净重"),
                        SimpleIngredient("羊奶酪", 30, "净重"),
                        SimpleIngredient("小番茄", 60, "净重")
                    ], 165, 7.2, ["开胃"]),

                    SimpleRecipe("坚果果干", [
                        SimpleIngredient("混合坚果", 20, "净重"),
                        SimpleIngredient("葡萄干", 15, "净重")
                    ], 185, 5.5, ["能量补充"])
                ],
                "午餐": [
                    SimpleRecipe("烤鱼配蔬菜", [
                        SimpleIngredient("鲑鱼", 120, "净重"),
                        SimpleIngredient("西红柿", 100, "净重"),
                        SimpleIngredient("橄榄油", 10, "净重")
                    ], 325, 25.8, ["ω-3脂肪酸"]),

                    SimpleRecipe("地中海沙拉", [
                        SimpleIngredient("黄瓜", 80, "净重"),
                        SimpleIngredient("番茄", 100, "净重"),
                        SimpleIngredient("羊奶酪", 40, "净重"),
                        SimpleIngredient("橄榄油", 8, "净重")
                    ], 185, 8.5, ["维生素丰富"]),

                    SimpleRecipe("烤鸡配时蔬", [
                        SimpleIngredient("鸡胸肉", 100, "净重"),
                        SimpleIngredient("彩椒", 80, "净重"),
                        SimpleIngredient("茄子", 60, "净重")
                    ], 245, 28.5, ["低脂高蛋白"]),

                    SimpleRecipe("海鲜拼盘", [
                        SimpleIngredient("虾仁", 80, "净重"),
                        SimpleIngredient("鱿鱼", 60, "净重"),
                        SimpleIngredient("柠檬", 20, "净重")
                    ], 165, 24.8, ["海洋营养"]),

                    SimpleRecipe("烤蔬菜", [
                        SimpleIngredient("西葫芦", 100, "净重"),
                        SimpleIngredient("茄子", 80, "净重"),
                        SimpleIngredient("彩椒", 60, "净重")
                    ], 125, 4.2, ["植物营养"]),

                    SimpleRecipe("橄榄油拌菜", [
                        SimpleIngredient("生菜", 120, "净重"),
                        SimpleIngredient("小番茄", 80, "净重"),
                        SimpleIngredient("橄榄油", 10, "净重")
                    ], 145, 3.5, ["生食营养"]),

                    SimpleRecipe("金枪鱼沙拉", [
                        SimpleIngredient("金枪鱼", 80, "净重"),
                        SimpleIngredient("生菜", 100, "净重"),
                        SimpleIngredient("橄榄", 15, "净重")
                    ], 185, 22.5, ["深海鱼类"])
                ],
                "晚餐": [
                    SimpleRecipe("地中海蔬菜汤", [
                        SimpleIngredient("西葫芦", 100, "净重"),
                        SimpleIngredient("番茄", 80, "净重"),
                        SimpleIngredient("洋葱", 40, "净重")
                    ], 125, 4.2, ["抗氧化"]),

                    SimpleRecipe("烤彩椒", [
                        SimpleIngredient("红黄椒", 150, "净重"),
                        SimpleIngredient("橄榄油", 5, "净重")
                    ], 85, 2.8, ["维生素C"]),

                    SimpleRecipe("茄子汤", [
                        SimpleIngredient("茄子", 120, "净重"),
                        SimpleIngredient("番茄", 60, "净重"),
                        SimpleIngredient("罗勒", 3, "净重")
                    ], 95, 3.5, ["膳食纤维"]),

                    SimpleRecipe("橄榄蔬菜汤", [
                        SimpleIngredient("橄榄", 20, "净重"),
                        SimpleIngredient("洋葱", 50, "净重"),
                        SimpleIngredient("胡萝卜", 60, "净重")
                    ], 105, 2.8, ["地中海风味"]),

                    SimpleRecipe("烤蔬菜拼盘", [
                        SimpleIngredient("西葫芦", 80, "净重"),
                        SimpleIngredient("茄子", 60, "净重"),
                        SimpleIngredient("番茄", 70, "净重")
                    ], 115, 3.8, ["烤制营养"]),

                    SimpleRecipe("地中海沙拉", [
                        SimpleIngredient("生菜", 100, "净重"),
                        SimpleIngredient("黄瓜", 60, "净重"),
                        SimpleIngredient("橄榄油", 5, "净重")
                    ], 85, 2.5, ["清爽"]),

                    SimpleRecipe("香草汤", [
                        SimpleIngredient("各式香草", 50, "净重"),
                        SimpleIngredient("蔬菜丁", 100, "净重")
                    ], 65, 2.8, ["香草营养"])
                ],
                "加餐": [
                    SimpleRecipe("橄榄坚果", [
                        SimpleIngredient("橄榄", 20, "净重"),
                        SimpleIngredient("杏仁", 15, "净重")
                    ], 145, 5.2, ["健康脂肪"]),

                    SimpleRecipe("无花果", [
                        SimpleIngredient("新鲜无花果", 80, "净重")
                    ], 75, 1.2, ["天然甜味"]),

                    SimpleRecipe("小番茄", [
                        SimpleIngredient("樱桃番茄", 100, "净重")
                    ], 25, 1.5, ["番茄红素"]),

                    SimpleRecipe("坚果拼盘", [
                        SimpleIngredient("混合坚果", 18, "净重")
                    ], 125, 4.5, ["多种坚果"]),

                    SimpleRecipe("橄榄", [
                        SimpleIngredient("绿橄榄", 25, "净重")
                    ], 35, 0.8, ["单不饱和脂肪"]),

                    SimpleRecipe("葡萄", [
                        SimpleIngredient("新鲜葡萄", 100, "净重")
                    ], 65, 0.8, ["抗氧化剂"]),

                    SimpleRecipe("羊奶酪", [
                        SimpleIngredient("羊奶酪", 30, "净重")
                    ], 85, 5.5, ["优质蛋白"])
                ]
            },

            "日韩": {
                "早餐": [
                    SimpleRecipe("日式蒸蛋", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("高汤", 150, "净重"),
                        SimpleIngredient("海苔", 2, "干重")
                    ], 185, 16.2, ["易消化"]),

                    SimpleRecipe("味噌汤", [
                        SimpleIngredient("味噌", 15, "净重"),
                        SimpleIngredient("豆腐", 60, "净重"),
                        SimpleIngredient("裙带菜", 5, "干重")
                    ], 85, 6.8, ["发酵食品"]),

                    SimpleRecipe("海苔拌饭", [
                        SimpleIngredient("米饭", 80, "熟重"),
                        SimpleIngredient("海苔片", 3, "干重"),
                        SimpleIngredient("芝麻", 5, "净重")
                    ], 195, 6.5, ["简单营养"]),

                    SimpleRecipe("日式豆腐", [
                        SimpleIngredient("嫩豆腐", 120, "净重"),
                        SimpleIngredient("小葱", 5, "净重"),
                        SimpleIngredient("生抽", 8, "净重")
                    ], 95, 8.5, ["植物蛋白"]),

                    SimpleRecipe("韩式蒸蛋", [
                        SimpleIngredient("鸡蛋", 120, "生重"),
                        SimpleIngredient("胡萝卜丝", 30, "净重"),
                        SimpleIngredient("菠菜", 50, "净重")
                    ], 195, 16.8, ["蔬菜搭配"]),

                    SimpleRecipe("海带汤", [
                        SimpleIngredient("海带", 8, "干重"),
                        SimpleIngredient("豆腐", 50, "净重"),
                        SimpleIngredient("小葱", 5, "净重")
                    ], 65, 5.2, ["补碘"]),

                    SimpleRecipe("紫菜蛋花汤", [
                        SimpleIngredient("紫菜", 5, "干重"),
                        SimpleIngredient("鸡蛋", 60, "生重")
                    ], 95, 7.8, ["快手营养"])
                ],
                "午餐": [
                    SimpleRecipe("韩式蒸蛋配菜", [
                        SimpleIngredient("鸡蛋", 120, "生重"),
                        SimpleIngredient("胡萝卜", 50, "净重"),
                        SimpleIngredient("豆芽", 60, "净重")
                    ], 235, 18.5, ["营养均衡"]),

                    SimpleRecipe("日式烤鱼", [
                        SimpleIngredient("鲭鱼", 100, "净重"),
                        SimpleIngredient("白萝卜", 80, "净重")
                    ], 165, 22.5, ["深海鱼"]),

                    SimpleRecipe("韩式豆腐汤", [
                        SimpleIngredient("嫩豆腐", 150, "净重"),
                        SimpleIngredient("韩式辣椒", 3, "净重"),
                        SimpleIngredient("大葱", 20, "净重")
                    ], 125, 12.8, ["微辣开胃"]),

                    SimpleRecipe("日式蒸蛋羹", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("鸡汤", 120, "净重"),
                        SimpleIngredient("香菇", 25, "净重")
                    ], 175, 15.2, ["鲜美"]),

                    SimpleRecipe("海苔包饭", [
                        SimpleIngredient("海苔", 5, "干重"),
                        SimpleIngredient("米饭", 100, "熟重"),
                        SimpleIngredient("黄瓜", 30, "净重")
                    ], 245, 7.5, ["便当风格"]),

                    SimpleRecipe("韩式拌菜", [
                        SimpleIngredient("菠菜", 100, "净重"),
                        SimpleIngredient("胡萝卜丝", 50, "净重"),
                        SimpleIngredient("香油", 3, "净重")
                    ], 85, 5.2, ["多种蔬菜"]),

                    SimpleRecipe("日式沙拉", [
                        SimpleIngredient("生菜", 80, "净重"),
                        SimpleIngredient("黄瓜", 60, "净重"),
                        SimpleIngredient("日式调料", 10, "净重")
                    ], 65, 2.8, ["清爽"])
                ],
                "晚餐": [
                    SimpleRecipe("味噌汤", [
                        SimpleIngredient("味噌", 15, "净重"),
                        SimpleIngredient("豆腐", 60, "净重"),
                        SimpleIngredient("裙带菜", 5, "干重")
                    ], 85, 6.8, ["传统日式"]),

                    SimpleRecipe("韩式海带汤", [
                        SimpleIngredient("海带", 8, "干重"),
                        SimpleIngredient("牛肉丝", 30, "净重")
                    ], 95, 8.5, ["滋补"]),

                    SimpleRecipe("日式豆腐汤", [
                        SimpleIngredient("嫩豆腐", 100, "净重"),
                        SimpleIngredient("小葱", 8, "净重"),
                        SimpleIngredient("高汤", 200, "净重")
                    ], 75, 7.2, ["清淡"]),

                    SimpleRecipe("紫菜汤", [
                        SimpleIngredient("紫菜", 6, "干重"),
                        SimpleIngredient("鸡蛋", 40, "生重"),
                        SimpleIngredient("香菇", 20, "净重")
                    ], 85, 6.5, ["补碘营养"]),

                    SimpleRecipe("韩式萝卜汤", [
                        SimpleIngredient("白萝卜", 150, "净重"),
                        SimpleIngredient("大葱", 15, "净重")
                    ], 45, 2.5, ["清热"]),

                    SimpleRecipe("味噌蔬菜汤", [
                        SimpleIngredient("味噌", 12, "净重"),
                        SimpleIngredient("白菜", 100, "净重"),
                        SimpleIngredient("豆腐", 40, "净重")
                    ], 75, 5.8, ["蔬菜丰富"]),

                    SimpleRecipe("日式清汤", [
                        SimpleIngredient("昆布", 3, "干重"),
                        SimpleIngredient("豆腐", 50, "净重"),
                        SimpleIngredient("小葱", 5, "净重")
                    ], 55, 4.2, ["清香"])
                ],
                "加餐": [
                    SimpleRecipe("海苔卷", [
                        SimpleIngredient("海苔", 3, "干重"),
                        SimpleIngredient("黄瓜", 40, "净重"),
                        SimpleIngredient("胡萝卜", 30, "净重")
                    ], 95, 6.2, ["便携"]),

                    SimpleRecipe("韩式泡菜", [
                        SimpleIngredient("白菜泡菜", 50, "净重")
                    ], 25, 1.5, ["发酵蔬菜"]),

                    SimpleRecipe("海苔片", [
                        SimpleIngredient("调味海苔", 5, "干重")
                    ], 15, 2.8, ["低热量"]),

                    SimpleRecipe("日式小菜", [
                        SimpleIngredient("萝卜丝", 40, "净重"),
                        SimpleIngredient("胡萝卜丝", 30, "净重")
                    ], 35, 1.8, ["清爽"]),

                    SimpleRecipe("韩式萝卜", [
                        SimpleIngredient("腌萝卜", 60, "净重")
                    ], 25, 1.2, ["开胃"]),

                    SimpleRecipe("味噌汤", [
                        SimpleIngredient("味噌", 8, "净重"),
                        SimpleIngredient("豆腐丁", 30, "净重")
                    ], 45, 3.5, ["小份汤品"]),

                    SimpleRecipe("海带丝", [
                        SimpleIngredient("凉拌海带丝", 60, "净重")
                    ], 35, 2.2, ["矿物质"])
                ]
            },

            "川菜": {
                "早餐": [
                    SimpleRecipe("酸菜鱼片粥", [
                        SimpleIngredient("鱼片", 60, "净重"),
                        SimpleIngredient("酸菜", 30, "净重"),
                        SimpleIngredient("大米", 40, "干重")
                    ], 245, 18.5, ["开胃"]),

                    SimpleRecipe("豆花", [
                        SimpleIngredient("嫩豆腐", 150, "净重"),
                        SimpleIngredient("榨菜丝", 20, "净重")
                    ], 125, 9.8, ["传统"]),

                    SimpleRecipe("小面", [
                        SimpleIngredient("面条", 60, "干重"),
                        SimpleIngredient("青菜", 50, "净重"),
                        SimpleIngredient("花生米", 10, "净重")
                    ], 285, 12.5, ["特色"]),

                    SimpleRecipe("蒸蛋", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("肉丝", 20, "净重")
                    ], 185, 16.8, ["咸鲜"]),

                    SimpleRecipe("泡菜鸡蛋汤", [
                        SimpleIngredient("泡菜", 40, "净重"),
                        SimpleIngredient("鸡蛋", 60, "生重")
                    ], 125, 8.5, ["酸辣"]),

                    SimpleRecipe("白粥配咸菜", [
                        SimpleIngredient("大米", 35, "干重"),
                        SimpleIngredient("四川咸菜", 25, "净重")
                    ], 195, 6.5, ["简单"]),

                    SimpleRecipe("豆浆油条", [
                        SimpleIngredient("豆浆", 200, "净重"),
                        SimpleIngredient("油条", 30, "净重")
                    ], 245, 12.8, ["经典搭配"])
                ],
                "午餐": [
                    SimpleRecipe("麻婆豆腐", [
                        SimpleIngredient("嫩豆腐", 150, "净重"),
                        SimpleIngredient("肉末", 30, "净重"),
                        SimpleIngredient("豆瓣酱", 8, "净重")
                    ], 185, 15.2, ["经典川菜"]),

                    SimpleRecipe("回锅肉", [
                        SimpleIngredient("五花肉", 80, "净重"),
                        SimpleIngredient("青椒", 60, "净重"),
                        SimpleIngredient("豆瓣酱", 10, "净重")
                    ], 285, 18.5, ["传统"]),

                    SimpleRecipe("水煮鱼", [
                        SimpleIngredient("鱼片", 120, "净重"),
                        SimpleIngredient("豆芽", 80, "净重"),
                        SimpleIngredient("青菜", 60, "净重")
                    ], 225, 26.8, ["经典菜品"]),

                    SimpleRecipe("蒜泥白肉", [
                        SimpleIngredient("猪肉", 100, "净重"),
                        SimpleIngredient("大蒜", 15, "净重"),
                        SimpleIngredient("黄瓜丝", 50, "净重")
                    ], 245, 22.5, ["凉菜"]),

                    SimpleRecipe("干煸豆角", [
                        SimpleIngredient("豆角", 150, "净重"),
                        SimpleIngredient("肉丝", 30, "净重"),
                        SimpleIngredient("榨菜", 20, "净重")
                    ], 165, 12.8, ["家常菜"]),

                    SimpleRecipe("鱼香茄子", [
                        SimpleIngredient("茄子", 120, "净重"),
                        SimpleIngredient("肉丝", 25, "净重"),
                        SimpleIngredient("豆瓣酱", 8, "净重")
                    ], 145, 8.5, ["茄子类"]),

                    SimpleRecipe("宫保鸡丁", [
                        SimpleIngredient("鸡胸肉", 100, "净重"),
                        SimpleIngredient("花生米", 20, "净重"),
                        SimpleIngredient("黄瓜丁", 40, "净重")
                    ], 245, 24.5, ["坚果搭配"])
                ],
                "晚餐": [
                    SimpleRecipe("酸辣汤", [
                        SimpleIngredient("豆腐丝", 60, "净重"),
                        SimpleIngredient("木耳", 10, "干重"),
                        SimpleIngredient("鸡蛋", 40, "生重")
                    ], 125, 9.5, ["酸辣开胃"]),

                    SimpleRecipe("冬瓜汤", [
                        SimpleIngredient("冬瓜", 150, "净重"),
                        SimpleIngredient("虾皮", 8, "干重"),
                        SimpleIngredient("小葱", 5, "净重")
                    ], 75, 6.2, ["清热"]),

                    SimpleRecipe("紫菜蛋花汤", [
                        SimpleIngredient("紫菜", 5, "干重"),
                        SimpleIngredient("鸡蛋", 50, "生重"),
                        SimpleIngredient("香菜", 8, "净重")
                    ], 95, 7.8, ["经典汤品"]),

                    SimpleRecipe("丝瓜汤", [
                        SimpleIngredient("丝瓜", 120, "净重"),
                        SimpleIngredient("鸡蛋", 40, "生重")
                    ], 85, 6.5, ["清淡"]),

                    SimpleRecipe("萝卜汤", [
                        SimpleIngredient("白萝卜", 150, "净重"),
                        SimpleIngredient("香菇", 25, "净重")
                    ], 65, 3.8, ["消食"]),

                    SimpleRecipe("番茄蛋汤", [
                        SimpleIngredient("番茄", 100, "净重"),
                        SimpleIngredient("鸡蛋", 60, "生重"),
                        SimpleIngredient("小葱", 5, "净重")
                    ], 125, 8.5, ["酸甜"]),

                    SimpleRecipe("青菜豆腐汤", [
                        SimpleIngredient("小青菜", 100, "净重"),
                        SimpleIngredient("嫩豆腐", 80, "净重")
                    ], 95, 7.2, ["清淡营养"])
                ],
                "加餐": [
                    SimpleRecipe("泡菜", [
                        SimpleIngredient("四川泡菜", 60, "净重")
                    ], 25, 1.5, ["开胃"]),

                    SimpleRecipe("花生米", [
                        SimpleIngredient("水煮花生", 25, "净重")
                    ], 125, 6.5, ["下酒菜"]),

                    SimpleRecipe("豆干", [
                        SimpleIngredient("五香豆干", 40, "净重")
                    ], 85, 8.2, ["豆制品"]),

                    SimpleRecipe("酸萝卜", [
                        SimpleIngredient("腌萝卜", 50, "净重")
                    ], 25, 1.2, ["爽脆"]),

                    SimpleRecipe("榨菜丝", [
                        SimpleIngredient("榨菜丝", 30, "净重")
                    ], 15, 1.8, ["咸菜"]),

                    SimpleRecipe("豆花", [
                        SimpleIngredient("嫩豆腐", 80, "净重"),
                        SimpleIngredient("调料", 5, "净重")
                    ], 65, 6.5, ["小份"]),

                    SimpleRecipe("凉粉", [
                        SimpleIngredient("凉粉", 100, "净重"),
                        SimpleIngredient("调料", 8, "净重")
                    ], 45, 1.8, ["清凉"])
                ]
            },

            "粤菜": {
                "早餐": [
                    SimpleRecipe("瘦肉粥", [
                        SimpleIngredient("瘦肉丝", 40, "净重"),
                        SimpleIngredient("大米", 35, "干重"),
                        SimpleIngredient("咸菜", 20, "净重")
                    ], 245, 16.8, ["养胃"]),

                    SimpleRecipe("白粥配咸菜", [
                        SimpleIngredient("大米", 40, "干重"),
                        SimpleIngredient("榨菜", 25, "净重")
                    ], 195, 6.5, ["清淡"]),

                    SimpleRecipe("蒸蛋羹", [
                        SimpleIngredient("鸡蛋", 100, "生重"),
                        SimpleIngredient("温水", 150, "净重"),
                        SimpleIngredient("香菇丁", 20, "净重")
                    ], 175, 14.8, ["嫩滑"]),

                    SimpleRecipe("虾仁粥", [
                        SimpleIngredient("虾仁", 50, "净重"),
                        SimpleIngredient("大米", 35, "干重"),
                        SimpleIngredient("青菜丁", 30, "净重")
                    ], 225, 18.5, ["海鲜"]),

                    SimpleRecipe("艇仔粥", [
                        SimpleIngredient("瘦肉", 30, "净重"),
                        SimpleIngredient("咸蛋", 25, "净重"),
                        SimpleIngredient("大米", 35, "干重")
                    ], 265, 16.8, ["传统"]),

                    SimpleRecipe("白切鸡", [
                        SimpleIngredient("鸡胸肉", 80, "净重"),
                        SimpleIngredient("生菜", 60, "净重")
                    ], 185, 24.5, ["原汁原味"]),

                    SimpleRecipe("肠粉", [
                        SimpleIngredient("河粉", 80, "净重"),
                        SimpleIngredient("虾仁", 30, "净重"),
                        SimpleIngredient("韭黄", 20, "净重")
                    ], 195, 12.5, ["经典"])
                ],
                "午餐": [
                    SimpleRecipe("白切鸡", [
                        SimpleIngredient("白切鸡", 120, "净重"),
                        SimpleIngredient("蘸料", 10, "净重")
                    ], 225, 28.5, ["经典粤菜"]),

                    SimpleRecipe("清蒸鱼", [
                        SimpleIngredient("鲈鱼", 150, "净重"),
                        SimpleIngredient("生姜丝", 8, "净重"),
                        SimpleIngredient("小葱", 10, "净重")
                    ], 195, 28.8, ["清蒸烹饪"]),

                    SimpleRecipe("白灼菜心", [
                        SimpleIngredient("菜心", 150, "净重"),
                        SimpleIngredient("蒜蓉", 8, "净重")
                    ], 85, 5.2, ["清淡蔬菜"]),

                    SimpleRecipe("蒸水蛋", [
                        SimpleIngredient("鸡蛋", 120, "生重"),
                        SimpleIngredient("瘦肉丝", 30, "净重"),
                        SimpleIngredient("香菇丁", 20, "净重")
                    ], 195, 18.5, ["嫩滑"]),

                    SimpleRecipe("白灼虾", [
                        SimpleIngredient("基围虾", 120, "净重"),
                        SimpleIngredient("生菜", 80, "净重")
                    ], 165, 22.8, ["海鲜"]),

                    SimpleRecipe("清汤鱼丸", [
                        SimpleIngredient("鱼丸", 100, "净重"),
                        SimpleIngredient("冬瓜", 80, "净重"),
                        SimpleIngredient("紫菜", 5, "干重")
                    ], 145, 16.5, ["清汤"]),

                    SimpleRecipe("蒸排骨", [
                        SimpleIngredient("排骨", 100, "净重"),
                        SimpleIngredient("豆豉", 8, "净重"),
                        SimpleIngredient("红椒丁", 20, "净重")
                    ], 245, 22.8, ["蒸制"])
                ],
                "晚餐": [
                    SimpleRecipe("冬瓜排骨汤", [
                        SimpleIngredient("冬瓜", 150, "净重"),
                        SimpleIngredient("排骨", 60, "净重")
                    ], 125, 12.8, ["清汤"]),

                    SimpleRecipe("丝瓜汤", [
                        SimpleIngredient("丝瓜", 120, "净重"),
                        SimpleIngredient("鸡蛋", 50, "生重")
                    ], 95, 7.5, ["清淡"]),

                    SimpleRecipe("紫菜蛋花汤", [
                        SimpleIngredient("紫菜", 5, "干重"),
                        SimpleIngredient("鸡蛋", 60, "生重")
                    ], 105, 8.5, ["经典汤"]),

                    SimpleRecipe("青菜豆腐汤", [
                        SimpleIngredient("小白菜", 100, "净重"),
                        SimpleIngredient("嫩豆腐", 80, "净重")
                    ], 85, 7.2, ["营养"]),

                    SimpleRecipe("萝卜汤", [
                        SimpleIngredient("白萝卜", 150, "净重"),
                        SimpleIngredient("瘦肉丝", 25, "净重")
                    ], 95, 8.5, ["清甜"]),

                    SimpleRecipe("蛤蜊汤", [
                        SimpleIngredient("蛤蜊", 100, "净重"),
                        SimpleIngredient("冬瓜", 80, "净重")
                    ], 85, 12.5, ["海鲜汤"]),

                    SimpleRecipe("瘦肉汤", [
                        SimpleIngredient("瘦肉", 60, "净重"),
                        SimpleIngredient("青菜", 80, "净重")
                    ], 125, 14.8, ["滋补"])
                ],
                "加餐": [
                    SimpleRecipe("广式点心", [
                        SimpleIngredient("虾饺", 60, "净重")
                    ], 145, 8.5, ["点心"]),

                    SimpleRecipe("白切鸡", [
                        SimpleIngredient("鸡肉", 50, "净重")
                    ], 125, 14.5, ["小份"]),

                    SimpleRecipe("蒸蛋挞", [
                        SimpleIngredient("蛋挞", 40, "净重")
                    ], 165, 5.8, ["甜点"]),

                    SimpleRecipe("凉拌海蜇", [
                        SimpleIngredient("海蜇", 60, "净重"),
                        SimpleIngredient("黄瓜丝", 30, "净重")
                    ], 45, 6.5, ["爽脆"]),

                    SimpleRecipe("白切猪肚", [
                        SimpleIngredient("猪肚", 40, "净重")
                    ], 85, 8.5, ["内脏"]),

                    SimpleRecipe("蒸蛋羹", [
                        SimpleIngredient("鸡蛋", 60, "生重"),
                        SimpleIngredient("温水", 90, "净重")
                    ], 95, 7.2, ["小份蒸蛋"]),

                    SimpleRecipe("白粥", [
                        SimpleIngredient("大米", 25, "干重")
                    ], 125, 3.5, ["简单"])
                ]
            }
        }

    def get_recipe_by_name(self, recipe_name: str) -> Optional[SimpleRecipe]:
        """根据名称查找菜谱"""
        for cuisine_type in self.recipes:
            for meal_type in self.recipes[cuisine_type]:
                for recipe in self.recipes[cuisine_type][meal_type]:
                    if recipe.name == recipe_name:
                        return recipe
        return None

    def format_recipe_for_display(self, recipe: SimpleRecipe) -> str:
        """格式化菜谱显示"""
        ingredients_text = []
        for ingredient in recipe.ingredients:
            ingredients_text.append(f"• **{ingredient.name}**: {ingredient.weight}g ({ingredient.weight_type})")

        return f"""
**食材清单:**
{chr(10).join(ingredients_text)}

**营养信息:**
• 总热量: {recipe.calories}kcal
• 蛋白质: {recipe.protein}g
• 适宜疾病: {', '.join(recipe.disease_suitable)}
"""

# 为了兼容性，创建别名
DetailedRecipeManager = SimpleRecipeManager
DetailedRecipe = SimpleRecipe
IngredientInfo = SimpleIngredient