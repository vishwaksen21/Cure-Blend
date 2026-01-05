# Manual Testing Guide for Cure-Blend

## Test URL
http://localhost:8501

## Test Cases

### TEST 1: Common Cold Symptoms ✅
**Input:** `fever, headache, runny nose, cough`
**Expected Results:**
- Disease detected (likely Common Cold or similar)
- Confidence level displayed
- Herbal recommendations shown (e.g., Ginger, Tulsi)
- Pharmaceutical recommendations shown (e.g., Paracetamol, Cetirizine)

---

### TEST 2: Detailed Symptoms (High Confidence) ✅
**Input:** `high fever 102F for 3 days, severe headache, body aches, extreme fatigue`
**Expected Results:**
- Higher confidence score (boosted by duration, severity, detail)
- Diagnostic symptom matching
- Confidence indicators visible
- Detailed recommendations

---

### TEST 3: Dengue Symptoms (Diagnostic Matching) ✅
**Input:** `high fever, severe headache behind eyes, joint pain, muscle pain, rash, nausea`
**Expected Results:**
- Should detect Dengue
- Confidence boosted by diagnostic symptoms (retro-orbital pain, joint pain)
- Specific Dengue recommendations
- Safety information displayed

---

### TEST 4: UTI Symptoms (Alias Matching) ✅
**Input:** `burning during urination, frequent urination, lower abdominal pain`
**Expected Results:**
- Should detect urinary tract infection (UTI)
- Antibiotic recommendations shown (filtered properly)
- Disease alias handling works

---

### TEST 5: Diabetes Symptoms ✅
**Input:** `excessive thirst, frequent urination, fatigue, blurred vision`
**Expected Results:**
- Should detect Diabetes
- Long-term management recommendations
- Lifestyle suggestions

---

### TEST 6: Malaria Symptoms ✅
**Input:** `high fever with chills, sweating, headache, nausea, muscle pain`
**Expected Results:**
- Should detect Malaria
- Specific diagnostic symptoms recognized
- Appropriate antimalarial recommendations

---

### TEST 7: Vague Symptoms (Low Confidence) ✅
**Input:** `not feeling well`
**Expected Results:**
- Low confidence score
- Follow-up questions appear
- Symptom checklist offered
- System asks for more details

---

### TEST 8: Stomach Issues ✅
**Input:** `stomach pain, nausea, vomiting, diarrhea`
**Expected Results:**
- Gastric condition detected
- Digestive health recommendations
- Herbal remedies (Ginger, Peppermint)
- Antacid recommendations

---

### TEST 9: Synonym Normalization ✅
**Input:** `temp, tummy ache, feeling sick`
**Expected Results:**
- Should normalize to: fever, stomach pain, nausea
- System processes correctly despite informal language
- Recommendations match normalized symptoms

---

### TEST 10: Emergency Symptoms ⚠️
**Input:** `severe chest pain, difficulty breathing, sudden weakness`
**Expected Results:**
- **EMERGENCY WARNING DISPLAYED**
- Red alert shown
- App execution stops after warning
- Emergency services message shown

---

## Structured Data Testing (Checklist)

### TEST 11: Using Symptom Checklist ✅
1. Open "Select Common Symptoms" expander
2. Check: Fever, Headache, Cough
3. Select duration: "3-7 days"
4. Move severity slider to 7
5. Click "Diagnose"

**Expected Results:**
- Confidence boosted by structured data
- Duration factor applied
- Severity factor considered
- Better accuracy than free text alone

---

## UI Element Testing

### TEST 12: Visual Components ✅
**Check:**
- ✅ Herbal recommendations show in native Streamlit expanders
- ✅ Pharmaceutical recommendations show in native Streamlit expanders
- ✅ Progress bars display correctly (green bars, not HTML)
- ✅ Confidence metrics show (with delta indicators)
- ✅ No raw HTML code visible
- ✅ No black sections with invisible text
- ✅ Success/warning/error messages display with proper colors

---

## Error Handling Testing

### TEST 13: Empty Input ⚠️
**Input:** (leave blank and click diagnose)
**Expected:** Error message asking for symptoms

### TEST 14: Special Characters 🔧
**Input:** `fever!!! headache??? @#$%`
**Expected:** System handles gracefully, processes valid words

### TEST 15: Very Long Input 📝
**Input:** (paste 500+ words of medical history)
**Expected:** System processes without crashing, may show performance message

---

## Drug Search Testing

### TEST 16: Drug Name with Parentheses (Regex Fix) ✅
**Search:** `Ibuprofen (Advil)`
**Expected Results:**
- Drug found correctly (no regex error)
- No console warnings about match groups
- Reviews displayed if available

### TEST 17: Antibiotic Filtering ✅
**Context:** After diagnosis requiring antibiotics
**Expected:**
- Antibiotic recommendations shown
- Keywords detected: antibiotic, antibacterial, antimicrobial
- Proper categorization

---

## Performance Checks

### TEST 18: Response Time ⏱️
**Check:**
- Diagnosis completes in < 3 seconds
- UI remains responsive
- No freezing or hanging

### TEST 19: Multiple Diagnoses 🔄
**Action:** Run 5 different diagnoses in sequence
**Expected:** Each works correctly, no memory leaks

---

## Console/Log Checks

### TEST 20: No Warnings ✅
**Check browser console and terminal:**
- ❌ No pandas regex warnings
- ❌ No deprecation warnings
- ❌ No unhandled exceptions
- ✅ Clean execution

---

## Testing Checklist Summary

- [ ] All 20 tests completed
- [ ] UI elements render correctly
- [ ] Confidence system working
- [ ] Emergency detection working
- [ ] No console errors/warnings
- [ ] App responsive and fast
- [ ] Recommendations relevant
- [ ] Error handling graceful

---

## How to Report Issues

If any test fails, note:
1. Test number and name
2. Exact input used
3. Expected vs actual result
4. Screenshots if UI issue
5. Console errors if any

