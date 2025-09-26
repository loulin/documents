# 糖尿病前期风险评估系统实现方案

## 数据模型设计

### 患者基本信息表 (PatientBasicInfo)
```sql
CREATE TABLE PatientBasicInfo (
    patient_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    gender ENUM('M', 'F'),
    birth_date DATE,
    age INT,
    height DECIMAL(5,2), -- cm
    weight DECIMAL(5,2), -- kg
    bmi DECIMAL(4,2),
    waist_circumference DECIMAL(5,2), -- cm
    hip_circumference DECIMAL(5,2), -- cm
    waist_hip_ratio DECIMAL(4,3),
    ethnicity VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 生化指标表 (BiochemicalIndicators)
```sql
CREATE TABLE BiochemicalIndicators (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    test_date DATE,
    
    -- 血糖相关
    fpg DECIMAL(4,2), -- 空腹血糖 mmol/L
    hba1c DECIMAL(4,2), -- 糖化血红蛋白 %
    ogtt_2h DECIMAL(4,2), -- 餐后2小时血糖 mmol/L
    
    -- 胰岛素相关
    fasting_insulin DECIMAL(6,2), -- 空腹胰岛素 mU/L
    homa_ir DECIMAL(5,2), -- HOMA-IR指数
    c_peptide_fasting DECIMAL(4,2), -- 空腹C肽 ng/mL
    c_peptide_postprandial DECIMAL(4,2), -- 餐后C肽 ng/mL
    
    -- 血脂相关
    triglycerides DECIMAL(4,2), -- 甘油三酯 mmol/L
    hdl_cholesterol DECIMAL(4,2), -- 高密度脂蛋白胆固醇 mmol/L
    ldl_cholesterol DECIMAL(4,2), -- 低密度脂蛋白胆固醇 mmol/L
    total_cholesterol DECIMAL(4,2), -- 总胆固醇 mmol/L
    
    -- 其他指标
    uric_acid DECIMAL(4,1), -- 尿酸 μmol/L
    creatinine DECIMAL(5,1), -- 肌酐 μmol/L
    albumin DECIMAL(4,1), -- 白蛋白 g/L
    
    FOREIGN KEY (patient_id) REFERENCES PatientBasicInfo(patient_id)
);
```

### 血压指标表 (BloodPressure)
```sql
CREATE TABLE BloodPressure (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    measurement_date DATETIME,
    systolic_bp INT, -- 收缩压 mmHg
    diastolic_bp INT, -- 舒张压 mmHg
    heart_rate INT, -- 心率 bpm
    measurement_method ENUM('自测', '诊室', '动态监测'),
    FOREIGN KEY (patient_id) REFERENCES PatientBasicInfo(patient_id)
);
```

### 家族史表 (FamilyHistory)
```sql
CREATE TABLE FamilyHistory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    
    -- 糖尿病家族史
    dm_first_degree BOOLEAN DEFAULT FALSE, -- 一级亲属糖尿病史
    dm_second_degree BOOLEAN DEFAULT FALSE, -- 二级亲属糖尿病史
    dm_relation VARCHAR(100), -- 具体关系
    
    -- 心血管疾病家族史
    cvd_family_history BOOLEAN DEFAULT FALSE,
    cvd_relation VARCHAR(100),
    
    -- 其他代谢疾病
    obesity_family_history BOOLEAN DEFAULT FALSE,
    hypertension_family_history BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (patient_id) REFERENCES PatientBasicInfo(patient_id)
);
```

### 既往病史表 (MedicalHistory)
```sql
CREATE TABLE MedicalHistory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    
    -- 妊娠相关（女性）
    gestational_diabetes BOOLEAN DEFAULT FALSE, -- 妊娠糖尿病史
    gdm_year YEAR, -- 妊娠糖尿病发生年份
    macrosomia_history BOOLEAN DEFAULT FALSE, -- 巨大儿分娩史
    
    -- 内分泌疾病
    pcos BOOLEAN DEFAULT FALSE, -- 多囊卵巢综合征
    thyroid_disease BOOLEAN DEFAULT FALSE, -- 甲状腺疾病
    
    -- 心血管疾病
    coronary_heart_disease BOOLEAN DEFAULT FALSE, -- 冠心病
    stroke BOOLEAN DEFAULT FALSE, -- 脑卒中
    hypertension BOOLEAN DEFAULT FALSE, -- 高血压
    
    -- 其他
    fatty_liver BOOLEAN DEFAULT FALSE, -- 脂肪肝
    sleep_apnea BOOLEAN DEFAULT FALSE, -- 睡眠呼吸暂停
    
    FOREIGN KEY (patient_id) REFERENCES PatientBasicInfo(patient_id)
);
```

### 用药史表 (MedicationHistory)
```sql
CREATE TABLE MedicationHistory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    medication_name VARCHAR(200),
    medication_type ENUM('糖皮质激素', '抗精神病药', '噻嗪类利尿剂', '其他'),
    start_date DATE,
    end_date DATE,
    dosage VARCHAR(100),
    indication VARCHAR(200), -- 用药指征
    FOREIGN KEY (patient_id) REFERENCES PatientBasicInfo(patient_id)
);
```

### 生活方式评估表 (LifestyleAssessment)
```sql
CREATE TABLE LifestyleAssessment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    assessment_date DATE,
    
    -- 体力活动
    exercise_frequency INT, -- 每周运动次数
    exercise_duration INT, -- 每次运动时长（分钟）
    exercise_intensity ENUM('轻度', '中度', '重度'),
    sedentary_hours DECIMAL(3,1), -- 每天静坐时间（小时）
    
    -- 吸烟
    smoking_status ENUM('从不吸烟', '已戒烟', '现在吸烟'),
    cigarettes_per_day INT, -- 每天吸烟支数
    smoking_years INT, -- 吸烟年数
    
    -- 饮酒
    alcohol_consumption ENUM('不饮酒', '轻度饮酒', '中度饮酒', '重度饮酒'),
    alcohol_units_per_week DECIMAL(4,1), -- 每周酒精单位
    
    -- 睡眠
    sleep_hours DECIMAL(3,1), -- 每晚睡眠时间
    sleep_quality ENUM('很好', '好', '一般', '差', '很差'),
    
    -- 饮食
    diet_pattern ENUM('地中海饮食', '低脂饮食', '低碳水化合物', '普通饮食'),
    fruit_vegetable_servings INT, -- 每日果蔬份数
    
    FOREIGN KEY (patient_id) REFERENCES PatientBasicInfo(patient_id)
);
```

### 风险评估结果表 (RiskAssessmentResult)
```sql
CREATE TABLE RiskAssessmentResult (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    assessment_date DATETIME,
    
    -- 各维度评分
    demographic_score INT, -- 人口学特征评分
    biochemical_score INT, -- 生化指标评分
    blood_pressure_score INT, -- 血压评分
    family_history_score INT, -- 家族史评分
    medical_history_score INT, -- 既往史评分
    lifestyle_score INT, -- 生活方式评分
    
    -- 总评分和风险等级
    total_score INT,
    risk_level ENUM('低风险', '中风险', '高风险', '极高风险'),
    
    -- 量化风险
    one_year_risk DECIMAL(5,2), -- 1年发病风险 %
    three_year_risk DECIMAL(5,2), -- 3年发病风险 %
    five_year_risk DECIMAL(5,2), -- 5年发病风险 %
    relative_risk DECIMAL(4,1), -- 相对风险倍数
    
    -- 管理建议
    screening_interval INT, -- 建议筛查间隔（月）
    intervention_recommendation TEXT, -- 干预建议
    
    -- 算法版本
    algorithm_version VARCHAR(20), -- 评估算法版本
    
    FOREIGN KEY (patient_id) REFERENCES PatientBasicInfo(patient_id)
);
```

## 风险评估算法实现

### 1. 评分算法类
```python
class PreDiabetesRiskCalculator:
    """糖尿病前期风险计算器"""
    
    def __init__(self):
        self.weights = {
            'age': 10,
            'bmi': 15,
            'waist_circumference': 8,
            'fpg': 15,
            'hba1c': 15,
            'blood_pressure': 8,
            'family_history': 8,
            'medical_history': 8,
            'lifestyle': 8,
            'other_indicators': 5
        }
    
    def calculate_demographic_score(self, patient_data):
        """计算人口学特征评分"""
        score = 0
        
        # 年龄评分
        age = patient_data['age']
        if age < 40:
            score += 0
        elif age < 60:
            score += 5
        else:
            score += 10
        
        # BMI评分
        bmi = patient_data['bmi']
        if bmi < 24:
            score += 0
        elif bmi < 28:
            score += 5
        else:
            score += 10
        
        # 腰围评分
        waist = patient_data['waist_circumference']
        gender = patient_data['gender']
        
        if gender == 'M':
            if waist < 90:
                score += 0
            elif waist < 95:
                score += 3
            else:
                score += 8
        else:  # Female
            if waist < 85:
                score += 0
            elif waist < 90:
                score += 3
            else:
                score += 8
        
        return min(score, self.weights['age'] + self.weights['bmi'] + self.weights['waist_circumference'])
    
    def calculate_biochemical_score(self, lab_data):
        """计算生化指标评分"""
        score = 0
        
        # 空腹血糖评分
        fpg = lab_data.get('fpg', 0)
        if fpg < 5.6:
            score += 0
        elif fpg < 6.1:
            score += 8
        elif fpg < 7.0:
            score += 15
        else:
            score += 15  # 已达糖尿病诊断标准
        
        # HbA1c评分
        hba1c = lab_data.get('hba1c', 0)
        if hba1c < 5.7:
            score += 0
        elif hba1c < 6.0:
            score += 8
        elif hba1c < 6.5:
            score += 15
        else:
            score += 15  # 已达糖尿病诊断标准
        
        return min(score, self.weights['fpg'] + self.weights['hba1c'])
    
    def calculate_total_risk_score(self, patient_data, lab_data, bp_data, 
                                 family_history, medical_history, lifestyle_data):
        """计算总体风险评分"""
        
        demographic_score = self.calculate_demographic_score(patient_data)
        biochemical_score = self.calculate_biochemical_score(lab_data)
        bp_score = self.calculate_blood_pressure_score(bp_data)
        family_score = self.calculate_family_history_score(family_history)
        medical_score = self.calculate_medical_history_score(medical_history)
        lifestyle_score = self.calculate_lifestyle_score(lifestyle_data)
        
        total_score = (demographic_score + biochemical_score + bp_score + 
                      family_score + medical_score + lifestyle_score)
        
        return {
            'demographic_score': demographic_score,
            'biochemical_score': biochemical_score,
            'blood_pressure_score': bp_score,
            'family_history_score': family_score,
            'medical_history_score': medical_score,
            'lifestyle_score': lifestyle_score,
            'total_score': total_score
        }
    
    def get_risk_level(self, total_score):
        """根据总分确定风险等级"""
        if total_score <= 20:
            return '低风险'
        elif total_score <= 40:
            return '中风险'
        elif total_score <= 60:
            return '高风险'
        else:
            return '极高风险'
    
    def calculate_absolute_risk(self, total_score, patient_data):
        """计算绝对发病风险"""
        # 基础风险率（基于人群流行病学数据）
        base_risk_1y = 0.005  # 1年基础风险0.5%
        base_risk_3y = 0.02   # 3年基础风险2%
        base_risk_5y = 0.05   # 5年基础风险5%
        
        # 相对风险系数
        if total_score <= 20:
            rr = 1.0 + (total_score / 20.0)  # 1.0-2.0
        elif total_score <= 40:
            rr = 2.0 + ((total_score - 20) / 20.0) * 2.0  # 2.0-4.0
        elif total_score <= 60:
            rr = 4.0 + ((total_score - 40) / 20.0) * 6.0  # 4.0-10.0
        else:
            rr = 10.0 + ((total_score - 60) / 20.0) * 10.0  # 10.0-20.0
            rr = min(rr, 20.0)  # 上限20倍
        
        return {
            'one_year_risk': min(base_risk_1y * rr * 100, 100),
            'three_year_risk': min(base_risk_3y * rr * 100, 100),
            'five_year_risk': min(base_risk_5y * rr * 100, 100),
            'relative_risk': rr
        }
