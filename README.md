# WoundTrack: AI-Powered Wound Healing Progress Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Automated wound healing assessment using Google MedGemma models**

## 🎯 Problem Statement

India faces a critical shortage of trained wound care specialists, placing enormous burden on nurses and healthcare workers. WoundTrack provides automated, consistent wound assessment tools accessible via mobile devices to:
- Track wound healing progression over time
- Classify wound status (Improving/Stable/Worsening)
- Generate clinical reports for healthcare providers
- Alert caregivers when wounds require escalation

## 🏗️ Project Structure

```
WoundTrack/
├── notebooks/
│   ├── woundtrack_main.ipynb          # Main Kaggle notebook (MedGemma pipeline)
│   └── synthetic_wound_generator.ipynb # Colab notebook for image generation
├── data/                               # Dataset directory (gitignored)
├── outputs/                            # Generated reports and visualizations
├── src/                                # Source code modules
│   ├── preprocessing.py                # Image preprocessing pipeline
│   ├── medgemma_inference.py          # MedGemma model wrappers
│   ├── longitudinal_analysis.py       # Temporal comparison logic
│   └── report_generator.py            # PDF report generation
└── README.md
```

## 📊 Datasets

**Baseline Images**:
- [Wound Segmentation Images](https://www.kaggle.com/datasets/leoscode/wound-segmentation-images) - 2,760 samples
- [Diabetic Foot Ulcer (DFU)](https://www.kaggle.com/datasets/laithjj/diabetic-foot-ulcer-dfu) - Medical center images

**Synthetic Progression**: Generated using Stable Diffusion img2img to create temporal sequences

## 🚀 Quick Start

### Option 1: Kaggle (Recommended)
1. Open `notebooks/woundtrack_main.ipynb` in Kaggle
2. Add the two datasets via "Add Data"
3. Run all cells

### Option 2: Google Colab
1. Upload notebooks to Colab
2. Connect to GPU runtime
3. Mount Kaggle datasets via API

## 🛠️ Technology Stack

- **LLM Models**: MedGemma 1.5 (4B + 27B)
- **ML Framework**: PyTorch, Hugging Face Transformers
- **Visualization**: Plotly, Matplotlib
- **Reports**: ReportLab (PDF generation)
- **Image Generation**: Stable Diffusion XL

## 📅 Development Timeline

- **Week 1**: Data infrastructure + MedGemma integration ✅
- **Week 2**: UI, evaluation, documentation
- **Weeks 3-4**: Testing and validation

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

This project uses datasets from multiple sources. Please cite the original papers when using this work.
