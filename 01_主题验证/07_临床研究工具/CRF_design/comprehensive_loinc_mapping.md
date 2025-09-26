# CRF实验室检查LOINC编码映射表

## 🎯 标准化实施方案

### 核心目标
- **通用编码标准**: 采用LOINC编码系统实现跨机构标准化
- **单位统一**: 建立标准单位系统和自动转换机制  
- **参考范围**: 统一参考区间标准，支持年龄性别分层
- **系统对接**: 符合HL7 FHIR标准，便于HIS/LIS系统集成

## 📊 LOINC编码映射详表

### 1. 血糖检测模块 (glucose_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 常用单位转换 | 参考范围 |
|---------|---------|----------|----------|----------|------------|----------|
| Fasting Glucose | 空腹血糖 | fasting_glucose | 1558-6 | mmol/L | mg/dL×0.0555→mmol/L | 3.9-6.1 mmol/L |
| Random Glucose | 随机血糖 | random_glucose | 33747-0 | mmol/L | mg/dL×0.0555→mmol/L | <11.1 mmol/L |
| HbA1c | 糖化血红蛋白 | hba1c_percent | 4548-4 | % | 无需转换 | <7.0% (糖尿病); <5.7% (正常) |
| Glycated Albumin | 糖化白蛋白 | glycated_albumin_percent | 33394-0 | % | 无需转换 | 11.0-16.0% |
| GADA | 谷氨酸脱羧酶抗体 | autoantibody_results | 13926-0 | IU/mL | 无需转换 | <1.0 IU/mL (阴性) |
| IAA | 胰岛素抗体 | autoantibody_results | 8086-3 | nU/mL | 无需转换 | <7.0 nU/mL (阴性) |
| IA-2A | 蛋白酪氨酸磷酸酶抗体 | autoantibody_results | 31835-7 | U/mL | 无需转换 | <0.75 U/mL (阴性) |
| ZnT8A | 锌转运蛋白8抗体 | autoantibody_results | 62301-5 | U/mL | 无需转换 | <15.0 U/mL (阴性) |
| ICA | 胰岛细胞抗体 | autoantibody_results | 13927-8 | JDF单位 | 无需转换 | <2.5 JDF单位 (阴性) |

### 2. OGTT胰岛素释放实验 (ogtt_insulin_test)

| 时间点 | 血糖LOINC | 胰岛素LOINC | C肽LOINC | 胰高血糖素LOINC |
|--------|-----------|------------|----------|----------------|
| 0小时 | 1558-6 | 20448-7 | 1986-9 | 2963-7 |
| 0.5小时 | 33743-9 | 6883-9 | 1987-7 | 2964-5 |
| 1小时 | 20436-2 | 12160-9 | 1988-5 | 2965-2 |
| 2小时 | 20438-8 | 12171-6 | 1989-3 | 2966-0 |
| 3小时 | 6777-3 | 33856-9 | 1990-1 | 2967-8 |

**单位标准化**:
- 血糖: mmol/L (mg/dL×0.0555)
- 胰岛素: mIU/L (pmol/L÷6.945, μIU/L=mIU/L)
- C肽: nmol/L (μg/L×0.331, ng/mL×0.298, pmol/L÷1000)
- 胰高血糖素: pmol/L (ng/L×0.287, pg/mL×0.287)

### 3. 肝功能检查 (liver_function_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 转换公式 | 参考范围 |
|---------|---------|----------|----------|----------|----------|----------|
| Total Protein | 总蛋白 | total_protein | 2885-2 | g/L | g/dL×10→g/L | 60-83 g/L |
| AST | 谷草转氨酶 | ast | 1920-8 | U/L | IU/L=U/L | 8-40 U/L |
| ALT | 谷丙转氨酶 | alt | 1742-6 | U/L | IU/L=U/L | 5-35 U/L |
| AST/ALT Ratio | 谷草/谷丙比值 | ast_alt_ratio | 16325-3 | 比值 | 自动计算 | 0.8-1.2 |
| Albumin | 白蛋白 | albumin | 1751-7 | g/L | g/dL×10→g/L | 35-55 g/L |
| Total Bilirubin | 总胆红素 | total_bilirubin | 1975-2 | μmol/L | mg/dL×17.1→μmol/L | 3.4-20.5 μmol/L |
| Indirect Bilirubin | 间接胆红素 | indirect_bilirubin | 1971-1 | μmol/L | mg/dL×17.1→μmol/L | 1.7-13.7 μmol/L |
| Direct Bilirubin | 直接胆红素 | direct_bilirubin | 1968-7 | μmol/L | mg/dL×17.1→μmol/L | 0-6.8 μmol/L |
| ALP | 碱性磷酸酶 | alkaline_phosphatase | 6768-6 | U/L | IU/L=U/L | 40-150 U/L |

