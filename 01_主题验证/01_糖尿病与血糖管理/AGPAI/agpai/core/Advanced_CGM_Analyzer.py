"""
高级CGM数据分析器
包含传统指标和混沌分析指标的完整计算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from scipy.fft import fft, fftfreq
import json
import warnings
warnings.filterwarnings('ignore')

class AdvancedCGMAnalyzer:
    """
    高级CGM分析器 - 整合传统指标与混沌分析
    """
    
    def __init__(self):
        # 目标范围定义
        self.target_low = 3.9
        self.target_high = 10.0
        self.very_low = 3.0
        self.very_low_severe = 2.2
        self.high_level1 = 13.9
        self.high_level2 = 16.7
        self.very_high = 22.2
        
    def load_cgm_data(self, file_path):
        """
        加载CGM数据
        """
        try:
            df = pd.read_csv(file_path)
            
            # 数据预处理
            df['LBDTC'] = pd.to_datetime(df['LBDTC'])
            df['glucose'] = df['LBORRES'].astype(float)
            df = df.sort_values('LBDTC').reset_index(drop=True)
            
            return df[['LBDTC', 'glucose']]
        except Exception as e:
            print(f"数据加载错误: {e}")
            return None
    
    def calculate_basic_stats(self, glucose_values):
        """
        计算基础统计指标
        """
        results = {}
        
        # 基础统计
        results['总读取数'] = len(glucose_values)
        results['平均血糖'] = np.mean(glucose_values)
        results['血糖中位数'] = np.median(glucose_values)
        results['血糖标准差'] = np.std(glucose_values)
        results['血糖变异系数'] = (results['血糖标准差'] / results['平均血糖']) * 100
        results['最低血糖'] = np.min(glucose_values)
        results['最高血糖'] = np.max(glucose_values)
        results['血糖范围'] = results['最高血糖'] - results['最低血糖']
        
        # 分位数
        results['Q25'] = np.percentile(glucose_values, 25)
        results['Q75'] = np.percentile(glucose_values, 75)
        results['四分位距'] = results['Q75'] - results['Q25']
        
        # 偏度和峰度
        results['偏度'] = stats.skew(glucose_values)
        results['峰度'] = stats.kurtosis(glucose_values)
        
        return results
    
    def calculate_tir_analysis(self, glucose_values):
        """
        计算TIR分析指标
        """
        results = {}
        total = len(glucose_values)
        
        # 各区间时间百分比
        very_low_severe_count = np.sum(glucose_values < self.very_low_severe)
        very_low_count = np.sum((glucose_values >= self.very_low_severe) & 
                               (glucose_values < self.very_low))
        low_count = np.sum((glucose_values >= self.very_low) & 
                          (glucose_values < self.target_low))
        target_count = np.sum((glucose_values >= self.target_low) & 
                             (glucose_values <= self.target_high))
        high_level1_count = np.sum((glucose_values > self.target_high) & 
                                  (glucose_values <= self.high_level1))
        high_level2_count = np.sum((glucose_values > self.high_level1) & 
                                  (glucose_values <= self.high_level2))
        very_high_count = np.sum((glucose_values > self.high_level2) & 
                                (glucose_values <= self.very_high))
        extreme_high_count = np.sum(glucose_values > self.very_high)
        
        results['极严重低血糖时间%'] = (very_low_severe_count / total) * 100
        results['严重低血糖时间%'] = (very_low_count / total) * 100
        results['低血糖时间%'] = (low_count / total) * 100
        results['目标范围时间% (TIR)'] = (target_count / total) * 100
        results['轻度高血糖时间%'] = (high_level1_count / total) * 100
        results['中度高血糖时间%'] = (high_level2_count / total) * 100
        results['严重高血糖时间%'] = (very_high_count / total) * 100
        results['极严重高血糖时间%'] = (extreme_high_count / total) * 100
        
        # 总低血糖时间
        results['总低血糖时间%'] = (results['极严重低血糖时间%'] + 
                               results['严重低血糖时间%'] + 
                               results['低血糖时间%'])
        
        return results
    
    def calculate_variability_metrics(self, glucose_values):
        """
        计算变异性指标
        """
        results = {}
        
        # CV (已在基础统计中计算)
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        results['CV%'] = (std_glucose / mean_glucose) * 100
        
        # MAGE - 平均血糖波动幅度
        # 简化版本：计算超过1个标准差的变化
        excursions = []
        for i in range(1, len(glucose_values)):
            diff = abs(glucose_values[i] - glucose_values[i-1])
            if diff > std_glucose:
                excursions.append(diff)
        
        results['MAGE'] = np.mean(excursions) if excursions else 0
        
        # 中位绝对偏差
        median_glucose = np.median(glucose_values)
        results['MAD'] = np.median(np.abs(glucose_values - median_glucose))
        
        # 变化率相关指标
        rate_of_change = np.diff(glucose_values)
        results['平均变化率'] = np.mean(np.abs(rate_of_change))
        results['最大变化率'] = np.max(np.abs(rate_of_change))
        results['变化率标准差'] = np.std(rate_of_change)
        
        return results
    
    def calculate_risk_indices(self, glucose_values):
        """
        计算风险指数
        """
        results = {}
        
        # 简化的LBGI和HBGI计算
        # 使用对数变换的风险函数
        def risk_function(bg, is_low=False):
            if is_low:
                # 低血糖风险
                if bg >= 3.9:
                    return 0
                else:
                    return (3.35 - 1.794 * np.log(bg)) ** 2
            else:
                # 高血糖风险  
                if bg <= 10.0:
                    return 0
                else:
                    return (1.794 * np.log(bg) - 3.35) ** 2
        
        # 计算每个血糖值的风险
        low_risks = [risk_function(bg, is_low=True) for bg in glucose_values]
        high_risks = [risk_function(bg, is_low=False) for bg in glucose_values]
        
        results['LBGI'] = np.mean(low_risks)
        results['HBGI'] = np.mean(high_risks)
        results['BGRI'] = results['LBGI'] + results['HBGI']
        
        # 简化的ADRR计算
        results['ADRR'] = results['LBGI'] + results['HBGI']
        
        return results
    
    def calculate_chaos_metrics(self, glucose_values):
        """
        计算混沌分析指标 (简化版本)
        """
        results = {}
        
        try:
            # Shannon熵
            hist, _ = np.histogram(glucose_values, bins=50, density=True)
            hist = hist[hist > 0]  # 移除零值
            results['Shannon熵'] = -np.sum(hist * np.log2(hist))
            
            # 近似熵 (简化计算)
            def approximate_entropy(data, m=2, r=0.2):
                N = len(data)
                if N < 10:
                    return 0
                
                def _maxdist(xi, xj, N, m):
                    return max([abs(ua - va) for ua, va in zip(xi, xj)])
                
                def _phi(m):
                    patterns = np.array([data[i:i+m] for i in range(N-m+1)])
                    C = np.zeros(N-m+1)
                    
                    for i in range(N-m+1):
                        template = patterns[i]
                        for j in range(N-m+1):
                            if _maxdist(template, patterns[j], N, m) <= r * np.std(data):
                                C[i] += 1
                    
                    phi = np.mean(np.log(C / (N-m+1)))
                    return phi
                
                return _phi(m) - _phi(m+1)
            
            results['近似熵'] = approximate_entropy(glucose_values)
            
            # Hurst指数 (R/S分析简化版本)
            def hurst_exponent(data):
                try:
                    lags = range(2, min(100, len(data)//4))
                    tau = [np.std(np.subtract(data[lag:], data[:-lag])) for lag in lags]
                    poly = np.polyfit(np.log(lags), np.log(tau), 1)
                    return poly[0]
                except:
                    return 0.5
            
            results['Hurst指数'] = hurst_exponent(glucose_values)
            
            # 简化的Lyapunov指数估计
            # 使用相邻点发散的平均对数增长率
            def lyapunov_estimate(data, lag=1):
                try:
                    divergence = []
                    for i in range(len(data) - 2*lag):
                        d1 = abs(data[i+lag] - data[i])
                        d2 = abs(data[i+2*lag] - data[i+lag])
                        if d1 > 0 and d2 > 0:
                            divergence.append(np.log(d2/d1))
                    
                    return np.mean(divergence) if divergence else 0
                except:
                    return 0
            
            results['Lyapunov指数估计'] = lyapunov_estimate(glucose_values)
            
        except Exception as e:
            print(f"混沌指标计算错误: {e}")
            results['Shannon熵'] = 0
            results['近似熵'] = 0
            results['Hurst指数'] = 0.5
            results['Lyapunov指数估计'] = 0
            
        return results
    
    def calculate_clinical_metrics(self, glucose_values):
        """
        计算临床质量指标
        """
        results = {}
        
        # GMI (Glucose Management Indicator)
        mean_glucose = np.mean(glucose_values)
        results['GMI%'] = 3.31 + 0.02392 * mean_glucose * 18.018  # 转换为mg/dL计算
        
        # 估算平均血糖 (eAG)
        results['eAG_mmol/L'] = mean_glucose
        
        # 简化的系统健康指标
        cv = (np.std(glucose_values) / mean_glucose) * 100
        tir = np.sum((glucose_values >= self.target_low) & 
                    (glucose_values <= self.target_high)) / len(glucose_values) * 100
        
        # β细胞功能指数 (简化估计)
        glucose_variability = cv / 100
        results['BCFI估计'] = max(0, 1 - glucose_variability)
        
        # 胰岛素抵抗代理指标 (基于血糖水平和变异性)
        results['IRPI估计'] = mean_glucose / 5.6 * (1 + glucose_variability)
        
        # 代谢应激指数
        results['MSI估计'] = cv / 10 * (mean_glucose / 7.0)
        
        # 稳态效率
        results['HE估计'] = tir / 100 * (1 - glucose_variability)
        
        return results
    
    def classify_brittleness_type(self, metrics):
        """
        血糖脆性分型
        """
        le = metrics.get('Lyapunov指数估计', 0)
        apen = metrics.get('近似熵', 0)
        cv = metrics.get('CV%', 0)
        shannon = metrics.get('Shannon熵', 0)
        hurst = metrics.get('Hurst指数', 0.5)
        
        # I型：混沌脆性
        if le > 0.1 and apen > 0.7 and cv > 40:
            return "I型混沌脆性", "系统完全失去可预测性，微小扰动引发巨大血糖波动"
        
        # II型：准周期脆性
        elif le > 0.01 and le <= 0.1 and cv > 30:
            return "II型准周期脆性", "血糖呈现复杂但有规律的周期性振荡"
        
        # III型：随机脆性
        elif le <= 0.01 and shannon > 0.8 and abs(hurst - 0.5) < 0.1:
            return "III型随机脆性", "血糖变化完全随机，无任何可识别模式"
        
        # IV型：记忆缺失脆性
        elif apen > 0.6 and hurst < 0.3:
            return "IV型记忆缺失脆性", "血糖调节系统失去'记忆'功能，无法维持稳态"
        
        # V型：频域脆性
        elif shannon > 0.7 and cv > 35:
            return "V型频域脆性", "血糖节律完全紊乱，昼夜调节机制失效"
        
        # 正常或轻度异常
        elif cv < 36 and le < 0.01:
            return "稳定型", "血糖调节系统稳定，变异性在可接受范围内"
        
        else:
            return "中等不稳定型", "血糖存在一定程度的不稳定性，需要关注"
    
    def generate_comprehensive_report(self, file_path, patient_id=None):
        """
        生成综合分析报告
        """
        # 加载数据
        df = self.load_cgm_data(file_path)
        if df is None:
            return None
        
        glucose_values = df['glucose'].values
        
        # 计算各类指标
        basic_stats = self.calculate_basic_stats(glucose_values)
        tir_analysis = self.calculate_tir_analysis(glucose_values)
        variability = self.calculate_variability_metrics(glucose_values)
        risk_indices = self.calculate_risk_indices(glucose_values)
        chaos_metrics = self.calculate_chaos_metrics(glucose_values)
        clinical_metrics = self.calculate_clinical_metrics(glucose_values)
        
        # 合并所有指标
        all_metrics = {**basic_stats, **tir_analysis, **variability, 
                      **risk_indices, **chaos_metrics, **clinical_metrics}
        
        # 血糖脆性分型
        brittleness_type, brittleness_description = self.classify_brittleness_type(all_metrics)
        
        # 生成报告
        report = {
            "患者信息": {
                "患者ID": patient_id or "未指定",
                "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "数据时间范围": f"{df['LBDTC'].min()} 至 {df['LBDTC'].max()}",
                "监测天数": (df['LBDTC'].max() - df['LBDTC'].min()).days + 1
            },
            
            "传统核心指标": {
                "TIR (目标范围时间%)": f"{all_metrics['目标范围时间% (TIR)']:.1f}%",
                "CV (变异系数%)": f"{all_metrics['CV%']:.1f}%",
                "GMI (血糖管理指标%)": f"{all_metrics['GMI%']:.1f}%",
                "平均血糖": f"{all_metrics['平均血糖']:.1f} mmol/L",
                "血糖标准差": f"{all_metrics['血糖标准差']:.2f} mmol/L"
            },
            
            "安全性评估": {
                "总低血糖时间%": f"{all_metrics['总低血糖时间%']:.2f}%",
                "LBGI (低血糖风险指数)": f"{all_metrics['LBGI']:.2f}",
                "严重低血糖时间%": f"{all_metrics['严重低血糖时间%']:.2f}%",
                "极严重低血糖时间%": f"{all_metrics['极严重低血糖时间%']:.2f}%"
            },
            
            "变异性分析": {
                "MAGE (平均血糖波动幅度)": f"{all_metrics['MAGE']:.2f} mmol/L",
                "MAD (中位绝对偏差)": f"{all_metrics['MAD']:.2f} mmol/L",
                "最大变化率": f"{all_metrics['最大变化率']:.3f} mmol/L/15min",
                "四分位距": f"{all_metrics['四分位距']:.2f} mmol/L"
            },
            
            "混沌分析指标": {
                "Lyapunov指数估计": f"{all_metrics['Lyapunov指数估计']:.4f}",
                "近似熵": f"{all_metrics['近似熵']:.3f}",
                "Shannon熵": f"{all_metrics['Shannon熵']:.3f}",
                "Hurst指数": f"{all_metrics['Hurst指数']:.3f}"
            },
            
            "病理生理评估": {
                "BCFI (β细胞功能指数估计)": f"{all_metrics['BCFI估计']:.3f}",
                "IRPI (胰岛素抵抗指数估计)": f"{all_metrics['IRPI估计']:.2f}",
                "MSI (代谢应激指数估计)": f"{all_metrics['MSI估计']:.2f}",
                "HE (稳态效率估计)": f"{all_metrics['HE估计']:.3f}"
            },
            
            "血糖脆性分型": {
                "分型结果": brittleness_type,
                "类型描述": brittleness_description
            },
            
            "临床建议": self.generate_clinical_recommendations(all_metrics, brittleness_type),
            
            "详细数值": all_metrics
        }
        
        return report
    
    def generate_clinical_recommendations(self, metrics, brittleness_type):
        """
        生成临床建议
        """
        recommendations = []
        
        tir = metrics.get('目标范围时间% (TIR)', 0)
        cv = metrics.get('CV%', 0)
        lbgi = metrics.get('LBGI', 0)
        le = metrics.get('Lyapunov指数估计', 0)
        
        # 基于TIR的建议
        if tir < 50:
            recommendations.append("TIR严重不达标(<50%)，需要全面重新评估治疗方案")
        elif tir < 70:
            recommendations.append("TIR不达标(<70%)，建议优化胰岛素治疗方案")
        else:
            recommendations.append("TIR达标(≥70%)，维持当前良好控制")
        
        # 基于变异性的建议
        if cv > 36:
            recommendations.append("血糖变异性过高(CV>36%)，需要改善血糖稳定性")
            if cv > 50:
                recommendations.append("血糖极不稳定，建议考虑胰岛素泵治疗")
        
        # 基于安全性的建议
        if lbgi > 5:
            recommendations.append("低血糖风险很高，需要调整胰岛素剂量，避免过度治疗")
        elif lbgi > 2.5:
            recommendations.append("存在低血糖风险，建议优化治疗方案")
        
        # 基于混沌指标的建议
        if "混沌脆性" in brittleness_type:
            recommendations.append("血糖系统处于混沌状态，建议:")
            recommendations.append("- 避免强化治疗，采用保守血糖目标")
            recommendations.append("- 24小时CGM监护，预防严重低血糖")
            recommendations.append("- 考虑胰岛移植等根本性治疗")
        elif "准周期脆性" in brittleness_type:
            recommendations.append("血糖存在病理性周期波动，建议:")
            recommendations.append("- 调整胰岛素给药时间，打破病理周期")
            recommendations.append("- 生活方式规律化")
            recommendations.append("- 重点管理Dawn现象")
        elif "随机脆性" in brittleness_type:
            recommendations.append("血糖变化随机性强，建议:")
            recommendations.append("- 考虑智能胰岛素泵+闭环系统")
            recommendations.append("- 频繁血糖监测")
            recommendations.append("- 评估并发症(神经病变等)")
        
        # 整合建议
        if le > 0.1 and tir > 70:
            recommendations.append("警告：TIR达标但系统不稳定('假性达标')，需要重新评估治疗目标")
        
        return recommendations

if __name__ == "__main__":
    # 演示分析功能
    analyzer = AdvancedCGMAnalyzer()
    
    # 分析示例数据
    file_path = "/Users/williamsun/Documents/gplus/HRS9531_305_cgms_simulation.csv"
    
    print("正在分析CGM数据...")
    report = analyzer.generate_comprehensive_report(file_path, patient_id="CN001001")
    
    if report:
        # 打印报告
        print("\n" + "="*60)
        print("CGM高级指标分析报告")
        print("="*60)
        
        for section, content in report.items():
            if section == "详细数值":
                continue
            
            print(f"\n【{section}】")
            if isinstance(content, dict):
                for key, value in content.items():
                    print(f"  {key}: {value}")
            elif isinstance(content, list):
                for item in content:
                    print(f"  • {item}")
            else:
                print(f"  {content}")
        
        print("\n" + "="*60)
        print("分析完成")
        print("="*60)
        
        # 保存详细报告为JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/Users/williamsun/Documents/gplus/docs/AGPAI/agpai/reports/Advanced_CGM_Report_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存至: {output_file}")
    
    else:
        print("数据分析失败")