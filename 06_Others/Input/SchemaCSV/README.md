# 内分泌代谢疾病诊疗Schema集合

## 概述

本目录包含了以内分泌代谢疾病为核心的完整医疗数据标准化Schema体系。这些Schema以CSV格式定义，涵盖19个医学专科领域，为内分泌代谢疾病的全生命周期、全系统、全方位管理提供统一的数据标准。

**当前共有74个Schema文件，8,704个标准化字段**，构建了从基础检验到前沿精准医学的完整医疗体系，特别针对糖尿病及其并发症、代谢综合征、内分泌功能异常、精准医学、功能评估、环境健康、问卷评估、护理记录等进行了全面扩展。

## Schema分类

### 🩸 基础医学检查类 (10个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `vital-signs-schema.csv` | 生命体征监测 | 45 | ⭐⭐⭐⭐⭐ |
| `blood-routine-schema.csv` | 血常规检查 | 68 | ⭐⭐⭐⭐⭐ |
| `blood-biochemistry-schema.csv` | 血生化检查 | 156 | ⭐⭐⭐⭐⭐ |
| `urine-routine-schema.csv` | 尿常规检查 | 78 | ⭐⭐⭐⭐⭐ |
| `electrocardiogram-schema.csv` | 心电图检查 | 89 | ⭐⭐⭐⭐⭐ |
| `chest-xray-schema.csv` | 胸部X线检查 | 112 | ⭐⭐⭐⭐⭐ |
| `blood-glucose-monitoring-schema.csv` | 血糖监测 | 125 | ⭐⭐⭐⭐⭐ |
| `body-composition-analysis-schema.csv` | 体成分分析 | 98 | ⭐⭐⭐⭐ |
| `neurophysiological-exam-schema.csv` | 神经电生理检查 | 132 | ⭐⭐⭐⭐ |
| `liver-stiffness-schema.csv` | 肝脏硬度检查 | 87 | ⭐⭐⭐⭐ |

### 🫁 专科影像检查类 (9个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `cardiac-ultrasound-schema.csv` | 心脏超声检查 | 168 | ⭐⭐⭐⭐⭐ |
| `carotid-artery-ultrasound-schema.csv` | 颈动脉超声 | 145 | ⭐⭐⭐⭐⭐ |
| `renal-ultrasound-schema.csv` | 肾脏超声检查 | 156 | ⭐⭐⭐⭐⭐ |
| `thyroid-ultrasound-schema.csv` | 甲状腺超声 | 134 | ⭐⭐⭐⭐⭐ |
| `liver-ultrasound-schema.csv` | 肝脏超声检查 | 142 | ⭐⭐⭐⭐ |
| `eye-fundus-schema.csv` | 眼底检查 | 187 | ⭐⭐⭐⭐ |
| `retinal-oct-schema.csv` | 视网膜OCT | 145 | ⭐⭐⭐⭐ |
| `lower-extremity-arterial-ultrasound-schema.csv` | 下肢动脉超声 | 156 | ⭐⭐⭐⭐ |
| `visceral-fat-ct-schema.csv` | 内脏脂肪CT | 98 | ⭐⭐⭐ |
| `visceral-fat-mri-schema.csv` | 内脏脂肪MRI | 102 | ⭐⭐⭐ |

### 🏥 核心内分泌代谢检查类 (10个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `diabetes-comprehensive-schema.csv` | 糖尿病综合检查 | 245 | ⭐⭐⭐⭐⭐ |
| `metabolic-syndrome-schema.csv` | 代谢综合征评估 | 198 | ⭐⭐⭐⭐⭐ |
| `insulin-resistance-schema.csv` | 胰岛素抵抗检查 | 167 | ⭐⭐⭐⭐⭐ |
| `lipid-metabolism-schema.csv` | 血脂代谢检查 | 189 | ⭐⭐⭐⭐⭐ |
| `thyroid-function-comprehensive-schema.csv` | 甲状腺功能综合检查 | 178 | ⭐⭐⭐⭐⭐ |
| `bone-metabolism-schema.csv` | 骨代谢检查 | 165 | ⭐⭐⭐⭐⭐ |
| `nutrition-energy-metabolism-schema.csv` | 营养与能量代谢检查 | 234 | ⭐⭐⭐⭐⭐ |
| `adrenal-function-schema.csv` | 肾上腺功能检查 | 142 | ⭐⭐⭐⭐ |
| `pituitary-function-schema.csv` | 垂体功能检查 | 156 | ⭐⭐⭐⭐ |
| `sex-specific-hormone-therapy-schema.csv` | 性别特异性激素治疗随访 | 27 | ⭐⭐⭐⭐ |

