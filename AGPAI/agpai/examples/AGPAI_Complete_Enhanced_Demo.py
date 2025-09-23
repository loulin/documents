#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGPAI完整增强演示
展示集成智能标注功能后的完整AGP分析流程
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional

# 导入新增的增强模块
from Enhanced_AGP_Visualizer_With_Annotations import EnhancedAGPVisualizer, AGPAnnotationEngine
from Clinical_Interpretation_Templates import ClinicalInterpretationTemplates, PatternType

# 模拟原有的简化分析器
class SimplifiedAGPAnalyzer:
    """简化版AGP分析器 - 模拟原有功能"""
    
    def analyze_cgm_data(self, cgm_data: pd.DataFrame, analysis_days: int = 14) -> Dict:
        """执行AGP分析"""
        
        # 基础统计
        glucose_values = cgm_data['glucose'].values
        
        results = {
            'mean_glucose': np.mean(glucose_values),
            'std_glucose': np.std(glucose_values),
            'cv_glucose': (np.std(glucose_values) / np.mean(glucose_values)) * 100,
            'min_glucose': np.min(glucose_values),
            'max_glucose': np.max(glucose_values)
        }
        
        # TIR/TAR/TBR计算
        tir_count = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0))
        tbr_count = np.sum(glucose_values < 3.9)
        tar_count = np.sum(glucose_values > 10.0)
        total_count = len(glucose_values)
        
        results.update({
            'tir_percentage': (tir_count / total_count) * 100,
            'tbr_percentage': (tbr_count / total_count) * 100,
            'tar_percentage': (tar_count / total_count) * 100
        })
        
        # AGP曲线分析
        cgm_data_copy = cgm_data.copy()
        cgm_data_copy['hour'] = cgm_data_copy['timestamp'].dt.hour + cgm_data_copy['timestamp'].dt.minute / 60.0
        
        # 黎明现象分析
        dawn_data = cgm_data_copy[(cgm_data_copy['hour'] >= 4) & (cgm_data_copy['hour'] <= 8)]
        if len(dawn_data) > 1:
            dawn_slope = np.polyfit(dawn_data['hour'], dawn_data['glucose'], 1)[0]
            results['dawn_curve_slope'] = dawn_slope
        else:
            results['dawn_curve_slope'] = 0
        
        # 早晨峰值
        morning_data = cgm_data_copy[(cgm_data_copy['hour'] >= 6) & (cgm_data_copy['hour'] <= 10)]
        baseline_data = cgm_data_copy[(cgm_data_copy['hour'] >= 0) & (cgm_data_copy['hour'] <= 6)]
        
        if len(morning_data) > 0 and len(baseline_data) > 0:
            morning_peak = np.max(morning_data['glucose'])
            baseline = np.mean(baseline_data['glucose'])
            results['morning_peak_height'] = morning_peak - baseline
        else:
            results['morning_peak_height'] = 0
        
        # 夜间稳定性
        night_data = cgm_data_copy[
            ((cgm_data_copy['hour'] >= 22) | (cgm_data_copy['hour'] <= 6))
        ]
        if len(night_data) > 0:
            night_cv = np.std(night_data['glucose']) / np.mean(night_data['glucose'])
            results['nocturnal_curve_flatness'] = 1 - night_cv
        else:
            results['nocturnal_curve_flatness'] = 0.5
        
        # 下午稳定性
        afternoon_data = cgm_data_copy[(cgm_data_copy['hour'] >= 14) & (cgm_data_copy['hour'] <= 18)]
        if len(afternoon_data) > 0:
            afternoon_cv = np.std(afternoon_data['glucose']) / np.mean(afternoon_data['glucose'])
            results['afternoon_curve_stability'] = 1 - afternoon_cv
        else:
            results['afternoon_curve_stability'] = 0.5
        
        return results
    
    def generate_agp_curve_data(self, cgm_data: pd.DataFrame) -> Dict:
        """生成AGP曲线数据"""
        cgm_data_copy = cgm_data.copy()
        cgm_data_copy['hour'] = cgm_data_copy['timestamp'].dt.hour + cgm_data_copy['timestamp'].dt.minute / 60.0
        
        # 按小时分组计算分位数
        hourly_stats = cgm_data_copy.groupby('hour')['glucose'].describe(
            percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]
        )
        
        # 插值到96个点 (每15分钟一个点)
        hour_points = np.linspace(0, 24, 96)
        
        agp_data = {
            'hour': hour_points,
            'p05': np.interp(hour_points, hourly_stats.index, hourly_stats['5%']),
            'p25': np.interp(hour_points, hourly_stats.index, hourly_stats['25%']),
            'p50': np.interp(hour_points, hourly_stats.index, hourly_stats['50%']),
            'p75': np.interp(hour_points, hourly_stats.index, hourly_stats['75%']),
            'p95': np.interp(hour_points, hourly_stats.index, hourly_stats['95%'])
        }
        
        return agp_data


