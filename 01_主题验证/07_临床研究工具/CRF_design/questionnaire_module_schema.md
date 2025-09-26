# 临床科研数据模块 - 问卷引擎架构设计 (V2)

## 1. 概述

本文档为临床科研数据模块中的"问卷引擎"提供第二版架构设计。此版设计采纳了**混合模型**，并借鉴了业界标准的 **HL7 FHIR Questionnaire** 规范，旨在实现极致的灵活性、可扩展性与数据互操作性。

- **混合模型核心思想**:
    1.  **专用问卷引擎**: 用于完整地、高保真地捕获和存储结构化问卷的原始定义与回答数据，包括复杂的跳转逻辑和多层嵌套问题。
    2.  **观测模型聚合**: 问卷完成后，系统自动计算出核心的、可用于快速分析的**摘要指标**（如总分），并将其作为标准`Observation`存入`gplus.observations`表，以便于和实验室检查等数据进行统一查询分析。

- **FHIR 标准借鉴**:
    - 我们不完全实现FHIR，但借鉴其核心思想：将问卷的定义和回答实例都视为一个独立的**文档 (Document)**，使用`JSONB`进行存储。这使得问卷的结构、校验、逻辑可以完全由元数据驱动，无需修改后端表结构。

本设计是[核心数据库架构](./database_schema.md)的扩展模块。

## 2. 核心设计原则

- **定义与实例分离**: 严格区分"问卷的定义"（模板文档）和"问卷的回答实例"（数据文档）。
- **元数据驱动 (Schema-on-Read)**: 问卷的结构、问题、校验规则和跳转逻辑全部作为元数据存储在`JSONB`文档中。后端负责存储和检索，前端/应用层负责解析、渲染和校验。
- **数据双向流动**: 原始答案流入问卷引擎，关键结果流出到观测模型。
- **原子化与可复用**: 每个问卷定义都是一个独立的、可版本化的实体，可以被多个科研项目复用。

## 3. 整体数据模型

```mermaid
erDiagram
    QUESTIONNAIRE_DEFINITION {
        uuid id PK
        string name
        string version UK
        jsonb definition_doc "FHIR-inspired Questionnaire"
    }
    QUESTIONNAIRE_RESPONSE {
        uuid id PK
        uuid visit_id FK "Links to clinical_visit"
        uuid questionnaire_def_id FK
        jsonb response_doc "FHIR-inspired QuestionnaireResponse"
        string status
        datetime completed_at
    }
    CLINICAL_VISIT {
        uuid id PK
    }
    OBSERVATIONS {
        uuid id PK
        uuid visit_id FK
        string observation_code
        numeric value_numeric
    }
    RESEARCH_PROJECT {
        int id PK
    }
    PROJECT_QUESTIONNAIRE_LINK {
        int project_id FK
        uuid questionnaire_def_id FK
    }

    QUESTIONNAIRE_DEFINITION ||--|{ QUESTIONNAIRE_RESPONSE : "is instance of"
    CLINICAL_VISIT ||--|{ QUESTIONNAIRE_RESPONSE : "has"
    QUESTIONNAIRE_RESPONSE }|..|> OBSERVATIONS : "generates"
    RESEARCH_PROJECT ||--|{ PROJECT_QUESTIONNAIRE_LINK : "uses"
    QUESTIONNAIRE_DEFINITION ||--|{ PROJECT_QUESTIONNAIRE_LINK : "is used by"
```

## 4. 表结构详解

### 4.1. 问卷定义 (The Template)

#### `gplus.questionnaire_definition`
存储问卷的元信息和完整的结构定义。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `name` | `string` | 问卷业务名称, 如 "焦虑抑郁量表 (GAD-7 & PHQ-9)" |
| `type` | `string` | 区分类型: `SCALE` (量表) 或 `QUESTIONNAIRE` (普通问卷) |
| `version`| `string` | 版本号, 如 "1.1"。与`name`共同构成业务唯一键。 |
| `description`| `text` | 问卷的详细描述和用途说明。 |
| `definition_doc`| `jsonb` | **核心字段**: 存储问卷完整定义的JSON文档，其结构借鉴FHIR。 |
| `result_mappings`|`jsonb` | **核心字段**: 定义如何从回答文档中计算摘要指标。 |

