"""
胰腺癌患者血糖脆性可视化与报告生成脚本
作者: 医学AI团队
日期: 2025-10-07
用途: 生成可视化图表和临床报告
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
import json

warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 100
sns.set_style("whitegrid")


class GlycemicBrittlenessVisualizer:
    """血糖脆性可视化工具"""

    def __init__(self, data_file):
        self.data_file = data_file
        self.df = pd.read_csv(data_file)
        self.augment_features()
        self.output_dir = '可视化结果'

        # 创建输出目录
        import os
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)


    def augment_features(self):
        """根据最新数据字典补充衍生特征"""
        if self.df is None:
            return

        df = self.df

        if 'assessment_date' in df.columns:
            df['assessment_date'] = pd.to_datetime(df['assessment_date'], errors='coerce')

        for col in ['severe_hypo_last_event_date', 'acidotic_event_last_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        numeric_cols = [
            'severe_hypo_events_12m_count', 'severe_hypo_requires_assistance',
            'severe_hypo_awareness_score', 'dka_events_12m_count',
            'hhs_events_12m_count', 'acidotic_event_lowest_ph',
            'caregiver_primary_relationship', 'caregiver_lives_with_patient',
            'caregiver_daily_support_hours', 'family_support_responsiveness_score',
            'tumor_T_stage', 'tumor_N_stage', 'tumor_M_stage', 'tumor_ajcc_stage',
            'arterial_invasion_grade', 'venous_invasion_grade', 'perineural_invasion_status',
            'postop_infection_onset_day', 'postop_infection_clavien_grade',
            'postop_pancreatic_fistula_grade', 'postop_pancreatic_fistula_drain_days',
            'postop_pain_nrs_day1', 'postop_analgesia_mode', 'postop_opioid_meq_day1',
            'rehospitalization_cause_category', 'complication_primary_type',
            'complication_onset_postop_day', 'complication_clavien_grade',
            'endocrine_function_recovery_day', 'exocrine_function_recovery_day'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        def parse_multi(value):
            if value is None:
                return []
            if isinstance(value, float) and pd.isna(value):
                return []
            if isinstance(value, (list, tuple)):
                return [str(v).strip() for v in value if str(v).strip() and str(v).strip().lower() not in ('无', 'none')]
            if isinstance(value, str):
                raw = value.strip()
                if raw == '' or raw.lower() in ('无', 'none', 'nan'):
                    return []
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, str):
                        return parse_multi([parsed])
                    if isinstance(parsed, (list, tuple)):
                        return [str(v).strip() for v in parsed if str(v).strip()]
                except json.JSONDecodeError:
                    pass
                separators = ';' if ';' in raw else ',' if ',' in raw else None
                if separators:
                    return [p.strip() for p in raw.split(separators) if p.strip() and p.strip().lower() not in ('无', 'none')]
                return [raw]
            return [str(value)]

        multi_cols = {
            'adjacent_organ_involvement': 'adjacent_organ_involvement_count',
            'postop_infection_site': 'postop_infection_site_count',
            'postop_pancreatic_fistula_intervention': 'postop_pancreatic_fistula_intervention_count',
            'pancreatic_function_followup_method': 'pancreatic_function_followup_method_count'
        }
        for col, count_col in multi_cols.items():
            if col in df.columns:
                df[count_col] = df[col].apply(lambda x: len(parse_multi(x)))

        assist_map = {0: 0, 1: 1, 2: 2}
        if 'severe_hypo_requires_assistance' in df.columns:
            df['severe_hypo_assist_score'] = df['severe_hypo_requires_assistance'].map(assist_map).fillna(0)
        else:
            df['severe_hypo_assist_score'] = 0

        if 'severe_hypo_awareness_score' in df.columns:
            df['severe_hypo_awareness_score'] = df['severe_hypo_awareness_score'].fillna(7)
        else:
            df['severe_hypo_awareness_score'] = 7

        if 'severe_hypo_last_event_date' in df.columns and 'assessment_date' in df.columns:
            df['severe_hypo_days_since_last'] = (df['assessment_date'] - df['severe_hypo_last_event_date']).dt.days
            df['severe_hypo_days_since_last'] = df['severe_hypo_days_since_last'].where(df['severe_hypo_days_since_last'] >= 0)
        else:
            df['severe_hypo_days_since_last'] = np.nan

        def recency_points(days):
            if pd.isna(days):
                return 0
            if days <= 30:
                return 3
            if days <= 180:
                return 2
            if days <= 365:
                return 1
            return 0

        df['severe_hypo_recency_points'] = df['severe_hypo_days_since_last'].apply(recency_points)
        df['severe_hypo_events_12m_count'] = df.get('severe_hypo_events_12m_count', pd.Series(0, index=df.index)).fillna(0)
        df['severe_hypo_burden_score'] = (
            df['severe_hypo_events_12m_count'] * 2
            + df['severe_hypo_assist_score']
            + (7 - df['severe_hypo_awareness_score']).clip(lower=0)
            + df['severe_hypo_recency_points']
        ).fillna(0)

        if 'acidotic_event_last_date' in df.columns and 'assessment_date' in df.columns:
            df['acidotic_days_since_last'] = (df['assessment_date'] - df['acidotic_event_last_date']).dt.days
            df['acidotic_days_since_last'] = df['acidotic_days_since_last'].where(df['acidotic_days_since_last'] >= 0)
        else:
            df['acidotic_days_since_last'] = np.nan

        df['acidotic_recency_points'] = df['acidotic_days_since_last'].apply(recency_points)
        df['acidotic_ph_penalty'] = (7.30 - df.get('acidotic_event_lowest_ph', pd.Series(7.30, index=df.index))).clip(lower=0) * 10
        df['dka_events_12m_count'] = df.get('dka_events_12m_count', pd.Series(0, index=df.index)).fillna(0)
        df['hhs_events_12m_count'] = df.get('hhs_events_12m_count', pd.Series(0, index=df.index)).fillna(0)
        df['dka_hhs_burden_score'] = (
            df['dka_events_12m_count'] * 2
            + df['hhs_events_12m_count'] * 2
            + df['acidotic_recency_points'].fillna(0)
            + df['acidotic_ph_penalty'].fillna(0)
        )

        relationship_map = {1: 3, 2: 2.5, 3: 2, 4: 1.5, 5: 1, 6: 0}
        responsiveness_map = {1: 3, 2: 2, 3: 1}
        df['family_support_score'] = (
            df.get('caregiver_primary_relationship', pd.Series(np.nan, index=df.index)).map(relationship_map).fillna(1.5)
            + df.get('caregiver_lives_with_patient', pd.Series(np.nan, index=df.index)).map({1: 2, 0: 0}).fillna(0)
            + (df.get('caregiver_daily_support_hours', pd.Series(0, index=df.index)).fillna(0) / 2).clip(upper=5)
            + df.get('family_support_responsiveness_score', pd.Series(np.nan, index=df.index)).map(responsiveness_map).fillna(2)
        )

        df['vascular_invasion_score'] = (
            df.get('arterial_invasion_grade', pd.Series(0, index=df.index)).fillna(0) * 2
            + df.get('venous_invasion_grade', pd.Series(0, index=df.index)).fillna(0) * 1.5
            + df.get('perineural_invasion_status', pd.Series(0, index=df.index)).fillna(0)
        )
        df['tumor_invasion_burden'] = df['vascular_invasion_score'] + df.get('adjacent_organ_involvement_count', pd.Series(0, index=df.index)).fillna(0)

        infection_grade = df.get('postop_infection_clavien_grade', pd.Series(0, index=df.index)).fillna(0)
        infection_onset = df.get('postop_infection_onset_day', pd.Series(np.nan, index=df.index))
        infection_site_count = df.get('postop_infection_site_count', pd.Series(0, index=df.index)).fillna(0)
        df['postop_infection_severity_score'] = (
            infection_grade * 2
            + infection_site_count
            + infection_onset.apply(lambda x: 3 if pd.notna(x) and x <= 3 else 1 if pd.notna(x) and x <= 7 else 0)
        )
        df['postop_infection_flag'] = (df['postop_infection_severity_score'] > 0).astype(int)

        fistula_grade = df.get('postop_pancreatic_fistula_grade', pd.Series(0, index=df.index)).fillna(0)
        fistula_drain = df.get('postop_pancreatic_fistula_drain_days', pd.Series(0, index=df.index)).fillna(0)
        fistula_intervention = df.get('postop_pancreatic_fistula_intervention_count', pd.Series(0, index=df.index)).fillna(0)
        df['postop_pancreatic_fistula_score'] = fistula_grade * 3 + fistula_drain / 5 + fistula_intervention
        df['severe_pancreatic_fistula_flag'] = (fistula_grade >= 2).astype(int)

        analgesia_map = {1: 2, 2: 3, 3: 3, 4: 1, 5: 1}
        df['postop_pain_control_score'] = (
            (10 - df.get('postop_pain_nrs_day1', pd.Series(5, index=df.index)).fillna(5)).clip(lower=0)
            + df.get('postop_analgesia_mode', pd.Series(0, index=df.index)).map(analgesia_map).fillna(0)
            - (df.get('postop_opioid_meq_day1', pd.Series(0, index=df.index)).fillna(0) / 10)
        )

        df['pancreatic_recovery_delay_score'] = (
            df.get('endocrine_function_recovery_day', pd.Series(0, index=df.index)).fillna(0) / 7
            + df.get('exocrine_function_recovery_day', pd.Series(0, index=df.index)).fillna(0) / 7
        )

        for col in ['postop_infection_site_count', 'postop_pancreatic_fistula_intervention_count', 'pancreatic_function_followup_method_count', 'adjacent_organ_involvement_count']:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        df['complication_severity_score'] = (
            df.get('complication_clavien_grade', pd.Series(0, index=df.index)).fillna(0)
            + df.get('complication_onset_postop_day', pd.Series(0, index=df.index)).fillna(0) / 7
        )

        self.df = df


    def plot_brittleness_distribution(self):
        """绘制脆性类型分布"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 脆性类型分布
        brittleness_counts = self.df['brittleness_type'].value_counts()
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        axes[0].pie(brittleness_counts.values, labels=brittleness_counts.index,
                    autopct='%1.1f%%', colors=colors, startangle=90)
        axes[0].set_title('术前血糖脆性类型分布', fontsize=14, fontweight='bold')

        # 未来风险分布
        risk_counts = self.df['future_brittleness_risk_3m'].value_counts()
        axes[1].pie(risk_counts.values, labels=risk_counts.index,
                    autopct='%1.1f%%', colors=colors, startangle=90)
        axes[1].set_title('术后3个月脆性恶化风险分布', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/01_脆性分布.png', bbox_inches='tight')
        print("✓ 已生成: 01_脆性分布.png")
        plt.close()

    def plot_preop_postop_comparison(self):
        """绘制术前术后指标对比"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        metrics = [
            ('HbA1c (%)', 'preop_hba1c', 'postop_hba1c_3m'),
            ('TIR (%)', 'preop_cgm_tir', 'postop_cgm_tir_3m'),
            ('CV (%)', 'preop_cgm_cv', 'postop_cgm_cv_3m'),
            ('MAGE (mmol/L)', 'preop_cgm_mage', 'postop_cgm_mage_3m')
        ]

        for idx, (metric_name, preop_col, postop_col) in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]

            # 按脆性类型分组
            data_to_plot = []
            labels = []
            colors_list = []

            for bt, color in zip(['低脆性', '中脆性', '高脆性'],
                                ['#2ecc71', '#f39c12', '#e74c3c']):
                subset = self.df[self.df['brittleness_type'] == bt]
                data_to_plot.append(subset[preop_col].values)
                data_to_plot.append(subset[postop_col].values)
                labels.extend([f'{bt}\n术前', f'{bt}\n术后'])
                colors_list.extend([color, color])

            bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                           showmeans=True, meanline=True)

            for patch, color in zip(bp['boxes'], colors_list):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)

            ax.set_title(metric_name, fontsize=12, fontweight='bold')
            ax.set_ylabel('数值', fontsize=10)
            ax.grid(axis='y', alpha=0.3)

            # 添加参考线
            if 'TIR' in metric_name:
                ax.axhline(y=70, color='red', linestyle='--', alpha=0.5,
                          label='目标线(70%)')
                ax.legend()

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/02_术前术后对比.png', bbox_inches='tight')
        print("✓ 已生成: 02_术前术后对比.png")
        plt.close()

    def plot_time_trajectory(self):
        """绘制血糖脆性时间轨迹"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # TIR轨迹
        time_points = ['术前', '术后72h', '术后2周', '术后3月']
        tir_cols = ['preop_cgm_tir', 'postop_cgm_tir_72h',
                    'postop_cgm_tir_2w', 'postop_cgm_tir_3m']

        for bt, color, marker in zip(['低脆性', '中脆性', '高脆性'],
                                     ['#2ecc71', '#f39c12', '#e74c3c'],
                                     ['o', 's', '^']):
            subset = self.df[self.df['brittleness_type'] == bt]
            means = [subset[col].mean() for col in tir_cols]
            stds = [subset[col].std() for col in tir_cols]

            axes[0].plot(time_points, means, marker=marker, linewidth=2,
                        label=bt, color=color, markersize=8)
            axes[0].fill_between(range(len(time_points)),
                                [m - s for m, s in zip(means, stds)],
                                [m + s for m, s in zip(means, stds)],
                                alpha=0.2, color=color)

        axes[0].axhline(y=70, color='red', linestyle='--', alpha=0.5, label='目标(70%)')
        axes[0].set_xlabel('时间点', fontsize=12)
        axes[0].set_ylabel('TIR (%)', fontsize=12)
        axes[0].set_title('TIR时间轨迹', fontsize=14, fontweight='bold')
        axes[0].legend(loc='best')
        axes[0].grid(True, alpha=0.3)

        # CV轨迹
        cv_cols = ['preop_cgm_cv', 'postop_cgm_cv_72h',
                   'postop_cgm_cv_2w', 'postop_cgm_cv_3m']

        for bt, color, marker in zip(['低脆性', '中脆性', '高脆性'],
                                     ['#2ecc71', '#f39c12', '#e74c3c'],
                                     ['o', 's', '^']):
            subset = self.df[self.df['brittleness_type'] == bt]
            means = [subset[col].mean() for col in cv_cols]
            stds = [subset[col].std() for col in cv_cols]

            axes[1].plot(time_points, means, marker=marker, linewidth=2,
                        label=bt, color=color, markersize=8)
            axes[1].fill_between(range(len(time_points)),
                                [m - s for m, s in zip(means, stds)],
                                [m + s for m, s in zip(means, stds)],
                                alpha=0.2, color=color)

        axes[1].axhline(y=36, color='red', linestyle='--', alpha=0.5, label='阈值(36%)')
        axes[1].set_xlabel('时间点', fontsize=12)
        axes[1].set_ylabel('CV (%)', fontsize=12)
        axes[1].set_title('CV时间轨迹', fontsize=14, fontweight='bold')
        axes[1].legend(loc='best')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/03_时间轨迹.png', bbox_inches='tight')
        print("✓ 已生成: 03_时间轨迹.png")
        plt.close()

    def plot_risk_transition_matrix(self):
        """绘制风险转移矩阵"""
        fig, ax = plt.subplots(figsize=(10, 8))

        # 创建转移矩阵
        transition = pd.crosstab(
            self.df['brittleness_type'],
            self.df['future_brittleness_risk_3m'],
            normalize='index'
        ) * 100

        # 确保顺序
        order = ['低脆性', '中脆性', '高脆性']
        transition = transition.reindex(order)
        transition = transition[['低', '中', '高']]

        # 绘制热力图
        sns.heatmap(transition, annot=True, fmt='.1f', cmap='RdYlGn_r',
                   center=50, vmin=0, vmax=100, cbar_kws={'label': '百分比(%)'},
                   linewidths=2, linecolor='white', ax=ax)

        ax.set_xlabel('术后3个月风险等级', fontsize=12, fontweight='bold')
        ax.set_ylabel('术前脆性类型', fontsize=12, fontweight='bold')
        ax.set_title('术前脆性类型 → 术后风险等级转移矩阵',
                    fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/04_风险转移矩阵.png', bbox_inches='tight')
        print("✓ 已生成: 04_风险转移矩阵.png")
        plt.close()

    def plot_complication_impact(self):
        """绘制并发症对风险的影响"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        complications = [
            ('胰瘘分级(ISGPS)', 'postop_pancreatic_fistula_grade', [0, 1, 2, 3]),
            ('迟发性胃排空', 'dge_occurrence', [0, 1]),
            ('术后感染Clavien分级', 'postop_infection_clavien_grade', [0, 1, 2, 3, 4])
        ]
        label_maps = {
            'postop_pancreatic_fistula_grade': {0: '无', 1: 'Biochemical leak', 2: 'Grade B', 3: 'Grade C'},
            'postop_infection_clavien_grade': {0: '无', 1: 'I', 2: 'II', 3: 'IIIa', 4: 'IIIb', 5: 'IVa', 6: 'IVb', 7: 'V'}
        }

        for idx, (title, col, values) in enumerate(complications):
            ax = axes[idx]

            if col not in self.df.columns:
                ax.axis('off')
                ax.set_title(f'{title}\n(数据缺失)', fontsize=12)
                continue

            risk_data = []
            labels = []
            series = self.df[col]

            for val in values:
                if col == 'dge_occurrence':
                    subset = self.df[series == val]
                    label = '无' if val == 0 else '有'
                else:
                    subset = self.df[series == val]
                    label = label_maps.get(col, {}).get(val, str(val))

                if len(subset) > 0:
                    risk_dist = subset['future_brittleness_risk_3m'].value_counts()
                    risk_dist = risk_dist.reindex(['低', '中', '高'], fill_value=0)
                    risk_pct = (risk_dist / len(subset) * 100).values
                    risk_data.append(risk_pct)
                    labels.append(f'{label}\n(n={len(subset)})')

            if risk_data:
                x = np.arange(len(labels))
                width = 0.25

                ax.bar(x - width, [d[0] for d in risk_data], width,
                      label='低风险', color='#2ecc71')
                ax.bar(x, [d[1] for d in risk_data], width,
                      label='中风险', color='#f39c12')
                ax.bar(x + width, [d[2] for d in risk_data], width,
                      label='高风险', color='#e74c3c')

                ax.set_ylabel('患者比例 (%)', fontsize=11)
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(labels, fontsize=10)
                ax.legend(loc='upper right')
                ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/05_并发症影响.png', bbox_inches='tight')
        print("✓ 已生成: 05_并发症影响.png")
        plt.close()

    def plot_correlation_heatmap(self):
        """绘制关键指标相关性热图"""
        fig, ax = plt.subplots(figsize=(14, 12))

        # 选择关键数值指标
        key_metrics = [
            'preop_hba1c', 'preop_cgm_tir', 'preop_cgm_cv', 'preop_cgm_mage',
            'diabetes_duration_years', 'insulin_dose_preop',
            'intraop_insulin_infusion_rate', 'intraop_glucose_range',
            'postop_cgm_tir_72h', 'postop_cgm_cv_72h',
            'postop_hba1c_3m', 'postop_cgm_tir_3m',
            'future_brittleness_risk_score'
        ]

        # 重命名为中文
        rename_dict = {
            'preop_hba1c': '术前HbA1c',
            'preop_cgm_tir': '术前TIR',
            'preop_cgm_cv': '术前CV',
            'preop_cgm_mage': '术前MAGE',
            'diabetes_duration_years': '糖尿病病程',
            'insulin_dose_preop': '术前胰岛素剂量',
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
        sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, vmin=-1, vmax=1, square=True,
                   linewidths=1, linecolor='white', ax=ax,
                   cbar_kws={'label': '相关系数'})

        ax.set_title('关键血糖指标相关性热图', fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/06_相关性热图.png', bbox_inches='tight')
        print("✓ 已生成: 06_相关性热图.png")
        plt.close()

    def generate_patient_report(self, patient_id):
        """生成单个患者的详细报告"""
        patient = self.df[self.df['patient_id'] == patient_id]

        if len(patient) == 0:
            print(f"错误: 未找到患者 {patient_id}")
            return



        patient = patient.iloc[0]

        fistula_grade_map = {0: '无', 1: 'Biochemical leak', 2: 'Grade B', 3: 'Grade C'}
        infection_grade_map = {0: '无', 1: 'I', 2: 'II', 3: 'IIIa', 4: 'IIIb', 5: 'IVa', 6: 'IVb', 7: 'V'}

        def map_grade(value, mapping, default='未知'):
            if pd.isna(value):
                return default
            try:
                return mapping.get(int(value), default)
            except (ValueError, TypeError):
                return default

        fistula_grade_text = map_grade(patient.get('postop_pancreatic_fistula_grade', np.nan), fistula_grade_map, '未知')
        infection_grade_text = map_grade(patient.get('postop_infection_clavien_grade', np.nan), infection_grade_map, '无')
        infection_site_raw = patient.get('postop_infection_site', '')
        if pd.isna(infection_site_raw):
            infection_site_raw = ''
        infection_site_raw = str(infection_site_raw).strip()
        if infection_grade_text == '无' and infection_site_raw in ('', '无'):
            infection_display = '无'
        else:
            infection_display = infection_grade_text
            if infection_site_raw not in ('', '无'):
                infection_display += f" - {infection_site_raw}"

        # 创建报告
        report = f"""
{'='*60}
胰腺癌患者血糖脆性评估报告
{'='*60}

患者ID: {patient['patient_id']}
评估日期: {patient['assessment_date']}
评估医生: {patient['assessor_name']}

{'='*60}
1. 基本信息与脆性分型
{'='*60}
年龄: {patient['age']}岁
性别: {patient['gender']}
糖尿病类型: {'1型' if patient['diabetes_type_detailed'] == 1 else '2型'}
糖尿病病程: {patient['diabetes_duration_years']}年
术前脆性分型: {patient['brittleness_type']}

{'='*60}
2. 术前血糖控制指标
{'='*60}
HbA1c: {patient['preop_hba1c']:.1f}% {'(目标<7%)' if patient['preop_hba1c'] < 7 else '(超标)'}
CGM指标:
  - TIR (3.9-10.0 mmol/L): {patient['preop_cgm_tir']:.1f}% {'(良好)' if patient['preop_cgm_tir'] >= 70 else '(需改善)'}
  - CV: {patient['preop_cgm_cv']:.1f}% {'(稳定)' if patient['preop_cgm_cv'] < 36 else '(不稳定)'}
  - MAGE: {patient['preop_cgm_mage']:.2f} mmol/L
  - GMI: {patient['preop_cgm_gmi']:.1f}%

{'='*60}
3. 手术与围术期管理
{'='*60}
手术类型: {patient['surgery_type']}
术中胰岛素用量: {patient['intraop_insulin_infusion_rate']:.2f} U/h
术中血糖波动: {patient['intraop_glucose_range']:.2f} mmol/L
术中低血糖事件: {patient['intraop_hypo_episodes']}次
术中并发症: {patient['intraop_complications']}

{'='*60}
4. 术后恢复情况
{'='*60}
胰瘘: {fistula_grade_text}
迟发性胃排空: {'是' if patient['dge_occurrence'] == 1 else '否'}
术后感染: {infection_display}

术后72小时血糖控制:
  - TIR: {patient['postop_cgm_tir_72h']:.1f}%
  - CV: {patient['postop_cgm_cv_72h']:.1f}%

术后3个月血糖控制:
  - HbA1c: {patient['postop_hba1c_3m']:.1f}%
  - TIR: {patient['postop_cgm_tir_3m']:.1f}%
  - CV: {patient['postop_cgm_cv_3m']:.1f}%
  - MAGE: {patient['postop_cgm_mage_3m']:.2f} mmol/L

{'='*60}
5. 风险评估与预测
{'='*60}
未来3个月脆性恶化风险: {patient['future_brittleness_risk_3m']}
风险评分: {patient['future_brittleness_risk_score']:.3f}

{'='*60}
6. 临床建议
{'='*60}
"""

        # 根据风险等级给出建议
        if patient['future_brittleness_risk_3m'] == '高':
            report += """
⚠️  高风险患者管理建议:
  1. 强化血糖监测: 建议持续CGM监测至少3个月
  2. 个体化治疗方案: 及时调整胰岛素治疗方案
  3. 营养支持: 评估胰腺外分泌功能,适当补充胰酶
  4. 密切随访: 每2周门诊随访一次
  5. 多学科协作: 内分泌、营养、外科联合管理
"""
        elif patient['future_brittleness_risk_3m'] == '中':
            report += """
⚡ 中等风险患者管理建议:
  1. 定期监测: CGM监测至少1个月,后续根据情况调整
  2. 优化治疗: 根据血糖变化及时调整用药
  3. 生活方式: 规律饮食和运动
  4. 定期随访: 每月门诊随访一次
"""
        else:
            report += """
✓ 低风险患者管理建议:
  1. 继续保持良好的血糖控制
  2. 定期监测HbA1c (每3个月)
  3. 维持健康生活方式
  4. 按时随访
"""

        report += "\n" + "="*60 + "\n"

        # 保存报告
        report_file = f'{self.output_dir}/患者报告_{patient_id}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✓ 已生成患者报告: {report_file}")
        return report

    def generate_all_visualizations(self):
        """生成所有可视化图表"""
        print("\n" + "="*60)
        print("生成可视化图表")
        print("="*60 + "\n")

        self.plot_brittleness_distribution()
        self.plot_preop_postop_comparison()
        self.plot_time_trajectory()
        self.plot_risk_transition_matrix()
        self.plot_complication_impact()
        self.plot_correlation_heatmap()

        print(f"\n✓ 所有图表已保存到 {self.output_dir}/ 目录")


def main():
    """主函数"""
    print("="*60)
    print("胰腺癌患者血糖脆性可视化与报告生成工具")
    print("="*60)
    print()

    # 初始化
    data_file = '虚拟患者数据_术前术中术后.csv'
    visualizer = GlycemicBrittlenessVisualizer(data_file)

    # 生成所有可视化
    visualizer.generate_all_visualizations()

    # 生成示例患者报告
    print("\n" + "="*60)
    print("生成示例患者报告")
    print("="*60)
    sample_patients = visualizer.df['patient_id'].head(3).tolist()
    for pid in sample_patients:
        visualizer.generate_patient_report(pid)

    print("\n" + "="*60)
    print("可视化与报告生成完成!")
    print("="*60)


if __name__ == "__main__":
    main()