class EnhancedAGPAISystem:
    """增强版AGPAI系统 - 集成智能标注功能"""
    
    def __init__(self, output_dir: str = "./agpai_reports"):
        self.analyzer = SimplifiedAGPAnalyzer()
        self.visualizer = EnhancedAGPVisualizer()
        self.template_system = ClinicalInterpretationTemplates()
        self.output_dir = output_dir
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def create_comprehensive_analysis(self, cgm_data: pd.DataFrame, 
                                    patient_info: Optional[Dict] = None) -> Dict:
        """创建完整的AGP分析和可视化"""
        
        print("🔬 开始进行AGP分析...")
        
        # 1. 执行基础AGP分析
        analysis_results = self.analyzer.analyze_cgm_data(cgm_data, analysis_days=14)
        
        print("📊 生成AGP曲线数据...")
        
        # 2. 生成AGP曲线数据
        agp_data = self.analyzer.generate_agp_curve_data(cgm_data)
        
        print("🧠 生成临床解读...")
        
        # 3. 生成临床解读
        clinical_interpretation = self.template_system.generate_comprehensive_interpretation(
            analysis_results
        )
        
        print("🎨 创建智能标注图表...")
        
        # 4. 创建可视化图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # AGP图表
        agp_chart_path = f"{self.output_dir}/Enhanced_AGP_Chart_{timestamp}.png"
        agp_chart = self.visualizer.create_annotated_agp_chart(
            agp_data, analysis_results, patient_info, save_path=agp_chart_path
        )
        
        # 每日曲线图表
        daily_chart_path = f"{self.output_dir}/Enhanced_Daily_Curves_{timestamp}.png"
        daily_chart = self.visualizer.create_annotated_daily_curves(
            cgm_data, analysis_results, days_to_show=5, save_path=daily_chart_path
        )
        
        print("📝 生成完整报告...")
        
        # 5. 创建完整报告
        complete_report = {
            'meta_info': {
                'analysis_timestamp': datetime.now().isoformat(),
                'agpai_version': '2.0_enhanced',
                'analysis_period_days': 14,
                'total_data_points': len(cgm_data)
            },
            'patient_info': patient_info or {},
            'technical_metrics': analysis_results,
            'clinical_interpretation': clinical_interpretation,
            'data_quality': {
                'completeness': self._assess_data_completeness(cgm_data),
                'reliability': self._assess_data_reliability(cgm_data)
            },
            'charts': {
                'agp_chart_path': agp_chart_path,
                'daily_chart_path': daily_chart_path
            },
            'recommendations_summary': self._generate_recommendations_summary(clinical_interpretation)
        }
        
        # 6. 保存报告
        report_path = f"{self.output_dir}/Complete_AGPAI_Report_{timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(complete_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 分析完成！报告保存至: {report_path}")
        
        return complete_report
    
    def _assess_data_completeness(self, cgm_data: pd.DataFrame) -> Dict:
        """评估数据完整性"""
        expected_points = 14 * 24 * 4  # 14天 * 24小时 * 4个点/小时
        actual_points = len(cgm_data)
        completeness = (actual_points / expected_points) * 100
        
        return {
            'expected_points': expected_points,
            'actual_points': actual_points,
            'completeness_percentage': completeness,
            'assessment': '优秀' if completeness >= 90 else '良好' if completeness >= 80 else '一般'
        }
    
    def _assess_data_reliability(self, cgm_data: pd.DataFrame) -> Dict:
        """评估数据可靠性"""
        glucose_values = cgm_data['glucose'].values
        
        # 检查异常值
        outliers = np.sum((glucose_values < 1.0) | (glucose_values > 30.0))
        outlier_rate = (outliers / len(glucose_values)) * 100
        
        # 检查缺失值模式
        time_gaps = []
        for i in range(1, len(cgm_data)):
            gap = (cgm_data.iloc[i]['timestamp'] - cgm_data.iloc[i-1]['timestamp']).total_seconds() / 60
            if gap > 20:  # 超过20分钟的间隔
                time_gaps.append(gap)
        
        return {
            'outlier_rate': outlier_rate,
            'time_gaps_count': len(time_gaps),
            'max_gap_minutes': max(time_gaps) if time_gaps else 0,
            'reliability_score': max(0, 100 - outlier_rate - len(time_gaps))
        }
    
    def _generate_recommendations_summary(self, clinical_interpretation: Dict) -> List[str]:
        """生成推荐总结"""
        summary = []
        
        # 优先问题
        if clinical_interpretation.get('priority_issues'):
            for issue in clinical_interpretation['priority_issues'][:3]:  # 前3个优先问题
                summary.append(f"🔴 {issue['issue']}: {issue['immediate_action']}")
        
        # 行动计划
        if clinical_interpretation.get('action_plan'):
            for action in clinical_interpretation['action_plan'][:2]:  # 前2个行动项
                summary.append(f"📋 {action['action']}: {action['details']}")
        
        return summary
    
    def display_analysis_summary(self, report: Dict):
        """显示分析摘要"""
        print("\n" + "="*60)
        print("🎯 AGPAI增强版分析摘要")
        print("="*60)
        
        # 患者信息
        patient = report.get('patient_info', {})
        if patient:
            print(f"📋 患者: {patient.get('name', '未知')} | 年龄: {patient.get('age', '未知')} | 类型: {patient.get('diabetes_type', '未知')}")
        
        # 整体评估
        overall = report['clinical_interpretation']['overall_assessment']
        print(f"\n🎯 整体控制水平: {overall['level']} ({overall['score']}/100分)")
        print(f"   {overall['description']}")
        print(f"   TIR: {overall['tir']} | TBR: {overall['tbr']} | CV: {overall['cv']}")
        
        # 数据质量
        quality = report['data_quality']
        print(f"\n📊 数据质量: 完整性 {quality['completeness']['completeness_percentage']:.1f}% | 可靠性 {quality['reliability']['reliability_score']:.1f}/100")
        
        # 优先问题
        priority_issues = report['clinical_interpretation'].get('priority_issues', [])
        if priority_issues:
            print(f"\n🚨 优先处理问题:")
            for i, issue in enumerate(priority_issues[:3], 1):
                severity_icon = {'critical': '🔴', 'warning': '🟡'}.get(issue['severity'], '📋')
                print(f"   {i}. {severity_icon} {issue['issue']}")
        
        # 积极表现
        positive = report['clinical_interpretation'].get('positive_findings', [])
        if positive:
            print(f"\n✅ 积极表现:")
            for finding in positive[:3]:
                print(f"   • {finding['finding']}")
        
        # 图表路径
        print(f"\n📈 生成的图表:")
        print(f"   AGP图表: {report['charts']['agp_chart_path']}")
        print(f"   每日曲线: {report['charts']['daily_chart_path']}")
        
        print("="*60)


