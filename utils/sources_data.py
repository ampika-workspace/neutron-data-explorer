"""
utils/sources_data.py
---------------------
ข้อมูล radioactive sources สำหรับ Neutron Data Explorer

ที่มาของข้อมูล (References):
  [1] ISO 8529-1:2021 — Reference neutron radiations
  [2] IAEA-TECDOC-465 (1988) — Neutron sources for calibration
  [3] IAEA Safety Reports Series No. 2 (1998) — Industrial radiography
  [4] NCRP Report No. 144 (2003) — Radiation protection
  [5] Knoll, G.F. — Radiation Detection and Measurement, 4th Ed.
  [6] NuDat 3.0 — https://www.nndc.bnl.gov/nudat3/

วิธีเพิ่ม source ใหม่:
  1. Copy entry ที่มีอยู่แล้ว
  2. แก้ค่าให้ถูกต้อง
  3. Save — แอปจะแสดงผลอัตโนมัติ
"""

# ─────────────────────────────────────────────────────────────────
# (α,n) SOURCES
# ─────────────────────────────────────────────────────────────────
ALPHA_N_SOURCES = [
    {
        # ── Identity ──────────────────────────────────────────────
        "id":            "AmBe",
        "name":          "Am-241/Be",
        "symbol":        "²⁴¹Am/Be",
        "category":      "alpha_n",
        "endf_file":     "n-004_Be_009.endf",   # target nucleus

        # ── Nuclear properties (Ref: ISO 8529-1, NuDat 3.0) ──────
        "alpha_emitter":          "Am-241",
        "target_nucleus":         "Be-9",
        "half_life_years":        432.2,         # Am-241 [NuDat 3.0]
        "alpha_energy_MeV":       5.486,         # weighted mean [NuDat 3.0]
        "mean_neutron_energy_MeV": 4.5,          # [ISO 8529-1]
        "max_neutron_energy_MeV":  11.0,         # [ISO 8529-1]
        "neutron_yield_n_s_per_GBq": 6.6e4,     # [ISO 8529-1] ~2.2×10⁶ n/s/Ci

        # ── Gamma contamination ───────────────────────────────────
        "gamma_contamination":    "ต่ำ — 59.5 keV จาก Am-241 เท่านั้น",
        "prompt_gamma_MeV":       4.44,          # จาก ¹²C* de-excitation

        # ── Practical info ────────────────────────────────────────
        "typical_activity_range": "mCi – Ci",
        "common_uses": [
            "Neutron calibration source (ISO 8529-1 reference field)",
            "Moisture gauge",
            "Well logging",
            "Neutron generator project",
        ],

        # ── Status ────────────────────────────────────────────────
        "status":          "active",
        "legacy_warning":  False,
        "safeguards":      False,
        "notes": (
            "ISO 8529-1 reference source มาตรฐานสากล "
            "Spectrum กว้าง peak ที่ ~4–5 MeV "
            "Gamma contamination ต่ำที่สุดในบรรดา (α,n) sources"
        ),
        "reference": "ISO 8529-1:2021; IAEA-TECDOC-465",
    },
    {
        "id":            "PuBe238",
        "name":          "Pu-238/Be",
        "symbol":        "²³⁸Pu/Be",
        "category":      "alpha_n",
        "endf_file":     "n-004_Be_009.endf",

        "alpha_emitter":          "Pu-238",
        "target_nucleus":         "Be-9",
        "half_life_years":        87.7,          # [NuDat 3.0]
        "alpha_energy_MeV":       5.489,         # weighted mean [NuDat 3.0]
        "mean_neutron_energy_MeV": 4.5,          # spectrum คล้าย Am-Be [Ref 5]
        "max_neutron_energy_MeV":  11.0,
        "neutron_yield_n_s_per_GBq": 6.4e4,     # ใกล้เคียง Am-Be [Ref 5]

        "gamma_contamination":    "ต่ำมาก — Pu-238 เป็น α emitter เป็นหลัก",
        "prompt_gamma_MeV":       4.44,

        "typical_activity_range": "Ci range",
        "common_uses": [
            "Space power systems (RTG)",
            "Industrial neutron source",
            "Well logging",
        ],

        "status":         "active",
        "legacy_warning": False,
        "safeguards":     True,   # Pu content → IAEA safeguards
        "notes": (
            "Half-life ยาว (87.7 ปี) เหมาะกับงานระยะยาว "
            "Spectrum คล้าย Am-241/Be มาก (alpha energy ต่างกันเพียง ~10 keV) "
            "⚠️ อยู่ภายใต้ IAEA safeguards เนื่องจากมี Pu"
        ),
        "reference": "NuDat 3.0; arXiv:1611.00213",
    },
    {
        "id":            "PuBe239",
        "name":          "Pu-239/Be",
        "symbol":        "²³⁹Pu/Be",
        "category":      "alpha_n",
        "endf_file":     "n-004_Be_009.endf",

        "alpha_emitter":          "Pu-239",
        "target_nucleus":         "Be-9",
        "half_life_years":        24110,         # [NuDat 3.0]
        "alpha_energy_MeV":       5.157,         # weighted mean [NuDat 3.0]
        "mean_neutron_energy_MeV": 4.24,         # [Anderson & Bond 1963; arXiv:1806.05255]
        "max_neutron_energy_MeV":  10.5,         # [Anderson & Bond 1963]
        "neutron_yield_n_s_per_GBq": 5.9e4,     # ~1.6×10⁶ n/s/Ci [arXiv:1806.05255]

        "gamma_contamination":    "ต่ำ",
        "prompt_gamma_MeV":       4.44,

        "typical_activity_range": "Ci range",
        "common_uses": [
            "Well logging (historical)",
            "Laboratory neutron source",
            "Neutron howitzer",
        ],

        "status":         "active",
        "legacy_warning": True,
        "safeguards":     True,   # fissile material → strict IAEA safeguards
        "notes": (
            "Half-life ยาวมาก (24,110 ปี) "
            "Spectrum peaks ที่ ~7 MeV และ ~9 MeV; mean energy 4.24 MeV "
            "⚠️ LEGACY + SAFEGUARDS: Pu-239 เป็น fissile material "
            "อยู่ภายใต้ IAEA safeguards อย่างเข้มงวด "
            "ISO 8529-1 ไม่ครอบคลุม Pu-Be sources"
        ),
        "reference": "Anderson & Bond (1963); arXiv:1806.05255; INIS-IAEA",
    },
    {
        "id":            "RaBe",
        "name":          "Ra-226/Be",
        "symbol":        "²²⁶Ra/Be",
        "category":      "alpha_n",
        "endf_file":     "n-004_Be_009.endf",

        "alpha_emitter":          "Ra-226",
        "target_nucleus":         "Be-9",
        "half_life_years":        1600,          # [NuDat 3.0]
        "alpha_energy_MeV":       None,          # หลาย alpha จาก decay chain
        "mean_neutron_energy_MeV": 3.9,          # [Ref 5, Knoll]
        "max_neutron_energy_MeV":  13.0,
        # Ra-226 ที่ secular equilibrium ผลิตนิวตรอน ~6–8× มากกว่า AmBe ต่อ GBq
        # เพราะมี alpha emitters หลายตัวใน decay chain
        "neutron_yield_n_s_per_GBq": 4.0e5,     # ประมาณ (equilibrium) [ionactive.co.uk]

        "gamma_contamination":    "สูงมาก — Bi-214 และ Pb-214 ใน decay chain ปล่อย gamma > 2 MeV",
        "prompt_gamma_MeV":       4.44,

        "typical_activity_range": "mCi – Ci",
        "common_uses": [
            "Legacy industrial source (ก่อน ค.ศ. 1980)",
            "Historical research sources",
        ],

        "status":         "legacy",
        "legacy_warning": True,
        "safeguards":     False,
        "notes": (
            "⚠️ LEGACY SOURCE — ใช้ด้วยความระมัดระวังสูงสุด "
            "Gamma dose rate สูงมากจาก Ra-226 decay chain "
            "(Rn-222 → Bi-214, Pb-214 ปล่อย gamma > 2 MeV) "
            "ไม่มีการผลิตใหม่แล้ว — พบเป็น legacy sources ในสถานที่เก่า "
            "ต้องการ shielding เพิ่มเติมมากกว่า Am-Be หรือ Pu-Be"
        ),
        "reference": "Knoll (4th Ed.); ionactive.co.uk neutron calculator",
    },
]

