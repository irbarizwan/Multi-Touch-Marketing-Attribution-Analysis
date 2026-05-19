"""
data_generator.py
-----------------
Ingests the provided category_tree.csv dataset to extract product categories,
then generates a realistic synthetic marketing touchpoint dataset.

NOTE: The touchpoint journey data below is SYNTHETIC (clearly labeled).
The category_tree.csv is the provided dataset used to derive product categories
for the simulation, as per task requirements.
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# ─── Reproducibility ────────────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_CATEGORY_FILE = os.path.join(DATA_DIR, "category_tree.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "marketing_touchpoints.csv")


# ─── Step 1: Load & Process Provided Dataset ────────────────────────────────
def load_category_tree(path: str) -> pd.DataFrame:
    """
    Loads the provided category_tree.csv dataset.
    Returns a cleaned DataFrame with category hierarchy information.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df["parentid"] = df["parentid"].fillna(-1).astype(int)
    df["is_root"] = df["parentid"] == -1
    df["depth"] = 0  # will be computed below
    return df


def compute_depths(df: pd.DataFrame) -> pd.DataFrame:
    """Compute tree depth for each category node."""
    id_to_parent = dict(zip(df["categoryid"], df["parentid"]))
    depth_cache = {}

    def get_depth(cid):
        if cid in depth_cache:
            return depth_cache[cid]
        pid = id_to_parent.get(cid, -1)
        if pid == -1:
            depth_cache[cid] = 0
        else:
            depth_cache[cid] = 1 + get_depth(pid)
        return depth_cache[cid]

    df["depth"] = df["categoryid"].apply(get_depth)
    return df


def extract_leaf_categories(df: pd.DataFrame) -> list:
    """Return leaf node category IDs (categories with no children)."""
    parent_ids = set(df[df["parentid"] != -1]["parentid"].tolist())
    leaves = df[~df["categoryid"].isin(parent_ids)]["categoryid"].tolist()
    return leaves


# ─── Step 2: Generate Synthetic Touchpoint Data ─────────────────────────────
# [SYNTHETIC DATA — clearly labeled as required by task instructions]

CHANNELS = ["Organic Search", "Paid Search", "Social Media",
            "Email", "Display Ads", "Referral", "Direct"]

# Realistic channel transition probabilities (first → next touchpoint)
CHANNEL_WEIGHTS = {
    "Organic Search": [0.20, 0.20, 0.15, 0.15, 0.10, 0.10, 0.10],
    "Paid Search":    [0.15, 0.25, 0.15, 0.15, 0.15, 0.05, 0.10],
    "Social Media":   [0.10, 0.15, 0.30, 0.15, 0.15, 0.10, 0.05],
    "Email":          [0.15, 0.10, 0.10, 0.30, 0.10, 0.10, 0.15],
    "Display Ads":    [0.15, 0.20, 0.20, 0.10, 0.20, 0.05, 0.10],
    "Referral":       [0.20, 0.10, 0.15, 0.10, 0.10, 0.25, 0.10],
    "Direct":         [0.15, 0.10, 0.10, 0.15, 0.05, 0.10, 0.35],
}

CONVERSION_PROB = {
    "Organic Search": 0.18,
    "Paid Search":    0.22,
    "Social Media":   0.12,
    "Email":          0.25,
    "Display Ads":    0.10,
    "Referral":       0.20,
    "Direct":         0.28,
}


def generate_journey(user_id: int, leaf_categories: list,
                     start_date: datetime) -> list:
    """Generate a single user's multi-touch marketing journey."""
    n_touchpoints = np.random.choice([1, 2, 3, 4, 5, 6],
                                     p=[0.10, 0.20, 0.25, 0.25, 0.12, 0.08])
    first_channel = random.choice(CHANNELS)
    journey = []
    current_channel = first_channel
    current_time = start_date + timedelta(days=random.randint(0, 60))
    category_id = random.choice(leaf_categories)

    for step in range(n_touchpoints):
        gap_hours = random.randint(1, 72)
        current_time += timedelta(hours=gap_hours)
        converted = False

        if step == n_touchpoints - 1:
            # Last touchpoint — determine conversion
            conv_p = CONVERSION_PROB[current_channel]
            # Longer journeys have higher conversion (engagement signal)
            conv_p *= (1 + 0.05 * step)
            converted = random.random() < min(conv_p, 0.95)

        journey.append({
            "user_id": f"U{user_id:05d}",
            "session_id": f"S{user_id:05d}_{step+1}",
            "touchpoint_order": step + 1,
            "channel": current_channel,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "category_id": category_id,
            "converted": int(converted),
            "journey_length": n_touchpoints,
            "data_source": "SYNTHETIC",   # <-- clearly labeled
        })

        # Next channel
        weights = CHANNEL_WEIGHTS[current_channel]
        current_channel = np.random.choice(CHANNELS, p=weights)

    return journey


def generate_touchpoint_dataset(n_users: int, leaf_categories: list) -> pd.DataFrame:
    """[SYNTHETIC DATA] Generate full multi-touch marketing dataset."""
    start_date = datetime(2025, 1, 1)
    records = []
    for uid in range(1, n_users + 1):
        records.extend(generate_journey(uid, leaf_categories, start_date))
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)
    return df


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    print("[1/4] Loading provided category_tree.csv dataset...")
    cat_df = load_category_tree(RAW_CATEGORY_FILE)
    cat_df = compute_depths(cat_df)
    leaf_cats = extract_leaf_categories(cat_df)
    print(f"      → {len(cat_df)} categories loaded | {len(leaf_cats)} leaf nodes identified")

    # Save processed category stats
    cat_stats = cat_df.groupby("depth")["categoryid"].count().reset_index()
    cat_stats.columns = ["tree_depth", "category_count"]
    cat_stats.to_csv(os.path.join(DATA_DIR, "category_stats.csv"), index=False)
    print("      → category_stats.csv saved")

    print("[2/4] Generating SYNTHETIC touchpoint data (2000 user journeys)...")
    tp_df = generate_touchpoint_dataset(n_users=2000, leaf_categories=leaf_cats)
    print(f"      → {len(tp_df)} touchpoint records generated")
    print(f"      → Conversions: {tp_df['converted'].sum()} "
          f"({tp_df['converted'].mean()*100:.1f}% of last touchpoints)")

    print("[3/4] Saving marketing_touchpoints.csv...")
    tp_df.to_csv(OUTPUT_FILE, index=False)
    print(f"      → Saved to {OUTPUT_FILE}")

    print("[4/4] Preview:")
    print(tp_df.head(10).to_string())
    return tp_df, cat_df


if __name__ == "__main__":
    main()
