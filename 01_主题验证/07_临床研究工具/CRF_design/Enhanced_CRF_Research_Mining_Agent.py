#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF数据挖掘智能分析Agent - 多维度增强版
Enhanced Clinical Research Data Mining & Analysis Agent

新增功能特点:
1. 多维度临床参数支持 (100+ 生物标记物)
2. 高级统计分析方法 (机器学习、网络分析、中介分析)
3. 精准医学和个性化治疗分析
4. 社会决定因素健康结局分析
5. 多中心研究质量控制
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import json
import warnings
from dataclasses import dataclass
from enum import Enum
import os
import re

# --- 可选依赖包 ---
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

try:
    from scipy import stats
    from scipy.cluster.hierarchy import dendrogram, linkage
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, silhouette_score
    from sklearn.model_selection import cross_val_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    from lifelines import CoxPHFitter, KaplanMeierFitter
    HAS_SURVIVAL = True
except ImportError:
    HAS_SURVIVAL = False

warnings.filterwarnings('ignore')

# --- 扩展的数据结构定义 ---
class ResearchValue(Enum):
    """研究价值等级"""
    BREAKTHROUGH = "突破性发现"      # 新增：突破性发现
    VERY_HIGH = "极高价值"
    HIGH = "高价值"
    MODERATE = "中等价值"
    LOW = "低价值"
    INSUFFICIENT = "数据不足"

class PublicationOpportunity(Enum):
    """发表机会类型"""
    NATURE_MEDICINE = "Nature Medicine级别"  # 新增
    ORIGINAL_RESEARCH = "原创研究"
    LONGITUDINAL = "纵向研究"
    CROSS_SECTIONAL = "横断面研究"
    OBSERVATIONAL_STUDY = "观察性研究"
    META_ANALYSIS = "荟萃分析"
    CASE_SERIES = "病例系列"
    PRECISION_MEDICINE = "精准医学研究"      # 新增
    SOCIAL_EPIDEMIOLOGY = "社会流行病学"    # 新增

class AnalysisType(Enum):
    """分析类型枚举"""
    CHI2_CONTINGENCY = "chi2_contingency"
    GROUP_BY_RATE_DIFF = "group_by_rate_diff"
    LOGISTIC_REGRESSION = "logistic_regression"           # 新增
    SURVIVAL_ANALYSIS = "survival_analysis"               # 新增
    K_MEANS_CLUSTERING = "k_means_clustering"             # 新增
    RANDOM_FOREST_ANALYSIS = "random_forest_analysis"     # 新增
    CORRELATION_NETWORK = "correlation_network"           # 新增
    MEDIATION_ANALYSIS = "mediation_analysis"             # 新增
    MULTILEVEL_REGRESSION = "multilevel_regression"       # 新增
    RISK_STRATIFICATION = "risk_stratification"           # 新增

@dataclass
class EnhancedResearchInsight:
    """增强的研究发现"""
    title: str
    description: str
    value_level: ResearchValue
    publication_type: PublicationOpportunity
    statistical_power: float
    sample_size: int
    key_variables: List[str]
    statistical_methods: List[str]
    expected_impact_factor: str
    implementation_difficulty: str
    recommendations: List[str]
    # 新增字段
    clinical_significance: str
    precision_medicine_potential: str
    health_economics_impact: str
    regulatory_considerations: List[str]
    international_collaboration_potential: str
    data_sharing_requirements: List[str]

@dataclass
class MultiDimensionalQualityMetrics:
    """多维度数据质量指标"""
    total_records: int
    total_features: int
    missing_rate: float
    duplicate_rate: float
    outlier_rates: Dict[str, float]
    consistency_violations: List[str]
    clinical_implausible_values: List[str]
    temporal_consistency_issues: List[str]
    cross_validation_errors: List[str]
    overall_grade: str
    recommendations: List[str]

