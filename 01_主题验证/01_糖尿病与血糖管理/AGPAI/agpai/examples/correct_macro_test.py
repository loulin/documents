#!/usr/bin/env python3
import sys
sys.path.append('/Users/williamsun/Documents/gplus/docs/AGPAI/agpai/examples')

# 直接调用完整的分析系统，但只提取宏观分段部分
import subprocess
import json
import os

def run_correct_macro_analysis():
    print("正在运行正确的宏观趋势分段算法...")
    print("(使用Agent2完整系统的宏观分段功能)")
    
    # 使用命令行参数运行完整分析，但指定macro模式
    cmd = [
        'python', 'Agent2_Intelligent_Analysis.py',
        '/Users/williamsun/Documents/gplus/docs/AGPAI/demodata/某科室/吴四毛-103782-1MH00V9XRF4.xlsx',
        '吴四毛-正确宏观分段',
        'macro'
    ]
    
    try:
        # 设置较长的超时时间
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding='utf-8')
        
        if result.returncode == 0:
            print("宏观分段分析完成！")
            print("输出:", result.stdout[-500:])  # 显示最后500个字符
        else:
            print("分析过程中出现错误:")
            print("错误输出:", result.stderr[-500:])
            
    except subprocess.TimeoutExpired:
        print("分析超时，但可能已生成部分结果")
    except Exception as e:
        print(f"运行错误: {e}")
    
    # 检查是否生成了结果文件
    import glob
    pattern = "Agent2_Intelligent_Analysis_吴四毛-正确宏观分段*.json"
    files = glob.glob(pattern)
    
    if files:
        latest_file = max(files, key=os.path.getctime)
        print(f"\n找到分析结果文件: {latest_file}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 提取宏观分段结果
            if '智能时间分段纵向脆性分析' in data:
                segment_analysis = data['智能时间分段纵向脆性分析']
                if '宏观趋势分段结果' in segment_analysis:
                    macro_result = segment_analysis['宏观趋势分段结果']
                    
                    print("\n" + "="*60)
                    print("🏢 吴四毛-103782 正确宏观趋势分段结果")  
                    print("="*60)
                    
                    segment_info = macro_result.get('分段结果', {})
                    print(f"分段数量: {segment_info.get('分段数量', 'N/A')}")
                    
                    if '段落详情' in segment_info:
                        for segment in segment_info['段落详情']:
                            print(f"\n【第{segment['段落编号']}段】")
                            print(f"  时间范围: {segment['开始时间']} - {segment['结束时间']}")
                            print(f"  持续时间: {segment['持续时间']}")
                    
                    return macro_result
        except Exception as e:
            print(f"读取结果文件时出错: {e}")
    else:
        print("未找到分析结果文件")
    
    return None

if __name__ == "__main__":
    run_correct_macro_analysis()