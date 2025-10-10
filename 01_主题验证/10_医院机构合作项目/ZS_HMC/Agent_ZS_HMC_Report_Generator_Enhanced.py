#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent_ZS: 中山HMC CGM报告生成器 v2.0 (增强版)
基于GPlus报告样式的可视化增强版本

🎨 新增功能 (基于GPlus PDF模板):
✅ AGP (Ambulatory Glucose Profile) 可视化
✅ 14天每日血糖曲线小图 (Small Multiples)
✅ TIR/TAR/TBR 堆叠柱状图
✅ 百分位数带状图 (5-95%, 25-75%)
✅ HTML专业报告导出 (可打印为PDF)
✅ 响应式图表布局

版本: 2.0 Enhanced
日期: 2025-10-09
作者: Enhanced based on GPlus Report Template
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ZSHMCReportGeneratorEnhanced:
    """中山HMC CGM报告生成器 - 增强版（含GPlus样式可视化）"""

    def __init__(self):
        """初始化报告生成器"""
        self.version = "2.0-Enhanced"
        self.agent_type = "Agent_ZS_Enhanced"
        self.institution = "中山健康管理中心 (ZSHMC)"

    def generate_html_report(self, filepath: str, patient_id: str = None,
                           patient_info: Dict = None, medication_data: Dict = None,
                           output_path: str = None) -> str:
        """
        生成带可视化的HTML报告（GPlus样式）

        Args:
            filepath: 血糖数据文件路径
            patient_id: 患者ID
            patient_info: 患者基本信息
            medication_data: 用药信息
            output_path: HTML输出路径

        Returns:
            HTML文件路径
        """
        # 加载数据
        df = self._load_data(filepath)

        # 生成分析数据
        analysis = self._comprehensive_analysis(df, patient_info, medication_data)

        # 生成HTML
        html_content = self._generate_html_content(analysis, patient_id, patient_info)

        # 保存HTML
        if output_path is None:
            output_path = f"ZS_HMC_CGM_Report_{patient_id or 'Unknown'}_{datetime.now().strftime('%Y%m%d')}.html"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML报告已生成: {output_path}")
        return output_path

    def _load_data(self, filepath: str) -> pd.DataFrame:
        """加载CGM数据"""
        try:
            df = pd.read_csv(filepath)

            # 标准化列名
            column_mapping = {
                'timestamp': 'timestamp',
                'Timestamp': 'timestamp',
                'time': 'timestamp',
                'glucose': 'glucose_value',
                'Glucose': 'glucose_value',
                'glucose_value': 'glucose_value',
                'value': 'glucose_value'
            }

            df = df.rename(columns=column_mapping)

            # 确保timestamp是datetime类型
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            return df
        except Exception as e:
            raise ValueError(f"数据加载失败: {e}")

    def _comprehensive_analysis(self, df: pd.DataFrame, patient_info: Dict,
                                medication_data: Dict) -> Dict:
        """综合分析"""
        glucose_values = df['glucose_value'].dropna().values
        timestamps = df['timestamp'].values

        # 基础指标
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        gmi = 3.31 + (0.02392 * mean_glucose * 18.018)

        # TIR/TAR/TBR
        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar_level1 = np.sum((glucose_values > 10.0) & (glucose_values <= 13.9)) / len(glucose_values) * 100
        tar_level2 = np.sum(glucose_values > 13.9) / len(glucose_values) * 100
        tar = tar_level1 + tar_level2

        tbr_level1 = np.sum((glucose_values >= 3.0) & (glucose_values < 3.9)) / len(glucose_values) * 100
        tbr_level2 = np.sum(glucose_values < 3.0) / len(glucose_values) * 100
        tbr = tbr_level1 + tbr_level2

        # CV
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0

        # AGP数据（百分位数）
        agp_data = self._calculate_agp_profile(df)

        # 每日数据
        daily_data = self._calculate_daily_metrics(df)

        return {
            "summary_metrics": {
                "mean_glucose": mean_glucose,
                "gmi": gmi,
                "cv": cv,
                "tir": tir,
                "tar": tar,
                "tar_level1": tar_level1,
                "tar_level2": tar_level2,
                "tbr": tbr,
                "tbr_level1": tbr_level1,
                "tbr_level2": tbr_level2,
                "monitoring_days": len(daily_data),
                "total_points": len(glucose_values)
            },
            "agp_profile": agp_data,
            "daily_data": daily_data,
            "patient_info": patient_info or {},
            "medication_data": medication_data or {}
        }

    def _calculate_agp_profile(self, df: pd.DataFrame) -> Dict:
        """计算AGP曲线数据（每小时的百分位数）"""
        df = df.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['time_of_day'] = df['hour'] + df['minute'] / 60.0

        # 按时间点分组
        time_bins = np.arange(0, 24, 0.25)  # 每15分钟一个点
        agp_profile = {
            "time_points": [],
            "p5": [],
            "p25": [],
            "p50": [],
            "p75": [],
            "p95": []
        }

        for t in time_bins:
            # 获取该时间段附近的数据（±15分钟）
            mask = (df['time_of_day'] >= t - 0.25) & (df['time_of_day'] < t + 0.25)
            values = df[mask]['glucose_value'].dropna().values

            if len(values) > 0:
                agp_profile["time_points"].append(t)
                agp_profile["p5"].append(np.percentile(values, 5))
                agp_profile["p25"].append(np.percentile(values, 25))
                agp_profile["p50"].append(np.percentile(values, 50))
                agp_profile["p75"].append(np.percentile(values, 75))
                agp_profile["p95"].append(np.percentile(values, 95))

        return agp_profile

    def _calculate_daily_metrics(self, df: pd.DataFrame) -> List[Dict]:
        """计算每日指标"""
        df = df.copy()
        df['date'] = df['timestamp'].dt.date

        daily_data = []
        for date, group in df.groupby('date'):
            values = group['glucose_value'].dropna().values

            if len(values) == 0:
                continue

            mean_glucose = np.mean(values)
            std_glucose = np.std(values)

            daily_data.append({
                "date": str(date),
                "mean_glucose": mean_glucose,
                "std": std_glucose,
                "cv": (std_glucose / mean_glucose * 100) if mean_glucose > 0 else 0,
                "tir": np.sum((values >= 3.9) & (values <= 10.0)) / len(values) * 100,
                "tar": np.sum(values > 10.0) / len(values) * 100,
                "tbr": np.sum(values < 3.9) / len(values) * 100,
                "data_points": len(values),
                "glucose_values": values.tolist(),
                "timestamps": group['timestamp'].dt.strftime('%H:%M').tolist()
            })

        return daily_data

    def _generate_html_content(self, analysis: Dict, patient_id: str,
                              patient_info: Dict) -> str:
        """生成HTML内容"""
        summary = analysis['summary_metrics']
        agp = analysis['agp_profile']
        daily_data = analysis['daily_data']

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中山HMC CGM报告 - {patient_id or '未命名患者'}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        @page {{
            size: A4;
            margin: 1.5cm;
        }}

        body {{
            font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header {{
            border-bottom: 3px solid #2196F3;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            color: #1976D2;
            margin: 0 0 10px 0;
            font-size: 28px;
        }}

        .header .patient-info {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
            font-size: 14px;
        }}

        .info-item {{
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
        }}

        .info-label {{
            font-weight: 600;
            color: #555;
        }}

        .metrics-summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 30px 0;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .metric-card.green {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        }}

        .metric-card.orange {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}

        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}

        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .metric-reference {{
            font-size: 12px;
            margin-top: 5px;
            opacity: 0.8;
        }}

        .section {{
            margin: 40px 0;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 20px;
            color: #1976D2;
            border-left: 4px solid #2196F3;
            padding-left: 12px;
            margin-bottom: 20px;
        }}

        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}

        .chart-container.agp {{
            height: 400px;
        }}

        .daily-grid {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 15px;
            margin-top: 20px;
        }}

        .daily-card {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            background: #fafafa;
        }}

        .daily-date {{
            font-weight: 600;
            font-size: 12px;
            color: #1976D2;
            margin-bottom: 5px;
            text-align: center;
        }}

        .daily-chart {{
            height: 100px;
            margin: 10px 0;
        }}

        .daily-metrics {{
            font-size: 11px;
            line-height: 1.4;
        }}

        .metric-row {{
            display: flex;
            justify-content: space-between;
            margin: 2px 0;
        }}

        .tir-bar {{
            display: flex;
            height: 24px;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .tir-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 600;
            color: white;
        }}

        .tir-segment.tbr {{
            background: #f44336;
        }}

        .tir-segment.tir {{
            background: #4caf50;
        }}

        .tir-segment.tar {{
            background: #ff9800;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                padding: 0;
            }}

            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 报告头部 -->
        <div class="header">
            <h1>🏥 中山健康管理中心 - 持续血糖监测报告</h1>
            <div class="patient-info">
                <div class="info-item">
                    <span class="info-label">患者ID:</span> {patient_id or '未提供'}
                </div>
                <div class="info-item">
                    <span class="info-label">姓名:</span> {patient_info.get('name', '未提供') if patient_info else '未提供'}
                </div>
                <div class="info-item">
                    <span class="info-label">性别:</span> {patient_info.get('gender', '未提供') if patient_info else '未提供'}
                </div>
                <div class="info-item">
                    <span class="info-label">年龄:</span> {patient_info.get('age', '未提供') if patient_info else '未提供'}
                </div>
                <div class="info-item">
                    <span class="info-label">监测天数:</span> {summary['monitoring_days']}天
                </div>
                <div class="info-item">
                    <span class="info-label">报告日期:</span> {datetime.now().strftime('%Y-%m-%d')}
                </div>
            </div>
        </div>

        <!-- 核心指标摘要 -->
        <div class="metrics-summary">
            <div class="metric-card">
                <div class="metric-label">平均血糖 (MG)</div>
                <div class="metric-value">{summary['mean_glucose']:.1f}</div>
                <div class="metric-reference">mmol/L</div>
            </div>
            <div class="metric-card green">
                <div class="metric-label">血糖管理指标 (GMI)</div>
                <div class="metric-value">{summary['gmi']:.1f}%</div>
                <div class="metric-reference">目标 &lt; 7.0%</div>
            </div>
            <div class="metric-card orange">
                <div class="metric-label">目标范围内时间 (TIR)</div>
                <div class="metric-value">{summary['tir']:.1f}%</div>
                <div class="metric-reference">目标 &gt; 70%</div>
            </div>
        </div>

        <!-- TIR可视化条 -->
        <div class="section">
            <h2 class="section-title">📊 血糖分布总览</h2>
            <div class="tir-bar">
                <div class="tir-segment tbr" style="width: {summary['tbr']:.1f}%">
                    {f"{summary['tbr']:.1f}%" if summary['tbr'] > 5 else ""}
                </div>
                <div class="tir-segment tir" style="width: {summary['tir']:.1f}%">
                    TIR {summary['tir']:.1f}%
                </div>
                <div class="tir-segment tar" style="width: {summary['tar']:.1f}%">
                    {f"{summary['tar']:.1f}%" if summary['tar'] > 5 else ""}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 5px;">
                <span style="color: #f44336;">◼ TBR (&lt;3.9): {summary['tbr']:.1f}%</span>
                <span style="color: #4caf50;">◼ TIR (3.9-10.0): {summary['tir']:.1f}%</span>
                <span style="color: #ff9800;">◼ TAR (&gt;10.0): {summary['tar']:.1f}%</span>
            </div>
        </div>

        <!-- AGP曲线 -->
        <div class="section">
            <h2 class="section-title">📈 AGP (动态血糖图谱)</h2>
            <div class="chart-container agp">
                <canvas id="agpChart"></canvas>
            </div>
            <div style="font-size: 12px; color: #666; margin-top: 10px;">
                <p><strong>解读说明:</strong>
                浅蓝色区域代表5-95%百分位数范围，深蓝色区域代表25-75%百分位数范围，
                中间线为中位数(50%)。绿色带为目标范围(3.9-10.0 mmol/L)。
                </p>
            </div>
        </div>

        <!-- 每日血糖曲线 -->
        <div class="section">
            <h2 class="section-title">📅 14天每日血糖曲线</h2>
            <div class="daily-grid">
