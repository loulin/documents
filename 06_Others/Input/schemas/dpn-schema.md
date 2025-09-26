# 糖尿病周围神经病变筛查结构化数据方案 (Diabetic Peripheral Neuropathy / DPN Screening Structured Data Schema)

---

## 1. 概述

本方案定义了糖尿病周围神经病变（DPN）筛查记录的结构化字段，覆盖症状、感觉检测、反射评估、评分体系及相关辅助检查。数据设计支持在基层筛查、专科门诊和随访复查场景下统一采集。日期字段使用 `YYYY-MM-DD`，定量指标遵循国际单位制。

## 2. 核心字段

| 字段名 (英文)                  | 字段名 (中文)            | 数据类型       | 描述                                                                                                                                       | 示例                               |
| :----------------------------- | :----------------------- | :------------- | :----------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------- |
| `examDate`                     | 检查日期                 | String         | DPN 筛查日期。                                                                                                                            | `2025-08-15`                       |
| `examType`                     | 检查类型                 | String         | **允许值**: `初诊`, `随访`, `住院评估`, `筛查营`                                                                                           | `随访`                             |
| `symptoms`                     | 神经病变症状             | Array<String>  | 主诉症状，可多选。<br>**允许值**: `无`, `麻木`, `疼痛`, `针刺感`, `烧灼感`, `蚁行感`, `感觉减退`, `下肢无力`, `自主神经症状` | `['麻木', '感觉减退']`             |
| `symptomDurationMonths`        | 症状持续时间 (月)        | Number         | 近似持续时间，单位月。                                                                                                                    | `12`                               |
| `monofilamentTestLeft`         | 左足10g单尼龙丝测试      | String         | **允许值**: `正常 (≥8/10)`, `减退 (1-7/10)`, `缺失 (0/10)`, `未测量`                                                                       | `减退 (6/10)`                      |
| `monofilamentTestRight`        | 右足10g单尼龙丝测试      | String         | 同上。                                                                                                                                     | `减退 (7/10)`                      |
| `vibrationPerceptionLeft`      | 左足振动感觉阈值 (VPT)   | Object         | 使用 VPT 设备或 128Hz 音叉测得阈值，单位 Volt。<br>`[见下方测量值对象定义]`                                                                | `[见下方测量值对象定义]`           |
| `vibrationPerceptionRight`     | 右足振动感觉阈值 (VPT)   | Object         | 同上。                                                                                                                                     | `[见下方测量值对象定义]`           |
| `temperatureSensationLeft`     | 左足温度感觉             | String         | **允许值**: `正常`, `减退`, `消失`, `未测量`                                                                                               | `正常`                             |
| `temperatureSensationRight`    | 右足温度感觉             | String         | 同上。                                                                                                                                     | `正常`                             |
| `pinprickSensationLeft`        | 左足针刺觉               | String         | **允许值**: `正常`, `减退`, `消失`, `未测量`                                                                                               | `减退`                             |
| `pinprickSensationRight`       | 右足针刺觉               | String         | 同上。                                                                                                                                     | `减退`                             |
| `ankleReflexLeft`              | 左踝反射                 | String         | **允许值**: `正常`, `减弱`, `消失`, `未测量`                                                                                              | `减弱`                             |
| `ankleReflexRight`             | 右踝反射                 | String         | 同上。                                                                                                                                     | `减弱`                             |
| `posturalHypotension`          | 体位性低血压             | String         | 自主神经功能表现。<br>**允许值**: `无`, `有`, `未评估`                                                                                    | `无`                               |
| `dpnScoreSystem`               | 评分体系                 | String         | **允许值**: `TCSS`, `MNSI`, `DNS`, `其他`                                                                                                | `TCSS`                             |
| `dpnScore`                     | DPN 评分                  | Number         | 对应量表分值。                                                                                                                             | `5`                                |
| `dpnClassification`            | DPN 分级                  | String         | **允许值**: `无神经病变`, `轻度神经病变`, `中度神经病变`, `重度神经病变`, `不可判定`                                                       | `中度神经病变`                    |
| `ncvStudyReference`            | 神经传导检查参考         | String         | 关联的 NCV/EMG 检查 ID 或路径。                                                                                                              | `NCV_PatientID_20250815`           |
| `ncvSummary`                   | 神经传导结论摘要         | String         | 摘要记录如“腓总神经运动传导减慢”。                                                                                                       | `腓总神经运动传导速度减慢`         |
| `hrvAssessment`                | HRV 评估                  | String         | 自主神经功能评估结果。<br>**允许值**: `正常`, `异常`, `未测量`                                                                             | `正常`                             |
| `diagnosisImpression`          | 诊断/印象                | String         | 综合判定。                                                                                                                                 | `确诊 DPN，考虑混合型`             |
| `recommendation`               | 建议                     | String         | 治疗或生活方式建议。                                                                                                                       | `建议营养神经并强化血糖控制`       |
| `followUpInterval`             | 推荐复查间隔 (月)        | Number         | 建议随访月数。                                                                                                                             | `6`                                |
| `reportNotes`                  | 报告备注                 | String         | 记录测量限制、患者配合度或特殊情况。                                                                                                       | `右足溃疡，部分测试未进行`         |

### 2.1 测量值对象定义 (Measurement Object Definition)

| 字段名 (英文)    | 字段名 (中文) | 数据类型 | 描述                                                                                         | 示例     |
| :--------------- | :------------ | :------- | :------------------------------------------------------------------------------------------- | :------- |
| `value`          | 值            | Number   | 具体测量结果。                                                                               | `18`     |
| `unit`           | 单位          | String   | 单位，如 `V`, `秒`。                                                                        | `V`      |
| `referenceRange` | 参考范围      | String   | 可选。填写指南或设备给出的正常范围。                                                          | `<15V`   |
| `measurementMethod` | 测量方式  | String   | 可选。记录设备或方法（如 `Biothesiometer`, `音叉`）。                                           | `Biothesiometer` |
| `qualityFlag`    | 质量标识      | String   | **允许值**: `有效`, `需复测`, `弃用`。                                                         | `有效`   |

## 3. 数据校验与扩展建议

- **症状-体征关联**: 当 `symptoms` 包含疼痛/感觉缺失且客观测试正常时，需在 `reportNotes` 解释（如夜间症状或自主神经受累），避免误判。
- **评分一致性**: `dpnClassification` 应与所选 `dpnScoreSystem` 的分值区间相匹配；系统可内置阈值校验，异常时提示人工确认。
- **多模态扩展**: 可新增 `skinBiopsyReference`、`cornealConfocalMicroscopy` 等字段，以纳入小纤维神经病变评估。
- **长期随访**: 建议维护时间序列，追踪评分变化；当分级升高应自动缩短 `followUpInterval` 并生成预警。
- **合并症联动**: 与足部检查、ABI 结果建立引用，可形成糖尿病足综合风险评估模型。