```

### 2. 风险评估服务类
```python
class RiskAssessmentService:
    """风险评估服务"""
    
    def __init__(self):
        self.calculator = PreDiabetesRiskCalculator()
    
    def perform_assessment(self, patient_id):
        """执行完整的风险评估"""
        
        # 获取患者数据
        patient_data = self.get_patient_basic_info(patient_id)
        lab_data = self.get_latest_lab_results(patient_id)
        bp_data = self.get_blood_pressure_data(patient_id)
        family_history = self.get_family_history(patient_id)
        medical_history = self.get_medical_history(patient_id)
        lifestyle_data = self.get_lifestyle_assessment(patient_id)
        
        # 计算风险评分
        scores = self.calculator.calculate_total_risk_score(
            patient_data, lab_data, bp_data, 
            family_history, medical_history, lifestyle_data
        )
        
        # 确定风险等级
        risk_level = self.calculator.get_risk_level(scores['total_score'])
        
        # 计算绝对风险
        absolute_risk = self.calculator.calculate_absolute_risk(
            scores['total_score'], patient_data
        )
        
        # 生成管理建议
        recommendations = self.generate_recommendations(risk_level, scores)
        
        # 保存评估结果
        result = {
            'patient_id': patient_id,
            'assessment_date': datetime.now(),
            'scores': scores,
            'risk_level': risk_level,
            'absolute_risk': absolute_risk,
            'recommendations': recommendations
        }
        
        self.save_assessment_result(result)
        return result
    
    def generate_recommendations(self, risk_level, scores):
        """生成个体化管理建议"""
        
        recommendations = {
            'screening_interval': None,
            'lifestyle_interventions': [],
            'medical_interventions': [],
            'monitoring_parameters': [],
            'referral_needed': False
        }
        
        if risk_level == '低风险':
            recommendations['screening_interval'] = 36  # 3年
            recommendations['lifestyle_interventions'] = [
                '维持健康体重',
                '规律运动（每周至少150分钟中等强度运动）',
                '健康饮食（地中海饮食模式）',
                '戒烟限酒',
                '充足睡眠'
            ]
            
        elif risk_level == '中风险':
            recommendations['screening_interval'] = 12  # 1年
            recommendations['lifestyle_interventions'] = [
                '减重5-10%',
                '增加体力活动',
                '营养咨询',
                '戒烟',
                '血压管理'
            ]
            recommendations['monitoring_parameters'] = [
                'OGTT检查',
                '血脂监测',
                '肝功能检查'
            ]
            
        elif risk_level == '高风险':
            recommendations['screening_interval'] = 6  # 6个月
            recommendations['lifestyle_interventions'] = [
                '强化生活方式干预',
                '结构化减重计划',
                '营养师指导',
                '运动处方'
            ]
            recommendations['medical_interventions'] = [
                '考虑二甲双胍预防治疗',
                '血压、血脂管理',
                '定期监测肝肾功能'
            ]
            recommendations['referral_needed'] = True
            
        elif risk_level == '极高风险':
            recommendations['screening_interval'] = 3  # 3个月
            recommendations['lifestyle_interventions'] = [
                '多学科团队管理',
                '强化生活方式干预'
            ]
            recommendations['medical_interventions'] = [
                '积极药物干预',
                '内分泌科会诊',
                '心血管风险评估',
                '定期实验室监测'
            ]
            recommendations['referral_needed'] = True
        
        return recommendations