### 🧪 罕见内分泌疾病评估类 (2个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `cushings-syndrome-evaluation-schema.csv` | 库欣综合征评估 | 29 | ⭐⭐⭐⭐⭐ |
| `pheochromocytoma-paraganglioma-schema.csv` | 嗜铬细胞瘤/副神经节瘤评估 | 26 | ⭐⭐⭐⭐ |

### 🔬 器官系统并发症检查类 (8个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `diabetic-nephropathy-schema.csv` | 糖尿病肾病检查 | 154 | ⭐⭐⭐⭐⭐ |
| `non-diabetic-renal-disease-schema.csv` | 非糖尿病性肾病综合评估 | 33 | ⭐⭐⭐⭐⭐ |
| `hyperuricemia-comorbidity-schema.csv` | 高尿酸血症合并症管理 | 27 | ⭐⭐⭐⭐ |
| `cardiovascular-metabolic-risk-schema.csv` | 心血管代谢风险评估 | 198 | ⭐⭐⭐⭐⭐ |
| `diabetic-neuropathy-schema.csv` | 糖尿病神经病变检查 | 187 | ⭐⭐⭐⭐⭐ |
| `peripheral-vascular-disease-schema.csv` | 周围血管疾病检查 | 176 | ⭐⭐⭐⭐⭐ |
| `diabetic-retinopathy-schema.csv` | 糖尿病视网膜病变检查 | 165 | ⭐⭐⭐⭐⭐ |
| `pulmonary-function-metabolism-schema.csv` | 肺功能代谢检查 | 258 | ⭐⭐⭐⭐ |

### 👶 特殊生理阶段检查类 (3个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `gestational-diabetes-schema.csv` | 妊娠期糖尿病检查 | 198 | ⭐⭐⭐⭐⭐ |
| `pregnancy-complications-schema.csv` | 孕期并发症精细化评估 | 39 | ⭐⭐⭐⭐⭐ |
| `pediatric-developmental-metabolism-schema.csv` | 儿童发育代谢检查 | 138 | ⭐⭐⭐⭐⭐ |

### 🧬 精准医学检查类 (8个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `immune-inflammation-metabolism-schema.csv` | 免疫炎症代谢检查 | 155 | ⭐⭐⭐⭐⭐ |
| `pharmacogenomic-testing-schema.csv` | 药物代谢基因检测 | 185 | ⭐⭐⭐⭐⭐ |
| `genetic-epigenetic-metabolic-schema.csv` | 遗传表观遗传代谢检查 | 178 | ⭐⭐⭐⭐ |
| `gut-microbiome-schema.csv` | 肠道微生物群检查 | 145 | ⭐⭐⭐⭐ |
| `vascular-endothelial-function-schema.csv` | 血管内皮功能检查 | 158 | ⭐⭐⭐⭐⭐ |
| `exercise-metabolism-function-schema.csv` | 运动代谢功能检查 | 148 | ⭐⭐⭐⭐ |
| `digestive-metabolism-function-schema.csv` | 消化代谢功能检查 | 238 | ⭐⭐⭐⭐ |
| `hypertension-comprehensive-schema.csv` | 高血压综合检查 | 189 | ⭐⭐⭐⭐⭐ |

### 💉 治疗过程监测与药物优化类 (1个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `insulin-therapy-optimization-schema.csv` | 胰岛素治疗优化评估 | 27 | ⭐⭐⭐⭐⭐ |

### 🧘 生活方式与可穿戴数据类 (1个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `lifestyle-wearable-monitoring-schema.csv` | 生活方式与可穿戴监测 | 27 | ⭐⭐⭐⭐ |

### 🏡 护理与居家管理类 (1个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `metabolic-home-care-schema.csv` | 代谢性疾病居家护理管理 | 24 | ⭐⭐⭐⭐ |

