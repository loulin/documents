"""
一周菜谱管理模块
实现7天不重复的高质量营养推荐系统
集成详细食材重量信息
"""

import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from simple_recipe_manager import SimpleRecipeManager, SimpleRecipe

@dataclass
class WeeklyMenuManager:
    """一周菜谱管理器"""

    def __init__(self):
        # 初始化简化菜谱管理器
        self.simple_recipe_manager = SimpleRecipeManager()

        # 一周高营养菜谱库 - 7天不重复，确保蛋白质充足度≥8，营养均衡度≥8，疾病适宜性≥9
        self.weekly_high_quality_recipes = {
            "清淡": {
                "早餐": [
                    "燕麦鸡蛋套餐",      # 周一
                    "小米粥配蒸蛋",      # 周二
                    "牛奶燕麦",          # 周三
                    "鸡蛋灌饼配粥",      # 周四
                    "蒸蛋羹配小米粥",    # 周五
                    "红薯鸡蛋粥",        # 周六
                    "全麦面包加鸡蛋"     # 周日
                ],
                "午餐": [
                    "清蒸鸡胸肉",        # 周一
                    "豆腐蔬菜汤",        # 周二
                    "清蒸鲈鱼配糙米",    # 周三
                    "白煮鸡蛋配米饭",    # 周四
                    "蒸虾仁配蔬菜",      # 周五
                    "清炖肉片汤",        # 周六
                    "豆腐鱼头汤"         # 周日
                ],
                "晚餐": [
                    "荞麦面配蔬菜",      # 周一
                    "蔬菜豆腐汤",        # 周二
                    "蒸蛋羹+青菜",       # 周三
                    "冬瓜排骨汤",        # 周四
                    "紫菜蛋花汤",        # 周五
                    "青菜豆腐汤",        # 周六
                    "白萝卜炒蛋"         # 周日
                ],
                "加餐": [
                    "酸奶",              # 周一
                    "水煮蛋",            # 周二
                    "蓝莓酸奶",          # 周三
                    "牛奶",              # 周四
                    "苹果片",            # 周五
                    "柚子片",            # 周六
                    "核桃仁"             # 周日
                ]
            },
            "地中海": {
                "早餐": [
                    "希腊酸奶配坚果",    # 周一
                    "橄榄油全麦吐司",    # 周二
                    "地中海果蔬杯",      # 周三
                    "坚果燕麦粥",        # 周四
                    "无花果酸奶",        # 周五
                    "鳄梨吐司",          # 周六
                    "浆果坚果拼盘"       # 周日
                ],
                "午餐": [
                    "地中海烤鱼配蔬菜",  # 周一
                    "橄榄油拌沙拉",      # 周二
                    "烤蔬菜配鱼肉",      # 周三
                    "地中海蔬菜卷",      # 周四
                    "烤鸡配时蔬",        # 周五
                    "海鲜沙拉",          # 周六
                    "蔬菜烘蛋"           # 周日
                ],
                "晚餐": [
                    "地中海蔬菜汤",      # 周一
                    "烤蔬菜拼盘",        # 周二
                    "番茄黄瓜沙拉",      # 周三
                    "烤茄子配橄榄",      # 周四
                    "蔬菜汤",            # 周五
                    "地中海沙拉",        # 周六
                    "烤彩椒"             # 周日
                ],
                "加餐": [
                    "橄榄坚果拼盘",      # 周一
                    "希腊酸奶",          # 周二
                    "坚果",              # 周三
                    "小番茄",            # 周四
                    "无花果",            # 周五
                    "橄榄",              # 周六
                    "杏仁"               # 周日
                ]
            },
            "日韩": {
                "早餐": [
                    "日式蒸蛋豆腐",      # 周一
                    "韩式海苔汤",        # 周二
                    "日式味噌汤",        # 周三
                    "韩式蒸蛋",          # 周四
                    "日式豆腐汤",        # 周五
                    "海苔拌饭",          # 周六
                    "蒸蛋羹"             # 周日
                ],
                "午餐": [
                    "韩式蒸蛋配蔬菜",    # 周一
                    "日式烤鱼",          # 周二
                    "韩式拌菜",          # 周三
                    "日式蒸蛋",          # 周四
                    "韩式豆腐汤",        # 周五
                    "日式沙拉",          # 周六
                    "蒸制海鲜"           # 周日
                ],
                "晚餐": [
                    "日式味噌汤",        # 周一
                    "韩式蔬菜汤",        # 周二
                    "日式豆腐汤",        # 周三
                    "韩式海带汤",        # 周四
                    "味噌蔬菜汤",        # 周五
                    "韩式萝卜汤",        # 周六
                    "日式清汤"           # 周日
                ],
                "加餐": [
                    "韩式海苔卷",        # 周一
                    "日式海苔",          # 周二
                    "韩式泡菜",          # 周三
                    "海苔片",            # 周四
                    "韩式萝卜",          # 周五
                    "日式小菜",          # 周六
                    "海苔汤"             # 周日
                ]
            },
            "川菜": {
                "早餐": [
                    "燕麦鸡蛋套餐",      # 周一
                    "豆腐脑配菜",         # 周二
                    "牛奶燕麦",            # 周三
                    "鸡蛋灌饼配粥",       # 周四
                    "蒸蛋羹配小米粥",   # 周五
                    "红薯鸡蛋粥",         # 周六
                    "全麦面包加鸡蛋"      # 周日
                ],
                "午餐": [
                    "清蒸鲈鱼配糙米",   # 周一
                    "清炖鸡汤配饭",     # 周二
                    "水煮虾仁",           # 周三
                    "麦片鸡蛋粥",         # 周四
                    "蒸蛋羹配糙米",     # 周五
                    "豆腐鱼头汤",         # 周六
                    "清炒鸡丝配面条"     # 周日
                ],
                "晚餐": [
                    "蒸蛋羹+青菜",       # 周一
                    "蔬菜豆腐汤",         # 周二
                    "荞麦面配蔬菜",     # 周三
                    "冬瓜丸子汤",         # 周四
                    "紫菜蛋花汤",         # 周五
                    "青菜豆腐汤",         # 周六
                    "白萝卜炒蛋"          # 周日
                ],
                "加餐": [
                    "水煮蛋",              # 周一
                    "酸奶",                 # 周二
                    "柚子片",              # 周三
                    "核桃仁",              # 周四
                    "蓝莓酸奶",           # 周五
                    "牛奶",                 # 周六
                    "苹果片"               # 周日
                ]
            },
            "粤菜": {
                "早餐": [
                    "煎蛋三明治",         # 周一
                    "蒸蛋羹配面包",     # 周二
                    "豆浆油条",           # 周三
                    "白粥配鸡蛋",         # 周四
                    "红豆薄饼+鸡蛋",    # 周五
                    "牛奶麦片",           # 周六
                    "葱花鸡蛋饼"          # 周日
                ],
                "午餐": [
                    "清蒸鲈鱼配糙米",   # 周一
                    "白切鸡配米饭",     # 周二
                    "清炖鸡汤配饭",     # 周三
                    "蒸虾仁配糙米",     # 周四
                    "白灼菜心配鱼片", # 周五
                    "蒸水蛋配米饭",     # 周六
                    "鱼肉粥"               # 周日
                ],
                "晚餐": [
                    "冬瓜排骨汤",         # 周一
                    "蒸蛋羹+青菜",       # 周二
                    "蔬菜豆腐汤",         # 周三
                    "紫菜蛋花汤",         # 周四
                    "小白菜豆腐汤",     # 周五
                    "蒸蛋羹",             # 周六
                    "青菜瘦肉汤"          # 周日
                ],
                "加餐": [
                    "蓝莓酸奶",           # 周一
                    "牛奶",                 # 周二
                    "苹果片",              # 周三
                    "奶酪鸡蛋粥",         # 周四
                    "核桃仁",              # 周五
                    "红枣豆浆",           # 周六
                    "香蕉"                 # 周日
                ]
            },
            "清淡": {
                "早餐": [
                    "燕麦鸡蛋套餐",      # 周一
                    "牛奶燕麦",            # 周二
                    "煎蛋三明治",         # 周三
                    "红薯糙米粥",         # 周四
                    "全麦面包加鸡蛋",   # 周五
                    "豆浆加鸡蛋",         # 周六
                    "小米鸡蛋粥"          # 周日
                ],
                "午餐": [
                    "清蒸鸡胸肉",         # 周一
                    "豆腐蔬菜汤",         # 周二
                    "清蒸鲈鱼配糙米",   # 周三
                    "白煮鸡蛋配米饭", # 周四
                    "蒸虾仁配蔬菜",     # 周五
                    "清炖肉片汤",         # 周六
                    "豆腐鱼头汤"          # 周日
                ],
                "晚餐": [
                    "荞麦面配蔬菜",     # 周一
                    "蔬菜豆腐汤",         # 周二
                    "蒸蛋羹+青菜",       # 周三
                    "冬瓜排骨汤",         # 周四
                    "紫菜蛋花汤",         # 周五
                    "青菜豆腐汤",         # 周六
                    "白萝卜炒蛋"          # 周日
                ],
                "加餐": [
                    "酸奶",                 # 周一
                    "水煮蛋",              # 周二
                    "蓝莓酸奶",           # 周三
                    "牛奶",                 # 周四
                    "苹果片",              # 周五
                    "柚子片",              # 周六
                    "核桃仁"               # 周日
                ]
            }
        }

    def get_today_menu(self, cuisine_preference: str = "清淡") -> Dict:
        """获取今日菜单（包含详细重量信息）"""
        day_of_week = datetime.datetime.now().weekday()  # 0=周一, 6=周日
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        today_name = weekday_names[day_of_week]

        # 确保菜系存在
        if cuisine_preference not in self.weekly_high_quality_recipes:
            cuisine_preference = "清淡"

        recipes = self.weekly_high_quality_recipes[cuisine_preference]

        # 获取今日推荐，并添加详细重量信息
        today_menu = {
            "早餐推荐": self._get_detailed_dish_info(recipes['早餐'][day_of_week], today_name),
            "午餐推荐": self._get_detailed_dish_info(recipes['午餐'][day_of_week], today_name),
            "晚餐推荐": self._get_detailed_dish_info(recipes['晚餐'][day_of_week], today_name),
            "加餐推荐": self._get_detailed_dish_info(recipes['加餐'][day_of_week], today_name),
            "一周菜单信息": {
                "当前日期": today_name,
                "菜系风格": cuisine_preference,
                "轮换说明": "系统每天自动推荐不同菜品，确保一周不重复，包含详细重量信息",
                "一周菜单": {
                    "早餐": recipes["早餐"],
                    "午餐": recipes["午餐"],
                    "晚餐": recipes["晚餐"],
                    "加餐": recipes["加餐"]
                }
            }
        }

        return today_menu

    def _get_detailed_dish_info(self, dish_name: str, day_name: str) -> List[str]:
        """获取菜品的详细信息"""
        simple_recipe = self.simple_recipe_manager.get_recipe_by_name(dish_name)

        if simple_recipe:
            # 如果找到详细菜谱，返回格式化的详细信息
            formatted_info = self.simple_recipe_manager.format_recipe_for_display(simple_recipe)
            return [f"{dish_name} ({day_name}推荐)", "详细配方:", formatted_info]
        else:
            # 如果没有找到详细菜谱，返回基本信息
            return [f"{dish_name} ({day_name}推荐)", "（详细配方待补充）"]

    def get_weekly_menu(self, cuisine_preference: str = "清淡") -> Dict:
        """获取完整一周菜单"""
        if cuisine_preference not in self.weekly_high_quality_recipes:
            cuisine_preference = "清淡"

        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        recipes = self.weekly_high_quality_recipes[cuisine_preference]

        weekly_plan = {}
        for i, day in enumerate(weekday_names):
            weekly_plan[day] = {
                "早餐": recipes["早餐"][i],
                "午餐": recipes["午餐"][i],
                "晚餐": recipes["晚餐"][i],
                "加餐": recipes["加餐"][i]
            }

        return {
            "菜系风格": cuisine_preference,
            "一周计划": weekly_plan,
            "特色说明": "精选营养菜品，确保蛋白质充足度≥8分，营养均衡度≥8分，疾病适宜性≥9分"
        }

    def get_detailed_weekly_menu(self, cuisine_preference: str = "清淡") -> Dict:
        """获取完整一周菜单（包含详细重量信息）"""
        if cuisine_preference not in self.weekly_high_quality_recipes:
            cuisine_preference = "清淡"

        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        recipes = self.weekly_high_quality_recipes[cuisine_preference]

        detailed_weekly_plan = {}
        for i, day in enumerate(weekday_names):
            detailed_weekly_plan[day] = {
                "早餐": {
                    "菜品名称": recipes["早餐"][i],
                    "详细信息": self._get_recipe_details(recipes["早餐"][i])
                },
                "午餐": {
                    "菜品名称": recipes["午餐"][i],
                    "详细信息": self._get_recipe_details(recipes["午餐"][i])
                },
                "晚餐": {
                    "菜品名称": recipes["晚餐"][i],
                    "详细信息": self._get_recipe_details(recipes["晚餐"][i])
                },
                "加餐": {
                    "菜品名称": recipes["加餐"][i],
                    "详细信息": self._get_recipe_details(recipes["加餐"][i])
                }
            }

        return {
            "菜系风格": cuisine_preference,
            "一周详细计划": detailed_weekly_plan,
            "特色说明": "精选营养菜品，确保蛋白质充足度≥8分，营养均衡度≥8分，疾病适宜性≥9分",
            "重量说明": "包含干重、湿重、净重等详细重量信息，便于患者精确执行"
        }

    def _get_recipe_details(self, dish_name: str) -> str:
        """获取菜品详细信息"""
        simple_recipe = self.simple_recipe_manager.get_recipe_by_name(dish_name)

        if simple_recipe:
            return self.simple_recipe_manager.format_recipe_for_display(simple_recipe)
        else:
            return "详细配方待补充，请参考基础营养建议"

    def get_dish_names_for_nutrition_db(self) -> List[str]:
        """获取所有菜品名称，用于营养数据库"""
        all_dishes = set()
        for cuisine in self.weekly_high_quality_recipes.values():
            for meal_type in cuisine.values():
                all_dishes.update(meal_type)
        return list(all_dishes)