```

## 数据来源分析

### 1. 医疗机构数据来源
```python
# 医院信息系统(HIS)集成
class HISDataIntegration:
    """医院信息系统数据集成"""
    
    def __init__(self):
        self.data_sources = {
            'patient_demographics': 'HIS.PatientMaster',
            'laboratory_results': 'LIS.LabResults',
            'vital_signs': 'NursingSystem.VitalSigns',
            'medical_history': 'EMR.MedicalHistory',
            'medications': 'CPOE.MedicationOrders'
        }
    
    def sync_patient_data(self, patient_id):
        """同步患者数据"""
        # 从各个系统同步数据
        demographics = self.get_demographics_from_his(patient_id)
        lab_results = self.get_lab_results_from_lis(patient_id)
        vital_signs = self.get_vital_signs(patient_id)
        # ... 其他数据同步
```

### 2. 健康管理平台数据
```python
# 健康管理平台数据集成
class HealthPlatformIntegration:
    """健康管理平台数据集成"""
    
    def __init__(self):
        self.wearable_devices = [
            'Apple Health',
            'Google Fit',
            '华为健康',
            '小米运动'
        ]
    
    def sync_lifestyle_data(self, patient_id):
        """同步生活方式数据"""
        # 从可穿戴设备同步数据
        activity_data = self.get_activity_data(patient_id)
        sleep_data = self.get_sleep_data(patient_id)
        heart_rate_data = self.get_heart_rate_data(patient_id)
