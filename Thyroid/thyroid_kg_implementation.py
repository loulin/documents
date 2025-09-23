#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
甲状腺疾病诊断-治疗知识图谱实现代码
Thyroid Disease Diagnosis-Treatment Knowledge Graph Implementation

Created: 2024-09
Author: AI-Optimized Medical System
"""

from neo4j import GraphDatabase
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Severity(Enum):
    """疾病严重程度枚举"""
    MILD = "轻度"
    MODERATE = "中度"
    SEVERE = "重度"
    CRITICAL = "危重"


class TreatmentLine(Enum):
    """治疗线枚举"""
    FIRST = "一线"
    SECOND = "二线"
    THIRD = "三线"
    RESCUE = "抢救"


@dataclass
class PatientData:
    """患者数据结构"""
    patient_id: str
    age: int
    gender: str
    symptoms: List[str]
    lab_results: Dict[str, float]
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    pregnancy_status: bool = False
    comorbidities: List[str] = None


@dataclass
class DiagnosticResult:
    """诊断结果数据结构"""
    disease: str
    confidence: float
    supporting_evidence: List[str]
    differential_diagnosis: List[str]
    recommended_tests: List[str]


@dataclass
class TreatmentRecommendation:
    """治疗建议数据结构"""
    treatment_name: str
    medication: str
    dosage: str
    duration: str
    monitoring_plan: Dict[str, Any]
    contraindications: List[str]
    success_probability: float


class ThyroidKnowledgeGraph:
    """甲状腺知识图谱核心类"""
    
    def __init__(self, uri: str, user: str, password: str):
        """初始化知识图谱连接"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = None
        
    def __enter__(self):
        self.session = self.driver.session()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
        self.driver.close()
    
    def run_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """执行Cypher查询"""
        try:
            result = self.session.run(query, parameters or {})
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            return []
    
    def initialize_knowledge_base(self):
        """初始化知识库数据"""
        logger.info("开始初始化甲状腺知识图谱...")
        
        # 创建索引
        self._create_indexes()
        
        # 创建疾病实体
        self._create_diseases()
        
        # 创建症状实体
        self._create_symptoms()
        
        # 创建实验室检查实体
        self._create_lab_tests()
        
        # 创建药物实体
        self._create_medications()
        
        # 创建治疗方案实体
        self._create_treatments()
        
        # 建立关系
        self._create_relationships()
        
        logger.info("知识图谱初始化完成")
    
    def _create_indexes(self):
        """创建数据库索引"""
        indexes = [
            "CREATE INDEX disease_name IF NOT EXISTS FOR (d:Disease) ON (d.name)",
            "CREATE INDEX symptom_name IF NOT EXISTS FOR (s:Symptom) ON (s.name)",
            "CREATE INDEX medication_name IF NOT EXISTS FOR (m:Medication) ON (m.name)",
            "CREATE INDEX lab_test_name IF NOT EXISTS FOR (l:LabTest) ON (l.name)",
            "CREATE INDEX treatment_name IF NOT EXISTS FOR (t:Treatment) ON (t.name)"
        ]
        
        for index in indexes:
            try:
                self.session.run(index)
                logger.info(f"索引创建成功: {index}")
            except Exception as e:
                logger.warning(f"索引创建失败: {e}")
    
    def _create_diseases(self):
        """创建疾病实体"""
        diseases = [
            {
                "id": "graves_disease",
                "name": "Graves病",
                "icd_code": "E05.0",
                "category": "甲状腺功能亢进",
                "prevalence": 0.008,
                "autoimmune": True,
                "description": "最常见的甲状腺功能亢进症，由TRAb刺激TSH受体引起"
            },
            {
                "id": "toxic_nodular_goiter",
                "name": "毒性结节性甲状腺肿",
                "icd_code": "E05.1",
                "category": "甲状腺功能亢进",
                "prevalence": 0.002,
                "autoimmune": False,
                "description": "甲状腺结节自主分泌甲状腺激素导致的甲亢"
            },
            {
                "id": "hashimoto_thyroiditis",
                "name": "桥本甲状腺炎",
                "icd_code": "E06.3",
                "category": "甲状腺功能减退",
                "prevalence": 0.035,
                "autoimmune": True,
                "description": "最常见的甲状腺功能减退症，自身免疫性甲状腺炎"
            }
        ]
        
        for disease in diseases:
            query = """
            CREATE (d:Disease {
                id: $id,
                name: $name,
                icd_code: $icd_code,
                category: $category,
                prevalence: $prevalence,
                autoimmune: $autoimmune,
                description: $description
            })
            """
            self.session.run(query, disease)
            logger.info(f"疾病创建成功: {disease['name']}")
    
    def _create_symptoms(self):
        """创建症状实体"""
        symptoms = [
            {
                "id": "palpitation",
                "name": "心悸",
                "category": "心血管症状",
                "frequency_in_hyperthyroid": 0.85,
                "severity_correlation": 0.7,
                "measurement": "心率>100次/分",
                "differential_weight": 0.6
            },
            {
                "id": "weight_loss",
                "name": "体重下降",
                "category": "代谢症状",
                "frequency_in_hyperthyroid": 0.90,
                "severity_correlation": 0.8,
                "measurement": "3个月内体重下降>10%",
                "differential_weight": 0.8
            },
            {
                "id": "heat_intolerance",
                "name": "怕热多汗",
                "category": "代谢症状",
                "frequency_in_hyperthyroid": 0.80,
                "severity_correlation": 0.7,
                "measurement": "主观评分+出汗量",
                "differential_weight": 0.7
            },
            {
                "id": "exophthalmos",
                "name": "突眼",
                "category": "眼部症状",
                "frequency_in_graves": 0.50,
                "specificity": 0.95,
                "measurement": "眼球突出度>20mm",
                "differential_weight": 0.9
            },
            {
                "id": "fatigue",
                "name": "疲劳乏力",
                "category": "全身症状",
                "frequency_in_hypothyroid": 0.95,
                "severity_correlation": 0.6,
                "differential_weight": 0.4
            }
        ]
        
        for symptom in symptoms:
            query = """
            CREATE (s:Symptom {
                id: $id,
                name: $name,
                category: $category,
                frequency_in_hyperthyroid: $frequency_in_hyperthyroid,
                severity_correlation: $severity_correlation,
                measurement: $measurement,
                differential_weight: $differential_weight
            })
            """
            self.session.run(query, symptom)
            logger.info(f"症状创建成功: {symptom['name']}")
    
    def _create_lab_tests(self):
        """创建实验室检查实体"""
        lab_tests = [
            {
                "id": "tsh",
                "name": "TSH",
                "full_name": "促甲状腺激素",
                "normal_range": "0.27-4.2 mIU/L",
                "suppressed_threshold": 0.1,
                "elevated_threshold": 10.0,
                "sensitivity": 0.95,
                "specificity": 0.85,
                "cost": 25.0,
                "turnaround_time": "2-4小时"
            },
            {
                "id": "ft4",
                "name": "FT4",
                "full_name": "游离甲状腺素",
                "normal_range": "12-22 pmol/L",
                "elevated_threshold": 25.0,
                "suppressed_threshold": 10.0,
                "sensitivity": 0.90,
                "specificity": 0.88,
                "cost": 35.0,
                "turnaround_time": "2-4小时"
            },
            {
                "id": "trab",
                "name": "TRAb",
                "full_name": "TSH受体抗体",
                "normal_range": "<1.75 IU/L",
                "positive_threshold": 1.75,
                "sensitivity": 0.95,
                "specificity": 0.98,
                "cost": 120.0,
                "turnaround_time": "1-2天"
            }
        ]
        
        for test in lab_tests:
            query = """
            CREATE (l:LabTest {
                id: $id,
                name: $name,
                full_name: $full_name,
                normal_range: $normal_range,
                sensitivity: $sensitivity,
                specificity: $specificity,
                cost: $cost,
                turnaround_time: $turnaround_time
            })
            """
            self.session.run(query, test)
            logger.info(f"检查项目创建成功: {test['name']}")
    
    def _create_medications(self):
        """创建药物实体"""
        medications = [
            {
                "id": "methimazole",
                "name": "甲巯咪唑",
                "generic_name": "Methimazole",
                "brand_names": ["赛治", "他巴唑"],
                "drug_class": "抗甲状腺药物",
                "mechanism": "抑制甲状腺过氧化物酶",
                "bioavailability": 0.93,
                "half_life": "4-6小时",
                "pregnancy_category": "D",
                "lactation_safety": "相对安全",
                "common_doses": [2.5, 5, 10, 15, 20]
            },
            {
                "id": "propylthiouracil",
                "name": "丙基硫氧嘧啶",
                "generic_name": "Propylthiouracil",
                "brand_names": ["丙嘧"],
                "drug_class": "抗甲状腺药物",
                "mechanism": "抑制甲状腺过氧化物酶+阻断T4转T3",
                "bioavailability": 0.75,
                "half_life": "1-2小时",
                "pregnancy_category": "D",
                "lactation_safety": "首选",
                "common_doses": [50, 100, 150, 200]
            }
        ]
        
        for med in medications:
            query = """
            CREATE (m:Medication {
                id: $id,
                name: $name,
                generic_name: $generic_name,
                brand_names: $brand_names,
                drug_class: $drug_class,
                mechanism: $mechanism,
                bioavailability: $bioavailability,
                half_life: $half_life,
                pregnancy_category: $pregnancy_category,
                lactation_safety: $lactation_safety,
                common_doses: $common_doses
            })
            """
            self.session.run(query, med)
            logger.info(f"药物创建成功: {med['name']}")
    
    def _create_treatments(self):
        """创建治疗方案实体"""
        treatments = [
            {
                "id": "ati_treatment",
                "name": "抗甲状腺药物治疗",
                "type": "药物治疗",
                "first_line": True,
                "success_rate": 0.75,
                "duration": "18-24个月",
                "recurrence_rate": 0.25,
                "contraindications": ["严重肝功能不全", "白细胞减少"]
            },
            {
                "id": "rai_treatment",
                "name": "放射性碘治疗",
                "type": "放射治疗",
                "first_line": False,
                "success_rate": 0.90,
                "duration": "单次治疗",
                "hypothyroidism_risk": 0.80,
                "contraindications": ["妊娠", "哺乳", "活动性眼病"]
            }
        ]
        
        for treatment in treatments:
            query = """
            CREATE (t:Treatment {
                id: $id,
                name: $name,
                type: $type,
                first_line: $first_line,
                success_rate: $success_rate,
                duration: $duration,
                contraindications: $contraindications
            })
            """
            self.session.run(query, treatment)
            logger.info(f"治疗方案创建成功: {treatment['name']}")
    
    def _create_relationships(self):
        """建立实体间关系"""
        logger.info("开始建立实体关系...")
        
        # 症状-疾病关系
        symptom_disease_relations = [
            ("心悸", "Graves病", 0.85, "早期"),
            ("体重下降", "Graves病", 0.90, "早期"),
            ("怕热多汗", "Graves病", 0.80, "早期"),
            ("突眼", "Graves病", 0.50, "中晚期"),
            ("疲劳乏力", "桥本甲状腺炎", 0.95, "早期")
        ]
        
        for symptom, disease, probability, timing in symptom_disease_relations:
            query = """
            MATCH (s:Symptom {name: $symptom})
            MATCH (d:Disease {name: $disease})
            CREATE (s)-[:INDICATES {
                probability: $probability,
                timing: $timing,
                specificity: "moderate"
            }]->(d)
            """
            self.session.run(query, {
                "symptom": symptom,
                "disease": disease,
                "probability": probability,
                "timing": timing
            })
        
        # 检查-疾病关系
        lab_disease_relations = [
            ("TSH", "Graves病", 0.95, 0.85, {"suppressed": "<0.1"}),
            ("FT4", "Graves病", 0.90, 0.88, {"elevated": ">25"}),
            ("TRAb", "Graves病", 0.95, 0.98, {"positive": ">1.75"})
        ]
        
        for lab, disease, sensitivity, specificity, thresholds in lab_disease_relations:
            query = """
            MATCH (l:LabTest {name: $lab})
            MATCH (d:Disease {name: $disease})
            CREATE (l)-[:DIAGNOSES {
                sensitivity: $sensitivity,
                specificity: $specificity,
                thresholds: $thresholds
            }]->(d)
            """
            self.session.run(query, {
                "lab": lab,
                "disease": disease,
                "sensitivity": sensitivity,
                "specificity": specificity,
                "thresholds": thresholds
            })
        
        # 疾病-治疗关系
        disease_treatment_relations = [
            ("Graves病", "抗甲状腺药物治疗", 0.85, "一线", "A"),
            ("Graves病", "放射性碘治疗", 0.90, "二线", "A")
        ]
        
        for disease, treatment, effectiveness, line, evidence in disease_treatment_relations:
            query = """
            MATCH (d:Disease {name: $disease})
            MATCH (t:Treatment {name: $treatment})
            CREATE (d)-[:TREATED_BY {
                effectiveness: $effectiveness,
                treatment_line: $line,
                evidence_level: $evidence
            }]->(t)
            """
            self.session.run(query, {
                "disease": disease,
                "treatment": treatment,
                "effectiveness": effectiveness,
                "line": line,
                "evidence": evidence
            })
        
        # 治疗-药物关系
        treatment_medication_relations = [
            ("抗甲状腺药物治疗", "甲巯咪唑", "5-15mg", "每日2-3次"),
            ("抗甲状腺药物治疗", "丙基硫氧嘧啶", "100-300mg", "每日3次")
        ]
        
        for treatment, medication, dosage, frequency in treatment_medication_relations:
            query = """
            MATCH (t:Treatment {name: $treatment})
            MATCH (m:Medication {name: $medication})
            CREATE (t)-[:INCLUDES {
                dosage: $dosage,
                frequency: $frequency
            }]->(m)
            """
            self.session.run(query, {
                "treatment": treatment,
                "medication": medication,
                "dosage": dosage,
                "frequency": frequency
            })
        
        logger.info("实体关系建立完成")


