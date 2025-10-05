# Schema覆盖度缺口分析报告

**分析日期**: 2025年10月03日
**当前Schema数量**: 135个
**分析目的**: 识别内分泌、肿瘤及其他临床领域的覆盖缺口

---

## 1️⃣ 内分泌代谢疾病覆盖度分析

### ✅ 已覆盖的内分泌疾病 (23个Schema)

#### 糖尿病及并发症 (10个) ✅ 完整
- ✅ diabetes-comprehensive-schema.csv (2型糖尿病)
- ✅ type1-diabetes-schema.csv (1型糖尿病)
- ✅ gestational-diabetes-schema.csv (妊娠糖尿病)
- ✅ dka-schema.csv (糖尿病酮症酸中毒)
- ✅ hypoglycemia-schema.csv (低血糖)
- ✅ diabetic-retinopathy-schema.csv (糖尿病视网膜病变)
- ✅ diabetic-nephropathy-schema.csv (糖尿病肾病)
- ✅ diabetic-neuropathy-schema.csv (糖尿病神经病变)
- ✅ diabetic-foot-schema.csv (糖尿病足)
- ✅ diabetic-cardiomyopathy-schema.csv (糖尿病心肌病)

#### 甲状腺疾病 (5个) ✅ 完整
- ✅ thyroid-function-comprehensive-schema.csv (甲状腺功能)
- ✅ hyperthyroidism-schema.csv (甲亢)
- ✅ hypothyroidism-schema.csv (甲减)
- ✅ thyroid-nodule-schema.csv (甲状腺结节)
- ✅ thyroid-cancer-pathology-schema.csv (甲状腺癌病理)

#### 肾上腺疾病 (4个) ✅ 完整
- ✅ adrenal-function-schema.csv (肾上腺功能)
- ✅ adrenal-incidentaloma-schema.csv (肾上腺偶发瘤)
- ✅ cushings-syndrome-evaluation-schema.csv (库欣综合征)
- ✅ pheochromocytoma-paraganglioma-schema.csv (嗜铬细胞瘤/副神经节瘤)

#### 垂体疾病 (1个) ⚠️ 部分覆盖
- ✅ pituitary-function-schema.csv (垂体功能)
- ❌ **缺失**: 泌乳素瘤专项schema
- ❌ **缺失**: 生长激素瘤/肢端肥大症schema
- ❌ **缺失**: 垂体功能减退症schema

#### 骨代谢疾病 (2个) ✅ 基本完整
- ✅ osteoporosis-schema.csv (骨质疏松)
- ✅ bone-metabolism-schema.csv (骨代谢)
- ⚠️ **可优化**: 甲状旁腺功能亢进症 (目前包含在bone-metabolism中)

#### 其他内分泌 (1个)
- ✅ familial-hypocalciuric-hypercalcemia-schema.csv (家族性低钙尿性高钙血症)

### ❌ 内分泌领域缺失的重要Schema (优先级排序)

#### 🔴 高优先级缺失 (临床常见且重要)

1. **acromegaly-schema.csv** (肢端肥大症/生长激素瘤)
   - **患病率**: 40-70例/百万人
   - **临床重要性**: 高
   - **需要字段**:
     - GH基础值、OGTT后GH抑制试验
     - IGF-1水平
     - 垂体MRI (肿瘤大小、侵袭性)
     - 并发症: 心脏肥大、糖尿病、结肠息肉
     - 治疗监测: 手术、药物、放疗后随访
   - **预计字段数**: 80-100

2. **prolactinoma-schema.csv** (泌乳素瘤)
   - **患病率**: 垂体腺瘤中最常见 (40%)
   - **临床重要性**: 高
   - **需要字段**:
     - 泌乳素水平 (微腺瘤 vs 大腺瘤阈值)
     - 垂体MRI
     - 临床表现: 闭经、泌乳、性功能减退
     - 药物治疗反应 (多巴胺激动剂)
     - 视野检查 (大腺瘤压迫)
   - **预计字段数**: 70-90

