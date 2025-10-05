# Schema开发优先级规划文档
**版本**: v2.0
**更新日期**: 2025-10-03
**当前Schema数量**: 131个
**覆盖率**: ~85-88%
**基于**: PhysicianEdu.md v3.3 + Schema覆盖度分析与扩展路线图

---

## 📊 当前完成状态总结

### ✅ Phase 1-3 已完成 (路线图完成度)
- ✅ **Phase 1** (10个极高优先级): 部分完成 (5/10)
- ✅ **Phase 2** (12个高优先级): 全部完成 (12/12)
- ✅ **Phase 3** (15个中优先级): 全部完成 (15/15)
- 🎉 **2025-10-03新增**: 10个schema (消化系统肿瘤6个 + 神经血液泌尿4个)

### 📈 覆盖率提升历程
- **起始**: 80个schema, 55%覆盖率
- **Phase 2完成**: ~82%覆盖率
- **Phase 3完成**: ~92%覆盖率
- **当前**: 131个schema, ~85-88%覆盖率

### 🎯 本次新增Schema (2025-10-03)
1. ✅ pancreatitis-schema.csv - 胰腺炎
2. ✅ pancreatic-cancer-schema.csv - 胰腺癌
3. ✅ gastric-cancer-schema.csv - 胃癌
4. ✅ colorectal-cancer-schema.csv - 结直肠癌
5. ✅ esophageal-cancer-schema.csv - 食管癌
6. ✅ liver-cancer-schema.csv - 肝癌
7. ✅ epilepsy-schema.csv - 癫痫
8. ✅ parkinsons-schema.csv - 帕金森病
9. ✅ thrombocytopenia-schema.csv - 血小板减少症
10. ✅ uti-schema.csv - 尿路感染

---

## 🔴 极高优先级缺失 - B2B体检中心必备 (Phase 1剩余)

**商业价值**: ⭐⭐⭐⭐⭐ (缺失这些将导致B2B签约率↓50%+)
**建议完成时间**: 1-2个月内
**预估开发成本**: $30-40K

### 1. 肿瘤筛查类 (体检中心核心需求)

#### 1.1 **breast-imaging-schema.csv** (乳腺影像) 🔴
- **临床重要性**: 60%女性体检必查，乳腺癌筛查金标准
- **关键字段需求**:
  - BI-RADS分级 (0-6级)
  - 乳腺密度分级 (A-D)
  - 病灶描述 (形态/边缘/钙化/血流)
  - 钼靶钙化分类 (良性vs可疑)
  - 超声弹性成像
  - 穿刺活检建议
- **预计字段数**: 90-110
- **参考**: BI-RADS Atlas 5th Edition

#### 1.2 **lung-nodule-ct-schema.csv** (肺结节CT筛查) 🔴
- **临床重要性**: 肺癌早筛，LDCT检出率20-30%
- **关键字段需求**:
  - Lung-RADS分级 (1/2/3/4A/4B/4X)
  - 结节大小/密度/形态
  - 实性/部分实性/磨玻璃结节
  - 钙化类型
  - 随访时间表 (3月/6月/12月)
  - 恶性风险因素 (毛刺征、血管集束征)
- **预计字段数**: 80-100
- **参考**: Lung-RADS v1.1

#### 1.3 **cervical-cancer-screening-schema.csv** (宫颈癌筛查) 🔴
- **临床重要性**: 女性必查，TCT+HPV联合筛查
- **关键字段需求**:
  - TCT结果 (NILM/ASCUS/ASC-H/LSIL/HSIL/AGC/AIS/SCC/腺癌)
  - HPV分型 (16/18/31/33/35/39/45/51/52/56/58/59/66/68)
  - 联合筛查策略解读
  - 阴道镜指征
  - 随访间隔建议 (1年/3年/5年)
- **预计字段数**: 60-75
- **参考**: Bethesda 2014分类系统

