# 踝臂指数结构化数据方案 (Ankle-Brachial Index / ABI Structured Data Schema)

---

## 1. 概述

本方案定义了从踝臂指数（ABI）及趾臂指数（TBI）检查报告中提取结构化数据的字段与规范。ABI/TBI 用于评估下肢外周动脉疾病（PAD）的存在与严重程度，尤其适用于糖尿病及高危动脉粥样硬化人群。数值字段默认使用国际单位（mmHg、比值），日期字段统一采用 `YYYY-MM-DD` 的 ISO 8601 格式。

## 2. 核心字段

以下字段描述 ABI/TBI 检查中的关键数据项，均为可选字段，可根据实际报告情况采集。

| 字段名 (英文)                      | 字段名 (中文)         | 数据类型 | 描述                                                                                                                                                            | 示例                             |
| :--------------------------------- | :-------------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------- |
| `examDate`                         | 检查日期              | String   | ABI/TBI 检查日期，使用 `YYYY-MM-DD`。                                                                                                                             | `2025-08-15`                     |
| `measurementDevice`               | 测量设备              | String   | 所使用的设备或型号，可用于溯源与数据质量评估。                                                                                                                   | `VaSera VS-1500`                 |
| `brachialSystolicPressure`         | 肱动脉收缩压 (mmHg)  | Number   | 左右上臂中较高的肱动脉收缩压，单位 mmHg。                                                                                                                         | `125`                            |
| `rightAnkleSystolicPressure`      | 右踝动脉收缩压 (mmHg) | Number   | 右侧胫后或足背动脉的最高收缩压，单位 mmHg。                                                                                                                       | `108`                            |
| `leftAnkleSystolicPressure`       | 左踝动脉收缩压 (mmHg) | Number   | 左侧胫后或足背动脉的最高收缩压，单位 mmHg。                                                                                                                       | `120`                            |
| `rightABIValue`                   | 右侧 ABI 值           | Number   | `右踝动脉收缩压 / 肱动脉收缩压` 的计算结果，保留两位小数。                                                                                                        | `0.86`                           |
| `leftABIValue`                    | 左侧 ABI 值           | Number   | `左踝动脉收缩压 / 肱动脉收缩压` 的计算结果，保留两位小数。                                                                                                        | `0.96`                           |
| `abiInterpretation`               | ABI 结果解读          | String   | 对双侧 ABI 的综合解读。<br>**允许值**: `正常 (0.90–1.30)`, `临界值 (0.91–0.99)`, `轻度阻塞 (0.70–0.89)`, `中度阻塞 (0.40–0.69)`, `重度阻塞 (<0.40)`, `动脉僵硬/不可压缩 (>1.30)` | `右侧轻度阻塞`                   |
| `rightToeSystolicPressure`        | 右趾动脉收缩压 (mmHg) | Number   | 右侧趾动脉的收缩压，单位 mmHg。                                                                                                                                 | `80`                             |
| `leftToeSystolicPressure`         | 左趾动脉收缩压 (mmHg) | Number   | 左侧趾动脉的收缩压，单位 mmHg。                                                                                                                                 | `90`                             |
| `rightTBIValue`                   | 右侧 TBI 值           | Number   | `右趾动脉收缩压 / 肱动脉收缩压` 的计算结果，保留两位小数。                                                                                                        | `0.64`                           |
| `leftTBIValue`                    | 左侧 TBI 值           | Number   | `左趾动脉收缩压 / 肱动脉收缩压` 的计算结果，保留两位小数。                                                                                                        | `0.72`                           |
| `tbiInterpretation`               | TBI 结果解读          | String   | 对双侧 TBI 的综合解读。<br>**允许值**: `正常 (≥0.70)`, `异常 (<0.70)`, `无法测量`                                                                                  | `右侧异常`                       |
| `rightDorsalisPedisArteryWaveform` | 右足背动脉波形        | String   | 右足背动脉多普勒血流波形类型。<br>**允许值**: `三相波`, `双相波`, `单相波`, `消失`                                                                                 | `双相波`                         |
| `leftDorsalisPedisArteryWaveform`  | 左足背动脉波形        | String   | 左足背动脉多普勒血流波形类型。<br>**允许值**: `三相波`, `双相波`, `单相波`, `消失`                                                                                 | `三相波`                         |
| `rightPosteriorTibialArteryWaveform` | 右胫后动脉波形     | String   | 右胫后动脉多普勒血流波形类型。<br>**允许值**: `三相波`, `双相波`, `单相波`, `消失`                                                                                 | `单相波`                         |
| `leftPosteriorTibialArteryWaveform`  | 左胫后动脉波形     | String   | 左胫后动脉多普勒血流波形类型。<br>**允许值**: `三相波`, `双相波`, `单相波`, `消失`                                                                                 | `三相波`                         |
| `measurementNotes`                | 测量备注              | String   | 记录测量次数、重测情况或导致数据偏差的原因，便于质量控制。                                                                                                         | `右踝因动脉钙化需重复测量`       |
| `imagingStudyReference`           | 影像学检查参考        | String   | 关联的下肢动脉超声、CTA 或 MRA 等检查的 ID 或链接。                                                                                                                | `Imaging_PatientID_20250815`     |
| `diagnosisImpression`             | 诊断/印象             | String   | 医生对检查结果的综合诊断或印象。                                                                                                                                 | `下肢动脉粥样硬化性狭窄`         |
| `recommendation`                  | 建议                  | String   | 根据检查结果给出的临床建议。                                                                                                                                     | `建议进一步行下肢动脉造影检查`   |

## 3. 数据校验与扩展建议

- **异常值联动校验**: 当 ABI < 0.40 或 > 1.30 时，建议强制填写 `measurementNotes` 与 `imagingStudyReference`，并提示确认是否存在测量误差或动脉钙化。
- **逻辑一致性**: `rightABIValue`、`leftABIValue` 必须可由对应收缩压直接计算得出；若存在四舍五入差异，应在 `measurementNotes` 标注计算基准。
- **结构化拓展**: 可扩展 Toe-Brachial Index 的分趾数据（如大趾、小趾）或加入自动化风险分层字段（如 Fontaine、Rutherford 分级）以满足临床随访需求。
- **跨检查关联**: 建议与同日的下肢血管超声或动脉 CTA 结果建立字段映射，以便联合评估血流动力学与解剖学狭窄程度。
