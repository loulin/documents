#!/usr/bin/env python3
"""
Convert ZS HMC CGM JSON report to markdown format
"""

import json
import sys
from pathlib import Path

def format_value(value):
    """Format value for markdown display"""
    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return value
    elif isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            return '\n'.join(f"- {item}" for item in value)
        else:
            return '\n'.join(f"- {str(item)}" for item in value)
    else:
        return str(value)

def dict_to_markdown(data, level=0):
    """Convert dictionary to markdown format"""
    markdown = ""

    for key, value in data.items():
        if isinstance(value, dict):
            # 检查是否是表格数据
            if key.endswith("对比表格") or key.endswith("comparison_table"):
                markdown += f"\n{'#' * (level + 3)} {key}\n\n"
                markdown += format_comparison_table(value)
            else:
                if level == 0:
                    markdown += f"\n# {key}\n\n"
                elif level == 1:
                    markdown += f"\n## {key}\n\n"
                elif level == 2:
                    markdown += f"\n### {key}\n\n"
                else:
                    markdown += f"\n{'#' * (level + 3)} {key}\n\n"

                markdown += dict_to_markdown(value, level + 1)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            # 检查是否是表格数据
            if "表格数据" in key or "分段数据表" in key or "趋势变化表" in key:
                markdown += f"\n{'#' * (level + 3)} {key}\n\n"
                markdown += format_table_data(value)
            else:
                markdown += f"\n{'#' * (level + 3)} {key}\n\n"
                for i, item in enumerate(value, 1):
                    if isinstance(item, dict):
                        markdown += f"**项目 {i}:**\n\n"
                        markdown += dict_to_markdown(item, level + 1)
                        markdown += "\n"
                    else:
                        markdown += f"- {format_value(item)}\n"
        else:
            # 特殊处理表格数据
            if (key.endswith("对比表格") or key.endswith("comparison_table") or "表格" in key) and isinstance(value, dict):
                markdown += f"\n{'#' * (level + 3)} {key}\n\n"
                markdown += format_longitudinal_table(value)
            else:
                formatted_value = format_value(value)
                if '\n' in formatted_value:
                    markdown += f"**{key}:**\n\n{formatted_value}\n\n"
                else:
                    markdown += f"**{key}:** {formatted_value}\n\n"

    return markdown

def format_comparison_table(table_data):
    """Format comparison table data as markdown table"""
    if "表格数据" not in table_data:
        return format_value(table_data)

    table_rows = table_data["表格数据"]
    if not table_rows:
        return "无表格数据\n\n"

    # 获取表格标题
    title = table_data.get("表格标题", "对比分析表")
    markdown = f"**{title}**\n\n"

    # 生成表格头
    headers = list(table_rows[0].keys())
    markdown += "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    # 生成表格行
    for row in table_rows:
        row_data = []
        for header in headers:
            value = row.get(header, "")
            row_data.append(str(value))
        markdown += "| " + " | ".join(row_data) + " |\n"

    markdown += "\n"

    # 添加总体评价
    if "总体评价" in table_data:
        markdown += f"**总体评价:** {table_data['总体评价']}\n\n"

    return markdown

def format_table_data(table_rows):
    """Format table data as markdown table"""
    if not table_rows:
        return "无表格数据\n\n"

    # 生成表格头
    headers = list(table_rows[0].keys())
    markdown = "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    # 生成表格行
    for row in table_rows:
        row_data = []
        for header in headers:
            value = row.get(header, "")
            row_data.append(str(value))
        markdown += "| " + " | ".join(row_data) + " |\n"

    markdown += "\n"
    return markdown

def format_longitudinal_table(table_data):
    """Format longitudinal table data as markdown"""
    if "表格数据" in table_data:
        return format_comparison_table(table_data)

    markdown = ""

    # 处理分段数据表
    if "分段数据表" in table_data:
        title = table_data.get("表格标题", "纵向趋势分析表")
        markdown += f"**{title}**\n\n"

        table_rows = table_data["分段数据表"]
        if table_rows:
            headers = list(table_rows[0].keys())
            markdown += "| " + " | ".join(headers) + " |\n"
            markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

            for row in table_rows:
                row_data = []
                for header in headers:
                    value = row.get(header, "")
                    row_data.append(str(value))
                markdown += "| " + " | ".join(row_data) + " |\n"
            markdown += "\n"

    # 处理趋势变化表
    if "趋势变化表" in table_data:
        markdown += "**趋势变化分析表**\n\n"

        trend_rows = table_data["趋势变化表"]
        if trend_rows:
            headers = list(trend_rows[0].keys())
            markdown += "| " + " | ".join(headers) + " |\n"
            markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

            for row in trend_rows:
                row_data = []
                for header in headers:
                    value = row.get(header, "")
                    row_data.append(str(value))
                markdown += "| " + " | ".join(row_data) + " |\n"
            markdown += "\n"

    # 添加总体趋势
    if "总体趋势" in table_data:
        markdown += f"**总体趋势:** {table_data['总体趋势']}\n\n"

    return markdown

def main():
    if len(sys.argv) != 2:
        print("Usage: python json_to_markdown.py <json_file>")
        sys.exit(1)

    json_file = Path(sys.argv[1])

    if not json_file.exists():
        print(f"Error: File {json_file} not found")
        sys.exit(1)

    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to markdown
    markdown_content = "# 中山健康管理中心 CGM 血糖监测报告\n"
    markdown_content += "=" * 50 + "\n\n"

    # Add report header info
    if "报告头信息" in data:
        header = data["报告头信息"]
        markdown_content += f"**患者:** {header.get('患者ID', 'N/A')}\n\n"
        markdown_content += f"**报告类型:** {header.get('报告类型', 'N/A')}\n\n"
        markdown_content += f"**生成时间:** {header.get('分析时间', 'N/A')}\n\n"
        markdown_content += f"**监测周期:** {header.get('监测周期', 'N/A')}\n\n"
        markdown_content += f"**数据点数:** {header.get('数据点数', 'N/A')}\n\n"
        markdown_content += "---\n\n"

    # Process main content sections
    sections_order = [
        "1_基本信息",
        "2_核心控制指标",
        "3_综合评估与建议",
        "4_详细血糖分析",
        "5_控制目标",
        "6_随诊方案",
        "7_注意事项"
    ]

    for section in sections_order:
        if section in data:
            section_name = section.split('_', 1)[1] if '_' in section else section
            markdown_content += f"# {section_name}\n\n"
            markdown_content += dict_to_markdown(data[section], level=1)
            markdown_content += "\n---\n\n"

    # Output filename
    output_file = json_file.parent / f"{json_file.stem}.md"

    # Save markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Markdown report saved to: {output_file}")

    # Also print to stdout
    print("\n" + "=" * 80)
    print("MARKDOWN REPORT CONTENT:")
    print("=" * 80)
    print(markdown_content)

if __name__ == "__main__":
    main()