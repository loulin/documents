# 健康顾问系统集成指南

## 🏗️ 系统整体架构

```
用户输入 → 边界处理 → 知识库检索 → 个性化规则 → 动态提示词 → 大模型 → 用户回复
    ↓            ↓            ↓            ↓            ↓          ↓
用户档案    健康分类    相关知识      条件匹配      上下文增强   智能回答
```

## 📚 核心组件说明

### 1. **核心提示词** (`core_prompt_advanced.md`)
- **作用**: 系统基础人格和行为准则
- **内容**: 112行的核心逻辑，包含思考链、边界规则、回复结构
- **使用**: 每次调用的固定基础模板

### 2. **知识库系统** (6个JSON文件)
- **边界处理**: `knowledge_base_boundary_handling.json` - 问题分类
- **疾病管理**: `knowledge_base_disease_management.json` - 症状处理  
- **运动指导**: `knowledge_base_exercises.json` - 运动建议
- **用药管理**: `knowledge_base_medication_management.json` - 药物指导
- **个性化规则**: `knowledge_base_personalization_rules.json` - 条件逻辑
- **睡眠管理**: `knowledge_base_sleep_management.json` - 睡眠指导
- **食物数据库**: `knowledge_base_food_database_v2.json` - 营养数据

### 3. **用户档案** (`template_user_health_profile.json`)
- **基础信息**: 年龄、性别、疾病类型、用药情况
- **健康记录**: 血糖、血压、运动、饮食、睡眠、症状日志

## 🔧 技术实现方案

### 方案A: RAG检索增强 (推荐)

```python
class HealthAdvisorSystem:
    def __init__(self):
        self.core_prompt = load_core_prompt()
        self.knowledge_bases = load_all_knowledge_bases()
        self.user_profiles = {}
        
    async def process_user_input(self, user_id: str, message: str):
        # 1. 加载用户档案
        user_profile = self.get_user_profile(user_id)
        
        # 2. 边界处理 - 判断问题类型
        question_type = self.classify_question(message)
        
        if question_type == "non_health":
            return self.handle_non_health_question(message)
            
        # 3. 知识库检索
        relevant_knowledge = self.retrieve_knowledge(message, user_profile)
        
        # 4. 个性化规则匹配
        personalization_rules = self.match_personalization_rules(
            message, user_profile
        )
        
        # 5. 动态提示词构建
        dynamic_prompt = self.build_dynamic_prompt(
            self.core_prompt,
            relevant_knowledge,
            personalization_rules,
            user_profile,
            message
        )
        
        # 6. 大模型调用
        response = await self.call_llm(dynamic_prompt)
        
        # 7. 更新用户档案
        self.update_user_profile(user_id, message, response)
        
        return response
```

### 关键实现函数

#### 1. **问题分类函数**
```python
def classify_question(self, message: str) -> str:
    """使用边界处理知识库判断问题类型"""
    boundary_kb = self.knowledge_bases["boundary_handling"]
    
    # 检查健康相关表达
    health_patterns = boundary_kb["health_related_phrases"]
    for category, data in health_patterns.items():
        for pattern in data["patterns"]:
            if pattern in message:
                return "health_related"
    
    # 检查非健康问题
    non_health_patterns = boundary_kb["non_health_questions"]
    for category, data in non_health_patterns.items():
        for pattern in data["patterns"]:
            if pattern in message:
                return "non_health"
                
    return "health_related"  # 默认视为健康相关
```

#### 2. **知识检索函数**
```python
def retrieve_knowledge(self, message: str, user_profile: dict) -> dict:
    """根据用户输入和档案检索相关知识"""
    relevant_knowledge = {}
    
    # 症状相关检索
    if any(symptom in message for symptom in ["头晕", "出汗", "心慌"]):
        relevant_knowledge["symptoms"] = self.knowledge_bases["disease_management"]
    
    # 用药相关检索  
    if any(med_word in message for med_word in ["忘记吃药", "药物"]):
        relevant_knowledge["medication"] = self.knowledge_bases["medication_management"]
        
    # 运动相关检索
    if any(exercise_word in message for exercise_word in ["运动", "锻炼"]):
        relevant_knowledge["exercise"] = self.knowledge_bases["exercises"]
        
    # 睡眠相关检索
    if any(sleep_word in message for sleep_word in ["睡眠", "睡不着"]):
        relevant_knowledge["sleep"] = self.knowledge_bases["sleep_management"]
        
    # 食物相关检索
    food_kb = self.knowledge_bases["food_database"]
    for food in food_kb:
        if food["name"] in message:
            relevant_knowledge["food"] = food
            break
            
    return relevant_knowledge
```

