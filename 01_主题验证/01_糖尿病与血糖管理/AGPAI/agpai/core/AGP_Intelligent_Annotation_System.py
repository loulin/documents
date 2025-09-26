#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGP智能标注系统
基于现有AGPAI系统，增加AGP图表和每日血糖曲线的智能标注功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging

# 导入现有的AGPAI系统
from .CGM_AGP_Analyzer_Agent import CGMDataReader, AGPVisualAnalyzer, AGPIntelligentReporter
from ..config.config_manager import ConfigManager

class AGPAnnotationEngine:
    """AGP图表智能标注引擎"""
    
    def __init__(self):
        self.annotation_styles = {
            'high_priority': {
                'color': '#FF4444',
                'fontsize': 10,
                'fontweight': 'bold',
                'bbox': dict(boxstyle="round,pad=0.3", facecolor='#FF4444', alpha=0.8)
            },
            'medium_priority': {
                'color': '#FF8800',
                'fontsize': 9,
                'fontweight': 'normal',
                'bbox': dict(boxstyle="round,pad=0.3", facecolor='#FF8800', alpha=0.7)
            },
            'low_priority': {
                'color': '#4488FF',
                'fontsize': 8,
                'fontweight': 'normal',
                'bbox': dict(boxstyle="round,pad=0.3", facecolor='#4488FF', alpha=0.6)
            },
            'positive': {
                'color': '#44AA44',
                'fontsize': 9,
                'fontweight': 'normal',
                'bbox': dict(boxstyle="round,pad=0.3", facecolor='#44AA44', alpha=0.7)
            }
        }
    
    def identify_annotation_points(self, analysis_results: Dict, agp_curve: Dict) -> List[Dict]:
        """识别需要标注的关键点"""
        annotations = []
        hours = agp_curve['hour']
        median_curve = agp_curve['p50']
        
        # 1. 黎明现象标注
        dawn_slope = analysis_results.get('dawn_curve_slope', 0)
        if abs(dawn_slope) > 0.5:
            dawn_peak_idx = np.argmax(median_curve[(hours >= 4) & (hours <= 8)])
            dawn_hour = hours[(hours >= 4) & (hours <= 8)][dawn_peak_idx]
            dawn_glucose = median_curve[(hours >= 4) & (hours <= 8)][dawn_peak_idx]
            
            if dawn_slope > 0.5:
                annotations.append({
                    'type': 'dawn_phenomenon',
                    'x': dawn_hour,
                    'y': dawn_glucose,
                    'text': f'黎明现象\n+{dawn_slope:.1f}mmol/L/h',
                    'priority': 'high_priority' if dawn_slope > 1.5 else 'medium_priority',
                    'arrow_direction': 'up'
                })
            else:
                annotations.append({
                    'type': 'reverse_dawn',
                    'x': dawn_hour,
                    'y': dawn_glucose,
                    'text': f'凌晨下降\n-{abs(dawn_slope):.1f}mmol/L/h',
                    'priority': 'medium_priority',
                    'arrow_direction': 'down'
                })
        
        # 2. 餐后峰值标注
        morning_peak_height = analysis_results.get('morning_peak_height', 0)
        if morning_peak_height > 3.0:
            breakfast_mask = (hours >= 7) & (hours <= 10)
            peak_idx = np.argmax(median_curve[breakfast_mask])
            peak_hour = hours[breakfast_mask][peak_idx]
            peak_glucose = median_curve[breakfast_mask][peak_idx]
            
            annotations.append({
                'type': 'postprandial_peak',
                'x': peak_hour,
                'y': peak_glucose,
                'text': f'餐后峰值\n+{morning_peak_height:.1f}mmol/L',
                'priority': 'high_priority' if morning_peak_height > 6 else 'medium_priority',
                'arrow_direction': 'up'
            })
        
        # 3. 夜间不稳定标注
        nocturnal_flatness = analysis_results.get('nocturnal_curve_flatness', 1.0)
        if nocturnal_flatness < 0.8:
            night_mask = (hours >= 22) | (hours <= 6)
            night_glucose = median_curve[night_mask]
            unstable_idx = np.argmax(np.abs(np.diff(night_glucose)))
            unstable_hour = hours[night_mask][unstable_idx]
            unstable_glucose = night_glucose[unstable_idx]
            
            annotations.append({
                'type': 'nocturnal_instability',
                'x': unstable_hour,
                'y': unstable_glucose,
                'text': f'夜间不稳定\n平坦度{nocturnal_flatness:.2f}',
                'priority': 'medium_priority',
                'arrow_direction': 'down'
            })
        
        # 4. 目标范围覆盖度标注
        target_coverage = analysis_results.get('target_range_coverage', 70)
        if target_coverage < 70:
            # 找到最需要改善的时段
            p25 = agp_curve['p25']
            p75 = agp_curve['p75']
            outside_target = ((p25 < 3.9) | (p75 > 10.0))
            
            if np.any(outside_target):
                worst_idx = np.argmax(np.abs(median_curve - 7.0))  # 离理想值最远的点
                worst_hour = hours[worst_idx]
                worst_glucose = median_curve[worst_idx]
                
                annotations.append({
                    'type': 'low_tir',
                    'x': worst_hour,
                    'y': worst_glucose,
                    'text': f'TIR偏低\n{target_coverage:.1f}%<70%',
                    'priority': 'high_priority' if target_coverage < 50 else 'medium_priority',
                    'arrow_direction': 'down' if worst_glucose > 10 else 'up'
                })
        
        # 5. 血糖变异性标注
        glucose_cv = analysis_results.get('glucose_coefficient_of_variation', 30)
        if glucose_cv > 36:
            # 找到变异最大的时段
            band_width = agp_curve['p75'] - agp_curve['p25']
            max_variation_idx = np.argmax(band_width)
            variation_hour = hours[max_variation_idx]
            variation_glucose = median_curve[max_variation_idx]
            
            annotations.append({
                'type': 'high_variability',
                'x': variation_hour,
                'y': variation_glucose,
                'text': f'变异性高\nCV={glucose_cv:.1f}%',
                'priority': 'medium_priority',
                'arrow_direction': 'up'
            })
        
        # 6. 优秀控制标注（正面反馈）
        smoothness = analysis_results.get('median_curve_smoothness', 0.5)
        if smoothness > 0.8 and target_coverage > 80:
            stable_hour = 14  # 下午时段通常最稳定
            stable_glucose = np.interp(stable_hour, hours, median_curve)
            
            annotations.append({
                'type': 'excellent_control',
                'x': stable_hour,
                'y': stable_glucose,
                'text': f'控制优秀\nTIR={target_coverage:.1f}%',
                'priority': 'positive',
                'arrow_direction': 'none'
            })
        
        return annotations
    
    def create_annotated_agp_chart(self, agp_curve: Dict, analysis_results: Dict, 
                                 patient_info: Dict = None, save_path: str = None) -> plt.Figure:
        """创建带智能标注的AGP图表"""
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Helvetica']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(14, 10))
        
        hours = agp_curve['hour']
        
        # 绘制AGP曲线和分位数带
        self._draw_agp_base_chart(ax, agp_curve)
        
        # 识别标注点
        annotations = self.identify_annotation_points(analysis_results, agp_curve)
        
        # 添加智能标注
        self._add_intelligent_annotations(ax, annotations)
        
        # 添加图例和说明
        self._add_chart_legend_and_info(ax, analysis_results, patient_info)
        
        # 设置图表样式
        self._set_chart_style(ax)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
        
        return fig
    
    def _draw_agp_base_chart(self, ax, agp_curve: Dict):
        """绘制AGP基础图表"""
        hours = agp_curve['hour']
        
        # 填充分位数区域
        ax.fill_between(hours, agp_curve['p05'], agp_curve['p95'], 
                       alpha=0.2, color='lightblue', label='5%-95%分位数')
        ax.fill_between(hours, agp_curve['p25'], agp_curve['p75'], 
                       alpha=0.4, color='lightblue', label='25%-75%分位数')
        
        # 绘制中位数线
        ax.plot(hours, agp_curve['p50'], color='darkblue', linewidth=2.5, 
                label='中位数曲线')
        
        # 添加目标范围背景
        ax.axhspan(3.9, 10.0, alpha=0.1, color='green', zorder=0)
        ax.axhline(y=3.9, color='orange', linestyle='--', alpha=0.6, label='目标范围')
        ax.axhline(y=10.0, color='orange', linestyle='--', alpha=0.6)
        
        # 添加危险区域
        ax.axhspan(0, 3.0, alpha=0.15, color='red', zorder=0)
        ax.axhspan(13.9, 25, alpha=0.15, color='red', zorder=0)
    
    def _add_intelligent_annotations(self, ax, annotations: List[Dict]):
        """添加智能标注"""
        annotation_offset = 0  # 用于避免标注重叠
        
        for ann in annotations:
            style = self.annotation_styles[ann['priority']]
            
            # 计算标注位置（避免重叠）
            y_offset = annotation_offset * 1.5
            annotation_offset = (annotation_offset + 1) % 3  # 循环使用偏移
            
            # 添加箭头（如果需要）
            if ann['arrow_direction'] != 'none':
                arrow_props = dict(
                    arrowstyle='->', 
                    color=style['color'], 
                    alpha=0.8,
                    lw=1.5
                )
                
                # 箭头方向
                dy = 1.5 if ann['arrow_direction'] == 'up' else -1.5
                
                ax.annotate('', 
                           xy=(ann['x'], ann['y']), 
                           xytext=(ann['x'], ann['y'] + dy + y_offset),
                           arrowprops=arrow_props)
            
            # 添加文本标注
            ax.annotate(ann['text'], 
                       xy=(ann['x'], ann['y']), 
                       xytext=(ann['x'], ann['y'] + 2.0 + y_offset),
                       fontsize=style['fontsize'],
                       fontweight=style['fontweight'],
                       color='white',
                       ha='center',
                       va='center',
                       bbox=style['bbox'],
                       zorder=10)
    
    def _add_chart_legend_and_info(self, ax, analysis_results: Dict, patient_info: Dict = None):
        """添加图例和信息"""
        # 添加标题
        title = "AGP (Ambulatory Glucose Profile) - 智能分析报告"
        if patient_info:
            title += f"\n患者: {patient_info.get('name', '未知')} | " \
                    f"分析日期: {datetime.now().strftime('%Y-%m-%d')}"
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # 添加关键指标文本框
        tir = analysis_results.get('target_range_coverage', 0)
        cv = analysis_results.get('glucose_coefficient_of_variation', 0)
        smoothness = analysis_results.get('median_curve_smoothness', 0)
        
        info_text = f"""关键指标:
TIR (目标范围): {tir:.1f}%
血糖CV: {cv:.1f}%
曲线平滑度: {smoothness:.2f}
分析天数: 14天"""
        
        # 在右上角添加信息框
        ax.text(0.98, 0.98, info_text, 
               transform=ax.transAxes, 
               fontsize=9,
               verticalalignment='top',
               horizontalalignment='right',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    def _set_chart_style(self, ax):
        """设置图表样式"""
        ax.set_xlabel('时间 (小时)', fontsize=12)
        ax.set_ylabel('血糖 (mmol/L)', fontsize=12)
        ax.set_xlim(0, 24)
        ax.set_ylim(0, 20)
        
        # 设置时间轴标签
        ax.set_xticks(range(0, 25, 2))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 2)], rotation=45)
        
        # 添加网格
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # 添加图例
        ax.legend(loc='upper left', fontsize=10)

