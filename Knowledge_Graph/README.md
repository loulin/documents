# 综合内分泌疾病知识图谱系统

## 项目概述

**综合内分泌代谢疾病知识图谱系统（包含风湿免疫疾病扩展模块）** - 基于美国权威医学指南构建的多学科医学知识图谱，专注内分泌代谢疾病诊疗，并扩展支持自身免疫性内分泌疾病和相关风湿免疫疾病的临床决策支持。

### 🎯 知识图谱定位与构成

| 疾病系统 | 实体占比 | 主要疾病 | 地位 |
|---------|---------|----------|------|
| **内分泌系统** | **62%** | 糖尿病、甲状腺、肾上腺、垂体、性腺疾病 | 🏗️ **核心模块** |
| **风湿免疫系统** | **20%** | 自身免疫性内分泌疾病、系统性风湿病、APS | 🆕 **扩展模块** |
| **代谢性疾病** | **10%** | 高尿酸血症、痛风、代谢综合征、血脂异常 | ⚗️ **代谢模块** |
| **心血管系统** | **5%** | 内分泌相关心血管疾病 | 📈 **关联模块** |
| **神经系统** | **3%** | 内分泌相关神经病变 | 🧠 **并发症模块** |

### 核心特性

- **🏥 多疾病系统整合**: 涵盖内分泌疾病、风湿免疫疾病、代谢性疾病、心血管疾病、脑血管疾病、神经病变
- **🦠 风湿免疫疾病支持**: 自身免疫性内分泌疾病、系统性风湿病、多腺体自身免疫综合征
- **⚗️ 代谢疾病支持**: 高尿酸血症、痛风、尿酸代谢异常与内分泌疾病关联
- **🤖 AI 智能诊断**: 基于症状、检验、影像的多维度诊断推理引擎  
- **💊 个性化治疗**: 考虑年龄、共病、禁忌症的精准治疗方案推荐
- **🔗 共病模式识别**: 疾病间关联分析和内分泌-风湿免疫共病管理
- **🧬 遗传风险评估**: HLA分型、家族史分析、多腺体综合征风险预测
- **📚 RAG 问答系统**: 检索增强生成的专业医学问答
- **📝 结构化解析**: 临床文本的医学实体识别和信息提取
- **🔬 研究支持**: 临床研究队列识别和统计分析建议

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Web/Mobile Frontend                     │
├─────────────────────────────────────────────────────────────┤
│                     FastAPI Gateway                        │
├─────────┬─────────────┬─────────────┬─────────────────────┤
│   AI    │  Knowledge  │    NLP      │     Research        │
│ Engine  │   Graph     │  Service    │     Support         │
├─────────┼─────────────┼─────────────┼─────────────────────┤
│  Neo4j  │    Redis    │  MongoDB    │   Elasticsearch     │
│ (Graph) │  (Cache)    │ (Document)  │   (Full-text)       │
└─────────┴─────────────┴─────────────┴─────────────────────┘
```

## 医学指南来源

### 权威指南支持

- **ADA Standards of Medical Care in Diabetes 2025**: 糖尿病诊疗标准
- **American Thyroid Association Guidelines 2025**: 甲状腺疾病管理
- **Endocrine Society Guidelines 2024**: 内分泌疾病诊疗共识
- **ACR/EULAR Rheumatoid Arthritis Guidelines 2024**: 类风湿关节炎管理指南
- **ACR Systemic Lupus Erythematosus Guidelines 2024**: 系统性红斑狼疮诊疗指南
- **EULAR Sjögren's Syndrome Guidelines 2024**: 干燥综合征管理共识
- **International APS Consensus Statement 2024**: 多腺体自身免疫综合征专家共识
- **AHA/ACC Hypertension Guidelines 2025**: 高血压防治指南
- **ACC/AHA Dyslipidemia Guidelines 2025**: 血脂异常管理
- **AHA/ACC/HFSA Heart Failure Guidelines 2024**: 心力衰竭管理指南
- **AHA/ACC/HRS Atrial Fibrillation Guidelines 2024**: 房颤管理指南
- **AHA/ASA Stroke Guidelines 2024**: 脑卒中防治指南
- **American Diabetes Association Neuropathy Guidelines 2024**: 糖尿病神经病变指南
- **PCOS Guideline International Evidence-based 2024**: 国际PCOS循证指南
- **ACR Gout Management Guidelines 2024**: 美国风湿病学会痛风管理指南
- **EULAR Gout Recommendations 2024**: 欧洲抗风湿病联盟痛风诊疗建议
- **Chinese Society of Nephrology Hyperuricemia Guidelines 2024**: 中国肾脏病学会高尿酸血症指南

### 知识图谱统计

| 指标 | 数量 |
|------|------|
| 总实体数 | 3,267 |
| 总关系数 | 6,892 |
| 推理规则 | 251 |
| 临床案例 | 158 |
| 共病模式 | 13 |
| API端点 | 13 |

### 疾病模块覆盖

| 疾病系统 | 疾病数量 | 主要疾病 |
|----------|----------|----------|
| 内分泌系统 | 23 | 糖尿病、甲状腺疾病、肾上腺疾病、垂体疾病 |
| 风湿免疫系统 | 9 | 1型糖尿病、桥本甲状腺炎、Addison病、SLE、RA、SS、APS、痛风 |
| 代谢性疾病 | 8 | 高尿酸血症、痛风、高血压、血脂异常、肥胖、代谢综合征 |
| 性腺系统 | 4 | PCOS、男/女性腺功能减退、性早熟 |
| 心血管系统 | 4 | 冠心病、心梗、心衰、房颤 |
| 脑血管系统 | 3 | 缺血性卒中、出血性卒中、TIA |
| 神经系统 | 3 | 糖尿病神经病变、自主神经病变、GBS |

## 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.11+
- 8GB+ RAM (推荐 16GB)
- 20GB+ 存储空间

### 一键部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd comprehensive-endocrine-knowledge-graph

# 2. 设置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY 等

# 3. 启动完整服务
docker-compose --profile full-stack up -d

# 4. 验证服务状态
curl http://localhost:8000/health
```

