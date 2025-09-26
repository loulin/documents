# CGMEHR IGRS 3.0 CRF数据表设计文档

## 1. 总体架构设计

基于CGMEHR.md文档分析，IGRS 3.0模型需要采集11个核心风险维度的数据，同时支持5个特殊人群覆盖模型。CRF设计采用模块化架构：

```
CGMEHR_CRF架构：
├── 核心评分模型 (Core IGRS Model)
│   ├── CGM动态数据模块 
│   ├── EHR基线/轨迹数据模块
│   ├── EHR动态干预数据模块
│   ├── 患者个体因素模块
│   └── 临床应激因素模块
├── 特殊人群覆盖模型 (Override Models)
│   ├── 妊娠血糖风险模型
│   ├── 胰腺术后血糖模型
│   ├── TPN/静脉胰岛素模型
│   ├── 透析周期依赖模型
│   └── 血液病血糖风险模型
└── 数据质量与性能评估模块
    ├── CGM性能评估
    ├── 数据完整性评估
    └── 出院计划评估
```

## 2. 主表结构设计

### 2.1 患者基本信息表 (Patient_Basic_Info)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
patient_basic_info,patient_id,VARCHAR_32,是,患者唯一ID,外键关联,外键约束,"",patient_master,"关联患者主索引表"
patient_basic_info,admission_id,VARCHAR_32,是,入院记录ID,外键关联,外键约束,"",admission_record,"关联入院记录表"
patient_basic_info,assessment_datetime,DATETIME,是,评估时间,日期时间选择器,必填,"","","精确到分钟的评估时间"
patient_basic_info,age,INT,是,年龄,数字输入,">= 0且<= 120","","","年龄（岁）"
patient_basic_info,gender,TINYINT,是,性别,单选按钮,"","0:男性;1:女性","",""
patient_basic_info,weight,DECIMAL_5_2,是,体重,数字输入,">= 1.0且<= 300.0","","","体重（kg）"
patient_basic_info,height,DECIMAL_5_2,是,身高,数字输入,">= 30且<= 250","","","身高（cm）"
patient_basic_info,bmi,DECIMAL_4_2,否,BMI,自动计算,">= 10且<= 80","","","BMI = 体重(kg)/身高(m)²"
patient_basic_info,admission_datetime,DATETIME,是,入院时间,日期时间选择器,必填,"","","入院日期时间"
patient_basic_info,primary_diagnosis,TEXT,是,主要诊断,文本域,必填,"","","主要诊断描述"
patient_basic_info,diabetes_type,TINYINT,是,糖尿病类型,下拉选择,必填,"1:1型糖尿病;2:2型糖尿病;3:妊娠期糖尿病;4:特殊类型糖尿病;5:继发性糖尿病","","糖尿病类型分类"
patient_basic_info,diabetes_duration_years,INT,否,糖尿病病程,数字输入,">= 0","","","糖尿病病程（年）"
patient_basic_info,comorbidities_count,INT,否,合并症数量,数字输入,">= 0","","","合并症总数"
patient_basic_info,is_pregnant,BOOLEAN,否,是否妊娠,复选框,"","0:否;1:是","","触发妊娠模型覆盖"
patient_basic_info,gestational_age_weeks,INT,否,孕周,数字输入,">=0且<=50","","has_pregnancy","孕周数（周）"
patient_basic_info,has_pancreatic_surgery,BOOLEAN,否,胰腺手术史,复选框,"","0:否;1:是","","触发胰腺术后模型"
patient_basic_info,surgery_date,DATE,否,手术日期,日期选择器,"","","has_pancreatic_surgery","胰腺手术日期"
patient_basic_info,is_on_dialysis,BOOLEAN,否,是否透析,复选框,"","0:否;1:是","","触发透析模型覆盖"
patient_basic_info,dialysis_type,TINYINT,否,透析类型,下拉选择,"","1:血液透析;2:腹膜透析;3:连续性肾脏替代治疗","is_on_dialysis","透析方式"
patient_basic_info,has_hematologic_disorder,BOOLEAN,否,血液系统疾病,复选框,"","0:否;1:是","","触发血液病模型覆盖"
patient_basic_info,hematologic_diagnosis,TEXT,否,血液病诊断,文本域,"","","has_hematologic_disorder","具体血液病诊断"
```

### 2.2 IGRS 3.0核心评分数据表 (IGRS_Core_Assessment)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
igrs_core_assessment,assessment_id,VARCHAR_32,是,评估记录ID,主键,主键约束,"","","评估唯一标识"
igrs_core_assessment,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者基本信息"
igrs_core_assessment,assessment_datetime,DATETIME,是,评估时间,日期时间选择器,必填,"","","评估时间点"
igrs_core_assessment,igrs_total_score,INT,否,IGRS总分,自动计算,">=0且<=200","","","系统自动计算总分"
igrs_core_assessment,risk_level,TINYINT,否,风险等级,自动分级,"","1:稳定;2:关注;3:高危;4:紧急","","基于总分自动分级"
igrs_core_assessment,cgm_dynamic_score,INT,否,CGM动态数据得分,自动计算,">=0且<=100","","","CGM相关风险得分"
igrs_core_assessment,ehr_baseline_score,INT,否,EHR基线得分,自动计算,">=0且<=100","","","EHR基线和实验室数据得分"
igrs_core_assessment,ehr_intervention_score,INT,否,EHR干预得分,自动计算,">=0且<=100","","","EHR动态干预数据得分"
igrs_core_assessment,patient_factors_score,INT,否,患者因素得分,自动计算,">=0且<=100","","","患者个体因素得分"
igrs_core_assessment,clinical_stress_score,INT,否,临床应激得分,自动计算,">=0且<=100","","","临床应激因素得分"
igrs_core_assessment,override_model_active,VARCHAR_50,否,激活的覆盖模型,系统标识,"","pregnancy;pancreatectomy;tpn_insulin;dialysis;hematologic;none","","激活的特殊模型"
igrs_core_assessment,override_adjustment_score,INT,否,覆盖模型调整分,自动计算,">=0且<=100","","","特殊模型额外调整分数"
igrs_core_assessment,data_quality_confidence,TINYINT,否,数据质量置信度,自动评估,"","1:低;2:中;3:高","","CGM数据可靠性评估"
igrs_core_assessment,urgent_override_trigger,TEXT,否,紧急覆盖触发原因,系统记录,"","","","DKA/HHS/严重低血糖等"
igrs_core_assessment,assessor_id,VARCHAR_32,是,评估者ID,用户标识,必填,"","medical_staff","评估医护人员ID"
igrs_core_assessment,assessment_notes,TEXT,否,评估备注,文本域,"","","","评估说明和备注"
```