class ThyroidDiagnosticEngine:
    """甲状腺诊断推理引擎"""
    
    def __init__(self, knowledge_graph: ThyroidKnowledgeGraph):
        self.kg = knowledge_graph
        
    def diagnose(self, patient_data: PatientData) -> DiagnosticResult:
        """执行诊断推理"""
        logger.info(f"开始对患者 {patient_data.patient_id} 进行诊断推理")
        
        # 1. 基于症状的初步筛查
        symptom_scores = self._analyze_symptoms(patient_data.symptoms)
        
        # 2. 基于实验室检查的精确诊断
        lab_scores = self._analyze_lab_results(patient_data.lab_results)
        
        # 3. 综合分析得出诊断结果
        diagnosis_result = self._integrate_evidence(
            symptom_scores, lab_scores, patient_data
        )
        
        logger.info(f"患者 {patient_data.patient_id} 诊断完成")
        return diagnosis_result
    
    def _analyze_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """分析症状模式"""
        query = """
        MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
        WHERE s.name IN $symptoms
        RETURN d.name as disease,
               collect(s.name) as matching_symptoms,
               avg(r.probability) as avg_probability,
               count(s) as symptom_count
        ORDER BY avg_probability DESC, symptom_count DESC
        """
        
        results = self.kg.run_query(query, {"symptoms": symptoms})
        
        symptom_scores = {}
        for result in results:
            disease = result["disease"]
            avg_prob = result["avg_probability"]
            symptom_count = result["symptom_count"]
            
            # 计算症状评分 (概率 × 症状数量 × 权重)
            score = avg_prob * symptom_count * 0.3
            symptom_scores[disease] = score
        
        return symptom_scores
    
    def _analyze_lab_results(self, lab_results: Dict[str, float]) -> Dict[str, float]:
        """分析实验室检查结果"""
        if not lab_results:
            return {}
        
        query = """
        MATCH (l:LabTest)-[r:DIAGNOSES]->(d:Disease)
        WHERE l.name IN $lab_tests
        RETURN d.name as disease,
               l.name as lab_test,
               r.sensitivity as sensitivity,
               r.specificity as specificity,
               r.thresholds as thresholds
        """
        
        results = self.kg.run_query(query, {"lab_tests": list(lab_results.keys())})
        
        lab_scores = {}
        for result in results:
            disease = result["disease"]
            lab_test = result["lab_test"]
            sensitivity = result["sensitivity"]
            thresholds = result["thresholds"]
            
            # 检查是否符合诊断阈值
            lab_value = lab_results[lab_test]
            is_abnormal = self._check_abnormal_threshold(lab_test, lab_value, thresholds)
            
            if is_abnormal:
                score = sensitivity * 0.7  # 实验室检查权重更高
                lab_scores[disease] = lab_scores.get(disease, 0) + score
        
        return lab_scores
    
    def _check_abnormal_threshold(self, lab_test: str, value: float, thresholds: Dict) -> bool:
        """检查是否超过异常阈值"""
        if lab_test == "TSH":
            return value < 0.1  # TSH抑制
        elif lab_test == "FT4":
            return value > 25.0  # FT4升高
        elif lab_test == "TRAb":
            return value > 1.75  # TRAb阳性
        return False
    
    def _integrate_evidence(self, symptom_scores: Dict[str, float], 
                          lab_scores: Dict[str, float], 
                          patient_data: PatientData) -> DiagnosticResult:
        """整合所有证据得出最终诊断"""
        
        # 合并所有疾病评分
        all_diseases = set(symptom_scores.keys()) | set(lab_scores.keys())
        final_scores = {}
        
        for disease in all_diseases:
            symptom_score = symptom_scores.get(disease, 0)
            lab_score = lab_scores.get(disease, 0)
            total_score = symptom_score + lab_score
            final_scores[disease] = total_score
        
        # 找出最高分疾病
        if final_scores:
            top_disease = max(final_scores, key=final_scores.get)
            confidence = min(final_scores[top_disease], 1.0)
            
            # 获取支持证据
            supporting_evidence = []
            if top_disease in symptom_scores:
                supporting_evidence.append(f"症状模式匹配 (评分: {symptom_scores[top_disease]:.2f})")
            if top_disease in lab_scores:
                supporting_evidence.append(f"实验室检查支持 (评分: {lab_scores[top_disease]:.2f})")
            
            # 鉴别诊断列表
            differential_diagnosis = [d for d in final_scores.keys() if d != top_disease]
            differential_diagnosis.sort(key=lambda x: final_scores[x], reverse=True)
            differential_diagnosis = differential_diagnosis[:3]  # 取前3个
            
            # 推荐进一步检查
            recommended_tests = self._recommend_additional_tests(top_disease, patient_data)
            
            return DiagnosticResult(
                disease=top_disease,
                confidence=confidence,
                supporting_evidence=supporting_evidence,
                differential_diagnosis=differential_diagnosis,
                recommended_tests=recommended_tests
            )
        else:
            return DiagnosticResult(
                disease="无明确诊断",
                confidence=0.0,
                supporting_evidence=[],
                differential_diagnosis=[],
                recommended_tests=["建议完善甲状腺功能检查"]
            )
    
    def _recommend_additional_tests(self, disease: str, patient_data: PatientData) -> List[str]:
        """推荐进一步检查"""
        recommendations = []
        
        if disease == "Graves病":
            if "TRAb" not in patient_data.lab_results:
                recommendations.append("TRAb检测 - 确认Graves病诊断")
            if "突眼" in patient_data.symptoms:
                recommendations.append("眼眶CT/MRI - 评估眼病严重程度")
            recommendations.append("甲状腺超声 - 评估甲状腺大小和结构")
            
        elif disease == "毒性结节性甲状腺肿":
            recommendations.append("甲状腺扫描 - 确认结节功能状态")
            recommendations.append("甲状腺超声 - 评估结节大小和性质")
            
        elif disease == "桥本甲状腺炎":
            recommendations.append("TPOAb和TgAb检测 - 确认自身免疫状态")
            recommendations.append("甲状腺超声 - 评估甲状腺结构变化")
        
        return recommendations


