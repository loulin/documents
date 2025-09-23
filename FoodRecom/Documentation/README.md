# 个性化中式营养建议系统

## 系统概述

这是一个基于现代营养学和循证医学的综合性中式营养管理系统。系统具备以下核心能力：

- 🧮 **精确计算**: 基于Harris-Benedict公式计算BMR和TDEE
- 🎯 **目标导向**: 根据健康目标和疾病状况调整营养方案
- 🏥 **循证医学**: 结合实验室指标提供科学建议
- 🍽️ **饮食偏好**: 完整的个人偏好管理系统
- 🍚 **GI数据库**: 集成95种食物的血糖生成指数数据
- 📊 **可视化**: 营养成分雷达图和健康指标分析
- 📝 **详细报告**: 生成完整的markdown和PDF格式报告
- 🏮 **中式菜谱**: 集成111道经典中式菜谱，覆盖8大菜系
- 🏥 **疾病支持**: 支持35+种疾病的专业营养管理

## 功能特点

### 🔍 用户画像分析
- **基本信息**: 年龄、性别、身高、体重、活动水平
- **健康指标**: BMI、血糖、血压、血脂等实验室检查
- **饮食偏好**: 偏好菜系、不喜食物、饮食限制、辣度承受、烹饪偏好
- **安全信息**: 食物过敏史、药物冲突、宗教饮食限制

### 🎯 健康目标支持
- **体重管理**: 减重、增重、维持体重、增肌
- **慢病管理**: 血糖控制、血压控制、血脂控制
- **营养优化**: 营养均衡、特殊营养需求

### 🍽️ 个性化食谱生成
- **智能搭配**: 根据营养目标自动搭配食物
- **分餐设计**: 早餐、午餐、晚餐、加餐的合理分配
- **营养计算**: 精确计算每餐和全天营养摄入

### 📊 科学营养分析
- **热量平衡**: BMR/TDEE计算，目标热量设定
- **宏量配比**: 碳水化合物、蛋白质、脂肪的科学配比
- **微量元素**: 纤维、钠、糖等微量营养素监控

## 使用方法

### 1. 综合营养系统使用

```python
from Core_Systems.integrated_nutrition_system_v2 import IntegratedNutritionSystemV2, PatientProfile

# 创建综合营养系统
system = IntegratedNutritionSystemV2()

# 创建患者档案（包含饮食偏好）
patient = PatientProfile(
    name="张先生",
    age=45,
    gender="男",
    height=175,
    weight=75,
    diagnosed_diseases=["糖尿病", "高血压"],

    # 饮食偏好设置
    preferred_cuisines=["川菜", "清淡"],
    disliked_foods=["海鲜", "动物内脏"],
    dietary_restrictions=["低盐", "低糖"],
    spice_tolerance="微辣",
    cooking_preferences=["蒸", "煮", "炖"],
    allergies=["虾", "蟹"]
)

# 生成个性化推荐
recommendations = system._recommend_recipes(patient)

# 生成完整报告
report = system.generate_comprehensive_report(patient)

# 生成营养雷达图
chart_file = system.create_nutrition_radar_chart("麻婆豆腐", patient_diseases=patient.diagnosed_diseases)
```

### 2. GI数据库专用系统

```python
from Core_Systems.gi_database_integration_v2 import GIDatabaseSystemV2

# 创建GI数据库系统
gi_system = GIDatabaseSystemV2()

# 生成糖尿病膳食计划
diabetes_plan = gi_system.generate_diabetes_meal_plan(target_gl=15.0, patient=patient)

# 获取个性化GI推荐
gi_recommendations = gi_system.generate_personalized_gi_recommendations(patient)
```

### 3. 饮食偏好配置

