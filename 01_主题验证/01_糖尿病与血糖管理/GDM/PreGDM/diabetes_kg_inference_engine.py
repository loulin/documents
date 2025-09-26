#!/usr/bin/env python3
"""
糖尿病知识图谱推理引擎
基于第一性原理构建的患者问答系统
"""

import json
import re
from typing import List, Dict, Set, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import sqlite3
from datetime import datetime


class EntityType(Enum):
    PHYSIOLOGICAL = "physiological_entity"
    PATHOLOGICAL = "pathological_entity" 
    CLINICAL = "clinical_entity"
    LIFESTYLE = "lifestyle_entity"


class RelationType(Enum):
    CAUSES = "causes"
    TRIGGERS = "triggers"
    WORSENS = "worsens"
    PREVENTS = "prevents"
    ALLEVIATES = "alleviates"
    REGULATES = "regulates"
    AFFECTS = "affects"
    IMPROVES = "improves"
    TREATS = "treats"


class QueryType(Enum):
    DIAGNOSTIC = "diagnostic"      # 诊断相关问题
    TREATMENT = "treatment"        # 治疗相关问题
    PREVENTION = "prevention"      # 预防相关问题
    SYMPTOM = "symptom"           # 症状相关问题
    PROGNOSIS = "prognosis"       # 预后相关问题
    LIFESTYLE = "lifestyle"       # 生活方式问题


@dataclass
class Entity:
    id: str
    name: str
    name_en: str
    type: EntityType
    category: str
    description: str
    properties: Dict[str, Any]
    
    
@dataclass
class Relationship:
    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    strength: str
    evidence_level: str
    properties: Dict[str, Any]


@dataclass
class QueryResult:
    query_text: str
    query_type: QueryType
    entities_found: List[Entity]
    relationships: List[Relationship]
    answer: str
    confidence: float
    sources: List[str]


