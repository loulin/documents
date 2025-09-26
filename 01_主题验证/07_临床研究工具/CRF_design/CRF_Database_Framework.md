# CGMEHR患者资料库框架设计

## 一、数据库设计概述

基于CRFmain.md文档要求，设计一个全面的患者信息收集和管理系统，支持多病区、多医生协作的患者数据录入、审核、分析和交互展示。

## 二、核心数据表结构

### 2.1 系统基础信息表

| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| system_id | VARCHAR(50) | ✓ | 系统唯一标识 | 自动生成 |
| hospital_code | VARCHAR(20) | ✓ | 医院代码 | 下拉选择 |
| hospital_name | VARCHAR(100) | ✓ | 医院名称 | 联动自动填充 |
| department_code | VARCHAR(20) | ✓ | 科室代码 | 下拉选择 |
| department_name | VARCHAR(100) | ✓ | 科室名称 | 联动自动填充 |
| doctor_id | VARCHAR(20) | ✓ | 医生ID | 登录用户自动填充 |
| doctor_name | VARCHAR(50) | ✓ | 医生姓名 | 登录用户自动填充 |
| create_time | TIMESTAMP | ✓ | 创建时间 | 系统自动生成 |
| update_time | TIMESTAMP | ✓ | 更新时间 | 系统自动更新 |

### 2.2 患者基本信息表 (patient_basic_info)

| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 | 验证规则 |
|--------|----------|------|------|----------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者唯一ID | UUID自动生成 | 系统生成 |
| id_card_number | VARCHAR(18) | ✓ | 身份证号 | 输入框 | 18位身份证校验 |
| name | VARCHAR(50) | ✓ | 姓名 | 输入框 | 2-10个字符 |
| gender | TINYINT | ✓ | 性别(1男2女) | 单选按钮 | 从身份证自动提取 |
| birth_date | DATE | ✓ | 出生日期 | 日期选择器 | 从身份证自动提取 |
| age | INT | ✓ | 年龄 | 数字显示 | 根据出生日期自动计算 |
| registration_time | TIMESTAMP | ✓ | 录入时间 | 时间显示 | 系统当前时间 |
| source_type | TINYINT | ✓ | 来源(1门诊2住院) | 单选按钮 | 必选 |
| hospitalization_number | VARCHAR(20) | | 住院号 | 输入框 | 选择住院时必填 |
| contact_phone | VARCHAR(20) | ✓ | 联系方式 | 输入框 | 手机号格式验证 |
| address_province | VARCHAR(20) | ✓ | 省份 | 级联选择器 | 三级联动 |
| address_city | VARCHAR(20) | ✓ | 城市 | 级联选择器 | 三级联动 |
| address_district | VARCHAR(20) | ✓ | 区县 | 级联选择器 | 三级联动 |
| address_detail | VARCHAR(200) | ✓ | 详细地址 | 文本框 | 详细地址填写 |
| occupation | TINYINT | ✓ | 职业类型 | 下拉选择 | 8种职业分类 |
| marital_status | TINYINT | ✓ | 婚姻状况 | 单选按钮 | 5种状态选择 |
| family_members_count | TINYINT | ✓ | 家庭成员数 | 数字输入 | 1-10人范围 |
| education_level | TINYINT | ✓ | 文化程度 | 下拉选择 | 5个等级 |
| annual_income | TINYINT | ✓ | 家庭年收入 | 下拉选择 | 4个收入区间 |
| insurance_types | JSON | ✓ | 保险类型 | 多选框 | JSON存储多选结果 |

### 2.3 病史信息表 (medical_history)

#### 2.3.1 糖尿病史子表 (diabetes_history)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| has_diabetes | BOOLEAN | ✓ | 是否有糖尿病 | 是/否选择 |
| diagnosis_year | YEAR | | 诊断年份 | 年份选择器 |
| diabetes_type | TINYINT | | 糖尿病类型 | 下拉选择8种类型 |
| current_medication | BOOLEAN | | 目前是否用药 | 是/否选择 |
| medication_list | JSON | | 用药清单 | 动态药物选择组件 |

#### 2.3.2 并发症表 (complications)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| complication_type | VARCHAR(50) | ✓ | 并发症类型 | 下拉选择 |
| has_complication | BOOLEAN | ✓ | 是否有该并发症 | 是/否选择 |
| diagnosis_year | YEAR | | 诊断年份 | 年份选择器 |
| current_treatment | BOOLEAN | | 目前是否治疗 | 是/否选择 |
| treatment_details | TEXT | | 治疗详情 | 文本域 |

