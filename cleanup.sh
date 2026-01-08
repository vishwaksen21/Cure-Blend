#!/bin/bash

# Remove backup files (already done, but adding for completeness)
rm -f streamlit_app_backup.py streamlit_app_v2_backup.py streamlit_app_v3_backup.py

# Remove redundant documentation files
rm -f PHARMA_FIX_QUICKREF.txt
rm -f TERMINAL_FIX_QUICKREF.txt
rm -f TERMINAL_FIX_SUMMARY.md
rm -f LOGIC_FIXES_SUMMARY.txt
rm -f QUICK_WINS_SUMMARY.txt
rm -f QUICK_REFERENCE.txt
rm -f TESTING_COMPLETE.txt
rm -f TOP_10_IMPROVEMENTS.txt
rm -f V3_ENHANCEMENT_VISUAL.txt
rm -f DEPLOY_QUICK_START.txt

# Remove redundant test/debug files
rm -f test_dengue_fix.py
rm -f test_fever_headache.py
rm -f test_quick_diagnosis.py
rm -f test_failed_cases.py
rm -f test_typhoid_debug.py
rm -f test_debug_confidence.py
rm -f test_pharma_fix.py
rm -f test_various_inputs.py
rm -f test_core_functions.py
rm -f test_disease_awareness.py
rm -f verify_fix.py
rm -f test_results_comprehensive.json

# Remove other redundant files
rm -f paper_corrected.tex
rm -f benchmark_system.py
rm -f quick_test_drugs.py

echo "Cleanup complete!"
ls -lh | wc -l
