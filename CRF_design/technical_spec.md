# 临床科研数据模块 - 技术规格说明书

## 1. 概述

本技术规格说明书 (Technical Specification) 旨在为"天津宋院CRF表0615"的数字化实现提供详细的数据映射方案。本文档基于已定义的[数据库架构](./database_schema.md)和[需求文档](./requirements.md)，为开发人员提供精确的实现蓝图。

## 2. CRF字段数据映射

### 2.1. 一、患者信息

此部分信息多为患者的半永久性个人资料。

| CRF字段 | 目标表 | 目标列/Code | 数据类型/值 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| 1. 身份证号 | `public.Patients` | `identity` | `string` | 需加密存储 |
| 2. 姓名 | `public.Patients` | `name` | `string` | 现有字段 |
| 3. 性别 | `public.Patients` | `sex` | `enum` | 现有字段 |
| 4. 出生年月日 | `public.Patients` | `birthday` | `date` | 现有字段 |
| 5. 年龄 | `public.Patients` | `years` | `integer` | 自动计算，允许覆盖 |
| 6. 就诊时间 | `gplus.clinical_visit` | `visit_date` | `datetime` | 访视核心字段 |
| 7. 病案号 | `gplus.patient` | `medical_record_number` | `string` | 扩展字段 |
| 8. 就诊科室 | `gplus.clinical_visit` | `department_id` | `integer` | 关联到`department`表 |
| 9. 本人联系方式 | `public.Patients` | `phone` | `jsonb` | 现有字段 |
| 10. 职业 | `gplus.patient` | `occupation` | `enum` | 扩展字段 |
| 11. 婚姻状况 | `public.Patients` | `marriage` | `integer` | 现有字段, 使用系统中已定义的代码 |
| 12. 最高文化程度 | `gplus.patient` | `education_level` | `enum` | 扩展字段 |

### 2.2. 二、既往史

存储于专用的历史信息表中，与患者直接关联。

| CRF字段 | 目标表 | 目标列/Code | 数据类型/值 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| 2. 高血压 | `gplus.medical_history` | `condition: 'hypertension'` | `string` | 一条记录代表一种病史 |
| 3. 冠心病 | `gplus.medical_history` | `condition: 'coronary_heart_disease'`| `string` | |
| 4. 血脂异常 | `gplus.medical_history` | `condition: 'dyslipidemia'` | `string` | |
| 5. 脑卒中 | `gplus.medical_history` | `condition: 'stroke'` | `string` | |
| ...其他病史 | `gplus.medical_history` | `condition: '...'` | `string` | |
| 诊断年份 | `gplus.medical_history` | `diagnosis_year` | `integer` | |
| 是否持续/用药 | `gplus.medical_history` | `metadata` | `jsonb` | `{ "ongoing": true, "on_medication": true, "medication_details": "..." }` |

### 2.3. 三、家族史

存储于专用的历史信息表中，与患者直接关联，支持多条记录。

| CRF字段 | 目标表 | 目标列/Code | 数据类型/值 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| 与本人关系 | `gplus.family_history`| `relationship` | `enum` | |
| 糖尿病类型 | `gplus.family_history`| `diabetes_type`| `enum` | |
| 是否出现肾病 | `gplus.family_history`| `has_nephropathy`| `boolean`| |
| 备注 | `gplus.family_history`| `remarks` | `text` | |

### 2.4. 四、糖尿病用药史

记录访视期间的患者常规用药方案。每条记录关联到`clinical_visit`和`drug_definitions`。

| CRF字段 | 目标表 | 目标列/Code | 数据类型/值 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| 药物 | `gplus.medication_log` | `drug_definition_id` | `integer` | 关联到药品字典的主键 |
| 开始日期 | `gplus.medication_log` | `start_date` | `date` | (可选) |
| 用药频率 | `gplus.medication_log` | `frequency` | `string` | 实际服用频率，如 'TID', 'BID'，可与推荐值不同 |
| 各次剂量 | `gplus.medication_log` | `dosages` | `numeric[]` | 数组存储每次剂量, 如 `[500, 500, 500]` |
| 是否持续 | `gplus.medication_log` | `is_ongoing`| `boolean`| |

