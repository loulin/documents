# 内分泌代谢疾病诊疗数据标准化体系

## 📋 项目概述

本项目构建了一套完整的内分泌代谢疾病诊疗数据标准化体系，涵盖19个医学专科领域，包含64个专业检查Schema，8,417个标准化字段，为内分泌代谢疾病的全生命周期、全系统、全方位管理提供统一的数据标准。

## 🎯 项目目标

- **标准化数据采集**：建立统一的医疗数据采集标准
- **多学科协作**：促进内分泌与各专科的协作诊疗
- **精准医学**：支持个体化诊疗方案制定
- **质量控制**：提高医疗数据质量和一致性
- **科研支撑**：为临床研究提供标准化数据基础

## 📁 项目结构

```
documents/
├── README.md                                    # 项目说明文档
├── 06_Others/Input/SchemaCSV/                  # 检查Schema目录
│   ├── 基础代谢检查/                            # 核心代谢检查
│   │   ├── diabetes-comprehensive-schema.csv
│   │   ├── metabolic-syndrome-schema.csv
│   │   ├── insulin-resistance-schema.csv
│   │   ├── lipid-metabolism-schema.csv
│   │   ├── bone-metabolism-schema.csv
│   │   └── nutrition-energy-metabolism-schema.csv
│   ├── 内分泌功能检查/                          # 内分泌系统检查
│   │   ├── thyroid-function-comprehensive-schema.csv
│   │   ├── adrenal-function-schema.csv
│   │   ├── pituitary-function-schema.csv
│   │   └── reproductive-endocrine-metabolism-schema.csv
│   ├── 器官系统并发症检查/                      # 并发症相关检查
│   │   ├── diabetic-nephropathy-schema.csv
│   │   ├── cardiovascular-metabolic-risk-schema.csv
│   │   ├── diabetic-neuropathy-schema.csv
│   │   ├── peripheral-vascular-disease-schema.csv
│   │   ├── diabetic-retinopathy-schema.csv
│   │   └── pulmonary-function-metabolism-schema.csv
│   ├── 特殊生理阶段检查/                        # 特殊阶段检查
│   │   ├── gestational-diabetes-schema.csv
│   │   └── pediatric-developmental-metabolism-schema.csv
│   ├── 精准医学检查/                            # 精准医学相关
│   │   ├── pharmacogenomic-testing-schema.csv
│   │   ├── genetic-epigenetic-metabolic-schema.csv
│   │   ├── nutrition-genomics-schema.csv
│   │   └── immune-inflammation-metabolism-schema.csv
│   ├── 功能评估检查/                            # 功能状态评估
│   │   ├── exercise-metabolism-function-schema.csv
│   │   ├── digestive-metabolism-function-schema.csv
│   │   ├── musculoskeletal-metabolism-schema.csv
│   │   ├── psychiatric-psychological-metabolism-assessment-schema.csv
│   │   └── vascular-endothelial-function-schema.csv
│   ├── 环境因素检查/                            # 环境与代谢
│   │   ├── environmental-metabolic-toxicology-schema.csv
│   │   └── dermatological-metabolism-schema.csv
│   ├── 问卷和评估/                              # 问卷调查和评估
│   │   ├── systematic-physical-examination-schema.csv
│   │   ├── diabetes-quality-of-life-assessment-schema.csv
│   │   ├── diabetes-self-management-assessment-schema.csv
│   │   ├── diabetes-nursing-assessment-schema.csv
│   │   ├── medication-adherence-assessment-schema.csv
│   │   ├── nutrition-knowledge-behavior-assessment-schema.csv
│   │   ├── insulin-injection-technique-assessment-schema.csv
│   │   ├── blood-glucose-monitoring-skills-assessment-schema.csv
│   │   ├── hypoglycemia-risk-assessment-schema.csv
│   │   ├── endocrine-disease-rehabilitation-assessment-schema.csv
│   │   ├── multidisciplinary-consultation-record-schema.csv
│   │   └── family-support-assessment-schema.csv
│   └── 基础检查/                                # 基础医学检查
│       ├── vital-signs-schema.csv
│       ├── blood-routine-schema.csv
│       ├── blood-biochemistry-schema.csv
│       ├── urine-routine-schema.csv
│       └── [其他基础检查...]
└── docs/                                        # 文档目录
    ├── schema-specifications.md                 # Schema规范说明
    ├── field-dictionary.md                     # 字段字典
    └── implementation-guide.md                  # 实施指南
```

