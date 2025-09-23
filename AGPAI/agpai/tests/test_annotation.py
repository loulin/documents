#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGP智能标注系统单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agpai.core.annotation_engine import AnnotationEngine, AGPAnnotationError
from agpai.config.config_manager import ConfigManager

class TestAnnotationEngine(unittest.TestCase):
    """测试标注引擎"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = AnnotationEngine()
        
        # 创建测试数据
        dates = pd.date_range(
            start='2025-08-16 00:00:00',
            end='2025-08-16 23:59:00',
            freq='5min'
        )
        
        glucose_values = np.random.normal(7.0, 1.5, len(dates))
        self.test_data = pd.DataFrame({
            'timestamp': dates,
            'glucose': glucose_values
        })
    
    def test_data_validation(self):
        """测试数据验证"""
        # 测试正常数据
        self.assertTrue(self.engine._validate_input_data(self.test_data))
        
        # 测试缺少必要列
        invalid_data = self.test_data.drop(columns=['glucose'])
        with self.assertRaises(AGPAnnotationError):
            self.engine._validate_input_data(invalid_data)
        
        # 测试数据量不足
        insufficient_data = self.test_data.iloc[:10]
        with self.assertRaises(AGPAnnotationError):
            self.engine._validate_input_data(insufficient_data)
    
    def test_pattern_detection(self):
        """测试模式检测"""
        annotations = self.engine.detect_patterns(self.test_data)
        self.assertIsInstance(annotations, list)
    
    def test_hypoglycemia_detection(self):
        """测试低血糖检测"""
        # 创建包含低血糖的测试数据
        self.test_data.loc[0:5, 'glucose'] = 3.0
        events = self.engine._detect_hypoglycemia(self.test_data)
        self.assertTrue(len(events) > 0)
    
    def test_hyperglycemia_detection(self):
        """测试高血糖检测"""
        # 创建包含高血糖的测试数据
        self.test_data.loc[0:5, 'glucose'] = 15.0
        events = self.engine._detect_hyperglycemia(self.test_data)
        self.assertTrue(len(events) > 0)
    
    def test_dawn_phenomenon_detection(self):
        """测试黎明现象检测"""
        # 创建模拟黎明现象的数据
        morning_indices = self.test_data[
            (self.test_data['timestamp'].dt.hour >= 4) & 
            (self.test_data['timestamp'].dt.hour <= 8)
        ].index
        self.test_data.loc[morning_indices, 'glucose'] = \
            np.linspace(5.0, 9.0, len(morning_indices))
        
        dawn_effect = self.engine._detect_dawn_phenomenon(self.test_data)
        self.assertIsNotNone(dawn_effect)

class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.config = ConfigManager()
    
    def test_default_thresholds(self):
        """测试默认阈值"""
        thresholds = self.config.get_thresholds()
        self.assertIn('hypoglycemia', thresholds)
        self.assertIn('hyperglycemia', thresholds)
    
    def test_pregnancy_thresholds(self):
        """测试孕期阈值"""
        thresholds = self.config.get_thresholds('pregnancy')
        self.assertIn('target_upper', thresholds)
        self.assertEqual(thresholds['target_upper'], 7.8)
    
    def test_styles(self):
        """测试样式配置"""
        styles = self.config.get_styles()
        self.assertIn('high_priority', styles)
        self.assertIn('color', styles['high_priority'])

if __name__ == '__main__':
    unittest.main()
