"""
utils/endf_loader.py
--------------------
โหลดและ parse ไฟล์ ENDF-6 ด้วย endf-userpy
Cache ผลลัพธ์ใน Streamlit session state เพื่อไม่ต้อง parse ซ้ำทุกครั้งที่เปลี่ยนหน้า

การใช้งานจากหน้าอื่น:
    from utils.endf_loader import load_endf, get_reactions, get_cross_section

โครงสร้าง session state:
    st.session_state["endf_cache"] = {
        "n-004_Be_009.endf": <endf_dict>,
        "n-098_Cf_252.endf": <endf_dict>,
        ...
    }
"""

import os
import streamlit as st
import numpy as np

# ── endf-userpy imports ────────────────────────────────────────────────────────
try:
    from endf_parserpy import EndfParserFactory
    from endf_userpy.quantities import (
        get_available_reactions,
        get_reaction_xs,
        get_incident_energies,
        get_residual_production_xs,
        get_particle_production_xs,
        get_particle_production_dxs_dE,
    )
    ENDF_AVAILABLE = True
except ImportError:
    ENDF_AVAILABLE = False

# ── Path ไปยังโฟลเดอร์ data/ ──────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# ── ไฟล์ ENDF ที่มีในโปรเจค ───────────────────────────────────────────────────
AVAILABLE_ENDF_FILES = {
    "n-004_Be_009.endf": "Be-9",
    "n-026_Fe_056.endf": "Fe-56",
    "n-027_Co_059.endf": "Co-59",
    "n-082_Pb_208.endf": "Pb-208",
    "n-098_Cf_252.endf": "Cf-252",
}


# ─────────────────────────────────────────────────────────────────────────────
# Core: โหลดและ cache ไฟล์ ENDF
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _get_parser():
    """สร้าง parser ครั้งเดียว แล้ว reuse ตลอด session"""
    if not ENDF_AVAILABLE:
        return None
    return EndfParserFactory.create()


def load_endf(filename: str) -> dict | None:
    """
    โหลดและ parse ไฟล์ ENDF จาก data/ folder
    Cache ผลลัพธ์ใน session state — parse ครั้งเดียวต่อ session

    Parameters
    ----------
    filename : str
        ชื่อไฟล์ เช่น "n-004_Be_009.endf"

    Returns
    -------
    dict | None
        endf_dict ที่ parse แล้ว หรือ None ถ้าเกิด error
    """
    if not ENDF_AVAILABLE:
        return None

    # เช็ค cache ก่อน
    if "endf_cache" not in st.session_state:
        st.session_state["endf_cache"] = {}

    if filename in st.session_state["endf_cache"]:
        return st.session_state["endf_cache"][filename]

    # Parse ไฟล์
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        st.error(f"ไม่พบไฟล์: {filepath}")
        return None

    try:
        parser = _get_parser()
        endf_dict = parser.parsefile(filepath)
        st.session_state["endf_cache"][filename] = endf_dict
        return endf_dict
    except Exception as e:
        st.error(f"ไม่สามารถ parse ไฟล์ {filename}: {e}")
        return None


def load_endf_for_source(source: dict) -> dict | None:
    """
    โหลด ENDF dict สำหรับ source จาก sources_data.py

    Parameters
    ----------
    source : dict
        source entry จาก ALPHA_N_SOURCES, FISSION_SOURCES, หรือ GAMMA_SOURCES

    Returns
    -------
    dict | None
    """
    endf_file = source.get("endf_file")
    if not endf_file:
        return None
    return load_endf(endf_file)


def is_endf_available() -> bool:
    """ตรวจสอบว่า endf-userpy install แล้วและพร้อมใช้งาน"""
    return ENDF_AVAILABLE


def get_endf_file_path(filename: str) -> str:
    """Return full path ของไฟล์ ENDF"""
    return os.path.join(DATA_DIR, filename)


def endf_file_exists(filename: str) -> bool:
    """ตรวจสอบว่าไฟล์ ENDF มีอยู่จริงใน data/"""
    return os.path.exists(os.path.join(DATA_DIR, filename))


# ─────────────────────────────────────────────────────────────────────────────
# Wrapper functions — เรียกใช้ง่ายจากทุกหน้า
# ─────────────────────────────────────────────────────────────────────────────

def get_reactions(endf_dict: dict) -> list[str]:
    """
    ดึงรายการ reactions ที่มีในไฟล์ ENDF

    Returns
    -------
    list[str]
        เช่น ['(n,total)', '(n,elastic)', '(n,2n)', '(n,gamma)', ...]
    """
    if endf_dict is None or not ENDF_AVAILABLE:
        return []
    try:
        return get_available_reactions(endf_dict)
    except Exception as e:
        st.warning(f"ไม่สามารถดึง reactions: {e}")
        return []