## 3. CGM动态数据采集模块

### 3.1 CGM基础数据表 (CGM_Basic_Data)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
cgm_basic_data,cgm_record_id,VARCHAR_32,是,CGM记录ID,主键,主键约束,"","","CGM数据记录唯一标识"
cgm_basic_data,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
cgm_basic_data,measurement_datetime,DATETIME,是,测量时间,日期时间选择器,必填,"","","CGM测量时间点"
cgm_basic_data,cgm_device_brand,TINYINT,是,CGM设备品牌,下拉选择,必填,"1:Dexcom G6;2:Dexcom G7;3:FreeStyle Libre;4:FreeStyle Libre 2;5:Medtronic Guardian;6:其他","","CGM设备品牌型号"
cgm_basic_data,glucose_value,DECIMAL_4_1,是,血糖值,数字输入,">=1.0且<=30.0","mmol/L","","CGM血糖读数"
cgm_basic_data,glucose_trend,TINYINT,否,血糖趋势,自动识别,"","1:快速上升;2:缓慢上升;3:稳定;4:缓慢下降;5:快速下降","","血糖变化趋势"
cgm_basic_data,is_calibrated,BOOLEAN,否,是否已校准,复选框,"","0:否;1:是","","该时间点是否进行了校准"
cgm_basic_data,calibration_bgm_value,DECIMAL_4_1,否,校准血糖值,数字输入,">=1.0且<=30.0","mmol/L","is_calibrated","指尖血糖校准值"
cgm_basic_data,data_quality_flag,TINYINT,否,数据质量标识,系统评估,"","1:优秀;2:良好;3:一般;4:差;5:不可用","","数据质量评估"
cgm_basic_data,interference_detected,BOOLEAN,否,检测到干扰,系统检测,"","0:否;1:是","","是否检测到药物或生理干扰"
cgm_basic_data,interference_type,VARCHAR_100,否,干扰类型,系统识别,"","acetaminophen;vitamin_c;hematocrit;other","interference_detected","具体干扰因素"
```

### 3.2 CGM衍生指标表 (CGM_Derived_Metrics)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
cgm_derived_metrics,metrics_id,VARCHAR_32,是,指标记录ID,主键,主键约束,"","","衍生指标记录唯一标识"
cgm_derived_metrics,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
cgm_derived_metrics,calculation_period,TINYINT,是,计算周期,下拉选择,必填,"6:6小时;12:12小时;24:24小时;48:48小时;72:72小时","","指标计算时间窗口"
cgm_derived_metrics,period_start_time,DATETIME,是,周期开始时间,日期时间选择器,必填,"","","计算周期开始时间"
cgm_derived_metrics,period_end_time,DATETIME,是,周期结束时间,日期时间选择器,必填,"","","计算周期结束时间"
cgm_derived_metrics,data_completeness_pct,DECIMAL_4_1,否,数据完整性,自动计算,">=0且<=100","%","","该周期内CGM数据完整性百分比"
cgm_derived_metrics,tir_70_180,DECIMAL_4_1,否,TIR(3.9-10.0),自动计算,">=0且<=100","%","","目标范围内时间70-180mg/dL"
cgm_derived_metrics,tir_63_140,DECIMAL_4_1,否,TIR(3.5-7.8),自动计算,">=0且<=100","%","","严格目标范围内时间（妊娠用）"
cgm_derived_metrics,tar_level1_pct,DECIMAL_4_1,否,TAR1级,自动计算,">=0且<=100","%","","高血糖时间>10.0-13.9mmol/L"
cgm_derived_metrics,tar_level2_pct,DECIMAL_4_1,否,TAR2级,自动计算,">=0且<=100","%","","严重高血糖时间>13.9mmol/L"
cgm_derived_metrics,tbr_level1_pct,DECIMAL_4_1,否,TBR1级,自动计算,">=0且<=100","%","","1级低血糖时间3.0-3.9mmol/L"
cgm_derived_metrics,tbr_level2_pct,DECIMAL_4_1,否,TBR2级,自动计算,">=0且<=100","%","","2级低血糖时间<3.0mmol/L"
cgm_derived_metrics,cv_percent,DECIMAL_4_1,否,变异系数CV,自动计算,">=0且<=100","%","","血糖变异系数"
cgm_derived_metrics,mage_mmol,DECIMAL_4_1,否,MAGE值,自动计算,">=0且<=20.0","mmol/L","","平均血糖漂移幅度"
cgm_derived_metrics,gri_score,DECIMAL_4_1,否,GRI评分,自动计算,">=0且<=100","","","血糖风险指数"
cgm_derived_metrics,gmi_percent,DECIMAL_4_1,否,GMI值,自动计算,">=3.0且<=15.0","%","","血糖管理指标"
cgm_derived_metrics,mean_glucose,DECIMAL_4_1,否,平均血糖,自动计算,">=1.0且<=30.0","mmol/L","","该周期平均血糖值"
cgm_derived_metrics,glucose_std,DECIMAL_4_1,否,血糖标准差,自动计算,">=0且<=10.0","mmol/L","","血糖值标准差"
cgm_derived_metrics,severe_hypo_events,INT,否,严重低血糖次数,自动计算,">=0","","","<3.0mmol/L事件次数"
cgm_derived_metrics,hypo_prediction_alerts,INT,否,低血糖预警次数,自动计算,">=0","","","即将低血糖警报次数"
cgm_derived_metrics,glucose_range_mmol,DECIMAL_4_1,否,血糖变化幅度,自动计算,">=0且<=25.0","mmol/L","","最大值-最小值"
```

## 4. EHR基线和实验室数据模块