#### 2.3.3 其他疾病史表 (other_diseases)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| disease_name | VARCHAR(100) | ✓ | 疾病名称 | 疾病搜索组件 |
| has_disease | BOOLEAN | ✓ | 是否患病 | 是/否选择 |
| diagnosis_year | YEAR | | 诊断年份 | 年份选择器 |
| current_medication | BOOLEAN | | 目前是否用药 | 是/否选择 |
| surgical_history | TEXT | | 手术史 | 文本域 |
| medication_details | JSON | | 用药详情 | 动态用药组件 |

#### 2.3.4 个人史表 (personal_history)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| smoking_status | BOOLEAN | ✓ | 是否吸烟 | 是/否选择 |
| smoking_start_year | YEAR | | 开始吸烟年份 | 年份选择器 |
| quit_smoking | BOOLEAN | | 是否戒烟 | 是/否选择 |
| quit_smoking_year | YEAR | | 戒烟年份 | 年份选择器 |
| cigarettes_per_day | INT | | 每日吸烟支数 | 数字输入 |
| drinking_status | BOOLEAN | ✓ | 是否饮酒 | 是/否选择 |
| drinking_start_year | YEAR | | 开始饮酒年份 | 年份选择器 |
| quit_drinking | BOOLEAN | | 是否戒酒 | 是/否选择 |
| quit_drinking_year | YEAR | | 戒酒年份 | 年份选择器 |
| alcohol_ml_per_day | INT | | 每日饮酒毫升 | 数字输入 |

#### 2.3.5 家族史表 (family_history)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| family_member_id | VARCHAR(32) | ✓ | 家属记录ID | UUID生成 |
| relationship | TINYINT | ✓ | 与患者关系 | 下拉选择7种关系 |
| disease_type | VARCHAR(50) | ✓ | 疾病类型 | 疾病选择组件 |
| diabetes_type | TINYINT | | 糖尿病类型 | 下拉选择 |
| onset_year | YEAR | | 发病年份 | 年份选择器 |
| complications | TEXT | | 并发症情况 | 文本域 |
| participate_project | BOOLEAN | | 是否参与本项目 | 是/否选择 |
| contact_info | TEXT | | 联系方式 | 文本域 |

### 2.4 体格检查表 (physical_examination)

| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 | 计算规则 |
|--------|----------|------|------|----------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 | |
| height_cm | DECIMAL(5,2) | ✓ | 身高(cm) | 数字输入 | 100-250cm范围 |
| weight_kg | DECIMAL(5,2) | ✓ | 体重(kg) | 数字输入 | 20-200kg范围 |
| bmi | DECIMAL(4,2) | ✓ | BMI指数 | 自动计算显示 | weight/(height/100)² |
| waist_circumference_cm | DECIMAL(5,2) | | 腰围(cm) | 数字输入 | 可选测量 |
| hip_circumference_cm | DECIMAL(5,2) | | 臀围(cm) | 数字输入 | 可选测量 |
| waist_hip_ratio | DECIMAL(4,3) | | 腰臀比 | 自动计算显示 | 腰围/臀围 |
| examination_date | DATE | ✓ | 检查日期 | 日期选择器 | 默认当前日期 |

### 2.5 实验室检查表 (laboratory_tests)

#### 2.5.1 血糖检测表 (glucose_tests)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| test_date | DATE | ✓ | 检测日期 | 日期选择器 |
| fasting_glucose | DECIMAL(4,2) | | 空腹血糖(mmol/L) | 数字输入 |
| random_glucose | DECIMAL(4,2) | | 随机血糖(mmol/L) | 数字输入 |
| hba1c_percent | DECIMAL(4,2) | | 糖化血红蛋白(%) | 数字输入 |
| glycated_albumin_percent | DECIMAL(4,2) | | 糖化白蛋白(%) | 数字输入 |
| autoantibody_results | JSON | | 自身抗体结果 | 多选框组合 |