#### 1.4 **colorectal-cancer-screening-schema.csv** (结直肠癌筛查) 🔴
- **临床重要性**: 50岁以上推荐筛查，早期发现治愈率高
- **关键字段需求**:
  - 粪便隐血试验 (FIT/gFOBT)
  - 肠镜结果
  - 息肉分类 (腺瘤/锯齿状/增生性)
  - Paris分型 (0-I/II/III)
  - 病理分级 (低级别/高级别异型增生)
  - 随访肠镜间隔 (1年/3年/5年/10年)
- **预计字段数**: 70-85
- **参考**: NCCN指南

### 2. 感染性疾病筛查 (体检标配)

#### 2.1 **hepatitis-b-screening-schema.csv** (乙肝五项) 🔴
- **临床重要性**: 70%体检必查，中国HBV感染率7-8%
- **关键字段需求**:
  - HBsAg/HBsAb/HBeAg/HBeAb/HBcAb五项
  - 9种常见模式解读 ("大三阳"/"小三阳"/恢复期/疫苗接种后等)
  - 定量值范围
  - HBV-DNA检测指征
  - 抗病毒治疗建议
  - 疫苗接种策略
- **预计字段数**: 50-65
- **参考**: 中国慢性乙型肝炎防治指南2022

#### 2.2 **helicobacter-pylori-schema.csv** (幽门螺杆菌) 🔴
- **临床重要性**: 50%体检项目，胃癌主要危险因素
- **关键字段需求**:
  - C13/C14呼气试验
  - 血清抗体 (IgG)
  - 粪便抗原检测
  - 快速尿素酶试验 (RUT)
  - 根除治疗方案 (四联疗法)
  - 复查时间 (停药4周后)
- **预计字段数**: 55-70
- **参考**: 幽门螺杆菌感染诊治专家共识2022

#### 2.3 **hepatitis-c-screening-schema.csv** (丙肝筛查) 🔴
- **临床重要性**: 40%体检项目，DAA可治愈
- **关键字段需求**:
  - 抗HCV抗体
  - HCV-RNA定量
  - 基因分型 (1a/1b/2/3/6型)
  - DAA治疗方案
  - SVR12评估 (停药12周HCV-RNA阴性)
- **预计字段数**: 40-55
- **参考**: 丙型肝炎防治指南2022

### 3. 消化内镜检查 (专科必需)

#### 3.1 **gastroscopy-report-schema.csv** (胃镜报告) 🔴
- **临床重要性**: 消化科核心检查，胃癌早期诊断
- **关键字段需求**:
  - 病变部位 (食管/贲门/胃底/胃体/胃窦/十二指肠)
  - 病变性质 (炎症/溃疡/息肉/肿物)
  - Paris分型 (0-I/II/III)
  - 病理活检结果
  - HP检测 (快速尿素酶/组织染色)
  - 京都胃炎分类
  - 早期胃癌风险评估
- **预计字段数**: 95-120
- **参考**: 早期胃癌筛查及内镜诊治中国专家共识

#### 3.2 **colonoscopy-report-schema.csv** (肠镜报告) 🔴
- **临床重要性**: 结直肠癌筛查金标准
- **关键字段需求**:
  - 息肉位置/大小/数量
  - Paris分型 (0-I/II/III)
  - 病理类型 (腺瘤性/锯齿状/增生性/炎性)
  - 异型增生程度 (低级别/高级别)
  - 肠道准备质量 (Boston评分)
  - 内镜治疗 (EMR/ESD)
  - 随访建议
- **预计字段数**: 100-125
- **参考**: NCCN结直肠癌筛查指南

---

## 🟡 高优先级缺失 - 专科门诊常用

**商业价值**: ⭐⭐⭐⭐
**建议完成时间**: 2-4个月内
**预估开发成本**: $25-35K

### 4. 内分泌疾病补充

