#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版学习引擎 - 生产级智能学习算法
"""
import re
import json
import difflib
from datetime import datetime
from collections import defaultdict, Counter
import numpy as np

class EnhancedLearningEngine:
    """生产级学习引擎"""
    
    def __init__(self, feedback_db_path="feedback_database.json"):
        self.feedback_db_path = feedback_db_path
        self.feedback_data = self.load_feedback_data()
        
        # 医学术语词典
        self.medical_terms = {
            "血糖控制": ["血糖管理", "糖代谢", "血糖调节"],
            "需要调整": ["建议优化", "应当改善", "需要改进"],
            "较高": ["偏高", "升高", "超标"],
            "风险": ["危险", "隐患", "问题"],
            "建议": ["推荐", "应考虑", "可以"],
        }
        
        # 学习参数
        self.learning_weights = {
            "terminology_weight": 0.4,
            "clinical_judgment_weight": 0.3,
            "structure_weight": 0.2,
            "parameter_weight": 0.1
        }
    
    def load_feedback_data(self):
        """加载反馈数据"""
        try:
            with open(self.feedback_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"feedback_records": [], "learning_stats": {}}
    
    def advanced_text_diff(self, original, modified):
        """高级文本差异分析"""
        # 使用SequenceMatcher进行精确差异检测
        matcher = difflib.SequenceMatcher(None, original, modified)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                original_text = original[i1:i2]
                modified_text = modified[j1:j2]
                
                change = {
                    'type': 'replacement',
                    'original': original_text.strip(),
                    'modified': modified_text.strip(),
                    'position': i1,
                    'confidence': self.calculate_change_confidence(original_text, modified_text)
                }
                changes.append(change)
            
            elif tag == 'insert':
                change = {
                    'type': 'addition',
                    'text': modified[j1:j2].strip(),
                    'position': i1,
                    'confidence': 0.8
                }
                changes.append(change)
                
            elif tag == 'delete':
                change = {
                    'type': 'deletion',
                    'text': original[i1:i2].strip(),
                    'position': i1,
                    'confidence': 0.9
                }
                changes.append(change)
        
        return changes
    
    def calculate_change_confidence(self, original, modified):
        """计算修改置信度"""
        # 基于字符相似度和语义相关性
        char_similarity = difflib.SequenceMatcher(None, original, modified).ratio()
        
        # 检查是否为医学术语替换
        medical_term_match = False
        for base_term, alternatives in self.medical_terms.items():
            if base_term in original and any(alt in modified for alt in alternatives):
                medical_term_match = True
                break
        
        confidence = char_similarity * 0.6
        if medical_term_match:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def extract_clinical_patterns(self, changes):
        """提取临床模式"""
        patterns = {
            'risk_assessment_changes': [],
            'treatment_recommendation_changes': [],
            'threshold_adjustments': [],
            'terminology_preferences': {}
        }
        
        for change in changes:
            if change['type'] == 'replacement':
                original = change['original'].lower()
                modified = change['modified'].lower()
                
                # 风险评估模式
                if any(word in original for word in ['风险', '安全', '危险']):
                    patterns['risk_assessment_changes'].append({
                        'original': change['original'],
                        'modified': change['modified'],
                        'confidence': change['confidence']
                    })
                
                # 治疗建议模式
                if any(word in original for word in ['建议', '推荐', '需要', '应当']):
                    patterns['treatment_recommendation_changes'].append({
                        'original': change['original'],
                        'modified': change['modified'],
                        'confidence': change['confidence']
                    })
                
                # 数值阈值调整
                original_numbers = re.findall(r'\d+\.?\d*', change['original'])
                modified_numbers = re.findall(r'\d+\.?\d*', change['modified'])
                if original_numbers and modified_numbers and original_numbers != modified_numbers:
                    patterns['threshold_adjustments'].append({
                        'original_values': original_numbers,
                        'modified_values': modified_numbers,
                        'context': change['original'][:50] + '...',
                        'confidence': change['confidence']
                    })
        
        return patterns
    
    def learn_doctor_preferences(self, doctor_id, changes):
        """学习医生个人偏好"""
        doctor_profile = {
            'terminology_preferences': defaultdict(list),
            'modification_style': 'conservative',  # conservative, moderate, comprehensive
            'clinical_focus': [],  # safety_first, efficacy_focused, patient_centered
            'confidence_threshold': 0.7
        }
        
        # 分析修改风格
        major_changes = sum(1 for c in changes if c.get('confidence', 0) > 0.8)
        total_changes = len(changes)
        
        if total_changes > 0:
            major_ratio = major_changes / total_changes
            if major_ratio > 0.7:
                doctor_profile['modification_style'] = 'comprehensive'
            elif major_ratio > 0.4:
                doctor_profile['modification_style'] = 'moderate'
        
        # 学习用词偏好
        for change in changes:
            if change['type'] == 'replacement' and change['confidence'] > 0.6:
                original = change['original']
                modified = change['modified']
                doctor_profile['terminology_preferences'][original].append(modified)
        
        return doctor_profile
    
    def generate_adaptive_suggestions(self, base_report, doctor_id=None):
        """基于学习生成自适应建议"""
        records = self.feedback_data.get('feedback_records', [])
        
        if not records:
            return base_report  # 无学习数据，返回原报告
        
        adapted_report = base_report
        
        # 应用全局学习模式
        global_patterns = self.extract_global_patterns(records)
        adapted_report = self.apply_global_patterns(adapted_report, global_patterns)
        
        # 应用医生个人偏好（如果指定）
        if doctor_id:
            doctor_patterns = self.extract_doctor_patterns(records, doctor_id)
            adapted_report = self.apply_doctor_patterns(adapted_report, doctor_patterns)
        
        return adapted_report
    
    def extract_global_patterns(self, records):
        """提取全局学习模式"""
        global_patterns = {
            'common_replacements': defaultdict(list),
            'frequent_additions': [],
            'common_deletions': []
        }
        
        for record in records:
            original = record.get('original_report', '')
            modified = record.get('modified_report', '')
            
            changes = self.advanced_text_diff(original, modified)
            
            for change in changes:
                if change['type'] == 'replacement' and change['confidence'] > 0.7:
                    global_patterns['common_replacements'][change['original']].append(
                        change['modified']
                    )
        
        return global_patterns
    
    def extract_doctor_patterns(self, records, doctor_id):
        """提取特定医生的模式"""
        doctor_records = [r for r in records if r.get('doctor_id') == doctor_id]
        
        if not doctor_records:
            return {}
        
        patterns = {
            'preferred_terminology': {},
            'modification_tendency': 'moderate'
        }
        
        # 分析该医生的用词偏好
        replacement_freq = defaultdict(list)
        
        for record in doctor_records:
            original = record.get('original_report', '')
            modified = record.get('modified_report', '')
            
            changes = self.advanced_text_diff(original, modified)
            
            for change in changes:
                if change['type'] == 'replacement':
                    replacement_freq[change['original']].append(change['modified'])
        
        # 找出该医生的一致偏好
        for original, modifications in replacement_freq.items():
            if len(modifications) >= 2:  # 至少修改过2次
                most_common = Counter(modifications).most_common(1)[0]
                if most_common[1] >= 2:  # 至少用过2次相同的替换
                    patterns['preferred_terminology'][original] = most_common[0]
        
        return patterns
    
    def apply_global_patterns(self, report, patterns):
        """应用全局学习模式"""
        adapted_report = report
        
        # 应用常见替换
        for original, modifications in patterns['common_replacements'].items():
            if len(modifications) >= 3:  # 至少3个医生做过此修改
                most_common = Counter(modifications).most_common(1)[0]
                if most_common[1] >= 2:  # 至少被用过2次
                    adapted_report = adapted_report.replace(original, most_common[0])
        
        return adapted_report
    
    def apply_doctor_patterns(self, report, patterns):
        """应用医生个人模式"""
        adapted_report = report
        
        # 应用该医生的用词偏好
        for original, preferred in patterns.get('preferred_terminology', {}).items():
            adapted_report = adapted_report.replace(original, preferred)
        
        return adapted_report
    
    def evaluate_learning_effectiveness(self):
        """评估学习效果"""
        records = self.feedback_data.get('feedback_records', [])
        
        if len(records) < 5:
            return {"status": "insufficient_data", "recommendation": "需要更多反馈数据"}
        
        # 计算修改频率趋势
        recent_records = sorted(records, key=lambda x: x['timestamp'])[-10:]
        modification_trend = []
        
        for record in recent_records:
            changes = self.advanced_text_diff(
                record.get('original_report', ''), 
                record.get('modified_report', '')
            )
            modification_trend.append(len(changes))
        
        # 如果最近修改次数在减少，说明学习效果好
        if len(modification_trend) >= 5:
            early_avg = np.mean(modification_trend[:5])
            recent_avg = np.mean(modification_trend[-5:])
            
            improvement_rate = (early_avg - recent_avg) / early_avg if early_avg > 0 else 0
            
            if improvement_rate > 0.2:
                status = "improving"
            elif improvement_rate > 0:
                status = "stable"
            else:
                status = "needs_attention"
        else:
            status = "insufficient_data"
        
        return {
            "status": status,
            "improvement_rate": improvement_rate if 'improvement_rate' in locals() else 0,
            "total_records": len(records),
            "recommendation": self.get_learning_recommendation(status)
        }
    
    def get_learning_recommendation(self, status):
        """获取学习建议"""
        recommendations = {
            "improving": "学习效果良好，继续收集反馈数据",
            "stable": "学习效果稳定，可考虑扩展学习领域",
            "needs_attention": "需要检查学习算法或增加数据质量",
            "insufficient_data": "需要收集更多高质量的反馈数据"
        }
        return recommendations.get(status, "状态未知")
    
    def export_learning_model(self, output_path="learned_model.json"):
        """导出学习模型"""
        records = self.feedback_data.get('feedback_records', [])
        
        model = {
            "version": "1.0",
            "training_data_size": len(records),
            "global_patterns": self.extract_global_patterns(records),
            "doctor_profiles": {},
            "model_effectiveness": self.evaluate_learning_effectiveness(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # 为每个医生生成profile
        doctor_ids = set(r.get('doctor_id', 'unknown') for r in records)
        for doctor_id in doctor_ids:
            if doctor_id != 'unknown':
                model["doctor_profiles"][doctor_id] = self.extract_doctor_patterns(records, doctor_id)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(model, f, ensure_ascii=False, indent=2)
        
        return output_path

def main():
    """测试增强学习引擎"""
    engine = EnhancedLearningEngine()
    
    # 评估当前学习效果
    effectiveness = engine.evaluate_learning_effectiveness()
    print("学习效果评估:", effectiveness)
    
    # 导出学习模型
    model_path = engine.export_learning_model()
    print(f"学习模型已导出到: {model_path}")
    
    # 生成自适应报告示例
    base_report = "血糖控制需要调整，建议强化生活方式管理"
    adapted_report = engine.generate_adaptive_suggestions(base_report, "张医生")
    
    print("\n原始报告:", base_report)
    print("自适应报告:", adapted_report)

if __name__ == "__main__":
    main()