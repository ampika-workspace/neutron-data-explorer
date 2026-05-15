"""
pages/03_Neutron_Spectrum.py
----------------------------
Neutron Spectrum — visualise energy spectrum ของ neutron sources
ใช้ข้อมูลจาก ENDF/B-VIII.0 (Cf-252) และ analytical models (Am-Be, Watt)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.lang import t, lang_toggle
from utils.endf_loader import (
    load_endf,
    get_emission_spectrum,
    make_log_energy_grid,
    eV_to_MeV,
    MeV_to_eV,
    is_endf_available,
    show_endf_status,
    endf_file_exists,
)
from utils.sources_data import get_source

st.set_page_config(
    page_title="Neutron Spectrum — Neutron Data Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.info-box {
    background: rgba(37,99,235,0.06);
    border-left: 3px solid rgba(37,99,235,0.5);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px; margin-bottom: 12px;
    font-size: 0.88rem; line-height: 1.6;
}
.warn-box {
    background: rgba(217,119,6,0.06);
    border-left: 3px solid rgba(217,119,6,0.5);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px; margin-bottom: 12px;
    font-size: 0.88rem; line-height: 1.6;
}
.metric-mini {
    background: var(--secondary-background-color, #f8fafc);
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
    margin-bottom: 8px;
}
.metric-mini-label { font-size:0.74rem; opacity:0.6; margin-bottom:4px; }
.metric-mini-value { font-size:1.1rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚛️ Neutron Data Explorer")
    st.divider()
    lang_toggle()
    st.divider()
    st.markdown("**Quick Navigation**")
    st.page_link("app.py",                                label="🏠 Home")
    st.page_link("pages/01_Source_Library.py",            label="📚 Source Library")
    st.page_link("pages/02_Reaction_Explorer.py",         label="⚛️ Reaction Explorer")
    st.page_link("pages/03_Neutron_Spectrum.py",          label="📊 Neutron Spectrum")
    st.page_link("pages/04_Activation_Calculator.py",     label="☢️ Activation Calculator")
    st.divider()
    show_endf_status()


# ── Analytical spectrum models ────────────────────────────────────────────────

def watt_spectrum(E_MeV: np.ndarray, a: float = 1.025, b: float = 2.926) -> np.ndarray:
    E    = np.asarray(E_MeV, dtype=float)
    vals = np.sinh(np.sqrt(b * E)) * np.exp(-E / a)
    vals = np.where(E > 0, vals, 0.0)
    _trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return vals / (_trapz(vals, E) + 1e-30)


def ambe_spectrum_analytical(E_MeV: np.ndarray) -> np.ndarray:
    E  = np.asarray(E_MeV, dtype=float)
    g1 = 0.30 * np.exp(-0.5 * ((E - 3.0) / 1.2) ** 2)
    g2 = 0.45 * np.exp(-0.5 * ((E - 4.5) / 1.5) ** 2)
    g3 = 0.20 * np.exp(-0.5 * ((E - 7.5) / 1.8) ** 2)
    vals = np.where(E > 0, g1 + g2 + g3, 0.0)
    _trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return vals / (_trapz(vals, E) + 1e-30)


def cm244_spectrum(E_MeV: np.ndarray) -> np.ndarray:
    return watt_spectrum(E_MeV, a=0.906, b=3.848)


# ── Source definitions for this page ─────────────────────────────────────────
SPECTRUM_SOURCES = {
    "AmBe": {
        "label":        "Am-241/Be",
        "symbol":       "²⁴¹Am/Be",
        "model":        "analytical",
        "fn":           ambe_spectrum_analytical,
        "color":        "#2563eb",
        "mean_MeV":     4.5,
        "max_MeV":      11.0,
        "description":  "Analytical model (ISO 8529-1 shape) — multi-Gaussian approximation",
        "endf_file":    None,
    },
    "Cf252": {
        "label":        "Cf-252",
        "symbol":       "²⁵²Cf",
        "model":        "watt",
        "fn":           lambda E: watt_spectrum(E, a=1.025, b=2.926),
        "color":        "#dc2626",
        "mean_MeV":     2.13,
        "max_MeV":      13.0,
        "description":  "Watt fission spectrum (a=1.025 MeV, b=2.926 MeV⁻¹) — ISO 8529-1",
        "endf_file":    "n-098_Cf_252.endf",
    },
    "Cm244": {
        "label":        "Cm-244",
        "symbol":       "²⁴⁴Cm",
        "model":        "watt",
        "fn":           cm244_spectrum,
        "color":        "#d97706",
        "mean_MeV":     2.12,
        "max_MeV":      12.0,
        "description":  "Watt fission spectrum (a=0.906 MeV, b=3.848 MeV⁻¹)",
        "endf_file":    None,
    },
    "PuBe238": {
        "label":        "Pu-238/Be",
        "symbol":       "²³⁸Pu/Be",
        "model":        "analytical",
        "fn":           ambe_spectrum_analytical,
        "color":        "#7c3aed",
        "mean_MeV":     4.5,
        "max_MeV":      11.0,
        "description":  "Analytical model — spectrum shape similar to Am-241/Be (alpha energy differs by ~10 keV)",
        "endf_file":    None,
    },
}

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Neutron Spectrum")
st.markdown(t("p03_desc"))
st.divider()

# ── Controls ──────────────────────────────────────────────────────────────────
col_ctrl, col_plot = st.columns([1, 2.5], gap="large")

with col_ctrl:
    st.markdown(t("p03_select_sources"))
    selected_sources = st.multiselect(
        t("p03_sources_label"),
        options=list(SPECTRUM_SOURCES.keys()),
        default=["AmBe", "Cf252"],
        format_func=lambda k: SPECTRUM_SOURCES[k]["label"],
        help=t("p03_sources_help"),
    )

    st.markdown(t("p03_energy_range"))
    e_max = st.slider(
        "E max (MeV)", min_value=5.0, max_value=20.0, value=14.0, step=0.5,
        help=t("p03_emax_help"),
    )
    n_pts = st.slider(t("p03_resolution"), 200, 1000, 500, 100)

    st.markdown(t("p03_ref_lines"))
    show_thermal    = st.checkbox("Thermal (0.025 eV)",       value=False)
    show_ambe_mean  = st.checkbox("Am-Be mean (4.5 MeV)",     value=True)
    show_cf252_mean = st.checkbox("Cf-252 mean (2.13 MeV)",   value=True)
    show_14mev      = st.checkbox("14.1 MeV (D-T generator)", value=False)

    st.markdown(t("p03_display"))
    normalize  = st.checkbox(t("p03_normalize"), value=True)
    fill_area  = st.checkbox(t("p03_fill_area"), value=True)
    log_x      = st.checkbox(t("p03_log_x"),     value=False)

# ── Plot ──────────────────────────────────────────────────────────────────────
with col_plot:
    if not selected_sources:
        st.info(t("p03_no_source"))
        st.stop()

    E_MeV = np.linspace(0.01, e_max, n_pts)

    fig = go.Figure()

    for sid in selected_sources:
        src      = SPECTRUM_SOURCES[sid]
        spectrum = src["fn"](E_MeV)

        if not normalize:
            mean_e   = src.get("mean_MeV", 1.0)
            spectrum = spectrum * mean_e

        color = src["color"]
        label = f'{src["label"]} ({src["symbol"]})'

        # fill
        if fill_area:
            if color.startswith("#") and len(color) in (7, 9):
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fill_color = f"rgba({r},{g},{b},0.08)"
            elif color.startswith("rgb("):
                fill_color = color.replace("rgb(", "rgba(").replace(")", ",0.08)")
            else:
                fill_color = color
            fig.add_trace(go.Scatter(
                x=E_MeV, y=spectrum,
                mode="none",
                fill="tozeroy",
                fillcolor=fill_color,
                showlegend=False,
                hoverinfo="skip",
            ))

        # line
        fig.add_trace(go.Scatter(
            x=E_MeV, y=spectrum,
            mode="lines",
            name=label,
            line=dict(color=color, width=2.2),
            hovertemplate=(
                f"<b>{label}</b><br>"
                "E: %{x:.3f} MeV<br>"
                "N(E): %{y:.4f}<extra></extra>"
            ),
        ))

    # ── Reference lines ──
    if show_cf252_mean and "Cf252" in selected_sources:
        fig.add_vline(
            x=2.13, line_dash="dash", line_color="#dc2626", line_width=1.2,
            annotation_text="Cf-252 mean", annotation_position="top right",
            annotation_font_size=11,
        )

    if show_ambe_mean and "AmBe" in selected_sources:
        fig.add_vline(
            x=4.5, line_dash="dash", line_color="#2563eb", line_width=1.2,
            annotation_text="Am-Be mean", annotation_position="top right",
            annotation_font_size=11,
        )

    if show_14mev and e_max >= 14.1:
        fig.add_vline(
            x=14.1, line_dash="dot", line_color="#64748b", line_width=1.2,
            annotation_text="D-T 14.1 MeV", annotation_position="top left",
            annotation_font_size=11,
        )

    y_label = "Normalised Intensity N(E)" if normalize else "Intensity (a.u.)"

    fig.update_layout(
        title=dict(text="Neutron Energy Spectrum", font=dict(size=15)),
        xaxis=dict(
            title="Neutron Energy (MeV)",
            type="log" if log_x else "linear",
            range=[None, e_max] if not log_x else None,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
        ),
        yaxis=dict(
            title=y_label,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=20, t=70, b=60),
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Source info cards ─────────────────────────────────────────────────────────
if selected_sources:
    st.markdown(t("p03_summary"))
    cols = st.columns(len(selected_sources))
    for i, sid in enumerate(selected_sources):
        src = SPECTRUM_SOURCES[sid]
        with cols[i]:
            st.markdown(
                f'<div class="metric-mini">'
                f'<div class="metric-mini-label">{src["label"]}</div>'
                f'<div class="metric-mini-value" style="color:{src["color"]}">'
                f'{src["symbol"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'{t("p03_mean_energy")} {src["mean_MeV"]} MeV')
            st.markdown(f'{t("p03_max_energy")} {src["max_MeV"]} MeV')
            st.caption(src["description"])

st.divider()

# ── Spectrum comparison table ─────────────────────────────────────────────────
with st.expander(t("p03_compare_expander")):
    import pandas as pd

    rows = []
    for sid, src in SPECTRUM_SOURCES.items():
        rows.append({
            t("p03_col_source"): src["label"],
            t("p03_col_symbol"): src["symbol"],
            t("p03_col_model"):  src["model"].capitalize(),
            t("p03_col_mean_e"): src["mean_MeV"],
            t("p03_col_max_e"):  src["max_MeV"],
            t("p03_col_desc"):   src["description"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Physics notes ─────────────────────────────────────────────────────────────
with st.expander(t("p03_physics_expander")):
    st.markdown(t("p03_physics_content"))

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(t("p03_footer"))