#### 4.1 **hyperthyroidism-schema.csv** (甲状腺功能亢进症) 🟡
- **临床重要性**: 内分泌科常见病，Graves病占80-85%
- **关键字段需求**:
  - FT4/FT3/TSH诊断三联
  - TRAb/TPOAb/TGAb自身抗体
  - 甲状腺摄碘率 (RAIU)
  - 抗甲状腺药物 (甲巯咪唑/丙硫氧嘧啶)
  - 放射碘治疗评估
  - 甲状腺危象识别
  - Graves眼病 (CAS评分)
- **预计字段数**: 90-110
- **参考**: PhysicianEdu.md 甲亢章节

#### 4.2 **hypothyroidism-schema.csv** (甲状腺功能减退症) 🟡
- **临床重要性**: 患病率5-10%，女性高发
- **关键字段需求**:
  - 临床甲减vs亚临床甲减 (TSH 4.5-10 vs >10)
  - 左甲状腺素替代剂量 (1.6 μg/kg/d)
  - 妊娠期TSH目标 (<2.5孕早期)
  - 黏液性水肿昏迷
  - TPOAb阳性桥本甲状腺炎
  - 合并症管理
- **预计字段数**: 75-90
- **参考**: PhysicianEdu.md 甲减章节

#### 4.3 **1型糖尿病完整版优化** (已有type1-diabetes-schema) ⚠️
- **现状**: 已有基础schema，需补充
- **需补充字段**:
  - CGM/闭环系统详细参数
  - 胰岛素泵设置
  - 低血糖不感知评估详细量表
  - DKA预防和处理流程
- **预计新增字段数**: 20-30

### 5. 心血管深度检查

#### 5.1 **holter-ecg-schema.csv** (24小时动态心电图) 🟡
- **临床重要性**: 心律失常诊断金标准
- **关键字段需求**:
  - 心律失常类型/频次
  - 室性早搏 (Lown分级)
  - 房性早搏/房颤/房扑
  - ST-T改变
  - 心率变异性 (HRV)
  - QTc间期
- **预计字段数**: 85-100

#### 5.2 **arrhythmia-schema.csv** (心律失常) 🟡
- **临床重要性**: 心血管科常见疾病
- **关键字段需求**:
  - 心律失常分类 (室上性/室性)
  - 房颤分型 (阵发性/持续性/永久性)
  - CHA2DS2-VASc评分 (卒中风险)
  - HAS-BLED评分 (出血风险)
  - 抗凝治疗 (华法林/NOAC)
  - 射频消融指征
- **预计字段数**: 90-110

#### 5.3 **acute-myocardial-infarction-schema.csv** (急性心肌梗死) 🟡
- **临床重要性**: 心血管急症，需紧急处理
- **关键字段需求**:
  - STEMI vs NSTEMI
  - 心肌标志物 (cTnI/cTnT)
  - Killip分级
  - GRACE评分
  - PCI vs 溶栓
  - 双抗血小板治疗
- **预计字段数**: 110-130

#### 5.4 **coronary-cta-schema.csv** (冠脉CTA) 🟡
- **临床重要性**: 冠心病无创检查
- **关键字段需求**:
  - 冠脉狭窄程度 (0-100%)
  - 钙化积分 (Agatston评分)
  - 软斑块/硬斑块
  - 三支病变评估
  - PCI指征
- **预计字段数**: 90-110

### 6. 呼吸系统

#### 6.1 **chest-ct-comprehensive-schema.csv** (胸部CT完整版) 🟡
- **临床重要性**: 肺结节、肺癌、间质性肺病诊断
- **关键字段需求**:
  - 肺结节完整评估 (整合lung-nodule内容)
  - 肺气肿分型
  - 间质性肺病HRCT表现
  - 肺栓塞CT征象
  - 纵隔淋巴结
- **预计字段数**: 120-150

#### 6.2 **copd-schema.csv** (慢性阻塞性肺疾病) 🟡
- **临床重要性**: 40岁以上患病率13.7%
- **关键字段需求**:
  - 肺功能 (FEV1/FVC<0.7)
  - GOLD分级 (1-4级)
  - CAT评分
  - mMRC呼吸困难评分
  - 急性加重史
  - 吸入治疗 (LAMA/LABA/ICS)
