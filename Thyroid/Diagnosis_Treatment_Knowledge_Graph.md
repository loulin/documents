# 甲状腺疾病诊断-治疗关联知识图谱构建

## 1. 核心数据模型设计

### 1.1 图谱架构概览

```
甲状腺诊断-治疗知识图谱
├── 疾病本体层 (Disease Ontology Layer)
├── 症状表现层 (Symptom Manifestation Layer)  
├── 诊断决策层 (Diagnostic Decision Layer)
├── 治疗策略层 (Treatment Strategy Layer)
├── 监测评估层 (Monitoring Assessment Layer)
└── 证据支撑层 (Evidence Support Layer)
```

### 1.2 核心实体类型 (Node Types)

#### 疾病实体 (Disease Entities)
```cypher
// 疾病节点结构
CREATE (d:Disease {
    id: "thyroid_disease_001",
    name: "甲状腺功能亢进症",
    icd_code: "E05",
    category: "内分泌代谢疾病",
    severity_levels: ["轻度", "中度", "重度"],
    prevalence: 0.012,
    age_distribution: "20-40岁高发",
    gender_ratio: "女性:男性 = 8:1",
    description: "由多种原因引起的甲状腺激素分泌过多所致的一组常见内分泌疾病"
})
```

#### 症状实体 (Symptom Entities)
```cypher
// 症状节点结构
CREATE (s:Symptom {
    id: "symptom_001",
    name: "心悸",
    category: "心血管症状",
    severity_scale: [1, 2, 3, 4, 5],
    frequency: "间断性/持续性",
    objective_measurable: true,
    measurement_method: "心率监测",
    differential_weight: 0.7
})
```

#### 检查指标实体 (Laboratory Test Entities)
```cypher
// 实验室检查节点
CREATE (l:LabTest {
    id: "lab_tsh_001",
    name: "促甲状腺激素(TSH)",
    normal_range: "0.27-4.2 mIU/L",
    critical_values: {
        low: "<0.1 mIU/L",
        high: ">10 mIU/L"
    },
    sensitivity: 0.95,
    specificity: 0.85,
    cost: 25.0,
    turnaround_time: "2-4小时"
})
```

#### 治疗方案实体 (Treatment Entities)
```cypher
// 治疗方案节点
CREATE (t:Treatment {
    id: "treatment_001",
    name: "抗甲状腺药物治疗",
    type: "药物治疗",
    first_line: true,
    contraindications: ["严重肝功能不全", "白细胞减少"],
    success_rate: 0.75,
    duration: "18-24个月",
    monitoring_requirements: ["肝功能", "血常规", "甲功"]
})
```

#### 药物实体 (Medication Entities)
```cypher
// 药物节点
CREATE (m:Medication {
    id: "med_mmi_001",
    name: "甲巯咪唑",
    generic_name: "Methimazole",
    drug_class: "硫脲类抗甲状腺药物",
    dosage_forms: ["片剂", "注射剂"],
    standard_dose: "5-10mg tid",
    max_dose: "60mg/day",
    half_life: "4-6小时",
    side_effects: ["皮疹", "肝功异常", "白细胞减少"],
    pregnancy_category: "D",
    cost_per_dose: 0.5
})
```

### 1.3 关系类型定义 (Relationship Types)

#### 诊断关联关系
```cypher
// 症状-疾病关联
(:Symptom)-[:INDICATES {
    probability: 0.8,
    specificity: "moderate",
    timing: "early/late",
    severity_correlation: 0.6
}]->(:Disease)

// 检查-疾病关联  
(:LabTest)-[:DIAGNOSES {
    sensitivity: 0.95,
    specificity: 0.85,
    positive_predictive_value: 0.75,
    negative_predictive_value: 0.98,
    threshold_values: {
        abnormal_low: "<0.1",
        abnormal_high: ">10"
    }
}]->(:Disease)
```

#### 治疗决策关系
```cypher
// 疾病-治疗关联
(:Disease)-[:TREATED_BY {
    effectiveness: 0.85,
    treatment_line: "first/second/third",
    evidence_level: "A/B/C",
    contraindications: [],
    special_populations: ["pregnancy", "elderly"],
    cost_effectiveness: 0.9
}]->(:Treatment)

// 治疗-药物关联
(:Treatment)-[:INCLUDES {
    dosage: "5-10mg tid",
    duration: "18-24个月",
    adjustment_factors: ["age", "weight", "severity"],
    monitoring_schedule: "weekly/monthly"
}]->(:Medication)
```

#### 监测评估关系
```cypher
// 治疗-监测关联
(:Treatment)-[:REQUIRES_MONITORING {
    frequency: "每4-6周",
    parameters: ["TSH", "FT4", "肝功能"],
    alert_thresholds: {},
    adjustment_criteria: "TSH正常化"
}]->(:LabTest)

// 疾病进展关系
(:Disease)-[:PROGRESSES_TO {
    probability: 0.15,
    timeframe: "6-12个月",
    risk_factors: ["未治疗", "治疗依从性差"],
    prevention_strategy: "规律随访"
}]->(:Disease)
```

### 1.4 属性权重系统

#### 诊断置信度计算
```python
class DiagnosticConfidence:
    def __init__(self):
        self.symptom_weights = {
            "心悸": 0.7,
            "体重下降": 0.8,
            "怕热多汗": 0.6,
            "眼征": 0.9,
            "甲状腺肿大": 0.8
        }
        
        self.lab_weights = {
            "TSH": 0.95,
            "FT4": 0.9,
            "FT3": 0.85,
            "TRAb": 0.95
        }
    
    def calculate_confidence(self, symptoms, lab_results):
        """计算诊断置信度"""
        symptom_score = sum(
            self.symptom_weights.get(s, 0.5) 
            for s in symptoms
        ) / len(symptoms) if symptoms else 0
        
        lab_score = sum(
            self.lab_weights.get(l, 0.5) 
            for l in lab_results
        ) / len(lab_results) if lab_results else 0
        
        # 综合置信度 (实验室检查权重更高)
        total_confidence = (symptom_score * 0.3 + lab_score * 0.7)
        return min(total_confidence, 1.0)
```

## 2. 甲状腺疾病本体构建

### 2.1 疾病分类体系

