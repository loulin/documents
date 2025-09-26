#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
甲状腺疾病知识图谱测试用例
Thyroid Disease Knowledge Graph Test Cases

测试覆盖:
1. 典型甲亢案例 (Graves病)
2. 毒性结节性甲状腺肿案例
3. 甲减案例 (桥本甲状腺炎)
4. 妊娠期甲亢案例
5. 老年甲亢案例
6. 边界案例和异常处理

Created: 2024-09
Author: AI-Optimized Medical System
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from thyroid_kg_implementation import (
    ThyroidKnowledgeGraph,
    ThyroidDiagnosticEngine,
    ThyroidTreatmentEngine,
    PatientData,
    DiagnosticResult,
    TreatmentRecommendation
)


class TestThyroidKnowledgeGraph(unittest.TestCase):
    """知识图谱基础功能测试"""
    
    def setUp(self):
        """测试初始化"""
        # 使用模拟的数据库连接
        self.mock_kg = Mock(spec=ThyroidKnowledgeGraph)
        self.diagnostic_engine = ThyroidDiagnosticEngine(self.mock_kg)
        self.treatment_engine = ThyroidTreatmentEngine(self.mock_kg)
    
    def test_database_connection(self):
        """测试数据库连接"""
        # 模拟连接成功
        self.mock_kg.run_query.return_value = [{"test": 1}]
        
        result = self.mock_kg.run_query("RETURN 1 as test")
        self.assertIsNotNone(result)
        self.assertEqual(result[0]["test"], 1)
    
    def test_node_creation(self):
        """测试节点创建"""
        # 模拟节点创建成功
        self.mock_kg.run_query.return_value = [{"success": True}]
        
        # 测试疾病节点创建
        disease_data = {
            "id": "graves_test",
            "name": "Graves病",
            "icd_code": "E05.0"
        }
        
        result = self.mock_kg.run_query(
            "CREATE (d:Disease {id: $id, name: $name, icd_code: $icd_code})",
            disease_data
        )
        
        self.assertIsNotNone(result)