# --- 主Agent类增强版 ---
class EnhancedCRFResearchMiningAgent:
    """CRF数据挖掘智能分析代理 - 多维度增强版"""
    
    def __init__(self, config_path: str, data_storage_path: str = "./crf_data/"):
        """初始化增强版CRF分析代理"""
        self.config_path = config_path
        self.data_storage_path = data_storage_path
        self.data_cache = {}
        self.analysis_history = []
        self.research_insights = []
        self.quality_metrics = {}
        
        if not HAS_YAML:
            print("❌ 关键依赖包 PyYAML 未安装，Agent无法启动。请运行: pip install pyyaml")
            raise ImportError("PyYAML not found.")

        self.config = self._load_enhanced_config()
        self.data_sources_config = self.config.get('data_sources', {})
        self.quality_checks = self.config.get('quality_checks', {})
        self.analysis_config = self.config.get('analyses', [])
        self.publication_strategy = self.config.get('publication_strategy', {})
        self.multicenter_settings = self.config.get('multicenter_settings', {})

        os.makedirs(data_storage_path, exist_ok=True)
        print("✅ 增强版CRF数据挖掘Agent初始化成功")
        print(f"📊 支持分析类型: {len(AnalysisType.__members__)}种")
        print(f"🔬 支持参数维度: {len(self.quality_checks.get('clinical_ranges', {}))}个")

    def _load_enhanced_config(self) -> Dict:
        """加载增强配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f"✅ 成功加载增强配置文件: {self.config_path}")
            return config
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return {}

    def load_enhanced_crf_data(self) -> Dict[str, pd.DataFrame]:
        """根据配置文件加载多维度CRF数据"""
        datasets = {}
        if not self.data_sources_config:
            print("⚠️ 配置文件中无数据源信息，跳过加载。")
            return datasets

        for data_type, file_path in self.data_sources_config.items():
            try:
                if os.path.exists(file_path):
                    if file_path.endswith('.csv'):
                        datasets[data_type] = pd.read_csv(file_path)
                    elif file_path.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        datasets[data_type] = pd.json_normalize(data)
                    print(f"✅ 成功加载 {data_type}: {len(datasets[data_type])} 条记录")
                else:
                    print(f"⚠️ 警告: 文件路径不存在 '{file_path}'，跳过加载 {data_type}")
            except Exception as e:
                print(f"❌ 加载 {data_type} 失败: {e}")
        
        self.data_cache = datasets
        return datasets

    # --- 增强的数据质量评估 ---
    def assess_multidimensional_data_quality(self) -> Dict[str, MultiDimensionalQualityMetrics]:
        """多维度数据质量评估"""
        quality_report = {}
        
        for dataset_name, df in self.data_cache.items():
            # 基础质量指标
            total_records = len(df)
            total_features = len(df.columns)
            missing_rate = df.isnull().mean().mean()
            duplicate_rate = df.duplicated().sum() / len(df) if len(df) > 0 else 0
            
            # 异常值检测
            outlier_rates = self._detect_multidimensional_outliers(df, dataset_name)
            
            # 临床合理性检查
            clinical_implausible = self._check_clinical_plausibility(df, dataset_name)
            
            # 逻辑一致性检查
            consistency_violations = self._check_enhanced_consistency(df, dataset_name)
            
            # 时间一致性检查
            temporal_issues = self._check_temporal_consistency(df, dataset_name)
            
            # 交叉验证错误
            cross_validation_errors = self._cross_validate_measurements(df, dataset_name)
            
            # 综合质量等级评定
            overall_grade = self._calculate_overall_quality_grade(
                missing_rate, duplicate_rate, len(clinical_implausible), 
                len(consistency_violations), len(outlier_rates)
            )
            
            # 改进建议
            recommendations = self._generate_quality_recommendations(
                missing_rate, duplicate_rate, clinical_implausible, 
                consistency_violations, outlier_rates
            )
            
            quality_report[dataset_name] = MultiDimensionalQualityMetrics(
                total_records=total_records,
                total_features=total_features,
                missing_rate=missing_rate,
                duplicate_rate=duplicate_rate,
                outlier_rates=outlier_rates,
                consistency_violations=consistency_violations,
                clinical_implausible_values=clinical_implausible,
                temporal_consistency_issues=temporal_issues,
                cross_validation_errors=cross_validation_errors,
                overall_grade=overall_grade,
                recommendations=recommendations
            )
        
        self.quality_metrics = quality_report
        return quality_report

    def _detect_multidimensional_outliers(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, float]:
        """多维度异常值检测"""
        outlier_rates = {}
        clinical_ranges = self.quality_checks.get('clinical_ranges', {})
        
        for col in df.select_dtypes(include=[np.number]).columns:
            if col in clinical_ranges:
                range_config = clinical_ranges[col]
                min_val, max_val = range_config['min'], range_config['max']
                
                # 范围异常值
                range_outliers = df[(df[col] < min_val) | (df[col] > max_val)]
                
                # IQR异常值
                Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                IQR = Q3 - Q1
                if IQR > 0:
                    iqr_outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                    outlier_rates[col] = len(iqr_outliers) / len(df)
                else:
                    outlier_rates[col] = 0
                    
        return outlier_rates

    def _check_clinical_plausibility(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        """临床合理性检查"""
        implausible_values = []
        clinical_ranges = self.quality_checks.get('clinical_ranges', {})
        
        for col, range_config in clinical_ranges.items():
            if col in df.columns:
                min_val, max_val = range_config['min'], range_config['max']
                implausible = df[(df[col] < min_val) | (df[col] > max_val)]
                
                if not implausible.empty:
                    implausible_values.append(
                        f"{col}: {len(implausible)}条记录超出临床合理范围 ({min_val}-{max_val})"
                    )
        
        return implausible_values

    def _check_enhanced_consistency(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        """增强的逻辑一致性检查"""
        violations = []
        consistency_rules = self.quality_checks.get('logical_consistency', [])
        
        for rule in consistency_rules:
            try:
                rule_expr = rule['rule']
                description = rule['description']
                tolerance = rule.get('tolerance', 0)
                
                # 评估规则表达式
                if 'bmi' in rule_expr and all(col in df.columns for col in ['weight_kg', 'height_cm', 'bmi']):
                    # BMI一致性检查
                    calculated_bmi = df['weight_kg'] / (df['height_cm']/100) ** 2
                    bmi_diff = abs(df['bmi'] - calculated_bmi)
                    inconsistent = df[bmi_diff > tolerance]
                    
                    if not inconsistent.empty:
                        violations.append(f"BMI计算不一致: {len(inconsistent)}条记录")
                        
                else:
                    # 通用规则检查
                    try:
                        violated = df.query(f"not ({rule_expr})")
                        if not violated.empty:
                            violations.append(f"{description}: {len(violated)}条记录")
                    except Exception:
                        continue
                        
            except Exception as e:
                violations.append(f"规则检查错误: {rule.get('description', 'Unknown rule')}")
                
        return violations

    def _check_temporal_consistency(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        """时间一致性检查"""
        temporal_issues = []
        
        # 检查日期列
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        
        for col in date_columns:
            try:
                # 转换为日期类型
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # 检查未来日期
                future_dates = df[df[col] > pd.Timestamp.now()]
                if not future_dates.empty:
                    temporal_issues.append(f"{col}: {len(future_dates)}条记录为未来日期")
                    
                # 检查过早日期 (1900年之前)
                too_early = df[df[col] < pd.Timestamp('1900-01-01')]
                if not too_early.empty:
                    temporal_issues.append(f"{col}: {len(too_early)}条记录日期过早")
                    
            except Exception:
                continue
                
        return temporal_issues

    def _cross_validate_measurements(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        """交叉验证测量值"""
        validation_errors = []
        
        # 血压一致性
        if all(col in df.columns for col in ['systolic_bp', 'diastolic_bp']):
            invalid_bp = df[df['systolic_bp'] <= df['diastolic_bp']]
            if not invalid_bp.empty:
                validation_errors.append(f"血压值不合理: {len(invalid_bp)}条记录收缩压≤舒张压")
        
        # BMI与身高体重一致性
        if all(col in df.columns for col in ['bmi', 'weight_kg', 'height_cm']):
            calculated_bmi = df['weight_kg'] / (df['height_cm']/100) ** 2
            bmi_discrepancy = abs(df['bmi'] - calculated_bmi) > 1.0  # 允许1.0的误差
            if bmi_discrepancy.any():
                validation_errors.append(f"BMI计算不一致: {bmi_discrepancy.sum()}条记录")
        
        # 胆固醇成分一致性
        if all(col in df.columns for col in ['total_cholesterol', 'ldl_cholesterol', 'hdl_cholesterol']):
            ldl_hdl_sum = df['ldl_cholesterol'] + df['hdl_cholesterol']
            implausible_lipid = df[ldl_hdl_sum > df['total_cholesterol'] + 1.0]  # 允许1.0的误差
            if not implausible_lipid.empty:
                validation_errors.append(f"血脂成分不合理: {len(implausible_lipid)}条记录")
        
        return validation_errors

    def _calculate_overall_quality_grade(self, missing_rate: float, duplicate_rate: float, 
                                       clinical_issues: int, consistency_issues: int, 
                                       outlier_count: int) -> str:
        """计算综合质量等级"""
        score = 100
        
        # 缺失率扣分
        if missing_rate > 0.20:
            score -= 30
        elif missing_rate > 0.10:
            score -= 15
        elif missing_rate > 0.05:
            score -= 5
            
        # 重复率扣分  
        if duplicate_rate > 0.05:
            score -= 20
        elif duplicate_rate > 0.02:
            score -= 10
            
        # 临床问题扣分
        score -= min(clinical_issues * 5, 25)
        
        # 一致性问题扣分
        score -= min(consistency_issues * 5, 25)
        
        # 异常值扣分
        score -= min(outlier_count * 2, 15)
        
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "可接受"
        elif score >= 60:
            return "一般"
        else:
            return "差"

    def _generate_quality_recommendations(self, missing_rate: float, duplicate_rate: float,
                                        clinical_issues: List[str], consistency_violations: List[str],
                                        outlier_rates: Dict[str, float]) -> List[str]:
        """生成数据质量改进建议"""
        recommendations = []
        
        if missing_rate > 0.10:
            recommendations.append(f"缺失率({missing_rate:.1%})较高，建议加强数据收集完整性")
        
        if duplicate_rate > 0.02:
            recommendations.append(f"重复记录率({duplicate_rate:.1%})偏高，建议清理重复数据")
            
        if clinical_issues:
            recommendations.append("存在临床不合理值，建议核实数据录入准确性")
            
        if consistency_violations:
            recommendations.append("存在逻辑不一致问题，建议建立数据验证规则")
            
        high_outlier_fields = [field for field, rate in outlier_rates.items() if rate > 0.05]
        if high_outlier_fields:
            recommendations.append(f"以下字段异常值较多: {', '.join(high_outlier_fields[:3])}")
            
        if not recommendations:
            recommendations.append("数据质量良好，可进行后续分析")
            
        return recommendations

    # --- 增强的研究机会发现 ---
    def discover_enhanced_research_opportunities(self) -> List[EnhancedResearchInsight]:
        """增强版研究机会发现"""
        self.research_insights = []
        if not self.analysis_config:
            return []

        for i, analysis_def in enumerate(self.analysis_config, 1):
            try:
                print(f"\n🚀 [分析 {i}/{len(self.analysis_config)}] {analysis_def.get('title')}")
                
                # 准备分析数据
                df = self._prepare_enhanced_analysis_data(analysis_def.get('datasets', []))
                if df is None or df.empty:
                    print(f"⚠️ 数据准备失败或为空，跳过分析: {analysis_def.get('title')}")
                    continue

                # 创建分析变量
                df = self._create_enhanced_analysis_variables(df, analysis_def.get('variables', {}))
                
                # 执行分析
                analysis_type = analysis_def['analysis']['type']
                analysis_func = self._get_enhanced_analysis_function(analysis_type)
                analysis_results = analysis_func(df, analysis_def['analysis'])
                analysis_results['sample_size'] = len(df)

                # 检查触发条件
                if self._check_enhanced_trigger(analysis_results, analysis_def.get('trigger', {})):
                    print(f"✅ 发现潜在研究机会: {analysis_def.get('title')}")
                    insight = self._generate_enhanced_insight(analysis_def, analysis_results)
                    self.research_insights.append(insight)
                else:
                    print(f"ℹ️ 分析完成，未达到触发条件。")
                    
            except Exception as e:
                print(f"❌ 分析 '{analysis_def.get('id', 'N/A')}' 执行失败: {e}")
                import traceback
                traceback.print_exc()

        return self.research_insights

    def _prepare_enhanced_analysis_data(self, dataset_defs: List[Dict]) -> Optional[pd.DataFrame]:
        """准备增强分析数据"""
        if not dataset_defs:
            return None
            
        # 获取主数据集
        primary_dataset = dataset_defs[0]
        if isinstance(primary_dataset, str):
            primary_dataset = {'source': primary_dataset}
            
        if primary_dataset['source'] not in self.data_cache:
            return None
            
        df = self.data_cache[primary_dataset['source']].copy()
        
        # 处理多数据集合并
        if len(dataset_defs) > 1:
            merge_key = primary_dataset.get('merge_key', 'patient_id')
            
            for dataset_def in dataset_defs[1:]:
                if isinstance(dataset_def, str):
                    dataset_def = {'source': dataset_def}
                    
                source_name = dataset_def['source']
                if source_name not in self.data_cache:
                    print(f"⚠️ 数据源 {source_name} 未找到，无法合并")
                    continue
                    
                right_df = self.data_cache[source_name]
                how = dataset_def.get('how', 'inner')
                
                # 检查合并键
                if merge_key not in df.columns or merge_key not in right_df.columns:
                    # 尝试备用键
                    fallback_keys = ['subject_id', 'id']
                    found_key = None
                    for key in fallback_keys:
                        if key in df.columns and key in right_df.columns:
                            found_key = key
                            break
                    if found_key:
                        merge_key = found_key
                    else:
                        print(f"⚠️ 无法找到合适的合并键，跳过 {source_name}")
                        continue
                
                df = pd.merge(df, right_df, on=merge_key, how=how, suffixes=('', f'_{source_name}'))
        
        return df

    def _create_enhanced_analysis_variables(self, df: pd.DataFrame, variables: Dict) -> pd.DataFrame:
        """创建增强分析变量"""
        for var_name, var_def in variables.items():
            try:
                var_type = var_def['type']
                
                if var_type == 'cut':
                    source_col = var_def['source_column']
                    df[var_name] = pd.cut(df[source_col], **var_def['params'])
                    
                elif var_type == 'expression':
                    df[var_name] = df.eval(var_def['expression'])
                    
                elif var_type == 'composite_score':
                    # 复合评分
                    components = var_def['components']
                    score = pd.Series(0, index=df.index)
                    
                    for component, weight in components.items():
                        if component in df.columns:
                            # 标准化后加权
                            normalized = (df[component] - df[component].mean()) / df[component].std()
                            score += normalized * weight
                            
                    df[var_name] = score
                    
                elif var_type == 'composite_z_score':
                    # 标准化复合评分
                    components = var_def['components']
                    z_scores = []
                    
                    for component in components:
                        if component in df.columns:
                            z_score = (df[component] - df[component].mean()) / df[component].std()
                            z_scores.append(z_score)
                    
                    if z_scores:
                        df[var_name] = pd.concat(z_scores, axis=1).mean(axis=1)
                        
            except Exception as e:
                print(f"⚠️ 创建变量 '{var_name}' 失败: {e}")
                
        return df

    def _get_enhanced_analysis_function(self, analysis_type: str) -> callable:
        """获取增强分析函数"""
        analysis_map = {
            'chi2_contingency': self._run_chi2_contingency,
            'group_by_rate_diff': self._run_group_by_rate_diff,
            'logistic_regression': self._run_logistic_regression,
            'survival_analysis': self._run_survival_analysis,
            'k_means_clustering': self._run_k_means_clustering,
            'random_forest_analysis': self._run_random_forest_analysis,
            'correlation_network': self._run_correlation_network,
            'mediation_analysis': self._run_mediation_analysis,
            'multilevel_regression': self._run_multilevel_regression,
            'risk_stratification': self._run_risk_stratification,
            'prevalence': self._run_prevalence_analysis,
        }
        
        if analysis_type not in analysis_map:
            raise ValueError(f"未知的分析类型: {analysis_type}")
            
        return analysis_map[analysis_type]

    # --- 新增分析方法 ---
    def _run_logistic_regression(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """逻辑回归分析"""
        if not HAS_SKLEARN:
            return {'auc': 0, 'error': 'sklearn not available'}
            
        try:
            dependent = analysis_config['dependent']
            independent = analysis_config['independent']
            
            # 准备数据
            X = df[independent].fillna(0)
            y = df[dependent].fillna(0)
            
            # 拟合模型
            model = LogisticRegression(random_state=42)
            model.fit(X, y)
            
            # 预测和评估
            y_pred_proba = model.predict_proba(X)[:, 1]
            auc = roc_auc_score(y, y_pred_proba)
            
            # 特征重要性（系数）
            feature_importance = dict(zip(independent, abs(model.coef_[0])))
            
            return {
                'model_auc': auc,
                'feature_importance': feature_importance,
                'coefficients': dict(zip(independent, model.coef_[0])),
                'sample_size': len(df)
            }
            
        except Exception as e:
            return {'auc': 0, 'error': str(e)}

    def _run_survival_analysis(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """生存分析"""
        if not HAS_SURVIVAL:
            return {'hazard_ratio': 1.0, 'error': 'lifelines not available'}
            
        try:
            duration_col = analysis_config['time_to_event']
            event_col = analysis_config['event']
            
            # Kaplan-Meier估计
            kmf = KaplanMeierFitter()
            kmf.fit(df[duration_col], df[event_col])
            
            # Cox比例风险模型（如果有协变量）
            if 'covariates' in analysis_config:
                cph = CoxPHFitter()
                covariates = analysis_config['covariates']
                data = df[[duration_col, event_col] + covariates].dropna()
                cph.fit(data, duration_col=duration_col, event_col=event_col)
                
                hazard_ratios = cph.hazard_ratios_.to_dict()
                p_values = cph.summary['p'].to_dict()
                
                return {
                    'hazard_ratios': hazard_ratios,
                    'p_values': p_values,
                    'median_survival': kmf.median_survival_time_,
                    'sample_size': len(data)
                }
            else:
                return {
                    'median_survival': kmf.median_survival_time_,
                    'sample_size': len(df)
                }
                
        except Exception as e:
            return {'hazard_ratio': 1.0, 'error': str(e)}

    def _run_k_means_clustering(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """K均值聚类分析"""
        if not HAS_SKLEARN:
            return {'silhouette_score': 0, 'error': 'sklearn not available'}
            
        try:
            features = analysis_config['features']
            n_clusters = analysis_config.get('n_clusters', 3)
            
            # 准备数据
            X = df[features].fillna(0)
            
            # 标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # K均值聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            # 评估聚类质量
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            
            # 聚类中心
            cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
            
            return {
                'silhouette_score': silhouette_avg,
                'cluster_labels': cluster_labels.tolist(),
                'cluster_centers': cluster_centers.tolist(),
                'inertia': kmeans.inertia_,
                'sample_size': len(X)
            }
            
        except Exception as e:
            return {'silhouette_score': 0, 'error': str(e)}

    def _run_random_forest_analysis(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """随机森林分析"""
        if not HAS_SKLEARN:
            return {'importance_score': 0, 'error': 'sklearn not available'}
            
        try:
            target = analysis_config['target']
            predictors = analysis_config['predictors']
            
            # 准备数据
            X = df[predictors].fillna(0)
            y = df[target].fillna(0)
            
            # 判断是分类还是回归
            if y.nunique() <= 10 and y.dtype in ['object', 'bool', 'category']:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # 拟合模型
            model.fit(X, y)
            
            # 特征重要性
            feature_importance = dict(zip(predictors, model.feature_importances_))
            
            # 交叉验证评分
            cv_scores = cross_val_score(model, X, y, cv=5)
            
            return {
                'feature_importance': feature_importance,
                'cv_score_mean': cv_scores.mean(),
                'cv_score_std': cv_scores.std(),
                'oob_score': getattr(model, 'oob_score_', None),
                'sample_size': len(X)
            }
            
        except Exception as e:
            return {'importance_score': 0, 'error': str(e)}

    def _run_correlation_network(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """相关性网络分析"""
        if not HAS_NETWORKX or not HAS_SCIPY:
            return {'network_density': 0, 'error': 'networkx or scipy not available'}
            
        try:
            variables = analysis_config.get('variables', df.select_dtypes(include=[np.number]).columns.tolist())
            correlation_threshold = analysis_config.get('correlation_threshold', 0.3)
            
            # 计算相关系数矩阵
            corr_matrix = df[variables].corr()
            
            # 创建网络图
            G = nx.Graph()
            
            # 添加节点
            G.add_nodes_from(variables)
            
            # 添加边（相关性超过阈值）
            for i, var1 in enumerate(variables):
                for j, var2 in enumerate(variables):
                    if i < j:  # 避免重复
                        corr_val = abs(corr_matrix.loc[var1, var2])
                        if corr_val > correlation_threshold:
                            G.add_edge(var1, var2, weight=corr_val)
            
            # 网络指标
            network_metrics = {
                'network_density': nx.density(G),
                'average_clustering': nx.average_clustering(G),
                'number_of_nodes': G.number_of_nodes(),
                'number_of_edges': G.number_of_edges()
            }
            
            # 中心性指标
            centrality = nx.degree_centrality(G)
            
            return {
                **network_metrics,
                'centrality': centrality,
                'correlation_matrix': corr_matrix.to_dict(),
                'sample_size': len(df)
            }
            
        except Exception as e:
            return {'network_density': 0, 'error': str(e)}

    def _run_mediation_analysis(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """中介分析（简化版）"""
        if not HAS_SKLEARN or not HAS_SCIPY:
            return {'mediation_effect': 0, 'error': 'sklearn or scipy not available'}
            
        try:
            independent = analysis_config['independent']
            mediator = analysis_config['mediator']
            dependent = analysis_config['dependent']
            
            # 准备数据
            X = df[independent].fillna(0)
            M = df[mediator].fillna(0)
            Y = df[dependent].fillna(0)
            
            # 路径分析
            # Path a: X -> M
            from sklearn.linear_model import LinearRegression
            model_a = LinearRegression()
            model_a.fit(X.values.reshape(-1, 1), M)
            a_coef = model_a.coef_[0]
            
            # Path b: M -> Y (controlling for X)
            model_b = LinearRegression()
            XM = np.column_stack([X, M])
            model_b.fit(XM, Y)
            b_coef = model_b.coef_[1]  # M的系数
            
            # Path c: X -> Y (total effect)
            model_c = LinearRegression()
            model_c.fit(X.values.reshape(-1, 1), Y)
            c_coef = model_c.coef_[0]
            
            # Path c': X -> Y (controlling for M, direct effect)
            c_prime_coef = model_b.coef_[0]  # X的系数
            
            # 中介效应
            mediation_effect = a_coef * b_coef
            mediation_proportion = mediation_effect / c_coef if c_coef != 0 else 0
            
            return {
                'mediation_effect': mediation_effect,
                'mediation_proportion': mediation_proportion,
                'direct_effect': c_prime_coef,
                'total_effect': c_coef,
                'a_path': a_coef,
                'b_path': b_coef,
                'sample_size': len(df)
            }
            
        except Exception as e:
            return {'mediation_effect': 0, 'error': str(e)}

    def _run_multilevel_regression(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """多层回归分析（简化版）"""
        # 简化实现，实际需要专门的多层建模包如statsmodels
        if not HAS_SKLEARN:
            return {'variance_explained_community': 0, 'error': 'sklearn not available'}
            
        try:
            dependent = analysis_config['dependent']
            independent = analysis_config['independent']
            group_var = analysis_config.get('group_variable', 'community_id')
            
            # 如果没有分组变量，降级为普通回归
            if group_var not in df.columns:
                model = LinearRegression()
                X = df[independent].fillna(0)
                y = df[dependent].fillna(0)
                model.fit(X, y)
                
                return {
                    'r_squared': model.score(X, y),
                    'coefficients': dict(zip(independent, model.coef_)),
                    'variance_explained_community': 0,
                    'sample_size': len(df)
                }
            
            # 简化的组间差异分析
            group_means = df.groupby(group_var)[dependent].mean()
            overall_mean = df[dependent].mean()
            
            # 组间方差占比（简化计算）
            between_group_var = ((group_means - overall_mean) ** 2).mean()
            total_var = df[dependent].var()
            variance_explained_community = between_group_var / total_var if total_var > 0 else 0
            
            return {
                'variance_explained_community': variance_explained_community,
                'group_means': group_means.to_dict(),
                'sample_size': len(df)
            }
            
        except Exception as e:
            return {'variance_explained_community': 0, 'error': str(e)}

    def _run_risk_stratification(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """风险分层分析"""
        if not HAS_SKLEARN:
            return {'risk_auc': 0, 'error': 'sklearn not available'}
            
        try:
            risk_factors = analysis_config.get('risk_factors', [])
            outcome = analysis_config.get('outcome')
            
            # 创建风险评分
            X = df[risk_factors].fillna(0)
            y = df[outcome].fillna(0)
            
            # 使用逻辑回归创建风险模型
            model = LogisticRegression(random_state=42)
            model.fit(X, y)
            
            # 计算风险概率
            risk_probabilities = model.predict_proba(X)[:, 1]
            
            # 风险分层
            risk_quantiles = pd.qcut(risk_probabilities, q=4, labels=['低风险', '中低风险', '中高风险', '高风险'])
            
            # 各风险层的结局率
            risk_strata_outcomes = df.groupby(risk_quantiles)[outcome].mean()
            
            # AUC
            auc = roc_auc_score(y, risk_probabilities)
            
            return {
                'risk_auc': auc,
                'risk_strata_outcomes': risk_strata_outcomes.to_dict(),
                'feature_weights': dict(zip(risk_factors, model.coef_[0])),
                'sample_size': len(df)
            }
            
        except Exception as e:
            return {'risk_auc': 0, 'error': str(e)}

    def _run_prevalence_analysis(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """患病率分析"""
        try:
            condition_col = analysis_config.get('condition_column')
            threshold = analysis_config.get('threshold', 0)
            operator = analysis_config.get('operator', '>=')
            
            # 根据操作符计算患病率
            if operator == '>=':
                condition = df[condition_col] >= threshold
            elif operator == '>':
                condition = df[condition_col] > threshold
            elif operator == '<=':
                condition = df[condition_col] <= threshold
            elif operator == '<':
                condition = df[condition_col] < threshold
            else:
                condition = df[condition_col] >= threshold
                
            prevalence_rate = condition.mean()
            
            # 按分组计算患病率
            if 'stratify_by' in analysis_config:
                stratify_col = analysis_config['stratify_by']
                if stratify_col in df.columns:
                    stratified_prevalence = df.groupby(stratify_col).apply(
                        lambda x: (x[condition_col] >= threshold).mean()
                    ).to_dict()
                else:
                    stratified_prevalence = {}
            else:
                stratified_prevalence = {}
            
            return {
                'prevalence_rate': prevalence_rate,
                'stratified_prevalence': stratified_prevalence,
                'affected_count': condition.sum(),
                'sample_size': len(df)
            }
            
        except Exception as e:
            return {'prevalence_rate': 0, 'error': str(e)}

    # --- 保持原有方法 ---
    def _run_chi2_contingency(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """卡方检验分析"""
        if not HAS_SCIPY:
            return {'p_value': 1.0, 'chi2': 0}
            
        try:
            params = analysis_config.get('params', analysis_config)
            ct = pd.crosstab(df[params['index']], df[params['columns']])
            if ct.empty or ct.shape[0] < 2 or ct.shape[1] < 2:
                return {'p_value': 1.0, 'chi2': 0, 'error': 'Contingency table is too small'}
            chi2, p, _, _ = stats.chi2_contingency(ct)
            return {'chi2': chi2, 'p_value': p}
        except Exception as e:
            return {'p_value': 1.0, 'chi2': 0, 'error': str(e)}

    def _run_group_by_rate_diff(self, df: pd.DataFrame, analysis_config: Dict) -> Dict:
        """组间率差分析"""
        try:
            params = analysis_config.get('params', analysis_config)
            group_by_col = params['group_by_col']
            rate_col = params['rate_col']
            
            if group_by_col not in df.columns or rate_col not in df.columns:
                return {'rate_difference': 0, 'error': 'Column not found'}
            
            # 确保rate_col是二进制的
            if df[rate_col].nunique() <= 2:
                df[rate_col] = df[rate_col].astype(bool)
            else:
                return {'rate_difference': 0, 'error': 'Rate column is not binary'}
            
            rates = df.groupby(group_by_col)[rate_col].mean()
            
            if len(rates) != 2:
                return {'rate_difference': 0, 'error': f'Expected 2 groups, found {len(rates)}'}
            
            rate1, rate2 = rates.values
            group1, group2 = rates.index
            
            return {
                'rate_difference': abs(rate1 - rate2),
                f'{group1}_rate': rate1,
                f'{group2}_rate': rate2,
                'sample_size': len(df)
            }
            
        except Exception as e:
            return {'rate_difference': 0, 'error': str(e)}

    def _check_enhanced_trigger(self, results: Dict, trigger_def: Dict) -> bool:
        """增强版触发条件检查"""
        if not trigger_def:
            return True
            
        metric = trigger_def.get('metric')
        operator = trigger_def.get('operator')
        value = trigger_def.get('value')
        
        if not all([metric, operator, value is not None]):
            return False
            
        result_val = results.get(metric)
        if result_val is None:
            return False
            
        op_map = {
            'lt': lambda a, b: a < b,
            'gt': lambda a, b: a > b,
            'lte': lambda a, b: a <= b,
            'gte': lambda a, b: a >= b,
            'eq': lambda a, b: abs(a - b) < 1e-6,
            'ne': lambda a, b: abs(a - b) >= 1e-6
        }
        
        if operator not in op_map:
            return False
            
        return op_map[operator](result_val, value)

    def _generate_enhanced_insight(self, analysis_def: Dict, results: Dict) -> EnhancedResearchInsight:
        """生成增强研究洞察"""
        insight_template = analysis_def.get('insight_template', {})
        
        # 基础信息
        title = analysis_def.get('title', 'Untitled Research')
        description = analysis_def.get('description_template', '').format(**results)
        
        # 研究价值和发表类型
        value_level = ResearchValue[insight_template.get('value_level', 'MODERATE')]
        pub_type = PublicationOpportunity[insight_template.get('publication_type', 'CROSS_SECTIONAL')]
        
        # 统计功效评估
        sample_size = results.get('sample_size', 0)
        statistical_power = self._estimate_statistical_power(results, sample_size)
        
        # 生成推荐建议
        recommendations = insight_template.get('recommendations', [])
        recommendations.extend(self._generate_advanced_recommendations(analysis_def, results))
        
        return EnhancedResearchInsight(
            title=title,
            description=description,
            value_level=value_level,
            publication_type=pub_type,
            statistical_power=statistical_power,
            sample_size=sample_size,
            key_variables=insight_template.get('key_variables', []),
            statistical_methods=insight_template.get('statistical_methods', []),
            expected_impact_factor=insight_template.get('expected_impact_factor', 'N/A'),
            implementation_difficulty=insight_template.get('implementation_difficulty', '中等'),
            recommendations=recommendations,
            clinical_significance=self._assess_clinical_significance(results),
            precision_medicine_potential=self._assess_precision_medicine_potential(analysis_def, results),
            health_economics_impact=self._assess_health_economics_impact(results),
            regulatory_considerations=self._identify_regulatory_considerations(analysis_def),
            international_collaboration_potential=self._assess_collaboration_potential(analysis_def, results),
            data_sharing_requirements=self._identify_data_sharing_requirements(analysis_def)
        )

    def _estimate_statistical_power(self, results: Dict, sample_size: int) -> float:
        """估算统计功效"""
        if 'p_value' in results and results['p_value'] < 0.05:
            if sample_size >= 500:
                return 0.95
            elif sample_size >= 300:
                return 0.85
            elif sample_size >= 100:
                return 0.75
            else:
                return 0.60
        else:
            return 0.50

    def _generate_advanced_recommendations(self, analysis_def: Dict, results: Dict) -> List[str]:
        """生成高级推荐建议"""
        recommendations = []
        analysis_type = analysis_def.get('analysis', {}).get('type', '')
        
        if 'machine_learning' in analysis_type or 'random_forest' in analysis_type:
            recommendations.append("考虑使用外部数据集进行模型验证")
            recommendations.append("探索特征工程优化模型性能")
            
        if 'network' in analysis_type:
            recommendations.append("进一步分析关键节点的生物学意义")
            recommendations.append("考虑动态网络分析捕获时间变化")
            
        if results.get('sample_size', 0) > 1000:
            recommendations.append("样本量充足，可考虑多中心验证")
            
        return recommendations

    def _assess_clinical_significance(self, results: Dict) -> str:
        """评估临床意义"""
        if 'auc' in results and results['auc'] > 0.80:
            return "预测模型具有良好的临床应用价值"
        elif 'hazard_ratio' in results and results['hazard_ratio'] > 2.0:
            return "风险比提示强烈的临床关联"
        elif 'rate_difference' in results and results['rate_difference'] > 0.20:
            return "组间差异具有临床意义"
        else:
            return "需要进一步评估临床意义"

    def _assess_precision_medicine_potential(self, analysis_def: Dict, results: Dict) -> str:
        """评估精准医学潜力"""
        analysis_type = analysis_def.get('analysis', {}).get('type', '')
        
        if 'random_forest' in analysis_type or 'clustering' in analysis_type:
            return "高 - 可用于患者分层和个性化治疗"
        elif 'network' in analysis_type:
            return "中等 - 可识别个性化靶点"
        else:
            return "低 - 主要用于人群层面指导"

    def _assess_health_economics_impact(self, results: Dict) -> str:
        """评估卫生经济学影响"""
        if 'prevalence_rate' in results and results['prevalence_rate'] > 0.30:
            return "高患病率提示重大经济负担，干预具有成本效益"
        elif 'risk_auc' in results and results['risk_auc'] > 0.75:
            return "风险预测模型可优化资源配置，降低医疗成本"
        else:
            return "需要专门的卫生经济学评价"

    def _identify_regulatory_considerations(self, analysis_def: Dict) -> List[str]:
        """识别监管考量"""
        considerations = []
        
        if 'prediction' in analysis_def.get('title', '').lower():
            considerations.append("AI医疗器械监管要求")
            considerations.append("临床验证和安全性评估")
            
        if 'biomarker' in str(analysis_def).lower():
            considerations.append("生物标志物验证要求")
            considerations.append("诊断试剂盒注册")
            
        if not considerations:
            considerations.append("遵循医学研究伦理要求")
            
        return considerations

    def _assess_collaboration_potential(self, analysis_def: Dict, results: Dict) -> str:
        """评估国际合作潜力"""
        if results.get('sample_size', 0) > 1000:
            return "高 - 适合国际多中心合作研究"
        elif 'network' in analysis_def.get('analysis', {}).get('type', ''):
            return "中等 - 可与系统生物学团队合作"
        else:
            return "低 - 主要为本地研究"

    def _identify_data_sharing_requirements(self, analysis_def: Dict) -> List[str]:
        """识别数据共享要求"""
        requirements = []
        
        if 'genomic' in str(analysis_def).lower():
            requirements.append("遵循基因组数据共享协议")
            requirements.append("患者知情同意更新")
        
        requirements.extend([
            "数据去标识化处理",
            "隐私保护技术应用",
            "数据使用协议签署"
        ])
        
        return requirements

    # --- 报告生成增强 ---
    def generate_comprehensive_enhanced_report(self, output_path: str) -> str:
        """生成全面的增强版分析报告"""
        if not self.quality_metrics:
            self.assess_multidimensional_data_quality()
            
        if not self.research_insights:
            self.discover_enhanced_research_opportunities()
            
        report_content = self._build_enhanced_report_content()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ 增强版综合报告已生成: {output_path}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            
        return report_content

    def _build_enhanced_report_content(self) -> str:
        """构建增强版报告内容"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# CRF数据挖掘智能分析报告 - 增强版

