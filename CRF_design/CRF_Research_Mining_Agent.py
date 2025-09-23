#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF数据挖掘智能分析Agent
Clinical Research Data Mining & Analysis Agent

功能特点:
1. 实时数据处理与质量评估 (配置驱动)
2. 多维度统计分析与关联发现 (配置驱动)
3. 研究价值评估与论文切入点推荐
4. 自动化报告生成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import warnings
from dataclasses import dataclass
from enum import Enum
import os

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
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

warnings.filterwarnings('ignore')

# --- 数据结构定义 ---
class ResearchValue(Enum):
    """研究价值等级"""
    VERY_HIGH = "极高价值"
    HIGH = "高价值"
    MODERATE = "中等价值"
    LOW = "低价值"
    INSUFFICIENT = "数据不足"

class PublicationOpportunity(Enum):
    """发表机会类型"""
    ORIGINAL_RESEARCH = "原创研究"
    OBSERVATIONAL_STUDY = "观察性研究"
    CROSS_SECTIONAL = "横断面研究"
    LONGITUDINAL = "纵向研究"
    META_ANALYSIS = "荟萃分析"
    CASE_SERIES = "病例系列"

@dataclass
class ResearchInsight:
    """研究发现"""
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

# --- 主Agent类 ---
class CRFResearchMiningAgent:
    """CRF数据挖掘智能分析代理 (配置驱动版)"""
    
    def __init__(self, config_dir: str, data_storage_path: str = "./crf_data/"):
        """初始化CRF分析代理"""
        self.config_dir = config_dir
        self.data_storage_path = data_storage_path
        self.data_cache = {}
        self.analysis_history = []
        self.research_insights = []
        
        if not HAS_YAML:
            print("❌ 关键依赖包 PyYAML 未安装，Agent无法启动。请运行: pip install pyyaml")
            raise ImportError("PyYAML not found.")

        self.config = self._load_config()
        self.data_sources_config = self.config.get('data_sources', {})
        self.quality_rules = self.config.get('quality_rules', {})
        self.analysis_config = self.config.get('analysis', [])

        os.makedirs(data_storage_path, exist_ok=True)
        print("✅ CRF数据挖掘Agent初始化成功")

    def _load_config(self) -> Dict:
        """加载目录中的所有YAML配置文件"""
        full_config = {}
        try:
            for filename in os.listdir(self.config_dir):
                if filename.endswith(('.yaml', '.yml')):
                    config_path = os.path.join(self.config_dir, filename)
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_key = os.path.splitext(filename)[0]
                        full_config[config_key] = yaml.safe_load(f)
                    print(f"✅ 成功加载配置文件: {config_path}")
            return full_config
        except Exception as e:
            print(f"❌ 加载配置文件目录 '{self.config_dir}' 失败: {e}")
            return {}
        
    def load_crf_data(self) -> Dict[str, pd.DataFrame]:
        """根据配置文件加载CRF数据"""
        datasets = {}
        if not self.data_sources_config:
            print("⚠️ 配置文件中无数据源信息(data_sources.yaml)，跳过加载。")
            return datasets

        for data_type, info in self.data_sources_config.items():
            file_path = info.get('path')
            if not file_path:
                print(f"⚠️ 警告: {data_type} 未配置'path'，跳过。")
                continue
            try:
                if os.path.exists(file_path):
                    if file_path.endswith('.csv'):
                        datasets[data_type] = pd.read_csv(file_path)
                    elif file_path.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        # 使用 json_normalize 来“压平”嵌套的JSON结构
                        datasets[data_type] = pd.json_normalize(data)
                    print(f"✅ 成功加载 {data_type}: {len(datasets[data_type])} 条记录")
                else:
                    print(f"⚠️ 警告: 文件路径不存在 '{file_path}'，跳过加载 {data_type}")
            except Exception as e:
                print(f"❌ 加载 {data_type} 失败: {e}")
        self.data_cache = datasets
        return datasets

    # --- 数据质量引擎 ---
    def assess_data_quality(self) -> Dict[str, Any]:
        """根据配置规则全面评估数据质量"""
        quality_report = {}
        for dataset_name, df in self.data_cache.items():
            quality_metrics = {
                'total_records': len(df),
                'total_features': len(df.columns),
                'missing_rate': df.isnull().mean().mean(),
                'duplicate_rate': df.duplicated().sum() / len(df) if len(df) > 0 else 0,
            }
            dataset_rules = self.quality_rules.get(dataset_name, {})
            generic_rules = self.quality_rules.get('__GENERIC__', {})
            quality_metrics['quality_issues'] = self._apply_rules(df, dataset_rules, generic_rules)
            quality_metrics.update(self._analyze_data_distribution(df, dataset_name))
            quality_report[dataset_name] = quality_metrics
        return quality_report

    def _apply_rules(self, df: pd.DataFrame, specific_rules: Dict, generic_rules: Dict) -> List[str]:
        """应用数据质量规则"""
        issues = []
        def get_col_rules(col_name, col_type):
            col_rules = list(specific_rules.get(col_name, []))
            if col_type == 'numeric':
                col_rules.extend(specific_rules.get('__ALL_NUMERIC__', []))
                col_rules.extend(generic_rules.get('__ALL_NUMERIC__', []))
            elif col_type == 'date':
                col_rules.extend(specific_rules.get('__ALL_DATE__', []))
                col_rules.extend(generic_rules.get('__ALL_DATE__', []))
            return col_rules

        for col in df.columns:
            col_type = 'other'
            if pd.api.types.is_numeric_dtype(df[col]): col_type = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(df[col]) or 'date' in col.lower() or 'time' in col.lower(): col_type = 'date'

            for rule in get_col_rules(col, col_type):
                try:
                    rule_type, params, message = rule.get('type'), rule.get('params'), rule.get('message', f"{col}未通过{rule.get('type')}检查")
                    if rule_type == 'range' and col_type == 'numeric' and not df[col].empty:
                        invalid = df[(df[col] < params[0]) | (df[col] > params[1])]
                        if not invalid.empty: issues.append(f"{message} ({len(invalid)}条记录)")
                    elif rule_type == 'expression':
                        invalid = df.query(f"not ({params})")
                        if not invalid.empty: issues.append(f"{message} ({len(invalid)}条记录)")
                    elif rule_type == 'outlier_iqr' and col_type == 'numeric' and not df[col].empty:
                        Q1, Q3, IQR = df[col].quantile(0.25), df[col].quantile(0.75), df[col].quantile(0.75) - df[col].quantile(0.25)
                        if IQR > 0:
                            outliers = df[(df[col] < Q1 - params * IQR) | (df[col] > Q3 + params * IQR)]
                            if not outliers.empty: issues.append(f"{col}: {message} ({len(outliers)}条记录)")
                    elif rule_type == 'is_date' and col_type == 'date' and not df[col].empty:
                        invalid_count = pd.to_datetime(df[col], errors='coerce').isnull().sum() - df[col].isnull().sum()
                        if invalid_count > 0: issues.append(f"{col}: {message} ({invalid_count}条记录)")
                except Exception as e: issues.append(f"规则执行错误 '{rule.get('type')}' on column '{col}': {e}")
        return list(set(issues))

    def _analyze_data_distribution(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """分析数据分布 (描述性统计)"""
        dist_report = {}
        # 仅对数值型数据进行描述性统计
        numeric_df = df.select_dtypes(include=np.number)
        if not numeric_df.empty:
            desc = numeric_df.describe().to_dict()
            dist_report['numeric_distribution'] = desc
        
        # 对类别型数据进行频数统计
        categorical_df = df.select_dtypes(include=['object', 'category'])
        if not categorical_df.empty:
            cat_report = {}
            for col in categorical_df.columns:
                # 仅报告类别数小于50的列，避免过于冗长
                if categorical_df[col].nunique() < 50:
                    cat_report[col] = categorical_df[col].value_counts().to_dict()
            dist_report['categorical_distribution'] = cat_report
            
        return dist_report

    # --- 研究分析引擎 ---
    def discover_research_opportunities(self) -> List[ResearchInsight]:
        """根据分析配置文件动态发现研究机会"""
        self.research_insights = []
        if not self.analysis_config: return []

        for i, analysis_def in enumerate(self.analysis_config, 1):
            try:
                print(f"\n🚀 [分析 {i}/{len(self.analysis_config)}] {analysis_def.get('title')}")
                df = self._prepare_analysis_data(analysis_def.get('datasets', []))
                if df is None or df.empty: 
                    print(f"⚠️ 数据准备失败或为空，跳过分析: {analysis_def.get('title')}")
                    continue

                df = self._create_analysis_variables(df, analysis_def.get('variables', {}))
                analysis_func = self._get_analysis_function(analysis_def['analysis']['type'])
                analysis_results = analysis_func(df, analysis_def['analysis']['params'])
                analysis_results['sample_size'] = len(df)

                if self._check_trigger(analysis_results, analysis_def.get('trigger', {})):
                    print(f"✅ 发现潜在研究机会: {analysis_def.get('title')}")
                    self.research_insights.append(self._generate_insight(analysis_def, analysis_results))
                else:
                    print(f"ℹ️ 分析完成，未达到触发条件。")
            except Exception as e:
                print(f"❌ 分析 '{analysis_def.get('id', 'N/A')}' 执行失败: {e}")
        return self.research_insights

    def _prepare_analysis_data(self, d_defs: List[Dict]) -> Optional[pd.DataFrame]:
        if not d_defs or d_defs[0]['source'] not in self.data_cache: return None
        df = self.data_cache[d_defs[0]['source']].copy()
        
        # 处理后续数据集的合并
        if len(d_defs) > 1:
            merge_key = d_defs[0].get('merge_key', 'patient_id') # 默认使用 patient_id
            for d_def in d_defs[1:]:
                source_name = d_def['source']
                if source_name not in self.data_cache: 
                    print(f"⚠️ 在数据缓存中未找到 {source_name}，无法合并。")
                    return None
                
                right_df = self.data_cache[source_name]
                how = d_def.get('how', 'inner')
                
                # 检查合并键是否存在
                if merge_key not in df.columns or merge_key not in right_df.columns:
                    print(f"⚠️ 合并键 '{merge_key}' 在数据集中不存在，无法合并 {source_name}。")
                    # 尝试寻找备用键，例如 'subject_id'
                    fallback_keys = ['subject_id', 'id']
                    found_key = False
                    for key in fallback_keys:
                        if key in df.columns and key in right_df.columns:
                            merge_key = key
                            print(f"ℹ️ 使用备用合并键: '{key}'")
                            found_key = True
                            break
                    if not found_key:
                        return None # 如果找不到任何合适的键，则放弃合并
                
                df = pd.merge(df, right_df, on=merge_key, how=how)
        return df

    def _create_analysis_variables(self, df: pd.DataFrame, v_defs: Dict) -> pd.DataFrame:
        for name, v_def in v_defs.items():
            try:
                if v_def['type'] == 'cut': 
                    df[name] = pd.cut(df[v_def['source_column']], **v_def['params'])
                elif v_def['type'] == 'expression':
                    df[name] = df.eval(v_def['expression'])
            except Exception as e:
                print(f"⚠️ 创建变量 '{name}' 失败: {e}")
        return df

    def _get_analysis_function(self, a_type: str) -> callable:
        if a_type == 'chi2_contingency': return self._run_chi2_contingency
        if a_type == 'group_by_rate_diff': return self._run_group_by_rate_diff
        raise ValueError(f"未知的分析类型: {a_type}")

    def _run_chi2_contingency(self, df: pd.DataFrame, params: Dict) -> Dict:
        if not HAS_SCIPY: return {'p_value': 1.0, 'chi2': 0}
        try:
            ct = pd.crosstab(df[params['index']], df[params['columns']])
            if ct.empty or ct.shape[0] < 2 or ct.shape[1] < 2:
                return {'p_value': 1.0, 'chi2': 0, 'error': 'Contingency table is too small'}
            chi2, p, _, _ = stats.chi2_contingency(ct)
            return {'chi2': chi2, 'p_value': p}
        except KeyError as e:
            return {'p_value': 1.0, 'chi2': 0, 'error': f"Column not found: {e}"}

    def _run_group_by_rate_diff(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Groups by a column, calculates rates of a boolean column, and finds the difference."""
        group_by_col = params['group_by_col']
        rate_col = params['rate_col']
        
        if group_by_col not in df.columns or rate_col not in df.columns:
            return {'rate_difference': 0, 'error': f"Column not found in group_by_rate_diff"}

        # Ensure rate_col is boolean or 0/1
        if df[rate_col].dtype != bool and df[rate_col].nunique() <= 2:
            df[rate_col] = df[rate_col].astype(bool)
        else:
            # 如果无法安全转换为bool，则返回错误
            return {'rate_difference': 0, 'error': f"Rate column '{rate_col}' is not binary."}

        rates = df.groupby(group_by_col)[rate_col].mean()
        
        if len(rates) != 2:
            print(f"⚠️ group_by_rate_diff需要group_by列正好有两个组，但发现了{len(rates)}个。")
            return {'rate_difference': 0}

        rate1, rate2 = rates.values
        group1, group2 = rates.index
        
        results = {
            'rate_difference': abs(rate1 - rate2),
            f"{group1}_rate": rate1,
            f"{group2}_rate": rate2,
        }
        # A bit of a hack to support the description template for male/female
        if 'male' in str(group1).lower() or '男' in str(group1):
            results['male_rate'] = rate1
            results['female_rate'] = rate2
        elif 'female' in str(group1).lower() or '女' in str(group1):
            results['female_rate'] = rate1
            results['male_rate'] = rate2
            
        return results

    def _check_trigger(self, results: Dict, t_def: Dict) -> bool:
        if not t_def: return True
        val = results.get(t_def['metric'])
        if val is None: return False
        op_map = {'lt': lambda a, b: a < b, 'gt': lambda a, b: a > b, 'lte': lambda a,b: a <=b, 'gte': lambda a,b: a >= b}
        return op_map[t_def['operator']](val, t_def['value']) if t_def['operator'] in op_map else False

    def _generate_insight(self, a_def: Dict, results: Dict) -> ResearchInsight:
        i_def = a_def['insight']
        # 使用 .get() 并提供默认值来增强鲁棒性
        description = a_def.get('description_template', "No description template provided.").format(**results)
        
        return ResearchInsight(
            title=a_def.get('title', 'Untitled Insight'),
            description=description,
            value_level=ResearchValue[i_def.get('value_level', 'LOW')],
            publication_type=PublicationOpportunity[i_def.get('publication_type', 'OBSERVATIONAL_STUDY')],
            statistical_power=results.get('power', 0.8), # Placeholder
            sample_size=results.get('sample_size', 0),
            key_variables=i_def.get('key_variables', []),
            statistical_methods=i_def.get('statistical_methods', []),
            expected_impact_factor=i_def.get('expected_impact_factor', 'N/A'),
            implementation_difficulty=i_def.get('implementation_difficulty', 'N/A'),
            recommendations=i_def.get('recommendations', [])
        )

    # --- 报告生成 ---
    def generate_research_priority_matrix(self, insights: List[ResearchInsight]) -> Optional[Any]:
        """生成研究优先级矩阵图"""
        if not HAS_PLOTTING or not insights:
            return None
        
        value_map = {val.value: i for i, val in enumerate(ResearchValue)}
        difficulty_map = {'低': 0, '中': 1, '高': 2}

        data = {
            'title': [i.title for i in insights],
            'value': [value_map.get(i.value_level.value, 0) for i in insights],
            'difficulty': [difficulty_map.get(i.implementation_difficulty, 0) for i in insights],
            'sample_size': [i.sample_size for i in insights]
        }
        df = pd.DataFrame(data)

        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df, x='difficulty', y='value', size='sample_size', hue='title', sizes=(100, 2000), legend=False)
        
        plt.title('Research Priority Matrix', fontsize=16)
        plt.xlabel('Implementation Difficulty', fontsize=12)
        plt.ylabel('Research Value', fontsize=12)
        
        plt.xticks(ticks=list(difficulty_map.values()), labels=list(difficulty_map.keys()))
        plt.yticks(ticks=list(value_map.values()), labels=list(value_map.keys()))
        
        for i, row in df.iterrows():
            plt.text(row['difficulty'] + 0.05, row['value'], row['title'], fontsize=9)
            
        plt.grid(True)
        plt.tight_layout()
        
        matrix_path = os.path.join(self.data_storage_path, 'research_priority_matrix.png')
        plt.savefig(matrix_path)
        plt.close()
        print(f"✅ 研究优先级矩阵已保存至: {matrix_path}")
        return matrix_path
    
    def generate_publication_roadmap(self, insights: List[ResearchInsight]) -> Dict[str, List[str]]:
        """生成发表路线图"""
        if not insights:
            return {}
        
        roadmap = {}
        sorted_insights = sorted(insights, key=lambda x: (
            list(ResearchValue).index(x.value_level), 
            {'低': 0, '中': 1, '高': 2}.get(x.implementation_difficulty, 0)
        ), reverse=False) # 价值越高、难度越低，越靠前

        for pub_type in PublicationOpportunity:
            roadmap[pub_type.value] = [
                f"{insight.title} (价值: {insight.value_level.value}, 难度: {insight.implementation_difficulty})"
                for insight in sorted_insights if insight.publication_type == pub_type
            ]
        return {k: v for k, v in roadmap.items() if v}


    def generate_comprehensive_report(self, quality_report: Dict, insights: List[ResearchInsight], output_path: str) -> str:
        """生成全面的Markdown格式分析报告"""
        report_content = f"""
# CRF数据挖掘智能分析报告

**报告生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. 数据质量评估

本部分总结了所加载数据集的整体质量情况。

"""
        for name, metrics in quality_report.items():
            report_content += f"""
### 1.1 数据集: `{name}`

*   **基本信息**:
    *   总记录数: {metrics.get('total_records', 'N/A')}
    *   总特征数: {metrics.get('total_features', 'N/A')}
*   **数据质量指标**:
    *   平均缺失率: {metrics.get('missing_rate', 0):.2%}
    *   重复记录率: {metrics.get('duplicate_rate', 0):.2%}
*   **发现的质量问题**:
"""
            issues = metrics.get('quality_issues', [])
            if issues:
                for issue in issues:
                    report_content += f"    *   {issue}\n"
            else:
                report_content += "    *   未发现明显的质量问题。\n"

        report_content += "\n---\n\n## 2. 研究机会洞察\n"

        if not insights:
            report_content += "本次分析未发现符合触发条件的显著研究机会。\n"
        else:
            matrix_path = self.generate_research_priority_matrix(insights)
            if matrix_path:
                report_content += "### 2.1 研究优先级矩阵\n\n"
                report_content += f"![研究优先级矩阵]({os.path.basename(matrix_path)})\n\n"

            roadmap = self.generate_publication_roadmap(insights)
            if roadmap:
                report_content += "### 2.2 发表路线图建议\n\n"
                for pub_type, items in roadmap.items():
                    report_content += f"#### {pub_type}\n"
                    for item in items:
                        report_content += f"- {item}\n"
                    report_content += "\n"

            report_content += "### 2.3 研究机会详情\n\n"
            for i, insight in enumerate(insights, 1):
                report_content += f"""
#### {i}. {insight.title}

*   **研究价值**: {insight.value_level.value}
*   **发表机会**: {insight.publication_type.value}
*   **核心发现**: {insight.description}
*   **样本量**: {insight.sample_size}
*   **关键变量**: `{', '.join(insight.key_variables)}`
*   **统计方法**: `{', '.join(insight.statistical_methods)}`
*   **预期影响因子**: {insight.expected_impact_factor}
*   **实施难度**: {insight.implementation_difficulty}
*   **建议**:
"""
                for rec in insight.recommendations:
                    report_content += f"    *   {rec}\n"
                report_content += "\n"

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ 综合报告已生成: {output_path}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            
        return report_content

# --- 主执行函数 ---
def main():
    """使用示例"""
    print("--- CRF数据挖掘智能分析Agent (配置驱动版) ---")
    config_dir = 'config'
    if not os.path.isdir(config_dir):
        print(f"❌ 错误: 配置目录不存在于 '{config_dir}'")
        print("请确保 'config' 目录存在，并且包含 data_sources.yaml, quality_rules.yaml, analysis.yaml")
        return

    agent = CRFResearchMiningAgent(config_dir=config_dir)
    
    print("\n--- 1. 加载数据 ---")
    datasets = agent.load_crf_data()
    if not datasets: return

    print("\n--- 2. 评估数据质量 ---")
    quality_report = agent.assess_data_quality()
    for name, metrics in quality_report.items():
        print(f"\n数据集: {name}")
        print(f"  - 问题列表: {metrics.get('quality_issues', [])}")

    print("\n--- 3. 发现研究机会 ---")
    insights = agent.discover_research_opportunities()
    
    print("\n--- 4. 生成综合报告 ---")
    report = agent.generate_comprehensive_report(quality_report, insights, 'CRF_Research_Analysis_Report.md')
    
    print("\n✅ 分析完成！")
    print(f"📄 发现 {len(agent.research_insights)} 个研究机会")
    print("🎯 请查看 'CRF_Research_Analysis_Report.md' 获取详细报告")

if __name__ == "__main__":
    main()