def create_realistic_demo_data(days: int = 14) -> pd.DataFrame:
    """创建真实的演示数据"""
    np.random.seed(42)  # 确保可重复性
    
    dates = pd.date_range('2024-01-01', periods=days*24*4, freq='15min')
    glucose_values = []
    
    for timestamp in dates:
        hour = timestamp.hour + timestamp.minute / 60.0
        day_of_week = timestamp.dayofweek
        
        # 基础血糖
        base_glucose = 7.5
        
        # 昼夜节律
        circadian = 1.0 * np.sin(2 * np.pi * (hour - 6) / 24)
        
        # 黎明现象 (模拟明显的黎明现象)
        dawn_effect = 0
        if 4 <= hour <= 8:
            dawn_effect = 2.5 * (hour - 4) / 4  # 线性上升
        
        # 餐后血糖
        postprandial = 0
        # 早餐后 (7-10点)
        if 7 <= hour <= 10:
            postprandial = 6.0 * np.exp(-(hour - 8)**2 / 1.5)
        # 午餐后 (12-15点)
        elif 12 <= hour <= 15:
            postprandial = 4.5 * np.exp(-(hour - 13)**2 / 1.2)
        # 晚餐后 (18-21点)
        elif 18 <= hour <= 21:
            postprandial = 5.0 * np.exp(-(hour - 19)**2 / 1.5)
        
        # 随机低血糖事件 (2%概率)
        hypo_event = 0
        if np.random.random() < 0.02:
            hypo_event = -np.random.uniform(2.0, 4.0)
        
        # 随机高血糖事件 (3%概率)  
        hyper_event = 0
        if np.random.random() < 0.03:
            hyper_event = np.random.uniform(3.0, 8.0)
        
        # 夜间不稳定性 (模拟基础胰岛素不足)
        night_instability = 0
        if 22 <= hour or hour <= 6:
            if np.random.random() < 0.15:  # 15%概率夜间波动
                night_instability = np.random.normal(0, 1.5)
        
        # 传感器噪声
        noise = np.random.normal(0, 0.6)
        
        # 合成血糖值
        glucose = (base_glucose + circadian + dawn_effect + postprandial + 
                  hypo_event + hyper_event + night_instability + noise)
        
        # 限制在生理范围
        glucose = np.clip(glucose, 2.0, 25.0)
        glucose_values.append(glucose)
    
    return pd.DataFrame({
        'timestamp': dates,
        'glucose': glucose_values,
        'device_info': 'enhanced_demo'
    })