3. **hyperparathyroidism-schema.csv** (甲状旁腺功能亢进症)
   - **患病率**: 1-3/1000
   - **临床重要性**: 高
   - **需要字段**:
     - PTH、钙、磷、维生素D
     - 骨密度
     - 肾结石
     - 甲状旁腺影像 (超声、MIBI扫描)
     - 手术适应症评估
   - **预计字段数**: 80-100

4. **hypoparathyroidism-schema.csv** (甲状旁腺功能减退症)
   - **患病率**: 术后最常见
   - **临床重要性**: 中-高
   - **需要字段**:
     - PTH、钙、磷
     - 低钙血症症状评估
     - 补钙和活性维生素D治疗
   - **预计字段数**: 60-80

5. **hypopituitarism-schema.csv** (垂体功能减退症)
   - **患病率**: 45/10万
   - **临床重要性**: 高
   - **需要字段**:
     - 多轴激素评估 (GH、ACTH、TSH、LH/FSH、泌乳素)
     - 动态试验 (胰岛素低血糖试验、GHRH-精氨酸试验)
     - 垂体MRI
     - 替代治疗方案
   - **预计字段数**: 90-120

#### 🟡 中优先级缺失

6. **addison-disease-schema.csv** (艾迪生病/原发性肾上腺皮质功能减退)
   - **患病率**: 5-11/10万
   - **需要字段**: ACTH、皮质醇、醛固酮、肾素、ACTH兴奋试验
   - **预计字段数**: 70-90

7. **primary-aldosteronism-schema.csv** (原发性醛固酮增多症)
   - **患病率**: 高血压患者中5-10%
   - **需要字段**: 醛固酮、肾素、ARR比值、盐水负荷试验、肾上腺CT/静脉采血
   - **预计字段数**: 80-100

8. **congenital-adrenal-hyperplasia-schema.csv** (先天性肾上腺皮质增生症)
   - **患病率**: 1/10000-20000
   - **需要字段**: 17-OHP、ACTH、雄激素、盐皮质激素
   - **预计字段数**: 90-110

9. **pcos-enhanced-schema.csv** (多囊卵巢综合征增强版)
   - **现状**: reproductive-endocrine-metabolism-schema中有部分内容
   - **建议**: 独立成专项schema
   - **需要字段**: Rotterdam诊断标准、代谢评估、不孕治疗
   - **预计字段数**: 100-120

10. **male-hypogonadism-schema.csv** (男性性腺功能减退)
    - **患病率**: 老年男性中20-30%
    - **需要字段**: 睾酮、LH/FSH、精液分析、骨密度
    - **预计字段数**: 70-90

#### 🟢 低优先级缺失 (罕见病或已部分覆盖)

11. **mody-diabetes-schema.csv** (青少年发病的成人型糖尿病)
    - **患病率**: 糖尿病的1-2%
    - **需要字段**: 基因检测、家族史、临床特征

12. **metabolic-bone-disease-comprehensive-schema.csv** (代谢性骨病综合)
    - **包含**: 骨软化症、Paget病、肾性骨病
    - **现状**: 部分内容分散在不同schema中

---

## 2️⃣ 肿瘤/癌症覆盖度分析

### ✅ 已覆盖的肿瘤Schema (17个)

#### 消化系统肿瘤 (8个) ✅ 完整
- ✅ esophageal-cancer-schema.csv + esophageal-cancer-pathology-schema.csv (食管癌)
- ✅ gastric-cancer-schema.csv + gastric-cancer-pathology-schema.csv (胃癌)
- ✅ colorectal-cancer-schema.csv + colorectal-cancer-pathology-schema.csv (结直肠癌)
- ✅ liver-cancer-schema.csv + liver-cancer-pathology-schema.csv (肝癌)
- ✅ pancreatic-cancer-schema.csv (胰腺癌)