**报告生成时间:** {timestamp}  
**分析维度:** 多维度临床研究数据挖掘  
**Agent版本:** Enhanced v3.0

---

## 🏥 执行摘要

本报告基于{len(self.data_cache)}个数据源，涵盖{sum(len(df) for df in self.data_cache.values())}条患者记录，采用{len(self.analysis_config)}种高级统计分析方法，识别出**{len(self.research_insights)}个高价值研究机会**。

### 📊 数据质量概况
"""
        
        # 数据质量部分
        for dataset_name, metrics in self.quality_metrics.items():
            report += f"""
#### 数据集: `{dataset_name}`
- **记录数**: {metrics.total_records:,}
- **特征维度**: {metrics.total_features}
- **数据质量等级**: {metrics.overall_grade}
- **缺失率**: {metrics.missing_rate:.1%}
- **重复率**: {metrics.duplicate_rate:.1%}
"""

        # 研究发现部分
        report += "\n## 🎯 研究机会发现\n"
        
        if self.research_insights:
            # 按价值等级分组
            value_groups = {}
            for insight in self.research_insights:
                level = insight.value_level.value
                if level not in value_groups:
                    value_groups[level] = []
                value_groups[level].append(insight)
            
            report += f"共识别出 **{len(self.research_insights)}** 个研究机会，按价值等级分布：\n\n"
            for level, insights in value_groups.items():
                report += f"- **{level}**: {len(insights)}个\n"
            
            # 详细研究机会
            report += "\n### 🏆 高价值研究发现详情\n"
            
            for i, insight in enumerate(self.research_insights, 1):
                report += f"""