#### 主要疾病类别
```cypher
// 创建疾病分类树
CREATE (thyroid:DiseaseCategory {name: "甲状腺疾病", level: 0})
CREATE (hyper:DiseaseCategory {name: "甲状腺功能亢进", level: 1})
CREATE (hypo:DiseaseCategory {name: "甲状腺功能减退", level: 1})
CREATE (nodular:DiseaseCategory {name: "甲状腺结节疾病", level: 1})
CREATE (cancer:DiseaseCategory {name: "甲状腺癌", level: 1})

// 建立层级关系
CREATE (thyroid)-[:CONTAINS]->(hyper)
CREATE (thyroid)-[:CONTAINS]->(hypo)
CREATE (thyroid)-[:CONTAINS]->(nodular)
CREATE (thyroid)-[:CONTAINS]->(cancer)

// 甲亢具体疾病
CREATE (graves:Disease {
    name: "Graves病",
    icd_code: "E05.0",
    prevalence: 0.008,
    autoimmune: true,
    genetic_factors: ["HLA-DR3", "CTLA-4"],
    environmental_triggers: ["碘摄入", "应激", "感染"]
})

CREATE (toxic_nodular:Disease {
    name: "毒性结节性甲状腺肿",
    icd_code: "E05.1",
    prevalence: 0.002,
    age_group: "中老年",
    autonomy: true
})

// 建立疾病归属关系
CREATE (hyper)-[:INCLUDES]->(graves)
CREATE (hyper)-[:INCLUDES]->(toxic_nodular)
```

#### 疾病严重程度分级
```cypher
// 甲亢严重程度
CREATE (graves)-[:HAS_SEVERITY {
    level: "轻度",
    criteria: "轻微症状，TSH轻度抑制",
    tsh_range: "0.1-0.4 mIU/L",
    treatment_urgency: "非紧急"
}]->(mild_hyper:Severity)

CREATE (graves)-[:HAS_SEVERITY {
    level: "中度", 
    criteria: "明显症状，TSH明显抑制",
    tsh_range: "0.01-0.1 mIU/L",
    treatment_urgency: "及时治疗"
}]->(moderate_hyper:Severity)

CREATE (graves)-[:HAS_SEVERITY {
    level: "重度",
    criteria: "严重症状，TSH完全抑制",
    tsh_range: "<0.01 mIU/L",
    treatment_urgency: "紧急治疗",
    complications_risk: "高"
}]->(severe_hyper:Severity)
```

### 2.2 病因学图谱

```cypher
// 病因分类
CREATE (autoimmune:Etiology {
    type: "自身免疫性",
    mechanism: "抗体介导",
    examples: ["Graves病", "桥本甲状腺炎"]
})

CREATE (toxic:Etiology {
    type: "毒性",
    mechanism: "甲状腺自主功能",
    examples: ["毒性腺瘤", "毒性多结节性甲状腺肿"]
})

CREATE (iatrogenic:Etiology {
    type: "医源性",
    mechanism: "外源性甲状腺激素",
    examples: ["碘过量", "甲状腺激素过量"]
})

// 病因-疾病关联
CREATE (autoimmune)-[:CAUSES {
    frequency: 0.8,
    pathophysiology: "TRAb刺激TSH受体"
}]->(graves)

CREATE (toxic)-[:CAUSES {
    frequency: 0.15,
    pathophysiology: "甲状腺结节自主分泌"
}]->(toxic_nodular)
```

## 3. 症状-诊断关联图谱

### 3.1 症状聚类分析

#### 症状类别定义
```cypher
// 创建症状分类
CREATE (cardio:SymptomCategory {
    name: "心血管系统症状",
    pathophysiology: "甲状腺激素增多导致心肌兴奋性增高"
})

CREATE (metabolic:SymptomCategory {
    name: "代谢系统症状", 
    pathophysiology: "基础代谢率增高"
})

CREATE (neuropsychiatric:SymptomCategory {
    name: "神经精神症状",
    pathophysiology: "神经系统兴奋性增高"
})

CREATE (ocular:SymptomCategory {
    name: "眼部症状",
    pathophysiology: "眼外肌和眼眶组织自身免疫反应"
})

// 具体症状节点
CREATE (palpitation:Symptom {
    name: "心悸",
    frequency_in_hyperthyroid: 0.85,
    severity_correlation: 0.7,
    measurement: "心率>100次/分",
    differential_value: 0.6
})

CREATE (weight_loss:Symptom {
    name: "体重下降",
    frequency_in_hyperthyroid: 0.90,
    severity_correlation: 0.8,
    measurement: "3个月内体重下降>10%",
    differential_value: 0.8
})

CREATE (heat_intolerance:Symptom {
    name: "怕热多汗",
    frequency_in_hyperthyroid: 0.80,
    severity_correlation: 0.7,
    measurement: "主观评分+出汗量",
    differential_value: 0.7
})

// 症状归属关系
CREATE (cardio)-[:INCLUDES]->(palpitation)
CREATE (metabolic)-[:INCLUDES]->(weight_loss)
CREATE (metabolic)-[:INCLUDES]->(heat_intolerance)
```

### 3.2 症状组合模式

```cypher
// 定义症状组合模式
CREATE (classic_hyper:SymptomPattern {
    name: "典型甲亢症状组合",
    components: ["心悸", "体重下降", "怕热多汗", "手颤"],
    sensitivity: 0.85,
    specificity: 0.75,
    positive_predictive_value: 0.80
})

CREATE (graves_specific:SymptomPattern {
    name: "Graves病特异性症状",
    components: ["甲状腺肿大", "突眼", "胫前黏液性水肿"],
    sensitivity: 0.70,
    specificity: 0.95,
    positive_predictive_value: 0.90
})

// 症状模式-疾病关联
CREATE (classic_hyper)-[:SUGGESTS {
    probability: 0.80,
    confidence_level: "高",
    next_step: "甲功检查"
}]->(graves)

CREATE (graves_specific)-[:STRONGLY_SUGGESTS {
    probability: 0.90,
    confidence_level: "很高", 
    next_step: "TRAb检查"
}]->(graves)
```

### 3.3 症状评分系统

```python
class ThyroidSymptomScoring:
    def __init__(self):
        self.symptom_scores = {
            # 心血管症状
            "心悸": {"weight": 2, "max_score": 3},
            "心律不齐": {"weight": 3, "max_score": 3},
            
            # 代谢症状  
            "体重下降": {"weight": 3, "max_score": 3},
            "食欲亢进": {"weight": 2, "max_score": 3},
            "怕热多汗": {"weight": 2, "max_score": 3},
            
            # 神经精神症状
            "手颤": {"weight": 2, "max_score": 3},
            "易激动": {"weight": 1, "max_score": 3},
            "失眠": {"weight": 1, "max_score": 3},
            
            # Graves病特异性
            "突眼": {"weight": 4, "max_score": 3},
            "甲状腺肿大": {"weight": 3, "max_score": 3},
            "胫前水肿": {"weight": 4, "max_score": 3}
        }
    
    def calculate_symptom_score(self, patient_symptoms):
        """计算症状总分"""
        total_score = 0
        max_possible = 0
        
        for symptom, severity in patient_symptoms.items():
            if symptom in self.symptom_scores:
                weight = self.symptom_scores[symptom]["weight"]
                max_severity = self.symptom_scores[symptom]["max_score"]
                total_score += weight * min(severity, max_severity)
                max_possible += weight * max_severity
        
        return {
            "total_score": total_score,
            "max_possible": max_possible,
            "percentage": total_score / max_possible if max_possible > 0 else 0,
            "risk_level": self._assess_risk(total_score / max_possible if max_possible > 0 else 0)
        }
    
    def _assess_risk(self, percentage):
        """根据症状评分评估风险等级"""
        if percentage >= 0.7:
            return "高风险"
        elif percentage >= 0.4:
            return "中等风险"
        elif percentage >= 0.2:
            return "低风险"
        else:
            return "极低风险"
```

