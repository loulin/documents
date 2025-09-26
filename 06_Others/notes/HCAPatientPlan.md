## 第四部分：用于v0.dev的原型开发提示词

### Prompt 1: 患者风险评估与个性化管理方案生成器

```
Design a comprehensive, single-page web application for medical professionals to conduct real-time patient risk assessment and generate personalized long-term management plans. The UI should be clean, intuitive, and responsive, optimized for use during patient consultations (e.g., on a tablet or desktop).

**Page Title:** "患者风险评估与管理"

**Layout:** The page should be divided into two main sections: a left-hand input form and a right-hand dynamic output/summary panel.

**Left Section: Patient Data Input Form**
This section should allow medical professionals to input patient data based on the provided risk stratification framework. Use clear labels, appropriate input types (text fields, dropdowns, radio buttons, checkboxes), and logical grouping.

1.  **基本信息与诊断类型 (Basic Info & Diagnosis Type):**
    *   Input field for "患者姓名 (Patient Name)".
    *   Dropdown/Radio buttons for "诊断类型 (Diagnosis Type)" with options: "健康 (Healthy)", "糖尿病前期 (Pre-diabetes)", "1型糖尿病 (Type 1 Diabetes)", "2型糖尿病 (Type 2 Diabetes)", "妊娠糖尿病 (Gestational Diabetes)", "特殊类型糖尿病 (Special Type Diabetes)". (This selection should influence the base score and potentially dynamic fields).

2.  **血糖状态 (Glycemic Status) - Based on First Part 1.1:**
    *   Input fields for: "HbA1c (%)", "TIR (%)", "TBR (%)", "CGM 血糖变异性 (CV%)", "CGM 数据完整性 (%)". Include units where applicable.

3.  **并发症与合并症 (Complications & Comorbidities) - Based on First Part 1.3:**
    *   **心脑血管与肾脏系统 (Cardiovascular & Renal System):** Checkboxes for: "心肌梗死史 (History of Myocardial Infarction)", "缺血性脑卒中史 (History of Ischemic Stroke)", "心脏支架/搭桥手术史 (History of Cardiac Stent/Bypass Surgery)", "心力衰竭 (Heart Failure)", "外周动脉疾病 (Peripheral Artery Disease)", "终末期肾病/透析 (ESRD/Dialysis)", "eGFR 45-59", "eGFR 30-44", "UACR 30-300 mg/g", "UACR > 300 mg/g".
    *   **其他合并症 (Other Comorbidities):** Checkboxes for: "高血压未达标 (Uncontrolled Hypertension)", "高血脂未达标 (Uncontrolled Dyslipidemia)", "非酒精性脂肪肝 (NAFLD)", "糖尿病视网膜病变 (Diabetic Retinopathy)", "糖尿病周围神经病变 (Diabetic Peripheral Neuropathy)".

4.  **个体背景因素 (Individual Background) - Based on First Part 1.4:**
    *   Radio buttons/Dropdown for "年龄 (Age)": "< 45岁", "45-64岁", "≥ 65岁".
    *   Radio buttons/Dropdown for "糖尿病病程 (Diabetes Duration)": "< 5年", "5-10年", "> 10年".
    *   Checkbox for "心血管疾病家族史 (Family History of CVD)".

5.  **生活方式与行为 (Lifestyle & Behavior) - Based on First Part 1.5:**
    *   Radio buttons/Dropdowns for: "体力活动 (Physical Activity)", "饮食习惯 (Diet Habits)", "吸烟状况 (Smoking Status)", "睡眠质量 (Sleep Quality)", "用药依从性 (Medication Adherence)". Each with the options as described in the document.

6.  **特殊人群额外考量 (Special Population Considerations) - Based on Second Part:**
    *   Radio buttons to select if the patient is: "妊娠期 (Pregnant)", "儿童与青少年 (<18岁) (Child/Adolescent)", "老年人 (≥65岁) (Elderly)", "运动员/长期运动人员 (Athlete/Long-term Exerciser)".
    *   **Dynamic Fields:** If a special population is selected, dynamically display relevant additional input fields (e.g., for Pregnancy: Gestational Week, specific GDM targets; for Elderly: Functional Status, Polypharmacy; for Athlete/Long-term Exerciser: Exercise Type, Intensity, Duration, Pre/Post-exercise Glucose Levels, Insulin/Medication Adjustment). These fields should influence the risk calculation and management plan.

**Right Section: Real-time Risk & Personalized Management Plan Output**
This section should dynamically update as the medical professional inputs data, providing immediate feedback and actionable plans.

1.  **实时风险概览 (Real-time Risk Overview):**
    *   Prominent display of "当前风险总分 (Current Risk Score)" (numeric value, e.g., "75").
    *   "计算风险等级 (Calculated Risk Level)" (e.g., "极高风险 (Extremely High Risk)") with clear color-coding (e.g., Green for Low, Yellow for Medium, Orange for High, Red for Extremely High).
    *   List of "已应用风险乘数 (Applied Risk Multipliers)" (e.g., "ASCVD: x2.0", "终末期肾病: x1.8").

2.  **个性化管理方案 (Personalized Management Plan):**
    *   **总体建议/摘要 (Overall Recommendation/Summary):** A concise, dynamically generated summary of the patient's primary risk areas and the overarching goals of the management plan.
    *   **建议日程安排/来院随访 (Suggested Schedule/Clinic Follow-ups):**
        *   A clear, actionable list of recommended appointments and their suggested timeframes (e.g., "心血管内科会诊 (Cardiology Consult) - 建议2周内完成", "年度眼科检查 (Annual Ophthalmology Exam) - 建议1个月内完成", "肾内科随访 (Nephrology Follow-up) - 建议3个月内完成").
        *   Each item should include a suggested due date/timeframe.
    *   **随访内容要点 (Key Follow-up Content):**
        *   For each suggested appointment, list the key discussion points, assessments, or tests to be performed (e.g., "心血管内科: 讨论SGLT2i/GLP1RA用药, 复查心脏超声结果", "眼科: 眼底照相, 视力检查", "肾内科: 复查eGFR/UACR趋势, 药物调整").
    *   **居家管理任务 (Home Management Tasks):**
        *   An actionable checklist for the patient to follow at home, dynamically generated based on their risk profile and lifestyle factors (e.g., "每日监测血糖 (餐前、餐后2小时)", "严格遵循低碳饮食，限制加工食品摄入", "目标每日快走30分钟，每周5次", "按医嘱服用所有药物，不漏服").
        *   **用药建议 (Medication Recommendations):** A section providing general medication class recommendations based on risk factors and comorbidities (e.g., "建议考虑SGLT2抑制剂或GLP-1受体激动剂，以改善心肾结局", "建议调整降压药物，目标血压<130/80mmHg"). This should be high-level guidance, not specific drug names or dosages.
        *   Each task should be clear, concise, and measurable where possible.

**General Design Principles:**
*   **Real-time Interaction:** All calculations and management plan generations should happen instantly as data is entered/changed.
*   **Clarity & Readability:** Use appropriate font sizes, spacing, and visual hierarchy for medical professionals.
*   **Error Handling/Validation:** (Implicitly) Ensure input fields have basic validation (e.g., numeric inputs for percentages).
*   **Professional Aesthetic:** Clean, modern, and trustworthy design suitable for a healthcare setting.
*   **Print/Export Option:** (Optional but beneficial) A button to print or export the generated management plan.
```