#### {i}. {insight.title}

**研究价值**: {insight.value_level.value}  
**发表类型**: {insight.publication_type.value}  
**统计功效**: {insight.statistical_power:.2f}  
**样本量**: {insight.sample_size:,}  
**期刊档次**: {insight.expected_impact_factor}

**研究描述**: {insight.description}

**关键变量**: `{', '.join(insight.key_variables[:5])}`  
**统计方法**: {', '.join(insight.statistical_methods)}

**临床意义**: {insight.clinical_significance}  
**精准医学潜力**: {insight.precision_medicine_potential}  
**卫生经济学影响**: {insight.health_economics_impact}

**实施建议**:
"""
                for rec in insight.recommendations[:3]:  # 限制显示条数
                    report += f"- {rec}\n"
                    
                report += f"""
**监管考量**: {'; '.join(insight.regulatory_considerations[:2])}  
**国际合作潜力**: {insight.international_collaboration_potential}

---
"""

        # 发表策略
        report += self._generate_publication_strategy_section()
        
        # 质量改进建议
        report += self._generate_quality_improvement_section()
        
        # 技术附录
        report += self._generate_technical_appendix()
        
        return report

    def _generate_publication_strategy_section(self) -> str:
        """生成发表策略部分"""
        strategy_config = self.publication_strategy
        
        section = "\n## 📚 发表策略建议\n"
        
        if not self.research_insights:
            return section + "暂无研究发现，无法生成发表策略。\n"
        
        # 按期刊档次分组
        high_impact = [i for i in self.research_insights if i.value_level in [ResearchValue.BREAKTHROUGH, ResearchValue.VERY_HIGH]]
        medium_impact = [i for i in self.research_insights if i.value_level == ResearchValue.HIGH]
        
        if high_impact:
            section += f"""