### 🩺 功能评估检查类 (4个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `psychiatric-psychological-metabolism-assessment-schema.csv` | 精神心理代谢评估 | 189 | ⭐⭐⭐⭐ |
| `musculoskeletal-metabolism-schema.csv` | 肌肉骨骼代谢检查 | 232 | ⭐⭐⭐⭐ |
| `dermatological-metabolism-schema.csv` | 皮肤代谢病变检查 | 298 | ⭐⭐⭐ |
| `pancreatic-cancer-schema.csv` | 胰腺癌检查 | 145 | ⭐⭐⭐⭐ |

### 🌍 环境健康检查类 (2个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `environmental-metabolic-toxicology-schema.csv` | 环境代谢毒理学检查 | 365 | ⭐⭐⭐ |
| `reproductive-endocrine-metabolism-schema.csv` | 生殖内分泌代谢检查 | 145 | ⭐⭐⭐⭐ |

### 📋 问卷和评估类 (13个)
| Schema文件 | 中文名称 | 字段数 | 重要程度 |
|------------|----------|--------|----------|
| `systematic-physical-examination-schema.csv` | 系统性体格检查 | 208 | ⭐⭐⭐⭐⭐ |
| `diabetes-quality-of-life-assessment-schema.csv` | 糖尿病生活质量评估 | 127 | ⭐⭐⭐⭐⭐ |
| `diabetes-self-management-assessment-schema.csv` | 糖尿病自我管理能力评估 | 134 | ⭐⭐⭐⭐⭐ |
| `diabetes-nursing-assessment-schema.csv` | 糖尿病标准化护理评估 | 162 | ⭐⭐⭐⭐⭐ |
| `medication-adherence-assessment-schema.csv` | 药物依从性评估 | 147 | ⭐⭐⭐⭐⭐ |
| `nutrition-knowledge-behavior-assessment-schema.csv` | 营养知识与行为评估 | 186 | ⭐⭐⭐⭐⭐ |
| `insulin-injection-technique-assessment-schema.csv` | 胰岛素注射技术评估 | 178 | ⭐⭐⭐⭐⭐ |
| `blood-glucose-monitoring-skills-assessment-schema.csv` | 血糖监测技能评估 | 176 | ⭐⭐⭐⭐⭐ |
| `hypoglycemia-risk-assessment-schema.csv` | 低血糖风险评估 | 165 | ⭐⭐⭐⭐⭐ |
| `endocrine-disease-rehabilitation-assessment-schema.csv` | 内分泌疾病康复评估 | 198 | ⭐⭐⭐⭐ |
| `multidisciplinary-consultation-record-schema.csv` | 多学科会诊记录 | 213 | ⭐⭐⭐⭐⭐ |
| `cardio-renal-metabolic-board-schema.csv` | 心肾代谢联合会诊记录 | 23 | ⭐⭐⭐⭐ |
| `family-support-assessment-schema.csv` | 家庭支持评估 | 189 | ⭐⭐⭐⭐ |

## Schema结构说明

### 标准字段格式
每个Schema文件包含以下标准列：
- **字段名 (英文)**: 数据库字段名，使用驼峰命名法
- **字段名 (中文)**: 中文字段名，便于理解
- **数据类型**: String, Number, Boolean等
- **描述**: 详细的字段描述，包含参考范围和建议值
- **示例**: 具体的示例数据

### 通用字段
所有Schema都包含以下通用字段：
- `examDate`: 检查日期
- `diagnosisImpression`: 诊断/印象
- `recommendation`: 建议

### 数据类型规范
- **String**: 文本类型，包括选项值和描述性文本
- **Number**: 数值类型，包括测量值和计算值
- **Boolean**: 布尔类型，用于是/否判断

## 使用指南

### 开发集成
1. **数据库设计**: 基于Schema创建数据表结构
2. **API接口**: 使用Schema定义API请求/响应格式
3. **前端表单**: 根据Schema生成动态表单
4. **数据验证**: 使用描述中的参考范围进行数据校验