```

## 系统架构设计

### 1. 微服务架构
```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                              │
│                  (身份验证/路由/限流)                        │
└─────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
┌───▼────┐            ┌──────▼──────┐           ┌──────▼──────┐
│患者管理 │            │风险评估服务 │           │数据集成服务 │
│服务    │            │            │           │            │
└────────┘            └─────────────┘           └─────────────┘
    │                         │                         │
┌───▼────┐            ┌──────▼──────┐           ┌──────▼──────┐
│用户界面│            │算法引擎服务 │           │外部数据源   │
│服务    │            │            │           │(HIS/LIS等)  │
└────────┘            └─────────────┘           └─────────────┘
```

### 2. API接口设计
```python
# FastAPI接口定义
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="糖尿病前期风险评估系统")

class PatientCreateRequest(BaseModel):
    name: str
    gender: str
    birth_date: str
    height: float
    weight: float
    phone: Optional[str] = None

class LabDataRequest(BaseModel):
    patient_id: str
    fpg: Optional[float] = None
    hba1c: Optional[float] = None
    triglycerides: Optional[float] = None
    hdl_cholesterol: Optional[float] = None

class RiskAssessmentResponse(BaseModel):
    patient_id: str
    risk_level: str
    total_score: int
    one_year_risk: float
    five_year_risk: float
    recommendations: List[str]
    screening_interval: int