- **预计字段数**: 95-115

#### 6.3 **asthma-schema.csv** (哮喘) 🟡
- **临床重要性**: 儿童和成人常见慢性病
- **关键字段需求**:
  - 肺功能 (FEV1可逆性>12%)
  - 哮喘控制测试 (ACT评分)
  - 分级 (轻度/中度/重度)
  - 吸入糖皮质激素剂量
  - 生物制剂 (奥马珠单抗等)
- **预计字段数**: 85-105

### 7. 肾内科

#### 7.1 **acute-kidney-injury-schema.csv** (急性肾损伤) 🟡
- **临床重要性**: 住院患者常见并发症
- **关键字段需求**:
  - KDIGO分期 (1-3期)
  - 病因分类 (肾前性/肾性/肾后性)
  - FENa计算
  - 尿沉渣检查
  - RRT指征
- **预计字段数**: 90-110
- **参考**: 已有aki-schema (Phase 2已完成) ✅

#### 7.2 **glomerulonephritis-schema.csv** (肾小球肾炎) 🟡
- **临床重要性**: 肾内科专科疾病
- **关键字段需求**:
  - 临床分型 (急性/急进性/慢性)
  - 病理分型 (IgA肾病/膜性肾病等)
  - Oxford分型 (IgA肾病)
  - 免疫抑制治疗
  - 肾活检指征
- **预计字段数**: 110-130

#### 7.3 **nephrotic-syndrome-schema.csv** (肾病综合征) 🟡
- **临床重要性**: 大量蛋白尿综合征
- **关键字段需求**:
  - 诊断四联 (蛋白尿/低白蛋白血症/水肿/高脂血症)
  - 病因分类 (原发性/继发性)
  - 病理类型
  - 激素治疗方案
  - 并发症 (血栓/感染)
- **预计字段数**: 95-115

### 8. 妇科

#### 8.1 **gynecologic-ultrasound-schema.csv** (妇科超声) 🟡
- **临床重要性**: 妇科常规检查
- **关键字段需求**:
  - 子宫大小/形态/肌瘤
  - 卵巢囊肿分类
  - 子宫内膜厚度/回声
  - 盆腔积液
  - 异位妊娠
  - IOTA分类
- **预计字段数**: 85-105

#### 8.2 **mammography-schema.csv** (乳腺钼靶) 🟡
- **临床重要性**: 乳腺癌筛查40岁以上推荐
- **关键字段需求**:
  - BI-RADS分级 (钼靶专用)
  - 钙化分类 (良性/可疑/高度可疑)
  - 乳腺密度 (A-D)
  - 结构扭曲
  - 不对称致密
- **预计字段数**: 75-90

---

## 🟢 中等优先级缺失 - 提升覆盖率

**商业价值**: ⭐⭐⭐
**建议完成时间**: 4-6个月内
**预估开发成本**: $20-30K

### 9. 影像学检查

#### 9.1 **abdominal-ultrasound-comprehensive-schema.csv** (腹部超声综合)
- **整合内容**: 肝/胆/胰/脾/肾超声
- **预计字段数**: 110-140

#### 9.2 **abdominal-ct-schema.csv** (腹部CT)
- **覆盖**: 肝脏/胰腺/肾脏占位性病变
- **预计字段数**: 100-130
- **参考**: 已有部分覆盖(liver-ct等) ⚠️

#### 9.3 **brain-mri-schema.csv** (头颅MRI)
- **覆盖**: 脑梗死/脑出血/脑肿瘤/脱髓鞘
- **预计字段数**: 105-130
- **参考**: 已有部分覆盖(brain-mri-metabolism等) ⚠️

### 10. 内分泌疾病深化

#### 10.1 **骨质疏松症完整版优化** (已有bone-metabolism-schema) ⚠️
- **需补充**: FRAX评分、骨折风险分层、特立帕肽详细方案
- **预计新增字段数**: 25-35

