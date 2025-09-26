#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版AGP可视化系统 - 带智能标注功能
在AGP图和每日血糖曲线上自动标注需要解读的关键模式和临床要点
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class AGPAnnotationEngine:
    """AGP智能标注引擎"""
    
    def __init__(self):
        self.clinical_thresholds = {
            'hypoglycemia': 3.9,
            'target_lower': 3.9,
            'target_upper': 10.0,
            'hyperglycemia': 13.9,
            'severe_hypo': 3.0,
            'severe_hyper': 16.7
        }
        
        self.annotation_styles = {
            'critical': {'color': '#FF0000', 'fontsize': 10, 'fontweight': 'bold'},
            'warning': {'color': '#FF8C00', 'fontsize': 9, 'fontweight': 'normal'},
            'info': {'color': '#0066CC', 'fontsize': 8, 'fontweight': 'normal'},
            'positive': {'color': '#008000', 'fontsize': 8, 'fontweight': 'normal'}
        }
    
    def detect_clinical_patterns(self, agp_data: Dict, analysis_results: Dict) -> List[Dict]:
        """检测临床重要模式并生成标注"""
        annotations = []
        
        # 检测黎明现象
        dawn_slope = analysis_results.get('dawn_curve_slope', 0)
        if dawn_slope > 1.0:
            annotations.append({
                'type': 'dawn_phenomenon',
                'hour_range': (4, 8),
                'severity': 'warning',
                'message': f'黎明现象显著\n血糖上升{dawn_slope:.1f}mmol/L/h',
                'clinical_note': '建议调整长效胰岛素',
                'position': (6, agp_data['p50'][24])  # 6点位置
            })
        
        # 检测餐后峰值
        morning_peak = analysis_results.get('morning_peak_height', 0)
        if morning_peak > 5.0:
            annotations.append({
                'type': 'postprandial_peak',
                'hour_range': (7, 10),
                'severity': 'warning',
                'message': f'早餐后峰值过高\n+{morning_peak:.1f}mmol/L',
                'clinical_note': '优化早餐胰岛素时机',
                'position': (8.5, agp_data['p75'][34])  # 8.5点位置
            })
        
        # 检测低血糖风险区域
        tbr = analysis_results.get('tbr_percentage', 0)
        if tbr > 4.0:
            hypo_hours = self._find_hypoglycemia_hours(agp_data)
            for hour in hypo_hours:
                annotations.append({
                    'type': 'hypoglycemia_risk',
                    'hour_range': (hour-0.5, hour+0.5),
                    'severity': 'critical',
                    'message': f'低血糖风险区\nTBR: {tbr:.1f}%',
                    'clinical_note': '减少胰岛素剂量',
                    'position': (hour, self.clinical_thresholds['hypoglycemia'])
                })
        
        # 检测夜间不稳定
        nocturnal_stability = analysis_results.get('nocturnal_curve_flatness', 1)
        if nocturnal_stability < 0.7:
            annotations.append({
                'type': 'nocturnal_instability',
                'hour_range': (22, 6),
                'severity': 'warning',
                'message': f'夜间血糖波动\n稳定性: {nocturnal_stability:.2f}',
                'clinical_note': '评估基础胰岛素',
                'position': (0, agp_data['p50'][0])
            })
        
        # 检测高血糖平台期
        tar = analysis_results.get('tar_percentage', 0)
        if tar > 25.0:
            hyper_hours = self._find_hyperglycemia_hours(agp_data)
            for hour in hyper_hours:
                annotations.append({
                    'type': 'hyperglycemia_plateau',
                    'hour_range': (hour-1, hour+1),
                    'severity': 'warning',
                    'message': f'高血糖持续\nTAR: {tar:.1f}%',
                    'clinical_note': '增加胰岛素剂量',
                    'position': (hour, agp_data['p75'][int(hour*4)])
                })
        
        # 检测变异性过大区域
        cv = analysis_results.get('cv_glucose', 0)
        if cv > 36:
            variable_hours = self._find_variable_hours(agp_data)
            for hour in variable_hours:
                annotations.append({
                    'type': 'high_variability',
                    'hour_range': (hour-1, hour+1),
                    'severity': 'info',
                    'message': f'血糖变异大\nCV: {cv:.1f}%',
                    'clinical_note': '规律化饮食用药',
                    'position': (hour, agp_data['p95'][int(hour*4)])
                })
        
        # 检测理想控制区域
        tir = analysis_results.get('tir_percentage', 0)
        if tir > 70:
            stable_hours = self._find_stable_hours(agp_data)
            for hour in stable_hours[:2]:  # 只标注前2个稳定区域
                annotations.append({
                    'type': 'good_control',
                    'hour_range': (hour-1, hour+1),
                    'severity': 'positive',
                    'message': f'血糖控制良好\nTIR: {tir:.1f}%',
                    'clinical_note': '维持当前方案',
                    'position': (hour, (agp_data['p25'][int(hour*4)] + agp_data['p75'][int(hour*4)])/2)
                })
        
        return annotations
    
    def _find_hypoglycemia_hours(self, agp_data: Dict) -> List[int]:
        """找到低血糖风险小时"""
        hours = []
        for i, glucose in enumerate(agp_data['p25']):
            if glucose < self.clinical_thresholds['hypoglycemia']:
                hours.append(int(i / 4))  # 转换为小时
        return list(set(hours))
    
    def _find_hyperglycemia_hours(self, agp_data: Dict) -> List[int]:
        """找到高血糖小时"""
        hours = []
        for i, glucose in enumerate(agp_data['p75']):
            if glucose > self.clinical_thresholds['hyperglycemia']:
                hours.append(int(i / 4))
        return list(set(hours))
    
    def _find_variable_hours(self, agp_data: Dict) -> List[int]:
        """找到变异性大的小时"""
        hours = []
        band_width = np.array(agp_data['p75']) - np.array(agp_data['p25'])
        threshold = np.percentile(band_width, 80)  # 找到最大的20%
        
        for i, width in enumerate(band_width):
            if width > threshold:
                hours.append(int(i / 4))
        return list(set(hours))
    
    def _find_stable_hours(self, agp_data: Dict) -> List[int]:
        """找到稳定控制的小时"""
        hours = []
        for i in range(len(agp_data['p50'])):
            glucose = agp_data['p50'][i]
            band_width = agp_data['p75'][i] - agp_data['p25'][i]
            
            # 在目标范围且变异小
            if (self.clinical_thresholds['target_lower'] <= glucose <= self.clinical_thresholds['target_upper'] 
                and band_width < 2.0):
                hours.append(int(i / 4))
        return list(set(hours))