## 🔧 Schema 设计规范

### 字段结构
每个Schema采用统一的CSV格式，包含以下标准字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| `fieldName` | 英文字段名 | `examDate` |
| `fieldNameCN` | 中文字段名 | `检查日期` |
| `dataType` | 数据类型 | `String`, `Number`, `Boolean` |
| `description` | 字段描述 | `检查日期，格式YYYY-MM-DD` |
| `examples` | 示例值 | `2024-12-01` |

### 通用字段
所有Schema包含以下标准字段：
- `examDate`: 检查日期
- `patientID`: 患者唯一标识符
- `patientName`: 患者姓名
- `clinicalIndication`: 临床适应症
- `diagnosisImpression`: 诊断印象
- `recommendation`: 建议

## 📊 Schema 分类统计

### 🎯 按优先级分类

#### 最高优先级 (5分)
- **免疫炎症代谢检查** (155字段) - 慢性炎症评估、免疫功能检测
- **血管内皮功能检查** (158字段) - 血管功能、内皮损伤评估

#### 次高优先级 (4分)
- **运动代谢功能检查** (148字段) - 心肺功能、运动处方制定
- **药物代谢基因检测** (185字段) - 个体化用药指导
- **精神心理代谢评估** (189字段) - 心理健康、生活质量评估
- **消化代谢功能检查** (238字段) - 胃肠功能、营养吸收评估
- **肌肉骨骼代谢检查** (232字段) - 肌少症、骨质疏松评估
- **肺功能代谢检查** (258字段) - 呼吸功能、睡眠呼吸评估

#### 一般优先级 (3分)
- **皮肤代谢病变检查** (298字段) - 皮肤并发症、黑棘皮病评估
- **环境代谢毒理学检查** (365字段) - 环境污染物、毒性评估

### 🏥 按专科领域分类

#### 核心内分泌代谢科 (9个Schema)
- 糖尿病综合评估、代谢综合征、胰岛素抵抗
- 脂质代谢、骨代谢、营养能量代谢
- 甲状腺功能、肾上腺功能、垂体功能

#### 并发症相关专科 (6个Schema)
- 糖尿病肾病、心血管代谢风险、糖尿病神经病变
- 周围血管疾病、糖尿病视网膜病变、肺功能异常

#### 特殊人群专科 (2个Schema)
- 妊娠期糖尿病、儿童发育代谢异常

#### 精准医学相关 (4个Schema)
- 药物基因组学检测、遗传表观遗传学代谢检查
- 营养基因组学检查、免疫炎症代谢检查

#### 功能评估相关 (15个Schema)
- 运动功能、消化功能、肌骨功能、心理功能
- 血管内皮功能、皮肤功能等

#### 环境健康相关 (2个Schema)
- 环境毒理学、皮肤代谢病变

#### 问卷和评估相关 (12个Schema)
- 系统性体格检查、生活质量评估、自我管理评估
- 护理评估、药物依从性、营养知识行为评估
- 技能评估（胰岛素注射、血糖监测）、风险评估
- 康复评估、多学科会诊记录、家庭支持评估

#### 基础医学检查 (10个Schema)
- 生命体征、血常规、生化、尿常规
- 影像学检查等基础项目

## 🚀 使用指南

### 数据采集流程
1. **患者基础信息录入** - 使用基础信息Schema
2. **临床症状评估** - 选择相应专科Schema
3. **实验室检查** - 使用生化、免疫等Schema
4. **影像学检查** - 使用相应影像Schema
5. **功能评估** - 使用功能相关Schema
6. **综合分析** - 整合多维度数据

### 质量控制要点
- **必填字段检查** - 确保核心字段完整性
- **数据类型验证** - 检查数据格式正确性
- **数值范围验证** - 验证数值在合理范围内
- **逻辑一致性检查** - 检查字段间逻辑关系
- **时间戳验证** - 确保时间逻辑正确

### 实施建议
1. **分阶段实施** - 优先实施高优先级Schema
2. **试点验证** - 选择典型科室试点应用
3. **培训教育** - 对医护人员进行培训
4. **持续改进** - 根据反馈优化Schema设计
5. **标准推广** - 逐步扩展到更多医疗机构

