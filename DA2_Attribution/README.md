# TEYZIX CORE — Multi-Touch Marketing Attribution Analysis
**Task ID:** DA-2 | **Domain:** Data Analytics | **Difficulty:** Advanced

---

## Project Structure

```
DA2_Attribution/
├── main.py                        ← Run this first
├── requirements.txt               ← Python dependencies
├── data/
│   ├── category_tree.csv          ← PROVIDED dataset (do not modify)
│   ├── category_stats.csv         ← Auto-generated from provided data
│   ├── marketing_touchpoints.csv  ← SYNTHETIC touchpoint data (auto-generated)
│   └── attribution_results.csv    ← Attribution model outputs (auto-generated)
├── src/
│   ├── data_generator.py          ← Step 1: Data ingestion & generation
│   ├── attribution_models.py      ← Step 2: All 5 attribution models
│   └── dashboard.py               ← Step 3: Interactive Plotly Dash dashboard
└── reports/
    └── insights_report.md         ← Final marketing insights report
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the full pipeline (data generation + all models)
```bash
python main.py
```

### 3. Launch the interactive dashboard
```bash
python src/dashboard.py
```
Then open: **http://127.0.0.1:8050**

---

## Attribution Models Implemented

| Model | Description |
|---|---|
| First-Touch | 100% credit to first touchpoint |
| Last-Touch | 100% credit to last touchpoint |
| Linear | Equal credit across all touchpoints |
| Time-Decay | More credit to touchpoints closer to conversion |
| **Markov Chain** *(Bonus)* | Data-driven removal effect model |

---

## Dataset Notes

- **Provided dataset:** `category_tree.csv` — contains 1,669 product category hierarchy records used to derive leaf-level product categories for journey simulation.
- **Synthetic data:** `marketing_touchpoints.csv` — clearly labeled with `data_source = SYNTHETIC` column as required by task guidelines. Generated using realistic channel transition probabilities seeded from the category tree.

---

## Key Findings

- **Email** is the top-performing channel across all 5 models
- **Markov Chain** reveals Email and Direct as structurally critical conversion paths
- **Social Media** and **Display Ads** are strong awareness channels but weak closers
- Longer customer journeys (4–6 touchpoints) convert at 3× higher rates than single-touch
