#!/usr/bin/env python3
"""
层级诊断系统 - 解决V4.0诊断层级缺失问题
建立完整的ECG诊断层级关系，提高与专家诊断的匹配率
"""

class HierarchicalDiagnosisSystem:
    """ECG诊断层级系统"""
    
    def __init__(self):
        # 完整的ECG诊断层级树
        self.diagnosis_hierarchy = {
            # 传导系统异常层级
            '束支阻滞': {
                'snomed_code': '426177001',
                'children': ['右束支阻滞', '左束支阻滞', '双束支阻滞'],
                'level': 'general',
                'clinical_significance': 'high'
            },
            '右束支阻滞': {
                'snomed_code': '59118001',
                'parent': '束支阻滞',
                'level': 'specific',
                'clinical_significance': 'moderate'
            },
            '左束支阻滞': {
                'snomed_code': '251146004',
                'parent': '束支阻滞',
                'level': 'specific',
                'clinical_significance': 'high'
            },
            
            # 心律失常层级
            '房性心律失常': {
                'snomed_code': '164889003',
                'children': ['心房颤动', '心房扑动', '房性期前收缩'],
                'level': 'general',
                'clinical_significance': 'high'
            },
            '心房颤动': {
                'snomed_code': '164934002',
                'parent': '房性心律失常',
                'level': 'specific',
                'clinical_significance': 'high'
            },
            
            '室性心律失常': {
                'snomed_code': '164890007',
                'children': ['室性期前收缩', '室性心动过速'],
                'level': 'general',
                'clinical_significance': 'high'
            },
            '室性期前收缩': {
                'snomed_code': '17338001',
                'parent': '室性心律失常',
                'level': 'specific',
                'clinical_significance': 'moderate'
            },
            
            # 窦性心律层级
            '窦性心律': {
                'snomed_code': '426783006',
                'children': ['窦性心动过缓', '窦性心动过速'],
                'level': 'general',
                'clinical_significance': 'low'
            },
            '窦性心动过缓': {
                'snomed_code': '427393009',
                'parent': '窦性心律',
                'level': 'specific',
                'clinical_significance': 'moderate'
            },
            '心动过速': {
                'snomed_code': '426627000',
                'children': ['窦性心动过速', '室上性心动过速'],
                'level': 'general',
                'clinical_significance': 'moderate'
            },
            
            # 形态学异常层级
            '心电图异常': {
                'snomed_code': '164884008',
                'children': ['ST段异常', 'T波异常', 'QRS异常'],
                'level': 'general',
                'clinical_significance': 'low'
            },
            '心肌缺血': {
                'snomed_code': '413444003',
                'parent': 'ST段异常',
                'level': 'specific',
                'clinical_significance': 'high'
            }
        }
    
    def expand_diagnosis_with_hierarchy(self, specific_diagnoses):
        """将具体诊断扩展为包含层级关系的完整诊断"""
        expanded_diagnoses = set(specific_diagnoses)
        
        # 向上扩展：添加父级诊断
        for diagnosis in specific_diagnoses:
            if diagnosis in self.diagnosis_hierarchy:
                parent = self.diagnosis_hierarchy[diagnosis].get('parent')
                if parent:
                    expanded_diagnoses.add(parent)
                    # 继续向上级扩展
                    grandparent = self.diagnosis_hierarchy[parent].get('parent')
                    if grandparent:
                        expanded_diagnoses.add(grandparent)
        
        return list(expanded_diagnoses)
    
    def calculate_hierarchical_similarity(self, expert_diagnoses, algorithm_diagnoses):
        """计算考虑层级关系的相似度"""
        # 扩展两个诊断集合
        expanded_expert = set(self.expand_diagnosis_with_hierarchy(expert_diagnoses))
        expanded_algorithm = set(self.expand_diagnosis_with_hierarchy(algorithm_diagnoses))
        
        # 计算加权相似度
        intersection = expanded_expert & expanded_algorithm
        union = expanded_expert | expanded_algorithm
        
        # 基础Jaccard相似度
        basic_jaccard = len(intersection) / len(union) if union else 0
        
        # 加权计算：精确匹配权重更高
        exact_matches = set(expert_diagnoses) & set(algorithm_diagnoses)
        hierarchical_matches = intersection - exact_matches
        
        exact_weight = 1.0
        hierarchical_weight = 0.5
        
        weighted_score = (
            len(exact_matches) * exact_weight + 
            len(hierarchical_matches) * hierarchical_weight
        ) / len(union) if union else 0
        
        return {
            'basic_jaccard': basic_jaccard,
            'weighted_similarity': weighted_score,
            'exact_matches': list(exact_matches),
            'hierarchical_matches': list(hierarchical_matches)
        }
    
    def prioritize_diagnoses_by_clinical_significance(self, diagnoses):
        """根据临床重要性排序诊断"""
        significance_order = {'high': 3, 'moderate': 2, 'low': 1}
        
        prioritized = []
        for diagnosis in diagnoses:
            if diagnosis in self.diagnosis_hierarchy:
                significance = self.diagnosis_hierarchy[diagnosis].get('clinical_significance', 'low')
                priority = significance_order.get(significance, 1)
                prioritized.append((diagnosis, priority))
        
        # 按优先级排序
        prioritized.sort(key=lambda x: x[1], reverse=True)
        return [diagnosis for diagnosis, _ in prioritized]
    
    def suggest_diagnosis_improvements(self, current_diagnoses, target_diagnoses):
        """建议诊断改进方案"""
        suggestions = []
        
        current_set = set(current_diagnoses)
        target_set = set(target_diagnoses)
        
        # 需要添加的诊断
        missing = target_set - current_set
        for diagnosis in missing:
            if diagnosis in self.diagnosis_hierarchy:
                level = self.diagnosis_hierarchy[diagnosis].get('level', 'unknown')
                suggestions.append({
                    'action': 'add',
                    'diagnosis': diagnosis,
                    'level': level,
                    'reason': f'专家诊断包含但算法未检出'
                })
        
        # 需要移除的诊断
        extra = current_set - target_set
        for diagnosis in extra:
            if diagnosis in self.diagnosis_hierarchy:
                level = self.diagnosis_hierarchy[diagnosis].get('level', 'unknown')
                # 检查是否有层级关系可以保留
                has_hierarchical_match = any(
                    self._is_hierarchically_related(diagnosis, target) 
                    for target in target_set
                )
                if not has_hierarchical_match:
                    suggestions.append({
                        'action': 'remove',
                        'diagnosis': diagnosis,
                        'level': level,
                        'reason': f'算法过度诊断，专家未包含'
                    })
        
        return suggestions
    
    def _is_hierarchically_related(self, diag1, diag2):
        """检查两个诊断是否有层级关系"""
        if diag1 in self.diagnosis_hierarchy and diag2 in self.diagnosis_hierarchy:
            # 检查父子关系
            parent1 = self.diagnosis_hierarchy[diag1].get('parent')
            parent2 = self.diagnosis_hierarchy[diag2].get('parent')
            children1 = self.diagnosis_hierarchy[diag1].get('children', [])
            children2 = self.diagnosis_hierarchy[diag2].get('children', [])
            
            return (
                parent1 == diag2 or parent2 == diag1 or
                diag1 in children2 or diag2 in children1
            )
        return False