# ─────────────────────────────────────────────────────────────────
# SPONTANEOUS FISSION SOURCES
# ─────────────────────────────────────────────────────────────────
FISSION_SOURCES = [
    {
        "id":            "Cf252",
        "name":          "Cf-252",
        "symbol":        "²⁵²Cf",
        "category":      "spontaneous_fission",
        "endf_file":     "n-098_Cf_252.endf",

        # ── Nuclear properties (Ref: ISO 8529-1, NuDat 3.0) ──────
        "half_life_years":         2.645,        # [NuDat 3.0]
        "sf_branching_ratio":      0.0309,       # 3.09% SF [NuDat 3.0]
        "mean_neutron_energy_MeV": 2.13,         # Watt spectrum [ISO 8529-1]
        "most_probable_energy_MeV": 0.70,        # [ISO 8529-1]
        "max_neutron_energy_MeV":  13.0,
        "neutron_yield_per_ug":    2.314e6,      # n/s per µg [ISO 8529-1]
        "avg_neutrons_per_fission": 3.757,       # [NuDat 3.0]

        # Watt spectrum: N(E) ∝ sinh(√(2E)) · exp(-E/1.025)
        "watt_a": 1.025,   # MeV (Watt parameter)
        "watt_b": 2.926,   # MeV⁻¹ (Watt parameter)

        "gamma_contamination":    "ปานกลาง",
        "typical_activity_range": "µg – mg",
        "common_uses": [
            "Neutron calibration (ISO 8529-1 primary reference)",
            "PGNAA (prompt gamma neutron activation analysis)",
            "Nuclear reactor startup source",
            "Neutron generator project",
        ],

        "status":         "active",
        "legacy_warning": False,
        "safeguards":     True,
        "notes": (
            "Gold standard สำหรับ spontaneous fission neutron source "
            "Watt spectrum: N(E) ∝ sinh(√(2E)) · exp(-E/1.025) "
            "⚠️ Half-life สั้นมาก (2.645 ปี) — activity ลดเร็ว "
            "ต้องวางแผน procurement timing อย่างรอบคอบ"
        ),
        "reference": "ISO 8529-1:2021; NuDat 3.0",
    },
    {
        "id":            "Cm244",
        "name":          "Cm-244",
        "symbol":        "²⁴⁴Cm",
        "category":      "spontaneous_fission",
        "endf_file":     None,   # ไม่มีในชุดไฟล์หลักที่ download

        "half_life_years":         18.1,         # [NuDat 3.0]
        "sf_branching_ratio":      0.000131,     # 0.0131% SF [NuDat 3.0]
        "mean_neutron_energy_MeV": 2.12,         # คล้าย Cf-252 [Ref 5]
        "most_probable_energy_MeV": 0.68,
        "max_neutron_energy_MeV":  12.0,
        "neutron_yield_per_ug":    1.08e5,       # n/s per µg [Ref 5]
        "avg_neutrons_per_fission": 2.72,        # [NuDat 3.0]

        "watt_a": 0.906,
        "watt_b": 3.848,

        "gamma_contamination":    "ต่ำ",
        "typical_activity_range": "mg range",
        "common_uses": [
            "Research neutron source",
            "RTG heat source",
        ],

        "status":         "active",
        "legacy_warning": False,
        "safeguards":     True,
        "notes": (
            "Half-life ยาวกว่า Cf-252 (18.1 ปี) — เหมาะกับงานระยะยาว "
            "Neutron yield ต่ำกว่า Cf-252 ต่อ unit mass "
            "Spectrum คล้าย Cf-252 (Watt distribution)"
        ),
        "reference": "NuDat 3.0; Knoll (4th Ed.)",
    },
]

