#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全移除5步法报告中的所有emoji并更改步骤编号为中文数字
"""
import re

def complete_emoji_cleanup():
    file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/5Steps/run_report_layered_assessment.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 步骤编号替换 - 更改为中文数字
    step_replacements = [
        (r'步骤 1:', '步骤一:'),
        (r'步骤 2:', '步骤二:'),
        (r'步骤 3:', '步骤三:'),
        (r'步骤 4:', '步骤四:'),
        (r'步骤 5:', '步骤五:'),
    ]
    
    for pattern, replacement in step_replacements:
        content = re.sub(pattern, replacement, content)
    
    # 完全移除所有emoji字符
    # Unicode emoji范围
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002700-\U000027BF"  # dingbats
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U00002600-\U000026FF"  # Miscellaneous Symbols
        u"\U0000FE00-\U0000FE0F"  # Variation Selectors
        "]+", flags=re.UNICODE)
    
    # 移除所有emoji
    content = emoji_pattern.sub('', content)
    
    # 清理多余的空格和格式
    content = re.sub(r' +', ' ', content)  # 多个空格变为单个
    content = re.sub(r'- \*\*', '- **', content)  # 修复可能的格式问题
    content = re.sub(r'#### ', '#### ', content)  # 确保标题格式正确
    content = re.sub(r'### ', '### ', content)
    content = re.sub(r'## ', '## ', content)
    
    # 特殊清理：移除可能残留的emoji相关字符
    content = re.sub(r'[\u2600-\u26FF\u2700-\u27BF]', '', content)  # 额外的符号范围
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 所有emoji已完全移除，步骤编号已更改为中文数字")

if __name__ == "__main__":
    complete_emoji_cleanup()