### 数据标准化
1. **建议值**: 严格按照Schema中的建议值填写
2. **参考范围**: 使用Schema中定义的正常值范围
3. **单位统一**: 按照Schema中指定的单位进行数据录入
4. **编码标准**: 使用统一的编码标准（如ICD-10）

### 质量控制
1. **必填字段**: 确保核心字段的完整性
2. **数据类型**: 严格按照定义的数据类型录入
3. **值域检查**: 验证数据是否在合理范围内
4. **逻辑校验**: 进行字段间的逻辑一致性检查

## 扩展和维护

### 体系设计原则
1. **以内分泌代谢疾病为核心**：围绕糖尿病、代谢综合征等构建完整体系
2. **全生命周期覆盖**：从儿童发育到老年期的全程管理
3. **多学科协作**：涵盖19个医学专科的协作诊疗
4. **精准医学导向**：整合基因检测、个体化医疗等前沿技术
5. **标准化规范**：统一的数据结构和质量标准

### 新增Schema指南
1. **命名规范**：遵循现有的`检查类型-schema.csv`格式
2. **字段结构**：包含fieldName、fieldNameCN、dataType、description、examples五个标准列
3. **通用字段**：必须包含examDate、patientID、diagnosisImpression、recommendation等标准字段
4. **医学验证**：经过相关专科医学专家审核
5. **质量保证**：符合临床实践和医疗标准

### Schema版本管理
1. **版本控制**：采用语义化版本号（v1.0.0）
2. **向后兼容**：确保新版本向后兼容现有数据
3. **变更记录**：详细记录每次更新的内容和影响
4. **测试验证**：在真实临床环境中验证更新效果
5. **文档同步**：及时更新相关技术文档

### Schema索引与单位管理
- **事实来源**：CSV 文件仍为唯一可信的 Schema 定义，所有调整必须先更新 CSV。
- **索引脚本**：目录内提供 `build_schema_index.py`，可批量解析字段描述，生成结构化索引文件。
- **生成命令**：在项目根目录执行 `python3 06_Others/Input/SchemaCSV/build_schema_index.py --input-dir 06_Others/Input/SchemaCSV --output 06_Others/Input/SchemaCSV/combined_schema_index.json`，即可刷新索引。
- **输出内容**：索引 JSON 包含字段的中英文名、数据类型、原始/清洗描述、示例值与推断单位，便于接口、LLM 提示词和后处理校验使用。
- **单位推断**：脚本优先读取描述中的“单位:”提示，回退到字段名括号信息；若仍无法判定，单位字段保持为空，建议补充描述后重新生成。
- **版本治理**：提交 `*.csv` 改动时应同步提交 `combined_schema_index.json` 等衍生文件，确保各环境使用一致的 Schema 快照，可结合 pre-commit/CI 检查同步性。
- **自动化拓展**：如需避免人工同步，可在服务启动时动态加载 CSV 或编写额外校验脚本，统筹考虑性能与维护成本。

### 临床应用验证
1. **医学准确性**：所有字段和参考值经过医学专家验证
2. **实用性评估**：在真实临床环境中测试可用性
3. **标准符合性**：符合HL7 FHIR、SNOMED CT等国际标准
4. **本土化适配**：适应中国医疗实践特点和法规要求
5. **多中心验证**：在不同级别医疗机构验证适用性

## 技术规范

