# 🏥 CureBlend AI — Intelligent Health Assistant

> **AI-powered disease prediction with herbal & pharmaceutical recommendations**  
> 97.4% accuracy • 43 diseases • Safety-first design • Production ready

---

## ⚖️ License

**MIT License** — Copyright (c) 2026 vishwaksen21

This project is open-source and free to use, modify, and distribute. See [LICENSE](LICENSE) file for full details.

---

## 🌟 Key Features

🎯 **Smart Disease Detection** — ML model trained on 4,300+ medical cases  
💊 **Dual Recommendations** — Both herbal remedies & pharmaceutical drugs  
🛡️ **Medical Safety** — Drug contraindications, emergency detection, special populations  
🤖 **AI Insights** — Disease-specific guidance for COVID-19, Dengue, Malaria & more  
📊 **Evidence-Based** — 15+ datasets with 8,000+ patient records  
🌐 **Easy to Use** — Beautiful web UI or simple command-line interface

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/vishwaksen21/Cure-Blend.git
cd Cure-Blend
pip install -r requirements.txt

# Launch web UI
streamlit run streamlit_app.py
```

Open **http://localhost:8501** in your browser.

### Optional: Enable AI Insights

```bash
# Get free token from: https://github.com/settings/tokens
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
streamlit run streamlit_app.py
```

---

## 📊 What You Get

### Example: Fever Symptoms

**Input:** `fever headache body aches fatigue`

**Output:**
- 🎯 **Diagnosis:** Influenza (89% confidence)
- 🌿 **Herbal:** Ginger, Turmeric, Echinacea (with effectiveness ratings)
- 💊 **Drugs:** Paracetamol, Ibuprofen (with prices & dosages)
- ⚠️ **Safety:** Personalized warnings based on your profile
- 🤖 **AI Insight:** Treatment comparison & lifestyle advice
- 🚨 **Severity:** Mild (25/100) — Self-care appropriate

---

## 📊 System Performance

| Metric | Value |
|--------|-------|
| Accuracy | **97.4%** |
| Diseases Covered | **43** |
| Confidence Score | **75.7%** avg |
| Herbal Database | **50+ herbs** |
| Drug Database | **40+ medications** |
| Datasets Integrated | **15+** (8,000+ records) |

---

## 🔒 Safety First

✅ Emergency detection (auto-alerts for critical symptoms)  
✅ Drug contraindication warnings  
✅ Special population safety (pregnancy, children, elderly)  
✅ Medical disclaimer on all outputs  

⚠️ **Not FDA approved** — For educational purposes only  
⚠️ **Not for emergencies** — Call 911 for critical conditions  
⚠️ **Always consult healthcare professionals**

---

## ⚠️ Medical Disclaimer

**FOR EDUCATIONAL & RESEARCH PURPOSES ONLY**

This tool provides general health information and should NOT replace professional medical advice. Always consult qualified healthcare professionals before starting any treatment.

---

## 📚 Documentation

- **[DISEASE_AWARE_AI_INSIGHTS_V3.5.md](DISEASE_AWARE_AI_INSIGHTS_V3.5.md)** — Medical accuracy details
- **[COMPREHENSIVE_DATABASE_ENHANCEMENT.md](COMPREHENSIVE_DATABASE_ENHANCEMENT.md)** — Technical specs
- **[AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md)** — LLM integration guide

---

## 🧪 Testing

```bash
python test_advanced_features.py     # 24 tests
python test_disease_awareness.py     # Disease-specific safety
python verify_database.py            # Database verification
```

---

## 🏗️ Tech Stack

- **ML:** scikit-learn, TF-IDF, Logistic Regression
- **NLP:** Natural language symptom processing
- **Graph:** Node2Vec embeddings
- **UI:** Streamlit (web), Python CLI
- **AI:** GitHub Models / OpenAI (optional)
- **Data:** 15+ medical datasets

---

## 📁 Key Files

```
streamlit_app.py          # Web interface
main.py                   # Command-line interface
src/ai_assistant.py       # Core engine
src/drug_database.py      # 40+ medications
data/symptom_model.pkl    # Trained ML model
```

---

## 🤝 Contributing

Contributions welcome! Areas to improve:
- Drug interaction checker (OpenFDA API)
- Real patient data integration
- Multi-language support
- Mobile app development

---

## 👨‍💻 Authors

**CureBlend Team**  
Repository: [github.com/vishwaksen21/Cure-Blend](https://github.com/vishwaksen21/Cure-Blend)

---

## 📄 License

Copyright (c) 2026 vishwaksen21. All Rights Reserved.  
This project is proprietary software. No license is granted for use, copying, modification, or distribution.

---

**⚡ Get Started:** `streamlit run streamlit_app.py`
