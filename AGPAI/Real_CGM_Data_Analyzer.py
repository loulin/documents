#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实CGM数据分析器
专门处理质肽生物CGM数据格式并进行完整的AGP分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from CGM_AGP_Analyzer_Agent import AGPVisualAnalyzer, AGPIntelligentReporter
from CGM_Data_Quality_Assessor import CGMDataQualityAssessor

class RealCGMDataProcessor:
    """真实CGM数据处理器"""
    
    def __init__(self):
        self.quality_assessor = CGMDataQualityAssessor()
        self.analyzer = AGPVisualAnalyzer(enable_quality_check=True)
        self.reporter = AGPIntelligentReporter()
    
    def read_real_cgm_file(self, file_path: str) -> pd.DataFrame:
        """
        读取真实的CGM数据文件
        
        格式: ID\t时间\t记录类型\t葡萄糖历史记录（mmol/L）
        """
        print(f"📁 正在读取CGM数据文件: {file_path}")
        
        try:
            # 读取文件，跳过前几行的标题
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 找到数据开始行（跳过标题和注释）
            data_start = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('ID\t时间\t记录类型'):
                    data_start = i + 1
                    break
            
            # 解析数据
            data_rows = []
            for line in lines[data_start:]:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 4:
                    try:
                        record_id = parts[0]
                        timestamp_str = parts[1]
                        record_type = parts[2]
                        glucose_value = float(parts[3])
                        
                        # 转换时间格式
                        timestamp = pd.to_datetime(timestamp_str, format='%Y/%m/%d %H:%M')
                        
                        data_rows.append({
                            'timestamp': timestamp,
                            'glucose': glucose_value,
                            'record_id': record_id,
                            'record_type': record_type,
                            'device_info': 'Real_CGM_Device'
                        })
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ 跳过无效行: {line} (错误: {e})")
                        continue
            
            if not data_rows:
                raise ValueError("未找到有效的CGM数据")
            
            # 创建DataFrame
            cgm_data = pd.DataFrame(data_rows)
            cgm_data = cgm_data.sort_values('timestamp').reset_index(drop=True)
            
            print(f"✅ 成功读取 {len(cgm_data)} 个数据点")
            print(f"📅 时间范围: {cgm_data['timestamp'].min()} 到 {cgm_data['timestamp'].max()}")
            print(f"🩸 血糖范围: {cgm_data['glucose'].min():.1f} - {cgm_data['glucose'].max():.1f} mmol/L")
            
            # 数据时间跨度
            time_span = (cgm_data['timestamp'].max() - cgm_data['timestamp'].min()).days
            print(f"⏱️ 数据时间跨度: {time_span} 天")
            
            return cgm_data
            
        except Exception as e:
            print(f"❌ 读取文件失败: {str(e)}")
            raise
    
    def analyze_real_cgm_data(self, file_path: str, patient_name: str = "患者R006") -> Dict:
        """
        完整分析真实CGM数据
        
        Args:
            file_path: CGM数据文件路径
            patient_name: 患者名称
            
        Returns:
            完整的分析报告
        """
        print("🔬 开始分析真实CGM数据\n")
        
        # 1. 读取数据
        cgm_data = self.read_real_cgm_file(file_path)
        
        # 2. 数据预处理检查
        print(f"\n📊 数据概览:")
        print(f"   数据点总数: {len(cgm_data)}")
        print(f"   数据密度: 每小时约 {len(cgm_data) / ((cgm_data['timestamp'].max() - cgm_data['timestamp'].min()).total_seconds() / 3600):.1f} 个点")
        
        # 检查数据间隔
        time_diffs = cgm_data['timestamp'].diff().dt.total_seconds() / 60  # 转换为分钟
        median_interval = time_diffs.median()
        print(f"   数据间隔: 中位数 {median_interval:.1f} 分钟")
        
        # 3. AGP分析
        print(f"\n🔍 开始AGP视觉分析...")
        
        # 计算分析天数
        time_span_days = (cgm_data['timestamp'].max() - cgm_data['timestamp'].min()).days
        analysis_days = min(time_span_days, 14)  # 最多分析14天
        
        # 进行分析
        analysis_results = self.analyzer.analyze_cgm_data(cgm_data, analysis_days=analysis_days)
        
        if 'error' in analysis_results:
            print("❌ AGP分析失败")
            print(f"错误原因: {analysis_results.get('message', 'Unknown error')}")
            
            # 如果是数据质量问题，显示质量报告
            if 'quality_assessment' in analysis_results:
                quality_report = self.quality_assessor.generate_quality_report(analysis_results['quality_assessment'])
                print("\n" + quality_report)
            
            return analysis_results
        
        print("✅ AGP分析完成")
        
        # 4. 生成智能报告
        print(f"\n📝 生成智能医学报告...")
        
        patient_info = {
            'name': patient_name,
            'age': 45,  # 示例年龄
            'gender': '未知',
            'diabetes_type': '待确定',
            'diabetes_duration': '未知',
            'cgm_device': 'Real CGM Device',
            'data_source': file_path.split('/')[-1]
        }
        
        intelligent_report = self.reporter.generate_intelligent_report(analysis_results, patient_info)
        
        # 5. 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存完整报告
        report_file = f"/Users/williamsun/Documents/gplus/docs/AGPAI/Real_CGM_Analysis_Report_{patient_name}_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(intelligent_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 完整报告已保存: {report_file}")
        
        # 6. 显示关键结果
        self._display_key_results(intelligent_report)
        
        return intelligent_report
    
    def _display_key_results(self, report: Dict):
        """显示关键分析结果"""
        print(f"\n" + "="*60)
        print(f"📋 真实CGM数据AGP分析报告")
        print(f"="*60)
        
        # 整体评估
        overall = report.get('overall_assessment', {})
        print(f"🎯 整体评估: {overall.get('level', 'Unknown')} ({overall.get('overall_score', 0):.1f}分)")
        print(f"📊 数据质量: {overall.get('data_quality', 'Unknown')}")
        print(f"📝 评估说明: {overall.get('description', 'No description')}")
        
        # 主要发现
        key_findings = report.get('key_findings', [])
        if key_findings:
            print(f"\n🔍 主要发现:")
            for finding in key_findings:
                severity_icon = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}.get(finding.get('severity', 'mild'), "⚪")
                print(f"   {severity_icon} {finding.get('description', 'No description')}")
                print(f"      临床意义: {finding.get('clinical_significance', 'No significance')}")
        
        # 风险警报
        risk_alerts = report.get('risk_alerts', [])
        if risk_alerts:
            print(f"\n⚠️ 风险警报:")
            for alert in risk_alerts:
                urgency_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(alert.get('urgency', 'low'), "⚪")
                print(f"   {urgency_icon} {alert.get('message', 'No message')}")
                print(f"      建议措施: {alert.get('action_required', 'No action')}")
        
        # 临床建议
        recommendations = report.get('clinical_recommendations', [])
        if recommendations:
            print(f"\n💡 临床建议:")
            for rec in recommendations[:3]:  # 只显示前3个建议
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get('priority', 'low'), "⚪")
                print(f"   {priority_icon} [{rec.get('category', 'general')}] {rec.get('recommendation', 'No recommendation')}")
                print(f"      理由: {rec.get('rationale', 'No rationale')}")
        
        # 关键技术指标
        technical = report.get('technical_metrics', {})
        if technical:
            print(f"\n📈 关键技术指标:")
            print(f"   TIR覆盖率: {technical.get('target_range_coverage', 0):.1f}%")
            print(f"   曲线平滑度: {technical.get('median_curve_smoothness', 0):.3f}")
            print(f"   黎明现象斜率: {technical.get('dawn_curve_slope', 0):.3f}")
            print(f"   夜间稳定性: {technical.get('nocturnal_curve_flatness', 0):.3f}")
        
        print(f"\n" + "="*60)

def main():
    """主函数 - 分析真实CGM数据"""
    
    # 真实CGM数据文件路径
    file_path = "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT-002最终版/40mg-v11-CGM导出原始数据-20240621/R006.txt"
    
    try:
        # 创建分析器
        processor = RealCGMDataProcessor()
        
        # 进行完整分析
        results = processor.analyze_real_cgm_data(file_path, patient_name="R006")
        
        if 'error' not in results:
            print(f"\n🎉 真实CGM数据分析完成！")
            print(f"📊 系统成功识别了血糖模式并生成了专业的临床分析报告")
        else:
            print(f"\n⚠️ 分析过程中遇到问题，请检查数据质量")
            
    except Exception as e:
        print(f"\n💥 分析过程发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()