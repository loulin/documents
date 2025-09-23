from typing import Dict, List, Any
from abc import ABC, abstractmethod
import jsonschema
import yaml
import os
import json
import sys

class DomainValidator(ABC):
    """域验证器基类"""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """验证数据并返回错误列表"""
        pass

class OntologyValidator(DomainValidator):
    """本体验证器"""
    
    def __init__(self):
        self.schema = {
            "type": "object",
            "required": ["concepts", "relationships"],
            "properties": {
                "concepts": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z0-9_]+$": {
                            "type": "object",
                            "required": ["name", "description"],
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "parent": {"type": "string"},
                                "synonyms": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "codes": {"type": "object"},
                                "attributes": {"type": "object"}
                            }
                        }
                    }
                },
                "relationships": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z0-9_]+$": {
                            "type": "object",
                            "required": ["name", "description"],
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "properties": {"type": "object"},
                                "constraints": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            errors.append(str(e))
            
        # 验证关系约束
        for rel_id, rel in data.get("relationships", {}).items():
            constraints = rel.get("constraints", {})
            source_types = constraints.get("source_types", [])
            target_types = constraints.get("target_types", [])
            
            # 检查源类型和目标类型是否存在
            for t in source_types:
                if not any(c.get("type") == t for c in data.get("concepts", {}).values()):
                    errors.append(f"关系 {rel_id} 的源类型 {t} 未定义")
                    
            for t in target_types:
                if not any(c.get("type") == t for c in data.get("concepts", {}).values()):
                    errors.append(f"关系 {rel_id} 的目标类型 {t} 未定义")
        
        return errors

class ExpertRuleValidator(DomainValidator):
    """专家规则验证器"""
    
    def __init__(self):
        self.schema = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "description", "conditions", "actions"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "conditions": {"type": "object"},
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["type"],
                            "properties": {
                                "type": {"type": "string"},
                                "test": {"type": "string"},
                                "frequency": {"type": "string"},
                                "condition": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "priority": {"type": "integer"},
                    "evidence_level": {"type": "string"},
                    "references": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            errors.append(str(e))
            
        # 验证规则优先级
        priorities = [rule.get("priority") for rule in data if "priority" in rule]
        if len(set(priorities)) != len(priorities):
            errors.append("规则优先级存在重复")
            
        # 验证证据等级
        valid_evidence_levels = {"A", "B", "C", "D"}
        for rule in data:
            if rule.get("evidence_level") not in valid_evidence_levels:
                errors.append(f"规则 {rule['id']} 的证据等级无效")
                
        return errors

class ConfigValidator(DomainValidator):
    """配置验证器"""
    
    def __init__(self):
        self.schema = {
            "type": "object",
            "required": ["name", "description", "sources", "validators"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "sources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["type", "path"],
                        "properties": {
                            "type": {"type": "string"},
                            "path": {"type": "string"},
                            "format": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                },
                "validators": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "rules"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "rules": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            errors.append(str(e))
            
        # 验证文件路径存在
        for source in data.get("sources", []):
            path = source.get("path")
            if not os.path.exists(path):
                errors.append(f"源文件路径不存在: {path}")
                
        return errors

def validate_domain(domain_path: str) -> List[str]:
    """验证整个域配置"""
    errors = []
    
    # 加载配置
    with open(os.path.join(domain_path, "config.yaml")) as f:
        config = yaml.safe_load(f)
        
    # 验证配置
    config_validator = ConfigValidator()
    errors.extend(config_validator.validate(config))
    
    # 验证本体
    ontology_path = os.path.join(domain_path, "ontology.json")
    if os.path.exists(ontology_path):
        with open(ontology_path) as f:
            ontology = json.load(f)
        ontology_validator = OntologyValidator()
        errors.extend(ontology_validator.validate(ontology))
    
    # 验证规则
    rules_path = os.path.join(domain_path, "expert_rules.json") 
    if os.path.exists(rules_path):
        with open(rules_path) as f:
            rules = json.load(f)
        rules_validator = ExpertRuleValidator()
        errors.extend(rules_validator.validate(rules))
        
    return errors

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("domain_path")
    args = parser.parse_args()
    
    errors = validate_domain(args.domain_path)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    else:
        print("验证通过")
        
if __name__ == "__main__":
    main()
