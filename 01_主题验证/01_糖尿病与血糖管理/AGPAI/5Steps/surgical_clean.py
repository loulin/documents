#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外科手术式精确清理：只移除emoji，完全保留中文内容
"""
import re

def surgical_clean():
    file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/run_report_layered_assessment.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 1: 更改步骤编号
    content = re.sub(r'步骤 1:', '步骤一:', content)
    content = re.sub(r'步骤 2:', '步骤二:', content) 
    content = re.sub(r'步骤 3:', '步骤三:', content)
    content = re.sub(r'步骤 4:', '步骤四:', content)
    content = re.sub(r'步骤 5:', '步骤五:', content)
    
    # Step 2: 清空emoji字段但保留字段结构
    content = re.sub(r'"level_emoji": "[^"]*"', '"level_emoji": ""', content)
    content = re.sub(r'"level_color": "[^"]*"', '"level_color": ""', content)
    
    # Step 3: 移除报告生成中的emoji（但保留后面的中文）
    # 这些替换只针对特定的emoji前缀模式
    patterns = [
        (r'📋 患者ID:', '患者ID:'),
        (r'📅 分析时间:', '分析时间:'),
        (r'🎯 评估类型:', '评估类型:'),
        (r'📊 主要建议:', '主要建议:'),
        (r'🔄 随访频率:', '随访频率:'),
        (r'### 📊 ', '### '),
        (r'### 🎯 ', '### '),
        (r'### ⚠️  ', '### '),
        (r'### 🔥 ', '### '),
        (r'### 📋 ', '### '),
        (r'#### 🚨 ', '#### '),
        (r'#### 💊 ', '#### '),
        (r'#### 🌙☀️ ', '#### '),
        (r'- 🕐 ', '- '),
        (r'- 📈 ', '- '),
        (r'- ✅ ', '- '),
        (r'- ❌ ', '- '),
        (r'- 🔧 ', '- '),
        (r'- 📊 ', '- '),
        (r'- 🎯 ', '- '),
        (r'- 🛡️  ', '- '),
        (r'- 🎉 ', '- '),
        (r'- 💎 ', '- '),
        (r'- 📋 ', '- '),
        (r'- 🔄 ', '- '),
        (r'- 🌙 ', '- '),
        (r'- ☀️ ', '- '),
        (r'- 🚨 ', '- '),
        (r'- ⚠️ ', '- '),
        (r'- 💚 ', '- '),
        (r'- 🟢 ', '- '),
        (r'- 🟡 ', '- '),
        (r'- 🔴 ', '- '),
        (r'- 📉 ', '- '),
        (r'- 📅 ', '- '),
        (r'- 🍬 ', '- '),
        (r'- 👨‍👩‍👧‍👦 ', '- '),
        (r'- 🏥 ', '- '),
        (r'- 📱 ', '- '),
        (r'- 📍 ', '- '),
        (r'print\(f"🔄 ', 'print(f"'),
        (r'print\("📊 ', 'print("'),
        (r'print\("📝 ', 'print("'),
        (r'print\(f"❌ ', 'print(f"'),
    ]
    
    # 应用替换
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Step 4: 移除layered_result中emoji的使用
    content = re.sub(r'\{layered_result\[\'level_color\'\]\} ', '', content)
    content = re.sub(r'\{layered_result\[\'level_emoji\'\]\} ', '', content)
    
    # Step 5: 移除报告底部的emoji
    content = re.sub(r'📊 \*\*分层评估报告生成完毕\*\*', '**分层评估报告生成完毕**', content)
    content = re.sub(r'⚠️  \*\*免责声明\*\*:', '**免责声明**:', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 外科手术式清理完成：emoji已精确移除，中文内容完全保留")

if __name__ == "__main__":
    surgical_clean()