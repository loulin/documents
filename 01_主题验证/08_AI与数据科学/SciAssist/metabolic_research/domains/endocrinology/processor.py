from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import json
import yaml
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProcessingContext:
    """处理上下文"""
    timestamp: datetime
    source: str
    domain: str
    metadata: Dict[str, Any]

class DomainProcessor(ABC):
    """域处理器基类"""
    
    @abstractmethod
    def process(self, data: Dict[str, Any], context: ProcessingContext) -> Dict[str, Any]:
        """处理数据并返回结果"""
        pass

class OntologyProcessor(DomainProcessor):
    """本体处理器"""
    
    def __init__(self):
        self.processed_concepts = {}
        self.processed_relationships = {}
        
    def normalize_text(self, text: str) -> str:
        """规范化文本"""
        return text.lower().strip()
    
    def extract_relationships(self, concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取概念关系"""
        relationships = []
        parent = concept.get("parent")
        if parent:
            relationships.append({
                "type": "is_a",
                "source": concept["id"],
                "target": parent
            })
        
        # 处理其他关系
        for attr, value in concept.get("attributes", {}).items():
            if isinstance(value, list):
                for item in value:
                    relationships.append({
                        "type": attr,
                        "source": concept["id"],
                        "target": item
                    })
        
        return relationships
    
    def validate_constraints(self, relationships: List[Dict[str, Any]]) -> List[str]:
        """验证关系约束"""
        errors = []
        for rel in relationships:
            rel_type = rel["type"]
            if rel_type in self.processed_relationships:
                constraints = self.processed_relationships[rel_type].get("constraints", {})
                
                # 验证源类型约束
                source_types = constraints.get("source_types", [])
                if source_types:
                    source_concept = self.processed_concepts.get(rel["source"])
                    if source_concept and source_concept.get("type") not in source_types:
                        errors.append(f"关系 {rel_type} 的源类型约束不满足")
                
                # 验证目标类型约束
                target_types = constraints.get("target_types", [])
                if target_types:
                    target_concept = self.processed_concepts.get(rel["target"])
                    if target_concept and target_concept.get("type") not in target_types:
                        errors.append(f"关系 {rel_type} 的目标类型约束不满足")
        
        return errors
    
    def process(self, data: Dict[str, Any], context: ProcessingContext) -> Dict[str, Any]:
        """处理本体数据"""
        processed_data = {
            "concepts": {},
            "relationships": [],
            "metadata": {
                "timestamp": context.timestamp.isoformat(),
                "source": context.source,
                "domain": context.domain
            }
        }
        
        # 处理概念
        for concept_id, concept in data.get("concepts", {}).items():
            processed_concept = {
                "id": concept_id,
                "name": self.normalize_text(concept["name"]),
                "description": concept["description"],
                "synonyms": [self.normalize_text(s) for s in concept.get("synonyms", [])],
                "codes": concept.get("codes", {}),
                "attributes": concept.get("attributes", {})
            }
            self.processed_concepts[concept_id] = processed_concept
            processed_data["concepts"][concept_id] = processed_concept
            
            # 提取并验证关系
            relationships = self.extract_relationships(concept)
            errors = self.validate_constraints(relationships)
            if not errors:
                processed_data["relationships"].extend(relationships)
        
        # 处理关系定义
        for rel_id, rel in data.get("relationships", {}).items():
            self.processed_relationships[rel_id] = rel
            
        return processed_data

class ExpertRuleProcessor(DomainProcessor):
    """专家规则处理器"""
    
    def parse_conditions(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """解析规则条件"""
        parsed = {}
        
        if isinstance(conditions, dict):
            for key, value in conditions.items():
                if key in ("and", "or"):
                    parsed[key] = [self.parse_conditions(c) for c in value]
                elif isinstance(value, dict):
                    if any(op in value for op in ("$gt", "$gte", "$lt", "$lte", "$eq", "$ne", "$in")):
                        parsed[key] = value
                    else:
                        parsed[key] = self.parse_conditions(value)
                else:
                    parsed[key] = value
                    
        return parsed
    
    def validate_actions(self, actions: List[Dict[str, Any]]) -> List[str]:
        """验证规则动作"""
        errors = []
        valid_types = {
            "recommend_test",
            "diagnose",
            "recommend_referral",
            "recommend_monitoring",
            "set_target"
        }
        
        for action in actions:
            if action["type"] not in valid_types:
                errors.append(f"无效的动作类型: {action['type']}")
            
            if action["type"] == "recommend_test":
                if "test" not in action or "frequency" not in action:
                    errors.append("推荐检测动作缺少必要参数")
                    
            elif action["type"] == "diagnose":
                if "condition" not in action or "confidence" not in action:
                    errors.append("诊断动作缺少必要参数")
                    
            elif action["type"] == "set_target":
                if "parameter" not in action or "range" not in action:
                    errors.append("设置目标动作缺少必要参数")
        
        return errors
    
    def check_conflicts(self, rules: List[Dict[str, Any]]) -> List[str]:
        """检查规则冲突"""
        errors = []
        
        # 按优先级分组
        priority_groups = {}
        for rule in rules:
            priority = rule.get("priority", 0)
            if priority in priority_groups:
                priority_groups[priority].append(rule)
            else:
                priority_groups[priority] = [rule]
        
        # 检查同一优先级的规则冲突
        for priority, group in priority_groups.items():
            if len(group) > 1:
                # 简单的动作类型冲突检查
                action_types = {}
                for rule in group:
                    for action in rule["actions"]:
                        action_type = action["type"]
                        if action_type in action_types:
                            errors.append(f"优先级 {priority} 存在动作类型 {action_type} 的冲突")
                        action_types[action_type] = True
        
        return errors
    
    def process(self, data: List[Dict[str, Any]], context: ProcessingContext) -> Dict[str, Any]:
        """处理专家规则数据"""
        processed_data = {
            "rules": [],
            "metadata": {
                "timestamp": context.timestamp.isoformat(),
                "source": context.source,
                "domain": context.domain
            }
        }
        
        for rule in data:
            # 解析条件
            conditions = self.parse_conditions(rule["conditions"])
            
            # 验证动作
            action_errors = self.validate_actions(rule["actions"])
            if action_errors:
                continue
                
            processed_rule = {
                "id": rule["id"],
                "name": rule["name"],
                "description": rule["description"],
                "conditions": conditions,
                "actions": rule["actions"],
                "priority": rule.get("priority", 0),
                "evidence_level": rule.get("evidence_level", "C"),
                "references": rule.get("references", [])
            }
            processed_data["rules"].append(processed_rule)
        
        # 检查规则冲突
        conflict_errors = self.check_conflicts(processed_data["rules"])
        if conflict_errors:
            processed_data["metadata"]["conflicts"] = conflict_errors
            
        return processed_data

def process_domain(domain_path: str, processors: Dict[str, DomainProcessor]) -> Dict[str, Any]:
    """处理整个域数据"""
    results = {}
    
    # 加载配置
    with open(os.path.join(domain_path, "config.yaml")) as f:
        config = yaml.safe_load(f)
    
    domain_name = config["name"]
    
    # 处理每个数据源
    for source in config.get("sources", []):
        source_type = source["type"]
        if source_type in processors:
            processor = processors[source_type]
            
            # 加载源数据
            source_path = os.path.join(domain_path, source["path"])
            if os.path.exists(source_path):
                with open(source_path) as f:
                    if source["format"] == "json":
                        data = json.load(f)
                    elif source["format"] == "yaml":
                        data = yaml.safe_load(f)
                    else:
                        continue
                
                # 创建处理上下文
                context = ProcessingContext(
                    timestamp=datetime.now(),
                    source=source["path"],
                    domain=domain_name,
                    metadata=source.get("metadata", {})
                )
                
                # 处理数据
                try:
                    results[source_type] = processor.process(data, context)
                except Exception as e:
                    print(f"处理 {source['path']} 时出错: {str(e)}")
    
    return results

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("domain_path")
    args = parser.parse_args()
    
    # 创建处理器
    processors = {
        "ontology": OntologyProcessor(),
        "expert_rules": ExpertRuleProcessor()
    }
    
    # 处理域数据
    results = process_domain(args.domain_path, processors)
    
    # 输出结果
    print(json.dumps(results, ensure_ascii=False, indent=2))
    
if __name__ == "__main__":
    main()
