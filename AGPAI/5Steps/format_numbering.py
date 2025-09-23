#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式编号调整：步骤编号简化，添加子项序号
"""
import re

def format_numbering_adjustment():
    file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/run_report_layered_assessment.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 简化步骤标题
    content = re.sub(r'### 步骤一:', '### 一.', content)
    content = re.sub(r'### 步骤二:', '### 二.', content)
    content = re.sub(r'### 步骤三:', '### 三.', content)
    content = re.sub(r'### 步骤四:', '### 四.', content)
    content = re.sub(r'### 步骤五:', '### 五.', content)
    
    # 2. 为步骤一添加序号
    # 数据质量评估
    content = re.sub(
        r'(### 一\. 数据质量评估\n)(- 佩戴天数:.*?\n)(- 有效数据:.*?\n)',
        r'\g<1>1. 佩戴天数: **{wear_days:.1f} 天** (标准: ≥14天)\n2. 有效数据: **{valid_data_pct:.1f}%** (标准: ≥70%)\n',
        content
    )
    
    # 需要更精确地处理报告生成逻辑，让我直接修改generate_layered_report函数
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("步骤1: 基础格式调整完成")

def detailed_format_adjustment():
    """详细格式调整，重写报告生成函数"""
    file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/run_report_layered_assessment.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到generate_layered_report函数并替换其中的报告生成部分
    new_report_section = '''    # 数据质量评估
    wear_days = patient_data.get("cgm_wear_days", 0)
    valid_data_pct = patient_data.get("cgm_valid_data_percentage", 0)
    
    report.append(f"### 一. 数据质量评估")
    report.append(f"1. 佩戴天数: **{wear_days:.1f} 天** (标准: ≥14天)")
    report.append(f"2. 有效数据: **{valid_data_pct:.1f}%** (标准: ≥70%)")
    
    if wear_days >= 14 and valid_data_pct >= 70:
        report.append(f"3. 评估结论: **数据充分可信**")
    else:
        report.append(f"3. 评估结论: **数据不充分**")
        report.append(f"4. 建议: 延长CGM佩戴时间或检查传感器贴合度")

    # 分层TIR评估详情
    standard_tir = patient_data.get("standard_tir", 0)
    strict_tir = patient_data.get("strict_tir", 0)
    lenient_tir = patient_data.get("lenient_tir", 0)
    mean_glucose = patient_data.get("mean_glucose", 0)
    
    report.append(f"\\n### 二. 分层血糖达标评估")
    report.append(f"#### 三层目标范围TIR对比")
    report.append(f"1. **标准TIR (3.9-10.0 mmol/L): {standard_tir:.1f}%** (糖尿病目标: >70%)")
    report.append(f"2. **严格TIR (3.9-7.8 mmol/L): {strict_tir:.1f}%** (代谢健康目标: >80%)")
    report.append(f"3. **宽松TIR (3.9-13.9 mmol/L): {lenient_tir:.1f}%** (基础安全目标: >50%)")
    report.append(f"4. **平均葡萄糖: {mean_glucose:.2f} mmol/L**")
    
    # 分层评估结果
    report.append(f"#### 分层评估结果")
    if layered_result["assessment_type"] == "严格评估":
        report.append(f"1. **评估路径**: 标准TIR ≥ 70%，启动严格评估")
        report.append(f"2. **严格评估等级**: {layered_result['level']}")
        report.append(f"3. **临床意义**: 血糖控制良好，按代谢健康人群标准评估")
    else:
        report.append(f"1. **评估路径**: 标准TIR < 70%，采用宽松评估")
        report.append(f"2. **宽松评估等级**: {layered_result['level']}")
        report.append(f"3. **临床意义**: 血糖控制欠佳，应重点关注低血糖风险")

    # 昼夜分析 - 安全性优先逻辑
    report.append(f"#### 昼夜分层对比分析")
    night_standard_tir = patient_data.get("night_standard_tir", 0)
    day_standard_tir = patient_data.get("day_standard_tir", 0)
    night_strict_tir = patient_data.get("night_strict_tir", 0)
    day_strict_tir = patient_data.get("day_strict_tir", 0)
    night_tbr = patient_data.get("night_tbr", 0)
    day_tbr = patient_data.get("day_tbr", 0)
    
    # 获取低血糖事件信息进行安全性评估
    hypo_events = critical_events.get('hypo_events', [])
    night_hypo = [e for e in hypo_events if 0 <= e['start_time'].hour < 6]
    day_hypo = [e for e in hypo_events if 6 <= e['start_time'].hour < 24]
    
    if layered_result["assessment_type"] == "严格评估":
        report.append(f"1. **夜间严格TIR**: {night_strict_tir:.1f}% |  **白天严格TIR**: {day_strict_tir:.1f}%")
        
        # 优先级1: 安全性评估
        night_safe = night_tbr < 4 and len(night_hypo) == 0
        day_safe = day_tbr < 4 and len(day_hypo) == 0
        
        if not night_safe and not day_safe:
            report.append(f"2. **风险提示**: 昼夜均存在低血糖风险，安全性是首要关注点")
        elif not night_safe:
            report.append(f"2. **风险提示**: 夜间存在低血糖风险 (TBR {night_tbr:.1f}%, {len(night_hypo)}次事件)")
            report.append(f"3. **管理要点**: 夜间安全性问题优先于达标率，需要调整夜间用药方案")
        elif not day_safe:
            report.append(f"2. **风险提示**: 白天存在低血糖风险 (TBR {day_tbr:.1f}%, {len(day_hypo)}次事件)")
            report.append(f"3. **管理要点**: 白天安全性问题需要关注，调整日间用药和活动")
        else:
            # 优先级2: 在安全前提下的有效性评估
            if abs(night_strict_tir - day_strict_tir) > 10:
                if night_strict_tir > day_strict_tir:
                    report.append(f"2. **安全性与有效性**: 夜间控制安全且有效，白天需要改善餐后血糖管理")
                else:
                    report.append(f"2. **安全性与有效性**: 白天控制相对较好，夜间血糖管理需要优化")
            else:
                report.append(f"2. **昼夜血糖控制**: 昼夜血糖控制相对稳定且安全")
    else:
        report.append(f"1. **夜间标准TIR**: {night_standard_tir:.1f}% |  **白天标准TIR**: {day_standard_tir:.1f}%")
        
        # 宽松评估也要考虑安全性
        night_safe = night_tbr < 4 and len(night_hypo) == 0
        day_safe = day_tbr < 4 and len(day_hypo) == 0
        
        if not night_safe or not day_safe:
            report.append(f"2. **安全性优先**: {'夜间' if not night_safe else '白天'}存在低血糖风险，安全性管理是当前重点")
        elif abs(night_standard_tir - day_standard_tir) > 15:
            if night_standard_tir > day_standard_tir:
                report.append(f"2. **管理重点**: 白天血糖控制不佳，需要强化日间治疗")
            else:
                report.append(f"2. **管理重点**: 夜间血糖控制不佳，需要调整基础治疗方案")

    # 低血糖和高血糖风险评估
    tbr = patient_data.get("tbr_percentage", 0)
    report.append(f"\\n### 三. 低血糖风险评估")
    report.append(f"1. **TBR (<3.9 mmol/L): {tbr:.1f}%** (安全目标: <4%)")
    
    if tbr == 0:
        report.append(f"2. **低血糖风险**: 无，低血糖风险极低")
    elif tbr < 1:
        report.append(f"2. **低血糖风险**: 较低，低血糖风险较低")
    elif tbr < 4:
        report.append(f"2. **低血糖风险**: 轻度，需要监测")
    else:
        report.append(f"2. **低血糖风险**: 较高，需要调整治疗")
    
    # 添加低血糖事件详情
    hypo_events = critical_events.get('hypo_events', [])
    if hypo_events:
        report.append(f"#### 低血糖事件详细记录")
        event_details = format_hypoglycemic_events(hypo_events, top_display=10)
        for i, detail in enumerate(event_details, 3):
            report.append(f"{i}. {detail}")
        
        # 分析低血糖发生模式
        night_hypo = [e for e in hypo_events if 0 <= e['start_time'].hour < 6]
        day_hypo = [e for e in hypo_events if 6 <= e['start_time'].hour < 24]
        
        next_num = len(event_details) + 3
        if night_hypo and day_hypo:
            report.append(f"{next_num}. **发生模式**: 昼夜均有低血糖发生 (夜间{len(night_hypo)}次, 白天{len(day_hypo)}次)")
        elif night_hypo:
            report.append(f"{next_num}. **发生模式**: 主要发生在夜间 ({len(night_hypo)}次)，需要关注睡前血糖和夜间用药")
        elif day_hypo:
            report.append(f"{next_num}. **发生模式**: 主要发生在白天 ({len(day_hypo)}次)，需要关注餐前用药和活动强度")
        
        report.append(f"#### 低血糖管理建议")
        mgmt_start = next_num + 1
        if tbr > 4:
            report.append(f"{mgmt_start}. **治疗调整**: 降糖药物剂量偏大，建议与医生讨论减量")
            report.append(f"{mgmt_start+1}. **监测强化**: 增加血糖自测频率，特别是餐前和睡前")
            mgmt_start += 2
        report.append(f"{mgmt_start}. **低血糖应急处理**: 随身携带快速升糖食物（葡萄糖片、糖果等）")
        report.append(f"{mgmt_start+1}. **患者及家属教育**: 家属需掌握低血糖识别和处理方法")
        if len(hypo_events) >= 3:
            report.append(f"{mgmt_start+2}. **专科医师评估**: 低血糖事件频发，建议内分泌科专科医师评估")
    else:
        if tbr > 0:
            report.append(f"3. **注意**: 虽有轻微低血糖，但未检测到明显的低血糖事件集中")

    # 血糖变异性
    cv = patient_data.get("cv", 0)
    report.append(f"\\n### 四. 血糖稳定性评估")
    report.append(f"1. **血糖变异系数 (CV): {cv:.1f}%** (理想目标: ≤36%)")
    
    if cv <= 25:
        report.append(f"2. **稳定性**: 良好，血糖波动较小")
    elif cv <= 36:
        report.append(f"2. **稳定性**: 尚可，血糖波动在临床可接受范围内")
    else:
        report.append(f"2. **稳定性**: 欠佳，血糖波动较大")

    # 高血糖负担评估
    if layered_result["assessment_type"] == "严格评估":
        strict_tar = patient_data.get("strict_tar", 0)
        report.append(f"\\n### 五. 高血糖负担评估 (严格标准)")
        report.append(f"1. **TAR (>7.8 mmol/L): {strict_tar:.1f}%** (代谢健康目标: <20%)")
        if strict_tar < 5:
            report.append(f"2. **高血糖负担**: 较低，代谢状态良好")
        elif strict_tar < 20:
            report.append(f"2. **高血糖负担**: 在临床可接受范围内")
        else:
            report.append(f"2. **高血糖负担**: 偏高，建议调整生活方式")
    else:
        lenient_tar = patient_data.get("lenient_tar", 0)
        report.append(f"\\n### 五. 高血糖负担评估 (宽松标准)")
        report.append(f"1. **TAR (>13.9 mmol/L): {lenient_tar:.1f}%** (基础安全目标: <25%)")
        if lenient_tar < 5:
            report.append(f"2. **高血糖负担**: 严重高血糖事件较少")
        elif lenient_tar < 25:
            report.append(f"2. **高血糖负担**: 在临床可接受范围内")
        else:
            report.append(f"2. **高血糖负担**: 较重，需要强化治疗")

    # 综合建议
    report.append(f"\\n### 综合评估与建议")
    report.append(f"1. **最终评级**: {layered_result['level']}")
    report.append(f"2. **主要建议**: {layered_result['recommendation']}")
    report.append(f"3. **随访计划**: {layered_result['follow_up']}")
    report.append(f"4. **下次CGM**: 建议{layered_result['follow_up_weeks']:.0f}周后" if layered_result['follow_up_weeks'] > 0 else "4. **监护要求**: 持续密切监护")'''
    
    # 找到并替换generate_layered_report函数中的报告生成部分
    pattern = r'(    # 数据质量评估.*?)(    # 暂时跳过关键事件分析)'
    content = re.sub(pattern, new_report_section + '\n\n    # 暂时跳过关键事件分析', content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 详细格式调整完成：步骤编号简化，子项序号已添加")

if __name__ == "__main__":
    format_numbering_adjustment()
    detailed_format_adjustment()