---

## 第五部分：参考文献与原始纪要

---

## 第六部分：前端原型数据录入字段与逻辑细化

本部分旨在为前端原型开发提供详细的数据录入字段定义、交互逻辑和评分计算规则，确保未受过糖尿病专业训练的医护人员也能便捷、准确地完成患者风险评估。

### 1. 患者基本信息

* **字段:** `patientName`

  * **类型:** 文本输入框
  * **标签:** 患者姓名
  * **说明:** 用于记录患者姓名。
* **字段:** `dateOfBirth`

  * **类型:** 日期选择器
  * **标签:** 出生日期
  * **说明:** 用于记录患者出生日期，前端根据此日期自动计算年龄，影响后续条件显示和特殊人群判断。
* **字段:** `gender`

  * **类型:** 单选框/下拉选择
  * **标签:** 性别
  * **选项:** 男, 女
  * **说明:** 影响妊娠期相关评估项的显示。
* **字段:** `diagnosisType`

  * **类型:** 单选框/下拉选择
  * **标签:** 诊断类型
  * **选项:** 健康/未诊断, 糖尿病前期, 1型糖尿病, 2型糖尿病, 妊娠糖尿病, 特殊类型糖尿病
  * **说明:** 影响基础分计算和大量糖尿病相关评估项的条件显示。
