"""
Centralized styling, layout, and theme configuration for OsdagBridge LaTeX reports
and embedded matplotlib visualizations.
"""

# ---------------------------------------------------------------------------
# Brand & Semantic Colors (Hex without '#' for LaTeX \definecolor{...}{HTML})
# ---------------------------------------------------------------------------
COLOR_OSDAG_GREEN = "91B014"
COLOR_HEADER_BG = "EEF4D7"       # Soft tint of Osdag green for table headers
COLOR_ROW_STRIPE = "F9FBF2"      # Subtle alternating row tint
COLOR_TEXT_DARK = "1F2937"
COLOR_PASS = "1B7A3E"            # Accessible dark green for PASS status
COLOR_FAIL = "C0392B"            # Clear red for FAIL status
COLOR_WARN = "D97706"            # Amber for warnings / high UR (> 0.85)
COLOR_BORDER = "B8C4A0"

# Matplotlib-compatible hex palette (with '#')
MPL_OSDAG_GREEN = f"#{COLOR_OSDAG_GREEN}"
MPL_PASS = f"#{COLOR_PASS}"
MPL_FAIL = f"#{COLOR_FAIL}"
MPL_WARN = f"#{COLOR_WARN}"
MPL_DARK = f"#{COLOR_TEXT_DARK}"
MPL_PALETTE = [
    "#91B014",  # Osdag Green
    "#2B6CB0",  # Steel Blue
    "#D97706",  # Amber
    "#4A5568",  # Slate Gray
    "#38A169",  # Emerald
    "#805AD5",  # Muted Purple
]

# ---------------------------------------------------------------------------
# Page Geometry & Footer Spacing (Fixes Task 2: Footer Overlap)
# ---------------------------------------------------------------------------
PAGE_GEOMETRY = (
    "a4paper, top=1in, bottom=1.25in, left=1in, right=1in, "
    "headheight=16pt, headsep=18pt, footskip=34pt"
)
LINE_STRETCH = 1.15
RULE_THICKNESS = "1pt"

# ---------------------------------------------------------------------------
# Table Spacing & Typography
# ---------------------------------------------------------------------------
TABLE_COL_SEP = "6pt"
TABLE_ARRAY_STRETCH = 1.15
TABLE_RULE_WIDTH = "0.5pt"
TABLE_EXTRA_ROW_HEIGHT = "0.8pt"
LONGTABLE_PRE_SKIP = "4pt"
LONGTABLE_POST_SKIP = "8pt"
MIN_NEEDSPACE_LINES = 6


def build_color_definitions() -> str:
    """Return LaTeX \\definecolor declarations for the report preamble."""
    return (
        f"\\definecolor{{osdagGreen}}{{HTML}}{{{COLOR_OSDAG_GREEN}}}\n"
        f"\\definecolor{{osdagHeaderBg}}{{HTML}}{{{COLOR_HEADER_BG}}}\n"
        f"\\definecolor{{osdagStripe}}{{HTML}}{{{COLOR_ROW_STRIPE}}}\n"
        f"\\definecolor{{osdagPass}}{{HTML}}{{{COLOR_PASS}}}\n"
        f"\\definecolor{{osdagFail}}{{HTML}}{{{COLOR_FAIL}}}\n"
        f"\\definecolor{{osdagWarn}}{{HTML}}{{{COLOR_WARN}}}\n"
    )


def build_table_spacing_commands() -> str:
    """Return LaTeX table padding and spacing configuration."""
    return (
        f"\\setlength{{\\tabcolsep}}{{{TABLE_COL_SEP}}}\n"
        f"\\renewcommand{{\\arraystretch}}{{{TABLE_ARRAY_STRETCH}}}\n"
        f"\\setlength{{\\LTpre}}{{{LONGTABLE_PRE_SKIP}}}\n"
        f"\\setlength{{\\LTpost}}{{{LONGTABLE_POST_SKIP}}}\n"
        f"\\setlength{{\\arrayrulewidth}}{{{TABLE_RULE_WIDTH}}}\n"
        f"\\setlength{{\\extrarowheight}}{{{TABLE_EXTRA_ROW_HEIGHT}}}\n"
        f"\\BeforeBeginEnvironment{{table}}{{\\needspace{{{MIN_NEEDSPACE_LINES}\\baselineskip}}}}\n"
        f"\\BeforeBeginEnvironment{{longtable}}{{\\needspace{{{MIN_NEEDSPACE_LINES}\\baselineskip}}}}\n"
    )


def build_footer_rule() -> str:
    """
    Build the custom fancyhdr \\footrule macro.
    Uses controlled spacing with increased bottom margin & footskip so the
    '* Software default value' note never overlaps body text or tables.
    """
    return (
        r"\renewcommand{\footrule}{%" + "\n"
        r"  \ifbool{hasSDonPage}{%" + "\n"
        r"    \vspace{-14pt}%" + "\n"
        r"    \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%" + "\n"
        r"    \vspace{3pt}%" + "\n"
        r"  }{%" + "\n"
        r"    \vspace{-4pt}%" + "\n"
        r"  }%" + "\n"
        f"  \\color{{osdagGreen}}\\hrule width\\headwidth height {RULE_THICKNESS} \\vspace{{5pt}}%\n"
        r"}"
    )


def build_longtable_headers(caption: str, header_row: str, col_count: int) -> str:
    """
    Generate standard LaTeX longtable header/footer blocks so multi-page tables
    automatically repeat column headers and show a '(Continued)' indicator.
    """
    return (
        f"\\caption{{{caption}}} \\\\\n"
        r"\hline" + "\n"
        r"\rowcolor{osdagHeaderBg}" + "\n"
        f"{header_row} \\\\\n"
        r"\hline" + "\n"
        r"\endfirsthead" + "\n"
        f"\\caption[]{{{caption} \\textit{{(Continued)}}}} \\\\\n"
        r"\hline" + "\n"
        r"\rowcolor{osdagHeaderBg}" + "\n"
        f"{header_row} \\\\\n"
        r"\hline" + "\n"
        r"\endhead" + "\n"
        r"\hline" + "\n"
        f"\\multicolumn{{{col_count}}}{{r}}{{\\footnotesize\\textit{{Continued on next page...}}}} \\\\\n"
        r"\endfoot" + "\n"
        r"\hline" + "\n"
        r"\endlastfoot"
    )


def apply_matplotlib_theme(plt) -> None:
    """Apply clean, publication-grade OsdagBridge styling to matplotlib charts."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 9.5,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.5,
        "axes.edgecolor": "#CBD5E0",
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": "#E2E8F0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.frameon": True,
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#E2E8F0",
        "figure.dpi": 300,
    })