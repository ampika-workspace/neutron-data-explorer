"""
pages/02_Reaction_Explorer.py
-----------------------------
Reaction Explorer — Cross section vs energy จากไฟล์ ENDF/B-VIII.0
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.endf_loader import (
    load_endf,
    get_reactions,
    get_cross_section,
    get_energy_grid,
    make_log_energy_grid,
    eV_to_MeV,
    is_endf_available,
    show_endf_status,
    AVAILABLE_ENDF_FILES,
    endf_file_exists,
)

st.set_page_config(
    page_title="Reaction Explorer — Neutron Data Explorer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.prop-label {
    font-size: 0.78rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em;
    opacity: 0.55; margin-bottom: 2px;
}
.info-box {
    background: rgba(37,99,235,0.06);
    border-left: 3px solid rgba(37,99,235,0.5);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 12px;
    font-size: 0.88rem;
    line-height: 1.6;
}
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


# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚛️ Reaction Explorer")
st.markdown(
    "Cross section ของ neutron-induced reactions จากไฟล์ **ENDF/B-VIII.0** "
    "ผ่าน [endf-userpy](https://github.com/IAEA-NDS/endf-userpy) (IAEA-NDS)"
)
st.divider()

# ── Check ENDF availability ───────────────────────────────────────────────────
if not is_endf_available():
    st.error(
        "**endf-userpy ไม่พร้อมใช้งาน**\n\n"
        "รัน `pip install endf-userpy` แล้วรีสตาร์ทแอปค่ะ"
    )
    st.stop()

# ── Target nucleus selector ───────────────────────────────────────────────────
available = {
    fname: label
    for fname, label in AVAILABLE_ENDF_FILES.items()
    if endf_file_exists(fname)
}

if not available:
    st.error("ไม่พบไฟล์ ENDF ใน data/ กรุณา upload ไฟล์ก่อนค่ะ")
    st.stop()

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.markdown("#### เลือก Target Nucleus")

    selected_file = st.selectbox(
        "Target nucleus",
        options=list(available.keys()),
        format_func=lambda f: available[f],
        help="Nucleus ที่นิวตรอนจะเข้าทำปฏิกิริยาด้วย",
    )

    # ── Load ENDF ──
    with st.spinner(f"กำลังโหลด {available[selected_file]}..."):
        endf_dict = load_endf(selected_file)

    if endf_dict is None:
        st.error("ไม่สามารถโหลดไฟล์ ENDF ได้")
        st.stop()

    # ── Reaction list ──
    reactions = get_reactions(endf_dict)
    if not reactions:
        st.warning("ไม่พบ reactions ในไฟล์นี้")
        st.stop()

    st.success(f"✅ โหลดสำเร็จ — พบ {len(reactions)} reactions")

    # ── Multi-select reactions ──
    st.markdown("#### เลือก Reactions")

    # Default: แสดง reactions ที่น่าสนใจก่อน
    default_reactions = [r for r in reactions if r in [
        "(n,total)", "(n,elastic)", "(n,inelastic)",
        "(n,2n)", "(n,gamma)", "(n,p)", "(n,a)",
    ]]
    if not default_reactions:
        default_reactions = reactions[:3]

    selected_reactions = st.multiselect(
        "Reactions",
        options=reactions,
        default=default_reactions[:4],
        help="เลือกได้หลาย reactions เพื่อเปรียบเทียบกัน",
    )

    st.markdown("#### Energy Range")
    e_min_MeV = st.number_input(
        "E min (MeV)", min_value=1e-9, max_value=1.0,
        value=1e-5, format="%.2e",
        help="พลังงานต่ำสุด (thermal neutron ≈ 0.025 eV = 2.5×10⁻⁸ MeV)",
    )
    e_max_MeV = st.number_input(
        "E max (MeV)", min_value=0.1, max_value=20.0,
        value=20.0, format="%.1f",
        help="พลังงานสูงสุด (14 MeV = D-T generator, 20 MeV = ENDF limit)",
    )
    n_points = st.slider("จำนวน energy points", 100, 1000, 300, 50)

    # ── Y-axis scale ──
    log_y = st.checkbox("Log scale (Y axis)", value=True)
    log_x = st.checkbox("Log scale (X axis)", value=True)

# ── Plot ──────────────────────────────────────────────────────────────────────
with col_right:
    if not selected_reactions:
        st.info("เลือก reaction อย่างน้อย 1 ตัวจากแถบซ้ายค่ะ")
        st.stop()

    energies_eV = make_log_energy_grid(
        e_min_eV=e_min_MeV * 1e6,
        e_max_eV=e_max_MeV * 1e6,
        n_points=n_points,
    )
    energies_MeV = eV_to_MeV(energies_eV)

    # ── สีสำหรับแต่ละ reaction ──
    COLORS = [
        "#2563eb", "#dc2626", "#16a34a", "#d97706",
        "#7c3aed", "#0891b2", "#db2777", "#65a30d",
    ]

    fig = go.Figure()
    xs_data = {}
    error_reactions = []

    with st.spinner("กำลังคำนวณ cross sections..."):
        for i, rxn in enumerate(selected_reactions):
            xs = get_cross_section(endf_dict, rxn, energies_eV)
            if xs is None:
                error_reactions.append(rxn)
                continue

            xs_data[rxn] = xs
            color = COLORS[i % len(COLORS)]

            fig.add_trace(go.Scatter(
                x=energies_MeV,
                y=xs,
                mode="lines",
                name=rxn,
                line=dict(color=color, width=1.8),
                hovertemplate=(
                    f"<b>{rxn}</b><br>"
                    "Energy: %{x:.4g} MeV<br>"
                    "σ: %{y:.4g} barn<extra></extra>"
                ),
            ))

    if error_reactions:
        st.warning(f"ไม่สามารถคำนวณ: {', '.join(error_reactions)}")

    # ── Layout ──
    fig.update_layout(
        title=dict(
            text=f"Neutron Cross Sections — {available[selected_file]}",
            font=dict(size=15),
        ),
        xaxis=dict(
            title="Incident Neutron Energy (MeV)",
            type="log" if log_x else "linear",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
        ),
        yaxis=dict(
            title="Cross Section (barn)",
            type="log" if log_y else "linear",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
        ),
        legend=dict(
            orientation="v",
            x=1.01, y=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=20, t=50, b=60),
        height=520,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Reference lines ──
    st.markdown(
        '<div class="info-box">'
        '⚡ <b>Energy references:</b> '
        'Thermal neutron = 0.025 eV (2.5×10⁻⁸ MeV) &nbsp;·&nbsp; '
        'Am-241/Be mean = 4.5 MeV &nbsp;·&nbsp; '
        'Cf-252 mean = 2.13 MeV &nbsp;·&nbsp; '
        'D-T generator = 14.1 MeV'
        '</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ── Data table ────────────────────────────────────────────────────────────────
if xs_data:
    with st.expander("📋 ดูตารางข้อมูล (sample points)"):
        import pandas as pd

        # sample 20 points
        idx = np.linspace(0, len(energies_MeV) - 1, 20, dtype=int)
        df_data = {"Energy (MeV)": energies_MeV[idx]}
        for rxn, xs in xs_data.items():
            df_data[f"{rxn} (barn)"] = xs[idx]

        df = pd.DataFrame(df_data)
        st.dataframe(
            df.style.format({
                "Energy (MeV)": "{:.4e}",
                **{col: "{:.4e}" for col in df.columns if "barn" in col},
            }),
            use_container_width=True,
        )

        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"cross_section_{available[selected_file].replace('-','_')}.csv",
            mime="text/csv",
        )

# ── Reaction reference ────────────────────────────────────────────────────────
with st.expander("📖 คำอธิบาย Reaction Notation"):
    st.markdown("""
| Notation | ความหมาย |
|----------|-----------|
| `(n,total)` | Total cross section — ผลรวมทุก reactions |
| `(n,elastic)` หรือ `(n,n_0)` | Elastic scattering — นิวตรอนกระเด็งออกโดยไม่เปลี่ยน nucleus |
| `(n,inelastic)` | Inelastic scattering — nucleus ถูก excite |
| `(n,gamma)` หรือ `(n,g)` | Radiative capture — nucleus ดูดนิวตรอนและปล่อย gamma |
| `(n,2n)` | นิวตรอนชน → ได้ 2 นิวตรอนออกมา |
| `(n,p)` | นิวตรอนชน → ได้ proton ออกมา |
| `(n,a)` | นิวตรอนชน → ได้ alpha particle ออกมา |
| `(n,f)` | Fission — nucleus แตกออก (เฉพาะ fissile/fissionable nuclei) |
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    "**Data source:** ENDF/B-VIII.0 via endf-userpy (IAEA-NDS) · "
    "**Disclaimer:** Independent tool for educational use — not an official IAEA product."
)
