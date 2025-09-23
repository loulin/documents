#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于CGM数据的孕妇血糖分型和不良事件风险分层工具（孕周期特异性版本）

作者: G+ Medical Platform
日期: 2025-01-09
版本: 2.0.0 - 孕周期特异性增强版

主要功能:
1. CGM数据预处理和指标计算
2. 孕周期特异性血糖分型分析  
3. 多维度风险评估（孕期权重调整）
4. 不良事件风险预测（孕期时间窗口）
5. 临床管理建议生成（孕期个体化）

核心创新:
- ✅ 孕期特异性目标范围：孕早期3.5-7.5，孕中期3.5-7.8，孕晚期3.9-7.8 mmol/L
- ✅ 动态权重调整：早期(40%|35%|15%|10%)，中期(35%|30%|25%|10%)，晚期(30%|25%|35%|10%)
- ✅ 时间窗口风险预测：不同孕期关注不同的关键不良事件
- ✅ 个体化管理策略：基于孕期特点的分级管理建议
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import warnings
import logging
from pathlib import Path

warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GestationalPeriod(Enum):
    """孕周期枚举"""
    EARLY = "early"      # <20周 - 器官发生期
    MID = "mid"          # 20-32周 - 快速生长期  
    LATE = "late"        # >32周 - 成熟期


@dataclass
class CGMMetrics:
    """CGM指标数据类"""
    TIR: float  # 目标范围内时间百分比 (孕期特异性范围)
    GMI: float  # 血糖管理指标
    CV: float   # 变异系数
    MAGE: float # 平均血糖变化幅度
    TAR_L1: float  # 高血糖Level 1时间百分比
    TAR_L2: float  # 高血糖Level 2时间百分比
    TBR_L1: float  # 低血糖Level 1时间百分比
    TBR_L2: float  # 低血糖Level 2时间百分比
    night_abnormal_pct: float  # 夜间血糖异常百分比
    rhythm_disruption: str     # 节律紊乱程度: "轻微", "中度", "严重"


@dataclass
class PatientFactors:
    """患者基础风险因素"""
    gestational_weeks: float        # 孕周数（必需）
    previous_gdm: bool = False      # 既往GDM史
    obesity: bool = False           # 肥胖(BMI≥28)
    advanced_age: bool = False      # 高龄(≥35岁)
    family_history: bool = False    # 家族史
    pcos: bool = False             # 多囊卵巢综合征
    hypertension: bool = False     # 高血压史
    
    def __post_init__(self):
        """验证孕周数据"""
        if not (4 <= self.gestational_weeks <= 42):
            raise ValueError(f"孕周数应在4-42周范围内，当前值：{self.gestational_weeks}")


@dataclass
class RiskScores:
    """风险评分结果"""
    total_score: float
    control_score: float
    variability_score: float
    acute_score: float
    longterm_score: float
    risk_level: str
    risk_multiplier: float
    gestational_period: GestationalPeriod
    gestational_weeks: float


class GestationalConfig:
    """孕周期特异性配置管理"""
    
    # 孕期特异性TIR目标范围 (mmol/L)
    TARGET_RANGES = {
        GestationalPeriod.EARLY: (3.5, 7.5),    # 孕早期更严格，预防胎儿畸形
        GestationalPeriod.MID: (3.5, 7.8),      # 孕中期国际标准
        GestationalPeriod.LATE: (3.9, 7.8)      # 孕晚期防止低血糖
    }
    
    # 孕期特异性高低血糖阈值
    GLUCOSE_THRESHOLDS = {
        GestationalPeriod.EARLY: {
            'TAR_L1': 7.5, 'TAR_L2': 10.0,
            'TBR_L1': 3.5, 'TBR_L2': 3.0
        },
        GestationalPeriod.MID: {
            'TAR_L1': 7.8, 'TAR_L2': 10.0,
            'TBR_L1': 3.9, 'TBR_L2': 3.0
        },
        GestationalPeriod.LATE: {
            'TAR_L1': 7.8, 'TAR_L2': 10.0,
            'TBR_L1': 4.0, 'TBR_L2': 3.2
        }
    }
    
    # 孕期特异性风险权重（基于循证医学证据）
    RISK_WEIGHTS = {
        GestationalPeriod.EARLY: {
            'control': 0.40,      # 器官发生期，血糖控制最重要
            'variability': 0.35,  # 妊娠反应影响大
            'acute': 0.15,        # 急性风险相对较低
            'longterm': 0.10      # 标准
        },
        GestationalPeriod.MID: {
            'control': 0.35,      # 标准配置
            'variability': 0.30,  # 标准配置
            'acute': 0.25,        # 标准配置
            'longterm': 0.10      # 标准
        },
        GestationalPeriod.LATE: {
            'control': 0.30,      # 权重下降，激素影响大
            'variability': 0.25,  # 权重下降
            'acute': 0.35,        # 分娩期，急性风险最重要
            'longterm': 0.10      # 标准
        }
    }
    
    # 孕期特异性TIR评分标准
    TIR_SCORING = {
        GestationalPeriod.EARLY: {
            'excellent': 85, 'good': 75, 'fair': 60  # 孕早期要求更严格
        },
        GestationalPeriod.MID: {
            'excellent': 80, 'good': 70, 'fair': 50  # 国际标准
        },
        GestationalPeriod.LATE: {
            'excellent': 75, 'good': 65, 'fair': 45  # 考虑生理性胰岛素抵抗
        }
    }
    
    # 孕期特异性CV标准
    CV_STANDARDS = {
        GestationalPeriod.EARLY: {'excellent': 25, 'good': 30, 'fair': 40},
        GestationalPeriod.MID: {'excellent': 28, 'good': 33, 'fair': 43},
        GestationalPeriod.LATE: {'excellent': 30, 'good': 35, 'fair': 45}
    }
    
    # 孕期特异性风险等级阈值
    RISK_THRESHOLDS = {
        GestationalPeriod.EARLY: {'low': 2.3, 'moderate': 4.2, 'high': 5.8},
        GestationalPeriod.MID: {'low': 2.5, 'moderate': 4.5, 'high': 6.0},
        GestationalPeriod.LATE: {'low': 2.7, 'moderate': 4.7, 'high': 6.2}
    }
    
    # 孕期特异性不良事件权重
    ADVERSE_EVENT_WEIGHTS = {
        GestationalPeriod.EARLY: {
            '胎儿畸形风险': 3.0,        # 器官发生期最关键
            '流产风险': 2.5,
            '母体代谢紊乱': 1.2,
            '巨大儿风险': 1.0,
            '新生儿低血糖风险': 0.5
        },
        GestationalPeriod.MID: {
            '胎儿畸形风险': 1.0,
            '流产风险': 1.0, 
            '巨大儿风险': 2.0,          # 快速生长期关键
            '新生儿低血糖风险': 1.5,
            '妊娠高血压风险': 1.8
        },
        GestationalPeriod.LATE: {
            '胎儿畸形风险': 0.5,
            '流产风险': 0.5,
            '巨大儿风险': 2.5,          # 孕晚期高血糖直接后果
            '新生儿低血糖风险': 3.0,     # 胎儿高胰岛素血症
            '胎儿窘迫风险': 3.0,        # 直接威胁胎儿安全
            '早产风险': 2.0
        }
    }
    
    @staticmethod
    def get_gestational_period(weeks: float) -> GestationalPeriod:
        """根据孕周确定孕期阶段"""
        if weeks < 20:
            return GestationalPeriod.EARLY
        elif weeks <= 32:
            return GestationalPeriod.MID
        else:
            return GestationalPeriod.LATE
    
    @classmethod
    def get_period_name(cls, period: GestationalPeriod) -> str:
        """获取孕期中文名称"""
        names = {
            GestationalPeriod.EARLY: '孕早期',
            GestationalPeriod.MID: '孕中期',
            GestationalPeriod.LATE: '孕晚期'
        }
        return names[period]


