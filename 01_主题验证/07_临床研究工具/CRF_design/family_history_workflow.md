# 家族史循环录入逻辑设计

## 📋 整体设计理念

家族史采用**"主控制表 + 详情表"**的设计模式，支持用户循环添加多个患有相同疾病的家属，直到所有相关家属都录入完毕。

## 🗃️ 数据表结构

### 1. 主控制表：`family_history_control`
- **作用**：控制整个家族史录入流程
- **核心字段**：
  - `has_diabetes_family`：家族中有无糖尿病患者（必选）
  - `has_hypertension_family`：家族中有无高血压患者（必选）
  - `has_coronary_family`：家族中有无冠心病患者（必选）
  - `diabetes_entry_completed`：糖尿病家族史录入完成确认
  - `total_diabetes_members`：已录入的糖尿病家属总数（自动计算）

### 2. 详情表：`family_diabetes_history` / `family_hypertension_history` / `family_coronary_history`
- **作用**：存储每个家属的详细信息
- **支持**：同一患者的多条家属记录
- **核心字段**：
  - `member_sequence`：家属序号（自动递增）
  - `relationship`：与患者关系
  - `member_gender`、`member_age`：家属基本信息
  - 疾病特定信息（类型、发病年份、治疗情况等）

## 🔄 用户界面录入流程

### 第一步：疾病筛查
```
问题：您的家族中有糖尿病患者吗？
选项：□ 有  □ 无
```

**如果选择"无"**：
- 跳过该疾病的所有后续问题
- 进入下一个疾病的筛查

**如果选择"有"**：
- 进入该疾病的家属详细录入流程

### 第二步：第一位家属信息录入
```
现在请填写第1位糖尿病家属的信息：

与您的关系：[下拉选择] ▼
  □ 祖父母
  □ 外祖父母  
  □ 父母
  □ 父亲兄弟姐妹
  □ 母亲兄弟姐妹
  □ 自己的兄弟姐妹
  □ 子女

家属性别：□ 男  □ 女
家属年龄：[___] 岁

糖尿病类型：[下拉选择] ▼
发病年份：[____] 年
诊断时年龄：[___] 岁
是否有并发症：□ 否  □ 视网膜病变  □ 肾病  □ 其他并发症
目前治疗情况：[下拉选择] ▼

是否愿意参与项目：□ 是  □ 否
（如选择"是"）
  联系人姓名：[____________]
  联系电话：[____________]
  联系人关系：[____________]

备注：[文本框]

[保存第1位家属信息]
```

### 第三步：循环录入控制
```
第1位糖尿病家属信息已保存。

您的家族中还有其他糖尿病患者需要录入吗？

□ 是，继续添加下一位家属
□ 否，糖尿病家族史录入完成

[继续添加] [录入完成]
```

**如果选择"继续添加"**：
- 系统自动递增序号：`member_sequence = 2`
- 显示"现在请填写第2位糖尿病家属的信息"
- 重复上述录入表单
- 继续循环直到用户选择"录入完成"

**如果选择"录入完成"**：
- 系统设置 `diabetes_entry_completed = true`
- 自动计算 `total_diabetes_members` 总数
- 进入下一个疾病（高血压）的筛查流程

### 第四步：进度提示与确认
```
✅ 糖尿病家族史录入完成
   已录入 3 位糖尿病家属

现在开始录入高血压家族史...

您的家族中有高血压患者吗？
□ 有  □ 无
```

## 💻 技术实现要点

### 1. 数据库设计
```sql
-- 主控制表
INSERT INTO family_history_control (patient_id, has_diabetes_family, diabetes_entry_completed)
VALUES ('patient_123', true, false);

-- 详情表支持多条记录
INSERT INTO family_diabetes_history (patient_id, member_sequence, relationship, diabetes_type, ...)
VALUES 
  ('patient_123', 1, 3, 2, ...),  -- 第1位家属：父母，2型糖尿病
  ('patient_123', 2, 6, 1, ...),  -- 第2位家属：兄弟姐妹，1型糖尿病
  ('patient_123', 3, 1, 3, ...);  -- 第3位家属：祖父母，不清楚类型
```

### 2. 前端交互逻辑
```javascript
// 伪代码
function addFamilyMember(diseaseType) {
  let currentSequence = getCurrentMemberCount(diseaseType) + 1;
  
  showMemberForm({
    title: `现在请填写第${currentSequence}位${diseaseType}家属的信息`,
    sequence: currentSequence,
    onSave: (memberData) => {
      saveMemberData(memberData);
      showContinueDialog();
    }
  });
}

function showContinueDialog() {
  showDialog({
    message: "您的家族中还有其他患者需要录入吗？",
    buttons: [
      {
        text: "是，继续添加",
        action: () => addFamilyMember(currentDiseaseType)
      },
      {
        text: "否，录入完成",
        action: () => {
          markEntryCompleted(currentDiseaseType);
          moveToNextDisease();
        }
      }
    ]
  });
}
```

### 3. 数据验证规则
- **必填字段验证**：关系、疾病类型必须填写
- **逻辑一致性验证**：参与项目为"是"时，联系信息必填
- **重复性检查**：同一关系的家属不应重复录入相同疾病
- **完整性验证**：确保用户明确表示录入完成

### 4. 用户体验优化
- **进度提示**：显示当前录入第几位家属
- **数据回显**：已录入家属的信息可查看和修改
- **快速录入**：常见关系和疾病类型的快捷选择
- **暂存功能**：支持未完成录入的暂时保存

## 🎯 业务场景示例

### 场景1：多个糖尿病家属
```
患者张三的家族史：
1. 父亲 - 2型糖尿病 - 50岁发病 - 有肾病并发症
2. 母亲 - 2型糖尿病 - 55岁发病 - 无并发症  
3. 哥哥 - 1型糖尿病 - 25岁发病 - 愿意参与项目
4. 外婆 - 糖尿病类型不清楚 - 发病年份不详

录入流程：选择"有糖尿病家属" → 录入父亲信息 → 继续添加 → 录入母亲信息 → 
继续添加 → 录入哥哥信息 → 继续添加 → 录入外婆信息 → 录入完成
```

### 场景2：无家族史
```
患者李四的家族史：
糖尿病：无 → 直接跳过
高血压：无 → 直接跳过  
冠心病：无 → 直接跳过
整个家族史部分快速完成
```

### 场景3：混合情况
```
患者王五的家族史：
糖尿病：有（录入2位家属）
高血压：有（录入1位家属）
冠心病：无

三个疾病分别处理，支持不同疾病的不同家属数量
```

## 📊 统计和分析支持

### 数据统计查询
```sql
-- 统计每个患者的家族史情况
SELECT 
  p.patient_id,
  p.name,
  fhc.total_diabetes_members,
  fhc.total_hypertension_members,
  fhc.total_coronary_members,
  (fhc.total_diabetes_members + fhc.total_hypertension_members + fhc.total_coronary_members) as total_family_patients
FROM patient_basic_info p
LEFT JOIN family_history_control fhc ON p.patient_id = fhc.patient_id;

-- 分析家族疾病聚集性
SELECT 
  relationship,
  COUNT(*) as member_count,
  AVG(diagnosis_age) as avg_diagnosis_age
FROM family_diabetes_history
WHERE diagnosis_age IS NOT NULL
GROUP BY relationship
ORDER BY member_count DESC;
```

这种设计既保证了数据的完整性和灵活性，又提供了良好的用户体验，支持真实临床场景中复杂的家族史录入需求。