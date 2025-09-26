#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能转折点检测系统 - API调用示例
演示如何在生产环境中集成和使用智能转折点检测功能
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from Test_Intelligent_Nodes import test_intelligent_nodes
from Intelligent_Segmentation import IntelligentSegmentationAnalyzer

class TurningPointsAPI:
    """智能转折点检测API封装"""
    
    def __init__(self, min_segment_days=1, max_segments=8):
        """
        初始化API
        
        Args:
            min_segment_days (int): 最小分段天数，默认1天
            max_segments (int): 最大分段数量，默认8段
        """
        self.analyzer = IntelligentSegmentationAnalyzer(
            min_segment_days=min_segment_days,
            max_segments=max_segments
        )
        
    def analyze_from_arrays(self, glucose_values, timestamps, patient_id=None):
        """
        从数组数据进行分析
        
        Args:
            glucose_values (list): 血糖数值列表
            timestamps (list): 时间戳列表 (字符串或datetime对象)
            patient_id (str): 患者ID，可选
            
        Returns:
            dict: 完整分析结果
        """
        try:
            # 数据预处理
            df = pd.DataFrame({
                'glucose': glucose_values,
                'timestamp': pd.to_datetime(timestamps)
            })
            df = df.sort_values('timestamp')
            
            # 计算监测天数
            total_days = (df['timestamp'].max() - df['timestamp'].min()).days + 1
            
            # 执行分析
            result = self.analyzer.analyze_intelligent_segments(
                df, 
                np.array(glucose_values), 
                total_days
            )
            
            # 添加患者信息
            if patient_id:
                result['patient_id'] = patient_id
                result['analysis_time'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'patient_id': patient_id,
                'status': 'failed'
            }
    
    def analyze_from_file(self, file_path, patient_name=None):
        """
        从文件进行分析（推荐用于完整分析）
        
        Args:
            file_path (str): Excel文件路径
            patient_name (str): 患者姓名
            
        Returns:
            dict: 完整分析结果
        """
        return test_intelligent_nodes(file_path, patient_name)
    
    def extract_key_insights(self, analysis_result):
        """
        提取关键见解，适合临床快速查看
        
        Args:
            analysis_result (dict): 完整分析结果
            
        Returns:
            dict: 关键见解摘要
        """
        if 'error' in analysis_result:
            return analysis_result
            
        try:
            segments = analysis_result.get('最终分段', [])
            quality = analysis_result.get('分段评估', {})
            
            # 基础信息
            insights = {
                'patient_id': analysis_result.get('patient_id', 'Unknown'),
                'analysis_time': analysis_result.get('analysis_time'),
                'segments_count': len(segments),
                'quality_score': quality.get('分段质量评分', 'N/A'),
                'quality_level': quality.get('质量等级', 'N/A')
            }
            
            # 分段信息
            insights['segments'] = []
            for i, seg in enumerate(segments, 1):
                insights['segments'].append({
                    'segment_id': i,
                    'duration_days': seg['duration_days'],
                    'start_time': seg['start_time'],
                    'end_time': seg['end_time']
                })
            
            # 趋势分析
            trend_analysis = analysis_result.get('段间差异分析', {}).get('段间差异统计', {})
            if trend_analysis:
                insights['overall_trend'] = trend_analysis.get('总体趋势', '未知')
                insights['improved_indicators'] = trend_analysis.get('改善指标数', 0)
                insights['worsened_indicators'] = trend_analysis.get('恶化指标数', 0)
                
                # 最显著变化
                if '最显著改善' in trend_analysis:
                    insights['best_improvement'] = {
                        'indicator': trend_analysis['最显著改善']['指标'],
                        'improvement': trend_analysis['最显著改善']['改善幅度']
                    }
                
                if '最显著恶化' in trend_analysis:
                    insights['worst_deterioration'] = {
                        'indicator': trend_analysis['最显著恶化']['指标'],
                        'deterioration': trend_analysis['最显著恶化']['恶化幅度']
                    }
            
            return insights
            
        except Exception as e:
            return {
                'error': f'提取见解时出错: {str(e)}',
                'patient_id': analysis_result.get('patient_id', 'Unknown')
            }

