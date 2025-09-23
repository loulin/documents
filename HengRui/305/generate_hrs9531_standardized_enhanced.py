#!/usr/bin/env python3
"""
修改版：严格按照HRS9531-305.csv格式生成CGMS模拟数据
主要修改：
1. 补充LBORRESU字段 (mmol/L)
2. 将W-2_V2改为"导入期W-2_V2"
3. 新增20例4mg剂量的受试者数据
4. 保持原有的50例2mg剂量数据
总计：70个受试者（50个2mg + 20个4mg）
"""

import csv
import random
from datetime import datetime, timedelta

def generate_hrs9531_standardized_enhanced_data():
    # 配置参数
    target_subjects_2mg = 50  # 2mg剂量组
    target_subjects_4mg = 20  # 4mg剂量组
    total_subjects = target_subjects_2mg + target_subjects_4mg
    records_per_subject = 1396
    
    print(f"🚀 开始生成HRS9531-305增强标准格式数据...")
    print(f"👥 总受试者数量: {total_subjects}")
    print(f"💊 2mg剂量组: {target_subjects_2mg}例")
    print(f"💊 4mg剂量组: {target_subjects_4mg}例")
    print(f"📊 每个受试者记录数: {records_per_subject}")
    print(f"📈 预计总记录数: {total_subjects * records_per_subject:,}")
    
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
            "siteid": center_id,
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
            "siteid": center_id,
            "cgms": cgms_id,
            "arm": "4mg"
        })
    
    # 项目配置（根据HRS9531-305.csv格式定义）
    studyid = "HRS9531-305"
    lab_name = "上海和杰健康咨询有限公司"
    visit = "导入期W-2_V2"  # 修改访视名称
    unit = "mmol/L"  # 新增单位字段
    
    # 输出文件（UTF-8编码，带BOM，逗号分隔）
    output_file = "/Users/williamsun/Documents/gplus/docs/HengRui/HRS9531_305_standardized_simulation.csv"
    
    total_records = 0
    
    # 使用UTF-8-sig编码写入文件（包含BOM）
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        # 增加LBORRESU字段到字段列表
        fieldnames = ['STUDYID', 'SUBJID', 'ARM', 'SITEID', 'LBNAM', 'VISIT', 'LBREFID', 'LBDTC', 'LBORRES', 'LBORRESU']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # 写入表头
        writer.writeheader()
        
        for idx, subject in enumerate(subjects):
            print(f"📝 正在生成受试者 {subject['subjid']} ({subject['arm']}) 的数据... ({idx + 1}/{total_subjects})")
            
            # 为每个受试者设置不同的起始时间 (2024年不同日期)
            start_time = datetime(2024, 1, 1, 8, 0) + timedelta(days=idx * 7)  # 每个受试者间隔7天开始
            
            for i in range(records_per_subject):
                # 计算当前时间点 (每15分钟一个数据点)
                current_time = start_time + timedelta(minutes=15 * i)
                
                # 根据剂量组调整基础血糖值
                if subject['arm'] == '2mg':
                    base_value = 7.0  # 2mg组基础血糖值
                else:  # 4mg组
                    base_value = 6.5  # 4mg组血糖控制更好，基础值稍低
                
                # 添加个体差异 (基于受试者ID的稳定差异)
                individual_hash = hash(subject['subjid']) % 100
                individual_offset = (individual_hash / 100) * 2.0 - 1.0  # -1.0 到 +1.0
                base_value += individual_offset
                
                # 根据剂量组调整血糖控制效果
                if subject['arm'] == '4mg':
                    # 4mg组血糖波动更小，控制更稳定
                    base_value *= 0.95  # 整体水平稍低
                
                # 添加日间变化模式
                hour = current_time.hour
                
                # 餐后血糖模式（4mg组峰值更低）
                meal_factor = 0.8 if subject['arm'] == '4mg' else 1.0
                
                if 7 <= hour <= 10:  # 早餐后
                    if hour == 8:
                        base_value += random.uniform(2.0, 4.0) * meal_factor  # 早餐后峰值
                    else:
                        base_value += random.uniform(1.0, 2.5) * meal_factor
                elif 12 <= hour <= 15:  # 午餐后
                    if hour == 13:
                        base_value += random.uniform(1.8, 3.5) * meal_factor  # 午餐后峰值
                    else:
                        base_value += random.uniform(0.8, 2.2) * meal_factor
                elif 18 <= hour <= 21:  # 晚餐后
                    if hour == 19:
                        base_value += random.uniform(1.5, 3.2) * meal_factor  # 晚餐后峰值
                    else:
                        base_value += random.uniform(0.6, 2.0) * meal_factor
                elif 1 <= hour <= 6:  # 凌晨低值期
                    base_value -= random.uniform(0.8, 2.0) * 0.9
                elif 22 <= hour <= 24:  # 睡前下降
                    base_value -= random.uniform(0.4, 1.2) * 0.9
                
                # 添加运动影响 (8%概率)
                if random.random() < 0.08:
                    base_value -= random.uniform(1.5, 3.0)
                
                # 添加应激/疾病影响 (5%概率)
                if random.random() < 0.05:
                    base_value += random.uniform(2.0, 4.0)
                
                # 添加随机波动（4mg组波动更小）
                fluctuation_range = 1.0 if subject['arm'] == '4mg' else 1.2
                glucose_value = base_value + random.uniform(-fluctuation_range, fluctuation_range)
                
                # 确保值在3-15范围内
                glucose_value = max(3.0, min(15.0, glucose_value))
                
                # 格式化为一位小数
                glucose_value = round(glucose_value, 1)
                
                # 写入数据行（包含新增的LBORRESU字段）
                writer.writerow({
                    'STUDYID': studyid,           # 项目编号
                    'SUBJID': subject['subjid'],   # 受试者代码
                    'ARM': subject['arm'],        # 剂量组 (2mg或4mg)
                    'SITEID': subject['siteid'],   # 送检中心编号
                    'LBNAM': lab_name,           # 实验室名称
                    'VISIT': visit,              # 访视 (导入期W-2_V2)
                    'LBREFID': subject['cgms'],   # CGMS编号
                    'LBDTC': current_time.strftime('%Y-%m-%d %H:%M'),  # 实际采样日期
                    'LBORRES': str(glucose_value), # 检测结果
                    'LBORRESU': unit             # 原始单位 (mmol/L)
                })
                
                total_records += 1
    
    print(f"\n🎉 HRS9531-305增强标准格式数据生成完成！")
    print(f"📁 文件保存为: {output_file}")
    print(f"👥 生成受试者数: {total_subjects}")
    print(f"💊 2mg剂量组: {target_subjects_2mg}例")
    print(f"💊 4mg剂量组: {target_subjects_4mg}例")
    print(f"📊 总记录数: {total_records:,}")
    print(f"📅 时间间隔: 15分钟")
    print(f"🔤 编码格式: UTF-8 with BOM")
    print(f"📋 分隔符: 逗号")
    print(f"🏥 访视: {visit}")
    print(f"📊 增加字段: LBORRESU ({unit})")
    
    # 验证文件大小
    import os
    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    print(f"💾 文件大小: {file_size:.2f} MB")
    
    # 显示受试者范围
    subjects_2mg = [s for s in subjects if s['arm'] == '2mg']
    subjects_4mg = [s for s in subjects if s['arm'] == '4mg']
    
    if subjects_2mg:
        print(f"📋 2mg组受试者编号: {subjects_2mg[0]['subjid']} - {subjects_2mg[-1]['subjid']}")
        print(f"🔬 2mg组CGMS编号: {subjects_2mg[0]['cgms']} - {subjects_2mg[-1]['cgms']}")
    
    if subjects_4mg:
        print(f"📋 4mg组受试者编号: {subjects_4mg[0]['subjid']} - {subjects_4mg[-1]['subjid']}")
        print(f"🔬 4mg组CGMS编号: {subjects_4mg[0]['cgms']} - {subjects_4mg[-1]['cgms']}")
    
    print(f"🏥 实验室: {lab_name}")
    
    # 统计研究中心
    centers = sorted(set(s['siteid'] for s in subjects))
    print(f"🏥 涉及研究中心: {', '.join(centers)}")
    
    return output_file

if __name__ == "__main__":
    generate_hrs9531_standardized_enhanced_data()