### 3.4 鉴别诊断决策树

```cypher
// 创建鉴别诊断决策节点
CREATE (initial_screen:DecisionNode {
    name: "初步筛查",
    question: "是否存在甲亢症状?",
    criteria: "心悸+体重下降+怕热"
})

CREATE (thyroid_exam:DecisionNode {
    name: "甲状腺检查",
    question: "甲状腺是否肿大?",
    examination: "触诊+超声"
})

CREATE (eye_exam:DecisionNode {
    name: "眼部检查", 
    question: "是否存在眼征?",
    examination: "眼球突出度+眼睑征"
})

CREATE (lab_tsh:DecisionNode {
    name: "TSH检测",
    question: "TSH是否抑制?",
    normal_range: "0.27-4.2 mIU/L"
})

// 决策路径
CREATE (initial_screen)-[:IF_POSITIVE]->(thyroid_exam)
CREATE (thyroid_exam)-[:IF_ENLARGED]->(eye_exam)
CREATE (eye_exam)-[:REGARDLESS]->(lab_tsh)

// 诊断结论节点
CREATE (graves_diagnosis:Diagnosis {
    name: "Graves病",
    criteria: "甲亢症状+弥漫性甲状腺肿+眼征+TSH抑制",
    confidence: 0.9,
    next_step: "TRAb检测确认"
})

CREATE (toxic_nodular_diagnosis:Diagnosis {
    name: "毒性结节性甲状腺肿",
    criteria: "甲亢症状+结节性肿大+无眼征+TSH抑制",
    confidence: 0.85,
    next_step: "甲状腺扫描"
})

// 决策到诊断的关联
CREATE (lab_tsh)-[:IF_SUPPRESSED_WITH_DIFFUSE_GOITER_AND_EYE_SIGNS]->(graves_diagnosis)
CREATE (lab_tsh)-[:IF_SUPPRESSED_WITH_NODULAR_GOITER_NO_EYE_SIGNS]->(toxic_nodular_diagnosis)
```

## 4. 诊断-治疗决策路径

### 4.1 治疗选择决策树

```cypher
// 治疗决策节点
CREATE (treatment_decision:TreatmentDecision {
    name: "治疗方案选择",
    factors: ["年龄", "疾病严重程度", "甲状腺大小", "患者偏好", "合并症"]
})

CREATE (age_assessment:DecisionNode {
    name: "年龄评估",
    question: "患者年龄分组",
    categories: ["<18岁", "18-65岁", ">65岁"]
})

CREATE (severity_assessment:DecisionNode {
    name: "严重程度评估", 
    question: "甲亢严重程度",
    criteria: ["TSH水平", "症状严重程度", "并发症"]
})

CREATE (goiter_size:DecisionNode {
    name: "甲状腺大小评估",
    question: "甲状腺肿大程度",
    grading: ["I度", "II度", "III度"]
})

// 治疗方案节点
CREATE (ati_treatment:Treatment {
    name: "抗甲状腺药物治疗",
    indication: "首选治疗",
    duration: "18-24个月",
    success_rate: 0.75,
    recurrence_rate: 0.25
})

CREATE (rai_treatment:Treatment {
    name: "放射性碘治疗", 
    indication: "药物治疗失败或复发",
    contraindications: ["妊娠", "哺乳", "甲状腺癌"],
    success_rate: 0.90,
    hypothyroidism_risk: 0.80
})

CREATE (surgery_treatment:Treatment {
    name: "甲状腺手术",
    indication: "大甲状腺肿或恶性可能",
    complications: ["喉返神经损伤", "甲状旁腺损伤"],
    success_rate: 0.95
})

// 决策路径建立
CREATE (treatment_decision)-[:ASSESS]->(age_assessment)
CREATE (treatment_decision)-[:ASSESS]->(severity_assessment) 
CREATE (treatment_decision)-[:ASSESS]->(goiter_size)

// 年龄相关的治疗推荐
CREATE (age_assessment)-[:IF_YOUNG_ADULT {
    age_range: "18-45岁",
    recommendation: "首选ATI治疗"
}]->(ati_treatment)

CREATE (age_assessment)-[:IF_MIDDLE_AGED {
    age_range: "45-65岁", 
    recommendation: "ATI或RAI治疗"
}]->(rai_treatment)

CREATE (age_assessment)-[:IF_ELDERLY {
    age_range: ">65岁",
    recommendation: "RAI治疗或低剂量ATI"
}]->(rai_treatment)
```

### 4.2 个性化治疗算法

