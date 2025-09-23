import pandas as pd
import json
import sys
from datetime import datetime

# 版本信息: 分层评估版 v3.0 - 自适应目标范围评估
# 更新日期: 2025-08-29
# 主要改进: 实现三层目标范围的自适应评估逻辑，根据标准TIR自动选择严格或宽松评估

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 1: 分层评估核心算法
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def layered_tir_assessment(standard_tir, strict_tir, lenient_tir):
    """
    分层TIR评估算法
    - 标准TIR ≥ 70% → 严格评估路径
    - 标准TIR < 70% → 宽松评估路径
    """
    if standard_tir >= 70.0:
        # 严格评估路径 (3.9-7.8 mmol/L)
        if strict_tir >= 85:
            return {
                "assessment_type": "严格评估",
                "level": "代谢健康状态理想",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "继续维持现有管理方案",
                "follow_up": "年度监测",
                "follow_up_weeks": 52
            }
        elif strict_tir >= 70:
            return {
                "assessment_type": "严格评估",
                "level": "代谢健康状态良好",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "维持现有治疗方案",
                "follow_up": "半年监测",
                "follow_up_weeks": 26
            }
        elif strict_tir >= 60:
            return {
                "assessment_type": "严格评估",
                "level": "代谢健康状态尚可",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "建议优化生活方式干预",
                "follow_up": "季度监测",
                "follow_up_weeks": 13
            }
        elif strict_tir >= 40:
            return {
                "assessment_type": "严格评估",
                "level": "血糖控制亚优，需要调整",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "需要强化生活方式管理",
                "follow_up": "月度监测",
                "follow_up_weeks": 4
            }
        else:
            return {
                "assessment_type": "严格评估",
                "level": "血糖控制不理想，需医学干预",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "建议内分泌专科医师评估",
                "follow_up": "双周监测",
                "follow_up_weeks": 2
            }
    else:
        # 宽松评估路径 (3.9-13.9 mmol/L)
        if lenient_tir >= 60:
            return {
                "assessment_type": "宽松评估",
                "level": "血糖控制基本达标",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "建议调整治疗方案",
                "follow_up": "月度监测",
                "follow_up_weeks": 4
            }
        elif lenient_tir >= 50:
            return {
                "assessment_type": "宽松评估",
                "level": "血糖控制欠佳",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "需优化治疗方案及生活方式",
                "follow_up": "双周监测",
                "follow_up_weeks": 2
            }
        elif lenient_tir >= 35:
            return {
                "assessment_type": "宽松评估",
                "level": "血糖控制不良，需强化治疗",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "需调整药物治疗并强化生活方式干预",
                "follow_up": "周度监测",
                "follow_up_weeks": 1
            }
        elif lenient_tir >= 20:
            return {
                "assessment_type": "宽松评估",
                "level": "血糖控制较差，需积极干预",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "需强化治疗，必要时住院管理",
                "follow_up": "每日监测",
                "follow_up_weeks": 0.14  # 1天
            }
        else:
            return {
                "assessment_type": "宽松评估",
                "level": "血糖控制较差，需紧急处理",
                "level_emoji": "",
                "level_color": "",
                "recommendation": "需立即医疗干预，建议住院治疗",
                "follow_up": "持续监护",
                "follow_up_weeks": 0
            }

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 2: 增强数据处理函数
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def calculate_layered_metrics(df: pd.DataFrame) -> dict:
    """计算三层目标范围的CGM指标"""
    glucose_values = df['glucose'].dropna()
    if glucose_values.empty:
        return {}

    # 基础信息计算
    monitoring_days = (df['timestamp'].max() - df['timestamp'].min()).days + 1
    if len(df['timestamp']) > 1:
        median_interval_seconds = df['timestamp'].diff().dt.total_seconds().median()
    else:
        median_interval_seconds = 0
    if median_interval_seconds and median_interval_seconds > 0:
        points_per_day = (24 * 3600) / median_interval_seconds
    else:
        points_per_day = 288
    expected_readings = monitoring_days * points_per_day
    valid_data_percentage = (len(glucose_values) / expected_readings) * 100 if expected_readings > 0 else 0

    mean_glucose = glucose_values.mean()
    cv = (glucose_values.std() / mean_glucose) * 100 if mean_glucose > 0 else 0
    
    total_readings = len(glucose_values)
    
    # 三层目标范围TIR计算
    standard_tir = (glucose_values.between(3.9, 10.0).sum() / total_readings) * 100  # 标准
    strict_tir = (glucose_values.between(3.9, 7.8).sum() / total_readings) * 100     # 严格
    lenient_tir = (glucose_values.between(3.9, 13.9).sum() / total_readings) * 100   # 宽松
    
    # TBR计算
    tbr_percentage = (glucose_values < 3.9).sum() / total_readings * 100
    
    # TAR计算（三个层次）
    standard_tar = (glucose_values > 10.0).sum() / total_readings * 100   # >10.0
    strict_tar = (glucose_values > 7.8).sum() / total_readings * 100      # >7.8
    lenient_tar = (glucose_values > 13.9).sum() / total_readings * 100    # >13.9
    
    # 昼夜时间段分析
    df_with_hour = df.copy()
    df_with_hour['hour'] = df_with_hour['timestamp'].dt.hour

    # 夜间数据（0-6点）
    night_data = df_with_hour[(df_with_hour['hour'] >= 0) & (df_with_hour['hour'] < 6)]
    if len(night_data) > 0:
        night_glucose = night_data['glucose'].dropna()
        night_standard_tir = (night_glucose.between(3.9, 10.0).sum() / len(night_glucose)) * 100 if len(night_glucose) > 0 else 0
        night_strict_tir = (night_glucose.between(3.9, 7.8).sum() / len(night_glucose)) * 100 if len(night_glucose) > 0 else 0
        night_mean = night_glucose.mean() if len(night_glucose) > 0 else 0
        night_tbr = (night_glucose < 3.9).sum() / len(night_glucose) * 100 if len(night_glucose) > 0 else 0
        night_standard_tar = (night_glucose > 10.0).sum() / len(night_glucose) * 100 if len(night_glucose) > 0 else 0
        night_strict_tar = (night_glucose > 7.8).sum() / len(night_glucose) * 100 if len(night_glucose) > 0 else 0
    else:
        night_standard_tir = night_strict_tir = night_mean = night_tbr = night_standard_tar = night_strict_tar = 0

    # 白天数据（6-24点）
    day_data = df_with_hour[(df_with_hour['hour'] >= 6) & (df_with_hour['hour'] < 24)]
    if len(day_data) > 0:
        day_glucose = day_data['glucose'].dropna()
        day_standard_tir = (day_glucose.between(3.9, 10.0).sum() / len(day_glucose)) * 100 if len(day_glucose) > 0 else 0
        day_strict_tir = (day_glucose.between(3.9, 7.8).sum() / len(day_glucose)) * 100 if len(day_glucose) > 0 else 0
        day_mean = day_glucose.mean() if len(day_glucose) > 0 else 0
        day_tbr = (day_glucose < 3.9).sum() / len(day_glucose) * 100 if len(day_glucose) > 0 else 0
        day_standard_tar = (day_glucose > 10.0).sum() / len(day_glucose) * 100 if len(day_glucose) > 0 else 0
        day_strict_tar = (day_glucose > 7.8).sum() / len(day_glucose) * 100 if len(day_glucose) > 0 else 0
    else:
        day_standard_tir = day_strict_tir = day_mean = day_tbr = day_standard_tar = day_strict_tar = 0

    # 分层评估
    layered_result = layered_tir_assessment(standard_tir, strict_tir, lenient_tir)

    patient_data = {
        "cgm_wear_days": monitoring_days,
        "cgm_valid_data_percentage": valid_data_percentage,
        "mean_glucose": mean_glucose,
        "cv": cv,
        
        # 三层TIR
        "standard_tir": standard_tir,
        "strict_tir": strict_tir,
        "lenient_tir": lenient_tir,
        
        # TBR和TAR
        "tbr_percentage": tbr_percentage,
        "standard_tar": standard_tar,
        "strict_tar": strict_tar,
        "lenient_tar": lenient_tar,
        
        # 昼夜分析
        "night_standard_tir": night_standard_tir,
        "night_strict_tir": night_strict_tir,
        "night_mean": night_mean,
        "night_tbr": night_tbr,
        "night_standard_tar": night_standard_tar,
        "night_strict_tar": night_strict_tar,
        
        "day_standard_tir": day_standard_tir,
        "day_strict_tir": day_strict_tir,
        "day_mean": day_mean,
        "day_tbr": day_tbr,
        "day_standard_tar": day_standard_tar,
        "day_strict_tar": day_strict_tar,
        
        # 分层评估结果
        "layered_assessment": layered_result
    }
    return patient_data

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 3: 关键事件分析
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def find_critical_events(df: pd.DataFrame, top_n=2) -> dict:
    """分析葡萄糖数据以找到最重要的高血糖和低血糖事件"""
    # 高血糖分析
    hyper_df = df[df['glucose'] > 13.9].copy()
    hyper_events_list = []
    if not hyper_df.empty:
        hyper_df['event_block'] = (hyper_df['timestamp'].diff().dt.total_seconds() > 300).cumsum()
        hyper_events = hyper_df.groupby('event_block').agg(
            start_time=('timestamp', 'min'),
            end_time=('timestamp', 'max'),
            duration_mins=('timestamp', lambda x: (x.max() - x.min()).total_seconds() / 60),
            max_glucose=('glucose', 'max')
        ).sort_values(by=['duration_mins', 'max_glucose'], ascending=[False, False]).head(top_n)
        
        for _, event in hyper_events.iterrows():
            hyper_events_list.append({
                'start_time': event['start_time'],
                'end_time': event['end_time'], 
                'duration_mins': event['duration_mins'],
                'max_glucose': event['max_glucose']
            })

    # 低血糖分析
    hypo_df = df[df['glucose'] < 3.9].copy()
    hypo_events_list = []
    if not hypo_df.empty:
        hypo_df['event_block'] = (hypo_df['timestamp'].diff().dt.total_seconds() > 300).cumsum()
        hypo_events = hypo_df.groupby('event_block').agg(
            start_time=('timestamp', 'min'),
            end_time=('timestamp', 'max'),
            duration_mins=('timestamp', lambda x: (x.max() - x.min()).total_seconds() / 60),
            min_glucose=('glucose', 'min')
        ).sort_values(by=['duration_mins', 'min_glucose'], ascending=[False, True]).head(top_n)

        for _, event in hypo_events.iterrows():
            hypo_events_list.append({
                'start_time': event['start_time'],
                'end_time': event['end_time'],
                'duration_mins': event['duration_mins'],
                'min_glucose': event['min_glucose']
            })

    return {
        'hyper_events': hyper_events_list,
        'hypo_events': hypo_events_list
    }