**说明**: 服用方式(`method`)和剂量单位(`unit`)现从`drug_definitions`表获取，无需在用药记录中重复存储。

### 2.5. 五、体格检查

全部采用"观测"模型进行存储。

| CRF字段 | 目标表 | `observation_code` | `value_type` |
| :--- | :--- | :--- | :--- |
| 1. 身高 | `gplus.observations` | `height` | `numeric` |
| 2. 体重 | `gplus.observations` | `weight` | `numeric` |
| 3. 血压(收缩压)|`gplus.observations` | `systolic_bp` | `numeric` |
| 3. 血压(舒张压)|`gplus.observations` | `diastolic_bp` | `numeric` |
| 4. 心率 | `gplus.observations` | `heart_rate` | `numeric` |
| 5. 腰围 | `gplus.observations` | `waist_circumference`| `numeric` |
| 6. 臀围 | `gplus.observations` | `hip_circumference` | `numeric` |

### 2.6. 六、实验室检查

全部采用"观测"模型进行存储。

| CRF字段 | 目标表 | `observation_code` | `value_type` |
| :--- | :--- | :--- | :--- |
| 1. 糖化血红蛋白 | `gplus.observations` | `hba1c` | `numeric` |
| 2. 空腹血糖 | `gplus.observations` | `fpg` | `numeric` |
| 3. 餐后血糖(0.5h)| `gplus.observations` | `ppg_0_5h` | `numeric` |
| 4. 餐后血糖(1h) | `gplus.observations` | `ppg_1h` | `numeric` |
| 5. 餐后血糖(2h) | `gplus.observations` | `ppg_2h` | `numeric` |
| 6. 餐后血糖(3h) | `gplus.observations` | `ppg_3h` | `numeric` |
| 7. 胰岛细胞抗体 | `gplus.observations` | `ica_status` | `text` |
| 8. ALT | `gplus.observations` | `alt` | `numeric` |
| 8. AST | `gplus.observations` | `ast` | `numeric` |
| 8. 总胆红素 | `gplus.observations` | `total_bilirubin` | `numeric` |
| 9. 肌酐 | `gplus.observations` | `creatinine` | `numeric` |
| 9. 尿素氮 | `gplus.observations` | `bun` | `numeric` |
| 10. 总胆固醇 | `gplus.observations` | `total_cholesterol` | `numeric` |
| 10. 甘油三酯 | `gplus.observations` | `triglycerides` | `numeric` |
| 10. HDL-C | `gplus.observations` | `hdl_c` | `numeric` |
| 10. LDL-C | `gplus.observations` | `ldl_c` | `numeric` |

### 2.7. 七、辅助检查 & 八、动态结果

这些多为问卷、量表或不常用的检查，同样适合用"观测"模型。

| CRF字段 | 目标表 | `observation_code` | `value_type` | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| 1. 踝臂指数(ABI)| `gplus.observations` | `abi_value` | `numeric` | |
| 2. 体成分分析 | `gplus.observations` | `body_composition_notes` | `text` | 存储备注信息 |
| 5. 焦虑抑郁量表| `gplus.observations` | `anxiety_depression_score` | `numeric` | |
| 8.1. 饮食问卷 | `gplus.observations` | `diet_questionnaire_result` | `text` | 或`jsonb`，取决于复杂度 |
| 8.2. 认知问卷 | `gplus.observations` | `cognitive_questionnaire_result`|`text`| |

## 3. 新增`observation_definitions`清单

为支持以上映射，`gplus.observation_definitions`表中需要预置以下记录。

- **体格检查类**: `height`, `weight`, `systolic_bp`, `diastolic_bp`, `heart_rate`, `waist_circumference`, `hip_circumference`
- **实验室检查类**: `hba1c`, `fpg`, `ppg_0_5h`, `ppg_1h`, `ppg_2h`, `ppg_3h`, `ica_status`, `alt`, `ast`, `total_bilirubin`, `creatinine`, `bun`, `total_cholesterol`, `triglycerides`, `hdl_c`, `ldl_c`
- **其他检查类**: `abi_value`, `body_composition_notes`, `anxiety_depression_score`, `diet_questionnaire_result`, ...

这份清单将作为初始化数据的依据。 