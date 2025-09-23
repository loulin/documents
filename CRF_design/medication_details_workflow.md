# 用药详情录入逻辑设计

## 📋 适用范围

从D2A到H7所有涉及用药的疾病，包括：

### 糖尿病并发症（D2A-D2D3）
- **D2A2A**：糖尿病肾病用药详情
- **D2B2A**：糖尿病视网膜病变用药详情  
- **D2C2A**：糖尿病周围神经病变用药详情

### 其他疾病史（H1-H7）
- **H1B1**：高血压用药详情
- **H2B1**：冠心病用药详情
- **H3C1**：心律失常用药详情
- **H4B1**：血脂异常用药详情
- **H5B1**：高尿酸血症用药详情
- **H6B1**：脑梗用药详情
- **H7B1**：脑出血用药详情

## 🔄 录入流程设计

### 第一步：疾病诊断确认
```
问题：是否患有糖尿病肾病？
选项：□ 有  □ 无

如果选择"有" ↓
  诊断年份：[____] 年
```

### 第二步：用药状态判断
```
问题：糖尿病肾病是否用药？
选项：□ 是  □ 否

如果选择"否" → 跳过用药详情，进入下一个疾病
如果选择"是" → 进入用药详情录入
```

### 第三步：用药详情录入界面
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        糖尿病肾病用药详情录入
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前已添加用药：0种

[+ 添加第1种用药]

┌─ 第1种用药信息 ─────────────────────┐
│ 药品通用名：[搜索下拉框] ▼             │
│             [阿司匹林             ]  │
│                                       │
│ 商品名：    [拜阿司匹林        ] (可选) │
│                                       │
│ 规格：      [下拉选择] ▼               │
│             100mg/片                  │
│                                       │
│ 单次剂量：  [100] [mg] ▼              │
│                                       │
│ 服用频次：  [下拉选择] ▼               │
│             每日1次                   │
│                                       │
│ 给药途径：  [下拉选择] ▼               │
│             口服                      │
│                                       │
│ 开始用药：  [2023]-[01]-[15] (可选)   │
│ 停药日期：  [____]-[__]-[__] (可选)   │
│                                       │
│ ☑ 目前仍在使用                       │
│                                       │
│ 用药效果：  [下拉选择] ▼               │
│             有效                      │
│                                       │
│ 不良反应：  □ 无  ☑ 胃肠不适          │
│             □ 其他: ____________      │
│                                       │
│ 备注：      [____________________]    │
└───────────────────────────────────┘

[保存第1种用药]  [取消]

┌─ 继续添加用药？ ───────────────────┐
│                                   │
│  是否还有其他糖尿病肾病用药？        │
│                                   │
│  [+ 添加下一种用药]  [录入完成]      │
│                                   │
└───────────────────────────────────┘
```

### 第四步：多药物循环录入
```
当前已添加用药：1种
  1. 阿司匹林 100mg/片，每日1次，口服

[+ 添加第2种用药]

（重复第3步的录入界面，序号递增）
```

### 第五步：完成确认
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      糖尿病肾病用药详情录入完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 已录入 2 种用药：
  1. 阿司匹林 100mg/片，每日1次，口服
  2. 厄贝沙坦 150mg/片，每日1次，口服

[修改用药信息]  [确认完成]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

继续录入下一个疾病...
```

## 💻 数据库设计

### 1. 主表字段（如diabetes_complications）
```sql
-- 是否用药字段
nephropathy_medication BOOLEAN  -- 是否用药

-- 用药详情关联字段（JSON格式存储medication_id列表）
nephropathy_medication_details JSON  -- 关联medication_list表的记录ID
-- 示例值: ["med_001", "med_002"]
```

### 2. 用药清单表（medication_list）
```sql
-- 基础关联信息
medication_id VARCHAR(32)      -- 主键
patient_id VARCHAR(32)         -- 患者ID
medication_category TINYINT    -- 用药分类（2=糖尿病肾病用药）
source_table VARCHAR(50)       -- 来源表（diabetes_complications）  
source_field VARCHAR(50)       -- 来源字段（nephropathy_medication_details）

-- 详细用药信息
drug_name VARCHAR(100)         -- 药品通用名
brand_name VARCHAR(100)        -- 商品名
specification VARCHAR(50)      -- 规格
dosage_amount DECIMAL(8,2)     -- 单次剂量
dosage_unit VARCHAR(20)        -- 剂量单位
frequency TINYINT              -- 服用频次
administration_route TINYINT   -- 给药途径

-- 时间管理
start_date DATE                -- 开始用药日期
end_date DATE                  -- 停药日期
is_current BOOLEAN             -- 是否目前在用

-- 效果评估
therapeutic_effect TINYINT     -- 治疗效果
side_effects JSON              -- 不良反应
```

### 3. 关联关系管理（medication_associations）
```sql
-- 建立用药与疾病的明确关联
association_id VARCHAR(32)     -- 主键
patient_id VARCHAR(32)         -- 患者ID
medication_id VARCHAR(32)      -- 用药记录ID
source_table VARCHAR(50)       -- 来源疾病表
medication_purpose VARCHAR(100) -- 用药目的（如：糖尿病肾病治疗）
is_primary_treatment BOOLEAN   -- 是否主要治疗药物
```