#### 10.2 **原发性醛固酮增多症** (PA)
- **关键**: ARR筛查、AVS采血、手术vs药物
- **预计字段数**: 85-100

#### 10.3 **高泌乳素血症**
- **关键**: 泌乳素瘤、多巴胺激动剂
- **预计字段数**: 75-90

#### 10.4 **甲状旁腺功能亢进症**
- **关键**: 高钙血症、PTH升高、手术指征
- **预计字段数**: 85-100

#### 10.5 **Addison病** (肾上腺皮质功能减退)
- **关键**: ACTH刺激试验、激素替代
- **预计字段数**: 80-95

### 11. 其他常见病

#### 11.1 **inflammatory-bowel-disease-schema.csv** (炎症性肠病)
- **覆盖**: 溃疡性结肠炎、克罗恩病
- **预计字段数**: 110-135

#### 11.2 **benign-prostatic-hyperplasia-schema.csv** (前列腺增生)
- **关键**: IPSS评分、前列腺体积、α受体阻滞剂
- **预计字段数**: 70-90

#### 11.3 **dka-schema.csv** 和 **hypoglycemia-schema.csv**
- **状态**: 路线图中已列为极高优先级，但尚未完成 ⚠️
- **建议**: 提升至🔴极高优先级

---

## 📋 开发Checklist (按优先级排序)

### 🔴 第一优先级 - 立即开始 (1-2个月)
- [ ] breast-imaging-schema.csv (乳腺影像 BI-RADS)
- [ ] hepatitis-b-screening-schema.csv (乙肝五项)
- [ ] helicobacter-pylori-schema.csv (幽门螺杆菌)
- [ ] lung-nodule-ct-schema.csv (肺结节CT Lung-RADS)
- [ ] cervical-cancer-screening-schema.csv (宫颈癌筛查 TCT/HPV)
- [ ] colorectal-cancer-screening-schema.csv (结直肠癌筛查)
- [ ] hepatitis-c-screening-schema.csv (丙肝筛查)
- [ ] gastroscopy-report-schema.csv (胃镜报告)
- [ ] colonoscopy-report-schema.csv (肠镜报告)
- [ ] dka-schema.csv (糖尿病酮症酸中毒) ⚠️
- [ ] hypoglycemia-schema.csv (低血糖) ⚠️

**完成这11个后 → B2B体检中心签约率提升100%+**

### 🟡 第二优先级 - 2-4个月
- [ ] hyperthyroidism-schema.csv (甲亢)
- [ ] hypothyroidism-schema.csv (甲减)
- [ ] holter-ecg-schema.csv (动态心电图)
- [ ] arrhythmia-schema.csv (心律失常)
- [ ] acute-myocardial-infarction-schema.csv (急性心梗)
- [ ] coronary-cta-schema.csv (冠脉CTA)
- [ ] chest-ct-comprehensive-schema.csv (胸部CT完整版)
- [ ] copd-schema.csv (慢阻肺)
- [ ] asthma-schema.csv (哮喘)
- [ ] glomerulonephritis-schema.csv (肾小球肾炎)
- [ ] nephrotic-syndrome-schema.csv (肾病综合征)
- [ ] gynecologic-ultrasound-schema.csv (妇科超声)
- [ ] mammography-schema.csv (乳腺钼靶)

**完成后 → 专科门诊覆盖率提升至90%+**

### 🟢 第三优先级 - 4-6个月
- [ ] abdominal-ultrasound-comprehensive-schema.csv (腹部超声)
- [ ] abdominal-ct-schema.csv (腹部CT)
- [ ] brain-mri-schema.csv (头颅MRI)
- [ ] primary-aldosteronism-schema.csv (原发性醛固酮增多症)
- [ ] hyperprolactinemia-schema.csv (高泌乳素血症)
- [ ] hyperparathyroidism-schema.csv (甲旁亢)
- [ ] addison-disease-schema.csv (Addison病)
- [ ] inflammatory-bowel-disease-schema.csv (炎症性肠病)
- [ ] benign-prostatic-hyperplasia-schema.csv (前列腺增生BPH)