### 服务端点

| 服务 | 端口 | 描述 |
|------|------|------|
| API Server | 8000 | 主要API服务 |
| Neo4j Browser | 7474 | 图数据库管理 |
| MongoDB | 27017 | 文档数据库 |
| Redis | 6379 | 缓存服务 |
| Kibana | 5601 | 数据可视化 |
| Grafana | 3000 | 监控面板 |

## API 使用指南

### 认证方式

```bash
# 获取访问令牌 (如果启用认证)
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### 核心API端点

#### 1. 智能诊断

```bash
curl -X POST "http://localhost:8000/api/v1/diagnose" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "patient_id": "P001",
      "age": 45,
      "gender": "女",
      "medical_history": ["高血压"],
      "medications": ["氨氯地平"]
    },
    "symptoms": {
      "symptoms": ["心悸", "多汗", "体重下降"],
      "duration": "3个月",
      "severity": "中度"
    },
    "lab_results": [
      {
        "test_name": "TSH",
        "value": 0.05,
        "unit": "mIU/L",
        "abnormal": true
      },
      {
        "test_name": "FT4", 
        "value": 35.2,
        "unit": "pmol/L",
        "abnormal": true
      }
    ]
  }'
```

**响应示例:**

```json
{
  "primary_diagnosis": "甲状腺功能亢进症",
  "confidence_score": 0.92,
  "supporting_evidence": [
    "症状模式与甲状腺功能亢进症典型表现相符",
    "TSH抑制，FT4升高支持诊断"
  ],
  "differential_diagnoses": [
    {
      "diagnosis": "毒性结节性甲状腺肿", 
      "confidence": 0.15,
      "rationale": "需要甲状腺显像鉴别"
    }
  ],
  "recommended_tests": [
    "TRAb检测",
    "甲状腺超声",
    "心电图"
  ],
  "urgency_level": "常规",
  "icd10_code": "E05"
}
```

#### 2. 风湿免疫疾病风险评估 🆕

```bash
curl -X POST "http://localhost:8000/api/v1/rheumatic/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "patient_id": "P002",
      "age": 28,
      "gender": "女",
      "family_history": ["1型糖尿病", "甲状腺疾病", "类风湿关节炎"]
    },
    "symptoms": [
      "多饮多尿",
      "体重下降",
      "疲乏",
      "关节晨僵",
      "手指关节疼痛"
    ],
    "lab_results": [
      {
        "test_name": "抗GAD抗体",
        "value": "阳性",
        "unit": "",
        "abnormal": true
      },
      {
        "test_name": "RF",
        "value": 45.2,
        "unit": "IU/mL",
        "abnormal": true
      },
      {
        "test_name": "HbA1c",
        "value": 9.2,
        "unit": "%",
        "abnormal": true
      }
    ],
    "family_history": ["母亲1型糖尿病", "姨妈类风湿关节炎"],
    "hla_typing": "DR3/DR4阳性"
  }'
