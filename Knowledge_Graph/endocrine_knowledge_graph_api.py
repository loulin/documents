"""
综合内分泌疾病知识图谱 API 服务器
基于FastAPI构建的RESTful API，支持大语言模型集成和临床决策支持

特性：
- 多疾病智能诊断和治疗推荐  
- 共病模式识别和管理
- 结构化医学文本解析
- RAG增强的问答系统
- 临床研究数据支持
- 实时医学知识更新
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# AI/ML imports
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
from transformers import AutoTokenizer, AutoModel
import torch

# Database imports  
from neo4j import GraphDatabase
import redis
from pymongo import MongoClient

# Medical NLP imports
import spacy
import scispacy
from scispacy.abbreviation import AbbreviationDetector
from scispacy.linking import EntityLinker

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="综合内分泌疾病知识图谱 API",
    description="基于权威医学指南的内分泌疾病智能诊疗支持系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# ===== 数据模型定义 =====

class PatientProfile(BaseModel):
    """患者基本信息"""
    patient_id: str
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., regex="^(男|女|male|female)$")
    height: Optional[float] = Field(None, ge=50, le=250)
    weight: Optional[float] = Field(None, ge=10, le=300)
    bmi: Optional[float] = None
    ethnicity: Optional[str] = None
    medical_history: List[str] = []
    family_history: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []

class SymptomInput(BaseModel):
    """症状输入"""
    symptoms: List[str] = Field(..., min_items=1)
    duration: Optional[str] = None
    severity: Optional[str] = Field(None, regex="^(轻度|中度|重度|mild|moderate|severe)$")
    onset: Optional[str] = None
    location: Optional[str] = None

class LabResult(BaseModel):
    """实验室检查结果"""
    test_name: str
    value: Union[float, str]
    unit: str
    reference_range: Optional[str] = None
    abnormal: Optional[bool] = None
    date_collected: Optional[datetime] = None

class ImagingResult(BaseModel):
    """影像学检查结果"""
    exam_type: str
    findings: str
    impression: str
    date_performed: Optional[datetime] = None
    images: Optional[List[str]] = []

class DiagnosticRequest(BaseModel):
    """诊断请求"""
    patient: PatientProfile
    symptoms: SymptomInput
    lab_results: List[LabResult] = []
    imaging: List[ImagingResult] = []
    clinical_notes: Optional[str] = None
    differential_diagnosis_count: int = Field(default=5, ge=1, le=10)

class DiagnosisResult(BaseModel):
    """诊断结果"""
    primary_diagnosis: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    supporting_evidence: List[str]
    differential_diagnoses: List[Dict[str, Any]]
    recommended_tests: List[str]
    urgency_level: str
    icd10_code: Optional[str] = None

class TreatmentRequest(BaseModel):
    """治疗推荐请求"""
    patient: PatientProfile
    diagnoses: List[str]
    severity: Optional[str] = None
    comorbidities: List[str] = []
    contraindications: List[str] = []
    treatment_goals: List[str] = []

class TreatmentPlan(BaseModel):
    """治疗方案"""
    treatment_id: str
    primary_therapy: Dict[str, Any]
    adjunctive_therapies: List[Dict[str, Any]] = []
    monitoring_plan: Dict[str, Any]
    follow_up_schedule: List[str]
    patient_education: List[str]
    expected_outcomes: Dict[str, Any]

class DrugInteractionCheck(BaseModel):
    """药物相互作用检查"""
    medications: List[str]
    severity_filter: Optional[str] = "all"

class ResearchQuery(BaseModel):
    """研究查询"""
    research_question: str
    inclusion_criteria: List[str] = []
    exclusion_criteria: List[str] = []
    outcome_measures: List[str] = []
    study_period: Optional[Dict[str, datetime]] = None

# ===== 核心服务类 =====

class KnowledgeGraphService:
    """知识图谱服务"""
    
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"), 
                os.getenv("NEO4J_PASSWORD", "password")
            )
        )
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
    def get_disease_info(self, disease_id: str) -> Dict[str, Any]:
        """获取疾病详细信息"""
        with self.neo4j_driver.session() as session:
            query = """
            MATCH (d:Disease {id: $disease_id})
            OPTIONAL MATCH (d)-[r]-(related)
            RETURN d, collect({relation: type(r), node: related}) as relationships
            """
            result = session.run(query, disease_id=disease_id)
            record = result.single()
            if record:
                return {
                    "disease": dict(record["d"]),
                    "relationships": record["relationships"]
                }
            return {}
    
    def find_related_diseases(self, symptoms: List[str], lab_values: Dict[str, float]) -> List[Dict]:
        """基于症状和检验值查找相关疾病"""
        with self.neo4j_driver.session() as session:
            query = """
            MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
            WHERE s.name IN $symptoms
            WITH d, count(s) as symptom_match_count
            MATCH (d)-[:DIAGNOSED_BY]->(t:Test)
            WHERE t.name IN $lab_tests
            RETURN d, symptom_match_count, count(t) as test_match_count
            ORDER BY symptom_match_count + test_match_count DESC
            LIMIT 10
            """
            lab_tests = list(lab_values.keys())
            result = session.run(query, symptoms=symptoms, lab_tests=lab_tests)
            return [dict(record) for record in result]

class MedicalNLPService:
    """医学自然语言处理服务"""
    
    def __init__(self):
        # 加载医学专用NLP模型
        self.nlp = spacy.load("en_core_sci_sm")
        self.nlp.add_pipe("abbreviation_detector")
        self.nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})
        
        # 中文医学NLP支持
        try:
            self.zh_nlp = spacy.load("zh_core_web_sm") 
        except:
            logger.warning("中文NLP模型未找到，将使用基础处理")
            self.zh_nlp = None
            
    def extract_medical_entities(self, text: str, language: str = "en") -> Dict[str, Any]:
        """从文本中提取医学实体"""
        if language == "zh" and self.zh_nlp:
            doc = self.zh_nlp(text)
        else:
            doc = self.nlp(text)
            
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": getattr(ent, 'confidence', 0.0)
            })
            
        return {
            "text": text,
            "entities": entities,
            "processed_at": datetime.now().isoformat()
        }
    
    def extract_clinical_information(self, clinical_text: str) -> Dict[str, Any]:
        """从临床文本中提取结构化信息"""
        doc = self.nlp(clinical_text)
        
        # 提取症状
        symptoms = []
        for ent in doc.ents:
            if ent.label_ in ["SYMPTOM", "SIGN"]:
                symptoms.append(ent.text)
        
        # 提取药物
        medications = []
        for ent in doc.ents:
            if ent.label_ in ["CHEMICAL", "DRUG"]:
                medications.append(ent.text)
                
        # 提取检验值
        lab_values = {}
        for ent in doc.ents:
            if ent.label_ == "QUANTITY":
                # 简单的数值提取逻辑
                text = ent.text.lower()
                if any(keyword in text for keyword in ["glucose", "tsh", "hba1c"]):
                    lab_values[ent.text] = self._extract_numeric_value(ent.text)
        
        return {
            "symptoms": symptoms,
            "medications": medications, 
            "lab_values": lab_values,
            "original_text": clinical_text
        }
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """从文本中提取数值"""
        import re
        match = re.search(r'\d+\.?\d*', text)
        return float(match.group()) if match else None

class DiagnosticEngine:
    """诊断推理引擎"""
    
    def __init__(self, kg_service: KnowledgeGraphService, nlp_service: MedicalNLPService):
        self.kg_service = kg_service
        self.nlp_service = nlp_service
        
    def diagnose(self, request: DiagnosticRequest) -> DiagnosisResult:
        """执行智能诊断"""
        # 1. 症状分析
        symptom_scores = self._analyze_symptoms(request.symptoms.symptoms)
        
        # 2. 实验室检查分析
        lab_scores = self._analyze_lab_results(request.lab_results)
        
        # 3. 影像学分析
        imaging_scores = self._analyze_imaging(request.imaging)
        
        # 4. 综合评分和排序
        combined_scores = self._combine_scores(symptom_scores, lab_scores, imaging_scores)
        
        # 5. 生成诊断结果
        primary_diagnosis = max(combined_scores, key=combined_scores.get)
        confidence = combined_scores[primary_diagnosis]
        
        # 6. 生成鉴别诊断
        differential = sorted(
            [(disease, score) for disease, score in combined_scores.items() 
             if disease != primary_diagnosis],
            key=lambda x: x[1], 
            reverse=True
        )[:request.differential_diagnosis_count-1]
        
        return DiagnosisResult(
            primary_diagnosis=primary_diagnosis,
            confidence_score=confidence,
            supporting_evidence=self._generate_evidence(primary_diagnosis, request),
            differential_diagnoses=[
                {"diagnosis": d, "confidence": s, "rationale": self._get_diagnosis_rationale(d)}
                for d, s in differential
            ],
            recommended_tests=self._recommend_tests(primary_diagnosis),
            urgency_level=self._assess_urgency(primary_diagnosis, confidence),
            icd10_code=self._get_icd10_code(primary_diagnosis)
        )
    
    def _analyze_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """分析症状并计算疾病概率"""
        # 基于知识图谱的症状-疾病关联分析
        disease_scores = {}
        related_diseases = self.kg_service.find_related_diseases(symptoms, {})
        
        for disease_record in related_diseases:
            disease = disease_record["d"]
            symptom_count = disease_record.get("symptom_match_count", 0)
            disease_scores[disease["name"]] = symptom_count / len(symptoms)
        
        # 增加风湿免疫疾病症状评分
        rheumatic_scores = self._analyze_rheumatic_symptoms(symptoms)
        disease_scores.update(rheumatic_scores)
        
        # 增加尿酸代谢疾病症状评分
        uric_acid_scores = self._analyze_uric_acid_symptoms(symptoms)
        disease_scores.update(uric_acid_scores)
        
        # 增加骨代谢疾病症状评分
        bone_metabolism_scores = self._analyze_bone_metabolism_symptoms(symptoms)
        disease_scores.update(bone_metabolism_scores)
        
        # 增加营养代谢疾病症状评分
        nutritional_metabolic_scores = self._analyze_nutritional_metabolic_symptoms(symptoms)
        disease_scores.update(nutritional_metabolic_scores)
        
        # 增加生殖内分泌疾病症状评分
        reproductive_endocrine_scores = self._analyze_reproductive_endocrine_symptoms(symptoms)
        disease_scores.update(reproductive_endocrine_scores)
            
        return disease_scores
        
    def _analyze_rheumatic_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """分析风湿免疫疾病相关症状"""
        rheumatic_scores = {}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            # 1型糖尿病（自身免疫性）
            if any(term in symptom_lower for term in ["酮症", "酸中毒", "快速体重下降", "年轻发病", "胰岛素依赖"]):
                rheumatic_scores["1型糖尿病"] = rheumatic_scores.get("1型糖尿病", 0.0) + 0.4
                
            # Hashimoto甲状腺炎特异症状
            if any(term in symptom_lower for term in ["甲状腺肿大", "吞咽困难", "颈部压迫感", "甲状腺结节"]):
                rheumatic_scores["桥本甲状腺炎"] = rheumatic_scores.get("桥本甲状腺炎", 0.0) + 0.3
                
            # Addison病症状
            if any(term in symptom_lower for term in ["色素沉着", "低血压", "恶心", "呕吐", "嗜盐", "电解质紊乱"]):
                rheumatic_scores["Addison病"] = rheumatic_scores.get("Addison病", 0.0) + 0.4
                
            # 系统性红斑狼疮症状
            if any(term in symptom_lower for term in ["蝶形红斑", "光敏感", "关节痛", "脱发", "口腔溃疡", "雷诺现象"]):
                rheumatic_scores["系统性红斑狼疮"] = rheumatic_scores.get("系统性红斑狼疮", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["蛋白尿", "血尿", "水肿", "肾功能异常"]):
                rheumatic_scores["狼疮肾炎"] = rheumatic_scores.get("狼疮肾炎", 0.0) + 0.3
                
            # 类风湿关节炎症状
            if any(term in symptom_lower for term in ["关节肿胀", "晨僵", "对称性关节痛", "手指关节痛"]):
                rheumatic_scores["类风湿关节炎"] = rheumatic_scores.get("类风湿关节炎", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["关节畸形", "皮下结节", "类风湿结节"]):
                rheumatic_scores["类风湿关节炎"] = rheumatic_scores.get("类风湿关节炎", 0.0) + 0.3
                
            # 干燥综合征症状
            if any(term in symptom_lower for term in ["口干", "眼干", "腮腺肿大", "干燥性角结膜炎"]):
                rheumatic_scores["干燥综合征"] = rheumatic_scores.get("干燥综合征", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["牙齿脱落", "反复龋齿", "吞咽干食困难"]):
                rheumatic_scores["干燥综合征"] = rheumatic_scores.get("干燥综合征", 0.0) + 0.3
                
            # APS-1特异症状
            if any(term in symptom_lower for term in ["慢性念珠菌感染", "鹅口疮", "指甲真菌感染", "反复口腔感染"]):
                rheumatic_scores["多腺体自身免疫综合征I型"] = rheumatic_scores.get("多腺体自身免疫综合征I型", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["手足搐搦", "癫痫", "肌肉痉挛", "感觉异常", "低钙症状"]):
                rheumatic_scores["甲状旁腺功能减退"] = rheumatic_scores.get("甲状旁腺功能减退", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["牙釉质缺陷", "斑秃", "白癜风", "外胚层发育异常"]):
                rheumatic_scores["多腺体自身免疫综合征I型"] = rheumatic_scores.get("多腺体自身免疫综合征I型", 0.0) + 0.3
                
            # APS-2症状组合
            if any(term in symptom_lower for term in ["多腺体受累", "多种激素缺乏", "家族聚集性"]):
                rheumatic_scores["多腺体自身免疫综合征II型"] = rheumatic_scores.get("多腺体自身免疫综合征II型", 0.0) + 0.4
                
        return rheumatic_scores
    
    def _analyze_uric_acid_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """分析尿酸代谢疾病相关症状"""
        uric_acid_scores = {}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            # 急性痛风发作症状
            if any(term in symptom_lower for term in ["关节疼痛", "红肿热痛", "夜间疼痛", "第一跖趾关节痛"]):
                uric_acid_scores["急性痛风"] = uric_acid_scores.get("急性痛风", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["足趾疼痛", "踝关节痛", "膝关节痛", "手指关节痛"]):
                uric_acid_scores["急性痛风"] = uric_acid_scores.get("急性痛风", 0.0) + 0.4
                
            # 慢性痛风症状
            if any(term in symptom_lower for term in ["痛风石", "tophi", "关节畸形", "慢性关节炎"]):
                uric_acid_scores["慢性痛风"] = uric_acid_scores.get("慢性痛风", 0.0) + 0.6
                
            if any(term in symptom_lower for term in ["关节僵硬", "活动受限", "反复发作", "间歇期"]):
                uric_acid_scores["慢性痛风"] = uric_acid_scores.get("慢性痛风", 0.0) + 0.3
                
            # 高尿酸血症相关症状（通常无症状，但可有并发症）
            if any(term in symptom_lower for term in ["肾结石", "血尿", "腰痛", "排尿困难"]):
                uric_acid_scores["高尿酸血症"] = uric_acid_scores.get("高尿酸血症", 0.0) + 0.4
                uric_acid_scores["尿酸性肾结石"] = uric_acid_scores.get("尿酸性肾结石", 0.0) + 0.5
                
            # 代谢综合征相关症状
            if any(term in symptom_lower for term in ["肥胖", "高血压", "血糖升高", "血脂异常"]):
                uric_acid_scores["高尿酸血症"] = uric_acid_scores.get("高尿酸血症", 0.0) + 0.2
                
            # 肾功能异常症状
            if any(term in symptom_lower for term in ["水肿", "少尿", "蛋白尿", "肾功能不全"]):
                uric_acid_scores["痛风性肾病"] = uric_acid_scores.get("痛风性肾病", 0.0) + 0.4
                uric_acid_scores["高尿酸血症"] = uric_acid_scores.get("高尿酸血症", 0.0) + 0.3
                
            # 心血管症状（高尿酸血症并发症）
            if any(term in symptom_lower for term in ["胸闷", "胸痛", "心悸", "气短"]):
                uric_acid_scores["高尿酸血症"] = uric_acid_scores.get("高尿酸血症", 0.0) + 0.1
                
        return uric_acid_scores
    
    def _analyze_bone_metabolism_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """分析骨代谢疾病相关症状"""
        bone_scores = {}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            # 骨质疏松症症状
            if any(term in symptom_lower for term in ["骨痛", "腰背痛", "背痛", "骨疼痛"]):
                bone_scores["骨质疏松症"] = bone_scores.get("骨质疏松症", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["身高降低", "身高下降", "驼背", "脊柱后凸"]):
                bone_scores["骨质疏松症"] = bone_scores.get("骨质疏松症", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["脆性骨折", "病理性骨折", "轻微外伤骨折", "椎体骨折", "髋部骨折"]):
                bone_scores["骨质疏松症"] = bone_scores.get("骨质疏松症", 0.0) + 0.8
                
            # 骨软化症特异症状
            if any(term in symptom_lower for term in ["肌无力", "近端肌群无力", "上楼困难", "举臂无力"]):
                bone_scores["骨软化症"] = bone_scores.get("骨软化症", 0.0) + 0.5
                bone_scores["维生素D缺乏"] = bone_scores.get("维生素D缺乏", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["骨骼畸形", "胸廓畸形", "下肢弯曲", "O型腿", "X型腿"]):
                bone_scores["骨软化症"] = bone_scores.get("骨软化症", 0.0) + 0.6
                bone_scores["佝偻病"] = bone_scores.get("佝偻病", 0.0) + 0.7
                
            if any(term in symptom_lower for term in ["假性骨折", "looser带", "对称性透明带"]):
                bone_scores["骨软化症"] = bone_scores.get("骨软化症", 0.0) + 0.9
                
            # 甲状旁腺功能亢进相关症状
            if any(term in symptom_lower for term in ["高钙血症症状", "多尿", "烦渴", "肾结石"]):
                bone_scores["甲状旁腺性骨病"] = bone_scores.get("甲状旁腺性骨病", 0.0) + 0.5
                bone_scores["原发性甲状旁腺功能亢进"] = bone_scores.get("原发性甲状旁腺功能亢进", 0.0) + 0.6
                
            if any(term in symptom_lower for term in ["褐色瘤", "颌骨肿胀", "面部肿胀"]):
                bone_scores["甲状旁腺性骨病"] = bone_scores.get("甲状旁腺性骨病", 0.0) + 0.8
                
            if any(term in symptom_lower for term in ["抑郁", "记忆力减退", "人格改变", "意识模糊"]):
                bone_scores["甲状旁腺性骨病"] = bone_scores.get("甲状旁腺性骨病", 0.0) + 0.3
                
            # 低钙血症症状（甲状旁腺功能减退、维生素D缺乏）
            if any(term in symptom_lower for term in ["手足搐搦", "肌肉痉挛", "感觉异常", "癫痫发作"]):
                bone_scores["骨软化症"] = bone_scores.get("骨软化症", 0.0) + 0.5
                bone_scores["维生素D缺乏"] = bone_scores.get("维生素D缺乏", 0.0) + 0.6
                bone_scores["甲状旁腺功能减退"] = bone_scores.get("甲状旁腺功能减退", 0.0) + 0.7
                
            # Chvostek征和Trousseau征
            if any(term in symptom_lower for term in ["chvostek征", "trousseau征", "面神经征", "止血带试验阳性"]):
                bone_scores["甲状旁腺功能减退"] = bone_scores.get("甲状旁腺功能减退", 0.0) + 0.8
                
            # 生长发育相关症状（儿童）
            if any(term in symptom_lower for term in ["生长迟缓", "牙齿萌出延迟", "囟门闭合延迟", "颅骨软化"]):
                bone_scores["佝偻病"] = bone_scores.get("佝偻病", 0.0) + 0.7
                bone_scores["维生素D缺乏"] = bone_scores.get("维生素D缺乏", 0.0) + 0.6
                
            # 跌倒和平衡问题
            if any(term in symptom_lower for term in ["跌倒", "平衡障碍", "步态不稳", "活动能力下降"]):
                bone_scores["骨质疏松症"] = bone_scores.get("骨质疏松症", 0.0) + 0.3
                bone_scores["骨软化症"] = bone_scores.get("骨软化症", 0.0) + 0.3
                
        return bone_scores
    
    def _analyze_nutritional_metabolic_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """分析营养代谢疾病相关症状"""
        nutritional_scores = {}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            # 肥胖症症状
            if any(term in symptom_lower for term in ["体重增加", "肥胖", "腹型肥胖", "向心性肥胖"]):
                nutritional_scores["肥胖症"] = nutritional_scores.get("肥胖症", 0.0) + 0.9
                nutritional_scores["代谢综合征"] = nutritional_scores.get("代谢综合征", 0.0) + 0.6
                
            if any(term in symptom_lower for term in ["食欲亢进", "暴饮暴食", "进食过量", "饮食失控"]):
                nutritional_scores["肥胖症"] = nutritional_scores.get("肥胖症", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["活动耐力下降", "运动不耐受", "易疲劳", "气促"]):
                nutritional_scores["肥胖症"] = nutritional_scores.get("肥胖症", 0.0) + 0.4
                nutritional_scores["代谢综合征"] = nutritional_scores.get("代谢综合征", 0.0) + 0.3
                
            if any(term in symptom_lower for term in ["睡眠呼吸暂停", "打鼾", "夜间憋醒", "日间嗜睡"]):
                nutritional_scores["肥胖症"] = nutritional_scores.get("肥胖症", 0.0) + 0.7
                
            if any(term in symptom_lower for term in ["关节疼痛", "膝关节痛", "腰痛", "负重关节痛"]):
                nutritional_scores["肥胖症"] = nutritional_scores.get("肥胖症", 0.0) + 0.3
                
            if any(term in symptom_lower for term in ["黑棘皮症", "颈部皮肤变黑", "腋下皮肤变黑", "皮肤色素沉着"]):
                nutritional_scores["肥胖症"] = nutritional_scores.get("肥胖症", 0.0) + 0.6
                nutritional_scores["代谢综合征"] = nutritional_scores.get("代谢综合征", 0.0) + 0.7
                nutritional_scores["胰岛素抵抗"] = nutritional_scores.get("胰岛素抵抗", 0.0) + 0.8
                
            # 代谢综合征特异症状
            if any(term in symptom_lower for term in ["血压升高", "高血压", "血压异常"]):
                nutritional_scores["代谢综合征"] = nutritional_scores.get("代谢综合征", 0.0) + 0.5
                nutritional_scores["肥胖症"] = nutritional_scores.get("肥胖症", 0.0) + 0.3
                
            if any(term in symptom_lower for term in ["血糖升高", "空腹血糖异常", "糖耐量异常", "餐后血糖高"]):
                nutritional_scores["代谢综合征"] = nutritional_scores.get("代谢综合征", 0.0) + 0.7
                nutritional_scores["胰岛素抵抗"] = nutritional_scores.get("胰岛素抵抗", 0.0) + 0.6
                nutritional_scores["2型糖尿病前期"] = nutritional_scores.get("2型糖尿病前期", 0.0) + 0.8
                
            if any(term in symptom_lower for term in ["血脂异常", "甘油三酯升高", "胆固醇异常", "hdl降低"]):
                nutritional_scores["代谢综合征"] = nutritional_scores.get("代谢综合征", 0.0) + 0.6
                nutritional_scores["脂代谢紊乱"] = nutritional_scores.get("脂代谢紊乱", 0.0) + 0.8
                
            # 维生素D缺乏症症状
            if any(term in symptom_lower for term in ["肌无力", "肌肉无力", "乏力", "全身无力"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.5
                nutritional_scores["肌病"] = nutritional_scores.get("肌病", 0.0) + 0.3
                
            if any(term in symptom_lower for term in ["骨痛", "骨骼疼痛", "胸骨痛", "肋骨痛"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.6
                nutritional_scores["骨软化症"] = nutritional_scores.get("骨软化症", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["抑郁", "情绪低落", "焦虑", "抑郁症状"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.3
                
            if any(term in symptom_lower for term in ["免疫力下降", "反复感染", "感冒频繁", "感染易感"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["手足搐搦", "肌肉痉挛", "抽搐", "癫痫发作"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.7
                nutritional_scores["低钙血症"] = nutritional_scores.get("低钙血症", 0.0) + 0.8
                
            if any(term in symptom_lower for term in ["跌倒", "平衡障碍", "步态不稳", "协调性差"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.5
                
            # 儿童生长发育症状
            if any(term in symptom_lower for term in ["生长迟缓", "身高偏矮", "发育缓慢", "青春期延迟"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.5
                nutritional_scores["营养不良"] = nutritional_scores.get("营养不良", 0.0) + 0.6
                
            if any(term in symptom_lower for term in ["牙齿萌出延迟", "牙齿问题", "龋齿增多", "牙釉质发育不良"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.4
                
            # 季节性相关症状
            if any(term in symptom_lower for term in ["冬季症状加重", "阳光不足", "室内工作", "缺乏日照"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.3
                
            # 胃肠道症状（吸收不良相关）
            if any(term in symptom_lower for term in ["腹泻", "脂肪泻", "吸收不良", "肠道疾病"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.4
                nutritional_scores["脂溶性维生素缺乏"] = nutritional_scores.get("脂溶性维生素缺乏", 0.0) + 0.5
                
            # 皮肤症状
            if any(term in symptom_lower for term in ["皮肤干燥", "皮炎", "湿疹", "皮肤感染"]):
                nutritional_scores["维生素D缺乏症"] = nutritional_scores.get("维生素D缺乏症", 0.0) + 0.2
                
            # 心血管症状
            if any(term in symptom_lower for term in ["心悸", "心律不齐", "心脏不适", "胸闷"]):
                nutritional_scores["代谢综合征"] = nutritional_scores.get("代谢综合征", 0.0) + 0.3
                nutritional_scores["低钙血症"] = nutritional_scores.get("低钙血症", 0.0) + 0.4
                
        return nutritional_scores
    
    def _analyze_reproductive_endocrine_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """分析生殖内分泌疾病相关症状"""
        reproductive_scores = {}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            # PCOS相关症状
            if any(term in symptom_lower for term in ["月经不调", "月经稀发", "月经推迟", "闭经", "无月经"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.7
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.4
                
            if any(term in symptom_lower for term in ["多毛症", "面部毛发增多", "体毛过多", "hirsutism"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.8
                reproductive_scores["高雄激素血症"] = reproductive_scores.get("高雄激素血症", 0.0) + 0.9
                
            if any(term in symptom_lower for term in ["痤疮", "成人痤疮", "雄激素性痤疮", "顽固性痤疮"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.6
                reproductive_scores["高雄激素血症"] = reproductive_scores.get("高雄激素血症", 0.0) + 0.7
                
            if any(term in symptom_lower for term in ["男性型脱发", "雄激素性脱发", "发际线后移", "头顶稀疏"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.7
                reproductive_scores["高雄激素血症"] = reproductive_scores.get("高雄激素血症", 0.0) + 0.8
                
            if any(term in symptom_lower for term in ["不孕", "不育", "难孕", "备孕困难"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.6
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.7
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["排卵障碍", "无排卵", "排卵异常"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.8
                
            # 男性性腺功能减退症状
            if any(term in symptom_lower for term in ["性欲减退", "性欲低下", "libido下降", "性冷淡"]):
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.8
                reproductive_scores["迟发性性腺功能减退"] = reproductive_scores.get("迟发性性腺功能减退", 0.0) + 0.7
                
            if any(term in symptom_lower for term in ["勃起功能障碍", "勃起困难", "阳痿", "ed"]):
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.7
                
            if any(term in symptom_lower for term in ["睾丸萎缩", "睾丸变小", "阴囊萎缩"]):
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.9
                
            if any(term in symptom_lower for term in ["乳房发育", "男性乳房增大", "gynecomastia"]):
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.6
                reproductive_scores["高泌乳素血症"] = reproductive_scores.get("高泌乳素血症", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["体毛减少", "胡须稀少", "腋毛减少", "阴毛稀疏"]):
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.6
                
            if any(term in symptom_lower for term in ["肌肉量减少", "肌肉力量下降", "肌无力", "体力下降"]):
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.4
                reproductive_scores["肌少症"] = reproductive_scores.get("肌少症", 0.0) + 0.3
                
            # 卵巢早衰相关症状
            if any(term in symptom_lower for term in ["潮热", "hot flashes", "潮红", "面部发热"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.8
                reproductive_scores["早期绝经"] = reproductive_scores.get("早期绝经", 0.0) + 0.7
                
            if any(term in symptom_lower for term in ["盗汗", "夜间出汗", "睡眠出汗"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.7
                reproductive_scores["早期绝经"] = reproductive_scores.get("早期绝经", 0.0) + 0.6
                
            if any(term in symptom_lower for term in ["阴道干燥", "性交痛", "阴道萎缩", "外阴萎缩"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.8
                reproductive_scores["雌激素缺乏"] = reproductive_scores.get("雌激素缺乏", 0.0) + 0.9
                
            if any(term in symptom_lower for term in ["情绪波动", "易怒", "抑郁", "情绪不稳定"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.4
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.3
                
            if any(term in symptom_lower for term in ["失眠", "睡眠质量差", "入睡困难", "多梦易醒"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.3
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.2
                
            # 年龄相关症状
            if any(term in symptom_lower for term in ["40岁前闭经", "早发闭经", "年轻闭经"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.9
                
            if any(term in symptom_lower for term in ["中年男性症状", "更年期综合征", "andropause"]):
                reproductive_scores["迟发性性腺功能减退"] = reproductive_scores.get("迟发性性腺功能减退", 0.0) + 0.6
                
            # 代谢相关症状
            if any(term in symptom_lower for term in ["腹部肥胖", "向心性肥胖", "内脏肥胖"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.5
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.3
                
            # 自身免疫相关症状
            if any(term in symptom_lower for term in ["甲状腺炎", "肾上腺功能不全", "1型糖尿病", "自身免疫病"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.4
                reproductive_scores["多腺体自身免疫综合征"] = reproductive_scores.get("多腺体自身免疫综合征", 0.0) + 0.6
                
            # 妊娠相关症状
            if any(term in symptom_lower for term in ["流产", "反复流产", "妊娠困难", "早产"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.4
                reproductive_scores["抗磷脂综合征"] = reproductive_scores.get("抗磷脂综合征", 0.0) + 0.5
                
            if any(term in symptom_lower for term in ["妊娠糖尿病", "巨大儿", "先兆子痫"]):
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.3
                
            # 骨骼相关症状
            if any(term in symptom_lower for term in ["骨质疏松", "骨折", "骨密度下降", "骨痛"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.4
                reproductive_scores["男性性腺功能减退症"] = reproductive_scores.get("男性性腺功能减退症", 0.0) + 0.3
                
            # 心血管症状
            if any(term in symptom_lower for term in ["心悸", "胸闷", "高血压", "血脂异常"]):
                reproductive_scores["卵巢早衰"] = reproductive_scores.get("卵巢早衰", 0.0) + 0.2
                reproductive_scores["多囊卵巢综合征"] = reproductive_scores.get("多囊卵巢综合征", 0.0) + 0.3
                
        return reproductive_scores
    
    def _analyze_lab_results(self, lab_results: List[LabResult]) -> Dict[str, float]:
        """分析实验室检查结果"""
        # 实验室检查的疾病关联分析
        lab_scores = {}
        lab_dict = {result.test_name: result.value for result in lab_results}
        
        # 增加风湿免疫疾病相关实验室检查
        rheumatic_lab_scores = self._analyze_rheumatic_labs(lab_results)
        lab_scores.update(rheumatic_lab_scores)
        
        # 增加尿酸代谢疾病相关实验室检查
        uric_acid_lab_scores = self._analyze_uric_acid_labs(lab_results)
        lab_scores.update(uric_acid_lab_scores)
        
        # 增加骨代谢疾病相关实验室检查
        bone_metabolism_lab_scores = self._analyze_bone_metabolism_labs(lab_results)
        lab_scores.update(bone_metabolism_lab_scores)
        
        # 基于知识图谱查询实验室检查-疾病关联
        # 这里简化处理，实际需要复杂的规则引擎
        for test_name, value in lab_dict.items():
            if isinstance(value, (int, float)):
                if test_name.lower() in ["tsh", "ft4", "ft3"]:
                    lab_scores["甲状腺疾病"] = 0.8
                elif test_name.lower() in ["glucose", "hba1c"]:
                    lab_scores["糖尿病"] = 0.9
                elif test_name.lower() in ["testosterone", "lh", "fsh"]:
                    lab_scores["性腺功能异常"] = 0.85
                elif test_name.lower() in ["cortisol", "acth"]:
                    lab_scores["肾上腺疾病"] = 0.8
                elif test_name.lower() in ["prolactin", "gh", "igf1"]:
                    lab_scores["垂体疾病"] = 0.8
                elif test_name.lower() in ["ck-mb", "troponin", "nt-probnp", "bnp"]:
                    lab_scores["心血管疾病"] = 0.85
                elif test_name.lower() in ["d-dimer", "fibrinogen", "homocysteine"]:
                    lab_scores["脑血管疾病"] = 0.75
                elif test_name.lower() in ["nerve_conduction", "emg"]:
                    lab_scores["神经病变"] = 0.9
        
        # 增加营养代谢疾病实验室检查评分
        nutritional_metabolic_lab_scores = self._analyze_nutritional_metabolic_labs(lab_results)
        lab_scores.update(nutritional_metabolic_lab_scores)
        
        # 增加生殖内分泌疾病实验室检查评分
        reproductive_endocrine_lab_scores = self._analyze_reproductive_endocrine_labs(lab_results)
        lab_scores.update(reproductive_endocrine_lab_scores)
                    
        return lab_scores
    
    def _analyze_imaging(self, imaging_results: List[ImagingResult]) -> Dict[str, float]:
        """分析影像学检查结果"""
        imaging_scores = {}
        
        for imaging in imaging_results:
            # 使用NLP分析影像学报告
            extracted = self.nlp_service.extract_clinical_information(imaging.findings)
            
            # 基于关键词判断相关疾病
            findings_lower = imaging.findings.lower()
            if "甲状腺" in findings_lower or "thyroid" in findings_lower:
                imaging_scores["甲状腺疾病"] = 0.7
            if "肾上腺" in findings_lower or "adrenal" in findings_lower:
                imaging_scores["肾上腺疾病"] = 0.7
            
            # 心血管系统影像学
            if any(term in findings_lower for term in ["冠脉", "冠状动脉", "心肌", "coronary", "myocardial"]):
                imaging_scores["心血管疾病"] = 0.8
            if any(term in findings_lower for term in ["心腔扩大", "射血分数", "心功能", "heart failure", "cardiac"]):
                imaging_scores["心力衰竭"] = 0.75
            
            # 脑血管系统影像学
            if any(term in findings_lower for term in ["脑梗", "脑梗死", "缺血", "stroke", "infarct"]):
                imaging_scores["急性缺血性脑卒中"] = 0.9
            if any(term in findings_lower for term in ["脑出血", "血肿", "hemorrhage", "hematoma"]):
                imaging_scores["急性出血性脑卒中"] = 0.9
            if any(term in findings_lower for term in ["颈动脉", "血管狭窄", "carotid", "stenosis"]):
                imaging_scores["脑血管疾病"] = 0.7
            
            # 神经系统影像学
            if any(term in findings_lower for term in ["神经根", "脱髓鞘", "周围神经", "neuropathy", "demyelination"]):
                imaging_scores["神经病变"] = 0.7
                
        return imaging_scores
    
    def _analyze_rheumatic_labs(self, lab_results: List[LabResult]) -> Dict[str, float]:
        """分析风湿免疫疾病相关实验室检查"""
        rheumatic_lab_scores = {}
        
        for result in lab_results:
            test_name_lower = result.test_name.lower()
            value = result.value
            
            # 自身抗体检查
            if "抗tpo" in test_name_lower or "tpo" in test_name_lower:
                if isinstance(value, (int, float)) and value > 50:
                    rheumatic_lab_scores["桥本甲状腺炎"] = rheumatic_lab_scores.get("桥本甲状腺炎", 0.0) + 0.6
            
            if "抗21羟化酶" in test_name_lower or "21-hydroxylase" in test_name_lower:
                if "阳性" in str(value) or (isinstance(value, (int, float)) and value > 1.0):
                    rheumatic_lab_scores["Addison病"] = rheumatic_lab_scores.get("Addison病", 0.0) + 0.7
                    
            if "抗gad" in test_name_lower or "gad" in test_name_lower:
                if "阳性" in str(value) or (isinstance(value, (int, float)) and value > 5.0):
                    rheumatic_lab_scores["1型糖尿病"] = rheumatic_lab_scores.get("1型糖尿病", 0.0) + 0.6
                    
            if "ana" in test_name_lower or "抗核抗体" in test_name_lower:
                if "阳性" in str(value) or "1:160" in str(value) or "1:320" in str(value):
                    rheumatic_lab_scores["系统性红斑狼疮"] = rheumatic_lab_scores.get("系统性红斑狼疮", 0.0) + 0.4
                    
            if "抗ds-dna" in test_name_lower or "ds-dna" in test_name_lower:
                if "阳性" in str(value) or (isinstance(value, (int, float)) and value > 30):
                    rheumatic_lab_scores["系统性红斑狼疮"] = rheumatic_lab_scores.get("系统性红斑狼疮", 0.0) + 0.7
                    
            if "抗sm" in test_name_lower or "sm抗体" in test_name_lower:
                if "阳性" in str(value):
                    rheumatic_lab_scores["系统性红斑狼疮"] = rheumatic_lab_scores.get("系统性红斑狼疮", 0.0) + 0.8
                    
            if "rf" in test_name_lower or "类风湿因子" in test_name_lower:
                if "阳性" in str(value) or (isinstance(value, (int, float)) and value > 20):
                    rheumatic_lab_scores["类风湿关节炎"] = rheumatic_lab_scores.get("类风湿关节炎", 0.0) + 0.4
                    
            if "抗ccp" in test_name_lower or "ccp" in test_name_lower:
                if "阳性" in str(value) or (isinstance(value, (int, float)) and value > 20):
                    rheumatic_lab_scores["类风湿关节炎"] = rheumatic_lab_scores.get("类风湿关节炎", 0.0) + 0.7
                    
            if "抗ssa" in test_name_lower or "抗ssb" in test_name_lower or "ro52" in test_name_lower:
                if "阳性" in str(value):
                    rheumatic_lab_scores["干燥综合征"] = rheumatic_lab_scores.get("干燥综合征", 0.0) + 0.6
                    
            # 激素检查异常提示多腺体综合征
            if "皮质醇" in test_name_lower and isinstance(value, (int, float)) and value < 100:
                rheumatic_lab_scores["肾上腺功能不全"] = rheumatic_lab_scores.get("肾上腺功能不全", 0.0) + 0.5
                
            if "pth" in test_name_lower and isinstance(value, (int, float)) and value < 15:
                rheumatic_lab_scores["甲状旁腺功能减退"] = rheumatic_lab_scores.get("甲状旁腺功能减退", 0.0) + 0.6
                
            # 炎症指标
            if "esr" in test_name_lower or "血沉" in test_name_lower:
                if isinstance(value, (int, float)) and value > 30:
                    rheumatic_lab_scores["系统性炎症疾病"] = rheumatic_lab_scores.get("系统性炎症疾病", 0.0) + 0.3
                    
            if "crp" in test_name_lower or "c反应蛋白" in test_name_lower:
                if isinstance(value, (int, float)) and value > 10:
                    rheumatic_lab_scores["活动性炎症"] = rheumatic_lab_scores.get("活动性炎症", 0.0) + 0.3
                    
            # 补体检查
            if "c3" in test_name_lower or "c4" in test_name_lower:
                if isinstance(value, (int, float)) and value < 0.8:
                    rheumatic_lab_scores["补体消耗性疾病"] = rheumatic_lab_scores.get("补体消耗性疾病", 0.0) + 0.4
                    rheumatic_lab_scores["系统性红斑狼疮"] = rheumatic_lab_scores.get("系统性红斑狼疮", 0.0) + 0.3
        
        return rheumatic_lab_scores
    
    def _analyze_uric_acid_labs(self, lab_results: List[LabResult]) -> Dict[str, float]:
        """分析尿酸代谢疾病相关实验室检查"""
        uric_acid_lab_scores = {}
        
        for result in lab_results:
            test_name_lower = result.test_name.lower()
            value = result.value
            
            # 血尿酸检查
            if "尿酸" in test_name_lower or "uric acid" in test_name_lower:
                if isinstance(value, (int, float)):
                    # 高尿酸血症诊断标准
                    if value > 420:  # μmol/L，男性
                        uric_acid_lab_scores["高尿酸血症"] = 0.9
                    elif value > 360:  # μmol/L，女性
                        uric_acid_lab_scores["高尿酸血症"] = 0.8
                    elif value > 300:  # 轻度升高
                        uric_acid_lab_scores["高尿酸血症"] = 0.6
                        
                    # 痛风风险评估
                    if value > 480:  # 高痛风风险
                        uric_acid_lab_scores["痛风"] = 0.7
                    elif value > 420:
                        uric_acid_lab_scores["痛风"] = 0.5
                        
            # 24小时尿尿酸
            if "24小时尿尿酸" in test_name_lower or "24h尿酸" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 4200:  # μmol/24h，尿酸产生过多型
                        uric_acid_lab_scores["尿酸产生过多型高尿酸血症"] = 0.8
                    elif value < 1800:  # 尿酸排泄减少型
                        uric_acid_lab_scores["尿酸排泄减少型高尿酸血症"] = 0.8
                        
            # 尿酸清除率
            if "尿酸清除率" in test_name_lower:
                if isinstance(value, (int, float)) and value < 6.2:
                    uric_acid_lab_scores["尿酸排泄减少型高尿酸血症"] = 0.7
                    
            # 肾功能检查（痛风性肾病相关）
            if "肌酐" in test_name_lower or "creatinine" in test_name_lower:
                if isinstance(value, (int, float)) and value > 115:  # μmol/L
                    uric_acid_lab_scores["痛风性肾病"] = uric_acid_lab_scores.get("痛风性肾病", 0.0) + 0.4
                    
            if "尿素氮" in test_name_lower or "bun" in test_name_lower:
                if isinstance(value, (int, float)) and value > 7.5:  # mmol/L
                    uric_acid_lab_scores["痛风性肾病"] = uric_acid_lab_scores.get("痛风性肾病", 0.0) + 0.3
                    
            # 尿液检查
            if "蛋白尿" in test_name_lower or "proteinuria" in test_name_lower:
                if "阳性" in str(value) or "+" in str(value):
                    uric_acid_lab_scores["痛风性肾病"] = uric_acid_lab_scores.get("痛风性肾病", 0.0) + 0.5
                    
            # 关节液检查（痛风诊断金标准）
            if "关节液" in test_name_lower or "synovial fluid" in test_name_lower:
                if "尿酸盐结晶" in str(value) or "urate crystal" in str(value):
                    uric_acid_lab_scores["急性痛风"] = 0.95
                    uric_acid_lab_scores["痛风"] = 0.95
                    
            # 代谢相关检查
            if "血糖" in test_name_lower or "glucose" in test_name_lower:
                if isinstance(value, (int, float)) and value > 7.0:  # mmol/L
                    uric_acid_lab_scores["代谢综合征合并高尿酸血症"] = 0.4
                    
            if "甘油三酯" in test_name_lower or "triglyceride" in test_name_lower:
                if isinstance(value, (int, float)) and value > 2.3:  # mmol/L
                    uric_acid_lab_scores["代谢综合征合并高尿酸血症"] = uric_acid_lab_scores.get("代谢综合征合并高尿酸血症", 0.0) + 0.3
                    
            # 炎症指标（急性痛风发作）
            if "白细胞" in test_name_lower or "wbc" in test_name_lower:
                if isinstance(value, (int, float)) and value > 10:  # x10^9/L
                    uric_acid_lab_scores["急性痛风"] = uric_acid_lab_scores.get("急性痛风", 0.0) + 0.3
                    
            if "中性粒细胞" in test_name_lower:
                if isinstance(value, (int, float)) and value > 70:  # %
                    uric_acid_lab_scores["急性痛风"] = uric_acid_lab_scores.get("急性痛风", 0.0) + 0.3
                    
        return uric_acid_lab_scores
    
    def _analyze_bone_metabolism_labs(self, lab_results: List[LabResult]) -> Dict[str, float]:
        """分析骨代谢疾病相关实验室检查"""
        bone_lab_scores = {}
        
        for result in lab_results:
            test_name_lower = result.test_name.lower()
            value = result.value
            
            # 钙磷代谢检查
            if "血钙" in test_name_lower or "血清钙" in test_name_lower or "calcium" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 2.65:  # mmol/L 高钙血症
                        bone_lab_scores["原发性甲状旁腺功能亢进"] = 0.8
                        bone_lab_scores["甲状旁腺性骨病"] = 0.7
                    elif value < 2.20:  # mmol/L 低钙血症
                        bone_lab_scores["甲状旁腺功能减退"] = 0.7
                        bone_lab_scores["维生素D缺乏"] = 0.6
                        bone_lab_scores["骨软化症"] = 0.5
                        
            if "血磷" in test_name_lower or "磷酸盐" in test_name_lower or "phosphate" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value < 0.85:  # mmol/L 低磷血症
                        bone_lab_scores["骨软化症"] = bone_lab_scores.get("骨软化症", 0.0) + 0.6
                        bone_lab_scores["维生素D缺乏"] = bone_lab_scores.get("维生素D缺乏", 0.0) + 0.5
                        bone_lab_scores["遗传性低磷血症性佝偻病"] = 0.7
                        
            # 甲状旁腺激素
            if "pth" in test_name_lower or "甲状旁腺激素" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 65:  # pg/mL (参考值因实验室而异)
                        bone_lab_scores["继发性甲状旁腺功能亢进"] = 0.7
                        bone_lab_scores["维生素D缺乏"] = 0.6
                        bone_lab_scores["骨软化症"] = 0.5
                        # 如果同时有高钙血症，提示原发性
                        bone_lab_scores["原发性甲状旁腺功能亢进"] = 0.8
                    elif value < 15:  # pg/mL
                        bone_lab_scores["甲状旁腺功能减退"] = 0.8
                        
            # 维生素D水平
            if "25羟维生素d" in test_name_lower or "25(oh)d" in test_name_lower or "维生素d" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value < 50:  # nmol/L (20ng/mL) 缺乏
                        bone_lab_scores["维生素D缺乏"] = 0.9
                        bone_lab_scores["骨软化症"] = 0.8
                        bone_lab_scores["佝偻病"] = 0.7
                    elif value < 75:  # nmol/L (30ng/mL) 不足
                        bone_lab_scores["维生素D不足"] = 0.7
                        bone_lab_scores["骨软化症"] = 0.4
                        
            # 碱性磷酸酶
            if "碱性磷酸酶" in test_name_lower or "alp" in test_name_lower or "alkaline" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 150:  # U/L (参考值因实验室而异)
                        bone_lab_scores["骨软化症"] = bone_lab_scores.get("骨软化症", 0.0) + 0.5
                        bone_lab_scores["甲状旁腺性骨病"] = bone_lab_scores.get("甲状旁腺性骨病", 0.0) + 0.4
                        bone_lab_scores["佝偻病"] = bone_lab_scores.get("佝偻病", 0.0) + 0.5
                        
            # 骨转换标志物
            if "骨特异性碱性磷酸酶" in test_name_lower or "balp" in test_name_lower:
                if isinstance(value, (int, float)) and value > 20:  # μg/L
                    bone_lab_scores["骨质疏松症"] = bone_lab_scores.get("骨质疏松症", 0.0) + 0.4
                    bone_lab_scores["甲状旁腺性骨病"] = bone_lab_scores.get("甲状旁腺性骨病", 0.0) + 0.5
                    
            if "骨钙蛋白" in test_name_lower or "osteocalcin" in test_name_lower:
                if isinstance(value, (int, float)) and value > 30:  # ng/mL
                    bone_lab_scores["骨转换增加"] = 0.5
                    
            if "ctx" in test_name_lower or "胶原交联" in test_name_lower:
                if isinstance(value, (int, float)) and value > 0.6:  # ng/mL
                    bone_lab_scores["骨吸收增加"] = 0.5
                    bone_lab_scores["骨质疏松症"] = bone_lab_scores.get("骨质疏松症", 0.0) + 0.3
                    
            # 24小时尿钙
            if "24小时尿钙" in test_name_lower or "24h尿钙" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 10:  # mmol/24h 高钙尿症
                        bone_lab_scores["原发性甲状旁腺功能亢进"] = bone_lab_scores.get("原发性甲状旁腺功能亢进", 0.0) + 0.4
                    elif value < 1:  # mmol/24h 低钙尿症
                        bone_lab_scores["家族性低钙尿性高钙血症"] = 0.6
                        bone_lab_scores["维生素D缺乏"] = bone_lab_scores.get("维生素D缺乏", 0.0) + 0.3
                        
            # 肾功能（影响维生素D代谢）
            if "肌酐" in test_name_lower or "creatinine" in test_name_lower:
                if isinstance(value, (int, float)) and value > 115:  # μmol/L
                    bone_lab_scores["肾性骨病"] = 0.6
                    bone_lab_scores["继发性甲状旁腺功能亢进"] = 0.5
                    
            # 镁（影响PTH分泌）
            if "血镁" in test_name_lower or "镁" in test_name_lower or "magnesium" in test_name_lower:
                if isinstance(value, (int, float)) and value < 0.7:  # mmol/L
                    bone_lab_scores["功能性甲状旁腺功能减退"] = 0.6
                    
        return bone_lab_scores
    
    def _analyze_nutritional_metabolic_labs(self, lab_results: List[LabResult]) -> Dict[str, float]:
        """分析营养代谢疾病相关实验室检查"""
        nutritional_lab_scores = {}
        
        for result in lab_results:
            test_name_lower = result.test_name.lower()
            value = result.value
            
            # 肥胖症相关指标
            if "bmi" in test_name_lower or "体质指数" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value >= 30:  # WHO标准
                        nutritional_lab_scores["肥胖症"] = 0.9
                    elif value >= 25:  # 亚洲标准超重
                        nutritional_lab_scores["肥胖症"] = 0.7
                        nutritional_lab_scores["代谢综合征"] = 0.5
                    elif value >= 23:  # 亚洲标准
                        nutritional_lab_scores["肥胖症"] = 0.5
            
            # 腰围指标  
            if "腰围" in test_name_lower or "waist" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value >= 90:  # 男性标准
                        nutritional_lab_scores["代谢综合征"] = 0.7
                        nutritional_lab_scores["肥胖症"] = 0.6
                    elif value >= 80:  # 女性标准
                        nutritional_lab_scores["代谢综合征"] = 0.6
                        nutritional_lab_scores["肥胖症"] = 0.5
                        
            # 体脂率
            if "体脂率" in test_name_lower or "body fat" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value >= 35:  # 女性肥胖标准
                        nutritional_lab_scores["肥胖症"] = 0.8
                    elif value >= 25:  # 男性肥胖标准
                        nutritional_lab_scores["肥胖症"] = 0.8
                        
            # 胰岛素相关检查
            if "胰岛素" in test_name_lower or "insulin" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 25:  # 高胰岛素血症
                        nutritional_lab_scores["胰岛素抵抗"] = 0.8
                        nutritional_lab_scores["代谢综合征"] = 0.7
                        nutritional_lab_scores["肥胖症"] = 0.5
                        
            # HOMA-IR胰岛素抵抗指数
            if "homa" in test_name_lower or "胰岛素抵抗指数" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 2.5:  # 胰岛素抵抗
                        nutritional_lab_scores["胰岛素抵抗"] = 0.9
                        nutritional_lab_scores["代谢综合征"] = 0.8
                    elif value > 1.9:  # 轻度胰岛素抵抗
                        nutritional_lab_scores["胰岛素抵抗"] = 0.6
                        nutritional_lab_scores["代谢综合征"] = 0.5
                        
            # 空腹血糖
            if "空腹血糖" in test_name_lower or "fasting glucose" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value >= 7.0:  # 糖尿病
                        nutritional_lab_scores["2型糖尿病"] = 0.9
                        nutritional_lab_scores["代谢综合征"] = 0.7
                    elif value >= 6.1:  # 空腹血糖受损
                        nutritional_lab_scores["2型糖尿病前期"] = 0.8
                        nutritional_lab_scores["代谢综合征"] = 0.8
                    elif value >= 5.6:  # 临界值
                        nutritional_lab_scores["代谢综合征"] = 0.5
                        
            # 糖化血红蛋白
            if "糖化血红蛋白" in test_name_lower or "hba1c" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value >= 6.5:  # 糖尿病
                        nutritional_lab_scores["2型糖尿病"] = 0.9
                        nutritional_lab_scores["代谢综合征"] = 0.7
                    elif value >= 6.0:  # 糖尿病前期
                        nutritional_lab_scores["2型糖尿病前期"] = 0.8
                        nutritional_lab_scores["代谢综合征"] = 0.6
                    elif value >= 5.7:  # 风险增加
                        nutritional_lab_scores["代谢综合征"] = 0.4
                        
            # 甘油三酯
            if "甘油三酯" in test_name_lower or "triglyceride" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value >= 2.26:  # 严重升高
                        nutritional_lab_scores["脂代谢紊乱"] = 0.9
                        nutritional_lab_scores["代谢综合征"] = 0.8
                    elif value >= 1.7:  # 代谢综合征标准
                        nutritional_lab_scores["代谢综合征"] = 0.7
                        nutritional_lab_scores["脂代谢紊乱"] = 0.6
                        
            # HDL胆固醇
            if "hdl" in test_name_lower or "高密度脂蛋白" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value < 1.0:  # 男性低HDL
                        nutritional_lab_scores["代谢综合征"] = 0.6
                        nutritional_lab_scores["脂代谢紊乱"] = 0.5
                    elif value < 1.3:  # 女性低HDL
                        nutritional_lab_scores["代谢综合征"] = 0.6
                        nutritional_lab_scores["脂代谢紊乱"] = 0.5
                        
            # 维生素D
            if "维生素d" in test_name_lower or "25羟维生素d" in test_name_lower or "25(oh)d" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value < 50:  # 缺乏(<20 ng/ml)
                        nutritional_lab_scores["维生素D缺乏症"] = 0.9
                    elif value < 75:  # 不足(20-30 ng/ml)
                        nutritional_lab_scores["维生素D缺乏症"] = 0.6
                        
            # C反应蛋白（炎症标志物）
            if "c反应蛋白" in test_name_lower or "crp" in test_name_lower or "hs-crp" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 3.0:  # 高敏CRP升高
                        nutritional_lab_scores["肥胖症"] = nutritional_lab_scores.get("肥胖症", 0.0) + 0.3
                        nutritional_lab_scores["代谢综合征"] = nutritional_lab_scores.get("代谢综合征", 0.0) + 0.3
                        
            # 瘦素
            if "瘦素" in test_name_lower or "leptin" in test_name_lower:
                if isinstance(value, (int, float)):
                    # 瘦素水平与BMI相关，升高提示瘦素抵抗
                    if value > 15:  # ng/ml，高瘦素血症
                        nutritional_lab_scores["肥胖症"] = 0.7
                        nutritional_lab_scores["瘦素抵抗"] = 0.8
                        
            # 脂联素
            if "脂联素" in test_name_lower or "adiponectin" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value < 4.0:  # μg/ml，脂联素降低
                        nutritional_lab_scores["代谢综合征"] = nutritional_lab_scores.get("代谢综合征", 0.0) + 0.4
                        nutritional_lab_scores["胰岛素抵抗"] = nutritional_lab_scores.get("胰岛素抵抗", 0.0) + 0.4
                        
            # ALT/AST（非酒精性脂肪肝相关）
            if "alt" in test_name_lower or "谷丙转氨酶" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 40:  # U/L，转氨酶升高
                        nutritional_lab_scores["非酒精性脂肪肝"] = 0.5
                        nutritional_lab_scores["肥胖症"] = nutritional_lab_scores.get("肥胖症", 0.0) + 0.2
                        
            # γ-GT（脂肪肝标志物）
            if "γ-gt" in test_name_lower or "ggt" in test_name_lower or "谷氨酰转肽酶" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 50:  # U/L
                        nutritional_lab_scores["非酒精性脂肪肝"] = nutritional_lab_scores.get("非酒精性脂肪肝", 0.0) + 0.4
                        
            # 尿酸（代谢综合征相关）
            if "尿酸" in test_name_lower or "uric acid" in test_name_lower:
                if isinstance(value, (int, float)):
                    if value > 420:  # μmol/L，男性高尿酸
                        nutritional_lab_scores["代谢综合征"] = nutritional_lab_scores.get("代谢综合征", 0.0) + 0.3
                    elif value > 360:  # μmol/L，女性高尿酸
                        nutritional_lab_scores["代谢综合征"] = nutritional_lab_scores.get("代谢综合征", 0.0) + 0.3
                        
        return nutritional_lab_scores
    
    def _combine_scores(self, symptom_scores: Dict, lab_scores: Dict, imaging_scores: Dict) -> Dict[str, float]:
        """综合各项评分"""
        all_diseases = set(symptom_scores.keys()) | set(lab_scores.keys()) | set(imaging_scores.keys())
        combined_scores = {}
        
        for disease in all_diseases:
            symptom_score = symptom_scores.get(disease, 0.0) * 0.4
            lab_score = lab_scores.get(disease, 0.0) * 0.4  
            imaging_score = imaging_scores.get(disease, 0.0) * 0.2
            
            combined_scores[disease] = symptom_score + lab_score + imaging_score
            
        return combined_scores
    
    def _generate_evidence(self, diagnosis: str, request: DiagnosticRequest) -> List[str]:
        """生成支持诊断的证据"""
        evidence = []
        evidence.append(f"症状模式与{diagnosis}典型表现相符")
        
        if request.lab_results:
            evidence.append("实验室检查支持诊断")
            
        if request.imaging:
            evidence.append("影像学检查提示相关病变")
            
        return evidence
    
    def _recommend_tests(self, diagnosis: str) -> List[str]:
        """推荐进一步检查"""
        # 基于诊断推荐相关检查
        recommendations = {
            "甲状腺疾病": ["甲状腺超声", "TRAb", "甲状腺核素显像"],
            "糖尿病": ["OGTT", "胰岛素水平", "C肽"],
            "肾上腺疾病": ["肾上腺CT", "24小时尿皮质醇", "地塞米松抑制试验"],
            "性腺功能异常": ["盆腔超声/阴囊超声", "性激素全套", "骨密度检查"],
            "垂体疾病": ["垂体MRI", "动态激素试验", "视野检查"],
            "多囊卵巢综合征": ["盆腔超声", "OGTT", "胰岛素释放试验", "雄激素谱"],
            "男性性腺功能减退症": ["睾丸超声", "骨密度", "前列腺检查", "精液分析"],
            # 风湿免疫疾病检查推荐
            "1型糖尿病": ["抗GAD抗体", "抗IA-2抗体", "抗ZnT8抗体", "C肽", "HbA1c"],
            "桥本甲状腺炎": ["抗TPO抗体", "抗TG抗体", "甲状腺超声", "TSH", "T4"],
            "Addison病": ["抗21羟化酶抗体", "ACTH刺激试验", "肾上腺CT", "电解质", "皮质醇"],
            "系统性红斑狼疮": ["ANA", "抗ds-DNA", "抗Sm抗体", "补体C3/C4", "24小时尿蛋白"],
            "类风湿关节炎": ["RF", "抗CCP抗体", "关节X线", "ESR", "CRP"],
            "干燥综合征": ["抗SSA/SSB抗体", "唇腺活检", "泪液分泌试验", "腮腺造影"],
            "多腺体自身免疫综合征I型": ["AIRE基因检测", "多种器官特异性抗体", "激素全套", "真菌培养"],
            "多腺体自身免疫综合征II型": ["HLA分型", "多种器官特异性抗体", "激素全套", "家族筛查"],
            "高血压": ["24小时动态血压", "肾动脉超声", "醛固酮/肾素比值"],
            # 骨代谢疾病检查推荐
            "骨质疏松症": ["双能X线骨密度测定(DEXA)", "血钙", "血磷", "甲状旁腺激素(PTH)", 
                       "25羟维生素D", "碱性磷酸酶", "骨转换标记物(CTX、P1NP)", "腰椎X线", "甲状腺功能"],
            "骨软化症": ["25羟维生素D", "1,25二羟维生素D", "血钙", "血磷", "甲状旁腺激素(PTH)", 
                      "碱性磷酸酶", "24小时尿磷", "骨活检", "X线检查", "肾功能"],
            "甲状旁腺性骨病": ["甲状旁腺激素(PTH)", "血钙", "血磷", "碱性磷酸酶", "25羟维生素D", 
                         "肌酐", "甲状旁腺超声或99mTc-MIBI显像", "双能X线骨密度测定", "尿钙", "骨转换标记物"],
            # 营养代谢疾病检查推荐
            "肥胖症": ["BMI测定", "腰围测量", "体脂率", "空腹血糖", "胰岛素", "HOMA-IR", 
                     "血脂全套", "肝功能", "甲状腺功能", "皮质醇", "睡眠呼吸监测"],
            "代谢综合征": ["腰围测量", "血压监测", "空腹血糖", "OGTT", "胰岛素释放试验", 
                        "血脂全套", "糖化血红蛋白", "尿酸", "hs-CRP", "肝功能"],
            "维生素D缺乏症": ["25羟维生素D", "1,25二羟维生素D", "甲状旁腺激素", "血钙", "血磷", 
                           "碱性磷酸酶", "骨密度测定", "骨转换标记物", "肾功能", "镁离子"],
            "心血管疾病": ["心电图", "超声心动图", "冠脉CTA", "心肌酶谱", "BNP"],
            "冠心病": ["冠脉造影", "运动负荷试验", "心肌血流灌注显像"],
            "急性心肌梗死": ["急诊冠脉造影", "肌钙蛋白", "CK-MB", "超声心动图"],
            "心力衰竭": ["NT-proBNP", "超声心动图", "胸部X线", "心脏MRI"],
            "心房颤动": ["动态心电图", "超声心动图", "食道超声", "甲状腺功能"],
            "脑血管疾病": ["头颅CT/MRI", "颈动脉超声", "心电图", "凝血功能"],
            "急性缺血性脑卒中": ["急诊CT", "弥散加权成像", "血管成像", "心脏评估"],
            "急性出血性脑卒中": ["急诊CT", "CTA", "凝血功能", "血管成像"],
            "短暂性脑缺血发作": ["MRI-DWI", "颈动脉超声", "动态心电图", "超声心动图"],
            "神经病变": ["神经传导速度", "肌电图", "定量感觉检查", "自主神经功能检查"],
            "糖尿病周围神经病变": ["10g单丝检查", "128Hz音叉", "神经传导速度", "HbA1c"],
            "糖尿病自主神经病变": ["心率变异性", "立位试验", "胃排空检查", "膀胱残余尿"],
            "格林-巴利综合征": ["脑脊液检查", "神经传导速度", "抗神经节苷脂抗体", "肺功能"],
            # 尿酸代谢疾病检查推荐
            "高尿酸血症": ["血尿酸", "24小时尿尿酸", "尿酸清除率", "肾功能", "血脂", "血糖", "肝功能"],
            "急性痛风": ["血尿酸", "关节液检查", "关节X线", "血常规", "CRP", "ESR", "肾功能"],
            "慢性痛风": ["血尿酸", "关节X线", "关节CT", "肾功能", "24小时尿尿酸", "尿常规", "心电图"],
            "痛风": ["血尿酸", "关节液检查", "关节影像学", "肾功能", "心血管风险评估"],
            "痛风性肾病": ["肾功能全套", "尿常规", "24小时尿蛋白", "肾脏超声", "血尿酸", "尿酸清除率"],
            "尿酸性肾结石": ["泌尿系CT", "尿常规", "24小时尿尿酸", "尿pH", "结石成分分析", "肾功能"],
            "尿酸产生过多型高尿酸血症": ["24小时尿尿酸", "嘌呤代谢酶检测", "细胞增殖性疾病筛查", "肝功能"],
            "尿酸排泄减少型高尿酸血症": ["尿酸清除率", "肾功能", "药物使用史评估", "内分泌功能检查"],
            "代谢综合征合并高尿酸血症": ["OGTT", "胰岛素释放试验", "血脂全套", "血压监测", "腰围测量", "肝脏超声"]
        }
        
        return recommendations.get(diagnosis, ["血常规", "生化全项", "相关激素检查"])
    
    def _assess_urgency(self, diagnosis: str, confidence: float) -> str:
        """评估紧急程度"""
        if confidence > 0.8:
            urgent_conditions = [
                "甲状腺危象", "糖尿病酮症酸中毒", "肾上腺危象",
                "急性心肌梗死", "急性心力衰竭", "心源性休克", 
                "急性缺血性脑卒中", "急性出血性脑卒中",
                "格林-巴利综合征"
            ]
            if any(condition in diagnosis for condition in urgent_conditions):
                return "紧急"
                
        moderate_urgent = [
            "心房颤动", "不稳定性心绞痛", "短暂性脑缺血发作"
        ]
        if confidence > 0.7 and any(condition in diagnosis for condition in moderate_urgent):
            return "较急"
        
        return "常规" if confidence > 0.6 else "需进一步评估"
    
    def _get_icd10_code(self, diagnosis: str) -> Optional[str]:
        """获取ICD-10编码"""
        icd10_codes = {
            "甲状腺功能亢进": "E05",
            "甲状腺功能减退": "E03", 
            "2型糖尿病": "E11",
            "原发性醛固酮增多症": "E26.0",
            "多囊卵巢综合征": "E28.2",
            "男性性腺功能减退症": "E29.1",
            "女性性腺功能减退症": "E28.3",
            "库欣综合征": "E24.9",
            "嗜铬细胞瘤": "D35.0",
            "泌乳素瘤": "D35.2",
            "肢端肥大症": "E22.0",
            "生长激素缺乏症": "E23.0",
            "中枢性尿崩症": "E23.2",
            # 风湿免疫疾病ICD-10编码
            "1型糖尿病": "E10",
            "桥本甲状腺炎": "E06.3",
            "Addison病": "E27.1",
            "系统性红斑狼疮": "M32",
            "类风湿关节炎": "M05",
            "干燥综合征": "M35.0",
            "多腺体自身免疫综合征I型": "E31.0",
            "多腺体自身免疫综合征II型": "E31.0",
            "甲状旁腺功能减退": "E20",
            # 骨代谢疾病ICD-10编码
            "骨质疏松症": "M80.9",
            "骨软化症": "M83.9", 
            "甲状旁腺性骨病": "E21.0",
            # 营养代谢疾病ICD-10编码
            "肥胖症": "E66.9",
            "代谢综合征": "E88.81", 
            "维生素D缺乏症": "E55.9",
            # 心血管疾病
            "冠心病": "I25.9",
            "急性心肌梗死": "I21.9",
            "心力衰竭": "I50.9",
            "心房颤动": "I48.9",
            # 脑血管疾病
            "急性缺血性脑卒中": "I63.9",
            "急性出血性脑卒中": "I61.9",
            "短暂性脑缺血发作": "G45.9",
            # 神经病变
            "糖尿病周围神经病变": "G63.2",
            "糖尿病自主神经病变": "G99.0",
            "急性炎症性脱髓鞘性多发性神经病变": "G61.0",
            "格林-巴利综合征": "G61.0",
            # 尿酸代谢疾病
            "高尿酸血症": "E79.0",
            "痛风": "M10.9",
            "急性痛风": "M10.9",
            "慢性痛风": "M10.9",
            "痛风性肾病": "N08.2",
            "尿酸性肾结石": "N20.0",
            "尿酸产生过多型高尿酸血症": "E79.0",
            "尿酸排泄减少型高尿酸血症": "E79.0",
            "代谢综合征合并高尿酸血症": "E88.9"
        }
        return icd10_codes.get(diagnosis)
    
    def _get_diagnosis_rationale(self, diagnosis: str) -> str:
        """获取诊断依据说明"""
        return f"{diagnosis}的诊断基于临床表现、实验室检查和影像学证据的综合分析"

class TreatmentEngine:
    """治疗推荐引擎"""
    
    def __init__(self, kg_service: KnowledgeGraphService):
        self.kg_service = kg_service
        
    def recommend_treatment(self, request: TreatmentRequest) -> List[TreatmentPlan]:
        """推荐个性化治疗方案"""
        treatment_plans = []
        
        for diagnosis in request.diagnoses:
            # 获取标准治疗方案
            standard_treatment = self._get_standard_treatment(diagnosis)
            
            # 个性化调整
            personalized_treatment = self._personalize_treatment(
                standard_treatment, 
                request.patient,
                request.comorbidities,
                request.contraindications
            )
            
            # 生成监测计划
            monitoring_plan = self._generate_monitoring_plan(diagnosis, personalized_treatment)
            
            treatment_plan = TreatmentPlan(
                treatment_id=f"TREAT_{diagnosis}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                primary_therapy=personalized_treatment["primary"],
                adjunctive_therapies=personalized_treatment.get("adjunctive", []),
                monitoring_plan=monitoring_plan,
                follow_up_schedule=self._generate_follow_up_schedule(diagnosis),
                patient_education=self._generate_patient_education(diagnosis),
                expected_outcomes=self._generate_expected_outcomes(diagnosis)
            )
            
            treatment_plans.append(treatment_plan)
            
        return treatment_plans
    
    def _get_standard_treatment(self, diagnosis: str) -> Dict[str, Any]:
        """获取标准治疗方案"""
        # 从知识图谱获取治疗信息
        disease_info = self.kg_service.get_disease_info(diagnosis)
        
        # 标准治疗方案模板
        standard_treatments = {
            "甲状腺功能亢进": {
                "primary": {
                    "medication": "甲巯咪唑",
                    "dose": "5-15mg 每日2-3次",
                    "duration": "18-24个月"
                },
                "alternatives": ["丙基硫氧嘧啶", "放射性碘治疗", "手术治疗"]
            },
            "2型糖尿病": {
                "primary": {
                    "medication": "二甲双胍", 
                    "dose": "500-1000mg 每日2次",
                    "duration": "长期"
                },
                "adjunctive": ["生活方式干预", "血糖监测", "并发症筛查"]
            }
        }
        
        return standard_treatments.get(diagnosis, {})
    
    def _personalize_treatment(self, standard_treatment: Dict, patient: PatientProfile, 
                             comorbidities: List[str], contraindications: List[str]) -> Dict[str, Any]:
        """个性化治疗方案"""
        personalized = standard_treatment.copy()
        
        # 年龄调整
        if patient.age >= 65:
            personalized["considerations"] = "老年人减量起始"
            
        # 合并症调整
        if "慢性肾病" in comorbidities:
            personalized["renal_adjustment"] = "根据肾功能调整剂量"
            
        # 禁忌症处理
        for contraindication in contraindications:
            if contraindication in personalized.get("primary", {}).get("medication", ""):
                personalized["alternative_required"] = True
                
        return personalized
    
    def _generate_monitoring_plan(self, diagnosis: str, treatment: Dict) -> Dict[str, Any]:
        """生成监测计划"""
        monitoring_plans = {
            "甲状腺功能亢进": {
                "baseline": ["TSH", "FT4", "FT3", "肝功能", "血常规"],
                "week_2": ["肝功能", "血常规"],
                "week_6": ["TSH", "FT4", "FT3"],
                "monthly": ["甲功", "症状评估"]
            },
            "2型糖尿病": {
                "baseline": ["HbA1c", "血糖", "肾功能", "血脂"],
                "monthly": ["血糖监测", "体重"],
                "quarterly": ["HbA1c", "并发症筛查"]
            }
        }
        
        return monitoring_plans.get(diagnosis, {"routine": "定期随访"})
    
    def _generate_follow_up_schedule(self, diagnosis: str) -> List[str]:
        """生成随访计划"""
        return [
            "治疗后2周初次随访",
            "治疗后1个月评估疗效", 
            "治疗后3个月全面评估",
            "之后每3-6个月定期随访"
        ]
    
    def _generate_patient_education(self, diagnosis: str) -> List[str]:
        """生成患者教育内容"""
        education_content = {
            "甲状腺功能亢进": [
                "按时服药，不可自行停药",
                "定期监测甲功和血常规",
                "出现发热、咽痛及时就诊",
                "避免含碘食物和药物"
            ],
            "2型糖尿病": [
                "健康饮食，控制总热量",
                "规律运动，每周150分钟中等强度", 
                "血糖监测，记录血糖日记",
                "定期检查并发症"
            ],
            "骨质疏松症": [
                "充足钙摄入，每日1200-1500mg",
                "维生素D补充，每日800-1000IU",
                "规律负重运动，避免跌倒",
                "戒烟限酒，定期骨密度检查"
            ],
            "骨软化症": [
                "充分维生素D和钙剂补充",
                "增加日光暴露，每日30分钟",
                "营养均衡饮食，富含蛋白质",
                "避免过度负重，预防骨折"
            ],
            "甲状旁腺性骨病": [
                "积极治疗原发甲状旁腺疾病",
                "监测血钙和磷水平",
                "适当补充维生素D和钙剂",
                "定期复查骨密度和肾功能"
            ],
            "肥胖症": [
                "建立健康的饮食习惯，控制总热量摄入",
                "规律进行有氧运动和阻抗训练",
                "设定合理减重目标，每月减重2-4kg",
                "监测血压、血糖、血脂变化"
            ],
            "代谢综合征": [
                "综合生活方式干预，减重5-10%",
                "采用地中海饮食模式",
                "每周至少150分钟中等强度运动",
                "定期监测血压、血糖、血脂"
            ],
            "维生素D缺乏症": [
                "合理日光暴露，每日15-30分钟",
                "规律服用维生素D补充剂",
                "增加富含维生素D食物摄入",
                "定期监测25羟维生素D水平"
            ]
        }
        
        return education_content.get(diagnosis, ["遵医嘱用药", "定期随访"])
    
    def _generate_expected_outcomes(self, diagnosis: str) -> Dict[str, Any]:
        """生成预期结果"""
        return {
            "short_term": "症状改善，指标趋向正常",
            "long_term": "疾病控制，预防并发症", 
            "success_rate": "85-95%",
            "time_to_effect": "2-6周"
        }

class RAGSystem:
    """检索增强生成系统"""
    
    def __init__(self, kg_service: KnowledgeGraphService):
        self.kg_service = kg_service
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def answer_question(self, question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """基于知识图谱回答医学问题"""
        # 1. 理解问题意图
        intent = self._classify_intent(question)
        
        # 2. 检索相关知识
        relevant_knowledge = self._retrieve_knowledge(question, intent)
        
        # 3. 生成回答
        answer = self._generate_answer(question, relevant_knowledge, context)
        
        return {
            "question": question,
            "intent": intent,
            "answer": answer,
            "sources": relevant_knowledge.get("sources", []),
            "confidence": answer.get("confidence", 0.0),
            "timestamp": datetime.now().isoformat()
        }
    
    def _classify_intent(self, question: str) -> str:
        """分类问题意图"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ["诊断", "症状", "检查"]):
            return "diagnosis"
        elif any(keyword in question_lower for keyword in ["治疗", "用药", "方案"]):
            return "treatment"
        elif any(keyword in question_lower for keyword in ["原因", "机制", "为什么"]):
            return "explanation"
        else:
            return "general"
    
    def _retrieve_knowledge(self, question: str, intent: str) -> Dict[str, Any]:
        """从知识图谱检索相关知识"""
        # 简化的检索逻辑
        knowledge = {
            "entities": [],
            "relationships": [],
            "sources": []
        }
        
        # 根据意图检索不同类型的知识
        if intent == "diagnosis":
            # 检索疾病、症状、检查相关知识
            pass
        elif intent == "treatment":
            # 检索治疗、药物相关知识  
            pass
            
        return knowledge
    
    def _generate_answer(self, question: str, knowledge: Dict, context: Optional[Dict]) -> Dict[str, Any]:
        """生成回答"""
        try:
            # 构建提示词
            prompt = self._build_prompt(question, knowledge, context)
            
            # 调用OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的内分泌科医生，请基于提供的医学知识回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return {
                "text": response.choices[0].message.content,
                "confidence": 0.8,  # 简化的置信度计算
                "model": "gpt-4"
            }
            
        except Exception as e:
            logger.error(f"生成回答时出错: {e}")
            return {
                "text": "抱歉，无法生成回答。请咨询专业医生。",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _build_prompt(self, question: str, knowledge: Dict, context: Optional[Dict]) -> str:
        """构建GPT提示词"""
        prompt_parts = [
            f"问题: {question}",
            "",
            "相关医学知识:",
        ]
        
        # 添加知识图谱中的相关信息
        if knowledge.get("entities"):
            prompt_parts.append("相关疾病实体:")
            for entity in knowledge["entities"]:
                prompt_parts.append(f"- {entity}")
        
        if context:
            prompt_parts.append(f"患者信息: {context}")
            
        prompt_parts.extend([
            "",
            "请基于以上医学知识回答问题，如果信息不足请说明需要更多信息。",
            "回答应该专业、准确、易懂，并提醒患者咨询专业医生。"
        ])
        
        return "\n".join(prompt_parts)

# ===== 服务实例化 =====
kg_service = KnowledgeGraphService()
nlp_service = MedicalNLPService()
diagnostic_engine = DiagnosticEngine(kg_service, nlp_service)
treatment_engine = TreatmentEngine(kg_service)
rag_system = RAGSystem(kg_service)

# ===== API 端点定义 =====

@app.get("/", summary="API根路径")
async def root():
    """API欢迎信息"""
    return {
        "name": "综合内分泌疾病知识图谱 API",
        "version": "1.0.0",
        "description": "基于权威医学指南的内分泌疾病智能诊疗支持系统",
        "endpoints": {
            "docs": "/docs",
            "health": "/health", 
            "diagnose": "/api/v1/diagnose",
            "treatment": "/api/v1/treatment",
            "qa": "/api/v1/qa"
        }
    }

@app.get("/health", summary="健康检查")
async def health_check():
    """系统健康状态检查"""
    try:
        # 检查各个服务状态
        kg_status = "healthy"  # 简化检查
        nlp_status = "healthy"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "knowledge_graph": kg_status,
                "nlp": nlp_status,
                "api": "healthy"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/api/v1/diagnose", response_model=DiagnosisResult, summary="智能诊断")
async def diagnose_patient(request: DiagnosticRequest):
    """
    基于患者症状、检验结果和影像学信息进行智能诊断
    
    - **患者信息**: 基本信息、既往史、用药史等
    - **症状**: 主要症状、持续时间、严重程度等  
    - **实验室检查**: 各项检验指标和结果
    - **影像学检查**: 影像学检查结果和印象
    
    返回主要诊断、置信度、鉴别诊断列表和推荐检查
    """
    try:
        result = diagnostic_engine.diagnose(request)
        logger.info(f"诊断完成 - 患者: {request.patient.patient_id}, 诊断: {result.primary_diagnosis}")
        return result
    except Exception as e:
        logger.error(f"诊断过程出错: {e}")
        raise HTTPException(status_code=500, detail=f"诊断失败: {str(e)}")

@app.post("/api/v1/treatment", response_model=List[TreatmentPlan], summary="治疗方案推荐")
async def recommend_treatment(request: TreatmentRequest):
    """
    基于诊断结果和患者特征推荐个性化治疗方案
    
    - **诊断列表**: 确诊疾病列表
    - **患者特征**: 年龄、性别、合并症等
    - **禁忌症**: 药物过敏、禁忌症等
    - **治疗目标**: 个性化治疗目标
    
    返回详细的治疗计划，包括用药方案、监测计划、随访安排等
    """
    try:
        treatment_plans = treatment_engine.recommend_treatment(request)
        logger.info(f"治疗推荐完成 - 患者: {request.patient.patient_id}, 方案数: {len(treatment_plans)}")
        return treatment_plans
    except Exception as e:
        logger.error(f"治疗推荐出错: {e}")
        raise HTTPException(status_code=500, detail=f"治疗推荐失败: {str(e)}")

@app.post("/api/v1/qa", summary="医学问答")
async def medical_qa(
    question: str = Body(..., description="医学问题"),
    context: Optional[Dict[str, Any]] = Body(None, description="上下文信息")
):
    """
    基于知识图谱的医学问答系统
    
    - **question**: 医学相关问题
    - **context**: 可选的上下文信息（如患者信息）
    
    返回基于权威医学知识的专业回答
    """
    try:
        answer = rag_system.answer_question(question, context)
        logger.info(f"问答完成 - 问题类型: {answer['intent']}")
        return answer
    except Exception as e:
        logger.error(f"问答系统出错: {e}")
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")

@app.post("/api/v1/extract", summary="临床文本结构化解析")
async def extract_clinical_info(
    text: str = Body(..., description="临床文本"),
    language: str = Body("zh", description="文本语言")
):
    """
    从临床文本中提取结构化医学信息
    
    - **text**: 临床记录、病历等文本
    - **language**: 文本语言（zh/en）
    
    返回提取的症状、药物、检验值等结构化信息
    """
    try:
        # 医学实体识别
        entities = nlp_service.extract_medical_entities(text, language)
        
        # 临床信息提取
        clinical_info = nlp_service.extract_clinical_information(text)
        
        result = {
            "original_text": text,
            "language": language,
            "entities": entities,
            "structured_info": clinical_info,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"文本解析完成 - 实体数: {len(entities.get('entities', []))}")
        return result
        
    except Exception as e:
        logger.error(f"文本解析出错: {e}")
        raise HTTPException(status_code=500, detail=f"文本解析失败: {str(e)}")

@app.post("/api/v1/drug-interactions", summary="药物相互作用检查") 
async def check_drug_interactions(request: DrugInteractionCheck):
    """
    检查药物相互作用
    
    - **medications**: 药物列表
    - **severity_filter**: 严重程度过滤（all/major/moderate/minor）
    
    返回药物相互作用详情和建议
    """
    try:
        # 简化的药物相互作用检查
        interactions = []
        
        # 这里应该连接专业的药物数据库进行检查
        # 目前使用简化的规则
        common_interactions = {
            ("华法林", "阿司匹林"): {"severity": "major", "description": "增加出血风险"},
            ("甲巯咪唑", "华法林"): {"severity": "moderate", "description": "可能影响抗凝效果"}
        }
        
        for i, drug1 in enumerate(request.medications):
            for drug2 in request.medications[i+1:]:
                key = tuple(sorted([drug1, drug2]))
                if key in common_interactions:
                    interaction = common_interactions[key]
                    interactions.append({
                        "drug1": drug1,
                        "drug2": drug2,
                        "severity": interaction["severity"],
                        "description": interaction["description"],
                        "recommendation": "咨询临床药师或医生"
                    })
        
        return {
            "medications": request.medications,
            "interactions_found": len(interactions),
            "interactions": interactions,
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"药物相互作用检查出错: {e}")
        raise HTTPException(status_code=500, detail=f"药物检查失败: {str(e)}")

@app.post("/api/v1/rheumatic/assess", summary="风湿免疫疾病风险评估")
async def assess_rheumatic_disease_risk(
    patient: PatientProfile = Body(..., description="患者信息"),
    symptoms: List[str] = Body(..., description="症状列表"),
    lab_results: List[LabResult] = Body([], description="实验室检查结果"),
    family_history: List[str] = Body([], description="家族史"),
    hla_typing: Optional[str] = Body(None, description="HLA分型结果")
):
    """
    风湿免疫疾病与内分泌疾病关联性风险评估
    
    专门针对自身免疫性内分泌疾病和系统性风湿病的综合评估：
    - **多腺体自身免疫综合征**风险评估
    - **内分泌-风湿共病**模式识别
    - **遗传易感性**分析（HLA关联）
    - **家族聚集性**评估
    - **疾病进展预测**和筛查建议
    
    返回详细的风险分层和管理建议
    """
    try:
        # 风湿免疫疾病风险计算
        risk_scores = {}
        
        # 症状评分
        rheumatic_symptom_scores = diagnostic_service._analyze_rheumatic_symptoms(symptoms)
        
        # 实验室检查评分  
        rheumatic_lab_scores = diagnostic_service._analyze_rheumatic_labs(lab_results)
        
        # 家族史评分
        family_risk_score = 0.0
        high_risk_family_conditions = [
            "1型糖尿病", "甲状腺疾病", "类风湿关节炎", "系统性红斑狼疮", 
            "干燥综合征", "多腺体综合征", "自身免疫疾病"
        ]
        for condition in family_history:
            if any(risk_condition in condition for risk_condition in high_risk_family_conditions):
                family_risk_score += 0.2
        
        # HLA分型风险评估
        hla_risk_score = 0.0
        genetic_risks = {}
        if hla_typing:
            hla_lower = hla_typing.lower()
            if "dr3" in hla_lower or "dr4" in hla_lower:
                hla_risk_score += 0.3
                genetic_risks["1型糖尿病"] = "高风险（DR3/DR4阳性）"
                genetic_risks["多腺体自身免疫综合征II型"] = "高风险（DR3/DR4阳性）"
            if "dq2" in hla_lower or "dq8" in hla_lower:
                genetic_risks["自身免疫性甲状腺炎"] = "中等风险（DQ2/DQ8阳性）"
        
        # 综合风险评估
        for disease in set(rheumatic_symptom_scores.keys()) | set(rheumatic_lab_scores.keys()):
            symptom_score = rheumatic_symptom_scores.get(disease, 0.0)
            lab_score = rheumatic_lab_scores.get(disease, 0.0)
            
            # 综合评分权重：症状40%，实验室40%，家族史10%，遗传10%
            total_score = (symptom_score * 0.4 + lab_score * 0.4 + 
                          family_risk_score * 0.1 + hla_risk_score * 0.1)
            
            if total_score > 0.3:  # 只报告有意义的风险
                risk_scores[disease] = min(total_score, 1.0)  # 限制最高分为1.0
        
        # 风险分层
        high_risk = {k: v for k, v in risk_scores.items() if v >= 0.7}
        moderate_risk = {k: v for k, v in risk_scores.items() if 0.4 <= v < 0.7}
        low_risk = {k: v for k, v in risk_scores.items() if 0.3 <= v < 0.4}
        
        # 多腺体综合征特殊评估
        aps_risk_assessment = {}
        endocrine_diseases = ["1型糖尿病", "桥本甲状腺炎", "Addison病", "甲状旁腺功能减退"]
        positive_endocrine = [disease for disease in endocrine_diseases if disease in risk_scores]
        
        if len(positive_endocrine) >= 2:
            if patient.age < 20:
                aps_risk_assessment["APS-1风险"] = "高度怀疑（多腺体受累+年轻发病）"
            else:
                aps_risk_assessment["APS-2风险"] = "高度怀疑（多腺体受累+成年发病）"
        elif len(positive_endocrine) == 1:
            aps_risk_assessment["多腺体综合征风险"] = "需要长期监测（单腺体受累）"
        
        # 筛查建议
        screening_recommendations = []
        if high_risk or moderate_risk:
            screening_recommendations.extend([
                "建议完善自身抗体谱检查",
                "定期监测相关激素水平",
                "HLA分型检测（如未完成）",
                "一级亲属筛查"
            ])
            
            if "系统性红斑狼疮" in high_risk:
                screening_recommendations.extend([
                    "补体C3/C4检测",
                    "24小时尿蛋白",
                    "眼底检查"
                ])
                
            if any("关节炎" in disease for disease in high_risk.keys()):
                screening_recommendations.append("关节X线检查")
        
        # 管理建议
        management_recommendations = []
        if high_risk:
            management_recommendations.extend([
                "建议风湿免疫科和内分泌科联合会诊",
                "制定个体化监测计划",
                "患者和家属疾病教育",
                "定期随访评估疾病进展"
            ])
        
        return {
            "patient_id": patient.patient_id,
            "assessment_date": datetime.now().isoformat(),
            "risk_stratification": {
                "high_risk": high_risk,
                "moderate_risk": moderate_risk, 
                "low_risk": low_risk
            },
            "genetic_risk_factors": genetic_risks,
            "aps_assessment": aps_risk_assessment,
            "family_risk_score": family_risk_score,
            "screening_recommendations": screening_recommendations,
            "management_recommendations": management_recommendations,
            "follow_up_interval": "3-6个月" if high_risk else "6-12个月" if moderate_risk else "年度体检",
            "specialist_referral": "风湿免疫科+内分泌科" if high_risk else "内分泌科" if moderate_risk else "不需要"
        }
        
    except Exception as e:
        logger.error(f"风湿免疫疾病风险评估出错: {e}")
        raise HTTPException(status_code=500, detail=f"风险评估失败: {str(e)}")

@app.post("/api/v1/research/cohort", summary="研究队列识别")
async def identify_research_cohort(request: ResearchQuery):
    """
    基于知识图谱支持临床研究队列识别
    
    - **research_question**: 研究问题
    - **inclusion_criteria**: 纳入标准
    - **exclusion_criteria**: 排除标准
    - **outcome_measures**: 结局指标
    
    返回符合条件的患者队列信息和统计分析建议
    """
    try:
        # 简化的队列识别逻辑
        result = {
            "research_question": request.research_question,
            "criteria": {
                "inclusion": request.inclusion_criteria,
                "exclusion": request.exclusion_criteria
            },
            "estimated_cohort_size": 150,  # 模拟数据
            "statistical_recommendations": [
                "建议样本量至少100例",
                "考虑分层分析（年龄、性别）",
                "主要终点采用意向治疗分析",
                "次要终点采用符合方案分析"
            ],
            "suggested_variables": [
                "基线人口学特征",
                "疾病严重程度评分", 
                "合并症情况",
                "治疗依从性"
            ],
            "analyzed_at": datetime.now().isoformat()
        }
        
        logger.info(f"队列识别完成 - 研究问题: {request.research_question}")
        return result
        
    except Exception as e:
        logger.error(f"队列识别出错: {e}")
        raise HTTPException(status_code=500, detail=f"队列识别失败: {str(e)}")

@app.get("/api/v1/diseases", summary="获取疾病列表")
async def get_diseases(
    category: Optional[str] = Query(None, description="疾病分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制")
):
    """
    获取知识图谱中的疾病列表
    
    - **category**: 疾病分类过滤
    - **search**: 关键词搜索 
    - **limit**: 返回结果数量限制
    
    返回疾病基本信息列表
    """
    try:
        # 从知识图谱查询疾病
        with kg_service.neo4j_driver.session() as session:
            query = """
            MATCH (d:Disease)
            WHERE ($category IS NULL OR d.category = $category)
            AND ($search IS NULL OR d.name CONTAINS $search)
            RETURN d
            LIMIT $limit
            """
            result = session.run(query, category=category, search=search, limit=limit)
            
            diseases = []
            for record in result:
                disease = dict(record["d"])
                diseases.append({
                    "id": disease.get("id"),
                    "name": disease.get("name"),
                    "name_en": disease.get("name_en"),
                    "category": disease.get("category"),
                    "icd10": disease.get("icd10_code"),
                    "prevalence": disease.get("prevalence")
                })
        
        return {
            "diseases": diseases,
            "total_count": len(diseases),
            "filters": {
                "category": category,
                "search": search
            }
        }
        
    except Exception as e:
        logger.error(f"获取疾病列表出错: {e}")
        raise HTTPException(status_code=500, detail=f"获取疾病列表失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "endocrine_knowledge_graph_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )