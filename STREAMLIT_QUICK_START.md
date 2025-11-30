# Streamlit Web UI - Quick Start Guide

## 🎉 Streamlit App is LIVE!

The comprehensive web interface for Cure-Blend is now running with **all advanced features integrated**.

## Access the App

**Local URL**: http://localhost:8501
**Network URL**: http://10.0.1.112:8501
**External URL**: http://4.240.18.227:8501

## Features Available

### ✅ Core Features
- **Symptom Analysis**: Enter symptoms and get instant recommendations
- **Dual Recommendations**: Both herbal and pharmaceutical options
- **AI Insights**: Detailed explanations powered by AI
- **Confidence Scoring**: Know how certain the diagnosis is
- **Medical Disclaimers**: Clear safety warnings

### ✅ Advanced Features (NEW)
- **Multi-Disease Detection**: Detects multiple conditions and comorbidities
- **Severity Scoring**: 0-100 scale with 5 levels (Emergency/Severe/Moderate/Mild)
- **Personalized Recommendations**: Based on patient profile
- **Visual Severity Gauge**: Color-coded severity indicator
- **Disease Probability Chart**: Bar chart showing all predictions
- **Contraindication Warnings**: Automatically filters unsafe medications

### ✅ Patient Profile
- Age and gender
- Pregnancy and breastfeeding status
- Existing conditions (diabetes, hypertension, kidney disease, liver disease)
- Automatic special population detection (child, elderly, pregnant, etc.)

## How to Use

### 1. Basic Usage (No Profile)
1. Enter symptoms in the text area
2. Click "🔍 Analyze Symptoms"
3. View recommendations in 3 tabs:
   - 🌿 Herbal
   - 💊 Pharmaceutical
   - 🤖 AI Insights

### 2. With Patient Profile (Recommended)
1. In sidebar: Check "Enable Personalized Recommendations"
2. Expand "📋 Enter Patient Information"
3. Fill in:
   - Age
   - Gender
   - Special conditions (pregnancy, breastfeeding)
   - Existing health conditions
4. Enter symptoms
5. Click "🔍 Analyze Symptoms"
6. View:
   - **Basic recommendations**
   - **Severity gauge** (color-coded 0-100 score)
   - **Multi-disease analysis** (comorbidity detection)
   - **Personalized warnings** (contraindicated medications)

### 3. Advanced Mode
- Sidebar: Check "Enable Advanced Features" (default: ON)
- Sidebar: Check "Enable AI Insights" (default: ON)

## UI Layout

```
┌─────────────────────────────────────────────────┐
│          🏥 Cure-Blend 🌿                       │
│   AI-Powered Health Recommendation System       │
└─────────────────────────────────────────────────┘

SIDEBAR:                       MAIN AREA:
┌──────────────────┐          ┌────────────────────┐
│ ⚙️ Settings       │          │ 💬 Symptoms        │
│ □ Advanced        │          │ [Text Area]        │
│ □ AI Insights     │          │ [Analyze] [Clear]  │
│                   │          │                    │
│ 👤 Patient        │          │ 📋 Results:        │
│    Profile        │          │ • Diagnosis        │
│ □ Enable          │          │ • Severity Gauge   │
│ ├─ Age            │          │ • Multi-Disease    │
│ ├─ Gender         │          │ • Warnings         │
│ ├─ Conditions     │          │                    │
│ └─ Profile        │          │ 💊 Tabs:           │
│    Summary        │          │ [Herbal] [Pharma]  │
│                   │          │ [AI Insights]      │
└──────────────────┘          └────────────────────┘
```

## Example Test Cases

### Test 1: Emergency Respiratory Case
**Symptoms**: `severe difficulty breathing chest pain crushing sensation`

**Expected Results**:
- Severity: **EMERGENCY (100/100)** - Red gauge
- Warning: "🚨 CALL AMBULANCE IMMEDIATELY"
- Multi-disease: Asthma, Heart Attack, Pneumonia

### Test 2: Pregnant Woman with UTI
**Symptoms**: `frequent urination burning sensation lower abdominal discomfort`

**Patient Profile**:
- Age: 28
- Gender: Female
- Pregnant: Yes

**Expected Results**:
- Severity: **MILD (15/100)** - Green gauge
- Warnings: "Patient is pregnant - special precautions required"
- Contraindications: 9 medications (NSAIDs, tetracyclines, fluoroquinolones, etc.)

### Test 3: Elderly with Multiple Conditions
**Symptoms**: `fatigue dizziness frequent urination`

**Patient Profile**:
- Age: 75
- Diabetes: Yes
- Hypertension: Yes

**Expected Results**:
- Special populations: Elderly, Diabetic, Hypertensive
- Warnings: 3-4 population-specific warnings
- Contraindications: Multiple medications flagged
- Dose adjustments: "Start low, go slow"

## Visual Features

### Severity Gauge Colors
- 🔴 **Red (100)**: Emergency - "Call 911"
- 🟠 **Orange (80-99)**: Severe - "Urgent care needed"
- 🟡 **Yellow (50-79)**: Moderate-Severe - "See doctor soon"
- 🟡 **Yellow (30-49)**: Moderate - "Schedule appointment"
- 🟢 **Green (0-29)**: Mild - "Self-care appropriate"

### Confidence Badges
- 🟢 **High (≥70%)**: Green text
- 🟡 **Medium (40-69%)**: Yellow text
- 🔴 **Low (<40%)**: Red text with warning

### Disease Probability Chart
Horizontal bar chart showing top 5 predictions with confidence percentages

## Technical Details

### Dependencies
- streamlit
- src.ai_assistant
- src.multi_disease_detector
- src.severity_classifier
- src.personalized_recommender

### Session State
- `knowledge_base`: Cached medical knowledge (loaded once)
- `patient_profile`: Current patient information
- `analysis_results`: Latest analysis output

### Caching
- `@st.cache_resource` on knowledge base loading
- Persistent across reruns for performance

## Stopping the App

To stop the Streamlit server:
```bash
# Find the process
ps aux | grep streamlit

# Kill it
pkill -f streamlit
```

Or press `Ctrl+C` in the terminal where it's running.

## Restarting the App

```bash
cd /workspaces/Cure-Blend
python3 -m streamlit run streamlit_app.py --server.port 8501 --server.headless true
```

## Troubleshooting

### Issue: Advanced features not showing
**Solution**: Check sidebar "Enable Advanced Features" is checked

### Issue: No personalized warnings
**Solution**: Enable "Enable Personalized Recommendations" and fill patient profile

### Issue: Port already in use
**Solution**: 
```bash
pkill -f streamlit
# Wait 2 seconds
python3 -m streamlit run streamlit_app.py --server.port 8502
```

### Issue: Module not found
**Solution**: Ensure you're in `/workspaces/Cure-Blend` directory

## Comparison: CLI vs Web UI

| Feature | CLI (main.py) | Web UI (streamlit_app.py) |
|---------|---------------|---------------------------|
| Symptom input | Text prompt | Text area |
| Patient profile | Sequential questions | Form with all fields |
| Severity display | Text output | Color-coded gauge + progress bar |
| Multi-disease | Text list | Bar chart visualization |
| Warnings | Text alerts | Expandable alert boxes |
| Navigation | Linear | Tabs + expanders |
| **Best for** | Quick terminal use | Visual analysis, sharing |

## Next Steps

### Immediate Enhancements
- [ ] Add export to PDF functionality
- [ ] Add history tracking (previous analyses)
- [ ] Add symptom suggestions/autocomplete
- [ ] Add medication search functionality

### Future Features
- [ ] Multi-language support
- [ ] Save patient profiles
- [ ] Drug-herb interaction checker
- [ ] Appointment booking integration

## Success Metrics

✅ **All features working**:
- [x] Basic symptom analysis
- [x] Dual recommendations (herbal + pharmaceutical)
- [x] AI insights generation
- [x] Patient profile creation
- [x] Multi-disease detection
- [x] Severity scoring with visual gauge
- [x] Personalized warnings
- [x] Contraindication filtering
- [x] Visual charts and progress bars
- [x] Responsive layout

---

**Status**: ✅ **FULLY OPERATIONAL**

The Streamlit web UI is complete with all advanced features integrated and tested.

Access it at: http://localhost:8501
