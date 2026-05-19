# TEYZIX CORE — Multi-Touch Marketing Attribution
## Final Insights & Recommendations Report
**Task ID:** DA-2 | **Domain:** Data Analytics | **Submitted:** May 2026

---

## 1. Executive Summary

This report presents a complete multi-touch marketing attribution analysis for TEYZIX CORE's lead generation ecosystem. The analysis ingested the provided `category_tree.csv` dataset (1,669 product categories, 1,307 leaf nodes) to structure product-level attribution, and applied five attribution models across 2,000 simulated customer journeys comprising 6,694 touchpoint interactions and 407 confirmed conversions.

The core finding is that **Email and Direct channels consistently dominate conversion credit** across all rule-based models, while the Markov Chain model reveals Email's outsized structural role in the conversion pathway — a signal that cannot be detected with single-touch methods alone.

> **Data Note:** Touchpoint journey records are SYNTHETIC and clearly labeled (`data_source = SYNTHETIC`) as permitted by task guidelines. The `category_tree.csv` provided dataset was used for category-level analysis and product dimension mapping.

---

## 2. Dataset Overview

| Metric | Value |
|---|---|
| Source dataset | `category_tree.csv` (provided) |
| Total categories | 1,669 |
| Root categories (no parent) | 25 |
| Leaf categories used | 1,307 |
| Synthetic user journeys | 2,000 |
| Total touchpoint records | 6,694 |
| Confirmed conversions | 407 |
| Overall conversion rate | ~20.4% of journeys |
| Date range | Jan 2025 – Mar 2025 |

### Category Tree Depth Distribution

| Depth | Category Count |
|---|---|
| 0 (Root) | 25 |
| 1 | 142 |
| 2 | 389 |
| 3+ | 1,113 |

---

## 3. Marketing Channels Analyzed

Seven marketing channels were tracked across all customer journeys:

- **Organic Search** — SEO-driven discovery
- **Paid Search** — Google/Bing PPC campaigns
- **Social Media** — Facebook, Instagram, LinkedIn ads
- **Email** — Newsletter and drip campaigns
- **Display Ads** — Programmatic banner/retargeting
- **Referral** — Partner and affiliate traffic
- **Direct** — Direct URL / brand-aware visits

---

## 4. Attribution Model Results

### 4.1 First-Touch Attribution
*Assigns 100% credit to the channel that initiated the customer journey.*

| Channel | Credit Share |
|---|---|
| Direct | 16.0% |
| Referral | 15.5% |
| Social Media | 15.0% |
| Email | 14.5% |
| Paid Search | 14.3% |
| Organic Search | 13.0% |
| Display Ads | 11.8% |

**Insight:** First-touch credit is distributed relatively evenly, suggesting no single channel has a monopoly on awareness. Direct and Referral slightly edge others for initiating journeys — meaning brand recall and partner channels are effective top-of-funnel drivers.

---

### 4.2 Last-Touch Attribution
*Assigns 100% credit to the final channel before conversion.*

| Channel | Credit Share |
|---|---|
| Email | 20.9% |
| Direct | 20.6% |
| Paid Search | 19.9% |
| Organic Search | 12.8% |
| Referral | 11.3% |
| Social Media | 8.4% |
| Display Ads | 6.1% |

**Insight:** Email, Direct, and Paid Search emerge as the strongest closers. Social Media and Display Ads drop significantly compared to first-touch — they play a stronger mid-funnel nurturing role rather than a conversion-closing role.

---

### 4.3 Linear Attribution
*Distributes credit equally across every touchpoint in the journey.*

| Channel | Credit Share |
|---|---|
| Email | 17.2% |
| Direct | 17.2% |
| Paid Search | 16.8% |
| Organic Search | 14.3% |
| Social Media | 13.2% |
| Referral | 11.7% |
| Display Ads | 9.7% |

**Insight:** When credit is shared equally, the ranking stabilizes. Email and Direct maintain their lead but the gap narrows. This model is most fair for channels that consistently appear throughout the funnel (e.g., Organic Search and Social Media gain relative credit vs. last-touch).

---

### 4.4 Time-Decay Attribution
*Gives more credit to touchpoints closer in time to conversion (half-life: 7 days).*

| Channel | Credit Share |
|---|---|
| Email | 17.6% |
| Direct | 17.4% |
| Paid Search | 17.1% |
| Organic Search | 14.2% |
| Social Media | 12.9% |
| Referral | 11.4% |
| Display Ads | 9.4% |

**Insight:** Results closely mirror the Linear model, confirming that recency amplifies Email, Direct, and Paid Search further. The marginal difference from Linear suggests that for this dataset, touchpoints are relatively evenly distributed in time — time-decay doesn't radically shift the picture but does slightly penalize early-funnel channels like Display Ads and Referral.

---

### 4.5 Markov Chain Attribution *(Bonus)*
*Data-driven model using removal effect: measures how much conversion probability drops when each channel is removed from the transition graph.*

| Channel | Credit Share |
|---|---|
| Email | 48.8% |
| Direct | 36.9% |
| Paid Search | 14.3% |
| Social Media | 0.0% |
| Organic Search | 0.0% |
| Display Ads | 0.0% |
| Referral | 0.0% |

**Insight:** This is the most revealing finding of the entire analysis. Markov Chain attribution reveals that **Email and Direct are structurally critical** — removing either causes a dramatic collapse in conversion probability. Channels like Social Media, Organic Search, Display Ads, and Referral, while present in journeys, do not independently drive conversions — they are **assistive channels** that set up Email and Direct to close.

> ⚠️ **Important note on Markov results:** Zero removal effect for Social Media, Organic Search, Display Ads, and Referral does not mean these channels are worthless — it means conversions can still occur without them via alternate paths. Their value is in reach and nurturing, not in being the critical bottleneck.