```

**响应示例:**

```json
{
  "patient_id": "P002",
  "assessment_date": "2024-12-19T10:30:00",
  "risk_stratification": {
    "high_risk": {
      "1型糖尿病": 0.85,
      "类风湿关节炎": 0.72
    },
    "moderate_risk": {
      "桥本甲状腺炎": 0.45
    },
    "low_risk": {}
  },
  "genetic_risk_factors": {
    "1型糖尿病": "高风险（DR3/DR4阳性）",
    "多腺体自身免疫综合征II型": "高风险（DR3/DR4阳性）"
  },
  "aps_assessment": {
    "多腺体综合征风险": "需要长期监测（单腺体受累）"
  },
  "family_risk_score": 0.4,
  "screening_recommendations": [
    "建议完善自身抗体谱检查",
    "定期监测相关激素水平",
    "HLA分型检测（已完成）",
    "一级亲属筛查",
    "关节X线检查"
  ],
  "management_recommendations": [
    "建议风湿免疫科和内分泌科联合会诊",
    "制定个体化监测计划",
    "患者和家属疾病教育",
    "定期随访评估疾病进展"
  ],
  "follow_up_interval": "3-6个月",
  "specialist_referral": "风湿免疫科+内分泌科"
}
```

#### 3. 高尿酸血症和痛风诊断 🆕

```bash
curl -X POST "http://localhost:8000/api/v1/diagnose" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "patient_id": "P003",
      "age": 52,
      "gender": "男",
      "medical_history": ["高血压", "2型糖尿病"],
      "medications": ["氢氯噻嗪", "二甲双胍"]
    },
    "symptoms": {
      "symptoms": ["第一跖趾关节疼痛", "红肿热痛", "夜间疼痛", "活动受限"],
      "duration": "2天",
      "severity": "重度"
    },
    "lab_results": [
      {
        "test_name": "血尿酸",
        "value": 485,
        "unit": "μmol/L",
        "abnormal": true
      },
      {
        "test_name": "白细胞",
        "value": 12.5,
        "unit": "x10^9/L",
        "abnormal": true
      },
      {
        "test_name": "CRP",
        "value": 15.2,
        "unit": "mg/L",
        "abnormal": true
      }
    ]
  }'
