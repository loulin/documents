#!/usr/bin/env python3
"""
使用ReportLab创建PDF营养建议报告
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_nutrition_pdf():
    """创建营养建议PDF报告"""

    print("📄 正在创建PDF营养建议报告...")

    # 创建PDF文档
    pdf_file = "王先生个性化营养干预方案.pdf"
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # 获取样式
    styles = getSampleStyleSheet()

    # 自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#34495e')
    )

    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#7f8c8d')
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leading=14,
        alignment=TA_JUSTIFY
    )

    # 存储所有内容
    story = []

    # 标题
    story.append(Paragraph("王先生 个性化营养干预方案", title_style))
    story.append(Paragraph("患者档案：58岁男性，高血压、血脂异常、肥胖症", normal_style))
    story.append(Spacer(1, 20))

    # 患者基本信息
    story.append(Paragraph("📋 患者基本信息", heading_style))

    basic_info_data = [
        ['项目', '数值', '评估'],
        ['姓名', '王先生', '-'],
        ['年龄', '58岁', '中老年男性'],
        ['身高', '170cm', '-'],
        ['体重', '85kg', '超重'],
        ['BMI', '29.4', '肥胖症(I度)'],
        ['活动水平', '轻度活动', '建议增加运动']
    ]

    basic_info_table = Table(basic_info_data, colWidths=[4*cm, 4*cm, 4*cm])
    basic_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#495057')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(basic_info_table)
    story.append(Spacer(1, 20))

    # 健康状况评估
    story.append(Paragraph("🏥 健康状况详细评估", heading_style))
    story.append(Paragraph("心血管风险评估", subheading_style))

    health_data = [
        ['指标', '数值', '正常范围', '风险评级'],
        ['收缩压', '155 mmHg', '<120 mmHg', '⚠️ 高血压2期'],
        ['舒张压', '95 mmHg', '<80 mmHg', '⚠️ 高血压2期'],
        ['总胆固醇', '6.8 mmol/L', '<5.2 mmol/L', '🔴 显著升高'],
        ['LDL胆固醇', '4.5 mmol/L', '<3.4 mmol/L', '🔴 显著升高'],
        ['HDL胆固醇', '0.9 mmol/L', '>1.0 mmol/L', '🔴 偏低'],
        ['甘油三酯', '2.8 mmol/L', '<1.7 mmol/L', '🔴 显著升高']
    ]

    health_table = Table(health_data, colWidths=[3*cm, 3*cm, 3*cm, 3.5*cm])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#495057')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # 高风险项目标红
        ('TEXTCOLOR', (3, 1), (3, -1), colors.red)
    ]))

    story.append(health_table)
    story.append(Spacer(1, 15))

    # 综合风险评估
    story.append(Paragraph("综合风险评估", subheading_style))
    risk_text = """
    • <b>心血管疾病风险</b>: 🔴 极高风险<br/>
    • <b>代谢综合征</b>: ✅ 符合诊断标准<br/>
    • <b>干预优先级</b>: 🚨 最高优先级
    """
    story.append(Paragraph(risk_text, normal_style))
    story.append(Spacer(1, 20))

    # 个性化营养目标
    story.append(Paragraph("🎯 个性化营养目标", heading_style))
    story.append(Paragraph("热量平衡计算", subheading_style))

    calorie_text = """
    • <b>基础代谢率(BMR)</b>: 1,714 千卡/天<br/>
    • <b>总日消耗(TDEE)</b>: 2,356 千卡/天<br/>
    • <b>减重目标热量</b>: 1,885 千卡/天 (减少20%)<br/>
    • <b>预期减重速度</b>: 0.5-0.7 kg/周
    """
    story.append(Paragraph(calorie_text, normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("宏量营养素分配", subheading_style))

    macro_data = [
        ['营养素', '目标摄入量', '热量占比', '科学依据'],
        ['碳水化合物', '236g', '50%', '复合碳水为主'],
        ['蛋白质', '118g', '25%', '增肌保护代谢'],
        ['脂肪', '52g', '25%', '限制饱和脂肪']
    ]

    macro_table = Table(macro_data, colWidths=[3*cm, 3*cm, 2.5*cm, 4*cm])
    macro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#495057')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(macro_table)
    story.append(PageBreak())

    # 每日详细食谱方案
    story.append(Paragraph("🍽️ 每日详细食谱方案", heading_style))

    # 早餐
    story.append(Paragraph("🌅 早餐 (450千卡)", subheading_style))
    story.append(Paragraph("推荐：燕麦鸡蛋套餐", normal_style))

    breakfast_data = [
        ['食物', '重量', '热量', '制作方法'],
        ['燕麦片', '40g', '156千卡', '热水冲泡，无糖'],
        ['鸡蛋(水煮)', '1个(60g)', '93千卡', '水煮7分钟'],
        ['脱脂牛奶', '200ml', '68千卡', '温热饮用'],
        ['苹果', '100g', '52千卡', '生食，带皮'],
        ['核桃(少量)', '10g', '65千卡', '补充ω-3脂肪酸']
    ]

    breakfast_table = Table(breakfast_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 4.5*cm])
    breakfast_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f5e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2d5016')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(breakfast_table)
    story.append(Paragraph("<i>营养亮点: 高纤维燕麦降胆固醇，优质蛋白维持饱腹感</i>", normal_style))
    story.append(Spacer(1, 15))

    # 午餐
    story.append(Paragraph("🍽️ 午餐 (630千卡)", subheading_style))
    story.append(Paragraph("推荐：清蒸鱼配蔬菜", normal_style))

    lunch_data = [
        ['食物', '重量', '制作方法', '营养价值'],
        ['糙米饭', '80g(干重)', '蒸制，不加油盐', '复合碳水，B族维生素'],
        ['清蒸鲈鱼', '150g', '姜丝蒸15分钟', '优质蛋白，ω-3脂肪酸'],
        ['蒜蓉菠菜', '200g', '少油快炒', '叶酸，钾，镁'],
        ['凉拌黄瓜', '150g', '醋拌，无油', '维生素C，膳食纤维']
    ]

    lunch_table = Table(lunch_data, colWidths=[3*cm, 2.5*cm, 3*cm, 4*cm])
    lunch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff3cd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#856404')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(lunch_table)
    story.append(Paragraph("<i>烹饪要点: 总用油量控制在8ml以内，菠菜焯水去草酸</i>", normal_style))
    story.append(Spacer(1, 15))

    # 晚餐
    story.append(Paragraph("🌙 晚餐 (550千卡)", subheading_style))
    story.append(Paragraph("推荐：豆腐蔬菜汤", normal_style))

    dinner_data = [
        ['食物', '重量', '制作方法', '健康功效'],
        ['荞麦面', '50g(干重)', '清水煮制', '低GI，降血脂'],
        ['冬瓜豆腐汤', '300g', '清汤煮制', '利尿消肿，植物蛋白'],
        ['西兰花', '150g', '水焯后调味', '维生素C，异硫氰酸酯'],
        ['紫菜蛋花汤', '一碗', '少盐调味', '碘，优质蛋白']
    ]

    dinner_table = Table(dinner_data, colWidths=[3*cm, 2.5*cm, 3*cm, 4*cm])
    dinner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1ecf1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0c5460')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(dinner_table)
    story.append(Paragraph("<i>营养特点: 低钠清淡，富含钾镁，有助血压控制</i>", normal_style))
    story.append(PageBreak())

    # 专业建议
    story.append(Paragraph("💡 专业营养建议", heading_style))

    story.append(Paragraph("🔴 高血压管理", subheading_style))
    hypertension_text = """
    <b>DASH饮食原则</b><br/>
    • 每日蔬果：400-500g<br/>
    • 全谷物：150-200g<br/>
    • 低脂乳制品：300ml<br/>
    • 瘦肉蛋白：150-200g<br/><br/>

    <b>限钠策略</b><br/>
    • 避免咸菜、腌制品<br/>
    • 烹饪用盐&lt;3g/天<br/>
    • 用柠檬、香草调味<br/>
    • 选择低钠调料
    """
    story.append(Paragraph(hypertension_text, normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("🔴 血脂管理", subheading_style))
    lipid_text = """
    <b>降胆固醇食物</b><br/>
    • 燕麦β-葡聚糖：3-6g/天<br/>
    • 坚果：25-30g/天<br/>
    • 深海鱼：每周2-3次<br/>
    • 植物固醇：2-3g/天<br/><br/>

    <b>避免食物</b><br/>
    • 动物内脏、蛋黄(限制)<br/>
    • 油炸食品、糕点<br/>
    • 椰子油、棕榈油<br/>
    • 反式脂肪食品
    """
    story.append(Paragraph(lipid_text, normal_style))
    story.append(Spacer(1, 15))

    # 预期效果
    story.append(Paragraph("🎯 预期效果", heading_style))

    effects_data = [
        ['时间段', '体重目标', '血压目标', '血脂目标'],
        ['1-3个月', '减重4-8kg', '下降10-20mmHg', '总胆固醇<5.5mmol/L'],
        ['3-6个月', 'BMI: 25-27', '<140/90mmHg', 'LDL<3.4mmol/L'],
        ['6-12个月', '理想体重75kg', '<130/80mmHg', '血脂全面达标']
    ]

    effects_table = Table(effects_data, colWidths=[3*cm, 3*cm, 3*cm, 3.5*cm])
    effects_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4edda')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#155724')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(effects_table)
    story.append(Spacer(1, 20))

    # 注意事项
    story.append(Paragraph("⚠️ 特别注意事项", heading_style))

    warnings_text = """
    <b>🚨 严格限制</b><br/>
    • 高钠食物: 咸菜、腌制品、方便面<br/>
    • 高糖食物: 甜品、含糖饮料、糖果<br/>
    • 高脂食物: 肥肉、油炸食品、糕点<br/>
    • 饮酒限制: 戒酒或严格限制(&lt;25g酒精/天)<br/><br/>

    <b>📋 监测指标</b><br/>
    • 每日监测: 体重(晨起空腹)、血压(早晚各一次)<br/>
    • 每周监测: 腰围(脐部水平)、体脂率<br/>
    • 每月监测: 血脂全套、肝肾功能、血糖指标<br/><br/>

    <b>💊 配合治疗</b><br/>
    • 按医嘱服用降压药和降脂药<br/>
    • 定期复查调整用药<br/>
    • 营养师定期随访
    """
    story.append(Paragraph(warnings_text, normal_style))
    story.append(Spacer(1, 20))

    # 底部信息
    footer_text = """
    <i>报告生成时间: 2025年09月20日<br/>
    基于循证医学和中国居民膳食指南<br/>
    本方案需在医生指导下实施</i>
    """
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=9,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER
    )))

    # 生成PDF
    doc.build(story)
    print(f"✅ PDF报告已生成: {pdf_file}")
    return pdf_file

if __name__ == "__main__":
    result = create_nutrition_pdf()
    print(f"\n🎉 PDF转换完成！")
    print(f"📁 文件位置: /Users/williamsun/Documents/gplus/docs/FoodRecom/{result}")
    print(f"📊 文件大小: {os.path.getsize(result) / 1024:.1f} KB")