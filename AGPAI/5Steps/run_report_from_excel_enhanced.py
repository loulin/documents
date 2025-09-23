import pandas as pd
import json
import sys
from datetime import datetime

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 1: Enhanced Critical Event Analysis
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def find_critical_events(df: pd.DataFrame, top_n=2) -> str:
    """
    分析葡萄糖数据以找到最重要的高血糖和低血糖事件
    返回具体日期和时间的字符串供审查
    """
    # --- 高血糖分析 ---
    hyper_df = df[df['glucose'] > 13.9].copy()
    if not hyper_df.empty:
        hyper_df['event_block'] = (hyper_df['timestamp'].diff().dt.total_seconds() > 300).cumsum()
        hyper_events = hyper_df.groupby('event_block').agg(
            start_time=('timestamp', 'min'),
            duration_mins=('timestamp', lambda x: (x.max() - x.min()).total_seconds() / 60),
            max_glucose=('glucose', 'max')
        ).sort_values(by=['duration_mins', 'max_glucose'], ascending=[False, False]).head(top_n)
        
        hyper_suggestions = []
        for _, event in hyper_events.iterrows():
            hyper_suggestions.append(f"{event['start_time'].strftime('%m-%d %H:%M')} (持续高血糖, 峰值 {event['max_glucose']:.1f})")
        hyper_string = '; '.join(hyper_suggestions)
    else:
        hyper_string = "无明显持续高血糖事件"

    # --- 低血糖分析 ---
    hypo_df = df[df['glucose'] < 3.9].copy()
    if not hypo_df.empty:
        hypo_df['event_block'] = (hypo_df['timestamp'].diff().dt.total_seconds() > 300).cumsum()
        hypo_events = hypo_df.groupby('event_block').agg(
            start_time=('timestamp', 'min'),
            duration_mins=('timestamp', lambda x: (x.max() - x.min()).total_seconds() / 60),
            min_glucose=('glucose', 'min')
        ).sort_values(by=['duration_mins', 'min_glucose'], ascending=[False, True]).head(top_n)

        hypo_suggestions = []
        for _, event in hypo_events.iterrows():
            hypo_suggestions.append(f"{event['start_time'].strftime('%m-%d %H:%M')} (低血糖, 谷值 {event['min_glucose']:.1f})")
        hypo_string = '; '.join(hypo_suggestions)
    else:
        hypo_string = "无明显低血糖事件"

    return f"请重点关注以下时间点的每日曲线: 高血糖时段-[{hyper_string}]; 低血糖时段-[{hypo_string}]"


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 2: Enhanced Clinical Summary Generation
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def generate_detailed_clinical_summary(patient_data):
    """生成详细的临床总结（修正：以TIR为主导的判定标准）"""
    tir = patient_data.get("tir_percentage", 0)
    tbr = patient_data.get("tbr_percentage", 0)
    tar = patient_data.get("tar_percentage", 0)
    mean_glucose = patient_data.get("mean_glucose", 0)
    cv = patient_data.get("cv", 0)
    
    # 血糖控制等级判定（修正：以TIR为主要标准，TAR和TBR为安全标准）
    if tir >= 70 and tbr < 4 and tar < 25:
        control_level = "优秀"
        control_color = "🟢"
    elif tir >= 50 and tbr < 10 and tar < 50:
        control_level = "良好"
        control_color = "🟡"
    elif tir >= 25 and tbr < 15:  # 修正阈值
        control_level = "一般"
        control_color = "🟠"
    else:
        control_level = "较差"
        control_color = "🔴"
    
    # 风险等级评估（修正：调整风险因素优先级）
    risk_factors = []
    if tbr > 10:
        risk_factors.append("严重低血糖风险")
    elif tbr > 4:
        risk_factors.append("低血糖风险")
    if tar > 75:
        risk_factors.append("极严重高血糖风险")
    elif tar > 50:
        risk_factors.append("严重高血糖风险")
    elif tar > 25:
        risk_factors.append("高血糖风险")
    if cv > 50:
        risk_factors.append("血糖极不稳定")
    elif cv > 36:
        risk_factors.append("血糖波动较大")
    if mean_glucose > 15:
        risk_factors.append("平均血糖过高")
    elif mean_glucose > 10:
        risk_factors.append("平均血糖偏高")
    
    return {
        "control_level": control_level,
        "control_color": control_color,
        "risk_factors": risk_factors
    }

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 3: Enhanced Report Generation (Major Enhancement)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def generate_5_step_report(patient_data, agp_rules):
    report = []
    steps = agp_rules['步骤列表']
    critical_events_string = patient_data.get("critical_events_string", "未进行关键事件分析。")
    clinical_summary = generate_detailed_clinical_summary(patient_data)

    report.append(f"## {agp_rules['流程名称']}: 增强版解读报告")
    report.append(f"---")
    report.append(f"📋 患者ID: {patient_data.get('patient_id', '未知')}")
    report.append(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"{clinical_summary['control_color']} 血糖控制等级: {clinical_summary['control_level']}")
    if clinical_summary['risk_factors']:
        report.append(f"⚠️  主要风险因素: {', '.join(clinical_summary['risk_factors'])}")
    report.append("---")

    # --- Step 1: 增强版信息采集及资料准备 ---
    step1 = steps[0]
    report.append(f"### 📊 步骤 1: {step1['步骤名称']}")
    wear_days = patient_data.get("cgm_wear_days", 0)
    valid_data_pct = patient_data.get("cgm_valid_data_percentage", 0)
    
    report.append(f"#### 数据质量评估")
    report.append(f"- 🕐 佩戴天数: **{wear_days:.1f} 天** (标准: ≥14天)")
    report.append(f"- 📈 有效数据: **{valid_data_pct:.1f}%** (标准: ≥70%)")
    
    if wear_days >= 14 and valid_data_pct >= 70:
        report.append(f"- ✅ 评估结论: **数据充分可信**")
        report.append(f"- 💡 数据解读: CGM数据满足临床分析要求，可进行全面血糖管理评估")
    else:
        report.append(f"- ❌ 评估结论: **数据不充分**")
        report.append(f"- 🔧 改进建议: {step1['子步骤'][0]['否路径']}")
        if wear_days < 14:
            report.append(f"  - 建议延长CGM佩戴至至少14天以获得更准确的血糖模式")
        if valid_data_pct < 70:
            report.append(f"  - 检查传感器贴合度，避免频繁脱落影响数据完整性")
        report.append(f"- ⚠️  注意: 基于当前数据的分析结果仅供参考，不建议作为治疗调整的主要依据")
        return report

    # --- Step 2: 增强版血糖整体达标情况 ---
    step2 = steps[1]
    report.append(f"\n### 🎯 步骤 2: {step2['步骤名称']}")
    tir = patient_data.get("tir_percentage", 0)
    mean_glucose = patient_data.get("mean_glucose", 0)
    tar = patient_data.get("tar_percentage", 0)
    
    report.append(f"#### 核心血糖指标")
    tir_status = "✅ 达标" if tir > 70 else "❌ 不达标"
    mg_status = "✅ 达标" if mean_glucose < 8.6 else "❌ 不达标"
    
    report.append(f"- 🎯 **TIR (目标范围内时间 3.9-10.0 mmol/L): {tir:.1f}%** (目标: >70%) - {tir_status}")
    report.append(f"- 📊 **MG (平均葡萄糖): {mean_glucose:.2f} mmol/L** (目标: <8.6 mmol/L) - {mg_status}")
    
    # TIR详细分析
    if tir > 70:
        report.append(f"- 💚 **血糖控制评价**: 优秀！患者大部分时间血糖保持在理想范围")
    elif tir > 50:
        report.append(f"- 🟡 **血糖控制评价**: 尚可，但仍有改善空间")
    elif tir > 25:
        report.append(f"- 🟠 **血糖控制评价**: 控制不佳，需要调整治疗方案")
    else:
        report.append(f"- 🔴 **血糖控制评价**: 控制很差，需要立即干预")
    
    if tir <= 70:
        report.append(f"#### 📋 详细分析与建议")
        report.append(f"- 🔍 **主要问题**: TIR仅为{tir:.1f}%，远低于70%的理想目标")
        report.append(f"- 📈 **原因分析**: 高血糖时间过长({tar:.1f}%)是TIR不达标的主要原因")
        report.append(f"- 💊 **治疗建议**:")
        if tar > 50:
            report.append(f"  - 考虑加强降糖治疗：增加药物剂量或联合用药")
            report.append(f"  - 重视餐后血糖管理：调整用餐时间和碳水化合物摄入")
        if mean_glucose > 12:
            report.append(f"  - 平均血糖过高({mean_glucose:.1f} mmol/L)，建议胰岛素治疗")
        report.append(f"  - 定期监测空腹血糖和餐后2小时血糖")
        report.append(f"  - 结合生活方式干预：合理饮食、规律运动")

    # --- Step 3: 增强版低血糖风险评估 ---
    step3 = steps[2]
    report.append(f"\n### ⚠️  步骤 3: {step3['步骤名称']}")
    tbr = patient_data.get("tbr_percentage", 0)
    
    report.append(f"#### 低血糖风险分析")
    tbr_status = "✅ 安全" if tbr < 4 else "❌ 风险高"
    report.append(f"- 📉 **TBR (低血糖时间 <3.9 mmol/L): {tbr:.1f}%** (安全标准: <4%) - {tbr_status}")
    
    # 低血糖风险分级
    if tbr == 0:
        report.append(f"- 💚 **低血糖风险**: 无，患者未出现临床意义上的低血糖")
        report.append(f"- 🛡️  **安全评价**: 当前治疗方案的低血糖风险很低，相对安全")
    elif tbr < 1:
        report.append(f"- 🟢 **低血糖风险**: 轻微，偶发性低血糖，需要关注")
    elif tbr < 4:
        report.append(f"- 🟡 **低血糖风险**: 中等，接近安全上限，需要监测")
    else:
        report.append(f"- 🔴 **低血糖风险**: 高风险，超出安全范围，需要立即处理")
    
    if tbr > 0:
        report.append(f"#### 🚨 低血糖事件分析")
        report.append(f"- 📍 **关键时间点**: {critical_events_string}")
        report.append(f"- 💊 **处理建议**:")
        if tbr > 4:
            report.append(f"  - 立即调整降糖药物剂量，避免过度治疗")
            report.append(f"  - 检查用药时间与进餐时间的匹配性")
        if tbr > 1:
            report.append(f"  - 患者及家属需掌握低血糖急救知识")
            report.append(f"  - 随身携带快速升糖食物（葡萄糖片、糖果等）")
        report.append(f"  - 加强血糖自监测，特别是餐前和夜间")
        report.append(f"  - 定期评估肾功能、肝功能对药物代谢的影响")
    else:
        if tar > 50:  # 高血糖严重时，强调可以积极治疗
            report.append(f"- ✨ **治疗优势**: 无低血糖风险，可以积极强化降糖治疗")
        else:
            report.append(f"- ✨ **优势**: 无低血糖负担，为进一步优化血糖控制提供了安全空间")

    # --- Step 4: 增强版血糖波动性评估 ---
    step4 = steps[3]
    report.append(f"\n### 📊 步骤 4: {step4['步骤名称']}")
    cv = patient_data.get("cv", 0)
    
    report.append(f"#### 血糖稳定性分析")
    cv_status = "✅ 稳定" if cv <= 36 else "❌ 波动过大"
    report.append(f"- 📈 **血糖变异系数 (CV): {cv:.1f}%** (理想目标: ≤36%) - {cv_status}")
    
    # CV详细分级评估（修正：考虑整体血糖控制状况）
    if cv <= 25:
        report.append(f"- 💚 **血糖稳定性**: 优秀，血糖波动很小")
        if tar < 25:  # 只有TAR也达标时才说并发症风险低
            report.append(f"- 🎯 **临床意义**: 血糖管理非常理想，并发症风险低")
        else:
            report.append(f"- ⚠️  **临床意义**: 虽然血糖波动小，但持续高血糖仍带来并发症风险")
    elif cv <= 36:
        report.append(f"- 🟢 **血糖稳定性**: 良好，血糖相对稳定")
        if tar < 50:
            report.append(f"- ✨ **临床意义**: 血糖波动控制良好，为优化整体血糖提供基础")
        else:
            report.append(f"- ⚠️  **临床意义**: 血糖波动虽稳定，但高血糖问题需重点关注")
    elif cv <= 50:
        report.append(f"- 🟡 **血糖稳定性**: 一般，存在明显波动")
        report.append(f"- ⚠️  **临床意义**: 血糖不稳定增加治疗难度和并发症风险")
    else:
        report.append(f"- 🔴 **血糖稳定性**: 很差，血糖波动剧烈")
        report.append(f"- 🚨 **临床意义**: 血糖极不稳定，严重影响治疗效果和并发症风险")
    
    if cv > 36:
        report.append(f"#### 🔍 波动原因分析")
        report.append(f"- **可能原因**:")
        report.append(f"  - 🍽️  进餐时间不规律或食物种类变化大")
        report.append(f"  - 💊 药物剂量与饮食摄入不匹配")
        report.append(f"  - 🏃 运动时间、强度变化较大")
        report.append(f"  - 😴 睡眠质量差或作息不规律")
        report.append(f"  - 😰 情绪波动或应激状态")
        
        report.append(f"#### 💡 稳定血糖的具体建议")
        report.append(f"- **生活方式调整**:")
        report.append(f"  - 固定三餐时间，每餐间隔4-6小时")
        report.append(f"  - 碳水化合物定量，避免暴饮暴食")
        report.append(f"  - 规律运动，建议餐后30-60分钟进行中等强度运动")
        report.append(f"  - 保持充足睡眠，建立良好作息习惯")
        report.append(f"- **治疗方案优化**:")
        report.append(f"  - 与医生讨论药物剂型调整（如长效制剂）")
        report.append(f"  - 考虑胰岛素泵或动态血糖监测系统")
        report.append(f"  - 加强血糖自监测，特别关注餐前餐后血糖配对")

    # --- Step 5: 增强版高血糖风险评估 ---
    step5 = steps[4]
    report.append(f"\n### 🔥 步骤 5: {step5['步骤名称']}")
    
    report.append(f"#### 高血糖负担评估")
    tar_status = "✅ 达标" if tar < 25 else "❌ 超标"
    report.append(f"- 📈 **TAR (高血糖时间 >10.0 mmol/L): {tar:.1f}%** (理想目标: <25%) - {tar_status}")
    
    # TAR详细分级
    if tar < 10:
        report.append(f"- 💚 **高血糖风险**: 很低，血糖控制优秀")
        report.append(f"- 🎯 **并发症风险**: 微血管和大血管并发症风险显著降低")
    elif tar < 25:
        report.append(f"- 🟢 **高血糖风险**: 低，血糖控制较好")
        report.append(f"- 📊 **并发症风险**: 在可接受范围内")
    elif tar < 50:
        report.append(f"- 🟡 **高血糖风险**: 中等，需要改善")
        report.append(f"- ⚠️  **并发症风险**: 长期高血糖可能导致慢性并发症")
    elif tar < 75:
        report.append(f"- 🟠 **高血糖风险**: 高，血糖控制不佳")
        report.append(f"- 🚨 **并发症风险**: 明显增加糖尿病并发症风险")
    else:
        report.append(f"- 🔴 **高血糖风险**: 极高，血糖控制很差")
        report.append(f"- 🆘 **并发症风险**: 急性和慢性并发症风险都很高")
    
    if tar >= 25:
        report.append(f"#### 🔍 高血糖事件详细分析")
        report.append(f"- 📍 **关键时间点**: {critical_events_string}")
        report.append(f"- 📊 **严重程度**: 高血糖时间占比{tar:.1f}%，远超25%安全标准")
        
        report.append(f"#### 💊 综合治疗建议")
        if tar > 75:
            report.append(f"- **紧急处理**: 血糖控制极差，建议立即就医调整治疗方案")
            report.append(f"  - 考虑胰岛素强化治疗")
            report.append(f"  - 排除急性并发症（如酮症酸中毒）")
        if tar > 50:
            report.append(f"- **药物调整**: 现有降糖方案效果不佳，需要优化")
            report.append(f"  - 增加降糖药物剂量或种类")
            report.append(f"  - 考虑联合用药（如二甲双胍+胰岛素）")
        if tar > 25:
            report.append(f"- **生活方式强化**:")
            report.append(f"  - 严格控制碳水化合物摄入，避免精制糖")
            report.append(f"  - 增加运动频率和强度（在安全范围内）")
            report.append(f"  - 定期监测餐后血糖，及时调整")
            
        report.append(f"#### 🎯 短期目标设定")
        if tar > 75:
            report.append(f"- **4周内目标**: TAR降至<60%，平均血糖<12 mmol/L")
        elif tar > 50:
            report.append(f"- **8周内目标**: TAR降至<40%，平均血糖<10 mmol/L")
        else:
            report.append(f"- **12周内目标**: TAR降至<25%，平均血糖<8.6 mmol/L")
    
    # 添加综合评估和后续建议（修正评分算法）
    report.append(f"\n### 📋 综合评估与随访计划")
    # 修正评分算法：更重视TIR和TAR，CV为辅助因素
    overall_score = tir*0.8 - tar*0.6 - tbr*5 - max(0, cv-36)*0.2
    overall_score = max(0, overall_score)  # 确保不为负数
    
    if overall_score >= 50:
        overall_rating = "优秀 🏆"
    elif overall_score >= 30:
        overall_rating = "良好 👍"
    elif overall_score >= 15:
        overall_rating = "一般 ⚠️"
    else:
        overall_rating = "需要改善 🚨"
        
    report.append(f"- 🎯 **血糖管理综合评分**: {overall_rating}")
    report.append(f"- 📅 **建议随访频率**: {'2-4周' if overall_score < 15 else '1-3个月' if overall_score < 30 else '3-6个月'}")
    report.append(f"- 🔄 **下次CGM建议**: {'立即重新佩戴' if tar > 75 or tbr > 10 else '3-6个月后' if overall_score > 30 else '1-3个月后'}")
    
    report.append("\n" + "="*60)
    report.append("📊 **报告生成完毕** | 建议与医生详细讨论制定个性化治疗方案")
    report.append("⚠️  **免责声明**: 本报告仅供临床参考，具体治疗方案请遵医嘱")
    report.append("="*60)
    return report

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 4: Data Loading and Calculation (Unchanged)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def load_data(filepath: str) -> pd.DataFrame:
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
    return df

