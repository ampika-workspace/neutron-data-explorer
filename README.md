# ⚛️ Neutron Data Explorer

An interactive web application for exploring neutron nuclear data from the
**IAEA Nuclear Data Section (IAEA-NDS)**, built with
[Streamlit](https://streamlit.io) and powered by
[endf-userpy](https://github.com/IAEA-NDS/endf-userpy).

> Developed by a **Radiation Safety Officer** and **Data Analyst** as an
> open educational tool for the radiation safety and nuclear science community.

---

## 🔬 Features

| Page | Description |
|------|-------------|
| 📚 **Source Library** | Browse all supported neutron and gamma reference sources with nuclear properties, neutron yield, half-life, and safety notes |
| ⚛️ **Reaction Explorer** | Plot neutron-induced cross sections vs. energy from ENDF/B-VIII.0 data for Be-9, Fe-56, Co-59, and Pb-208 |
| 📊 **Neutron Spectrum** | Visualise and compare energy spectra of Am-241/Be, Cf-252, Cm-244, and Pu-238/Be |
| ☢️ **Activation Calculator** | Calculate radionuclides produced by neutron activation, with isomer-resolved production cross sections and radiation safety guidance |

---

## 🗂️ Supported Sources

### (α,n) Sources
| Source | Half-life | Mean neutron energy |
|--------|-----------|---------------------|
| Am-241/Be | 432.2 yr | 4.5 MeV |
| Pu-238/Be | 87.7 yr | 4.5 MeV |
| Pu-239/Be ⚠️ | 24,110 yr | 4.24 MeV |
| Ra-226/Be ⚠️ | 1,600 yr | 3.9 MeV |

> ⚠️ Legacy or IAEA-safeguarded sources — displayed with appropriate warnings.

### Spontaneous Fission Sources
| Source | Half-life | Mean neutron energy |
|--------|-----------|---------------------|
| Cf-252 | 2.645 yr | 2.13 MeV (Watt) |
| Cm-244 | 18.1 yr | 2.12 MeV (Watt) |

### Gamma Reference Sources
Cs-137 · Co-60 · Ir-192 · Se-75 · Yb-169 · Na-24

---

## 🚀 Getting Started

### Run locally

```bash
git clone https://github.com/<your-username>/neutron-data-explorer.git
cd neutron-data-explorer
pip install -r requirements.txt
streamlit run app.py
```

### ENDF data files

This app requires **ENDF/B-VIII.0** neutron reaction files placed in the `data/` directory.
Download the **Neutron Reaction Sublibrary** from the
[NNDC ENDF/B-VIII.0 download page](https://www.nndc.bnl.gov/endf-b8.0/download.html),
extract the archive, and copy the following files into `data/`:

```
data/
├── n-004_Be_009.endf
├── n-026_Fe_056.endf
├── n-027_Co_059.endf
├── n-082_Pb_208.endf
└── n-098_Cf_252.endf
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web application framework |
| `endf-userpy` | High-level ENDF-6 data interpretation (IAEA-NDS) |
| `endf-parserpy` | ENDF-6 file parser |
| `numpy` / `scipy` | Numerical computation |
| `plotly` | Interactive charts |
| `pandas` | Data tables and CSV export |

---

## 📊 Data Sources & Credits

### Nuclear Reaction Data
Nuclear reaction data (cross sections, emission spectra, activation yields) are
read directly from **ENDF/B-VIII.0** evaluated nuclear data files via the
**endf-userpy** library.

- **ENDF/B-VIII.0** — D.A. Brown et al., *Nuclear Data Sheets* 148 (2018) 1–30.
  Produced and distributed by the
  [National Nuclear Data Center (NNDC)](https://www.nndc.bnl.gov/), Brookhaven National Laboratory.

- **endf-userpy** — High-level interpretation of ENDF-6 nuclear data.
  Copyright © 2026 International Atomic Energy Agency.
  Repository: [IAEA-NDS/endf-userpy](https://github.com/IAEA-NDS/endf-userpy).
  Licensed under the MIT License.

- **endf-parserpy** — ENDF-6 file parser.
  [IAEA-NDS/endf-parserpy](https://github.com/IAEA-NDS/endf-parserpy).

### Source Properties & Standards
Physical properties of radioactive sources are sourced from:

- **ISO 8529-1:2021** — *Reference neutron radiations — Part 1: Characteristics and
  methods of production.*
  International Organization for Standardization.

- **IAEA-TECDOC-465** (1988) — *Neutron sources for calibration.*
  International Atomic Energy Agency, Vienna.

- **NuDat 3.0** — *Nuclear Structure and Decay Data.*
  National Nuclear Data Center (NNDC), Brookhaven National Laboratory.
  [www.nndc.bnl.gov/nudat3](https://www.nndc.bnl.gov/nudat3/)

- **IAEA Safety Reports Series No. 2** (1998) —
  *Radiation Protection in the Design of Radiotherapy Facilities.*
  International Atomic Energy Agency, Vienna.

- Knoll, G.F. (2010) — *Radiation Detection and Measurement*, 4th Edition.
  John Wiley & Sons.

---

## ⚠️ Disclaimer

This application is an **independent educational tool** developed for the
radiation safety and nuclear science community.

- This is **not** an official product of the IAEA, NNDC, or any regulatory body.
- Nuclear data presented here are sourced from publicly available, peer-reviewed
  references and are provided for **educational and informational purposes only**.
- This tool is **not** a substitute for official radiation safety assessments,
  regulatory compliance calculations, or professional medical physics advice.
- Always consult a qualified **Radiation Protection Officer (RPO)** or
  **Medical Physicist** for operational radiation safety decisions.
- The author assumes no liability for any decisions made based on the outputs
  of this application.

---

## 🔗 Related Application

**Nuclear Source Toolkit** — A companion app for practical radiation safety
calculations (decay, dose rate, shielding, procurement, working time):

👉 [nuclear-source-toolkit on Streamlit Cloud](https://nuclear-source-toolkit-g5sxa75wivgvrv9axgbnhd.streamlit.app/)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

The ENDF/B-VIII.0 data files distributed by NNDC are subject to their own terms of use.
The endf-userpy library is copyright © 2026 International Atomic Energy Agency and
is licensed under the MIT License.

---

## 🙏 Acknowledgements

- **IAEA Nuclear Data Section (IAEA-NDS)** for developing and maintaining
  endf-userpy and the ENDF data infrastructure.
- **National Nuclear Data Center (NNDC)**, Brookhaven National Laboratory,
  for the ENDF/B-VIII.0 evaluated nuclear data library.
- The **Cross Section Evaluation Working Group (CSEWG)** for the continuous
  development and maintenance of the ENDF/B library since 1968.

---

*Built with ❤️ by a Radiation Safety Officer · Bangkok, Thailand · 2026*
