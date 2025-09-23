#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF实验室检查多单位转换算法实现
Multi-Unit Conversion Algorithms for CRF Laboratory Tests

版本: 1.0
日期: 2025-08-31
作者: CRF标准化团队
"""

import json
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """单位转换异常类"""
    pass


class ValidationError(Exception):
    """数据验证异常类"""
    pass


@dataclass
class ConversionRule:
    """单位转换规则数据类"""
    from_unit: str
    to_unit: str
    formula: str
    factor: Optional[float] = None
    precision: int = 2
    bidirectional: bool = True


@dataclass
class QualityControlLimits:
    """质量控制限制数据类"""
    absolute_min: Optional[float] = None
    absolute_max: Optional[float] = None
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None
    panic_low: Optional[float] = None
    panic_high: Optional[float] = None


@dataclass
class ReferenceRange:
    """参考范围数据类"""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    population: str = "general"
    gender: str = "both"
    age_group: str = "adult"
    condition: Optional[str] = None


class TestCategory(Enum):
    """检验类别枚举"""
    GLUCOSE_METABOLISM = "glucose_metabolism"
    CARDIOVASCULAR = "cardiovascular"
    LIVER_FUNCTION = "liver_function"
    KIDNEY_FUNCTION = "kidney_function"
    LIPID_PROFILE = "lipid_profile"
    THYROID_FUNCTION = "thyroid_function"
    BLOOD_ROUTINE = "blood_routine"
    URINE_TESTS = "urine_tests"


class LabTestConverter:
    """实验室检查单位转换器主类"""
    
    def __init__(self, config_file: str = None):
        """
        初始化转换器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置
        """
        self.conversion_rules: Dict[str, Dict[str, ConversionRule]] = {}
        self.quality_limits: Dict[str, Dict[str, QualityControlLimits]] = {}
        self.reference_ranges: Dict[str, List[ReferenceRange]] = {}
        
        if config_file:
            self.load_config(config_file)
        else:
            self._initialize_default_config()
    
    def _initialize_default_config(self):
        """初始化默认配置"""
        # 血糖相关转换
        self._add_glucose_conversions()
        # 心血管标志物转换
        self._add_cardiovascular_conversions()
        # 肝功能转换
        self._add_liver_function_conversions()
        # 肾功能转换
        self._add_kidney_function_conversions()
        # 血脂转换
        self._add_lipid_conversions()
        # 甲状腺功能转换
        self._add_thyroid_conversions()
        # 血常规转换
        self._add_blood_routine_conversions()
        # 尿液检查转换
        self._add_urine_test_conversions()
    
    def _add_glucose_conversions(self):
        """添加血糖相关转换规则"""
        # 血糖转换
        glucose_rules = {
            "mg/dL_to_mmol/L": ConversionRule(
                from_unit="mg/dL", to_unit="mmol/L",
                formula="value * 0.05551", factor=0.05551, precision=1
            ),
            "mmol/L_to_mg/dL": ConversionRule(
                from_unit="mmol/L", to_unit="mg/dL", 
                formula="value * 18.0182", factor=18.0182, precision=0
            ),
            "g/L_to_mmol/L": ConversionRule(
                from_unit="g/L", to_unit="mmol/L",
                formula="value * 5.551", factor=5.551, precision=1
            )
        }
        self.conversion_rules["glucose"] = glucose_rules
        
        # 血糖质量控制限制
        self.quality_limits["glucose"] = {
            "mmol/L": QualityControlLimits(
                absolute_min=1.0, absolute_max=33.3,
                critical_low=2.8, critical_high=22.2,
                panic_low=2.2, panic_high=27.8
            ),
            "mg/dL": QualityControlLimits(
                absolute_min=18, absolute_max=600,
                critical_low=50, critical_high=400,
                panic_low=40, panic_high=500
            )
        }
        
        # 血糖参考范围
        self.reference_ranges["glucose"] = [
            ReferenceRange(min_value=3.9, max_value=6.1, population="normal"),
            ReferenceRange(min_value=6.1, max_value=7.0, population="prediabetic"),
            ReferenceRange(min_value=7.0, population="diabetic")
        ]
        
        # HbA1c转换
        hba1c_rules = {
            "%_to_mmol/mol": ConversionRule(
                from_unit="%", to_unit="mmol/mol",
                formula="(value - 2.15) * 10.929", precision=0
            ),
            "mmol/mol_to_%": ConversionRule(
                from_unit="mmol/mol", to_unit="%",
                formula="(value / 10.929) + 2.15", precision=1
            )
        }
        self.conversion_rules["hba1c"] = hba1c_rules
        
        # C肽转换
        c_peptide_rules = {
            "ng/mL_to_nmol/L": ConversionRule(
                from_unit="ng/mL", to_unit="nmol/L",
                formula="value * 0.331", factor=0.331, precision=2
            ),
            "pmol/L_to_nmol/L": ConversionRule(
                from_unit="pmol/L", to_unit="nmol/L",
                formula="value / 1000", factor=0.001, precision=3
            )
        }
        self.conversion_rules["c_peptide"] = c_peptide_rules
    
    def _add_cardiovascular_conversions(self):
        """添加心血管标志物转换规则"""
        # 肌钙蛋白I转换
        troponin_rules = {
            "μg/L_to_ng/mL": ConversionRule(
                from_unit="μg/L", to_unit="ng/mL",
                formula="value * 1.0", factor=1.0, precision=3
            ),
            "pg/mL_to_ng/mL": ConversionRule(
                from_unit="pg/mL", to_unit="ng/mL",
                formula="value / 1000", factor=0.001, precision=3
            )
        }
        self.conversion_rules["troponin_i"] = troponin_rules
        
        # BNP转换
        bnp_rules = {
            "ng/L_to_pg/mL": ConversionRule(
                from_unit="ng/L", to_unit="pg/mL",
                formula="value * 1.0", factor=1.0, precision=0
            ),
            "pmol/L_to_pg/mL": ConversionRule(
                from_unit="pmol/L", to_unit="pg/mL",
                formula="value * 3.47", factor=3.47, precision=0
            )
        }
        self.conversion_rules["bnp"] = bnp_rules
        
        # hs-CRP转换
        hscrp_rules = {
            "mg/dL_to_mg/L": ConversionRule(
                from_unit="mg/dL", to_unit="mg/L",
                formula="value * 10", factor=10, precision=1
            ),
            "μg/mL_to_mg/L": ConversionRule(
                from_unit="μg/mL", to_unit="mg/L",
                formula="value * 1.0", factor=1.0, precision=1
            )
        }
        self.conversion_rules["hs_crp"] = hscrp_rules
    
    def _add_liver_function_conversions(self):
        """添加肝功能转换规则"""
        # ALT/AST转换
        alt_rules = {
            "IU/L_to_U/L": ConversionRule(
                from_unit="IU/L", to_unit="U/L",
                formula="value * 1.0", factor=1.0, precision=0
            ),
            "μkat/L_to_U/L": ConversionRule(
                from_unit="μkat/L", to_unit="U/L",
                formula="value * 60", factor=60, precision=0
            )
        }
        self.conversion_rules["alt"] = alt_rules
        self.conversion_rules["ast"] = alt_rules  # AST使用相同转换规则
        
        # 总胆红素转换
        bilirubin_rules = {
            "mg/dL_to_μmol/L": ConversionRule(
                from_unit="mg/dL", to_unit="μmol/L",
                formula="value * 17.1", factor=17.1, precision=1
            ),
            "mg/L_to_μmol/L": ConversionRule(
                from_unit="mg/L", to_unit="μmol/L",
                formula="value * 1.71", factor=1.71, precision=1
            )
        }
        self.conversion_rules["total_bilirubin"] = bilirubin_rules
        self.conversion_rules["direct_bilirubin"] = bilirubin_rules
        self.conversion_rules["indirect_bilirubin"] = bilirubin_rules
    
    def _add_kidney_function_conversions(self):
        """添加肾功能转换规则"""
        # 肌酐转换
        creatinine_rules = {
            "mg/dL_to_μmol/L": ConversionRule(
                from_unit="mg/dL", to_unit="μmol/L",
                formula="value * 88.42", factor=88.42, precision=0
            ),
            "mg/L_to_μmol/L": ConversionRule(
                from_unit="mg/L", to_unit="μmol/L",
                formula="value * 8.842", factor=8.842, precision=0
            )
        }
        self.conversion_rules["creatinine"] = creatinine_rules
        
        # 尿素转换
        urea_rules = {
            "mg/dL_to_mmol/L": ConversionRule(
                from_unit="mg/dL", to_unit="mmol/L",
                formula="value * 0.357", factor=0.357, precision=1
            ),
            "g/L_to_mmol/L": ConversionRule(
                from_unit="g/L", to_unit="mmol/L",
                formula="value * 16.67", factor=16.67, precision=1
            )
        }
        self.conversion_rules["urea"] = urea_rules
        
        # 尿酸转换
        uric_acid_rules = {
            "mg/dL_to_μmol/L": ConversionRule(
                from_unit="mg/dL", to_unit="μmol/L",
                formula="value * 59.48", factor=59.48, precision=0
            ),
            "mg/L_to_μmol/L": ConversionRule(
                from_unit="mg/L", to_unit="μmol/L",
                formula="value * 5.948", factor=5.948, precision=0
            )
        }
        self.conversion_rules["uric_acid"] = uric_acid_rules
    
    def _add_lipid_conversions(self):
        """添加血脂转换规则"""
        # 胆固醇转换
        cholesterol_rules = {
            "mg/dL_to_mmol/L": ConversionRule(
                from_unit="mg/dL", to_unit="mmol/L",
                formula="value * 0.02586", factor=0.02586, precision=2
            ),
            "mg/L_to_mmol/L": ConversionRule(
                from_unit="mg/L", to_unit="mmol/L",
                formula="value * 0.002586", factor=0.002586, precision=2
            )
        }
        self.conversion_rules["total_cholesterol"] = cholesterol_rules
        self.conversion_rules["ldl_cholesterol"] = cholesterol_rules
        self.conversion_rules["hdl_cholesterol"] = cholesterol_rules
        
        # 甘油三酯转换
        triglycerides_rules = {
            "mg/dL_to_mmol/L": ConversionRule(
                from_unit="mg/dL", to_unit="mmol/L",
                formula="value * 0.01129", factor=0.01129, precision=2
            )
        }
        self.conversion_rules["triglycerides"] = triglycerides_rules
    
    def _add_thyroid_conversions(self):
        """添加甲状腺功能转换规则"""
        # TSH转换
        tsh_rules = {
            "μIU/mL_to_mIU/L": ConversionRule(
                from_unit="μIU/mL", to_unit="mIU/L",
                formula="value * 1.0", factor=1.0, precision=2
            )
        }
        self.conversion_rules["tsh"] = tsh_rules
        
        # Free T4转换
        ft4_rules = {
            "ng/dL_to_pmol/L": ConversionRule(
                from_unit="ng/dL", to_unit="pmol/L",
                formula="value * 12.87", factor=12.87, precision=1
            ),
            "μg/dL_to_pmol/L": ConversionRule(
                from_unit="μg/dL", to_unit="pmol/L",
                formula="value * 12870", factor=12870, precision=1
            )
        }
        self.conversion_rules["free_t4"] = ft4_rules
        
        # Free T3转换
        ft3_rules = {
            "ng/dL_to_pmol/L": ConversionRule(
                from_unit="ng/dL", to_unit="pmol/L",
                formula="value * 15.36", factor=15.36, precision=1
            )
        }
        self.conversion_rules["free_t3"] = ft3_rules
    
    def _add_blood_routine_conversions(self):
        """添加血常规转换规则"""
        # 血红蛋白转换
        hemoglobin_rules = {
            "g/dL_to_g/L": ConversionRule(
                from_unit="g/dL", to_unit="g/L",
                formula="value * 10", factor=10, precision=0
            ),
            "mmol/L_to_g/L": ConversionRule(
                from_unit="mmol/L", to_unit="g/L",
                formula="value * 16.11", factor=16.11, precision=0
            )
        }
        self.conversion_rules["hemoglobin"] = hemoglobin_rules
        
        # 血小板计数转换
        platelet_rules = {
            "G/L_to_×10⁹/L": ConversionRule(
                from_unit="G/L", to_unit="×10⁹/L",
                formula="value * 1.0", factor=1.0, precision=0
            ),
            "/μL_to_×10⁹/L": ConversionRule(
                from_unit="/μL", to_unit="×10⁹/L",
                formula="value / 1000", factor=0.001, precision=0
            )
        }
        self.conversion_rules["platelet_count"] = platelet_rules
    
    def _add_urine_test_conversions(self):
        """添加尿液检查转换规则"""
        # 尿微量白蛋白转换
        microalbumin_rules = {
            "μg/mL_to_mg/L": ConversionRule(
                from_unit="μg/mL", to_unit="mg/L",
                formula="value * 1.0", factor=1.0, precision=1
            ),
            "mg/dL_to_mg/L": ConversionRule(
                from_unit="mg/dL", to_unit="mg/L",
                formula="value * 10", factor=10, precision=1
            )
        }
        self.conversion_rules["microalbumin"] = microalbumin_rules
        
        # 白蛋白/肌酐比转换
        acr_rules = {
            "mg/mmol_to_mg/g": ConversionRule(
                from_unit="mg/mmol", to_unit="mg/g",
                formula="value * 8.84", factor=8.84, precision=1
            ),
            "μg/mg_to_mg/g": ConversionRule(
                from_unit="μg/mg", to_unit="mg/g",
                formula="value / 1000", factor=0.001, precision=1
            )
        }
        self.conversion_rules["albumin_creatinine_ratio"] = acr_rules
    
    def convert_value(self, test_name: str, value: float, from_unit: str, 
                     to_unit: str) -> Tuple[float, Dict[str, Any]]:
        """
        转换检验值单位
        
        Args:
            test_name: 检验项目名称
            value: 原始数值
            from_unit: 原始单位
            to_unit: 目标单位
            
        Returns:
            转换后的数值和元数据字典
            
        Raises:
            ConversionError: 转换失败时抛出
        """
        if from_unit == to_unit:
            return value, {"conversion_applied": False, "original_unit": from_unit}
        
        if test_name not in self.conversion_rules:
            raise ConversionError(f"No conversion rules found for test: {test_name}")
        
        conversion_key = f"{from_unit}_to_{to_unit}"
        if conversion_key not in self.conversion_rules[test_name]:
            raise ConversionError(
                f"No conversion rule from {from_unit} to {to_unit} for {test_name}"
            )
        
        rule = self.conversion_rules[test_name][conversion_key]
        
        try:
            if rule.factor is not None:
                # 使用简单因子转换
                converted_value = value * rule.factor
            else:
                # 使用公式转换
                converted_value = self._evaluate_formula(rule.formula, value)
            
            # 根据精度要求进行四舍五入
            converted_value = round(converted_value, rule.precision)
            
            metadata = {
                "conversion_applied": True,
                "original_value": value,
                "original_unit": from_unit,
                "target_unit": to_unit,
                "conversion_formula": rule.formula,
                "precision": rule.precision
            }
            
            return converted_value, metadata
            
        except Exception as e:
            raise ConversionError(f"Conversion failed: {str(e)}")
    
    def _evaluate_formula(self, formula: str, value: float) -> float:
        """
        安全评估转换公式
        
        Args:
            formula: 转换公式，其中'value'代表输入值
            value: 输入数值
            
        Returns:
            计算结果
        """
        # 允许的数学函数
        allowed_names = {
            "value": value,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
            "sqrt": math.sqrt,
            "exp": math.exp,
            "log": math.log,
            "log10": math.log10,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan
        }
        
        # 创建受限的命名空间
        code = compile(formula, "<string>", "eval")
        
        # 检查代码中是否包含不安全的操作
        for name in code.co_names:
            if name not in allowed_names:
                raise ConversionError(f"Unsafe operation in formula: {name}")
        
        return eval(code, {"__builtins__": {}}, allowed_names)
    
    def validate_value(self, test_name: str, value: float, unit: str,
                      patient_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        验证检验值的生物学合理性
        
        Args:
            test_name: 检验项目名称
            value: 检验值
            unit: 单位
            patient_info: 患者信息（年龄、性别等）
            
        Returns:
            验证结果字典
        """
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "alerts": [],
            "flags": []
        }
        
        # 检查生物学合理范围
        if test_name in self.quality_limits and unit in self.quality_limits[test_name]:
            limits = self.quality_limits[test_name][unit]
            
            # 绝对限制检查
            if limits.absolute_min is not None and value < limits.absolute_min:
                validation_result["is_valid"] = False
                validation_result["alerts"].append(
                    f"Value {value} {unit} below absolute minimum {limits.absolute_min}"
                )
            
            if limits.absolute_max is not None and value > limits.absolute_max:
                validation_result["is_valid"] = False
                validation_result["alerts"].append(
                    f"Value {value} {unit} above absolute maximum {limits.absolute_max}"
                )
            
            # 危急值检查
            if limits.critical_low is not None and value <= limits.critical_low:
                validation_result["flags"].append("CRITICAL_LOW")
            
            if limits.critical_high is not None and value >= limits.critical_high:
                validation_result["flags"].append("CRITICAL_HIGH")
            
            # 恐慌值检查
            if limits.panic_low is not None and value <= limits.panic_low:
                validation_result["flags"].append("PANIC_LOW")
            
            if limits.panic_high is not None and value >= limits.panic_high:
                validation_result["flags"].append("PANIC_HIGH")
        
        # 参考范围检查
        if test_name in self.reference_ranges:
            ref_range = self._get_applicable_reference_range(
                test_name, patient_info or {}
            )
            if ref_range:
                if ref_range.min_value is not None and value < ref_range.min_value:
                    validation_result["flags"].append("BELOW_REFERENCE")
                
                if ref_range.max_value is not None and value > ref_range.max_value:
                    validation_result["flags"].append("ABOVE_REFERENCE")
        
        return validation_result
    
    def _get_applicable_reference_range(self, test_name: str, 
                                      patient_info: Dict) -> Optional[ReferenceRange]:
        """
        获取适用的参考范围
        
        Args:
            test_name: 检验项目名称
            patient_info: 患者信息
            
        Returns:
            适用的参考范围，如果没有找到则返回None
        """
        if test_name not in self.reference_ranges:
            return None
        
        ranges = self.reference_ranges[test_name]
        
        # 简单的匹配逻辑，实际应用中可能需要更复杂的规则
        for ref_range in ranges:
            if self._matches_population(ref_range, patient_info):
                return ref_range
        
        # 如果没有匹配的特定范围，返回通用范围
        for ref_range in ranges:
            if ref_range.population == "general":
                return ref_range
        
        return ranges[0] if ranges else None
    
    def _matches_population(self, ref_range: ReferenceRange, 
                          patient_info: Dict) -> bool:
        """
        检查参考范围是否适用于特定患者
        
        Args:
            ref_range: 参考范围
            patient_info: 患者信息
            
        Returns:
            是否匹配
        """
        # 性别匹配
        if ref_range.gender != "both":
            if patient_info.get("gender") != ref_range.gender:
                return False
        
        # 年龄组匹配
        patient_age = patient_info.get("age")
        if patient_age is not None:
            age_group = self._classify_age_group(patient_age)
            if ref_range.age_group != "all" and age_group != ref_range.age_group:
                return False
        
        # 疾病状态匹配
        if ref_range.condition:
            patient_conditions = patient_info.get("conditions", [])
            if ref_range.condition not in patient_conditions:
                return False
        
        return True
    
    def _classify_age_group(self, age: int) -> str:
        """
        根据年龄分类年龄组
        
        Args:
            age: 年龄
            
        Returns:
            年龄组分类
        """
        if age < 18:
            return "pediatric"
        elif age < 65:
            return "adult"
        else:
            return "elderly"
    
    def batch_convert(self, test_data: List[Dict]) -> List[Dict]:
        """
        批量转换检验数据
        
        Args:
            test_data: 检验数据列表，每个元素包含test_name, value, from_unit, to_unit等字段
            
        Returns:
            转换结果列表
        """
        results = []
        
        for data in test_data:
            try:
                converted_value, metadata = self.convert_value(
                    data["test_name"],
                    data["value"], 
                    data["from_unit"],
                    data["to_unit"]
                )
                
                validation_result = self.validate_value(
                    data["test_name"],
                    converted_value,
                    data["to_unit"],
                    data.get("patient_info")
                )
                
                result = {
                    **data,
                    "converted_value": converted_value,
                    "conversion_metadata": metadata,
                    "validation_result": validation_result
                }
                
            except (ConversionError, ValidationError) as e:
                result = {
                    **data,
                    "error": str(e),
                    "conversion_failed": True
                }
            
            results.append(result)
        
        return results
    
    def get_supported_conversions(self, test_name: str) -> Dict[str, List[str]]:
        """
        获取指定检验项目支持的单位转换
        
        Args:
            test_name: 检验项目名称
            
        Returns:
            支持的转换关系字典
        """
        if test_name not in self.conversion_rules:
            return {}
        
        conversions = {}
        for conversion_key in self.conversion_rules[test_name].keys():
            from_unit, to_unit = conversion_key.split("_to_")
            if from_unit not in conversions:
                conversions[from_unit] = []
            conversions[from_unit].append(to_unit)
        
        return conversions
    
    def load_config(self, config_file: str):
        """
        从配置文件加载转换规则
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 解析转换规则
            if "conversion_rules" in config:
                for test_name, rules in config["conversion_rules"].items():
                    self.conversion_rules[test_name] = {}
                    for rule_key, rule_data in rules.items():
                        self.conversion_rules[test_name][rule_key] = ConversionRule(
                            **rule_data
                        )
            
            # 解析质量控制限制
            if "quality_limits" in config:
                for test_name, limits in config["quality_limits"].items():
                    self.quality_limits[test_name] = {}
                    for unit, limit_data in limits.items():
                        self.quality_limits[test_name][unit] = QualityControlLimits(
                            **limit_data
                        )
            
            # 解析参考范围
            if "reference_ranges" in config:
                for test_name, ranges in config["reference_ranges"].items():
                    self.reference_ranges[test_name] = [
                        ReferenceRange(**range_data) for range_data in ranges
                    ]
            
            logger.info(f"Configuration loaded successfully from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise


def main():
    """主函数，演示用法"""
    # 创建转换器实例
    converter = LabTestConverter()
    
    # 示例：血糖转换
    try:
        glucose_mgdl = 126  # mg/dL
        glucose_mmol, metadata = converter.convert_value(
            "glucose", glucose_mgdl, "mg/dL", "mmol/L"
        )
        print(f"血糖: {glucose_mgdl} mg/dL = {glucose_mmol} mmol/L")
        print(f"转换元数据: {metadata}")
        
        # 验证转换后的值
        validation = converter.validate_value("glucose", glucose_mmol, "mmol/L")
        print(f"验证结果: {validation}")
        
    except ConversionError as e:
        print(f"转换错误: {e}")
    
    # 示例：批量转换
    test_data = [
        {
            "test_name": "glucose",
            "value": 126,
            "from_unit": "mg/dL",
            "to_unit": "mmol/L",
            "patient_info": {"age": 45, "gender": "male"}
        },
        {
            "test_name": "creatinine", 
            "value": 1.2,
            "from_unit": "mg/dL",
            "to_unit": "μmol/L",
            "patient_info": {"age": 60, "gender": "female"}
        }
    ]
    
    results = converter.batch_convert(test_data)
    print("\n批量转换结果:")
    for result in results:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 示例：查看支持的转换
    print(f"\n血糖支持的转换: {converter.get_supported_conversions('glucose')}")


if __name__ == "__main__":
    main()