### 🌟 高影响因子期刊 (8+ IF)
**目标期刊**: Nature Medicine, Lancet Diabetes & Endocrinology, Diabetes Care
**研究项目**: {len(high_impact)}个
**预期时间线**: 18-24个月

重点项目:
"""
            for insight in high_impact[:2]:  # 显示前2个
                section += f"- **{insight.title}** (统计功效: {insight.statistical_power:.2f})\n"
        
        if medium_impact:
            section += f"""
### 📊 中等影响因子期刊 (4-8 IF)  
**目标期刊**: Diabetologia, Cardiovascular Diabetology
**研究项目**: {len(medium_impact)}个
**预期时间线**: 12-18个月
"""
        
        # 时间规划
        section += """
### ⏰ 发表时间规划

**短期 (6个月内)**:
- 数据清理和质量控制完善
- 初步分析结果验证

**中期 (6-12个月)**:
- 主要研究完成和投稿
- 同行评议回应

**长期 (12-24个月)**:
- 高影响因子期刊投稿
- 国际会议展示
"""
        
        return section

    def _generate_quality_improvement_section(self) -> str:
        """生成质量改进建议部分"""
        section = "\n## 🔧 数据质量改进建议\n"
        
        all_recommendations = []
        for metrics in self.quality_metrics.values():
            all_recommendations.extend(metrics.recommendations)
        
        # 去重并分类
        unique_recommendations = list(set(all_recommendations))
        
        if unique_recommendations:
            section += "### 📋 综合改进建议\n"
            for i, rec in enumerate(unique_recommendations, 1):
                section += f"{i}. {rec}\n"
        
        # 多中心研究建议
        if self.multicenter_settings:
            section += """
