"""
领域知识库配置和加载模块
提供领域特定知识的配置和加载功能
"""

from typing import Dict, List, Optional, Union, Type
from dataclasses import dataclass
import json
import yaml
from pathlib import Path
import importlib
from abc import ABC, abstractmethod

@dataclass
class DomainConfig:
    """领域配置"""
    domain_id: str
    name: str
    description: str
    version: str
    ontology_path: str
    rules_path: str
    metrics_path: str
    validators_path: str
    expert_rules_path: str
    metadata: Dict

@dataclass
class DomainOntology:
    """领域本体"""
    concepts: Dict[str, Dict]
    relationships: Dict[str, Dict]
    attributes: Dict[str, Dict]
    axioms: Dict[str, Dict]

@dataclass
class DomainRule:
    """领域规则"""
    id: str
    type: str
    condition: str
    action: str
    priority: int
    metadata: Dict

@dataclass
class DomainMetric:
    """领域指标"""
    id: str
    name: str
    unit: str
    normal_range: Dict
    warning_thresholds: Dict
    calculation: str
    dependencies: List[str]

class DomainValidator(ABC):
    """领域验证器基类"""
    
    @abstractmethod
    async def validate(self, data: Dict) -> bool:
        """验证数据
        
        Args:
            data: 要验证的数据
            
        Returns:
            bool: 验证是否通过
        """
        pass

class DomainKnowledgeBase:
    """领域知识库"""
    
    def __init__(self, domain_id: str, base_path: str = None):
        """初始化领域知识库
        
        Args:
            domain_id: 领域ID
            base_path: 知识库基础路径
        """
        self.domain_id = domain_id
        self.base_path = Path(base_path or "domains")
        self.config = self._load_config()
        
        # 加载各组件
        self.ontology = self._load_ontology()
        self.rules = self._load_rules()
        self.metrics = self._load_metrics()
        self.validators = self._load_validators()
        self.expert_rules = self._load_expert_rules()
        
    def _load_config(self) -> DomainConfig:
        """加载领域配置"""
        config_path = self.base_path / self.domain_id / "config.yaml"
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        return DomainConfig(**config_data)
        
    def _load_ontology(self) -> DomainOntology:
        """加载领域本体"""
        ontology_path = self.base_path / self.config.ontology_path
        with open(ontology_path) as f:
            ontology_data = json.load(f)
        return DomainOntology(**ontology_data)
        
    def _load_rules(self) -> List[DomainRule]:
        """加载领域规则"""
        rules_path = self.base_path / self.config.rules_path
        with open(rules_path) as f:
            rules_data = json.load(f)
        return [DomainRule(**rule) for rule in rules_data]
        
    def _load_metrics(self) -> List[DomainMetric]:
        """加载领域指标"""
        metrics_path = self.base_path / self.config.metrics_path
        with open(metrics_path) as f:
            metrics_data = json.load(f)
        return [DomainMetric(**metric) for metric in metrics_data]
        
    def _load_validators(self) -> List[Type[DomainValidator]]:
        """加载领域验证器"""
        validators = []
        validators_dir = self.base_path / self.config.validators_path
        
        # 动态导入验证器模块
        for validator_file in validators_dir.glob("*.py"):
            if validator_file.name == "__init__.py":
                continue
            
            module_path = f"domains.{self.domain_id}.validators.{validator_file.stem}"
            module = importlib.import_module(module_path)
            
            # 查找继承自DomainValidator的类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, DomainValidator) and 
                    attr != DomainValidator):
                    validators.append(attr)
                    
        return validators
        
    def _load_expert_rules(self) -> Dict:
        """加载专家规则"""
        expert_rules_path = self.base_path / self.config.expert_rules_path
        with open(expert_rules_path) as f:
            return json.load(f)
            
    async def validate_data(self, data: Dict) -> bool:
        """验证数据
        
        Args:
            data: 要验证的数据
            
        Returns:
            bool: 所有验证是否通过
        """
        # 创建验证器实例并执行验证
        for validator_cls in self.validators:
            validator = validator_cls()
            if not await validator.validate(data):
                return False
        return True
        
    def get_metric_definition(self, metric_id: str) -> Optional[DomainMetric]:
        """获取指标定义
        
        Args:
            metric_id: 指标ID
            
        Returns:
            Optional[DomainMetric]: 指标定义
        """
        for metric in self.metrics:
            if metric.id == metric_id:
                return metric
        return None
        
    def get_applicable_rules(self, context: Dict) -> List[DomainRule]:
        """获取适用的规则
        
        Args:
            context: 上下文信息
            
        Returns:
            List[DomainRule]: 适用的规则列表
        """
        # 根据上下文筛选规则
        applicable_rules = []
        for rule in self.rules:
            # TODO: 实现规则匹配逻辑
            applicable_rules.append(rule)
        
        # 按优先级排序
        return sorted(applicable_rules, key=lambda r: r.priority)
        
    def get_concept_definition(self, concept_id: str) -> Optional[Dict]:
        """获取概念定义
        
        Args:
            concept_id: 概念ID
            
        Returns:
            Optional[Dict]: 概念定义
        """
        return self.ontology.concepts.get(concept_id)
        
    def get_relationship_definition(self, relationship_id: str) -> Optional[Dict]:
        """获取关系定义
        
        Args:
            relationship_id: 关系ID
            
        Returns:
            Optional[Dict]: 关系定义
        """
        return self.ontology.relationships.get(relationship_id)
        
    def get_expert_rule(self, rule_id: str) -> Optional[Dict]:
        """获取专家规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            Optional[Dict]: 专家规则
        """
        return self.expert_rules.get(rule_id)
