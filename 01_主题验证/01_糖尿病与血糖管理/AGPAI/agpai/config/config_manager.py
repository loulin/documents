#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
管理AGP智能标注系统的所有配置项
"""

import os
import yaml
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器类"""
    
    DEFAULT_THRESHOLDS = {
        'default': {
            'hypoglycemia': 3.9,
            'target_lower': 3.9,
            'target_upper': 10.0,
            'hyperglycemia': 13.9,
            'severe_hypo': 3.0,
            'severe_hyper': 16.7
        },
        'pregnancy': {
            'target_lower': 3.9,
            'target_upper': 7.8,
            'hypoglycemia': 3.3,
            'hyperglycemia': 10.0,
            'severe_hypo': 3.0,
            'severe_hyper': 14.0
        }
    }
    
    DEFAULT_STYLES = {
        'high_priority': {
            'color': '#FF4444',
            'fontsize': 10,
            'fontweight': 'bold',
            'bbox': {
                'boxstyle': 'round,pad=0.3',
                'facecolor': '#FF4444',
                'alpha': 0.8
            }
        },
        'medium_priority': {
            'color': '#FF8800',
            'fontsize': 9,
            'fontweight': 'normal',
            'bbox': {
                'boxstyle': 'round,pad=0.3',
                'facecolor': '#FF8800',
                'alpha': 0.7
            }
        },
        'low_priority': {
            'color': '#4488FF',
            'fontsize': 8,
            'fontweight': 'normal',
            'bbox': {
                'boxstyle': 'round,pad=0.3',
                'facecolor': '#4488FF',
                'alpha': 0.6
            }
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config_path = config_path
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                'thresholds': self.DEFAULT_THRESHOLDS,
                'styles': self.DEFAULT_STYLES
            }
    
    def get_thresholds(self, patient_type: str = 'default') -> Dict[str, float]:
        """
        获取血糖阈值配置
        
        Args:
            patient_type: 患者类型，如 'default' 或 'pregnancy'
            
        Returns:
            Dict[str, float]: 血糖阈值配置
        """
        return self.config['thresholds'].get(patient_type, 
                                           self.DEFAULT_THRESHOLDS[patient_type])
    
    def get_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        获取标注样式配置
        
        Returns:
            Dict[str, Dict[str, Any]]: 标注样式配置
        """
        return self.config.get('styles', self.DEFAULT_STYLES)
    
    def save_config(self):
        """保存配置到文件"""
        if self.config_path:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True)
                
    def update_thresholds(self, new_thresholds: Dict[str, Dict[str, float]]):
        """
        更新血糖阈值配置
        
        Args:
            new_thresholds: 新的阈值配置
        """
        self.config['thresholds'].update(new_thresholds)
        self.save_config()
    
    def update_styles(self, new_styles: Dict[str, Dict[str, Any]]):
        """
        更新标注样式配置
        
        Args:
            new_styles: 新的样式配置
        """
        self.config['styles'].update(new_styles)
        self.save_config()