class ThyroidTreatmentEngine:
    """甲状腺治疗推荐引擎"""
    
    def __init__(self, knowledge_graph: ThyroidKnowledgeGraph):
        self.kg = knowledge_graph
    
    def recommend_treatment(self, diagnosis: str, patient_data: PatientData) -> List[TreatmentRecommendation]:
        """推荐治疗方案"""
        logger.info(f"为患者 {patient_data.patient_id} 推荐 {diagnosis} 治疗方案")
        
        # 查询治疗方案
        query = """
        MATCH (d:Disease {name: $diagnosis})-[r:TREATED_BY]->(t:Treatment)
        OPTIONAL MATCH (t)-[inc:INCLUDES]->(m:Medication)
        RETURN t.name as treatment,
               t.type as treatment_type,
               r.effectiveness as effectiveness,
               r.treatment_line as line,
               r.evidence_level as evidence,
               t.contraindications as contraindications,
               m.name as medication,
               inc.dosage as dosage,
               inc.frequency as frequency
        ORDER BY r.treatment_line, r.effectiveness DESC
        """
        
        results = self.kg.run_query(query, {"diagnosis": diagnosis})
        
        recommendations = []
        for result in results:
            # 检查禁忌症
            contraindications = result.get("contraindications", [])
            if self._has_contraindications(contraindications, patient_data):
                continue
            
            # 调整治疗方案
            adjusted_treatment = self._adjust_for_patient(result, patient_data)
            recommendations.append(adjusted_treatment)
        
        return recommendations[:3]  # 返回前3个推荐方案
    
    def _has_contraindications(self, contraindications: List[str], patient_data: PatientData) -> bool:
        """检查是否有禁忌症"""
        if not contraindications:
            return False
        
        patient_conditions = (
            patient_data.medical_history + 
            patient_data.comorbidities + 
            (["妊娠"] if patient_data.pregnancy_status else [])
        )
        
        return any(contra in patient_conditions for contra in contraindications)
    
    def _adjust_for_patient(self, treatment_result: Dict, patient_data: PatientData) -> TreatmentRecommendation:
        """根据患者特征调整治疗方案"""
        treatment_name = treatment_result["treatment"]
        medication = treatment_result.get("medication", "")
        base_dosage = treatment_result.get("dosage", "")
        
        # 年龄调整
        if patient_data.age > 65:
            adjusted_dosage = f"{base_dosage} (老年人减量)"
        elif patient_data.age < 18:
            adjusted_dosage = f"{base_dosage} (儿童剂量)"
        else:
            adjusted_dosage = base_dosage
        
        # 妊娠期调整
        if patient_data.pregnancy_status and medication == "甲巯咪唑":
            medication = "丙基硫氧嘧啶 (妊娠期首选)"
        
        # 生成监测计划
        monitoring_plan = self._generate_monitoring_plan(treatment_name, patient_data)
        
        return TreatmentRecommendation(
            treatment_name=treatment_name,
            medication=medication,
            dosage=adjusted_dosage,
            duration=treatment_result.get("duration", "个体化"),
            monitoring_plan=monitoring_plan,
            contraindications=treatment_result.get("contraindications", []),
            success_probability=treatment_result.get("effectiveness", 0.0)
        )
    
    def _generate_monitoring_plan(self, treatment_name: str, patient_data: PatientData) -> Dict[str, Any]:
        """生成监测计划"""
        base_plan = {
            "baseline": ["TSH", "FT4", "FT3", "肝功能", "血常规"],
            "week_2": ["肝功能", "血常规"],
            "week_6": ["TSH", "FT4", "FT3"],
            "month_3": ["TSH", "FT4", "FT3", "TRAb"],
            "maintenance": ["TSH", "FT4"]
        }
        
        # 根据风险因素调整
        if patient_data.age > 65:
            base_plan["additional_monitoring"] = ["心电图", "心率监测"]
        
        if patient_data.pregnancy_status:
            base_plan["pregnancy_specific"] = ["每4周甲功检查", "胎儿监测"]
        
        return base_plan


