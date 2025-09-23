#!/usr/bin/env python3
"""
手动切点管理器
支持临床医生手动添加、编辑和管理治疗调整切点
结合临床知识和数据分析，提供更精准的分段脆性评估
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
import json

class ManualCutpointManager:
    """
    手动切点管理器
    支持临床医生根据实际治疗记录添加切点
    """
    
    def __init__(self):
        """初始化手动切点管理器"""
        self.manager_name = "Manual Cutpoint Manager"
        self.version = "1.0.0"
        
        # 支持的切点类型
        self.cutpoint_types = {
            # 手术相关
            'PANCREATIC_SURGERY': {
                'name': '胰腺手术',
                'description': '胰腺切除术、胰十二指肠切除术等',
                'expected_effects': ['血糖升高', '胰岛功能下降', '变异性增加']
            },
            'GALLBLADDER_SURGERY': {
                'name': '胆囊手术', 
                'description': '胆囊切除术等',
                'expected_effects': ['短期血糖波动', '消化功能影响']
            },
            
            # 药物调整
            'INSULIN_INITIATION': {
                'name': '胰岛素启动',
                'description': '首次开始胰岛素治疗',
                'expected_effects': ['血糖下降', '变异性可能增加', '低血糖风险']
            },
            'INSULIN_ADJUSTMENT': {
                'name': '胰岛素调整',
                'description': '胰岛素剂量或方案调整',
                'expected_effects': ['血糖水平变化', '控制质量改善']
            },
            'ORAL_MEDICATION_CHANGE': {
                'name': '口服药物调整',
                'description': '口服降糖药物的更换或调整',
                'expected_effects': ['血糖缓慢变化', '控制稳定性改善']
            },
            'STEROID_TREATMENT': {
                'name': '激素治疗',
                'description': '糖皮质激素等使用',
                'expected_effects': ['血糖显著升高', '变异性增加']
            },
            
            # 营养相关
            'TPN_INITIATION': {
                'name': 'TPN启动',
                'description': '全肠外营养开始',
                'expected_effects': ['血糖升高', '需要胰岛素覆盖']
            },
            'TPN_TO_EN_TRANSITION': {
                'name': 'TPN转EN',
                'description': '全肠外营养转为肠内营养',
                'expected_effects': ['血糖模式变化', '波动性改变']
            },
            'DIET_RESUMPTION': {
                'name': '恢复饮食',
                'description': '术后恢复正常饮食',
                'expected_effects': ['餐后血糖峰值', '昼夜节律恢复']
            },
            
            # 临床事件
            'INFECTION': {
                'name': '感染',
                'description': '术后感染或其他感染',
                'expected_effects': ['血糖升高', '控制困难', '变异性增加']
            },
            'STRESS_RESPONSE': {
                'name': '应激反应',
                'description': '手术、疼痛等应激反应',
                'expected_effects': ['血糖升高', '激素水平变化']
            },
            'DISCHARGE_PREPARATION': {
                'name': '出院准备',
                'description': '出院前药物调整和教育',
                'expected_effects': ['治疗方案简化', '控制目标调整']
            }
        }
    
    def create_manual_cutpoint(self,
                              timestamp: Union[str, pd.Timestamp, datetime],
                              cutpoint_type: str,
                              description: str = "",
                              clinical_details: Optional[Dict] = None,
                              expected_duration_hours: Optional[int] = None) -> Dict:
        """
        创建手动切点
        
        Args:
            timestamp: 切点时间
            cutpoint_type: 切点类型
            description: 具体描述
            clinical_details: 临床细节信息
            expected_duration_hours: 预期影响持续时间
            
        Returns:
            切点信息字典
        """
        # 转换时间格式
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        elif isinstance(timestamp, datetime):
            timestamp = pd.Timestamp(timestamp)
        
        # 验证切点类型
        if cutpoint_type not in self.cutpoint_types:
            raise ValueError(f"不支持的切点类型: {cutpoint_type}. 支持的类型: {list(self.cutpoint_types.keys())}")
        
        cutpoint_info = self.cutpoint_types[cutpoint_type]
        
        manual_cutpoint = {
            'timestamp': timestamp,
            'type': cutpoint_type,
            'type_info': cutpoint_info,
            'description': description or cutpoint_info['description'],
            'method': 'manual',
            'created_by': 'clinical_user',
            'created_at': pd.Timestamp.now(),
            'clinical_details': clinical_details or {},
            'expected_duration_hours': expected_duration_hours,
            'expected_effects': cutpoint_info['expected_effects'],
            'validated': True,  # 手动添加的切点默认已验证
            'confidence': 1.0   # 手动切点置信度最高
        }
        
        return manual_cutpoint
    
    def validate_cutpoint_timing(self,
                                cutpoint: Dict,
                                glucose_data: np.ndarray,
                                timestamps: np.ndarray) -> Dict:
        """
        验证手动切点的时间合理性
        
        Args:
            cutpoint: 切点信息
            glucose_data: 血糖数据
            timestamps: 时间戳数组
            
        Returns:
            验证结果
        """
        cutpoint_time = cutpoint['timestamp']
        
        # 找到最接近的数据点
        cutpoint_time_np = pd.Timestamp(cutpoint_time).value  # 转换为纳秒
        timestamps_np = pd.to_datetime(timestamps).values.astype('datetime64[ns]')
        
        time_diffs = np.abs(timestamps_np.astype('int64') - cutpoint_time_np)
        closest_idx = np.argmin(time_diffs)
        closest_time_diff = time_diffs[closest_idx] / (1e9 * 3600)  # 转换为小时
        
        validation_result = {
            'is_valid': True,
            'closest_index': closest_idx,
            'closest_timestamp': timestamps[closest_idx],
            'time_difference_hours': closest_time_diff,
            'warnings': [],
            'recommendations': []
        }
        
        # 检查时间差
        if closest_time_diff > 6:  # 超过6小时
            validation_result['warnings'].append(f"切点时间与最近数据点相差 {closest_time_diff:.1f} 小时")
            validation_result['recommendations'].append("建议检查切点时间是否正确")
        
        # 检查数据完整性
        window_size = min(50, len(glucose_data) // 10)  # 动态窗口
        start_idx = max(0, closest_idx - window_size)
        end_idx = min(len(glucose_data), closest_idx + window_size)
        
        window_data = glucose_data[start_idx:end_idx]
        if len(window_data) < 20:
            validation_result['warnings'].append("切点附近数据点过少")
            validation_result['recommendations'].append("建议扩大分析时间窗口")
        
        # 分析切点前后的数据变化
        if closest_idx > 20 and closest_idx < len(glucose_data) - 20:
            pre_data = glucose_data[closest_idx-20:closest_idx]
            post_data = glucose_data[closest_idx:closest_idx+20]
            
            pre_mean = np.mean(pre_data)
            post_mean = np.mean(post_data)
            mean_change = post_mean - pre_mean
            
            pre_std = np.std(pre_data)
            post_std = np.std(post_data)
            
            validation_result['data_analysis'] = {
                'pre_mean': pre_mean,
                'post_mean': post_mean,
                'mean_change': mean_change,
                'pre_std': pre_std,
                'post_std': post_std,
                'variance_ratio': post_std / (pre_std + 1e-6)
            }
            
            # 根据切点类型检查预期效应
            cutpoint_type = cutpoint['type']
            expected_effects = cutpoint['expected_effects']
            
            self._validate_expected_effects(validation_result, mean_change, 
                                          post_std/pre_std if pre_std > 0 else 1,
                                          expected_effects)
        
        return validation_result
    
    def _validate_expected_effects(self, validation_result: Dict, 
                                 mean_change: float, variance_ratio: float,
                                 expected_effects: List[str]):
        """验证是否符合预期效应"""
        effect_validations = []
        
        for effect in expected_effects:
            if '血糖升高' in effect:
                if mean_change > 1.0:
                    effect_validations.append(f"✅ {effect}: 检测到升高 {mean_change:.1f} mmol/L")
                elif mean_change < -1.0:
                    effect_validations.append(f"⚠️ {effect}: 实际下降 {abs(mean_change):.1f} mmol/L")
                else:
                    effect_validations.append(f"❓ {effect}: 变化不明显 {mean_change:.1f} mmol/L")
            
            elif '血糖下降' in effect:
                if mean_change < -1.0:
                    effect_validations.append(f"✅ {effect}: 检测到下降 {abs(mean_change):.1f} mmol/L")
                elif mean_change > 1.0:
                    effect_validations.append(f"⚠️ {effect}: 实际升高 {mean_change:.1f} mmol/L")
                else:
                    effect_validations.append(f"❓ {effect}: 变化不明显 {mean_change:.1f} mmol/L")
            
            elif '变异性增加' in effect:
                if variance_ratio > 1.5:
                    effect_validations.append(f"✅ {effect}: 检测到变异性增加 {variance_ratio:.1f}x")
                elif variance_ratio < 0.7:
                    effect_validations.append(f"⚠️ {effect}: 实际变异性降低 {variance_ratio:.1f}x")
                else:
                    effect_validations.append(f"❓ {effect}: 变异性变化不明显 {variance_ratio:.1f}x")
        
        validation_result['effect_validations'] = effect_validations
    
    def merge_cutpoints(self, 
                       manual_cutpoints: List[Dict],
                       detected_cutpoints: List[Dict],
                       merge_strategy: str = 'prioritize_manual') -> List[Dict]:
        """
        合并手动切点和算法检测的切点
        
        Args:
            manual_cutpoints: 手动添加的切点
            detected_cutpoints: 算法检测的切点
            merge_strategy: 合并策略
                - 'prioritize_manual': 优先手动切点
                - 'merge_all': 合并所有切点
                - 'validate_detected': 用手动切点验证检测结果
                
        Returns:
            合并后的切点列表
        """
        merged_cutpoints = []
        
        if merge_strategy == 'prioritize_manual':
            # 首先添加所有手动切点
            merged_cutpoints.extend(manual_cutpoints)
            
            # 添加不与手动切点冲突的检测切点
            for detected in detected_cutpoints:
                detected_time = detected.get('timestamp')
                
                # 检查是否与手动切点太接近
                too_close = False
                for manual in manual_cutpoints:
                    manual_time = manual.get('timestamp')
                    if abs((detected_time - manual_time) / np.timedelta64(1, 'h')) < 12:  # 12小时内
                        too_close = True
                        break
                
                if not too_close:
                    detected['source'] = 'algorithm_detected'
                    merged_cutpoints.append(detected)
        
        elif merge_strategy == 'merge_all':
            # 合并所有切点并排序
            all_cutpoints = manual_cutpoints + detected_cutpoints
            for cutpoint in manual_cutpoints:
                cutpoint['source'] = 'manual'
            for cutpoint in detected_cutpoints:
                cutpoint['source'] = 'algorithm_detected'
            
            merged_cutpoints = sorted(all_cutpoints, 
                                   key=lambda x: x.get('timestamp', pd.Timestamp.min))
        
        elif merge_strategy == 'validate_detected':
            # 使用手动切点验证检测结果
            merged_cutpoints.extend(manual_cutpoints)
            
            for detected in detected_cutpoints:
                detected_time = detected.get('timestamp')
                
                # 寻找最近的手动切点进行验证
                closest_manual = None
                min_time_diff = float('inf')
                
                for manual in manual_cutpoints:
                    manual_time = manual.get('timestamp')
                    time_diff = abs((detected_time - manual_time) / np.timedelta64(1, 'h'))
                    
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_manual = manual
                
                # 如果检测切点与手动切点接近，进行验证
                if closest_manual and min_time_diff < 24:  # 24小时内
                    detected['validation'] = {
                        'closest_manual_cutpoint': closest_manual,
                        'time_difference_hours': min_time_diff,
                        'validated_by_manual': True
                    }
                    detected['source'] = 'algorithm_validated'
                    merged_cutpoints.append(detected)
                elif min_time_diff >= 24:  # 远离手动切点的检测结果
                    detected['source'] = 'algorithm_additional'
                    detected['validation'] = {'validated_by_manual': False}
                    merged_cutpoints.append(detected)
        
        # 按时间排序
        merged_cutpoints = sorted(merged_cutpoints, 
                                key=lambda x: x.get('timestamp', pd.Timestamp.min))
        
        return merged_cutpoints
    
    def create_cutpoint_template(self, patient_info: Dict) -> Dict:
        """
        根据患者信息创建切点模板
        
        Args:
            patient_info: 患者信息
            
        Returns:
            切点模板
        """
        department = patient_info.get('department', '').lower()
        
        templates = {
            'common_cutpoints': [
                {
                    'type': 'INSULIN_INITIATION',
                    'description': '首次胰岛素治疗',
                    'timing_hint': '通常在入院后24-48小时'
                },
                {
                    'type': 'DISCHARGE_PREPARATION', 
                    'description': '出院前药物调整',
                    'timing_hint': '出院前1-2天'
                }
            ]
        }
        
        # 胰腺外科特殊模板
        if '胰腺外科' in patient_info.get('department', '') or 'pancreatic' in department:
            templates['pancreatic_surgery_cutpoints'] = [
                {
                    'type': 'PANCREATIC_SURGERY',
                    'description': '胰腺手术（请指定具体手术类型）',
                    'timing_hint': '手术日期和时间',
                    'expected_duration_hours': 72
                },
                {
                    'type': 'TPN_INITIATION',
                    'description': '术后TPN开始',
                    'timing_hint': '通常在术后6-12小时'
                },
                {
                    'type': 'DIET_RESUMPTION',
                    'description': '恢复饮食',
                    'timing_hint': '术后3-7天，根据恢复情况'
                }
            ]
        
        return templates
    
    def export_cutpoints(self, cutpoints: List[Dict], format: str = 'json') -> str:
        """
        导出切点信息
        
        Args:
            cutpoints: 切点列表
            format: 导出格式 ('json', 'csv', 'timeline')
            
        Returns:
            格式化的切点信息
        """
        if format == 'json':
            # 处理不能序列化的类型
            serializable_cutpoints = []
            for cp in cutpoints:
                serializable_cp = {}
                for key, value in cp.items():
                    if isinstance(value, (pd.Timestamp, np.datetime64)):
                        serializable_cp[key] = str(value)
                    elif isinstance(value, (np.integer, np.floating)):
                        serializable_cp[key] = float(value)
                    else:
                        serializable_cp[key] = value
                serializable_cutpoints.append(serializable_cp)
            
            return json.dumps(serializable_cutpoints, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            # 创建CSV格式
            csv_lines = ['时间,类型,描述,来源,置信度']
            for cp in cutpoints:
                line = f"{cp.get('timestamp', '')},{cp.get('type', '')},{cp.get('description', '')},{cp.get('source', 'manual')},{cp.get('confidence', 1.0)}"
                csv_lines.append(line)
            return '\\n'.join(csv_lines)
        
        elif format == 'timeline':
            # 创建时间线格式
            timeline_lines = ['📅 治疗调整时间线', '=' * 50]
            
            for i, cp in enumerate(cutpoints):
                timestamp = cp.get('timestamp', '')
                type_info = cp.get('type_info', {})
                type_name = type_info.get('name', cp.get('type', ''))
                description = cp.get('description', '')
                source = cp.get('source', 'manual')
                
                timeline_lines.append(f"\\n{i+1}. {timestamp}")
                timeline_lines.append(f"   🏷️  类型: {type_name}")
                timeline_lines.append(f"   📝 描述: {description}")
                timeline_lines.append(f"   🔍 来源: {source}")
                
                # 预期效应
                expected_effects = cp.get('expected_effects', [])
                if expected_effects:
                    timeline_lines.append(f"   📊 预期效应: {', '.join(expected_effects)}")
            
            return '\\n'.join(timeline_lines)
        
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def suggest_cutpoints_from_notes(self, clinical_notes: str) -> List[Dict]:
        """
        从临床记录中建议可能的切点
        
        Args:
            clinical_notes: 临床记录文本
            
        Returns:
            建议的切点列表
        """
        suggestions = []
        notes_lower = clinical_notes.lower()
        
        # 关键词映射
        keyword_mapping = {
            'PANCREATIC_SURGERY': ['胰腺手术', '胰十二指肠切除', '胰体尾切除', 'whipple', 'pancreatic resection'],
            'INSULIN_INITIATION': ['开始胰岛素', '胰岛素治疗', 'insulin initiation', 'start insulin'],
            'TPN_INITIATION': ['开始TPN', '全肠外营养', 'total parenteral nutrition', 'start TPN'],
            'INFECTION': ['感染', '发热', 'infection', 'fever', 'sepsis'],
            'STEROID_TREATMENT': ['激素治疗', '糖皮质激素', 'steroid', 'prednisolone']
        }
        
        for cutpoint_type, keywords in keyword_mapping.items():
            for keyword in keywords:
                if keyword in notes_lower:
                    suggestions.append({
                        'suggested_type': cutpoint_type,
                        'type_info': self.cutpoint_types[cutpoint_type],
                        'matched_keyword': keyword,
                        'context': self._extract_context(clinical_notes, keyword),
                        'confidence': 0.8
                    })
        
        return suggestions
    
    def _extract_context(self, text: str, keyword: str, context_length: int = 50) -> str:
        """提取关键词周围的上下文"""
        text_lower = text.lower()
        keyword_pos = text_lower.find(keyword.lower())
        
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - context_length)
        end = min(len(text), keyword_pos + len(keyword) + context_length)
        
        return text[start:end].strip()