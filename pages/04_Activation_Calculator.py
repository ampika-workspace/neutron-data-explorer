"""
pages/04_Activation_Calculator.py
----------------------------------
Activation Calculator — คำนวณ radionuclides ที่เกิดจาก neutron activation
ใช้ข้อมูล production cross section จากไฟล์ ENDF/B-VIII.0
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from utils.lang import t, get_lang
from utils.endf_loader import (
    load_endf,
    get_activation_xs,
    get_reactions,
    get_cross_section,
    make_log_energy_grid,
    eV_to_MeV,
    MeV_to_eV,
    is_endf_available,
    show_endf_status,
    endf_file_exists,
    AVAILABLE_ENDF_FILES,
)

st.set_page_config(
    page_title="Activation Calculator — Neutron Data Explorer",
    page_icon="☢️",
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
    background: rgba(217,119,6,0.07);
    border-left: 3px solid rgba(217,119,6,0.55);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px; margin-bottom: 12px;
    font-size: 0.88rem; line-height: 1.6;
}
.result-card {
    background: var(--secondary-background-color, #f8fafc);
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
}
.result-name  { font-size:1.05rem; font-weight:700; margin-bottom:4px; }
.result-xs    { font-size:1.4rem;  font-weight:700; color:#2563eb; }
.result-label { font-size:0.75rem; opacity:0.6; }
.badge {
    display:inline-block; border-radius:999px;
    padding:2px 10px; font-size:0.74rem; font-weight:600;
    margin:2px 3px 2px 0; white-space:nowrap;
}
.badge-blue  { background:rgba(37,99,235,0.1);  color:#2563eb; }
.badge-green { background:rgba(5,150,105,0.1);  color:#059669; }
.badge-amber { background:rgba(217,119,6,0.1);  color:#d97706; }
.badge-red   { background:rgba(220,38,38,0.1);  color:#dc2626; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚛️ Neutron Data Explorer")
    st.divider()
    st.markdown("**Quick Navigation**")
    st.page_link("app.py",                                label="🏠 Home")
    st.page_link("pages/01_Source_Library.py",            label="📚 Source Library")
    st.page_link("pages/02_Reaction_Explorer.py",         label="⚛️ Reaction Explorer")
    st.page_link("pages/03_Neutron_Spectrum.py",          label="📊 Neutron Spectrum")
    st.page_link("pages/04_Activation_Calculator.py",     label="☢️ Activation Calculator")
    st.divider()
    show_endf_status()

# ── Known activation products per target ──────────────────────────────────────
# Each entry has a Thai field and an _en counterpart for bilingual display.
ACTIVATION_PRODUCTS = {
    "n-027_Co_059.endf": [
        {
            "residual":    "Co-60",
            "label":       "⁶⁰Co (ground state)",
            "label_en":    "⁶⁰Co (ground state)",
            "half_life":   "5.271 ปี",
            "half_life_en":"5.271 years",
            "radiation":   "β⁻ + γ (1.17 & 1.33 MeV)",
            "endf_id":     "27-Co-60",
            "badge_class": "badge-red",
            "note":        "⚠️ High-energy gamma — ต้องการ shielding หนา (Pb หรือ concrete)",
            "note_en":     "⚠️ High-energy gamma — requires thick shielding (Pb or concrete)",
        },
        {
            "residual":    "Co-60m",
            "label":       "⁶⁰Co (metastable)",
            "label_en":    "⁶⁰Co (metastable)",
            "half_life":   "10.47 นาที",
            "half_life_en":"10.47 minutes",
            "radiation":   "IT → ⁶⁰Co (γ 58.6 keV)",
            "endf_id":     "27-Co-60m",
            "badge_class": "badge-amber",
            "note":        "สลายตัวเร็วไปเป็น ⁶⁰Co ground state",
            "note_en":     "Quickly decays to ⁶⁰Co ground state",
        },
        {
            "residual":    "Co-58",
            "label":       "⁵⁸Co (จาก (n,2n))",
            "label_en":    "⁵⁸Co (from (n,2n))",
            "half_life":   "70.86 วัน",
            "half_life_en":"70.86 days",
            "radiation":   "β⁺ + γ (810.8 keV)",
            "endf_id":     "27-Co-58",
            "badge_class": "badge-amber",
            "note":        "เกิดจาก (n,2n) reaction — ต้องการนิวตรอนพลังงานสูง (> ~10 MeV)",
            "note_en":     "Produced via (n,2n) reaction — requires high-energy neutrons (> ~10 MeV)",
        },
    ],
    "n-026_Fe_056.endf": [
        {
            "residual":    "Fe-57",
            "label":       "⁵⁷Fe (stable, จาก (n,γ))",
            "label_en":    "⁵⁷Fe (stable, from (n,γ))",
            "half_life":   "Stable",
            "half_life_en":"Stable",
            "radiation":   "—",
            "endf_id":     "26-Fe-57",
            "badge_class": "badge-green",
            "note":        "ผลิตภัณฑ์ที่เสถียร ไม่มีอันตรายทางรังสี",
            "note_en":     "Stable product — no radiation hazard",
        },
        {
            "residual":    "Mn-56",
            "label":       "⁵⁶Mn (จาก (n,p))",
            "label_en":    "⁵⁶Mn (from (n,p))",
            "half_life":   "2.578 ชั่วโมง",
            "half_life_en":"2.578 hours",
            "radiation":   "β⁻ + γ (846.8 keV, 1810.7 keV)",
            "endf_id":     "25-Mn-56",
            "badge_class": "badge-amber",
            "note":        "เกิดจาก (n,p) reaction — สลายตัวเร็ว แต่ gamma energy สูง",
            "note_en":     "Produced via (n,p) reaction — short half-life but high gamma energy",
        },
        {
            "residual":    "Fe-55",
            "label":       "⁵⁵Fe (จาก (n,2n))",
            "label_en":    "⁵⁵Fe (from (n,2n))",
            "half_life":   "2.744 ปี",
            "half_life_en":"2.744 years",
            "radiation":   "EC + X-ray (5.9 keV)",
            "endf_id":     "26-Fe-55",
            "badge_class": "badge-blue",
            "note":        "Low-energy X-ray — อันตรายหลักคือการกินเข้าร่างกาย (internal dose)",
            "note_en":     "Low-energy X-ray — primary hazard is internal dose via ingestion",
        },
    ],
    "n-082_Pb_208.endf": [
        {
            "residual":    "Pb-207",
            "label":       "²⁰⁷Pb (stable, จาก (n,2n))",
            "label_en":    "²⁰⁷Pb (stable, from (n,2n))",
            "half_life":   "Stable",
            "half_life_en":"Stable",
            "radiation":   "—",
            "endf_id":     "82-Pb-207",
            "badge_class": "badge-green",
            "note":        "ผลิตภัณฑ์ที่เสถียร",
            "note_en":     "Stable product",
        },
        {
            "residual":    "Pb-209",
            "label":       "²⁰⁹Pb (จาก (n,γ))",
            "label_en":    "²⁰⁹Pb (from (n,γ))",
            "half_life":   "3.253 ชั่วโมง",
            "half_life_en":"3.253 hours",
            "radiation":   "β⁻ (0.64 MeV) → ²⁰⁹Bi",
            "endf_id":     "82-Pb-209",
            "badge_class": "badge-blue",
            "note":        "Beta emitter เท่านั้น — gamma dose ต่ำ แต่ต้องระวัง skin dose",
            "note_en":     "Beta emitter only — low gamma dose but skin dose is a concern",
        },
    ],
    "n-004_Be_009.endf": [
        {
            "residual":    "Be-10",
            "label":       "¹⁰Be (จาก (n,γ))",
            "label_en":    "¹⁰Be (from (n,γ))",
            "half_life":   "1.387×10⁶ ปี",
            "half_life_en":"1.387×10⁶ years",
            "radiation":   "β⁻ (0.556 MeV)",
            "endf_id":     "4-Be-10",
            "badge_class": "badge-blue",
            "note":        "Half-life ยาวมาก — ความเข้มต่ำ แต่ต้องระวังการปนเปื้อนในระยะยาว",
            "note_en":     "Very long half-life — low activity but long-term contamination concern",
        },
        {
            "residual":    "He-4 + He-4",
            "label":       "²α (จาก (n,2α))",
            "label_en":    "²α (from (n,2α))",
            "half_life":   "Stable",
            "half_life_en":"Stable",
            "radiation":   "Alpha particles",
            "endf_id":     None,
            "badge_class": "badge-amber",
            "note":        "Be-9(n,2α) → alpha particles ปล่อยออกมา — อันตรายถ้าสูดดม Be dust",
            "note_en":     "Be-9(n,2α) → alpha particles released — hazardous if Be dust is inhaled",
        },
    ],
}

# ── Helpers for bilingual product fields ──────────────────────────────────────

def _prod_label(prod: dict) -> str:
    return prod.get("label_en", prod["label"]) if get_lang() == "en" else prod["label"]

def _prod_half_life(prod: dict) -> str:
    return prod.get("half_life_en", prod["half_life"]) if get_lang() == "en" else prod["half_life"]

def _prod_note(prod: dict) -> str:
    return prod.get("note_en", prod.get("note", "")) if get_lang() == "en" else prod.get("note", "")

# ── Source neutron energy presets ─────────────────────────────────────────────
NEUTRON_SOURCES = {
    "AmBe":   {"label": "Am-241/Be (mean 4.5 MeV)",  "mean_MeV": 4.5,  "max_MeV": 11.0},
    "Cf252":  {"label": "Cf-252 (mean 2.13 MeV)",    "mean_MeV": 2.13, "max_MeV": 13.0},
    "custom": {"label_key": "p04_custom_label",        "mean_MeV": 1.0,  "max_MeV": 20.0},
}

def _nsrc_label(k: str) -> str:
    src = NEUTRON_SOURCES[k]
    if "label_key" in src:
        return t(src["label_key"])
    return src["label"]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("☢️ Activation Calculator")
st.markdown(t("p04_desc"))
st.divider()

# ── Check ENDF ────────────────────────────────────────────────────────────────
if not is_endf_available():
    st.error(t("p04_no_endf"))
    st.stop()

# ── Controls ──────────────────────────────────────────────────────────────────
col_ctrl, col_result = st.columns([1, 2.2], gap="large")

with col_ctrl:
    st.markdown(t("p04_target_material"))

    available_targets = {
        fname: AVAILABLE_ENDF_FILES[fname]
        for fname in ACTIVATION_PRODUCTS
        if endf_file_exists(fname)
    }

    if not available_targets:
        st.error(t("p04_no_targets"))
        st.stop()

    selected_target = st.selectbox(
        "Target nucleus",
        options=list(available_targets.keys()),
        format_func=lambda f: available_targets[f],
        help=t("p04_target_help"),
    )

    st.markdown(t("p04_neutron_source"))
    selected_nsrc = st.selectbox(
        "Neutron source",
        options=list(NEUTRON_SOURCES.keys()),
        format_func=_nsrc_label,
    )

    if selected_nsrc == "custom":
        incident_energy_MeV = st.number_input(
            t("p04_incident_energy"),
            min_value=0.001, max_value=20.0,
            value=1.0, step=0.1, format="%.3f",
        )
    else:
        incident_energy_MeV = NEUTRON_SOURCES[selected_nsrc]["mean_MeV"]
        st.info(t("p04_mean_energy_info", incident_energy_MeV))

    incident_energy_eV = incident_energy_MeV * 1e6

    st.markdown(t("p04_xs_plot"))
    e_min_plot = st.number_input(
        "E min (MeV)", min_value=1e-8, max_value=1.0,
        value=1e-5, format="%.2e",
    )
    e_max_plot = st.number_input(
        "E max (MeV)", min_value=1.0, max_value=20.0,
        value=20.0, format="%.1f",
    )
    log_y = st.checkbox("Log scale (Y)", value=True)

# ── Load ENDF ─────────────────────────────────────────────────────────────────
with st.spinner(t("p04_spinner", available_targets[selected_target])):
    endf_dict = load_endf(selected_target)

if endf_dict is None:
    st.error(t("p04_load_error"))
    st.stop()

# ── Results ───────────────────────────────────────────────────────────────────
with col_result:
    products     = ACTIVATION_PRODUCTS.get(selected_target, [])
    target_label = available_targets[selected_target]

    st.markdown(t("p04_products_header", target_label))
    st.markdown(
        f'<div class="info-box">'
        f'Neutron source: <b>{_nsrc_label(selected_nsrc)}</b> &nbsp;·&nbsp; '
        f'Incident energy: <b>{incident_energy_MeV:.3f} MeV</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Energy grid for plot ──
    energies_eV  = make_log_energy_grid(
        e_min_eV=e_min_plot * 1e6,
        e_max_eV=e_max_plot * 1e6,
        n_points=400,
    )
    energies_MeV = eV_to_MeV(energies_eV)

    COLORS = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"]
    fig = go.Figure()
    xs_at_incident = {}

    for i, prod in enumerate(products):
        endf_id = prod.get("endf_id")
        if endf_id is None:
            continue

        xs_arr = get_activation_xs(endf_dict, endf_id, energies_eV)
        if xs_arr is None:
            continue

        color = COLORS[i % len(COLORS)]
        lbl   = _prod_label(prod)

        fig.add_trace(go.Scatter(
            x=energies_MeV, y=xs_arr,
            mode="lines",
            name=lbl,
            line=dict(color=color, width=2),
            hovertemplate=(
                f"<b>{lbl}</b><br>"
                "E: %{x:.4g} MeV<br>"
                "σ: %{y:.4g} barn<extra></extra>"
            ),
        ))

        xs_at_e = get_activation_xs(
            endf_dict, endf_id,
            np.array([incident_energy_eV]),
        )
        if xs_at_e is not None and len(xs_at_e) > 0:
            xs_at_incident[prod["residual"]] = float(xs_at_e[0])

            fig.add_trace(go.Scatter(
                x=[incident_energy_MeV],
                y=[float(xs_at_e[0])],
                mode="markers",
                marker=dict(color=color, size=10, symbol="circle"),
                name=f"{lbl} @ {incident_energy_MeV:.2f} MeV",
                showlegend=False,
                hovertemplate=(
                    f"<b>{lbl}</b><br>"
                    f"E = {incident_energy_MeV:.3f} MeV<br>"
                    f"σ = {float(xs_at_e[0]):.4g} barn<extra></extra>"
                ),
            ))

    fig.add_vline(
        x=incident_energy_MeV,
        line_dash="dash", line_color="#64748b", line_width=1.2,
        annotation_text=f"E = {incident_energy_MeV:.2f} MeV",
        annotation_position="top right",
        annotation_font_size=11,
    )

    fig.update_layout(
        title=dict(text=f"Production Cross Section — {target_label}", font=dict(size=14)),
        xaxis=dict(
            title="Incident Neutron Energy (MeV)",
            type="log",
            showgrid=True, gridcolor="rgba(128,128,128,0.15)",
        ),
        yaxis=dict(
            title="Production Cross Section (barn)",
            type="log" if log_y else "linear",
            showgrid=True, gridcolor="rgba(128,128,128,0.15)",
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
        height=420,
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Activation product detail cards ──────────────────────────────────────────
st.markdown(t("p04_detail_header"))

if not products:
    st.info(t("p04_no_products"))
else:
    cols = st.columns(min(len(products), 3))
    for i, prod in enumerate(products):
        with cols[i % 3]:
            xs_val  = xs_at_incident.get(prod["residual"])
            xs_str  = f"{xs_val:.4g} barn" if xs_val is not None else "—"
            lbl     = _prod_label(prod)
            hl      = _prod_half_life(prod)

            st.markdown(
                f'<div class="result-card">'
                f'<div class="result-name">{lbl}</div>'
                f'<span class="badge {prod["badge_class"]}">{prod["residual"]}</span>'
                f'<br><br>'
                f'<div class="result-label">{t("p04_sigma_label", incident_energy_MeV)}</div>'
                f'<div class="result-xs">{xs_str}</div>'
                f'<br>'
                f'<div class="result-label">{t("p04_half_life_label")}</div>'
                f'<div style="font-size:0.9rem;margin-bottom:6px">{hl}</div>'
                f'<div class="result-label">{t("p04_radiation_label")}</div>'
                f'<div style="font-size:0.88rem;margin-bottom:8px">{prod["radiation"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            note = _prod_note(prod)
            if note:
                st.caption(note)

st.divider()

# ── Summary table ─────────────────────────────────────────────────────────────
if xs_at_incident:
    with st.expander(t("p04_table_expander")):
        rows = []
        for prod in products:
            xs_val = xs_at_incident.get(prod["residual"])
            rows.append({
                t("p04_col_residual"):  prod["residual"],
                t("p04_col_halflife"):  _prod_half_life(prod),
                t("p04_col_radiation"): prod["radiation"],
                t("p04_sigma_label", incident_energy_MeV) + " (barn)":
                    f"{xs_val:.4e}" if xs_val is not None else "N/A",
                t("p04_col_safety"):    _prod_note(prod),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"activation_{target_label.replace('-','_')}_{incident_energy_MeV:.1f}MeV.csv",
            mime="text/csv",
        )

# ── Safety guidance ───────────────────────────────────────────────────────────
with st.expander(t("p04_safety_expander")):
    st.markdown(t("p04_safety_content", target=target_label, energy=incident_energy_MeV))

# ── Link to Nuclear Source Toolkit ───────────────────────────────────────────
st.markdown(t("p04_link_box"), unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(t("p04_footer"))
