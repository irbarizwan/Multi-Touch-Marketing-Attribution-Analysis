"""
main.py
-------
Entry point for the TEYZIX CORE Multi-Touch Attribution pipeline.
Runs data generation → attribution models → saves results.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from data_generator import main as generate_data
from attribution_models import run_all_models

DATA_DIR = os.path.join(BASE_DIR, "data")
TP_FILE = os.path.join(DATA_DIR, "marketing_touchpoints.csv")


def run_pipeline():
    print("=" * 60)
    print("  TEYZIX CORE — Multi-Touch Attribution Pipeline")
    print("  Task DA-2 | Data Analytics")
    print("=" * 60)

    # Step 1 — Generate / validate data
    print("\n[STEP 1] Data Ingestion & Generation")
    generate_data()

    # Step 2 — Run attribution models
    print("\n[STEP 2] Running Attribution Models")
    results, combined, df = run_all_models(TP_FILE)

    # Step 3 — Print summary
    print("\n[STEP 3] Attribution Summary")
    print("-" * 50)
    for model_name, res in results.items():
        top = res.iloc[0]
        print(f"  {model_name:<18} → Top channel: {top['channel']:<16} "
              f"({top['credit']*100:.1f}%)")

    print("\n[DONE] All outputs saved to /data/")
    print("       Run `python src/dashboard.py` to launch the dashboard.")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
