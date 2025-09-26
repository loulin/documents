"""
血糖混沌分析治疗效果追踪系统
基于混沌指标评估治疗方案的效果和优化方向
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class TreatmentIntervention:
    """
    治疗干预记录
    """
    date: datetime
    intervention_type: str  # 胰岛素调整、药物变更、生活方式等
    description: str
    dosage_change: Optional[Dict] = None  # 剂量变化
    target_metrics: List[str] = None  # 目标改善指标
    expected_effect: str = ""  # 预期效果
    
@dataclass  
class MetricsPeriod:
    """
    指标周期记录
    """
    start_date: datetime
    end_date: datetime
    glucose_data: List[float]
    traditional_metrics: Dict
    chaos_metrics: Dict
    brittleness_type: str
    clinical_score: float
    
class TreatmentEffectTracker:
    """
    治疗效果追踪分析系统
    """
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.interventions: List[TreatmentIntervention] = []
        self.metric_periods: List[MetricsPeriod] = []
        self.baseline_established = False
        self.baseline_period: Optional[MetricsPeriod] = None
        
    def establish_baseline(self, glucose_data: List[float], start_date: datetime, end_date: datetime):
        """
        建立基线指标
        """
        print(f"建立患者 {self.patient_id} 的基线指标...")
        
        # 计算基线指标
        traditional_metrics = self.calculate_traditional_metrics(glucose_data)
        chaos_metrics = self.calculate_chaos_metrics(glucose_data)
        brittleness_type = self.classify_brittleness(traditional_metrics, chaos_metrics)
        clinical_score = self.calculate_clinical_score(traditional_metrics, chaos_metrics)
        
        self.baseline_period = MetricsPeriod(
            start_date=start_date,
            end_date=end_date,
            glucose_data=glucose_data,
            traditional_metrics=traditional_metrics,
            chaos_metrics=chaos_metrics,
            brittleness_type=brittleness_type,
            clinical_score=clinical_score
        )
        
        self.baseline_established = True
        
        print(f"基线建立完成:")
        print(f"  - 脆性类型: {brittleness_type}")
        print(f"  - 临床评分: {clinical_score:.1f}/100")
        print(f"  - TIR: {traditional_metrics['TIR']:.1f}%")
        print(f"  - CV: {traditional_metrics['CV']:.1f}%")
        print(f"  - Lyapunov指数: {chaos_metrics['lyapunov']:.4f}")
        
    def add_intervention(self, intervention: TreatmentIntervention):
        """
        添加治疗干预
        """
        self.interventions.append(intervention)
        print(f"记录治疗干预: {intervention.intervention_type} - {intervention.description}")
        
    def add_follow_up_period(self, glucose_data: List[float], start_date: datetime, end_date: datetime):
        """
        添加随访期数据
        """
        if not self.baseline_established:
            print("警告: 尚未建立基线，请先建立基线指标")
            return
            
        # 计算当前期指标
        traditional_metrics = self.calculate_traditional_metrics(glucose_data)
        chaos_metrics = self.calculate_chaos_metrics(glucose_data)
        brittleness_type = self.classify_brittleness(traditional_metrics, chaos_metrics)
        clinical_score = self.calculate_clinical_score(traditional_metrics, chaos_metrics)
        
        period = MetricsPeriod(
            start_date=start_date,
            end_date=end_date,
            glucose_data=glucose_data,
            traditional_metrics=traditional_metrics,
            chaos_metrics=chaos_metrics,
            brittleness_type=brittleness_type,
            clinical_score=clinical_score
        )
        
        self.metric_periods.append(period)
        
        # 分析变化
        self.analyze_period_changes(period)
        
    def calculate_traditional_metrics(self, glucose_data: List[float]) -> Dict:
        """
        计算传统血糖指标
        """
        glucose_array = np.array(glucose_data)
        
        # 基础统计
        mean_glucose = np.mean(glucose_array)
        std_glucose = np.std(glucose_array)
        cv = (std_glucose / mean_glucose) * 100
        
        # TIR
        tir = np.sum((glucose_array >= 3.9) & (glucose_array <= 10.0)) / len(glucose_array) * 100
        
        # 低血糖时间
        time_below_70 = np.sum(glucose_array < 3.9) / len(glucose_array) * 100
        time_very_low = np.sum(glucose_array < 3.0) / len(glucose_array) * 100
        
        # 高血糖时间  
        time_above_180 = np.sum(glucose_array > 10.0) / len(glucose_array) * 100
        time_very_high = np.sum(glucose_array > 13.9) / len(glucose_array) * 100
        
        # GMI
        gmi = 3.31 + 0.02392 * mean_glucose * 18.018
        
        return {
            "mean_glucose": mean_glucose,
            "CV": cv,
            "TIR": tir,
            "time_below_70": time_below_70,
            "time_very_low": time_very_low,
            "time_above_180": time_above_180,
            "time_very_high": time_very_high,
            "GMI": gmi,
            "glucose_range": np.max(glucose_array) - np.min(glucose_array)
        }
    
    def calculate_chaos_metrics(self, glucose_data: List[float]) -> Dict:
        """
        计算混沌分析指标
        """
        glucose_array = np.array(glucose_data)
        
        try:
            # Lyapunov指数估计
            rate_changes = np.diff(glucose_array)
            divergence = []
            
            for i in range(len(rate_changes)-1):
                if abs(rate_changes[i]) > 0.01:
                    ratio = abs(rate_changes[i+1]) / abs(rate_changes[i])
                    if ratio > 0:
                        divergence.append(np.log(ratio))
            
            lyapunov = np.mean(divergence) if divergence else 0
            
            # Shannon熵
            hist, _ = np.histogram(glucose_array, bins=20, density=True)
            hist = hist[hist > 0]
            shannon_entropy = -np.sum(hist * np.log2(hist)) if len(hist) > 0 else 0
            
            # 近似熵
            def approximate_entropy(data, m=2, r=0.2):
                N = len(data)
                if N < 10:
                    return 0
                    
                def _maxdist(xi, xj):
                    return max([abs(ua - va) for ua, va in zip(xi, xj)])
                
                def _phi(m):
                    patterns = [data[i:i+m] for i in range(N-m+1)]
                    C = []
                    
                    for i in range(N-m+1):
                        template_i = patterns[i]
                        matches = 0
                        
                        for j in range(N-m+1):
                            if _maxdist(template_i, patterns[j]) <= r * np.std(data):
                                matches += 1
                        
                        C.append(matches / (N-m+1))
                    
                    phi = np.mean([np.log(c) for c in C if c > 0])
                    return phi
                
                return _phi(m) - _phi(m+1)
            
            approx_entropy = approximate_entropy(glucose_array)
            
            # Hurst指数
            def hurst_exponent(data):
                try:
                    lags = range(2, min(50, len(data)//4))
                    if len(lags) < 3:
                        return 0.5
                    tau = [np.std(np.subtract(data[lag:], data[:-lag])) for lag in lags]
                    poly = np.polyfit(np.log(lags), np.log(tau), 1)
                    return poly[0]
                except:
                    return 0.5
            
            hurst = hurst_exponent(glucose_array)
            
            # 复杂度指标
            changes = np.abs(np.diff(glucose_array))
            max_change = np.max(changes) if len(changes) > 0 else 0
            mean_change = np.mean(changes) if len(changes) > 0 else 0
            
            return {
                "lyapunov": lyapunov,
                "shannon_entropy": shannon_entropy,
                "approximate_entropy": approx_entropy,
                "hurst_exponent": hurst,
                "max_change_rate": max_change,
                "mean_change_rate": mean_change,
                "complexity_score": shannon_entropy * (1 + abs(lyapunov))
            }
            
        except Exception as e:
            print(f"混沌指标计算错误: {e}")
            return {
                "lyapunov": 0,
                "shannon_entropy": 0,
                "approximate_entropy": 0,
                "hurst_exponent": 0.5,
                "max_change_rate": 0,
                "mean_change_rate": 0,
                "complexity_score": 0
            }
    
    def classify_brittleness(self, traditional_metrics: Dict, chaos_metrics: Dict) -> str:
        """
        分类血糖脆性
        """
        cv = traditional_metrics["CV"]
        lyapunov = chaos_metrics["lyapunov"]
        approx_entropy = chaos_metrics["approximate_entropy"]
        shannon_entropy = chaos_metrics["shannon_entropy"]
        
        if lyapunov > 0.1 and cv > 40:
            return "I型混沌脆性"
        elif lyapunov > 0.01 and cv > 30:
            return "II型准周期脆性"
        elif cv > 35 and shannon_entropy > 4:
            return "III型随机脆性"
        elif approx_entropy > 0.5 and cv > 25:
            return "IV型记忆缺失脆性"
        elif shannon_entropy > 3.5:
            return "V型频域脆性"
        elif cv < 25:
            return "稳定型"
        else:
            return "中等不稳定型"
    
    def calculate_clinical_score(self, traditional_metrics: Dict, chaos_metrics: Dict) -> float:
        """
        计算综合临床评分 (0-100分)
        """
        score = 0
        
        # TIR评分 (40分)
        tir = traditional_metrics["TIR"]
        if tir >= 70:
            score += 40
        elif tir >= 50:
            score += 30
        elif tir >= 25:
            score += 15
        else:
            score += 5
        
        # 安全性评分 (30分)
        low_time = traditional_metrics["time_below_70"]
        very_low_time = traditional_metrics["time_very_low"]
        
        if very_low_time == 0 and low_time < 4:
            score += 30
        elif very_low_time < 1 and low_time < 10:
            score += 20
        elif very_low_time < 2:
            score += 10
        
        # 稳定性评分 (20分)
        cv = traditional_metrics["CV"]
        if cv < 25:
            score += 20
        elif cv < 36:
            score += 15
        elif cv < 50:
            score += 10
        else:
            score += 2
        
        # 混沌稳定性评分 (10分)
        lyapunov = chaos_metrics["lyapunov"]
        if lyapunov < 0.01:
            score += 10
        elif lyapunov < 0.05:
            score += 7
        elif lyapunov < 0.1:
            score += 3
        
        return min(score, 100)
    
    def analyze_period_changes(self, current_period: MetricsPeriod):
        """
        分析相对于基线的变化
        """
        if not self.baseline_period:
            return
            
        print(f"\n--- 随访期分析 ({current_period.start_date.strftime('%Y-%m-%d')} 至 {current_period.end_date.strftime('%Y-%m-%d')}) ---")
        
        # 脆性类型变化
        baseline_type = self.baseline_period.brittleness_type
        current_type = current_period.brittleness_type
        
        if current_type != baseline_type:
            print(f"🔄 脆性类型变化: {baseline_type} → {current_type}")
        else:
            print(f"📊 脆性类型: {current_type} (无变化)")
        
        # 临床评分变化
        baseline_score = self.baseline_period.clinical_score
        current_score = current_period.clinical_score
        score_change = current_score - baseline_score
        
        if score_change > 5:
            print(f"📈 临床评分改善: {baseline_score:.1f} → {current_score:.1f} (+{score_change:.1f})")
        elif score_change < -5:
            print(f"📉 临床评分下降: {baseline_score:.1f} → {current_score:.1f} ({score_change:.1f})")
        else:
            print(f"📊 临床评分: {current_score:.1f} (变化 {score_change:+.1f})")
        
        # 关键指标对比
        self.compare_key_metrics(current_period)
        
        # 治疗建议
        self.generate_treatment_recommendations(current_period)
    
    def compare_key_metrics(self, current_period: MetricsPeriod):
        """
        对比关键指标
        """
        baseline = self.baseline_period
        current = current_period
        
        print(f"\n关键指标对比:")
        
        # TIR对比
        tir_change = current.traditional_metrics["TIR"] - baseline.traditional_metrics["TIR"]
        tir_symbol = "📈" if tir_change > 5 else "📉" if tir_change < -5 else "➡️"
        print(f"  TIR: {baseline.traditional_metrics['TIR']:.1f}% → {current.traditional_metrics['TIR']:.1f}% "
              f"({tir_change:+.1f}%) {tir_symbol}")
        
        # CV对比
        cv_change = current.traditional_metrics["CV"] - baseline.traditional_metrics["CV"]
        cv_symbol = "📉" if cv_change < -5 else "📈" if cv_change > 5 else "➡️"
        print(f"  CV: {baseline.traditional_metrics['CV']:.1f}% → {current.traditional_metrics['CV']:.1f}% "
              f"({cv_change:+.1f}%) {cv_symbol}")
        
        # Lyapunov指数对比
        ly_change = current.chaos_metrics["lyapunov"] - baseline.chaos_metrics["lyapunov"]
        ly_symbol = "📉" if ly_change < -0.01 else "📈" if ly_change > 0.01 else "➡️"
        print(f"  Lyapunov: {baseline.chaos_metrics['lyapunov']:.4f} → {current.chaos_metrics['lyapunov']:.4f} "
              f"({ly_change:+.4f}) {ly_symbol}")
        
        # 低血糖时间对比
        low_change = current.traditional_metrics["time_below_70"] - baseline.traditional_metrics["time_below_70"]
        low_symbol = "📉" if low_change < -1 else "📈" if low_change > 1 else "➡️"
        print(f"  低血糖时间: {baseline.traditional_metrics['time_below_70']:.1f}% → "
              f"{current.traditional_metrics['time_below_70']:.1f}% ({low_change:+.1f}%) {low_symbol}")
    
    def generate_treatment_recommendations(self, current_period: MetricsPeriod):
        """
        生成治疗建议
        """
        recommendations = []
        
        baseline = self.baseline_period
        current = current_period
        
        # 基于脆性类型变化的建议
        if current.brittleness_type != baseline.brittleness_type:
            if "混沌" in current.brittleness_type:
                recommendations.append("⚠️ 脆性恶化为混沌型，建议立即调整治疗策略，采用保守目标")
            elif "稳定" in current.brittleness_type:
                recommendations.append("✅ 脆性改善为稳定型，可考虑逐步优化血糖目标")
        
        # 基于指标变化的建议
        tir_change = current.traditional_metrics["TIR"] - baseline.traditional_metrics["TIR"]
        cv_change = current.traditional_metrics["CV"] - baseline.traditional_metrics["CV"]
        ly_change = current.chaos_metrics["lyapunov"] - baseline.chaos_metrics["lyapunov"]
        
        if tir_change > 10:
            recommendations.append("🎯 TIR显著改善，当前治疗方案有效，建议维持")
        elif tir_change < -10:
            recommendations.append("📊 TIR下降较多，需要重新评估治疗方案")
        
        if cv_change < -10:
            recommendations.append("📉 血糖变异性显著降低，稳定性改善")
        elif cv_change > 10:
            recommendations.append("📈 血糖变异性增加，需要改善治疗稳定性")
        
        if ly_change < -0.05:
            recommendations.append("🔧 混沌指数降低，系统稳定性改善")
        elif ly_change > 0.05:
            recommendations.append("⚠️ 混沌指数升高，系统不稳定性增加")
        
        # 安全性建议
        if current.traditional_metrics["time_very_low"] > 1:
            recommendations.append("🚨 严重低血糖时间过长，需要调整胰岛素剂量")
        
        if not recommendations:
            recommendations.append("📊 各项指标相对稳定，继续当前治疗方案并定期监测")
        
        print(f"\n治疗建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    def generate_comprehensive_report(self) -> Dict:
        """
        生成综合追踪报告
        """
        if not self.baseline_established:
            return {"error": "基线未建立"}
        
        report = {
            "患者ID": self.patient_id,
            "报告生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "追踪概览": {
                "基线建立日期": self.baseline_period.start_date.strftime("%Y-%m-%d"),
                "随访期数": len(self.metric_periods),
                "治疗干预次数": len(self.interventions),
                "追踪总天数": (self.metric_periods[-1].end_date - self.baseline_period.start_date).days if self.metric_periods else 0
            },
            "基线指标": {
                "脆性类型": self.baseline_period.brittleness_type,
                "临床评分": self.baseline_period.clinical_score,
                "TIR": self.baseline_period.traditional_metrics["TIR"],
                "CV": self.baseline_period.traditional_metrics["CV"],
                "Lyapunov指数": self.baseline_period.chaos_metrics["lyapunov"]
            }
        }
        
        if self.metric_periods:
            latest = self.metric_periods[-1]
            report["最新指标"] = {
                "脆性类型": latest.brittleness_type,
                "临床评分": latest.clinical_score,
                "TIR": latest.traditional_metrics["TIR"],
                "CV": latest.traditional_metrics["CV"],
                "Lyapunov指数": latest.chaos_metrics["lyapunov"]
            }
            
            # 计算总体变化
            report["总体变化"] = {
                "脆性类型变化": f"{self.baseline_period.brittleness_type} → {latest.brittleness_type}",
                "临床评分变化": latest.clinical_score - self.baseline_period.clinical_score,
                "TIR变化": latest.traditional_metrics["TIR"] - self.baseline_period.traditional_metrics["TIR"],
                "CV变化": latest.traditional_metrics["CV"] - self.baseline_period.traditional_metrics["CV"],
                "Lyapunov变化": latest.chaos_metrics["lyapunov"] - self.baseline_period.chaos_metrics["lyapunov"]
            }
        
        # 治疗干预历史
        report["治疗干预"] = []
        for intervention in self.interventions:
            report["治疗干预"].append({
                "日期": intervention.date.strftime("%Y-%m-%d"),
                "类型": intervention.intervention_type,
                "描述": intervention.description,
                "预期效果": intervention.expected_effect
            })
        
        return report

def demonstrate_treatment_tracking():
    """
    演示治疗效果追踪功能
    """
    print("="*70)
    print("血糖混沌分析治疗效果追踪系统演示")
    print("="*70)
    
    # 创建追踪器
    tracker = TreatmentEffectTracker("DEMO_PATIENT_001")
    
    # 1. 建立基线（治疗前的血糖数据）
    print("\n1. 建立基线指标")
    np.random.seed(42)
    baseline_glucose = []
    for i in range(96):  # 24小时数据
        # 模拟脆性糖尿病患者：高变异性，偶有极端值
        base = 9.0 + 3 * np.sin(i * 0.1) + np.random.normal(0, 2.5)
        if np.random.random() < 0.1:  # 10%概率极端值
            base += np.random.uniform(-6, 8)
        baseline_glucose.append(np.clip(base, 3, 18))
    
    baseline_start = datetime.now() - timedelta(days=30)
    baseline_end = baseline_start + timedelta(days=1)
    
    tracker.establish_baseline(baseline_glucose, baseline_start, baseline_end)
    
    # 2. 记录治疗干预
    print(f"\n2. 记录治疗干预")
    
    intervention1 = TreatmentIntervention(
        date=datetime.now() - timedelta(days=20),
        intervention_type="胰岛素调整",
        description="基础胰岛素增加20%，调整餐时胰岛素时间",
        expected_effect="改善血糖稳定性，降低变异系数"
    )
    tracker.add_intervention(intervention1)
    
    intervention2 = TreatmentIntervention(
        date=datetime.now() - timedelta(days=15),
        intervention_type="生活方式干预",
        description="规律作息，固定进餐时间，增加血糖监测频率",
        expected_effect="建立血糖节律，降低混沌指数"
    )
    tracker.add_intervention(intervention2)
    
    # 3. 第一次随访期（干预后1周）
    print(f"\n3. 第一次随访期分析")
    np.random.seed(123)
    followup1_glucose = []
    for i in range(96):
        # 模拟治疗后改善：变异性降低，但仍有波动
        base = 8.5 + 2 * np.sin(i * 0.1) + np.random.normal(0, 1.8)
        if np.random.random() < 0.05:  # 极端值概率降低
            base += np.random.uniform(-3, 4)
        followup1_glucose.append(np.clip(base, 3, 16))
    
    followup1_start = datetime.now() - timedelta(days=14)
    followup1_end = followup1_start + timedelta(days=1)
    
    tracker.add_follow_up_period(followup1_glucose, followup1_start, followup1_end)
    
    # 4. 第二次随访期（干预后3周）
    print(f"\n4. 第二次随访期分析")
    np.random.seed(456)
    followup2_glucose = []
    for i in range(96):
        # 模拟持续改善：更加稳定
        base = 7.8 + 1.5 * np.sin(i * 0.1) + np.random.normal(0, 1.2)
        if np.random.random() < 0.02:  # 极端值进一步降低
            base += np.random.uniform(-2, 2)
        followup2_glucose.append(np.clip(base, 4, 12))
    
    followup2_start = datetime.now() - timedelta(days=7)
    followup2_end = followup2_start + timedelta(days=1)
    
    tracker.add_follow_up_period(followup2_glucose, followup2_start, followup2_end)
    
    # 5. 生成综合报告
    print(f"\n" + "="*50)
    print("生成综合治疗效果报告")
    print("="*50)
    
    comprehensive_report = tracker.generate_comprehensive_report()
    
    print(f"\n【追踪概览】")
    print(f"  患者ID: {comprehensive_report['患者ID']}")
    print(f"  追踪总天数: {comprehensive_report['追踪概览']['追踪总天数']} 天")
    print(f"  随访期数: {comprehensive_report['追踪概览']['随访期数']} 次")
    print(f"  治疗干预: {comprehensive_report['追踪概览']['治疗干预次数']} 次")
    
    print(f"\n【治疗效果总结】")
    print(f"  脆性类型: {comprehensive_report['总体变化']['脆性类型变化']}")
    print(f"  临床评分: {comprehensive_report['基线指标']['临床评分']:.1f} → "
          f"{comprehensive_report['最新指标']['临床评分']:.1f} "
          f"({comprehensive_report['总体变化']['临床评分变化']:+.1f})")
    print(f"  TIR: {comprehensive_report['基线指标']['TIR']:.1f}% → "
          f"{comprehensive_report['最新指标']['TIR']:.1f}% "
          f"({comprehensive_report['总体变化']['TIR变化']:+.1f}%)")
    print(f"  CV: {comprehensive_report['基线指标']['CV']:.1f}% → "
          f"{comprehensive_report['最新指标']['CV']:.1f}% "
          f"({comprehensive_report['总体变化']['CV变化']:+.1f}%)")
    print(f"  Lyapunov: {comprehensive_report['基线指标']['Lyapunov指数']:.4f} → "
          f"{comprehensive_report['最新指标']['Lyapunov指数']:.4f} "
          f"({comprehensive_report['总体变化']['Lyapunov变化']:+.4f})")
    
    print(f"\n【治疗干预记录】")
    for i, intervention in enumerate(comprehensive_report['治疗干预'], 1):
        print(f"  {i}. {intervention['日期']}: {intervention['类型']}")
        print(f"     描述: {intervention['描述']}")
        print(f"     预期: {intervention['预期效果']}")
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/Users/williamsun/Documents/gplus/docs/AGPAI/agpai/reports/Treatment_Tracking_Report_{timestamp}.json"
    
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_report, f, ensure_ascii=False, indent=2, default=json_serial)
    
    print(f"\n详细追踪报告已保存至: {output_file}")
    print("="*70)

if __name__ == "__main__":
    demonstrate_treatment_tracking()