#### 2.5.2 OGTT胰岛素释放实验表 (ogtt_insulin_test)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| test_date | DATE | ✓ | 检查日期 | 日期选择器 |
| glucose_0h | DECIMAL(4,2) | | 0小时血糖 | 数字输入 |
| glucose_0_5h | DECIMAL(4,2) | | 0.5小时血糖 | 数字输入 |
| glucose_1h | DECIMAL(4,2) | | 1小时血糖 | 数字输入 |
| glucose_2h | DECIMAL(4,2) | | 2小时血糖 | 数字输入 |
| glucose_3h | DECIMAL(4,2) | | 3小时血糖 | 数字输入 |
| insulin_unit | VARCHAR(20) | | 胰岛素单位 | 下拉选择 |
| insulin_0h | DECIMAL(6,2) | | 0小时胰岛素 | 数字输入 |
| insulin_0_5h | DECIMAL(6,2) | | 0.5小时胰岛素 | 数字输入 |
| insulin_1h | DECIMAL(6,2) | | 1小时胰岛素 | 数字输入 |
| insulin_2h | DECIMAL(6,2) | | 2小时胰岛素 | 数字输入 |
| insulin_3h | DECIMAL(6,2) | | 3小时胰岛素 | 数字输入 |
| c_peptide_unit | VARCHAR(20) | | C肽单位 | 下拉选择 |
| c_peptide_0h | DECIMAL(6,2) | | 0小时C肽 | 数字输入 |
| c_peptide_0_5h | DECIMAL(6,2) | | 0.5小时C肽 | 数字输入 |
| c_peptide_1h | DECIMAL(6,2) | | 1小时C肽 | 数字输入 |
| c_peptide_2h | DECIMAL(6,2) | | 2小时C肽 | 数字输入 |
| c_peptide_3h | DECIMAL(6,2) | | 3小时C肽 | 数字输入 |

#### 2.5.3 肝功能检查表 (liver_function_tests)
| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| test_date | DATE | ✓ | 检查日期 | 日期选择器 |
| total_protein | DECIMAL(5,2) | | 总蛋白 | 数字输入+单位 |
| ast | DECIMAL(6,2) | | 谷草转氨酶 | 数字输入+单位 |
| alt | DECIMAL(6,2) | | 谷丙转氨酶 | 数字输入+单位 |
| ast_alt_ratio | DECIMAL(4,2) | | 谷草/谷丙 | 自动计算 |
| albumin | DECIMAL(4,2) | | 白蛋白 | 数字输入+单位 |
| total_bilirubin | DECIMAL(5,2) | | 总胆红素 | 数字输入+单位 |
| indirect_bilirubin | DECIMAL(5,2) | | 间接胆红素 | 数字输入+单位 |
| direct_bilirubin | DECIMAL(5,2) | | 直接胆红素 | 数字输入+单位 |
| alkaline_phosphatase | DECIMAL(6,2) | | 碱性磷酸酶 | 数字输入+单位 |

#### 2.5.4 肾功能检查表 (kidney_function_tests)
#### 2.5.5 血脂检查表 (lipid_tests)
#### 2.5.6 尿液检查表 (urine_tests)
#### 2.5.7 血常规检查表 (blood_routine_tests)
#### 2.5.8 甲状腺功能检查表 (thyroid_function_tests)
#### 2.5.9 维生素D检查表 (vitamin_d_tests)

### 2.6 辅助检查表 (auxiliary_examinations)

| 字段名 | 数据类型 | 必填 | 说明 | 交互设计 |
|--------|----------|------|------|----------|
| patient_id | VARCHAR(32) | ✓ | 患者ID | 外键关联 |
| examination_type | VARCHAR(50) | ✓ | 检查类型 | 检查项目选择 |
| is_performed | BOOLEAN | ✓ | 是否进行检查 | 是/否选择 |
| examination_data | JSON | | 检查数据 | 动态表单组件 |
| questionnaire_results | JSON | | 问卷结果 | 问卷组件 |
| image_attachments | JSON | | 图片附件 | 文件上传组件 |
| examination_date | DATE | | 检查日期 | 日期选择器 |
| notes | TEXT | | 备注 | 文本域 |

## 三、交互页面设计架构

### 3.1 页面层次结构

```
患者资料库系统
├── 登录页面
├── 主界面
│   ├── 患者列表页
│   ├── 患者详情页
│   │   ├── 基本信息Tab
│   │   ├── 病史信息Tab
│   │   ├── 体格检查Tab
│   │   ├── 实验室检查Tab
│   │   └── 辅助检查Tab
│   ├── 数据录入页
│   │   ├── 分步骤向导模式
│   │   └── 智能表单验证
│   ├── 数据审核页
│   ├── 统计分析页
│   └── 系统管理页
```

### 3.2 核心交互组件设计

#### 3.2.1 智能表单组件
- **身份证智能解析**：输入身份证号自动提取姓名、性别、出生日期、年龄
- **地址级联选择**：省-市-区三级联动选择组件
- **药物搜索组件**：支持拼音搜索的药物数据库
- **动态表单组件**：根据选择动态显示/隐藏相关字段
- **实时计算组件**：BMI、腰臀比等指标自动计算