def demonstrate_hierarchical_system():
    """演示层级诊断系统"""
    system = HierarchicalDiagnosisSystem()
    
    print("🏗️ ECG诊断层级系统演示")
    print("=" * 50)
    
    # 示例1：层级扩展
    print("\\n📊 示例1: 诊断层级扩展")
    specific_diagnoses = ['右束支阻滞', '心房颤动']
    expanded = system.expand_diagnosis_with_hierarchy(specific_diagnoses)
    print(f"输入诊断: {specific_diagnoses}")
    print(f"层级扩展: {expanded}")
    
    # 示例2：层级相似度计算
    print("\\n📊 示例2: 层级相似度计算")
    expert_diagnoses = ['束支阻滞', '房性心律失常']
    algorithm_diagnoses = ['右束支阻滞', '心房颤动']
    
    similarity = system.calculate_hierarchical_similarity(expert_diagnoses, algorithm_diagnoses)
    print(f"专家诊断: {expert_diagnoses}")
    print(f"算法诊断: {algorithm_diagnoses}")
    print(f"基础Jaccard: {similarity['basic_jaccard']:.3f}")
    print(f"加权相似度: {similarity['weighted_similarity']:.3f}")
    print(f"精确匹配: {similarity['exact_matches']}")
    print(f"层级匹配: {similarity['hierarchical_matches']}")
    
    # 示例3：诊断优先级
    print("\\n📊 示例3: 临床重要性排序")
    mixed_diagnoses = ['心电图异常', '左束支阻滞', '窦性心律', '心房颤动']
    prioritized = system.prioritize_diagnoses_by_clinical_significance(mixed_diagnoses)
    print(f"原始诊断: {mixed_diagnoses}")
    print(f"优先级排序: {prioritized}")
    
    # 示例4：改进建议
    print("\\n📊 示例4: 诊断改进建议")
    current = ['右束支阻滞', '心肌缺血']
    target = ['束支阻滞', '心电图异常'] 
    suggestions = system.suggest_diagnosis_improvements(current, target)
    print(f"当前诊断: {current}")
    print(f"目标诊断: {target}")
    print("改进建议:")
    for suggestion in suggestions:
        print(f"  - {suggestion['action']} {suggestion['diagnosis']} ({suggestion['level']}) - {suggestion['reason']}")

if __name__ == '__main__':
    demonstrate_hierarchical_system()