* **字段:** `isAthlete`

  * **类型:** 复选框
  * **标签:** 是否为运动员/长期运动人员
  * **说明:** 勾选后，动态显示“运动员/长期运动人员”相关的评估项。

### 2. 血糖状态 (Glycemic Status) - 动态显示与计算

* **条件:** 仅当 `diagnosisType` 为“健康/未诊断”、“糖尿病前期”、“1型糖尿病”、“2型糖尿病”、“妊娠糖尿病”、“特殊类型糖尿病”时显示。
* **字段:** `hasCGMData`

  * **类型:** 复选框
  * **标签:** 是否有CGM数据 (勾选后可自动读取或手动填写CGM相关指标)
  * **说明:** 勾选此项表示可获取CGM数据，CGM相关指标将优先通过接口自动计算。若未勾选或接口不可用，则允许手动填写。
* **字段:** `hba1c`

  * **类型:** 数字输入框 (百分比)
  * **标签:** HbA1c (%)
  * **评分逻辑:**
    * `< 7.0%`: 0分
    * `7.0% <= HbA1c < 8.0%`: 5分
    * `8.0% <= HbA1c < 9.0%`: 15分
    * `>= 9.0%`: 20分
* **字段:** `tir`

  * **类型:** 数字输入框 (百分比) / 自动计算 (若有CGM数据)
  * **标签:** TIR (Time in Range) (%)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算，若无CGM数据或自动计算失败，则允许手动填写。
  * **评分逻辑:**
    * `> 70%`: 0分
    * `50% - 70%`: 10分
    * `< 50%`: 20分
* **字段:** `tbr`

  * **类型:** 数字输入框 (百分比) / 自动计算 (若有CGM数据)
  * **标签:** TBR (Time Below Range) (%)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算，若无CGM数据或自动计算失败，则允许手动填写。
  * **评分逻辑:**
    * `< 1%`: 0分
    * `1% - 4%`: 10分
    * `> 4%`: 25分
* **字段:** `cgmGV`

  * **类型:** 数字输入框 (百分比) / 自动计算 (若有CGM数据)
  * **标签:** CGM 血糖变异性 (CV%)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算，若无CGM数据或自动计算失败，则允许手动填写。
  * **评分逻辑:**
    * `CV < 36%`: 0分
    * `CV 36% - 45%`: 5分
    * `CV > 45%`: 10分
* **字段:** `mage`

  * **类型:** 数字输入框 (mmol/L) / 自动计算 (若有CGM数据)
  * **标签:** MAGE (Mean Amplitude of Glycemic Excursions)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算，若无CGM数据或自动计算失败，则允许手动填写。
  * **评分逻辑:**
    * `< 3.9 mmol/L`: 0分
    * `3.9 - 5.0 mmol/L`: 5分
    * `> 5.0 mmol/L`: 10分
* **字段:** `modd`

  * **类型:** 数字输入框 (mmol/L) / 自动计算 (若有CGM数据)
  * **标签:** MODD (Mean of Daily Differences)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算，若无CGM数据或自动计算失败，则允许手动填写。
  * **评分逻辑:**
    * `< 2.0 mmol/L`: 0分
    * `2.0 - 4.0 mmol/L`: 5分
    * `> 4.0 mmol/L`: 10分
* **字段:** `lbgi`

  * **类型:** 数字输入框 / 自动计算 (若有CGM数据)
  * **标签:** LBGI (Low Blood Glucose Index)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算，若无CGM数据或自动计算失败，则允许手动填写。
  * **评分逻辑:**
    * `< 2.5`: 0分
    * `2.5 - 5.0`: 5分
    * `> 5.0`: 10分
