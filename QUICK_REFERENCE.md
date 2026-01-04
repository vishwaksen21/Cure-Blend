# 🎯 Quick Reference: Enhanced Recommendation System

## 🏥 Now Supported Conditions (40+ Categories)

### 🫁 Respiratory & Throat
- Common Cold, Flu, Cough
- Tonsillitis, Pharyngitis, Sore Throat
- Bronchitis, Asthma, Pneumonia
- Sinus Congestion, Rhinitis
- **Drugs**: Antibiotics, Lozenges, Antihistamines, Inhalers, Decongestants
- **Herbs**: Tulsi, Ginger, Licorice, Eucalyptus, Honey

### 🍽️ Digestive System
- Stomach Pain, Acidity, GERD, Ulcers
- Diarrhea, Vomiting, Food Poisoning
- IBS, Crohn's, Colitis
- Constipation, Bloating
- **Drugs**: PPIs, Antacids, Anti-diarrheals, Probiotics, Antispasmodics
- **Herbs**: Ginger, Peppermint, Turmeric, Chamomile, Fennel

### 🤕 Pain & Inflammation
- Headache, Migraine
- Muscle Pain, Back Pain, Joint Pain
- Arthritis, Rheumatism
- Sprains, Strains
- **Drugs**: Paracetamol, Ibuprofen, Aspirin, Diclofenac, Tramadol
- **Herbs**: Turmeric, Ginger, Boswellia, Willow Bark

### 🦠 Infections
- Bacterial Infections
- UTI (Urinary Tract)
- Fungal Infections
- Dental Infections
- **Drugs**: Amoxicillin, Azithromycin, Ciprofloxacin, Metronidazole, Doxycycline
- **Herbs**: Neem, Tulsi, Garlic, Tea Tree Oil

### 🩺 Chronic Diseases

#### Diabetes
- **Drugs**: Metformin, Glimepiride
- **Herbs**: Bitter Melon, Fenugreek, Cinnamon, Gymnema, Jamun

#### Hypertension
- **Drugs**: Amlodipine, Losartan
- **Herbs**: Garlic, Hawthorn, Arjuna, Hibiscus, Flaxseed

### 🧴 Skin Conditions
- Rashes, Eczema, Psoriasis
- Acne, Dermatitis
- Fungal Infections
- Itching, Burns, Insect Bites
- **Drugs**: Hydrocortisone, Antifungal Creams, Calamine
- **Herbs**: Neem, Aloe Vera, Turmeric, Tea Tree Oil

### 🧠 Mental Health & Sleep
- Anxiety, Stress
- Depression
- Insomnia, Sleep Disorders
- **Drugs**: Melatonin
- **Herbs**: Ashwagandha, Brahmi, Valerian Root, Chamomile, Lavender

### 🔴 Fever & Viral
- General Fever
- Dengue, Malaria
- Viral Infections
- **Drugs**: Paracetamol, Ibuprofen, ORS
- **Herbs**: Tulsi, Giloy, Neem, Turmeric

### 🫀 Kidney & Urinary
- Kidney Stones
- UTI
- Renal Problems
- **Drugs**: Ciprofloxacin, ORS
- **Herbs**: Punarnava, Gokshura, Cranberry, Dandelion

### 🫁 Liver & Detox
- Liver Disease
- Jaundice
- Detoxification
- **Herbs**: Milk Thistle, Dandelion Root, Turmeric, Bhuiamlaki

### 🤧 Allergies
- Seasonal Allergies
- Hay Fever
- Hives, Allergic Reactions
- **Drugs**: Cetirizine, Chlorpheniramine, Hydrocortisone
- **Herbs**: Butterbur, Stinging Nettle, Quercetin, Turmeric

### 👩 Women's Health
- Menstrual Cramps
- PMS
- **Herbs**: Shatavari, Ginger, Chamomile, Cinnamon

### 🩸 Anemia & Blood
- Iron Deficiency
- Blood Health
- **Herbs**: Punarnava, Beetroot, Spirulina, Nettle, Moringa

### ⚖️ Weight Management
- Obesity
- Weight Loss Support
- **Herbs**: Green Tea, Garcinia Cambogia, Triphala, Guggul

### 💪 General Health & Immunity
- Weak Immunity
- Fatigue, Tiredness
- General Wellness
- **Drugs**: Multivitamins, Vitamin C, D3, Zinc
- **Herbs**: Ashwagandha, Giloy, Tulsi, Amla, Ginseng

---

## 🔍 How to Use

### Terminal Interface
```bash
python3 main.py
```
Enter any symptom or condition:
- "throat pain" → Tonsillitis recommendations
- "diabetes" → Chronic disease management
- "anxiety" → Mental health support
- "skin rash" → Topical treatments

### Web Interface
```bash
streamlit run streamlit_app.py
```
Navigate to http://localhost:8501 and describe symptoms

---

## 📊 What You Get

For **every condition**, you receive:

### 💊 Pharmaceutical (5 recommendations)
- Generic Name
- Brand Names (Indian market)
- Type/Category
- Dosage Guidelines
- Purpose/Use
- Availability (OTC/Prescription)
- Price Range (₹)
- Side Effects

### 🌿 Herbal (5 recommendations)
- Herb Name
- Relevance Score (%)
- Benefits
- Active Compounds
- Usage Instructions
- Safety Information

### 🤖 AI Insights (if LLM enabled)
- Condition explanation
- Why recommendations fit
- Lifestyle advice
- When to see doctor

---

## ✅ Quality Guarantees

1. **No Empty Results**: Every condition gets recommendations
2. **Accurate Matching**: 100+ keywords ensure relevance
3. **Safety First**: Side effects and contraindications listed
4. **Comprehensive Coverage**: 40 drugs + 50+ herbs
5. **Multi-Category**: Conditions can match multiple treatments
6. **Smart Fallback**: Unknown conditions get general health support

---

## 🎯 Best Results For

✅ Common cold, flu, cough  
✅ Digestive issues (stomach pain, acidity, diarrhea)  
✅ Pain management (headache, muscle pain, arthritis)  
✅ Chronic diseases (diabetes, hypertension)  
✅ Infections (UTI, bacterial, fungal)  
✅ Skin problems (rash, eczema, acne)  
✅ Mental health (anxiety, stress, insomnia)  
✅ Allergies and hay fever  
✅ General wellness and immunity  

---

## ⚠️ Important Notes

- This is an **informational tool** only
- Always **consult a healthcare professional**
- Do not use for **emergency situations**
- Call emergency services for **serious symptoms**
- Check for **drug allergies** before use
- Follow **prescription requirements**
- Read **side effects** carefully

---

## 🚀 Quick Start

1. **Run test**: `python3 test_comprehensive_recommendations.py`
2. **Try terminal**: `python3 main.py` → Enter "throat pain"
3. **Launch web app**: `streamlit run streamlit_app.py`
4. **Check stats**: `python3 verify_database.py`

---

**Version**: 3.0  
**Status**: ✅ Production Ready  
**Coverage**: 100% for common conditions  
**Database**: 40 drugs, 50+ herbs, 18 categories
