# =============================================================================
# Chapter 7: Material Take-off & Quantity Summary
# =============================================================================

from osdagbridge.core.reports.report_utils import _fig_embed
from osdagbridge.core.reports.styles import build_longtable_headers


def ch7_quantities(input_dict, fig_paths=None):
    fig_paths = fig_paths or {}

    header_row = (
        r"\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & "
        r"\textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & "
        r"\textbf{Total Weight (MT)}"
    )

    chart_tex = ""
    if fig_paths.get("material_quantities"):
        chart_tex = (
            "\n\\vspace{1em}\n"
            + _fig_embed(
                fig_paths["material_quantities"],
                r"\textbf{Material Quantity Distribution by Component (Metric Tonnes)}",
                width=r"0.92\textwidth",
            )
        )

    return (
        r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This chapter summarizes the estimated Bill of Materials (BOM) for structural steel, deck concrete, reinforcement, shear connectors, and crash barriers.

\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|}
"""
        + build_longtable_headers(
            r"\textbf{Bill of Materials (Steel, Concrete, and Reinforcement Quantities)}",
            header_row,
            7,
        )
        + r"""
1 & Structural Steel (IS 2062) for Girders & """
        + str(input_dict.get("steel_girders_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("steel_girders_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("steel_girders_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("steel_girders_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("steel_girders_wt_total", "N.A."))
        + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """
        + str(input_dict.get("bracing_top_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_top_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_top_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_top_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_top_wt_total", "N.A."))
        + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """
        + str(input_dict.get("bracing_bot_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_bot_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_bot_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_bot_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_bot_wt_total", "N.A."))
        + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """
        + str(input_dict.get("bracing_diag_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_diag_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_diag_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_diag_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("bracing_diag_wt_total", "N.A."))
        + r""" \\
\hline
3 & Concrete (M40) for Deck Slab & """
        + str(input_dict.get("concrete_deck_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("concrete_deck_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("concrete_deck_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("concrete_deck_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("concrete_deck_wt_total", "N.A."))
        + r""" \\
\hline
4 & Reinforcement Steel (Fe 500) & """
        + str(input_dict.get("rebar_deck_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("rebar_deck_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("rebar_deck_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("rebar_deck_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("rebar_deck_wt_total", "N.A."))
        + r""" \\
\hline
5 & Shear Stud Connectors & """
        + str(input_dict.get("shear_studs_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("shear_studs_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("shear_studs_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("shear_studs_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("shear_studs_wt_total", "N.A."))
        + r""" \\
\hline
6 & Crash Barrier & """
        + str(input_dict.get("crash_barrier_vol_formula", "N.A."))
        + r""" & """
        + str(input_dict.get("crash_barrier_qty", "N.A."))
        + r""" & """
        + str(input_dict.get("crash_barrier_vol_total", "N.A."))
        + r""" & """
        + str(input_dict.get("crash_barrier_wt_single", "N.A."))
        + r""" & """
        + str(input_dict.get("crash_barrier_wt_total", "N.A."))
        + r""" \\
\end{longtable}
\endgroup
"""
        + chart_tex
    )