* **字段:** `hbgi`

  * **类型:** 数字输入框 / 自动计算 (若有CGM数据)
  * **标签:** HBGI (High Blood Glucose Index)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算，若无CGM数据或自动计算失败，则允许手动填写。
  * **评分逻辑:**
    * `≤ 4.5`: 0分
    * `4.5 - 9.0`: 5分
    * `> 9.0`: 10分
* **字段:** `gri`

  * **类型:** 单选框/下拉选择 / 自动计算 (若有CGM数据)
  * **标签:** 综合血糖质量指标
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。优先通过CGM数据自动计算(支持Dexcom GRI、FreeStyle等各品牌质量指标)，若无CGM数据或自动计算失败，则允许手动填写。
  * **选项:** 低风险, 中风险, 高风险
  * **评分逻辑:**
    * `低风险` (如Dexcom GRI < 20, 或其他品牌等效指标): 0分
    * `中风险` (如Dexcom GRI 20-60, 或其他品牌等效指标): 5分
    * `高风险` (如Dexcom GRI > 60, 或其他品牌等效指标): 10分
* **字段:** `severeHypoglycemiaHistory`

  * **类型:** 复选框
  * **标签:** 严重低血糖事件史
  * **评分逻辑:** 勾选则 +25分。

### 3. 并发症与合并症 (Complications & Comorbidities) - 动态显示与计算

* **心脑血管系统 (Cardiovascular System) - 条件:** 仅当根据 `dateOfBirth` 计算的年龄 >= 18岁时显示。
* **字段:** `hasMI`

  * **类型:** 复选框
  * **标签:** 是否有过心肌梗死 (心脏病发作)？
  * **评分逻辑:** 勾选则总分 x 2.0 (乘数)。
* **字段:** `hasStroke`

  * **类型:** 复选框
  * **标签:** 是否有过缺血性脑卒中 (中风)？
  * **评分逻辑:** 勾选则总分 x 2.0 (乘数)。
* **字段:** `hasCardiacSurgery`

  * **类型:** 复选框
  * **标签:** 是否做过心脏支架/搭桥手术？
  * **评分逻辑:** 勾选则总分 x 2.0 (乘数)。
* **字段:** `hasHeartFailure`

  * **类型:** 复选框
  * **标签:** 是否诊断为心力衰竭 (心衰)？
  * **评分逻辑:** 勾选则总分 x 1.8 (乘数)。
* **字段:** `hasPAD`

  * **类型:** 复选框
  * **标签:** 是否诊断为外周动脉疾病 (如腿部血管堵塞)？
  * **评分逻辑:** 勾选则 +15分。
* **肾脏系统 (Renal System) - 始终显示**
* **字段:** `hasESRD`

  * **类型:** 复选框
  * **标签:** 是否处于终末期肾病 (尿毒症) 或正在透析？
  * **评分逻辑:** 勾选则总分 x 1.8 (乘数)。
* **字段:** `eGFR`

  * **类型:** 数字输入框 (ml/min/1.73m²)
  * **标签:** eGFR (肾小球滤过率)
  * **评分逻辑:**
    * `>= 60`: 0分 (正常或轻度下降，无额外风险分)
    * `45-59`: +15分
    * `30-44`: +20分
    * `< 30`: +25分 (更严重的肾功能下降，增加风险分)
* **字段:** `uacr`

  * **类型:** 数字输入框 (mg/g)
  * **标签:** UACR (尿微量白蛋白/肌酐比)
  * **评分逻辑:**
    * `< 30 mg/g`: 0分 (正常范围，无额外风险分)
    * `30-300 mg/g`: +10分
    * `> 300 mg/g`: +20分
* **其他合并症 (Other Comorbidities) - 始终显示**
  * **说明:** 此部分评估患者可能存在的其他常见合并症，这些合并症会增加糖尿病管理的复杂性和整体风险。
* **字段:** `hasHypertensionDiagnosis`

  * **类型:** 复选框
  * **标签:** 是否诊断为高血压
  * **说明:** 勾选此项表示患者已诊断高血压。
