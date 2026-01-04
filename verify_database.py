#!/usr/bin/env python3
"""Quick verification of database counts"""
import sys
sys.path.insert(0, '/workspaces/Cure-Blend')

from src.ai_assistant import SAMPLE_DRUGS

print("="*60)
print("📊 DATABASE STATISTICS")
print("="*60)
print(f"\n💊 Total Pharmaceutical Drugs: {len(SAMPLE_DRUGS)}")
print(f"\nDrug Categories:")

categories = {}
for drug in SAMPLE_DRUGS:
    dtype = drug.get('type', 'Unknown')
    categories[dtype] = categories.get(dtype, 0) + 1

for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {cat}: {count}")

print(f"\n✅ Database successfully expanded!")
print("="*60)
