# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE,
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import build_longtable_headers


def ch3_loads(input_dict):
    # Live load vehicle names mapping
    vehicles = []
    if input_dict.get(KEY_LL_IRC_CLASS_A):
        vehicles.append("Class A")
    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        vehicles.append("Class 70R (Wheeled)")
    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        vehicles.append("Class 70R (Tracked)")
    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        vehicles.append("Class AA (Wheeled)")
    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        vehicles.append("Class AA (Tracked)")
    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        vehicles.append("Class SV")
    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        vehicles.append("Class 70R (Bogie)")
    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        vehicles.append("Class Fatigue")

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            if isinstance(c, dict) and c.get("name"):
                vehicles.append(c["name"])
            elif isinstance(c, str):
                vehicles.append(c)

    vehicles_str = ", ".join(vehicles) if vehicles else "None"

    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    impact_factor_str = "N/A"
    if span not in (None, ""):
        try:
            span_m = float(span)
            factors = []
            if input_dict.get(KEY_LL_IRC_CLASS_A):
                im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
                factors.append(f"Class A: {1.0 + im_a:.3f}")
            is_wheeled_heavy = (
                input_dict.get(KEY_LL_IRC_70R_WHEELED)
                or input_dict.get(KEY_LL_IRC_AA_WHEELED)
                or input_dict.get(KEY_LL_IRC_70R_BOGIE)
            )
            is_tracked_heavy = (
                input_dict.get(KEY_LL_IRC_70R_TRACKED)
                or input_dict.get(KEY_LL_IRC_AA_TRACKED)
            )
            if is_wheeled_heavy or is_tracked_heavy:
                im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
                factors.append(f"Class AA/70R: {1.0 + im_aa:.3f}")

            if factors:
                impact_factor_str = ", ".join(factors)
        except Exception:
            impact_factor_str = "N/A"

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    braking_force_str = "N/A"
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
            braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
            braking_force_kN = braking_force_t * 9.81
            braking_force_str = f"{braking_force_kN:.2f} kN ({braking_force_t:.2f} tonnes)"
        except Exception:
            braking_force_str = "N/A"

    # Footway / Footpath Live Load
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        try:
            fp_val_tex = f"{IRC6_2017.cl_206_1_footway_load():.3f}" + r" kN/m\textsuperscript{2} (IRC 6 Cl. 206.1)"
        except Exception:
            fp_val_tex = "N/A"
    elif fp_value not in (None, ""):
        fp_val_tex = _tex(fp_value) + r" kN/m\textsuperscript{2}"
    else:
        fp_val_tex = "N/A"
    fp_mode_tex = _tex(fp_mode) if fp_mode not in (None, "") else "As per IRC 6"

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get("wind_speed")
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_tex = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_tex = f"{float(pz_val):.2f}" + r" N/m\textsuperscript{2}" if pz_val not in (None, "") else "N/A"

    # Seismic — prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get("seismic_zone")
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {
                "Type I – Rocky or Hard": 1,
                "Type II – Medium Soil": 2,
                "Type III – Soft Soil": 3,
            }
            _st = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res = IRC6_2017.cl_218_5_1(
                zone=f"Zone {_z}",
                soil_type=_st,
                dead_load_kN=_dead,
                live_load_kN=_live,
                period_T=float(_tp) if _tp else None,
                damping_percent=float(_damp),
            )
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah = _res.get("Ah")
            if not sl_av:
                sl_av = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v):
        try:
            return f"{float(v):.4f}" if v not in (None, "") else "N/A"
        except (TypeError, ValueError):
            return _tex(v)

    # Temperature — prefer stored values, fall back to IRC6 calculation
    tl_temp_min = input_dict.get(KEY_TL_BRIDGE_TEMP_MIN)
    tl_temp_max = input_dict.get(KEY_TL_BRIDGE_TEMP_MAX)
    tl_rise = input_dict.get(KEY_TL_TEMP_RISE)
    tl_fall = input_dict.get(KEY_TL_TEMP_FALL)
    if not tl_temp_min or not tl_temp_max:
        try:
            _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get("shade_temp_max")
            _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or input_dict.get("shade_temp_min")
            if _tmax and _tmin:
                _res = IRC6_2017.cl_215_2_effective_bridge_temperature(
                    float(_tmax), float(_tmin), "metallic", False
                )
                _bt_min = _res.get("T_min", 0)
                _bt_max = _res.get("T_max", 0)
                _mean = (_bt_max + _bt_min) / 2.0
                tl_temp_min = f"{_bt_min:.2f}"
                tl_temp_max = f"{_bt_max:.2f}"
                tl_rise = f"{_bt_max - _mean:.2f}"
                tl_fall = f"{_mean - _bt_min:.2f}"
        except Exception:
            pass
    tl_temp_min = _tex(tl_temp_min) if tl_temp_min not in (None, "") else "N/A"
    tl_temp_max = _tex(tl_temp_max) if tl_temp_max not in (None, "") else "N/A"
    tl_rise = _tex(tl_rise) if tl_rise not in (None, "") else "N/A"
    tl_fall = _tex(tl_fall) if tl_fall not in (None, "") else "N/A"

    # --- Load Combinations (separated into ULS and SLS tables) ---
    _LOAD_LABEL_MAP = {
        "dead_load": "DL",
        "surfacing": "SIDL",
        "live_load": "LL",
        "wind_load": "WL",
        "thermal_load": "TL",
        "vehicle_collision": "VC",
        "barge_impact": "BI",
        "floating_bodies": "FB",
        "seismic": "EQ",
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get("adding")
                rel = val.get("relieving")
                add_s = f"{add:.2f}" if add is not None else "--"
                rel_s = f"{rel:.2f}" if rel is not None else "--"
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return " + ".join(parts)

    uls_rows = []
    for i, combo in enumerate(IRC6_2017.uls_load_combinations(), start=1):
        cases = _fmt_factors(combo["factors"])
        uls_rows.append(f"ULS-{i:02d}" + r" & " + cases + r" \\[4pt]" + "\n" + r"\hline")
    uls_rows_str = "\n".join(uls_rows)

    sls_rows = []
    for i, combo in enumerate(IRC6_2017.sls_load_combinations(), start=1):
        cases = _fmt_factors(combo["factors"])
        sls_rows.append(f"SLS-{i:02d}" + r" & " + cases + r" \\[4pt]" + "\n" + r"\hline")
    sls_rows_str = "\n".join(sls_rows)

    hdr_pv = r"\textbf{Parameter} & \textbf{Value}"
    hdr_lc = r"\textbf{Combination ID} & \textbf{Load Cases}"

    return (
        r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge superstructure and the Ultimate Limit State (ULS) and Serviceability Limit State (SLS) load combinations considered for analysis and design as per IRC 6:2017.

\vspace{0.5em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Dead Load -- Self Weight (DL)}", hdr_pv, 2)
        + r"""
\textnormal{Steel Self-Weight Applied} & """
        + _render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, r" kN/m\textsuperscript{3}")
        + r""" \\[4pt]
\hline
\textnormal{Concrete Deck Weight} & """
        + _render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, r" kN/m\textsuperscript{3}")
        + r""" \\[4pt]
\hline
\textnormal{Self-Weight Factor} & """
        + _render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)
        + r""" \\[4pt]
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Dead Load for Surfacing \& Appurtenances (DW / SIDL)}", hdr_pv, 2)
        + r"""