### 4. 肾功能检查 (kidney_function_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 转换公式 | 参考范围 |
|---------|---------|----------|----------|----------|----------|----------|
| Urea | 尿素 | urea | 3094-0 | mmol/L | mg/dL×0.357→mmol/L | 2.5-7.5 mmol/L |
| Creatinine | 肌酐 | creatinine | 2160-0 | μmol/L | mg/dL×88.4→μmol/L | 男:62-115 μmol/L; 女:53-97 μmol/L |
| Uric Acid | 尿酸 | uric_acid | 3084-1 | μmol/L | mg/dL×59.48→μmol/L | 男:208-428 μmol/L; 女:155-357 μmol/L |
| eGFR | 估算肾小球滤过率 | egfr | 33914-3 | mL/min/1.73m² | 无需转换 | >90 mL/min/1.73m² |

### 5. 血脂检查 (lipid_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 转换公式 | 参考范围 |
|---------|---------|----------|----------|----------|----------|----------|
| Triglycerides | 甘油三酯 | triglycerides | 2571-8 | mmol/L | mg/dL×0.0113→mmol/L | <1.7 mmol/L |
| Total Cholesterol | 总胆固醇 | total_cholesterol | 2093-3 | mmol/L | mg/dL×0.0259→mmol/L | <5.2 mmol/L |
| HDL-C | 高密度脂蛋白 | hdl_cholesterol | 2085-9 | mmol/L | mg/dL×0.0259→mmol/L | >1.0 mmol/L (男); >1.3 mmol/L (女) |
| LDL-C | 低密度脂蛋白 | ldl_cholesterol | 18262-6 | mmol/L | mg/dL×0.0259→mmol/L | <3.4 mmol/L |
| VLDL-C | 极低密度脂蛋白 | vldl_cholesterol | 13457-7 | mmol/L | mg/dL×0.0259→mmol/L | 0.13-0.65 mmol/L |
| ApoA1 | 载脂蛋白A1 | apolipoprotein_a1 | 1869-7 | g/L | mg/dL÷100→g/L | 1.0-1.6 g/L |
| ApoB | 载脂蛋白B | apolipoprotein_b | 1884-6 | g/L | mg/dL÷100→g/L | 0.6-1.2 g/L |
| Lp(a) | 脂蛋白(a) | lipoprotein_a | 10835-7 | g/L | mg/dL÷100→g/L | <0.3 g/L |
| FFA | 游离脂肪酸 | free_fatty_acid | 33747-0 | mmol/L | 无需转换 | 0.1-0.6 mmol/L |

### 6. 尿液检查 (urine_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 编码方式 | 参考范围 |
|---------|---------|----------|----------|----------|----------|----------|
| Urine Protein | 尿蛋白 | urine_protein | 2887-8 | 定性 | 0=阴性,1=弱阳性,2=+,3=++,4=+++ | 阴性 |
| Ketone Bodies | 酮体 | ketone_bodies | 2514-8 | 定性 | 0=阴性,1=弱阳性,2=+,3=++,4=+++ | 阴性 |
| ACR | 白蛋白/肌酐比 | albumin_creatinine_ratio | 14959-1 | mg/g | mg/mmol×8.84→mg/g | <30 mg/g |
| Microalbumin | 微量白蛋白 | microalbumin | 14957-5 | mg/L | μg/mL=mg/L | <20 mg/L |