#### 3. **个性化规则匹配**
```python
def match_personalization_rules(self, message: str, user_profile: dict) -> list:
    """匹配适用的个性化规则"""
    matched_rules = []
    rules_kb = self.knowledge_bases["personalization_rules"]
    
    for rule in rules_kb:
        if self.evaluate_rule_condition(rule["condition"], message, user_profile):
            matched_rules.append(rule["action"])
            
    return matched_rules
```

#### 4. **动态提示词构建**
```python
def build_dynamic_prompt(self, core_prompt: str, knowledge: dict, 
                        rules: list, user_profile: dict, message: str) -> str:
    """构建动态提示词"""
    
    # 基础提示词
    dynamic_prompt = core_prompt
    
    # 添加用户个人信息
    if user_profile.get("age"):
        dynamic_prompt += f"\n\n用户基本信息：年龄{user_profile['age']}岁"
        
    if user_profile.get("disease_ids"):
        diseases = ", ".join(user_profile["disease_ids"])
        dynamic_prompt += f"，疾病：{diseases}"
    
    # 注入相关知识
    for knowledge_type, data in knowledge.items():
        dynamic_prompt += f"\n\n## {knowledge_type}相关知识：\n{json.dumps(data, ensure_ascii=False, indent=2)}"
    
    # 应用个性化规则
    for rule_action in rules:
        if "inject_to_prompt" in rule_action:
            for instruction in rule_action["inject_to_prompt"]:
                dynamic_prompt += f"\n重要提示：{instruction}"
    
    # 添加用户当前输入
    dynamic_prompt += f"\n\n用户当前问题：{message}"
    dynamic_prompt += f"\n\n请根据以上信息，按照标准回复结构给出专业、温暖的健康建议。"
    
    return dynamic_prompt
```

## 🚀 部署实现步骤

### 第1步：数据预处理
```python
# 预加载所有知识库
knowledge_bases = {}
kb_files = [
    "knowledge_base_boundary_handling.json",
    "knowledge_base_disease_management.json", 
    "knowledge_base_exercises.json",
    "knowledge_base_medication_management.json",
    "knowledge_base_personalization_rules.json",
    "knowledge_base_sleep_management.json",
    "knowledge_base_food_database_v2.json"
]

for kb_file in kb_files:
    with open(f"docs/Yilan/{kb_file}", "r", encoding="utf-8") as f:
        kb_name = kb_file.replace("knowledge_base_", "").replace(".json", "")
        knowledge_bases[kb_name] = json.load(f)
```

### 第2步：接口服务
```python
from fastapi import FastAPI
app = FastAPI()

health_advisor = HealthAdvisorSystem()

@app.post("/chat")
async def chat_endpoint(user_id: str, message: str):
    try:
        response = await health_advisor.process_user_input(user_id, message)
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### 第3步：前端集成
```javascript
// 前端调用示例
async function sendHealthQuery(message) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: getCurrentUserId(),
            message: message
        })
    });
    
    const result = await response.json();
    return result.response;
}
```

## 📊 系统工作流程示例

### 用户输入："头晕了"

```
1. 边界处理 ✅
   - 匹配到 "physical_symptoms" → "头晕" 
   - 分类为：health_related

2. 知识检索 ✅
   - disease_management.json → 低血糖症状处理
   - 匹配症状："头晕" → 轻度低血糖可能

3. 个性化规则 ✅
   - RULE_002: 症状严重程度评估规则
   - 用户用药情况：胰岛素 → 高风险提醒

4. 动态提示词 ✅
   core_prompt + 
   "用户描述了头晕症状，需要立即评估严重程度" +
   低血糖症状知识 +
   "如果用户使用胰岛素，特别关注低血糖风险"

5. 大模型生成 ✅
   "头晕症状需要重视，可能与血糖状况有关..."
```

### 用户输入："你用什么AI？"

```
1. 边界处理 ✅
   - 匹配到 "ai_technical" → "什么AI"
   - 分类为：non_health

2. 标准回复 ✅
   "这个问题我不清楚，不属于健康相关问题。
   我是您的健康顾问，专门帮助您管理血糖、饮食和运动。
   有什么健康方面的问题需要咨询吗？"
```

## 🎯 优化建议

### 性能优化
1. **知识库索引化** - 使用向量数据库加速检索
2. **缓存机制** - 缓存用户档案和常用知识
3. **并行处理** - 多个知识库并行检索

### 功能增强
1. **学习机制** - 根据用户反馈优化回答
2. **多轮对话** - 保持上下文连续性
3. **实时数据** - 集成血糖仪等设备数据

## 📋 部署清单

- [ ] 环境配置（Python 3.8+, FastAPI, 大模型API）
- [ ] 知识库预加载和索引  
- [ ] 用户档案数据库设计
- [ ] API接口开发和测试
- [ ] 前端界面集成
- [ ] 系统监控和日志
- [ ] 安全认证和数据保护

这个整合方案将提示词、知识库和大模型无缝连接，形成完整的智能健康顾问系统！