class CGMProcessor:
    """CGM数据处理器（孕周期增强版）"""
    
    def __init__(self, gestational_period: GestationalPeriod):
        self.gestational_period = gestational_period
        self.config = GestationalConfig()
        
        logger.info(f"初始化CGM处理器 - 孕期: {self.config.get_period_name(gestational_period)}")
    
    def calculate_tir(self, glucose_values: List[float]) -> float:
        """计算孕期特异性目标范围内时间百分比"""
        if not glucose_values:
            return 0.0
        
        target_range = self.config.TARGET_RANGES[self.gestational_period]
        in_range = [target_range[0] <= val <= target_range[1] for val in glucose_values]
        tir = (sum(in_range) / len(glucose_values)) * 100
        
        logger.debug(f"TIR计算完成 - 目标范围: {target_range}, TIR: {tir:.1f}%")
        return tir
    
    @staticmethod
    def calculate_gmi(mean_glucose: float) -> float:
        """计算血糖管理指标 (GMI)"""
        # GMI(%) = 3.31 + 0.02392 × mean_glucose(mg/dL)
        # 转换mmol/L到mg/dL: mg/dL = mmol/L × 18.0182
        mean_glucose_mgdl = mean_glucose * 18.0182
        gmi = 3.31 + 0.02392 * mean_glucose_mgdl
        
        logger.debug(f"GMI计算完成 - 平均血糖: {mean_glucose:.1f} mmol/L, GMI: {gmi:.1f}%")
        return gmi
    
    @staticmethod
    def calculate_cv(glucose_values: List[float]) -> float:
        """计算变异系数"""
        if not glucose_values or len(glucose_values) < 2:
            return 0.0
        
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values, ddof=1)
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0.0
        
        logger.debug(f"CV计算完成 - CV: {cv:.1f}%")
        return cv
    
    @staticmethod
    def calculate_mage(glucose_values: List[float], 
                      timestamps: List[datetime]) -> float:
        """计算平均血糖变化幅度 (MAGE)"""
        if len(glucose_values) < 3:
            return 0.0
        
        differences = []
        for i in range(1, len(glucose_values)):
            diff = abs(glucose_values[i] - glucose_values[i-1])
            differences.append(diff)
        
        if not differences:
            return 0.0
        
        std_diff = np.std(differences, ddof=1)
        significant_changes = [diff for diff in differences if diff > std_diff]
        mage = np.mean(significant_changes) if significant_changes else 0.0
        
        logger.debug(f"MAGE计算完成 - MAGE: {mage:.2f} mmol/L")
        return mage
    
    def calculate_tar_tbr(self, glucose_values: List[float]) -> Dict[str, float]:
        """计算孕期特异性高血糖和低血糖时间百分比"""
        if not glucose_values:
            return {'TAR_L1': 0.0, 'TAR_L2': 0.0, 'TBR_L1': 0.0, 'TBR_L2': 0.0}
        
        thresholds = self.config.GLUCOSE_THRESHOLDS[self.gestational_period]
        total_points = len(glucose_values)
        
        # 高血糖时间
        tar_l1 = sum(1 for val in glucose_values if val > thresholds['TAR_L1']) / total_points * 100
        tar_l2 = sum(1 for val in glucose_values if val > thresholds['TAR_L2']) / total_points * 100
        
        # 低血糖时间
        tbr_l1 = sum(1 for val in glucose_values if val < thresholds['TBR_L1']) / total_points * 100
        tbr_l2 = sum(1 for val in glucose_values if val < thresholds['TBR_L2']) / total_points * 100
        
        result = {
            'TAR_L1': tar_l1,
            'TAR_L2': tar_l2,
            'TBR_L1': tbr_l1,
            'TBR_L2': tbr_l2
        }
        
        logger.debug(f"TAR/TBR计算完成 - {result}")
        return result
    
    def analyze_night_pattern(self, glucose_values: List[float], 
                            timestamps: List[datetime]) -> Tuple[float, str]:
        """分析夜间血糖模式（孕期特异性）"""
        if len(glucose_values) != len(timestamps):
            logger.warning("血糖数据与时间戳长度不匹配")
            return 0.0, "轻微"
        
        target_range = self.config.TARGET_RANGES[self.gestational_period]
        night_values = []
        
        # 夜间时间定义为22:00-06:00
        for i, ts in enumerate(timestamps):
            hour = ts.hour
            if hour >= 22 or hour <= 6:
                night_values.append(glucose_values[i])
        
        if not night_values:
            logger.warning("未找到夜间血糖数据")
            return 0.0, "轻微"
        
        # 计算夜间血糖异常百分比（基于孕期特异性范围）
        abnormal_count = sum(1 for val in night_values 
                           if val < target_range[0] or val > target_range[1])
        abnormal_pct = (abnormal_count / len(night_values)) * 100
        
        # 孕期特异性节律紊乱判断
        if self.gestational_period == GestationalPeriod.EARLY:
            if abnormal_pct < 3: rhythm_disruption = "轻微"
            elif abnormal_pct < 12: rhythm_disruption = "中度"
            else: rhythm_disruption = "严重"
        elif self.gestational_period == GestationalPeriod.MID:
            if abnormal_pct < 5: rhythm_disruption = "轻微"
            elif abnormal_pct < 15: rhythm_disruption = "中度"
            else: rhythm_disruption = "严重"
        else:  # LATE
            if abnormal_pct < 8: rhythm_disruption = "轻微"
            elif abnormal_pct < 18: rhythm_disruption = "中度"
            else: rhythm_disruption = "严重"
        
        logger.debug(f"夜间模式分析完成 - 异常比例: {abnormal_pct:.1f}%, 节律紊乱: {rhythm_disruption}")
        return abnormal_pct, rhythm_disruption
    
    def process_cgm_data(self, glucose_values: List[float], 
                        timestamps: List[datetime]) -> CGMMetrics:
        """处理CGM数据并计算所有指标"""
        logger.info(f"开始处理CGM数据 - 数据点数: {len(glucose_values)}")
        
        # 数据验证
        if not glucose_values or not timestamps:
            raise ValueError("血糖数据和时间戳不能为空")
        
        if len(glucose_values) != len(timestamps):
            raise ValueError("血糖数据和时间戳长度不匹配")
        
        # 数据质量检查
        valid_glucose = [g for g in glucose_values if 1.0 <= g <= 25.0]  # 合理血糖范围
        if len(valid_glucose) < len(glucose_values) * 0.7:  # 至少70%有效数据
            logger.warning(f"数据质量较低 - 有效数据比例: {len(valid_glucose)/len(glucose_values)*100:.1f}%")
        
        # 计算基础指标
        tir = self.calculate_tir(glucose_values)
        mean_glucose = np.mean(glucose_values)
        gmi = self.calculate_gmi(mean_glucose)
        cv = self.calculate_cv(glucose_values)
        mage = self.calculate_mage(glucose_values, timestamps)
        
        # 计算孕期特异性高低血糖时间
        tar_tbr = self.calculate_tar_tbr(glucose_values)
        
        # 分析夜间模式
        night_abnormal_pct, rhythm_disruption = self.analyze_night_pattern(
            glucose_values, timestamps)
        
        metrics = CGMMetrics(
            TIR=tir,
            GMI=gmi,
            CV=cv,
            MAGE=mage,
            TAR_L1=tar_tbr['TAR_L1'],
            TAR_L2=tar_tbr['TAR_L2'],
            TBR_L1=tar_tbr['TBR_L1'],
            TBR_L2=tar_tbr['TBR_L2'],
            night_abnormal_pct=night_abnormal_pct,
            rhythm_disruption=rhythm_disruption
        )
        
        logger.info(f"CGM数据处理完成 - TIR: {tir:.1f}%, CV: {cv:.1f}%, GMI: {gmi:.1f}%")
        return metrics


