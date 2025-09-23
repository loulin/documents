# 妊娠糖尿病(GDM)风险评估与分层工具

## 概述

本工具基于国际最新指南和循证医学证据，为妊娠期女性提供系统性的GDM风险评估、早期筛查和动态监测。集成连续血糖监测(CGM)技术，实现精准的个体化风险分层和管理策略。

### 核心特点
- **全孕期覆盖**: 孕前-孕早期-孕中期-孕晚期全程评估
- **动态风险评估**: 基于CGM的实时血糖监测和风险重新分层
- **多维度整合**: 结合临床、生化、影像和生活方式因素
- **个体化管理**: 根据风险分层提供针对性干预方案
- **预测模型**: 机器学习算法优化的GDM发生风险预测

## 风险评估参数体系

### 1. 孕前风险因素 (Pre-conception Risk Factors)

#### 1.1 人口学特征
| 参数 | 低风险 | 中风险 | 高风险 | 权重 |
|------|--------|--------|--------|------|
| **年龄** | <25岁 | 25-34岁 | ≥35岁 | 高 |
| **孕前BMI** | 18.5-24.9 | 25.0-29.9 | ≥30.0 | 极高 |
| **种族** | 低风险种族 | 中等风险 | 高风险(亚洲、西班牙裔) | 中 |

#### 1.2 既往妊娠史
| 参数 | 低风险 | 中风险 | 高风险 | 权重 |
|------|--------|--------|--------|------|
| **GDM史** | 无 | - | 有GDM史 | 极高 |
| **巨大儿史** | 无 | - | 新生儿体重≥4000g | 高 |
| **妊娠丢失** | 无 | 偶发 | 反复流产/死胎 | 中 |
| **多胎妊娠** | 单胎 | - | 双胎/多胎 | 中 |

#### 1.3 家族史与遗传因素
| 参数 | 低风险 | 中风险 | 高风险 | 权重 |
|------|--------|--------|--------|------|
| **糖尿病家族史** | 无 | 二级亲属 | 一级亲属T2DM | 高 |
| **GDM家族史** | 无 | 二级亲属 | 母亲/姐妹GDM史 | 高 |
| **遗传综合征** | 无 | - | PCOS/代谢综合征 | 中 |

#### 1.4 基础代谢状态
| 参数 | 正常范围 | 边界值 | 异常值 | 权重 |
|------|----------|--------|--------|------|
| **空腹血糖** | <5.1 mmol/L | 5.1-5.5 | ≥5.6 mmol/L | 极高 |
| **HbA1c** | <5.7% | 5.7-6.4% | ≥6.5% | 极高 |
| **HOMA-IR** | <2.5 | 2.5-3.5 | >3.5 | 高 |
| **胰岛素** | 2.6-24.9 mIU/L | 25-35 | >35 mIU/L | 高 |

### 2. 孕期动态风险因素 (Pregnancy Dynamic Factors)

#### 2.1 妊娠期生理变化
| 孕周 | 评估重点 | 关键指标 | 风险阈值 |
|------|----------|----------|----------|
| **6-12周** | 早期胰岛素抵抗 | 空腹血糖、胰岛素 | FPG ≥5.1 mmol/L |
| **13-27周** | 胎盘激素影响 | 餐后血糖、体重增长 | PPG ≥7.8 mmol/L |
| **28-36周** | 胰岛素抵抗峰值 | OGTT、CGM数据 | 标准OGTT阳性 |
| **37-42周** | 分娩前评估 | 血糖控制、胎儿监测 | 血糖波动>3.9 mmol/L |

#### 2.2 体重管理指标
```
推荐体重增长(kg) = 基础推荐 + 个体化调整

基础推荐:
- BMI <18.5: 12.5-18.0 kg
- BMI 18.5-24.9: 11.5-16.0 kg  
- BMI 25.0-29.9: 7.0-11.5 kg
- BMI ≥30.0: 5.0-9.0 kg

风险评估:
- 适宜增重: 低风险
- 超重增长: 中风险 (+1.5倍标准)
- 过度增重: 高风险 (+2.0倍标准)
```

#### 2.3 CGM集成评估
| CGM指标 | 正常范围 | 边界值 | 异常值 |
|---------|----------|--------|--------|
| **平均血糖** | 4.0-6.5 mmol/L | 6.6-7.0 | >7.0 mmol/L |
| **血糖变异系数** | <36% | 36-40% | >40% |
| **目标范围时间(TIR)** | >70% | 50-70% | <50% |
| **高血糖时间** | <25% | 25-35% | >35% |
| **夜间血糖稳定性** | 变异<1.4 mmol/L | 1.4-2.0 | >2.0 mmol/L |

### 3. 临床实验室指标

#### 3.1 标准OGTT诊断标准 (24-28周)
| 时间点 | 正常值 | GDM诊断阈值 | 单位 |
|--------|--------|-------------|------|
| **空腹** | <5.1 | ≥5.1 | mmol/L |
| **1小时** | <10.0 | ≥10.0 | mmol/L |
| **2小时** | <8.5 | ≥8.5 | mmol/L |