```python
class PersonalizedTreatmentSelector:
    def __init__(self):
        self.treatment_algorithms = {
            "graves_disease": self._graves_treatment_algorithm,
            "toxic_nodular": self._toxic_nodular_algorithm,
            "subclinical_hyper": self._subclinical_algorithm
        }
        
        self.contraindications = {
            "ati": ["严重肝病", "白细胞<3000"],
            "rai": ["妊娠", "哺乳", "活动性眼病"],
            "surgery": ["严重心肺疾病", "凝血功能异常"]
        }
    
    def select_treatment(self, patient_profile):
        """根据患者特征选择最佳治疗方案"""
        diagnosis = patient_profile["diagnosis"]
        age = patient_profile["age"]
        severity = patient_profile["severity"]
        comorbidities = patient_profile.get("comorbidities", [])
        preferences = patient_profile.get("preferences", {})
        
        # 获取相应的治疗算法
        algorithm = self.treatment_algorithms.get(diagnosis)
        if not algorithm:
            return {"error": "未知诊断类型"}
        
        # 执行治疗选择算法
        recommendations = algorithm(patient_profile)
        
        # 检查禁忌症
        filtered_recommendations = self._filter_contraindications(
            recommendations, comorbidities
        )
        
        # 考虑患者偏好
        final_recommendations = self._apply_preferences(
            filtered_recommendations, preferences
        )
        
        return final_recommendations
    
    def _graves_treatment_algorithm(self, patient):
        """Graves病治疗算法"""
        age = patient["age"]
        severity = patient["severity"]
        goiter_size = patient.get("goiter_size", "small")
        eye_disease = patient.get("eye_disease", False)
        
        recommendations = []
        
        # 首选抗甲状腺药物
        if age < 50 and severity in ["mild", "moderate"]:
            recommendations.append({
                "treatment": "抗甲状腺药物",
                "priority": 1,
                "drug": "甲巯咪唑",
                "dose": "5-10mg tid",
                "duration": "18-24个月",
                "monitoring": "4-6周复查甲功",
                "success_probability": 0.75
            })
        
        # 放射性碘治疗
        if age > 40 and not eye_disease:
            recommendations.append({
                "treatment": "放射性碘",
                "priority": 2,
                "dose": "10-15 mCi",
                "contraindications": ["妊娠", "哺乳"],
                "success_probability": 0.90,
                "hypothyroidism_risk": 0.80
            })
        
        # 手术治疗
        if goiter_size == "large" or patient.get("malignancy_risk", False):
            recommendations.append({
                "treatment": "甲状腺手术",
                "priority": 3,
                "type": "甲状腺次全切除",
                "complications_risk": 0.05,
                "success_probability": 0.95
            })
        
        return recommendations
    
    def _filter_contraindications(self, recommendations, comorbidities):
        """过滤有禁忌症的治疗方案"""
        filtered = []
        
        for rec in recommendations:
            treatment_type = rec["treatment"]
            contraindicated = False
            
            # 检查禁忌症
            for contra in self.contraindications.get(treatment_type, []):
                if contra in comorbidities:
                    contraindicated = True
                    rec["contraindication_reason"] = contra
                    break
            
            if not contraindicated:
                filtered.append(rec)
        
        return filtered
    
    def _apply_preferences(self, recommendations, preferences):
        """应用患者偏好调整推荐"""
        if not preferences:
            return recommendations
        
        # 根据偏好调整优先级
        preference_weights = {
            "drug_treatment": {"抗甲状腺药物": 1.5},
            "avoid_radiation": {"放射性碘": 0.5},
            "avoid_surgery": {"甲状腺手术": 0.5}
        }
        
        for pref, weight_map in preference_weights.items():
            if preferences.get(pref):
                for rec in recommendations:
                    if rec["treatment"] in weight_map:
                        rec["preference_adjusted_priority"] = (
                            rec["priority"] * weight_map[rec["treatment"]]
                        )
        
        # 重新排序
        recommendations.sort(
            key=lambda x: x.get("preference_adjusted_priority", x["priority"])
        )
        
        return recommendations
```

### 4.3 治疗监测路径

```cypher
// 创建监测时间线
CREATE (baseline:MonitoringTimepoint {
    name: "基线评估",
    timing: "治疗前",
    required_tests: ["TSH", "FT4", "FT3", "肝功能", "血常规"],
    clinical_assessment: ["症状评分", "体重", "心率", "血压"]
})

CREATE (week2:MonitoringTimepoint {
    name: "治疗2周",
    timing: "治疗后2周",
    required_tests: ["肝功能", "血常规"],
    clinical_assessment: ["症状改善", "不良反应"],
    action_required: "如有肝功异常需调整剂量"
})

CREATE (week6:MonitoringTimepoint {
    name: "治疗6周",
    timing: "治疗后6周", 
    required_tests: ["TSH", "FT4", "FT3"],
    clinical_assessment: ["症状缓解程度"],
    dose_adjustment: true
})

CREATE (month3:MonitoringTimepoint {
    name: "治疗3个月",
    timing: "治疗后3个月",
    required_tests: ["TSH", "FT4", "FT3", "TRAb"],
    clinical_assessment: ["完全缓解评估"],
    milestone: "甲功正常化"
})

// 监测路径关联
CREATE (baseline)-[:NEXT {interval: "2周"}]->(week2)
CREATE (week2)-[:NEXT {interval: "4周"}]->(week6)  
CREATE (week6)-[:NEXT {interval: "6周"}]->(month3)

// 异常处理路径
CREATE (abnormal_liver:Alert {
    condition: "肝功能异常",
    criteria: "ALT/AST > 2倍正常上限",
    action: "停药或减量",
    follow_up: "1周复查"
})

CREATE (week2)-[:IF_ABNORMAL]->(abnormal_liver)
```

## 5. 实现代码框架

### 5.1 Neo4j数据库连接和基础操作

```python
from neo4j import GraphDatabase
import json
from typing import Dict, List, Optional

class ThyroidKnowledgeGraph:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_disease_node(self, disease_data: Dict):
        """创建疾病节点"""
        with self.driver.session() as session:
            query = """
            CREATE (d:Disease {
                id: $id,
                name: $name,
                icd_code: $icd_code,
                category: $category,
                prevalence: $prevalence,
                description: $description
            })
            RETURN d
            """
            result = session.run(query, **disease_data)
            return result.single()
    
    def create_symptom_relationship(self, symptom_id: str, disease_id: str, 
                                  relationship_data: Dict):
        """创建症状-疾病关联"""
        with self.driver.session() as session:
            query = """
            MATCH (s:Symptom {id: $symptom_id})
            MATCH (d:Disease {id: $disease_id})
            CREATE (s)-[r:INDICATES {
                probability: $probability,
                specificity: $specificity,
                timing: $timing
            }]->(d)
            RETURN r
            """
            params = {
                "symptom_id": symptom_id,
                "disease_id": disease_id,
                **relationship_data
            }
            result = session.run(query, params)
            return result.single()
    
    def create_treatment_pathway(self, disease_id: str, treatment_id: str,
                               pathway_data: Dict):
        """创建治疗路径"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Disease {id: $disease_id})
            MATCH (t:Treatment {id: $treatment_id})
            CREATE (d)-[r:TREATED_BY {
                effectiveness: $effectiveness,
                treatment_line: $treatment_line,
                evidence_level: $evidence_level,
                contraindications: $contraindications
            }]->(t)
            RETURN r
            """
            params = {
                "disease_id": disease_id,
                "treatment_id": treatment_id,
                **pathway_data
            }
            result = session.run(query, params)
            return result.single()
```

## 6. 药物治疗知识图谱

### 6.1 抗甲状腺药物体系

```cypher
// 创建药物分类
CREATE (ati_drugs:DrugClass {
    name: "抗甲状腺药物",
    mechanism: "抑制甲状腺过氧化物酶",
    target_enzyme: "TPO"
})

CREATE (thiourea:DrugSubclass {
    name: "硫脲类",
    parent_class: "抗甲状腺药物",
    mechanism: "阻断碘的有机化和偶联"
})

CREATE (imidazole:DrugSubclass {
    name: "咪唑类", 
    parent_class: "抗甲状腺药物",
    mechanism: "阻断碘的有机化和偶联"
})

// 具体药物节点
CREATE (mmi:Medication {
    id: "mmi_001",
    name: "甲巯咪唑",
    generic_name: "Methimazole",
    brand_names: ["赛治", "他巴唑"],
    drug_class: "咪唑类",
    bioavailability: 0.93,
    half_life: "4-6小时",
    metabolism: "肝脏代谢",
    excretion: "肾脏排泄",
    pregnancy_category: "D",
    lactation_safety: "相对安全"
})

CREATE (ptu:Medication {
    id: "ptu_001", 
    name: "丙基硫氧嘧啶",
    generic_name: "Propylthiouracil",
    brand_names: ["丙嘧"],
    drug_class: "硫脲类",
    bioavailability: 0.75,
    half_life: "1-2小时",
    metabolism: "肝脏代谢", 
    excretion: "肾脏排泄",
    pregnancy_category: "D",
    lactation_safety: "首选"
})

// 药物归属关系
CREATE (thiourea)-[:INCLUDES]->(ptu)
CREATE (imidazole)-[:INCLUDES]->(mmi)
CREATE (ati_drugs)-[:CONTAINS]->(thiourea)
CREATE (ati_drugs)-[:CONTAINS]->(imidazole)
```

