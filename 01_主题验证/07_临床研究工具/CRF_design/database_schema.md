# 临床科研数据模块 - 数据库架构设计

## 1. 概述

本文档旨在为糖尿病管理系统的临床科研数据模块设计一个灵活、可扩展且支持长期随访的数据库架构。设计需求源于"天津宋院CRF表"及未来支持多个不同科研项目的业务目标。

核心挑战在于，系统需要能够处理多个科研项目（每个项目可能有不同的CRF），并对同一患者进行多时间点（纵向）的数据采集。因此，设计的核心是**灵活性**、**可扩展性**与**高性能查询**的平衡。

## 2. 核心设计原则

- **项目为中心，访视为驱动**: 所有科研数据都归属于一个`科研项目(ResearchProject)`，并通过`临床访视(ClinicalVisit)`这个核心事件进行串联。
- **拥抱"观测"模型**: 摒弃为每类数据创建僵硬宽表的传统模式，采用统一的、长表形式的`观测(Observation)`模型来存储绝大多数测量类数据（如体格检查、实验室指标），以获得极致的灵活性。
- **事实与档案分离**:
    - **`clinical_visit` (事实表)**: 作为事件驱动的核心，记录每一次访视的原始数据，是数据的最终"事实来源"。
    - **`project_enrollment` (档案表)**: 作为患者参与项目的聚合档案，用于高性能地查询项目队列及管理患者在项目中的生命周期。此表由系统根据`clinical_visit`的事件自动维护。
- **混合数据建模**: 针对不同形态的数据采用最适合的模型。
- **遵守现有架构**: 严格遵循现有的`public`（基础库）和`gplus`（业务库）双Schema分离策略。所有新增的科研模块相关表均创建于`gplus` Schema。

## 3. 整体数据模型

```mermaid
erDiagram
    RESEARCH_PROJECT {
        int id PK "管理实体，保留int ID"
        string name
        string description
        int organization_id
        string status
        date start_date
        date end_date
    }
    PROJECT_ENROLLMENT {
        uuid id PK "项目档案，使用UUID"
        int project_id FK
        int patient_id FK
        date enrollment_date
        string status
    }
    CLINICAL_VISIT {
        uuid id PK "核心事件，使用UUID"
        int patient_id FK
        int project_id FK
        uuid visit_template_id FK
        datetime visit_date
    }
    VISIT_TEMPLATE {
        uuid id PK "访视模板"
        int project_id FK
        string name
        string code
        int day_offset
    }
    PATIENTS {
        int id PK "来自 public schema"
        string name
    }
    OBSERVATION {
        uuid id PK
        uuid visit_id FK
        string observation_code FK
        float value_numeric
        string value_text
        string unit
    }
    OBSERVATION_DEFINITION {
        string code PK
        string name
        string category
        string value_type
    }
    MEDICAL_HISTORY {
        uuid id PK
        int patient_id FK
        string condition
        int diagnosis_year
    }
    FAMILY_HISTORY {
        uuid id PK
        int patient_id FK
        string relationship
        string diabetes_type
    }
    MEDICATION_LOG {
        uuid id PK
        uuid visit_id FK
        int drug_definition_id FK "FK to drug_definitions"
        string frequency
        "numeric[]" dosages
    }
    DRUG_DEFINITIONS {
        int id PK
        string drug_code UK
        string generic_name
        string specification
    }

    RESEARCH_PROJECT ||--|{ PROJECT_ENROLLMENT : "manages"
    RESEARCH_PROJECT ||--|{ CLINICAL_VISIT : "has"
    RESEARCH_PROJECT ||--|{ VISIT_TEMPLATE : "defines"
    VISIT_TEMPLATE ||--|{ CLINICAL_VISIT : "is instance of"
    "Patients" ||--|{ PROJECT_ENROLLMENT : "is enrolled in"
    "Patients" ||--|{ CLINICAL_VISIT : "has"
    "Patients" ||--|{ MEDICAL_HISTORY : "has"
    "Patients" ||--|{ FAMILY_HISTORY : "has"
    CLINICAL_VISIT ||--|{ OBSERVATION : "has"
    CLINICAL_VISIT ||--|{ MEDICATION_LOG : "has"
    OBSERVATION_DEFINITION ||--|{ OBSERVATION : "defines"
    DRUG_DEFINITIONS ||--|{ MEDICATION_LOG : "defines"
```