```

**响应示例:**

```json
{
  "patient_id": "P003",
  "primary_diagnosis": "急性痛风",
  "confidence_score": 0.91,
  "supporting_evidence": [
    "典型的第一跖趾关节急性红肿热痛",
    "血尿酸显著升高(485 μmol/L)",
    "炎症指标升高支持急性发作",
    "男性患者，有代谢性疾病史"
  ],
  "differential_diagnoses": [
    {
      "diagnosis": "化脓性关节炎",
      "probability": 0.15,
      "distinguishing_features": "需要关节液检查鉴别"
    },
    {
      "diagnosis": "慢性痛风急性发作",
      "probability": 0.12,
      "distinguishing_features": "需要评估痛风石和关节损伤"
    }
  ],
  "recommended_tests": [
    "关节液检查（寻找尿酸盐结晶）",
    "关节X线",
    "24小时尿尿酸",
    "肾功能",
    "心电图"
  ],
  "urgency_level": "紧急",
  "icd10_code": "M10.9",
  "metabolic_associations": {
    "diabetes_interaction": "糖尿病与高尿酸血症相互促进",
    "hypertension_management": "利尿剂可能加重高尿酸血症",
    "treatment_considerations": "需要调整降压药物选择"
  }
}
```

#### 4. 治疗方案推荐

```bash
curl -X POST "http://localhost:8000/api/v1/treatment" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "patient_id": "P001",
      "age": 45,
      "gender": "女"
    },
    "diagnoses": ["甲状腺功能亢进症"],
    "comorbidities": ["高血压"],
    "contraindications": []
  }'
```

#### 3. 医学问答

```bash
curl -X POST "http://localhost:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "甲亢患者合并糖尿病应该如何管理？",
    "context": {
      "patient_age": 45,
      "comorbidities": ["糖尿病", "甲状腺功能亢进"]
    }
  }'
```

#### 4. 临床文本解析

```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "患者，女性，45岁，主诉心悸、多汗3个月。既往高血压病史5年。查体：甲状腺II度肿大，质软，未及结节。实验室检查：TSH 0.05 mIU/L，FT4 35.2 pmol/L。",
    "language": "zh"
  }'
```

#### 5. 药物相互作用检查

```bash
curl -X POST "http://localhost:8000/api/v1/drug-interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "medications": ["甲巯咪唑", "华法林", "阿司匹林"],
    "severity_filter": "major"
  }'
```

## 临床应用场景

### 1. 门诊诊疗支持

**场景**: 内分泌科门诊医生接诊疑似甲亢患者

**工作流程**:
1. 输入患者症状和基本信息
2. 系统分析症状模式，提供初步诊断建议  
3. 根据实验室检查结果，确认诊断
4. 生成个性化治疗方案和监测计划
5. 提供患者教育材料

**价值**: 提高诊断准确性，规范化治疗流程

### 2. 共病患者管理

**场景**: 糖尿病合并甲状腺疾病患者的综合管理

**系统支持**:
- 识别疾病间相互影响
- 调整治疗目标和用药方案
- 优化监测频率和指标
- 预警药物相互作用

**价值**: 降低治疗风险，改善患者预后

### 3. 临床教学培训

**场景**: 住院医师内分泌科轮转学习

**功能支持**:
- 典型病例分析和推理过程展示
- 鉴别诊断思路训练  
- 治疗方案选择逻辑解释
- 最新指南知识更新

**价值**: 加速临床技能培养，提高教学效果

### 4. 临床研究支持

**场景**: 开展内分泌疾病队列研究

**研究功能**:
- 自动化患者队列识别
- 基线特征和结局变量提取
- 统计分析方法建议
- 假设生成和文献证据整合

**价值**: 提高研究效率，发现新的临床证据

## 开发指南

### 本地开发环境

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动数据库服务
docker-compose up -d neo4j redis mongodb

# 3. 设置环境变量
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j" 
export NEO4J_PASSWORD="endocrine123"
export OPENAI_API_KEY="your-api-key"

# 4. 启动开发服务器
uvicorn endocrine_knowledge_graph_api:app --reload --port 8000
```

### 代码结构

```
knowledge_graph/
├── comprehensive_endocrine_knowledge_graph.json  # 核心知识图谱
├── endocrine_knowledge_graph_api.py             # API服务器
├── requirements.txt                              # Python依赖
├── docker-compose.yml                           # 容器编排
├── Dockerfile                                   # API容器
├── entrypoint.sh                               # 启动脚本
├── nginx.conf                                  # 反向代理配置
└── README.md                                   # 项目文档
```