### 7. 血常规检查 (blood_routine_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 转换公式 | 参考范围 |
|---------|---------|----------|----------|----------|----------|----------|
| WBC | 白细胞计数 | wbc_count | 6690-2 | ×10⁹/L | G/L×10⁹→×10⁹/L, K/μL×10⁻³→×10⁹/L | 4.0-10.0×10⁹/L |
| RBC | 红细胞计数 | rbc_count | 789-8 | ×10¹²/L | T/L×10¹²→×10¹²/L, M/μL×10⁻⁶→×10¹²/L | 男:4.0-5.5×10¹²/L; 女:3.5-5.0×10¹²/L |
| PLT | 血小板计数 | platelet_count | 777-3 | ×10⁹/L | G/L×10⁹→×10⁹/L, K/μL×10⁻³→×10⁹/L | 100-300×10⁹/L |
| Hb | 血红蛋白 | hemoglobin | 718-7 | g/L | g/dL×10→g/L | 男:120-160 g/L; 女:110-150 g/L |
| NEU | 中性粒细胞 | neutrophil_count | 751-8 | ×10⁹/L | G/L×10⁹→×10⁹/L, K/μL×10⁻³→×10⁹/L | 2.0-7.0×10⁹/L |
| LYM | 淋巴细胞 | lymphocyte_count | 731-0 | ×10⁹/L | G/L×10⁹→×10⁹/L, K/μL×10⁻³→×10⁹/L | 0.8-4.0×10⁹/L |
| MON | 单核细胞 | monocyte_count | 742-7 | ×10⁹/L | G/L×10⁹→×10⁹/L, K/μL×10⁻³→×10⁹/L | 0.12-0.8×10⁹/L |

### 8. 甲状腺功能 (thyroid_function_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 转换公式 | 参考范围 |
|---------|---------|----------|----------|----------|----------|----------|
| FT3 | 游离三碘甲状原氨酸 | free_t3 | 3051-0 | pmol/L | ng/dL×15.36→pmol/L | 3.5-6.5 pmol/L |
| FT4 | 游离甲状腺素 | free_t4 | 3024-7 | pmol/L | ng/dL×12.87→pmol/L | 11.5-23.0 pmol/L |
| TSH | 促甲状腺素 | tsh | 3016-3 | mIU/L | μIU/mL=mIU/L | 0.55-4.78 mIU/L |

### 9. 维生素D检查 (vitamin_d_tests)

| 检查项目 | 中文名称 | CRF字段名 | LOINC代码 | 标准单位 | 转换公式 | 参考范围 |
|---------|---------|----------|----------|----------|----------|----------|
| 25(OH)D | 25羟基维生素D | vitamin_d_25_oh | 14635-7 | nmol/L | ng/mL×2.496→nmol/L | 75-250 nmol/L |

## 🔄 单位转换算法

### 自动转换函数设计

```javascript
// 血糖转换
function convertGlucose(value, fromUnit, toUnit) {
    if (fromUnit === 'mg/dL' && toUnit === 'mmol/L') {
        return (value * 0.0555).toFixed(1);
    }
    if (fromUnit === 'mmol/L' && toUnit === 'mg/dL') {
        return (value * 18.018).toFixed(0);
    }
    return value;
}

// 胰岛素转换
function convertInsulin(value, fromUnit, toUnit) {
    const conversions = {
        'pmol/L_to_mIU/L': value / 6.945,
        'mIU/L_to_pmol/L': value * 6.945,
        'μIU/L_to_mIU/L': value
    };
    const key = `${fromUnit}_to_${toUnit}`;
    return conversions[key] ? conversions[key].toFixed(2) : value;
}

// C肽转换
function convertCPeptide(value, fromUnit, toUnit) {
    const conversions = {
        'μg/L_to_nmol/L': value * 0.331,
        'ng/mL_to_nmol/L': value * 0.298,
        'pmol/L_to_nmol/L': value / 1000
    };
    const key = `${fromUnit}_to_${toUnit}`;
    return conversions[key] ? conversions[key].toFixed(2) : value;
}
```

## 📋 HL7 FHIR结构定义

### 血糖观察资源示例