```python
# 完整的饮食偏好示例
patient_preferences = {
    "preferred_cuisines": ["川菜", "粤菜", "清淡"],     # 偏好菜系
    "disliked_foods": ["海鲜", "动物内脏", "羊肉"],   # 不喜欢的食物
    "dietary_restrictions": ["素食", "低盐", "低糖"],  # 饮食限制
    "spice_tolerance": "微辣",                        # 辣度承受
    "cooking_preferences": ["蒸", "煮", "炖", "凉拌"], # 烹饪偏好
    "allergies": ["花生", "虾", "蟹"]                  # 过敏史
}

# 创建带偏好的患者档案
patient = PatientProfile(
    name="患者姓名",
    # ... 基本信息 ...
    **patient_preferences
)
```

### 4. 系统演示

```python
# 运行完整功能演示
python3 comprehensive_system_demo.py

# 运行饮食偏好案例
python3 饮食偏好案例示例.py
```

## 系统架构

### 核心类设计

1. **UserProfile**: 用户档案类
   - 基本信息（年龄、性别、身高、体重）
   - 活动水平和健康目标
   - 实验室检查指标
   - 个人偏好和限制

2. **Food & NutritionInfo**: 食物和营养信息类
   - 食物基本信息和分类
   - 每100g营养成分
   - 升糖指数和过敏原信息

3. **Meal**: 餐食类
   - 食物组合和分量
   - 营养计算功能

4. **PersonalizedFoodRecommender**: 核心推荐引擎
   - BMR/TDEE计算
   - 营养需求分析
   - 食物筛选和搭配
   - 报告生成

### 算法逻辑

1. **代谢率计算**
   ```
   BMR = Harris-Benedict公式
   TDEE = BMR × 活动系数
   目标热量 = TDEE ± 调整值（基于健康目标）
   ```

2. **营养素配比**
   ```
   糖尿病: 碳水40% + 蛋白质25% + 脂肪35%
   减重: 碳水35% + 蛋白质30% + 脂肪35%
   增肌: 碳水45% + 蛋白质30% + 脂肪25%
   标准: 碳水50% + 蛋白质20% + 脂肪30%
   ```

3. **食物筛选**
   - 过敏原排除
   - 饮食限制过滤
   - 偏好匹配
   - 营养目标导向选择

## 报告内容

生成的markdown报告包含：

### 📋 基本信息
- 用户基本资料
- 健康分析（BMI、血糖、血压等）
- 健康目标和饮食限制

### 🎯 营养目标
- 基础代谢率和总消耗
- 目标热量摄入
- 宏量营养素分配

### 🍽️ 个性化食谱
- 四餐详细食谱（早餐、午餐、晚餐、加餐）
- 食物重量和营养含量表格
- 每餐营养合计

### 📊 营养总结
- 全天营养摄入总结
- 目标达成率分析
- 营养素充足性评估

### 💡 专业建议
- 用餐建议和食物选择指导
- 针对性健康建议
- 注意事项提醒

## 技术特性

### 🔬 科学性
- 基于Harris-Benedict公式的BMR计算
- 参考中国居民膳食指南的营养推荐
- 遵循现代营养学和循证医学原理
- 集成国际权威营养组织建议

### 🎯 个性化
- 多维度用户画像
- 智能算法匹配
- 动态调整机制

### 📱 易用性
- 简洁的API设计
- 清晰的配置模板
- 详细的使用文档

### 🔧 可扩展性
- 模块化设计
- 易于添加新食物
- 支持自定义算法

## 适用人群

- 🏥 **医疗机构**: 营养科、内分泌科、心血管科
- 🏋️ **健身行业**: 私人教练、营养师、健身房
- 👨‍⚕️ **营养师**: 临床营养师、公共营养师
- 🏢 **企业健康**: 员工健康管理、体检中心
- 👥 **个人用户**: 有特殊营养需求的个人

## 注意事项

⚠️ **免责声明**:
- 本系统生成的建议仅供参考
- 具体饮食方案请咨询专业营养师或医生
- 特殊疾病患者需在医生指导下使用
- 系统不能替代专业医疗诊断

## 版本信息

- **当前版本**: v1.0
- **最后更新**: 2025年
- **开发者**: Claude Code
- **许可证**: MIT

---

*如有问题或建议，请联系开发团队*