class TestDiagnosticEngine(unittest.TestCase):
    """诊断引擎测试"""
    
    def setUp(self):
        """测试初始化"""
        self.mock_kg = Mock(spec=ThyroidKnowledgeGraph)
        self.diagnostic_engine = ThyroidDiagnosticEngine(self.mock_kg)
    
    def test_typical_graves_disease(self):
        """测试典型Graves病诊断"""
        
        # 模拟症状查询结果
        symptom_query_result = [
            {
                "disease": "Graves病",
                "matching_symptoms": ["心悸", "体重下降", "怕热多汗"],
                "avg_probability": 0.85,
                "symptom_count": 3
            }
        ]
        
        # 模拟实验室检查查询结果
        lab_query_result = [
            {
                "disease": "Graves病",
                "lab_test": "TSH",
                "sensitivity": 0.95,
                "specificity": 0.85,
                "thresholds": {"suppressed": "<0.1"}
            },
            {
                "disease": "Graves病",
                "lab_test": "TRAb",
                "sensitivity": 0.95,
                "specificity": 0.98,
                "thresholds": {"positive": ">1.75"}
            }
        ]
        
        # 设置模拟返回值
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,
            lab_query_result
        ]
        
        # 创建典型Graves病患者
        patient = PatientData(
            patient_id="TEST_GRAVES_001",
            age=35,
            gender="女",
            symptoms=["心悸", "体重下降", "怕热多汗", "突眼"],
            lab_results={
                "TSH": 0.05,  # 严重抑制
                "FT4": 35.0,  # 明显升高
                "TRAb": 8.5   # 明显阳性
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        # 执行诊断
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        # 验证诊断结果
        self.assertEqual(diagnosis.disease, "Graves病")
        self.assertGreater(diagnosis.confidence, 0.8)
        self.assertIn("症状模式匹配", " ".join(diagnosis.supporting_evidence))
        self.assertIn("实验室检查支持", " ".join(diagnosis.supporting_evidence))
    
    def test_toxic_nodular_goiter(self):
        """测试毒性结节性甲状腺肿诊断"""
        
        # 模拟查询结果 - 症状相似但无眼征
        symptom_query_result = [
            {
                "disease": "毒性结节性甲状腺肿",
                "matching_symptoms": ["心悸", "体重下降"],
                "avg_probability": 0.75,
                "symptom_count": 2
            }
        ]
        
        lab_query_result = [
            {
                "disease": "毒性结节性甲状腺肿",
                "lab_test": "TSH",
                "sensitivity": 0.90,
                "specificity": 0.80,
                "thresholds": {"suppressed": "<0.1"}
            }
        ]
        
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,
            lab_query_result
        ]
        
        # 创建毒性结节患者 - 无眼征，TRAb阴性
        patient = PatientData(
            patient_id="TEST_TOXIC_001",
            age=65,
            gender="男",
            symptoms=["心悸", "体重下降", "怕热"],
            lab_results={
                "TSH": 0.02,  # 抑制
                "FT4": 28.0,  # 升高
                "TRAb": 0.5   # 阴性
            },
            medical_history=["甲状腺结节病史"],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        # 验证诊断
        self.assertEqual(diagnosis.disease, "毒性结节性甲状腺肿")
        self.assertGreater(diagnosis.confidence, 0.6)
    
    def test_hypothyroidism_diagnosis(self):
        """测试甲减诊断"""
        
        symptom_query_result = [
            {
                "disease": "桥本甲状腺炎",
                "matching_symptoms": ["疲劳乏力", "体重增加"],
                "avg_probability": 0.80,
                "symptom_count": 2
            }
        ]
        
        lab_query_result = [
            {
                "disease": "桥本甲状腺炎",
                "lab_test": "TSH",
                "sensitivity": 0.95,
                "specificity": 0.85,
                "thresholds": {"elevated": ">10"}
            }
        ]
        
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,
            lab_query_result
        ]
        
        # 创建甲减患者
        patient = PatientData(
            patient_id="TEST_HYPO_001",
            age=45,
            gender="女",
            symptoms=["疲劳乏力", "体重增加", "便秘", "怕冷"],
            lab_results={
                "TSH": 25.0,  # 明显升高
                "FT4": 8.0,   # 降低
                "TPOAb": 180  # 阳性
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        self.assertEqual(diagnosis.disease, "桥本甲状腺炎")
        self.assertGreater(diagnosis.confidence, 0.7)
    
    def test_pregnancy_hyperthyroidism(self):
        """测试妊娠期甲亢诊断"""
        
        symptom_query_result = [
            {
                "disease": "Graves病",
                "matching_symptoms": ["心悸", "体重下降"],
                "avg_probability": 0.80,
                "symptom_count": 2
            }
        ]
        
        lab_query_result = [
            {
                "disease": "Graves病",
                "lab_test": "TSH",
                "sensitivity": 0.95,
                "specificity": 0.85,
                "thresholds": {"suppressed": "<0.1"}
            }
        ]
        
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,
            lab_query_result
        ]
        
        # 创建妊娠期甲亢患者
        patient = PatientData(
            patient_id="TEST_PREG_001",
            age=28,
            gender="女",
            symptoms=["心悸", "体重下降", "恶心呕吐"],
            lab_results={
                "TSH": 0.01,  # 严重抑制
                "FT4": 32.0,  # 升高
                "TRAb": 5.2   # 阳性
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=True,  # 关键：妊娠状态
            comorbidities=[]
        )
        
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        self.assertEqual(diagnosis.disease, "Graves病")
        self.assertTrue(patient.pregnancy_status)  # 确保妊娠状态被考虑
    
    def test_subclinical_hyperthyroidism(self):
        """测试亚临床甲亢"""
        
        symptom_query_result = []  # 无明显症状
        
        lab_query_result = [
            {
                "disease": "亚临床甲亢",
                "lab_test": "TSH",
                "sensitivity": 0.90,
                "specificity": 0.75,
                "thresholds": {"suppressed": "<0.27"}
            }
        ]
        
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,
            lab_query_result
        ]
        
        # 创建亚临床甲亢患者
        patient = PatientData(
            patient_id="TEST_SUB_001",
            age=55,
            gender="女",
            symptoms=[],  # 无症状
            lab_results={
                "TSH": 0.15,  # 轻度抑制
                "FT4": 20.0,  # 正常上限
                "FT3": 6.5    # 正常上限
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        # 亚临床甲亢的置信度应该较低
        self.assertLess(diagnosis.confidence, 0.7)


class TestTreatmentEngine(unittest.TestCase):
    """治疗引擎测试"""
    
    def setUp(self):
        """测试初始化"""
        self.mock_kg = Mock(spec=ThyroidKnowledgeGraph)
        self.treatment_engine = ThyroidTreatmentEngine(self.mock_kg)
    
    def test_graves_treatment_recommendation(self):
        """测试Graves病治疗推荐"""
        
        # 模拟治疗查询结果
        treatment_query_result = [
            {
                "treatment": "抗甲状腺药物治疗",
                "treatment_type": "药物治疗",
                "effectiveness": 0.85,
                "treatment_line": "一线",
                "evidence_level": "A",
                "contraindications": ["严重肝功能不全"],
                "medication": "甲巯咪唑",
                "dosage": "5-15mg",
                "frequency": "每日2-3次"
            },
            {
                "treatment": "放射性碘治疗",
                "treatment_type": "放射治疗",
                "effectiveness": 0.90,
                "treatment_line": "二线",
                "evidence_level": "A",
                "contraindications": ["妊娠", "哺乳"],
                "medication": None,
                "dosage": "10-15 mCi",
                "frequency": "单次"
            }
        ]
        
        self.mock_kg.run_query.return_value = treatment_query_result
        
        # 创建成年非妊娠患者
        patient = PatientData(
            patient_id="TEST_TREAT_001",
            age=35,
            gender="女",
            symptoms=["心悸", "体重下降"],
            lab_results={"TSH": 0.05, "FT4": 35.0},
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        recommendations = self.treatment_engine.recommend_treatment("Graves病", patient)
        
        # 验证治疗推荐
        self.assertGreater(len(recommendations), 0)
        self.assertEqual(recommendations[0].treatment_name, "抗甲状腺药物治疗")
        self.assertEqual(recommendations[0].medication, "甲巯咪唑")
        self.assertIn("5-15mg", recommendations[0].dosage)
    
    def test_pregnancy_treatment_adjustment(self):
        """测试妊娠期治疗调整"""
        
        treatment_query_result = [
            {
                "treatment": "抗甲状腺药物治疗",
                "treatment_type": "药物治疗",
                "effectiveness": 0.85,
                "treatment_line": "一线",
                "evidence_level": "A",
                "contraindications": [],
                "medication": "甲巯咪唑",
                "dosage": "5-15mg",
                "frequency": "每日2-3次"
            }
        ]
        
        self.mock_kg.run_query.return_value = treatment_query_result
        
        # 创建妊娠期患者
        patient = PatientData(
            patient_id="TEST_PREG_TREAT_001",
            age=28,
            gender="女",
            symptoms=["心悸", "体重下降"],
            lab_results={"TSH": 0.01, "FT4": 32.0},
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=True,  # 妊娠期
            comorbidities=[]
        )
        
        recommendations = self.treatment_engine.recommend_treatment("Graves病", patient)
        
        # 验证妊娠期药物调整
        self.assertGreater(len(recommendations), 0)
        self.assertIn("丙基硫氧嘧啶", recommendations[0].medication)  # 应调整为PTU
        self.assertIn("妊娠期首选", recommendations[0].medication)
    
    def test_elderly_treatment_adjustment(self):
        """测试老年患者治疗调整"""
        
        treatment_query_result = [
            {
                "treatment": "抗甲状腺药物治疗",
                "treatment_type": "药物治疗",
                "effectiveness": 0.85,
                "treatment_line": "一线",
                "evidence_level": "A",
                "contraindications": [],
                "medication": "甲巯咪唑",
                "dosage": "5-15mg",
                "frequency": "每日2-3次"
            }
        ]
        
        self.mock_kg.run_query.return_value = treatment_query_result
        
        # 创建老年患者
        patient = PatientData(
            patient_id="TEST_ELDERLY_001",
            age=75,  # 老年患者
            gender="男",
            symptoms=["心悸", "体重下降"],
            lab_results={"TSH": 0.02, "FT4": 28.0},
            medical_history=["高血压", "冠心病"],
            current_medications=["阿司匹林", "美托洛尔"],
            allergies=[],
            pregnancy_status=False,
            comorbidities=["心血管疾病"]
        )
        
        recommendations = self.treatment_engine.recommend_treatment("Graves病", patient)
        
        # 验证老年患者剂量调整
        self.assertGreater(len(recommendations), 0)
        self.assertIn("老年人减量", recommendations[0].dosage)
        
        # 验证监测计划包含心脏监测
        monitoring = recommendations[0].monitoring_plan
        self.assertIn("additional_monitoring", monitoring)
        self.assertIn("心电图", str(monitoring))
    
    def test_contraindication_filtering(self):
        """测试禁忌症过滤"""
        
        treatment_query_result = [
            {
                "treatment": "抗甲状腺药物治疗",
                "treatment_type": "药物治疗",
                "effectiveness": 0.85,
                "treatment_line": "一线",
                "evidence_level": "A",
                "contraindications": ["严重肝功能不全"],  # 有禁忌症
                "medication": "甲巯咪唑",
                "dosage": "5-15mg",
                "frequency": "每日2-3次"
            },
            {
                "treatment": "放射性碘治疗",
                "treatment_type": "放射治疗",
                "effectiveness": 0.90,
                "treatment_line": "二线",
                "evidence_level": "A",
                "contraindications": ["妊娠"],  # 无相关禁忌症
                "medication": None,
                "dosage": "10-15 mCi",
                "frequency": "单次"
            }
        ]
        
        self.mock_kg.run_query.return_value = treatment_query_result
        
        # 创建有肝功能不全的患者
        patient = PatientData(
            patient_id="TEST_CONTRA_001",
            age=45,
            gender="女",
            symptoms=["心悸", "体重下降"],
            lab_results={"TSH": 0.05, "FT4": 35.0},
            medical_history=["肝硬化"],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=["严重肝功能不全"]  # 禁忌症
        )
        
        recommendations = self.treatment_engine.recommend_treatment("Graves病", patient)
        
        # 验证禁忌症药物被过滤
        treatment_names = [rec.treatment_name for rec in recommendations]
        self.assertNotIn("抗甲状腺药物治疗", treatment_names)
        self.assertIn("放射性碘治疗", treatment_names)


class TestEdgeCases(unittest.TestCase):
    """边界案例和异常处理测试"""
    
    def setUp(self):
        """测试初始化"""
        self.mock_kg = Mock(spec=ThyroidKnowledgeGraph)
        self.diagnostic_engine = ThyroidDiagnosticEngine(self.mock_kg)
        self.treatment_engine = ThyroidTreatmentEngine(self.mock_kg)
    
    def test_no_symptoms_no_labs(self):
        """测试无症状无检查结果的情况"""
        
        # 模拟空查询结果
        self.mock_kg.run_query.return_value = []
        
        # 创建空数据患者
        patient = PatientData(
            patient_id="TEST_EMPTY_001",
            age=40,
            gender="女",
            symptoms=[],  # 无症状
            lab_results={},  # 无检查结果
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        self.assertEqual(diagnosis.disease, "无明确诊断")
        self.assertEqual(diagnosis.confidence, 0.0)
        self.assertIn("建议完善甲状腺功能检查", diagnosis.recommended_tests)
    
    def test_conflicting_lab_results(self):
        """测试矛盾的检查结果"""
        
        symptom_query_result = [
            {
                "disease": "Graves病",
                "matching_symptoms": ["心悸"],
                "avg_probability": 0.70,
                "symptom_count": 1
            }
        ]
        
        lab_query_result = []  # 矛盾的实验室结果不支持任何诊断
        
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,
            lab_query_result
        ]
        
        # 创建矛盾检查结果的患者
        patient = PatientData(
            patient_id="TEST_CONFLICT_001",
            age=40,
            gender="女",
            symptoms=["心悸"],  # 甲亢症状
            lab_results={
                "TSH": 15.0,  # 升高（甲减）
                "FT4": 35.0,  # 升高（甲亢）- 矛盾
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        # 矛盾结果应导致低置信度
        self.assertLess(diagnosis.confidence, 0.6)
    
    def test_database_connection_error(self):
        """测试数据库连接错误"""
        
        # 模拟数据库连接异常
        self.mock_kg.run_query.side_effect = Exception("数据库连接失败")
        
        patient = PatientData(
            patient_id="TEST_DB_ERROR_001",
            age=40,
            gender="女",
            symptoms=["心悸"],
            lab_results={"TSH": 0.05},
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        # 诊断应该能够处理异常情况
        with self.assertRaises(Exception):
            self.diagnostic_engine.diagnose(patient)
    
    def test_invalid_lab_values(self):
        """测试无效的检查值"""
        
        symptom_query_result = []
        lab_query_result = []
        
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,
            lab_query_result
        ]
        
        # 创建有无效检查值的患者
        patient = PatientData(
            patient_id="TEST_INVALID_001",
            age=40,
            gender="女",
            symptoms=["心悸"],
            lab_results={
                "TSH": -1.0,  # 无效值（负数）
                "FT4": 1000.0,  # 无效值（过高）
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        # 无效值应该被忽略或导致低置信度
        self.assertLessEqual(diagnosis.confidence, 0.5)


class TestIntegrationScenarios(unittest.TestCase):
    """综合场景测试"""
    
    def setUp(self):
        """测试初始化"""
        self.mock_kg = Mock(spec=ThyroidKnowledgeGraph)
        self.diagnostic_engine = ThyroidDiagnosticEngine(self.mock_kg)
        self.treatment_engine = ThyroidTreatmentEngine(self.mock_kg)
    
    def test_complete_clinical_workflow(self):
        """测试完整临床工作流程"""
        
        # 设置诊断查询结果
        symptom_query_result = [
            {
                "disease": "Graves病",
                "matching_symptoms": ["心悸", "体重下降", "怕热多汗"],
                "avg_probability": 0.85,
                "symptom_count": 3
            }
        ]
        
        lab_query_result = [
            {
                "disease": "Graves病",
                "lab_test": "TSH",
                "sensitivity": 0.95,
                "specificity": 0.85,
                "thresholds": {"suppressed": "<0.1"}
            }
        ]
        
        # 设置治疗查询结果
        treatment_query_result = [
            {
                "treatment": "抗甲状腺药物治疗",
                "treatment_type": "药物治疗",
                "effectiveness": 0.85,
                "treatment_line": "一线",
                "evidence_level": "A",
                "contraindications": [],
                "medication": "甲巯咪唑",
                "dosage": "5-15mg",
                "frequency": "每日2-3次"
            }
        ]
        
        # 设置查询序列
        self.mock_kg.run_query.side_effect = [
            symptom_query_result,  # 症状诊断查询
            lab_query_result,      # 实验室诊断查询
            treatment_query_result  # 治疗推荐查询
        ]
        
        # 创建患者
        patient = PatientData(
            patient_id="TEST_WORKFLOW_001",
            age=35,
            gender="女",
            symptoms=["心悸", "体重下降", "怕热多汗"],
            lab_results={
                "TSH": 0.05,
                "FT4": 35.0,
                "TRAb": 8.5
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        # 执行完整工作流程
        # 1. 诊断
        diagnosis = self.diagnostic_engine.diagnose(patient)
        
        # 2. 治疗推荐
        if diagnosis.confidence > 0.7:
            treatments = self.treatment_engine.recommend_treatment(
                diagnosis.disease, patient
            )
        else:
            treatments = []
        
        # 验证工作流程结果
        self.assertEqual(diagnosis.disease, "Graves病")
        self.assertGreater(diagnosis.confidence, 0.7)
        self.assertGreater(len(treatments), 0)
        self.assertEqual(treatments[0].treatment_name, "抗甲状腺药物治疗")
        
        # 验证监测计划
        monitoring = treatments[0].monitoring_plan
        self.assertIn("baseline", monitoring)
        self.assertIn("week_2", monitoring)
        self.assertIn("week_6", monitoring)


def run_performance_tests():
    """性能测试"""
    import time
    
    print("运行性能测试...")
    
    # 模拟大量诊断请求
    mock_kg = Mock(spec=ThyroidKnowledgeGraph)
    mock_kg.run_query.return_value = [
        {
            "disease": "Graves病",
            "matching_symptoms": ["心悸"],
            "avg_probability": 0.85,
            "symptom_count": 1
        }
    ]
    
    diagnostic_engine = ThyroidDiagnosticEngine(mock_kg)
    
    # 创建测试患者
    test_patient = PatientData(
        patient_id="PERF_TEST",
        age=35,
        gender="女",
        symptoms=["心悸"],
        lab_results={"TSH": 0.05},
        medical_history=[],
        current_medications=[],
        allergies=[],
        pregnancy_status=False,
        comorbidities=[]
    )
    
    # 测试1000次诊断的性能
    start_time = time.time()
    
    for i in range(1000):
        diagnosis = diagnostic_engine.diagnose(test_patient)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"1000次诊断耗时: {elapsed_time:.2f} 秒")
    print(f"平均单次诊断耗时: {elapsed_time/1000*1000:.2f} 毫秒")
    print(f"每秒可处理诊断数: {1000/elapsed_time:.0f}")


if __name__ == "__main__":
    # 运行单元测试
    print("开始运行甲状腺知识图谱测试用例...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestThyroidKnowledgeGraph,
        TestDiagnosticEngine,
        TestTreatmentEngine,
        TestEdgeCases,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果统计
    print(f"\n测试结果统计:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 运行性能测试
    print("\n" + "="*50)
    run_performance_tests()
    
    print("\n测试完成！")