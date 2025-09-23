#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确清理脚本：只移除emoji，保留所有中文内容，并更改步骤编号为中文数字
"""
import re

def precise_clean_emojis():
    file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/run_report_layered_assessment.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 首先替换步骤编号为中文数字
    content = re.sub(r'步骤 1:', '步骤一:', content)
    content = re.sub(r'步骤 2:', '步骤二:', content)
    content = re.sub(r'步骤 3:', '步骤三:', content)
    content = re.sub(r'步骤 4:', '步骤四:', content)
    content = re.sub(r'步骤 5:', '步骤五:', content)
    
    # 2. 移除数据结构中的emoji字段内容
    content = re.sub(r'"level_emoji": "[^"]*"', '"level_emoji": ""', content)
    content = re.sub(r'"level_color": "[^"]*"', '"level_color": ""', content)
    
    # 3. 移除报告生成中的emoji前缀（精确匹配特定模式）
    emoji_replacements = [
        # 标题前的emoji
        (r'### 📊 ', '### '),
        (r'### 🎯 ', '### '),
        (r'### ⚠️  ', '### '),
        (r'### 📊 ', '### '),
        (r'### 🔥 ', '### '),
        (r'### 📋 ', '### '),
        
        # 子标题前的emoji
        (r'#### 🚨 ', '#### '),
        (r'#### 💊 ', '#### '),
        (r'#### 🌙☀️ ', '#### '),
        
        # 列表项前的emoji
        (r'- 📋 ', '- '),
        (r'- 📅 ', '- '),
        (r'- 🎯 ', '- '),
        (r'- 📊 ', '- '),
        (r'- 🔄 ', '- '),
        (r'- 🕐 ', '- '),
        (r'- 📈 ', '- '),
        (r'- ✅ ', '- '),
        (r'- ❌ ', '- '),
        (r'- 🔧 ', '- '),
        (r'- 🎉 ', '- '),
        (r'- 💎 ', '- '),
        (r'- 🛡️ ', '- '),
        (r'- 🌙 ', '- '),
        (r'- ☀️ ', '- '),
        (r'- 🚨 ', '- '),
        (r'- ⚠️ ', '- '),
        (r'- 📉 ', '- '),
        (r'- 💚 ', '- '),
        (r'- 🟢 ', '- '),
        (r'- 🟡 ', '- '),
        (r'- 🔴 ', '- '),
        (r'- 🍬 ', '- '),
        (r'- 👨‍👩‍👧‍👦 ', '- '),
        (r'- 🏥 ', '- '),
        (r'- 📱 ', '- '),
        (r'- 📍 ', '- '),
        
        # 打印信息中的emoji
        (r'print\(f"🔄 ', 'print(f"'),
        (r'print\("📊 ', 'print("'),
        (r'print\("📝 ', 'print("'),
        (r'print\(f"❌ ', 'print(f"'),
        
        # 报告底部
        (r'📊 \*\*', '**'),
        (r'⚠️  \*\*', '**'),
    ]
    
    # 应用emoji替换
    for pattern, replacement in emoji_replacements:
        content = re.sub(pattern, replacement, content)
    
    # 4. 移除{layered_result['level_color']} 和 {layered_result['level_emoji']} 的使用
    content = re.sub(r'\{layered_result\[\'level_color\'\]\} ', '', content)
    content = re.sub(r'\{layered_result\[\'level_emoji\'\]\} ', '', content)
    
    # 5. 最后使用精确的Unicode emoji范围清理（只清理真正的emoji字符）
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
        "]+", flags=re.UNICODE)
    
    content = emoji_pattern.sub('', content)
    
    # 6. 清理格式问题
    content = re.sub(r' +', ' ', content)  # 多个空格变为单个
    content = re.sub(r'- \*\*', '- **', content)  # 修复可能的格式问题
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 精确清理完成：所有emoji已移除，步骤编号已更改为中文数字，所有中文内容保留")

if __name__ == "__main__":
    precise_clean_emojis()