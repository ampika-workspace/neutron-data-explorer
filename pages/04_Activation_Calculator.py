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
# (residual, isomer_label, half_life, radiation, safety_note)
ACTIVATION_PRODUCTS = {
    "n-027_Co_059.endf": [
        {
            "residual":    "Co-60",
            "label":       "⁶⁰Co (ground state)",
            "half_life":   "5.271 ปี",
            "radiation":   "β⁻ + γ (1.17 & 1.33 MeV)",
            "endf_id":     "27-Co-60",
            "badge_class": "badge-red",
            "note":        "⚠️ High-energy gamma — ต้องการ shielding หนา (Pb หรือ concrete)",
        },
        {
            "residual":    "Co-60m",
            "label":       "⁶⁰Co (metastable)",
            "half_life":   "10.47 นาที",
            "radiation":   "IT → ⁶⁰Co (γ 58.6 keV)",
            "endf_id":     "27-Co-60m",
            "badge_class": "badge-amber",
            "note":        "สลายตัวเร็วไปเป็น ⁶⁰Co ground state",
        },
        {
            "residual":    "Co-58",
            "label":       "⁵⁸Co (จาก (n,2n))",
            "half_life":   "70.86 วัน",
            "radiation":   "β⁺ + γ (810.8 keV)",
            "endf_id":     "27-Co-58",
            "badge_class": "badge-amber",
            "note":        "เกิดจาก (n,2n) reaction — ต้องการนิวตรอนพลังงานสูง (> ~10 MeV)",
        },
    ],
    "n-026_Fe_056.endf": [
        {
            "residual":    "Fe-57",
            "label":       "⁵⁷Fe (stable, จาก (n,γ))",
            "half_life":   "Stable",
            "radiation":   "—",
            "endf_id":     "26-Fe-57",
            "badge_class": "badge-green",
            "note":        "ผลิตภัณฑ์ที่เสถียร ไม่มีอันตรายทางรังสี",
        },
        {
            "residual":    "Mn-56",
            "label":       "⁵⁶Mn (จาก (n,p))",
            "half_life":   "2.578 ชั่วโมง",
            "radiation":   "β⁻ + γ (846.8 keV, 1810.7 keV)",
            "endf_id":     "25-Mn-56",
            "badge_class": "badge-amber",
            "note":        "เกิดจาก (n,p) reaction — สลายตัวเร็ว แต่ gamma energy สูง",
        },
        {
            "residual":    "Fe-55",
            "label":       "⁵⁵Fe (จาก (n,2n))",
            "half_life":   "2.744 ปี",
            "radiation":   "EC + X-ray (5.9 keV)",
            "endf_id":     "26-Fe-55",
            "badge_class": "badge-blue",
            "note":        "Low-energy X-ray — อันตรายหลักคือการกินเข้าร่างกาย (internal dose)",
        },
    ],
    "n-082_Pb_208.endf": [
        {
            "residual":    "Pb-207",
            "label":       "²⁰⁷Pb (stable, จาก (n,2n))",
            "half_life":   "Stable",
            "radiation":   "—",
            "endf_id":     "82-Pb-207",
            "badge_class": "badge-green",
            "note":        "ผลิตภัณฑ์ที่เสถียร",
        },
        {
            "residual":    "Pb-209",
            "label":       "²⁰⁹Pb (จาก (n,γ))",
            "half_life":   "3.253 ชั่วโมง",
            "radiation":   "β⁻ (0.64 MeV) → ²⁰⁹Bi",
            "endf_id":     "82-Pb-209",
            "badge_class": "badge-blue",
            "note":        "Beta emitter เท่านั้น — gamma dose ต่ำ แต่ต้องระวัง skin dose",
        },
    ],
    "n-004_Be_009.endf": [
        {
            "residual":    "Be-10",
            "label":       "¹⁰Be (จาก (n,γ))",
            "half_life":   "1.387×10⁶ ปี",
            "radiation":   "β⁻ (0.556 MeV)",
            "endf_id":     "4-Be-10",
            "badge_class": "badge-blue",
            "note":        "Half-life ยาวมาก — ความเข้มต่ำ แต่ต้องระวังการปนเปื้อนในระยะยาว",
        },
        {
            "residual":    "He-4 + He-4",
            "label":       "²α (จาก (n,2α))",
            "half_life":   "Stable",
            "radiation":   "Alpha particles",
            "endf_id":     None,
            "badge_class": "badge-amber",
            "note":        "Be-9(n,2α) → alpha particles ปล่อยออกมา — อันตรายถ้าสูดดม Be dust",
        },
    ],
}