### 6.2 药物剂量和给药方案

```cypher
// 甲巯咪唑给药方案
CREATE (mmi_initial:DosageRegimen {
    medication: "甲巯咪唑",
    phase: "初始治疗",
    dose: "5-15mg",
    frequency: "每日2-3次",
    max_daily_dose: "60mg",
    duration: "4-8周",
    adjustment_criteria: "根据甲功结果"
})

CREATE (mmi_maintenance:DosageRegimen {
    medication: "甲巯咪唑", 
    phase: "维持治疗",
    dose: "2.5-10mg",
    frequency: "每日1-2次",
    duration: "12-18个月",
    monitoring: "每4-6周复查甲功"
})

// PTU给药方案  
CREATE (ptu_initial:DosageRegimen {
    medication: "丙基硫氧嘧啶",
    phase: "初始治疗",
    dose: "50-150mg",
    frequency: "每日3次",
    max_daily_dose: "600mg",
    duration: "4-8周"
})

// 特殊人群剂量调整
CREATE (pregnancy_dosing:SpecialPopulationDosing {
    population: "妊娠期",
    preferred_drug: "丙基硫氧嘧啶",
    dose_adjustment: "最小有效剂量",
    monitoring: "每4周甲功检查",
    target_ft4: "正常上限"
})

CREATE (elderly_dosing:SpecialPopulationDosing {
    population: "老年人",
    dose_adjustment: "起始剂量减半",
    monitoring: "更频繁监测心率",
    contraindications: ["严重心律失常"]
})

// 剂量-药物关联
CREATE (mmi)-[:HAS_REGIMEN]->(mmi_initial)
CREATE (mmi)-[:HAS_REGIMEN]->(mmi_maintenance)
CREATE (ptu)-[:HAS_REGIMEN]->(ptu_initial)
```

### 6.3 药物相互作用图谱

```python
class DrugInteractionChecker:
    def __init__(self):
        self.interactions = {
            "甲巯咪唑": {
                "华法林": {
                    "severity": "major",
                    "mechanism": "增强抗凝作用",
                    "clinical_effect": "出血风险增加",
                    "management": "监测INR，调整华法林剂量"
                },
                "地高辛": {
                    "severity": "moderate", 
                    "mechanism": "甲亢改善后地高辛清除率下降",
                    "clinical_effect": "地高辛中毒风险",
                    "management": "监测地高辛血药浓度"
                },
                "茶碱": {
                    "severity": "moderate",
                    "mechanism": "甲亢改善后茶碱清除率下降", 
                    "clinical_effect": "茶碱血浓度升高",
                    "management": "调整茶碱剂量"
                }
            },
            "丙基硫氧嘧啶": {
                "华法林": {
                    "severity": "major",
                    "mechanism": "增强抗凝作用", 
                    "clinical_effect": "出血风险显著增加",
                    "management": "密切监测INR"
                }
            }
        }
    
    def check_interactions(self, medications):
        """检查药物相互作用"""
        interactions_found = []
        
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                interaction = self._get_interaction(med1, med2)
                if interaction:
                    interactions_found.append({
                        "drug1": med1,
                        "drug2": med2,
                        **interaction
                    })
        
        return interactions_found
    
    def _get_interaction(self, drug1, drug2):
        """获取两个药物间的相互作用"""
        if drug1 in self.interactions:
            return self.interactions[drug1].get(drug2)
        elif drug2 in self.interactions:
            return self.interactions[drug2].get(drug1)
        return None
```

### 6.4 不良反应监测体系

```cypher
// 创建不良反应分类
CREATE (hepatotoxicity:AdverseEffect {
    name: "肝毒性",
    frequency: "1-5%", 
    severity: "严重",
    mechanism: "直接肝细胞损伤",
    monitoring: "肝功能检查",
    risk_factors: ["高剂量", "长期使用"],
    management: "立即停药"
})

CREATE (agranulocytosis:AdverseEffect {
    name: "粒细胞缺乏症",
    frequency: "0.1-0.5%",
    severity: "严重",
    mechanism: "骨髓抑制",
    monitoring: "血常规检查", 
    early_signs: ["发热", "咽痛", "感染"],
    management: "立即停药，抗生素治疗"
})

CREATE (skin_rash:AdverseEffect {
    name: "皮疹",
    frequency: "5-10%",
    severity: "轻-中度",
    mechanism: "过敏反应",
    types: ["荨麻疹", "斑丘疹"],
    management: "抗组胺药，严重时停药"
})

// 药物-不良反应关联
CREATE (mmi)-[:MAY_CAUSE {
    incidence: 0.03,
    dose_dependent: true,
    reversible: true
}]->(hepatotoxicity)

CREATE (mmi)-[:MAY_CAUSE {
    incidence: 0.002,
    dose_dependent: false,
    reversible: true
}]->(agranulocytosis)

CREATE (ptu)-[:MAY_CAUSE {
    incidence: 0.05,
    dose_dependent: true,
    reversible: true
}]->(hepatotoxicity)
```

## 7. 监测指标-调整策略图谱

### 7.1 实验室监测网络

```cypher
// 甲状腺功能监测指标
CREATE (tsh:LabParameter {
    name: "促甲状腺激素(TSH)",
    normal_range: "0.27-4.2 mIU/L",
    suppressed: "<0.1 mIU/L",
    elevated: ">10 mIU/L",
    half_life: "7天",
    response_time: "6-8周"
})

CREATE (ft4:LabParameter {
    name: "游离甲状腺素(FT4)",
    normal_range: "12-22 pmol/L",
    elevated: ">25 pmol/L", 
    suppressed: "<10 pmol/L",
    half_life: "7天",
    response_time: "2-3周"
})

CREATE (ft3:LabParameter {
    name: "游离三碘甲状腺原氨酸(FT3)",
    normal_range: "3.1-6.8 pmol/L",
    elevated: ">8.0 pmol/L",
    suppressed: "<3.0 pmol/L", 
    half_life: "1天",
    response_time: "1-2周"
})

// 安全性监测指标
CREATE (alt:LabParameter {
    name: "丙氨酸转氨酶(ALT)",
    normal_range: "7-40 U/L",
    mild_elevation: "40-80 U/L",
    moderate_elevation: "80-200 U/L",
    severe_elevation: ">200 U/L"
})

CREATE (wbc:LabParameter {
    name: "白细胞计数(WBC)",
    normal_range: "3.5-9.5 ×10^9/L",
    mild_low: "3.0-3.5 ×10^9/L", 
    moderate_low: "1.5-3.0 ×10^9/L",
    severe_low: "<1.5 ×10^9/L"
})

CREATE (anc:LabParameter {
    name: "中性粒细胞绝对计数(ANC)",
    normal_range: ">1.5 ×10^9/L",
    mild_low: "1.0-1.5 ×10^9/L",
    agranulocytosis: "<0.5 ×10^9/L"
})
```