def main():
    """主函数 - 演示系统使用"""
    
    # 连接知识图谱
    with ThyroidKnowledgeGraph("bolt://localhost:7687", "neo4j", "password") as kg:
        
        # 初始化知识库 (首次运行时)
        # kg.initialize_knowledge_base()
        
        # 创建诊断和治疗引擎
        diagnostic_engine = ThyroidDiagnosticEngine(kg)
        treatment_engine = ThyroidTreatmentEngine(kg)
        
        # 模拟患者数据
        patient = PatientData(
            patient_id="P001",
            age=35,
            gender="女",
            symptoms=["心悸", "体重下降", "怕热多汗", "突眼"],
            lab_results={
                "TSH": 0.05,  # 抑制
                "FT4": 35.0,  # 升高
                "TRAb": 8.5   # 阳性
            },
            medical_history=[],
            current_medications=[],
            allergies=[],
            pregnancy_status=False,
            comorbidities=[]
        )
        
        # 执行诊断
        diagnosis_result = diagnostic_engine.diagnose(patient)
        
        print(f"诊断结果: {diagnosis_result.disease}")
        print(f"置信度: {diagnosis_result.confidence:.2f}")
        print(f"支持证据: {diagnosis_result.supporting_evidence}")
        print(f"鉴别诊断: {diagnosis_result.differential_diagnosis}")
        print(f"推荐检查: {diagnosis_result.recommended_tests}")
        
        # 获取治疗建议
        if diagnosis_result.confidence > 0.7:
            treatment_recommendations = treatment_engine.recommend_treatment(
                diagnosis_result.disease, patient
            )
            
            print("\n治疗建议:")
            for i, rec in enumerate(treatment_recommendations, 1):
                print(f"{i}. {rec.treatment_name}")
                print(f"   药物: {rec.medication}")
                print(f"   剂量: {rec.dosage}")
                print(f"   成功率: {rec.success_probability:.1%}")
                print(f"   监测: {rec.monitoring_plan}")
                print()


if __name__ == "__main__":
    main()