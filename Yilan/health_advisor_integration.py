#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康顾问系统集成示例
整合提示词、知识库和大模型的完整实现
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class HealthAdvisorSystem:
    """健康顾问系统主类"""
    
    def __init__(self, knowledge_base_path: str = "docs/Yilan"):
        """
        初始化系统
        
        Args:
            knowledge_base_path: 知识库文件路径
        """
        self.kb_path = knowledge_base_path
        self.knowledge_bases = {}
        self.core_prompt = ""
        self.user_profiles = {}
        
        # 加载所有组件
        self._load_core_prompt()
        self._load_knowledge_bases()
        
    def _load_core_prompt(self):
        """加载核心提示词"""
        prompt_file = os.path.join(self.kb_path, "core_prompt_advanced.md")
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.core_prompt = f.read()
                print("✅ 核心提示词加载成功")
        except FileNotFoundError:
            print(f"❌ 核心提示词文件未找到: {prompt_file}")
            
    def _load_knowledge_bases(self):
        """加载所有知识库"""
        kb_files = {
            "boundary": "knowledge_base_boundary_handling.json",
            "disease": "knowledge_base_disease_management.json", 
            "exercise": "knowledge_base_exercises.json",
            "medication": "knowledge_base_medication_management.json",
            "personalization": "knowledge_base_personalization_rules.json",
            "sleep": "knowledge_base_sleep_management.json",
            "food": "knowledge_base_food_database_v2.json"
        }
        
        for kb_name, filename in kb_files.items():
            filepath = os.path.join(self.kb_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.knowledge_bases[kb_name] = json.load(f)
                    print(f"✅ {kb_name}知识库加载成功")
            except FileNotFoundError:
                print(f"❌ 知识库文件未找到: {filepath}")
                self.knowledge_bases[kb_name] = {}
                
    def classify_question(self, message: str) -> str:
        """
        问题分类：判断是健康相关还是非健康问题
        
        Args:
            message: 用户输入
            
        Returns:
            "health_related" 或 "non_health"
        """
        if "boundary" not in self.knowledge_bases:
            return "health_related"  # 默认健康相关
            
        boundary_kb = self.knowledge_bases["boundary"]
        
        # 检查健康相关表达
        health_patterns = boundary_kb.get("health_related_phrases", {})
        for category_data in health_patterns.values():
            patterns = category_data.get("patterns", [])
            for pattern in patterns:
                if pattern in message:
                    print(f"🟢 健康相关问题识别: {pattern}")
                    return "health_related"
        
        # 检查非健康问题
        non_health_patterns = boundary_kb.get("non_health_questions", {})
        for category_data in non_health_patterns.values():
            patterns = category_data.get("patterns", [])
            for pattern in patterns:
                if pattern in message:
                    print(f"🔴 非健康问题识别: {pattern}")
                    return "non_health"
                    
        return "health_related"  # 默认健康相关
        
    def handle_non_health_question(self, message: str) -> str:
        """处理非健康相关问题"""
        if "boundary" not in self.knowledge_bases:
            return "抱歉，我专注于健康相关问题的咨询。"
            
        boundary_kb = self.knowledge_bases["boundary"]
        responses = boundary_kb.get("standard_responses", {})
        
        # 根据问题类型返回标准回复
        if any(pattern in message for pattern in ["大模型", "AI", "技术"]):
            return responses.get("ai_technical", {}).get("response", "") + "\n\n" + \
                   responses.get("ai_technical", {}).get("redirect", "")
        
        return responses.get("general_non_health", {}).get("response", "") + "\n\n" + \
               responses.get("general_non_health", {}).get("redirect", "")
    
    def retrieve_knowledge(self, message: str, user_profile: Dict = None) -> Dict[str, Any]:
        """
        知识检索：根据用户输入检索相关知识
        
        Args:
            message: 用户输入
            user_profile: 用户档案
            
        Returns:
            相关知识字典
        """
        relevant_knowledge = {}
        
        # 症状相关检索
        symptom_keywords = ["头晕", "出汗", "心慌", "手抖", "视力模糊", "胸闷", "恶心", "口渴", "尿频"]
        if any(keyword in message for keyword in symptom_keywords):
            relevant_knowledge["symptoms"] = self.knowledge_bases.get("disease", [])
            print("🔍 检索到症状相关知识")
        
        # 用药相关检索  
        medication_keywords = ["忘记吃药", "药物", "副作用", "胰岛素", "二甲双胍", "降糖药"]
        if any(keyword in message for keyword in medication_keywords):
            relevant_knowledge["medication"] = self.knowledge_bases.get("medication", [])
            print("🔍 检索到用药相关知识")
            
        # 运动相关检索
        exercise_keywords = ["运动", "锻炼", "散步", "跑步", "游泳", "健身", "刚运动完"]
        if any(keyword in message for keyword in exercise_keywords):
            relevant_knowledge["exercise"] = self.knowledge_bases.get("exercise", [])
            print("🔍 检索到运动相关知识")
            
        # 睡眠相关检索
        sleep_keywords = ["睡眠", "睡不着", "失眠", "起床", "晚安", "熬夜"]
        if any(keyword in message for keyword in sleep_keywords):
            relevant_knowledge["sleep"] = self.knowledge_bases.get("sleep", {})
            print("🔍 检索到睡眠相关知识")
            
        # 食物相关检索
        if "food" in self.knowledge_bases:
            food_db = self.knowledge_bases["food"]
            for food_item in food_db:
                if food_item.get("name", "") in message:
                    relevant_knowledge["food"] = food_item
                    print(f"🔍 检索到食物知识: {food_item.get('name')}")
                    break
                    
        return relevant_knowledge
    
    def match_personalization_rules(self, message: str, user_profile: Dict = None) -> List[Dict]:
        """
        个性化规则匹配
        
        Args:
            message: 用户输入
            user_profile: 用户档案
            
        Returns:
            匹配的规则列表
        """
        if "personalization" not in self.knowledge_bases:
            return []
            
        matched_rules = []
        rules = self.knowledge_bases["personalization"]
        
        for rule in rules:
            rule_id = rule.get("rule_id", "")
            condition = rule.get("condition", {})
            
            # 简化的规则匹配逻辑
            if "user_input" in condition:
                contains_condition = condition["user_input"]
                if contains_condition.get("operator") == "contains" or "contains" in str(condition):
                    patterns = contains_condition.get("value", [])
                    if isinstance(patterns, str):
                        patterns = [patterns]
                    
                    for pattern in patterns:
                        if pattern in message:
                            matched_rules.append(rule.get("action", {}))
                            print(f"✅ 匹配个性化规则: {rule_id}")
                            break
                            
        return matched_rules
    
    def build_dynamic_prompt(self, message: str, knowledge: Dict, rules: List, user_profile: Dict = None) -> str:
        """
        构建动态提示词
        
        Args:
            message: 用户输入
            knowledge: 检索到的知识
            rules: 匹配的个性化规则
            user_profile: 用户档案
            
        Returns:
            完整的动态提示词
        """
        # 基础提示词
        dynamic_prompt = self.core_prompt
        
        # 添加用户信息（如果有）
        if user_profile:
            dynamic_prompt += "\\n\\n## 用户档案信息：\\n"
            if user_profile.get("age"):
                dynamic_prompt += f"年龄：{user_profile['age']}岁\\n"
            if user_profile.get("disease_ids"):
                dynamic_prompt += f"疾病：{', '.join(user_profile['disease_ids'])}\\n"
        
        # 注入相关知识
        if knowledge:
            dynamic_prompt += "\\n\\n## 相关专业知识：\\n"
            for kb_type, kb_data in knowledge.items():
                if kb_data:  # 确保知识不为空
                    dynamic_prompt += f"### {kb_type}知识：\\n"
                    # 简化知识展示，避免过长
                    if isinstance(kb_data, dict):
                        dynamic_prompt += f"{json.dumps(kb_data, ensure_ascii=False, indent=2)[:500]}...\\n"
                    elif isinstance(kb_data, list) and kb_data:
                        dynamic_prompt += f"{json.dumps(kb_data[0], ensure_ascii=False, indent=2)[:500]}...\\n"
        
        # 应用个性化规则
        if rules:
            dynamic_prompt += "\\n\\n## 个性化指导：\\n"
            for rule_action in rules:
                if "inject_to_prompt" in rule_action:
                    for instruction in rule_action["inject_to_prompt"]:
                        dynamic_prompt += f"- {instruction}\\n"
        
        # 添加用户当前问题
        dynamic_prompt += f"\\n\\n## 用户当前问题：\\n{message}"
        dynamic_prompt += "\\n\\n请根据以上信息，按照标准回复结构（🤗 理解确认 → 💡 专业分析 → 📋 具体建议 → ⚠️ 注意事项 → 💪 鼓励支持）给出专业、温暖的健康建议。"
        
        return dynamic_prompt
    
    def process_user_input(self, message: str, user_id: str = "default", user_profile: Dict = None) -> Dict[str, Any]:
        """
        处理用户输入的主函数
        
        Args:
            message: 用户输入
            user_id: 用户ID  
            user_profile: 用户档案
            
        Returns:
            处理结果字典
        """
        print(f"\\n🔄 开始处理用户输入: {message}")
        print("=" * 50)
        
        # 1. 问题分类
        question_type = self.classify_question(message)
        print(f"📋 问题分类: {question_type}")
        
        if question_type == "non_health":
            response = self.handle_non_health_question(message)
            return {
                "type": "non_health",
                "response": response,
                "processing_steps": ["问题分类", "标准回复"]
            }
        
        # 2. 知识检索
        relevant_knowledge = self.retrieve_knowledge(message, user_profile)
        print(f"📚 检索到知识类别: {list(relevant_knowledge.keys())}")
        
        # 3. 个性化规则匹配
        personalization_rules = self.match_personalization_rules(message, user_profile)
        print(f"⚙️ 匹配到规则数量: {len(personalization_rules)}")
        
        # 4. 构建动态提示词
        dynamic_prompt = self.build_dynamic_prompt(message, relevant_knowledge, personalization_rules, user_profile)
        print(f"📝 动态提示词长度: {len(dynamic_prompt)} 字符")
        
        # 5. 模拟大模型调用（实际使用时替换为真实API调用）
        llm_response = self._simulate_llm_call(dynamic_prompt, message)
        
        return {
            "type": "health_related",
            "response": llm_response,
            "knowledge_used": list(relevant_knowledge.keys()),
            "rules_applied": len(personalization_rules),
            "processing_steps": ["问题分类", "知识检索", "规则匹配", "提示词构建", "大模型生成"],
            "prompt_length": len(dynamic_prompt)
        }
    
    def _simulate_llm_call(self, prompt: str, user_input: str) -> str:
        """
        模拟大模型调用（实际部署时替换为真实API）
        
        Args:
            prompt: 完整提示词
            user_input: 用户输入
            
        Returns:
            模拟回复
        """
        # 这里是模拟回复，实际使用时需要调用真实的大模型API
        # 比如 OpenAI GPT, Claude, 或者本地部署的模型
        
        if "头晕" in user_input:
            return """🤗 **理解确认**
我理解您感到头晕，这确实需要重视，头晕可能与血糖状况有关。

💡 **专业分析**  
头晕的可能原因包括：
• 低血糖：血糖过低时常伴有头晕、出汗、心慌
• 高血糖：严重高血糖也可能导致头晕
• 血压变化：糖尿病患者常伴有血压问题
• 脱水：高血糖时容易脱水导致头晕

📋 **具体建议**
1. 立即测量血糖值
2. 如血糖低于3.9mmol/L，立即补充15g快速碳水化合物
3. 坐下或躺下休息，避免跌倒
4. 观察其他症状（出汗、心慌、视力模糊等）

⚠️ **注意事项**
如果头晕严重或持续不缓解，请立即就医！

💪 **鼓励支持**
及时关注身体症状是很好的健康意识，通过正确的处理措施，这种情况是可以很好改善的。"""

        elif any(word in user_input for word in ["大模型", "AI"]):
            return "这个问题我不清楚，不属于健康相关问题。\\n\\n我是您的健康顾问，专门帮助您管理血糖、饮食和运动。有什么健康方面的问题需要咨询吗？"
        
        else:
            return f"""🤗 **理解确认**
我理解您的关切，让我为您提供专业的健康指导。

💡 **专业分析**
根据您的描述和相关医学知识，我为您分析如下...

📋 **具体建议**
1. 建议您采取以下措施...
2. 可以尝试...
3. 注意观察...

⚠️ **注意事项**
请注意相关风险因素，必要时咨询医生。

💪 **鼓励支持**
您的健康意识很好，通过科学的管理方法，相信会有很好的效果！

（注：这是模拟回复，实际部署时会调用真实的大模型API生成更准确的回答）"""


def main():
    """主函数 - 系统使用示例"""
    print("🏥 健康顾问系统初始化...")
    
    # 创建系统实例
    advisor = HealthAdvisorSystem()
    
    # 测试用例
    test_cases = [
        "头晕了",
        "忘记吃药了", 
        "睡不着",
        "刚运动完",
        "你是用什么大模型？",
        "起床了"
    ]
    
    print("\\n🧪 开始测试用例...")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\\n🔹 测试用例 {i}:")
        result = advisor.process_user_input(test_input)
        
        print(f"输入: {test_input}")
        print(f"类型: {result['type']}")
        print(f"回复: {result['response'][:100]}...")
        if result['type'] == 'health_related':
            print(f"使用知识: {result['knowledge_used']}")
            print(f"应用规则: {result['rules_applied']}")
        print("-" * 30)

if __name__ == "__main__":
    main()