class DailyCurveAnnotationEngine:
    """每日血糖曲线标注引擎"""
    
    def __init__(self):
        self.meal_times = {
            'breakfast': (7, 9),
            'lunch': (12, 14),
            'dinner': (18, 20)
        }
    
    def create_annotated_daily_curves(self, cgm_data: pd.DataFrame, analysis_results: Dict,
                                    days_to_show: int = 7, save_path: str = None) -> plt.Figure:
        """创建带标注的每日血糖曲线"""
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Helvetica']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 选择最近几天的数据
        latest_date = cgm_data['timestamp'].max().date()
        start_date = latest_date - timedelta(days=days_to_show-1)
        
        daily_data = cgm_data[cgm_data['timestamp'].dt.date >= start_date].copy()
        daily_data['date'] = daily_data['timestamp'].dt.date
        daily_data['hour'] = daily_data['timestamp'].dt.hour + daily_data['timestamp'].dt.minute / 60.0
        
        # 创建子图
        fig, axes = plt.subplots(days_to_show, 1, figsize=(16, 3*days_to_show), sharex=True)
        if days_to_show == 1:
            axes = [axes]
        
        # 为每一天创建标注曲线
        for i, (date, day_data) in enumerate(daily_data.groupby('date')):
            if i >= days_to_show:
                break
                
            ax = axes[i]
            self._draw_daily_curve_with_annotations(ax, day_data, analysis_results, date)
        
        # 设置整体样式
        plt.xlabel('时间 (小时)', fontsize=12)
        plt.suptitle('每日血糖曲线 - 智能标注分析', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
        
        return fig
    
    def _draw_daily_curve_with_annotations(self, ax, day_data: pd.DataFrame, 
                                         analysis_results: Dict, date):
        """绘制单日曲线并添加标注"""
        
        if len(day_data) == 0:
            ax.text(0.5, 0.5, f'{date}\n无数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            return
        
        hours = day_data['hour']
        glucose = day_data['glucose']
        
        # 绘制基础曲线
        ax.plot(hours, glucose, color='darkblue', linewidth=1.5, alpha=0.8)
        ax.scatter(hours, glucose, color='darkblue', s=20, alpha=0.6)
        
        # 添加目标范围背景
        ax.axhspan(3.9, 10.0, alpha=0.1, color='green', zorder=0)
        ax.axhline(y=3.9, color='orange', linestyle='--', alpha=0.6)
        ax.axhline(y=10.0, color='orange', linestyle='--', alpha=0.6)
        
        # 添加餐时标记
        self._add_meal_time_markers(ax)
        
        # 检测并标注异常模式
        self._detect_and_annotate_daily_patterns(ax, day_data, analysis_results)
        
        # 设置样式
        ax.set_ylabel(f'{date}\n血糖 (mmol/L)', fontsize=10)
        ax.set_xlim(0, 24)
        ax.set_ylim(0, max(20, glucose.max() * 1.1))
        ax.grid(True, alpha=0.3)
        
        # 设置时间轴
        ax.set_xticks(range(0, 25, 4))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 4)])
    
    def _add_meal_time_markers(self, ax):
        """添加餐时标记"""
        meal_colors = {'breakfast': '#FF6B6B', 'lunch': '#4ECDC4', 'dinner': '#45B7D1'}
        meal_names = {'breakfast': '早餐', 'lunch': '午餐', 'dinner': '晚餐'}
        
        for meal, (start_hour, end_hour) in self.meal_times.items():
            # 添加餐时背景区域
            ax.axvspan(start_hour, end_hour, alpha=0.15, color=meal_colors[meal], zorder=0)
            
            # 添加餐时标签
            mid_hour = (start_hour + end_hour) / 2
            ax.text(mid_hour, ax.get_ylim()[1] * 0.95, meal_names[meal], 
                   ha='center', va='top', fontsize=9, 
                   bbox=dict(boxstyle="round,pad=0.2", facecolor=meal_colors[meal], alpha=0.7))
    
    def _detect_and_annotate_daily_patterns(self, ax, day_data: pd.DataFrame, analysis_results: Dict):
        """检测并标注每日模式"""
        hours = day_data['hour'].values
        glucose = day_data['glucose'].values
        
        if len(glucose) < 10:  # 数据太少无法分析
            return
        
        # 1. 检测餐后峰值
        for meal, (start_hour, end_hour) in self.meal_times.items():
            meal_mask = (hours >= start_hour) & (hours <= end_hour + 2)  # 包括餐后2小时
            if np.any(meal_mask):
                meal_glucose = glucose[meal_mask]
                meal_hours = hours[meal_mask]
                
                if len(meal_glucose) > 0:
                    peak_idx = np.argmax(meal_glucose)
                    peak_glucose = meal_glucose[peak_idx]
                    peak_hour = meal_hours[peak_idx]
                    
                    # 计算餐前基线
                    pre_meal_mask = (hours >= start_hour - 0.5) & (hours <= start_hour)
                    if np.any(pre_meal_mask):
                        baseline = np.mean(glucose[pre_meal_mask])
                        peak_height = peak_glucose - baseline
                        
                        # 标注餐后峰值
                        if peak_height > 3.0:
                            color = '#FF4444' if peak_height > 6 else '#FF8800'
                            ax.annotate(f'+{peak_height:.1f}', 
                                       xy=(peak_hour, peak_glucose),
                                       xytext=(peak_hour, peak_glucose + 1.5),
                                       ha='center', va='bottom',
                                       fontsize=8, fontweight='bold',
                                       color='white',
                                       bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.8),
                                       arrowprops=dict(arrowstyle='->', color=color, alpha=0.8))
        
        # 2. 检测低血糖事件
        hypo_mask = glucose < 3.9
        if np.any(hypo_mask):
            hypo_glucose = glucose[hypo_mask]
            hypo_hours = hours[hypo_mask]
            
            # 找到最低点
            min_idx = np.argmin(hypo_glucose)
            min_glucose = hypo_glucose[min_idx]
            min_hour = hypo_hours[min_idx]
            
            ax.annotate(f'低血糖\n{min_glucose:.1f}', 
                       xy=(min_hour, min_glucose),
                       xytext=(min_hour, min_glucose - 1.5),
                       ha='center', va='top',
                       fontsize=8, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='#FF0000', alpha=0.9),
                       arrowprops=dict(arrowstyle='->', color='#FF0000', alpha=0.8))
        
        # 3. 检测高血糖事件
        hyper_mask = glucose > 13.9
        if np.any(hyper_mask):
            hyper_glucose = glucose[hyper_mask]
            hyper_hours = hours[hyper_mask]
            
            # 找到最高点
            max_idx = np.argmax(hyper_glucose)
            max_glucose = hyper_glucose[max_idx]
            max_hour = hyper_hours[max_idx]
            
            ax.annotate(f'高血糖\n{max_glucose:.1f}', 
                       xy=(max_hour, max_glucose),
                       xytext=(max_hour, max_glucose + 2),
                       ha='center', va='bottom',
                       fontsize=8, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='#AA0000', alpha=0.9),
                       arrowprops=dict(arrowstyle='->', color='#AA0000', alpha=0.8))
        
        # 4. 检测急剧变化
        if len(glucose) > 1:
            glucose_diff = np.diff(glucose)
            time_diff = np.diff(hours)
            
            # 避免除零错误
            valid_time_mask = time_diff > 0
            if np.any(valid_time_mask):
                rates = glucose_diff[valid_time_mask] / time_diff[valid_time_mask]
                
                # 急剧上升
                rapid_rise_mask = rates > 5
                if np.any(rapid_rise_mask):
                    rise_idx = np.where(valid_time_mask)[0][rapid_rise_mask][0]
                    rise_hour = hours[rise_idx + 1]
                    rise_glucose = glucose[rise_idx + 1]
                    
                    ax.annotate('急升', 
                               xy=(rise_hour, rise_glucose),
                               xytext=(rise_hour + 0.5, rise_glucose + 1),
                               ha='center', va='center',
                               fontsize=7, fontweight='bold',
                               color='white',
                               bbox=dict(boxstyle="round,pad=0.1", facecolor='#FF6600', alpha=0.8))
                
                # 急剧下降
                rapid_drop_mask = rates < -3
                if np.any(rapid_drop_mask):
                    drop_idx = np.where(valid_time_mask)[0][rapid_drop_mask][0]
                    drop_hour = hours[drop_idx + 1]
                    drop_glucose = glucose[drop_idx + 1]
                    
                    ax.annotate('急降', 
                               xy=(drop_hour, drop_glucose),
                               xytext=(drop_hour + 0.5, drop_glucose - 1),
                               ha='center', va='center',
                               fontsize=7, fontweight='bold',
                               color='white',
                               bbox=dict(boxstyle="round,pad=0.1", facecolor='#0066FF', alpha=0.8))