---
**`definition_doc` 示例 (简化版 FHIR 风格):**
```json
{
  "resourceType": "Questionnaire",
  "id": "gad-7",
  "title": "Generalized Anxiety Disorder 7-item (GAD-7) scale",
  "status": "active",
  "item": [
    {
      "linkId": "1", // 题目唯一标识
      "text": "在过去的两周里，您是否经常感到紧张、焦虑或烦躁？",
      "type": "choice", // 题目类型
      "options": [ // 选项
        {"value": 0, "display": "完全没有"},
        {"value": 1, "display": "好几天"},
        {"value": 2, "display": "超过一半时间"},
        {"value": 3, "display": "几乎每天"}
      ]
    },
    {
      "linkId": "2",
      "text": "在过去的两周里，您是否经常无法停止或控制担忧？",
      "type": "choice",
      "options": [
        {"value": 0, "display": "完全没有"},
        {"value": 1, "display": "好几天"},
        {"value": 2, "display": "超过一半时间"},
        {"value": 3, "display": "几乎每天"}
      ]
    }
    // ... more items
  ]
}
```

---
**`result_mappings` 示例:**
```json
{
  "scores": [
    {
      "observation_code": "gad7_total_score", // 目标 observation_code
      "calculation": "sum", // 计算方法
      "source_linkIds": ["1", "2", "3", "4", "5", "6", "7"] // 来源题目
    }
  ]
}
```
---

### 4.2. 问卷实例 (The Data)

#### `gplus.questionnaire_response`
存储一次具体的、完整的问卷填写记录。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | `uuid` | 主键 |
| `visit_id` | `uuid` | **关键外键**，关联到`clinical_visit`，将其锚定到具体的访视事件。 |
| `questionnaire_def_id`| `uuid` | 记录填写的是哪份问卷模板。 |
| `response_doc` | `jsonb` | **核心字段**: 存储用户提交的完整答案文档。 |
| `status` | `string` | 状态, 如 `in-progress`, `completed`, `amended` |
| `started_at` | `datetime`| 开始填写时间 |
| `completed_at` | `datetime`| 完成填写时间 |

---
**`response_doc` 示例 (简化版 FHIR 风格):**
```json
{
  "resourceType": "QuestionnaireResponse",
  "questionnaire": "urn:uuid:...", // 指向 definition 的 ID
  "status": "completed",
  "subject": {"reference": "Patient/123"},
  "authored": "2024-07-30T10:00:00Z",
  "item": [
    {
      "linkId": "1",
      "answer": [{"valueInteger": 2}] // 答案
    },
    {
      "linkId": "2",
      "answer": [{"valueInteger": 1}]
    }
    // ... more answers
  ]
}
```
---

### 4.3. 关联关系

#### `gplus.project_questionnaire_link`
实现科研项目与问卷模板的"多对多"关系，允许项目从"问卷库"中选用问卷。
| 列名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `project_id` | `integer` | 关联到`research_project` |
| `questionnaire_def_id`| `uuid` | 关联到`questionnaire_definition` |

## 5. 数据流：混合模型的实际运作

1.  **选择与渲染**: 用户在某次临床访视中，选择填写"GAD-7"问卷。前端请求`questionnaire_definition`表，获取`definition_doc`，并根据该JSON动态渲染出问卷界面。
2.  **提交与存储**: 用户完成填写后，前端将答案打包成一个`response_doc` JSON对象，并创建一条新的`questionnaire_response`记录，将其与`visit_id`关联。
3.  **计算与聚合 (核心)**:
    - `questionnaire_response`记录的创建（或状态变为`completed`）触发一个**后端服务**（可以通过数据库触发器、消息队列或批处理任务实现）。
    - 该服务加载对应的`questionnaire_definition`中的`result_mappings`。
    - 服务根据`result_mappings`的规则，解析`response_doc`中的原始答案，计算出`gad7_total_score`。
    - 服务在`gplus.observations`表中创建一条新记录: `{ visit_id: [current_visit_id], observation_code: 'gad7_total_score', value_numeric: [calculated_score] }`。
4.  **查询与分析**:
    - **深度分析**: 研究人员需要分析"第二题回答为3分的患者，其预后如何"时，可以查询`questionnaire_response`表，解析`response_doc`JSON。
    - **快速分析**: 研究人员需要分析"所有患者GAD-7总分的趋势"时，可以直接查询`gplus.observations`表，如同查询血糖、血压一样，高效、简单。

通过此设计，我们既获得了处理复杂问卷的灵活性，又保留了对关键结果进行高性能查询的能力，实现了两全其美。 