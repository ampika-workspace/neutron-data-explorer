"""
utils/lang.py
-------------
Bilingual (Thai / English) string table.

Usage:
    from utils.lang import t
    st.markdown(t("p01_desc"))

The language is stored in st.session_state["lang"] ("th" | "en").
Each page sidebar renders:
    st.radio("", ["th","en"], format_func=..., horizontal=True, key="lang")
which persists across page navigation automatically.
"""

TEXTS: dict[str, dict[str, str]] = {
    # ── Thai ─────────────────────────────────────────────────────────────────
    "th": {
        # ── Shared sidebar ──
        "nav_title":        "### ⚛️ Neutron Data Explorer",
        "nav_quick":        "**Quick Navigation**",

        # ── Page 01: Source Library ──────────────────────────────────────────
        "p01_desc": (
            "รายละเอียด radioactive sources ทั้งหมดที่รองรับในแอปนี้ "
            "ข้อมูลอ้างอิงจาก **ISO 8529-1:2021**, **IAEA-TECDOC-465**, และ **NuDat 3.0**"
        ),
        "p01_filter":           "**Filter**",
        "p01_category":         "Category",
        "p01_all_categories":   "All Categories",
        "p01_show_legacy":      "แสดง Legacy sources",
        "p01_show_safeguards":  "แสดง Safeguards sources",
        "p01_metric_total":     "Sources ทั้งหมด",
        "p01_metric_endf":      "มีไฟล์ ENDF ✅",
        "p01_no_source":        "ไม่พบ source ที่ตรงกับ filter ที่เลือก",
        "p01_footer": (
            "**Disclaimer:** Independent tool for educational and laboratory use — "
            "not an official IAEA product.  "
            "Data sourced from ISO 8529-1:2021, IAEA-TECDOC-465, NuDat 3.0, "
            "and peer-reviewed references."
        ),

        # ── Page 02: Reaction Explorer ───────────────────────────────────────
        "p02_desc": (
            "Cross section ของ neutron-induced reactions จากไฟล์ **ENDF/B-VIII.0** "
            "ผ่าน [endf-userpy](https://github.com/IAEA-NDS/endf-userpy) (IAEA-NDS)"
        ),
        "p02_no_endf": (
            "**endf-userpy ไม่พร้อมใช้งาน**\n\n"
            "รัน `pip install endf-userpy` แล้วรีสตาร์ทแอปค่ะ"
        ),
        "p02_no_files":         "ไม่พบไฟล์ ENDF ใน data/ กรุณา upload ไฟล์ก่อนค่ะ",
        "p02_select_target":    "#### เลือก Target Nucleus",
        "p02_target_help":      "Nucleus ที่นิวตรอนจะเข้าทำปฏิกิริยาด้วย",
        "p02_spinner_load":     "กำลังโหลด {}...",
        "p02_load_error":       "ไม่สามารถโหลดไฟล์ ENDF ได้",
        "p02_no_reactions":     "ไม่พบ reactions ในไฟล์นี้",
        "p02_load_success":     "✅ โหลดสำเร็จ — พบ {} reactions",
        "p02_select_reactions": "#### เลือก Reactions",
        "p02_reactions_help":   "เลือกได้หลาย reactions เพื่อเปรียบเทียบกัน",
        "p02_energy_range":     "#### Energy Range",
        "p02_emin_help":        "พลังงานต่ำสุด (thermal neutron ≈ 0.025 eV = 2.5×10⁻⁸ MeV)",
        "p02_emax_help":        "พลังงานสูงสุด (14 MeV = D-T generator, 20 MeV = ENDF limit)",
        "p02_n_points":         "จำนวน energy points",
        "p02_no_selection":     "เลือก reaction อย่างน้อย 1 ตัวจากแถบซ้ายค่ะ",
        "p02_calc_spinner":     "กำลังคำนวณ cross sections...",
        "p02_calc_warning":     "ไม่สามารถคำนวณ: {}",
        "p02_table_expander":   "📋 ดูตารางข้อมูล (sample points)",
        "p02_notation_expander":"📖 คำอธิบาย Reaction Notation",
        "p02_notation_table": """\
| Notation | ความหมาย |
|----------|-----------|
| `(n,total)` | Total cross section — ผลรวมทุก reactions |
| `(n,elastic)` หรือ `(n,n_0)` | Elastic scattering — นิวตรอนกระเด็งโดยไม่เปลี่ยน nucleus |
| `(n,inelastic)` | Inelastic scattering — nucleus ถูก excite |
| `(n,gamma)` หรือ `(n,g)` | Radiative capture — nucleus ดูดนิวตรอนและปล่อย gamma |
| `(n,2n)` | นิวตรอนชน → ได้ 2 นิวตรอนออกมา |
| `(n,p)` | นิวตรอนชน → ได้ proton ออกมา |
| `(n,a)` | นิวตรอนชน → ได้ alpha particle ออกมา |
| `(n,f)` | Fission — nucleus แตกออก (เฉพาะ fissile/fissionable nuclei) |
""",
        "p02_footer": (
            "**Data source:** ENDF/B-VIII.0 via endf-userpy (IAEA-NDS) · "
            "**Disclaimer:** Independent tool for educational use — not an official IAEA product."
        ),

        # ── Page 03: Neutron Spectrum ────────────────────────────────────────
        "p03_desc": (
            "Energy spectrum ของนิวตรอนจาก neutron sources ต่างๆ "
            "เปรียบเทียบ spectrum ระหว่าง sources และดูผลกระทบต่อการป้องกันรังสี"
        ),
        "p03_select_sources":   "#### เลือก Sources",
        "p03_sources_label":    "Sources ที่ต้องการแสดง",
        "p03_sources_help":     "เลือกได้หลาย sources เพื่อเปรียบเทียบ",
        "p03_energy_range":     "#### Energy Range",
        "p03_emax_help":        "14 MeV = พลังงานสูงสุดของ D-T generator",
        "p03_resolution":       "Resolution",
        "p03_ref_lines":        "#### Reference Lines",
        "p03_display":          "#### Display",
        "p03_normalize":        "Normalise (area = 1)",
        "p03_fill_area":        "Fill area under curve",
        "p03_log_x":            "Log scale (X axis)",
        "p03_no_source":        "เลือก source อย่างน้อย 1 ตัวจากแถบซ้ายค่ะ",
        "p03_summary":          "#### สรุปคุณสมบัติ Spectrum",
        "p03_mean_energy":      "**Mean energy:**",
        "p03_max_energy":       "**Max energy:**",
        "p03_compare_expander": "📋 เปรียบเทียบคุณสมบัติ Spectrum",
        "p03_col_source":       "Source",
        "p03_col_symbol":       "Symbol",
        "p03_col_model":        "Spectrum model",
        "p03_col_mean_e":       "Mean E (MeV)",
        "p03_col_max_e":        "Max E (MeV)",
        "p03_col_desc":         "Model",
        "p03_physics_expander": "📖 Physics Notes — Spectrum Models",
        "p03_physics_content": """\
**Watt Fission Spectrum (Cf-252, Cm-244)**

ฟังก์ชันมาตรฐาน ISO 8529-1 สำหรับ spontaneous fission neutron sources:

$$N(E) \\propto \\sinh(\\sqrt{bE}) \\cdot e^{-E/a}$$

| Source | a (MeV) | b (MeV⁻¹) | Mean E |
|--------|---------|-----------|--------|
| Cf-252 | 1.025   | 2.926     | 2.13 MeV |
| Cm-244 | 0.906   | 3.848     | 2.12 MeV |

---

**Am-241/Be Analytical Model**

Spectrum ของ Am-Be ไม่สามารถอธิบายด้วยสูตรเดียวได้ เนื่องจากมีหลาย reaction channels ของ
⁹Be(α,n)¹²C ที่พลังงานต่างกัน ผลคือ spectrum มีลักษณะ **double-hump** (สองยอด)
ที่ ~3 MeV และ ~4.5 MeV

Model ที่ใช้ในแอปนี้เป็น **multi-Gaussian approximation** ตาม ISO 8529-1 spectrum shape

---

**หมายเหตุ:**
- Pu-238/Be มี spectrum คล้าย Am-241/Be มาก เพราะ alpha energy ต่างกันเพียง ~10 keV
- สำหรับงาน shielding design ควรใช้ spectrum จาก Monte Carlo simulation (MCNP, PHITS)
  ร่วมกับข้อมูล ENDF สำหรับความแม่นยำสูงสุด
""",
        "p03_footer": (
            "**Data source:** ISO 8529-1:2021 (Watt parameters) · "
            "Geiger & Hargrove (1966) (Am-Be model) · "
            "**Disclaimer:** Independent tool for educational use — not an official IAEA product."
        ),

        # ── Page 04: Activation Calculator ──────────────────────────────────
        "p04_desc": (
            "คำนวณ **radionuclides ที่เกิดจาก neutron activation** ของวัสดุต่างๆ "
            "พร้อม production cross section จาก **ENDF/B-VIII.0** "
            "และข้อมูลความปลอดภัยทางรังสีสำหรับแต่ละ activation product"
        ),
        "p04_no_endf": (
            "**endf-userpy ไม่พร้อมใช้งาน**\n\n"
            "รัน `pip install endf-userpy` แล้วรีสตาร์ทแอปค่ะ"
        ),
        "p04_target_material":  "#### Target Material",
        "p04_target_help":      "วัสดุที่ถูก activate โดยนิวตรอน",
        "p04_no_targets":       "ไม่พบไฟล์ ENDF ที่รองรับใน data/",
        "p04_neutron_source":   "#### Neutron Source",
        "p04_custom_label":     "กำหนดเอง",
        "p04_incident_energy":  "Incident neutron energy (MeV)",
        "p04_mean_energy_info": "Mean energy: **{} MeV**",
        "p04_xs_plot":          "#### Cross Section Plot",
        "p04_spinner":          "กำลังโหลด {}...",
        "p04_load_error":       "ไม่สามารถโหลดไฟล์ ENDF ได้",
        "p04_products_header":  "#### Activation Products ของ {}",
        "p04_detail_header":    "#### รายละเอียด Activation Products",
        "p04_no_products":      "ยังไม่มีข้อมูล activation products สำหรับ target นี้ค่ะ",
        "p04_sigma_label":      "σ @ {:.2f} MeV",
        "p04_half_life_label":  "Half-life",
        "p04_radiation_label":  "Radiation",
        "p04_table_expander":   "📋 ตารางสรุป Activation Products",
        "p04_col_residual":     "Residual",
        "p04_col_halflife":     "Half-life",
        "p04_col_radiation":    "Radiation",
        "p04_col_safety":       "Safety note",
        "p04_safety_expander":  "🛡️ Radiation Safety — สิ่งที่ต้องระวัง",
        "p04_safety_content": """\
**Target: {target}** ที่ incident energy {energy:.2f} MeV

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
""",
        "p04_link_box": (
            '<div class="info-box">'
            "🔗 <b>ต้องการคำนวณ dose rate หรือ shielding จาก activated source?</b><br>"
            'ใช้ <a href="https://nuclear-source-toolkit-g5sxa75wivgvrv9axgbnhd.streamlit.app/" '
            'target="_blank">Nuclear Source Toolkit</a> '
            "สำหรับ Dose Rate Calculator และ Shielding Calculator ค่ะ"
            "</div>"
        ),
        "p04_footer": (
            "**Data source:** ENDF/B-VIII.0 via endf-userpy (IAEA-NDS) · "
            "NuDat 3.0 (half-life & decay data) · "
            "**Disclaimer:** Independent tool for educational use — not an official IAEA product. "
            "ข้อมูลนี้ไม่ใช่คำแนะนำทางรังสีวิทยาอย่างเป็นทางการ"
        ),
    },

    # ── English ───────────────────────────────────────────────────────────────
    "en": {
        # ── Shared sidebar ──
        "nav_title":        "### ⚛️ Neutron Data Explorer",
        "nav_quick":        "**Quick Navigation**",

        # ── Page 01: Source Library ──────────────────────────────────────────
        "p01_desc": (
            "Details of all radioactive sources supported in this app. "
            "Data referenced from **ISO 8529-1:2021**, **IAEA-TECDOC-465**, and **NuDat 3.0**"
        ),
        "p01_filter":           "**Filter**",
        "p01_category":         "Category",
        "p01_all_categories":   "All Categories",
        "p01_show_legacy":      "Show Legacy sources",
        "p01_show_safeguards":  "Show Safeguards sources",
        "p01_metric_total":     "Total Sources",
        "p01_metric_endf":      "ENDF Available ✅",
        "p01_no_source":        "No sources match the selected filter",
        "p01_footer": (
            "**Disclaimer:** Independent tool for educational and laboratory use — "
            "not an official IAEA product.  "
            "Data sourced from ISO 8529-1:2021, IAEA-TECDOC-465, NuDat 3.0, "
            "and peer-reviewed references."
        ),

        # ── Page 02: Reaction Explorer ───────────────────────────────────────
        "p02_desc": (
            "Cross sections of neutron-induced reactions from **ENDF/B-VIII.0** files "
            "via [endf-userpy](https://github.com/IAEA-NDS/endf-userpy) (IAEA-NDS)"
        ),
        "p02_no_endf": (
            "**endf-userpy is not available**\n\n"
            "Run `pip install endf-userpy` and restart the app."
        ),
        "p02_no_files":         "No ENDF files found in data/ — please upload files first.",
        "p02_select_target":    "#### Select Target Nucleus",
        "p02_target_help":      "Nucleus for neutron interaction",
        "p02_spinner_load":     "Loading {}...",
        "p02_load_error":       "Failed to load ENDF file",
        "p02_no_reactions":     "No reactions found in this file",
        "p02_load_success":     "✅ Loaded — found {} reactions",
        "p02_select_reactions": "#### Select Reactions",
        "p02_reactions_help":   "Select multiple reactions to compare",
        "p02_energy_range":     "#### Energy Range",
        "p02_emin_help":        "Minimum energy (thermal neutron ≈ 0.025 eV = 2.5×10⁻⁸ MeV)",
        "p02_emax_help":        "Maximum energy (14 MeV = D-T generator, 20 MeV = ENDF limit)",
        "p02_n_points":         "Number of energy points",
        "p02_no_selection":     "Select at least 1 reaction from the left panel.",
        "p02_calc_spinner":     "Calculating cross sections...",
        "p02_calc_warning":     "Could not calculate: {}",
        "p02_table_expander":   "📋 View Data Table (sample points)",
        "p02_notation_expander":"📖 Reaction Notation Reference",
        "p02_notation_table": """\
| Notation | Meaning |
|----------|---------|
| `(n,total)` | Total cross section — sum of all reactions |
| `(n,elastic)` or `(n,n_0)` | Elastic scattering — neutron deflected, nucleus unchanged |
| `(n,inelastic)` | Inelastic scattering — nucleus is excited |
| `(n,gamma)` or `(n,g)` | Radiative capture — nucleus absorbs neutron and emits gamma |
| `(n,2n)` | Neutron incident → 2 neutrons emitted |
| `(n,p)` | Neutron incident → proton emitted |
| `(n,a)` | Neutron incident → alpha particle emitted |
| `(n,f)` | Fission — nucleus splits (fissile/fissionable nuclei only) |
""",
        "p02_footer": (
            "**Data source:** ENDF/B-VIII.0 via endf-userpy (IAEA-NDS) · "
            "**Disclaimer:** Independent tool for educational use — not an official IAEA product."
        ),

        # ── Page 03: Neutron Spectrum ────────────────────────────────────────
        "p03_desc": (
            "Energy spectrum of neutrons from various sources. "
            "Compare spectra between sources and explore radiation shielding implications."
        ),
        "p03_select_sources":   "#### Select Sources",
        "p03_sources_label":    "Sources to display",
        "p03_sources_help":     "Select multiple sources to compare",
        "p03_energy_range":     "#### Energy Range",
        "p03_emax_help":        "14 MeV = maximum energy of D-T generator",
        "p03_resolution":       "Resolution",
        "p03_ref_lines":        "#### Reference Lines",
        "p03_display":          "#### Display",
        "p03_normalize":        "Normalise (area = 1)",
        "p03_fill_area":        "Fill area under curve",
        "p03_log_x":            "Log scale (X axis)",
        "p03_no_source":        "Select at least 1 source from the left panel.",
        "p03_summary":          "#### Spectrum Properties Summary",
        "p03_mean_energy":      "**Mean energy:**",
        "p03_max_energy":       "**Max energy:**",
        "p03_compare_expander": "📋 Compare Spectrum Properties",
        "p03_col_source":       "Source",
        "p03_col_symbol":       "Symbol",
        "p03_col_model":        "Spectrum model",
        "p03_col_mean_e":       "Mean E (MeV)",
        "p03_col_max_e":        "Max E (MeV)",
        "p03_col_desc":         "Model",
        "p03_physics_expander": "📖 Physics Notes — Spectrum Models",
        "p03_physics_content": """\
**Watt Fission Spectrum (Cf-252, Cm-244)**

Standard formula from ISO 8529-1 for spontaneous fission neutron sources:

$$N(E) \\propto \\sinh(\\sqrt{bE}) \\cdot e^{-E/a}$$

| Source | a (MeV) | b (MeV⁻¹) | Mean E |
|--------|---------|-----------|--------|
| Cf-252 | 1.025   | 2.926     | 2.13 MeV |
| Cm-244 | 0.906   | 3.848     | 2.12 MeV |

---

**Am-241/Be Analytical Model**

The Am-Be spectrum cannot be described by a single formula because of multiple
reaction channels of ⁹Be(α,n)¹²C at different energies.
The result is a **double-hump** spectrum with peaks at ~3 MeV and ~4.5 MeV.

The model used here is a **multi-Gaussian approximation** following the ISO 8529-1 spectrum shape.

---

**Notes:**
- Pu-238/Be has a spectrum very similar to Am-241/Be (alpha energy differs by only ~10 keV).
- For shielding design work, use spectra from Monte Carlo simulations (MCNP, PHITS)
  combined with ENDF data for maximum accuracy.
""",
        "p03_footer": (
            "**Data source:** ISO 8529-1:2021 (Watt parameters) · "
            "Geiger & Hargrove (1966) (Am-Be model) · "
            "**Disclaimer:** Independent tool for educational use — not an official IAEA product."
        ),

        # ── Page 04: Activation Calculator ──────────────────────────────────
        "p04_desc": (
            "Calculate **radionuclides produced by neutron activation** of various materials, "
            "with production cross sections from **ENDF/B-VIII.0** "
            "and radiation safety information for each activation product."
        ),
        "p04_no_endf": (
            "**endf-userpy is not available**\n\n"
            "Run `pip install endf-userpy` and restart the app."
        ),
        "p04_target_material":  "#### Target Material",
        "p04_target_help":      "Material to be activated by neutrons",
        "p04_no_targets":       "No supported ENDF files found in data/",
        "p04_neutron_source":   "#### Neutron Source",
        "p04_custom_label":     "Custom",
        "p04_incident_energy":  "Incident neutron energy (MeV)",
        "p04_mean_energy_info": "Mean energy: **{} MeV**",
        "p04_xs_plot":          "#### Cross Section Plot",
        "p04_spinner":          "Loading {}...",
        "p04_load_error":       "Failed to load ENDF file",
        "p04_products_header":  "#### Activation Products of {}",
        "p04_detail_header":    "#### Activation Product Details",
        "p04_no_products":      "No activation product data available for this target.",
        "p04_sigma_label":      "σ @ {:.2f} MeV",
        "p04_half_life_label":  "Half-life",
        "p04_radiation_label":  "Radiation",
        "p04_table_expander":   "📋 Activation Products Summary Table",
        "p04_col_residual":     "Residual",
        "p04_col_halflife":     "Half-life",
        "p04_col_radiation":    "Radiation",
        "p04_col_safety":       "Safety note",
        "p04_safety_expander":  "🛡️ Radiation Safety — Key Considerations",
        "p04_safety_content": """\
**Target: {target}** at incident energy {energy:.2f} MeV

**ALARA principles for activated materials:**

1. **Time** — Limit contact time with activated materials
2. **Distance** — Increase distance from activated material (inverse square law)
3. **Shielding** — Use appropriate shielding for the type of radiation emitted
4. **Measurement** — Always measure dose rate before and after irradiation

**Warnings:**
- Cross sections shown are from ENDF/B-VIII.0 for the specified reactions
- Actual activity depends on neutron flux, irradiation time, and target mass
- Consult a Medical Physicist or Radiation Protection Officer
  before working with neutron-irradiated materials
""",
        "p04_link_box": (
            '<div class="info-box">'
            "🔗 <b>Need to calculate dose rate or shielding from an activated source?</b><br>"
            'Use <a href="https://nuclear-source-toolkit-g5sxa75wivgvrv9axgbnhd.streamlit.app/" '
            'target="_blank">Nuclear Source Toolkit</a> '
            "for Dose Rate Calculator and Shielding Calculator."
            "</div>"
        ),
        "p04_footer": (
            "**Data source:** ENDF/B-VIII.0 via endf-userpy (IAEA-NDS) · "
            "NuDat 3.0 (half-life & decay data) · "
            "**Disclaimer:** Independent tool for educational use — not an official IAEA product."
        ),
    },
}


def get_lang() -> str:
    import streamlit as st
    return st.session_state.get("lang", "th")


def t(key: str, *args, **kwargs) -> str:
    """Return translated string for the current language."""
    lang = get_lang()
    text = TEXTS.get(lang, TEXTS["th"]).get(key) or TEXTS["th"].get(key, key)
    if args:
        return text.format(*args)
    if kwargs:
        return text.format(**kwargs)
    return text


def lang_toggle() -> None:
    """Render the language radio toggle inside a sidebar context."""
    import streamlit as st
    st.radio(
        "🌐",
        options=["th", "en"],
        format_func=lambda x: "🇹🇭 ภาษาไทย" if x == "th" else "🇬🇧 English",
        horizontal=True,
        key="lang",
        label_visibility="collapsed",
    )