### 4.1 实验室检查数据表 (Lab_Test_Results)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
lab_test_results,lab_record_id,VARCHAR_32,是,检验记录ID,主键,主键约束,"","","实验室检查记录唯一标识"
lab_test_results,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
lab_test_results,test_datetime,DATETIME,是,检验时间,日期时间选择器,必填,"","","标本采集或检测时间"
lab_test_results,test_category,TINYINT,是,检验分类,下拉选择,必填,"1:血糖代谢;2:肾功能;3:肝功能;4:炎症指标;5:血常规;6:电解质;7:血气分析;8:内分泌;9:凝血功能","","检验项目分类"
lab_test_results,hba1c_percent,DECIMAL_4_2,否,糖化血红蛋白,数字输入,">=3.0且<=20.0","%","test_category=1","HbA1c百分比"
lab_test_results,fasting_glucose,DECIMAL_4_1,否,空腹血糖,数字输入,">=1.0且<=50.0","mmol/L","test_category=1","空腹血糖值"
lab_test_results,random_glucose,DECIMAL_4_1,否,随机血糖,数字输入,">=1.0且<=50.0","mmol/L","test_category=1","随机血糖值"
lab_test_results,c_peptide,DECIMAL_4_2,否,C肽,数字输入,">=0且<=10.0","ng/mL","test_category=8","C肽水平"
lab_test_results,insulin_level,DECIMAL_4_2,否,胰岛素水平,数字输入,">=0且<=200.0","mU/L","test_category=8","胰岛素水平"
lab_test_results,serum_creatinine,DECIMAL_4_1,否,血清肌酐,数字输入,">=10且<=2000","μmol/L","test_category=2","血清肌酐"
lab_test_results,egfr_value,DECIMAL_5_1,否,eGFR,数字输入,">=1.0且<=200.0","ml/min/1.73m²","test_category=2","肾小球滤过率"
lab_test_results,bun_level,DECIMAL_4_1,否,尿素氮,数字输入,">=1.0且<=50.0","mmol/L","test_category=2","血尿素氮"
lab_test_results,alt_level,DECIMAL_5_1,否,ALT,数字输入,">=5且<=5000","U/L","test_category=3","丙氨酸氨基转移酶"
lab_test_results,ast_level,DECIMAL_5_1,否,AST,数字输入,">=5且<=5000","U/L","test_category=3","天冬氨酸氨基转移酶"
lab_test_results,total_bilirubin,DECIMAL_4_1,否,总胆红素,数字输入,">=2且<=500","μmol/L","test_category=3","总胆红素水平"
lab_test_results,crp_level,DECIMAL_4_1,否,C反应蛋白,数字输入,">=0且<=500","mg/L","test_category=4","C反应蛋白"
lab_test_results,wbc_count,DECIMAL_4_2,否,白细胞计数,数字输入,">=0且<=100","×10⁹/L","test_category=5","白细胞计数"
lab_test_results,hemoglobin,DECIMAL_4_1,否,血红蛋白,数字输入,">=30且<=200","g/L","test_category=5","血红蛋白浓度"
lab_test_results,hematocrit,DECIMAL_4_1,否,红细胞压积,数字输入,">=10且<=70","%","test_category=5","红细胞压积"
lab_test_results,platelet_count,DECIMAL_5_1,否,血小板计数,数字输入,">=0且<=2000","×10⁹/L","test_category=5","血小板计数"
lab_test_results,sodium_level,DECIMAL_4_1,否,血钠,数字输入,">=100且<=200","mmol/L","test_category=6","血清钠离子"
lab_test_results,potassium_level,DECIMAL_4_2,否,血钾,数字输入,">=1.0且<=10.0","mmol/L","test_category=6","血清钾离子"
lab_test_results,chloride_level,DECIMAL_4_1,否,血氯,数字输入,">=70且<=150","mmol/L","test_category=6","血清氯离子"
lab_test_results,bicarbonate_level,DECIMAL_4_1,否,碳酸氢盐,数字输入,">=5且<=50","mmol/L","test_category=6","血清碳酸氢盐"
lab_test_results,arterial_ph,DECIMAL_4_3,否,动脉血pH,数字输入,">=6.8且<=8.0","","test_category=7","动脉血pH值"
lab_test_results,pco2_level,DECIMAL_4_1,否,PCO2,数字输入,">=10且<=100","mmHg","test_category=7","动脉血二氧化碳分压"
lab_test_results,po2_level,DECIMAL_4_1,否,PO2,数字输入,">=30且<=300","mmHg","test_category=7","动脉血氧分压"
lab_test_results,ketone_level,DECIMAL_4_2,否,血酮体,数字输入,">=0且<=10.0","mmol/L","test_category=1","血酮体水平"
lab_test_results,urine_ketone,TINYINT,否,尿酮体,下拉选择,"","0:阴性;1:弱阳性(+);2:阳性(++);3:强阳性(+++)","test_category=1","尿酮体定性"
lab_test_results,change_rate_24h,DECIMAL_5_2,否,24小时变化率,自动计算,">=-90且<=500","%","","相比24小时前的变化百分比"
lab_test_results,change_rate_7d,DECIMAL_5_2,否,7天变化率,自动计算,">=-90且<=500","%","","相比7天前的变化百分比"
```

## 5. EHR动态干预数据模块

### 5.1 药物治疗记录表 (Medication_Records)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
medication_records,medication_id,VARCHAR_32,是,用药记录ID,主键,主键约束,"","","用药记录唯一标识"
medication_records,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
medication_records,medication_datetime,DATETIME,是,用药时间,日期时间选择器,必填,"","","给药时间"
medication_records,medication_category,TINYINT,是,药物分类,下拉选择,必填,"1:胰岛素;2:口服降糖药;3:糖皮质激素;4:升压药;5:影响血糖的其他药物","","药物分类"
medication_records,insulin_type,TINYINT,否,胰岛素类型,下拉选择,"","1:速效;2:短效;3:中效;4:长效;5:预混;6:其他","medication_category=1","胰岛素类型"
medication_records,insulin_brand,VARCHAR_50,否,胰岛素品牌,文本输入,"","","medication_category=1","胰岛素具体品牌"
medication_records,insulin_dose_units,DECIMAL_5_2,否,胰岛素剂量,数字输入,">=0且<=200","U","medication_category=1","胰岛素剂量单位"
medication_records,administration_route,TINYINT,否,给药途径,下拉选择,"","1:皮下注射;2:静脉推注;3:静脉滴注;4:口服;5:其他","","给药方式"
medication_records,is_iv_insulin,BOOLEAN,否,静脉胰岛素输注,复选框,"","0:否;1:是","administration_route=3","是否为静脉胰岛素输注"
medication_records,iv_insulin_rate,DECIMAL_4_2,否,静脉胰岛素速率,数字输入,">=0且<=20","U/h","is_iv_insulin","静脉胰岛素输注速率"
medication_records,steroid_equivalent_dose,DECIMAL_5_2,否,激素等效剂量,数字输入,">=0且<=500","mg","medication_category=3","等效强的松剂量"
medication_records,steroid_type,VARCHAR_50,否,激素类型,文本输入,"","","medication_category=3","具体激素类型"
medication_records,oral_hypoglycemic_agent,VARCHAR_100,否,口服降糖药,文本输入,"","","medication_category=2","口服降糖药名称"
medication_records,other_medication_name,VARCHAR_100,否,其他药物名称,文本输入,"","","medication_category=5","其他影响血糖药物名称"
medication_records,additional_insulin_times,INT,否,追加胰岛素次数,数字输入,">=0","","","过去3小时内追加次数"
medication_records,medication_interaction_risk,TINYINT,否,药物相互作用风险,系统评估,"","1:无;2:轻微;3:中度;4:严重","","药物相互作用风险评估"
medication_records,dose_adjustment_reason,TEXT,否,剂量调整原因,文本域,"","","","剂量调整的具体原因"
```