# ── Source neutron energy presets ─────────────────────────────────────────────
NEUTRON_SOURCES = {
    "AmBe":   {"label": "Am-241/Be (mean 4.5 MeV)",  "mean_MeV": 4.5,  "max_MeV": 11.0},
    "Cf252":  {"label": "Cf-252 (mean 2.13 MeV)",    "mean_MeV": 2.13, "max_MeV": 13.0},
    "custom": {"label": "กำหนดเอง",                   "mean_MeV": 1.0,  "max_MeV": 20.0},
}

# ── Header ────────────────────────────────────────────────────────────────────
st.title("☢️ Activation Calculator")
st.markdown(
    "คำนวณ **radionuclides ที่เกิดจาก neutron activation** ของวัสดุต่างๆ "
    "พร้อม production cross section จาก **ENDF/B-VIII.0** "
    "และข้อมูลความปลอดภัยทางรังสีสำหรับแต่ละ activation product"
)
st.divider()

# ── Check ENDF ────────────────────────────────────────────────────────────────
if not is_endf_available():
    st.error(
        "**endf-userpy ไม่พร้อมใช้งาน**\n\n"
        "รัน `pip install endf-userpy` แล้วรีสตาร์ทแอปค่ะ"
    )
    st.stop()

# ── Controls ──────────────────────────────────────────────────────────────────
col_ctrl, col_result = st.columns([1, 2.2], gap="large")

with col_ctrl:
    st.markdown("#### Target Material")

    available_targets = {
        fname: AVAILABLE_ENDF_FILES[fname]
        for fname in ACTIVATION_PRODUCTS
        if endf_file_exists(fname)
    }

    if not available_targets:
        st.error("ไม่พบไฟล์ ENDF ที่รองรับใน data/")
        st.stop()

    selected_target = st.selectbox(
        "Target nucleus",
        options=list(available_targets.keys()),
        format_func=lambda f: available_targets[f],
        help="วัสดุที่ถูก activate โดยนิวตรอน",
    )

    st.markdown("#### Neutron Source")
    selected_nsrc = st.selectbox(
        "Neutron source",
        options=list(NEUTRON_SOURCES.keys()),
        format_func=lambda k: NEUTRON_SOURCES[k]["label"],
    )

    if selected_nsrc == "custom":
        incident_energy_MeV = st.number_input(
            "Incident neutron energy (MeV)",
            min_value=0.001, max_value=20.0,
            value=1.0, step=0.1, format="%.3f",
        )
    else:
        incident_energy_MeV = NEUTRON_SOURCES[selected_nsrc]["mean_MeV"]
        st.info(f"Mean energy: **{incident_energy_MeV} MeV**")

    incident_energy_eV = incident_energy_MeV * 1e6

    st.markdown("#### Cross Section Plot")
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
with st.spinner(f"กำลังโหลด {available_targets[selected_target]}..."):
    endf_dict = load_endf(selected_target)

if endf_dict is None:
    st.error("ไม่สามารถโหลดไฟล์ ENDF ได้")
    st.stop()