def get_cross_section(
    endf_dict: dict,
    reaction: str,
    energies_eV: np.ndarray,
) -> np.ndarray | None:
    """
    ดึง cross section ของ reaction ที่ระบุ

    Parameters
    ----------
    endf_dict : dict
    reaction : str
        เช่น "(n,total)", "(n,gamma)", "(n,2n)"
    energies_eV : np.ndarray
        array ของ incident neutron energies หน่วย eV

    Returns
    -------
    np.ndarray | None
        cross section หน่วย barn
    """
    if endf_dict is None or not ENDF_AVAILABLE:
        return None
    try:
        return get_reaction_xs(endf_dict, reaction, energies_eV)
    except Exception as e:
        st.warning(f"ไม่สามารถดึง cross section สำหรับ {reaction}: {e}")
        return None


def get_energy_grid(endf_dict: dict, reaction: str) -> np.ndarray | None:
    """
    ดึง energy grid ที่ tabulate ไว้สำหรับ reaction นั้นๆ

    Returns
    -------
    np.ndarray | None
        energies หน่วย eV
    """
    if endf_dict is None or not ENDF_AVAILABLE:
        return None
    try:
        return get_incident_energies(endf_dict, reaction)
    except Exception as e:
        st.warning(f"ไม่สามารถดึง energy grid สำหรับ {reaction}: {e}")
        return None


def get_activation_xs(
    endf_dict: dict,
    residual: str,
    energies_eV: np.ndarray,
) -> np.ndarray | None:
    """
    ดึง production cross section ของ residual nucleus (activation)

    Parameters
    ----------
    endf_dict : dict
    residual : str
        เช่น "Co-60", "Co-60m", "27-Co-60"
    energies_eV : np.ndarray

    Returns
    -------
    np.ndarray | None
        cross section หน่วย barn
    """
    if endf_dict is None or not ENDF_AVAILABLE:
        return None
    try:
        return get_residual_production_xs(endf_dict, residual, energies_eV)
    except Exception as e:
        st.warning(f"ไม่สามารถดึง activation XS สำหรับ {residual}: {e}")
        return None


def get_emission_spectrum(
    endf_dict: dict,
    reaction: str,
    particle: str,
    incident_energies_eV: np.ndarray,
    outgoing_energies_eV: np.ndarray,
) -> np.ndarray | None:
    """
    ดึง dσ/dE — energy spectrum ของ particle ที่ปล่อยออกมา

    Parameters
    ----------
    endf_dict : dict
    reaction : str
        เช่น "(n,total)", "(n,f)"
    particle : str
        "n" (neutron), "g" (gamma), "p" (proton), "a" (alpha)
    incident_energies_eV : np.ndarray
        หน่วย eV
    outgoing_energies_eV : np.ndarray
        หน่วย eV

    Returns
    -------
    np.ndarray | None
        dσ/dE หน่วย barn/eV
    """
    if endf_dict is None or not ENDF_AVAILABLE:
        return None
    try:
        return get_particle_production_dxs_dE(
            endf_dict, reaction, particle,
            incident_energies_eV, outgoing_energies_eV,
        )
    except Exception as e:
        st.warning(f"ไม่สามารถดึง emission spectrum: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Energy grid helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_log_energy_grid(
    e_min_eV: float = 1e-5,
    e_max_eV: float = 2e7,
    n_points: int = 500,
) -> np.ndarray:
    """
    สร้าง log-spaced energy grid

    Parameters
    ----------
    e_min_eV : float   ค่า default = 0.025 meV (thermal)
    e_max_eV : float   ค่า default = 20 MeV
    n_points : int

    Returns
    -------
    np.ndarray หน่วย eV
    """
    return np.logspace(np.log10(e_min_eV), np.log10(e_max_eV), n_points)


def eV_to_MeV(energies_eV: np.ndarray) -> np.ndarray:
    """แปลง eV → MeV"""
    return energies_eV * 1e-6


def MeV_to_eV(energies_MeV: np.ndarray) -> np.ndarray:
    """แปลง MeV → eV"""
    return energies_MeV * 1e6


# ─────────────────────────────────────────────────────────────────────────────
# Status display helper
# ─────────────────────────────────────────────────────────────────────────────

def show_endf_status():
    """
    แสดงสถานะ endf-userpy ใน sidebar
    เรียกจาก app.py หรือทุกหน้าที่ต้องการ
    """
    if not ENDF_AVAILABLE:
        st.sidebar.error(
            "⚠️ endf-userpy ไม่พร้อมใช้งาน\n\n"
            "รัน: `pip install endf-userpy`"
        )
        return

    cached = st.session_state.get("endf_cache", {})
    if cached:
        st.sidebar.success(f"✅ ENDF loaded: {len(cached)} ไฟล์")
    else:
        st.sidebar.info("📂 ยังไม่ได้โหลดไฟล์ ENDF")