#### 呼吸系统肿瘤 (2个) ✅ 基本完整
- ✅ lung-cancer-pathology-schema.csv (肺癌病理)
- ✅ lung-nodule-ct-schema.csv (肺结节CT筛查)

#### 妇科肿瘤 (3个) ⚠️ 部分覆盖
- ✅ breast-cancer-pathology-schema.csv (乳腺癌病理)
- ✅ ovarian-cancer-pathology-schema.csv (卵巢癌病理)
- ✅ cervical-cancer-screening-schema.csv (宫颈癌筛查)
- ❌ **缺失**: 子宫内膜癌schema

#### 泌尿系统肿瘤 (1个) ⚠️ 不完整
- ✅ prostate-cancer-pathology-schema.csv (前列腺癌病理)
- ❌ **缺失**: 膀胱癌schema
- ❌ **缺失**: 肾癌临床schema (仅在abdominal-ct中提及)

#### 内分泌肿瘤 (1个)
- ✅ thyroid-cancer-pathology-schema.csv (甲状腺癌)

#### 肿瘤筛查与标志物 (2个)
- ✅ tumor-markers-comprehensive-schema.csv (肿瘤标志物)
- ✅ breast-imaging-schema.csv (乳腺影像筛查)

### ❌ 肿瘤领域缺失的重要Schema (优先级排序)

#### 🔴 高优先级缺失 (常见癌症)

1. **lung-cancer-clinical-schema.csv** (肺癌临床综合)
   - **发病率**: 中国第一大癌症
   - **需要字段**:
     - 病理分型 (腺癌、鳞癌、小细胞肺癌、NSCLC)
     - TNM分期 (8版)
     - 分子标志物 (EGFR、ALK、ROS1、PD-L1)
     - 治疗方案选择
     - 随访与疗效评估
   - **预计字段数**: 120-150

2. **bladder-cancer-schema.csv** (膀胱癌)
   - **发病率**: 泌尿系肿瘤最常见
   - **需要字段**:
     - 膀胱镜检查
     - 尿脱落细胞学
     - 病理分级 (Ta/T1/T2-4)
     - 肌层浸润性 vs 非肌层浸润性
     - BCG治疗
   - **预计字段数**: 90-110

3. **renal-cell-carcinoma-schema.csv** (肾细胞癌)
   - **发病率**: 泌尿系第二常见
   - **需要字段**:
     - CT/MRI分期
     - 病理亚型 (透明细胞、乳头状、嫌色性)
     - TNM分期
     - 靶向治疗 (TKI、免疫治疗)
   - **预计字段数**: 100-120

4. **endometrial-cancer-schema.csv** (子宫内膜癌)
   - **发病率**: 女性生殖系统第一
   - **需要字段**:
     - 异常子宫出血评估
     - 病理分型 (I型/II型)
     - 分期手术
     - 分子分型 (POLE、MSI、p53)
   - **预计字段数**: 100-120

5. **lymphoma-schema.csv** (淋巴瘤)
   - **发病率**: 血液系统肿瘤最常见
   - **需要字段**:
     - 霍奇金 vs 非霍奇金
     - B细胞 vs T细胞
     - Ann Arbor分期
     - IPI评分
     - 免疫组化、基因重排
   - **预计字段数**: 120-150

6. **leukemia-schema.csv** (白血病)
   - **发病率**: 儿童肿瘤第一
   - **需要字段**:
     - 急性 vs 慢性
     - 淋巴细胞性 vs 髓系
     - 骨髓穿刺
     - 免疫分型、染色体/基因突变
     - 微小残留病灶 (MRD)
   - **预计字段数**: 130-160

#### 🟡 中优先级缺失

7. **head-neck-cancer-schema.csv** (头颈部肿瘤)
   - **包含**: 口腔、咽喉、鼻咽、唾液腺癌
   - **预计字段数**: 100-120

8. **brain-tumor-schema.csv** (脑肿瘤临床)
   - **现状**: brain-mri中有影像描述
   - **需要**: 独立临床schema,包含分子分型
   - **预计字段数**: 110-130