\textnormal{Wearing Course Load} & """
        + _render_value(input_dict, KEY_WC_MATERIAL)
        + r""" $\times$ """
        + _render_value(input_dict, KEY_WC_THICKNESS)
        + r""" \\[4pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """
        + _render_value(input_dict, KEY_CB_LOAD)
        + r""" kN/m per barrier \\[4pt]
\hline
\textnormal{Railing Load} & """
        + _render_value(input_dict, KEY_RL_LOAD_VALUE)
        + r""" kN/m\sdstar{} \\[4pt]
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Vehicular Live Loads (LL) --- per IRC 6}", hdr_pv, 2)
        + r"""
\textnormal{Vehicles Considered} & """
        + _tex(vehicles_str)
        + r""" \\[4pt]
\hline
\textnormal{Impact Factor (IRC 6 Cl. 208)} & """
        + _tex(impact_factor_str)
        + r""" \\[4pt]
\hline
\textnormal{Braking Load (IRC 6 Cl. 211)} & """
        + _tex(braking_force_str)
        + r""" \\[4pt]
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Footway / Footpath Live Load --- per IRC 6 Cl. 206}", hdr_pv, 2)
        + r"""
\textnormal{Footpath Load Mode} & """
        + fp_mode_tex
        + r""" \\[4pt]