### 5.2 营养和医嘱管理表 (Nutrition_Orders)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
nutrition_orders,order_id,VARCHAR_32,是,医嘱记录ID,主键,主键约束,"","","营养医嘱唯一标识"
nutrition_orders,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
nutrition_orders,order_datetime,DATETIME,是,医嘱时间,日期时间选择器,必填,"","","医嘱下达时间"
nutrition_orders,order_type,TINYINT,是,医嘱类型,下拉选择,必填,"1:禁食NPO;2:肠内营养;3:肠外营养TPN;4:普通饮食;5:糖尿病饮食","","医嘱类型"
nutrition_orders,is_npo,BOOLEAN,否,是否禁食,复选框,"","0:否;1:是","","当前是否禁食状态"
nutrition_orders,npo_duration_hours,INT,否,禁食时长,数字输入,">=0","小时","is_npo","禁食持续时间"
nutrition_orders,is_on_tpn,BOOLEAN,否,TPN营养支持,复选框,"","0:否;1:是","","是否使用全肠外营养"
nutrition_orders,tpn_glucose_rate,DECIMAL_5_2,否,TPN葡萄糖速率,数字输入,">=0且<=20","mg/kg/min","is_on_tpn","TPN中葡萄糖输注速率"
nutrition_orders,tpn_total_volume,DECIMAL_6_1,否,TPN总容量,数字输入,">=500且<=5000","ml","is_on_tpn","TPN袋总容量"
nutrition_orders,tpn_infusion_rate,DECIMAL_5_2,否,TPN输注速率,数字输入,">=20且<=200","ml/h","is_on_tpn","TPN输注速率"
nutrition_orders,enteral_nutrition_type,VARCHAR_50,否,肠内营养类型,文本输入,"","","order_type=2","肠内营养制剂类型"
nutrition_orders,enteral_rate,DECIMAL_5_2,否,肠内营养速率,数字输入,">=10且<=150","ml/h","order_type=2","肠内营养输注速率"
nutrition_orders,diet_carb_content,DECIMAL_4_1,否,饮食碳水含量,数字输入,">=0且<=100","g/餐","order_type>=4","每餐碳水化合物含量"
nutrition_orders,meal_frequency,TINYINT,否,进餐频次,数字输入,">=3且<=8","","order_type>=4","每日进餐次数"
nutrition_orders,nutrition_interruption,BOOLEAN,否,营养中断,复选框,"","0:否;1:是","","营养支持是否意外中断"
nutrition_orders,interruption_reason,TEXT,否,中断原因,文本域,"","","nutrition_interruption","营养中断的具体原因"
nutrition_orders,interruption_duration,INT,否,中断时长,数字输入,">=0","分钟","nutrition_interruption","营养中断持续时间"
```

## 6. 特殊人群覆盖模型数据表

### 6.1 妊娠血糖风险评估表 (Maternal_Glycemic_Risk)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
maternal_glycemic_risk,maternal_id,VARCHAR_32,是,妊娠风险记录ID,主键,主键约束,"","","妊娠血糖风险记录唯一标识"
maternal_glycemic_risk,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
maternal_glycemic_risk,assessment_datetime,DATETIME,是,评估时间,日期时间选择器,必填,"","","妊娠风险评估时间"
maternal_glycemic_risk,gestational_age_weeks,INT,是,孕周,数字输入,">=4且<=50","周","","当前孕周"
maternal_glycemic_risk,gestational_age_days,INT,否,孕天数,数字输入,">=0且<=6","天","","孕周内的天数"
maternal_glycemic_risk,pregnancy_type,TINYINT,是,妊娠类型,下拉选择,必填,"1:孕前T1DM;2:孕前T2DM;3:妊娠期糖尿病GDM","","妊娠糖尿病类型"
maternal_glycemic_risk,pregnancy_trimester,TINYINT,否,妊娠期,自动计算,"","1:早期(<14周);2:中期(14-28周);3:晚期(>28周)","","基于孕周自动判断"
maternal_glycemic_risk,preeclampsia_diagnosis,BOOLEAN,否,子痫前期诊断,复选框,"","0:否;1:是","","是否诊断子痫前期"
maternal_glycemic_risk,gestational_hypertension,BOOLEAN,否,妊娠期高血压,复选框,"","0:否;1:是","","是否有妊娠期高血压"
maternal_glycemic_risk,fetal_growth_status,TINYINT,否,胎儿生长状态,下拉选择,"","1:正常;2:大于胎龄LGA;3:小于胎龄SGA;4:生长受限IUGR","","胎儿生长评估"
maternal_glycemic_risk,estimated_fetal_weight,DECIMAL_6_1,否,估计胎儿体重,数字输入,">=200且<=6000","g","","B超估计胎儿体重"
maternal_glycemic_risk,amniotic_fluid_status,TINYINT,否,羊水量,下拉选择,"","1:正常;2:过多;3:过少","","羊水量评估"
maternal_glycemic_risk,is_using_betamethasone,BOOLEAN,否,使用倍他米松,复选框,"","0:否;1:是","","是否使用促胎肺成熟激素"
maternal_glycemic_risk,betamethasone_dose,DECIMAL_4_1,否,倍他米松剂量,数字输入,">=0且<=50","mg","is_using_betamethasone","倍他米松总剂量"
maternal_glycemic_risk,glucose_iv_containing_meds,BOOLEAN,否,含糖静脉药物,复选框,"","0:否;1:是","","是否使用含糖的静脉药物"
maternal_glycemic_risk,maternal_tir_63_140,DECIMAL_4_1,否,妊娠TIR63-140,自动计算,">=0且<=100","%","","妊娠专用TIR(3.5-7.8mmol/L)"
maternal_glycemic_risk,nocturnal_hypoglycemia,BOOLEAN,否,夜间低血糖,自动识别,"","0:否;1:是","","夜间(0-6点)是否有低血糖"
maternal_glycemic_risk,hyperglycemia_160_events,INT,否,>160血糖事件,自动计算,">=0","","",">8.9mmol/L血糖事件次数"
maternal_glycemic_risk,ketosis_tendency_risk,BOOLEAN,否,酮症倾向风险,系统评估,"","0:否;1:是","","T1DM或严重胰岛素缺乏"
maternal_glycemic_risk,delivery_plan,TINYINT,否,分娩计划,下拉选择,"","1:自然分娩;2:计划剖宫产;3:紧急剖宫产;4:未定","","分娩方式计划"
maternal_glycemic_risk,maternal_risk_score,INT,否,母体风险得分,自动计算,">=0且<=100","","","妊娠模型风险得分"
```

