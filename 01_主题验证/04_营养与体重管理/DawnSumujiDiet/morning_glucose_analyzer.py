#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清晨血糖升高现象分析工具
用于区分黎明现象、苏木杰效应和进食相关血糖升高

支持的数据格式：
1. HRS9531标准格式：STUDYID,SUBJID,ARM,SITEID,LBNAM,VISIT,LBREFID,LBDTC,LBORRES,LBORRESU
2. 简化格式：datetime,glucose 或 timestamp,glucose
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文编码
import sys
import os
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class MorningGlucoseAnalyzer:
    def __init__(self):
        self.glucose_data = None
        self.analysis_results = []
        
    def load_data(self, file_path, format_type="auto"):
        """
        加载血糖数据
        
        Args:
            file_path: 数据文件路径
            format_type: 数据格式类型 ("auto", "hrs9531", "simple")
        """
        try:
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                data = pd.read_excel(file_path)
            else:
                raise ValueError("支持的文件格式：CSV, XLSX")
                
            # 自动检测格式
            if format_type == "auto":
                if "LBDTC" in data.columns and "LBORRES" in data.columns:
                    format_type = "hrs9531"
                elif "datetime" in data.columns or "timestamp" in data.columns:
                    format_type = "simple"
                else:
                    print("警告：无法自动识别格式，尝试通用解析...")
                    format_type = "generic"
            
            self.glucose_data = self._parse_data(data, format_type)
            print(f"✅ 成功加载数据：{len(self.glucose_data)} 条记录")
            return True
            
        except Exception as e:
            print(f"❌ 数据加载失败：{e}")
            return False
    
    def _parse_data(self, data, format_type):
        """解析不同格式的数据"""
        
        if format_type == "hrs9531":
            # HRS9531标准格式
            df = data[['SUBJID', 'LBDTC', 'LBORRES']].copy()
            df['datetime'] = pd.to_datetime(df['LBDTC'])
            df['glucose'] = pd.to_numeric(df['LBORRES'], errors='coerce')
            df['subject_id'] = df['SUBJID']
            
        elif format_type == "simple":
            # 简化格式
            df = data.copy()
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            elif 'timestamp' in df.columns:
                df['datetime'] = pd.to_datetime(df['timestamp'])
            
            # 查找血糖列
            glucose_cols = [col for col in df.columns if 'glucose' in col.lower() or 'bg' in col.lower() or 'value' in col.lower()]
            if glucose_cols:
                df['glucose'] = pd.to_numeric(df[glucose_cols[0]], errors='coerce')
            
            df['subject_id'] = 'Patient_1'  # 默认单患者
            
        else:
            # 通用格式尝试
            df = data.copy()
            datetime_cols = [col for col in df.columns if any(x in col.lower() for x in ['time', 'date', 'datetime'])]
            if datetime_cols:
                df['datetime'] = pd.to_datetime(df[datetime_cols[0]])
            
            value_cols = [col for col in df.columns if any(x in col.lower() for x in ['glucose', 'value', 'bg', 'result'])]
            if value_cols:
                df['glucose'] = pd.to_numeric(df[value_cols[0]], errors='coerce')
            
            df['subject_id'] = 'Patient_1'
        
        # 数据清理
        df = df.dropna(subset=['datetime', 'glucose'])
        df = df[(df['glucose'] >= 1.0) & (df['glucose'] <= 30.0)]  # 合理血糖范围
        df = df.sort_values(['subject_id', 'datetime'])
        
        return df[['subject_id', 'datetime', 'glucose']]
    
    def analyze_morning_patterns(self, subject_id=None, days_window=7):
        """
        分析清晨血糖升高模式
        
        Args:
            subject_id: 患者ID，None表示分析所有患者
            days_window: 分析天数窗口
        """
        if self.glucose_data is None:
            print("❌ 请先加载数据")
            return
        
        subjects = [subject_id] if subject_id else self.glucose_data['subject_id'].unique()
        
        for subj in subjects:
            print(f"\n🔍 分析患者：{subj}")
            subject_data = self.glucose_data[self.glucose_data['subject_id'] == subj].copy()
            
            # 按日期分组分析
            subject_data['date'] = subject_data['datetime'].dt.date
            daily_patterns = []
            
            for date in subject_data['date'].unique()[:days_window]:
                daily_data = subject_data[subject_data['date'] == date]
                if len(daily_data) < 20:  # 数据点太少跳过
                    continue
                    
                pattern = self._analyze_single_day(daily_data, date)
                if pattern:
                    daily_patterns.append(pattern)
            
            # 汇总分析结果
            if daily_patterns:
                summary = self._summarize_patterns(subj, daily_patterns)
                self.analysis_results.append(summary)
                self._print_analysis_results(summary)
    
    def _analyze_single_day(self, daily_data, date):
        """分析单日血糖模式"""
        # 提取关键时间段数据
        morning_data = self._extract_morning_period(daily_data)
        night_data = self._extract_night_period(daily_data)
        
        if len(morning_data) < 5 or len(night_data) < 10:
            return None
        
        # 检测清晨血糖升高
        morning_rise = self._detect_morning_rise(morning_data)
        if not morning_rise:
            return None
        
        # 分析夜间模式
        night_pattern = self._analyze_night_pattern(night_data)
        
        # 分析上升特征
        rise_characteristics = self._analyze_rise_characteristics(morning_data)
        
        # 模式分类评分
        scores = self._calculate_pattern_scores(night_pattern, rise_characteristics)
        
        return {
            'date': date,
            'morning_rise': morning_rise,
            'night_pattern': night_pattern,
            'rise_characteristics': rise_characteristics,
            'scores': scores,
            'classification': self._classify_pattern(scores)
        }
    
    def _extract_morning_period(self, daily_data):
        """提取清晨时段数据 (3:00-9:00)"""
        return daily_data[
            (daily_data['datetime'].dt.hour >= 3) & 
            (daily_data['datetime'].dt.hour <= 9)
        ].copy()
    
    def _extract_night_period(self, daily_data):
        """提取夜间时段数据 (22:00-6:00)"""
        return daily_data[
            (daily_data['datetime'].dt.hour >= 22) | 
            (daily_data['datetime'].dt.hour <= 6)
        ].copy()
    
    def _detect_morning_rise(self, morning_data):
        """检测清晨血糖升高事件"""
        if len(morning_data) < 5:
            return None
        
        glucose_values = morning_data['glucose'].values
        start_bg = np.mean(glucose_values[:3])  # 前3个点平均
        peak_bg = np.max(glucose_values)
        end_bg = np.mean(glucose_values[-3:])  # 后3个点平均
        
        rise_amount = peak_bg - start_bg
        
        if rise_amount >= 1.5:  # 血糖上升≥1.5 mmol/L才考虑
            peak_time = morning_data.iloc[np.argmax(glucose_values)]['datetime']
            return {
                'start_glucose': start_bg,
                'peak_glucose': peak_bg,
                'end_glucose': end_bg,
                'rise_amount': rise_amount,
                'peak_time': peak_time,
                'rise_detected': True
            }
        
        return None
    
    def _analyze_night_pattern(self, night_data):
        """分析夜间血糖模式"""
        if len(night_data) < 10:
            return {}
        
        glucose_values = night_data['glucose'].values
        min_glucose = np.min(glucose_values)
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        
        # 检测低血糖
        hypoglycemia = min_glucose < 3.9
        severe_hypo = min_glucose < 3.0
        
        # 检测血糖下降趋势
        if len(glucose_values) >= 6:
            early_night = np.mean(glucose_values[:len(glucose_values)//3])
            late_night = np.mean(glucose_values[-len(glucose_values)//3:])
            glucose_decline = early_night - late_night
        else:
            glucose_decline = 0
        
        return {
            'min_glucose': min_glucose,
            'mean_glucose': mean_glucose,
            'glucose_variability': std_glucose,
            'has_hypoglycemia': hypoglycemia,
            'has_severe_hypo': severe_hypo,
            'glucose_decline': glucose_decline,
            'stable_night': std_glucose < 1.0
        }
    
    def _analyze_rise_characteristics(self, morning_data):
        """分析血糖上升特征"""
        if len(morning_data) < 5:
            return {}
        
        glucose_values = morning_data['glucose'].values
        time_values = morning_data['datetime'].values
        
        # 计算上升速率
        time_diff = (time_values[-1] - time_values[0]) / np.timedelta64(1, 'h')  # 小时
        if time_diff > 0:
            rise_rate = (glucose_values[-1] - glucose_values[0]) / time_diff
        else:
            rise_rate = 0
        
        # 分析上升模式
        # 计算30分钟窗口内的最大上升速率
        max_rise_rate = 0
        for i in range(len(glucose_values) - 2):
            window_time = (time_values[i+2] - time_values[i]) / np.timedelta64(1, 'h')
            if window_time > 0:
                window_rate = (glucose_values[i+2] - glucose_values[i]) / window_time
                max_rise_rate = max(max_rise_rate, window_rate)
        
        # 判断上升模式
        gradual_rise = max_rise_rate < 2.0  # 缓慢上升
        rapid_rise = max_rise_rate > 4.0    # 快速上升
        
        # 持续时间
        rise_duration = time_diff
        
        return {
            'average_rise_rate': rise_rate,
            'max_rise_rate': max_rise_rate,
            'gradual_rise': gradual_rise,
            'rapid_rise': rapid_rise,
            'rise_duration': rise_duration,
            'consistent_pattern': np.std(np.diff(glucose_values)) < 0.8
        }
    
    def _calculate_pattern_scores(self, night_pattern, rise_characteristics):
        """计算各种模式的评分"""
        dawn_score = 0
        somogyi_score = 0
        food_score = 0
        
        # 黎明现象评分
        if rise_characteristics.get('gradual_rise', False):
            dawn_score += 2
        if rise_characteristics.get('consistent_pattern', False):
            dawn_score += 2
        if night_pattern.get('stable_night', False):
            dawn_score += 2
        if not night_pattern.get('has_hypoglycemia', False):
            dawn_score += 2
        if 2.0 <= rise_characteristics.get('average_rise_rate', 0) <= 4.0:
            dawn_score += 1
        
        # 苏木杰效应评分
        if night_pattern.get('has_hypoglycemia', False):
            somogyi_score += 3
        if night_pattern.get('has_severe_hypo', False):
            somogyi_score += 2
        if night_pattern.get('glucose_decline', 0) > 2.0:
            somogyi_score += 2
        if rise_characteristics.get('max_rise_rate', 0) > 4.0:
            somogyi_score += 2
        if not rise_characteristics.get('consistent_pattern', False):
            somogyi_score += 1
        
        # 进食相关评分
        if rise_characteristics.get('rapid_rise', False):
            food_score += 3
        if rise_characteristics.get('max_rise_rate', 0) > 6.0:
            food_score += 2
        if rise_characteristics.get('rise_duration', 0) < 2.0:
            food_score += 2
        if not rise_characteristics.get('gradual_rise', False):
            food_score += 1
        
        return {
            'dawn_phenomenon': dawn_score,
            'somogyi_effect': somogyi_score,
            'food_related': food_score
        }
    
    def _classify_pattern(self, scores):
        """根据评分分类模式"""
        max_score = max(scores.values())
        
        if max_score < 4:
            return "未分类/混合因素"
        
        if scores['dawn_phenomenon'] == max_score:
            return "黎明现象"
        elif scores['somogyi_effect'] == max_score:
            return "苏木杰效应"
        elif scores['food_related'] == max_score:
            return "进食相关"
        else:
            return "未分类/混合因素"
    
    def _summarize_patterns(self, subject_id, daily_patterns):
        """汇总分析结果"""
        classifications = [p['classification'] for p in daily_patterns]
        
        # 统计各类型出现频率
        from collections import Counter
        pattern_counts = Counter(classifications)
        
        # 计算平均评分
        avg_scores = {
            'dawn_phenomenon': np.mean([p['scores']['dawn_phenomenon'] for p in daily_patterns]),
            'somogyi_effect': np.mean([p['scores']['somogyi_effect'] for p in daily_patterns]),
            'food_related': np.mean([p['scores']['food_related'] for p in daily_patterns])
        }
        
        # 主要模式判断和置信度计算
        main_pattern = pattern_counts.most_common(1)[0][0]
        
        # 改进的置信度计算方法
        confidence = self._calculate_enhanced_confidence(daily_patterns, main_pattern, pattern_counts)
        
        return {
            'subject_id': subject_id,
            'analysis_days': len(daily_patterns),
            'pattern_distribution': dict(pattern_counts),
            'main_pattern': main_pattern,
            'confidence': confidence,
            'average_scores': avg_scores,
            'daily_details': daily_patterns
        }
    
    def _print_analysis_results(self, summary):
        """打印分析结果"""
        print(f"\n📊 患者 {summary['subject_id']} 分析结果：")
        print(f"   分析天数: {summary['analysis_days']} 天")
        print(f"   主要模式: {summary['main_pattern']} (置信度: {summary['confidence']:.1%})")
        
        print("\n   模式分布:")
        for pattern, count in summary['pattern_distribution'].items():
            percentage = count / summary['analysis_days'] * 100
            print(f"     {pattern}: {count}天 ({percentage:.1f}%)")
        
        print("\n   平均评分:")
        for pattern, score in summary['average_scores'].items():
            pattern_name = {'dawn_phenomenon': '黎明现象', 
                          'somogyi_effect': '苏木杰效应', 
                          'food_related': '进食相关'}[pattern]
            print(f"     {pattern_name}: {score:.1f}分")
        
        # 显示置信度计算详情
        if hasattr(self, '_last_confidence_details'):
            self._print_confidence_breakdown()
        
        # 详细的日期模式分析
        self._print_detailed_daily_analysis(summary)
        
        # 给出临床建议
        self._provide_clinical_recommendations(summary)
    
    def _print_detailed_daily_analysis(self, summary):
        """打印详细的每日模式分析"""
        print("\n📅 详细日期分析:")
        
        daily_patterns = summary['daily_details']
        
        # 按模式分组显示
        pattern_groups = {
            '黎明现象': [],
            '苏木杰效应': [],
            '进食相关': [],
            '未分类/混合因素': []
        }
        
        for pattern in daily_patterns:
            classification = pattern['classification']
            date_str = pattern['date'].strftime('%Y-%m-%d')
            
            # 提取关键信息
            morning_rise = pattern['morning_rise']
            night_pattern = pattern['night_pattern']
            scores = pattern['scores']
            
            detail_info = {
                'date': date_str,
                'rise_amount': morning_rise['rise_amount'] if morning_rise else 0,
                'peak_time': morning_rise['peak_time'].strftime('%H:%M') if morning_rise else 'N/A',
                'night_min': night_pattern.get('min_glucose', 'N/A'),
                'has_hypo': night_pattern.get('has_hypoglycemia', False),
                'scores': scores
            }
            
            pattern_groups[classification].append(detail_info)
        
        # 显示每种模式的详细信息
        for pattern_type, details in pattern_groups.items():
            if details:
                print(f"\n   🔸 {pattern_type} ({len(details)}天):")
                for detail in details:
                    print(f"     {detail['date']}: ", end="")
                    print(f"升高{detail['rise_amount']:.1f}mmol/L (峰值{detail['peak_time']}), ", end="")
                    print(f"夜间最低{detail['night_min']:.1f}mmol/L", end="")
                    if detail['has_hypo']:
                        print(" ⚠️低血糖", end="")
                    print(f" [评分: 黎明{detail['scores']['dawn_phenomenon']:.1f}/苏木杰{detail['scores']['somogyi_effect']:.1f}/进食{detail['scores']['food_related']:.1f}]")
        
        # 混合模式特别提醒
        mixed_patterns = len([p for p in daily_patterns if self._is_mixed_pattern(p['scores'])])
        if mixed_patterns > 0:
            print(f"\n   ⚠️  发现 {mixed_patterns} 天存在模式重叠或难以区分的情况")
            print("      这些日期需要结合临床情况进一步分析:")
            for pattern in daily_patterns:
                if self._is_mixed_pattern(pattern['scores']):
                    date_str = pattern['date'].strftime('%Y-%m-%d')
                    scores = pattern['scores']
                    max_score = max(scores.values())
                    if max_score < 5:  # 评分都不高
                        print(f"        {date_str}: 各模式评分接近，需要更多信息判断")
                    else:
                        # 找到评分接近的模式
                        high_score_patterns = [k for k, v in scores.items() if v >= max_score - 1]
                        if len(high_score_patterns) > 1:
                            pattern_names = [{'dawn_phenomenon': '黎明现象', 'somogyi_effect': '苏木杰效应', 'food_related': '进食相关'}[p] for p in high_score_patterns]
                            print(f"        {date_str}: {'/'.join(pattern_names)} 模式重叠")
    
    def _is_mixed_pattern(self, scores):
        """判断是否为混合模式"""
        sorted_scores = sorted(scores.values(), reverse=True)
        # 如果最高分和第二高分差距小于2分，或者最高分小于5分，认为是混合模式
        return (sorted_scores[0] - sorted_scores[1] < 2) or (sorted_scores[0] < 5)
    
    def _calculate_enhanced_confidence(self, daily_patterns, main_pattern, pattern_counts):
        """计算增强版置信度"""
        total_days = len(daily_patterns)
        main_pattern_days = pattern_counts[main_pattern]
        
        # 1. 基础频率置信度
        frequency_confidence = main_pattern_days / total_days
        
        # 2. 评分强度置信度
        main_pattern_key = {
            '黎明现象': 'dawn_phenomenon',
            '苏木杰效应': 'somogyi_effect', 
            '进食相关': 'food_related',
            '未分类/混合因素': None
        }.get(main_pattern)
        
        if main_pattern_key:
            # 获取主模式的评分
            main_scores = [p['scores'][main_pattern_key] for p in daily_patterns 
                          if p['classification'] == main_pattern]
            
            # 计算评分强度 (归一化到0-1)
            if main_scores:
                avg_score = np.mean(main_scores)
                max_possible_score = 10  # 理论最大评分
                score_confidence = min(avg_score / max_possible_score, 1.0)
            else:
                score_confidence = 0
        else:
            score_confidence = 0
        
        # 3. 模式区分度置信度
        mixed_days = len([p for p in daily_patterns if self._is_mixed_pattern(p['scores'])])
        distinction_confidence = 1 - (mixed_days / total_days)
        
        # 4. 时间连续性置信度 (连续天数越多，置信度越高)
        continuity_confidence = self._calculate_continuity_confidence(daily_patterns, main_pattern)
        
        # 综合置信度计算 (加权平均)
        weights = {
            'frequency': 0.4,      # 频率权重40%
            'score': 0.3,          # 评分强度权重30%  
            'distinction': 0.2,    # 模式区分度权重20%
            'continuity': 0.1      # 时间连续性权重10%
        }
        
        enhanced_confidence = (
            frequency_confidence * weights['frequency'] +
            score_confidence * weights['score'] + 
            distinction_confidence * weights['distinction'] +
            continuity_confidence * weights['continuity']
        )
        
        # 保存计算详情用于显示
        self._last_confidence_details = {
            'frequency': frequency_confidence,
            'score': score_confidence,
            'distinction': distinction_confidence, 
            'continuity': continuity_confidence,
            'weights': weights,
            'final': enhanced_confidence
        }
        
        return enhanced_confidence
    
    def _print_confidence_breakdown(self):
        """打印置信度计算详情"""
        details = self._last_confidence_details
        print(f"\n   📈 置信度计算详情 (最终: {details['final']:.1%}):")
        print(f"     频率置信度: {details['frequency']:.1%} (权重 {details['weights']['frequency']:.0%})")
        print(f"     评分强度: {details['score']:.1%} (权重 {details['weights']['score']:.0%})")
        print(f"     模式区分度: {details['distinction']:.1%} (权重 {details['weights']['distinction']:.0%})")
        print(f"     时间连续性: {details['continuity']:.1%} (权重 {details['weights']['continuity']:.0%})")
    
    def _calculate_continuity_confidence(self, daily_patterns, main_pattern):
        """计算时间连续性置信度"""
        # 按日期排序
        sorted_patterns = sorted(daily_patterns, key=lambda x: x['date'])
        
        # 找到最长连续序列
        max_continuous = 0
        current_continuous = 0
        
        for pattern in sorted_patterns:
            if pattern['classification'] == main_pattern:
                current_continuous += 1
                max_continuous = max(max_continuous, current_continuous)
            else:
                current_continuous = 0
        
        # 连续性置信度 = 最长连续天数 / 总天数
        continuity_confidence = max_continuous / len(daily_patterns)
        
        return continuity_confidence
    
    def _provide_clinical_recommendations(self, summary):
        """提供临床建议"""
        print("\n💡 临床建议:")
        
        main_pattern = summary['main_pattern']
        confidence = summary['confidence']
        
        if confidence < 0.6:
            print("     ⚠️  模式不够明确，建议:")
            print("        - 延长监测时间")
            print("        - 记录详细的饮食和用药时间")
            print("        - 考虑多种因素共同作用")
        
        elif main_pattern == "黎明现象":
            print("     ✅ 主要为黎明现象，建议:")
            print("        - 调整晚餐时间和药物剂量")
            print("        - 考虑使用长效胰岛素")
            print("        - 避免睡前加餐")
            
        elif main_pattern == "苏木杰效应":
            print("     ⚠️  存在苏木杰效应，建议:")
            print("        - 减少睡前胰岛素剂量")
            print("        - 调整晚餐后用药时间")
            print("        - 睡前适量加餐")
            print("        - 密切监测夜间血糖")
            
        elif main_pattern == "进食相关":
            print("     🍽️ 主要与进食相关，建议:")
            print("        - 调整早餐时间和内容")
            print("        - 优化餐前用药时间")
            print("        - 记录详细饮食日志")
        
        else:
            print("     📝 模式复杂，建议综合管理:")
            print("        - 详细记录生活作息")
            print("        - 个体化调整治疗方案")
            print("        - 定期复评血糖模式")
    
    def plot_analysis_results(self, subject_id=None, save_plot=False):
        """输出分析结果摘要 (不生成图表)"""
        if not self.analysis_results:
            print("❌ 没有分析结果可输出")
            return
        
        subjects = [r for r in self.analysis_results if subject_id is None or r['subject_id'] == subject_id]
        
        for summary in subjects:
            self._output_analysis_summary(summary)
    
    def _output_analysis_summary(self, summary):
        """输出分析摘要 (替代图表)"""
        print(f"\n📈 {summary['subject_id']} 分析摘要:")
        print(f"   监测天数: {summary['analysis_days']}天")
        print(f"   主要模式: {summary['main_pattern']}")
        print(f"   置信度: {summary['confidence']:.1%}")
        
        # 输出统计数据而非图表
        daily_patterns = summary['daily_details']
        rise_amounts = [p['morning_rise']['rise_amount'] for p in daily_patterns if p['morning_rise']]
        
        if rise_amounts:
            print(f"   平均血糖升高: {np.mean(rise_amounts):.1f} mmol/L")
            print(f"   升高范围: {np.min(rise_amounts):.1f} - {np.max(rise_amounts):.1f} mmol/L")
        
        print("   ✅ 分析完成，无图表生成")

# 示例使用函数
def analyze_sample_data():
    """分析示例数据"""
    analyzer = MorningGlucoseAnalyzer()
    
    print("🔍 清晨血糖升高模式分析工具")
    print("=" * 50)
    
    # 尝试加载HengRui文件夹中的数据
    sample_files = [
        "/Users/williamsun/Documents/gplus/docs/HengRui/HRS9531_305_standardized_simulation.csv",
        "/Users/williamsun/Documents/gplus/HRS9531_305_cgms_simulation.csv",
        "/Users/williamsun/Documents/gplus/4million_cgms_simulation.csv"
    ]
    
    for file_path in sample_files:
        print(f"\n🔄 尝试加载文件: {file_path}")
        if analyzer.load_data(file_path):
            print("✅ 数据加载成功，开始分析...")
            
            # 分析前几个患者
            subjects = analyzer.glucose_data['subject_id'].unique()[:3]  # 分析前3个患者
            
            for subject in subjects:
                analyzer.analyze_morning_patterns(subject_id=subject, days_window=7)
            
            # 输出结果摘要
            print(f"\n📊 输出分析摘要...")
            analyzer.plot_analysis_results()
            
            break
    else:
        print("❌ 未找到可用的数据文件")
        print("\n💡 使用方法:")
        print("   analyzer = MorningGlucoseAnalyzer()")
        print("   analyzer.load_data('your_data_file.csv')")
        print("   analyzer.analyze_morning_patterns()")
        print("   analyzer.plot_analysis_results()")

if __name__ == "__main__":
    analyze_sample_data()