## 🔬 技术特性

### 数据标准化
- **统一命名规范** - 中英文对照的标准化命名
- **标准化数据类型** - 统一的数据类型定义
- **标准化值域** - 规范的取值范围和格式
- **标准化描述** - 详细的字段说明和示例

### 可扩展性
- **模块化设计** - 独立的Schema模块，便于扩展
- **版本管理** - 支持Schema版本迭代更新
- **自定义字段** - 预留扩展字段支持个性化需求
- **多系统兼容** - 支持不同HIS/EMR系统集成

### 互操作性
- **HL7 FHIR兼容** - 符合国际医疗信息交换标准
- **ICD编码对应** - 与国际疾病分类编码对应
- **SNOMED CT映射** - 支持标准医学术语体系
- **本土化适配** - 适配中国医疗实践特点

## 📈 应用场景

### 临床诊疗
- **多学科会诊** - 提供标准化的会诊数据格式
- **病历质控** - 自动化病历质量检查
- **临床路径** - 支持标准化临床路径执行
- **随访管理** - 标准化的随访数据收集

### 科研分析
- **队列研究** - 为大规模队列研究提供数据标准
- **真实世界研究** - 支持RWE研究数据标准化
- **AI模型训练** - 为机器学习提供结构化数据
- **生物统计分析** - 标准化的统计分析数据格式

### 质量管理
- **质量指标监测** - 自动化质量指标计算
- **绩效评估** - 标准化的绩效评估指标
- **风险预警** - 基于标准化数据的风险识别
- **持续改进** - 数据驱动的质量改进

### 公共卫生
- **疾病监测** - 标准化的疾病监测数据
- **流行病学调查** - 统一的流行病学数据格式
- **健康管理** - 个人健康档案标准化
- **政策制定** - 为卫生政策提供数据支撑

## 🛠️ 开发维护

### 版本管理
- **版本号规则** - 采用语义化版本号 (v1.0.0)
- **变更记录** - 详细记录每个版本的变更内容
- **向后兼容** - 确保新版本向后兼容
- **升级指南** - 提供详细的版本升级指南

### 质量保证
- **专家评审** - 邀请领域专家评审Schema设计
- **用户反馈** - 收集一线医护人员使用反馈
- **持续测试** - 在真实环境中持续测试验证
- **国际对标** - 与国际先进标准对比完善

### 社区参与
- **开放协作** - 欢迎医疗机构和技术团队参与
- **标准化组织** - 与相关标准化组织合作
- **学术交流** - 在学术会议上分享交流经验
- **培训推广** - 组织培训和推广活动

## 📚 参考文献

### 国际标准
- HL7 FHIR R4 Implementation Guide
- SNOMED CT International Edition
- ICD-11 for Mortality and Morbidity Statistics
- LOINC Database

### 临床指南
- 中国2型糖尿病防治指南(2020年版)
- 美国糖尿病学会糖尿病医学诊疗标准
- 欧洲糖尿病研究协会临床实践指南
- WHO全球糖尿病报告

### 技术规范
- 国家卫健委医院信息化建设标准与规范
- 医疗健康信息互联互通标准化成熟度测评
- 电子病历系统功能应用水平分级评价
- 医院智慧服务分级评估标准体系

## 📞 联系方式

### 技术支持
- **问题反馈** - 通过GitHub Issues提交问题
- **功能建议** - 欢迎提出改进建议
- **技术讨论** - 加入技术讨论群组

### 合作咨询
- **实施咨询** - 提供Schema实施指导
- **定制开发** - 支持个性化定制需求
- **培训服务** - 提供专业培训服务

## 📄 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源许可证。

## 🙏 致谢

感谢所有参与项目开发的医疗专家、技术团队和合作机构，特别感谢：

- 各大医院内分泌科专家的专业指导
- 医疗信息化技术团队的技术支持
- 标准化组织的规范参考
- 开源社区的技术贡献

---

**版本信息**: v4.0.0
**最后更新**: 2024年12月01日
**维护团队**: 内分泌代谢疾病数据标准化项目组
**总Schema数**: 64个
**总字段数**: 8,417个