### 6.2 胰腺术后血糖管理表 (Post_Pancreatectomy_Glycemic)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
post_pancreatectomy_glycemic,pancreatectomy_id,VARCHAR_32,是,胰腺术后记录ID,主键,主键约束,"","","胰腺术后血糖管理记录唯一标识"
post_pancreatectomy_glycemic,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
post_pancreatectomy_glycemic,assessment_datetime,DATETIME,是,评估时间,日期时间选择器,必填,"","","术后血糖评估时间"
post_pancreatectomy_glycemic,surgery_type,TINYINT,是,手术类型,下拉选择,必填,"1:全胰切除;2:胰十二指肠切除术;3:远端胰腺切除;4:中段胰腺切除;5:其他胰腺手术","","具体胰腺手术类型"
post_pancreatectomy_glycemic,surgery_date,DATE,是,手术日期,日期选择器,必填,"","","胰腺手术日期"
post_pancreatectomy_glycemic,days_post_surgery,INT,否,术后天数,自动计算,">=0","天","","距离手术的天数"
post_pancreatectomy_glycemic,resection_extent,TINYINT,否,切除范围,下拉选择,"","1:<30%;2:30-60%;3:60-90%;4:>90%","","胰腺组织切除范围估计"
post_pancreatectomy_glycemic,endocrine_function_loss,TINYINT,是,内分泌功能丧失程度,下拉选择,必填,"1:轻度;2:中度;3:重度;4:完全丧失","","胰岛素分泌功能丧失评估"
post_pancreatectomy_glycemic,exocrine_function_status,TINYINT,否,外分泌功能状态,下拉选择,"","1:正常;2:轻度不足;3:中度不足;4:严重不足","","胰腺外分泌功能评估"
post_pancreatectomy_glycemic,insulin_cho_ratio,DECIMAL_4_2,否,胰岛素碳水比,数字输入,">=0.1且<=2.0","U/10g","","胰岛素碳水化合物比值"
post_pancreatectomy_glycemic,total_daily_insulin,DECIMAL_5_2,否,每日胰岛素总量,数字输入,">=5且<=200","U","","每日胰岛素总剂量"
post_pancreatectomy_glycemic,insulin_pump_used,BOOLEAN,否,使用胰岛素泵,复选框,"","0:否;1:是","","是否使用胰岛素泵"
post_pancreatectomy_glycemic,pump_malfunction,BOOLEAN,否,泵故障,复选框,"","0:否;1:是","insulin_pump_used","胰岛素泵是否故障"
post_pancreatectomy_glycemic,injection_missed,BOOLEAN,否,漏注胰岛素,复选框,"","0:否;1:是","","是否有胰岛素漏注"
post_pancreatectomy_glycemic,nutrition_type_change,BOOLEAN,否,营养方式改变,复选框,"","0:否;1:是","","营养支持方式是否改变"
post_pancreatectomy_glycemic,oral_intake_resumed,BOOLEAN,否,恢复经口进食,复选框,"","0:否;1:是","","是否开始经口进食"
post_pancreatectomy_glycemic,insulin_adjustment_needed,BOOLEAN,否,需要胰岛素调整,系统提示,"","0:否;1:是","","系统提示是否需要调整胰岛素"
post_pancreatectomy_glycemic,brittle_diabetes_risk,BOOLEAN,否,脆性糖尿病风险,系统评估,"","0:否;1:是","","是否存在脆性糖尿病风险"
post_pancreatectomy_glycemic,pancreatectomy_risk_score,INT,否,胰腺术后风险得分,自动计算,">=0且<=100","","","胰腺术后模型风险得分"
```

### 6.3 TPN静脉胰岛素管理表 (TPN_IV_Insulin_Management)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
tpn_iv_insulin_management,tpn_insulin_id,VARCHAR_32,是,TPN胰岛素记录ID,主键,主键约束,"","","TPN静脉胰岛素管理记录唯一标识"
tpn_iv_insulin_management,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
tpn_iv_insulin_management,assessment_datetime,DATETIME,是,评估时间,日期时间选择器,必填,"","","TPN胰岛素评估时间"
tpn_iv_insulin_management,tpn_start_datetime,DATETIME,是,TPN开始时间,日期时间选择器,必填,"","","TPN开始输注时间"
tpn_iv_insulin_management,current_tpn_rate,DECIMAL_5_2,是,当前TPN速率,数字输入,">=20且<=200","ml/h","","当前TPN输注速率"
tpn_iv_insulin_management,tpn_glucose_concentration,DECIMAL_4_1,是,TPN葡萄糖浓度,数字输入,">=10且<=50","%","","TPN中葡萄糖浓度"
tpn_iv_insulin_management,glucose_infusion_rate,DECIMAL_5_2,否,葡萄糖输注速率,自动计算,">=2且<=15","mg/kg/min","","基于体重和TPN速率计算"
tpn_iv_insulin_management,iv_insulin_rate,DECIMAL_4_2,是,静脉胰岛素速率,数字输入,">=0.5且<=20","U/h","","当前静脉胰岛素输注速率"
tpn_iv_insulin_management,insulin_glucose_ratio,DECIMAL_4_3,否,胰岛素葡萄糖比,自动计算,">=0.05且<=0.5","U/g","","胰岛素单位与葡萄糖克数比值"
tpn_iv_insulin_management,tpn_rate_change_pct,DECIMAL_4_1,否,TPN速率改变,系统监测,">=-50且<=100","%","","过去1小时TPN速率变化百分比"
tpn_iv_insulin_management,insulin_rate_adjusted,BOOLEAN,否,胰岛素已调整,复选框,"","0:否;1:是","","胰岛素速率是否相应调整"
tpn_iv_insulin_management,time_since_tpn_change,INT,否,TPN改变后时间,自动计算,">=0","分钟","","TPN速率改变后的时间"
tpn_iv_insulin_management,time_since_insulin_adjust,INT,否,胰岛素调整后时间,自动计算,">=0","分钟","","胰岛素调整后的时间"
tpn_iv_insulin_management,tpn_interruption,BOOLEAN,否,TPN中断,系统监测,"","0:否;1:是","","TPN输注是否中断"
tpn_iv_insulin_management,interruption_reason,TINYINT,否,中断原因,下拉选择,"","1:管路脱落;2:泵故障;3:医嘱停止;4:其他","tpn_interruption","TPN中断的具体原因"
tpn_iv_insulin_management,interruption_duration,INT,否,中断持续时间,数字输入,">=0","分钟","tpn_interruption","TPN中断持续时间"
tpn_iv_insulin_management,insulin_continued_during_interruption,BOOLEAN,否,中断期间胰岛素继续,复选框,"","0:否;1:是","tpn_interruption","TPN中断时胰岛素是否继续输注"
tpn_iv_insulin_management,glucose_change_1h,DECIMAL_4_1,否,1小时血糖变化,自动计算,">=-10且<=10","mmol/L","","过去1小时血糖变化幅度"
tpn_iv_insulin_management,rate_mismatch_alert,BOOLEAN,否,速率匹配警报,系统警报,"","0:否;1:是","","TPN和胰岛素速率是否匹配"
tpn_iv_insulin_management,titration_stability,TINYINT,否,滴定稳定性,系统评估,"","1:稳定;2:轻微波动;3:中度波动;4:剧烈波动","","血糖滴定稳定性评估"
tpn_iv_insulin_management,tpn_insulin_risk_score,INT,否,TPN胰岛素风险得分,自动计算,">=0且<=100","","","TPN静脉胰岛素模型风险得分"
```