## 4. 表结构详解

### 4.1. 顶层管理实体

#### `gplus.research_project`
管理所有科研项目的基础信息，并包含项目生命周期管理字段。**此表由现有`project`表改造而来，为保证兼容性，主键保留为`integer`类型。**
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `integer` | 主键 (自增) |
| `name` | `string` | 项目名称 |
| `description`| `text` | 项目详细描述 |
| `organization_id`| `integer` | 所属机构ID, 关联`public."Organizations"` |
| `status` | `string` | 项目状态 (如: 'DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED') |
| `start_date`| `date` | 项目开始日期 |
| `end_date` | `date` | 项目结束日期 |
| `metadata` | `jsonb` | 其他元数据 |

### 4.2. 核心枢纽与档案

#### `gplus.project_enrollment`
患者项目档案表，用于高性能查询项目队列和管理患者在项目中的状态。**此表是对原`project_patient`表的升级，由系统自动维护。**
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `project_id` | `integer` | 关联到`research_project`表 |
| `patient_id` | `integer` | 关联到`public."Patients"`表 |
| `organization_id`|`integer`| 数据所属机构ID |
| `enrollment_date`| `date` | 入组日期（首次访视日期） |
| `status` | `string` | 在项目中的状态 (如: 'ACTIVE', 'WITHDRAWN') |
| `added_by_user_id`|`integer`| 操作人ID |

#### `gplus.visit_templates`
预定义的访视计划模板，用于规范化访视事件。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `project_id` | `integer` | 关联到 `research_project` |
| `name` | `string` | 访视显示名称, 如 "3月随访" |
| `code` | `string` | 访视短代码, 如 "M3", 项目内唯一 |
| `order`| `integer` | 用于排序，定义访视的先后顺序 |
| `day_offset`| `integer` | 相对入组日期的天数偏移，如 90 |
| `day_window`| `integer` | 时间窗，如 7，表示偏移前后7天均有效 |

#### `gplus.clinical_visit`
记录患者在某项目中的一次访视事件，是连接所有动态数据的枢纽。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `patient_id` | `integer` | 关联到`public."Patients"`表 |
| `project_id` | `integer` | 关联到`research_project`表 |
| `visit_template_id` | `uuid` | 关联到`visit_templates`表，取代了自由文本的名称 |
| `visit_date` | `datetime`| 访视发生的日期 |
| `medical_record_number` | `string` | 本次访视的病案号 (主要针对住院)，允许为空 |
| `custom_data`| `jsonb` | **补充字段**：用于存储无法标准化的项目特有数据 |

### 4.3. 核心数据字典与观测模型

#### `gplus.observation_definitions` (数据字典)
定义了系统中所有可用的观测项，是实现标准化和灵活性的基石。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `code` | `string` | 观测项唯一编码 (主键)，如 `hba1c` |
| `name` | `string` | 显示名称，如 `糖化血红蛋白` |
| `short_name` | `string` | 简称/别名，如 `HbA1c` |
| `category` | `string` | 分类，如 `实验室检查`, `体格检查` |
| `value_type`| `string` | 值类型 (`numeric`, `text`)，用于程序判断 |
| `canonical_unit_code` | `string` | 标准单位的编码, 关联到`unit_definitions` |
| `is_unit_locked` | `boolean` | 单位是否固定 (如问卷得分，无单位转换) |

#### `gplus.drug_definitions` (药物字典)
定义了系统中所有可用的药物成分，是实现用药标准化的基石。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `integer` | **主键**: 内部自增ID，无业务含义。 |
| `drug_code` | `string` | **业务编码**: 例如 `METFORMIN_0.5G`，由通用名和规格生成，保证唯一。 |
| `generic_name`| `string` | **药品通用名**: 如 "盐酸二甲双胍"。 |
| `specification`| `string` | **规格**: 如 "0.5g"。与`generic_name`一起构成业务上的唯一标识。 |
| `unit` | `string` | **标准剂量单位**, 如 "片"。对于同一药物通常固定。 |
| `form` | `string` | 剂型, 如 "片剂", "注射液"。 |
| `method` | `string` | **标准服用方式**, 如 "PO", "iv"。对于同一药物通常固定。 |
| `series` | `string` | 药物分类, 如 "口服药"。 |
| `metadata` | `jsonb` | **推荐配置**: 包含推荐频率、推荐剂量等。如 `{"recommended_frequency": "TID", "recommended_dosages": [500, 500, 500]}` |