## 风湿免疫疾病模块 🆕

### 支持的疾病类型

#### 自身免疫性内分泌疾病
- **RHEUM_001**: 1型糖尿病 - 胰岛β细胞自身免疫破坏
- **RHEUM_002**: Hashimoto甲状腺炎 - 甲状腺自身免疫炎症
- **RHEUM_003**: Addison病 - 肾上腺皮质自身免疫破坏

#### 系统性风湿病
- **RHEUM_004**: 系统性红斑狼疮 - 多系统自身免疫疾病
- **RHEUM_005**: 类风湿关节炎 - 关节滑膜自身免疫炎症
- **RHEUM_006**: 干燥综合征 - 外分泌腺体自身免疫

#### 多腺体自身免疫综合征
- **RHEUM_007**: APS-I型 - AIRE基因缺陷导致的多腺体衰竭
- **RHEUM_008**: APS-II型 - 成人型多腺体自身免疫综合征

### 临床应用场景

#### 场景1：多腺体综合征筛查
```bash
# 患者：25岁女性，1型糖尿病史，现出现甲状腺功能减退
curl -X POST "http://localhost:8000/api/v1/rheumatic/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {"patient_id": "APS001", "age": 25, "gender": "女"},
    "symptoms": ["疲乏", "怕冷", "体重增加", "便秘"],
    "lab_results": [
      {"test_name": "TSH", "value": 15.2, "unit": "mIU/L", "abnormal": true},
      {"test_name": "抗TPO抗体", "value": "阳性", "unit": "", "abnormal": true},
      {"test_name": "抗GAD抗体", "value": "阳性", "unit": "", "abnormal": true}
    ],
    "medical_history": ["1型糖尿病"],
    "hla_typing": "DR3/DR4杂合子"
  }'
```

#### 场景2：SLE内分泌并发症评估
```bash
# 患者：32岁女性，SLE病史，现出现月经紊乱和骨质疏松
curl -X POST "http://localhost:8000/api/v1/diagnose" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {"patient_id": "SLE001", "age": 32, "gender": "女"},
    "symptoms": ["月经不调", "关节痛", "疲乏", "脱发"],
    "lab_results": [
      {"test_name": "ANA", "value": "1:320颗粒型", "unit": "", "abnormal": true},
      {"test_name": "抗ds-DNA", "value": 120, "unit": "IU/mL", "abnormal": true},
      {"test_name": "C3", "value": 0.6, "unit": "g/L", "abnormal": true},
      {"test_name": "雌二醇", "value": 45, "unit": "pg/mL", "abnormal": true}
    ],
    "medical_history": ["系统性红斑狼疮", "长期泼尼松治疗"]
  }'
```

### 最佳实践

#### 1. 风险分层管理
- **高风险**：多种自身抗体阳性 + HLA高风险基因型 + 家族史
- **中风险**：单一抗体阳性或症状典型但实验室阴性
- **低风险**：仅有轻微症状或家族史

#### 2. 监测策略
- **APS高风险患者**：每3-6个月全面激素检查
- **单腺体患者**：年度其他腺体功能筛查
- **家族成员**：定期自身抗体和激素筛查

#### 3. 多学科协作
- **内分泌科**：激素替代治疗和代谢管理
- **风湿免疫科**：免疫抑制治疗和疾病活动监测
- **临床药师**：药物相互作用和剂量调整

### 添加新疾病实体

1. **知识图谱扩展**:
```json
{
  "id": "RHEUM_009",
  "name": "新的风湿免疫疾病",
  "category": "自身免疫性疾病",
  "pathophysiology": {
    "immune_mechanism": "具体的免疫病理机制",
    "autoantibodies": ["相关自身抗体"],
    "genetic_factors": ["遗传易感基因"]
  },
  "clinical_manifestations": {
    "endocrine_features": "内分泌系统受累表现",
    "rheumatic_features": "风湿系统受累表现"
  },
  "diagnosis": {
    "classification_criteria": "诊断分类标准",
    "laboratory_tests": "特异性实验室检查"
  },
  "treatment": {
    "immunosuppressive_therapy": "免疫抑制治疗",
    "hormone_replacement": "激素替代治疗"
  }
}
```