# ── Results ───────────────────────────────────────────────────────────────────
with col_result:
    products = ACTIVATION_PRODUCTS.get(selected_target, [])
    target_label = available_targets[selected_target]

    st.markdown(f"#### Activation Products ของ {target_label}")
    st.markdown(
        f'<div class="info-box">'
        f'Neutron source: <b>{NEUTRON_SOURCES[selected_nsrc]["label"]}</b> &nbsp;·&nbsp; '
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

    # ── Plot: production XS ──
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
        lbl   = prod["label"]

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

        # XS at incident energy
        xs_at_e = get_activation_xs(
            endf_dict, endf_id,
            np.array([incident_energy_eV]),
        )
        if xs_at_e is not None and len(xs_at_e) > 0:
            xs_at_incident[prod["residual"]] = float(xs_at_e[0])

            # marker
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

    # vertical line at incident energy
    fig.add_vline(
        x=incident_energy_MeV,
        line_dash="dash", line_color="#64748b", line_width=1.2,
        annotation_text=f"E = {incident_energy_MeV:.2f} MeV",
        annotation_position="top right",
        annotation_font_size=11,
    )

    fig.update_layout(
        title=dict(
            text=f"Production Cross Section — {target_label}",
            font=dict(size=14),
        ),
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
st.markdown("#### รายละเอียด Activation Products")

if not products:
    st.info("ยังไม่มีข้อมูล activation products สำหรับ target นี้ค่ะ")
else:
    cols = st.columns(min(len(products), 3))
    for i, prod in enumerate(products):
        with cols[i % 3]:
            xs_val = xs_at_incident.get(prod["residual"])
            xs_str = f"{xs_val:.4g} barn" if xs_val is not None else "—"

            st.markdown(
                f'<div class="result-card">'
                f'<div class="result-name">{prod["label"]}</div>'
                f'<span class="badge {prod["badge_class"]}">{prod["residual"]}</span>'
                f'<br><br>'
                f'<div class="result-label">σ @ {incident_energy_MeV:.2f} MeV</div>'
                f'<div class="result-xs">{xs_str}</div>'
                f'<br>'
                f'<div class="result-label">Half-life</div>'
                f'<div style="font-size:0.9rem;margin-bottom:6px">{prod["half_life"]}</div>'
                f'<div class="result-label">Radiation</div>'
                f'<div style="font-size:0.88rem;margin-bottom:8px">{prod["radiation"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if prod.get("note"):
                st.caption(prod["note"])

st.divider()

# ── Summary table ─────────────────────────────────────────────────────────────
if xs_at_incident:
    with st.expander("📋 ตารางสรุป Activation Products"):
        rows = []
        for prod in products:
            xs_val = xs_at_incident.get(prod["residual"])
            rows.append({
                "Residual":      prod["residual"],
                "Half-life":     prod["half_life"],
                "Radiation":     prod["radiation"],
                f"σ @ {incident_energy_MeV:.2f} MeV (barn)":
                    f"{xs_val:.4e}" if xs_val is not None else "N/A",
                "Safety note":   prod.get("note", ""),
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
with st.expander("🛡️ Radiation Safety — สิ่งที่ต้องระวัง"):
    st.markdown(f"""
**Target: {target_label}** ที่ incident energy {incident_energy_MeV:.2f} MeV

**หลักการ ALARA สำหรับ activated materials:**

1. **ระยะเวลา** — จำกัดเวลาสัมผัสกับวัสดุที่ถูก activate
2. **ระยะห่าง** — เพิ่มระยะห่างจากวัสดุ activated (inverse square law)
3. **การป้องกัน** — ใช้ shielding ที่เหมาะสมกับประเภทรังสีที่ปล่อย
4. **การตรวจวัด** — วัด dose rate ก่อนและหลัง irradiation เสมอ

**คำเตือน:**
- Cross section ที่แสดงเป็นค่าจาก ENDF/B-VIII.0 สำหรับ reaction ที่ระบุ
- Activity จริงขึ้นอยู่กับ neutron flux, irradiation time, และมวลของ target
- ควรปรึกษา Medical Physicist หรือ Radiation Protection Officer
  ก่อนทำงานกับวัสดุที่ผ่าน neutron irradiation
    """)

# ── Link to Nuclear Source Toolkit ───────────────────────────────────────────
st.markdown(
    '<div class="info-box">'
    '🔗 <b>ต้องการคำนวณ dose rate หรือ shielding จาก activated source?</b><br>'
    'ใช้ <a href="https://nuclear-source-toolkit-g5sxa75wivgvrv9axgbnhd.streamlit.app/" '
    'target="_blank">Nuclear Source Toolkit</a> '
    'สำหรับ Dose Rate Calculator และ Shielding Calculator ค่ะ'
    '</div>',
    unsafe_allow_html=True,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    "**Data source:** ENDF/B-VIII.0 via endf-userpy (IAEA-NDS) · "
    "NuDat 3.0 (half-life & decay data) · "
    "**Disclaimer:** Independent tool for educational use — not an official IAEA product. "
    "ข้อมูลนี้ไม่ใช่คำแนะนำทางรังสีวิทยาอย่างเป็นทางการ"
)
