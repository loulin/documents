#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared data models for CGM + nutrition integration workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


@dataclass
class MedicationEntry:
    """Single medication record."""

    name: str
    dosage: str
    frequency: str
    start_date: Optional[date] = None
    purpose: Optional[str] = None
    compliance: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class MedicationPlan:
    """Collection of medications a patient is currently using."""

    entries: List[MedicationEntry] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "medications": [
                {
                    "name": entry.name,
                    "dosage": entry.dosage,
                    "frequency": entry.frequency,
                    "start_date": entry.start_date.isoformat() if entry.start_date else None,
                    "purpose": entry.purpose,
                    "compliance": entry.compliance,
                    "notes": entry.notes,
                }
                for entry in self.entries
            ]
        }


@dataclass
class DietQuestionnaire:
    """Structured dietary questionnaire answers."""

    preferred_cuisines: List[str] = field(default_factory=list)
    disliked_foods: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    spice_tolerance: str = "中等"
    carbohydrate_tolerance: str = "中等"
    snacking_frequency: str = "适中"
    meal_regulariy: str = "规律"
    hydration: str = "适中"
    notes: Optional[str] = None


@dataclass
class CGMMetricSnapshot:
    """Compact CGM metrics required for downstream nutrition reasoning."""

    mean_glucose: float
    gmi: float
    tir: float
    tar: float
    tbr: float
    cv: float
    mage: Optional[float] = None
    auc_day: Optional[float] = None
    auc_night: Optional[float] = None
    lbgi: Optional[float] = None
    hbgi: Optional[float] = None
    risk_tags: List[str] = field(default_factory=list)
    monitoring_days: Optional[int] = None


@dataclass
class CGMInsights:
    """Full CGM analysis structured for integration."""

    summary: CGMMetricSnapshot
    patterns: Dict
    period_analysis: Dict
    weekday_weekend: Dict
    medication_analysis: Dict
    text_assessment: str
    html_report_path: Optional[str] = None


@dataclass
class IntegratedPatientContext:
    """Aggregates all inputs needed for the combined pipeline."""

    patient_profile: "PatientProfile"
    medications: MedicationPlan
    questionnaire: DietQuestionnaire
    cgm_file: str
    patient_id: str


@dataclass
class IntegratedRecommendation:
    """Final combined output delivered to clinicians/patients."""

    cgm_summary: CGMInsights
    nutrition_report: str
    nutrition_targets: Dict
    meal_plan: Dict[str, List[str]]
    recipe_recommendations: Dict
    guidance_notes: List[str]
    medication_plan: MedicationPlan
    questionnaire: DietQuestionnaire
