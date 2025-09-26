# 患者健康顾问知识库文档说明

## 📚 知识库文件组织

### 核心文件结构
```
/Yilan/
├── core_prompt_advanced.md             # 🎯 核心提示词(高级版v2) ⭐更新
├── patiens_prompts.md                  # 📋 完整系统设计(1368行)
├── README_knowledge_base.md            # 📖 本说明文档
├── README.md                           # 🏗️ 系统架构说明 ⭐新增
├── 
├── 知识库模块:
├── knowledge_base_food_database_v2.json # 🍎 食物营养数据库v2 ⭐升级
├── knowledge_base_portion_reference.json # 📏 食物份量参考 
├── knowledge_base_boundary_handling.json # 🚫 边界问题处理
├── knowledge_base_disease_management.json # 🏥 疾病管理指南 ⭐升级
├── knowledge_base_personalization_rules.json # 👤 个性化规则 ⭐升级
├── knowledge_base_exercises.json       # 🏃‍♀️ 运动知识库 ⭐新增
├── template_user_health_profile.json   # 👤 用户档案模板 ⭐新增
├── 
├── 辅助文档:
├── patient_health_advisor.md           # 💝 系统设计理念
├── usage_examples.md                   # 💬 使用示例对比
└── system_architecture.md             # 🏗️ 技术架构建议
```

## 🎯 如何使用这些文档

### 方案1: 直接使用核心提示词
**文件**: `core_prompt_advanced.md` ⭐更新
**适用**: 快速部署，功能完整，支持情绪识别和记忆
**大小**: ~112行，包含完整示例
**包含**: 所有核心功能+详细示例+边界处理

### 方案2: 模块化系统开发  
**主文件**: `core_prompt_advanced.md` (核心提示词)
**数据库**: 
- `knowledge_base_food_database_v2.json` (食物营养数据v2) ⭐升级
- `knowledge_base_personalization_rules.json` (个性化规则) ⭐升级
- `knowledge_base_exercises.json` (运动知识库) ⭐新增
**指南**: `knowledge_base_disease_management.json` (疾病管理) ⭐升级

### 方案3: 完整系统参考
**文件**: `patiens_prompts.md` (1368行完整版)
**适用**: 产品设计、培训、开发规格
**内容**: 所有功能的详细说明和示例

## 📊 数据库使用说明

### 食物数据库 (knowledge_base_food_database.json)
```javascript
// 使用示例
const foodData = foodDatabase.grains.white_rice;
console.log(`${foodData.name}: ${foodData.calories_per_100g}kcal, GI=${foodData.gi}`);
// 输出: 白米饭: 116kcal, GI=83
```

### 个性化规则 (knowledge_base_personalization_rules.json)
```javascript
// 根据年龄获取血糖目标
const elderlyRules = personalizationRules.age_based_rules.elderly;
console.log(`老年人HbA1c目标: ${elderlyRules.glucose_target.hba1c}`);
// 输出: 老年人HbA1c目标: 7.5-8.5%
```

## 🔄 文档关系图

```
core_prompt_simplified.md (实际使用的提示词)
     ↓ 引用
knowledge_base_*.json/md (结构化数据和规则)
     ↓ 详细展开  
patiens_prompts.md (完整设计文档1368行)
     ↓ 技术实现
system_architecture.md (架构建议)
```

## 🚀 快速开始

### 步骤1: 直接使用
复制 `core_prompt_simplified.md` 内容到你的AI系统

### 步骤2: 数据增强  
读取 `knowledge_base_food_database.json` 提供精确营养数据

### 步骤3: 个性化
使用 `knowledge_base_personalization_rules.json` 实现个性化建议

### 步骤4: 完整功能
参考 `patiens_prompts.md` 添加高级功能

## ⚠️ 重要功能说明

### 🚨 食物份量确认机制
**核心原则**：绝不假设食物份量，必须用户确认后才分析！

**为什么重要**：
- 食物营养分析的准确性100%依赖于准确份量
- 1个苹果可能是80g-200g，卡路里相差2.5倍
- 错误份量导致错误的健康建议

**如何实现**：
1. 用户说"吃了苹果" → AI立即询问"多少量？"
2. 提供视觉参考："小(鸡蛋大)、中(网球大)、大(垒球大)"
3. 用户回答"中等" → AI直接按150g苹果进行营养分析
4. **不进行二次确认**，直接展示卡路里、GI、运动消耗结果

### 🚫 非健康问题边界处理
**核心原则**：礼貌拒绝技术问题，引导回健康话题

**标准回复模板**：
- 用户问"你是什么大模型？" 
- AI回复"这个问题我不清楚，不属于健康相关问题。我是您的健康顾问，专门帮助您管理血糖、饮食和运动。有什么健康方面的问题需要咨询吗？"

## ❓ 常见问题

**Q: 为什么有这么多文件？**
A: 原本1368行的"提示词"实际上是完整系统设计，我们拆分成了实用的模块。

**Q: 我只想要一个简单的提示词，用哪个？**  
A: 使用 `core_prompt_advanced.md`，包含完整功能，约112行，支持情绪识别和历史记忆。

**Q: 食物份量确认是否必要？**
A: ⚡**非常必要！**这是食物量化分析准确性的基础，不能省略。

**Q: 用户问技术问题怎么处理？**
A: 统一回复"这个问题我不清楚，不属于健康相关问题"，然后引导到健康话题。

**Q: 我想开发完整的健康顾问系统，怎么办？**
A: 参考 `system_architecture.md` 的模块化建议，使用所有知识库文件。

**Q: 1368行的原文件还有用吗？**
A: 有用！它是完整的产品设计文档，包含所有细节和示例，适合产品设计和开发参考。

## 📈 版本说明

- **v1.0** (patiens_prompts.md): 完整设计文档，1368行
- **v2.0** (core_prompt_simplified.md): 精简核心提示词，50行  
- **v2.1** (knowledge_base_*.json): 结构化数据库
- **v2.2** (README_knowledge_base.md): 使用说明文档
- **v2.3** (boundary_handling): 新增非健康问题边界处理
- **v3.0** (core_prompt_advanced.md): 高级版，情绪识别+记忆 ⭐当前版本
- **v3.1** (knowledge_base_v2): 知识库全面升级，JSON格式统一

---
*现在"详细知识库和管理指南参见完整版文档"有了明确的位置！*