*注: 满足任意一项即可诊断GDM*

#### 3.2 辅助生化指标
| 指标 | 正常范围 | 风险阈值 | 临床意义 |
|------|----------|----------|----------|
| **糖化血红蛋白** | <5.7% | ≥5.7% | 长期血糖控制 |
| **果糖胺** | 200-285 μmol/L | >285 | 近期血糖控制 |
| **1,5-脱水葡萄糖醇** | <14.6 μmol/L | ≥14.6 | 短期血糖波动 |
| **C肽** | 1.1-4.4 ng/mL | >4.4 | 胰岛素分泌功能 |
| **HOMA-β** | >100% | <75% | β细胞功能 |

#### 3.3 炎症与代谢标志物
| 标志物 | 正常范围 | 异常阈值 | 风险意义 |
|--------|----------|----------|----------|
| **CRP** | <3.0 mg/L | ≥3.0 mg/L | 慢性炎症 |
| **TNF-α** | <2.3 pg/mL | ≥2.3 pg/mL | 胰岛素抵抗 |
| **IL-6** | <1.8 pg/mL | ≥1.8 pg/mL | 炎症反应 |
| **脂联素** | >10 μg/mL | <10 μg/mL | 代谢保护因子 |
| **瘦素** | 10-30 ng/mL | >30 ng/mL | 能量代谢异常 |

### 4. 胎儿相关风险指标

#### 4.1 超声评估参数
| 孕周 | 评估项目 | 正常范围 | 风险阈值 |
|------|----------|----------|----------|
| **20-24周** | 双顶径、腹围 | 同孕周正常值 | >95百分位 |
| **28-32周** | 估计胎儿体重 | 50-75百分位 | >90百分位 |
| **34-37周** | 腹围/双顶径比值 | <1.1 | ≥1.1 |
| **38-40周** | 估计出生体重 | 2500-4000g | >4000g |

#### 4.2 羊水与胎盘评估
| 指标 | 正常 | 异常 | 临床意义 |
|------|------|------|----------|
| **羊水量** | AFI 8-20cm | >25cm | 羊水过多提示血糖控制不佳 |
| **胎盘厚度** | <40mm | ≥40mm | 可能提示代谢异常 |
| **脐动脉血流** | PI <95百分位 | PI ≥95百分位 | 胎盘功能评估 |

## GDM风险分层系统

### 低风险 (总分 0-25分)
**特征:**
- 年龄 <30岁
- 孕前BMI <25 kg/m²
- 无GDM/T2DM家族史
- 无不良妊娠史
- 基础血糖正常
- 早孕期代谢指标正常

**量化风险:**
- GDM发生率: <3%
- 巨大儿风险: <2%
- 母儿并发症: 最低

**管理策略:**
- 24-28周标准OGTT筛查
- 孕期营养指导
- 体重管理
- 常规产检

### 中风险 (总分 26-45分)
**特征:**
- 年龄 30-34岁
- 孕前BMI 25-29.9 kg/m²
- 有二级亲属糖尿病史
- 既往巨大儿史
- 边界性血糖升高
- 轻度胰岛素抵抗

**量化风险:**
- GDM发生率: 8-15%
- 巨大儿风险: 5-10%
- 需要强化监测

**管理策略:**
- 孕早期(12-16周) + 24-28周双重筛查
- CGM监测考虑
- 营养师咨询
- 体重严格管理
- 2周1次专科随访

### 高风险 (总分 46-65分)
**特征:**
- 年龄 ≥35岁
- 孕前BMI ≥30 kg/m²
- 一级亲属T2DM史
- 既往GDM史
- PCOS/代谢综合征
- 明显胰岛素抵抗

**量化风险:**
- GDM发生率: 25-40%
- 巨大儿风险: 15-25%
- 母儿并发症显著增加

**管理策略:**
- 孕早期即开始血糖监测
- CGM持续监测
- 内分泌专科管理
- 营养治疗优先
- 必要时孕期胰岛素治疗
- 每周专科随访

### 极高风险 (总分 >65分)
**特征:**
- 多重高危因素聚集
- 既往反复GDM史
- 孕前糖尿病前期
- 严重肥胖(BMI ≥35)
- 多胎妊娠

**量化风险:**
- GDM发生率: >50%
- 巨大儿风险: >30%
- 严重母儿并发症高发

**管理策略:**
- 孕前及孕早期积极干预
- CGM全程监测
- 多学科团队管理
- 早期胰岛素治疗
- 密切胎儿监测
- 必要时提前终止妊娠

## 综合评分算法