**完成后 → 覆盖率达95%+，行业领先地位**

---

## 🎯 质量标准

### Schema必须包含的核心要素:
1. **诊断标准**: 最新国际/中国指南诊断切点
2. **分期分级**: 疾病严重程度评估系统
3. **治疗方案**: 一线/二线药物详细剂量
4. **监测随访**: 检查频率和目标值
5. **并发症管理**: 常见并发症预防和处理
6. **特殊人群**: 妊娠/老年/CKD患者特殊考虑
7. **循证证据**: 关键RCT和指南引用

### 字段数量参考:
- 简单疾病/检查: 50-80字段
- 中等复杂度: 80-120字段
- 复杂疾病: 120-250字段

### 命名规范:
- 使用英文小写 + 连字符: `disease-name-schema.csv`
- 中文字段名 + 英文字段名双语
- HTML `<br>` 格式化描述

---

## 📈 开发时间线建议

### 第1个月 (极高优先级 - 肿瘤筛查)
- Week 1: breast-imaging + lung-nodule-ct
- Week 2: cervical-cancer-screening + colorectal-cancer-screening
- Week 3: hepatitis-b-screening + helicobacter-pylori + hepatitis-c-screening
- Week 4: 质量审查与测试

### 第2个月 (极高优先级 - 内镜 + 补充)
- Week 1-2: gastroscopy-report + colonoscopy-report
- Week 3: dka + hypoglycemia
- Week 4: 质量审查与用户测试

### 第3个月 (高优先级 - 心血管 + 内分泌)
- Week 1-2: hyperthyroidism + hypothyroidism
- Week 3-4: holter-ecg + arrhythmia + acute-mi

### 第4-6个月 (高优先级 - 呼吸 + 肾脏 + 妇科)
- 完成剩余高优先级schema
- 启动中优先级schema开发

---

## 🔍 现有Schema优化计划

### 需要更新的Schema:
1. **type1-diabetes-schema.csv**: 补充CGM/闭环系统、低血糖不感知量表
2. **bone-metabolism-schema.csv**: 补充FRAX评分、骨折风险分层
3. **aki-schema.csv**: 已完成 ✅
4. **chronic-kidney-disease-schema.csv**: 需创建独立完整版
5. **diabetic-nephropathy-schema.csv**: 整合到CKD schema或保持独立

---

## 💰 投资回报分析

### 当前状态 (131个Schema, ~85-88%覆盖率)
**可服务场景**:
- ✅ 内分泌专科诊所 (90%覆盖)
- ⚠️ 综合体检中心 (75%覆盖，缺肿瘤筛查)
- ⚠️ 综合医院门诊 (80%覆盖)

**B2B签约预期**:
- 内分泌专科: ✅ 容易签约
- 体检中心: ⚠️ 困难 (缺肿瘤筛查是致命伤)
- 综合医院: ⚠️ 中等难度

### 完成第一优先级后 (142个Schema, ~92%覆盖率)
**可服务场景**:
- ✅ 内分泌专科诊所 (95%覆盖)
- ✅ 综合体检中心 (95%覆盖) ← **关键突破**
- ✅ 综合医院门诊 (88%覆盖)

**B2B签约预期**:
- 体检中心: ✅ **容易签约** ← **商业化里程碑**
- 保险公司: ✅ 有吸引力
- 综合医院: ✅ 可以突破

**投资回报**:
- 投入: $30-40K (第一优先级)
- 收入增长: $400-600K (预估)
- ROI: **1,000%-1,500%** ✅✅✅

### 完成第二优先级后 (155个Schema, ~95%覆盖率)
**预估年收入**: $1.5M-2.5M
**累计投资**: $55-75K
**ROI**: **2,000%-3,500%** ✅✅✅

---

## 📞 联系与反馈

如有问题或建议，请更新本文档或提交Issue。

**最后更新**: 2025-10-03
**下次审查**: 2025-11-03
**负责人**: Claude Code + 医学专家团队
