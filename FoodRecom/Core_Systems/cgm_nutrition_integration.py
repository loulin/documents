#!/usr/bin/env python3
"""
CGM-营养推荐集成模块
结合连续血糖监测数据，实现个性化营养推荐优化
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class CGMNutritionIntegration:
    """CGM数据与营养推荐系统集成"""

    def __init__(self):
        """初始化CGM-营养集成系统"""
        # CGM血糖目标范围
        self.glucose_targets = {
            'fasting': {'target': 5.1, 'max': 6.1},      # 空腹血糖
            'post_meal_1h': {'target': 8.0, 'max': 10.0}, # 餐后1小时
            'post_meal_2h': {'target': 6.7, 'max': 8.5},  # 餐后2小时
            'bedtime': {'target': 6.0, 'max': 7.8}        # 睡前
        }

        # 个性化血糖反应阈值
        self.personalized_thresholds = {
            'low_response': 1.5,     # 低血糖反应（mmol/L）
            'normal_response': 3.0,  # 正常血糖反应
            'high_response': 4.5,    # 高血糖反应
            'severe_response': 6.0   # 严重血糖反应
        }

        # 食物血糖影响评估
        self.food_impact_categories = {
            'low_impact': {'gi_max': 35, 'gl_max': 10},
            'medium_impact': {'gi_max': 70, 'gl_max': 20},
            'high_impact': {'gi_max': 100, 'gl_max': 50}
        }

    def analyze_meal_glucose_response(self, cgm_data: pd.DataFrame,
                                    meal_time: datetime,
                                    meal_composition: Dict) -> Dict:
        """
        分析特定餐次的血糖反应

        Args:
            cgm_data: CGM数据 (包含时间戳和血糖值)
            meal_time: 用餐时间
            meal_composition: 餐食组成 {'dishes': [...], 'gi_total': xx, 'gl_total': xx}

        Returns:
            餐后血糖反应分析结果
        """
        try:
            # 提取餐前餐后数据
            pre_meal_window = meal_time - timedelta(minutes=30)
            post_meal_2h = meal_time + timedelta(hours=2)
            post_meal_4h = meal_time + timedelta(hours=4)

            # 获取相关时间段数据
            pre_meal_data = cgm_data[
                (cgm_data['timestamp'] >= pre_meal_window) &
                (cgm_data['timestamp'] <= meal_time)
            ]

            post_meal_data = cgm_data[
                (cgm_data['timestamp'] > meal_time) &
                (cgm_data['timestamp'] <= post_meal_4h)
            ]

            if pre_meal_data.empty or post_meal_data.empty:
                return {'error': '数据不足，无法分析'}

            # 计算关键指标
            baseline_glucose = pre_meal_data['glucose'].mean()
            peak_glucose = post_meal_data['glucose'].max()
            peak_time = post_meal_data.loc[post_meal_data['glucose'].idxmax(), 'timestamp']

            # 餐后2小时血糖
            post_2h_data = post_meal_data[
                post_meal_data['timestamp'] <= post_meal_2h
            ]
            glucose_2h = post_2h_data['glucose'].iloc[-1] if not post_2h_data.empty else None

            # 血糖上升幅度
            glucose_excursion = peak_glucose - baseline_glucose
            time_to_peak = (peak_time - meal_time).total_seconds() / 60  # 分钟

            # 血糖回归时间
            recovery_threshold = baseline_glucose + 1.0  # 回归到基线+1mmol/L
            recovery_data = post_meal_data[post_meal_data['glucose'] <= recovery_threshold]
            recovery_time = None
            if not recovery_data.empty:
                recovery_time = (recovery_data.iloc[0]['timestamp'] - meal_time).total_seconds() / 60

            # 计算曲线下面积 (AUC)
            auc = self._calculate_glucose_auc(post_meal_data, baseline_glucose)

            # 餐后血糖反应评级
            response_grade = self._grade_glucose_response(
                glucose_excursion, glucose_2h, baseline_glucose, auc
            )

            # 与预期GI/GL反应对比
            expected_response = self._predict_glucose_response(meal_composition)
            response_match = self._compare_actual_vs_expected(
                glucose_excursion, expected_response
            )

            return {
                'baseline_glucose': round(baseline_glucose, 1),
                'peak_glucose': round(peak_glucose, 1),
                'glucose_excursion': round(glucose_excursion, 1),
                'time_to_peak': round(time_to_peak, 1),
                'glucose_2h': round(glucose_2h, 1) if glucose_2h else None,
                'recovery_time': round(recovery_time, 1) if recovery_time else None,
                'auc': round(auc, 1),
                'response_grade': response_grade,
                'expected_response': expected_response,
                'response_match': response_match,
                'meal_composition': meal_composition
            }

        except Exception as e:
            return {'error': f'分析失败: {str(e)}'}

    def _calculate_glucose_auc(self, glucose_data: pd.DataFrame, baseline: float) -> float:
        """计算血糖曲线下面积"""
        if len(glucose_data) < 2:
            return 0.0

        # 使用梯形积分计算AUC
        times = [(t - glucose_data.iloc[0]['timestamp']).total_seconds() / 60
                for t in glucose_data['timestamp']]
        glucose_values = glucose_data['glucose'].values - baseline
        glucose_values[glucose_values < 0] = 0  # 只考虑超过基线的部分

        auc = np.trapz(glucose_values, times)
        return auc

    def _grade_glucose_response(self, excursion: float, glucose_2h: float,
                              baseline: float, auc: float) -> Dict:
        """评估血糖反应等级"""
        score = 0
        recommendations = []

        # 血糖上升幅度评分
        if excursion <= self.personalized_thresholds['low_response']:
            score += 10
            recommendations.append("✅ 血糖反应温和，食物选择适宜")
        elif excursion <= self.personalized_thresholds['normal_response']:
            score += 8
            recommendations.append("✅ 血糖反应正常")
        elif excursion <= self.personalized_thresholds['high_response']:
            score += 5
            recommendations.append("⚠️ 血糖反应较高，建议调整食物选择")
        else:
            score += 2
            recommendations.append("🚨 血糖反应过高，需要优化膳食")

        # 餐后2小时血糖评分
        if glucose_2h and glucose_2h <= self.glucose_targets['post_meal_2h']['target']:
            score += 10
            recommendations.append("✅ 餐后2小时血糖达标")
        elif glucose_2h and glucose_2h <= self.glucose_targets['post_meal_2h']['max']:
            score += 6
            recommendations.append("⚠️ 餐后2小时血糖偏高")
        else:
            score += 0
            recommendations.append("🚨 餐后2小时血糖超标")

        # AUC评分
        if auc <= 100:
            score += 10
        elif auc <= 200:
            score += 6
        else:
            score += 2

        grade = "优秀" if score >= 25 else "良好" if score >= 20 else "需改进" if score >= 15 else "不佳"

        return {
            'score': score,
            'grade': grade,
            'recommendations': recommendations
        }

    def _predict_glucose_response(self, meal_composition: Dict) -> Dict:
        """基于GI/GL预测血糖反应"""
        gi_total = meal_composition.get('gi_total', 50)
        gl_total = meal_composition.get('gl_total', 15)

        # 预测血糖上升幅度
        predicted_excursion = (gi_total * 0.05) + (gl_total * 0.1)

        # 预测反应类型
        if gi_total <= 35 and gl_total <= 10:
            response_type = "低血糖反应"
            expected_excursion_range = (1.0, 2.5)
        elif gi_total <= 70 and gl_total <= 20:
            response_type = "中等血糖反应"
            expected_excursion_range = (2.0, 4.0)
        else:
            response_type = "高血糖反应"
            expected_excursion_range = (3.5, 6.0)

        return {
            'predicted_excursion': round(predicted_excursion, 1),
            'response_type': response_type,
            'expected_range': expected_excursion_range,
            'gi_total': gi_total,
            'gl_total': gl_total
        }

    def _compare_actual_vs_expected(self, actual_excursion: float,
                                  expected_response: Dict) -> Dict:
        """比较实际与预期血糖反应"""
        predicted = expected_response['predicted_excursion']
        expected_range = expected_response['expected_range']

        # 计算偏差
        deviation = actual_excursion - predicted
        deviation_percentage = abs(deviation) / predicted * 100 if predicted > 0 else 0

        # 判断匹配度
        if expected_range[0] <= actual_excursion <= expected_range[1]:
            match_level = "完全匹配"
            match_score = 10
        elif deviation_percentage <= 20:
            match_level = "较好匹配"
            match_score = 8
        elif deviation_percentage <= 40:
            match_level = "一般匹配"
            match_score = 6
        else:
            match_level = "匹配度低"
            match_score = 3

        # 个体化建议
        if actual_excursion > expected_range[1]:
            suggestion = "您对此类食物血糖反应较敏感，建议减少摄入或调整搭配"
        elif actual_excursion < expected_range[0]:
            suggestion = "您对此类食物血糖反应较平缓，可以适量增加摄入"
        else:
            suggestion = "血糖反应符合预期，当前食物选择适宜"

        return {
            'match_level': match_level,
            'match_score': match_score,
            'deviation': round(deviation, 1),
            'deviation_percentage': round(deviation_percentage, 1),
            'suggestion': suggestion
        }

    def generate_personalized_recommendations(self,
                                           cgm_history: List[Dict],
                                           current_glucose: float,
                                           next_meal_type: str,
                                           patient_profile: Dict) -> Dict:
        """
        基于CGM历史数据生成个性化营养推荐

        Args:
            cgm_history: CGM历史分析结果列表
            current_glucose: 当前血糖值
            next_meal_type: 下一餐类型 (early_breakfast, lunch, dinner, snack)
            patient_profile: 患者档案

        Returns:
            个性化营养推荐方案
        """
        try:
            # 分析个体血糖反应模式
            glucose_sensitivity = self._analyze_glucose_sensitivity(cgm_history)

            # 当前血糖状态评估
            current_status = self._assess_current_glucose_status(
                current_glucose, next_meal_type
            )

            # 生成食物推荐调整方案
            food_adjustments = self._generate_food_adjustments(
                glucose_sensitivity, current_status, patient_profile
            )

            # 生成详细推荐
            detailed_recommendations = self._create_detailed_recommendations(
                food_adjustments, next_meal_type, current_status
            )

            return {
                'glucose_sensitivity': glucose_sensitivity,
                'current_status': current_status,
                'food_adjustments': food_adjustments,
                'recommendations': detailed_recommendations,
                'monitoring_advice': self._generate_monitoring_advice(current_status)
            }

        except Exception as e:
            return {'error': f'推荐生成失败: {str(e)}'}

    def _analyze_glucose_sensitivity(self, cgm_history: List[Dict]) -> Dict:
        """分析个体血糖敏感性"""
        if not cgm_history:
            return {'sensitivity_level': 'unknown', 'confidence': 0}

        # 收集血糖反应数据
        excursions = []
        gi_values = []
        gl_values = []

        for record in cgm_history:
            if 'glucose_excursion' in record and 'meal_composition' in record:
                excursions.append(record['glucose_excursion'])
                meal_comp = record['meal_composition']
                gi_values.append(meal_comp.get('gi_total', 50))
                gl_values.append(meal_comp.get('gl_total', 15))

        if len(excursions) < 3:
            return {'sensitivity_level': 'insufficient_data', 'confidence': 0}

        # 计算敏感性指标
        avg_excursion = np.mean(excursions)
        excursion_variability = np.std(excursions)

        # 计算GI/GL相关性
        gi_correlation = np.corrcoef(gi_values, excursions)[0, 1] if len(gi_values) > 2 else 0
        gl_correlation = np.corrcoef(gl_values, excursions)[0, 1] if len(gl_values) > 2 else 0

        # 敏感性分级
        if avg_excursion <= 2.0:
            sensitivity_level = 'low'
            sensitivity_desc = "血糖反应较平缓"
        elif avg_excursion <= 3.5:
            sensitivity_level = 'moderate'
            sensitivity_desc = "血糖反应适中"
        else:
            sensitivity_level = 'high'
            sensitivity_desc = "血糖反应较敏感"

        confidence = min(len(excursions) / 10.0, 1.0)  # 最多10次记录达到100%置信度

        return {
            'sensitivity_level': sensitivity_level,
            'sensitivity_desc': sensitivity_desc,
            'avg_excursion': round(avg_excursion, 1),
            'variability': round(excursion_variability, 1),
            'gi_correlation': round(gi_correlation, 2),
            'gl_correlation': round(gl_correlation, 2),
            'confidence': round(confidence, 2),
            'sample_size': len(excursions)
        }

    def _assess_current_glucose_status(self, glucose: float, meal_type: str) -> Dict:
        """评估当前血糖状态"""
        status = "normal"
        recommendations = []
        urgency = "low"

        if meal_type == "breakfast":
            target = self.glucose_targets['fasting']
            if glucose > target['max']:
                status = "高血糖"
                recommendations.append("建议选择低GI食物")
                urgency = "medium"
            elif glucose < 3.9:
                status = "低血糖"
                recommendations.append("需要适量碳水化合物补充")
                urgency = "high"
        else:
            if glucose > 10.0:
                status = "餐后高血糖"
                recommendations.append("建议延后进餐或选择极低GI食物")
                urgency = "high"
            elif glucose > 8.0:
                status = "血糖偏高"
                recommendations.append("建议选择低GI食物，控制分量")
                urgency = "medium"
            elif glucose < 4.0:
                status = "低血糖"
                recommendations.append("需要快速补充碳水化合物")
                urgency = "high"

        return {
            'glucose_value': glucose,
            'status': status,
            'urgency': urgency,
            'recommendations': recommendations,
            'meal_type': meal_type
        }

    def _generate_food_adjustments(self, glucose_sensitivity: Dict,
                                 current_status: Dict,
                                 patient_profile: Dict) -> Dict:
        """生成食物调整建议"""
        adjustments = {
            'gi_target': 55,  # 默认中等GI
            'gl_target': 15,  # 默认中等GL
            'portion_modifier': 1.0,
            'priority_foods': [],
            'avoid_foods': [],
            'special_considerations': []
        }

        # 基于血糖敏感性调整
        sensitivity = glucose_sensitivity.get('sensitivity_level', 'moderate')

        if sensitivity == 'high':
            adjustments['gi_target'] = 35  # 低GI
            adjustments['gl_target'] = 10  # 低GL
            adjustments['special_considerations'].append("高血糖敏感体质，严格控制碳水化合物")

        elif sensitivity == 'low':
            adjustments['gi_target'] = 70  # 可接受中高GI
            adjustments['gl_target'] = 20  # 可接受中高GL
            adjustments['special_considerations'].append("血糖反应平缓，食物选择相对宽松")

        # 基于当前血糖状态调整
        if current_status['status'] == "高血糖" or current_status['status'] == "餐后高血糖":
            adjustments['gi_target'] = min(adjustments['gi_target'], 25)  # 极低GI
            adjustments['gl_target'] = min(adjustments['gl_target'], 8)   # 极低GL
            adjustments['portion_modifier'] = 0.7
            adjustments['priority_foods'].extend([
                "蔬菜类", "优质蛋白质", "纤维丰富食物"
            ])
            adjustments['avoid_foods'].extend([
                "高糖食物", "精制碳水", "高GI水果"
            ])

        elif current_status['status'] == "低血糖":
            adjustments['priority_foods'].extend([
                "中等GI碳水化合物", "蛋白质搭配"
            ])
            adjustments['special_considerations'].append("低血糖状态，需要适量快速升糖食物")

        # 基于疾病状态调整
        if 'diagnosed_diseases' in patient_profile:
            diseases = patient_profile['diagnosed_diseases']
            if '糖尿病' in diseases or '2型糖尿病' in diseases:
                adjustments['gi_target'] = min(adjustments['gi_target'], 35)
                adjustments['special_considerations'].append("糖尿病患者，严格血糖控制")

        return adjustments

    def _create_detailed_recommendations(self, food_adjustments: Dict,
                                       meal_type: str,
                                       current_status: Dict) -> Dict:
        """创建详细的营养推荐"""
        recommendations = {
            'meal_type': meal_type,
            'glucose_status': current_status['status'],
            'target_gi': food_adjustments['gi_target'],
            'target_gl': food_adjustments['gl_target'],
            'recommended_foods': [],
            'cooking_methods': [],
            'timing_advice': "",
            'portion_guidance': "",
            'monitoring_points': []
        }

        # 基于餐次类型的推荐
        if meal_type == "breakfast":
            recommendations['recommended_foods'] = [
                "燕麦粥（低GI）", "蒸蛋羹", "牛奶", "坚果少量"
            ]
            recommendations['timing_advice'] = "餐后1-2小时监测血糖峰值"

        elif meal_type == "lunch":
            recommendations['recommended_foods'] = [
                "糙米（少量）", "清蒸鱼", "蔬菜炒制", "豆腐"
            ]
            recommendations['timing_advice'] = "餐后1小时和2小时监测血糖"

        elif meal_type == "dinner":
            recommendations['recommended_foods'] = [
                "蔬菜为主", "瘦肉蛋白", "少量碳水", "清汤"
            ]
            recommendations['timing_advice'] = "餐后2小时和睡前监测血糖"

        # 烹饪方法建议
        recommendations['cooking_methods'] = [
            "蒸煮为主", "少油炒制", "避免油炸", "低温烹饪"
        ]

        # 分量指导
        portion_modifier = food_adjustments['portion_modifier']
        if portion_modifier < 0.8:
            recommendations['portion_guidance'] = "建议减少20-30%正常分量"
        elif portion_modifier > 1.2:
            recommendations['portion_guidance'] = "可适量增加蛋白质和蔬菜分量"
        else:
            recommendations['portion_guidance'] = "正常分量，注意营养均衡"

        # 监测要点
        recommendations['monitoring_points'] = [
            "餐前血糖记录",
            "餐后1小时血糖峰值",
            "餐后2小时血糖回落",
            "下一餐前血糖状态"
        ]

        return recommendations

    def _generate_monitoring_advice(self, current_status: Dict) -> Dict:
        """生成血糖监测建议"""
        monitoring_advice = {
            'frequency': 'normal',
            'key_timepoints': [],
            'alert_thresholds': {},
            'action_plans': {}
        }

        urgency = current_status.get('urgency', 'low')

        if urgency == 'high':
            monitoring_advice['frequency'] = 'intensive'
            monitoring_advice['key_timepoints'] = [
                '餐前', '餐后30分钟', '餐后1小时', '餐后2小时'
            ]
            monitoring_advice['alert_thresholds'] = {
                'high_alert': 11.1,
                'low_alert': 3.9
            }

        elif urgency == 'medium':
            monitoring_advice['frequency'] = 'enhanced'
            monitoring_advice['key_timepoints'] = [
                '餐前', '餐后1小时', '餐后2小时'
            ]
            monitoring_advice['alert_thresholds'] = {
                'high_alert': 10.0,
                'low_alert': 4.0
            }

        else:
            monitoring_advice['frequency'] = 'normal'
            monitoring_advice['key_timepoints'] = [
                '餐前', '餐后2小时'
            ]
            monitoring_advice['alert_thresholds'] = {
                'high_alert': 8.5,
                'low_alert': 4.0
            }

        # 行动计划
        monitoring_advice['action_plans'] = {
            'high_glucose': "血糖过高时延后进餐，选择低GI食物",
            'low_glucose': "血糖过低时适量补充碳水化合物",
            'stable_glucose': "血糖稳定时按计划进餐"
        }

        return monitoring_advice

# 示例使用函数
def demo_cgm_nutrition_integration():
    """演示CGM-营养推荐集成功能"""
    integrator = CGMNutritionIntegration()

    # 模拟CGM数据
    sample_cgm_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01 08:00', periods=120, freq='5min'),
        'glucose': np.random.normal(6.5, 1.2, 120)
    })

    # 模拟餐食组成
    sample_meal = {
        'dishes': ['燕麦鸡蛋套餐'],
        'gi_total': 45,
        'gl_total': 12
    }

    # 分析餐后血糖反应
    meal_time = datetime(2024, 1, 1, 8, 0)
    response_analysis = integrator.analyze_meal_glucose_response(
        sample_cgm_data, meal_time, sample_meal
    )

    print("=== CGM餐后血糖反应分析 ===")
    print(f"血糖上升幅度: {response_analysis.get('glucose_excursion', 'N/A')} mmol/L")
    print(f"血糖反应等级: {response_analysis.get('response_grade', {}).get('grade', 'N/A')}")

    # 生成个性化推荐
    cgm_history = [response_analysis]
    current_glucose = 6.8
    recommendations = integrator.generate_personalized_recommendations(
        cgm_history, current_glucose, 'lunch', {'diagnosed_diseases': ['糖尿病']}
    )

    print("\n=== 个性化营养推荐 ===")
    print(f"血糖敏感性: {recommendations.get('glucose_sensitivity', {}).get('sensitivity_desc', 'N/A')}")
    print(f"推荐GI目标: {recommendations.get('recommendations', {}).get('target_gi', 'N/A')}")

    return integrator, response_analysis, recommendations

if __name__ == "__main__":
    demo_cgm_nutrition_integration()