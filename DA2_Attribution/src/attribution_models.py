"""
attribution_models.py
---------------------
Implements five marketing attribution models:
  1. First-Touch Attribution
  2. Last-Touch Attribution
  3. Linear Attribution
  4. Time-Decay Attribution
  5. Markov Chain Attribution  ← Bonus challenge
"""

import pandas as pd
import numpy as np
from itertools import permutations
from collections import defaultdict


# ─── Preprocessing ───────────────────────────────────────────────────────────

def load_and_validate(filepath: str) -> pd.DataFrame:
    """Load touchpoints CSV, validate schema, return clean DataFrame."""
    df = pd.read_csv(filepath, parse_dates=["timestamp"])
    required = {"user_id", "touchpoint_order", "channel",
                "timestamp", "converted", "journey_length"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df = df.sort_values(["user_id", "touchpoint_order"]).reset_index(drop=True)
    return df


def get_converted_journeys(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to only journeys that resulted in a conversion."""
    converted_users = df[df["converted"] == 1]["user_id"].unique()
    return df[df["user_id"].isin(converted_users)].copy()


# ─── Model 1: First-Touch Attribution ────────────────────────────────────────

def first_touch_attribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns 100% of conversion credit to the FIRST touchpoint in the journey.
    Best for understanding awareness-stage channels.
    """
    conv_df = get_converted_journeys(df)
    first = conv_df.groupby("user_id").apply(
        lambda g: g.sort_values("touchpoint_order").iloc[0]["channel"]
    ).reset_index()
    first.columns = ["user_id", "channel"]
    result = first["channel"].value_counts().reset_index()
    result.columns = ["channel", "conversions"]
    result["credit"] = result["conversions"] / result["conversions"].sum()
    result["model"] = "First-Touch"
    return result.sort_values("credit", ascending=False).reset_index(drop=True)


# ─── Model 2: Last-Touch Attribution ─────────────────────────────────────────

def last_touch_attribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns 100% of conversion credit to the LAST touchpoint.
    Best for understanding closing/conversion-stage channels.
    """
    conv_df = get_converted_journeys(df)
    last = conv_df.groupby("user_id").apply(
        lambda g: g.sort_values("touchpoint_order").iloc[-1]["channel"]
    ).reset_index()
    last.columns = ["user_id", "channel"]
    result = last["channel"].value_counts().reset_index()
    result.columns = ["channel", "conversions"]
    result["credit"] = result["conversions"] / result["conversions"].sum()
    result["model"] = "Last-Touch"
    return result.sort_values("credit", ascending=False).reset_index(drop=True)


# ─── Model 3: Linear Attribution ─────────────────────────────────────────────

def linear_attribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Distributes conversion credit EQUALLY across all touchpoints.
    Best for balanced multi-channel credit.
    """
    conv_df = get_converted_journeys(df)
    channel_credits = defaultdict(float)

    for _, journey in conv_df.groupby("user_id"):
        n = len(journey)
        for _, row in journey.iterrows():
            channel_credits[row["channel"]] += 1.0 / n

    result = pd.DataFrame(list(channel_credits.items()),
                          columns=["channel", "credit"])
    total = result["credit"].sum()
    result["credit"] = result["credit"] / total
    result["conversions"] = (result["credit"] * len(conv_df["user_id"].unique())).round(1)
    result["model"] = "Linear"
    return result.sort_values("credit", ascending=False).reset_index(drop=True)


# ─── Model 4: Time-Decay Attribution ─────────────────────────────────────────

def time_decay_attribution(df: pd.DataFrame, half_life_days: float = 7.0) -> pd.DataFrame:
    """
    Gives MORE credit to touchpoints CLOSER in time to conversion.
    Uses exponential decay with configurable half-life (default: 7 days).
    """
    conv_df = get_converted_journeys(df).copy()
    channel_credits = defaultdict(float)

    for _, journey in conv_df.groupby("user_id"):
        journey = journey.sort_values("timestamp")
        conversion_time = journey["timestamp"].max()
        weights = []
        for _, row in journey.iterrows():
            delta_days = (conversion_time - row["timestamp"]).total_seconds() / 86400
            weight = np.exp(-np.log(2) * delta_days / half_life_days)
            weights.append(weight)
        total_weight = sum(weights)
        for (_, row), w in zip(journey.iterrows(), weights):
            channel_credits[row["channel"]] += w / total_weight

    result = pd.DataFrame(list(channel_credits.items()),
                          columns=["channel", "credit"])
    total = result["credit"].sum()
    result["credit"] = result["credit"] / total
    result["conversions"] = (result["credit"] * len(conv_df["user_id"].unique())).round(1)
    result["model"] = "Time-Decay"
    return result.sort_values("credit", ascending=False).reset_index(drop=True)


# ─── Model 5: Markov Chain Attribution (Bonus) ───────────────────────────────

def markov_chain_attribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    [BONUS] Markov Chain-based data-driven attribution.
    Computes removal effect: how much conversion probability drops
    when each channel is removed from the transition graph.
    Steps:
      1. Build transition probability matrix (including 'Start', 'Conversion', 'Null')
      2. For each channel, remove it and recompute conversion probability
      3. Credit = (base_prob - removed_prob) / sum(all removal effects)
    """
    conv_df = get_converted_journeys(df)
    all_journeys_df = df.copy()  # includes non-converting for transition matrix

    START = "Start"
    CONV = "Conversion"
    NULL = "Null"

    # Build transition counts
    transition_counts = defaultdict(lambda: defaultdict(int))

    for uid, journey in all_journeys_df.groupby("user_id"):
        journey = journey.sort_values("touchpoint_order")
        channels = journey["channel"].tolist()
        converted = journey["converted"].max()

        # Start → first channel
        transition_counts[START][channels[0]] += 1

        for i in range(len(channels) - 1):
            transition_counts[channels[i]][channels[i + 1]] += 1

        # Last channel → Conversion or Null
        if converted:
            transition_counts[channels[-1]][CONV] += 1
        else:
            transition_counts[channels[-1]][NULL] += 1

    # Convert to transition probabilities
    states = set()
    for src, targets in transition_counts.items():
        states.add(src)
        for tgt in targets:
            states.add(tgt)

    def build_transition_matrix(excluded_channel=None):
        tm = {}
        for src, targets in transition_counts.items():
            if src == excluded_channel:
                continue
            total = sum(v for k, v in targets.items()
                        if k != excluded_channel)
            if total == 0:
                continue
            tm[src] = {k: v / total for k, v in targets.items()
                       if k != excluded_channel}
        return tm

    def compute_conversion_probability(tm, max_steps=1000):
        """Run random walk on transition matrix to estimate P(conversion)."""
        n_simulations = 5000
        conversions = 0
        for _ in range(n_simulations):
            state = START
            for _ in range(max_steps):
                if state not in tm:
                    break
                targets = tm[state]
                if not targets:
                    break
                state = np.random.choice(list(targets.keys()),
                                         p=list(targets.values()))
                if state == CONV:
                    conversions += 1
                    break
                elif state == NULL:
                    break
        return conversions / n_simulations

    # Base conversion probability
    base_tm = build_transition_matrix()
    base_prob = compute_conversion_probability(base_tm)

    # Removal effects for each real channel
    real_channels = [c for c in states
                     if c not in (START, CONV, NULL)]
    removal_effects = {}
    for ch in real_channels:
        tm_removed = build_transition_matrix(excluded_channel=ch)
        prob_removed = compute_conversion_probability(tm_removed)
        removal_effects[ch] = max(0, base_prob - prob_removed)

    total_effect = sum(removal_effects.values())
    if total_effect == 0:
        total_effect = 1e-9  # avoid divide-by-zero

    result_rows = []
    for ch, effect in removal_effects.items():
        result_rows.append({
            "channel": ch,
            "credit": effect / total_effect,
            "conversions": round(effect / total_effect * len(
                conv_df["user_id"].unique()), 1),
            "model": "Markov Chain",
        })

    result = pd.DataFrame(result_rows)
    return result.sort_values("credit", ascending=False).reset_index(drop=True)


# ─── Run All Models ───────────────────────────────────────────────────────────

def run_all_models(filepath: str) -> dict:
    """Load data and run all 5 attribution models. Returns dict of DataFrames."""
    print("[Attribution] Loading touchpoint data...")
    df = load_and_validate(filepath)
    print(f"  → {len(df)} records | {df['user_id'].nunique()} users")

    print("[Attribution] Running First-Touch model...")
    ft = first_touch_attribution(df)

    print("[Attribution] Running Last-Touch model...")
    lt = last_touch_attribution(df)

    print("[Attribution] Running Linear model...")
    lin = linear_attribution(df)

    print("[Attribution] Running Time-Decay model...")
    td = time_decay_attribution(df)

    print("[Attribution] Running Markov Chain model (Bonus)...")
    mc = markov_chain_attribution(df)

    results = {
        "First-Touch": ft,
        "Last-Touch": lt,
        "Linear": lin,
        "Time-Decay": td,
        "Markov Chain": mc,
    }

    # Combined long-format DataFrame for visualization
    combined = pd.concat(results.values(), ignore_index=True)
    combined.to_csv(
        filepath.replace("marketing_touchpoints.csv", "attribution_results.csv"),
        index=False
    )
    print("[Attribution] All models complete. Results saved.")
    return results, combined, df


if __name__ == "__main__":
    import os
    fp = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                      "data", "marketing_touchpoints.csv")
    results, combined, df = run_all_models(fp)
    for model_name, res in results.items():
        print(f"\n── {model_name} ──")
        print(res.to_string(index=False))
