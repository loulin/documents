"""
胰腺癌患者血糖脆性可视化 - 优化版
作者: 医学AI团队
日期: 2025-10-07
特点:
- 更清晰的坐标轴标签
- 更详细的图例说明
- 增加数值标注
- 优化配色方案
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# 配色方案
COLORS = {
    '低脆性': '#2ecc71',  # 绿色
    '中脆性': '#f39c12',  # 橙色
    '高脆性': '#e74c3c',  # 红色
    '低': '#2ecc71',
    '中': '#f39c12',
    '高': '#e74c3c'
}


class OptimizedVisualizer:
    """优化版可视化工具"""

    def __init__(self, data_file):
        self.data_file = data_file
        self.df = pd.read_csv(data_file)
        self.output_dir = '可视化结果_优化版'

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def plot_brittleness_overview(self):
        """图1: 脆性类型总览 - 优化版"""
        fig = plt.figure(figsize=(16, 6))

        # 子图1: 术前脆性分布
        ax1 = plt.subplot(131)
        brittleness_counts = self.df['brittleness_type'].value_counts()
        colors = [COLORS[bt] for bt in brittleness_counts.index]

        wedges, texts, autotexts = ax1.pie(
            brittleness_counts.values,
            labels=None,  # 标签放在外面
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )

        # 添加图例，显示数量
        legend_labels = [f'{bt} ({count}例)'
                        for bt, count in brittleness_counts.items()]
        ax1.legend(legend_labels, loc='upper left', bbox_to_anchor=(0, 1))
        ax1.set_title('术前血糖脆性分型\n(n=100)', fontweight='bold', pad=20)

        # 子图2: 未来风险分布
        ax2 = plt.subplot(132)
        risk_counts = self.df['future_brittleness_risk_3m'].value_counts()
        colors = [COLORS[r] for r in risk_counts.index]

        wedges, texts, autotexts = ax2.pie(
            risk_counts.values,
            labels=None,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )

        legend_labels = [f'{r}风险 ({count}例)'
                        for r, count in risk_counts.items()]
        ax2.legend(legend_labels, loc='upper left', bbox_to_anchor=(0, 1))
        ax2.set_title('术后3个月脆性恶化风险\n(n=100)', fontweight='bold', pad=20)

        # 子图3: 脆性转移条形图
        ax3 = plt.subplot(133)
        transition = pd.crosstab(
            self.df['brittleness_type'],
            self.df['future_brittleness_risk_3m'],
            normalize='index'
        ) * 100

        # 确保顺序
        transition = transition.reindex(['低脆性', '中脆性', '高脆性'])
        transition = transition[['低', '中', '高']]

        x = np.arange(len(transition.index))
        width = 0.25

        for i, col in enumerate(transition.columns):
            values = transition[col].values
            bars = ax3.bar(x + i*width, values, width,
                          label=f'{col}风险', color=COLORS[col], alpha=0.8)

            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                if height > 5:  # 只显示大于5%的值
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.0f}%',
                            ha='center', va='bottom', fontsize=9)

        ax3.set_ylabel('患者比例 (%)', fontweight='bold')
        ax3.set_xlabel('术前脆性类型', fontweight='bold')
        ax3.set_title('术前脆性 → 术后风险转移', fontweight='bold', pad=20)
        ax3.set_xticks(x + width)
        ax3.set_xticklabels(transition.index)
        ax3.legend(loc='upper right')
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        ax3.set_ylim(0, 110)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/01_脆性分型总览.png',
                   dpi=300, bbox_inches='tight')
        print("✓ 已生成: 01_脆性分型总览.png")
        plt.close()

    def plot_glycemic_metrics_comparison(self):
        """图2: 血糖指标对比 - 优化版"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        metrics = [
            ('HbA1c (%)', 'preop_hba1c', 'postop_hba1c_3m',
             '糖化血红蛋白 (目标<7%)', 7.0),
            ('TIR (%)', 'preop_cgm_tir', 'postop_cgm_tir_3m',
             '目标范围内时间 (目标≥70%)', 70),
            ('CV (%)', 'preop_cgm_cv', 'postop_cgm_cv_3m',
             '血糖变异系数 (目标<36%)', 36),
            ('MAGE (mmol/L)', 'preop_cgm_mage', 'postop_cgm_mage_3m',
             '平均血糖漂移幅度 (目标<3.9)', 3.9)
        ]

        for idx, (metric_name, preop_col, postop_col, title, target) in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]

            # 准备数据
            positions = []
            data_to_plot = []
            labels = []
            colors_list = []

            for i, bt in enumerate(['低脆性', '中脆性', '高脆性']):
                subset = self.df[self.df['brittleness_type'] == bt]

                # 术前数据
                positions.append(i*3 + 0.5)
                data_to_plot.append(subset[preop_col].values)
                labels.append(f'{bt}\n术前')
                colors_list.append(COLORS[bt])

                # 术后数据
                positions.append(i*3 + 1.5)
                data_to_plot.append(subset[postop_col].values)
                labels.append(f'{bt}\n术后3月')
                colors_list.append(COLORS[bt])

            # 绘制箱线图
            bp = ax.boxplot(data_to_plot, positions=positions,
                           widths=0.6, patch_artist=True,
                           showmeans=True, meanline=True,
                           meanprops={'color': 'blue', 'linewidth': 2},
                           medianprops={'color': 'red', 'linewidth': 2},
                           boxprops={'alpha': 0.7},
                           flierprops={'marker': 'o', 'markersize': 4, 'alpha': 0.5})

            # 设置颜色
            for patch, color in zip(bp['boxes'], colors_list):
                patch.set_facecolor(color)

            # 添加参考线
            if target:
                ax.axhline(y=target, color='red', linestyle='--',
                          linewidth=2, alpha=0.6,
                          label=f'临床目标: {target}')

            # 添加均值标注
            for i, (pos, data) in enumerate(zip(positions, data_to_plot)):
                mean_val = np.mean(data)
                ax.text(pos, mean_val, f'{mean_val:.1f}',
                       ha='center', va='bottom', fontsize=8,
                       bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='yellow', alpha=0.3))

            # 设置标签和标题
            ax.set_xticks(positions)
            ax.set_xticklabels(labels, rotation=0, ha='center')
            ax.set_ylabel(metric_name, fontweight='bold', fontsize=12)
            ax.set_title(title, fontweight='bold', fontsize=13, pad=15)
            ax.grid(axis='y', alpha=0.3, linestyle='--')

            if target:
                ax.legend(loc='best', framealpha=0.9)

            # 添加说明
            textstr = '红线=中位数  蓝线=均值'
            ax.text(0.02, 0.98, textstr, transform=ax.transAxes,
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/02_血糖指标对比.png',
                   dpi=300, bbox_inches='tight')
        print("✓ 已生成: 02_血糖指标对比.png")
        plt.close()

    def plot_time_trajectories(self):
        """图3: 时间轨迹图 - 优化版"""
        fig, axes = plt.subplots(1, 2, figsize=(18, 7))

        # TIR轨迹
        ax1 = axes[0]
        time_points = ['术前', '术后\n72小时', '术后\n2周', '术后\n3个月']
        tir_cols = ['preop_cgm_tir', 'postop_cgm_tir_72h',
                    'postop_cgm_tir_2w', 'postop_cgm_tir_3m']

        for bt, color, marker in zip(['低脆性', '中脆性', '高脆性'],
                                     [COLORS['低脆性'], COLORS['中脆性'], COLORS['高脆性']],
                                     ['o', 's', '^']):
            subset = self.df[self.df['brittleness_type'] == bt]
            means = [subset[col].mean() for col in tir_cols]
            stds = [subset[col].std() for col in tir_cols]
            n = len(subset)

            # 绘制均值线
            line = ax1.plot(range(len(time_points)), means,
                          marker=marker, linewidth=3, markersize=10,
                          label=f'{bt} (n={n})', color=color)

            # 添加标准误差阴影
            ax1.fill_between(range(len(time_points)),
                            [m - s for m, s in zip(means, stds)],
                            [m + s for m, s in zip(means, stds)],
                            alpha=0.15, color=color)

            # 添加数值标注
            for i, (x, y) in enumerate(zip(range(len(time_points)), means)):
                ax1.text(x, y, f'{y:.1f}%',
                        ha='left' if i < 2 else 'right',
                        va='bottom', fontsize=9, color=color,
                        bbox=dict(boxstyle='round,pad=0.3',
                                 facecolor='white', alpha=0.7))

        # 参考线
        ax1.axhline(y=70, color='red', linestyle='--', linewidth=2,
                   alpha=0.6, label='临床目标 (70%)')
        ax1.axhline(y=50, color='orange', linestyle=':', linewidth=2,
                   alpha=0.5, label='警戒线 (50%)')

        ax1.set_xlabel('时间点', fontweight='bold', fontsize=13)
        ax1.set_ylabel('TIR - 目标范围内时间 (%)', fontweight='bold', fontsize=13)
        ax1.set_title('血糖目标范围内时间(TIR)变化轨迹\n3.9-10.0 mmol/L范围',
                     fontweight='bold', fontsize=14, pad=20)
        ax1.set_xticks(range(len(time_points)))
        ax1.set_xticklabels(time_points)
        ax1.legend(loc='best', framealpha=0.95, fontsize=10)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_ylim(20, 100)

        # CV轨迹
        ax2 = axes[1]
        cv_cols = ['preop_cgm_cv', 'postop_cgm_cv_72h',
                   'postop_cgm_cv_2w', 'postop_cgm_cv_3m']

        for bt, color, marker in zip(['低脆性', '中脆性', '高脆性'],
                                     [COLORS['低脆性'], COLORS['中脆性'], COLORS['高脆性']],
                                     ['o', 's', '^']):
            subset = self.df[self.df['brittleness_type'] == bt]
            means = [subset[col].mean() for col in cv_cols]
            stds = [subset[col].std() for col in cv_cols]
            n = len(subset)

            line = ax2.plot(range(len(time_points)), means,
                          marker=marker, linewidth=3, markersize=10,
                          label=f'{bt} (n={n})', color=color)

            ax2.fill_between(range(len(time_points)),
                            [m - s for m, s in zip(means, stds)],
                            [m + s for m, s in zip(means, stds)],
                            alpha=0.15, color=color)

            # 添加数值标注
            for i, (x, y) in enumerate(zip(range(len(time_points)), means)):
                ax2.text(x, y, f'{y:.1f}%',
                        ha='left' if i < 2 else 'right',
                        va='top', fontsize=9, color=color,
                        bbox=dict(boxstyle='round,pad=0.3',
                                 facecolor='white', alpha=0.7))

        # 参考线
        ax2.axhline(y=36, color='red', linestyle='--', linewidth=2,
                   alpha=0.6, label='稳定阈值 (36%)')
        ax2.axhline(y=45, color='orange', linestyle=':', linewidth=2,
                   alpha=0.5, label='高波动线 (45%)')

        ax2.set_xlabel('时间点', fontweight='bold', fontsize=13)
        ax2.set_ylabel('CV - 血糖变异系数 (%)', fontweight='bold', fontsize=13)
        ax2.set_title('血糖变异系数(CV)变化轨迹\nCV越低表示血糖越稳定',
                     fontweight='bold', fontsize=14, pad=20)
        ax2.set_xticks(range(len(time_points)))
        ax2.set_xticklabels(time_points)
        ax2.legend(loc='best', framealpha=0.95, fontsize=10)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_ylim(15, 65)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/03_时间轨迹图.png',
                   dpi=300, bbox_inches='tight')
        print("✓ 已生成: 03_时间轨迹图.png")
        plt.close()

    def plot_complication_impact(self):
        """图4: 并发症影响分析 - 优化版"""
        fig, axes = plt.subplots(1, 3, figsize=(20, 7))

        complications = [
            ('胰瘘等级', 'postop_pancreatic_fistula_grade',
             ['无', 'A', 'B', 'C'], '胰瘘'),
            ('迟发性胃排空', 'dge_occurrence',
             [0, 1], '胃排空延迟'),
            ('术后感染', 'postop_infection_type',
             ['无', '切口感染', '腹腔感染', '肺部感染'], '感染')
        ]

        for idx, (title, col, values, short_name) in enumerate(complications):
            ax = axes[idx]

            # 计算每种情况下的风险分布
            risk_data = []
            labels = []
            counts = []

            for val in values:
                if col == 'dge_occurrence':
                    subset = self.df[self.df[col] == val]
                    label = '无' if val == 0 else '有'
                else:
                    subset = self.df[self.df[col] == val]
                    label = val

                if len(subset) > 0:
                    risk_dist = subset['future_brittleness_risk_3m'].value_counts()
                    risk_dist = risk_dist.reindex(['低', '中', '高'], fill_value=0)
                    risk_pct = (risk_dist / len(subset) * 100).values

                    risk_data.append(risk_pct)
                    labels.append(f'{label}')
                    counts.append(len(subset))

            if risk_data:
                x = np.arange(len(labels))
                width = 0.25

                # 绘制堆叠柱状图
                low_bars = ax.bar(x, [d[0] for d in risk_data], width*3,
                                 label='低风险', color=COLORS['低'], alpha=0.8)
                mid_bars = ax.bar(x, [d[1] for d in risk_data], width*3,
                                 bottom=[d[0] for d in risk_data],
                                 label='中风险', color=COLORS['中'], alpha=0.8)
                high_bars = ax.bar(x, [d[2] for d in risk_data], width*3,
                                  bottom=[d[0]+d[1] for d in risk_data],
                                  label='高风险', color=COLORS['高'], alpha=0.8)

                # 添加百分比标注
                for i, (low, mid, high) in enumerate(risk_data):
                    # 低风险标注
                    if low > 8:
                        ax.text(i, low/2, f'{low:.0f}%',
                               ha='center', va='center', fontsize=10,
                               fontweight='bold', color='white')
                    # 中风险标注
                    if mid > 8:
                        ax.text(i, low + mid/2, f'{mid:.0f}%',
                               ha='center', va='center', fontsize=10,
                               fontweight='bold', color='white')
                    # 高风险标注
                    if high > 8:
                        ax.text(i, low + mid + high/2, f'{high:.0f}%',
                               ha='center', va='center', fontsize=10,
                               fontweight='bold', color='white')

                    # 顶部显示样本量
                    ax.text(i, 102, f'n={counts[i]}',
                           ha='center', va='bottom', fontsize=9,
                           fontweight='bold')

                ax.set_ylabel('脆性恶化风险分布 (%)', fontweight='bold', fontsize=12)
                ax.set_title(f'{short_name}对血糖脆性恶化的影响',
                           fontweight='bold', fontsize=13, pad=15)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, fontsize=11)
                ax.legend(loc='upper right', framealpha=0.95)
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                ax.set_ylim(0, 115)

                # 添加说明
                ax.text(0.5, -0.15, f'柱状图显示不同{short_name}情况下的风险分布',
                       transform=ax.transAxes, ha='center', fontsize=10,
                       style='italic', color='gray')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/04_并发症影响分析.png',
                   dpi=300, bbox_inches='tight')
        print("✓ 已生成: 04_并发症影响分析.png")
        plt.close()

    def plot_nutrition_psycho_factors(self):
        """图5: 营养和心理因素分析 - 新增"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))

        # 营养指标
        nutrition_metrics = [
            ('BMI (kg/m²)', 'bmi', '体质指数', (16, 28)),
            ('握力 (kg)', 'handgrip_strength', '肌肉力量', (10, 45)),
            ('NRS2002评分', 'nrs2002_score', '营养风险筛查', (0, 7))
        ]

        for idx, (ylabel, col, title, ylim) in enumerate(nutrition_metrics):
            ax = axes[0, idx]

            data_by_bt = []
            labels = []
            colors_list = []

            for bt in ['低脆性', '中脆性', '高脆性']:
                subset = self.df[self.df['brittleness_type'] == bt]
                data_by_bt.append(subset[col].values)
                labels.append(f'{bt}\n(n={len(subset)})')
                colors_list.append(COLORS[bt])

            bp = ax.boxplot(data_by_bt, labels=labels, patch_artist=True,
                           showmeans=True, meanline=True)

            for patch, color in zip(bp['boxes'], colors_list):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            # 添加均值标注
            for i, data in enumerate(data_by_bt):
                mean_val = np.mean(data)
                ax.text(i+1, mean_val, f'{mean_val:.1f}',
                       ha='center', va='bottom', fontsize=9,
                       bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='yellow', alpha=0.3))

            ax.set_ylabel(ylabel, fontweight='bold')
            ax.set_title(title, fontweight='bold', pad=10)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_ylim(ylim)

        # 心理因素
        psycho_metrics = [
            ('PHQ-9评分', 'phq9_score', '抑郁评分\n(≥10需关注)', (0, 27)),
            ('GAD-7评分', 'gad7_score', '焦虑评分\n(≥10需关注)', (0, 21)),
            ('IPAQ (MET-min/周)', 'ipaq_score', '体力活动水平', (0, 3500))
        ]

        for idx, (ylabel, col, title, ylim) in enumerate(psycho_metrics):
            ax = axes[1, idx]

            data_by_bt = []
            labels = []
            colors_list = []

            for bt in ['低脆性', '中脆性', '高脆性']:
                subset = self.df[self.df['brittleness_type'] == bt]
                data_by_bt.append(subset[col].values)
                labels.append(f'{bt}\n(n={len(subset)})')
                colors_list.append(COLORS[bt])

            bp = ax.boxplot(data_by_bt, labels=labels, patch_artist=True,
                           showmeans=True, meanline=True)

            for patch, color in zip(bp['boxes'], colors_list):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            # 添加参考线
            if 'PHQ-9' in ylabel:
                ax.axhline(y=10, color='red', linestyle='--', alpha=0.6,
                          label='中度抑郁线')
                ax.legend(loc='best', fontsize=9)
            elif 'GAD-7' in ylabel:
                ax.axhline(y=10, color='red', linestyle='--', alpha=0.6,
                          label='中度焦虑线')
                ax.legend(loc='best', fontsize=9)

            # 添加均值标注
            for i, data in enumerate(data_by_bt):
                mean_val = np.mean(data)
                if 'IPAQ' in ylabel:
                    ax.text(i+1, mean_val, f'{mean_val:.0f}',
                           ha='center', va='bottom', fontsize=9,
                           bbox=dict(boxstyle='round,pad=0.3',
                                    facecolor='yellow', alpha=0.3))
                else:
                    ax.text(i+1, mean_val, f'{mean_val:.1f}',
                           ha='center', va='bottom', fontsize=9,
                           bbox=dict(boxstyle='round,pad=0.3',
                                    facecolor='yellow', alpha=0.3))

            ax.set_ylabel(ylabel, fontweight='bold')
            ax.set_title(title, fontweight='bold', pad=10)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_ylim(ylim)

        plt.suptitle('营养和心理社会因素分析', fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/05_营养心理因素.png',
                   dpi=300, bbox_inches='tight')
        print("✓ 已生成: 05_营养心理因素.png")
        plt.close()

    def plot_correlation_heatmap(self):
        """图6: 相关性热图 - 优化版"""
        fig, ax = plt.subplots(figsize=(16, 14))

        # 选择关键指标
        key_metrics = [
            'preop_hba1c', 'preop_cgm_tir', 'preop_cgm_cv', 'preop_cgm_mage',
            'diabetes_duration_years', 'insulin_dose_preop',
            'bmi', 'phq9_score', 'gad7_score',
            'prealbumin', 'hs_crp', 'il6',
            'intraop_insulin_infusion_rate', 'intraop_glucose_range',
            'postop_cgm_tir_72h', 'postop_cgm_cv_72h',
            'postop_hba1c_3m', 'postop_cgm_tir_3m',
            'future_brittleness_risk_score'
        ]

        # 中文标签
        rename_dict = {
            'preop_hba1c': '术前HbA1c',
            'preop_cgm_tir': '术前TIR',
            'preop_cgm_cv': '术前CV',
            'preop_cgm_mage': '术前MAGE',
            'diabetes_duration_years': '糖尿病病程',
            'insulin_dose_preop': '术前胰岛素',
            'bmi': 'BMI',
            'phq9_score': '抑郁评分',
            'gad7_score': '焦虑评分',
            'prealbumin': '前白蛋白',
            'hs_crp': 'hs-CRP',
            'il6': 'IL-6',
            'intraop_insulin_infusion_rate': '术中胰岛素速率',
            'intraop_glucose_range': '术中血糖波动',
            'postop_cgm_tir_72h': '术后72h TIR',
            'postop_cgm_cv_72h': '术后72h CV',
            'postop_hba1c_3m': '术后3月HbA1c',
            'postop_cgm_tir_3m': '术后3月TIR',
            'future_brittleness_risk_score': '风险评分'
        }

        # 计算相关性
        corr_data = self.df[key_metrics].corr()
        corr_data = corr_data.rename(columns=rename_dict, index=rename_dict)

        # 绘制热图
        mask = np.triu(np.ones_like(corr_data, dtype=bool), k=1)
        sns.heatmap(corr_data, mask=mask, annot=True, fmt='.2f',
                   cmap='RdYlGn_r', center=0, vmin=-1, vmax=1,
                   square=False, linewidths=0.5, linecolor='white',
                   cbar_kws={'label': '相关系数\n(红色=正相关, 绿色=负相关)',
                            'shrink': 0.8},
                   annot_kws={'size': 8},
                   ax=ax)

        ax.set_title('关键血糖和临床指标相关性矩阵\n(仅显示下三角)',
                    fontweight='bold', fontsize=15, pad=20)

        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        # 添加说明
        textstr = '相关系数范围: -1(完全负相关) 到 +1(完全正相关)\n|r|>0.7: 强相关  |r|0.4-0.7: 中等相关  |r|<0.4: 弱相关'
        ax.text(0.5, -0.15, textstr, transform=ax.transAxes,
               ha='center', fontsize=10, style='italic',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/06_相关性热图.png',
                   dpi=300, bbox_inches='tight')
        print("✓ 已生成: 06_相关性热图.png")
        plt.close()

    def generate_all_visualizations(self):
        """生成所有优化版可视化"""
        print("\n" + "="*70)
        print("生成优化版可视化图表")
        print("="*70 + "\n")

        try:
            self.plot_brittleness_overview()
            self.plot_glycemic_metrics_comparison()
            self.plot_time_trajectories()
            self.plot_complication_impact()
            self.plot_nutrition_psycho_factors()
            self.plot_correlation_heatmap()

            print(f"\n✓ 所有图表已保存到 {self.output_dir}/ 目录")
            print("\n优化要点:")
            print("  ✓ 坐标轴标签更清晰，增加单位和说明")
            print("  ✓ 添加数值标注，便于理解")
            print("  ✓ 增加参考线和目标线")
            print("  ✓ 优化配色方案，更易区分")
            print("  ✓ 新增营养和心理因素分析图")

        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    print("="*70)
    print("胰腺癌患者血糖脆性可视化 - 优化版")
    print("="*70)
    print()

    # 使用完整版数据
    data_file = '虚拟患者数据_完整版.csv'

    if not os.path.exists(data_file):
        print(f"错误: 找不到数据文件 {data_file}")
        print("请先运行: python 01_模拟患者数据生成_完整版.py")
        return

    visualizer = OptimizedVisualizer(data_file)
    visualizer.generate_all_visualizations()

    print("\n" + "="*70)
    print("优化版可视化生成完成!")
    print("="*70)


if __name__ == "__main__":
    main()
