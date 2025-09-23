"""
详细菜谱重量管理模块
提供具体的食材重量信息（干重/湿重），让患者能够准确执行营养方案
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

class WeightType(Enum):
    """重量类型"""
    RAW = "生重"        # 生重/购买重量
    DRY = "干重"        # 干重（如大米、面条等）
    COOKED = "熟重"     # 烹饪后重量
    NET = "净重"        # 净重（去皮去骨后）

@dataclass
class IngredientInfo:
    """食材详细信息"""
    name: str                              # 食材名称
    raw_weight: float                      # 生重(g)
    dry_weight: Optional[float] = None     # 干重(g)，适用于米面等
    cooked_weight: Optional[float] = None  # 熟重(g)
    net_weight: Optional[float] = None     # 净重(g)，去皮去骨后
    preparation_note: str = ""             # 处理说明
    nutrition_note: str = ""               # 营养说明

@dataclass
class DetailedRecipe:
    """详细菜谱信息"""
    name: str                              # 菜谱名称
    category: str                          # 餐次分类
    cuisine_type: str                      # 菜系类型
    ingredients: List[IngredientInfo]      # 食材列表
    cooking_method: str                    # 烹饪方法
    preparation_time: int                  # 准备时间(分钟)
    cooking_time: int                      # 烹饪时间(分钟)
    difficulty: str                        # 难度等级
    instructions: List[str]                # 制作步骤
    nutrition_highlights: List[str]        # 营养亮点
    disease_suitability: List[str]         # 疾病适宜性
    total_calories: float                  # 总热量(kcal)
    protein: float                         # 蛋白质(g)
    carbs: float                          # 碳水化合物(g)
    fat: float                            # 脂肪(g)
    fiber: float                          # 膳食纤维(g)

class DetailedRecipeManager:
    """详细菜谱管理器"""

    def __init__(self):
        self.detailed_recipes = self._initialize_detailed_recipes()

    def _initialize_detailed_recipes(self) -> Dict[str, Dict[str, List[DetailedRecipe]]]:
        """初始化详细菜谱数据库"""

        return {
            "清淡": {
                "早餐": [
                    DetailedRecipe(
                        name="燕麦鸡蛋套餐",
                        category="早餐",
                        cuisine_type="清淡",
                        ingredients=[
                            IngredientInfo(
                                name="燕麦片",
                                raw_weight=40,
                                dry_weight=40,
                                cooked_weight=120,
                                preparation_note="选择无糖燕麦片",
                                nutrition_note="富含β-葡聚糖，有助降低胆固醇"
                            ),
                            IngredientInfo(
                                name="鸡蛋",
                                raw_weight=60,
                                net_weight=50,
                                cooked_weight=55,
                                preparation_note="选择新鲜鸡蛋，水煮7-8分钟",
                                nutrition_note="优质蛋白质来源，富含维生素B12"
                            ),
                            IngredientInfo(
                                name="脱脂牛奶",
                                raw_weight=200,
                                preparation_note="可温热饮用，避免过烫",
                                nutrition_note="提供钙质和蛋白质，脂肪含量低"
                            ),
                            IngredientInfo(
                                name="苹果",
                                raw_weight=120,
                                net_weight=100,
                                preparation_note="带皮食用，充分清洗",
                                nutrition_note="富含果胶和维生素C"
                            ),
                            IngredientInfo(
                                name="核桃仁",
                                raw_weight=10,
                                preparation_note="少量即可，补充ω-3脂肪酸",
                                nutrition_note="提供不饱和脂肪酸，有益心血管健康"
                            )
                        ],
                        cooking_method="水煮+冲泡",
                        preparation_time=5,
                        cooking_time=10,
                        difficulty="简单",
                        instructions=[
                            "1. 将鸡蛋放入冷水中，煮开后继续煮7-8分钟",
                            "2. 用热水冲泡燕麦片，静置3-5分钟至软糯",
                            "3. 牛奶可微波加热至温热（约50-60°C）",
                            "4. 苹果洗净切块，核桃仁可稍微压碎",
                            "5. 所有食材搭配食用，注意细嚼慢咽"
                        ],
                        nutrition_highlights=[
                            "高蛋白质：约25g",
                            "高纤维：约8g",
                            "低升糖指数",
                            "富含不饱和脂肪酸"
                        ],
                        disease_suitability=["糖尿病", "高血压", "高血脂", "心血管疾病"],
                        total_calories=420,
                        protein=25.2,
                        carbs=42.8,
                        fat=15.6,
                        fiber=8.2
                    ),
                    DetailedRecipe(
                        name="豆腐脑配菜",
                        category="早餐",
                        cuisine_type="川菜",
                        ingredients=[
                            IngredientInfo(
                                name="嫩豆腐",
                                raw_weight=200,
                                preparation_note="选择新鲜嫩豆腐，无添加剂",
                                nutrition_note="植物蛋白质，含有异黄酮"
                            ),
                            IngredientInfo(
                                name="紫菜",
                                raw_weight=3,
                                dry_weight=3,
                                cooked_weight=15,
                                preparation_note="撕成小片，用温水泡发",
                                nutrition_note="富含碘和膳食纤维"
                            ),
                            IngredientInfo(
                                name="小白菜",
                                raw_weight=100,
                                net_weight=80,
                                cooked_weight=60,
                                preparation_note="选择嫩叶，充分清洗",
                                nutrition_note="富含维生素C和叶酸"
                            ),
                            IngredientInfo(
                                name="香菇",
                                raw_weight=30,
                                net_weight=25,
                                cooked_weight=20,
                                preparation_note="切片，可提前泡发",
                                nutrition_note="提供膳食纤维和B族维生素"
                            ),
                            IngredientInfo(
                                name="胡萝卜丝",
                                raw_weight=30,
                                net_weight=25,
                                preparation_note="切细丝，利于消化",
                                nutrition_note="富含β-胡萝卜素"
                            )
                        ],
                        cooking_method="蒸煮",
                        preparation_time=10,
                        cooking_time=15,
                        difficulty="简单",
                        instructions=[
                            "1. 豆腐切块，用开水略烫去腥",
                            "2. 香菇切片，胡萝卜切丝",
                            "3. 小白菜洗净切段",
                            "4. 紫菜用温水泡发",
                            "5. 锅内加水烧开，依次放入香菇、胡萝卜丝",
                            "6. 煮3分钟后加入豆腐和小白菜",
                            "7. 最后加入紫菜，调味即可"
                        ],
                        nutrition_highlights=[
                            "植物蛋白丰富",
                            "低热量高营养",
                            "富含膳食纤维",
                            "适合糖尿病患者"
                        ],
                        disease_suitability=["糖尿病", "高血压", "肥胖症", "便秘"],
                        total_calories=180,
                        protein=15.8,
                        carbs=12.4,
                        fat=6.2,
                        fiber=5.6
                    )
                ],
                "午餐": [
                    DetailedRecipe(
                        name="清蒸鲈鱼配糙米",
                        category="午餐",
                        cuisine_type="川菜",
                        ingredients=[
                            IngredientInfo(
                                name="鲈鱼",
                                raw_weight=200,
                                net_weight=150,
                                cooked_weight=120,
                                preparation_note="去鳞去内脏，切段或整条蒸制",
                                nutrition_note="优质蛋白质，富含ω-3脂肪酸"
                            ),
                            IngredientInfo(
                                name="糙米",
                                raw_weight=80,
                                dry_weight=80,
                                cooked_weight=200,
                                preparation_note="提前浸泡1小时，利于煮制",
                                nutrition_note="富含B族维生素和膳食纤维"
                            ),
                            IngredientInfo(
                                name="生姜",
                                raw_weight=5,
                                preparation_note="切丝，去腥增香",
                                nutrition_note="促进消化，温中散寒"
                            ),
                            IngredientInfo(
                                name="大葱",
                                raw_weight=10,
                                preparation_note="切段，蒸制时使用",
                                nutrition_note="含有硫化物，有抗菌作用"
                            ),
                            IngredientInfo(
                                name="蒸鱼豉油",
                                raw_weight=10,
                                preparation_note="选择低钠版本",
                                nutrition_note="调味用，控制钠摄入"
                            ),
                            IngredientInfo(
                                name="菠菜",
                                raw_weight=150,
                                net_weight=120,
                                cooked_weight=80,
                                preparation_note="去根洗净，焯水去草酸",
                                nutrition_note="富含叶酸和铁质"
                            )
                        ],
                        cooking_method="清蒸+水煮",
                        preparation_time=15,
                        cooking_time=25,
                        difficulty="中等",
                        instructions=[
                            "1. 糙米淘洗干净，加水1.5倍煮制（约25分钟）",
                            "2. 鲈鱼处理干净，两面划几刀便于入味",
                            "3. 鱼身摆放姜丝和葱段，腌制10分钟",
                            "4. 水开后将鱼放入蒸锅，大火蒸8-10分钟",
                            "5. 菠菜焯水1分钟后过冷水，挤干水分",
                            "6. 蒸好的鱼淋上蒸鱼豉油",
                            "7. 配菠菜和糙米饭食用"
                        ],
                        nutrition_highlights=[
                            "优质蛋白质：约32g",
                            "ω-3脂肪酸丰富",
                            "低脂肪制作方式",
                            "血糖指数较低"
                        ],
                        disease_suitability=["糖尿病", "高血脂", "心血管疾病", "高血压"],
                        total_calories=485,
                        protein=32.5,
                        carbs=58.2,
                        fat=8.4,
                        fiber=4.8
                    )
                ],
                "晚餐": [
                    DetailedRecipe(
                        name="蒸蛋羹+青菜",
                        category="晚餐",
                        cuisine_type="川菜",
                        ingredients=[
                            IngredientInfo(
                                name="鸡蛋",
                                raw_weight=100,  # 约2个鸡蛋
                                preparation_note="选择新鲜鸡蛋，打散备用",
                                nutrition_note="完全蛋白质，易于消化"
                            ),
                            IngredientInfo(
                                name="温开水",
                                raw_weight=150,
                                preparation_note="水温约40°C，蛋液与水比例1:1.5",
                                nutrition_note="稀释蛋液，使口感更嫩滑"
                            ),
                            IngredientInfo(
                                name="小青菜",
                                raw_weight=200,
                                net_weight=160,
                                cooked_weight=120,
                                preparation_note="选择嫩叶，充分清洗",
                                nutrition_note="富含维生素C和叶绿素"
                            ),
                            IngredientInfo(
                                name="香油",
                                raw_weight=3,
                                preparation_note="蒸蛋完成后滴几滴增香",
                                nutrition_note="少量使用，提供必需脂肪酸"
                            ),
                            IngredientInfo(
                                name="生抽",
                                raw_weight=5,
                                preparation_note="选择低钠生抽",
                                nutrition_note="调味用，控制钠摄入量"
                            )
                        ],
                        cooking_method="蒸制+快炒",
                        preparation_time=10,
                        cooking_time=15,
                        difficulty="简单",
                        instructions=[
                            "1. 鸡蛋打散，加入温开水搅拌均匀",
                            "2. 过筛去除泡沫，倒入蒸碗中",
                            "3. 蒸碗表面覆盖保鲜膜，防止水汽滴入",
                            "4. 水开后放入蒸锅，中小火蒸10-12分钟",
                            "5. 青菜洗净，热锅少油快速翻炒2-3分钟",
                            "6. 蒸蛋完成后滴几滴香油和生抽",
                            "7. 搭配青菜一起食用"
                        ],
                        nutrition_highlights=[
                            "优质蛋白质容易消化",
                            "低热量营养丰富",
                            "维生素含量高",
                            "适合晚餐食用"
                        ],
                        disease_suitability=["糖尿病", "胃病", "高血压", "老年人"],
                        total_calories=220,
                        protein=16.8,
                        carbs=8.4,
                        fat=12.6,
                        fiber=3.2
                    )
                ],
                "加餐": [
                    DetailedRecipe(
                        name="水煮蛋",
                        category="加餐",
                        cuisine_type="通用",
                        ingredients=[
                            IngredientInfo(
                                name="鸡蛋",
                                raw_weight=50,  # 1个中等大小鸡蛋
                                cooked_weight=45,
                                preparation_note="选择新鲜鸡蛋，室温放置",
                                nutrition_note="完全蛋白质，含有必需氨基酸"
                            )
                        ],
                        cooking_method="水煮",
                        preparation_time=2,
                        cooking_time=8,
                        difficulty="简单",
                        instructions=[
                            "1. 鸡蛋从冰箱取出，恢复室温",
                            "2. 锅内加水，水量要完全覆盖鸡蛋",
                            "3. 冷水下锅，大火煮开",
                            "4. 水开后转中火，继续煮6-8分钟",
                            "5. 煮好后立即放入冷水中降温",
                            "6. 轻敲蛋壳，剥皮食用"
                        ],
                        nutrition_highlights=[
                            "纯蛋白质来源",
                            "零碳水化合物",
                            "饱腹感强",
                            "便于携带"
                        ],
                        disease_suitability=["糖尿病", "减肥", "健身", "高血压"],
                        total_calories=70,
                        protein=6.3,
                        carbs=0.4,
                        fat=4.8,
                        fiber=0
                    )
                ]
            },
            "粤菜": {
                "早餐": [
                    DetailedRecipe(
                        name="瘦肉粥配咸菜",
                        category="早餐",
                        cuisine_type="粤菜",
                        ingredients=[
                            IngredientInfo(
                                name="大米",
                                raw_weight=50,
                                dry_weight=50,
                                cooked_weight=150,
                                preparation_note="选择优质大米，提前浸泡30分钟",
                                nutrition_note="提供碳水化合物和B族维生素"
                            ),
                            IngredientInfo(
                                name="瘦猪肉",
                                raw_weight=80,
                                net_weight=75,
                                cooked_weight=60,
                                preparation_note="切丝，用料酒和生抽腌制",
                                nutrition_note="优质蛋白质，铁含量丰富"
                            ),
                            IngredientInfo(
                                name="生菜",
                                raw_weight=100,
                                net_weight=85,
                                preparation_note="洗净切段，最后加入保持脆嫩",
                                nutrition_note="富含维生素A和叶酸"
                            ),
                            IngredientInfo(
                                name="胡萝卜",
                                raw_weight=30,
                                net_weight=25,
                                preparation_note="切小丁，增加营养和颜色",
                                nutrition_note="β-胡萝卜素含量丰富"
                            ),
                            IngredientInfo(
                                name="生姜",
                                raw_weight=5,
                                preparation_note="切丝，去腥增香",
                                nutrition_note="促进消化，温胃散寒"
                            )
                        ],
                        cooking_method="煮粥",
                        preparation_time=15,
                        cooking_time=45,
                        difficulty="中等",
                        instructions=[
                            "1. 大米淘洗干净，浸泡30分钟",
                            "2. 瘦肉切丝，用少量料酒和生抽腌制15分钟",
                            "3. 锅内加水1200ml，大火煮开",
                            "4. 加入大米，转小火慢煮35分钟，期间搅拌防粘",
                            "5. 加入腌制好的肉丝和胡萝卜丁",
                            "6. 继续煮10分钟至肉丝熟透",
                            "7. 最后加入生菜段，煮2分钟即可",
                            "8. 调味后关火，静置5分钟再食用"
                        ],
                        nutrition_highlights=[
                            "易消化吸收",
                            "蛋白质含量适中",
                            "温胃养胃",
                            "适合早餐食用"
                        ],
                        disease_suitability=["胃病", "糖尿病", "老年人", "术后恢复"],
                        total_calories=380,
                        protein=22.4,
                        carbs=52.8,
                        fat=6.8,
                        fiber=2.4
                    )
                ]
            },
            "清淡": {
                "早餐": [
                    DetailedRecipe(
                        name="小米粥配蒸蛋",
                        category="早餐",
                        cuisine_type="清淡",
                        ingredients=[
                            IngredientInfo(
                                name="小米",
                                raw_weight=50,
                                dry_weight=50,
                                cooked_weight=200,
                                preparation_note="淘洗干净，可提前浸泡",
                                nutrition_note="富含B族维生素和矿物质"
                            ),
                            IngredientInfo(
                                name="鸡蛋",
                                raw_weight=50,
                                preparation_note="打散后蒸制，口感嫩滑",
                                nutrition_note="优质蛋白质，消化率高"
                            ),
                            IngredientInfo(
                                name="温开水",
                                raw_weight=75,
                                preparation_note="与蛋液混合，比例1:1.5",
                                nutrition_note="使蒸蛋更加嫩滑"
                            ),
                            IngredientInfo(
                                name="红枣",
                                raw_weight=20,
                                net_weight=18,
                                preparation_note="去核切片，与小米同煮",
                                nutrition_note="补血养颜，富含维生素C"
                            )
                        ],
                        cooking_method="煮粥+蒸制",
                        preparation_time=10,
                        cooking_time=30,
                        difficulty="简单",
                        instructions=[
                            "1. 小米淘洗干净，红枣去核切片",
                            "2. 锅内加水800ml，放入小米和红枣",
                            "3. 大火煮开后转小火慢煮25分钟",
                            "4. 鸡蛋打散，加入温开水搅匀",
                            "5. 过筛去泡沫，倒入小碗中",
                            "6. 水开后蒸8-10分钟至凝固",
                            "7. 小米粥煮至粘稠即可",
                            "8. 搭配蒸蛋一起食用"
                        ],
                        nutrition_highlights=[
                            "养胃易消化",
                            "营养均衡",
                            "温补脾胃",
                            "适合体弱者"
                        ],
                        disease_suitability=["胃病", "贫血", "产后调理", "儿童"],
                        total_calories=280,
                        protein=12.6,
                        carbs=48.2,
                        fat=5.8,
                        fiber=3.2
                    )
                ]
            },

            # 地中海饮食菜系
            "地中海": {
                "早餐": [
                    DetailedRecipe(
                        name="希腊酸奶配坚果",
                        category="早餐",
                        cuisine_type="地中海",
                        ingredients=[
                            IngredientInfo(
                                name="希腊酸奶",
                                raw_weight=150,
                                preparation_note="选择无糖原味希腊酸奶",
                                nutrition_note="高蛋白质，含益生菌"
                            ),
                            IngredientInfo(
                                name="核桃仁",
                                raw_weight=15,
                                preparation_note="轻微烘烤增加香味",
                                nutrition_note="富含ω-3脂肪酸和维生素E"
                            ),
                            IngredientInfo(
                                name="杏仁片",
                                raw_weight=10,
                                preparation_note="无盐烘烤杏仁片",
                                nutrition_note="提供维生素E和镁"
                            ),
                            IngredientInfo(
                                name="蓝莓",
                                raw_weight=80,
                                preparation_note="新鲜或冷冻均可",
                                nutrition_note="富含花青素和抗氧化剂"
                            ),
                            IngredientInfo(
                                name="蜂蜜",
                                raw_weight=8,
                                preparation_note="天然蜂蜜，适量调味",
                                nutrition_note="天然甜味剂，含抗菌成分"
                            )
                        ],
                        cooking_method="混合",
                        preparation_time=5,
                        cooking_time=0,
                        difficulty="简单",
                        instructions=[
                            "1. 将希腊酸奶倒入碗中",
                            "2. 撒上核桃仁和杏仁片",
                            "3. 加入新鲜蓝莓",
                            "4. 淋上少量蜂蜜调味",
                            "5. 轻轻搅拌即可享用"
                        ],
                        nutrition_highlights=[
                            "高蛋白质：约18g",
                            "富含益生菌",
                            "抗氧化剂丰富",
                            "健康脂肪来源"
                        ],
                        disease_suitability=["糖尿病", "心血管疾病", "高血脂"],
                        total_calories=285,
                        protein=18.2,
                        carbs=22.5,
                        fat=16.8,
                        fiber=5.2
                    )
                ],
                "午餐": [
                    DetailedRecipe(
                        name="地中海烤鱼配蔬菜",
                        category="午餐",
                        cuisine_type="地中海",
                        ingredients=[
                            IngredientInfo(
                                name="鲑鱼片",
                                raw_weight=120,
                                net_weight=120,
                                cooked_weight=100,
                                preparation_note="去皮去骨，用柠檬汁腌制",
                                nutrition_note="富含ω-3脂肪酸和优质蛋白"
                            ),
                            IngredientInfo(
                                name="西红柿",
                                raw_weight=100,
                                net_weight=95,
                                preparation_note="切块，保留皮和籽",
                                nutrition_note="富含番茄红素和维生素C"
                            ),
                            IngredientInfo(
                                name="黄瓜",
                                raw_weight=80,
                                net_weight=75,
                                preparation_note="切片，可带皮食用",
                                nutrition_note="高水分，低热量"
                            ),
                            IngredientInfo(
                                name="紫洋葱",
                                raw_weight=30,
                                net_weight=25,
                                preparation_note="切薄片，减少辛辣味",
                                nutrition_note="含硫化合物，有抗炎作用"
                            ),
                            IngredientInfo(
                                name="橄榄油",
                                raw_weight=10,
                                preparation_note="特级初榨橄榄油",
                                nutrition_note="单不饱和脂肪酸丰富"
                            ),
                            IngredientInfo(
                                name="柠檬汁",
                                raw_weight=15,
                                preparation_note="新鲜柠檬现榨",
                                nutrition_note="维生素C和柠檬酸"
                            )
                        ],
                        cooking_method="烤制",
                        preparation_time=15,
                        cooking_time=20,
                        difficulty="中等",
                        instructions=[
                            "1. 鱼片用柠檬汁、盐腌制15分钟",
                            "2. 烤箱预热至200°C",
                            "3. 蔬菜切好，淋上橄榄油",
                            "4. 鱼片和蔬菜一起烤18-20分钟",
                            "5. 出炉后挤柠檬汁调味"
                        ],
                        nutrition_highlights=[
                            "优质蛋白质：约25g",
                            "ω-3脂肪酸丰富",
                            "抗氧化剂充足",
                            "低碳水化合物"
                        ],
                        disease_suitability=["糖尿病", "心血管疾病", "高血脂", "高血压"],
                        total_calories=325,
                        protein=25.8,
                        carbs=8.5,
                        fat=22.3,
                        fiber=3.2
                    )
                ],
                "晚餐": [
                    DetailedRecipe(
                        name="地中海蔬菜汤",
                        category="晚餐",
                        cuisine_type="地中海",
                        ingredients=[
                            IngredientInfo(
                                name="西葫芦",
                                raw_weight=100,
                                net_weight=90,
                                cooked_weight=75,
                                preparation_note="切块，保留皮",
                                nutrition_note="低热量，富含钾"
                            ),
                            IngredientInfo(
                                name="茄子",
                                raw_weight=80,
                                net_weight=75,
                                cooked_weight=60,
                                preparation_note="去蒂切块",
                                nutrition_note="含膳食纤维和抗氧化剂"
                            ),
                            IngredientInfo(
                                name="彩椒",
                                raw_weight=60,
                                net_weight=55,
                                preparation_note="红黄椒各半，去籽切条",
                                nutrition_note="维生素C含量极高"
                            ),
                            IngredientInfo(
                                name="洋葱",
                                raw_weight=40,
                                net_weight=35,
                                preparation_note="切丁爆香",
                                nutrition_note="含硫化合物，增强免疫"
                            ),
                            IngredientInfo(
                                name="番茄",
                                raw_weight=80,
                                net_weight=75,
                                preparation_note="去皮切块",
                                nutrition_note="番茄红素丰富"
                            ),
                            IngredientInfo(
                                name="罗勒叶",
                                raw_weight=3,
                                preparation_note="新鲜罗勒叶",
                                nutrition_note="天然香草，有抗菌作用"
                            )
                        ],
                        cooking_method="炖煮",
                        preparation_time=20,
                        cooking_time=25,
                        difficulty="简单",
                        instructions=[
                            "1. 洋葱爆香，加入番茄炒制",
                            "2. 依次加入茄子、西葫芦",
                            "3. 加水没过蔬菜，小火炖煮",
                            "4. 最后加入彩椒和罗勒",
                            "5. 调味后炖煮5分钟即可"
                        ],
                        nutrition_highlights=[
                            "高纤维低热量",
                            "维生素丰富",
                            "抗氧化剂充足",
                            "饱腹感强"
                        ],
                        disease_suitability=["糖尿病", "高血压", "肥胖", "便秘"],
                        total_calories=125,
                        protein=4.2,
                        carbs=25.8,
                        fat=2.1,
                        fiber=8.5
                    )
                ],
                "加餐": [
                    DetailedRecipe(
                        name="橄榄坚果拼盘",
                        category="加餐",
                        cuisine_type="地中海",
                        ingredients=[
                            IngredientInfo(
                                name="黑橄榄",
                                raw_weight=20,
                                preparation_note="去核橄榄",
                                nutrition_note="单不饱和脂肪酸丰富"
                            ),
                            IngredientInfo(
                                name="开心果",
                                raw_weight=15,
                                preparation_note="无盐烘烤",
                                nutrition_note="富含蛋白质和健康脂肪"
                            ),
                            IngredientInfo(
                                name="小番茄",
                                raw_weight=60,
                                preparation_note="樱桃番茄，对半切开",
                                nutrition_note="番茄红素和维生素C"
                            )
                        ],
                        cooking_method="直接食用",
                        preparation_time=5,
                        cooking_time=0,
                        difficulty="简单",
                        instructions=[
                            "1. 橄榄去核切半",
                            "2. 开心果去壳",
                            "3. 小番茄洗净对半切",
                            "4. 装盘搭配食用"
                        ],
                        nutrition_highlights=[
                            "健康脂肪来源",
                            "抗氧化剂丰富",
                            "适量蛋白质",
                            "低升糖指数"
                        ],
                        disease_suitability=["糖尿病", "心血管疾病", "高血脂"],
                        total_calories=145,
                        protein=5.2,
                        carbs=8.5,
                        fat=11.8,
                        fiber=3.1
                    )
                ]
            },

            # 日式/韩式菜系
            "日韩": {
                "早餐": [
                    DetailedRecipe(
                        name="日式蒸蛋豆腐",
                        category="早餐",
                        cuisine_type="日韩",
                        ingredients=[
                            IngredientInfo(
                                name="鸡蛋",
                                raw_weight=100,
                                net_weight=90,
                                cooked_weight=85,
                                preparation_note="打散成蛋液",
                                nutrition_note="完整蛋白质来源"
                            ),
                            IngredientInfo(
                                name="嫩豆腐",
                                raw_weight=80,
                                preparation_note="切小块，质地嫩滑",
                                nutrition_note="植物蛋白和异黄酮"
                            ),
                            IngredientInfo(
                                name="鸡汤",
                                raw_weight=150,
                                preparation_note="清淡鸡汤或高汤",
                                nutrition_note="提供鲜味和营养"
                            ),
                            IngredientInfo(
                                name="海苔丝",
                                raw_weight=2,
                                dry_weight=2,
                                preparation_note="切丝装饰",
                                nutrition_note="富含碘和矿物质"
                            ),
                            IngredientInfo(
                                name="小葱",
                                raw_weight=5,
                                preparation_note="切葱花点缀",
                                nutrition_note="含维生素C和挥发油"
                            )
                        ],
                        cooking_method="蒸制",
                        preparation_time=10,
                        cooking_time=15,
                        difficulty="中等",
                        instructions=[
                            "1. 鸡蛋打散，加入温鸡汤调匀",
                            "2. 豆腐块放入蒸碗中",
                            "3. 倒入蛋液，撇去浮沫",
                            "4. 上锅蒸12-15分钟至凝固",
                            "5. 出锅撒葱花和海苔丝"
                        ],
                        nutrition_highlights=[
                            "高蛋白质：约16g",
                            "低脂肪低热量",
                            "易消化吸收",
                            "富含矿物质"
                        ],
                        disease_suitability=["糖尿病", "胃病", "高血压", "老年营养"],
                        total_calories=185,
                        protein=16.2,
                        carbs=4.5,
                        fat=11.8,
                        fiber=1.2
                    )
                ],
                "午餐": [
                    DetailedRecipe(
                        name="韩式蒸蛋配蔬菜",
                        category="午餐",
                        cuisine_type="日韩",
                        ingredients=[
                            IngredientInfo(
                                name="鸡蛋",
                                raw_weight=120,
                                net_weight=110,
                                cooked_weight=100,
                                preparation_note="打散加少量水",
                                nutrition_note="优质蛋白质和维生素"
                            ),
                            IngredientInfo(
                                name="胡萝卜丝",
                                raw_weight=50,
                                net_weight=45,
                                preparation_note="切细丝，焯水备用",
                                nutrition_note="β-胡萝卜素丰富"
                            ),
                            IngredientInfo(
                                name="菠菜",
                                raw_weight=80,
                                net_weight=70,
                                cooked_weight=40,
                                preparation_note="焯水去草酸",
                                nutrition_note="叶酸和铁质丰富"
                            ),
                            IngredientInfo(
                                name="豆芽菜",
                                raw_weight=60,
                                net_weight=55,
                                cooked_weight=45,
                                preparation_note="去根须，焯水",
                                nutrition_note="维生素C和膳食纤维"
                            ),
                            IngredientInfo(
                                name="香油",
                                raw_weight=3,
                                preparation_note="芝麻香油调味",
                                nutrition_note="维生素E和香味"
                            )
                        ],
                        cooking_method="蒸制",
                        preparation_time=15,
                        cooking_time=12,
                        difficulty="中等",
                        instructions=[
                            "1. 蔬菜分别焯水处理备用",
                            "2. 鸡蛋打散，加入蔬菜拌匀",
                            "3. 装入蒸碗，滴几滴香油",
                            "4. 上锅蒸10-12分钟",
                            "5. 出锅后稍凉即可食用"
                        ],
                        nutrition_highlights=[
                            "营养均衡全面",
                            "膳食纤维丰富",
                            "维生素充足",
                            "低热量高营养"
                        ],
                        disease_suitability=["糖尿病", "高血压", "便秘", "贫血"],
                        total_calories=235,
                        protein=18.5,
                        carbs=8.2,
                        fat=15.2,
                        fiber=4.8
                    )
                ],
                "晚餐": [
                    DetailedRecipe(
                        name="日式味噌汤",
                        category="晚餐",
                        cuisine_type="日韩",
                        ingredients=[
                            IngredientInfo(
                                name="嫩豆腐",
                                raw_weight=60,
                                preparation_note="切小块",
                                nutrition_note="植物蛋白质来源"
                            ),
                            IngredientInfo(
                                name="裙带菜",
                                raw_weight=5,
                                dry_weight=5,
                                cooked_weight=25,
                                preparation_note="干制品需提前泡发",
                                nutrition_note="富含碘和膳食纤维"
                            ),
                            IngredientInfo(
                                name="味噌酱",
                                raw_weight=15,
                                preparation_note="选择低盐味噌",
                                nutrition_note="发酵食品，含益生菌"
                            ),
                            IngredientInfo(
                                name="小葱",
                                raw_weight=8,
                                preparation_note="切葱花",
                                nutrition_note="增加维生素和香味"
                            ),
                            IngredientInfo(
                                name="高汤",
                                raw_weight=250,
                                preparation_note="清淡昆布高汤",
                                nutrition_note="天然鲜味来源"
                            )
                        ],
                        cooking_method="煮制",
                        preparation_time=10,
                        cooking_time=8,
                        difficulty="简单",
                        instructions=[
                            "1. 裙带菜提前泡发",
                            "2. 高汤加热至微沸",
                            "3. 加入豆腐和裙带菜",
                            "4. 味噌用少量汤调开后加入",
                            "5. 撒葱花即可出锅"
                        ],
                        nutrition_highlights=[
                            "低热量高营养",
                            "含益生菌",
                            "易消化",
                            "矿物质丰富"
                        ],
                        disease_suitability=["糖尿病", "胃病", "高血压", "甲状腺疾病"],
                        total_calories=85,
                        protein=6.8,
                        carbs=8.5,
                        fat=3.2,
                        fiber=2.8
                    )
                ],
                "加餐": [
                    DetailedRecipe(
                        name="韩式海苔卷",
                        category="加餐",
                        cuisine_type="日韩",
                        ingredients=[
                            IngredientInfo(
                                name="海苔片",
                                raw_weight=3,
                                dry_weight=3,
                                preparation_note="烘烤海苔片",
                                nutrition_note="富含碘、蛋白质和矿物质"
                            ),
                            IngredientInfo(
                                name="黄瓜条",
                                raw_weight=40,
                                net_weight=35,
                                preparation_note="去皮切条",
                                nutrition_note="高水分低热量"
                            ),
                            IngredientInfo(
                                name="胡萝卜条",
                                raw_weight=30,
                                net_weight=25,
                                preparation_note="切细条",
                                nutrition_note="β-胡萝卜素来源"
                            ),
                            IngredientInfo(
                                name="鸡蛋丝",
                                raw_weight=30,
                                cooked_weight=25,
                                preparation_note="摊成薄饼切丝",
                                nutrition_note="优质蛋白质"
                            )
                        ],
                        cooking_method="卷制",
                        preparation_time=15,
                        cooking_time=5,
                        difficulty="中等",
                        instructions=[
                            "1. 鸡蛋摊成薄饼切丝",
                            "2. 蔬菜切成细条备用",
                            "3. 海苔铺平，放入蔬菜和蛋丝",
                            "4. 紧密卷成圆筒状",
                            "5. 用刀切成段装盘"
                        ],
                        nutrition_highlights=[
                            "营养搭配均衡",
                            "富含矿物质",
                            "低热量饱腹",
                            "便于携带"
                        ],
                        disease_suitability=["糖尿病", "高血压", "减重", "甲状腺疾病"],
                        total_calories=95,
                        protein=6.2,
                        carbs=8.8,
                        fat=4.5,
                        fiber=2.8
                    )
                ]
            },

            # 川菜重新整理
            "川菜": {
                "早餐": [
                    DetailedRecipe(
                        name="四川酸菜鱼片粥",
                        category="早餐",
                        cuisine_type="川菜",
                        ingredients=[
                            IngredientInfo(
                                name="鱼片",
                                raw_weight=60,
                                net_weight=55,
                                preparation_note="选择草鱼或鲈鱼片",
                                nutrition_note="优质蛋白质，低脂肪"
                            ),
                            IngredientInfo(
                                name="酸菜",
                                raw_weight=30,
                                preparation_note="四川泡菜，切丝",
                                nutrition_note="发酵蔬菜，含益生菌"
                            ),
                            IngredientInfo(
                                name="大米",
                                raw_weight=40,
                                dry_weight=40,
                                cooked_weight=120,
                                preparation_note="优质大米，提前浸泡",
                                nutrition_note="碳水化合物主要来源"
                            ),
                            IngredientInfo(
                                name="生姜丝",
                                raw_weight=5,
                                preparation_note="切细丝去腥",
                                nutrition_note="温胃散寒"
                            ),
                            IngredientInfo(
                                name="小葱",
                                raw_weight=5,
                                preparation_note="切葱花",
                                nutrition_note="增香调味"
                            )
                        ],
                        cooking_method="煮制",
                        preparation_time=15,
                        cooking_time=25,
                        difficulty="中等",
                        instructions=[
                            "1. 大米洗净加水煮粥",
                            "2. 鱼片用料酒腌制去腥",
                            "3. 粥煮至软糯后加入酸菜",
                            "4. 最后加入鱼片煮3分钟",
                            "5. 撒葱花和胡椒粉调味"
                        ],
                        nutrition_highlights=[
                            "高蛋白质易消化",
                            "酸味开胃",
                            "温胃养胃",
                            "营养均衡"
                        ],
                        disease_suitability=["胃病", "消化不良", "体质虚弱"],
                        total_calories=245,
                        protein=18.5,
                        carbs=32.8,
                        fat=4.2,
                        fiber=2.1
                    )
                ],
                "午餐": [],
                "晚餐": [],
                "加餐": []
            }
        }

    def get_detailed_recipe(self, cuisine_type: str, meal_type: str, recipe_name: str) -> Optional[DetailedRecipe]:
        """获取详细菜谱信息"""
        try:
            recipes = self.detailed_recipes[cuisine_type][meal_type]
            for recipe in recipes:
                if recipe.name == recipe_name:
                    return recipe
            return None
        except KeyError:
            return None

    def get_recipe_by_name(self, recipe_name: str) -> Optional[DetailedRecipe]:
        """根据菜谱名称搜索菜谱（跨菜系和餐次）"""
        for cuisine_type in self.detailed_recipes:
            for meal_type in self.detailed_recipes[cuisine_type]:
                for recipe in self.detailed_recipes[cuisine_type][meal_type]:
                    if recipe.name == recipe_name:
                        return recipe
        return None

    def get_all_recipes_by_cuisine(self, cuisine_type: str) -> Dict[str, List[DetailedRecipe]]:
        """获取指定菜系的所有详细菜谱"""
        return self.detailed_recipes.get(cuisine_type, {})

    def search_recipes_by_ingredient(self, ingredient_name: str) -> List[DetailedRecipe]:
        """根据食材搜索菜谱"""
        found_recipes = []
        for cuisine_recipes in self.detailed_recipes.values():
            for meal_recipes in cuisine_recipes.values():
                for recipe in meal_recipes:
                    for ingredient in recipe.ingredients:
                        if ingredient_name in ingredient.name:
                            found_recipes.append(recipe)
                            break
        return found_recipes

    def get_recipes_for_disease(self, disease: str) -> List[DetailedRecipe]:
        """获取适合特定疾病的菜谱"""
        suitable_recipes = []
        for cuisine_recipes in self.detailed_recipes.values():
            for meal_recipes in cuisine_recipes.values():
                for recipe in meal_recipes:
                    if disease in recipe.disease_suitability:
                        suitable_recipes.append(recipe)
        return suitable_recipes

    def format_recipe_display(self, recipe: DetailedRecipe) -> str:
        """格式化菜谱显示信息"""
        output = []
        output.append(f"🍽️ **{recipe.name}** ({recipe.cuisine_type} · {recipe.category})")
        output.append(f"⏱️ 准备时间: {recipe.preparation_time}分钟 | 烹饪时间: {recipe.cooking_time}分钟 | 难度: {recipe.difficulty}")
        output.append(f"🔥 总热量: {recipe.total_calories}kcal")
        output.append("")

        output.append("📋 **食材清单:**")
        for ingredient in recipe.ingredients:
            weight_info = f"生重: {ingredient.raw_weight}g"
            if ingredient.dry_weight:
                weight_info += f" | 干重: {ingredient.dry_weight}g"
            if ingredient.cooked_weight:
                weight_info += f" | 熟重: {ingredient.cooked_weight}g"
            if ingredient.net_weight:
                weight_info += f" | 净重: {ingredient.net_weight}g"

            output.append(f"• **{ingredient.name}**: {weight_info}")
            if ingredient.preparation_note:
                output.append(f"  📝 处理: {ingredient.preparation_note}")
            if ingredient.nutrition_note:
                output.append(f"  💡 营养: {ingredient.nutrition_note}")
            output.append("")

        output.append("👨‍🍳 **制作步骤:**")
        for i, instruction in enumerate(recipe.instructions, 1):
            output.append(f"{i}. {instruction}")
        output.append("")

        output.append("🌟 **营养亮点:**")
        for highlight in recipe.nutrition_highlights:
            output.append(f"• {highlight}")
        output.append("")

        output.append("🏥 **适宜疾病:**")
        output.append(f"适合: {', '.join(recipe.disease_suitability)}")
        output.append("")

        output.append("📊 **营养成分:**")
        output.append(f"蛋白质: {recipe.protein}g | 碳水: {recipe.carbs}g | 脂肪: {recipe.fat}g | 纤维: {recipe.fiber}g")

        return "\n".join(output)

    def format_recipe_for_display(self, recipe: DetailedRecipe) -> str:
        """格式化菜谱显示信息（别名方法，与format_recipe_display相同）"""
        return self.format_recipe_display(recipe)

# 示例使用
if __name__ == "__main__":
    manager = DetailedRecipeManager()

    # 获取详细菜谱
    recipe = manager.get_detailed_recipe("川菜", "早餐", "燕麦鸡蛋套餐")
    if recipe:
        print(manager.format_recipe_display(recipe))

    # 搜索糖尿病适宜菜谱
    diabetes_recipes = manager.get_recipes_for_disease("糖尿病")
    print(f"\n找到 {len(diabetes_recipes)} 道适合糖尿病的菜谱")