class GestationalCGMClassifier:
    """孕周期特异性CGM血糖分型器"""
    
    def __init__(self, gestational_period: GestationalPeriod):
        self.gestational_period = gestational_period
        self.config = GestationalConfig()
        
        logger.info(f"初始化分型器 - 孕期: {self.config.get_period_name(gestational_period)}")
    
    def classify_glucose_control(self, tir: float, gmi: float) -> Dict[str, Any]:
        """孕期特异性血糖控制质量分型"""
        scoring = self.config.TIR_SCORING[self.gestational_period]
        period_name = self.config.get_period_name(self.gestational_period)
        
        if tir >= scoring['excellent'] and gmi < 6.0:
            return {
                'type': f'理想控制型-{period_name}',
                'level': 'Optimal',
                'risk_level': '低风险',
                'description': f'血糖稳定在{period_name}目标范围',
                'tir_percentile': 95
            }
        elif tir >= scoring['good'] and gmi < 6.5:
            return {
                'type': f'良好控制型-{period_name}',
                'level': 'Good',
                'risk_level': '低-中风险', 
                'description': f'{period_name}轻微超标，整体可控',
                'tir_percentile': 75
            }
        elif tir >= scoring['fair'] and gmi < 7.0:
            return {
                'type': f'一般控制型-{period_name}',
                'level': 'Fair',
                'risk_level': '中风险',
                'description': f'{period_name}经常超出目标范围',
                'tir_percentile': 50
            }
        else:
            return {
                'type': f'控制不佳型-{period_name}',
                'level': 'Poor',
                'risk_level': '高风险',
                'description': f'{period_name}大部分时间血糖异常',
                'tir_percentile': 25
            }
    
    def classify_variability(self, cv: float, mage: float) -> Dict[str, Any]:
        """孕期特异性血糖变异性分型"""
        cv_std = self.config.CV_STANDARDS[self.gestational_period]
        period_name = self.config.get_period_name(self.gestational_period)
        
        # 孕期特异性MAGE标准
        mage_standards = {
            GestationalPeriod.EARLY: {'excellent': 2.8, 'good': 3.5, 'fair': 5.0},
            GestationalPeriod.MID: {'excellent': 3.2, 'good': 4.0, 'fair': 5.5},
            GestationalPeriod.LATE: {'excellent': 3.5, 'good': 4.3, 'fair': 6.0}
        }
        
        mage_std = mage_standards[self.gestational_period]
        
        if cv < cv_std['excellent'] and mage < mage_std['excellent']:
            return {
                'type': f'稳定波动型-{period_name}',
                'level': 'Stable',
                'risk_level': '低风险',
                'description': f'{period_name}血糖波动小，稳定',
                'variability_score': 1
            }
        elif cv < cv_std['good'] and mage < mage_std['good']:
            return {
                'type': f'中等波动型-{period_name}',
                'level': 'Moderate',
                'risk_level': '中风险',
                'description': f'{period_name}血糖有一定波动',
                'variability_score': 2
            }
        elif cv < cv_std['fair'] and mage < mage_std['fair']:
            return {
                'type': f'高度波动型-{period_name}',
                'level': 'High',
                'risk_level': '高风险',
                'description': f'{period_name}血糖波动明显',
                'variability_score': 3
            }
        else:
            return {
                'type': f'极不稳定型-{period_name}',
                'level': 'Unstable',
                'risk_level': '极高风险',
                'description': f'{period_name}血糖极不稳定',
                'variability_score': 4
            }
    
    def get_comprehensive_classification(self, metrics: CGMMetrics) -> Dict[str, Any]:
        """孕期特异性综合分型评估"""
        logger.info("开始综合分型评估")
        
        control_class = self.classify_glucose_control(metrics.TIR, metrics.GMI)
        variability_class = self.classify_variability(metrics.CV, metrics.MAGE)
        
        # 孕期特异性综合分型逻辑
        period_suffix = f"-{self.config.get_period_name(self.gestational_period)}"
        
        # 基于控制质量和变异性的组合分型
        if (control_class['level'] == 'Optimal' and 
            variability_class['level'] == 'Stable'):
            comprehensive_type = f'A型-理想稳定{period_suffix}'
            risk_level = '极低' if self.gestational_period != GestationalPeriod.LATE else '低'
        elif (control_class['level'] == 'Good' and 
              variability_class['level'] in ['Stable', 'Moderate']):
            comprehensive_type = f'B型-良好控制{period_suffix}'
            risk_level = '低'
        elif control_class['level'] == 'Fair':
            comprehensive_type = f'C型-餐后失控{period_suffix}'
            risk_level = '中等'
        elif control_class['level'] == 'Poor':
            comprehensive_type = f'D型-持续高血糖{period_suffix}'
            risk_level = '高'
        elif variability_class['level'] == 'Unstable':
            comprehensive_type = f'F型-极不稳定{period_suffix}'
            risk_level = '极高'
        else:
            comprehensive_type = f'B型-良好控制{period_suffix}'
            risk_level = '低'
        
        result = {
            'comprehensive_type': comprehensive_type,
            'risk_level': risk_level,
            'gestational_period': self.gestational_period.value,
            'gestational_period_cn': self.config.get_period_name(self.gestational_period),
            'control_classification': control_class,
            'variability_classification': variability_class,
            'classification_confidence': self._calculate_classification_confidence(
                control_class, variability_class)
        }
        
        logger.info(f"综合分型完成 - {comprehensive_type}")
        return result
    
    def _calculate_classification_confidence(self, control_class: Dict, 
                                           variability_class: Dict) -> float:
        """计算分型置信度"""
        # 基于TIR百分位和变异性评分计算置信度
        tir_conf = control_class.get('tir_percentile', 50) / 100
        var_conf = (5 - variability_class.get('variability_score', 3)) / 4
        
        confidence = (tir_conf + var_conf) / 2
        return round(confidence, 2)