def demo_usage():
    """演示API使用方法"""
    
    print("🚀 智能转折点检测API演示")
    print("="*50)
    
    # 创建API实例
    api = TurningPointsAPI(min_segment_days=1, max_segments=6)
    
    # 演示1: 从数组数据分析
    print("\n📊 演示1: 从数组数据分析")
    
    # 模拟14天血糖数据 (每5分钟一个点)
    start_time = datetime.now() - timedelta(days=14)
    timestamps = []
    glucose_values = []
    
    for i in range(14 * 24 * 12):  # 14天 * 24小时 * 12个点/小时
        timestamps.append(start_time + timedelta(minutes=5*i))
        
        # 模拟血糖数据：前7天高变异，后7天逐步改善
        if i < 14 * 24 * 6:  # 前7天
            base_glucose = 14.0 + np.random.normal(0, 3.0)
        else:  # 后7天
            base_glucose = 10.0 + np.random.normal(0, 1.5)
        
        glucose_values.append(max(4.0, min(25.0, base_glucose)))
    
    # 执行分析
    result = api.analyze_from_arrays(glucose_values, timestamps, "DEMO_001")
    
    if 'error' not in result:
        print("✅ 分析成功完成")
        print(f"检测到 {len(result['最终分段'])} 个分段")
        
        # 提取关键见解
        insights = api.extract_key_insights(result)
        print("\n🎯 关键见解:")
        print(f"  质量评分: {insights['quality_score']}")
        print(f"  整体趋势: {insights.get('overall_trend', '未知')}")
        print(f"  改善指标: {insights.get('improved_indicators', 0)}个")
        print(f"  恶化指标: {insights.get('worsened_indicators', 0)}个")
        
        # 显示分段信息
        print("\n📋 分段详情:")
        for seg in insights['segments']:
            print(f"  第{seg['segment_id']}段: {seg['duration_days']:.1f}天 "
                  f"({seg['start_time'][:16]} ~ {seg['end_time'][:16]})")
    else:
        print(f"❌ 分析失败: {result['error']}")
    
    print("\n" + "="*50)
    print("🎉 演示完成！")

def integration_example():
    """集成到现有系统的示例"""
    
    class HospitalSystemIntegration:
        """医院系统集成示例"""
        
        def __init__(self):
            self.turning_points_api = TurningPointsAPI()
        
        def analyze_patient_cgm_data(self, patient_id, cgm_data):
            """
            分析患者CGM数据的完整流程
            
            Args:
                patient_id (str): 患者ID
                cgm_data (dict): CGM数据，包含glucose_values和timestamps
                
            Returns:
                dict: 标准化的分析结果
            """
            
            # Step 1: 数据验证
            if not self._validate_cgm_data(cgm_data):
                return {'success': False, 'message': '数据格式不正确'}
            
            # Step 2: 执行转折点分析
            analysis_result = self.turning_points_api.analyze_from_arrays(
                cgm_data['glucose_values'],
                cgm_data['timestamps'],
                patient_id
            )
            
            if 'error' in analysis_result:
                return {'success': False, 'message': analysis_result['error']}
            
            # Step 3: 提取关键见解
            insights = self.turning_points_api.extract_key_insights(analysis_result)
            
            # Step 4: 格式化为医院系统标准格式
            formatted_result = self._format_for_hospital_system(
                patient_id, insights, analysis_result
            )
            
            return {'success': True, 'data': formatted_result}
        
        def _validate_cgm_data(self, cgm_data):
            """验证CGM数据格式"""
            required_keys = ['glucose_values', 'timestamps']
            if not all(key in cgm_data for key in required_keys):
                return False
            
            if len(cgm_data['glucose_values']) != len(cgm_data['timestamps']):
                return False
                
            if len(cgm_data['glucose_values']) < 288:  # 至少1天数据
                return False
                
            return True
        
        def _format_for_hospital_system(self, patient_id, insights, full_result):
            """格式化为医院系统标准格式"""
            return {
                'patient_id': patient_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'turning_points_count': insights['segments_count'],
                'quality_assessment': {
                    'score': insights['quality_score'],
                    'level': insights['quality_level']
                },
                'clinical_summary': {
                    'overall_trend': insights.get('overall_trend', '未评估'),
                    'improvement_indicators': insights.get('improved_indicators', 0),
                    'deterioration_indicators': insights.get('worsened_indicators', 0)
                },
                'segments': insights['segments'],
                'recommendations': full_result.get('分段评估', {}).get('建议', []),
                'detailed_analysis': full_result  # 完整分析结果
            }
    
    # 使用示例
    hospital_system = HospitalSystemIntegration()
    
    # 模拟CGM数据
    sample_cgm_data = {
        'glucose_values': [8.5, 9.2, 12.1, 15.3] * 400,  # 模拟数据
        'timestamps': [datetime.now() - timedelta(minutes=5*i) for i in range(1600)]
    }
    
    result = hospital_system.analyze_patient_cgm_data("P12345", sample_cgm_data)
    
    if result['success']:
        print("✅ 医院系统集成测试成功")
        data = result['data']
        print(f"患者ID: {data['patient_id']}")
        print(f"转折点数量: {data['turning_points_count']}")
        print(f"整体趋势: {data['clinical_summary']['overall_trend']}")
    else:
        print(f"❌ 集成测试失败: {result['message']}")

if __name__ == "__main__":
    # 运行演示
    demo_usage()
    
    print("\n" + "="*50)
    print("🏥 医院系统集成示例")
    print("="*50)
    
    # 运行集成示例
    integration_example()