# 患者健康顾问AI系统 - 主文档

## 🎯 系统概述

本系统是一个先进的AI健康顾问，通过大语言模型为App用户提供个性化、专业化的健康知识服务。系统具备情绪识别、历史记忆、食物量化分析、边界处理等完整功能。

---

## 🏗️ 核心架构三要素

### 1. 🧠 大脑：高级提示词 (`core_prompt_advanced.md`)
**作用**: AI的"操作系统"和"性格设定"
- 定义AI的性格（专业、温暖、高情商）
- 思考流程（评估情绪、回顾历史、识别任务、检查安全）
- 标准对话结构和边界处理
- 食物份量确认和营养分析功能

### 2. 📚 静态图书馆：核心知识库 (JSON文件)
**作用**: AI的"知识储备"，确保专业性
- `knowledge_base_food_database_v2.json`: 深度食物营养库
- `knowledge_base_disease_management.json`: 常见疾病饮食原则
- `knowledge_base_exercises.json`: 科学运动信息库
- `knowledge_base_personalization_rules.json`: 个性化决策规则引擎
- `knowledge_base_portion_reference.json`: 食物份量参考
- `knowledge_base_boundary_handling.json`: 非健康问题边界处理

### 3. 👤 动态日志本：用户健康档案 (`template_user_health_profile.json`)
**作用**: 实现真正"个性化"的关键
- 记录用户持续变化的健康指标（血糖、血压等）
- 支持个性化规则引擎的条件判断
- 实现从"通用顾问"到"私人管家"的升级

---

## ⚡ 快速开始

### 🚀 方案1: 直接使用 (推荐)
**文件**: `core_prompt_advanced.md`
**特点**: 包含完整功能，支持情绪识别和记忆，约112行
**适用**: 快速部署，功能完整

### 🔧 方案2: 模块化开发
**主文件**: `core_prompt_advanced.md` (核心提示词)
**数据支持**: 使用5个knowledge_base JSON文件提供数据
**动态档案**: 集成`template_user_health_profile.json`实现个性化

### 📋 方案3: 完整系统参考
**文件**: `patiens_prompts.md` (1368行完整版)
**适用**: 产品设计、培训、开发规格参考

---

## 🔄 工作流程

当用户发起查询时：

```
用户问题 → 系统整合 → AI处理 → 个性化回复
           ↓
    ┌─────────────────┐
    │ 核心提示词      │ ← 控制逻辑和对话结构
    │ +              │
    │ 相关知识库数据   │ ← 专业事实依据  
    │ +              │
    │ 用户健康档案    │ ← 个性化参数
    └─────────────────┘
           ↓
       大语言模型推理
           ↓
    专业、个性化、温暖的回复
```

---

## ✨ 核心功能特性

### 🍎 食物量化分析
- **份量确认**: 必须确认准确份量后分析
- **营养计算**: 精确计算卡路里、GI、GL、运动消耗
- **健康评估**: 🟢绿灯/🟡黄灯/🔴红灯分级
- **替代建议**: 提供更健康的食物选择

### 👤 个性化服务
- **年龄分层**: 青少年/成年/老年不同建议
- **疾病适配**: 1型/2型/妊娠糖尿病差异化管理
- **情绪识别**: 根据用户情绪调整语气和建议
- **历史记忆**: 记住近期互动，提供连续性服务

### 🚫 安全边界
- **非健康问题**: 统一拒绝技术/娱乐问题，引导回健康话题
- **紧急情况**: 识别危险症状，强烈建议就医
- **医疗边界**: 明确不替代医生诊断和治疗

---

## 📊 版本历史

- **v3.1** (当前): 知识库全面升级，JSON格式统一，个性化规则引擎
- **v3.0**: 高级版提示词，情绪识别+历史记忆功能  
- **v2.3**: 边界处理功能，拒绝非健康问题
- **v2.0-v2.2**: 模块化架构，功能拆分
- **v1.0**: 完整设计文档（1368行原版）

---

## 📚 文档导航

### 🎯 核心使用文档
- **`core_prompt_advanced.md`** - 高级版提示词（直接使用）
- **`README_knowledge_base.md`** - 详细的知识库说明文档
- **`template_user_health_profile.json`** - 用户档案模板

### 🏗️ 系统设计文档  
- **`README.md`** - 系统架构概览
- **`system_architecture.md`** - 技术架构建议
- **`patiens_prompts.md`** - 完整设计规格（1368行）

### 🔧 知识库文件
- **`knowledge_base_food_database_v2.json`** - 食物营养数据
- **`knowledge_base_personalization_rules.json`** - 个性化规则
- **`knowledge_base_disease_management.json`** - 疾病管理
- **`knowledge_base_exercises.json`** - 运动知识库
- **`knowledge_base_portion_reference.json`** - 份量参考  
- **`knowledge_base_boundary_handling.json`** - 边界处理

---

## ❓ 常见问题

**Q: 我想快速部署，用哪个文件？**
A: 直接使用 `core_prompt_advanced.md`，功能完整，开箱即用。

**Q: 如何实现个性化？**  
A: 使用 `template_user_health_profile.json` 记录用户数据，结合 `knowledge_base_personalization_rules.json` 规则引擎。

**Q: 食物分析准确吗？**
A: 系统强制要求份量确认，避免假设，确保分析精度。基于专业营养数据库。

**Q: 如何处理非健康问题？**
A: 统一回复"不清楚，不属于健康问题"，然后引导回健康话题。

**Q: 系统安全吗？** 
A: 有完整的边界处理和紧急情况识别，明确医疗边界，不替代医生。

---

*🏆 这是一个完整的、专业的、安全的AI健康顾问系统！*