"""

        # 添加每日小图
        for i, day_data in enumerate(daily_data[:14]):  # 最多显示14天
            html += f"""
                <div class="daily-card">
                    <div class="daily-date">{day_data['date']}</div>
                    <div class="daily-chart">
                        <canvas id="dailyChart{i}"></canvas>
                    </div>
                    <div class="daily-metrics">
                        <div class="metric-row">
                            <span>TIR:</span>
                            <span style="color: #4caf50; font-weight: 600;">{day_data['tir']:.0f}%</span>
                        </div>
                        <div class="metric-row">
                            <span>平均:</span>
                            <span>{day_data['mean_glucose']:.1f}</span>
                        </div>
                        <div class="metric-row">
                            <span>CV:</span>
                            <span>{day_data['cv']:.1f}%</span>
                        </div>
                    </div>
                </div>
"""

        html += """
            </div>
        </div>

        <!-- 页脚 -->
        <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666;">
            <p><strong>声明:</strong> 本报告仅供医疗专业人员参考，不能替代医疗诊断。具体治疗方案请咨询医生。</p>
            <p>报告生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>报告版本: Agent_ZS v2.0 Enhanced (基于GPlus样式)</p>
        </div>
    </div>

    <script>
        // AGP Chart
        const agpCtx = document.getElementById('agpChart').getContext('2d');
        const agpData = """ + json.dumps(agp) + """;

        new Chart(agpCtx, {
            type: 'line',
            data: {
                labels: agpData.time_points.map(t => {
                    const hour = Math.floor(t);
                    const minute = Math.round((t - hour) * 60);
                    return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                }),
                datasets: [
                    {
                        label: '95th percentile',
                        data: agpData.p95,
                        borderColor: 'rgba(100, 181, 246, 0.3)',
                        backgroundColor: 'rgba(100, 181, 246, 0.1)',
                        fill: '+1',
                        borderWidth: 1,
                        pointRadius: 0
                    },
                    {
                        label: '75th percentile',
                        data: agpData.p75,
                        borderColor: 'rgba(33, 150, 243, 0.6)',
                        backgroundColor: 'rgba(33, 150, 243, 0.3)',
                        fill: '+1',
                        borderWidth: 1,
                        pointRadius: 0
                    },
                    {
                        label: 'Median (50th)',
                        data: agpData.p50,
                        borderColor: 'rgba(25, 118, 210, 1)',
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        pointRadius: 0
                    },
                    {
                        label: '25th percentile',
                        data: agpData.p25,
                        borderColor: 'rgba(33, 150, 243, 0.6)',
                        backgroundColor: 'rgba(33, 150, 243, 0.3)',
                        fill: '+1',
                        borderWidth: 1,
                        pointRadius: 0
                    },
                    {
                        label: '5th percentile',
                        data: agpData.p5,
                        borderColor: 'rgba(100, 181, 246, 0.3)',
                        backgroundColor: 'rgba(100, 181, 246, 0.1)',
                        fill: false,
                        borderWidth: 1,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '时间'
                        },
                        ticks: {
                            maxTicksLimit: 12
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '血糖 (mmol/L)'
                        },
                        min: 2,
                        max: 16,
                        ticks: {
                            stepSize: 2
                        }
                    }
                },
                annotation: {
                    annotations: {
                        targetRange: {
                            type: 'box',
                            yMin: 3.9,
                            yMax: 10.0,
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            borderColor: 'rgba(76, 175, 80, 0.5)',
                            borderWidth: 1
                        }
                    }
                }
            }
        });

        // Daily Charts
        const dailyData = """ + json.dumps(daily_data[:14]) + """;

        dailyData.forEach((day, index) => {
            const ctx = document.getElementById(`dailyChart${index}`).getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: day.timestamps,
                    datasets: [{
                        data: day.glucose_values,
                        borderColor: 'rgba(33, 150, 243, 1)',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    },
                    scales: {
                        x: { display: false },
                        y: {
                            display: false,
                            min: 2,
                            max: 16
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>
"""

        return html


def generate_enhanced_report(filepath: str, patient_id: str = None,
                            patient_info: Dict = None, medication_data: Dict = None,
                            output_path: str = None) -> str:
    """
    便捷函数：生成增强版CGM报告

    Args:
        filepath: 血糖数据CSV文件路径
        patient_id: 患者ID
        patient_info: 患者信息字典 (name, age, gender等)
        medication_data: 用药信息
        output_path: 输出HTML路径

    Returns:
        生成的HTML文件路径
    """
    generator = ZSHMCReportGeneratorEnhanced()
    return generator.generate_html_report(filepath, patient_id, patient_info,
                                         medication_data, output_path)


# 示例用法
if __name__ == "__main__":
    # 示例：生成报告
    example_patient_info = {
        "name": "张三",
        "age": 45,
        "gender": "男"
    }

    # 假设数据文件路径
    data_file = "cgm_data.csv"

    # 生成报告
    try:
        html_path = generate_enhanced_report(
            filepath=data_file,
            patient_id="P001",
            patient_info=example_patient_info,
            output_path="CGM_Report_Enhanced.html"
        )
        print(f"✅ 报告生成成功: {html_path}")
        print(f"💡 请在浏览器中打开此文件，然后使用 Cmd+P (Mac) 或 Ctrl+P (Windows) 打印为PDF")
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