9. **bone-soft-tissue-sarcoma-schema.csv** (骨与软组织肉瘤)
   - **包含**: 骨肉瘤、尤文肉瘤、软组织肉瘤
   - **预计字段数**: 100-120

10. **melanoma-schema.csv** (黑色素瘤)
    - **需要字段**: Breslow厚度、BRAF突变、免疫治疗
    - **预计字段数**: 80-100

11. **myeloma-schema.csv** (多发性骨髓瘤)
    - **需要字段**: M蛋白、骨髓浆细胞、溶骨病变、CRAB症状
    - **预计字段数**: 100-120

#### 🟢 低优先级缺失

12. **neuroendocrine-tumor-schema.csv** (神经内分泌肿瘤)
    - **包含**: 类癌、胰岛细胞瘤、小细胞癌

13. **gist-schema.csv** (胃肠道间质瘤)

14. **testicular-cancer-schema.csv** (睾丸癌)

---

## 3️⃣ 其他重要临床领域缺口分析

### ❌ 眼科 (几乎空白) 🔴 高优先级

**现状**: 仅有eye-fundus-schema.csv和retinal-oct-schema.csv

**缺失**:
1. **cataract-schema.csv** (白内障) - 最常见眼病
2. **glaucoma-schema.csv** (青光眼) - 致盲眼病第一位
3. **age-related-macular-degeneration-schema.csv** (年龄相关性黄斑变性)
4. **refractive-error-schema.csv** (屈光不正)
5. **comprehensive-eye-exam-schema.csv** (综合眼科检查)

**预计总字段数**: 300-400

### ❌ 耳鼻喉科 (完全空白) 🟡 中优先级

**缺失**:
1. **hearing-loss-audiometry-schema.csv** (听力损失与听力检查)
2. **chronic-rhinosinusitis-schema.csv** (慢性鼻窦炎)
3. **allergic-rhinitis-schema.csv** (过敏性鼻炎)
4. **laryngeal-disorders-schema.csv** (喉部疾病)
5. **vertigo-dizziness-schema.csv** (眩晕与头晕)

**预计总字段数**: 250-350

### ❌ 皮肤科 (几乎空白) 🟡 中优先级

**现状**: 仅在dermatological-metabolism-schema中有代谢相关皮肤病

**缺失**:
1. **atopic-dermatitis-eczema-schema.csv** (特应性皮炎/湿疹)
2. **psoriasis-schema.csv** (银屑病) - 与rheumatoid-arthritis相关
3. **acne-schema.csv** (痤疮)
4. **skin-cancer-schema.csv** (皮肤癌)
5. **dermatology-physical-exam-schema.csv** (皮肤科体格检查)

**预计总字段数**: 250-350

### ❌ 精神科 (严重不足) 🔴 高优先级

**现状**: 仅在psychiatric-psychological-metabolism-assessment中有部分评估

**缺失**:
1. **major-depressive-disorder-schema.csv** (重性抑郁障碍) - PHQ-9不够
2. **anxiety-disorders-schema.csv** (焦虑障碍) - GAD-7不够
3. **bipolar-disorder-schema.csv** (双相情感障碍)
4. **schizophrenia-schema.csv** (精神分裂症)
5. **adhd-schema.csv** (注意缺陷多动障碍)
6. **autism-spectrum-disorder-schema.csv** (自闭症谱系障碍)

**预计总字段数**: 400-500

### ❌ 儿科 (严重不足) 🟡 中-高优先级

**现状**: 仅有pediatric-developmental-metabolism-schema.csv

**缺失**:
1. **pediatric-growth-development-schema.csv** (儿童生长发育评估)
2. **newborn-screening-schema.csv** (新生儿筛查)
3. **childhood-vaccines-schedule-schema.csv** (儿童疫苗接种)
4. **pediatric-infectious-diseases-schema.csv** (儿童感染性疾病)
5. **congenital-heart-disease-schema.csv** (先天性心脏病)