class EnhancedAGPVisualizer:
    """增强版AGP可视化器 - 带智能标注"""
    
    def __init__(self):
        self.annotation_engine = AGPAnnotationEngine()
        self.color_scheme = {
            'target_range': '#90EE90',
            'target_range_alpha': 0.3,
            'percentile_bands': ['#FFE4E1', '#FFB6C1', '#F08080', '#CD5C5C'],
            'median_line': '#DC143C',
            'hypo_zone': '#FF6B6B',
            'hyper_zone': '#FFA500',
            'background': '#F8F9FA'
        }
    
    def create_annotated_agp_chart(self, agp_data: Dict, analysis_results: Dict, 
                                  patient_info: Dict = None, save_path: str = None) -> plt.Figure:
        """创建带智能标注的AGP图表"""
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(16, 10))
        fig.patch.set_facecolor(self.color_scheme['background'])
        ax.set_facecolor('white')
        
        hours = agp_data['hour']
        
        # 绘制目标范围背景
        ax.axhspan(3.9, 10.0, alpha=self.color_scheme['target_range_alpha'], 
                  color=self.color_scheme['target_range'], label='目标范围 (3.9-10.0 mmol/L)')
        
        # 绘制分位数带
        ax.fill_between(hours, agp_data['p05'], agp_data['p95'], 
                       alpha=0.2, color=self.color_scheme['percentile_bands'][0], label='5%-95%范围')
        ax.fill_between(hours, agp_data['p25'], agp_data['p75'], 
                       alpha=0.4, color=self.color_scheme['percentile_bands'][1], label='25%-75%范围')
        
        # 绘制中位数曲线
        ax.plot(hours, agp_data['p50'], color=self.color_scheme['median_line'], 
               linewidth=3, label='中位数曲线', zorder=5)
        
        # 绘制参考线
        ax.axhline(y=3.9, color='red', linestyle='--', alpha=0.7, linewidth=1, label='低血糖阈值')
        ax.axhline(y=10.0, color='orange', linestyle='--', alpha=0.7, linewidth=1, label='高血糖阈值')
        ax.axhline(y=3.0, color='darkred', linestyle=':', alpha=0.5, linewidth=1, label='严重低血糖')
        
        # 获取智能标注
        annotations = self.annotation_engine.detect_clinical_patterns(agp_data, analysis_results)
        
        # 添加智能标注
        self._add_intelligent_annotations(ax, annotations)
        
        # 添加临床解读框
        self._add_clinical_interpretation_box(fig, analysis_results)
        
        # 设置图表样式
        self._style_agp_chart(ax, patient_info)
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                       facecolor=self.color_scheme['background'])
        
        return fig
    
    def create_annotated_daily_curves(self, cgm_data: pd.DataFrame, analysis_results: Dict,
                                    days_to_show: int = 7, save_path: str = None) -> plt.Figure:
        """创建带标注的每日血糖曲线"""
        
        # 选择最近N天的数据
        latest_date = cgm_data['timestamp'].max().date()
        selected_days = []
        
        for i in range(days_to_show):
            day = latest_date - timedelta(days=i)
            day_data = cgm_data[cgm_data['timestamp'].dt.date == day].copy()
            if len(day_data) > 10:  # 确保有足够数据
                selected_days.append(day_data)
        
        # 创建子图
        fig, axes = plt.subplots(days_to_show, 1, figsize=(16, 3*days_to_show))
        if days_to_show == 1:
            axes = [axes]
        
        fig.patch.set_facecolor(self.color_scheme['background'])
        
        for i, (ax, day_data) in enumerate(zip(axes, selected_days)):
            # 绘制当日血糖曲线
            self._plot_single_day_curve(ax, day_data, analysis_results)
            
            # 添加当日特异性标注
            self._add_daily_annotations(ax, day_data, analysis_results)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor=self.color_scheme['background'])
        
        return fig
    
    def _add_intelligent_annotations(self, ax, annotations: List[Dict]):
        """添加智能标注到AGP图表"""
        
        for i, annotation in enumerate(annotations):
            x, y = annotation['position']
            message = annotation['message']
            clinical_note = annotation['clinical_note']
            severity = annotation['severity']
            
            style = self.annotation_engine.annotation_styles[severity]
            
            # 创建标注文本
            full_text = f"{message}\n💡 {clinical_note}"
            
            # 添加标注箭头和文本
            bbox_props = dict(
                boxstyle="round,pad=0.3",
                facecolor='white',
                edgecolor=style['color'],
                linewidth=2,
                alpha=0.9
            )
            
            # 计算标注位置避免重叠
            offset_y = 2 + (i % 3) * 1.5
            if y > 15:
                offset_y = -offset_y
            
            ax.annotate(full_text,
                       xy=(x, y),
                       xytext=(x + 1, y + offset_y),
                       fontsize=style['fontsize'],
                       fontweight=style['fontweight'],
                       color=style['color'],
                       bbox=bbox_props,
                       arrowprops=dict(
                           arrowstyle='->',
                           color=style['color'],
                           lw=1.5,
                           alpha=0.8
                       ),
                       zorder=10)
            
            # 在对应时间段添加高亮
            if 'hour_range' in annotation:
                start_hour, end_hour = annotation['hour_range']
                if end_hour < start_hour:  # 跨午夜
                    ax.axvspan(start_hour, 24, alpha=0.1, color=style['color'])
                    ax.axvspan(0, end_hour, alpha=0.1, color=style['color'])
                else:
                    ax.axvspan(start_hour, end_hour, alpha=0.1, color=style['color'])
    
    def _add_clinical_interpretation_box(self, fig, analysis_results: Dict):
        """添加临床解读信息框"""
        
        # 计算关键指标
        tir = analysis_results.get('tir_percentage', 0)
        tbr = analysis_results.get('tbr_percentage', 0)
        tar = analysis_results.get('tar_percentage', 0)
        cv = analysis_results.get('cv_glucose', 0)
        mean_glucose = analysis_results.get('mean_glucose', 0)
        
        # 生成解读文本
        interpretation = f"""
📊 关键指标解读:
• TIR (目标范围内时间): {tir:.1f}% {'✅' if tir >= 70 else '⚠️'}
• TBR (低血糖时间): {tbr:.1f}% {'⚠️' if tbr > 4 else '✅'}
• TAR (高血糖时间): {tar:.1f}% {'⚠️' if tar > 25 else '✅'}
• CV (血糖变异系数): {cv:.1f}% {'⚠️' if cv > 36 else '✅'}
• 平均血糖: {mean_glucose:.1f} mmol/L

🎯 总体评价: {'血糖控制达标' if tir >= 70 and tbr <= 4 else '需要优化治疗方案'}
        """
        
        # 添加文本框
        fig.text(0.02, 0.02, interpretation.strip(), fontsize=10,
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8),
                verticalalignment='bottom', fontfamily='monospace')
    
    def _plot_single_day_curve(self, ax, day_data: pd.DataFrame, analysis_results: Dict):
        """绘制单日血糖曲线"""
        
        # 绘制目标范围背景
        ax.axhspan(3.9, 10.0, alpha=0.2, color=self.color_scheme['target_range'])
        
        # 绘制血糖曲线
        hours = day_data['timestamp'].dt.hour + day_data['timestamp'].dt.minute / 60.0
        ax.plot(hours, day_data['glucose'], color='#2E86AB', linewidth=2, marker='o', markersize=3)
        
        # 绘制参考线
        ax.axhline(y=3.9, color='red', linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=10.0, color='orange', linestyle='--', alpha=0.7, linewidth=1)
        
        # 设置样式
        date_str = day_data['timestamp'].iloc[0].strftime('%Y-%m-%d %A')
        ax.set_title(f'血糖曲线 - {date_str}', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 24)
        ax.set_ylim(2, 20)
        ax.set_ylabel('血糖 (mmol/L)', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 设置x轴标签
        ax.set_xticks(range(0, 25, 3))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 3)], fontsize=9)
    
    def _add_daily_annotations(self, ax, day_data: pd.DataFrame, analysis_results: Dict):
        """添加每日特异性标注"""
        
        hours = day_data['timestamp'].dt.hour + day_data['timestamp'].dt.minute / 60.0
        glucose = day_data['glucose']
        
        # 标注低血糖事件
        hypo_mask = glucose < 3.9
        if hypo_mask.any():
            hypo_hours = hours[hypo_mask]
            hypo_glucose = glucose[hypo_mask]
            for h, g in zip(hypo_hours, hypo_glucose):
                ax.annotate('低血糖!', xy=(h, g), xytext=(h, g-1.5),
                           color='red', fontweight='bold', fontsize=9,
                           arrowprops=dict(arrowstyle='->', color='red'))
        
        # 标注餐后峰值
        meal_times = [7.5, 12.5, 18.5]  # 假设的用餐时间
        for meal_time in meal_times:
            # 查找餐后2小时内的峰值
            post_meal_mask = (hours >= meal_time) & (hours <= meal_time + 2)
            if post_meal_mask.any():
                post_meal_glucose = glucose[post_meal_mask]
                if len(post_meal_glucose) > 0:
                    max_glucose = post_meal_glucose.max()
                    if max_glucose > 13.0:
                        max_hour = hours[post_meal_mask][post_meal_glucose.argmax()]
                        ax.annotate(f'餐后高峰\n{max_glucose:.1f}', 
                                  xy=(max_hour, max_glucose), 
                                  xytext=(max_hour, max_glucose + 2),
                                  color='orange', fontsize=8,
                                  arrowprops=dict(arrowstyle='->', color='orange'))
        
        # 标注长时间高血糖
        hyper_mask = glucose > 13.0
        if hyper_mask.any():
            # 找连续高血糖区间
            hyper_periods = self._find_continuous_periods(hours[hyper_mask])
            for start_h, end_h in hyper_periods:
                if end_h - start_h > 2:  # 持续超过2小时
                    mid_h = (start_h + end_h) / 2
                    mid_glucose = glucose[(hours >= start_h) & (hours <= end_h)].mean()
                    ax.annotate(f'持续高血糖\n{end_h-start_h:.1f}小时', 
                              xy=(mid_h, mid_glucose), 
                              xytext=(mid_h, mid_glucose + 1.5),
                              color='darkorange', fontsize=8,
                              arrowprops=dict(arrowstyle='->', color='darkorange'))
    
    def _find_continuous_periods(self, hours_series) -> List[Tuple[float, float]]:
        """查找连续时间段"""
        if len(hours_series) == 0:
            return []
        
        periods = []
        start = hours_series.iloc[0]
        end = start
        
        for i in range(1, len(hours_series)):
            if hours_series.iloc[i] - hours_series.iloc[i-1] <= 0.5:  # 30分钟内连续
                end = hours_series.iloc[i]
            else:
                periods.append((start, end))
                start = hours_series.iloc[i]
                end = start
        
        periods.append((start, end))
        return periods
    
    def _style_agp_chart(self, ax, patient_info: Dict = None):
        """设置AGP图表样式"""
        
        # 基本样式
        ax.set_xlim(0, 24)
        ax.set_ylim(2, 20)
        ax.set_xlabel('时间 (小时)', fontsize=12, fontweight='bold')
        ax.set_ylabel('血糖 (mmol/L)', fontsize=12, fontweight='bold')
        
        # 标题
        title = '智能标注AGP分析图'
        if patient_info:
            title += f" - {patient_info.get('name', '患者')}"
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # X轴标签
        ax.set_xticks(range(0, 25, 3))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 3)])
        
        # 网格和图例
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=10)
        
        # 添加时间段标记
        time_periods = [
            (6, 12, '上午', '#E6F3FF'),
            (12, 18, '下午', '#FFF0E6'), 
            (18, 24, '晚上', '#F0E6FF'),
            (0, 6, '夜间', '#E6FFE6')
        ]
        
        for start, end, label, color in time_periods:
            ax.axvspan(start, end, alpha=0.1, color=color)
            ax.text((start + end) / 2, 19, label, ha='center', va='center', 
                   fontsize=10, alpha=0.7, fontweight='bold')