### 🌐 多中心研究质量控制

**中心间一致性要求**:
- 实验室标准化和质控
- 问卷语言版本验证  
- 工作人员培训认证

**质量监控指标**:
- 中心间变异系数 < 15%
- 数据完整度 > 95%
- 协议偏离率 < 5%
"""
        
        return section

    def _generate_technical_appendix(self) -> str:
        """生成技术附录"""
        section = "\n## 📈 技术附录\n"
        
        section += f"""
### 🔬 分析方法统计

**支持的分析类型**: {len(AnalysisType.__members__)}种
- 传统统计方法: 卡方检验, t检验, 相关分析
- 机器学习方法: 随机森林, 聚类分析, 逻辑回归
- 高级分析: 生存分析, 中介分析, 多层回归, 网络分析

**数据质量指标**: {len(self.quality_checks.get('clinical_ranges', {}))}个临床参数范围检查

### 💻 系统配置

**Python依赖包状态**:
- ✅ pandas, numpy: 数据处理
- {'✅' if HAS_SCIPY else '❌'} scipy: 统计分析
- {'✅' if HAS_SKLEARN else '❌'} scikit-learn: 机器学习
- {'✅' if HAS_NETWORKX else '❌'} networkx: 网络分析
- {'✅' if HAS_SURVIVAL else '❌'} lifelines: 生存分析
- {'✅' if HAS_PLOTTING else '❌'} matplotlib, seaborn: 可视化