# ─────────────────────────────────────────────────────────────────
# GAMMA REFERENCE SOURCES
# ─────────────────────────────────────────────────────────────────
GAMMA_SOURCES = [
    {
        "id":            "Cs137",
        "name":          "Cs-137",
        "symbol":        "¹³⁷Cs",
        "category":      "gamma_reference",
        "endf_file":     None,   # ไม่ใช่ neutron target หลัก

        "half_life_years":  30.17,               # [NuDat 3.0]
        "half_life_days":   None,
        "principal_gamma_keV":   [661.7],        # จาก Ba-137m [NuDat 3.0]
        "gamma_intensity_pct":   [85.1],
        "dose_rate_const_uSv_h_per_GBq_1m": 77.9,  # [IAEA Safety Reports]

        "typical_activity_range": "mCi – Ci",
        "common_uses": [
            "Gamma calibration reference (single clean line)",
            "Density gauge",
            "Level gauge",
        ],

        "status":         "active",
        "legacy_warning": False,
        "notes": (
            "Gamma line เดียวที่ 661.7 keV — ideal calibration source "
            "Half-life ยาว (30.17 ปี) — activity stable ในระยะยาว "
            "Daughter Ba-137m (t½ = 2.55 min) เป็น gamma emitter จริง"
        ),
        "reference": "NuDat 3.0; IAEA Safety Reports Series No. 2",
    },
    {
        "id":            "Co60",
        "name":          "Co-60",
        "symbol":        "⁶⁰Co",
        "category":      "gamma_reference",
        "endf_file":     "n-027_Co_059.endf",   # Co-59(n,γ)Co-60

        "half_life_years":  5.271,               # [NuDat 3.0]
        "half_life_days":   None,
        "principal_gamma_keV":   [1173.2, 1332.5],   # [NuDat 3.0]
        "gamma_intensity_pct":   [99.85,  99.98],
        "dose_rate_const_uSv_h_per_GBq_1m": 309.0,

        "typical_activity_range": "mCi – kCi",
        "common_uses": [
            "Gamma sterilisation",
            "Industrial radiography",
            "Teletherapy (historical)",
            "Detector calibration",
        ],

        "status":         "active",
        "legacy_warning": False,
        "notes": (
            "Two coincident high-energy gammas (1.17 & 1.33 MeV) "
            "Dose rate constant สูงมาก — ต้องการ shielding หนา "
            "ผลิตจาก neutron activation: ⁵⁹Co(n,γ)⁶⁰Co "
            "Activity ลด ~12.5% ต่อปี"
        ),
        "reference": "NuDat 3.0; IAEA Safety Reports Series No. 2",
    },
    {
        "id":            "Ir192",
        "name":          "Ir-192",
        "symbol":        "¹⁹²Ir",
        "category":      "gamma_reference",
        "endf_file":     None,

        "half_life_years":  None,
        "half_life_days":   73.83,               # [NuDat 3.0]
        "principal_gamma_keV":   [295.96, 308.46, 316.51, 468.07],
        "gamma_intensity_pct":   [28.72,  29.68,  82.71,  47.81],
        "dose_rate_const_uSv_h_per_GBq_1m": 113.0,

        "typical_activity_range": "Ci range",
        "common_uses": [
            "Industrial gamma radiography (pipeline, weld inspection)",
            "HDR brachytherapy",
        ],

        "status":         "active",
        "legacy_warning": False,
        "notes": (
            "Source หลักสำหรับ industrial gamma radiography "
            "Half-life สั้น (73.83 วัน) — ต้องเปลี่ยน source บ่อย "
            "Gamma spectrum ซับซ้อน หลาย lines ในช่วง 0.2–0.6 MeV"
        ),
        "reference": "NuDat 3.0; IAEA Safety Reports Series No. 2",
    },
    {
        "id":            "Se75",
        "name":          "Se-75",
        "symbol":        "⁷⁵Se",
        "category":      "gamma_reference",
        "endf_file":     None,

        "half_life_years":  None,
        "half_life_days":   119.78,              # [NuDat 3.0]
        "principal_gamma_keV":   [121.12, 136.00, 264.66, 279.54, 400.66],
        "gamma_intensity_pct":   [17.2,   58.3,   58.9,   25.0,   11.5],
        "dose_rate_const_uSv_h_per_GBq_1m": 51.0,

        "typical_activity_range": "Ci range",
        "common_uses": [
            "Pipeline weld inspection (thin-wall, small diameter)",
            "Petrochemical industry NDT",
        ],

        "status":         "active",
        "legacy_warning": False,
        "notes": (
            "Energy ต่ำกว่า Ir-192 — เหมาะกับ thin-wall pipeline inspection "
            "เหล็กหนา 10–40 mm "
            "Half-life ~120 วัน"
        ),
        "reference": "NuDat 3.0; IAEA Safety Reports Series No. 2",
    },
    {
        "id":            "Yb169",
        "name":          "Yb-169",
        "symbol":        "¹⁶⁹Yb",
        "category":      "gamma_reference",
        "endf_file":     None,

        "half_life_years":  None,
        "half_life_days":   32.01,               # [NuDat 3.0]
        "principal_gamma_keV":   [63.12, 109.78, 130.52, 177.21, 197.96],
        "gamma_intensity_pct":   [44.2,  17.5,   11.4,   22.2,   35.9],
        "dose_rate_const_uSv_h_per_GBq_1m": 56.0,

        "typical_activity_range": "Ci range",
        "common_uses": [
            "Portable radiography (วัสดุ density ต่ำ)",
            "Aluminium และ light alloy inspection",
            "Electronics component inspection",
        ],

        "status":         "active",
        "legacy_warning": False,
        "notes": (
            "Low-energy gammas — เหมาะกับวัสดุเบาและ thin sections "
            "Half-life สั้น (32 วัน) — ต้องเปลี่ยน source บ่อยมาก "
            "ทางเลือกแทน X-ray สำหรับงานภาคสนาม portable"
        ),
        "reference": "NuDat 3.0; IAEA Safety Reports Series No. 2",
    },
    {
        "id":            "Na24",
        "name":          "Na-24",
        "symbol":        "²⁴Na",
        "category":      "gamma_reference",
        "endf_file":     None,

        "half_life_years":  None,
        "half_life_days":   None,
        "half_life_hours":  14.96,               # [NuDat 3.0]
        "principal_gamma_keV":   [1368.6, 2754.0],   # [NuDat 3.0]
        "gamma_intensity_pct":   [99.99,  99.86],
        "dose_rate_const_uSv_h_per_GBq_1m": 481.0,

        "typical_activity_range": "ผลิต on-site เท่านั้น",
        "common_uses": [
            "Neutron activation analysis tracer",
            "Flow studies (short-lived tracer)",
        ],

        "status":         "active",
        "legacy_warning": False,
        "notes": (
            "Half-life สั้นมาก (14.96 ชั่วโมง) "
            "ต้องผลิตใหม่จาก neutron activation: ²³Na(n,γ)²⁴Na "
            "ไม่มีจำหน่ายเป็น sealed source — ผลิตจาก reactor หรือ neutron generator "
            "High-energy gammas (1.37 & 2.75 MeV) ต้องการ heavy shielding"
        ),
        "reference": "NuDat 3.0",
    },
]