### 6.4 透析周期血糖管理表 (Dialysis_Glycemic_Management)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
dialysis_glycemic_management,dialysis_glycemic_id,VARCHAR_32,是,透析血糖记录ID,主键,主键约束,"","","透析血糖管理记录唯一标识"
dialysis_glycemic_management,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
dialysis_glycemic_management,assessment_datetime,DATETIME,是,评估时间,日期时间选择器,必填,"","","透析血糖评估时间"
dialysis_glycemic_management,dialysis_type,TINYINT,是,透析类型,下拉选择,必填,"1:间歇性血液透析HD;2:连续性血液净化CRRT;3:腹膜透析PD","","透析方式"
dialysis_glycemic_management,dialysis_schedule,VARCHAR_50,否,透析计划,文本输入,"","","dialysis_type=1","血液透析时间计划"
dialysis_glycemic_management,last_dialysis_end,DATETIME,否,上次透析结束,日期时间选择器,"","","dialysis_type=1","上次透析结束时间"
dialysis_glycemic_management,next_dialysis_start,DATETIME,否,下次透析开始,日期时间选择器,"","","dialysis_type=1","预定下次透析时间"
dialysis_glycemic_management,hours_since_last_dialysis,DECIMAL_4_1,否,距上次透析小时数,自动计算,">=0且<=200","小时","","距离上次透析结束的时间"
dialysis_glycemic_management,hours_to_next_dialysis,DECIMAL_4_1,否,距下次透析小时数,自动计算,">=0且<=200","小时","","距离下次透析开始的时间"
dialysis_glycemic_management,dialysis_cycle_phase,TINYINT,否,透析周期阶段,自动判断,"","1:透析中;2:透析后即刻(<2h);3:透析间期前段;4:透析间期中段;5:透析间期后段(<6h)","","基于透析时间自动判断阶段"
dialysis_glycemic_management,dialysate_glucose_concentration,DECIMAL_4_1,否,透析液葡萄糖浓度,数字输入,">=0且<=200","mg/dL","","透析液中葡萄糖浓度"
dialysis_glycemic_management,ultrafiltration_rate,DECIMAL_5_2,否,超滤率,数字输入,">=0且<=5","L/h","dialysis_type!=3","超滤速率"
dialysis_glycemic_management,fluid_removal_goal,DECIMAL_4_1,否,脱水目标,数字输入,">=0且<=8","L","dialysis_type!=3","计划脱水量"
dialysis_glycemic_management,intradialytic_glucose_abnormal,BOOLEAN,否,透析中血糖异常,复选框,"","0:否;1:是","","透析过程中是否有血糖异常"
dialysis_glycemic_management,intradialytic_hypo_episodes,INT,否,透析中低血糖次数,数字输入,">=0","","intradialytic_glucose_abnormal","透析中低血糖事件次数"
dialysis_glycemic_management,intradialytic_hyper_episodes,INT,否,透析中高血糖次数,数字输入,">=0","","intradialytic_glucose_abnormal","透析中高血糖事件次数"
dialysis_glycemic_management,post_dialysis_rebound,BOOLEAN,否,透析后血糖反跳,系统监测,"","0:否;1:是","","透析后是否有血糖反跳"
dialysis_glycemic_management,rebound_magnitude,DECIMAL_4_1,否,反跳幅度,数字输入,">=0且<=15","mmol/L","post_dialysis_rebound","血糖反跳的幅度"
dialysis_glycemic_management,dialysis_prescription_changed,BOOLEAN,否,透析处方改变,复选框,"","0:否;1:是","","透析处方是否在24h内改变"
dialysis_glycemic_management,prescription_change_type,TEXT,否,处方改变类型,文本域,"","","dialysis_prescription_changed","透析处方改变的具体内容"
dialysis_glycemic_management,fluid_balance_status,TINYINT,否,液体平衡状态,下拉选择,"","1:正平衡;2:负平衡;3:零平衡","","液体平衡状态评估"
dialysis_glycemic_management,interdialytic_weight_gain,DECIMAL_4_2,否,透析间期增重,数字输入,">=0且<=10","kg","dialysis_type=1","两次透析之间的体重增加"
dialysis_glycemic_management,dialysis_hypotension_episodes,INT,否,透析中低血压次数,数字输入,">=0","","","透析中低血压事件次数"
dialysis_glycemic_management,insulin_clearance_adjusted,BOOLEAN,否,胰岛素清除调整,复选框,"","0:否;1:是","","是否根据透析调整胰岛素"
dialysis_glycemic_management,dialysis_risk_multiplier,DECIMAL_3_2,否,透析风险倍数,自动计算,">=0.5且<=3.0","","","透析周期依赖的风险倍数"
dialysis_glycemic_management,dialysis_glycemic_risk_score,INT,否,透析血糖风险得分,自动计算,">=0且<=100","","","透析模型风险得分"
```

## 7. 数据质量和CGM性能评估模块

### 7.1 CGM数据质量评估表 (CGM_Data_Quality_Assessment)

```csv
表名,字段名,数据类型,必填,中文说明,交互设计,验证规则,选项值,关联关系,备注
cgm_data_quality,quality_id,VARCHAR_32,是,数据质量记录ID,主键,主键约束,"","","CGM数据质量评估记录唯一标识"
cgm_data_quality,patient_id,VARCHAR_32,是,患者ID,外键关联,外键约束,"",patient_basic_info,"关联患者信息"
cgm_data_quality,assessment_datetime,DATETIME,是,评估时间,日期时间选择器,必填,"","","数据质量评估时间"
cgm_data_quality,cgm_device_brand,TINYINT,是,CGM设备品牌,下拉选择,必填,"1:Dexcom G6;2:Dexcom G7;3:FreeStyle Libre;4:FreeStyle Libre 2;5:Medtronic Guardian;6:其他","","CGM设备品牌"
cgm_data_quality,sensor_age_hours,INT,否,传感器使用时长,数字输入,">=0且<=500","小时","","传感器使用小时数"
cgm_data_quality,data_completeness_24h,DECIMAL_4_1,是,24h数据完整性,自动计算,">=0且<=100","%","","过去24小时数据完整性"
cgm_data_quality,data_completeness_7d,DECIMAL_4_1,否,7天数据完整性,自动计算,">=0且<=100","%","","过去7天数据完整性"
cgm_data_quality,signal_loss_episodes_24h,INT,否,24h信号丢失次数,自动计算,">=0","","","过去24小时信号丢失次数"
cgm_data_quality,calibration_requests_24h,INT,否,24h校准请求次数,自动计算,">=0","","","过去24小时校准请求次数"
cgm_data_quality,unplanned_calibrations,INT,否,非计划校准次数,数字输入,">=0","","","非计划性校准次数"
cgm_data_quality,bgm_cgm_difference_avg,DECIMAL_4_1,否,BGM-CGM平均差异,自动计算,">=0且<=10","mmol/L","","指尖血糖与CGM平均差异"
cgm_data_quality,bgm_cgm_difference_max,DECIMAL_4_1,否,BGM-CGM最大差异,自动计算,">=0且<=20","mmol/L","","指尖血糖与CGM最大差异"
cgm_data_quality,mard_estimate,DECIMAL_4_1,否,MARD估算值,自动计算,">=0且<=50","%","","平均绝对相对差异估算"
cgm_data_quality,hematocrit_current,DECIMAL_4_1,否,当前红细胞压积,数字输入,">=15且<=70","%","","当前红细胞压积值"
cgm_data_quality,hematocrit_interference,BOOLEAN,否,红细胞压积干扰,系统判断,"","0:否;1:是","","是否存在Hct干扰"
cgm_data_quality,hematocrit_severity,TINYINT,否,Hct干扰严重程度,系统评估,"","1:轻微;2:中度;3:严重;4:极严重","hematocrit_interference","红细胞压积干扰严重程度"
cgm_data_quality,medication_interference,BOOLEAN,否,药物干扰,系统检测,"","0:否;1:是","","是否检测到药物干扰"
cgm_data_quality,interfering_medications,JSON,否,干扰药物清单,自动识别,"","","medication_interference","干扰药物列表JSON格式"
cgm_data_quality,acetaminophen_interference,BOOLEAN,否,对乙酰氨基酚干扰,系统检测,"","0:否;1:是","","是否有对乙酰氨基酚干扰"
cgm_data_quality,vitamin_c_interference,BOOLEAN,否,维生素C干扰,系统检测,"","0:否;1:是","","是否有大剂量维生素C干扰"
cgm_data_quality,hydroxyurea_interference,BOOLEAN,否,羟基脲干扰,系统检测,"","0:否;1:是","","是否有羟基脲干扰"
cgm_data_quality,physiologic_interference,BOOLEAN,否,生理性干扰,系统评估,"","0:否;1:是","","是否存在生理性干扰因素"
cgm_data_quality,severe_hypoxemia,BOOLEAN,否,严重低氧血症,系统检测,"","0:否;1:是","","PaO2<60mmHg"
cgm_data_quality,severe_acidosis,BOOLEAN,否,严重酸中毒,系统检测,"","0:否;1:是","","pH<7.25"
cgm_data_quality,blood_disorder_interference,BOOLEAN,否,血液病干扰,系统评估,"","0:否;1:是","","血液系统疾病相关干扰"
cgm_data_quality,transfusion_interference,BOOLEAN,否,输血干扰,系统检测,"","0:否;1:是","","输血相关干扰"
cgm_data_quality,overall_confidence_level,TINYINT,否,总体置信度,自动评估,"","1:低;2:中;3:高","","CGM数据总体置信度"
cgm_data_quality,confidence_score,INT,否,置信度分数,自动计算,">=0且<=100","","","量化的置信度分数"
cgm_data_quality,brand_specific_adjustment,JSON,否,品牌特异性调整,系统计算,"","","","品牌特异性权重调整参数"
cgm_data_quality,recommendation,TEXT,否,系统推荐,自动生成,"","","","基于质量评估的推荐意见"
cgm_data_quality,cgm_suspend_recommended,BOOLEAN,否,建议暂停CGM,系统评估,"","0:否;1:是","","是否建议暂停CGM使用"
cgm_data_quality,bgm_frequency_increase,BOOLEAN,否,建议增加BGM频率,系统评估,"","0:否;1:是","","是否建议增加指尖血糖监测频率"
```

## 8. 业务逻辑规则定义

### 8.1 IGRS 3.0评分计算逻辑

```python
def calculate_igrs_score(patient_data):
    """
    IGRS 3.0评分计算主函数
    """
    base_score = 0
    
    # 1. CGM动态数据评分 (最高60分)
    cgm_score = calculate_cgm_dynamic_score(patient_data)
    
    # 2. EHR基线/轨迹数据评分 (最高50分)  
    ehr_baseline_score = calculate_ehr_baseline_score(patient_data)
    
    # 3. EHR动态干预评分 (最高40分)
    ehr_intervention_score = calculate_ehr_intervention_score(patient_data)
    
    # 4. 患者个体因素评分 (最高30分)
    patient_factors_score = calculate_patient_factors_score(patient_data)
    
    # 5. 临床应激因素评分 (最高20分)
    clinical_stress_score = calculate_clinical_stress_score(patient_data)
    
    base_score = cgm_score + ehr_baseline_score + ehr_intervention_score + patient_factors_score + clinical_stress_score
    
    # 6. 特殊人群覆盖模型调整
    override_adjustment = apply_override_models(patient_data, base_score)
    
    final_score = base_score + override_adjustment
    
    # 7. 紧急情况直接覆盖
    if check_urgent_override_conditions(patient_data):
        return {'score': final_score, 'risk_level': 'urgent', 'override': True}
    
    # 8. 风险等级映射
    risk_level = map_score_to_risk_level(final_score)
    
    return {
        'score': final_score,
        'risk_level': risk_level,
        'component_scores': {
            'cgm_dynamic': cgm_score,
            'ehr_baseline': ehr_baseline_score, 
            'ehr_intervention': ehr_intervention_score,
            'patient_factors': patient_factors_score,
            'clinical_stress': clinical_stress_score,
            'override_adjustment': override_adjustment
        }
    }