### 文件格式
- 编码：UTF-8
- 分隔符：逗号(,)
- 换行符：LF(\n)
- 引用符：双引号(")

### 命名规范
- Schema文件：`检查类型-schema.csv`
- 字段命名：驼峰命名法（camelCase）
- 中文字段：简洁明确，避免歧义

### 版本管理
- 使用Git进行版本控制
- 重要更新打tag标记
- 维护详细的变更日志

## 应用场景

### 🏥 临床诊疗应用
- **多学科会诊**：提供标准化的内分泌代谢疾病会诊数据格式
- **病历质控**：自动化病历质量检查和缺陷提醒
- **临床路径**：支持糖尿病等疾病标准化临床路径执行
- **随访管理**：标准化的长期随访数据收集和分析

### 🔬 科研分析应用
- **队列研究**：为大规模内分泌代谢疾病队列研究提供数据标准
- **真实世界研究**：支持RWE研究的标准化数据收集
- **AI模型训练**：为机器学习和人工智能提供结构化训练数据
- **多中心研究**：统一的多中心研究数据格式和质控标准

### 📊 质量管理应用
- **质量指标监测**：自动化计算糖尿病等疾病质量指标
- **绩效评估**：标准化的科室和医生绩效评估指标
- **风险预警**：基于标准化数据的疾病风险识别和预警
- **持续改进**：数据驱动的医疗质量持续改进

### 🌐 公共卫生应用
- **疾病监测**：标准化的内分泌代谢疾病监测数据
- **流行病学调查**：统一的流行病学调查数据格式
- **健康管理**：个人健康档案标准化和健康管理
- **政策制定**：为卫生政策制定提供标准化数据支撑

## 技术特性

### 🔄 互操作性
- **HL7 FHIR兼容**：符合国际医疗信息交换标准
- **SNOMED CT映射**：支持标准医学术语体系
- **ICD编码对应**：与国际疾病分类编码对应
- **本土化适配**：适配中国医疗实践特点

### 📈 可扩展性
- **模块化设计**：独立的Schema模块，便于扩展和维护
- **版本管理**：支持Schema版本迭代更新
- **自定义字段**：预留扩展字段支持个性化需求
- **多系统兼容**：支持不同HIS/EMR系统集成

### 🛡️ 安全性
- **隐私保护**：Schema设计考虑了患者数据隐私保护需求
- **访问控制**：支持基于角色的数据访问控制
- **审计追踪**：包含必要的数据操作审计字段
- **法规遵循**：符合《网络安全法》、《数据安全法》等法律法规

## 实施指南

### 📋 实施步骤
1. **需求分析**：分析医疗机构具体需求和现状
2. **系统设计**：基于Schema设计数据库和系统架构
3. **试点部署**：选择典型科室进行试点应用
4. **培训推广**：对医护人员进行系统培训
5. **全面实施**：逐步推广到全院各科室
6. **持续优化**：根据使用反馈持续改进

### 💡 最佳实践
- **分阶段实施**：优先实施核心内分泌代谢检查Schema
- **数据质控**：建立完善的数据质量控制机制
- **用户培训**：定期组织医护人员培训和考核
- **技术支持**：建立专业的技术支持团队
- **持续改进**：建立用户反馈和系统优化机制

## 注意事项

1. **数据隐私**：严格遵守患者数据隐私保护相关法律法规
2. **法规遵循**：符合医疗数据相关法律法规和行业标准
3. **安全考虑**：建立完善的数据安全防护体系
4. **质量控制**：建立严格的数据质量控制和审核机制
5. **用户培训**：确保所有用户充分理解和正确使用Schema

## 版本历史

### v4.0 (2024-12-01)
- ✅ 新增12个问卷和评估类Schema，实现全面数据处理覆盖
- ✅ 完善内分泌代谢疾病诊疗体系，达到64个Schema
- ✅ 增加系统性体格检查、生活质量评估等临床实用Schema
- ✅ 新增护理评估、技能评估、风险评估等专业Schema
- ✅ 优化Schema分类，新增问卷和评估类别

### v3.0 (2024-09-01)
- ✅ 新增10个专科Schema（免疫炎症、血管内皮、运动代谢等）
- ✅ 完善内分泌代谢疾病诊疗体系，达到52个Schema
- ✅ 增加精准医学相关Schema（药物基因检测等）
- ✅ 优化Schema分类和组织结构

### v2.0 (2024-09-01)
- ✅ 新增前沿代谢检查类Schema
- ✅ 完善内分泌代谢疾病专科Schema
- ✅ 优化字段描述和示例数据

### v1.0 (2024-06-01)
- ✅ 建立基础医学检查Schema体系
- ✅ 实现标准化数据结构定义
- ✅ 完成基础文档和使用指南

---

**维护团队**: 内分泌代谢疾病数据标准化项目组
**最后更新**: 2024年12月01日
**当前版本**: v4.0
**总Schema数**: 64个
**总字段数**: 8,417个

📧 **联系方式**: 如有问题或建议，请联系开发团队或提交Issue
🔗 **技术支持**: 提供Schema实施指导和技术咨询服务
📚 **培训服务**: 提供专业的Schema使用培训和认证
