# WoundTrack: AI-Powered Wound Healing Progress Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Automated wound healing assessment using Google MedGemma models (4B VLM + 27B LLM)**

## 🎯 Problem Statement

India faces a critical shortage of trained wound care specialists, placing an enormous burden on nurses and healthcare workers. WoundTrack provides automated, consistent wound assessment tools accessible via mobile devices to:
- Track wound healing progression over time.
- Classify wound status (Improving/Stable/Worsening).
- Generate clinical reports for healthcare providers.
- Alert caregivers when wounds require escalation.

## 🧠 MedGemma Integration

This project heavily leverages Google's state-of-the-art MedGemma family of models:
- **MedGemma 4B VLM**: Analyzes wound images to accurately segment tissue types (granulation, slough, eschar) and measure the overall wound area.
- **MedGemma 27B LLM**: Analyzes the longitudinal data provided by the VLM combined with patient history to compute clinical scores (PUSH, Wagner), evaluate amputation risk (RiskFusion), and predict the healing trajectory (HealCast).

By uniting these multimodal capabilities, WoundTrack acts as an expert "copilot" for tracking longitudinal wound progression.

## 🏗️ Project Structure

For this competition, the repository is focused on the core deliverables:

```
WoundTrack/
├── app/                        # Patient-facing frontend and backend API
│   ├── backend/                # FastAPI backend serving MedGemma endpoints
│   └── frontend/               # React-based mobile UI
├── data/                       # Contains necessary wound images for ML
├── notebooks/                  # MedGemma pipeline execution notebooks
│   └── woundtrack_main.ipynb   # Main Kaggle notebook for MedGemma inference
├── src/                        # Core ML logic and longitudinal analysis
│   ├── medgemma_inference.py   # MedGemma model wrappers
│   ├── unified_pipeline.py     # End-to-end wound analysis pipeline
│   ├── longitudinal_analysis.py# Temporal patient analysis
│   └── ...                     
├── README.md                   # You are here
└── requirements.txt            # Python dependencies
```

*Note: Our local experimental, archive, and testing data are kept out of this branch for evaluation clarity.*

## 🚀 The Enhanced Longitudinal Pipeline

WoundTrack doesn't just look at a wound once. Our **Enhanced Longitudinal Pipeline** tracks changes over multiple visits:
- **Unified Analysis**: Combines WoundVision, WoundScore, RiskFusion, HealCast, and CareGuide in one seamless flow.
- **Trend Analysis**: Automatically detects patterns—is the healing accelerating or plateauing?
- **Clinical Alerts**: Flags warnings, such as stagnation or sudden deterioration.
- **Comprehensive Reports**: Outputs patient reports and interactive tracking dashboards.

### Quick Start (Kaggle)

1. Open `notebooks/woundtrack_main.ipynb` in Kaggle.
2. Add the base wound image datasets (e.g. DFU) via "Add Data".
3. Run the notebook to see the MedGemma components extract insights from sequential images.

### Quick Start (Local Backend API)

To test the application backend:
```bash
cd app/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 📊 Datasets

**Baseline Images**:
- [Wound Segmentation Images](https://www.kaggle.com/datasets/leoscode/wound-segmentation-images)
- [Diabetic Foot Ulcer (DFU)](https://www.kaggle.com/datasets/laithjj/diabetic-foot-ulcer-dfu) - Medical center images

These are ingested, normalized, and analyzed by the **MedGemma 4B VLM** module.

## 📄 License

MIT License - See LICENSE file for details