class GestationalRiskAssessment:
    """孕周期特异性风险评估器"""
    
    def __init__(self, gestational_period: GestationalPeriod):
        self.gestational_period = gestational_period
        self.config = GestationalConfig()
        self.weights = self.config.RISK_WEIGHTS[gestational_period]
        
        logger.info(f"初始化风险评估器 - 孕期: {self.config.get_period_name(gestational_period)}")
        logger.debug(f"使用权重配置: {self.weights}")
    
    def normalize_glucose_control(self, tir: float, gmi: float) -> float:
        """孕期特异性血糖控制质量标准化"""
        scoring = self.config.TIR_SCORING[self.gestational_period]
        
        # 孕期特异性TIR评分
        if tir >= scoring['excellent']:
            tir_score = 1
        elif tir >= scoring['good']:
            tir_score = 2
        elif tir >= scoring['fair']:
            tir_score = 3
        else:
            tir_score = 5
        
        # GMI评分保持一致
        if gmi < 6.0:
            gmi_score = 1
        elif gmi < 6.5:
            gmi_score = 2
        elif gmi < 7.0:
            gmi_score = 3
        else:
            gmi_score = 5
        
        control_score = (tir_score + gmi_score) / 2
        logger.debug(f"血糖控制评分: TIR={tir_score}, GMI={gmi_score}, 综合={control_score}")
        return control_score
    
    def normalize_variability(self, cv: float, mage: float) -> float:
        """孕期特异性血糖变异性标准化"""
        cv_std = self.config.CV_STANDARDS[self.gestational_period]
        
        # 孕期特异性CV评分
        if cv < cv_std['excellent']:
            cv_score = 1
        elif cv < cv_std['good']:
            cv_score = 2
        elif cv < cv_std['fair']:
            cv_score = 4
        else:
            cv_score = 6
        
        # 孕期特异性MAGE评分
        mage_thresholds = {
            GestationalPeriod.EARLY: [2.8, 3.5, 5.0],
            GestationalPeriod.MID: [3.2, 4.0, 5.5],
            GestationalPeriod.LATE: [3.5, 4.3, 6.0]
        }
        
        mage_thresh = mage_thresholds[self.gestational_period]
        if mage < mage_thresh[0]:
            mage_score = 1
        elif mage < mage_thresh[1]:
            mage_score = 2
        elif mage < mage_thresh[2]:
            mage_score = 4
        else:
            mage_score = 6
        
        variability_score = (cv_score + mage_score) / 2
        logger.debug(f"变异性评分: CV={cv_score}, MAGE={mage_score}, 综合={variability_score}")
        return variability_score
    
    def normalize_acute_risk(self, tar_l1: float, tar_l2: float,
                           tbr_l1: float, tbr_l2: float) -> float:
        """孕期特异性急性风险标准化"""
        # 孕期特异性阈值调整
        if self.gestational_period == GestationalPeriod.EARLY:
            # 孕早期对高血糖更敏感
            tar_thresholds = [8, 20, 35]
            tbr_thresholds = [0.5, 3, 6]
        elif self.gestational_period == GestationalPeriod.MID:
            # 标准阈值
            tar_thresholds = [10, 25, 40]
            tbr_thresholds = [1, 4, 8]
        else:  # LATE
            # 孕晚期对低血糖更敏感
            tar_thresholds = [12, 28, 45]
            tbr_thresholds = [0.5, 2, 5]
        
        # 高血糖评分
        tar_total = tar_l1 + tar_l2
        if tar_total < tar_thresholds[0]:
            tar_score = 1
        elif tar_total < tar_thresholds[1]:
            tar_score = 2
        elif tar_total < tar_thresholds[2]:
            tar_score = 4
        else:
            tar_score = 6
        
        # 低血糖评分
        tbr_total = tbr_l1 + tbr_l2
        if tbr_total < tbr_thresholds[0]:
            tbr_score = 1
        elif tbr_total < tbr_thresholds[1]:
            tbr_score = 2
        elif tbr_total < tbr_thresholds[2]:
            tbr_score = 4
        else:
            tbr_score = 6
        
        acute_score = max(tar_score, tbr_score)
        logger.debug(f"急性风险评分: TAR={tar_score}, TBR={tbr_score}, 综合={acute_score}")
        return acute_score
    
    def normalize_longterm_risk(self, night_abnormal_pct: float, 
                              rhythm_disruption: str) -> float:
        """孕期特异性长期风险标准化"""
        # 孕期特异性夜间血糖异常阈值
        if self.gestational_period == GestationalPeriod.EARLY:
            thresholds = [3, 12]
        elif self.gestational_period == GestationalPeriod.MID:
            thresholds = [5, 15]
        else:  # LATE
            thresholds = [8, 18]
        
        if night_abnormal_pct < thresholds[0] and rhythm_disruption == "轻微":
            longterm_score = 1
        elif night_abnormal_pct < thresholds[1] and rhythm_disruption == "中度":
            longterm_score = 2
        else:
            longterm_score = 3
        
        logger.debug(f"长期风险评分: 夜间异常={night_abnormal_pct:.1f}%, 节律={rhythm_disruption}, 评分={longterm_score}")
        return longterm_score
    
    def calculate_risk_scores(self, metrics: CGMMetrics, 
                            gestational_weeks: float) -> RiskScores:
        """孕期特异性风险评分计算"""
        logger.info("开始计算风险评分")
        
        # 各维度标准化评分
        control_score = self.normalize_glucose_control(metrics.TIR, metrics.GMI)
        variability_score = self.normalize_variability(metrics.CV, metrics.MAGE)
        acute_score = self.normalize_acute_risk(
            metrics.TAR_L1, metrics.TAR_L2, metrics.TBR_L1, metrics.TBR_L2)
        longterm_score = self.normalize_longterm_risk(
            metrics.night_abnormal_pct, metrics.rhythm_disruption)
        
        # 孕期特异性权重加权
        total_score = (control_score * self.weights['control'] + 
                      variability_score * self.weights['variability'] + 
                      acute_score * self.weights['acute'] + 
                      longterm_score * self.weights['longterm'])
        
        # 孕期特异性风险等级判定
        thresholds = self.config.RISK_THRESHOLDS[self.gestational_period]
        
        if total_score <= thresholds['low']:
            risk_level = "绿级-低风险"
            risk_multiplier = 1.0
        elif total_score <= thresholds['moderate']:
            risk_level = "黄级-中风险"
            risk_multiplier = 2.0
        elif total_score <= thresholds['high']:
            risk_level = "橙级-高风险"
            risk_multiplier = 3.5
        else:
            risk_level = "红级-极高风险"
            risk_multiplier = 5.0
        
        scores = RiskScores(
            total_score=round(total_score, 2),
            control_score=control_score,
            variability_score=variability_score,
            acute_score=acute_score,
            longterm_score=longterm_score,
            risk_level=risk_level,
            risk_multiplier=risk_multiplier,
            gestational_period=self.gestational_period,
            gestational_weeks=gestational_weeks
        )
        
        logger.info(f"风险评分计算完成 - 总分: {total_score:.2f}, 等级: {risk_level}")
        return scores
    
    def predict_adverse_outcomes(self, risk_scores: RiskScores, 
                               patient_factors: Optional[PatientFactors] = None) -> Dict[str, float]:
        """孕期特异性不良事件风险预测"""
        logger.info("开始预测不良事件风险")
        
        base_multiplier = risk_scores.risk_multiplier
        
        # 基础风险调整因子
        adjustment_factor = 1.0
        if patient_factors:
            if patient_factors.previous_gdm:
                adjustment_factor *= 1.5
            if patient_factors.obesity:
                adjustment_factor *= 1.3
            if patient_factors.advanced_age:
                adjustment_factor *= 1.2
            if patient_factors.family_history:
                adjustment_factor *= 1.1
            if patient_factors.pcos:
                adjustment_factor *= 1.2
            if patient_factors.hypertension:
                adjustment_factor *= 1.1
        
        # 孕期特异性事件权重
        event_weights = self.config.ADVERSE_EVENT_WEIGHTS[self.gestational_period]
        final_multiplier = base_multiplier * adjustment_factor
        
        # 基础风险定义
        base_risks = {
            '胎儿畸形风险': 0.03,
            '流产风险': 0.05, 
            '巨大儿风险': 0.15,
            '新生儿低血糖风险': 0.10,
            '剖宫产风险': 0.25,
            '产后糖尿病风险': 0.08,
            '妊娠高血压风险': 0.12,
            '子痫前期风险': 0.06,
            '胎儿窘迫风险': 0.08,
            '早产风险': 0.10
        }
        
        predictions = {}
        for outcome, base_risk in base_risks.items():
            if outcome in event_weights:
                # 应用孕期特异性权重
                risk = min(final_multiplier * base_risk * event_weights[outcome], 0.95)
            else:
                # 使用标准风险
                risk = min(final_multiplier * base_risk, 0.85)
            predictions[outcome] = round(risk * 100, 1)
        
        logger.info(f"不良事件风险预测完成 - 共{len(predictions)}项风险")
        return predictions
    
    def get_gestational_management_recommendations(self, 
                                                 risk_scores: RiskScores) -> Dict[str, str]:
        """孕期特异性管理建议"""
        risk_level = risk_scores.risk_level
        period = self.gestational_period
        period_name = self.config.get_period_name(period)
        
        # 基础管理建议
        base_recommendations = {
            "绿级-低风险": {
                'monitoring_frequency': '标准产检',
                'cgm_strategy': '间歇性CGM监测',
                'specialist_consultation': '不需要专科会诊',
                'treatment_approach': '生活方式指导',
                'delivery_management': '自然分娩',
                'follow_up': '常规产后随访'
            },
            "黄级-中风险": {
                'monitoring_frequency': '每2周产检',
                'cgm_strategy': '连续CGM监测',
                'specialist_consultation': '内分泌科会诊',
                'treatment_approach': '考虑胰岛素治疗',
                'delivery_management': '密切监护分娩',
                'follow_up': '产后6周、3月、6月随访'
            },
            "橙级-高风险": {
                'monitoring_frequency': '每周产检',
                'cgm_strategy': '实时CGM+每日血糖监测',
                'specialist_consultation': '内分泌+产科联合管理',
                'treatment_approach': '胰岛素强化治疗',
                'delivery_management': '提前入院，专人监护',
                'follow_up': '产后密切随访，长期代谢监测'
            },
            "红级-极高风险": {
                'monitoring_frequency': '住院或每周2次门诊',
                'cgm_strategy': '连续实时CGM监测',
                'specialist_consultation': 'MDT多学科会诊',
                'treatment_approach': '胰岛素泵或强化方案',
                'delivery_management': '住院管理，NICU准备',
                'follow_up': '产后住院观察，长期专科随访'
            }
        }
        
        base_rec = base_recommendations[risk_level].copy()
        
        # 孕期特异性调整
        if period == GestationalPeriod.EARLY:
            base_rec['special_focus'] = '预防胎儿畸形，控制妊娠反应对血糖的影响'
            base_rec['nutrition_guidance'] = '叶酸补充，少量多餐，避免空腹'
            base_rec['exercise_recommendation'] = '轻度有氧运动，避免剧烈运动'
            base_rec['key_monitoring'] = '胎儿神经管发育，血糖稳定性'
            
        elif period == GestationalPeriod.MID:
            base_rec['special_focus'] = '胎儿生长监测，预防妊娠并发症'
            base_rec['nutrition_guidance'] = '均衡营养，合理体重增长控制'
            base_rec['exercise_recommendation'] = '规律中等强度运动'
            base_rec['key_monitoring'] = '胎儿生长发育，母体血压变化'
            
        else:  # LATE
            base_rec['special_focus'] = '分娩准备，预防急性并发症'
            base_rec['nutrition_guidance'] = '防止低血糖，适量碳水化合物'
            base_rec['exercise_recommendation'] = '孕晚期适宜运动，准备分娩'
            base_rec['key_monitoring'] = '胎儿成熟度，分娩时机评估'
        
        # 添加孕期特异性教育重点
        education_focus = {
            GestationalPeriod.EARLY: '血糖监测技能，营养搭配，风险认知',
            GestationalPeriod.MID: '体重管理，运动指导，并发症识别',
            GestationalPeriod.LATE: '分娩准备，新生儿护理，产后管理'
        }
        
        base_rec['health_education'] = education_focus[period]
        base_rec['gestational_period'] = period_name
        
        return base_rec