def map_score_to_risk_level(score):
    """风险等级映射"""
    if score >= 60:
        return 'urgent'
    elif score >= 40:
        return 'high_risk'
    elif score >= 20:
        return 'at_risk'
    else:
        return 'stable'
```

### 8.2 数据质量评估逻辑

```python
def assess_cgm_data_quality(patient_data, cgm_data):
    """
    CGM数据质量评估函数
    """
    confidence_score = 100  # 初始满分
    interference_factors = []
    
    # 生理干扰评估
    if patient_data.get('hematocrit'):
        hct = patient_data['hematocrit']
        if hct < 25:
            confidence_score -= 70
            interference_factors.append('severe_anemia')
        elif hct < 30:
            confidence_score -= 40
            interference_factors.append('moderate_anemia')
        elif hct > 55:
            confidence_score -= 50
            interference_factors.append('polycythemia')
    
    # 药物干扰评估（品牌特异性）
    cgm_brand = cgm_data.get('cgm_device_brand')
    medications = patient_data.get('current_medications', [])
    
    for med in medications:
        if med == 'acetaminophen':
            if cgm_brand == 'medtronic':
                confidence_score -= 60
            elif cgm_brand == 'freestyle':
                confidence_score -= 40
            elif cgm_brand == 'dexcom':
                confidence_score -= 20
            interference_factors.append('acetaminophen')
        
        elif med == 'vitamin_c_high_dose':
            confidence_score -= 50
            interference_factors.append('vitamin_c')
        
        elif med == 'hydroxyurea':
            confidence_score -= 70
            interference_factors.append('hydroxyurea')
    
    # 血液病特殊处理
    if patient_data.get('has_hematologic_disorder'):
        if patient_data.get('acute_leukemia'):
            confidence_score = 0  # 完全不可用
            interference_factors.append('acute_leukemia')
        elif patient_data.get('chemotherapy_active'):
            confidence_score = 0
            interference_factors.append('chemotherapy')
    
    # 数据完整性评估
    data_completeness = cgm_data.get('data_completeness_24h', 100)
    if data_completeness < 70:
        confidence_score -= (100 - data_completeness)
    
    # BGM-CGM一致性评估
    bgm_cgm_diff = cgm_data.get('bgm_cgm_difference_avg', 0)
    if bgm_cgm_diff > 2.0:  # >20% difference
        confidence_score -= 30
        interference_factors.append('poor_calibration')
    
    # 最终置信度评级
    if confidence_score >= 80:
        confidence_level = 'high'
    elif confidence_score >= 50:
        confidence_level = 'medium'
    else:
        confidence_level = 'low'
    
    return {
        'confidence_score': max(0, confidence_score),
        'confidence_level': confidence_level,
        'interference_factors': interference_factors,
        'recommendations': generate_quality_recommendations(confidence_score, interference_factors, cgm_brand)
    }