# ─────────────────────────────────────────────────────────────────
# CONVENIENCE LOOKUPS
# ─────────────────────────────────────────────────────────────────
ALL_SOURCES = ALPHA_N_SOURCES + FISSION_SOURCES + GAMMA_SOURCES

SOURCE_BY_ID = {s["id"]: s for s in ALL_SOURCES}

CATEGORY_LABELS = {
    "alpha_n":             "⚛️ (α,n) Sources",
    "spontaneous_fission": "💥 Spontaneous Fission Sources",
    "gamma_reference":     "🔆 Gamma Reference Sources",
}

CATEGORY_ORDER = ["alpha_n", "spontaneous_fission", "gamma_reference"]


def get_sources_by_category(category: str) -> list:
    """Return all sources in a given category."""
    return [s for s in ALL_SOURCES if s["category"] == category]


def get_source(source_id: str) -> dict | None:
    """Return a single source dict by ID, or None if not found."""
    return SOURCE_BY_ID.get(source_id)


def get_sources_with_endf() -> list:
    """Return only sources that have an associated ENDF file (usable with endf-userpy)."""
    return [s for s in ALL_SOURCES if s.get("endf_file")]


def get_half_life_display(source: dict) -> str:
    """Return human-readable half-life string."""
    if source.get("half_life_years"):
        hl = source["half_life_years"]
        if hl >= 1000:
            return f"{hl:,.0f} ปี"
        return f"{hl} ปี"
    if source.get("half_life_days"):
        return f"{source['half_life_days']} วัน"
    if source.get("half_life_hours"):
        return f"{source['half_life_hours']} ชั่วโมง"
    return "N/A"