class EnhancedAGPAISystem:
    """增强版AGPAI系统 - 集成智能标注功能"""
    
    def __init__(self):
        self.cgm_reader = CGMDataReader()
        self.agp_analyzer = AGPVisualAnalyzer()
        self.report_generator = AGPIntelligentReporter()
        self.agp_annotator = AGPAnnotationEngine()
        self.daily_annotator = DailyCurveAnnotationEngine()
    
    def comprehensive_analysis_with_annotations(self, cgm_file_path: str, 
                                              patient_info: Dict = None,
                                              output_dir: str = "./") -> Dict:
        """
        完整的CGM分析，包含智能标注的AGP图和每日曲线
        
        Args:
            cgm_file_path: CGM数据文件路径
            patient_info: 患者信息
            output_dir: 输出目录
            
        Returns:
            包含所有分析结果和图表路径的字典
        """
        
        print("🔬 开始增强版AGPAI智能分析...")
        
        # 1. 读取CGM数据
        print("📖 正在读取CGM数据...")
        cgm_data = self.cgm_reader.read_cgm_file(cgm_file_path, device_type='generic_csv')
        print(f"✅ 成功读取{len(cgm_data)}个数据点")
        
        # 2. 进行57种视觉指标分析
        print("🔍 正在进行57种视觉指标分析...")
        analysis_results = self.agp_analyzer.analyze_cgm_data(cgm_data, analysis_days=14)
        
        if 'error' in analysis_results:
            print(f"❌ 分析错误: {analysis_results['error']}")
            return analysis_results
        
        print("✅ 完成57种视觉指标分析")
        
        # 3. 生成智能报告
        print("📊 正在生成智能分析报告...")
        intelligent_report = self.report_generator.generate_intelligent_report(
            analysis_results, patient_info)
        
        # 4. 生成带标注的AGP图表
        print("🎨 正在生成智能标注AGP图表...")
        processed_data = self._get_processed_data(cgm_data, 14)
        agp_curve = processed_data['agp_curve']
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        agp_chart_path = f"{output_dir}/AGP_智能标注图表_{timestamp}.png"
        
        agp_fig = self.agp_annotator.create_annotated_agp_chart(
            agp_curve, analysis_results, patient_info, agp_chart_path)
        
        print(f"✅ AGP标注图表已保存: {agp_chart_path}")
        
        # 5. 生成带标注的每日曲线
        print("📈 正在生成智能标注每日曲线...")
        daily_chart_path = f"{output_dir}/每日血糖曲线_智能标注_{timestamp}.png"
        
        daily_fig = self.daily_annotator.create_annotated_daily_curves(
            cgm_data, analysis_results, days_to_show=7, save_path=daily_chart_path)
        
        print(f"✅ 每日曲线标注图表已保存: {daily_chart_path}")
        
        # 6. 保存完整报告
        report_path = f"{output_dir}/AGPAI_完整智能分析报告_{timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(intelligent_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 完整分析报告已保存: {report_path}")
        
        # 7. 生成分析总结
        self._print_analysis_summary(intelligent_report)
        
        return {
            'analysis_results': analysis_results,
            'intelligent_report': intelligent_report,
            'agp_chart_path': agp_chart_path,
            'daily_chart_path': daily_chart_path,
            'report_path': report_path,
            'figures': {
                'agp_figure': agp_fig,
                'daily_figure': daily_fig
            }
        }
    
    def _get_processed_data(self, cgm_data: pd.DataFrame, analysis_days: int) -> Dict:
        """获取预处理的AGP数据"""
        # 复用AGPVisualAnalyzer中的预处理逻辑
        end_date = cgm_data['timestamp'].max()
        start_date = end_date - timedelta(days=analysis_days)
        data = cgm_data[cgm_data['timestamp'] >= start_date].copy()
        
        data['hour'] = data['timestamp'].dt.hour + data['timestamp'].dt.minute / 60.0
        hourly_stats = data.groupby('hour')['glucose'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
        
        agp_curve = {
            'hour': np.linspace(0, 24, 96),
            'p05': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['5%']),
            'p25': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['25%']),
            'p50': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['50%']),
            'p75': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['75%']),
            'p95': np.interp(np.linspace(0, 24, 96), hourly_stats.index, hourly_stats['95%'])
        }
        
        return {'agp_curve': agp_curve}
    
    def _print_analysis_summary(self, intelligent_report: Dict):
        """打印分析总结"""
        print("\n" + "="*60)
        print("🎯 AGPAI智能标注分析总结")
        print("="*60)
        
        # 整体评估
        overall = intelligent_report['overall_assessment']
        print(f"📊 整体评估: {overall['level']} ({overall['overall_score']}分)")
        print(f"📝 评估说明: {overall['description']}")
        print(f"📈 数据质量: {overall['data_quality']}")
        
        # 关键发现
        findings = intelligent_report['key_findings']
        if findings:
            print(f"\n🔍 主要发现 ({len(findings)}项):")
            for i, finding in enumerate(findings, 1):
                severity_icon = {'severe': '🔴', 'moderate': '🟡', 'mild': '🟢'}.get(finding.get('severity'), '📋')
                print(f"   {i}. {severity_icon} {finding['description']}")
        
        # 风险警报
        alerts = intelligent_report['risk_alerts']
        if alerts:
            print(f"\n⚠️  风险警报 ({len(alerts)}项):")
            for alert in alerts:
                urgency_icon = {'high': '🚨', 'medium': '⚠️', 'low': '💡'}.get(alert['urgency'], '📋')
                print(f"   {urgency_icon} [{alert['urgency'].upper()}] {alert['message']}")
        
        # 临床建议
        recommendations = intelligent_report['clinical_recommendations']
        if recommendations:
            print(f"\n💡 临床建议 ({len(recommendations)}项):")
            for i, rec in enumerate(recommendations, 1):
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '📋')
                print(f"   {i}. {priority_icon} {rec['recommendation']}")
        
        # 关键指标
        metrics = intelligent_report['technical_metrics']
        print(f"\n📊 关键指标:")
        key_metrics = [
            ('target_range_coverage', 'TIR目标范围', '%'),
            ('glucose_coefficient_of_variation', '血糖变异系数', '%'),
            ('median_curve_smoothness', '曲线平滑度', ''),
            ('dawn_curve_slope', '黎明现象斜率', 'mmol/L/h'),
            ('comprehensive_smoothness_score', '综合平滑度', '')
        ]
        
        for key, desc, unit in key_metrics:
            if key in metrics:
                value = metrics[key]
                print(f"   • {desc}: {value:.2f}{unit}")
        
        print("\n🎉 AGPAI智能标注分析完成！图表已生成智能标注。")
        print("="*60)

# 主程序演示
def main():
    """主程序 - 演示增强版AGPAI智能标注系统"""
    
    # 创建增强版AGPAI系统
    enhanced_agpai = EnhancedAGPAISystem()
    
    # 患者信息
    patient_info = {
        'name': '李明',
        'age': 52,
        'gender': '男',
        'diabetes_type': 'T2DM',
        'diabetes_duration': '10年',
        'cgm_device': 'Dexcom G6',
        'current_treatment': '基础-餐时胰岛素方案'
    }
    
    # CGM数据文件路径
    cgm_file_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/R002 V5.txt"
    
    try:
        # 执行完整的智能标注分析
        results = enhanced_agpai.comprehensive_analysis_with_annotations(
            cgm_file_path=cgm_file_path,
            patient_info=patient_info,
            output_dir="."
        )
        
        print(f"\n🎯 分析完成！生成的文件:")
        print(f"   📊 AGP标注图表: {results['agp_chart_path']}")
        print(f"   📈 每日曲线图表: {results['daily_chart_path']}")
        print(f"   📄 完整分析报告: {results['report_path']}")
        
        # 显示图表（可选）
        # plt.show()  # 取消注释以显示图表
        
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        logging.exception("详细错误信息:")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 运行主程序
    main()