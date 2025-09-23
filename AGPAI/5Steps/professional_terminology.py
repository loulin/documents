#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业术语替换：将活泼用词替换为医学指南标准表述
"""
import re

def professional_terminology_upgrade():
    file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/run_report_layered_assessment.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 评估等级专业化
    professional_replacements = [
        # 评估等级替换
        ('"level": "代谢健康卓越"', '"level": "代谢健康状态理想"'),
        ('"level": "代谢健康优秀"', '"level": "代谢健康状态良好"'),
        ('"level": "代谢健康良好"', '"level": "代谢健康状态尚可"'),
        ('"level": "需要生活方式优化"', '"level": "血糖控制亚优，需要调整"'),
        ('"level": "需要医学关注"', '"level": "血糖控制不理想，需医学干预"'),
        ('"level": "基础控制良好"', '"level": "血糖控制基本达标"'),
        ('"level": "基础控制可接受"', '"level": "血糖控制欠佳"'),
        ('"level": "需要治疗强化"', '"level": "血糖控制不良，需强化治疗"'),
        ('"level": "需要积极干预"', '"level": "血糖控制较差，需积极干预"'),
        ('"level": "需要紧急医疗干预"', '"level": "血糖控制很差，需紧急处理"'),
        
        # 建议内容专业化
        ('"recommendation": "继续维持当前优秀状态"', '"recommendation": "继续维持现有管理方案"'),
        ('"recommendation": "保持现有生活方式"', '"recommendation": "维持现有治疗方案"'),
        ('"recommendation": "可适当优化饮食和运动"', '"recommendation": "建议优化生活方式干预"'),
        ('"recommendation": "积极改善饮食结构和运动习惯"', '"recommendation": "需要强化生活方式管理"'),
        ('"recommendation": "建议专科医生评估"', '"recommendation": "建议内分泌专科评估"'),
        ('"recommendation": "渐进式改善治疗方案"', '"recommendation": "建议调整治疗方案"'),
        ('"recommendation": "优化治疗方案和生活方式"', '"recommendation": "需优化治疗方案及生活方式"'),
        ('"recommendation": "调整药物剂量，强化生活干预"', '"recommendation": "需调整药物治疗并强化生活方式干预"'),
        ('"recommendation": "强化治疗，必要时住院调整"', '"recommendation": "需强化治疗，必要时住院管理"'),
        ('"recommendation": "立即医疗干预，考虑住院治疗"', '"recommendation": "需立即医疗干预，建议住院治疗"'),
        
        # 报告中的表述专业化
        ('血糖控制优秀，按代谢健康标准评估', '血糖控制良好，按代谢健康人群标准评估'),
        ('血糖控制需要改善，重点关注安全性', '血糖控制欠佳，应重点关注低血糖风险'),
        ('安全性极佳', '低血糖风险极低'),
        ('整体安全', '低血糖风险较低'),
        ('优秀，血糖波动很小', '良好，血糖波动较小'),
        ('良好，血糖相对稳定', '尚可，血糖波动在可接受范围内'),
        ('需要改善，存在明显波动', '欠佳，血糖波动较大'),
        ('很低，代谢状态优秀', '较低，代谢状态良好'),
        ('在可接受范围内', '在临床可接受范围内'),
        ('偏高，建议生活方式调整', '偏高，建议调整生活方式'),
        ('重度高血糖较少', '严重高血糖事件较少'),
        ('过重，需要强化治疗', '较重，需要强化治疗'),
        
        # 风险评估专业化
        ('安全警示', '风险提示'),
        ('重点管理', '管理要点'),
        ('安全有效性', '安全性与有效性'),
        ('昼夜均衡', '昼夜血糖控制'),
        ('安全优先', '安全性优先'),
        ('重点改善', '管理重点'),
        
        # 建议内容专业化
        ('立即调整', '治疗调整'),
        ('监测加强', '监测强化'),
        ('急救准备', '低血糖应急处理'),
        ('家属教育', '患者及家属教育'),
        ('专科评估', '专科医师评估'),
        
        # 删除过于主观的修饰词
        ('明显不佳', '不佳'),
        ('相对更好', '相对较好'),
        ('表现较好', '控制较好'),
        ('尽管TIR表现较好', ''),
    ]
    
    # 应用替换
    for old_text, new_text in professional_replacements:
        content = re.sub(re.escape(old_text), new_text, content)
    
    # 2. 清理残留的emoji和非专业表述
    content = re.sub(r'☀️', '', content)
    content = re.sub(r'🛡️', '', content)
    
    # 3. 规范化专业表述
    content = re.sub(r'很低', '较低', content)
    content = re.sub(r'很小', '较小', content)
    content = re.sub(r'很差', '较差', content)
    content = re.sub(r'极佳', '良好', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 专业术语升级完成：用词已规范化为医学指南标准表述")

if __name__ == "__main__":
    professional_terminology_upgrade()