\hline
\textnormal{Footpath Live Load Intensity} & """
        + fp_val_tex
        + r""" \\[4pt]
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Wind Load (WL) --- per IRC 6}", hdr_pv, 2)
        + r"""
\textnormal{Basic Wind Speed, $V_b$} & """
        + _render_value(input_dict, "wind_speed", " m/s")
        + r""" [from Project Location] \\[4pt]
\hline
\textnormal{Terrain Type} & """
        + _render_value(input_dict, KEY_WL_TERRAIN_TYPE)
        + r""" \\[4pt]
\hline
\textnormal{Average Exposed Height, $H$} & """
        + _render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, " m")
        + r""" \\[4pt]
\hline
\textnormal{Hourly Mean Wind Speed, $V_z$} & """
        + vz_tex
        + r""" \\[4pt]
\hline
\textnormal{Hourly Wind Pressure, $P_z$} & """
        + pz_tex
        + r""" \\[4pt]
\hline
\textnormal{Transverse Wind Force} & """
        + _render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, " kN")
        + r""" \\[4pt]
\hline
\textnormal{Longitudinal Wind Force} & """
        + _render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, " kN")
        + r""" \\[4pt]
\hline
\textnormal{Vertical Wind Force} & """
        + _render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, " kN")
        + r""" \\[4pt]
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Earthquake Load (EL) --- per IRC 6}", hdr_pv, 2)
        + r"""
\textnormal{Seismic Zone} & """
        + _render_value(input_dict, "seismic_zone")
        + r""" [from Project Location] \\[4pt]
\hline
\textnormal{Zone Factor, $Z$} & """
        + _sl(sl_zone_factor)
        + r""" \\[4pt]
\hline
\textnormal{Importance Factor, $I$} & """
        + _render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)
        + r""" \\[4pt]
\hline
\textnormal{Type of Soil} & """
        + _render_value(input_dict, KEY_SL_SOIL_TYPE)
        + r""" \\[4pt]
\hline
\textnormal{Spectral Acceleration, $S_a/g$} & """
        + _sl(sl_spectral)
        + r""" \\[4pt]
\hline
\textnormal{Horizontal Seismic Coefficient, $A_h$} & """
        + _sl(sl_ah)
        + r""" \\[4pt]
\hline
\textnormal{Vertical Seismic Coefficient, $A_v$} & """
        + _sl(sl_av)
        + r""" \\[4pt]
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Temperature Load (TL) --- per IRC 6}", hdr_pv, 2)
        + r"""
\textnormal{Maximum Shade Temperature} & """
        + _render_value(input_dict, "shade_temp_max")
        + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Minimum Shade Temperature} & """
        + _render_value(input_dict, "shade_temp_min")
        + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """
        + tl_temp_min
        + r""" to """
        + tl_temp_max
        + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +"""
        + tl_rise
        + r""" $^\circ$C / $-$"""
        + tl_fall
        + r""" $^\circ$C \\[4pt]
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|C{3.5cm}|p{12.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Ultimate Limit State (ULS) Load Combinations}", hdr_lc, 2)
        + "\n"
        + uls_rows_str
        + r"""
\end{longtable}

\vspace{0.5em}
\begin{longtable}{|C{3.5cm}|p{12.0cm}|}
"""
        + build_longtable_headers(r"\textbf{Serviceability Limit State (SLS) Load Combinations}", hdr_lc, 2)
        + "\n"
        + sls_rows_str
        + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""
    )