def calculate_metrics(df: pd.DataFrame) -> dict:
    glucose_values = df['glucose'].dropna()
    if glucose_values.empty:
        return {}

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
    tir_percentage = (glucose_values.between(3.9, 10.0).sum() / total_readings) * 100
    tbr_percentage = (glucose_values < 3.9).sum() / total_readings * 100
    tar_percentage = (glucose_values > 10.0).sum() / total_readings * 100

    critical_events_string = find_critical_events(df)

    patient_data = {
        "cgm_wear_days": monitoring_days,
        "cgm_valid_data_percentage": valid_data_percentage,
        "tir_percentage": tir_percentage,
        "tbr_percentage": tbr_percentage,
        "tar_percentage": tar_percentage,
        "mean_glucose": mean_glucose,
        "cv": cv,
        "critical_events_string": critical_events_string
    }
    return patient_data

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Section 5: Main execution block (Enhanced)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main():
    if len(sys.argv) < 2:
        print("错误: 请提供Excel或CSV文件路径作为参数。")
        sys.exit(1)

    filepath = sys.argv[1]
    patient_id = filepath.split('/')[-1].split('-')[0]

    try:
        with open('/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/5Steps.json', 'r', encoding='utf-8') as f:
            agp_rules = json.load(f)

        print(f"🔄 正在读取数据: {filepath}")
        raw_df = load_data(filepath)
        
        print("📊 正在计算各项血糖指标...")
        patient_metrics = calculate_metrics(raw_df)
        patient_metrics['patient_id'] = patient_id

        print("📝 正在生成增强版五步法解读报告...")
        report_lines = generate_5_step_report(patient_metrics, agp_rules)
        
        print("\n" + "="*80)
        for line in report_lines:
            print(line)
        print("="*80)

    except FileNotFoundError as e:
        print(f"❌ 文件未找到错误: {e}")
    except ValueError as e:
        print(f"❌ 数据处理错误: {e}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

if __name__ == "__main__":
    main()