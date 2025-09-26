import unittest
from pathlib import Path
import json
import yaml
from datetime import datetime

from validator import validate_domain, OntologyValidator, ExpertRuleValidator, ConfigValidator
from processor import process_domain, OntologyProcessor, ExpertRuleProcessor, ProcessingContext

class TestDomainValidation(unittest.TestCase):
    
    def setUp(self):
        self.domain_path = Path(__file__).parent
        
    def test_ontology_validation(self):
        """测试本体验证"""
        with open(self.domain_path / "ontology.json") as f:
            ontology = json.load(f)
            
        validator = OntologyValidator()
        errors = validator.validate(ontology)
        self.assertEqual(len(errors), 0, f"本体验证错误: {errors}")
        
    def test_expert_rules_validation(self):
        """测试专家规则验证"""
        with open(self.domain_path / "expert_rules.json") as f:
            rules = json.load(f)
            
        validator = ExpertRuleValidator()
        errors = validator.validate(rules)
        self.assertEqual(len(errors), 0, f"规则验证错误: {errors}")
        
    def test_config_validation(self):
        """测试配置验证"""
        with open(self.domain_path / "config.yaml") as f:
            config = yaml.safe_load(f)
            
        validator = ConfigValidator()
        errors = validator.validate(config)
        self.assertEqual(len(errors), 0, f"配置验证错误: {errors}")
        
    def test_full_domain_validation(self):
        """测试完整域验证"""
        errors = validate_domain(str(self.domain_path))
        self.assertEqual(len(errors), 0, f"域验证错误: {errors}")

class TestDomainProcessing(unittest.TestCase):
    
    def setUp(self):
        self.domain_path = Path(__file__).parent
        self.ontology_processor = OntologyProcessor()
        self.rule_processor = ExpertRuleProcessor()
        self.context = ProcessingContext(
            timestamp=datetime.now(),
            source="test",
            domain="endocrinology",
            metadata={}
        )
        
    def test_ontology_processing(self):
        """测试本体处理"""
        with open(self.domain_path / "ontology.json") as f:
            ontology = json.load(f)
            
        result = self.ontology_processor.process(ontology, self.context)
        
        # 验证处理结果
        self.assertIn("concepts", result)
        self.assertIn("relationships", result)
        self.assertIn("metadata", result)
        
        # 验证概念处理
        self.assertTrue(len(result["concepts"]) > 0)
        for concept_id, concept in result["concepts"].items():
            self.assertIn("name", concept)
            self.assertIn("description", concept)
            
        # 验证关系处理
        if result["relationships"]:
            for rel in result["relationships"]:
                self.assertIn("type", rel)
                self.assertIn("source", rel)
                self.assertIn("target", rel)
                
    def test_expert_rules_processing(self):
        """测试专家规则处理"""
        with open(self.domain_path / "expert_rules.json") as f:
            rules = json.load(f)
            
        result = self.rule_processor.process(rules, self.context)
        
        # 验证处理结果
        self.assertIn("rules", result)
        self.assertIn("metadata", result)
        
        # 验证规则处理
        self.assertTrue(len(result["rules"]) > 0)
        for rule in result["rules"]:
            self.assertIn("id", rule)
            self.assertIn("name", rule)
            self.assertIn("conditions", rule)
            self.assertIn("actions", rule)
            
            # 验证条件解析
            conditions = rule["conditions"]
            if isinstance(conditions, dict):
                for key, value in conditions.items():
                    if key in ("and", "or"):
                        self.assertIsInstance(value, list)
                    elif isinstance(value, dict):
                        self.assertTrue(
                            any(op in value for op in ("$gt", "$gte", "$lt", "$lte", "$eq", "$ne", "$in"))
                            or all(isinstance(v, (dict, bool, int, float, str)) for v in value.values())
                        )
            
            # 验证动作
            for action in rule["actions"]:
                self.assertIn("type", action)
                if action["type"] == "recommend_test":
                    self.assertIn("test", action)
                    self.assertIn("frequency", action)
                elif action["type"] == "diagnose":
                    self.assertIn("condition", action)
                    self.assertIn("confidence", action)
                elif action["type"] == "set_target":
                    self.assertIn("parameter", action)
                    self.assertIn("range", action)
                    
    def test_full_domain_processing(self):
        """测试完整域处理"""
        processors = {
            "ontology": self.ontology_processor,
            "expert_rules": self.rule_processor
        }
        
        results = process_domain(str(self.domain_path), processors)
        
        # 验证处理结果
        self.assertIn("ontology", results)
        self.assertIn("expert_rules", results)
        
        # 验证元数据
        for source_type, result in results.items():
            self.assertIn("metadata", result)
            metadata = result["metadata"]
            self.assertIn("timestamp", metadata)
            self.assertIn("source", metadata)
            self.assertIn("domain", metadata)

if __name__ == "__main__":
    unittest.main()