* **字段:** `systolicBP`

  * **类型:** 数字输入框 (mmHg)
  * **标签:** 收缩压
* **字段:** `diastolicBP`

  * **类型:** 数字输入框 (mmHg)
  * **标签:** 舒张压
* **内部计算逻辑 (高血压未达标):**

  * **条件:** 如果 `systolicBP` > 130 或 `diastolicBP` > 80，则视为“血压未达标”。
  * **评分逻辑:**
    * 如果“血压未达标”且 `hasHypertensionDiagnosis` 勾选，则 +10分。
    * 如果 `systolicBP` <= 130 且 `diastolicBP` <= 80，则 0分 (血压达标或正常，无额外风险分)。
* **字段:** `hasDyslipidemiaDiagnosis`

  * **类型:** 复选框
  * **标签:** 是否诊断为高血脂
  * **说明:** 勾选此项表示患者已诊断高血脂。
* **字段:** `ldlC`

  * **类型:** 数字输入框 (mmol/L 或 mg/dL)
  * **标签:** LDL-C (低密度脂蛋白)
* **内部计算逻辑 (高血脂未达标):**

  * **条件:** 根据LDL-C数值和患者风险等级（需后端计算或前端预设阈值，例如：对于一般成年糖尿病患者，LDL-C目标通常为 < 2.6 mmol/L 或 < 100 mg/dL；对于高风险患者，目标可能更低）判断是否“未达标”。
  * **评分逻辑:** 如果“LDL-C未达标”且 `hasDyslipidemiaDiagnosis` 勾选，则 +10分。
* **字段:** `hasNAFLD`

  * **类型:** 复选框
  * **标签:** 是否诊断为非酒精性脂肪肝
  * **评分逻辑:** 勾选则 +5分。
* **字段:** `hasDR`

  * **类型:** 复选框
  * **标签:** 是否诊断为糖尿病视网膜病变
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **评分逻辑:** 勾选则 +5分。
* **字段:** `hasDPN`

  * **类型:** 复选框
  * **标签:** 是否诊断为糖尿病周围神经病变 (如手脚麻木、疼痛)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **评分逻辑:** 勾选则 +5分。

### 4. 个体背景因素 (Individual Background) - 始终显示

* **字段:** `diabetesDuration`

  * **类型:** 数字输入框 (年)
  * **标签:** 糖尿病病程
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **评分逻辑:**
    * `< 5年`: 0分
    * `5-10年`: 5分
    * `> 10年`: 10分
* **字段:** `familyHistoryCVD`

  * **类型:** 复选框
  * **标签:** 心血管疾病家族史
  * **评分逻辑:** 勾选则 +5分。

### 5. 特殊人群额外考量 (Special Population Considerations) - 动态显示与计算

* **条件:** 仅当 `diagnosisType` 为"妊娠糖尿病"或根据 `dateOfBirth` 计算的年龄 < 18 或根据 `dateOfBirth` 计算的年龄 >= 65 或 `isAthlete` 勾选时，显示相应特殊人群的评估项。

#### 5.1. 妊娠期 (GDM 及合并糖尿病的妊娠) - 条件：`diagnosisType` 为“妊娠糖尿病”且 `gender` 为“女”

* **字段:** `lastMenstrualPeriodDate`

  * **类型:** 日期选择器
  * **标签:** 末次月经日期
  * **说明:** 用于记录末次月经日期，前端根据此日期自动计算孕周，并判断孕期阶段，影响血糖目标。
* **字段:** `fastingGlucose`

  * **类型:** 数字输入框 (mmol/L)
  * **标签:** 空腹血糖
  * **评分逻辑:** 根据孕周和血糖目标进行评分。
* **字段:** `postMeal1hrGlucose`

  * **类型:** 数字输入框 (mmol/L)
  * **标签:** 餐后1小时血糖
  * **评分逻辑:** 根据孕周和血糖目标进行评分。
* **字段:** `postMeal2hrGlucose`

  * **类型:** 数字输入框 (mmol/L)
  * **标签:** 餐后2小时血糖
  * **评分逻辑:** 根据孕周和血糖目标进行评分。
