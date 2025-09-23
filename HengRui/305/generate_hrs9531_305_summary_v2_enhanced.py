#!/usr/bin/env python3
"""
修改版：严格按照HRS9531-305-2.csv格式生成血糖分析汇总统计数据
主要修改：
1. 将VISIT从"W-2_V2"改为"导入期W-2_V2"
2. 新增20例4mg剂量的受试者统计数据
3. 保持原有的50例2mg剂量数据
总计：70个受试者（50个2mg + 20个4mg）
"""

import csv
import random
from datetime import datetime, timedelta

def generate_hrs9531_305_summary_v2_enhanced():
    # 配置参数
    target_subjects_2mg = 50  # 2mg剂量组
    target_subjects_4mg = 20  # 4mg剂量组
    total_subjects = target_subjects_2mg + target_subjects_4mg
    
    print(f"🚀 开始生成HRS9531-305-2增强血糖分析汇总数据...")
    print(f"👥 总受试者数量: {total_subjects}")
    print(f"💊 2mg剂量组: {target_subjects_2mg}例")
    print(f"💊 4mg剂量组: {target_subjects_4mg}例")
    
    # 生成受试者列表
    subjects = []
    
    # 生成50个2mg受试者 (CN001001-CN001050)
    for i in range(target_subjects_2mg):
        center_id = f"CN{(i // 100 + 1):03d}"
        subject_num = f"{(i % 100 + 1):03d}"
        subjid = f"{center_id}{subject_num}"
        cgms_id = f"1MH00M4{(i + 1):04d}"
        
        subjects.append({
            "subjid": subjid,
            "cgms": cgms_id,
            "arm": "2mg"
        })
    
    # 生成20个4mg受试者 (CN001051-CN001070)
    for i in range(target_subjects_4mg):
        idx = target_subjects_2mg + i  # 从51开始
        center_id = f"CN{(idx // 100 + 1):03d}"
        subject_num = f"{(idx % 100 + 1):03d}"
        subjid = f"{center_id}{subject_num}"
        cgms_id = f"1MH00M4{(idx + 1):04d}"
        
        subjects.append({
            "subjid": subjid,
            "cgms": cgms_id,
            "arm": "4mg"
        })
    
    # 输出文件（UTF-8编码，带BOM，逗号分隔）
    output_file = "/Users/williamsun/Documents/gplus/docs/HengRui/HRS9531_305_summary_v2.csv"
    
    # 使用UTF-8-sig编码写入文件（包含BOM）
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        # 严格按照HRS9531-305-2.csv中定义的字段顺序（85个字段）
        fieldnames = [
            'SUBJID', 'ARM', 'VISIT', 'CONTARGET', 'LBREFID', 'STDTC', 'ENDTC', 
            'DAYNUM', 'MEASQUANTITY', 'VDATA', 'MEABG', 'Median', 'eHbA1c(%)', 
            'eHbA1c(mmol/mol)', 'CV', 'SD', 'MAGE', 'MODD', 'LAGE', 'BGRI', 
            'LBGI', 'HBGI', 'Min', 'Max', 'JIndex', 'ADRR', 'MValue', 
            'GMI(mmol/mol)', 'GMI(%)', 'IQR', 'MEDIAN10%', 'MEDIAN25%', 
            'MEDIAN50%', 'MEDIAN75%', 'MEDIAN90%', 'CONGA', 'CONGA2', 
            'CONGA3', 'CONGA4', 'CONGA6', 'CONGA12', 'gAUC(<3.9)', 
            'gAUC(3.9~10)', 'gAUC(>10)', 'tAUC(<3.9)', 'tAUC(3.9~10)', 
            'tAUC(>10)', '<2.8(min)', '<2.8(%)', '<3(min)', '<3(%)', 
            '≥3~<3.9(min)', '≥3~<3.9(%)', '<3.9(min)', '<3.9(%)', 
            '≥3.9~≤10(min)', '≥3.9~≤10(%)', '>10(min)', '>10(%)', 
            '>10~≤13.9(min)', '>10~≤13.9(%)', '>13.9(min)', '>13.9(%)', 
            '>10~<16.7(min)', '>10~<16.7(%)', '>13.9~<16.7(min)', 
            '>13.9~<16.7(%)', '≥16.7(min)', '≥16.7(%)', '≥3~<3.9LBGNUM', 
            '≥3~<3.9NINUM', '≥3~<3.9AVERDUR(min)', '<3LBGNUM', '<3NINUM', 
            '<3AVERDUR (min)', '<3.9LBGNUM', '<3.9NINUM', '<3.9AVERDUR (min)', 
            '<3.5LBGNUM', '<3.5NINUM', '<3.5AVERDUR (min)', '<2.8LBGNUM', 
            '<2.8NINUM', '<2.8AVERDUR (min)', 'GRI'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # 写入表头
        writer.writeheader()
        
        for idx, subject in enumerate(subjects):
            print(f"📝 正在生成受试者 {subject['subjid']} ({subject['arm']}) 的统计数据... ({idx + 1}/{total_subjects})")
            
            # 设置基准日期（每个受试者间隔7天开始）
            base_date = datetime(2024, 1, 1) + timedelta(days=idx * 7)
            start_time = base_date
            end_time = base_date + timedelta(days=14)  # 14天间隔
            
            # 根据剂量组调整血糖统计指标
            if subject['arm'] == '2mg':
                # 2mg组血糖控制指标（原有逻辑）
                mean_bg = round(random.uniform(6.5, 8.5), 1)
                median_bg = round(random.uniform(6.0, 8.0), 1)
                ehba1c_percent = round(random.uniform(6.5, 8.0), 1)
                cv = round(random.uniform(20, 35), 1)
                tir_percent = round(random.uniform(65, 85), 1)
                tbr_percent = round(random.uniform(2, 8), 1)
                gri = round(random.uniform(25, 65), 1)
            else:  # 4mg组
                # 4mg组血糖控制更好
                mean_bg = round(random.uniform(6.0, 7.8), 1)  # 平均血糖更低
                median_bg = round(random.uniform(5.8, 7.5), 1)  # 中位值更低
                ehba1c_percent = round(random.uniform(6.0, 7.5), 1)  # 糖化血红蛋白更低
                cv = round(random.uniform(18, 30), 1)  # 变异性更小
                tir_percent = round(random.uniform(75, 90), 1)  # TIR更高
                tbr_percent = round(random.uniform(1, 5), 1)  # TBR更少
                gri = round(random.uniform(20, 55), 1)  # 血糖风险指数更低
            
            # 计算糖化血红蛋白mmol/mol
            ehba1c_mmol = round((ehba1c_percent - 2.15) * 10.93, 1)
            
            # 变异性指标（4mg组更稳定）
            dose_factor = 0.8 if subject['arm'] == '4mg' else 1.0
            sd = round(random.uniform(1.5, 3.0) * dose_factor, 2)
            mage = round(random.uniform(3.0, 6.0) * dose_factor, 2)
            modd = round(random.uniform(1.5, 3.5) * dose_factor, 2)
            
            # 时间范围指标（分钟和百分比）
            total_minutes = 14 * 24 * 60  # 14天总分钟数
            
            # TIR (Time in Range) - 目标范围内时间
            tir_minutes = int(total_minutes * tir_percent / 100)
            
            # TBR (Time Below Range) - 低血糖时间
            tbr_minutes = int(total_minutes * tbr_percent / 100)
            
            # TAR (Time Above Range) - 高血糖时间
            tar_percent = round(100 - tir_percent - tbr_percent, 1)
            tar_minutes = int(total_minutes * tar_percent / 100)
            
            # 写入数据行（严格按照85个字段的顺序）
            writer.writerow({
                'SUBJID': subject['subjid'],
                'ARM': subject['arm'],  # 剂量组 (2mg或4mg)
                'VISIT': '导入期W-2_V2',  # 修改后的访视名称
                'CONTARGET': '3.9~10',  # 控制目标
                'LBREFID': subject['cgms'],  # CGMS编号
                'STDTC': start_time.strftime('%Y-%m-%d %H:%M'),  # 计算开始时间
                'ENDTC': end_time.strftime('%Y-%m-%d %H:%M'),    # 计算结束时间
                'DAYNUM': '14',  # 计算天数
                'MEASQUANTITY': '1396',  # 采用测量数量
                'VDATA': '100%',  # 有效数据
                'MEABG': str(mean_bg),  # 平均血糖
                'Median': str(median_bg),  # 中位值
                'eHbA1c(%)': str(ehba1c_percent),  # 计算糖化%
                'eHbA1c(mmol/mol)': str(ehba1c_mmol),  # 计算糖化mmol/mol
                'CV': str(cv),  # 变异度
                'SD': str(sd),  # 标准误差
                'MAGE': str(mage),  # 平均日内波动
                'MODD': str(modd),  # 平均日间波动
                'LAGE': str(round(random.uniform(8, 15) * dose_factor, 1)),  # 极差
                'BGRI': str(round(random.uniform(3, 8) * dose_factor, 2)),  # 血糖风险指数
                'LBGI': str(round(random.uniform(1, 4) * dose_factor, 2)),  # 低血糖风险指数
                'HBGI': str(round(random.uniform(2, 6) * dose_factor, 2)),  # 高血糖风险指数
                'Min': str(round(random.uniform(3.5, 5.0), 1)),  # 最小值
                'Max': str(round(random.uniform(12, 16) * (0.9 if subject['arm'] == '4mg' else 1.0), 1)),  # 最大值
                'JIndex': str(round(random.uniform(25, 45) * dose_factor, 1)),  # J指数
                'ADRR': str(round(random.uniform(15, 35) * dose_factor, 2)),  # 每日
                'MValue': str(round(random.uniform(8, 25) * dose_factor, 2)),  # M值
                'GMI(mmol/mol)': str(round(random.uniform(48, 64) * (0.9 if subject['arm'] == '4mg' else 1.0), 1)),  # 血糖管理系数
                'GMI(%)': str(round(random.uniform(6.5, 8.0) * (0.95 if subject['arm'] == '4mg' else 1.0), 1)),  # 血糖管理系数%
                'IQR': str(round(random.uniform(2, 4) * dose_factor, 2)),  # 四分差
                'MEDIAN10%': str(round(random.uniform(4.5, 5.5), 1)),  # 中位值10%
                'MEDIAN25%': str(round(random.uniform(5.5, 6.5), 1)),  # 中位值25%
                'MEDIAN50%': str(median_bg),  # 中位值50%
                'MEDIAN75%': str(round(random.uniform(7.5, 8.5) * (0.95 if subject['arm'] == '4mg' else 1.0), 1)),  # 中位值75%
                'MEDIAN90%': str(round(random.uniform(9, 11) * (0.9 if subject['arm'] == '4mg' else 1.0), 1)),  # 中位值90%
                'CONGA': str(round(random.uniform(1.5, 3.5) * dose_factor, 2)),  # CONGA
                'CONGA2': str(round(random.uniform(1.8, 4.0) * dose_factor, 2)),  # CONGA2
                'CONGA3': str(round(random.uniform(2.0, 4.5) * dose_factor, 2)),  # CONGA3
                'CONGA4': str(round(random.uniform(2.2, 5.0) * dose_factor, 2)),  # CONGA4
                'CONGA6': str(round(random.uniform(2.5, 5.5) * dose_factor, 2)),  # CONGA6
                'CONGA12': str(round(random.uniform(3.0, 6.0) * dose_factor, 2)),  # CONGA12
                'gAUC(<3.9)': str(round(random.uniform(0, 50) * (0.7 if subject['arm'] == '4mg' else 1.0), 1)),  # 血糖曲线下面积<3.9
                'gAUC(3.9~10)': str(round(random.uniform(800, 1200), 1)),  # 血糖曲线下面积3.9~10
                'gAUC(>10)': str(round(random.uniform(50, 200) * (0.8 if subject['arm'] == '4mg' else 1.0), 1)),  # 血糖曲线下面积>10
                'tAUC(<3.9)': str(round(random.uniform(0, 100) * (0.7 if subject['arm'] == '4mg' else 1.0), 1)),  # 血糖曲线下面积<3.9
                'tAUC(3.9~10)': str(round(random.uniform(15000, 18000), 1)),  # 血糖曲线下面积3.9~10
                'tAUC(>10)': str(round(random.uniform(500, 2000) * (0.8 if subject['arm'] == '4mg' else 1.0), 1)),  # 血糖曲线下面积>10
                '<2.8(min)': str(int(random.uniform(0, 50) * (0.6 if subject['arm'] == '4mg' else 1.0))),  # TBR <2.8分钟
                '<2.8(%)': str(round(random.uniform(0, 3) * (0.6 if subject['arm'] == '4mg' else 1.0), 1)),  # TBR <2.8百分比
                '<3(min)': str(int(random.uniform(10, 100) * (0.7 if subject['arm'] == '4mg' else 1.0))),  # TBR <3分钟
                '<3(%)': str(round(random.uniform(1, 5) * (0.7 if subject['arm'] == '4mg' else 1.0), 1)),  # TBR <3百分比
                '≥3~<3.9(min)': str(int(random.uniform(50, 150) * (0.8 if subject['arm'] == '4mg' else 1.0))),  # TBR ≥3~<3.9分钟
                '≥3~<3.9(%)': str(round(random.uniform(2, 8) * (0.8 if subject['arm'] == '4mg' else 1.0), 1)),  # TBR ≥3~<3.9百分比
                '<3.9(min)': str(tbr_minutes),  # TBR <3.9分钟
                '<3.9(%)': str(tbr_percent),  # TBR <3.9百分比
                '≥3.9~≤10(min)': str(tir_minutes),  # TIR ≥3.9~≤10分钟
                '≥3.9~≤10(%)': str(tir_percent),  # TIR ≥3.9~≤10百分比
                '>10(min)': str(tar_minutes),  # TAR >10分钟
                '>10(%)': str(tar_percent),  # TAR >10百分比
                '>10~≤13.9(min)': str(int(tar_minutes * 0.7)),  # TAR >10~≤13.9分钟
                '>10~≤13.9(%)': str(round(tar_percent * 0.7, 1)),  # TAR >10~≤13.9百分比
                '>13.9(min)': str(int(tar_minutes * 0.3)),  # TAR >13.9分钟
                '>13.9(%)': str(round(tar_percent * 0.3, 1)),  # TAR >13.9百分比
                '>10~<16.7(min)': str(int(tar_minutes * 0.9)),  # TAR >10~<16.7分钟
                '>10~<16.7(%)': str(round(tar_percent * 0.9, 1)),  # TAR >10~<16.7百分比
                '>13.9~<16.7(min)': str(int(tar_minutes * 0.2)),  # TAR >13.9~<16.7分钟
                '>13.9~<16.7(%)': str(round(tar_percent * 0.2, 1)),  # TAR >13.9~<16.7百分比
                '≥16.7(min)': str(int(tar_minutes * 0.1)),  # TAR ≥16.7分钟
                '≥16.7(%)': str(round(tar_percent * 0.1, 1)),  # TAR ≥16.7百分比
                '≥3~<3.9LBGNUM': str(int(random.uniform(2, 8) * (0.8 if subject['arm'] == '4mg' else 1.0))),  # ≥3~<3.9低血糖次数
                '≥3~<3.9NINUM': str(int(random.uniform(0, 3) * (0.7 if subject['arm'] == '4mg' else 1.0))),  # ≥3~<3.9夜间次数
                '≥3~<3.9AVERDUR(min)': str(int(random.uniform(15, 45))),  # ≥3~<3.9平均持续时间
                '<3LBGNUM': str(int(random.uniform(0, 5) * (0.6 if subject['arm'] == '4mg' else 1.0))),  # <3低血糖次数
                '<3NINUM': str(int(random.uniform(0, 2) * (0.5 if subject['arm'] == '4mg' else 1.0))),  # <3夜间次数
                '<3AVERDUR (min)': str(int(random.uniform(10, 30))),  # <3平均持续时间
                '<3.9LBGNUM': str(int(random.uniform(3, 12) * (0.8 if subject['arm'] == '4mg' else 1.0))),  # <3.9低血糖次数
                '<3.9NINUM': str(int(random.uniform(1, 5) * (0.7 if subject['arm'] == '4mg' else 1.0))),  # <3.9夜间次数
                '<3.9AVERDUR (min)': str(int(random.uniform(20, 60))),  # <3.9平均持续时间
                '<3.5LBGNUM': str(int(random.uniform(1, 8) * (0.7 if subject['arm'] == '4mg' else 1.0))),  # <3.5低血糖次数
                '<3.5NINUM': str(int(random.uniform(0, 3) * (0.6 if subject['arm'] == '4mg' else 1.0))),  # <3.5夜间次数
                '<3.5AVERDUR (min)': str(int(random.uniform(15, 40))),  # <3.5平均持续时间
                '<2.8LBGNUM': str(int(random.uniform(0, 3) * (0.5 if subject['arm'] == '4mg' else 1.0))),  # <2.8低血糖次数
                '<2.8NINUM': str(int(random.uniform(0, 1) * (0.4 if subject['arm'] == '4mg' else 1.0))),  # <2.8夜间次数
                '<2.8AVERDUR (min)': str(int(random.uniform(5, 20))),  # <2.8平均持续时间
                'GRI': str(gri)  # 血糖风险指数
            })
    
    print(f"\n🎉 HRS9531-305-2增强血糖分析汇总数据生成完成！")
    print(f"📁 文件保存为: {output_file}")
    print(f"👥 生成受试者数: {total_subjects}")
    print(f"💊 2mg剂量组: {target_subjects_2mg}例")
    print(f"💊 4mg剂量组: {target_subjects_4mg}例")
    print(f"📊 字段数量: 85个")
    print(f"🔤 编码格式: UTF-8 with BOM")
    print(f"📋 分隔符: 逗号")
    print(f"🏥 访视: 导入期W-2_V2 (已更新)")
    
    # 验证文件大小
    import os
    file_size = os.path.getsize(output_file) / 1024  # KB
    print(f"💾 文件大小: {file_size:.2f} KB")
    
    # 显示受试者范围
    subjects_2mg = [s for s in subjects if s['arm'] == '2mg']
    subjects_4mg = [s for s in subjects if s['arm'] == '4mg']
    
    if subjects_2mg:
        print(f"📋 2mg组受试者编号: {subjects_2mg[0]['subjid']} - {subjects_2mg[-1]['subjid']}")
        print(f"🔬 2mg组CGMS编号: {subjects_2mg[0]['cgms']} - {subjects_2mg[-1]['cgms']}")
    
    if subjects_4mg:
        print(f"📋 4mg组受试者编号: {subjects_4mg[0]['subjid']} - {subjects_4mg[-1]['subjid']}")
        print(f"🔬 4mg组CGMS编号: {subjects_4mg[0]['cgms']} - {subjects_4mg[-1]['cgms']}")
    
    print(f"🎯 控制目标: 3.9~10 (统一)")
    print(f"📅 计算天数: 14天 (统一)")
    print(f"📊 测量数量: 1396 (统一)")
    print(f"✅ 有效数据: 100% (统一)")
    
    return output_file

if __name__ == "__main__":
    generate_hrs9531_305_summary_v2_enhanced()