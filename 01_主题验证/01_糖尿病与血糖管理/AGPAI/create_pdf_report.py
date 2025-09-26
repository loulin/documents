#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Markdown到PDF转换工具
使用HTML作为中间格式
"""

import re
import os

def markdown_to_html(md_content):
    """简单的Markdown到HTML转换"""
    
    # 基本HTML模板
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>连续血糖监测分析报告</title>
    <style>
        @media print {{
            body {{ margin: 0; padding: 20px; }}
            .page-break {{ page-break-before: always; }}
        }}
        body {{
            font-family: "PingFang SC", "Microsoft YaHei", "SimHei", sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            font-size: 24px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            font-size: 20px;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #34495e;
            font-size: 16px;
            margin-top: 25px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #bdc3c7;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #ecf0f1;
            font-weight: bold;
            color: #2c3e50;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .checkmark {{
            color: #27ae60;
            font-weight: bold;
        }}
        ul, ol {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        strong {{
            color: #2c3e50;
        }}
        hr {{
            border: none;
            border-top: 1px solid #bdc3c7;
            margin: 30px 0;
        }}
        .summary-box {{
            background-color: #e8f6f3;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

    # 转换标题
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md_content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # 转换表格
    lines = content.split('\n')
    html_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                html_lines.append('<table>')
                in_table = True
            
            # 处理表头分隔行
            if re.match(r'^\|[\s\-\|]+\|$', line.strip()):
                continue
                
            # 处理表格行
            cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
            
            # 判断是否为表头（下一行是分隔行）
            is_header = (i + 1 < len(lines) and 
                        re.match(r'^\|[\s\-\|]+\|$', lines[i + 1].strip()))
            
            if is_header:
                row_html = '<tr>' + ''.join(f'<th>{cell}</th>' for cell in cells) + '</tr>'
            else:
                # 处理特殊标记
                processed_cells = []
                for cell in cells:
                    cell = cell.replace('✓', '<span class="checkmark">✓</span>')
                    cell = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', cell)
                    processed_cells.append(cell)
                row_html = '<tr>' + ''.join(f'<td>{cell}</td>' for cell in processed_cells) + '</tr>'
            
            html_lines.append(row_html)
        else:
            if in_table:
                html_lines.append('</table>')
                in_table = False
            
            # 处理其他元素
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'^\- (.+)$', r'<li>\1</li>', line, flags=re.MULTILINE)
            line = re.sub(r'^(\d+)\. (.+)$', r'<li>\1. \2</li>', line, flags=re.MULTILINE)
            
            # 处理段落
            if line.strip() and not line.startswith('<'):
                line = f'<p>{line}</p>'
            
            html_lines.append(line)
    
    if in_table:
        html_lines.append('</table>')
    
    # 处理列表
    content = '\n'.join(html_lines)
    content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', content, flags=re.DOTALL)
    content = re.sub(r'</ul>\s*<ul>', '', content)
    
    # 清理空段落
    content = re.sub(r'<p>\s*</p>', '', content)
    content = re.sub(r'<p>\s*<h', r'<h', content)
    content = re.sub(r'</h([123])>\s*</p>', r'</h\1>', content)
    
    return html_template.format(content=content)

def main():
    md_file = "/Users/williamsun/Documents/gplus/docs/AGPAI/临床血糖分析报告-匿名版.md"
    html_file = "/Users/williamsun/Documents/gplus/docs/AGPAI/临床血糖分析报告-匿名版-formatted.html"
    
    print("开始转换Markdown到HTML...")
    
    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 转换为HTML
    html_content = markdown_to_html(md_content)
    
    # 保存HTML文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML文件已生成: {html_file}")
    print("您可以:")
    print("1. 在浏览器中打开HTML文件")
    print("2. 使用浏览器的打印功能保存为PDF")
    print("3. 使用 Cmd+P -> 保存为PDF")

if __name__ == "__main__":
    main()