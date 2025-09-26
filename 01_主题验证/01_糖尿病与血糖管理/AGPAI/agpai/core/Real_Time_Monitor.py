"""
血糖混沌分析实时监测预警系统
基于混沌指标的智能预警和风险评估
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import deque
import json
import warnings
warnings.filterwarnings('ignore')

class RealTimeGlucoseMonitor:
    """
    实时血糖监测与混沌分析预警系统
    """
    
    def __init__(self, window_size=96, alert_threshold_config=None):
        """
        初始化监测器
        
        Args:
            window_size: 滑动窗口大小（默认96 = 24小时，15分钟间隔）
            alert_threshold_config: 预警阈值配置
        """
        self.window_size = window_size
        self.glucose_buffer = deque(maxlen=window_size)
        self.time_buffer = deque(maxlen=window_size)
        
        # 预警阈值配置
        self.thresholds = alert_threshold_config or {
            "critical": {
                "lyapunov": 0.15,      # 临界混沌阈值
                "cv": 50,              # 临界变异系数
                "low_glucose": 3.0,    # 严重低血糖
                "high_glucose": 16.7   # 严重高血糖
            },
            "warning": {
                "lyapunov": 0.05,      # 警告混沌阈值
                "cv": 36,              # 警告变异系数
                "low_glucose": 3.9,    # 低血糖警告
                "high_glucose": 13.9   # 高血糖警告
            },
            "trend": {
                "rapid_change": 3.0,   # 快速变化阈值 (mmol/L/15min)
                "sustained_trend": 5   # 持续趋势时长（个数据点）
            }
        }
        
        # 预警状态
        self.current_alerts = []
        self.alert_history = []
        self.last_analysis_time = None
        self.brittleness_trend = deque(maxlen=10)  # 脆性类型趋势
        
        # 系统状态
        self.is_monitoring = False
        self.total_alerts = 0
        
    def add_glucose_reading(self, glucose_value, timestamp=None):
        """
        添加新的血糖读数
        
        Args:
            glucose_value: 血糖值 (mmol/L)
            timestamp: 时间戳（默认当前时间）
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # 验证数据合理性
        if not (1.0 <= glucose_value <= 30.0):
            self.add_alert("数据异常", f"血糖值异常: {glucose_value} mmol/L", "warning")
            return
        
        # 添加到缓冲区
        self.glucose_buffer.append(glucose_value)
        self.time_buffer.append(timestamp)
        
        # 实时分析
        if len(self.glucose_buffer) >= 20:  # 最少需要20个数据点
            self.real_time_analysis()
            
        self.is_monitoring = True
        
    def real_time_analysis(self):
        """
        实时分析当前血糖状态
        """
        current_time = datetime.now()
        glucose_data = np.array(list(self.glucose_buffer))
        
        # 清除过期警报
        self.clear_expired_alerts()
        
        # 1. 即时危险检查
        self.check_immediate_risks(glucose_data[-1], current_time)
        
        # 2. 趋势分析 
        if len(glucose_data) >= 5:
            self.check_glucose_trends(glucose_data, current_time)
            
        # 3. 混沌分析（需要足够数据点）
        if len(glucose_data) >= 50:
            self.chaos_analysis_alerts(glucose_data, current_time)
            
        # 4. 脆性分型监测
        if len(glucose_data) >= self.window_size // 2:
            self.monitor_brittleness_changes(glucose_data, current_time)
            
        self.last_analysis_time = current_time
        
    def check_immediate_risks(self, current_glucose, timestamp):
        """
        检查即时危险
        """
        # 严重低血糖
        if current_glucose < self.thresholds["critical"]["low_glucose"]:
            self.add_alert("严重低血糖", 
                          f"血糖值 {current_glucose:.1f} mmol/L < {self.thresholds['critical']['low_glucose']} mmol/L",
                          "critical", timestamp)
        elif current_glucose < self.thresholds["warning"]["low_glucose"]:
            self.add_alert("低血糖警告",
                          f"血糖值 {current_glucose:.1f} mmol/L 接近低血糖范围",
                          "warning", timestamp)
            
        # 严重高血糖
        if current_glucose > self.thresholds["critical"]["high_glucose"]:
            self.add_alert("严重高血糖",
                          f"血糖值 {current_glucose:.1f} mmol/L > {self.thresholds['critical']['high_glucose']} mmol/L",
                          "critical", timestamp)
        elif current_glucose > self.thresholds["warning"]["high_glucose"]:
            self.add_alert("高血糖警告",
                          f"血糖值 {current_glucose:.1f} mmol/L 超过正常范围",
                          "warning", timestamp)
    
    def check_glucose_trends(self, glucose_data, timestamp):
        """
        检查血糖趋势
        """
        recent_data = glucose_data[-10:]  # 最近10个数据点
        
        # 计算变化率
        changes = np.diff(recent_data)
        
        # 快速变化检查
        if len(changes) > 0:
            max_change = np.max(np.abs(changes))
            if max_change > self.thresholds["trend"]["rapid_change"]:
                direction = "上升" if changes[-1] > 0 else "下降"
                self.add_alert("血糖快速变化",
                              f"血糖快速{direction} {max_change:.1f} mmol/L/15min",
                              "warning", timestamp)
        
        # 持续趋势检查
        if len(recent_data) >= self.thresholds["trend"]["sustained_trend"]:
            # 检查是否持续上升或下降
            trend_length = 0
            if len(changes) >= 3:
                # 连续上升
                for i in range(len(changes)-1, -1, -1):
                    if changes[i] > 0.5:  # 持续上升
                        trend_length += 1
                    else:
                        break
                
                if trend_length >= self.thresholds["trend"]["sustained_trend"]:
                    self.add_alert("持续上升趋势",
                                  f"血糖持续上升 {trend_length} 个数据点",
                                  "warning", timestamp)
                
                # 连续下降
                trend_length = 0
                for i in range(len(changes)-1, -1, -1):
                    if changes[i] < -0.5:  # 持续下降
                        trend_length += 1
                    else:
                        break
                        
                if trend_length >= self.thresholds["trend"]["sustained_trend"]:
                    self.add_alert("持续下降趋势",
                                  f"血糖持续下降 {trend_length} 个数据点",
                                  "warning", timestamp)
    
    def chaos_analysis_alerts(self, glucose_data, timestamp):
        """
        混沌分析预警
        """
        try:
            # 计算混沌指标
            chaos_metrics = self.calculate_chaos_metrics(glucose_data)
            
            # Lyapunov指数预警
            lyapunov = chaos_metrics.get('lyapunov', 0)
            if lyapunov > self.thresholds["critical"]["lyapunov"]:
                self.add_alert("血糖系统混沌",
                              f"Lyapunov指数 {lyapunov:.4f} 表明系统极不稳定",
                              "critical", timestamp)
            elif lyapunov > self.thresholds["warning"]["lyapunov"]:
                self.add_alert("系统不稳定预警",
                              f"Lyapunov指数 {lyapunov:.4f} 显示系统趋向不稳定",
                              "warning", timestamp)
            
            # CV预警
            mean_glucose = np.mean(glucose_data)
            cv = (np.std(glucose_data) / mean_glucose) * 100
            
            if cv > self.thresholds["critical"]["cv"]:
                self.add_alert("极高血糖变异",
                              f"变异系数 {cv:.1f}% 远超安全范围",
                              "critical", timestamp)
            elif cv > self.thresholds["warning"]["cv"]:
                self.add_alert("血糖变异过高",
                              f"变异系数 {cv:.1f}% 超过稳定阈值",
                              "warning", timestamp)
            
            # 近似熵预警
            approx_entropy = chaos_metrics.get('approximate_entropy', 0)
            if approx_entropy > 0.8:
                self.add_alert("血糖模式复杂化",
                              f"近似熵 {approx_entropy:.3f} 表明血糖模式极度复杂",
                              "warning", timestamp)
        
        except Exception as e:
            self.add_alert("混沌分析错误",
                          f"混沌分析计算错误: {str(e)}",
                          "info", timestamp)
    
    def monitor_brittleness_changes(self, glucose_data, timestamp):
        """
        监测脆性类型变化
        """
        try:
            # 计算当前脆性类型
            current_type = self.classify_brittleness(glucose_data)
            self.brittleness_trend.append(current_type)
            
            # 检查脆性类型突变
            if len(self.brittleness_trend) >= 3:
                recent_types = list(self.brittleness_trend)[-3:]
                
                # 如果连续变化到更危险的类型
                danger_levels = {
                    "稳定型": 0,
                    "中等不稳定型": 1,
                    "IV型记忆缺失脆性": 2,
                    "II型准周期脆性": 3,
                    "III型随机脆性": 4,
                    "I型混沌脆性": 5
                }
                
                current_level = danger_levels.get(current_type, 0)
                previous_level = danger_levels.get(recent_types[0], 0)
                
                if current_level > previous_level + 1:  # 危险级别跳跃提升
                    self.add_alert("脆性类型恶化",
                                  f"脆性类型从 {recent_types[0]} 变为 {current_type}",
                                  "critical", timestamp)
                elif current_level > previous_level:
                    self.add_alert("脆性类型变化",
                                  f"脆性类型变为 {current_type}",
                                  "warning", timestamp)
        
        except Exception as e:
            pass  # 静默处理分类错误
    
    def calculate_chaos_metrics(self, glucose_data):
        """
        计算混沌指标
        """
        metrics = {}
        
        try:
            # Lyapunov指数估计
            rate_changes = np.diff(glucose_data)
            divergence = []
            for i in range(len(rate_changes)-1):
                if abs(rate_changes[i]) > 0.01:
                    ratio = abs(rate_changes[i+1]) / abs(rate_changes[i])
                    if ratio > 0:
                        divergence.append(np.log(ratio))
            
            metrics['lyapunov'] = np.mean(divergence) if divergence else 0
            
            # 近似熵
            def approx_entropy(data, m=2, r=0.2):
                N = len(data)
                if N < 10:
                    return 0
                
                patterns = [data[i:i+m] for i in range(N-m+1)]
                phi_m = 0
                phi_m1 = 0
                
                for i in range(len(patterns)):
                    template = patterns[i]
                    matches_m = 0
                    matches_m1 = 0
                    
                    for j in range(len(patterns)):
                        if max([abs(a-b) for a, b in zip(template, patterns[j])]) <= r * np.std(data):
                            matches_m += 1
                            
                    for j in range(N-m):
                        template_ext = data[i:i+m+1] if i+m+1 <= N else None
                        pattern_ext = data[j:j+m+1] if j+m+1 <= N else None
                        
                        if template_ext and pattern_ext:
                            if max([abs(a-b) for a, b in zip(template_ext, pattern_ext)]) <= r * np.std(data):
                                matches_m1 += 1
                    
                    if matches_m > 0:
                        phi_m += np.log(matches_m / (N-m+1))
                    if matches_m1 > 0:
                        phi_m1 += np.log(matches_m1 / (N-m))
                
                phi_m /= (N-m+1)
                phi_m1 /= (N-m)
                
                return phi_m - phi_m1
            
            metrics['approximate_entropy'] = approx_entropy(glucose_data)
            
        except Exception as e:
            metrics = {'lyapunov': 0, 'approximate_entropy': 0}
            
        return metrics
    
    def classify_brittleness(self, glucose_data):
        """
        分类血糖脆性类型
        """
        try:
            mean_glucose = np.mean(glucose_data)
            cv = (np.std(glucose_data) / mean_glucose) * 100
            
            # 计算混沌指标
            chaos_metrics = self.calculate_chaos_metrics(glucose_data)
            lyapunov = chaos_metrics.get('lyapunov', 0)
            approx_entropy = chaos_metrics.get('approximate_entropy', 0)
            
            # 分类逻辑
            if lyapunov > 0.1 and cv > 40:
                return "I型混沌脆性"
            elif lyapunov > 0.01 and cv > 30:
                return "II型准周期脆性"
            elif cv > 35 and approx_entropy > 0.6:
                return "III型随机脆性"
            elif approx_entropy > 0.5:
                return "IV型记忆缺失脆性"
            elif cv < 30:
                return "稳定型"
            else:
                return "中等不稳定型"
                
        except Exception:
            return "未知类型"
    
    def add_alert(self, alert_type, message, severity, timestamp=None):
        """
        添加预警
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        alert = {
            "id": f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{len(self.current_alerts)}",
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": timestamp,
            "status": "active"
        }
        
        # 避免重复预警（5分钟内同类型）
        recent_alerts = [a for a in self.current_alerts 
                        if a["type"] == alert_type and 
                        (timestamp - a["timestamp"]).total_seconds() < 300]
        
        if not recent_alerts:
            self.current_alerts.append(alert)
            self.alert_history.append(alert.copy())
            self.total_alerts += 1
            
            # 打印实时预警
            severity_symbols = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}
            print(f"{severity_symbols.get(severity, '•')} {alert_type}: {message}")
    
    def clear_expired_alerts(self, expiry_minutes=60):
        """
        清除过期预警
        """
        current_time = datetime.now()
        self.current_alerts = [
            alert for alert in self.current_alerts
            if (current_time - alert["timestamp"]).total_seconds() < expiry_minutes * 60
        ]
    
    def get_current_status(self):
        """
        获取当前监测状态
        """
        if not self.glucose_buffer:
            return {
                "status": "未开始监测",
                "current_glucose": None,
                "alerts": [],
                "brittleness_type": "未知",
                "monitoring_duration": 0
            }
        
        current_glucose = list(self.glucose_buffer)[-1]
        glucose_data = np.array(list(self.glucose_buffer))
        
        # 计算基础指标
        mean_glucose = np.mean(glucose_data)
        cv = (np.std(glucose_data) / mean_glucose) * 100 if len(glucose_data) > 1 else 0
        
        # TIR计算
        tir = np.sum((glucose_data >= 3.9) & (glucose_data <= 10.0)) / len(glucose_data) * 100
        
        # 当前脆性类型
        current_brittleness = self.classify_brittleness(glucose_data) if len(glucose_data) >= 20 else "数据不足"
        
        # 监测时长
        if len(self.time_buffer) >= 2:
            duration_hours = (list(self.time_buffer)[-1] - list(self.time_buffer)[0]).total_seconds() / 3600
        else:
            duration_hours = 0
        
        return {
            "status": "正在监测",
            "current_glucose": current_glucose,
            "mean_glucose": mean_glucose,
            "cv": cv,
            "tir": tir,
            "active_alerts": len([a for a in self.current_alerts if a["status"] == "active"]),
            "total_alerts": self.total_alerts,
            "brittleness_type": current_brittleness,
            "monitoring_duration": duration_hours,
            "data_points": len(self.glucose_buffer),
            "recent_alerts": self.current_alerts[-5:]  # 最近5个预警
        }
    
    def generate_monitoring_report(self):
        """
        生成监测报告
        """
        status = self.get_current_status()
        
        report = {
            "报告生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "监测状态": status,
            "预警统计": {
                "总预警数": self.total_alerts,
                "活跃预警": len([a for a in self.current_alerts if a["status"] == "active"]),
                "严重预警": len([a for a in self.alert_history if a["severity"] == "critical"]),
                "警告预警": len([a for a in self.alert_history if a["severity"] == "warning"])
            },
            "脆性类型趋势": list(self.brittleness_trend) if self.brittleness_trend else [],
            "近期预警": self.current_alerts[-10:] if self.current_alerts else [],
            "建议": self.generate_recommendations(status)
        }
        
        return report
    
    def generate_recommendations(self, status):
        """
        生成建议
        """
        recommendations = []
        
        brittleness = status.get("brittleness_type", "未知")
        cv = status.get("cv", 0)
        active_alerts = status.get("active_alerts", 0)
        
        # 基于脆性类型的建议
        if "混沌脆性" in brittleness:
            recommendations.append("血糖系统处于混沌状态，建议立即联系医生调整治疗方案")
            recommendations.append("避免强化治疗，采用保守血糖目标")
            recommendations.append("考虑24小时持续监护")
        elif "随机脆性" in brittleness:
            recommendations.append("血糖变化随机性强，建议考虑智能胰岛素泵治疗")
            recommendations.append("增加监测频率，评估神经功能")
        elif cv > 36:
            recommendations.append("血糖变异性过高，需要优化治疗方案")
        
        # 基于预警的建议
        if active_alerts >= 3:
            recommendations.append("当前预警较多，建议密切关注血糖变化")
        
        if not recommendations:
            recommendations.append("当前血糖状态相对稳定，继续保持现有治疗方案")
            
        return recommendations

def simulate_real_time_monitoring():
    """
    模拟实时监测演示
    """
    print("="*60)
    print("血糖混沌分析实时监测系统演示")
    print("="*60)
    
    # 创建监测器
    monitor = RealTimeGlucoseMonitor()
    
    # 模拟血糖数据流
    print("开始模拟实时血糖数据流...\n")
    
    # 模拟不同阶段的血糖变化
    scenarios = [
        # 阶段1：正常稳定
        {"name": "正常稳定期", "base": 7.5, "variation": 0.5, "points": 20},
        # 阶段2：逐渐上升
        {"name": "血糖上升期", "base": 9.0, "variation": 1.0, "points": 15},
        # 阶段3：高血糖波动
        {"name": "高血糖波动期", "base": 12.0, "variation": 3.0, "points": 20},
        # 阶段4：混沌期
        {"name": "混沌不稳定期", "base": 8.0, "variation": 5.0, "points": 25},
        # 阶段5：恢复期
        {"name": "恢复稳定期", "base": 7.0, "variation": 0.8, "points": 15}
    ]
    
    current_time = datetime.now()
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        for i in range(scenario["points"]):
            # 生成模拟血糖值
            if scenario["name"] == "混沌不稳定期":
                # 混沌模式：大幅随机波动
                glucose = scenario["base"] + np.random.uniform(-scenario["variation"], scenario["variation"])
                if np.random.random() < 0.2:  # 20%概率极端值
                    glucose += np.random.uniform(-8, 8)
            elif scenario["name"] == "血糖上升期":
                # 持续上升趋势
                glucose = scenario["base"] + i * 0.3 + np.random.normal(0, scenario["variation"])
            else:
                # 正常模式
                glucose = scenario["base"] + np.random.normal(0, scenario["variation"])
            
            glucose = np.clip(glucose, 2.0, 20.0)
            
            # 添加到监测器
            current_time += timedelta(minutes=15)
            monitor.add_glucose_reading(glucose, current_time)
            
            # 每5个数据点显示一次状态
            if (i + 1) % 5 == 0:
                status = monitor.get_current_status()
                print(f"  当前血糖: {status['current_glucose']:.1f} mmol/L, "
                      f"CV: {status['cv']:.1f}%, 脆性类型: {status['brittleness_type']}")
    
    # 生成最终报告
    print("\n" + "="*60)
    print("监测完成 - 生成综合报告")
    print("="*60)
    
    final_report = monitor.generate_monitoring_report()
    
    print(f"监测时长: {final_report['监测状态']['monitoring_duration']:.1f} 小时")
    print(f"数据点数: {final_report['监测状态']['data_points']} 个")
    print(f"总预警数: {final_report['预警统计']['总预警数']} 个")
    print(f"当前脆性类型: {final_report['监测状态']['brittleness_type']}")
    
    print(f"\n预警分布:")
    print(f"  严重预警: {final_report['预警统计']['严重预警']} 个")
    print(f"  警告预警: {final_report['预警统计']['警告预警']} 个")
    
    print(f"\n脆性类型变化:")
    for i, btype in enumerate(final_report['脆性类型趋势']):
        print(f"  阶段{i+1}: {btype}")
    
    print(f"\n临床建议:")
    for i, rec in enumerate(final_report['建议'], 1):
        print(f"  {i}. {rec}")
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/Users/williamsun/Documents/gplus/docs/AGPAI/agpai/reports/Real_Time_Monitor_Report_{timestamp}.json"
    
    # 处理时间序列化问题
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2, default=json_serial)
    
    print(f"\n详细报告已保存至: {output_file}")
    print("="*60)

if __name__ == "__main__":
    simulate_real_time_monitoring()