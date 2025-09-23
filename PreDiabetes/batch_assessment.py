#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量糖尿病风险评估工具
支持CSV文件导入和批量处理

适用人群（基于ADA/ISPAD 2024指南）：
- 成年非妊娠期人群（18-65岁）
- 自动识别并标记不适用人群：
  * <10岁：学龄前儿童
  * 10-18岁：儿童青少年（需要专用评估体系）
  * >65岁：老年人群
  * 妊娠期女性
  * 已确诊糖尿病患者

使用方法：
1. 准备CSV文件，包含患者数据
2. python batch_assessment.py input.csv output.csv
3. 创建示例文件：python batch_assessment.py --sample

CSV文件格式要求：
age,gender,height,weight,waist_circumference,systolic_bp,diastolic_bp,fpg,hba1c,tg,hdl_c,ldl_c,family_history_t2dm,history_gdm,history_cvd,history_pcos,exercise_minutes_per_week,smoking_status,alcohol_status,sleep_hours_per_day

注意：不适用人群将在结果中标记为"适用性：否"，并提供相应的临床建议
"""

import csv
import sys
import json
import pandas as pd
from PreDiab_RiskAssessment_Script import DiabetesRiskAssessment, PatientData
from typing import List, Dict

class BatchAssessment:
    """批量评估类"""
    
    def __init__(self):
        self.assessor = DiabetesRiskAssessment()
        self.results = []
    
    def read_csv_file(self, filename: str) -> List[Dict]:
        """读取CSV文件"""
        try:
            df = pd.read_csv(filename)
            return df.to_dict('records')
        except Exception as e:
            print(f"❌ 读取CSV文件失败: {e}")
            return []
    
    def validate_patient_data(self, row: Dict) -> tuple:
        """验证患者数据"""
        required_fields = [
            'age', 'gender', 'height', 'weight', 'waist_circumference',
            'systolic_bp', 'diastolic_bp', 'fpg', 'hba1c'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in row or pd.isna(row[field]):
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"缺少必填字段: {', '.join(missing_fields)}"
        
        return True, "数据完整"
    
    def convert_to_patient_data(self, row: Dict) -> PatientData:
        """将CSV行数据转换为PatientData对象"""
        
        # 处理可选字段的默认值
        def safe_float(value, default=None):
            if pd.isna(value):
                return default
            return float(value)
        
        def safe_str(value, default=""):
            if pd.isna(value):
                return default
            return str(value)
        
        def safe_bool(value, default=False):
            if pd.isna(value):
                return default
            return str(value).lower() in ['true', '1', 'yes', '是']
        
        patient = PatientData(
            age=int(row['age']),
            gender=str(row['gender']),
            is_pregnant=safe_bool(row.get('is_pregnant', False)),
            height=float(row['height']),
            weight=float(row['weight']),
            waist_circumference=float(row['waist_circumference']),
            systolic_bp=int(row['systolic_bp']),
            diastolic_bp=int(row['diastolic_bp']),
            fpg=float(row['fpg']),
            hba1c=float(row['hba1c']),
            tg=safe_float(row.get('tg')),
            hdl_c=safe_float(row.get('hdl_c')),
            ldl_c=safe_float(row.get('ldl_c')),
            family_history_t2dm=safe_str(row.get('family_history_t2dm', '无')),
            history_gdm=safe_bool(row.get('history_gdm', False)),
            history_cvd=safe_bool(row.get('history_cvd', False)),
            history_pcos=safe_bool(row.get('history_pcos', False)),
            exercise_minutes_per_week=int(safe_float(row.get('exercise_minutes_per_week', 0))),
            smoking_status=safe_str(row.get('smoking_status', '从不吸烟')),
            alcohol_status=safe_str(row.get('alcohol_status', '不饮酒')),
            sleep_hours_per_day=safe_float(row.get('sleep_hours_per_day', 7.0))
        )
        
        return patient
    
    def process_batch(self, data: List[Dict]) -> List[Dict]:
        """批量处理患者数据"""
        results = []
        
        for i, row in enumerate(data, 1):
            print(f"处理第 {i}/{len(data)} 例患者...")
            
            try:
                # 验证数据
                is_valid, message = self.validate_patient_data(row)
                
                if not is_valid:
                    result = {
                        "患者编号": i,
                        "处理状态": "失败",
                        "错误信息": message,
                        "原始数据": row
                    }
                    results.append(result)
                    continue
                
                # 转换数据
                patient = self.convert_to_patient_data(row)
                
                # 进行评估
                report = self.assessor.generate_report(patient)
                
                # 整理结果
                result = {
                    "患者编号": i,
                    "处理状态": "成功",
                    "年龄": patient.age,
                    "性别": patient.gender,
                    "BMI": round(self.assessor.calculate_bmi(patient), 1),
                    "适用性": report["适用性"],
                    "糖尿病状态": report.get("糖尿病状态", "N/A"),
                    "代谢综合征": report.get("代谢综合征", {}).get("诊断", "N/A"),
                    "风险评分": report.get("风险评分", {}).get("总分", "N/A"),
                    "风险等级": report.get("风险评分", {}).get("风险等级", "N/A"),
                    "1年发病率": report.get("发病风险", {}).get("1年发病率", "N/A"),
                    "3年发病率": report.get("发病风险", {}).get("3年发病率", "N/A"),
                    "5年发病率": report.get("发病风险", {}).get("5年发病率", "N/A"),
                    "筛查建议": "、".join(report.get("管理建议", {}).get("筛查频率", [])),
                    "完整报告": report
                }
                
                results.append(result)
                
            except Exception as e:
                result = {
                    "患者编号": i,
                    "处理状态": "异常",
                    "错误信息": str(e),
                    "原始数据": row
                }
                results.append(result)
        
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        """保存结果到CSV文件"""
        
        # 准备CSV输出数据
        csv_data = []
        
        for result in results:
            csv_row = {
                "患者编号": result["患者编号"],
                "处理状态": result["处理状态"]
            }
            
            if result["处理状态"] == "成功":
                csv_row.update({
                    "年龄": result["年龄"],
                    "性别": result["性别"],
                    "BMI": result["BMI"],
                    "适用性": "是" if result["适用性"] else "否",
                    "糖尿病状态": result["糖尿病状态"],
                    "代谢综合征": result["代谢综合征"],
                    "风险评分": result["风险评分"],
                    "风险等级": result["风险等级"],
                    "1年发病率(%)": result["1年发病率"],
                    "3年发病率(%)": result["3年发病率"],
                    "5年发病率(%)": result["5年发病率"],
                    "筛查建议": result["筛查建议"]
                })
            else:
                csv_row["错误信息"] = result.get("错误信息", "")
            
            csv_data.append(csv_row)
        
        # 保存CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 保存详细报告(JSON)
        json_file = output_file.replace('.csv', '_detailed.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 结果已保存到: {output_file}")
        print(f"📄 详细报告已保存到: {json_file}")
    
    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """生成汇总报告"""
        total_patients = len(results)
        successful_assessments = sum(1 for r in results if r["处理状态"] == "成功")
        failed_assessments = total_patients - successful_assessments
        
        # 统计成功评估的结果
        successful_results = [r for r in results if r["处理状态"] == "成功" and r["适用性"]]
        
        risk_level_stats = {}
        diabetes_status_stats = {}
        metabolic_syndrome_stats = {}
        
        for result in successful_results:
            # 风险等级统计
            risk_level = result["风险等级"]
            risk_level_stats[risk_level] = risk_level_stats.get(risk_level, 0) + 1
            
            # 糖尿病状态统计
            diabetes_status = result["糖尿病状态"]
            diabetes_status_stats[diabetes_status] = diabetes_status_stats.get(diabetes_status, 0) + 1
            
            # 代谢综合征统计
            ms_status = result["代谢综合征"]
            metabolic_syndrome_stats[ms_status] = metabolic_syndrome_stats.get(ms_status, 0) + 1
        
        summary = {
            "评估总览": {
                "总患者数": total_patients,
                "成功评估数": successful_assessments,
                "失败评估数": failed_assessments,
                "成功率": f"{successful_assessments/total_patients*100:.1f}%" if total_patients > 0 else "0%"
            },
            "风险等级分布": risk_level_stats,
            "糖尿病状态分布": diabetes_status_stats,
            "代谢综合征分布": metabolic_syndrome_stats,
            "高风险患者统计": {
                "高风险+极高风险人数": sum(risk_level_stats.get(level, 0) for level in ["高风险", "极高风险"]),
                "糖尿病前期人数": diabetes_status_stats.get("糖尿病前期", 0),
                "代谢综合征人数": metabolic_syndrome_stats.get("是", 0)
            }
        }
        
        return summary

def create_sample_csv():
    """创建示例CSV文件"""
    sample_data = [
        {
            "age": 35, "gender": "男", "height": 175, "weight": 70, "waist_circumference": 85,
            "systolic_bp": 120, "diastolic_bp": 80, "fpg": 5.2, "hba1c": 5.4,
            "tg": 1.2, "hdl_c": 1.2, "family_history_t2dm": "无",
            "exercise_minutes_per_week": 180, "smoking_status": "从不吸烟"
        },
        {
            "age": 45, "gender": "女", "height": 165, "weight": 75, "waist_circumference": 90,
            "systolic_bp": 135, "diastolic_bp": 85, "fpg": 6.1, "hba1c": 5.9,
            "tg": 2.1, "hdl_c": 1.0, "family_history_t2dm": "一级亲属",
            "exercise_minutes_per_week": 60, "smoking_status": "现在吸烟"
        },
        {
            "age": 55, "gender": "男", "height": 170, "weight": 85, "waist_circumference": 98,
            "systolic_bp": 145, "diastolic_bp": 92, "fpg": 6.5, "hba1c": 6.2,
            "tg": 2.8, "hdl_c": 0.9, "family_history_t2dm": "一级亲属",
            "history_cvd": True, "exercise_minutes_per_week": 30, "smoking_status": "既往吸烟"
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv("sample_patients.csv", index=False)
    print("✅ 示例文件已创建: sample_patients.csv")

def main():
    """主程序"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  批量评估: python batch_assessment.py input.csv [output.csv]")
        print("  创建示例: python batch_assessment.py --sample")
        return
    
    if sys.argv[1] == "--sample":
        create_sample_csv()
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "assessment_results.csv"
    
    print("="*60)
    print("批量糖尿病风险评估工具")
    print("="*60)
    
    # 创建批量评估实例
    batch_processor = BatchAssessment()
    
    # 读取输入文件
    print(f"📁 读取输入文件: {input_file}")
    data = batch_processor.read_csv_file(input_file)
    
    if not data:
        print("❌ 无法读取数据或文件为空")
        return
    
    print(f"📊 共读取 {len(data)} 例患者数据")
    
    # 批量处理
    print("\n🔄 开始批量评估...")
    results = batch_processor.process_batch(data)
    
    # 保存结果
    print(f"\n💾 保存结果到: {output_file}")
    batch_processor.save_results(results, output_file)
    
    # 生成汇总报告
    summary = batch_processor.generate_summary_report(results)
    
    print("\n" + "="*60)
    print("批量评估汇总报告")
    print("="*60)
    
    print(f"\n【评估总览】")
    for key, value in summary["评估总览"].items():
        print(f"{key}: {value}")
    
    print(f"\n【风险等级分布】")
    for level, count in summary["风险等级分布"].items():
        print(f"{level}: {count}例")
    
    print(f"\n【糖尿病状态分布】")
    for status, count in summary["糖尿病状态分布"].items():
        print(f"{status}: {count}例")
    
    print(f"\n【代谢综合征分布】")
    for status, count in summary["代谢综合征分布"].items():
        print(f"代谢综合征{status}: {count}例")
    
    print(f"\n【重点关注人群】")
    high_risk_stats = summary["高风险患者统计"]
    for key, value in high_risk_stats.items():
        print(f"{key}: {value}例")
    
    print("\n" + "="*60)
    print("✅ 批量评估完成")

if __name__ == "__main__":
    main()