* **字段:** `pregnancyTIR`

  * **类型:** 数字输入框 (百分比) / 自动计算 (若有CGM数据)
  * **标签:** 妊娠期 TIR (63-140mg/dL) (%)
  * **条件:** 仅当 `diagnosisType` 为妊娠糖尿病且有CGM数据时显示。
  * **评分逻辑:**
    * `>= 85%`: 0分 (目标范围，无额外风险分)
    * `70% <= TIR < 85%`: +10分
    * `< 70%`: +20分
* **字段:** `pregnancyTBR`

  * **类型:** 数字输入框 (百分比) / 自动计算 (若有CGM数据)
  * **标签:** 妊娠期 TBR (%)
  * **条件:** 仅当 `diagnosisType` 为妊娠糖尿病且有CGM数据时显示。
  * **评分逻辑:**
    * `< 1%`: 0分 (目标范围，无额外风险分)
    * `1% <= TBR <= 4%`: +10分
    * `> 4%`: +20分
* **字段:** `pregnancyTAR`

  * **类型:** 数字输入框 (百分比) / 自动计算 (若有CGM数据)
  * **标签:** 妊娠期 TAR (%)
  * **条件:** 仅当 `diagnosisType` 为妊娠糖尿病且有CGM数据时显示。
  * **评分逻辑:**
    * `< 25%`: 0分 (目标范围，无额外风险分)
    * `>= 25%`: +15分
* **字段:** `prePregnancyDiabetes`

  * **类型:** 复选框
  * **标签:** 孕前糖尿病 (1型/2型)
  * **评分逻辑:** 勾选则 +15分。
* **字段:** `hasHypertensionPreeclampsia`

  * **类型:** 复选框
  * **标签:** 合并高血压/子痫前期
  * **评分逻辑:** 勾选则 +20分。
* **字段:** `historyMacrosomiaPolyhydramnios`

  * **类型:** 复选框
  * **标签:** 巨大儿/羊水过多史
  * **评分逻辑:** 勾选则 +10分。
* **字段:** `fetalGrowthRestriction`

  * **类型:** 复选框
  * **标签:** 胎儿生长受限 (FGR)
  * **评分逻辑:** 勾选则 +15分。
* **字段:** `historyFetalMalformation`

  * **类型:** 复选框
  * **标签:** 胎儿畸形史
  * **评分逻辑:** 勾选则 +20分。

#### 5.2. 儿童与青少年 (计算年龄 < 18岁) - 条件：根据 `dateOfBirth` 计算的年龄 < 18

* **字段:** `childAgeGroup`

  * **类型:** 单选框/下拉选择
  * **标签:** 年龄/发育阶段
  * **选项:** 学龄前 (<6岁), 学龄期 (6-12岁), 青春期 (13-18岁)
  * **评分逻辑:** 对应选项的分值 (高风险基础, 中风险, 高风险基础)。
* **字段:** `childTIR`

  * **类型:** 数字输入框 (百分比)
  * **标签:** TIR (%)
  * **条件:** 仅当有CGM数据时显示。
  * **评分逻辑:**
    * `> 70%`: 0分
    * `50-70%`: +10分
    * `< 50%`: +20分
* **字段:** `childTBR`

  * **类型:** 数字输入框 (百分比)
  * **标签:** TBR (%)
  * **条件:** 仅当有CGM数据时显示。
  * **评分逻辑:**
    * `> 4%`: +20分
* **字段:** `childHba1c`

  * **类型:** 数字输入框 (百分比)
  * **标签:** HbA1c (%)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **评分逻辑:**
    * `> 9%`: +15分
* **字段:** `selfManagementAbility`

  * **类型:** 单选框/下拉选择
  * **标签:** 自我管理能力
  * **选项:** 家长管理, 自主管理过渡期, 可自主管理
  * **评分逻辑:** 对应选项的分值 (视家长能力而定, +10分, 0分)。

#### 5.3. 老年人 (计算年龄 ≥ 65岁) - 条件：根据 `dateOfBirth` 计算的年龄 >= 65

