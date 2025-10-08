"""
胰腺癌患者血糖脆性分析脚本
作者: 医学AI团队
日期: 2025-10-07
用途: 对患者数据进行血糖脆性分型、预测建模和特征重要性分析
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import json

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class GlycemicBrittlenessAnalyzer:
    """血糖脆性分析器"""

    def __init__(self, data_file):
        """初始化分析器"""
        self.data_file = data_file
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}

    def load_data(self):
        """加载数据"""
        print("加载数据...")
        self.df = pd.read_csv(self.data_file)
        self.augment_features()
        print(f"✓ 已加载 {len(self.df)} 例患者数据")
        print(f"  列数: {len(self.df.columns)}")
        return self.df


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

    def exploratory_analysis(self):
        """探索性数据分析"""
        print("\n" + "=" * 60)
        print("探索性数据分析")
        print("=" * 60)

        # 基本统计
        print("\n1. 基本信息:")
        print(f"   患者总数: {len(self.df)}")
        print(f"   特征数量: {len(self.df.columns)}")
        print(f"   缺失值总数: {self.df.isnull().sum().sum()}")

        # 脆性类型分布
        print("\n2. 脆性类型分布:")
        for bt, count in self.df['brittleness_type'].value_counts().items():
            print(f"   {bt}: {count} 例 ({count/len(self.df)*100:.1f}%)")

        # 术前术后血糖指标对比
        print("\n3. 术前/术后血糖指标对比:")
        metrics = {
            'HbA1c': ('preop_hba1c', 'postop_hba1c_3m'),
            'TIR': ('preop_cgm_tir', 'postop_cgm_tir_3m'),
            'CV': ('preop_cgm_cv', 'postop_cgm_cv_3m'),
            'MAGE': ('preop_cgm_mage', 'postop_cgm_mage_3m')
        }

        for metric_name, (preop_col, postop_col) in metrics.items():
            preop_mean = self.df[preop_col].mean()
            postop_mean = self.df[postop_col].mean()
            change = ((postop_mean - preop_mean) / preop_mean) * 100
            print(f"   {metric_name}:")
            print(f"     术前: {preop_mean:.2f}")
            print(f"     术后3月: {postop_mean:.2f}")
            print(f"     变化: {change:+.1f}%")

        # 按脆性分型分析术后风险
        print("\n4. 不同脆性类型的术后恶化风险:")
        risk_by_type = pd.crosstab(
            self.df['brittleness_type'],
            self.df['future_brittleness_risk_3m'],
            normalize='index'
        ) * 100
        print(risk_by_type.round(1))

        # 并发症与风险的关系
        print("\n5. 术后并发症对风险的影响:")
        complications = {}
        if 'severe_pancreatic_fistula_flag' in self.df.columns:
            complications['胰瘘'] = self.df['severe_pancreatic_fistula_flag'] > 0
        if 'dge_occurrence' in self.df.columns:
            complications['迟发性胃排空'] = self.df['dge_occurrence'] == 1
        if 'postop_infection_flag' in self.df.columns:
            complications['术后感染'] = self.df['postop_infection_flag'] > 0

        for comp_name, mask in complications.items():
            mask = mask.fillna(False).astype(bool)
            if mask.sum() > 0:
                high_risk_pct = (
                    self.df.loc[mask, 'future_brittleness_risk_3m'] == '高'
                ).sum() / mask.sum() * 100
                print(f"   {comp_name}: {high_risk_pct:.1f}% 的患者发展为高风险")

    def prepare_features_for_modeling(self, task='classification'):
        """准备建模特征"""
        print("\n准备建模特征...")

        # 选择特征列（排除标识符和目标变量）
        exclude_cols = [
            'patient_id', 'assessment_date', 'assessor_name',
            'brittleness_type', 'future_brittleness_risk_3m',
            'future_brittleness_risk_score',
            'severe_hypo_last_event_date', 'acidotic_event_last_date',
            'postop_hba1c_3m', 'postop_hba1c_6m', 'postop_hba1c_1y',
            'postop_cgm_cv_3m', 'postop_cgm_tir_3m', 'postop_cgm_tar_level1_3m',
            'postop_cgm_tar_level2_3m', 'postop_cgm_tbr_level1_3m',
            'postop_cgm_tbr_level2_3m', 'postop_cgm_mage_3m', 'postop_cgm_gmi_3m',
            'postop_fecal_elastase1_3m', 'adjacent_organ_involvement',
            'postop_infection_site', 'postop_pancreatic_fistula_intervention',
            'rehospitalization_cause_detail', 'postop_infection_culture_result'
        ]

        # 数值型特征
        numeric_features = self.df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_features = [col for col in numeric_features if col not in exclude_cols]

        # 分类特征（简化处理）
        categorical_features = [
            'tumor_type_detailed', 'surgery_type', 'anesthesia_type',
            'intraop_complications'
        ]

        # 创建特征矩阵
        X = pd.DataFrame()

        # 添加数值特征
        for col in numeric_features:
            if col in self.df.columns:
                X[col] = self.df[col].fillna(self.df[col].median())

        # 编码分类特征
        le = LabelEncoder()
        for col in categorical_features:
            if col in self.df.columns:
                X[f'{col}_encoded'] = le.fit_transform(
                    self.df[col].fillna('未知').astype(str)
                )

        # 目标变量
        if task == 'classification':
            y = self.df['future_brittleness_risk_3m'].copy()
        else:
            y = self.df['future_brittleness_risk_score'].copy()

        print(f"✓ 特征准备完成")
        print(f"  特征数: {X.shape[1]}")
        print(f"  样本数: {X.shape[0]}")
        print(f"  目标变量: {y.name}")

        return X, y

    def build_classification_model(self):
        """构建分类模型（预测风险等级）"""
        print("\n" + "=" * 60)
        print("构建血糖脆性风险分类模型")
        print("=" * 60)

        # 准备数据
        X, y = self.prepare_features_for_modeling(task='classification')

        # 划分训练集和测试集
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\n训练集: {len(self.X_train)} 例")
        print(f"测试集: {len(self.X_test)} 例")

        # 特征标准化
        scaler = StandardScaler()
        self.X_train_scaled = scaler.fit_transform(self.X_train)
        self.X_test_scaled = scaler.transform(self.X_test)

        # 训练多个模型
        print("\n训练模型...")

        # 1. Random Forest
        print("  - Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        )
        rf_model.fit(self.X_train, self.y_train)
        self.models['RandomForest'] = rf_model

        # 2. Gradient Boosting
        print("  - Gradient Boosting...")
        gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        gb_model.fit(self.X_train, self.y_train)
        self.models['GradientBoosting'] = gb_model

        print("✓ 模型训练完成")

        return self.models

    def evaluate_models(self):
        """评估模型性能"""
        print("\n" + "=" * 60)
        print("模型性能评估")
        print("=" * 60)

        for model_name, model in self.models.items():
            print(f"\n{model_name} 模型:")
            print("-" * 40)

            # 预测
            y_pred = model.predict(self.X_test)
            y_pred_proba = model.predict_proba(self.X_test)

            # 准确率
            accuracy = (y_pred == self.y_test).sum() / len(self.y_test)
            print(f"准确率: {accuracy:.3f}")

            # 交叉验证
            cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5)
            print(f"交叉验证准确率: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

            # 分类报告
            print("\n分类报告:")
            print(classification_report(self.y_test, y_pred, zero_division=0))

            # 混淆矩阵
            print("混淆矩阵:")
            cm = confusion_matrix(self.y_test, y_pred)
            print(cm)

            # 保存结果
            self.results[model_name] = {
                'accuracy': accuracy,
                'cv_scores': cv_scores,
                'y_pred': y_pred,
                'y_pred_proba': y_pred_proba,
                'confusion_matrix': cm
            }

    def analyze_feature_importance(self):
        """分析特征重要性"""
        print("\n" + "=" * 60)
        print("特征重要性分析")
        print("=" * 60)

        # 使用Random Forest模型的特征重要性
        rf_model = self.models['RandomForest']
        feature_importance = pd.DataFrame({
            'feature': self.X_train.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("\nTop 20 最重要特征:")
        print(feature_importance.head(20).to_string(index=False))

        return feature_importance

    def analyze_brittleness_trajectory(self):
        """分析血糖脆性的时间轨迹"""
        print("\n" + "=" * 60)
        print("血糖脆性时间轨迹分析")
        print("=" * 60)

        # 计算不同时间点的平均指标
        time_points = {
            '术前': {
                'TIR': 'preop_cgm_tir',
                'CV': 'preop_cgm_cv',
                'MAGE': 'preop_cgm_mage'
            },
            '术后72h': {
                'TIR': 'postop_cgm_tir_72h',
                'CV': 'postop_cgm_cv_72h'
            },
            '术后2周': {
                'TIR': 'postop_cgm_tir_2w',
                'CV': 'postop_cgm_cv_2w',
                'MAGE': 'postop_cgm_mage_2w'
            },
            '术后3月': {
                'TIR': 'postop_cgm_tir_3m',
                'CV': 'postop_cgm_cv_3m',
                'MAGE': 'postop_cgm_mage_3m'
            }
        }

        trajectories = {}

        for brittleness_type in ['低脆性', '中脆性', '高脆性']:
            df_subset = self.df[self.df['brittleness_type'] == brittleness_type]
            trajectories[brittleness_type] = {}

            print(f"\n{brittleness_type} 患者 (n={len(df_subset)}):")
            for time_point, metrics in time_points.items():
                print(f"  {time_point}:")
                trajectories[brittleness_type][time_point] = {}
                for metric_name, col_name in metrics.items():
                    if col_name in df_subset.columns:
                        mean_val = df_subset[col_name].mean()
                        std_val = df_subset[col_name].std()
                        print(f"    {metric_name}: {mean_val:.2f} ± {std_val:.2f}")
                        trajectories[brittleness_type][time_point][metric_name] = {
                            'mean': mean_val,
                            'std': std_val
                        }

        return trajectories

    def clinical_insights(self):
        """生成临床洞察"""
        print("\n" + "=" * 60)
        print("临床洞察与建议")
        print("=" * 60)

        insights = []

        # 1. 识别高风险患者特征
        high_risk_patients = self.df[self.df['future_brittleness_risk_3m'] == '高']
        low_risk_patients = self.df[self.df['future_brittleness_risk_3m'] == '低']

        print("\n1. 高风险患者特征对比:")
        print(f"   高风险患者数: {len(high_risk_patients)}")
        print(f"   低风险患者数: {len(low_risk_patients)}")

        comparison_metrics = [
            ('术前HbA1c', 'preop_hba1c'),
            ('术前TIR', 'preop_cgm_tir'),
            ('术前MAGE', 'preop_cgm_mage'),
            ('糖尿病病程', 'diabetes_duration_years'),
            ('术前胰岛素剂量', 'insulin_dose_preop')
        ]

        for metric_name, col_name in comparison_metrics:
            if col_name in self.df.columns:
                high_mean = high_risk_patients[col_name].mean()
                low_mean = low_risk_patients[col_name].mean()
                diff_pct = ((high_mean - low_mean) / low_mean * 100) if low_mean != 0 else 0
                print(f"\n   {metric_name}:")
                print(f"     高风险: {high_mean:.2f}")
                print(f"     低风险: {low_mean:.2f}")
                print(f"     差异: {diff_pct:+.1f}%")

                if abs(diff_pct) > 20:
                    insights.append(
                        f"{metric_name}在高风险和低风险患者间差异显著({diff_pct:+.1f}%)，"
                        f"可作为重要预测指标"
                    )

        # 2. 术后并发症的影响
        print("\n2. 术后并发症对风险的影响:")
        complications_impact = {}

        # 胰瘘
        if 'severe_pancreatic_fistula_flag' in self.df.columns:
            fistula_severe = self.df[self.df['severe_pancreatic_fistula_flag'] > 0]
            if len(fistula_severe) > 0:
                high_risk_pct = (
                    fistula_severe['future_brittleness_risk_3m'] == '高'
                ).sum() / len(fistula_severe) * 100
                print(f"   严重胰瘘: {high_risk_pct:.1f}% 发展为高风险")
                complications_impact['严重胰瘘'] = high_risk_pct

        # 感染
        if 'postop_infection_flag' in self.df.columns:
            infection = self.df[self.df['postop_infection_flag'] > 0]
            if len(infection) > 0:
                high_risk_pct = (
                    infection['future_brittleness_risk_3m'] == '高'
                ).sum() / len(infection) * 100
                print(f"   术后感染: {high_risk_pct:.1f}% 发展为高风险")
                complications_impact['术后感染'] = high_risk_pct

        # 3. 改善病例分析
        print("\n3. 术后血糖脆性改善的病例特点:")
        improved_cases = self.df[
            (self.df['brittleness_type'].isin(['中脆性', '高脆性'])) &
            (self.df['future_brittleness_risk_3m'] == '低')
        ]
        print(f"   改善病例数: {len(improved_cases)}")
        if len(improved_cases) > 0:
            print(f"   特点:")
            print(f"     - 平均术中胰岛素用量: "
                  f"{improved_cases['intraop_insulin_infusion_rate'].mean():.2f} U/h")
            severe_fistula = improved_cases['severe_pancreatic_fistula_flag'] if 'severe_pancreatic_fistula_flag' in improved_cases else pd.Series(0, index=improved_cases.index)
            infection_flag = improved_cases['postop_infection_flag'] if 'postop_infection_flag' in improved_cases else pd.Series(0, index=improved_cases.index)
            no_major_comp = ~((severe_fistula > 0) | (infection_flag > 0))
            no_major_ratio = no_major_comp.mean() * 100 if len(no_major_comp) else 0
            print(f"     - 无严重并发症比例: {no_major_ratio:.1f}%")
            print(f"     - 术后72h TIR: {improved_cases['postop_cgm_tir_72h'].mean():.1f}%")

        # 4. 临床建议
        print("\n4. 临床管理建议:")
        recommendations = [
            "术前评估时重点关注HbA1c、TIR和MAGE指标，识别高脆性患者",
            "对于术前脆性高的患者，术中应加强血糖监测和精准胰岛素管理",
            "积极预防和处理术后并发症（特别是胰瘘和感染），可显著降低脆性恶化风险",
            "术后早期（72小时内）的血糖管理质量是预测长期预后的重要窗口",
            "建议对高风险患者实施术后3个月内的强化CGM监测和个体化干预"
        ]

        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

        return insights, recommendations

    def save_analysis_report(self, output_file='血糖脆性分析报告.txt'):
        """保存分析报告"""
        print(f"\n保存分析报告到 {output_file}...")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("胰腺癌患者血糖脆性分析报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"生成时间: {pd.Timestamp.now()}\n")
            f.write(f"数据文件: {self.data_file}\n")
            f.write(f"样本量: {len(self.df)}\n\n")

            # 模型性能
            f.write("模型性能:\n")
            for model_name, result in self.results.items():
                f.write(f"\n{model_name}:\n")
                f.write(f"  准确率: {result['accuracy']:.3f}\n")
                f.write(f"  交叉验证: {result['cv_scores'].mean():.3f} "
                       f"(+/- {result['cv_scores'].std() * 2:.3f})\n")

        print("✓ 报告已保存")


def main():
    """主函数"""
    print("=" * 60)
    print("胰腺癌患者血糖脆性分析工具")
    print("=" * 60)
    print()

    # 初始化分析器
    data_file = '虚拟患者数据_术前术中术后.csv'
    analyzer = GlycemicBrittlenessAnalyzer(data_file)

    # 加载数据
    analyzer.load_data()

    # 探索性分析
    analyzer.exploratory_analysis()

    # 构建预测模型
    analyzer.build_classification_model()

    # 评估模型
    analyzer.evaluate_models()

    # 特征重要性
    feature_importance = analyzer.analyze_feature_importance()

    # 时间轨迹分析
    trajectories = analyzer.analyze_brittleness_trajectory()

    # 临床洞察
    insights, recommendations = analyzer.clinical_insights()

    # 保存报告
    analyzer.save_analysis_report()

    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)

    return analyzer


if __name__ == "__main__":
    analyzer = main()