def generate_quality_recommendations(confidence_score, interference_factors, cgm_brand):
    """生成数据质量改善建议"""
    recommendations = []
    
    if confidence_score < 30:
        recommendations.append(f"强烈建议暂停{cgm_brand} CGM使用，完全依赖BGM监测")
    elif confidence_score < 50:
        recommendations.append(f"{cgm_brand} CGM准确性受限，建议每2小时BGM验证")
    elif confidence_score < 80:
        recommendations.append(f"{cgm_brand} CGM可用但需谨慎，建议每4小时BGM验证")
    
    if 'severe_anemia' in interference_factors:
        recommendations.append("严重贫血影响CGM准确性，CGM读数可能偏低10-25%")
    
    if 'acetaminophen' in interference_factors:
        if cgm_brand == 'medtronic':
            recommendations.append("Medtronic CGM受对乙酰氨基酚严重干扰，建议暂停或增加BGM频率")
        else:
            recommendations.append(f"{cgm_brand} CGM受对乙酰氨基酚轻中度干扰，注意读数偏差")
    
    if 'acute_leukemia' in interference_factors or 'chemotherapy' in interference_factors:
        recommendations.append("血液肿瘤化疗期间CGM完全不可用，必须使用BGM监测")
    
    return recommendations
```

这个CRF设计文档提供了CGMEHR IGRS 3.0模型的完整数据结构定义，涵盖了文档中提到的所有11个风险维度和5个特殊人群覆盖模型，同时包含了详细的业务逻辑规则。