class DiabetesKnowledgeGraph:
    """糖尿病知识图谱核心类"""
    
    def __init__(self, db_path: str = "diabetes_kg.db"):
        self.db_path = db_path
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.inference_rules: List[Dict] = []
        self._init_database()
        self._load_knowledge()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建实体表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_en TEXT,
                type TEXT NOT NULL,
                category TEXT,
                description TEXT,
                properties TEXT
            )
        ''')
        
        # 创建关系表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                target_id TEXT,
                relation_type TEXT,
                strength TEXT,
                evidence_level TEXT,
                properties TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_knowledge(self):
        """从数据库加载知识"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 加载实体
        cursor.execute("SELECT * FROM entities")
        for row in cursor.fetchall():
            entity = Entity(
                id=row[0],
                name=row[1], 
                name_en=row[2],
                type=EntityType(row[3]),
                category=row[4],
                description=row[5],
                properties=json.loads(row[6]) if row[6] else {}
            )
            self.entities[entity.id] = entity
        
        # 加载关系
        cursor.execute("SELECT * FROM relationships")
        for row in cursor.fetchall():
            relationship = Relationship(
                id=row[0],
                source_id=row[1],
                target_id=row[2],
                relation_type=RelationType(row[3]),
                strength=row[4],
                evidence_level=row[5],
                properties=json.loads(row[6]) if row[6] else {}
            )
            self.relationships.append(relationship)
        
        conn.close()


class QueryProcessor:
    """查询处理器 - 理解和分析用户问题"""
    
    def __init__(self):
        self.medical_terms = self._load_medical_terms()
        self.query_patterns = self._load_query_patterns()
    
    def _load_medical_terms(self) -> Dict[str, str]:
        """加载医学术语词典"""
        return {
            # 疾病相关
            "糖尿病": "PATH_001",
            "2型糖尿病": "PATH_001", 
            "高血糖": "PHYS_002",
            "低血糖": "PHYS_003",
            "糖尿病肾病": "PATH_002",
            "糖尿病视网膜病变": "PATH_003",
            
            # 检查相关
            "血糖": "CLIN_001",
            "糖化血红蛋白": "CLIN_002",
            "HbA1c": "CLIN_002",
            "空腹血糖": "CLIN_003",
            
            # 治疗相关
            "胰岛素": "CLIN_004",
            "二甲双胍": "CLIN_005",
            "运动": "LIFE_001",
            "饮食": "LIFE_002",
            
            # 症状相关
            "多饮": "SYMP_001",
            "多尿": "SYMP_002", 
            "体重下降": "SYMP_003"
        }
    
    def _load_query_patterns(self) -> Dict[QueryType, List[str]]:
        """加载查询模式"""
        return {
            QueryType.DIAGNOSTIC: [
                r".*诊断.*", r".*确诊.*", r".*检查.*", r".*化验.*",
                r".*什么是.*", r".*如何判断.*", r".*怎么知道.*"
            ],
            QueryType.TREATMENT: [
                r".*治疗.*", r".*怎么办.*", r".*用药.*", r".*服用.*",
                r".*吃什么药.*", r".*如何治.*", r".*怎么治.*"
            ],
            QueryType.PREVENTION: [
                r".*预防.*", r".*避免.*", r".*如何防止.*", r".*怎么预防.*",
                r".*注意.*", r".*防范.*"
            ],
            QueryType.SYMPTOM: [
                r".*症状.*", r".*表现.*", r".*感觉.*", r".*不舒服.*",
                r".*疼痛.*", r".*异常.*"
            ],
            QueryType.LIFESTYLE: [
                r".*饮食.*", r".*运动.*", r".*生活.*", r".*日常.*",
                r".*吃.*", r".*食物.*", r".*锻炼.*"
            ]
        }
    
    def analyze_query(self, query_text: str) -> Tuple[QueryType, List[str]]:
        """分析查询类型和提及的实体"""
        # 确定查询类型
        query_type = self._classify_query_type(query_text)
        
        # 提取实体
        entities = self._extract_entities(query_text)
        
        return query_type, entities
    
    def _classify_query_type(self, query_text: str) -> QueryType:
        """分类查询类型"""
        for qtype, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_text):
                    return qtype
        return QueryType.DIAGNOSTIC  # 默认类型
    
    def _extract_entities(self, query_text: str) -> List[str]:
        """从查询中提取实体"""
        entities = []
        for term, entity_id in self.medical_terms.items():
            if term in query_text:
                entities.append(entity_id)
        return entities


class InferenceEngine:
    """推理引擎 - 基于知识图谱进行推理"""
    
    def __init__(self, kg: DiabetesKnowledgeGraph):
        self.kg = kg
        self.inference_rules = self._load_inference_rules()
    
    def _load_inference_rules(self) -> List[Dict]:
        """加载推理规则"""
        return [
            {
                "id": "DIAG_RULE_001",
                "name": "糖尿病诊断规则",
                "conditions": [
                    {"entity": "空腹血糖", "operator": ">=", "value": "7.0", "unit": "mmol/L"},
                    {"entity": "随机血糖", "operator": ">=", "value": "11.1", "unit": "mmol/L"}
                ],
                "conclusion": "诊断为糖尿病",
                "confidence": 0.95
            },
            {
                "id": "TREAT_RULE_001", 
                "name": "2型糖尿病一线治疗",
                "conditions": [
                    {"entity": "2型糖尿病", "status": "confirmed"},
                    {"entity": "肾功能", "status": "normal"}
                ],
                "conclusion": "推荐二甲双胍治疗",
                "confidence": 0.90
            },
            {
                "id": "COMP_RULE_001",
                "name": "糖尿病肾病风险",
                "conditions": [
                    {"entity": "糖尿病", "duration": ">10年"},
                    {"entity": "HbA1c", "operator": ">", "value": "8.0", "unit": "%"}
                ],
                "conclusion": "高风险发生糖尿病肾病",
                "confidence": 0.80
            }
        ]
    
    def reason(self, query_type: QueryType, entities: List[str]) -> Dict[str, Any]:
        """基于查询类型和实体进行推理"""
        reasoning_result = {
            "matched_rules": [],
            "inferred_entities": [],
            "relationships": [],
            "confidence": 0.0
        }
        
        if query_type == QueryType.DIAGNOSTIC:
            reasoning_result = self._diagnostic_reasoning(entities)
        elif query_type == QueryType.TREATMENT:
            reasoning_result = self._treatment_reasoning(entities)
        elif query_type == QueryType.PREVENTION:
            reasoning_result = self._prevention_reasoning(entities)
        elif query_type == QueryType.SYMPTOM:
            reasoning_result = self._symptom_reasoning(entities)
        
        return reasoning_result
    
    def _diagnostic_reasoning(self, entities: List[str]) -> Dict[str, Any]:
        """诊断推理"""
        result = {"matched_rules": [], "inferred_entities": [], "relationships": [], "confidence": 0.0}
        
        # 查找相关的诊断关系
        for rel in self.kg.relationships:
            if rel.relation_type in [RelationType.CAUSES, RelationType.TRIGGERS]:
                if rel.source_id in entities or rel.target_id in entities:
                    result["relationships"].append(rel)
        
        # 应用诊断规则
        for rule in self.inference_rules:
            if "诊断" in rule["name"]:
                result["matched_rules"].append(rule)
                result["confidence"] = max(result["confidence"], rule["confidence"])
        
        return result
    
    def _treatment_reasoning(self, entities: List[str]) -> Dict[str, Any]:
        """治疗推理"""
        result = {"matched_rules": [], "inferred_entities": [], "relationships": [], "confidence": 0.0}
        
        # 查找治疗关系
        for rel in self.kg.relationships:
            if rel.relation_type in [RelationType.TREATS, RelationType.ALLEVIATES]:
                if rel.target_id in entities:  # 找到治疗目标疾病的方法
                    result["relationships"].append(rel)
                    result["inferred_entities"].append(rel.source_id)
        
        return result
    
    def _prevention_reasoning(self, entities: List[str]) -> Dict[str, Any]:
        """预防推理"""
        result = {"matched_rules": [], "inferred_entities": [], "relationships": [], "confidence": 0.0}
        
        # 查找预防关系
        for rel in self.kg.relationships:
            if rel.relation_type == RelationType.PREVENTS:
                if rel.target_id in entities:
                    result["relationships"].append(rel)
                    result["inferred_entities"].append(rel.source_id)
        
        return result
    
    def _symptom_reasoning(self, entities: List[str]) -> Dict[str, Any]:
        """症状推理"""
        result = {"matched_rules": [], "inferred_entities": [], "relationships": [], "confidence": 0.0}
        
        # 查找症状相关关系
        for rel in self.kg.relationships:
            if rel.relation_type == RelationType.CAUSES:
                if rel.source_id in entities:  # 疾病导致症状
                    result["relationships"].append(rel)
                    result["inferred_entities"].append(rel.target_id)
        
        return result


class AnswerGenerator:
    """答案生成器"""
    
    def __init__(self, kg: DiabetesKnowledgeGraph):
        self.kg = kg
    
    def generate_answer(self, query_text: str, query_type: QueryType, 
                       entities: List[str], reasoning_result: Dict[str, Any]) -> str:
        """生成结构化答案"""
        
        if query_type == QueryType.DIAGNOSTIC:
            return self._generate_diagnostic_answer(query_text, entities, reasoning_result)
        elif query_type == QueryType.TREATMENT:
            return self._generate_treatment_answer(query_text, entities, reasoning_result)
        elif query_type == QueryType.PREVENTION:
            return self._generate_prevention_answer(query_text, entities, reasoning_result)
        elif query_type == QueryType.SYMPTOM:
            return self._generate_symptom_answer(query_text, entities, reasoning_result)
        else:
            return self._generate_general_answer(query_text, entities, reasoning_result)
    
    def _generate_diagnostic_answer(self, query_text: str, entities: List[str], 
                                   reasoning_result: Dict[str, Any]) -> str:
        """生成诊断相关答案"""
        answer_parts = []
        
        # 基础信息
        for entity_id in entities:
            if entity_id in self.kg.entities:
                entity = self.kg.entities[entity_id]
                answer_parts.append(f"**{entity.name}**：{entity.description}")
        
        # 诊断标准
        for rule in reasoning_result.get("matched_rules", []):
            if "诊断" in rule["name"]:
                answer_parts.append(f"\n**诊断标准**：{rule['conclusion']}")
                for condition in rule["conditions"]:
                    answer_parts.append(f"- {condition}")
        
        # 相关检查
        related_tests = []
        for rel in reasoning_result.get("relationships", []):
            if rel.relation_type == RelationType.REGULATES:
                source_entity = self.kg.entities.get(rel.source_id)
                if source_entity and source_entity.type == EntityType.CLINICAL:
                    related_tests.append(source_entity.name)
        
        if related_tests:
            answer_parts.append(f"\n**相关检查**：{', '.join(related_tests)}")
        
        return "\n".join(answer_parts)
    
    def _generate_treatment_answer(self, query_text: str, entities: List[str],
                                  reasoning_result: Dict[str, Any]) -> str:
        """生成治疗相关答案"""
        answer_parts = []
        
        # 治疗方案
        treatments = []
        for entity_id in reasoning_result.get("inferred_entities", []):
            if entity_id in self.kg.entities:
                entity = self.kg.entities[entity_id]
                if entity.type == EntityType.CLINICAL:
                    treatments.append(f"- **{entity.name}**：{entity.description}")
        
        if treatments:
            answer_parts.append("**推荐治疗方案**：")
            answer_parts.extend(treatments)
        
        # 治疗原理
        for rel in reasoning_result.get("relationships", []):
            if rel.relation_type == RelationType.TREATS:
                mechanism = rel.properties.get("mechanism", "")
                if mechanism:
                    answer_parts.append(f"\n**作用机制**：{mechanism}")
        
        return "\n".join(answer_parts)
    
    def _generate_prevention_answer(self, query_text: str, entities: List[str],
                                   reasoning_result: Dict[str, Any]) -> str:
        """生成预防相关答案"""
        answer_parts = []
        
        # 预防措施
        preventions = []
        for entity_id in reasoning_result.get("inferred_entities", []):
            if entity_id in self.kg.entities:
                entity = self.kg.entities[entity_id]
                if entity.type == EntityType.LIFESTYLE:
                    preventions.append(f"- **{entity.name}**：{entity.description}")
        
        if preventions:
            answer_parts.append("**预防措施**：")
            answer_parts.extend(preventions)
        
        return "\n".join(answer_parts)
    
    def _generate_symptom_answer(self, query_text: str, entities: List[str],
                                reasoning_result: Dict[str, Any]) -> str:
        """生成症状相关答案"""
        answer_parts = []
        
        # 症状描述
        for entity_id in entities:
            if entity_id in self.kg.entities:
                entity = self.kg.entities[entity_id]
                answer_parts.append(f"**{entity.name}**：{entity.description}")
        
        # 可能原因
        causes = []
        for rel in reasoning_result.get("relationships", []):
            if rel.relation_type == RelationType.CAUSES:
                cause_entity = self.kg.entities.get(rel.source_id)
                if cause_entity:
                    causes.append(cause_entity.name)
        
        if causes:
            answer_parts.append(f"\n**可能原因**：{', '.join(causes)}")
        
        return "\n".join(answer_parts)
    
    def _generate_general_answer(self, query_text: str, entities: List[str],
                                reasoning_result: Dict[str, Any]) -> str:
        """生成通用答案"""
        answer_parts = []
        
        for entity_id in entities:
            if entity_id in self.kg.entities:
                entity = self.kg.entities[entity_id]
                answer_parts.append(f"**{entity.name}**：{entity.description}")
        
        return "\n".join(answer_parts) if answer_parts else "抱歉，我无法理解您的问题，请重新描述。"


class DiabetesQASystem:
    """糖尿病问答系统主类"""
    
    def __init__(self):
        self.kg = DiabetesKnowledgeGraph()
        self.query_processor = QueryProcessor()
        self.inference_engine = InferenceEngine(self.kg)
        self.answer_generator = AnswerGenerator(self.kg)
    
    def answer_question(self, question: str) -> QueryResult:
        """回答用户问题"""
        # 1. 查询理解
        query_type, entities = self.query_processor.analyze_query(question)
        
        # 2. 推理
        reasoning_result = self.inference_engine.reason(query_type, entities)
        
        # 3. 生成答案
        answer = self.answer_generator.generate_answer(
            question, query_type, entities, reasoning_result
        )
        
        # 4. 构建结果
        result = QueryResult(
            query_text=question,
            query_type=query_type,
            entities_found=[self.kg.entities[eid] for eid in entities if eid in self.kg.entities],
            relationships=reasoning_result.get("relationships", []),
            answer=answer,
            confidence=reasoning_result.get("confidence", 0.5),
            sources=["糖尿病诊疗指南", "临床医学教科书"]
        )
        
        return result


# 使用示例
if __name__ == "__main__":
    # 初始化问答系统
    qa_system = DiabetesQASystem()
    
    # 示例问题
    test_questions = [
        "糖尿病如何诊断？",
        "2型糖尿病怎么治疗？",
        "如何预防糖尿病？",
        "糖尿病有什么症状？",
        "血糖高了怎么办？"
    ]
    
    for question in test_questions:
        print(f"\n问题：{question}")
        result = qa_system.answer_question(question)
        print(f"查询类型：{result.query_type.value}")
        print(f"答案：{result.answer}")
        print(f"置信度：{result.confidence}")
        print("-" * 50)