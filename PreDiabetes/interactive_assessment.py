#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式糖尿病风险评估工具
基于PreDiab.md文档的用户友好界面

使用方法：python interactive_assessment.py
"""

import json
from PreDiab_RiskAssessment_Script import DiabetesRiskAssessment, PatientData

def population_screening():
    """人群筛选和分流"""
    print("="*60)
    print("糖尿病风险评估系统")
    print("="*60)
    
    print("\n请提供基本信息以确定适用的评估方法：")
    
    # 年龄筛选
    while True:
        try:
            age = int(input("年龄 (岁): "))
            if 1 <= age <= 120:
                break
            else:
                print("请输入合理的年龄范围")
        except ValueError:
            print("请输入有效的数字")
    
    # 性别确认
    while True:
        gender = input("性别 (男/女): ").strip()
        if gender in ["男", "女"]:
            break
        else:
            print("请输入'男'或'女'")
    
    # 妊娠状态(仅女性)
    is_pregnant = False
    if gender == "女":
        pregnant_input = input("是否怀孕？(是/否): ").strip()
        is_pregnant = pregnant_input == "是"
    
    # 糖尿病诊断状态
    diabetes_diagnosed = input("是否已确诊糖尿病？(是/否): ").strip() == "是"
    
    print("\n" + "="*60)
    print("人群分类结果：")
    print("="*60)
    
    # 分流逻辑 (基于ADA/ISPAD 2024指南)
    if age < 10:
        print("🚫 学龄前儿童(<10岁)")
        print("说明：青春期前儿童代谢特点不同，糖尿病发病率极低")
        print("建议：如有家族史或症状，请咨询儿科内分泌专科")
        return None
    
    elif 10 <= age < 18:
        print("👶 儿童青少年(10-18岁)")
        print("说明：青春期开始后胰岛素抵抗风险增加，需专用评估体系")
        print("特点：需要家长参与，使用年龄调整BMI标准")
        print("建议：请使用儿童青少年2型糖尿病专用评估体系")
        print("文档路径：/docs/Pediatric_Diabetes/Pediatric_T2DM_RiskAssessment.md")
        return None
    
    elif is_pregnant:
        print("🤰 妊娠期女性")
        print("建议：请使用妊娠期糖尿病(GDM)专用评估体系") 
        print("文档路径：/docs/GDM/GDM_RiskAssessment.md")
        return None
    
    elif diabetes_diagnosed:
        print("🩺 已确诊糖尿病患者")
        print("建议：请使用糖尿病管理和并发症评估工具")
        return None
    
    elif age > 65:
        print("👴 老年人群(>65岁)")
        print("⚠️  本评估体系主要适用于18-60岁成年人")
        choice = input("是否继续使用成人评估体系？(是/否): ").strip()
        if choice != "是":
            print("建议：请咨询老年科医师获得专业评估")
            return None
        else:
            print("✅ 继续使用成人评估体系（结果仅供参考）")
            return {"age": age, "gender": gender, "note": "老年人群，结果仅供参考"}
    
    elif 18 <= age <= 65:
        print("✅ 成年非妊娠人群(18-65岁)")
        print("适用：成人糖尿病前期风险评估体系")
        return {"age": age, "gender": gender, "is_pregnant": is_pregnant}
    
    else:
        print("🚫 年龄超出范围")
        print("建议：请咨询专科医师")
        return None

def get_patient_input(basic_info):
    """交互式收集患者详细信息"""
    print("\n" + "="*60)
    print("成人糖尿病前期风险评估")
    print("="*60)
    
    # 使用传入的基本信息
    age = basic_info["age"]
    gender = basic_info["gender"]
    is_pregnant = basic_info.get("is_pregnant", False)
    
    print(f"患者信息：{age}岁 {gender}性")
    if basic_info.get("note"):
        print(f"特别说明：{basic_info['note']}")
    print()
    
    # 体格测量
    print("\n【体格测量】")
    while True:
        try:
            height = float(input("身高 (cm): "))
            if 100 <= height <= 250:
                break
            else:
                print("请输入合理的身高范围")
        except ValueError:
            print("请输入有效的数字")
    
    while True:
        try:
            weight = float(input("体重 (kg): "))
            if 30 <= weight <= 200:
                break
            else:
                print("请输入合理的体重范围")
        except ValueError:
            print("请输入有效的数字")
    
    while True:
        try:
            waist = float(input("腰围 (cm): "))
            if 50 <= waist <= 150:
                break
            else:
                print("请输入合理的腰围范围")
        except ValueError:
            print("请输入有效的数字")
    
    while True:
        try:
            sbp = int(input("收缩压 (mmHg): "))
            dbp = int(input("舒张压 (mmHg): "))
            if 70 <= sbp <= 250 and 40 <= dbp <= 150:
                break
            else:
                print("请输入合理的血压范围")
        except ValueError:
            print("请输入有效的数字")
    
    # 生化指标
    print("\n【生化指标】")
    while True:
        try:
            fpg = float(input("空腹血糖 (mmol/L): "))
            if 2.0 <= fpg <= 20.0:
                break
            else:
                print("请输入合理的血糖范围")
        except ValueError:
            print("请输入有效的数字")
    
    while True:
        try:
            hba1c = float(input("糖化血红蛋白 (%): "))
            if 3.0 <= hba1c <= 15.0:
                break
            else:
                print("请输入合理的HbA1c范围")
        except ValueError:
            print("请输入有效的数字")
    
    # 血脂（可选）
    print("\n【血脂指标】(可选，直接回车跳过)")
    tg = None
    hdl_c = None
    ldl_c = None
    
    tg_input = input("甘油三酯 (mmol/L): ").strip()
    if tg_input:
        try:
            tg = float(tg_input)
        except ValueError:
            print("血脂输入无效，将跳过血脂评估")
    
    hdl_input = input("HDL胆固醇 (mmol/L): ").strip()
    if hdl_input:
        try:
            hdl_c = float(hdl_input)
        except ValueError:
            pass
    
    ldl_input = input("LDL胆固醇 (mmol/L): ").strip()
    if ldl_input:
        try:
            ldl_c = float(ldl_input)
        except ValueError:
            pass
    
    # 家族史
    print("\n【家族史】")
    print("糖尿病家族史选项：")
    print("1. 无")
    print("2. 二级亲属(祖父母、叔伯姑舅)")
    print("3. 一级亲属(父母、兄弟姐妹)")
    
    while True:
        try:
            family_choice = int(input("请选择 (1-3): "))
            if family_choice in [1, 2, 3]:
                family_map = {1: "无", 2: "二级亲属", 3: "一级亲属"}
                family_history = family_map[family_choice]
                break
            else:
                print("请输入1-3的数字")
        except ValueError:
            print("请输入有效的数字")
    
    # 既往史
    print("\n【既往史】")
    history_gdm = False
    history_cvd = False
    history_pcos = False
    
    if gender == "女":
        gdm_input = input("是否有妊娠糖尿病史？(是/否): ").strip()
        history_gdm = gdm_input == "是"
        
        pcos_input = input("是否有多囊卵巢综合征？(是/否): ").strip()
        history_pcos = pcos_input == "是"
    
    cvd_input = input("是否有心血管疾病史(冠心病、心梗、脑卒中)？(是/否): ").strip()
    history_cvd = cvd_input == "是"
    
    # 生活方式
    print("\n【生活方式】")
    while True:
        try:
            exercise = int(input("每周运动时间 (分钟): "))
            if 0 <= exercise <= 2000:
                break
            else:
                print("请输入合理的运动时间")
        except ValueError:
            print("请输入有效的数字")
    
    print("吸烟状态：")
    print("1. 从不吸烟")
    print("2. 既往吸烟")
    print("3. 现在吸烟")
    
    while True:
        try:
            smoke_choice = int(input("请选择 (1-3): "))
            if smoke_choice in [1, 2, 3]:
                smoke_map = {1: "从不吸烟", 2: "既往吸烟", 3: "现在吸烟"}
                smoking = smoke_map[smoke_choice]
                break
            else:
                print("请输入1-3的数字")
        except ValueError:
            print("请输入有效的数字")
    
    print("饮酒状态：")
    print("1. 不饮酒")
    print("2. 适量饮酒")
    print("3. 过量饮酒")
    
    while True:
        try:
            alcohol_choice = int(input("请选择 (1-3): "))
            if alcohol_choice in [1, 2, 3]:
                alcohol_map = {1: "不饮酒", 2: "适量饮酒", 3: "过量饮酒"}
                alcohol = alcohol_map[alcohol_choice]
                break
            else:
                print("请输入1-3的数字")
        except ValueError:
            print("请输入有效的数字")
    
    while True:
        try:
            sleep = float(input("每日睡眠时间 (小时): "))
            if 3.0 <= sleep <= 15.0:
                break
            else:
                print("请输入合理的睡眠时间")
        except ValueError:
            print("请输入有效的数字")
    
    # 创建患者数据对象
    patient = PatientData(
        age=age,
        gender=gender,
        is_pregnant=is_pregnant,
        height=height,
        weight=weight,
        waist_circumference=waist,
        systolic_bp=sbp,
        diastolic_bp=dbp,
        fpg=fpg,
        hba1c=hba1c,
        tg=tg,
        hdl_c=hdl_c,
        ldl_c=ldl_c,
        family_history_t2dm=family_history,
        history_gdm=history_gdm,
        history_cvd=history_cvd,
        history_pcos=history_pcos,
        exercise_minutes_per_week=exercise,
        smoking_status=smoking,
        alcohol_status=alcohol,
        sleep_hours_per_day=sleep
    )
    
    return patient

def print_report(report):
    """格式化打印评估报告"""
    print("\n" + "="*60)
    print("糖尿病风险评估报告")
    print("="*60)
    
    print(f"评估日期: {report['评估日期']}")
    
    if not report["适用性"]:
        print(f"\n❌ {report['消息']}")
        print(f"建议: {report['建议']}")
        return
    
    if report.get("特殊说明"):
        print(f"\n⚠️  {report['特殊说明']}")
    
    # 患者基本信息
    print(f"\n【患者信息】")
    info = report["患者基本信息"]
    print(f"年龄: {info['年龄']}岁")
    print(f"性别: {info['性别']}")
    print(f"BMI: {info['BMI']} kg/m²")
    print(f"腰围: {info['腰围']} cm")
    print(f"血压: {info['血压']} mmHg")
    
    # 糖尿病状态
    status = report["糖尿病状态"]
    status_icon = {
        "正常": "✅",
        "糖尿病前期": "⚠️",
        "糖尿病": "❌"
    }
    print(f"\n【糖尿病状态】")
    print(f"{status_icon.get(status, '⚠️')} {status}")
    
    # 代谢综合征
    ms = report["代谢综合征"]
    ms_icon = "❌" if ms["诊断"] == "是" else "✅"
    print(f"\n【代谢综合征】")
    print(f"{ms_icon} {ms['诊断']}")
    if ms["满足组分"]:
        print("满足组分:")
        for component in ms["满足组分"]:
            print(f"  • {component}")
    
    # 风险评分和等级
    score_info = report["风险评分"]
    print(f"\n【风险评估】")
    print(f"总评分: {score_info['总分']}/100分")
    
    risk_icons = {
        "低风险": "🟢",
        "中风险": "🟡", 
        "高风险": "🟠",
        "极高风险": "🔴"
    }
    risk_level = score_info["风险等级"]
    print(f"风险等级: {risk_icons.get(risk_level, '⚠️')} {risk_level}")
    
    # 详细评分
    print(f"\n评分详情:")
    for item, score in score_info["详细评分"].items():
        print(f"  {item}: {score}分")
    
    # 发病风险
    prob = report["发病风险"]
    print(f"\n【发病概率】")
    print(f"1年内: {prob['1年发病率']}%")
    print(f"3年内: {prob['3年发病率']}%")
    print(f"5年内: {prob['5年发病率']}%")
    
    # 管理建议
    recommendations = report["管理建议"]
    print(f"\n【管理建议】")
    
    for category, items in recommendations.items():
        if items:
            print(f"\n{category}:")
            for item in items:
                print(f"  • {item}")
    
    print(f"\n【评估依据】")
    print(f"{report['评估依据']}")
    
    print("\n" + "="*60)

def save_report(report, filename=None):
    """保存报告到文件"""
    if filename is None:
        timestamp = report["评估日期"].replace(":", "").replace(" ", "_").replace("-", "")
        filename = f"diabetes_risk_report_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 报告已保存到: {filename}")

def main():
    """主程序"""
    try:
        # 第一步：人群筛选和分流
        basic_info = population_screening()
        
        if basic_info is None:
            # 不适用当前评估体系，程序结束
            return
        
        # 第二步：收集详细信息（仅适用人群）
        patient = get_patient_input(basic_info)
        
        if patient is None:
            return
        
        # 第三步：进行风险评估
        assessor = DiabetesRiskAssessment()
        report = assessor.generate_report(patient)
        
        # 第四步：显示评估报告
        print_report(report)
        
        # 第五步：询问是否保存
        save_choice = input("\n是否保存报告到文件？(是/否): ").strip()
        if save_choice == "是":
            save_report(report)
        
        # 第六步：询问是否继续评估
        continue_choice = input("\n是否继续评估其他患者？(是/否): ").strip()
        if continue_choice == "是":
            print("\n" + "="*60)
            main()
    
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("请检查输入数据是否正确")

if __name__ == "__main__":
    main()