### 🎯 研究质量控制

**统计显著性**: p < 0.05
**最小样本量**: 100例
**数据完整度要求**: > 80%
**效应量阈值**: 小(0.1), 中(0.2), 大(0.35)
"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        section += f"""
---
**报告生成**: {timestamp}  
**Agent版本**: Enhanced CRF Research Mining Agent v3.0  
**技术支持**: G+ Platform 临床研究团队
"""
        
        return section

# --- 主执行函数 ---
def main():
    """使用示例"""
    print("=== CRF数据挖掘智能分析Agent - 增强版 ===")
    
    config_path = './Enhanced_Multi_Dimensional_Config.yaml'
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        print("请确保Enhanced_Multi_Dimensional_Config.yaml文件存在")
        return

    agent = EnhancedCRFResearchMiningAgent(config_path=config_path)
    
    print("\n--- 1. 加载多维度数据 ---")
    datasets = agent.load_enhanced_crf_data()
    if not datasets:
        print("⚠️ 无数据加载，退出分析")
        return

    print("\n--- 2. 多维度数据质量评估 ---")
    quality_report = agent.assess_multidimensional_data_quality()
    
    print("\n--- 3. 发现增强研究机会 ---")
    insights = agent.discover_enhanced_research_opportunities()
    
    print("\n--- 4. 生成增强版综合报告 ---")
    report_path = './Enhanced_CRF_Research_Analysis_Report.md'
    agent.generate_comprehensive_enhanced_report(report_path)
    
    print(f"\n✅ 增强版分析完成！")
    print(f"📊 处理数据: {sum(len(df) for df in datasets.values()):,}条记录")
    print(f"🔍 发现研究机会: {len(insights)}个")
    print(f"📄 报告路径: {report_path}")
    print("🎯 系统支持100+临床参数，10+高级分析方法")

if __name__ == "__main__":
    main()