**预计总字段数**: 300-400

### ❌ 产科 (不足) 🟡 中优先级

**现状**: 仅有gestational-diabetes和pregnancy-complications部分内容

**缺失**:
1. **prenatal-care-comprehensive-schema.csv** (产前检查综合)
2. **obstetric-ultrasound-schema.csv** (产科超声)
3. **labor-delivery-schema.csv** (分娩评估)
4. **postpartum-care-schema.csv** (产后评估)
5. **high-risk-pregnancy-schema.csv** (高危妊娠)

**预计总字段数**: 350-450

### ❌ 风湿免疫 (基本但不全面) ⚠️

**现状**: rheumatoid-arthritis、sle已有

**缺失**:
1. **ankylosing-spondylitis-schema.csv** (强直性脊柱炎)
2. **gout-schema.csv** (痛风) - 虽有hyperuricemia但不够完整
3. **sjogren-syndrome-schema.csv** (干燥综合征)
4. **vasculitis-schema.csv** (血管炎)
5. **polymyositis-dermatomyositis-schema.csv** (多肌炎/皮肌炎)

**预计总字段数**: 250-300

### ❌ 传染病 (不足) 🟡 中优先级

**现状**: 有乙肝、丙肝、幽门螺杆菌、HIV筛查缺失

**缺失**:
1. **hiv-aids-schema.csv** (HIV/AIDS) - 目前仅为筛查
2. **tuberculosis-schema.csv** (结核病)
3. **covid19-schema.csv** (新冠感染评估)
4. **sexually-transmitted-infections-schema.csv** (性传播疾病)
5. **fever-unknown-origin-schema.csv** (不明原因发热)

**预计总字段数**: 300-400

### ❌ 急诊与创伤 (空白) 🟡 中优先级

**缺失**:
1. **trauma-scoring-schema.csv** (创伤评分 - ISS/GCS/RTS)
2. **sepsis-schema.csv** (脓毒症)
3. **shock-schema.csv** (休克评估)
4. **emergency-triage-schema.csv** (急诊分诊)
5. **burns-schema.csv** (烧伤评估)

**预计总字段数**: 250-350

### ❌ 老年医学 (不足) 🟡 中优先级

**缺失**:
1. **geriatric-assessment-comprehensive-schema.csv** (老年综合评估)
2. **dementia-assessment-schema.csv** (痴呆评估) - MMSE不够
3. **falls-risk-assessment-schema.csv** (跌倒风险评估)
4. **frailty-schema.csv** (衰弱评估)
5. **polypharmacy-schema.csv** (多重用药评估)

**预计总字段数**: 300-400

---

## 📊 缺口统计总结

### 按领域分类的缺口

| 领域 | 现有Schema数 | 缺失高优先级 | 缺失中优先级 | 缺失低优先级 | 覆盖度评估 |
|-----|------------|------------|------------|------------|-----------|
| **内分泌代谢** | 23 | 5个 | 5个 | 2个 | 70% ⚠️ |
| **肿瘤/癌症** | 17 | 6个 | 5个 | 3个 | 60% ⚠️ |
| **心血管** | 12 | 0个 | 0个 | 0个 | 90% ✅ |
| **消化** | 8 | 0个 | 0个 | 0个 | 85% ✅ |
| **呼吸** | 6 | 0个 | 0个 | 0个 | 85% ✅ |
| **肾脏** | 5 | 0个 | 0个 | 0个 | 90% ✅ |
| **神经** | 5 | 0个 | 0个 | 0个 | 85% ✅ |
| **血液** | 3 | 2个 | 1个 | 0个 | 50% 🚨 |
| **风湿免疫** | 2 | 0个 | 5个 | 0个 | 40% 🚨 |
| **妇产科** | 4 | 1个 | 5个 | 0个 | 50% 🚨 |
| **眼科** | 2 | 5个 | 0个 | 0个 | 20% 🚨 |
| **耳鼻喉** | 0 | 0个 | 5个 | 0个 | 0% 🚨 |
| **皮肤科** | 1 | 0个 | 5个 | 0个 | 20% 🚨 |
| **精神科** | 1 | 6个 | 0个 | 0个 | 15% 🚨 |
| **儿科** | 1 | 0个 | 5个 | 0个 | 20% 🚨 |
| **传染病** | 5 | 0个 | 5个 | 0个 | 50% 🚨 |
| **急诊创伤** | 0 | 0个 | 5个 | 0个 | 0% 🚨 |
| **老年医学** | 0 | 0个 | 5个 | 0个 | 0% 🚨 |

