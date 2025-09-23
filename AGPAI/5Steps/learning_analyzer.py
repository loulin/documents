#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习分析器 - 分析医生修改模式，优化AI建议生成
"""
import json
import re
from datetime import datetime
from collections import defaultdict, Counter
import difflib

class LearningAnalyzer:
    """学习分析器 - 分析修改反馈并提取优化建议"""
    
    def __init__(self, feedback_db_path="feedback_database.json"):
        self.feedback_db_path = feedback_db_path
        self.feedback_data = self.load_feedback_data()
        self.learning_insights = {}
    
    def load_feedback_data(self):
        """加载反馈数据"""
        try:
            with open(self.feedback_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"feedback_records": [], "learning_stats": {}}
    
    def analyze_all_feedback(self):
        """分析所有反馈数据"""
        records = self.feedback_data.get("feedback_records", [])
        
        if not records:
            print("没有找到反馈记录")
            return
        
        print(f"开始分析 {len(records)} 条反馈记录...")
        
        # 分析各个维度
        self.learning_insights = {
            "terminology_patterns": self.analyze_terminology_changes(records),
            "content_structure_patterns": self.analyze_structure_changes(records),
            "clinical_judgment_patterns": self.analyze_clinical_modifications(records),
            "doctor_preferences": self.analyze_doctor_preferences(records),
            "parameter_adjustments": self.analyze_parameter_trends(records),
            "summary": self.generate_learning_summary(records)
        }
        
        return self.learning_insights
    
    def analyze_terminology_changes(self, records):
        """分析用词修改模式"""
        print("分析用词修改模式...")
        
        word_replacements = defaultdict(list)
        phrase_replacements = defaultdict(list)
        
        for record in records:
            original = record.get("original_report", "")
            modified = record.get("modified_report", "")
            
            # 使用difflib找出具体的修改
            diff = list(difflib.unified_diff(
                original.split(), modified.split(), lineterm=''
            ))
            
            # 提取替换词汇
            for i, line in enumerate(diff):
                if line.startswith('-') and i+1 < len(diff) and diff[i+1].startswith('+'):
                    original_word = line[1:].strip()
                    modified_word = diff[i+1][1:].strip()
                    if original_word != modified_word:
                        word_replacements[original_word].append(modified_word)
        
        # 统计最常见的替换
        common_replacements = {}
        for original, replacements in word_replacements.items():
            if len(replacements) > 1:  # 至少被替换过2次
                most_common = Counter(replacements).most_common(1)[0]
                common_replacements[original] = {
                    "preferred_replacement": most_common[0],
                    "frequency": most_common[1],
                    "total_occurrences": len(replacements)
                }
        
        return {
            "common_replacements": common_replacements,
            "replacement_patterns": dict(word_replacements)
        }
    
    def analyze_structure_changes(self, records):
        """分析结构修改模式"""
        print("分析报告结构修改模式...")
        
        structure_patterns = {
            "section_additions": [],
            "section_removals": [],
            "reordering_patterns": [],
            "formatting_preferences": []
        }
        
        for record in records:
            original = record.get("original_report", "")
            modified = record.get("modified_report", "")
            
            # 分析标题结构
            original_headers = re.findall(r'<h[1-6]>(.*?)</h[1-6]>', original)
            modified_headers = re.findall(r'<h[1-6]>(.*?)</h[1-6]>', modified)
            
            # 检测新增或删除的章节
            added_sections = set(modified_headers) - set(original_headers)
            removed_sections = set(original_headers) - set(modified_headers)
            
            if added_sections:
                structure_patterns["section_additions"].extend(list(added_sections))
            if removed_sections:
                structure_patterns["section_removals"].extend(list(removed_sections))
        
        return structure_patterns
    
    def analyze_clinical_modifications(self, records):
        """分析临床判断修改模式"""
        print("分析临床判断修改模式...")
        
        clinical_patterns = {
            "risk_assessment_adjustments": [],
            "recommendation_modifications": [],
            "threshold_adjustments": [],
            "safety_emphasis_patterns": []
        }
        
        # 关键词匹配模式
        risk_keywords = ["风险", "安全", "低血糖", "高血糖", "TBR", "TAR"]
        recommendation_keywords = ["建议", "推荐", "应当", "需要", "调整"]
        threshold_keywords = ["阈值", "标准", "目标", "70%", "80%", "4%"]
        
        for record in records:
            original = record.get("original_report", "")
            modified = record.get("modified_report", "")
            
            # 检查风险评估修改
            for keyword in risk_keywords:
                if keyword in original and keyword in modified:
                    original_context = self.extract_context(original, keyword)
                    modified_context = self.extract_context(modified, keyword)
                    if original_context != modified_context:
                        clinical_patterns["risk_assessment_adjustments"].append({
                            "keyword": keyword,
                            "original": original_context,
                            "modified": modified_context,
                            "doctor_id": record.get("doctor_id", "unknown")
                        })
        
        return clinical_patterns
    
    def analyze_doctor_preferences(self, records):
        """分析不同医生的偏好模式"""
        print("分析医生个人偏好...")
        
        doctor_patterns = defaultdict(lambda: {
            "modification_frequency": 0,
            "preferred_terminology": defaultdict(list),
            "common_additions": [],
            "modification_style": "unknown"
        })
        
        for record in records:
            doctor_id = record.get("doctor_id", "unknown")
            doctor_patterns[doctor_id]["modification_frequency"] += 1
            
            # 分析修改风格
            change_summary = record.get("change_summary", {})
            mod_type = change_summary.get("modification_type", "unknown")
            if mod_type in ["major_revision", "moderate_edit"]:
                doctor_patterns[doctor_id]["modification_style"] = "detailed"
            elif mod_type == "minor_edit":
                doctor_patterns[doctor_id]["modification_style"] = "conservative"
        
        return dict(doctor_patterns)
    
    def analyze_parameter_trends(self, records):
        """分析参数调整趋势"""
        print("分析参数调整趋势...")
        
        parameter_trends = {
            "tir_threshold_adjustments": [],
            "risk_weight_changes": [],
            "assessment_criteria_modifications": []
        }
        
        # 这里可以实现更复杂的数值参数分析
        # 目前先做基础的文本分析
        
        for record in records:
            original = record.get("original_report", "")
            modified = record.get("modified_report", "")
            
            # 提取数值变化
            original_numbers = re.findall(r'\d+\.?\d*%?', original)
            modified_numbers = re.findall(r'\d+\.?\d*%?', modified)
            
            if len(original_numbers) != len(modified_numbers):
                parameter_trends["assessment_criteria_modifications"].append({
                    "original_count": len(original_numbers),
                    "modified_count": len(modified_numbers),
                    "doctor_id": record.get("doctor_id", "unknown")
                })
        
        return parameter_trends
    
    def generate_learning_summary(self, records):
        """生成学习总结"""
        total_records = len(records)
        
        # 统计修改类型分布
        modification_types = defaultdict(int)
        for record in records:
            mod_type = record.get("change_summary", {}).get("modification_type", "unknown")
            modification_types[mod_type] += 1
        
        # 找出最活跃的医生
        doctor_activity = defaultdict(int)
        for record in records:
            doctor_id = record.get("doctor_id", "unknown")
            doctor_activity[doctor_id] += 1
        
        most_active_doctor = max(doctor_activity.items(), key=lambda x: x[1]) if doctor_activity else ("none", 0)
        
        return {
            "total_records_analyzed": total_records,
            "modification_type_distribution": dict(modification_types),
            "most_active_doctor": most_active_doctor[0],
            "most_active_doctor_count": most_active_doctor[1],
            "analysis_timestamp": datetime.now().isoformat(),
            "learning_recommendations": self.generate_optimization_recommendations()
        }
    
    def generate_optimization_recommendations(self):
        """生成优化建议"""
        if not self.learning_insights:
            return ["请先运行analyze_all_feedback()方法"]
        
        recommendations = []
        
        # 基于常见替换词汇的建议
        terminology = self.learning_insights.get("terminology_patterns", {})
        common_replacements = terminology.get("common_replacements", {})
        
        if common_replacements:
            recommendations.append(
                f"发现{len(common_replacements)}个常见用词替换模式，建议更新默认词汇表"
            )
        
        # 基于结构修改的建议
        structure = self.learning_insights.get("content_structure_patterns", {})
        if structure.get("section_additions"):
            recommendations.append("医生经常添加新章节，建议扩充报告模板")
        
        # 基于医生偏好的建议
        doctor_prefs = self.learning_insights.get("doctor_preferences", {})
        if len(doctor_prefs) > 1:
            recommendations.append("检测到多位医生的不同偏好，建议实现个性化配置")
        
        if not recommendations:
            recommendations.append("暂未发现明显的优化模式，建议收集更多反馈数据")
        
        return recommendations
    
    def extract_context(self, text, keyword, window=50):
        """提取关键词周围的上下文"""
        pos = text.find(keyword)
        if pos == -1:
            return ""
        
        start = max(0, pos - window)
        end = min(len(text), pos + len(keyword) + window)
        
        return text[start:end]
    
    def export_learning_report(self, output_path="learning_analysis_report.json"):
        """导出学习分析报告"""
        if not self.learning_insights:
            self.analyze_all_feedback()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.learning_insights, f, ensure_ascii=False, indent=2)
        
        print(f"学习分析报告已导出到: {output_path}")
        return output_path
    
    def print_summary(self):
        """打印学习总结"""
        if not self.learning_insights:
            self.analyze_all_feedback()
        
        summary = self.learning_insights.get("summary", {})
        
        print("\n" + "="*60)
        print("📊 五步法Plus 学习分析总结")
        print("="*60)
        print(f"📈 分析记录总数: {summary.get('total_records_analyzed', 0)}")
        print(f"👨‍⚕️ 最活跃医生: {summary.get('most_active_doctor', 'unknown')} ({summary.get('most_active_doctor_count', 0)} 次修改)")
        print(f"🕐 分析时间: {summary.get('analysis_timestamp', 'unknown')}")
        
        print("\n📋 修改类型分布:")
        mod_dist = summary.get('modification_type_distribution', {})
        for mod_type, count in mod_dist.items():
            print(f"  • {mod_type}: {count} 次")
        
        print("\n💡 优化建议:")
        recommendations = summary.get('learning_recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("="*60)


def main():
    """主程序"""
    analyzer = LearningAnalyzer()
    
    # 分析所有反馈
    analyzer.analyze_all_feedback()
    
    # 打印总结
    analyzer.print_summary()
    
    # 导出详细报告
    analyzer.export_learning_report()


if __name__ == "__main__":
    main()