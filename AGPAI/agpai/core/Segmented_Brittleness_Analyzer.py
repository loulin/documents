#!/usr/bin/env python3
"""
分段脆性分析器
结合切点检测和脆性分析，专门用于胰腺外科等断崖式治疗调整场景
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Treatment_Cutpoint_Detector import TreatmentCutpointDetector
from Brittleness_Clinical_Advisor import BrittlenessClinicalAdvisor
from Manual_Cutpoint_Manager import ManualCutpointManager

class SegmentedBrittlenessAnalyzer:
    """
    分段脆性分析器
    专门用于识别治疗调整前后的脆性变化
    """
    
    def __init__(self):
        """初始化分段脆性分析器"""
        self.analyzer_name = "Segmented Brittleness Analyzer"
        self.version = "1.0.0"
        
        # 初始化组件
        self.cutpoint_detector = TreatmentCutpointDetector()
        self.brittleness_advisor = BrittlenessClinicalAdvisor()
        self.manual_cutpoint_manager = ManualCutpointManager()
        
        # 分析参数
        self.analysis_params = {
            'min_segment_hours': 48,       # 最小分析段长度
            'cutpoint_methods': ['comprehensive'],  # 切点检测方法
            'brittleness_confidence': 0.8   # 脆性分型置信度阈值
        }
    
    def analyze_with_cutpoints(self, 
                              glucose_data: np.ndarray,
                              timestamps: np.ndarray,
                              patient_info: Dict,
                              detect_cutpoints: bool = True,
                              manual_cutpoints: Optional[List[Dict]] = None,
                              merge_strategy: str = 'prioritize_manual') -> Dict:
        """
        带切点检测的脆性分析 - 支持手动切点
        
        Args:
            glucose_data: 血糖数据
            timestamps: 时间戳
            patient_info: 患者信息
            detect_cutpoints: 是否进行自动切点检测
            manual_cutpoints: 手动添加的切点列表
            merge_strategy: 切点合并策略
            
        Returns:
            完整的分段分析结果
        """
        analysis_result = {
            'patient_info': patient_info,
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'total_data_points': len(glucose_data),
            'time_range': {
                'start': str(timestamps[0]),
                'end': str(timestamps[-1]),
                'duration_hours': (timestamps[-1] - timestamps[0]) / np.timedelta64(1, 'h')
            }
        }
        
        # 处理切点
        final_cutpoints = []
        
        # 1. 处理手动切点
        if manual_cutpoints:
            print(f"📝 处理 {len(manual_cutpoints)} 个手动切点...")
            validated_manual_cutpoints = []
            
            for manual_cp in manual_cutpoints:
                # 验证手动切点
                validation = self.manual_cutpoint_manager.validate_cutpoint_timing(
                    manual_cp, glucose_data, timestamps
                )
                manual_cp['validation'] = validation
                validated_manual_cutpoints.append(manual_cp)
                
                print(f"   ✅ {manual_cp.get('type', 'Unknown')}: {manual_cp.get('timestamp')}")
                if validation['warnings']:
                    for warning in validation['warnings']:
                        print(f"      ⚠️ {warning}")
            
            final_cutpoints.extend(validated_manual_cutpoints)
        
        # 2. 自动检测切点（如果启用）
        detected_cutpoints = []
        if detect_cutpoints:
            print("🔍 自动检测治疗调整切点...")
            detected_cutpoints = self.cutpoint_detector.detect_cutpoints(
                glucose_data, timestamps, method='comprehensive'
            )
            print(f"   发现 {len(detected_cutpoints)} 个算法检测切点")
        
        # 3. 合并切点
        if manual_cutpoints and detected_cutpoints:
            print(f"🔄 合并切点 (策略: {merge_strategy})...")
            final_cutpoints = self.manual_cutpoint_manager.merge_cutpoints(
                manual_cutpoints, detected_cutpoints, merge_strategy
            )
        elif detected_cutpoints:
            final_cutpoints = detected_cutpoints
        
        analysis_result['cutpoints'] = final_cutpoints
        analysis_result['manual_cutpoints'] = manual_cutpoints or []
        analysis_result['detected_cutpoints'] = detected_cutpoints
        analysis_result['merge_strategy'] = merge_strategy
        analysis_result['cutpoint_count'] = len(final_cutpoints)
        
        if final_cutpoints:
            # 分割数据段
            print(f"📊 基于 {len(final_cutpoints)} 个切点进行分段分析...")
            segments = self.cutpoint_detector.analyze_segments(
                glucose_data, timestamps, final_cutpoints
            )
            
            # 3. 分段脆性分析
            segment_analyses = []
            for segment in segments:
                segment_analysis = self._analyze_segment_brittleness(segment, patient_info)
                segment_analyses.append(segment_analysis)
            
            analysis_result['segments'] = segment_analyses
            analysis_result['segment_count'] = len(segments)
            
            # 4. 段间比较
            if len(segments) > 1:
                print("🆚 进行段间治疗效果比较...")
                comparison = self.cutpoint_detector.compare_segments(segments)
                segment_brittleness_comparison = self._compare_segment_brittleness(segment_analyses)
                
                analysis_result['segment_comparison'] = comparison
                analysis_result['brittleness_comparison'] = segment_brittleness_comparison
                analysis_result['treatment_effectiveness'] = self._assess_treatment_effectiveness(
                    segment_analyses, comparison
                )
        else:
            # 整段分析
            print("📈 进行整段脆性分析...")
            whole_analysis = self._analyze_whole_data(glucose_data, timestamps, patient_info)
            analysis_result.update(whole_analysis)
        
        return analysis_result
    
    def _analyze_segment_brittleness(self, segment: Dict, patient_info: Dict) -> Dict:
        """分析单个片段的脆性特征"""
        glucose_data = segment['glucose_data']
        segment_info = {
            'segment_id': segment['segment_id'],
            'type': segment['type'],
            'duration_hours': segment['duration_hours'],
            'data_points': len(glucose_data)
        }
        
        try:
            # 脆性分析
            brittleness_result = self.brittleness_advisor.generate_brittleness_report(
                glucose_data, 
                f"{patient_info.get('name', 'Patient')}_Segment_{segment['segment_id']}", 
                patient_info
            )
            
            # 提取关键指标
            segment_analysis = {
                'segment_info': segment_info,
                'basic_metrics': {
                    'mean_glucose': segment.get('mean_glucose', np.mean(glucose_data)),
                    'glucose_std': segment.get('glucose_std', np.std(glucose_data)),
                    'cv': segment.get('cv', np.std(glucose_data)/np.mean(glucose_data)*100),
                    'glucose_range': segment.get('glucose_range', np.max(glucose_data) - np.min(glucose_data))
                },
                'brittleness_analysis': brittleness_result,
                'chaos_indicators': self.brittleness_advisor._calculate_chaos_indicators(glucose_data),
                'clinical_assessment': self._assess_segment_clinical_status(segment, glucose_data)
            }
            
        except Exception as e:
            print(f"⚠️ 片段 {segment['segment_id']} 分析失败: {e}")
            segment_analysis = {
                'segment_info': segment_info,
                'error': str(e),
                'basic_metrics': {
                    'mean_glucose': np.mean(glucose_data),
                    'glucose_std': np.std(glucose_data),
                    'cv': np.std(glucose_data)/np.mean(glucose_data)*100
                }
            }
        
        return segment_analysis
    
    def _assess_segment_clinical_status(self, segment: Dict, glucose_data: np.ndarray) -> Dict:
        """评估片段的临床状态"""
        mean_glucose = np.mean(glucose_data)
        cv = np.std(glucose_data) / mean_glucose * 100
        
        # TIR计算
        tir = np.sum((glucose_data >= 3.9) & (glucose_data <= 10.0)) / len(glucose_data) * 100
        tbr = np.sum(glucose_data < 3.9) / len(glucose_data) * 100
        tar = np.sum(glucose_data > 10.0) / len(glucose_data) * 100
        
        # 临床评估
        clinical_status = {
            'tir': tir,
            'tbr': tbr,
            'tar': tar,
            'glycemic_control': self._classify_glycemic_control(tir, cv),
            'safety_profile': self._assess_safety_profile(tbr, np.min(glucose_data)),
            'stability_profile': self._assess_stability(cv, np.std(glucose_data))
        }
        
        # 胰腺外科专项评估
        if 'type' in segment and 'post_treatment' in segment['type']:
            clinical_status['post_surgical_status'] = self._assess_post_surgical_status(
                glucose_data, mean_glucose, cv
            )
        
        return clinical_status
    
    def _classify_glycemic_control(self, tir: float, cv: float) -> str:
        """分类血糖控制水平"""
        if tir >= 70 and cv < 36:
            return "excellent"
        elif tir >= 50 and cv < 50:
            return "good"  
        elif tir >= 30:
            return "fair"
        else:
            return "poor"
    
    def _assess_safety_profile(self, tbr: float, min_glucose: float) -> str:
        """评估安全性"""
        if tbr == 0 and min_glucose > 3.0:
            return "very_safe"
        elif tbr < 1 and min_glucose > 2.5:
            return "safe"
        elif tbr < 5:
            return "moderate_risk"
        else:
            return "high_risk"
    
    def _assess_stability(self, cv: float, std: float) -> str:
        """评估稳定性"""
        if cv < 20:
            return "very_stable"
        elif cv < 30:
            return "stable"
        elif cv < 40:
            return "moderate_variability"
        else:
            return "high_variability"
    
    def _assess_post_surgical_status(self, glucose_data: np.ndarray, 
                                   mean_glucose: float, cv: float) -> Dict:
        """评估术后血糖状态"""
        return {
            'pancreatic_function': self._estimate_pancreatic_function(mean_glucose, cv),
            'insulin_sensitivity': self._estimate_insulin_sensitivity(glucose_data),
            'metabolic_adaptation': self._assess_metabolic_adaptation(glucose_data),
            'recovery_indicator': self._calculate_recovery_score(glucose_data, mean_glucose, cv)
        }
    
    def _estimate_pancreatic_function(self, mean_glucose: float, cv: float) -> str:
        """估计胰腺功能状态"""
        if mean_glucose < 10 and cv < 30:
            return "preserved"
        elif mean_glucose < 15 and cv < 50:
            return "impaired"
        else:
            return "severely_impaired"
    
    def _estimate_insulin_sensitivity(self, glucose_data: np.ndarray) -> str:
        """估计胰岛素敏感性"""
        # 简化的估计方法，基于血糖模式
        dawn_phenomenon = self._detect_dawn_phenomenon(glucose_data)
        postprandial_excursion = np.std(glucose_data)  # 简化指标
        
        if not dawn_phenomenon and postprandial_excursion < 2:
            return "high"
        elif postprandial_excursion < 4:
            return "normal"
        else:
            return "low"
    
    def _detect_dawn_phenomenon(self, glucose_data: np.ndarray) -> bool:
        """检测黎明现象（简化版）"""
        # 这里需要时间信息，简化处理
        return False
    
    def _assess_metabolic_adaptation(self, glucose_data: np.ndarray) -> str:
        """评估代谢适应性"""
        # 基于血糖变化模式评估
        autocorr = np.corrcoef(glucose_data[:-1], glucose_data[1:])[0, 1] if len(glucose_data) > 1 else 0
        
        if autocorr > 0.7:
            return "good_adaptation"
        elif autocorr > 0.3:
            return "moderate_adaptation"
        else:
            return "poor_adaptation"
    
    def _calculate_recovery_score(self, glucose_data: np.ndarray, 
                                mean_glucose: float, cv: float) -> float:
        """计算恢复评分 (0-100)"""
        # 目标：均值接近7-8 mmol/L，低变异性
        mean_score = max(0, 100 - abs(mean_glucose - 7.5) * 10)
        cv_score = max(0, 100 - cv * 2)
        stability_score = self._calculate_stability_score(glucose_data)
        
        return (mean_score * 0.4 + cv_score * 0.4 + stability_score * 0.2)
    
    def _calculate_stability_score(self, glucose_data: np.ndarray) -> float:
        """计算稳定性评分"""
        if len(glucose_data) < 10:
            return 0
        
        # 基于自相关和趋势强度
        from scipy import stats
        autocorr = np.corrcoef(glucose_data[:-1], glucose_data[1:])[0, 1] if len(glucose_data) > 1 else 0
        trend_strength = abs(stats.linregress(range(len(glucose_data)), glucose_data)[2])
        
        stability = (abs(autocorr) * 50 + (1 - trend_strength) * 50)
        return max(0, min(100, stability))
    
    def _compare_segment_brittleness(self, segment_analyses: List[Dict]) -> Dict:
        """比较各段的脆性特征"""
        if len(segment_analyses) < 2:
            return {'error': '需要至少2个片段进行脆性比较'}
        
        comparison = {
            'brittleness_changes': [],
            'chaos_indicator_changes': [],
            'clinical_improvements': []
        }
        
        for i in range(len(segment_analyses) - 1):
            pre_analysis = segment_analyses[i]
            post_analysis = segment_analyses[i + 1]
            
            # 脆性类型变化
            pre_brittleness = pre_analysis.get('brittleness_analysis', {}).get('分型结果', 'Unknown')
            post_brittleness = post_analysis.get('brittleness_analysis', {}).get('分型结果', 'Unknown')
            
            brittleness_change = {
                'from_segment': pre_analysis['segment_info']['segment_id'],
                'to_segment': post_analysis['segment_info']['segment_id'],
                'brittleness_change': f"{pre_brittleness} → {post_brittleness}",
                'improvement': self._assess_brittleness_improvement(pre_brittleness, post_brittleness)
            }
            comparison['brittleness_changes'].append(brittleness_change)
            
            # 混沌指标变化
            pre_chaos = pre_analysis.get('chaos_indicators', {})
            post_chaos = post_analysis.get('chaos_indicators', {})
            
            chaos_change = {
                'from_segment': pre_analysis['segment_info']['segment_id'],
                'to_segment': post_analysis['segment_info']['segment_id'],
                'lyapunov_change': post_chaos.get('lyapunov_exponent', 0) - pre_chaos.get('lyapunov_exponent', 0),
                'entropy_change': post_chaos.get('approximate_entropy', 0) - pre_chaos.get('approximate_entropy', 0),
                'hurst_change': post_chaos.get('hurst_exponent', 0.5) - pre_chaos.get('hurst_exponent', 0.5)
            }
            comparison['chaos_indicator_changes'].append(chaos_change)
            
            # 临床改善评估
            pre_clinical = pre_analysis.get('clinical_assessment', {})
            post_clinical = post_analysis.get('clinical_assessment', {})
            
            clinical_improvement = {
                'from_segment': pre_analysis['segment_info']['segment_id'],
                'to_segment': post_analysis['segment_info']['segment_id'],
                'tir_improvement': post_clinical.get('tir', 0) - pre_clinical.get('tir', 0),
                'control_improvement': post_clinical.get('glycemic_control', '') != pre_clinical.get('glycemic_control', ''),
                'safety_improvement': post_clinical.get('safety_profile', '') != pre_clinical.get('safety_profile', '')
            }
            comparison['clinical_improvements'].append(clinical_improvement)
        
        return comparison
    
    def _assess_brittleness_improvement(self, pre_type: str, post_type: str) -> str:
        """评估脆性类型变化是否为改善"""
        improvement_hierarchy = {
            '稳定型': 5,
            'V型频域脆性': 4, 
            'IV型记忆缺失脆性': 3,
            'II型准周期脆性': 2,
            'III型随机脆性': 1,
            'I型混沌脆性': 0
        }
        
        pre_score = improvement_hierarchy.get(pre_type, 0)
        post_score = improvement_hierarchy.get(post_type, 0)
        
        if post_score > pre_score:
            return "improved"
        elif post_score == pre_score:
            return "unchanged"
        else:
            return "worsened"
    
    def _assess_treatment_effectiveness(self, segment_analyses: List[Dict], 
                                     comparison: Dict) -> Dict:
        """评估整体治疗效果"""
        if len(segment_analyses) < 2:
            return {'error': '无法评估治疗效果'}
        
        # 提取关键改善指标
        improvements = {
            'glycemic_control': 0,
            'brittleness_stability': 0,
            'safety_profile': 0,
            'overall_score': 0
        }
        
        # 统计改善情况
        brittleness_changes = comparison.get('brittleness_changes', [])
        clinical_improvements = comparison.get('clinical_improvements', [])
        
        for change in brittleness_changes:
            if change['improvement'] == 'improved':
                improvements['brittleness_stability'] += 1
        
        for improvement in clinical_improvements:
            if improvement['tir_improvement'] > 0:
                improvements['glycemic_control'] += 1
            if improvement['safety_improvement']:
                improvements['safety_profile'] += 1
        
        # 整体评分
        total_changes = len(brittleness_changes)
        if total_changes > 0:
            improvements['overall_score'] = (
                improvements['glycemic_control'] * 40 + 
                improvements['brittleness_stability'] * 40 + 
                improvements['safety_profile'] * 20
            ) / total_changes
        
        # 治疗推荐
        effectiveness_assessment = {
            'improvements': improvements,
            'recommendation': self._generate_treatment_recommendation(improvements, segment_analyses),
            'next_steps': self._suggest_next_steps(segment_analyses[-1])
        }
        
        return effectiveness_assessment
    
    def _generate_treatment_recommendation(self, improvements: Dict, 
                                         segment_analyses: List[Dict]) -> str:
        """生成治疗建议"""
        overall_score = improvements.get('overall_score', 0)
        
        if overall_score >= 80:
            return "治疗效果优秀，继续当前方案"
        elif overall_score >= 60:
            return "治疗效果良好，可适当优化"
        elif overall_score >= 40:
            return "治疗效果一般，需要调整方案"
        else:
            return "治疗效果不佳，建议重新制定方案"
    
    def _suggest_next_steps(self, latest_segment: Dict) -> List[str]:
        """建议下一步措施"""
        suggestions = []
        
        clinical_assessment = latest_segment.get('clinical_assessment', {})
        brittleness_type = latest_segment.get('brittleness_analysis', {}).get('分型结果', '')
        
        # 基于脆性类型的建议
        if 'I型混沌脆性' in brittleness_type:
            suggestions.append("考虑胰岛素泵治疗或连续血糖监测")
        elif 'IV型记忆缺失脆性' in brittleness_type:
            suggestions.append("建立规律的血糖监测和饮食计划")
        
        # 基于TIR的建议
        tir = clinical_assessment.get('tir', 0)
        if tir < 50:
            suggestions.append("优先改善血糖控制达标率")
        
        # 安全性建议
        safety = clinical_assessment.get('safety_profile', '')
        if 'high_risk' in safety:
            suggestions.append("密切监测低血糖风险，调整治疗强度")
        
        if not suggestions:
            suggestions.append("继续监测，保持当前治疗方案")
        
        return suggestions
    
    def _analyze_whole_data(self, glucose_data: np.ndarray, 
                          timestamps: np.ndarray, patient_info: Dict) -> Dict:
        """整段数据分析（无切点检测）"""
        brittleness_result = self.brittleness_advisor.generate_brittleness_report(
            glucose_data, patient_info.get('name', 'Patient'), patient_info
        )
        
        return {
            'analysis_type': 'whole_data',
            'brittleness_analysis': brittleness_result,
            'basic_metrics': {
                'mean_glucose': np.mean(glucose_data),
                'glucose_std': np.std(glucose_data),
                'cv': np.std(glucose_data)/np.mean(glucose_data)*100,
                'data_points': len(glucose_data)
            }
        }