def format_hypoglycemic_events(hypo_events, top_display=5):
    """格式化低血糖事件信息"""
    if not hypo_events:
        return "无低血糖事件记录"
    
    event_descriptions = []
    for i, event in enumerate(hypo_events[:top_display], 1):
        start_str = event['start_time'].strftime('%Y-%m-%d %H:%M')
        end_str = event['end_time'].strftime('%H:%M')
        duration = event['duration_mins']
        min_glucose = event['min_glucose']
        
        if duration > 0:
            event_descriptions.append(
                f"事件{i}: {start_str}-{end_str} (持续{duration:.0f}分钟, 最低{min_glucose:.1f} mmol/L)"
            )
        else:
            event_descriptions.append(
                f"事件{i}: {start_str} (最低{min_glucose:.1f} mmol/L)"
            )
    
    return event_descriptions

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 4: 分层评估报告生成
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def generate_layered_report(patient_data, agp_rules, raw_df):
    """生成分层评估报告"""
    report = []
    layered_result = patient_data["layered_assessment"]
    
    # 分析关键事件
    critical_events = find_critical_events(raw_df)
    
    report.append(f"## AGP 报告分层评估解读: v3.0")
    report.append(f"---")
    report.append(f"患者ID: {patient_data.get('patient_id', '未知')}")
    report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"血糖管理等级: {layered_result['level']}")
    report.append(f"评估类型: {layered_result['assessment_type']}")
    report.append(f"主要建议: {layered_result['recommendation']}")
    report.append(f"随访频率: {layered_result['follow_up']}")
    report.append("---")

    # 数据质量评估
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
    
    report.append(f"\n### 二. 分层血糖达标评估")
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
    report.append(f"\n### 三. 低血糖风险评估")
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
    report.append(f"\n### 四. 血糖稳定性评估")
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
        report.append(f"\n### 五. 高血糖负担评估 (严格标准)")
        report.append(f"1. **TAR (>7.8 mmol/L): {strict_tar:.1f}%** (代谢健康目标: <20%)")
        if strict_tar < 5:
            report.append(f"2. **高血糖负担**: 较低，代谢状态良好")
        elif strict_tar < 20:
            report.append(f"2. **高血糖负担**: 在临床可接受范围内")
        else:
            report.append(f"2. **高血糖负担**: 偏高，建议调整生活方式")
    else:
        lenient_tar = patient_data.get("lenient_tar", 0)
        report.append(f"\n### 五. 高血糖负担评估 (宽松标准)")
        report.append(f"1. **TAR (>13.9 mmol/L): {lenient_tar:.1f}%** (基础安全目标: <25%)")
        if lenient_tar < 5:
            report.append(f"2. **高血糖负担**: 严重高血糖事件较少")
        elif lenient_tar < 25:
            report.append(f"2. **高血糖负担**: 在临床可接受范围内")
        else:
            report.append(f"2. **高血糖负担**: 较重，需要强化治疗")

    # 综合建议
    report.append(f"\n### 综合评估与建议")
    report.append(f"1. **最终评级**: {layered_result['level']}")
    report.append(f"2. **主要建议**: {layered_result['recommendation']}")
    report.append(f"3. **随访计划**: {layered_result['follow_up']}")
    report.append(f"4. **下次CGM**: 建议{layered_result['follow_up_weeks']:.0f}周后" if layered_result['follow_up_weeks'] > 0 else "4. **监护要求**: 持续密切监护")

    # 暂时跳过关键事件分析
    # critical_events = find_critical_events(raw_df)
    # if "无明显" not in critical_events:
    #     report.append(f"- **重点关注**: {critical_events}")

    report.append("\n" + "="*60)
    report.append("**分层评估报告生成完毕**")
    report.append("**免责声明**: 本报告仅供临床参考，具体治疗方案请遵医嘱")
    report.append("="*60)
    
    return report

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 5: 数据加载和处理
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def load_data(filepath: str) -> pd.DataFrame:
    """加载Excel或CSV数据"""
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        raise ValueError(f"不支持的文件格式: {filepath}")
    
    column_mapping = {'时间': 'timestamp','time': 'timestamp','Time': 'timestamp','值': 'glucose','glucose': 'glucose','血糖值': 'glucose'}
    df = df.rename(columns=lambda c: column_mapping.get(c, c))
    
    if 'timestamp' not in df.columns or 'glucose' not in df.columns:
        raise ValueError("文件中未找到'时间'或'值'列")
        
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['glucose'] = pd.to_numeric(df['glucose'], errors='coerce')
    df = df.dropna(subset=['glucose'])
    
    # 单位转换检测
    if df['glucose'].mean() > 20:  # 假设平均值>20为mg/dL
        df['glucose'] = df['glucose'] / 18.0182
        
    return df

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 6: 主程序入口
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main():
    if len(sys.argv) < 2:
        print("错误: 请提供Excel或CSV文件路径作为参数。")
        sys.exit(1)

    filepath = sys.argv[1]
    patient_id = filepath.split('/')[-1].split('-')[0]

    try:
        # 加载配置文件
        config_path = '/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/5Steps.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            agp_rules = json.load(f)

        print(f"正在读取数据: {filepath}")
        raw_df = load_data(filepath)
        
        print("正在计算分层血糖指标...")
        patient_metrics = calculate_layered_metrics(raw_df)
        patient_metrics['patient_id'] = patient_id

        print("正在生成分层评估报告...")
        report_lines = generate_layered_report(patient_metrics, agp_rules, raw_df)
        
        print("\n" + "="*80)
        for line in report_lines:
            print(line)
        print("="*80)

    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
    except ValueError as e:
        print(f"数据处理错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    main()