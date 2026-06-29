# Uplift — A/B Testing Framework

An end-to-end experimentation platform built on Google BigQuery and Streamlit. Uplift goes beyond basic significance testing — it combines frequentist, Bayesian, and causal inference methods to give analysts a complete picture of experiment results.

Built on the Google Analytics sample dataset (714K users, 903K sessions, 3 simulated experiments).

---

## Features

### Experiment Registry & Setup
Select experiments from a live BigQuery registry showing user counts, date ranges, metric types, and completion status — with full configuration controls for significance threshold, MDE, and practical effect size.

![Experiment Registry](<img width="1765" height="802" alt="Experiment Registry   Setup" src="https://github.com/user-attachments/assets/d3eddca7-ab47-4699-8869-4fe7ca099229" />
)

---

### Actionable Recommendations
Ship, don't ship, or keep running — with plain-English reasoning combining both frequentist and Bayesian evidence.

![Results Dashboard](<img width="1837" height="797" alt="Screenshot 2026-06-29 193145" src="https://github.com/user-attachments/assets/123794cc-8f13-4bec-a776-cecb334b1ee7" />
)

---

### Bayesian Analysis
P(Treatment > Control) with a credible interval and visual gauge. Threshold-based shipping decision: >95% = ship, 80–95% = keep running, <80% = not enough evidence.

![Bayesian Analysis](<img width="1757" height="747" alt="Screenshot 2026-06-29 193422" src="https://github.com/user-attachments/assets/7287beea-0e59-487c-8cbf-7202c6228a35" />
)

---

### Difference-in-Differences
Controls for pre-existing trends between groups to isolate the true causal effect of the treatment — not just the observed difference.

![Difference in Differences](<img width="1781" height="766" alt="Screenshot 2026-06-29 193303" src="https://github.com/user-attachments/assets/b2743d03-21e1-4c68-8d27-fdd2e1e331b5" />
)

---

### CUPED — Variance Reduction
Uses pre-experiment behavior to reduce noise and produce a more precise estimate of the treatment effect. The same technique used by Netflix, Spotify, and Booking.com.

![CUPED](<img width="1776" height="351" alt="Screenshot 2026-06-29 193445" src="https://github.com/user-attachments/assets/ca99f98c-f7ce-47a9-b248-45c47a3e6ffb" />
)

---

### Export & Summary
Full results table with absolute lift, relative lift, p-value, Bayesian probability, and recommendation — downloadable as CSV or TXT report.

![Export Summary](<img width="1797" height="792" alt="Screenshot 2026-06-29 193350" src="https://github.com/user-attachments/assets/cbf323ff-2ae3-4ba7-ad94-c19581b3c080" />
)

---

## Statistical Methods

| Method | Purpose |
|---|---|
| Chi-Square Test | Conversion rate significance (binary metrics) |
| Welch's T-Test | Continuous metric significance (revenue, time on site) |
| Bayesian A/B Test | Probability treatment beats control with credible interval |
| Difference-in-Differences | Causal effect controlling for pre-existing trends |
| CUPED | Variance reduction using pre-experiment covariates |
| Power Analysis | Sample size requirements and underpowered experiment detection |
| SRM Check | Sample ratio mismatch detection for experiment validity |
| Sequential Testing | Peeking correction to control false positive rate |
| Segment Analysis | Heterogeneous treatment effects across user segments |

---

## Data Pipeline

```
Google Analytics Sample Dataset (BigQuery Public Data)
        ↓
Data Cleaning (null removal, outlier capping at P99)
        ↓
User Feature Engineering (user_features table)
        ↓
Experiment Assignment (FARM_FINGERPRINT hash randomization)
        ↓
SQL Analysis Layer (experiment_results, daily_trends, cohort_retention, did_metrics, guardrail_metrics)
        ↓
stats_engine.py (11 statistical functions)
        ↓
Uplift Streamlit App (Setup → Results → Deep Dive → Export)
```

---

## Tech Stack

- **Data Warehouse:** Google BigQuery
- **Statistical Engine:** Python, SciPy, scikit-learn, NumPy
- **Frontend:** Streamlit, Plotly
- **Data:** Google Analytics sample dataset (bigquery-public-data)

---

## Run Locally

```bash
git clone https://github.com/varun200/ab-testing-framework.git
cd ab-testing-framework
pip install -r requirements.txt
streamlit run app.py
```

For BigQuery connection, set up Google Cloud credentials:
```bash
gcloud auth application-default login
```

---

## Project Structure

```
ab-testing-framework/
├── app.py              # Streamlit app (Setup, Results, Deep Dive, Export tabs)
├── stats_engine.py     # Statistical analysis functions
├── requirements.txt    # Python dependencies
├── screenshots/        # README screenshots
│   ├── experiment_registry.png
│   ├── results_dashboard.png
│   ├── bayesian_analysis.png
│   ├── did.png
│   ├── cuped.png
│   └── export_summary.png
└── README.md
```<img width="1765" height="802" alt="Experiment Registry   Setup" src="https://github.com/user-attachments/assets/cf764b82-3752-48bf-bc9b-097d5694670c" />
