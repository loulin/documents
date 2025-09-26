#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确移除所有emoji并更改步骤编号为中文数字
"""
import re

def precise_emoji_cleanup():
    file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/run_report_layered_assessment.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 移除level_emoji和level_color中的emoji
    content = re.sub(r'"level_emoji": "[^"]*"', '"level_emoji": ""', content)
    content = re.sub(r'"level_color": "[^"]*"', '"level_color": ""', content)
    
    # 2. 步骤编号替换为中文数字
    content = re.sub(r'步骤 1:', '步骤一:', content)
    content = re.sub(r'步骤 2:', '步骤二:', content)
    content = re.sub(r'步骤 3:', '步骤三:', content)
    content = re.sub(r'步骤 4:', '步骤四:', content)
    content = re.sub(r'步骤 5:', '步骤五:', content)
    
    # 3. 移除报告生成中的所有emoji
    # 标题中的emoji
    emoji_replacements = [
        # 报告头部
        (r'📋 患者ID:', '患者ID:'),
        (r'📅 分析时间:', '分析时间:'),
        (r'🎯 评估类型:', '评估类型:'),
        (r'📊 主要建议:', '主要建议:'),
        (r'🔄 随访频率:', '随访频率:'),
        
        # 步骤标题
        (r'### 📊 ', '### '),
        (r'### 🎯 ', '### '),
        (r'### ⚠️  ', '### '),
        (r'### 🔥 ', '### '),
        (r'### 📋 ', '### '),
        
        # 子标题
        (r'#### 🚨 ', '#### '),
        (r'#### 💊 ', '#### '),
        (r'#### 🌙☀️ ', '#### '),
        
        # 列表项目
        (r'- 🕐 ', '- '),
        (r'- 📈 ', '- '),
        (r'- ✅ ', '- '),
        (r'- ❌ ', '- '),
        (r'- 🔧 ', '- '),
        (r'- 📊 \*\*', '- **'),
        (r'- 🎯 \*\*', '- **'),
        (r'- 🛡️  \*\*', '- **'),
        (r'- 🎉 \*\*', '- **'),
        (r'- 💎 \*\*', '- **'),
        (r'- 📋 \*\*', '- **'),
        (r'- 🔄 \*\*', '- **'),
        (r'- 🌙 \*\*', '- **'),
        (r'- ☀️ \*\*', '- **'),
        (r'- 🚨 \*\*', '- **'),
        (r'- ⚠️ \*\*', '- **'),
        (r'- 💚 \*\*', '- **'),
        (r'- 🟢 \*\*', '- **'),
        (r'- 🟡 \*\*', '- **'),
        (r'- 🔴 \*\*', '- **'),
        (r'- 📉 \*\*', '- **'),
        (r'- 📅 ', '- '),
        (r'- 🍬 \*\*', '- **'),
        (r'- 👨‍👩‍👧‍👦 \*\*', '- **'),
        (r'- 🏥 \*\*', '- **'),
        (r'- 📱 \*\*', '- **'),
        (r'- 📊 \*\*', '- **'),
        
        # 打印信息中的emoji
        (r'print\(f"🔄 ', 'print(f"'),
        (r'print\("📊 ', 'print("'),
        (r'print\("📝 ', 'print("'),
        (r'print\(f"❌ ', 'print(f"'),
        
        # 底部信息
        (r'📊 \*\*', '**'),
        (r'⚠️  \*\*', '**'),
    ]
    
    # 应用替换
    for pattern, replacement in emoji_replacements:
        content = re.sub(pattern, replacement, content)
    
    # 4. 移除{layered_result['level_color']}前缀
    content = re.sub(r'{layered_result\[\'level_color\'\]} ', '', content)
    
    # 5. 移除{layered_result['level_emoji']}前缀 
    content = re.sub(r'{layered_result\[\'level_emoji\'\]} \*\*', '**', content)
    
    # 6. 通用emoji清理 - 只移除Unicode emoji字符
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002600-\U000026FF"  # miscellaneous symbols
        u"\U00002700-\U000027BF"  # dingbats
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U0000FE00-\U0000FE0F"  # Variation Selectors
        "]+", flags=re.UNICODE)
    
    content = emoji_pattern.sub('', content)
    
    # 7. 清理格式
    content = re.sub(r' +', ' ', content)  # 多个空格变为单个
    content = re.sub(r'- \*\*', '- **', content)  # 修复格式
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 所有emoji已完全移除，步骤编号已更改为中文数字")

if __name__ == "__main__":
    precise_emoji_cleanup()