* **字段:** `healthStatusElderly`

  * **类型:** 单选框/下拉选择
  * **标签:** 健康状况
  * **选项:** 健康 (认知/功能完好), 中等复杂 (合并多种慢性病), 非常复杂 (功能受限/临终)
  * **评分逻辑:** 对应选项的分值 (标准同一般成人, 高风险基础, 极高风险基础)。
* **字段:** `functionalStatus`

  * **类型:** 单选框/下拉选择
  * **标签:** 功能状态
  * **选项:** 可自理, 日常生活需部分协助 (ADL受限), 完全依赖他人
  * **评分逻辑:** 对应选项的分值 (0分, +10分, +20分)。
* **字段:** `elderlyHypoglycemiaHistory`

  * **类型:** 复选框
  * **标签:** 严重低血糖事件史
  * **评分逻辑:** 勾选则 +25分。
* **字段:** `elderlyTBR`

  * **类型:** 数字输入框 (百分比)
  * **标签:** TBR (%)
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **评分逻辑:**
    * `> 1%`: +15分
* **字段:** `polypharmacy`

  * **类型:** 数字输入框
  * **标签:** 多重用药 (药物种类数量)
  * **评分逻辑:**
    * `≥ 5种药物`: +5分

#### 5.4. 运动员/长期运动人员 - 条件：`isAthlete` 勾选

* **字段:** `exerciseTypeIntensity`

  * **类型:** 单选框/下拉选择
  * **标签:** 运动类型与强度
  * **选项:** 高强度间歇训练 (HIIT) / 耐力运动 (马拉松、长距离骑行), 中等强度有氧运动 / 力量训练
  * **评分逻辑:** 对应选项的分值 (+10分, +5分)。
* **字段:** `exerciseFrequencyDuration`

  * **类型:** 单选框/下拉选择
  * **标签:** 运动频率与持续时间
  * **选项:** 每日高强度长时间运动, 每周多次规律运动
  * **评分逻辑:** 对应选项的分值 (+10分, 0分)。
* **字段:** `preExerciseGlucose`

  * **类型:** 数字输入框 (mmol/L)
  * **标签:** 运动前血糖水平
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **评分逻辑:**
    * `< 5.0 mmol/L`: +15分
    * `5.0-7.0 mmol/L`: 0分
    * `> 13.9 mmol/L (伴酮体)`: +20分
* **字段:** `inExerciseSupplyStrategy`

  * **类型:** 单选框/下拉选择
  * **标签:** 运动中补给策略
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **选项:** 无规律补给或补给不足, 规律且充足的碳水化合物补给
  * **评分逻辑:** 对应选项的分值 (+10分, 0分)。
* **字段:** `insulinMedicationAdjustment`

  * **类型:** 单选框/下拉选择
  * **标签:** 胰岛素/药物调整
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **选项:** 运动前未调整胰岛素/口服药剂量, 根据运动计划调整胰岛素/口服药剂量
  * **评分逻辑:** 对应选项的分值 (+15分, 0分)。
* **字段:** `postExerciseGlucoseMonitoring`

  * **类型:** 单选框/下拉选择
  * **标签:** 运动后血糖监测
  * **条件:** 仅当 `diagnosisType` 为糖尿病相关时显示。
  * **选项:** 运动后未监测血糖, 运动后规律监测血糖
  * **评分逻辑:** 对应选项的分值 (+5分, 0分)。

### 6. 生活方式与行为 (Lifestyle & Behavior) - 始终显示

* **字段:** `physicalActivity`

  * **类型:** 单选框/下拉选择
  * **标签:** 体力活动
  * **选项:**
    * 每周至少进行150分钟中等强度运动 或 75分钟高强度运动，并包含2次以上抗阻训练。
    * 每周至少进行150分钟中等强度运动 或 75分钟高强度运动。
    * 每周能进行75-150分钟中等强度运动。
    * 每周运动不足75分钟，大部分时间久坐。
  * **评分逻辑:** 对应选项的分值 (-5, 0, 3, 5)。