def demo_enhanced_agp_visualization():
    """演示增强版AGP可视化功能"""
    
    # 生成模拟数据
    print("🔬 生成演示数据...")
    dates = pd.date_range('2024-01-01', periods=14*24*4, freq='15min')
    np.random.seed(42)
    
    glucose_values = []
    for timestamp in dates:
        hour = timestamp.hour + timestamp.minute / 60.0
        
        # 基础血糖模式
        base_glucose = 7.0
        circadian = 1.2 * np.sin(2 * np.pi * (hour - 6) / 24)
        
        # 黎明现象
        dawn = 2.0 if 4 <= hour <= 8 else 0
        
        # 餐后峰值
        postprandial = 0
        if 7 <= hour <= 9:
            postprandial = 5 * np.exp(-(hour - 7.5)**2 / 0.8)
        elif 12 <= hour <= 14:
            postprandial = 4 * np.exp(-(hour - 12.5)**2 / 0.6)
        elif 18 <= hour <= 21:
            postprandial = 4.5 * np.exp(-(hour - 18.8)**2 / 0.9)
        
        # 随机波动和一些极端值
        noise = np.random.normal(0, 0.8)
        if np.random.random() < 0.05:  # 5%概率的极端值
            noise += np.random.choice([-3, 5]) 
        
        glucose = base_glucose + circadian + dawn + postprandial + noise
        glucose = np.clip(glucose, 2.5, 25.0)
        glucose_values.append(glucose)
    
    cgm_data = pd.DataFrame({
        'timestamp': dates,
        'glucose': glucose_values,
        'device_info': 'demo'
    })
    
    # 模拟分析结果
    analysis_results = {
        'tir_percentage': 65.5,
        'tbr_percentage': 5.2,
        'tar_percentage': 29.3,
        'cv_glucose': 42.1,
        'mean_glucose': 9.2,
        'dawn_curve_slope': 1.8,
        'morning_peak_height': 6.2,
        'nocturnal_curve_flatness': 0.6,
        'afternoon_curve_stability': 0.8
    }
    
    # 生成AGP数据
    cgm_data['hour'] = cgm_data['timestamp'].dt.hour + cgm_data['timestamp'].dt.minute / 60.0
    hourly_stats = cgm_data.groupby('hour')['glucose'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
    
    agp_data = {
        'hour': np.linspace(0, 24, 96),
        'p05': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['5%']),
        'p25': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['25%']),
        'p50': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['50%']),
        'p75': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['75%']),
        'p95': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['95%'])
    }
    
    patient_info = {
        'name': '张先生',
        'age': 45,
        'diabetes_type': 'T2DM'
    }
    
    # 创建可视化
    print("📊 创建智能标注AGP图表...")
    visualizer = EnhancedAGPVisualizer()
    
    # 生成AGP图表
    agp_fig = visualizer.create_annotated_agp_chart(
        agp_data, analysis_results, patient_info,
        save_path='Annotated_AGP_Chart.png'
    )
    
    # 生成每日曲线图表
    print("📈 创建每日血糖曲线标注...")
    daily_fig = visualizer.create_annotated_daily_curves(
        cgm_data, analysis_results, days_to_show=3,
        save_path='Annotated_Daily_Curves.png'
    )
    
    print("✅ 图表生成完成!")
    print("   - Annotated_AGP_Chart.png: 智能标注AGP图")
    print("   - Annotated_Daily_Curves.png: 标注每日血糖曲线")
    
    # 显示图表
    plt.show()
    
    return agp_fig, daily_fig


if __name__ == "__main__":
    # 运行演示
    demo_enhanced_agp_visualization()