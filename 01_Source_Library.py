"""
pages/01_Source_Library.py
--------------------------
Source Library — รายละเอียด radioactive sources ทั้งหมดในแอป
"""

import streamlit as st
from utils.sources_data import (
    ALL_SOURCES,
    ALPHA_N_SOURCES,
    FISSION_SOURCES,
    GAMMA_SOURCES,
    CATEGORY_LABELS,
    CATEGORY_ORDER,
    get_sources_by_category,
    get_half_life_display,
)
from utils.endf_loader import endf_file_exists, show_endf_status

st.set_page_config(
    page_title="Source Library — Neutron Data Explorer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.source-card {
    background-color: var(--secondary-background-color, #f8fafc);
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 12px;
    padding: 20px 22px 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.source-card-legacy {
    border: 1.5px solid rgba(220,38,38,0.35);
    background: rgba(220,38,38,0.03);
}
.source-name {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-color, #1e293b);
    margin-bottom: 2px;
}
.source-symbol {
    font-size: 0.95rem;
    opacity: 0.6;
    margin-bottom: 10px;
}
.prop-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.55;
    margin-bottom: 2px;
}
.prop-value {
    font-size: 0.92rem;
    margin-bottom: 10px;
}
.badge {
    display: inline-block;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.74rem;
    font-weight: 600;
    margin: 2px 3px 2px 0;
    white-space: nowrap;
}
.badge-blue   { background:rgba(37,99,235,0.1);  color:#2563eb; }
.badge-red    { background:rgba(220,38,38,0.1);  color:#dc2626; }
.badge-amber  { background:rgba(217,119,6,0.1);  color:#d97706; }
.badge-green  { background:rgba(5,150,105,0.1);  color:#059669; }
.badge-gray   { background:rgba(100,116,139,0.1);color:#64748b; }
.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.6;
    margin-bottom: 8px;
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

    # ── Filter ──
    st.markdown("**Filter**")
    selected_category = st.selectbox(
        "Category",
        options=["All"] + CATEGORY_ORDER,
        format_func=lambda x: "All Categories" if x == "All" else CATEGORY_LABELS.get(x, x),
    )
    show_legacy = st.checkbox("แสดง Legacy sources", value=True)
    show_safeguards = st.checkbox("แสดง Safeguards sources", value=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.title("📚 Source Library")
st.markdown(
    "รายละเอียด radioactive sources ทั้งหมดที่รองรับในแอปนี้ "
    "ข้อมูลอ้างอิงจาก **ISO 8529-1:2021**, **IAEA-TECDOC-465**, และ **NuDat 3.0**"
)
st.divider()


# ── Summary badges ────────────────────────────────────────────────────────────
total = len(ALL_SOURCES)
n_an  = len(ALPHA_N_SOURCES)
n_sf  = len(FISSION_SOURCES)
n_gr  = len(GAMMA_SOURCES)
n_endf = sum(1 for s in ALL_SOURCES if s.get("endf_file") and endf_file_exists(s["endf_file"]))

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Sources ทั้งหมด", total)
m2.metric("(α,n) Sources",   n_an)
m3.metric("Spontaneous Fission", n_sf)
m4.metric("Gamma Reference", n_gr)
m5.metric("มีไฟล์ ENDF ✅",  n_endf)

st.divider()


# ── Helper: render source card ────────────────────────────────────────────────
def _render_source_card(source: dict):
    is_legacy = source.get("legacy_warning", False)
    card_class = "source-card source-card-legacy" if is_legacy else "source-card"
    cat = source.get("category", "")

    # ── header badges ──
    badges = []
    if is_legacy:
        badges.append('<span class="badge badge-red">⚠️ Legacy</span>')
    if source.get("safeguards"):
        badges.append('<span class="badge badge-amber">🔒 IAEA Safeguards</span>')
    if source.get("endf_file") and endf_file_exists(source["endf_file"]):
        badges.append('<span class="badge badge-green">✅ ENDF Available</span>')
    elif source.get("endf_file"):
        badges.append('<span class="badge badge-gray">📂 ENDF file missing</span>')
    else:
        badges.append('<span class="badge badge-gray">Static data only</span>')

    badge_html = " ".join(badges)

    st.markdown(
        f'<div class="{card_class}">'
        f'<div class="source-name">{source["name"]}</div>'
        f'<div class="source-symbol">{source["symbol"]}</div>'
        f'{badge_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── properties grid ──
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="prop-label">Half-life</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="prop-value">{get_half_life_display(source)}</div>',
            unsafe_allow_html=True,
        )

        if cat in ("alpha_n", "spontaneous_fission"):
            st.markdown('<div class="prop-label">Mean neutron energy</div>', unsafe_allow_html=True)
            mean_e = source.get("mean_neutron_energy_MeV")
            st.markdown(
                f'<div class="prop-value">{mean_e} MeV</div>' if mean_e
                else '<div class="prop-value">—</div>',
                unsafe_allow_html=True,
            )

        if cat == "alpha_n":
            st.markdown('<div class="prop-label">Max neutron energy</div>', unsafe_allow_html=True)
            max_e = source.get("max_neutron_energy_MeV")
            st.markdown(
                f'<div class="prop-value">{max_e} MeV</div>' if max_e
                else '<div class="prop-value">—</div>',
                unsafe_allow_html=True,
            )

    with col2:
        if cat == "alpha_n":
            st.markdown('<div class="prop-label">Alpha emitter</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="prop-value">{source.get("alpha_emitter", "—")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="prop-label">Target nucleus</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="prop-value">{source.get("target_nucleus", "—")}</div>',
                unsafe_allow_html=True,
            )
            yield_val = source.get("neutron_yield_n_s_per_GBq")
            if yield_val:
                st.markdown('<div class="prop-label">Neutron yield</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="prop-value">{yield_val:.2e} n/s/GBq</div>',
                    unsafe_allow_html=True,
                )

        elif cat == "spontaneous_fission":
            sf = source.get("sf_branching_ratio")
            if sf:
                st.markdown('<div class="prop-label">SF branching ratio</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="prop-value">{sf*100:.4f}%</div>',
                    unsafe_allow_html=True,
                )
            yield_ug = source.get("neutron_yield_per_ug")
            if yield_ug:
                st.markdown('<div class="prop-label">Neutron yield</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="prop-value">{yield_ug:.3e} n/s/µg</div>',
                    unsafe_allow_html=True,
                )

        elif cat == "gamma_reference":
            gammas = source.get("principal_gamma_keV", [])
            intens = source.get("gamma_intensity_pct", [])
            if gammas:
                st.markdown('<div class="prop-label">Principal gamma lines</div>', unsafe_allow_html=True)
                lines = ", ".join(
                    f"{e} keV ({i}%)" for e, i in zip(gammas, intens)
                )
                st.markdown(f'<div class="prop-value">{lines}</div>', unsafe_allow_html=True)

            dr = source.get("dose_rate_const_uSv_h_per_GBq_1m")
            if dr:
                st.markdown('<div class="prop-label">Dose rate constant</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="prop-value">{dr} µSv/h per GBq @ 1 m</div>',
                    unsafe_allow_html=True,
                )

    with col3:
        uses = source.get("common_uses", [])
        if uses:
            st.markdown('<div class="prop-label">Common uses</div>', unsafe_allow_html=True)
            for u in uses:
                st.markdown(f"• {u}")

        gamma_cont = source.get("gamma_contamination")
        if gamma_cont and cat != "gamma_reference":
            st.markdown('<div class="prop-label">Gamma contamination</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="prop-value">{gamma_cont}</div>', unsafe_allow_html=True)

    # ── notes ──
    notes = source.get("notes")
    if notes:
        if is_legacy:
            st.warning(notes)
        else:
            with st.expander("📝 Notes & References"):
                st.markdown(notes)
                ref = source.get("reference")
                if ref:
                    st.caption(f"Reference: {ref}")

    st.markdown("---")


# ── Filter sources ────────────────────────────────────────────────────────────
if selected_category == "All":
    sources_to_show = ALL_SOURCES
else:
    sources_to_show = get_sources_by_category(selected_category)

if not show_legacy:
    sources_to_show = [s for s in sources_to_show if not s.get("legacy_warning")]
if not show_safeguards:
    sources_to_show = [s for s in sources_to_show if not s.get("safeguards")]


# ── Render by category ────────────────────────────────────────────────────────
if not sources_to_show:
    st.info("ไม่พบ source ที่ตรงกับ filter ที่เลือก")
else:
    current_cat = None
    for source in sources_to_show:
        cat = source.get("category")
        if cat != current_cat:
            current_cat = cat
            st.markdown(
                f'<div class="section-label">{CATEGORY_LABELS.get(cat, cat)}</div>',
                unsafe_allow_html=True,
            )
        _render_source_card(source)


# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    "**Disclaimer:** Independent tool for educational and laboratory use — not an official IAEA product.  "
    "Data sourced from ISO 8529-1:2021, IAEA-TECDOC-465, NuDat 3.0, and peer-reviewed references."
)