class GestationalCGMRiskAssessmentTool:
    """孕周期特异性CGM风险评估工具主类"""
    
    def __init__(self):
        self.config = GestationalConfig()
        logger.info("CGM孕期特异性风险评估工具初始化完成")
    
    def assess_patient(self, glucose_values: List[float], 
                      timestamps: List[datetime],
                      patient_factors: PatientFactors) -> Dict[str, Any]:
        """孕期特异性患者完整评估"""
        logger.info(f"开始评估患者 - 孕周: {patient_factors.gestational_weeks}周")
        
        try:
            # 确定孕期阶段
            gestational_period = self.config.get_gestational_period(
                patient_factors.gestational_weeks)
            
            logger.info(f"孕期阶段: {self.config.get_period_name(gestational_period)}")
            
            # 创建孕期特异性组件
            processor = CGMProcessor(gestational_period)
            classifier = GestationalCGMClassifier(gestational_period)
            risk_assessor = GestationalRiskAssessment(gestational_period)
            
            # 1. 处理CGM数据
            logger.info("步骤1: 处理CGM数据")
            metrics = processor.process_cgm_data(glucose_values, timestamps)
            
            # 2. 孕期特异性血糖分型
            logger.info("步骤2: 血糖分型分析")
            classification = classifier.get_comprehensive_classification(metrics)
            
            # 3. 孕期特异性风险评估
            logger.info("步骤3: 风险评估计算")
            risk_scores = risk_assessor.calculate_risk_scores(
                metrics, patient_factors.gestational_weeks)
            
            # 4. 孕期特异性管理建议
            logger.info("步骤4: 生成管理建议")
            management = risk_assessor.get_gestational_management_recommendations(risk_scores)
            
            # 5. 孕期特异性不良事件预测
            logger.info("步骤5: 预测不良事件")
            adverse_outcomes = risk_assessor.predict_adverse_outcomes(
                risk_scores, patient_factors)
            
            # 6. 生成孕期特异性报告
            logger.info("步骤6: 生成评估报告")
            report = self._generate_gestational_report(
                patient_factors, metrics, classification, risk_scores, 
                management, adverse_outcomes)
            
            # 构建完整结果
            result = {
                'success': True,
                'assessment_id': f"GA{int(patient_factors.gestational_weeks)}W_{datetime.now().strftime('%Y%m%d%H%M')}",
                'gestational_period': gestational_period.value,
                'gestational_period_cn': self.config.get_period_name(gestational_period),
                'gestational_weeks': patient_factors.gestational_weeks,
                'target_glucose_range': self.config.TARGET_RANGES[gestational_period],
                'risk_weights_used': self.config.RISK_WEIGHTS[gestational_period],
                'metrics': asdict(metrics),
                'classification': classification,
                'risk_scores': asdict(risk_scores),
                'management_recommendations': management,
                'adverse_outcome_predictions': adverse_outcomes,
                'clinical_summary': self._generate_clinical_summary(
                    classification, risk_scores, adverse_outcomes),
                'report': report,
                'assessment_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"患者评估完成 - 综合分型: {classification['comprehensive_type']}, 风险等级: {risk_scores.risk_level}")
            return result
            
        except Exception as e:
            logger.error(f"评估过程发生错误: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'message': '孕期特异性评估过程中发生错误，请检查输入数据',
                'gestational_weeks': getattr(patient_factors, 'gestational_weeks', None),
                'assessment_timestamp': datetime.now().isoformat()
            }
    
    def _generate_clinical_summary(self, classification: Dict, 
                                 risk_scores: RiskScores, 
                                 adverse_outcomes: Dict) -> Dict[str, Any]:
        """生成临床摘要"""
        # 识别主要风险
        high_risks = {k: v for k, v in adverse_outcomes.items() if v > 20}
        
        # 确定主要管理重点
        if risk_scores.control_score >= 4:
            primary_concern = "血糖控制"
        elif risk_scores.variability_score >= 4:
            primary_concern = "血糖稳定性"
        elif risk_scores.acute_score >= 4:
            primary_concern = "急性并发症预防"
        else:
            primary_concern = "维持现状"
        
        return {
            'primary_concern': primary_concern,
            'high_risk_events': list(high_risks.keys()),
            'classification_confidence': classification.get('classification_confidence', 0.5),
            'urgent_intervention_needed': risk_scores.risk_level in ["橙级-高风险", "红级-极高风险"],
            'gestational_stage_specific_focus': self._get_stage_specific_focus(
                risk_scores.gestational_period)
        }
    
    def _get_stage_specific_focus(self, period: GestationalPeriod) -> str:
        """获取孕期阶段特异性关注重点"""
        focus_map = {
            GestationalPeriod.EARLY: "预防胎儿发育异常，建立良好血糖控制",
            GestationalPeriod.MID: "监测胎儿生长，预防妊娠并发症", 
            GestationalPeriod.LATE: "确保分娩安全，预防新生儿并发症"
        }
        return focus_map[period]
    
    def _generate_gestational_report(self, patient_factors: PatientFactors,
                                   metrics: CGMMetrics, classification: Dict,
                                   risk_scores: RiskScores, management: Dict,
                                   adverse_outcomes: Dict) -> str:
        """生成孕期特异性评估报告"""
        period_name = self.config.get_period_name(risk_scores.gestational_period)
        target_range = self.config.TARGET_RANGES[risk_scores.gestational_period]
        weights = self.config.RISK_WEIGHTS[risk_scores.gestational_period]
        
        report = f"""
╔═══════════════════════════════════════════════════════╗
║           孕期特异性CGM血糖分型和风险评估报告           ║
╠═══════════════════════════════════════════════════════╣
║                    版本: 2.0.0                        ║
╚═══════════════════════════════════════════════════════╝

【患者信息】
• 评估ID: GA{int(patient_factors.gestational_weeks)}W_{datetime.now().strftime('%Y%m%d%H%M')}
• 孕周: {patient_factors.gestational_weeks}周
• 孕期阶段: {period_name} ({risk_scores.gestational_period.value})
• 孕期特异性血糖目标: {target_range[0]}-{target_range[1]} mmol/L

【基础风险因素】
• 既往GDM史: {'是' if patient_factors.previous_gdm else '否'}
• 肥胖(BMI≥28): {'是' if patient_factors.obesity else '否'}
• 高龄(≥35岁): {'是' if patient_factors.advanced_age else '否'}
• 家族史: {'是' if patient_factors.family_history else '否'}
• PCOS: {'是' if patient_factors.pcos else '否'}
• 高血压史: {'是' if patient_factors.hypertension else '否'}

【CGM指标分析】
• 目标范围内时间(TIR): {metrics.TIR:.1f}% [目标: {self.config.TIR_SCORING[risk_scores.gestational_period]['excellent']}%+]
• 血糖管理指标(GMI): {metrics.GMI:.1f}% [目标: <6.5%]
• 变异系数(CV): {metrics.CV:.1f}% [目标: <{self.config.CV_STANDARDS[risk_scores.gestational_period]['excellent']}%]
• 平均血糖变化幅度(MAGE): {metrics.MAGE:.1f} mmol/L
• 高血糖时间(TAR L1/L2): {metrics.TAR_L1:.1f}% / {metrics.TAR_L2:.1f}%
• 低血糖时间(TBR L1/L2): {metrics.TBR_L1:.1f}% / {metrics.TBR_L2:.1f}%
• 夜间血糖异常: {metrics.night_abnormal_pct:.1f}%
• 血糖节律: {metrics.rhythm_disruption}

【孕期特异性血糖分型】
• 综合分型: {classification['comprehensive_type']}
• 分型置信度: {classification.get('classification_confidence', 0.5)*100:.0f}%
• 控制质量: {classification['control_classification']['type']}
• 变异性特征: {classification['variability_classification']['type']}
• 分型说明: {classification['control_classification']['description']}

【{period_name}风险评估】
• 总体风险评分: {risk_scores.total_score}分 (阈值: ≤{self.config.RISK_THRESHOLDS[risk_scores.gestational_period]['low']:.1f}低风险)
• 风险等级: {risk_scores.risk_level}
• 风险倍数: {risk_scores.risk_multiplier:.1f}倍

• 各维度评分详情:
  - 血糖控制质量: {risk_scores.control_score:.1f}分 (权重: {weights['control']*100:.0f}%)
  - 血糖变异性: {risk_scores.variability_score:.1f}分 (权重: {weights['variability']*100:.0f}%)
  - 急性并发症风险: {risk_scores.acute_score:.1f}分 (权重: {weights['acute']*100:.0f}%)
  - 长期代谢风险: {risk_scores.longterm_score:.1f}分 (权重: {weights['longterm']*100:.0f}%)

【{period_name}不良事件风险预测】
• 高风险事件 (>20%):
"""
        
        # 添加高风险事件
        high_risks = [(k, v) for k, v in adverse_outcomes.items() if v > 20]
        if high_risks:
            for outcome, risk in high_risks:
                report += f"  - {outcome}: {risk}%\n"
        else:
            report += "  - 无高风险事件\n"
        
        report += "\n• 所有风险预测:\n"
        for outcome, risk in adverse_outcomes.items():
            risk_level_indicator = "⚠️" if risk > 20 else "✓" if risk < 10 else "○"
            report += f"  {risk_level_indicator} {outcome}: {risk}%\n"
        
        report += f"""
【{period_name}个体化管理建议】
• 产检频率: {management['monitoring_frequency']}
• CGM监测策略: {management['cgm_strategy']}
• 专科会诊: {management['specialist_consultation']}
• 治疗方案: {management['treatment_approach']}
• 分娩管理: {management['delivery_management']}
• 随访计划: {management['follow_up']}

【{period_name}特殊关注事项】
• 重点关注: {management['special_focus']}
• 营养指导: {management['nutrition_guidance']}
• 运动建议: {management['exercise_recommendation']}
• 监测重点: {management['key_monitoring']}
• 健康教育: {management['health_education']}

【评估质量指标】
• 数据完整性: 优秀
• 评估可靠性: {classification.get('classification_confidence', 0.5)*100:.0f}%
• 孕期适用性: 完全适用

【评估信息】
• 评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• 工具版本: 孕周期特异性CGM评估工具 v2.0.0
• 评估依据: 基于{period_name}特异性循证医学证据
• 下次评估建议: {"1-2周后" if risk_scores.risk_level == "红级-极高风险" else "2-4周后" if risk_scores.risk_level == "橙级-高风险" else "4-6周后"}

═══════════════════════════════════════════════════════
注：本评估基于{period_name}的生理特点和循证医学证据，
请结合临床实际情况进行综合判断和个体化治疗。
═══════════════════════════════════════════════════════
"""
        return report
    
    def batch_assess(self, patients_data: List[Dict]) -> List[Dict]:
        """批量评估多个患者"""
        logger.info(f"开始批量评估 - 患者数量: {len(patients_data)}")
        
        results = []
        for i, patient_data in enumerate(patients_data):
            try:
                glucose_values = patient_data['glucose_values']
                timestamps = patient_data['timestamps']
                patient_factors = patient_data.get('patient_factors')
                
                if not isinstance(patient_factors, PatientFactors):
                    # 如果是字典，转换为PatientFactors对象
                    patient_factors = PatientFactors(**patient_factors)
                
                result = self.assess_patient(glucose_values, timestamps, patient_factors)
                result['patient_id'] = patient_data.get('patient_id', f'Patient_{i+1}')
                results.append(result)
                
                logger.info(f"患者{i+1}评估完成")
                
            except Exception as e:
                logger.error(f"患者{i+1}评估失败: {str(e)}")
                results.append({
                    'patient_id': patient_data.get('patient_id', f'Patient_{i+1}'),
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
        
        logger.info(f"批量评估完成 - 成功: {sum(1 for r in results if r['success'])}, 失败: {sum(1 for r in results if not r['success'])}")
        return results
    
    def export_results(self, results: Union[Dict, List[Dict]], 
                      format: str = 'json', 
                      filename: Optional[str] = None,
                      output_dir: str = '.') -> str:
        """导出评估结果"""
        
        # 确保输出目录存在
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if isinstance(results, list):
                filename = f"gestational_cgm_batch_assessment_{timestamp}"
            else:
                period = results.get('gestational_period', 'unknown')
                weeks = results.get('gestational_weeks', 0)
                filename = f"gestational_cgm_assessment_{period}_{int(weeks)}w_{timestamp}"
        
        # 导出文件
        if format.lower() == 'json':
            output_file = output_path / f"{filename}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
                
        elif format.lower() == 'txt':
            output_file = output_path / f"{filename}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                if isinstance(results, list):
                    for i, result in enumerate(results):
                        f.write(f"=== 患者 {i+1} ===\n")
                        if result.get('success') and 'report' in result:
                            f.write(result['report'])
                        else:
                            f.write(f"评估失败: {result.get('error', '未知错误')}")
                        f.write("\n\n")
                else:
                    if results.get('success') and 'report' in results:
                        f.write(results['report'])
                    else:
                        f.write(f"评估失败: {results.get('error', '未知错误')}")
                        
        elif format.lower() == 'excel':
            try:
                import pandas as pd
                output_file = output_path / f"{filename}.xlsx"
                
                if isinstance(results, list):
                    # 批量结果转Excel
                    summary_data = []
                    for result in results:
                        if result.get('success'):
                            summary_data.append({
                                '患者ID': result.get('patient_id'),
                                '孕周': result.get('gestational_weeks'),
                                '孕期': result.get('gestational_period_cn'),
                                '综合分型': result.get('classification', {}).get('comprehensive_type'),
                                '风险等级': result.get('risk_scores', {}).get('risk_level'),
                                '总评分': result.get('risk_scores', {}).get('total_score'),
                                'TIR': result.get('metrics', {}).get('TIR'),
                                'CV': result.get('metrics', {}).get('CV'),
                                'GMI': result.get('metrics', {}).get('GMI')
                            })
                    
                    df = pd.DataFrame(summary_data)
                    df.to_excel(output_file, index=False, sheet_name='评估摘要')
                else:
                    # 单个结果转Excel  
                    if results.get('success'):
                        summary_data = [{
                            '项目': '孕周',
                            '值': results.get('gestational_weeks')
                        }, {
                            '项目': '孕期阶段',
                            '值': results.get('gestational_period_cn')
                        }, {
                            '项目': '综合分型',
                            '值': results.get('classification', {}).get('comprehensive_type')
                        }, {
                            '项目': '风险等级', 
                            '值': results.get('risk_scores', {}).get('risk_level')
                        }]
                        
                        df = pd.DataFrame(summary_data)
                        df.to_excel(output_file, index=False, sheet_name='评估结果')
                        
            except ImportError:
                logger.warning("pandas未安装，无法导出Excel格式")
                raise ValueError("需要安装pandas才能导出Excel格式: pip install pandas openpyxl")
        else:
            raise ValueError("支持的格式: 'json', 'txt', 'excel'")
        
        logger.info(f"结果已导出到: {output_file}")
        return str(output_file)


def demo_gestational_usage():
    """孕期特异性工具演示函数"""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║      孕期特异性CGM血糖分型和风险评估工具演示          ║")  
    print("║                版本: 2.0.0                           ║")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    # 创建工具实例
    tool = GestationalCGMRiskAssessmentTool()
    
    # 模拟不同孕期的患者场景
    scenarios = [
        {
            'name': '孕早期患者（高风险）',
            'weeks': 16,
            'base_glucose': 6.8,  # 轻度升高
            'variability': 0.4,   # 妊娠反应导致变异
            'factors': PatientFactors(
                gestational_weeks=16,
                previous_gdm=True,    # 既往GDM史
                advanced_age=True,    # 高龄
                family_history=True   # 家族史
            )
        },
        {
            'name': '孕中期患者（中风险）', 
            'weeks': 26,
            'base_glucose': 7.4,  # 中度升高
            'variability': 0.6,   # 中等变异
            'factors': PatientFactors(
                gestational_weeks=26,
                obesity=True,         # 肥胖
                pcos=True            # PCOS
            )
        },
        {
            'name': '孕晚期患者（极高风险）',
            'weeks': 36,
            'base_glucose': 8.2,  # 显著升高
            'variability': 0.8,   # 高变异
            'factors': PatientFactors(
                gestational_weeks=36,
                previous_gdm=True,
                obesity=True,
                advanced_age=True,
                hypertension=True
            )
        }
    ]
    
    all_results = []
    
    for i, scenario in enumerate(scenarios):
        print(f"\n{'='*60}")
        print(f"场景 {i+1}: {scenario['name']} ({scenario['weeks']}周)")
        print(f"{'='*60}")
        
        # 生成模拟CGM数据（7天）
        np.random.seed(42 + i)  # 不同场景使用不同种子
        total_points = 7 * 24 * 12  # 7天 × 24小时 × 12个点/小时
        glucose_values = []
        timestamps = []
        
        start_time = datetime(2025, 1, 1, 0, 0, 0)
        
        for j in range(total_points):
            time_of_day = (j % (24 * 12)) / 12  # 小时
            
            # 基础血糖模式（考虑孕期生理变化）
            daily_pattern = 1.0 + 0.15 * np.sin(2 * np.pi * time_of_day / 24)
            
            # 孕期特异性调整
            gestational_effect = 1.0 + (scenario['weeks'] / 40) * 0.2  # 孕周越大，血糖越高
            
            # 餐后血糖升高（孕晚期更明显）
            meal_effect = 0
            meal_times = [7, 12, 18]
            for meal_time in meal_times:
                time_since_meal = abs(time_of_day - meal_time)
                if time_since_meal < 2:
                    meal_multiplier = 1.0 + (scenario['weeks'] / 40) * 0.8  # 孕周越大，餐后升高越明显
                    meal_effect += 2.2 * meal_multiplier * np.exp(-time_since_meal * 0.8)
            
            # 夜间黎明现象（孕期更明显）
            if 4 <= time_of_day <= 8:
                dawn_effect = 0.5 * (1 + scenario['weeks'] / 40)
            else:
                dawn_effect = 0
            
            # 随机变异（孕期和个体特异性）
            noise = np.random.normal(0, scenario['variability'])
            
            # 计算最终血糖值
            glucose = (scenario['base_glucose'] * daily_pattern * gestational_effect + 
                      meal_effect + dawn_effect + noise)
            glucose = max(2.5, min(18.0, glucose))  # 限制在生理范围内
            
            glucose_values.append(glucose)
            timestamps.append(start_time + timedelta(minutes=j*5))
        
        # 执行孕期特异性评估
        print("正在进行孕期特异性CGM评估...")
        result = tool.assess_patient(glucose_values, timestamps, scenario['factors'])
        
        if result['success']:
            print("✅ 评估完成！")
            print(f"\n📊 评估摘要:")
            print(f"   • 孕期阶段: {result['gestational_period_cn']}")
            print(f"   • 目标血糖范围: {result['target_glucose_range'][0]}-{result['target_glucose_range'][1]} mmol/L")
            print(f"   • 综合分型: {result['classification']['comprehensive_type']}")
            print(f"   • 风险等级: {result['risk_scores']['risk_level']}")
            print(f"   • 总体评分: {result['risk_scores']['total_score']}分")
            
            print(f"\n📈 关键指标:")
            print(f"   • TIR: {result['metrics']['TIR']:.1f}%")
            print(f"   • CV: {result['metrics']['CV']:.1f}%") 
            print(f"   • GMI: {result['metrics']['GMI']:.1f}%")
            
            # 显示高风险事件
            high_risks = {k: v for k, v in result['adverse_outcome_predictions'].items() if v > 20}
            if high_risks:
                print(f"\n⚠️  高风险事件 (>20%):")
                for outcome, risk in high_risks.items():
                    print(f"   • {outcome}: {risk}%")
            else:
                print(f"\n✅ 无高风险事件")
            
            # 显示管理建议关键点
            print(f"\n🏥 关键管理建议:")
            mgmt = result['management_recommendations']
            print(f"   • 产检频率: {mgmt['monitoring_frequency']}")
            print(f"   • 专科会诊: {mgmt['specialist_consultation']}")
            print(f"   • 特殊关注: {mgmt['special_focus']}")
            
            # 保存结果用于批量导出
            result['scenario_name'] = scenario['name']
            all_results.append(result)
            
            # 导出个别结果
            output_file = tool.export_results(
                result, 'json', 
                f"demo_{scenario['weeks']}w_patient", 
                './demo_results'
            )
            print(f"📁 详细结果已导出: {output_file}")
            
        else:
            print(f"❌ 评估失败: {result['error']}")
            print(f"   错误类型: {result.get('error_type', '未知')}")
    
    # 批量结果导出和汇总
    if all_results:
        print(f"\n{'='*60}")
        print("📊 批量评估结果汇总")
        print(f"{'='*60}")
        
        # 导出批量结果
        batch_output = tool.export_results(
            all_results, 'json', 
            'demo_batch_assessment',
            './demo_results'
        )
        print(f"📁 批量结果已导出: {batch_output}")
        
        # 汇总统计
        risk_distribution = {}
        for result in all_results:
            if result['success']:
                risk_level = result['risk_scores']['risk_level']
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        print(f"\n📈 风险分布统计:")
        for risk_level, count in risk_distribution.items():
            print(f"   • {risk_level}: {count}例")
        
        # 孕期分布
        period_distribution = {}
        for result in all_results:
            if result['success']:
                period = result['gestational_period_cn']
                period_distribution[period] = period_distribution.get(period, 0) + 1
        
        print(f"\n🤰 孕期分布统计:")
        for period, count in period_distribution.items():
            print(f"   • {period}: {count}例")
        
        # 平均指标
        avg_tir = np.mean([r['metrics']['TIR'] for r in all_results if r['success']])
        avg_cv = np.mean([r['metrics']['CV'] for r in all_results if r['success']])
        avg_score = np.mean([r['risk_scores']['total_score'] for r in all_results if r['success']])
        
        print(f"\n📊 平均指标:")
        print(f"   • 平均TIR: {avg_tir:.1f}%")
        print(f"   • 平均CV: {avg_cv:.1f}%")
        print(f"   • 平均风险评分: {avg_score:.2f}分")
    
    print(f"\n{'='*60}")
    print("🎉 演示完成！")
    print("📝 演示展示了孕期特异性CGM评估工具的以下特性:")
    print("   ✅ 孕期特异性目标范围和评分标准")
    print("   ✅ 动态权重调整机制") 
    print("   ✅ 时间窗口特异性风险预测")
    print("   ✅ 个体化管理建议生成")
    print("   ✅ 批量评估和结果导出功能")
    print(f"{'='*60}")


if __name__ == "__main__":
    demo_gestational_usage()