2. **关系定义**:
```json
{
  "id": "REL_NEW_001",
  "type": "comorbidity", 
  "source": "NEW_001",
  "target": "EXISTING_001",
  "description": "关系描述",
  "prevalence": 0.XX
}
```

3. **推理规则**:
```json
{
  "id": "RULE_NEW_001",
  "name": "新疾病诊断规则",
  "condition": {...},
  "conclusion": {...},
  "evidence_grade": "A"
}
```

### API扩展

添加新的API端点:

```python
@app.post("/api/v1/new-endpoint", summary="新功能")
async def new_endpoint(request: NewRequest):
    """新功能的API实现"""
    try:
        result = process_new_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 版本更新记录

### v2.2.0 - 高尿酸血症和痛风模块 (2024-12-19) 🆕

#### 新增功能
- ✅ **高尿酸血症模块**: 完整的高尿酸血症疾病实体(METAB_009)，包含病理生理、诊断、治疗
- ✅ **痛风模块**: 急性和慢性痛风疾病实体(RHEUM_009)，涵盖关节炎和痛风石管理  
- ✅ **内分泌关联分析**: 尿酸代谢与糖尿病、甲状腺疾病、代谢综合征等关联
- ✅ **智能诊断支持**: API增加尿酸代谢疾病症状和实验室检查分析
- ✅ **检查推荐优化**: 9种尿酸相关疾病的个性化检查建议

#### 技术改进  
- 🔧 **症状识别增强**: 新增急性痛风、慢性痛风、痛风性肾病症状识别
- 🔧 **实验室支持**: 支持血尿酸、24小时尿尿酸、关节液检查等分析
- 🔧 **ICD-10编码**: 新增9个尿酸代谢疾病编码(E79.0、M10.9、N08.2等)
- 🔧 **关联关系网络**: 详细的尿酸代谢与内分泌疾病双向关联机制

#### 知识图谱统计
- 📊 总实体数: 3,256 → 3,267 (+11)
- 📊 总关系数: 6,847 → 6,892 (+45)
- 📊 推理规则: 248 → 251 (+3)
- 📊 共病模式: 12 → 13 (+1)

### v2.1.0 - 风湿免疫疾病模块 (2024-12-19) 🆕

#### 新增功能
- ✅ **8种风湿免疫疾病**: 完整的自身免疫性内分泌疾病、系统性风湿病、多腺体综合征
- ✅ **疾病关联网络**: 366个疾病间关联关系，涵盖内分泌-风湿免疫共病模式
- ✅ **风险评估API**: `/api/v1/rheumatic/assess` - 综合风险分层和管理建议
- ✅ **HLA遗传风险**: 基于HLA分型的遗传易感性分析
- ✅ **家族史评估**: 多腺体自身免疫综合征家族风险预测

#### 技术改进
- 🔧 **症状识别增强**: 新增47种风湿免疫疾病特异症状识别
- 🔧 **实验室支持扩展**: 支持28种自身抗体和炎症标志物分析
- 🔧 **ICD-10编码更新**: 新增9个风湿免疫疾病编码
- 🔧 **检查推荐优化**: 基于疾病类型的个性化检查建议

#### 知识图谱统计
- 📊 总实体数: 2,533 → 3,256 (+723)
- 📊 总关系数: 5,119 → 6,847 (+1,728)  
- 📊 推理规则: 195 → 248 (+53)
- 📊 共病模式: 5 → 12 (+7)

### v2.0.0 - 基础版本
- 23种内分泌疾病支持
- 心血管、神经系统疾病模块
- 基础AI诊断和治疗推荐
- RAG问答系统

## 监控和维护

### 系统监控指标

- **API性能**: 响应时间、吞吐量、错误率
- **数据库性能**: 查询响应时间、连接数、缓存命中率
- **资源使用**: CPU、内存、磁盘、网络使用率
- **业务指标**: 诊断准确率、治疗方案采用率

### 日志管理

```bash
# 查看API日志
docker logs -f endocrine-kg-api