#### 3.2.2 数据录入增强组件
- **分步骤向导**：将复杂表单分解为多个步骤
- **进度指示器**：显示当前录入进度
- **自动保存功能**：定时保存草稿，防止数据丢失
- **数据校验组件**：实时验证数据格式和逻辑一致性
- **智能提示组件**：根据历史数据提供录入建议

#### 3.2.3 文件管理组件
- **多文件上传**：支持批量上传检查报告、影像资料
- **图片预览组件**：支持图片缩放、旋转预览
- **文件分类管理**：按检查类型自动分类存储
- **版本控制**：同一检查项的多次结果版本管理

### 3.3 响应式设计考虑

#### 3.3.1 多设备适配
- **桌面端**：1920x1080以上分辨率优化
- **平板端**：适配iPad等平板设备
- **移动端**：基本信息查看和简单录入

#### 3.3.2 用户体验优化
- **Loading状态**：数据加载时的友好提示
- **错误提示**：清晰的错误信息和修正建议
- **操作反馈**：成功/失败操作的即时反馈
- **键盘导航**：支持Tab键快速切换输入框

## 四、CSV数据表格文件

基于本框架设计，已生成完整的CSV格式数据表文件：`CRFchart.csv`

### 4.1 文件规范

#### 数据格式标准
- **CSV字段分隔**：统一使用逗号`,`
- **选项值内部分隔**：统一使用分号`;`
- **数据类型格式**：`DECIMAL_5_2`、`VARCHAR_50`等（避免括号内逗号冲突）

#### 字段结构
| 列名 | 说明 | 示例 |
|------|------|------|
| 表名 | 数据库表名 | patient_basic_info |
| 字段名 | 具体字段名 | id_card_number |
| 数据类型 | 标准化数据类型 | VARCHAR_18 |
| 必填 | 是否必填字段 | 是/否 |
| 中文说明 | 字段中文描述 | 身份证号 |
| 交互设计 | 前端交互方式 | 输入框 |
| 验证规则 | 数据验证规则 | 18位身份证校验 |
| 选项值 | 可选值列表 | 1男;2女 |
| 关联关系 | 外键等关系 | 外键关联patient_basic_info |
| 备注 | 额外说明 | 其他相关信息 |

#### 选项值格式示例
- **编码选项**：`1专业人士;2服务业;3自由职业;4工人;5公司职员;6事业单位;7学生;8家庭主妇`
- **文本选项**：`城镇职工医疗保险;城镇居民医疗保险;新型农村合作医疗保险`
- **单位选项**：`μU/mL;mU/L;pmol/L`
- **检查项目**：`ABI;体成分分析;眼底镜;颈动脉超声;神经肌电图`

### 4.2 文件内容

- **13个主要数据表**：从系统基础信息到辅助检查
- **124个字段定义**：涵盖患者全生命周期数据
- **完整交互设计**：每个字段的前端交互方式
- **详细验证规则**：数据质量控制规范

### 4.3 使用说明

#### 导入数据库
```sql
-- 数据类型转换示例
DECIMAL_5_2 → DECIMAL(5,2)
VARCHAR_50 → VARCHAR(50)
```

#### 前端解析
```javascript
// 选项值解析示例
const options = fieldValue.split(';');
// ['1专业人士', '2服务业', '3自由职业', ...]
```

#### 开发参考
1. **数据库设计**：直接参考表结构和字段定义
2. **前端开发**：根据交互设计列实现UI组件
3. **数据验证**：按验证规则列实现校验逻辑
4. **业务逻辑**：参考选项值和关联关系

## 五、总结

本患者资料库框架设计基于CGMEHR系统的实际需求，提供了一个完整的、可扩展的、实用的患者数据管理解决方案。

### 核心优势：
1. **数据结构完整**：覆盖患者全生命周期的医疗数据
2. **交互设计友好**：智能化的数据录入和管理界面  
3. **质量控制严格**：多层次的数据验证和审核机制
4. **扩展能力强**：支持未来功能扩展和系统集成
5. **格式规范统一**：CSV文件严格遵循标准格式，便于系统导入

### 交付文件：
- **CRF_Database_Framework.md**：完整框架设计文档
- **CRFchart.csv**：标准化数据表格文件

该框架可以有效支撑CGMEHR系统的患者数据管理需求，为临床研究和医疗决策提供可靠的数据基础。