### 7.2 监测时间表和频率

```cypher
// 治疗监测时间节点
CREATE (baseline_monitoring:MonitoringSchedule {
    timepoint: "基线(治疗前)",
    required_tests: ["TSH", "FT4", "FT3", "ALT", "AST", "WBC", "ANC"],
    optional_tests: ["TRAb", "TPOAb", "甲状腺超声"],
    clinical_assessment: ["症状评分", "体重", "心率", "血压"]
})

CREATE (week2_monitoring:MonitoringSchedule {
    timepoint: "治疗后2周",
    required_tests: ["ALT", "AST", "WBC", "ANC"],
    rationale: "早期发现肝毒性和血液学毒性",
    action_threshold: "ALT>2×ULN或WBC<3.0"
})

CREATE (week6_monitoring:MonitoringSchedule {
    timepoint: "治疗后6周", 
    required_tests: ["TSH", "FT4", "FT3"],
    optional_tests: ["ALT", "WBC"],
    dose_adjustment: true,
    target: "FT4降至正常范围"
})

CREATE (month3_monitoring:MonitoringSchedule {
    timepoint: "治疗后3个月",
    required_tests: ["TSH", "FT4", "FT3", "TRAb"],
    milestone: "甲功完全正常化",
    dose_adjustment: "减量至维持剂量"
})

// 长期随访监测
CREATE (longterm_monitoring:MonitoringSchedule {
    timepoint: "维持期",
    frequency: "每3-4个月",
    required_tests: ["TSH", "FT4"],
    duration: "治疗全程",
    stop_criteria: "TRAb转阴且停药后甲功稳定"
})
```

### 7.3 剂量调整算法

```python
class ThyroidDoseAdjustmentEngine:
    def __init__(self):
        self.adjustment_rules = {
            "methimazole": {
                "target_ft4": (12, 22),  # pmol/L
                "target_tsh": (0.27, 4.2),  # mIU/L
                "dose_steps": [2.5, 5, 7.5, 10, 15, 20, 30],
                "max_dose": 60
            },
            "propylthiouracil": {
                "target_ft4": (12, 22),
                "target_tsh": (0.27, 4.2), 
                "dose_steps": [50, 100, 150, 200, 300, 400],
                "max_dose": 600
            }
        }
    
    def adjust_dose(self, current_dose, current_ft4, current_tsh, 
                   drug_name, weeks_on_current_dose):
        """根据检查结果调整药物剂量"""
        drug_info = self.adjustment_rules.get(drug_name.lower())
        if not drug_info:
            return {"error": "未知药物"}
        
        target_ft4_min, target_ft4_max = drug_info["target_ft4"]
        target_tsh_min, target_tsh_max = drug_info["target_tsh"]
        dose_steps = drug_info["dose_steps"]
        
        # 剂量调整逻辑
        adjustment = self._calculate_adjustment(
            current_dose, current_ft4, current_tsh,
            target_ft4_min, target_ft4_max,
            target_tsh_min, target_tsh_max,
            dose_steps, weeks_on_current_dose
        )
        
        return adjustment
    
    def _calculate_adjustment(self, current_dose, ft4, tsh,
                            ft4_min, ft4_max, tsh_min, tsh_max,
                            dose_steps, weeks_on_dose):
        """计算具体的剂量调整"""
        
        # 如果时间不足，建议继续观察
        if weeks_on_dose < 4:
            return {
                "action": "continue_current_dose",
                "rationale": "药物作用时间不足4周",
                "next_check": "2-4周后复查"
            }
        
        # FT4仍然升高 - 增加剂量
        if ft4 > ft4_max:
            severity = "severe" if ft4 > ft4_max * 1.5 else "moderate"
            
            if severity == "severe":
                # 严重升高，大幅增加剂量
                increase = self._find_next_dose_step(current_dose, dose_steps, 2)
            else:
                # 中度升高，适度增加剂量  
                increase = self._find_next_dose_step(current_dose, dose_steps, 1)
            
            return {
                "action": "increase_dose",
                "new_dose": increase,
                "rationale": f"FT4 {ft4} pmol/L 仍高于正常({ft4_max})",
                "next_check": "4-6周后复查"
            }
        
        # FT4正常但TSH仍被抑制 - 继续当前剂量
        elif ft4_min <= ft4 <= ft4_max and tsh < tsh_min:
            return {
                "action": "continue_current_dose",
                "rationale": "FT4已正常，等待TSH恢复",
                "next_check": "6-8周后复查"
            }
        
        # FT4和TSH都正常 - 减量至维持剂量
        elif ft4_min <= ft4 <= ft4_max and tsh_min <= tsh <= tsh_max:
            maintenance_dose = self._calculate_maintenance_dose(current_dose)
            return {
                "action": "reduce_to_maintenance",
                "new_dose": maintenance_dose,
                "rationale": "甲功已正常，减至维持剂量",
                "next_check": "6-8周后复查"
            }
        
        # FT4偏低 - 减少剂量
        elif ft4 < ft4_min:
            decrease = self._find_previous_dose_step(current_dose, dose_steps, 1)
            return {
                "action": "decrease_dose", 
                "new_dose": decrease,
                "rationale": f"FT4 {ft4} pmol/L 低于正常({ft4_min})",
                "next_check": "4-6周后复查"
            }
        
        else:
            return {
                "action": "continue_current_dose",
                "rationale": "检查结果在目标范围内",
                "next_check": "8周后复查"
            }
    
    def _find_next_dose_step(self, current_dose, dose_steps, step_increment=1):
        """找到下一个剂量档位"""
        try:
            current_index = dose_steps.index(current_dose)
            new_index = min(current_index + step_increment, len(dose_steps) - 1)
            return dose_steps[new_index]
        except ValueError:
            # 当前剂量不在标准档位中，找最接近的更高档位
            for dose in dose_steps:
                if dose > current_dose:
                    return dose
            return dose_steps[-1]  # 返回最大剂量
    
    def _find_previous_dose_step(self, current_dose, dose_steps, step_decrement=1):
        """找到前一个剂量档位"""
        try:
            current_index = dose_steps.index(current_dose)
            new_index = max(current_index - step_decrement, 0)
            return dose_steps[new_index]
        except ValueError:
            # 当前剂量不在标准档位中，找最接近的更低档位
            for dose in reversed(dose_steps):
                if dose < current_dose:
                    return dose
            return dose_steps[0]  # 返回最小剂量
    
    def _calculate_maintenance_dose(self, current_dose):
        """计算维持剂量(通常为当前剂量的1/2-2/3)"""
        return round(current_dose * 0.6, 1)
```

