# Uplift — A/B Testing Framework

An end-to-end experimentation platform built on Google BigQuery and Streamlit. Uplift goes beyond basic significance testing — it combines frequentist, Bayesian, and causal inference methods to give analysts a complete picture of experiment results.

Built on the Google Analytics sample dataset (714K users, 903K sessions, 3 simulated experiments).

---

## Features

**Experiment Health Monitoring**
Real-time SRM detection, power analysis, and a composite health score so you know if your experiment is trustworthy before you read the results.

![Health Cards](screenshots/health_cards.png)

---

**Actionable Recommendations**
Ship, don't ship, or keep running — with plain-English reasoning combining both frequentist and Bayesian evidence.

![Recommendation Banner](screenshots/recommendation.png)

---

**Bayesian Analysis**
P(Treatment > Control) with a credible interval and visual gauge. Threshold-based shipping decision: >95% = ship, 80–95% = keep running, <80% = not enough evidence.

![Bayesian Gauge](screenshots/bayesian.png)

---

**Difference-in-Differences**
Controls for pre-existing trends between groups to isolate the true causal effect of the treatment — not just the observed difference.

![DiD Chart](screenshots/did.png)

---

**CUPED — Variance Reduction**
Uses pre-experiment behavior to reduce noise and produce a more precise estimate of the treatment effect. The same technique used by Netflix, Spotify, and Booking.com.

![CUPED](screenshots/cuped.png)

---

**Cohort Retention**
Tracks whether the treatment effect holds over time or fades after the first week — distinguishing genuine improvement from novelty effects.

![Cohort Retention](screenshots/cohort_retention.png)

---

**Guardrail Metrics**
Monitors secondary metrics (bounce rate, sessions, pageviews, time on site, revenue) to catch unintended side effects while improving the primary metric.

![Guardrails](screenshots/guardrails.png)

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
└── screenshots/        # README screenshots
```