## 🎯 技术实现要点

### 1. 前端交互逻辑
```javascript
// 伪代码
function handleMedicationStatus(diseaseField, medicationField) {
  if (medicationField.value === true) {
    // 显示用药详情录入界面
    showMedicationDetailsForm({
      diseaseType: diseaseField.name,
      onAddMedication: (medicationData) => {
        // 保存到medication_list表
        saveMedicationToDatabase(medicationData);
        // 更新关联字段的medication_details JSON
        updateMedicationDetailsField(diseaseField, medicationData.id);
        // 显示继续添加选项
        showContinueAddingDialog();
      }
    });
  } else {
    // 隐藏用药详情，清空相关数据
    hideMedicationDetailsForm();
    clearMedicationDetailsField(diseaseField);
  }
}

function showContinueAddingDialog() {
  showDialog({
    message: "是否还有其他用药需要添加？",
    buttons: [
      { text: "添加下一种用药", action: () => showNextMedicationForm() },
      { text: "录入完成", action: () => completeMedicationEntry() }
    ]
  });
}
```

### 2. 数据保存逻辑
```javascript
// 保存用药详情的完整流程
async function saveMedicationDetails(diseaseTable, diseaseField, medications) {
  try {
    // 1. 保存所有用药到medication_list表
    const medicationIds = [];
    for (let med of medications) {
      const medRecord = await saveMedication({
        ...med,
        medication_category: getMedicationCategory(diseaseField),
        source_table: diseaseTable,
        source_field: diseaseField + '_details'
      });
      medicationIds.push(medRecord.id);
      
      // 2. 建立关联关系
      await saveMedicationAssociation({
        medication_id: medRecord.id,
        source_table: diseaseTable,
        medication_purpose: getMedicationPurpose(diseaseField),
        is_primary_treatment: med.isPrimary
      });
    }
    
    // 3. 更新疾病表的medication_details字段
    await updateDiseaseTable(diseaseTable, {
      [diseaseField + '_details']: JSON.stringify(medicationIds)
    });
    
  } catch (error) {
    console.error('保存用药详情失败:', error);
  }
}
```

### 3. 数据验证规则
```javascript
const validationRules = {
  // 必填字段验证
  required: ['drug_name', 'specification', 'dosage_amount', 'frequency', 'administration_route'],
  
  // 条件必填
  conditionalRequired: {
    'brand_name': null,  // 可选
    'contact_info': (data) => data.participate_project === true,  // 参与项目时必填
    'end_date': (data) => data.is_current === false  // 已停药时必填停药日期
  },
  
  // 逻辑一致性
  consistency: {
    startDateBeforeEndDate: (data) => {
      if (data.start_date && data.end_date) {
        return new Date(data.start_date) <= new Date(data.end_date);
      }
      return true;
    }
  }
};
```

## 📊 统计分析支持

### 1. 用药统计查询
```sql
-- 按疾病统计用药情况
SELECT 
  medication_category,
  COUNT(*) as medication_count,
  COUNT(DISTINCT patient_id) as patient_count
FROM medication_list 
WHERE source_table IN ('diabetes_complications', 'other_diseases')
GROUP BY medication_category;

-- 分析常用药物组合
SELECT 
  source_field,
  drug_name,
  COUNT(*) as usage_count,
  AVG(therapeutic_effect) as avg_effectiveness
FROM medication_list ml
JOIN medication_associations ma ON ml.medication_id = ma.medication_id
GROUP BY source_field, drug_name
ORDER BY usage_count DESC;
```

### 2. 用药依从性分析
```sql
-- 分析用药依从性和治疗效果
SELECT 
  medication_purpose,
  adherence_level,
  therapeutic_effect,
  COUNT(*) as case_count
FROM medication_list ml
JOIN medication_associations ma ON ml.medication_id = ma.medication_id
WHERE adherence_level IS NOT NULL
GROUP BY medication_purpose, adherence_level, therapeutic_effect
ORDER BY medication_purpose, adherence_level;
```

## 🎨 用户体验优化

### 1. 智能提示功能
- **药物搜索**：支持通用名、商品名的模糊搜索
- **规格联想**：根据选择的药物自动提示常见规格
- **剂量建议**：基于药物和规格提供推荐剂量
- **频次优化**：根据药物特性建议最佳服用频次

### 2. 数据质量控制
- **重复检查**：防止录入相同药物
- **相互作用提醒**：检测潜在的药物相互作用
- **剂量合理性**：验证剂量是否在安全范围内
- **完整性验证**：确保必填信息完整

### 3. 便捷操作
- **快速录入**：常用药物的快捷选择模板
- **批量操作**：支持相似药物的批量录入
- **历史参考**：显示该患者的历史用药记录
- **打印输出**：支持用药清单的打印输出

这种设计确保了从D2A到H7所有疾病的用药详情都能得到完整、准确的记录，同时提供良好的用户体验和数据管理功能。