### 7.4 预警和决策支持系统

```cypher
// 创建临床预警规则
CREATE (hepatotoxicity_alert:ClinicalAlert {
    name: "肝毒性预警",
    condition: "ALT/AST > 2×正常上限",
    severity: "高",
    action: "立即停药并肝病科会诊",
    follow_up: "每周监测肝功能"
})

CREATE (agranulocytosis_alert:ClinicalAlert {
    name: "粒细胞缺乏预警", 
    condition: "ANC < 1.0×10^9/L",
    severity: "紧急",
    action: "立即停药，血液科急诊会诊",
    isolation: "保护性隔离"
})

CREATE (hyperthyroid_crisis_alert:ClinicalAlert {
    name: "甲亢危象预警",
    condition: "高热+心率>140+意识障碍",
    severity: "危急", 
    action: "ICU监护，大剂量抗甲状腺药",
    additional_treatment: ["糖皮质激素", "β受体阻滞剂"]
})

// 预警触发条件
CREATE (lab_threshold:AlertTrigger {
    parameter: "ALT",
    threshold: "> 80 U/L",
    alert_type: "肝毒性预警",
    notification: ["主治医生", "药师", "患者"]
})

CREATE (symptom_threshold:AlertTrigger {
    parameter: "发热+咽痛",
    threshold: "体温>38.5°C + 咽痛",
    alert_type: "感染预警",
    urgent_check: "血常规+中性粒细胞计数"
})
```

## 8. 知识图谱查询和推理引擎

### 8.1 诊断推理查询

```python
class ThyroidDiagnosticReasoner:
    def __init__(self, kg_connection):
        self.kg = kg_connection
        
    def differential_diagnosis(self, patient_symptoms, lab_results):
        """执行鉴别诊断推理"""
        
        # 1. 基于症状查找候选疾病
        symptom_query = """
        MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
        WHERE s.name IN $symptoms
        RETURN d.name as disease, 
               collect(s.name) as matching_symptoms,
               avg(r.probability) as avg_probability,
               count(s) as symptom_count
        ORDER BY avg_probability DESC, symptom_count DESC
        """
        
        candidate_diseases = self.kg.run_query(symptom_query, 
                                             {"symptoms": patient_symptoms})
        
        # 2. 基于实验室检查精确诊断
        lab_query = """
        MATCH (l:LabTest)-[r:DIAGNOSES]->(d:Disease)
        WHERE l.name IN $lab_tests
        RETURN d.name as disease,
               l.name as lab_test,
               r.sensitivity as sensitivity,
               r.specificity as specificity
        """
        
        lab_diseases = self.kg.run_query(lab_query, 
                                       {"lab_tests": list(lab_results.keys())})
        
        # 3. 综合分析和评分
        final_diagnosis = self._integrate_evidence(
            candidate_diseases, lab_diseases, lab_results
        )
        
        return final_diagnosis
    
    def _integrate_evidence(self, symptom_evidence, lab_evidence, lab_values):
        """整合症状和实验室证据"""
        disease_scores = {}
        
        # 症状证据评分
        for record in symptom_evidence:
            disease = record["disease"]
            symptom_score = record["avg_probability"] * record["symptom_count"]
            disease_scores[disease] = {"symptom_score": symptom_score}
        
        # 实验室证据评分  
        for record in lab_evidence:
            disease = record["disease"]
            lab_test = record["lab_test"]
            sensitivity = record["sensitivity"]
            
            if disease not in disease_scores:
                disease_scores[disease] = {"symptom_score": 0}
            
            # 根据实际检查值计算实验室评分
            lab_score = self._calculate_lab_score(lab_test, lab_values.get(lab_test), sensitivity)
            disease_scores[disease]["lab_score"] = lab_score
        
        # 计算最终评分
        final_scores = []
        for disease, scores in disease_scores.items():
            symptom_score = scores.get("symptom_score", 0)
            lab_score = scores.get("lab_score", 0)
            
            # 加权总分 (实验室检查权重更高)
            total_score = symptom_score * 0.3 + lab_score * 0.7
            
            final_scores.append({
                "disease": disease,
                "total_score": total_score,
                "symptom_score": symptom_score,
                "lab_score": lab_score,
                "confidence": min(total_score, 1.0)
            })
        
        return sorted(final_scores, key=lambda x: x["total_score"], reverse=True)
    
    def get_treatment_recommendations(self, diagnosed_disease, patient_profile):
        """获取治疗建议"""
        treatment_query = """
        MATCH (d:Disease {name: $disease})-[r:TREATED_BY]->(t:Treatment)
        RETURN t.name as treatment,
               r.effectiveness as effectiveness,
               r.treatment_line as line,
               r.evidence_level as evidence,
               t.contraindications as contraindications
        ORDER BY r.treatment_line, r.effectiveness DESC
        """
        
        treatments = self.kg.run_query(treatment_query, {"disease": diagnosed_disease})
        
        # 过滤禁忌症
        suitable_treatments = self._filter_contraindications(treatments, patient_profile)
        
        return suitable_treatments
    
    def get_monitoring_plan(self, treatment_name, patient_risk_factors):
        """获取监测计划"""
        monitoring_query = """
        MATCH (t:Treatment {name: $treatment})-[r:REQUIRES_MONITORING]->(l:LabTest)
        RETURN l.name as test,
               r.frequency as frequency,
               r.alert_thresholds as thresholds
        """
        
        monitoring_tests = self.kg.run_query(monitoring_query, {"treatment": treatment_name})
        
        # 根据风险因素调整监测频率
        adjusted_plan = self._adjust_monitoring_frequency(monitoring_tests, patient_risk_factors)
        
        return adjusted_plan
```

### 8.2 治疗决策支持查询