@app.post("/patients", response_model=dict)
async def create_patient(patient: PatientCreateRequest):
    """创建患者档案"""
    # 实现患者创建逻辑
    pass

@app.post("/patients/{patient_id}/lab-data")
async def update_lab_data(patient_id: str, lab_data: LabDataRequest):
    """更新实验室检查数据"""
    # 实现实验室数据更新逻辑
    pass

@app.post("/risk-assessment/{patient_id}", response_model=RiskAssessmentResponse)
async def assess_risk(patient_id: str):
    """执行风险评估"""
    try:
        service = RiskAssessmentService()
        result = service.perform_assessment(patient_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/risk-history")
async def get_risk_history(patient_id: str):
    """获取风险评估历史"""
    # 实现历史数据查询逻辑
    pass
```

### 3. 前端界面设计（React组件）
```javascript
// 风险评估表单组件
import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Button, Steps, Card, Progress } from 'antd';

const RiskAssessmentForm = ({ patientId }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});
  const [riskResult, setRiskResult] = useState(null);

  const steps = [
    {
      title: '基本信息',
      content: <BasicInfoForm onDataChange={setFormData} />
    },
    {
      title: '实验室检查',
      content: <LabDataForm onDataChange={setFormData} />
    },
    {
      title: '生活方式',
      content: <LifestyleForm onDataChange={setFormData} />
    },
    {
      title: '风险评估结果',
      content: <RiskResultDisplay result={riskResult} />
    }
  ];

  const performRiskAssessment = async () => {
    try {
      const response = await fetch(`/api/risk-assessment/${patientId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const result = await response.json();
      setRiskResult(result);
      setCurrentStep(3);
    } catch (error) {
      console.error('风险评估失败:', error);
    }
  };

  return (
    <div className="risk-assessment-container">
      <Steps current={currentStep}>
        {steps.map(item => (
          <Steps.Step key={item.title} title={item.title} />
        ))}
      </Steps>
      
      <div className="steps-content">
        {steps[currentStep].content}
      </div>
      
      {currentStep < 2 && (
        <Button type="primary" onClick={() => setCurrentStep(currentStep + 1)}>
          下一步
        </Button>
      )}
      
      {currentStep === 2 && (
        <Button type="primary" onClick={performRiskAssessment}>
          开始评估
        </Button>
      )}
    </div>
  );
};

// 风险结果展示组件
const RiskResultDisplay = ({ result }) => {
  if (!result) return <div>正在评估...</div>;

  const getRiskColor = (level) => {
    switch(level) {
      case '低风险': return '#52c41a';
      case '中风险': return '#faad14';
      case '高风险': return '#fa541c';
      case '极高风险': return '#f5222d';
      default: return '#d9d9d9';
    }
  };

  return (
    <div className="risk-result-display">
      <Card title="风险评估结果">
        <div className="risk-level">
          <h2 style={{ color: getRiskColor(result.risk_level) }}>
            {result.risk_level}
          </h2>
          <div className="risk-score">
            总评分: {result.total_score}/100
            <Progress 
              percent={result.total_score} 
              strokeColor={getRiskColor(result.risk_level)}
            />
          </div>
        </div>
        
        <div className="absolute-risk">
          <h3>发病风险预测</h3>
          <div className="risk-timeline">
            <div>1年内发病风险: {result.one_year_risk.toFixed(1)}%</div>
            <div>3年内发病风险: {result.three_year_risk.toFixed(1)}%</div>
            <div>5年内发病风险: {result.five_year_risk.toFixed(1)}%</div>
          </div>
        </div>
        
        <div className="recommendations">
          <h3>管理建议</h3>
          <ul>
            {result.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
          <div className="screening-interval">
            建议筛查间隔: {result.screening_interval}个月
          </div>
        </div>
      </Card>
    </div>
  );
};
```

## 数据质量控制

### 1. 数据验证规则
```python
class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.validation_rules = {
            'fpg': {'min': 2.0, 'max': 20.0, 'unit': 'mmol/L'},
            'hba1c': {'min': 3.0, 'max': 15.0, 'unit': '%'},
            'bmi': {'min': 10.0, 'max': 60.0, 'unit': 'kg/m²'},
            'age': {'min': 0, 'max': 120, 'unit': 'years'},
            'systolic_bp': {'min': 60, 'max': 300, 'unit': 'mmHg'},
            'diastolic_bp': {'min': 30, 'max': 200, 'unit': 'mmHg'}
        }
    
    def validate_lab_data(self, data):
        """验证实验室数据"""
        errors = []
        
        for field, value in data.items():
            if field in self.validation_rules:
                rule = self.validation_rules[field]
                if value < rule['min'] or value > rule['max']:
                    errors.append(f"{field}值{value}超出正常范围({rule['min']}-{rule['max']} {rule['unit']})")
        
        # 逻辑一致性检查
        if 'fpg' in data and 'hba1c' in data:
            fpg = data['fpg']
            hba1c = data['hba1c']
            
            # 检查空腹血糖与糖化血红蛋白的一致性
            if fpg >= 7.0 and hba1c < 6.0:
                errors.append("空腹血糖提示糖尿病但HbA1c正常，请复查")
            elif fpg < 5.6 and hba1c >= 6.5:
                errors.append("HbA1c提示糖尿病但空腹血糖正常，请复查")
        
        return errors
    
    def validate_patient_data(self, patient_data):
        """验证患者基本数据"""
        errors = []
        
        # BMI计算验证
        if 'height' in patient_data and 'weight' in patient_data:
            height_m = patient_data['height'] / 100
            calculated_bmi = patient_data['weight'] / (height_m ** 2)
            reported_bmi = patient_data.get('bmi', calculated_bmi)
            
            if abs(calculated_bmi - reported_bmi) > 0.5:
                errors.append(f"BMI计算不一致: 计算值{calculated_bmi:.1f}, 录入值{reported_bmi:.1f}")
        
        return errors
```

### 2. 缺失数据处理策略
```python
class MissingDataHandler:
    """缺失数据处理器"""
    
    def __init__(self):
        self.imputation_methods = {
            'fpg': 'population_median',  # 使用人群中位数
            'hba1c': 'correlation_based',  # 基于相关性推算
            'bmi': 'required',  # 必填字段
            'blood_pressure': 'last_observation',  # 使用最近一次测量值
            'lifestyle_factors': 'questionnaire_required'  # 问卷必填
        }
    
    def handle_missing_data(self, patient_data, field):
        """处理缺失数据"""
        method = self.imputation_methods.get(field, 'skip')
        
        if method == 'population_median':
            return self.get_population_median(field, patient_data)
        elif method == 'correlation_based':
            return self.predict_from_correlations(field, patient_data)
        elif method == 'required':
            raise ValueError(f"必填字段{field}不能为空")
        elif method == 'last_observation':
            return self.get_last_observation(patient_data['patient_id'], field)
        else:
            return None
```

## 系统部署和运维

### 1. Docker容器化部署
```dockerfile
# Dockerfile for Risk Assessment Service
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes部署配置
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prediabetes-risk-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prediabetes-risk-service
  template:
    metadata:
      labels:
        app: prediabetes-risk-service
    spec:
      containers:
      - name: api-service
        image: prediabetes-risk:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: prediabetes-risk-service
spec:
  selector:
    app: prediabetes-risk-service
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 3. 监控和日志系统
```python
# 监控和日志配置
import logging
from prometheus_client import Counter, Histogram, start_http_server

# 指标定义
ASSESSMENT_COUNTER = Counter('risk_assessments_total', '总评估次数')
ASSESSMENT_DURATION = Histogram('assessment_duration_seconds', '评估耗时')
ERROR_COUNTER = Counter('assessment_errors_total', '评估错误次数')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/risk-assessment.log'),
        logging.StreamHandler()
    ]
)

class MonitoredRiskAssessmentService(RiskAssessmentService):
    """带监控的风险评估服务"""
    
    def perform_assessment(self, patient_id):
        """执行带监控的风险评估"""
        ASSESSMENT_COUNTER.inc()
        
        with ASSESSMENT_DURATION.time():
            try:
                logging.info(f"开始为患者{patient_id}执行风险评估")
                result = super().perform_assessment(patient_id)
                logging.info(f"患者{patient_id}风险评估完成, 风险等级: {result['risk_level']}")
                return result
            except Exception as e:
                ERROR_COUNTER.inc()
                logging.error(f"患者{patient_id}风险评估失败: {str(e)}")
                raise
```

## 数据安全和隐私保护

### 1. 数据加密
```python
from cryptography.fernet import Fernet
import hashlib

class DataEncryption:
    """数据加密服务"""
    
    def __init__(self, key=None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_sensitive_data(self, data):
        """加密敏感数据"""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)
    
    def decrypt_sensitive_data(self, encrypted_data):
        """解密敏感数据"""
        return self.cipher.decrypt(encrypted_data).decode()
    
    def hash_patient_id(self, patient_id):
        """对患者ID进行哈希处理"""
        return hashlib.sha256(patient_id.encode()).hexdigest()
```

### 2. 访问控制
```python
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

def role_required(required_roles):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user_roles = get_user_roles(current_user)
            
            if not any(role in user_roles for role in required_roles):
                return {'error': '权限不足'}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/risk-assessment/<patient_id>')
@role_required(['医生', '护士', '管理员'])
def get_risk_assessment(patient_id):
    """获取风险评估结果（需要医护人员权限）"""
    pass
```

## 系统参数配置

### 1. 算法参数配置
```python
# config.py - 系统配置参数
class RiskAssessmentConfig:
    """风险评估配置参数"""
    
    # 评分权重配置
    SCORING_WEIGHTS = {
        'age': 10,
        'bmi': 15,
        'waist_circumference': 8,
        'fpg': 15,
        'hba1c': 15,
        'blood_pressure': 8,
        'family_history': 8,
        'medical_history': 8,
        'lifestyle': 8,
        'other_indicators': 5
    }
    
    # 阈值配置
    THRESHOLDS = {
        'fpg_prediabetes': 6.1,  # mmol/L
        'fpg_diabetes': 7.0,     # mmol/L
        'hba1c_prediabetes': 6.0,  # %
        'hba1c_diabetes': 6.5,     # %
        'bmi_overweight': 24.0,     # kg/m²
        'bmi_obesity': 28.0,        # kg/m²
        'waist_male_risk': 90,      # cm
        'waist_female_risk': 85     # cm
    }
    
    # 基础风险率（基于中国人群数据）
    BASE_RISK_RATES = {
        '1year': 0.005,   # 0.5%
        '3year': 0.02,    # 2%
        '5year': 0.05,    # 5%
        '10year': 0.12    # 12%
    }
    
    # 相对风险系数
    RELATIVE_RISK_COEFFICIENTS = {
        'age_per_year': 1.03,        # 每增加1岁
        'bmi_per_unit': 1.12,        # 每增加1 kg/m²
        'fpg_per_mmol': 2.3,         # 每增加1 mmol/L
        'family_history_first': 3.5,  # 一级亲属糖尿病史
        'family_history_second': 1.8, # 二级亲属糖尿病史
        'gdm_history': 7.4,          # 妊娠糖尿病史
        'hypertension': 2.1,         # 高血压
        'metabolic_syndrome': 4.8     # 代谢综合征
    }
    
    # 筛查间隔配置（月）
    SCREENING_INTERVALS = {
        '低风险': 36,    # 3年
        '中风险': 12,    # 1年
        '高风险': 6,     # 6个月
        '极高风险': 3    # 3个月
    }
```

## 质量保证和测试

### 1. 单元测试
```python
import unittest
from unittest.mock import patch, MagicMock

class TestRiskCalculator(unittest.TestCase):
    """风险计算器测试"""
    
    def setUp(self):
        self.calculator = PreDiabetesRiskCalculator()
    
    def test_demographic_score_calculation(self):
        """测试人口学评分计算"""
        patient_data = {
            'age': 45,
            'bmi': 26.5,
            'waist_circumference': 95,
            'gender': 'M'
        }
        
        score = self.calculator.calculate_demographic_score(patient_data)
        
        # 期望评分: 年龄5分 + BMI5分 + 腰围8分 = 18分
        self.assertEqual(score, 18)
    
    def test_biochemical_score_calculation(self):
        """测试生化指标评分计算"""
        lab_data = {
            'fpg': 6.3,    # 糖尿病前期，15分
            'hba1c': 6.2   # 糖尿病前期，15分
        }
        
        score = self.calculator.calculate_biochemical_score(lab_data)
        
        # 期望总分: 15 + 15 = 30分
        self.assertEqual(score, 30)
    
    def test_risk_level_determination(self):
        """测试风险等级确定"""
        test_cases = [
            (15, '低风险'),
            (35, '中风险'),
            (55, '高风险'),
            (75, '极高风险')
        ]
        
        for score, expected_level in test_cases:
            with self.subTest(score=score):
                level = self.calculator.get_risk_level(score)
                self.assertEqual(level, expected_level)

class TestDataValidator(unittest.TestCase):
    """数据验证器测试"""
    
    def setUp(self):
        self.validator = DataValidator()
    
    def test_lab_data_validation(self):
        """测试实验室数据验证"""
        # 正常数据
        normal_data = {'fpg': 5.5, 'hba1c': 5.8}
        errors = self.validator.validate_lab_data(normal_data)
        self.assertEqual(len(errors), 0)
        
        # 异常数据
        abnormal_data = {'fpg': 25.0, 'hba1c': 2.0}  # 超出正常范围
        errors = self.validator.validate_lab_data(abnormal_data)
        self.assertGreater(len(errors), 0)
    
    def test_data_consistency_check(self):
        """测试数据一致性检查"""
        inconsistent_data = {'fpg': 8.0, 'hba1c': 5.5}  # 数据不一致
        errors = self.validator.validate_lab_data(inconsistent_data)
        self.assertGreater(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
```

### 2. 集成测试
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestRiskAssessmentAPI:
    """风险评估API集成测试"""
    
    def test_create_patient(self):
        """测试创建患者"""
        patient_data = {
            "name": "张三",
            "gender": "M",
            "birth_date": "1980-01-01",
            "height": 175.0,
            "weight": 75.0
        }
        
        response = client.post("/patients", json=patient_data)
        assert response.status_code == 200
        assert "patient_id" in response.json()
    
    def test_risk_assessment_flow(self):
        """测试完整的风险评估流程"""
        # 1. 创建患者
        patient_data = {
            "name": "李四",
            "gender": "F",
            "birth_date": "1975-05-15",
            "height": 160.0,
            "weight": 68.0
        }
        
        create_response = client.post("/patients", json=patient_data)
        patient_id = create_response.json()["patient_id"]
        
        # 2. 添加实验室数据
        lab_data = {
            "patient_id": patient_id,
            "fpg": 6.2,
            "hba1c": 6.1,
            "triglycerides": 2.1,
            "hdl_cholesterol": 1.0
        }
        
        lab_response = client.post(f"/patients/{patient_id}/lab-data", json=lab_data)
        assert lab_response.status_code == 200
        
        # 3. 执行风险评估
        assessment_response = client.post(f"/risk-assessment/{patient_id}")
        assert assessment_response.status_code == 200
        
        result = assessment_response.json()
        assert "risk_level" in result
        assert "total_score" in result
        assert "recommendations" in result
```

## 数据来源详细说明

### 1. 医疗机构数据源
```python
# 数据来源映射表
DATA_SOURCE_MAPPING = {
    # 医院信息系统(HIS)
    'patient_demographics': {
        'source': 'HIS.PatientMaster',
        'fields': ['患者ID', '姓名', '性别', '出生日期', '身高', '体重'],
        'update_frequency': 'on_registration',
        'data_quality': 'high'
    },
    
    # 实验室信息系统(LIS)
    'laboratory_results': {
        'source': 'LIS.LabResults',
        'fields': ['空腹血糖', '糖化血红蛋白', '血脂', '肝肾功能'],
        'update_frequency': 'real_time',
        'data_quality': 'high',
        'normal_ranges': {
            'fpg': '3.9-6.1 mmol/L',
            'hba1c': '4.0-6.0%',
            'triglycerides': '<1.7 mmol/L'
        }
    },
    
    # 护理信息系统
    'vital_signs': {
        'source': 'NursingSystem.VitalSigns',
        'fields': ['血压', '心率', '体温', '体重'],
        'update_frequency': 'per_visit',
        'data_quality': 'medium'
    },
    
    # 电子病历系统(EMR)
    'medical_history': {
        'source': 'EMR.MedicalHistory',
        'fields': ['既往史', '家族史', '药物史', '手术史'],
        'update_frequency': 'on_visit',
        'data_quality': 'medium'
    }
}
```

### 2. 外部数据源集成
```python
# 外部数据源配置
EXTERNAL_DATA_SOURCES = {
    # 可穿戴设备数据
    'wearable_devices': {
        'apple_health': {
            'api_endpoint': 'https://api.apple.com/health',
            'data_types': ['steps', 'heart_rate', 'sleep', 'activity'],
            'sync_interval': '1_hour'
        },
        'google_fit': {
            'api_endpoint': 'https://www.googleapis.com/fitness/v1',
            'data_types': ['activity', 'location', 'nutrition'],
            'sync_interval': '1_hour'
        }
    },
    
    # 第三方健康平台
    'health_platforms': {
        'yuanfudao_health': {
            'data_types': ['diet_records', 'exercise_logs', 'weight_tracking'],
            'sync_method': 'webhook'
        }
    },
    
    # 公共卫生数据
    'population_data': {
        'china_cdc': {
            'data_types': ['diabetes_prevalence', 'risk_factors_distribution'],
            'update_frequency': 'annually',
            'use_case': 'baseline_risk_calculation'
        }
    }
}
```

这个实现方案涵盖了：
- 完整的数据模型设计
- 风险评估算法实现
- 系统架构和API设计
- 前端界面组件
- 数据质量控制
- 安全和隐私保护
- 部署和运维方案
- 测试策略
- 详细的数据来源说明

您希望我详细展开哪个部分，或者有其他特定的实现问题需要讨论？
```