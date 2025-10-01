#!/usr/bin/env python3
"""Enhanced anomaly detection for CGMS glucose data.

Features:
- Clinical high/low thresholds (default 27.8 / 2.2 mmol/L)
- Statistical Z-score and IQR checks (flagged only if outside clinical range)
- Rate-of-change detection for sudden jumps
- Summary report + anomaly CSV + diagnostic plot
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class Thresholds:
    high: float = 27.8
    low: float = 2.2
    jump: float = 5.0  # mmol/L change
    max_jump_minutes: int = 20


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, sep="\t", skiprows=2)
    df.columns = ["ID", "timestamp", "record_type", "glucose"]
    df = df[df["timestamp"] != "时间"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y/%m/%d %H:%M")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["glucose"] = pd.to_numeric(df["glucose"], errors="coerce")
    df = df.dropna(subset=["glucose", "timestamp"])
    return df


def detect_anomalies(df: pd.DataFrame, thresholds: Thresholds) -> pd.DataFrame:
    out = df.copy()
    mean = out["glucose"].mean()
    std = out["glucose"].std(ddof=0)
    out["zscore"] = (out["glucose"] - mean) / std

    q1 = out["glucose"].quantile(0.25)
    q3 = out["glucose"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    out["clinical_high"] = out["glucose"] >= thresholds.high
    out["clinical_low"] = out["glucose"] <= thresholds.low

    out["zscore_flag"] = out["zscore"].abs() > 3
    out["iqr_flag"] = (out["glucose"] < lower) | (out["glucose"] > upper)
    # Only keep statistical anomalies if outside clinical safe band
    out["statistical_flag"] = (out["zscore_flag"] | out["iqr_flag"]) & ~(out["clinical_high"] | out["clinical_low"])

    out["delta"] = out["glucose"].diff()
    out["minutes_delta"] = out["timestamp"].diff().dt.total_seconds().div(60)
    out["jump_flag"] = (out["delta"].abs() >= thresholds.jump) & (out["minutes_delta"] <= thresholds.max_jump_minutes)

    reasons: List[List[str]] = [[] for _ in range(len(out))]
    for idx, row in out.iterrows():
        if row["clinical_high"]:
            reasons[idx].append(f"clinical_high(>={thresholds.high})")
        if row["clinical_low"]:
            reasons[idx].append(f"clinical_low(<= {thresholds.low})")
        if row["jump_flag"]:
            reasons[idx].append(f"jump(|Δ|>={thresholds.jump})")
        if row["statistical_flag"]:
            reasons[idx].append("statistical_outlier")

    out["anomaly_reasons"] = [";".join(r) for r in reasons]
    out["is_anomaly"] = out["anomaly_reasons"].astype(bool)

    out.attrs["summary"] = {
        "total_points": len(out),
        "clinical_high": int(out["clinical_high"].sum()),
        "clinical_low": int(out["clinical_low"].sum()),
        "statistical_only": int(((out["statistical_flag"]) & ~(out["clinical_high"] | out["clinical_low"] | out["jump_flag"])).sum()),
        "jump_anomalies": int(out["jump_flag"].sum()),
        "iqr_bounds": (round(float(lower), 2), round(float(upper), 2)),
        "glucose_range": (round(float(out["glucose"].min()), 2), round(float(out["glucose"].max()), 2)),
    }
    return out


def save_outputs(df: pd.DataFrame, base_path: Path) -> Path:
    anomalies = df[df["is_anomaly"]].copy()
    anomaly_path = base_path.with_name(base_path.stem + "_anomalies.csv")
    anomalies[["timestamp", "glucose", "delta", "zscore", "anomaly_reasons"]].to_csv(anomaly_path, index=False)
    return anomaly_path


def plot_series(df: pd.DataFrame, anomalies: pd.DataFrame, base_path: Path) -> Path:
    plt.figure(figsize=(14, 6))
    plt.plot(df["timestamp"], df["glucose"], label="Glucose (mmol/L)", color="#1f77b4", linewidth=1.1)
    if not anomalies.empty:
        plt.scatter(anomalies["timestamp"], anomalies["glucose"], color="#d62728", label="Anomalies", zorder=5, s=65)
        for _, row in anomalies.iterrows():
            plt.annotate(row["anomaly_reasons"], (row["timestamp"], row["glucose"]), textcoords="offset points", xytext=(0, 8), ha='center', fontsize=8, color="#d62728")
    plt.xlabel("Time")
    plt.ylabel("Glucose (mmol/L)")
    plt.title("CGMS Glucose Series with Detected Anomalies")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plot_path = base_path.with_name(base_path.stem + "_anomalies.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    return plot_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Enhanced CGMS anomaly detection")
    parser.add_argument("data", type=Path, help="Path to tab-separated CGMS file (same format as R026 v5.txt)")
    parser.add_argument("--high", type=float, default=27.8, help="Clinical high glucose threshold")
    parser.add_argument("--low", type=float, default=2.2, help="Clinical low glucose threshold")
    parser.add_argument("--jump", type=float, default=5.0, help="Jump threshold (mmol/L change)")
    parser.add_argument("--jump-minutes", type=int, default=20, help="Maximum minutes between readings for jump detection")
    args = parser.parse_args()

    thresholds = Thresholds(high=args.high, low=args.low, jump=args.jump, max_jump_minutes=args.jump_minutes)
    df = load_data(args.data)
    result = detect_anomalies(df, thresholds)
    summary = result.attrs["summary"]

    anomalies_path = save_outputs(result, args.data)
    plot_path = plot_series(result, result[result["is_anomaly"]], args.data)

    report = {
        "summary": summary,
        "anomaly_csv": str(anomalies_path),
        "plot": str(plot_path),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