```cypher
// 复杂治疗决策查询示例
// 查询适合妊娠期患者的治疗方案
MATCH (d:Disease {name: "Graves病"})-[r:TREATED_BY]->(t:Treatment)-[inc:INCLUDES]->(m:Medication)
WHERE NOT "妊娠期禁用" IN t.contraindications
AND m.pregnancy_category IN ["A", "B", "C"]
RETURN t.name as treatment,
       m.name as medication,
       m.pregnancy_category as safety_category,
       r.effectiveness as effectiveness
ORDER BY m.pregnancy_category, r.effectiveness DESC

// 查询老年患者的剂量调整建议
MATCH (m:Medication)-[r:HAS_SPECIAL_DOSING]->(sp:SpecialPopulation {population: "老年人"})
RETURN m.name as medication,
       sp.dose_adjustment as adjustment,
       sp.monitoring as special_monitoring,
       sp.contraindications as additional_contraindications

// 查询药物相互作用
MATCH (m1:Medication)-[r:INTERACTS_WITH]->(m2:Medication)
WHERE m1.name = "甲巯咪唑" AND m2.name IN ["华法林", "地高辛", "茶碱"]
RETURN m2.name as interacting_drug,
       r.severity as interaction_severity,
       r.mechanism as mechanism,
       r.management as management_strategy
```

### 8.3 实时决策支持API

```python
class RealTimeClinicalDecisionSupport:
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        self.reasoner = ThyroidDiagnosticReasoner(knowledge_graph)
        
    async def process_clinical_scenario(self, patient_data):
        """处理临床场景，提供实时决策支持"""
        
        scenario_type = self._identify_scenario_type(patient_data)
        
        if scenario_type == "initial_diagnosis":
            return await self._handle_initial_diagnosis(patient_data)
        elif scenario_type == "treatment_selection":
            return await self._handle_treatment_selection(patient_data)
        elif scenario_type == "monitoring_alert":
            return await self._handle_monitoring_alert(patient_data)
        elif scenario_type == "dose_adjustment":
            return await self._handle_dose_adjustment(patient_data)
        else:
            return {"error": "未识别的临床场景"}
    
    async def _handle_initial_diagnosis(self, patient_data):
        """处理初诊场景"""
        symptoms = patient_data.get("symptoms", [])
        lab_results = patient_data.get("lab_results", {})
        
        # 执行鉴别诊断
        diagnosis_results = self.reasoner.differential_diagnosis(symptoms, lab_results)
        
        # 获取推荐的进一步检查
        next_steps = self._recommend_additional_tests(diagnosis_results)
        
        return {
            "scenario": "初诊鉴别诊断",
            "differential_diagnosis": diagnosis_results,
            "recommended_tests": next_steps,
            "urgency_level": self._assess_urgency(diagnosis_results, symptoms)
        }
    
    async def _handle_treatment_selection(self, patient_data):
        """处理治疗选择场景"""
        diagnosis = patient_data.get("diagnosis")
        patient_profile = patient_data.get("patient_profile", {})
        
        # 获取治疗建议
        treatments = self.reasoner.get_treatment_recommendations(diagnosis, patient_profile)
        
        # 个性化治疗选择
        personalized_treatments = self._personalize_treatment_selection(treatments, patient_profile)
        
        return {
            "scenario": "治疗方案选择",
            "diagnosis": diagnosis,
            "recommended_treatments": personalized_treatments,
            "monitoring_plan": self.reasoner.get_monitoring_plan(
                personalized_treatments[0]["treatment"], 
                patient_profile.get("risk_factors", [])
            )
        }
    
    async def _handle_monitoring_alert(self, patient_data):
        """处理监测预警场景"""
        current_treatment = patient_data.get("current_treatment")
        lab_values = patient_data.get("lab_values", {})
        symptoms = patient_data.get("new_symptoms", [])
        
        # 检查是否触发预警
        alerts = self._check_clinical_alerts(lab_values, symptoms)
        
        # 生成处理建议
        management_recommendations = self._generate_alert_management(alerts, current_treatment)
        
        return {
            "scenario": "监测预警",
            "alerts": alerts,
            "recommendations": management_recommendations,
            "urgency": self._calculate_alert_urgency(alerts)
        }
    
    def _check_clinical_alerts(self, lab_values, symptoms):
        """检查临床预警"""
        alerts = []
        
        # 检查肝毒性
        alt = lab_values.get("ALT", 0)
        if alt > 80:  # 2倍正常上限
            severity = "严重" if alt > 200 else "中度"
            alerts.append({
                "type": "肝毒性预警",
                "severity": severity,
                "value": f"ALT: {alt} U/L",
                "action": "立即停药" if severity == "严重" else "减量并监测"
            })
        
        # 检查血液学毒性
        wbc = lab_values.get("WBC", 5)
        if wbc < 3.0:
            severity = "严重" if wbc < 1.5 else "中度"
            alerts.append({
                "type": "白细胞减少预警",
                "severity": severity,
                "value": f"WBC: {wbc} ×10^9/L",
                "action": "立即停药并血液科会诊" if severity == "严重" else "密切监测"
            })
        
        # 检查感染症状
        if "发热" in symptoms and "咽痛" in symptoms:
            alerts.append({
                "type": "感染预警",
                "severity": "高",
                "description": "发热+咽痛提示可能感染",
                "action": "立即查血常规，考虑粒细胞缺乏可能"
            })
        
        return alerts
    
    def _generate_alert_management(self, alerts, current_treatment):
        """生成预警处理建议"""
        recommendations = []
        
        for alert in alerts:
            if alert["type"] == "肝毒性预警":
                recommendations.append({
                    "immediate_action": "停用抗甲状腺药物",
                    "monitoring": "每周监测肝功能直至正常",
                    "alternative_treatment": "考虑放射性碘治疗或手术",
                    "follow_up": "肝病科会诊评估"
                })
            
            elif alert["type"] == "白细胞减少预警":
                recommendations.append({
                    "immediate_action": "停用抗甲状腺药物",
                    "monitoring": "每日血常规监测",
                    "supportive_care": "预防感染措施",
                    "specialist_referral": "血液科急诊会诊"
                })
            
            elif alert["type"] == "感染预警":
                recommendations.append({
                    "urgent_assessment": "立即查血常规+CRP+PCT",
                    "empirical_treatment": "如确诊感染，立即抗生素治疗",
                    "drug_safety": "评估是否为药物相关粒细胞缺乏",
                    "isolation": "必要时保护性隔离"
                })
        
        return recommendations
```

这个完整的甲状腺疾病诊断-治疗知识图谱构建方案提供了：

1. **核心数据模型** - 定义了疾病、症状、检查、治疗、药物等实体及其关系
2. **疾病本体系统** - 建立了完整的甲状腺疾病分类和病因学体系  
3. **症状-诊断关联** - 构建了症状模式识别和鉴别诊断决策树
4. **诊断-治疗路径** - 建立了个性化治疗选择和决策支持算法
5. **药物治疗图谱** - 涵盖了药物信息、剂量方案、相互作用和不良反应
6. **监测调整策略** - 实现了智能化的剂量调整和临床预警系统
7. **推理查询引擎** - 提供了实时的临床决策支持和智能推理能力

整个系统可以支持从初诊到长期随访的全程智能化甲状腺疾病管理。