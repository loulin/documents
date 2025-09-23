# 体成分分析结构化数据方案 (Body Composition Analysis Structured Data Schema)

---

## 1. 概述

本方案定义了从体成分分析（如 BIA、DEXA、空气置换体积测量）报告中提取结构化数据的字段及规范。文档强调关键指标、测量方法以及质量控制要点，便于将个体营养状态、肌肉量与脂肪分布数据纳入代谢风险评估。数值字段默认使用国际单位制，日期使用 `YYYY-MM-DD` 格式。

## 2. 核心字段

以下字段汇总体成分分析的主要结构化数据项，可按报告实际情况进行采集。

| 字段名 (英文)                     | 字段名 (中文)              | 数据类型 | 描述                                                                                                                                   | 示例                       |
| :-------------------------------- | :------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------- | :------------------------- |
| `examDate`                        | 检查日期                   | String   | 体成分分析日期，`YYYY-MM-DD`。                                                                                                         | `2025-08-15`               |
| `measurementMethod`               | 测量方法                   | String   | 使用的测量技术。<br>**允许值**: `DEXA`, `BIA`, `水下称重`, `空气置换体积测量`, `MRI`, `CT`                                           | `BIA`                      |
| `bodyWeight`                      | 体重 (kg)                  | Number   | 测量时体重，单位 kg。                                                                                                                 | `70.5`                     |
| `bodyHeight`                      | 身高 (cm)                  | Number   | 测量时身高，单位 cm。                                                                                                                 | `175.0`                    |
| `bmi`                             | 体质指数 (BMI)             | Number   | 体重指数，保留一位小数。                                                                                                             | `23.0`                     |
| `waistCircumference`              | 腰围 (cm)                  | Number   | 腰围测量值，单位 cm。                                                                                                                 | `85.0`                     |
| `hipCircumference`                | 臀围 (cm)                  | Number   | 臀围测量值，单位 cm。                                                                                                                 | `95.0`                     |
| `waistHipRatio`                   | 腰臀比                     | Number   | 腰围与臀围的比值，保留两位小数。                                                                                                     | `0.89`                     |
| `bodyFatMass`                     | 脂肪量 (kg)                | Number   | 全身脂肪质量，单位 kg。                                                                                                              | `18.2`                     |
| `leanBodyMass`                    | 去脂体重 (kg)              | Number   | 非脂肪体质量（骨骼肌、骨骼、水分等），单位 kg。                                                                                       | `52.3`                     |
| `skeletalMuscleMass`              | 骨骼肌量 (kg)              | Number   | 全身骨骼肌量，单位 kg。                                                                                                              | `30.5`                     |
| `appendicularLeanMass`            | 四肢去脂体重 (kg)          | Number   | 上下肢去脂体重之和，常用于诊断肌少症。                                                                                               | `20.8`                     |
| `bodyFatPercentage`               | 体脂百分比 (%)             | Number   | 全身脂肪占体重比例，单位 %。                                                                                                         | `25.8`                     |
| `visceralFatArea`                 | 内脏脂肪面积 (cm²)         | Number   | 部分 BIA/CT 设备提供的内脏脂肪截面积。                                                                                               | `90`                       |
| `totalBodyWater`                  | 总体水分 (kg)              | Number   | 体内总水含量，单位 kg。                                                                                                               | `40.1`                     |
| `intracellularWater`              | 细胞内液 (kg)              | Number   | 细胞内水含量，单位 kg。                                                                                                               | `25.5`                     |
| `extracellularWater`              | 细胞外液 (kg)              | Number   | 细胞外水含量，单位 kg。                                                                                                               | `14.6`                     |
| `resistance`                      | 电阻 (Ω)                   | Number   | BIA 检查中的电阻值，单位欧姆。                                                                                                        | `500`                      |
| `reactance`                       | 电抗 (Ω)                   | Number   | BIA 检查中的电抗值，单位欧姆。                                                                                                        | `50`                       |
| `phaseAngle`                      | 相位角 (°)                 | Number   | 由电阻与电抗计算所得的相位角，单位度。                                                                                               | `5.7`                      |
| `skeletalMuscleAssessment`        | 骨骼肌评估                 | String   | 对骨骼肌量的定性解读（与人群参考比较）。<br>**允许值**: `偏低`, `正常`, `偏高`                                                      | `正常`                     |
| `bodyFatAssessment`               | 体脂评估                   | String   | 对体脂百分比的定性解读。<br>**允许值**: `偏低`, `正常`, `偏高`, `肥胖`                                                              | `偏高`                     |
| `segmentalComposition`            | 分段成分列表               | Array<Object> | 记录躯干及四肢的脂肪量、肌肉量等详细信息。<br>`[见下方分段成分对象定义]`                                                            | `[见下方分段成分对象定义]` |
| `boneMineralContent`              | 骨矿物质含量 (kg)          | Number   | 若采用 DEXA，可记录骨矿物质含量。                                                                                                   | `2.6`                      |
| `basalMetabolicRate`              | 基础代谢率 (kcal)          | Number   | 估算的基础代谢率，单位 kcal。                                                                                                       | `1500`                     |
| `diagnosisImpression`             | 诊断/印象                  | String   | 医师对体成分结果的综合判断。                                                                                                         | `体脂率偏高，肌肉量不足`     |
| `recommendation`                  | 建议                       | String   | 根据结果提出的生活方式或医学建议。                                                                                                   | `建议增加抗阻运动`           |
| `measurementNotes`                | 测量备注                   | String   | 记录测量条件（空腹/非空腹）、设备校准情况或异常数据说明。                                                                      | `饭后2小时测量，提醒复测`     |

### 2.1 分段成分对象定义 (Segmental Composition Object Definition)

| 字段名 (英文) | 字段名 (中文)     | 数据类型 | 描述                                                                                      | 示例       |
| :------------ | :---------------- | :------- | :---------------------------------------------------------------------------------------- | :--------- |
| `segment`     | 部位              | String   | 记录身体部位。<br>**允许值**: `左上肢`, `右上肢`, `躯干`, `左下肢`, `右下肢`               | `左下肢`   |
| `fatMass`     | 脂肪量 (kg)       | Number   | 该部位的脂肪质量，单位 kg。                                                              | `4.2`      |
| `leanMass`    | 去脂体重 (kg)     | Number   | 该部位的去脂体重，单位 kg。                                                              | `6.1`      |
| `muscleQuality` | 肌肉质量评价    | String   | 定性描述肌肉量状况。<br>**允许值**: `低`, `正常`, `高`                                   | `正常`     |

## 3. 数据校验与扩展建议

- **单位与格式统一**: 数值字段需统一单位（如体重 kg、身高 cm），并限定小数位；若设备输出不同单位，应在存储前完成转换并在 `measurementNotes` 记录原始信息。
- **逻辑校验**: `leanBodyMass + bodyFatMass` 应约等于 `bodyWeight`，偏差超过 3% 时需校验原始数据；腰臀比、BMI 等衍生指标应可由基础测量直接再现。
- **人群参考值**: 建议扩展记录性别、年龄、地区对应的参考范围 ID，以便与标准化数据库比对实现自动分层。
- **趋势跟踪**: 可新增字段存放历史测量数组（如 `historicalMeasurements`），支持体重管理或运动干预的纵向分析。
- **图像与原始数据链接**: 对于 DEXA/MRI 结果，可关联原始扫描图像或 CSV 导出文件，确保高维数据可追溯。