* **字段:** `dietHabits`

  * **类型:** 单选框/下拉选择
  * **标签:** 饮食习惯
  * **选项:**
    * 遵循明确的健康饮食模式，营养均衡。
    * 有控制饮食的意识，但难以严格执行。
    * 经常食用高油、高盐、高糖食物。
  * **评分逻辑:** 对应选项的分值 (0, 3, 8)。
* **字段:** `smokingStatus`

  * **类型:** 单选框/下拉选择
  * **标签:** 吸烟状况
  * **选项:** 从不吸烟或已戒烟超过1年, 目前仍在吸烟。
  * **评分逻辑:** 对应选项的分值 (0, 10)。
* **字段:** `sleepQuality`

  * **类型:** 单选框/下拉选择
  * **标签:** 睡眠质量
  * **选项:**
    * 每晚平均睡眠7-8小时，质量良好。
    * 睡眠不足6小时或超过9小时，或质量不佳。
  * **评分逻辑:** 对应选项的分值 (0, 5)。

### 7. 风险分层算法与管理方案生成

* **实时计算:** 前端应根据用户输入实时计算总风险分，并根据第一部分“风险分层算法”确定风险等级。
* **动态管理方案生成:** 根据患者的诊断类型、年龄、特殊人群标识、各项评估得分、并发症情况以及生活方式评估结果，动态生成个性化管理方案。管理方案应包含：
  * **总体建议/摘要:** 针对患者主要风险点的综合性建议。
  * **建议日程安排/来院随访:** 具体的随访时间、科室和目的。
  * **随访内容要点:** 每次随访需要关注的检查、讨论内容。
  * **居家管理任务:** 患者日常需要执行的行动清单，包括饮食、运动、血糖监测等。
  * **用药建议:** 基于风险评估结果，提供高层级的药物类别建议（例如：建议考虑SGLT2抑制剂或GLP-1受体激动剂，以改善心肾结局；建议调整降压药物，目标血压<130/80mmHg；对于1型糖尿病运动员，建议运动前胰岛素减量或增加碳水化合物摄入）。**此处不涉及具体药物名称和剂量，仅为指导性建议。**

### 8. 交互与用户体验

* **动态表单:** 根据“条件显示”规则，动态显示/隐藏相关输入字段，避免不必要的填写。
* **实时反馈:** 风险总分和风险等级应在用户输入时实时更新。
* **清晰提示:** 对每个输入字段提供清晰的标签和单位。
* **数据校验:** 对数字输入进行基本范围校验。
* **可打印/导出:** 提供将生成的管理方案打印或导出为PDF的功能。
* **响应式设计:** 确保在不同设备（桌面、平板）上均有良好的用户体验。

### 参考文献

1. **American Diabetes Association (ADA).** Standards of Medical Care in Diabetes. (Published annually). *Diabetes Care*.
2. **American College of Obstetricians and Gynecologists (ACOG).** Practice Bulletin No. 201: Gestational Diabetes Mellitus. (2018). *Obstetrics & Gynecology*.
3. **International Society for Pediatric and Adolescent Diabetes (ISPAD).** Clinical Practice Consensus Guidelines. (Published regularly).
4. **Battelino, T., et al.** (2019). Clinical targets for continuous glucose monitoring data interpretation: recommendations from the international consensus on time in range. *Diabetes Care*.
5. **Voormolen, D. N., et al.** (2025). Real-time continuous glucose monitoring in gestational diabetes mellitus: the DipGluMo randomised controlled trial. *The Lancet Diabetes & Endocrinology*.

### v0.dev 提示词生成讨论纪要

#### 核心主题

构建一个与健康相关的应用，重点关注糖尿病管理。

#### 关键数据点与指标

- **基础血糖指标:** 血糖水平
- **动态血糖监测 (CGM) 指标:** TIR, TAR, TBR, GV, GMI

#### 用户群体/画像

- 不同类型的糖尿病患者
- 特定状况下的患者 (例如: 妊娠期)

#### 核心功能

- 追踪并可视化血糖数据
- 基于权威医学指南 (ADA, ACOG, ACSM) 提供个性化建议
- 进行风险评估与分层
