"""
Matplotlib chart generators for OsdagBridge LaTeX Design Reports.
Uses centralized styling from styles.py and non-interactive Agg backend.
"""

import logging
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from osdagbridge.core.reports.styles import (
    MPL_DARK,
    MPL_FAIL,
    MPL_OSDAG_GREEN,
    MPL_PALETTE,
    MPL_PASS,
    MPL_WARN,
    apply_matplotlib_theme,
)

logger = logging.getLogger(__name__)


def _parse_float(value):
    """Extract a leading float from numeric or string values (e.g. '12.45 MT')."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[-+]?\d*\.?\d+", str(value))
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None


def _max_member_efficiency(pair_designs):
    """Extract maximum utilization ratio from cross-bracing / end-diaphragm results."""
    from osdagbridge.core.bridge_types.plate_girder.results_data import _extract_osdag_summary

    if not isinstance(pair_designs, dict):
        return None
    best = None
    for members in pair_designs.values():
        if not isinstance(members, dict):
            continue
        for force_types in members.values():
            if not isinstance(force_types, dict):
                continue
            for raw in force_types.values():
                try:
                    val = _extract_osdag_summary(raw or {}).get("efficiency")
                    if val is None:
                        continue
                    f = float(val)
                    if best is None or f > best:
                        best = f
                except (TypeError, ValueError, AttributeError):
                    continue
    return best


def generate_ur_chart(output_dict: dict, out_path: str):
    """
    Generate a horizontal bar chart of maximum Utilization Ratios (UR)
    across major bridge components. Returns out_path on success, else None.
    """
    try:
        output_dict = output_dict or {}
        design_results = output_dict.get("design_results", {}) or {}
        per_girder = design_results.get("per_girder", {}) or {}
        deck_results = output_dict.get("deck_design_results", {}) or {}
        cb_results = output_dict.get("crossbracing_design_results", {}) or {}
        ed_results = output_dict.get("end_diaphragm_design_results", {}) or {}

        # Girder max UR
        girder_ur = None
        for g, gd in per_girder.items():
            if str(g).startswith("EB"):
                continue
            for chk in (gd.get("checks") or []):
                dcr = _parse_float(chk.get("dcr"))
                if dcr is not None and (girder_ur is None or dcr > girder_ur):
                    girder_ur = dcr

        # Deck slab max UR
        deck_urs = [
            _parse_float(v)
            for k, v in deck_results.items()
            if str(k).startswith("ur_")
        ]
        deck_urs = [u for u in deck_urs if u is not None]
        deck_ur = max(deck_urs) if deck_urs else None

        cb_ur = _max_member_efficiency(cb_results)
        ed_ur = _max_member_efficiency(ed_results)

        items = [
            ("Plate Girder", girder_ur),
            ("Deck Slab", deck_ur),
            ("Cross Bracing", cb_ur),
            ("End Diaphragm", ed_ur),
        ]
        items = [(label, val) for label, val in items if val is not None]
        if not items:
            return None

        labels = [i[0] for i in items]
        values = [i[1] for i in items]
        colors = [
            MPL_FAIL if v > 1.0 else (MPL_WARN if v >= 0.85 else MPL_PASS)
            for v in values
        ]

        apply_matplotlib_theme(plt)
        fig, ax = plt.subplots(figsize=(6.8, max(2.6, 0.75 * len(items) + 1.0)))

        bars = ax.barh(labels, values, color=colors, height=0.52, edgecolor="none")
        ax.axvline(1.0, color=MPL_FAIL, linestyle="--", linewidth=1.2, label="Limit (UR = 1.0)")

        max_x = max(1.18, max(values) * 1.18)
        ax.set_xlim(0, max_x)
        ax.set_xlabel("Utilization Ratio (Demand / Capacity)")
        ax.set_title("Component-wise Maximum Utilization Ratio (UR)")
        ax.invert_yaxis()

        for bar, val in zip(bars, values):
            status = "FAIL" if val > 1.0 else "PASS"
            ax.text(
                val + max_x * 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.2f} ({status})",
                va="center",
                ha="left",
                fontsize=8.5,
                fontweight="bold",
                color=MPL_DARK,
            )

        ax.legend(loc="lower right", fontsize=8.5)
        fig.tight_layout()
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return out_path
    except Exception as exc:
        logger.warning("Failed to generate UR chart: %s", exc)
        return None


def generate_material_quantity_chart(input_dict: dict, out_path: str):
    """
    Generate a bar chart of Bill of Materials total weights (Metric Tonnes).
    Returns out_path on success, else None.
    """
    try:
        input_dict = input_dict or {}

        bracing_total = sum(
            v
            for v in (
                _parse_float(input_dict.get("bracing_top_wt_total")),
                _parse_float(input_dict.get("bracing_bot_wt_total")),
                _parse_float(input_dict.get("bracing_diag_wt_total")),
            )
            if v is not None
        )

        raw_items = [
            ("Steel Girders", _parse_float(input_dict.get("steel_girders_wt_total"))),
            ("Cross Bracing", bracing_total if bracing_total > 0 else None),
            ("Deck Concrete", _parse_float(input_dict.get("concrete_deck_wt_total"))),
            ("Rebar (Fe 500)", _parse_float(input_dict.get("rebar_deck_wt_total"))),
            ("Shear Studs", _parse_float(input_dict.get("shear_studs_wt_total"))),
            ("Crash Barrier", _parse_float(input_dict.get("crash_barrier_wt_total"))),
        ]
        items = [(lbl, val) for lbl, val in raw_items if val is not None and val > 0]
        if not items:
            return None

        labels = [i[0] for i in items]
        values = [i[1] for i in items]
        colors = [MPL_PALETTE[idx % len(MPL_PALETTE)] for idx in range(len(items))]

        apply_matplotlib_theme(plt)
        fig, ax = plt.subplots(figsize=(7.0, 3.6))

        bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor="none")
        max_y = max(values) * 1.18
        ax.set_ylim(0, max_y)
        ax.set_ylabel("Total Weight (Metric Tonnes)")
        ax.set_title("Estimated Material Quantities by Bridge Component")
        plt.setp(ax.get_xticklabels(), rotation=18, ha="right")

        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + max_y * 0.02,
                f"{val:.2f}",
                ha="center",
                va="bottom",
                fontsize=8.5,
                fontweight="bold",
                color=MPL_DARK,
            )

        fig.tight_layout()
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return out_path
    except Exception as exc:
        logger.warning("Failed to generate Material Quantity chart: %s", exc)
        return None