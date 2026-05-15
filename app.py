import re
import streamlit as st
from utils.sources_data import (
    ALPHA_N_SOURCES,
    FISSION_SOURCES,
    GAMMA_SOURCES,
    CATEGORY_LABELS,
)
from utils.endf_loader import is_endf_available, show_endf_status


def _page_slug(page_path: str) -> str:
    """Derive Streamlit MPA URL from a pages/ file path (e.g. pages/01_Foo.py → /Foo)."""
    name = page_path.split("/")[-1].replace(".py", "")
    return "/" + re.sub(r"^\d+_", "", name)


APP_VERSION = "1.0.0"
APP_UPDATED = "May 2026"

st.set_page_config(
    page_title="Neutron Data Explorer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.tool-card {
    background-color: var(--secondary-background-color, #f8fafc);
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 12px;
    padding: 22px 24px 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s ease;
    margin-bottom: 4px;
    box-sizing: border-box;
    width: 100%;
    overflow: hidden;
}
.tool-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.13); }
.coming-soon-card {
    background: repeating-linear-gradient(
        45deg,
        var(--secondary-background-color, #f8fafc) 0px,
        var(--secondary-background-color, #f8fafc) 10px,
        rgba(128,128,128,0.06) 10px,
        rgba(128,128,128,0.06) 20px
    );
    border: 1.5px dashed rgba(128,128,128,0.35);
    border-radius: 12px;
    padding: 22px 24px 18px;
    margin-bottom: 4px;
    box-sizing: border-box;
    width: 100%;
    overflow: hidden;
}
.source-badge {
    display: inline-block;
    background: rgba(37,99,235,0.1);
    color: #2563eb;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.76rem;
    font-weight: 600;
    margin: 2px 3px 2px 0;
    white-space: nowrap;
}
.source-badge-warn {
    background: rgba(220,38,38,0.1);
    color: #dc2626;
}
.source-badge-fission {
    background: rgba(217,119,6,0.1);
    color: #d97706;
}
.source-badge-gamma {
    background: rgba(5,150,105,0.1);
    color: #059669;
}
.card-icon  { font-size: 2rem; margin-bottom: 10px; line-height: 1; }
.card-title { font-size: 1.1rem; font-weight: 700;
              color: var(--text-color, #1e293b); margin-bottom: 6px; }
.card-desc  { font-size: 0.88rem; color: var(--text-color, #64748b);
              opacity: 0.75; line-height: 1.55; margin-bottom: 14px; }
.card-tags  { display: flex; flex-wrap: wrap; gap: 5px; }
.tag {
    background: rgba(37,99,235,0.1);
    color: #2563eb;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.76rem;
    font-weight: 500;
    white-space: nowrap;
}
.tag-soon {
    background: rgba(22,163,74,0.1);
    color: #16a34a;
}
.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-color, #94a3b8);
    opacity: 0.7;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚛️ Neutron Data Explorer")
    st.caption(f"v{APP_VERSION} · Updated {APP_UPDATED}")
    st.divider()
    st.markdown("**Quick Navigation**")
    st.page_link("pages/01_Source_Library.py",        label="📚 Source Library")
    st.page_link("pages/02_Reaction_Explorer.py",     label="⚛️ Reaction Explorer")
    st.page_link("pages/03_Neutron_Spectrum.py",      label="📊 Neutron Spectrum")
    st.page_link("pages/04_Activation_Calculator.py", label="☢️ Activation Calculator")

    st.divider()
    st.markdown("**Related App**")
    st.markdown(
        "🔗 [Nuclear Source Toolkit]"
        "(https://nuclear-source-toolkit-g5sxa75wivgvrv9axgbnhd.streamlit.app/)",
        unsafe_allow_html=False,
    )

    st.divider()
    show_endf_status()


# ── Header ────────────────────────────────────────────────────────────────────
hdr_left, hdr_right = st.columns([6, 1])
with hdr_left:
    st.title("⚛️ Neutron Data Explorer")
    st.markdown(
        "Nuclear reaction data powered by **[ENDF/B-VIII.0](https://www.nndc.bnl.gov/endf-b8.0/)** "
        "via **[endf-userpy](https://github.com/IAEA-NDS/endf-userpy)** (IAEA-NDS). "
        "Explore cross sections, neutron spectra, and activation products for neutron sources "
        "used in radiation safety and research."
    )
with hdr_right:
    endf_ok = is_endf_available()
    if endf_ok:
        st.markdown(
            '<div style="text-align:right;padding-top:20px;">'
            '<span style="color:#16a34a;font-weight:600;font-size:0.95rem;">● ENDF Ready</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align:right;padding-top:20px;">'
            '<span style="color:#d97706;font-weight:600;font-size:0.95rem;">● ENDF Unavailable</span>'
            '</div>',
            unsafe_allow_html=True,
        )

st.divider()


# ── Card helpers ──────────────────────────────────────────────────────────────
def _tags(items: list[str], extra_class: str = "") -> str:
    return "".join(f'<span class="tag {extra_class}">{t}</span>' for t in items)


def tool_card(
    icon: str, title: str, desc: str,
    tags: list[str], page_path: str = "",
) -> str:
    inner = (
        f'<div class="tool-card">'
        f'<div class="card-icon">{icon}</div>'
        f'<div class="card-title">{title}</div>'
        f'<div class="card-desc">{desc}</div>'
        f'<div class="card-tags">{_tags(tags)}</div>'
        f'</div>'
    )
    if page_path:
        href = _page_slug(page_path)
        return (
            f'<a href="{href}" target="_self" '
            f'style="text-decoration:none;display:block;color:inherit;width:100%;overflow:hidden;">'
            f'{inner}</a>'
        )
    return inner


def coming_soon_card(icon: str, title: str, desc: str, tags: list[str]) -> str:
    return (
        f'<div class="coming-soon-card">'
        f'<div class="card-icon">{icon}</div>'
        f'<div class="card-title" style="opacity:0.65;">{title}</div>'
        f'<div class="card-desc">{desc}</div>'
        f'<div class="card-tags">{_tags(tags, "tag-soon")}</div>'
        f'</div>'
    )


# ── Section: Tools ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Tools</div>', unsafe_allow_html=True)

r1c1, r1c2 = st.columns(2, gap="large")
with r1c1:
    st.markdown(tool_card(
        "📚", "Source Library",
        "Browse all supported neutron and gamma reference sources. "
        "View nuclear properties, neutron yield, half-life, common uses, "
        "and safety notes including legacy warnings.",
        ["(α,n) sources", "Spontaneous fission", "Gamma reference", "ISO 8529-1"],
        page_path="pages/01_Source_Library.py",
    ), unsafe_allow_html=True)

with r1c2:
    st.markdown(tool_card(
        "⚛️", "Reaction Explorer",
        "Explore neutron-induced reactions on any target nucleus. "
        "Plot cross section vs. energy from ENDF/B-VIII.0 data, "
        "compare reactions, and identify dominant interaction channels.",
        ["Cross section", "ENDF/B-VIII.0", "Be-9 · Fe-56 · Co-59 · Pb-208", "Interactive plot"],
        page_path="pages/02_Reaction_Explorer.py",
    ), unsafe_allow_html=True)

st.divider()

r2c1, r2c2 = st.columns(2, gap="large")
with r2c1:
    st.markdown(tool_card(
        "📊", "Neutron Spectrum",
        "Visualise the energy spectrum of neutrons emitted from "
        "Am-241/Be, Cf-252, and other sources. Compare spectra side-by-side "
        "and explore how incident energy affects the emission distribution.",
        ["Am-241/Be", "Cf-252 Watt spectrum", "Spectrum comparison", "ENDF-based"],
        page_path="pages/03_Neutron_Spectrum.py",
    ), unsafe_allow_html=True)

with r2c2:
    st.markdown(tool_card(
        "☢️", "Activation Calculator",
        "Calculate which radionuclides are produced when neutrons activate "
        "a target material. Isomer-resolved production cross sections for "
        "Co-59 → Co-60g/m and other key activation products.",
        ["Activation products", "Isomer resolution", "Co-59 · Fe-56", "Production XS"],
        page_path="pages/04_Activation_Calculator.py",
    ), unsafe_allow_html=True)

st.divider()


# ── Section: Sources in this app ──────────────────────────────────────────────
st.markdown('<div class="section-label">Radioactive Sources in This App</div>', unsafe_allow_html=True)

col_an, col_sf, col_gr = st.columns(3, gap="large")

with col_an:
    st.markdown(f"**{CATEGORY_LABELS['alpha_n']}**")
    for s in ALPHA_N_SOURCES:
        badge_class = "source-badge source-badge-warn" if s.get("legacy_warning") else "source-badge"
        safeguards = " 🔒" if s.get("safeguards") else ""
        legacy = " ⚠️ Legacy" if s.get("legacy_warning") else ""
        st.markdown(
            f'<span class="{badge_class}">{s["symbol"]}{safeguards}{legacy}</span>',
            unsafe_allow_html=True,
        )

with col_sf:
    st.markdown(f"**{CATEGORY_LABELS['spontaneous_fission']}**")
    for s in FISSION_SOURCES:
        st.markdown(
            f'<span class="source-badge source-badge-fission">{s["symbol"]}</span>',
            unsafe_allow_html=True,
        )

with col_gr:
    st.markdown(f"**{CATEGORY_LABELS['gamma_reference']}**")
    for s in GAMMA_SOURCES:
        st.markdown(
            f'<span class="source-badge source-badge-gamma">{s["symbol"]}</span>',
            unsafe_allow_html=True,
        )

st.divider()


# ── Section: Data source info ─────────────────────────────────────────────────
st.markdown('<div class="section-label">Data Sources</div>', unsafe_allow_html=True)

info_col1, info_col2 = st.columns(2, gap="large")
with info_col1:
    st.info(
        "**Nuclear Reaction Data**\n\n"
        "ENDF/B-VIII.0 via [endf-userpy](https://github.com/IAEA-NDS/endf-userpy) (IAEA-NDS) · "
        "Cross sections, spectra, and activation data are read directly from local ENDF-6 files."
    )
with info_col2:
    st.info(
        "**Source Properties**\n\n"
        "ISO 8529-1:2021 · IAEA-TECDOC-465 · NuDat 3.0 (NNDC) · "
        "Half-life, neutron yield, and gamma data are sourced from peer-reviewed references."
    )

st.divider()


# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    f"**v{APP_VERSION}** · Last updated {APP_UPDATED}  ·  "
    "**Disclaimer:** Independent tool for educational and laboratory use — not an official IAEA product.  "
    "Nuclear data sourced from [IAEA NDS](https://nds.iaea.org) and "
    "[NNDC ENDF/B-VIII.0](https://www.nndc.bnl.gov/endf-b8.0/)."
)