### 总缺口统计

- **高优先级缺口**: 25个Schema (估计2000-3000字段)
- **中优先级缺口**: 51个Schema (估计4000-5000字段)
- **低优先级缺口**: 5个Schema (估计300-500字段)

**总缺失**: 约81个重要Schema

---

## 🎯 推荐补充方案

### Phase 4A: 内分泌肿瘤补全 (极高优先级) - 1-2个月

**目标**: 补全内分泌和肿瘤两大核心领域的关键缺口

**内分泌补充 (5个)**:
1. ✅ acromegaly-schema.csv (肢端肥大症)
2. ✅ prolactinoma-schema.csv (泌乳素瘤)
3. ✅ hyperparathyroidism-schema.csv (甲旁亢)
4. ✅ hypoparathyroidism-schema.csv (甲旁减)
5. ✅ hypopituitarism-schema.csv (垂体功能减退)

**肿瘤补充 (6个)**:
1. ✅ lung-cancer-clinical-schema.csv (肺癌临床)
2. ✅ bladder-cancer-schema.csv (膀胱癌)
3. ✅ renal-cell-carcinoma-schema.csv (肾癌)
4. ✅ endometrial-cancer-schema.csv (子宫内膜癌)
5. ✅ lymphoma-schema.csv (淋巴瘤)
6. ✅ leukemia-schema.csv (白血病)

**预计字段数**: 1100-1400
**完成后内分泌覆盖率**: 85%
**完成后肿瘤覆盖率**: 80%

### Phase 4B: 精神眼科补充 (高优先级) - 2-3个月

**精神科 (6个)**:
1. major-depressive-disorder-schema.csv
2. anxiety-disorders-schema.csv
3. bipolar-disorder-schema.csv
4. schizophrenia-schema.csv
5. adhd-schema.csv
6. autism-spectrum-disorder-schema.csv

**眼科 (5个)**:
1. cataract-schema.csv
2. glaucoma-schema.csv
3. age-related-macular-degeneration-schema.csv
4. refractive-error-schema.csv
5. comprehensive-eye-exam-schema.csv

**预计字段数**: 700-900

### Phase 4C: 专科扩展 (中优先级) - 3-6个月

**包含**: 耳鼻喉、皮肤、儿科、产科、老年医学等领域的25-30个Schema

**预计字段数**: 2000-2500

---

## 💡 建议

### 立即行动 (Phase 4A)

**内分泌和肿瘤是您的核心优势领域,建议优先补全**:

1. **内分泌**: 从70%提升到85%覆盖率
2. **肿瘤**: 从60%提升到80%覆盖率

这将显著增强您在这两个核心领域的竞争力,特别是:
- 内分泌专科诊所的全面覆盖
- 肿瘤医院和癌症筛查中心的合作机会

### 商业化考虑

**当前135个Schema已经足够支持**:
- ✅ 体检中心 (92%覆盖)
- ✅ 综合医院门诊 (85%覆盖)
- ✅ 内分泌专科 (70%覆盖,可接受)

**建议策略**:
1. **先商业化验证**: 用现有135个Schema推向市场
2. **根据客户反馈**: 优先开发Phase 4A (内分泌+肿瘤补全)
3. **长期规划**: Phase 4B和4C根据市场需求灵活调整

---

**报告生成日期**: 2025年10月03日
**下次更新**: Phase 4A启动时