# 查看数据库日志  
docker logs -f endocrine-kg-neo4j

# 集中日志查看
docker-compose logs -f
```

### 备份策略

```bash
# Neo4j数据备份
docker exec endocrine-kg-neo4j neo4j-admin dump --database=neo4j --to=/backup/

# MongoDB数据备份
docker exec endocrine-kg-mongodb mongodump --out /backup/mongodb

# 自动化备份脚本
./scripts/backup.sh
```

## 安全考虑

### 数据安全

- **加密传输**: 全程HTTPS/TLS加密
- **访问控制**: JWT令牌认证和角色授权
- **数据脱敏**: 敏感信息自动脱敏处理
- **审计日志**: 完整的操作审计追踪

### 隐私保护

- **去标识化**: 患者信息自动去标识化
- **最小权限**: 基于角色的最小权限访问
- **数据生命周期**: 自动化数据保留和清理策略
- **合规性**: 符合HIPAA、GDPR等法规要求

## 性能优化

### 数据库优化

- **索引策略**: 基于查询模式的索引优化
- **查询优化**: Cypher查询性能调优
- **缓存策略**: 多层缓存提高响应速度
- **分布式部署**: 支持集群部署和读写分离

### API优化

- **异步处理**: FastAPI异步请求处理
- **连接池**: 数据库连接池管理
- **限流控制**: API请求限流和熔断保护
- **CDN加速**: 静态资源CDN分发

## 质量保证

### 测试策略

```bash
# 单元测试
pytest tests/unit/

# 集成测试  
pytest tests/integration/

# API测试
pytest tests/api/

# 性能测试
pytest tests/performance/
```

### 代码质量

```bash
# 代码格式化
black .

# 静态检查
flake8 .
mypy .

# 安全扫描
bandit -r .
```

## 部署选项

### Docker部署 (推荐)

```bash
# 生产环境完整部署
docker-compose --profile full-stack up -d

# 基础服务部署
docker-compose up -d
```

### Kubernetes部署

```yaml
# kubernetes 部署配置示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: endocrine-kg-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: endocrine-kg-api
  template:
    metadata:
      labels:
        app: endocrine-kg-api
    spec:
      containers:
      - name: api
        image: endocrine-kg-api:latest
        ports:
        - containerPort: 8000
```

### 云原生部署

- **AWS**: EKS + RDS + ElastiCache + S3
- **Azure**: AKS + CosmosDB + Redis Cache + Blob Storage  
- **GCP**: GKE + Cloud SQL + Memorystore + Cloud Storage

## 版本历史

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| v2.0.0 | 2025-01-15 | 完整的内分泌疾病知识图谱系统，支持多疾病诊疗 |
| v1.0.0 | 2024-12-01 | 基础糖尿病知识图谱和API框架 |

## 贡献指南

### 参与贡献

1. Fork 项目仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`  
5. 提交Pull Request

### 问题反馈

- **Bug报告**: GitHub Issues
- **功能请求**: GitHub Discussions
- **技术支持**: support@endocrine-kg.com

### 开发规范

- **代码规范**: 遵循PEP 8标准
- **提交规范**: 使用常规提交格式
- **文档更新**: 同步更新相关文档
- **测试覆盖**: 保持>90%测试覆盖率

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 免责声明

本系统仅供医学教育和研究使用，不能替代专业医疗诊断。所有临床决策应由合格的医疗专业人员做出。

---

**联系方式**  
- 项目主页: https://github.com/endocrine-kg/comprehensive-knowledge-graph
- 技术文档: https://docs.endocrine-kg.com
- 邮箱: info@endocrine-kg.com

**致谢**  
感谢所有为项目贡献知识和代码的医学专家、工程师和研究人员。