#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-end pipeline that bridges CGM analytics (ZS_HMC) with nutrition
recommendations (FoodRecom).
"""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from integration_models import (
    CGMInsights,
    CGMMetricSnapshot,
    DietQuestionnaire,
    IntegratedPatientContext,
    IntegratedRecommendation,
    MedicationPlan,
)

# Resolve ZS_HMC package path for imports
CURRENT_DIR = Path(__file__).resolve()
ZS_HMC_SRC = CURRENT_DIR.parents[3] / "10_医院机构合作项目" / "ZS_HMC" / "src"
if str(ZS_HMC_SRC) not in sys.path:
    sys.path.insert(0, str(ZS_HMC_SRC))

from zshmc_report.data_utils import load_cgm_data  # noqa: E402
from zshmc_report.generator_v3 import ZSHMCReportGeneratorV3  # noqa: E402

from integrated_nutrition_system_v2 import IntegratedNutritionSystemV2  # noqa: E402


class IntegratedCGMNutritionPipeline:
    """High level orchestrator for CGM + nutrition workflows."""

    def __init__(
        self,
        nutrition_system: Optional[IntegratedNutritionSystemV2] = None,
        report_output_dir: Optional[Path] = None,
    ) -> None:
        self.nutrition_system = nutrition_system or IntegratedNutritionSystemV2()
        self.cgm_generator = ZSHMCReportGeneratorV3()
        self.report_output_dir = (
            report_output_dir
            if report_output_dir is not None
            else CURRENT_DIR.parents[1] / "Reports" / "combined"
        )
        self.report_output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(self, context: IntegratedPatientContext) -> IntegratedRecommendation:
        """Execute the integrated pipeline and return combined outputs."""
        cgm_insights = self._analyze_cgm(context)
        adjusted_assessment, guidance_notes = self._integrate_assessments(
            context, cgm_insights
        )

        nutrition_report = self.nutrition_system.generate_comprehensive_report_v2(
            context.patient_profile,
            include_charts=True,
            assessment_override=adjusted_assessment,
            additional_sections=self._build_additional_section(
                cgm_insights,
                context.medications,
                context.questionnaire,
                adjusted_assessment["recipe_recommendations"],
                guidance_notes,
            ),
        )

        meal_plan = {
            "早餐": adjusted_assessment["recipe_recommendations"].get("早餐推荐", []),
            "午餐": adjusted_assessment["recipe_recommendations"].get("午餐推荐", []),
            "晚餐": adjusted_assessment["recipe_recommendations"].get("晚餐推荐", []),
            "加餐": adjusted_assessment["recipe_recommendations"].get("加餐推荐", []),
        }

        return IntegratedRecommendation(
            cgm_summary=cgm_insights,
            nutrition_report=nutrition_report,
            nutrition_targets=adjusted_assessment["nutrition_targets"],
            meal_plan=meal_plan,
            recipe_recommendations=adjusted_assessment["recipe_recommendations"],
            guidance_notes=guidance_notes,
            medication_plan=context.medications,
            questionnaire=context.questionnaire,
        )

    # ------------------------------------------------------------------ #
    # CGM processing
    # ------------------------------------------------------------------ #
    def _analyze_cgm(self, context: IntegratedPatientContext) -> CGMInsights:
        """Run CGM analytics and persist HTML report."""
        df = load_cgm_data(context.cgm_file)
        patient_info = self._compose_patient_info(context)
        medication_payload = context.medications.to_dict()

        analysis = self.cgm_generator._perform_full_analysis(
            df, patient_info, medication_payload
        )

        html_report = self.cgm_generator._generate_comprehensive_html(
            analysis, context.patient_id, patient_info
        )
        html_path = self.report_output_dir / f"CGM_Report_{context.patient_id}.html"
        html_path.write_text(html_report, encoding="utf-8")

        summary = analysis["summary_metrics"]
        snapshot = CGMMetricSnapshot(
            mean_glucose=summary["mean_glucose"],
            gmi=summary["gmi"],
            tir=summary["tir"],
            tar=summary["tar"],
            tbr=summary["tbr"],
            cv=summary["cv"],
            mage=summary.get("mage"),
            auc_day=summary.get("auc_day"),
            auc_night=summary.get("auc_night"),
            lbgi=summary.get("lbgi"),
            hbgi=summary.get("hbgi"),
            monitoring_days=summary.get("monitoring_days"),
            risk_tags=self._derive_risk_tags(summary, analysis["patterns"]),
        )

        return CGMInsights(
            summary=snapshot,
            patterns=analysis["patterns"],
            period_analysis=analysis["period_analysis"],
            weekday_weekend=analysis["weekday_weekend"],
            medication_analysis=analysis["medication_analysis"],
            text_assessment=analysis["text_assessment"],
            html_report_path=str(html_path),
        )

    def _compose_patient_info(self, context: IntegratedPatientContext) -> Dict:
        """Map patient dataclass to dict expected by CGM generator."""
        profile = context.patient_profile
        return {
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "height": profile.height,
            "weight": profile.weight,
            "diagnosed_diseases": profile.diagnosed_diseases,
            "activity_level": profile.activity_level,
        }

    def _derive_risk_tags(self, summary: Dict, patterns: Dict) -> List[str]:
        """Generate human-readable risk tags from CGM metrics."""
        tags: List[str] = []
        if summary["tir"] < 70:
            tags.append("TIR低于70%")
        if summary["tar"] > 25:
            tags.append("高血糖暴露增加")
        if summary["tbr"] >= 4:
            tags.append("夜间/低血糖风险")
        if summary["cv"] >= 36:
            tags.append("血糖波动显著")

        dawn = patterns["patterns"]["dawn_phenomenon"]
        if dawn.get("detected"):
            tags.append("黎明现象")

        nocturnal = patterns["patterns"]["nocturnal_hypoglycemia"]
        if nocturnal.get("detected"):
            tags.append("夜间低血糖事件")

        return tags

    # ------------------------------------------------------------------ #
    # Assessment integration
    # ------------------------------------------------------------------ #
    def _integrate_assessments(
        self, context: IntegratedPatientContext, cgm_insights: CGMInsights
    ) -> Tuple[Dict, List[str]]:
        """Merge CGM insights into nutrition assessment."""
        assessment = deepcopy(
            self.nutrition_system.comprehensive_assessment(context.patient_profile)
        )

        notes: List[str] = []
        snapshot = cgm_insights.summary

        dietary_notes = assessment["recipe_recommendations"].setdefault(
            "饮食注意事项", []
        )

        if snapshot.tir < 70:
            msg = (
                "TIR不足70%，需要进一步降低精制碳水摄入并增加膳食纤维。"
            )
            dietary_notes.append(msg)
            notes.append(msg)
        if snapshot.tar > 25:
            msg = "高血糖暴露较高，建议餐前强化低GI主食替换并关注进餐顺序。"
            dietary_notes.append(msg)
            notes.append(msg)
        if snapshot.tbr >= 4:
            msg = "存在低血糖风险，请确保睡前加餐及运动后补充。"
            dietary_notes.append(msg)
            notes.append(msg)
        if snapshot.cv >= 36:
            msg = "血糖波动明显，建议规范作息并分配均衡碳水。"
            dietary_notes.append(msg)
            notes.append(msg)

        dawn = cgm_insights.patterns["patterns"]["dawn_phenomenon"]
        if dawn.get("detected"):
            msg = (
                f"黎明现象检出率 {dawn.get('detection_rate', 0)}%，建议晚餐 "
                "减少高GI食物并评估夜间用药。"
            )
            dietary_notes.append(msg)
            notes.append(msg)

        nocturnal = cgm_insights.patterns["patterns"]["nocturnal_hypoglycemia"]
        if nocturnal.get("detected"):
            msg = (
                f"夜间低血糖发生 {nocturnal.get('frequency', 0)} 次，需要安排低GI "
                "睡前加餐并监测凌晨血糖。"
            )
            dietary_notes.append(msg)
            notes.append(msg)

        questionnaire = context.questionnaire
        if questionnaire.carbohydrate_tolerance == "低":
            msg = "患者自述碳水耐受低，建议主食粗细搭配并分餐进食。"
            dietary_notes.append(msg)
            notes.append(msg)
        if questionnaire.snacking_frequency == "频繁":
            msg = "加餐频率较高，请使用坚果/乳制品等低GI选项控制血糖波动。"
            dietary_notes.append(msg)
            notes.append(msg)
        if questionnaire.dietary_restrictions:
            msg = f"特殊饮食限制：{', '.join(questionnaire.dietary_restrictions)}，已在菜单中规避。"
            dietary_notes.append(msg)
            notes.append(msg)

        # Update monitoring plan with CGM-specific reminders
        monitoring = assessment["monitoring_plan"]
        monitoring.setdefault("每日监测", []).append("CGM数据上传与回顾")
        monitoring.setdefault("每周监测", []).append("至少一次餐后血糖复盘")

        # Attach CGM risk tags into patient info overview
        assessment["patient_info"][
            "CGM风险提示"
        ] = ", ".join(snapshot.risk_tags) if snapshot.risk_tags else "暂无显著风险"

        return assessment, notes

    def _build_additional_section(
        self,
        insights: CGMInsights,
        medication_plan: MedicationPlan,
        questionnaire: DietQuestionnaire,
        recipe_recommendations: Dict,
        guidance_notes: List[str],
    ) -> str:
        """Generate markdown section summarising CGM findings."""
        snapshot = insights.summary
        lines = [
            "## 🩺 CGM 血糖洞察摘要",
            "",
            f"- 平均血糖: **{snapshot.mean_glucose:.1f} mmol/L**",
            f"- GMI: **{snapshot.gmi:.1f}%** | CV: **{snapshot.cv:.1f}%**",
            f"- TIR/TAR/TBR: **{snapshot.tir:.1f}% / {snapshot.tar:.1f}% / {snapshot.tbr:.1f}%**",
            f"- MAGE: **{snapshot.mage:.2f} mmol/L**" if snapshot.mage is not None else "",
            f"- 日间/夜间 AUC: **{snapshot.auc_day:.1f} / {snapshot.auc_night:.1f} mmol·h**"
            if snapshot.auc_day is not None and snapshot.auc_night is not None
            else "",
            f"- 低/高血糖风险指数: **LBGI {snapshot.lbgi:.2f} | HBGI {snapshot.hbgi:.2f}**"
            if snapshot.lbgi is not None and snapshot.hbgi is not None
            else "",
            f"- 风险标签: **{', '.join(snapshot.risk_tags)}**"
            if snapshot.risk_tags
            else "- 风险标签: 暂无显著风险",
            "",
            "### 🧭 系统建议",
            insights.text_assessment,
            "",
            f"[🔗 点击查看完整CGM报告]({insights.html_report_path})",
            "",
            "### 💊 当前用药概览",
        ]

        if medication_plan.entries:
            for entry in medication_plan.entries:
                lines.extend(
                    [
                        f"- **{entry.name}** | 剂量: {entry.dosage or '未填写'} | 频次: {entry.frequency or '未填写'}",
                        f"  - 用药目的: {entry.purpose or '未提供'}",
                        f"  - 依从性: {entry.compliance or '未评估'}",
                        f"  - 起始日期: {entry.start_date.isoformat() if entry.start_date else '未知'}",
                        f"  - 备注: {entry.notes or '无'}",
                    ]
                )
        else:
            lines.append("- 暂无药物信息记录")

        lines.extend(
            [
                "",
                "### 📝 饮食问卷概览",
                f"- 偏好菜系: {', '.join(questionnaire.preferred_cuisines) or '未填写'}",
                f"- 不喜欢的食物: {', '.join(questionnaire.disliked_foods) or '未填写'}",
                f"- 饮食限制: {', '.join(questionnaire.dietary_restrictions) or '无'}",
                f"- 辣度承受: {questionnaire.spice_tolerance}",
                f"- 碳水耐受: {questionnaire.carbohydrate_tolerance}",
                f"- 加餐频率: {questionnaire.snacking_frequency}",
                f"- 进餐规律性: {questionnaire.meal_regulariy}",
                f"- 饮水情况: {questionnaire.hydration}",
            ]
        )

        if questionnaire.notes:
            lines.append(f"- 其它备注: {questionnaire.notes}")

        lines.extend(
            [
                "",
                "### 🍽️ 今日推荐菜单摘要",
            ]
        )
        for meal, dishes in recipe_recommendations.items():
            if isinstance(dishes, list) and dishes:
                meal_name = meal.replace("推荐", "")
                lines.append(f"- **{meal_name}**: {dishes[0]}")

        if guidance_notes:
            lines.extend(
                [
                    "",
                    "### ⚠️ CGM 重点提醒",
                ]
            )
            lines.extend([f"- {note}" for note in guidance_notes])

        return "\n".join([line for line in lines if line.strip()])