#### `gplus.observations`
存储每一次具体的观测数据。**所有数值型数据在写入时，必须被转换为其定义的标准单位 (canonical_unit) 进行存储。**
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `visit_id` | `uuid` | 关联到`clinical_visit`表 |
| `observation_code`| `string` | 关联到`observation_definitions`表 |
| `value_numeric`| `numeric(15, 5)` | 数值型结果 (按标准单位存储) |
| `value_text` | `string` | 文本型结果 |
| `unit` | `string` | **冗余字段**: 存储本次观测的标准单位，即`canonical_unit` |

### 4.4. 单位与偏好设置

#### `gplus.unit_definitions`
定义了系统中所有可用的单位及其换算规则，由后端`UnitConversionService`集中管理和使用。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `code` | `string` | 单位的唯一编码 (主键), 如 `cm`, `kg` |
| `name` | `string` | 显示名称, 如 "厘米", "千克" |
| `type` | `string` | 单位类型, 如 `length`, `weight`, `concentration` |
| `to_canonical_factor` | `float` | 乘以该系数可得到同类型下的标准单位值 |
| `is_canonical` | `boolean` | 标记该单位是否是其类型下的标准单位 |

#### `gplus.project_unit_preferences`
允许每个科研项目自定义其对某个观测项的显示单位偏好。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `project_id` | `integer` | 关联到 `research_project` |
| `observation_code` | `string` | 关联到 `observation_definitions` |
| `preferred_unit_code` | `string` | 关联到 `unit_definitions`, 指定偏好显示单位 |

### 4.5. 专用数据表

#### 对`gplus.patient`的扩展
对于患者的半永久性信息，直接扩展`gplus.patient`业务表。
- `occupation` (职业)
- `education_level` (最高文化程度)

#### `gplus.medical_history` & `gplus.family_history`
这些是患者自身的历史背景，与具体访视无关，因此直接关联患者。
- **medical_history**: `id`, `patient_id` (关联`public."Patients"`), `condition` (病症), `diagnosis_year` (诊断年份)...
- **family_history**: `id`, `patient_id` (关联`public."Patients"`), `relationship` (亲属关系), `diabetes_type` (糖尿病类型)...

#### `gplus.medication_log`
用药方案记录表，关联到`clinical_visit`。此表用于记录患者在访视期间的常规用药方案，而非单次用药事件。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `visit_id` | `uuid` | 关联到 `clinical_visit` 表 |
| `drug_definition_id`| `integer`| **外键**: 关联到 `gplus.drug_definitions.id`。 |
| `frequency` | `string` | **实际服用频率** (如: 'TID', 'BID')，可与药物字典中的推荐值不同 |
| `dosages`   | `numeric[]` | **核心字段**: 实际每次用量的数组。例如: TID (每日三次) -> `[500, 500, 500]` |
| `start_date`| `date` | 开始服用此药物的日期 (可选) |
| `is_ongoing`| `boolean`| 是否仍在持续用药, 默认为`true` |
| `remarks`   | `text`   | 备注信息 |

## 5. 应用示例

**场景**: 患者"张三"参与"天津宋院糖尿病研究"项目，在"入组访视"时采集CRF数据。

1.  **访视记录**: 在`clinical_visit`表中创建一条记录，关联"张三"的`patient_id`和项目的`project_id`。
2.  **自动创建档案**: 系统检测到这是"张三"在该项目的首次访视，于是在`project_enrollment`表中自动创建一条记录，`{ project_id: '...', patient_id: '...', enrollment_date: '...' }`。
3.  **体格检查**:
    - 在`observations`表中插入身高记录：`{ visit_id: '...', observation_code: 'height', value_numeric: 175, unit: 'cm' }`
    - 在`observations`表中插入体重记录：`{ visit_id: '...', observation_code: 'weight', value_numeric: 80, unit: 'kg' }`
4.  **实验室检查**:
    - 在`observations`表中插入HbA1c记录：`{ visit_id: '...', observation_code: 'hba1c', value_numeric: 8.1, unit: '%' }`
    - ...插入其他所有化验指标的记录。
5.  **查询项目成员**: 当需要查看项目所有参与者时，直接高效地查询`project_enrollment`表即可。

通过这种方式，所有数据都被清晰、灵活且可查询地存储起来，完美地满足了科研需求。