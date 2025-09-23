#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指尖血糖数据处理脚本
用于处理多个患者的指尖血糖CSV数据，支持多日数据

作者: Claude
创建日期: 2025-09-07
更新日期: 2025-09-07
编码: UTF-8
"""

import pandas as pd
import numpy as np
import re
import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SMBGDataProcessor:
    """指尖血糖数据处理器 - 支持多日数据"""
    
    def __init__(self, csv_file_path: str):
        """
        初始化处理器
        
        Args:
            csv_file_path (str): CSV文件路径
        """
        self.csv_file_path = csv_file_path
        self.raw_data = None
        self.processed_data = []
        
        # 定义血糖测量时间点
        self.time_points = [
            '凌晨', '早餐前', '早餐后', '午餐前', 
            '午餐后', '晚餐前', '晚餐后', '睡前', '随机'
        ]
        
        # 定义CSV列名（更新后的格式）
        self.expected_columns = [
            '案例编号', '日期', '凌晨', '早餐前', '早餐后', 
            '午餐前', '午餐后', '晚餐前', '晚餐后', '睡前', '随机'
        ]
        
        # 定义正常血糖参考范围（mmol/L）
        self.glucose_ranges = {
            '空腹': {'normal': (3.9, 6.1), 'prediabetic': (6.1, 7.0), 'diabetic': 7.0},
            '餐后2小时': {'normal': (3.9, 7.8), 'prediabetic': (7.8, 11.1), 'diabetic': 11.1},
            '随机': {'normal': (3.9, 7.8), 'prediabetic': (7.8, 11.1), 'diabetic': 11.1}
        }

    def load_data(self) -> pd.DataFrame:
        """
        加载CSV数据，并验证列格式
        
        Returns:
            pd.DataFrame: 原始数据
        """
        try:
            self.raw_data = pd.read_csv(
                self.csv_file_path, 
                encoding='utf-8',
                sep=',',
                dtype={'案例编号': str, '日期': str}  # 确保案例编号和日期为字符串
            )
            
            # 验证列名
            if list(self.raw_data.columns) != self.expected_columns:
                logger.warning(f"CSV列名可能不匹配预期格式")
                logger.info(f"实际列名: {list(self.raw_data.columns)}")
                logger.info(f"期望列名: {self.expected_columns}")
            
            # 预处理日期列
            self.raw_data = self._preprocess_date_column(self.raw_data)
            
            logger.info(f"成功加载数据，共{len(self.raw_data)}行记录")
            return self.raw_data
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            raise

    def _preprocess_date_column(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理日期列，支持多种日期格式
        
        Args:
            data (pd.DataFrame): 原始数据
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        if '日期' not in data.columns:
            logger.warning("未找到'日期'列")
            return data
        
        # 处理日期格式
        for idx, date_val in enumerate(data['日期']):
            if pd.isna(date_val) or date_val == '':
                continue
                
            date_str = str(date_val).strip()
            
            # 尝试解析不同的日期格式
            parsed_date = self._parse_date_format(date_str)
            if parsed_date:
                data.loc[idx, '日期'] = parsed_date
            else:
                logger.warning(f"无法解析日期格式: {date_str}")
        
        return data
    
    def _parse_date_format(self, date_str: str) -> Optional[str]:
        """
        解析日期格式，支持多种格式
        
        Args:
            date_str (str): 日期字符串
            
        Returns:
            Optional[str]: 标准化的日期字符串
        """
        # 支持的日期格式
        date_patterns = [
            r'D(\d+)',  # D1, D2, D3 格式
            r'Day(\d+)',  # Day1, Day2, Day3 格式
            r'第(\d+)天',  # 第1天, 第2天 格式
            r'(\d{4}-\d{1,2}-\d{1,2})',  # 2023-12-31 格式
            r'(\d{4}/\d{1,2}/\d{1,2})',  # 2023/12/31 格式
            r'(\d{1,2}-\d{1,2})',  # 12-31 格式
            r'(\d{1,2}/\d{1,2})'   # 12/31 格式
        ]
        
        for pattern in date_patterns:
            match = re.match(pattern, date_str, re.IGNORECASE)
            if match:
                if pattern.startswith(r'D(\d+)') or pattern.startswith(r'Day(\d+)') or pattern.startswith(r'第(\d+)天'):
                    # 转换为标准的D1, D2格式
                    return f"D{match.group(1)}"
                else:
                    # 保持日期格式
                    return match.group(1)
        
        return date_str  # 如果都不匹配，返回原字符串

    def parse_random_glucose(self, random_data: str) -> List[Dict]:
        """
        解析随机血糖列中的多个数据和时间
        
        Args:
            random_data (str): 随机血糖列的原始数据
            
        Returns:
            List[Dict]: 解析后的血糖数据列表
        """
        if pd.isna(random_data) or random_data == '':
            return []
        
        random_records = []
        
        # 尝试多种格式的正则表达式
        patterns = [
            r'(\d{1,2}:\d{2})\s*[：:]\s*(\d+\.?\d*)',  # 时间:血糖值
            r'(\d+\.?\d*)\s*[@在]\s*(\d{1,2}:\d{2})',  # 血糖值@时间
            r'(\d{1,2}:\d{2})\s*(\d+\.?\d*)',         # 时间 血糖值
            r'(\d+\.?\d*)\s*(\d{1,2}:\d{2})'          # 血糖值 时间
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, str(random_data))
            if matches:
                for match in matches:
                    try:
                        # 判断哪个是时间，哪个是血糖值
                        if ':' in match[0]:
                            time_str, glucose_val = match[0], match[1]
                        else:
                            glucose_val, time_str = match[0], match[1]
                        
                        random_records.append({
                            'time': time_str,
                            'glucose': float(glucose_val),
                            'raw_data': random_data
                        })
                    except (ValueError, IndexError) as e:
                        logger.warning(f"解析随机血糖数据失败: {match}, 错误: {e}")
                break
        
        return random_records

    def classify_glucose_level(self, glucose_value: float, measurement_type: str = '随机') -> str:
        """
        根据血糖值分类血糖水平
        
        Args:
            glucose_value (float): 血糖值
            measurement_type (str): 测量类型
            
        Returns:
            str: 血糖水平分类
        """
        if pd.isna(glucose_value) or glucose_value <= 0:
            return '无效'
        
        ranges = self.glucose_ranges.get(measurement_type, self.glucose_ranges['随机'])
        
        if glucose_value < ranges['normal'][0]:
            return '低血糖'
        elif glucose_value <= ranges['normal'][1]:
            return '正常'
        elif glucose_value <= ranges['prediabetic'][1]:
            return '糖尿病前期'
        else:
            return '糖尿病范围'

    def calculate_glucose_statistics(self, glucose_values: List[float]) -> Dict:
        """
        计算血糖统计指标
        
        Args:
            glucose_values (List[float]): 血糖值列表
            
        Returns:
            Dict: 统计指标
        """
        valid_values = [v for v in glucose_values if not pd.isna(v) and v > 0]
        
        if not valid_values:
            return {
                'count': 0,
                'mean': None,
                'median': None,
                'std': None,
                'min': None,
                'max': None,
                'cv': None,  # 变异系数
                'range': None
            }
        
        mean_val = np.mean(valid_values)
        std_val = np.std(valid_values, ddof=1) if len(valid_values) > 1 else 0
        
        return {
            'count': len(valid_values),
            'mean': round(mean_val, 2),
            'median': round(np.median(valid_values), 2),
            'std': round(std_val, 2),
            'min': round(min(valid_values), 2),
            'max': round(max(valid_values), 2),
            'cv': round((std_val / mean_val) * 100, 2) if mean_val != 0 else 0,  # 变异系数百分比
            'range': round(max(valid_values) - min(valid_values), 2)
        }

    def calculate_glucose_management_indicators(self, glucose_values: List[float], measurement_days: int = 1) -> Dict:
        """
        计算血糖管理指标（GMI相关参数）
        
        Args:
            glucose_values (List[float]): 血糖值列表
            measurement_days (int): 测量天数
            
        Returns:
            Dict: 血糖管理指标
        """
        valid_values = [v for v in glucose_values if not pd.isna(v) and v > 0]
        
        if not valid_values:
            return {
                'measurement_days': measurement_days,
                'measurement_coverage': 0,
                'average_glucose': None,
                'time_in_range': 0,
                'gmi': None,
                'level1_hypoglycemia': 0,
                'level2_hypoglycemia': 0,
                'cv': 0,
                'level1_hyperglycemia': 0,
                'level2_hyperglycemia': 0
            }
        
        total_measurements = len(valid_values)
        expected_measurements = measurement_days * 8  # 每日8次测量
        measurement_coverage = round((total_measurements / expected_measurements) * 100, 2) if expected_measurements > 0 else 0
        
        # 血糖分布统计
        mean_glucose = np.mean(valid_values)
        
        # TIR: 目标范围内时间 (3.9-10.0 mmol/L)
        tir_count = sum(1 for v in valid_values if 3.9 <= v <= 10.0)
        time_in_range = round((tir_count / total_measurements) * 100, 2)
        
        # GMI计算 (基于平均血糖的估算糖化血红蛋白)
        # GMI(%) = 3.31 + 0.02392 × 平均血糖(mg/dL)
        # 转换mmol/L到mg/dL: mmol/L × 18.018
        mean_glucose_mgdl = mean_glucose * 18.018
        gmi = round(3.31 + 0.02392 * mean_glucose_mgdl, 2)
        
        # 1级低血糖 TBR (3.0-3.8 mmol/L)
        level1_hypo_count = sum(1 for v in valid_values if 3.0 <= v < 3.9)
        level1_hypoglycemia = round((level1_hypo_count / total_measurements) * 100, 2)
        
        # 2级低血糖 TBR (<3.0 mmol/L)
        level2_hypo_count = sum(1 for v in valid_values if v < 3.0)
        level2_hypoglycemia = round((level2_hypo_count / total_measurements) * 100, 2)
        
        # 变异系数 CV
        cv = round((np.std(valid_values, ddof=1) / mean_glucose) * 100, 2) if mean_glucose != 0 and len(valid_values) > 1 else 0
        
        # 1级高血糖 TAR (10.1-13.9 mmol/L)
        level1_hyper_count = sum(1 for v in valid_values if 10.1 <= v <= 13.9)
        level1_hyperglycemia = round((level1_hyper_count / total_measurements) * 100, 2)
        
        # 2级高血糖 TAR (>13.9 mmol/L)
        level2_hyper_count = sum(1 for v in valid_values if v > 13.9)
        level2_hyperglycemia = round((level2_hyper_count / total_measurements) * 100, 2)
        
        return {
            'measurement_days': measurement_days,
            'measurement_coverage': measurement_coverage,  # 参数2
            'average_glucose': round(mean_glucose, 2),     # 参数3
            'time_in_range': time_in_range,               # 参数4
            'gmi': gmi,                                   # 参数5
            'level1_hypoglycemia': level1_hypoglycemia,   # 参数6
            'level2_hypoglycemia': level2_hypoglycemia,   # 参数7
            'cv': cv,                                     # 参数8
            'level1_hyperglycemia': level1_hyperglycemia, # 参数9
            'level2_hyperglycemia': level2_hyperglycemia  # 参数10
        }

    def calculate_daily_gmi_parameters(self, daily_glucose_values: List[float]) -> Dict:
        """
        计算单日血糖管理指标
        
        Args:
            daily_glucose_values (List[float]): 单日血糖值列表
            
        Returns:
            Dict: 单日血糖管理指标
        """
        return self.calculate_glucose_management_indicators(daily_glucose_values, measurement_days=1)

    def process_patient_data(self, patient_id: str, patient_records: pd.DataFrame) -> Dict:
        """
        处理单个患者的多日数据
        
        Args:
            patient_id (str): 患者编号
            patient_records (pd.DataFrame): 患者记录
            
        Returns:
            Dict: 处理后的患者数据
        """
        patient_data = {
            'patient_id': patient_id,
            'total_records': len(patient_records),
            'measurement_days': [],
            'daily_data': {},
            'time_points': {},
            'random_measurements': [],
            'statistics': {},
            'daily_statistics': {},
            'glucose_distribution': {},
            'multi_day_analysis': {}
        }
        
        all_glucose_values = []
        daily_glucose_data = {}
        
        # 按日期分组处理数据
        if '日期' in patient_records.columns:
            unique_dates = patient_records['日期'].dropna().unique()
            patient_data['measurement_days'] = sorted(unique_dates)
            
            for date_val in unique_dates:
                date_records = patient_records[patient_records['日期'] == date_val]
                daily_glucose_values = []
                daily_time_points = {}
                daily_random_measurements = []
                
                # 处理该日期的固定时间点血糖数据
                for time_point in self.time_points[:-1]:  # 除了"随机"
                    if time_point in date_records.columns:
                        values = []
                        for _, row in date_records.iterrows():
                            value = row[time_point]
                            if not pd.isna(value) and value != '':
                                try:
                                    glucose_val = float(value)
                                    values.append(glucose_val)
                                    daily_glucose_values.append(glucose_val)
                                    all_glucose_values.append(glucose_val)
                                except ValueError:
                                    logger.warning(f"患者{patient_id}在{date_val}的{time_point}数据格式错误: {value}")
                        
                        daily_time_points[time_point] = {
                            'values': values,
                            'statistics': self.calculate_glucose_statistics(values)
                        }
                
                # 处理该日期的随机血糖数据
                if '随机' in date_records.columns:
                    for _, row in date_records.iterrows():
                        random_data = row['随机']
                        random_records = self.parse_random_glucose(random_data)
                        for record in random_records:
                            record['date'] = date_val  # 添加日期信息
                            daily_random_measurements.append(record)
                            patient_data['random_measurements'].append(record)
                            daily_glucose_values.append(record['glucose'])
                            all_glucose_values.append(record['glucose'])
                
                # 计算该日期的统计数据
                daily_stats = self.calculate_glucose_statistics(daily_glucose_values)
                daily_gmi_params = self.calculate_daily_gmi_parameters(daily_glucose_values)
                daily_glucose_data[date_val] = {
                    'date': date_val,
                    'time_points': daily_time_points,
                    'random_measurements': daily_random_measurements,
                    'statistics': daily_stats,
                    'gmi_parameters': daily_gmi_params,
                    'glucose_values': daily_glucose_values
                }
        
        else:
            # 如果没有日期列，按原方式处理
            logger.warning(f"患者{patient_id}缺少日期列，按单日处理")
            daily_glucose_values = []
            
            # 处理固定时间点的血糖数据
            for time_point in self.time_points[:-1]:  # 除了"随机"
                if time_point in patient_records.columns:
                    values = []
                    for _, row in patient_records.iterrows():
                        value = row[time_point]
                        if not pd.isna(value) and value != '':
                            try:
                                glucose_val = float(value)
                                values.append(glucose_val)
                                all_glucose_values.append(glucose_val)
                            except ValueError:
                                logger.warning(f"患者{patient_id}的{time_point}数据格式错误: {value}")
                    
                    patient_data['time_points'][time_point] = {
                        'values': values,
                        'statistics': self.calculate_glucose_statistics(values)
                    }
            
            # 处理随机血糖数据
            if '随机' in patient_records.columns:
                for _, row in patient_records.iterrows():
                    random_data = row['随机']
                    random_records = self.parse_random_glucose(random_data)
                    for record in random_records:
                        patient_data['random_measurements'].append(record)
                        all_glucose_values.append(record['glucose'])
        
        # 存储每日数据
        patient_data['daily_data'] = daily_glucose_data
        
        # 汇总所有时间点的数据（跨多日）
        for time_point in self.time_points[:-1]:
            all_time_point_values = []
            for daily_data in daily_glucose_data.values():
                if time_point in daily_data['time_points']:
                    all_time_point_values.extend(daily_data['time_points'][time_point]['values'])
            
            patient_data['time_points'][time_point] = {
                'values': all_time_point_values,
                'statistics': self.calculate_glucose_statistics(all_time_point_values)
            }
        
        # 计算总体统计（所有日期汇总）
        patient_data['statistics'] = self.calculate_glucose_statistics(all_glucose_values)
        
        # 计算血糖管理指标（GMI相关参数）
        measurement_days = len(patient_data['measurement_days']) if patient_data['measurement_days'] else 1
        patient_data['gmi_parameters'] = self.calculate_glucose_management_indicators(all_glucose_values, measurement_days)
        
        # 计算每日统计汇总
        daily_means = []
        daily_cvs = []
        daily_counts = []
        for daily_data in daily_glucose_data.values():
            if daily_data['statistics']['mean'] is not None:
                daily_means.append(daily_data['statistics']['mean'])
                daily_cvs.append(daily_data['statistics']['cv'])
                daily_counts.append(daily_data['statistics']['count'])
        
        patient_data['daily_statistics'] = {
            'measurement_days_count': len(daily_glucose_data),
            'avg_daily_mean': round(np.mean(daily_means), 2) if daily_means else None,
            'avg_daily_cv': round(np.mean(daily_cvs), 2) if daily_cvs else None,
            'avg_daily_measurements': round(np.mean(daily_counts), 2) if daily_counts else None,
            'daily_means': daily_means,
            'daily_cvs': daily_cvs,
            'daily_counts': daily_counts
        }
        
        # 多日分析指标
        patient_data['multi_day_analysis'] = self._calculate_multi_day_metrics(daily_glucose_data)
        
        # 血糖分布统计（汇总所有日期）
        glucose_distribution = {'低血糖': 0, '正常': 0, '糖尿病前期': 0, '糖尿病范围': 0, '无效': 0}
        for glucose_val in all_glucose_values:
            level = self.classify_glucose_level(glucose_val)
            glucose_distribution[level] += 1
        
        patient_data['glucose_distribution'] = glucose_distribution
        
        return patient_data
    
    def _calculate_multi_day_metrics(self, daily_glucose_data: Dict) -> Dict:
        """
        计算多日血糖指标
        
        Args:
            daily_glucose_data (Dict): 每日血糖数据
            
        Returns:
            Dict: 多日分析指标
        """
        if not daily_glucose_data:
            return {}
        
        daily_means = []
        day_to_day_changes = []
        consistent_days = 0  # 血糖控制一致的天数
        
        prev_mean = None
        for date_val in sorted(daily_glucose_data.keys()):
            daily_data = daily_glucose_data[date_val]
            if daily_data['statistics']['mean'] is not None:
                current_mean = daily_data['statistics']['mean']
                daily_means.append(current_mean)
                
                if prev_mean is not None:
                    change = current_mean - prev_mean
                    day_to_day_changes.append(abs(change))
                    
                    # 判断是否为一致控制（变化小于10%）
                    if abs(change / prev_mean) <= 0.1:
                        consistent_days += 1
                
                prev_mean = current_mean
        
        multi_day_metrics = {
            'day_to_day_variability': {
                'mean_change': round(np.mean(day_to_day_changes), 2) if day_to_day_changes else None,
                'max_change': round(max(day_to_day_changes), 2) if day_to_day_changes else None,
                'consistent_days_ratio': round(consistent_days / len(daily_means), 2) if len(daily_means) > 1 else None
            },
            'trend_analysis': {
                'overall_trend': 'stable',  # 可以进一步实现趋势分析
                'daily_mean_cv': round(np.std(daily_means) / np.mean(daily_means) * 100, 2) if len(daily_means) > 1 and np.mean(daily_means) != 0 else None
            }
        }
        
        # 简单趋势分析
        if len(daily_means) >= 3:
            first_half_mean = np.mean(daily_means[:len(daily_means)//2])
            second_half_mean = np.mean(daily_means[len(daily_means)//2:])
            
            if second_half_mean > first_half_mean * 1.1:
                multi_day_metrics['trend_analysis']['overall_trend'] = 'increasing'
            elif second_half_mean < first_half_mean * 0.9:
                multi_day_metrics['trend_analysis']['overall_trend'] = 'decreasing'
            else:
                multi_day_metrics['trend_analysis']['overall_trend'] = 'stable'
        
        return multi_day_metrics

    def process_all_data(self) -> List[Dict]:
        """
        处理所有患者数据
        
        Returns:
            List[Dict]: 所有患者的处理结果
        """
        if self.raw_data is None:
            raise ValueError("请先加载数据")
        
        # 按案例编号分组
        grouped_data = self.raw_data.groupby('案例编号')
        
        for patient_id, patient_records in grouped_data:
            logger.info(f"处理患者: {patient_id}")
            patient_data = self.process_patient_data(patient_id, patient_records)
            self.processed_data.append(patient_data)
        
        logger.info(f"共处理{len(self.processed_data)}个患者的数据")
        return self.processed_data

    def generate_summary_report(self) -> Dict:
        """
        生成汇总报告
        
        Returns:
            Dict: 汇总报告
        """
        if not self.processed_data:
            return {}
        
        summary = {
            'total_patients': len(self.processed_data),
            'total_measurements': 0,
            'overall_statistics': {},
            'time_point_coverage': {},
            'glucose_distribution_summary': {'低血糖': 0, '正常': 0, '糖尿病前期': 0, '糖尿病范围': 0}
        }
        
        all_glucose_values = []
        time_point_counts = {tp: 0 for tp in self.time_points[:-1]}
        
        for patient in self.processed_data:
            summary['total_measurements'] += patient['statistics']['count']
            
            # 收集所有血糖值
            for time_point, data in patient['time_points'].items():
                all_glucose_values.extend(data['values'])
                time_point_counts[time_point] += len(data['values'])
            
            # 收集随机测量值
            for random_record in patient['random_measurements']:
                all_glucose_values.append(random_record['glucose'])
            
            # 汇总血糖分布
            for level, count in patient['glucose_distribution'].items():
                if level in summary['glucose_distribution_summary']:
                    summary['glucose_distribution_summary'][level] += count
        
        # 计算总体统计
        summary['overall_statistics'] = self.calculate_glucose_statistics(all_glucose_values)
        summary['time_point_coverage'] = time_point_counts
        
        return summary

    def save_results(self, output_dir: str = None):
        """
        保存处理结果
        
        Args:
            output_dir (str): 输出目录，默认为CSV文件同级目录
        """
        if output_dir is None:
            output_dir = os.path.dirname(self.csv_file_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存详细结果
        detailed_file = os.path.join(output_dir, 'smbg_detailed_results.json')
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_data, f, ensure_ascii=False, indent=2)
        
        # 保存汇总报告
        summary = self.generate_summary_report()
        summary_file = os.path.join(output_dir, 'smbg_summary_report.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 生成CSV格式的患者统计表
        self.generate_patient_summary_csv(output_dir)
        
        logger.info(f"结果已保存到目录: {output_dir}")

    def generate_patient_summary_csv(self, output_dir: str):
        """
        生成患者汇总CSV表格（支持多日数据）
        
        Args:
            output_dir (str): 输出目录
        """
        summary_data = []
        
        for patient in self.processed_data:
            row = {
                '患者编号': patient['patient_id'],
                '总记录数': patient['total_records'],
                '总测量次数': patient['statistics']['count'],
                '平均血糖': patient['statistics']['mean'],
                '血糖中位数': patient['statistics']['median'],
                '血糖标准差': patient['statistics']['std'],
                '最低血糖': patient['statistics']['min'],
                '最高血糖': patient['statistics']['max'],
                '变异系数(CV%)': patient['statistics']['cv'],
                '血糖范围': patient['statistics']['range'],
                '低血糖次数': patient['glucose_distribution']['低血糖'],
                '正常血糖次数': patient['glucose_distribution']['正常'],
                '糖尿病前期次数': patient['glucose_distribution']['糖尿病前期'],
                '糖尿病范围次数': patient['glucose_distribution']['糖尿病范围']
            }
            
            # 添加多日数据统计（如果有）
            if 'multi_day_analysis' in patient and patient['multi_day_analysis']:
                multi_day = patient['multi_day_analysis']
                row['测量天数'] = len(patient.get('daily_data', {}))
                
                # 获取日间变异系数
                if 'trend_analysis' in multi_day and multi_day['trend_analysis']['daily_mean_cv']:
                    row['日间变异系数'] = multi_day['trend_analysis']['daily_mean_cv']
                else:
                    row['日间变异系数'] = None
                
                # 获取趋势方向
                if 'trend_analysis' in multi_day and multi_day['trend_analysis']['overall_trend']:
                    row['血糖趋势'] = multi_day['trend_analysis']['overall_trend']
                else:
                    row['血糖趋势'] = 'stable'
                
                # 获取日间平均变化
                if 'day_to_day_variability' in multi_day and multi_day['day_to_day_variability']['mean_change']:
                    row['日间平均变化'] = multi_day['day_to_day_variability']['mean_change']
                else:
                    row['日间平均变化'] = None
            else:
                row['测量天数'] = 1
                row['日间变异系数'] = None
                row['血糖趋势'] = 'stable'
                row['日间平均变化'] = None
            
            # 添加各时间点测量次数和平均值
            for time_point in self.time_points[:-1]:
                if time_point in patient['time_points']:
                    row[f'{time_point}_测量次数'] = patient['time_points'][time_point]['statistics']['count']
                    row[f'{time_point}_平均值'] = patient['time_points'][time_point]['statistics']['mean']
                else:
                    row[f'{time_point}_测量次数'] = 0
                    row[f'{time_point}_平均值'] = None
            
            row['随机测量次数'] = len(patient['random_measurements'])
            
            # 添加血糖管理指标（10个参数）
            if 'gmi_parameters' in patient:
                gmi_params = patient['gmi_parameters']
                # 注意：这里的“measurement_days”和“measurement_coverage”已经在前面的多日数据中处理了
                row['测量覆盖率(%)'] = gmi_params.get('measurement_coverage', 0)       # 参数2
                row['平均葡萄糖'] = gmi_params.get('average_glucose', None)            # 参数3
                row['目标范围内时间TIR(%)'] = gmi_params.get('time_in_range', 0)   # 参数4
                row['葡萄糖管理指标GMI(%)'] = gmi_params.get('gmi', None)          # 参数5
                row['1级低血糖TBR(%)'] = gmi_params.get('level1_hypoglycemia', 0)      # 参数6
                row['2级低血糖TBR(%)'] = gmi_params.get('level2_hypoglycemia', 0)      # 参数7
                row['变异系数CV(%)'] = gmi_params.get('cv', 0)                       # 参数8
                row['1级高血糖TAR(%)'] = gmi_params.get('level1_hyperglycemia', 0)     # 参数9
                row['2级高血糖TAR(%)'] = gmi_params.get('level2_hyperglycemia', 0)     # 参数10
            else:
                # 默认值
                row['测量覆盖率(%)'] = 0
                row['平均葡萄糖'] = None
                row['目标范围内时间TIR(%)'] = 0
                row['葡萄糖管理指标GMI(%)'] = None
                row['1级低血糖TBR(%)'] = 0
                row['2级低血糖TBR(%)'] = 0
                row['变异系数CV(%)'] = 0
                row['1级高血糖TAR(%)'] = 0
                row['2级高血糖TAR(%)'] = 0
            
            summary_data.append(row)
        
        # 保存为CSV
        summary_df = pd.DataFrame(summary_data)
        csv_file = os.path.join(output_dir, 'patient_summary.csv')
        summary_df.to_csv(csv_file, index=False, encoding='utf-8-sig')  # 使用utf-8-sig确保Excel正确显示中文
        
        logger.info(f"患者汇总表已保存: {csv_file}")
        logger.info(f"表格包含 {len(summary_data)} 个患者的多日统计数据")


def main():
    """主函数示例"""
    # 示例用法
    csv_file_path = "/Users/williamsun/Documents/gplus/docs/SMBG_CV/sample_data.csv"
    
    # 创建处理器
    processor = SMBGDataProcessor(csv_file_path)
    
    try:
        # 加载数据
        processor.load_data()
        
        # 处理数据
        processor.process_all_data()
        
        # 保存结果
        processor.save_results()
        
        # 生成汇总报告
        summary = processor.generate_summary_report()
        print("\n=== 汇总报告 ===")
        print(f"总患者数: {summary['total_patients']}")
        print(f"总测量次数: {summary['total_measurements']}")
        print(f"平均血糖: {summary['overall_statistics']['mean']} mmol/L")
        print(f"血糖变异系数: {summary['overall_statistics']['cv']}%")
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        raise


if __name__ == "__main__":
    main()