```json
{
    "resourceType": "Observation",
    "id": "glucose-fasting-001",
    "status": "final",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }
            ]
        }
    ],
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "1558-6",
                "display": "Fasting glucose [Moles/volume] in Blood"
            }
        ]
    },
    "subject": {
        "reference": "Patient/patient-001"
    },
    "valueQuantity": {
        "value": 6.2,
        "unit": "mmol/L",
        "system": "http://unitsofmeasure.org",
        "code": "mmol/L"
    },
    "referenceRange": [
        {
            "low": {
                "value": 3.9,
                "unit": "mmol/L"
            },
            "high": {
                "value": 6.1,
                "unit": "mmol/L"
            },
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/referencerange-meaning",
                        "code": "normal",
                        "display": "Normal Range"
                    }
                ]
            }
        }
    ]
}
```

### 糖化血红蛋白观察资源示例

```json
{
    "resourceType": "Observation",
    "id": "hba1c-001",
    "status": "final",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory"
                }
            ]
        }
    ],
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "4548-4",
                "display": "Hemoglobin A1c/Hemoglobin.total in Blood"
            }
        ]
    },
    "subject": {
        "reference": "Patient/patient-001"
    },
    "valueQuantity": {
        "value": 7.2,
        "unit": "%",
        "system": "http://unitsofmeasure.org",
        "code": "%"
    },
    "interpretation": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": "H",
                    "display": "High"
                }
            ]
        }
    ]
}
```

## 🎯 系统集成建议

### 1. 数据交换接口设计

**RESTful API端点**:
```
GET /api/lab-tests/standards         # 获取标准化配置
POST /api/lab-tests/convert         # 单位转换服务
POST /api/lab-tests/validate       # 数据验证服务
GET /api/lab-tests/reference-ranges # 获取参考范围
POST /api/lab-tests/fhir-transform  # FHIR格式转换
```

### 2. 数据库标准化表设计

```sql
-- LOINC编码映射表
CREATE TABLE lab_test_loinc_mapping (
    id UUID PRIMARY KEY,
    crf_field_name VARCHAR(100) NOT NULL,
    test_name_cn VARCHAR(100) NOT NULL,
    test_name_en VARCHAR(100) NOT NULL,
    loinc_code VARCHAR(20) NOT NULL,
    standard_unit VARCHAR(20) NOT NULL,
    alternative_units JSON,
    conversion_factors JSON,
    reference_ranges JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 单位转换规则表
CREATE TABLE unit_conversion_rules (
    id UUID PRIMARY KEY,
    from_unit VARCHAR(20) NOT NULL,
    to_unit VARCHAR(20) NOT NULL,
    conversion_factor DECIMAL(10,6) NOT NULL,
    conversion_formula TEXT,
    test_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 参考范围表
CREATE TABLE reference_ranges (
    id UUID PRIMARY KEY,
    loinc_code VARCHAR(20) NOT NULL,
    gender VARCHAR(10),
    age_min INT,
    age_max INT,
    range_low DECIMAL(10,3),
    range_high DECIMAL(10,3),
    unit VARCHAR(20) NOT NULL,
    population VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. 验证与质控机制

**数据完整性检查**:
- LOINC代码有效性验证
- 单位合理性检查
- 数值范围合理性验证
- 必填字段完整性检查

**异常值检测**:
- 基于参考范围的异常值标识
- 危急值报警机制
- 趋势异常检测算法

## 📈 实施roadmap

### Phase 1: 核心编码映射 (2周)
- [ ] 完成9大检查模块LOINC编码映射
- [ ] 建立单位转换算法库
- [ ] 创建参考范围数据库

### Phase 2: 系统接口开发 (3周)
- [ ] 开发数据转换API服务
- [ ] 实现FHIR格式输出接口
- [ ] 创建数据验证中间件

### Phase 3: 集成测试 (2周)
- [ ] 与现有HIS/LIS系统对接测试
- [ ] 数据准确性验证
- [ ] 性能压力测试

### Phase 4: 部署与培训 (1周)
- [ ] 生产环境部署
- [ ] 用户培训和文档完善
- [ ] 监控与反馈机制建立

---

**标准化效果评估指标**:
- 数据一致性: >99%
- 转换准确性: >99.9%
- 系统响应时间: <200ms
- 跨机构数据交换成功率: >98%