def main():
    """主演示程序"""
    
    print("🚀 AGPAI增强版完整演示")
    print("集成智能标注功能的AGP分析系统\n")
    
    # 1. 创建演示数据
    print("📊 生成真实CGM演示数据...")
    cgm_data = create_realistic_demo_data(days=14)
    print(f"   生成 {len(cgm_data)} 个数据点，时间跨度14天")
    print(f"   血糖范围: {cgm_data['glucose'].min():.1f} - {cgm_data['glucose'].max():.1f} mmol/L\n")
    
    # 2. 设置患者信息
    patient_info = {
        'name': '李明',
        'age': 52,
        'gender': '男',
        'diabetes_type': 'T2DM',
        'diabetes_duration': '8年',
        'current_treatment': '基础+餐时胰岛素',
        'cgm_device': 'Dexcom G6'
    }
    
    # 3. 创建增强AGPAI系统
    print("🧠 初始化增强版AGPAI系统...")
    agpai_system = EnhancedAGPAISystem(output_dir="./enhanced_agpai_reports")
    
    # 4. 执行完整分析
    print("\n🔍 执行完整AGP分析和可视化...")
    complete_report = agpai_system.create_comprehensive_analysis(cgm_data, patient_info)
    
    # 5. 显示分析摘要
    agpai_system.display_analysis_summary(complete_report)
    
    # 6. 显示技术指标
    print(f"\n📈 详细技术指标:")
    metrics = complete_report['technical_metrics']
    key_metrics = [
        ('mean_glucose', '平均血糖', 'mmol/L'),
        ('cv_glucose', '变异系数', '%'),
        ('tir_percentage', 'TIR目标范围内时间', '%'),
        ('tbr_percentage', 'TBR低血糖时间', '%'),
        ('tar_percentage', 'TAR高血糖时间', '%'),
        ('dawn_curve_slope', '黎明现象斜率', 'mmol/L/h'),
        ('morning_peak_height', '早晨峰值高度', 'mmol/L'),
        ('nocturnal_curve_flatness', '夜间稳定性', ''),
        ('afternoon_curve_stability', '下午稳定性', '')
    ]
    
    for key, name, unit in key_metrics:
        value = metrics.get(key, 0)
        print(f"   {name}: {value:.2f} {unit}")
    
    # 7. 显示文件输出信息
    print(f"\n📁 输出文件:")
    charts = complete_report['charts']
    print(f"   📊 智能标注AGP图: {charts['agp_chart_path']}")
    print(f"   📈 每日血糖曲线: {charts['daily_chart_path']}")
    
    print(f"\n🎉 演示完成！")
    print(f"   这就是增强版AGPAI系统的完整功能展示")
    print(f"   包含智能标注、临床解读和个性化建议的AGP分析")
    
    # 显示图表 (如果在交互环境中)
    try:
        import matplotlib.pyplot as plt
        plt.show()
        print(f"\n👀 图表已在新窗口中显示")
    except:
        print(f"\n💡 可通过图片查看器打开生成的PNG文件查看图表")
    
    return complete_report


if __name__ == "__main__":
    # 运行完整演示
    report = main()