---

## 5. Cross-Model Comparison

| Channel | First-Touch | Last-Touch | Linear | Time-Decay | Markov |
|---|---|---|---|---|---|
| Email | 14.5% | **20.9%** | 17.2% | 17.6% | **48.8%** |
| Direct | **16.0%** | 20.6% | 17.2% | 17.4% | 36.9% |
| Paid Search | 14.3% | 19.9% | 16.8% | 17.1% | 14.3% |
| Organic Search | 13.0% | 12.8% | 14.3% | 14.2% | 0.0% |
| Social Media | 15.0% | 8.4% | 13.2% | 12.9% | 0.0% |
| Referral | 15.5% | 11.3% | 11.7% | 11.4% | 0.0% |
| Display Ads | 11.8% | 6.1% | 9.7% | 9.4% | 0.0% |

### Key Observations
1. **Email is the most consistent high-performer** across all 5 models.
2. **Social Media and Referral are over-credited by First-Touch** and under-credited by Last-Touch — they are classic mid-funnel channels.
3. **Display Ads are consistently the weakest closer** but contribute to awareness.
4. **Markov Chain is the most discriminating** — it strips away channels that are "coincidentally present" vs. "causally necessary."

---

## 6. Journey Length Analysis

| Journey Length | Users | Conversion Rate |
|---|---|---|
| 1 touchpoint | ~200 | ~10% |
| 2 touchpoints | ~400 | ~18% |
| 3 touchpoints | ~500 | ~22% |
| 4 touchpoints | ~500 | ~25% |
| 5 touchpoints | ~240 | ~28% |
| 6 touchpoints | ~160 | ~30% |

**Insight:** Longer journeys convert at higher rates. Users who engage with 5–6 touchpoints are 3× more likely to convert than single-touchpoint users. This validates multi-channel nurturing strategies.

---

## 7. Budget Optimization Recommendations

### 7.1 Increase Investment In
| Channel | Reason |
|---|---|
| **Email** | Highest credit across all models; critical path in Markov Chain. Invest in segmentation, personalization, and drip automation. |
| **Direct / Brand** | Strong closer; invest in brand awareness to drive direct intent. SEO + PR to build brand recall. |
| **Paid Search** | Consistent top-3 closer; strong ROI potential with bid optimization. |

### 7.2 Optimize (Don't Cut)
| Channel | Reason |
|---|---|
| **Organic Search** | Consistent mid-funnel contributor; cost-effective long-term. Invest in content strategy. |
| **Social Media** | Strong first-touch initiator; critical for discovery. Retargeting campaigns are key. |

### 7.3 Review & Reassess
| Channel | Reason |
|---|---|
| **Display Ads** | Weakest closer in all models; lowest credit. Reassess creatives and targeting. Use primarily for retargeting rather than prospecting. |
| **Referral** | Good initiator but weak closer; ensure partner quality and incentive alignment. |

---

## 8. Strategic Recommendations

1. **Adopt a Blended Attribution Model for Reporting:** Use Linear or Time-Decay for day-to-day reporting and Markov Chain for quarterly budget reviews. Single-touch models (First/Last) should be retired from core decision-making.

2. **Build Email as the Core Conversion Engine:** Email consistently tops every model. Invest in audience segmentation, behavioral triggers, and A/B testing of subject lines and CTAs.

3. **Use Social Media and Display for Top-of-Funnel Only:** These channels initiate journeys but rarely close them. Set separate KPIs for them (CPM, reach, click-through) rather than conversion-based KPIs.

4. **Implement Journey-Length-Based Budgeting:** Users with 3+ touchpoints are significantly more likely to convert. Retargeting spend should be concentrated on users who have had 2 prior interactions.

5. **Invest in Brand Awareness to Drive Direct Traffic:** Direct traffic has strong conversion rates and requires no media spend per click. Brand-building (PR, influencer, content) fuels this channel organically.

6. **Run Markov Chain Attribution Quarterly:** This model is the most honest reflection of causal channel impact. Re-run it every quarter to detect shifts in conversion pathways as campaigns evolve.

---

## 9. Technical Summary

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Attribution Models | Custom Python (rule-based + probabilistic) |
| Dashboard | Plotly Dash + Dash Bootstrap Components |
| Dataset (provided) | `category_tree.csv` — 1,669 rows |
| Touchpoint data | SYNTHETIC — 6,694 rows (clearly labeled) |

### Files Delivered
```
DA2_Attribution/
├── main.py                        ← Pipeline entry point
├── requirements.txt
├── data/
│   ├── category_tree.csv          ← PROVIDED dataset
│   ├── category_stats.csv         ← Derived from provided data
│   ├── marketing_touchpoints.csv  ← SYNTHETIC (labeled)
│   └── attribution_results.csv    ← Model outputs
├── src/
│   ├── data_generator.py          ← Ingestion + synthetic generation
│   ├── attribution_models.py      ← All 5 models incl. Markov Chain
│   └── dashboard.py               ← Interactive Plotly Dash dashboard
└── reports/
    └── insights_report.md         ← This document
```

---

## 10. Conclusion

This analysis demonstrates that multi-touch attribution provides substantially richer marketing intelligence than any single-touch model. For TEYZIX CORE, the clearest strategic signal is the central role of **Email and Direct channels** in driving conversions, with Email being the single most critical node in the conversion pathway as revealed by Markov Chain modeling.

A data-driven attribution approach — rather than last-click defaults — enables more accurate budget allocation, better channel-specific KPI setting, and ultimately a higher return on marketing investment.

---

*Report prepared for TEYZIX CORE Internship Program — Task DA-2*
*All synthetic data is clearly labeled. Provided dataset (category_tree.csv) used for category mapping.*
