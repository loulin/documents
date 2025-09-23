#!/usr/bin/env python3
"""
生成V4.0诊断与内置诊断的对比表格
基于高标准V4.0方法的真实诊断对比分析
"""

import pandas as pd
import numpy as np
import os
from collections import Counter

class V4DiagnosisComparator:
    """V4.0诊断对比分析器"""
    
    def __init__(self):
        # SNOMED-CT代码映射
        self.snomed_to_chinese = {
            '426627000': '心动过速',
            '426177001': '束支阻滞', 
            '164889003': '房性心律失常',
            '59118001': '右束支阻滞',
            '164934002': '心房颤动',
            '251146004': '左束支阻滞',
            '428750005': '左束支阻滞',
            '427393009': '窦性心动过缓',
            '426783006': '窦性心律',
            '164917005': '心律不齐',
            '413444003': '心肌缺血',
            '164884008': '心电图异常',
            '164865005': '二度房室阻滞',
            '164890007': '室性心律失常',
            '164909002': '左轴偏转',
            '17338001': '室性期前收缩',
            '39732003': '左心室肥厚',
            '429622005': '左前分支阻滞'
        }
        
        # 反向映射
        self.chinese_to_snomed = {v: k for k, v in self.snomed_to_chinese.items()}
    
    def load_builtin_diagnoses(self, data_dir):
        """加载内置诊断"""
        builtin_data = []
        
        # 读取RECORDS文件
        records_file = os.path.join(data_dir, 'RECORDS')
        if not os.path.exists(records_file):
            print("❌ 未找到RECORDS文件")
            return None
        
        with open(records_file, 'r') as f:
            record_names = [line.strip() for line in f if line.strip()]
        
        print(f"📋 加载 {len(record_names)} 个记录的内置诊断...")
        
        for record_name in record_names:
            header_file = os.path.join(data_dir, f"{record_name}.hea")
            if not os.path.exists(header_file):
                continue
                
            # 解析头文件
            try:
                with open(header_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 提取患者信息和诊断
                age, sex, diagnosis = None, None, None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('#Age:'):
                        age = line.split(':')[1].strip()
                    elif line.startswith('#Sex:'):
                        sex = line.split(':')[1].strip()
                    elif line.startswith('#Dx:'):
                        diagnosis = line.split(':')[1].strip()
                        break
                
                # 处理诊断代码
                builtin_diagnoses = []
                if diagnosis:
                    codes = [code.strip() for code in diagnosis.split(',')]
                    for code in codes:
                        if code in self.snomed_to_chinese:
                            builtin_diagnoses.append(self.snomed_to_chinese[code])
                        else:
                            builtin_diagnoses.append(f"未知诊断({code})")
                
                builtin_data.append({
                    'record_name': record_name,
                    'age': age,
                    'sex': sex,
                    'builtin_diagnosis_codes': diagnosis if diagnosis else '',
                    'builtin_diagnosis_names': ', '.join(builtin_diagnoses) if builtin_diagnoses else '无诊断'
                })
                
            except Exception as e:
                print(f"❌ 解析{record_name}.hea失败: {e}")
                continue
        
        return pd.DataFrame(builtin_data)
    
    def load_v4_results(self, v4_results_file):
        """加载V4.0诊断结果"""
        try:
            df = pd.read_csv(v4_results_file)
            print(f"📊 加载V4.0诊断结果: {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"❌ 加载V4.0结果失败: {e}")
            return None
    
    def convert_algorithm_diagnosis(self, diagnosis_codes):
        """转换算法诊断代码为中文名称"""
        if not diagnosis_codes or pd.isna(diagnosis_codes):
            return '无诊断'
        
        diagnoses = []
        codes = [code.strip() for code in str(diagnosis_codes).split(',')]
        
        for code in codes:
            if code in self.snomed_to_chinese:
                diagnoses.append(self.snomed_to_chinese[code])
            else:
                diagnoses.append(f"未知({code})")
        
        return ', '.join(diagnoses)
    
    def calculate_similarity(self, builtin_str, algorithm_str):
        """计算诊断相似性"""
        if not builtin_str or not algorithm_str or builtin_str == '无诊断' or algorithm_str == '无诊断':
            return {
                'exact_match': False,
                'partial_match': 0,
                'jaccard': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0,
                'match_details': '无有效诊断对比'
            }
        
        # 分词处理
        builtin_set = set([d.strip() for d in builtin_str.split(',')])
        algorithm_set = set([d.strip() for d in algorithm_str.split(',')])
        
        # 计算交集
        intersection = builtin_set & algorithm_set
        union = builtin_set | algorithm_set
        
        # 计算指标
        exact_match = builtin_set == algorithm_set
        partial_match = len(intersection)
        
        jaccard = len(intersection) / len(union) if len(union) > 0 else 0.0
        precision = len(intersection) / len(algorithm_set) if len(algorithm_set) > 0 else 0.0
        recall = len(intersection) / len(builtin_set) if len(builtin_set) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # 匹配详情
        if exact_match:
            match_details = '完全匹配'
        elif partial_match > 0:
            matched = list(intersection)
            match_details = f'部分匹配: {", ".join(matched)}'
        else:
            match_details = '无匹配'
        
        return {
            'exact_match': exact_match,
            'partial_match': partial_match,
            'jaccard': jaccard,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'match_details': match_details
        }
    
    def generate_comparison_table(self, data_dir, v4_results_file, output_file):
        """生成完整对比表格"""
        print("🔍 生成V4.0诊断与内置诊断对比表格")
        print("=" * 60)
        
        # 加载数据
        builtin_df = self.load_builtin_diagnoses(data_dir)
        v4_df = self.load_v4_results(v4_results_file)
        
        if builtin_df is None or v4_df is None:
            print("❌ 数据加载失败")
            return None
        
        # 合并数据
        merged_df = pd.merge(builtin_df, v4_df, on='record_name', how='inner')
        print(f"📊 成功匹配 {len(merged_df)} 条记录")
        
        # 生成对比结果
        comparison_results = []
        
        for _, row in merged_df.iterrows():
            # 转换算法诊断
            algorithm_diagnosis_names = self.convert_algorithm_diagnosis(row['algorithm_diagnosis'])
            
            # 计算相似性
            similarity = self.calculate_similarity(
                row['builtin_diagnosis_names'], 
                algorithm_diagnosis_names
            )
            
            # 创建对比记录
            result = {
                'record_name': row['record_name'],
                'age': row['age'],
                'sex': row['sex'],
                'builtin_diagnosis': row['builtin_diagnosis_names'],
                'builtin_codes': row['builtin_diagnosis_codes'],
                'v4_algorithm_diagnosis': algorithm_diagnosis_names,
                'v4_algorithm_codes': row['algorithm_diagnosis'],
                'v4_confidence': row.get('diagnosis_confidence', 0.0),
                'v4_features_total': row.get('features_used_total', 0),
                'v4_features_morphology': row.get('features_used_morphology', 0),
                **similarity
            }
            
            comparison_results.append(result)
        
        # 创建结果DataFrame
        results_df = pd.DataFrame(comparison_results)
        
        # 保存结果
        results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 生成统计报告
        self.generate_statistics_report(results_df)
        
        print(f"💾 对比表格已保存至: {output_file}")
        return results_df
    
    def generate_statistics_report(self, df):
        """生成统计报告"""
        print(f"\\n" + "=" * 60)
        print("📊 V4.0诊断对比统计报告")
        print("=" * 60)
        
        total_records = len(df)
        exact_matches = df['exact_match'].sum()
        partial_matches = (df['partial_match'] > 0).sum()
        no_matches = total_records - partial_matches
        
        print(f"\\n🎯 总体统计:")
        print(f"   - 总病例数: {total_records}")
        print(f"   - 完全匹配: {exact_matches} 例 ({exact_matches/total_records*100:.1f}%)")
        print(f"   - 部分匹配: {partial_matches - exact_matches} 例 ({(partial_matches - exact_matches)/total_records*100:.1f}%)")
        print(f"   - 无匹配: {no_matches} 例 ({no_matches/total_records*100:.1f}%)")
        print(f"   - 总体有效匹配率: {partial_matches/total_records*100:.1f}%")
        
        print(f"\\n📈 平均性能指标:")
        print(f"   - Jaccard相似度: {df['jaccard'].mean():.3f}")
        print(f"   - 精确率: {df['precision'].mean():.3f}")
        print(f"   - 召回率: {df['recall'].mean():.3f}")
        print(f"   - F1分数: {df['f1'].mean():.3f}")
        
        print(f"\\n🔬 V4.0系统特征:")
        print(f"   - 平均置信度: {df['v4_confidence'].mean():.3f}")
        print(f"   - 平均特征使用数: {df['v4_features_total'].mean():.1f}")
        print(f"   - 平均形态学特征数: {df['v4_features_morphology'].mean():.1f}")
        
        # 诊断分布分析
        print(f"\\n🔍 诊断分布分析:")
        
        # 内置诊断分布
        builtin_diagnoses = []
        for dx_str in df['builtin_diagnosis']:
            if pd.notna(dx_str) and dx_str != '无诊断':
                for dx in dx_str.split(','):
                    builtin_diagnoses.append(dx.strip())
        
        # V4.0诊断分布
        v4_diagnoses = []
        for dx_str in df['v4_algorithm_diagnosis']:
            if pd.notna(dx_str) and dx_str != '无诊断':
                for dx in dx_str.split(','):
                    v4_diagnoses.append(dx.strip())
        
        builtin_counts = Counter(builtin_diagnoses)
        v4_counts = Counter(v4_diagnoses)
        
        print(f"\\n{'诊断类型':<20} {'内置频次':<10} {'V4.0频次':<10} {'差异':<10}")
        print("-" * 50)
        
        all_diagnoses = set(builtin_counts.keys()) | set(v4_counts.keys())
        for diagnosis in sorted(all_diagnoses):
            builtin_count = builtin_counts.get(diagnosis, 0)
            v4_count = v4_counts.get(diagnosis, 0)
            diff = v4_count - builtin_count
            diff_str = f"{diff:+d}" if diff != 0 else "0"
            
            print(f"{diagnosis:<20} {builtin_count:<10} {v4_count:<10} {diff_str:<10}")

def main():
    """主函数"""
    # 文件路径
    data_dir = '/Users/williamsun/Documents/gplus/docs/ECG/ECG_demodata/01/010'
    v4_results_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/v4_diagnosis_results/integrated_algorithm_diagnosis_v4.csv'
    output_file = '/Users/williamsun/Documents/gplus/docs/ECG/report/v4_diagnosis_detailed_comparison.csv'
    
    # 生成对比表格
    comparator = V4DiagnosisComparator()
    results_df = comparator.generate_comparison_table(data_dir, v4_results_file, output_file)
    
    if results_df is not None:
        print(f"\\n✅ V4.0诊断对比表格生成完成!")
        print(f"🔍 详细对比数据已保存至CSV文件")
        
        # 显示前几行示例
        print(f"\\n📋 前10个记录预览:")
        print("=" * 120)
        for i, row in results_df.head(10).iterrows():
            print(f"记录 {row['record_name']} ({row['age']}岁 {row['sex']})")
            print(f"  📋 内置诊断: {row['builtin_diagnosis']}")
            print(f"  🤖 V4.0诊断: {row['v4_algorithm_diagnosis']}")
            print(f"  🎯 匹配情况: {row['match_details']}")
            print(f"  📊 相似度: Jaccard={row['jaccard']:.3f}, 精确率={row['precision']:.3f}, 召回率={row['recall']:.3f}")
            print(f"  🔧 置信度: {row['v4_confidence']:.3f}, 特征数: {row['v4_features_total']}")
            print()
    
    return results_df

if __name__ == '__main__':
    main()