### 基础评分公式
```python
def calculate_gdm_risk_score(patient_data):
    """
    GDM风险综合评分算法
    """
    
    # 权重系数
    weights = {
        'age': 0.15,           # 年龄权重
        'bmi': 0.20,           # BMI权重  
        'family_history': 0.15, # 家族史权重
        'obstetric_history': 0.20, # 产科史权重
        'metabolic_markers': 0.25,  # 代谢指标权重
        'lifestyle_factors': 0.05   # 生活方式权重
    }
    
    # 各维度评分
    age_score = calculate_age_score(patient_data['age'])
    bmi_score = calculate_bmi_score(patient_data['bmi'])
    family_score = calculate_family_history_score(patient_data['family_history'])
    obstetric_score = calculate_obstetric_history_score(patient_data['obstetric_history'])
    metabolic_score = calculate_metabolic_score(patient_data['metabolic_markers'])
    lifestyle_score = calculate_lifestyle_score(patient_data['lifestyle'])
    
    # 加权总分
    total_score = (
        age_score * weights['age'] +
        bmi_score * weights['bmi'] +
        family_score * weights['family_history'] +
        obstetric_score * weights['obstetric_history'] +
        metabolic_score * weights['metabolic_markers'] +
        lifestyle_score * weights['lifestyle_factors']
    ) * 100
    
    return total_score

def calculate_dynamic_risk_adjustment(cgm_data, gestational_week):
    """
    基于CGM数据的动态风险调整
    """
    
    adjustment_factors = {
        'glucose_variability': calculate_glucose_variability(cgm_data),
        'time_in_range': calculate_time_in_range(cgm_data),
        'dawn_phenomenon': calculate_dawn_phenomenon(cgm_data),
        'postprandial_response': calculate_postprandial_response(cgm_data)
    }
    
    # 孕周特异性调整
    gestational_multiplier = get_gestational_week_multiplier(gestational_week)
    
    risk_adjustment = sum(adjustment_factors.values()) * gestational_multiplier
    
    return risk_adjustment
```

### CGM集成风险评估
```python
class CGM_GDM_RiskAssessment:
    def __init__(self):
        self.glucose_targets = {
            'fasting': 5.1,      # mmol/L
            'post_meal_1h': 10.0, # mmol/L  
            'post_meal_2h': 8.5,  # mmol/L
            'bedtime': 7.8        # mmol/L
        }
    
    def analyze_cgm_patterns(self, cgm_data, gestational_week):
        """
        分析CGM数据模式
        """
        patterns = {
            'dawn_phenomenon': self._detect_dawn_phenomenon(cgm_data),
            'postprandial_peaks': self._detect_postprandial_peaks(cgm_data),
            'overnight_stability': self._assess_overnight_stability(cgm_data),
            'glucose_variability': self._calculate_glucose_variability(cgm_data)
        }
        
        risk_score = self._convert_patterns_to_risk_score(patterns, gestational_week)
        
        return {
            'patterns': patterns,
            'risk_score': risk_score,
            'recommendations': self._generate_recommendations(patterns)
        }
    
    def _detect_dawn_phenomenon(self, cgm_data):
        """检测黎明现象"""
        early_morning = cgm_data.between_time('03:00', '07:00')
        dawn_rise = early_morning.glucose.max() - early_morning.glucose.min()
        
        return {
            'present': dawn_rise > 1.7,  # mmol/L
            'magnitude': dawn_rise,
            'clinical_significance': 'high' if dawn_rise > 2.8 else 'moderate' if dawn_rise > 1.7 else 'low'
        }
    
    def _detect_postprandial_peaks(self, cgm_data):
        """检测餐后血糖峰值"""
        meal_windows = [
            ('07:00', '10:00'),  # 早餐后
            ('12:00', '15:00'),  # 午餐后  
            ('18:00', '21:00')   # 晚餐后
        ]
        
        peaks = {}
        for i, (start, end) in enumerate(meal_windows):
            window_data = cgm_data.between_time(start, end)
            peaks[f'meal_{i+1}'] = {
                'max_glucose': window_data.glucose.max(),
                'time_to_peak': window_data.glucose.idxmax(),
                'exceeds_target': window_data.glucose.max() > self.glucose_targets['post_meal_1h']
            }
        
        return peaks
```

## 实施建议与质量控制

### 临床实施流程
1. **孕前咨询期**: 风险评估、生活方式指导
2. **孕早期(6-13周)**: 基线评估、高危筛查
3. **孕中期(14-27周)**: 动态监测、风险重新分层
4. **孕晚期(28-40周)**: 强化管理、分娩准备
5. **产后随访**: 产后糖代谢评估、远期风险管理

### 质量控制要点
- **标准化操作**: 统一的评估流程和诊断标准
- **设备校准**: CGM设备定期校准和质控
- **人员培训**: 专业团队持续教育
- **数据质量**: 实时数据验证和异常值处理
- **临床验证**: 定期评估预测模型的准确性

### 技术集成建议
- **EMR集成**: 与医院信息系统无缝对接
- **移动应用**: 患者端血糖记录和健康教育
- **远程监护**: 高危患者的远程血糖监测
- **AI辅助**: 机器学习优化风险预测算法
- **多中心协作**: 数据共享和循证医学研究

---

*本工具基于最新国际指南制定，需要结合临床实际情况使用，不能替代医师的专业判断。*