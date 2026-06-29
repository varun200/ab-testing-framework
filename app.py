import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from google.cloud import bigquery
from stats_engine import (
    srm_check,
    chi_square_test,
    t_test,
    power_analysis,
    bayesian_ab_test,
    difference_in_differences,
    cuped_ttest,
    practical_significance,
    sequential_test_correction,
    segment_analysis
)

st.set_page_config(
    page_title="Uplift",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background-color: #0e0e14; }

.uplift-header {
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-bottom: 0px;
}

.workflow-card {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    height: 100%;
}

.workflow-number {
    font-size: 0.75rem;
    font-weight: 600;
    color: #7C83FD;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.workflow-title {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 6px;
}

.workflow-desc {
    font-size: 0.8rem;
    color: #666;
    line-height: 1.4;
}

.verdict-ship {
    background: linear-gradient(135deg, #0d2818 0%, #0a1f12 100%);
    border: 1px solid #00CC96;
    border-left: 4px solid #00CC96;
    padding: 24px 28px;
    border-radius: 12px;
    margin: 16px 0;
}

.verdict-no {
    background: linear-gradient(135deg, #2a0d0d 0%, #1f0a0a 100%);
    border: 1px solid #EF553B;
    border-left: 4px solid #EF553B;
    padding: 24px 28px;
    border-radius: 12px;
    margin: 16px 0;
}

.verdict-wait {
    background: linear-gradient(135deg, #2a2100 0%, #1f1800 100%);
    border: 1px solid #FFA15A;
    border-left: 4px solid #FFA15A;
    padding: 24px 28px;
    border-radius: 12px;
    margin: 16px 0;
}

.verdict-warn {
    background: linear-gradient(135deg, #1a1a2e 0%, #12122a 100%);
    border: 1px solid #7C83FD;
    border-left: 4px solid #7C83FD;
    padding: 24px 28px;
    border-radius: 12px;
    margin: 16px 0;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #444;
    margin-bottom: 14px;
    margin-top: 24px;
}

.hypothesis-box {
    background: #0a0a14;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 16px 20px;
    font-size: 0.9rem;
    color: #aaa;
    line-height: 1.8;
    margin: 12px 0;
}

.context-bar {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 16px;
}

div[data-testid="stMetric"] {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    color: #666 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #ffffff !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #0e0e14;
    border-bottom: 1px solid #1e1e2e;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 6px 6px 0 0;
    color: #555;
    font-size: 0.83rem;
    font-weight: 500;
    padding: 10px 20px;
}

.stTabs [aria-selected="true"] {
    background: #13131f;
    color: #ffffff;
    border-bottom: 2px solid #7C83FD;
}

.stButton > button {
    background: #7C83FD;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 12px 24px;
    font-size: 0.9rem;
}

.stButton > button:hover {
    background: #6366f1;
    transform: translateY(-1px);
}

.sig-bar-container {
    background: #1e1e2e;
    border-radius: 6px;
    height: 8px;
    width: 100%;
    margin: 6px 0;
    overflow: hidden;
}

.sig-bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
defaults = {
    'data': None, 'control': None, 'treatment': None,
    'config': {}, 'results': {}, 'analysis_complete': False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── HEADER ──
st.markdown('''
<div style="height:3px;background:linear-gradient(90deg,#7C83FD 0%,#00CC96 100%);margin-bottom:0;"></div>
''', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('''
    <div style="padding:10px 0 4px 0;">
        <div style="font-size:1.5rem;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">Uplift</div>
        <div style="font-size:0.72rem;color:#444;margin-top:2px;">Experimentation · Statistics · Decisions</div>
    </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown("<div style='padding-top:16px;'>", unsafe_allow_html=True)
    show_advanced = st.toggle("Advanced mode", value=False)
    st.markdown("</div>", unsafe_allow_html=True)

# Context bar when analysis is complete
if st.session_state.analysis_complete and st.session_state.config:
    config = st.session_state.config
    source = "BigQuery" if 'experiment_id' in config else "CSV"
    n_total = len(st.session_state.data) if st.session_state.data is not None else 0
    st.markdown(f"""
    <div class="context-bar">
        📊 Source: {source} &nbsp;·&nbsp; 
        👥 {n_total:,} users loaded &nbsp;·&nbsp;
        🎯 Metric: {config.get('metric_type', '').capitalize()} &nbsp;·&nbsp;
        α = {config.get('alpha', 0.05)}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── TABS ──
tab1, tab2, tab3, tab4 = st.tabs([
    "⚙️  Setup", "📊  Results", "🔬  Deep Dive", "📄  Export"
])

# ─────────────────────────────────────────
# TAB 1: SETUP
# ─────────────────────────────────────────
with tab1:

    # Landing state — show workflow if no data loaded
    if not st.session_state.analysis_complete:
        st.markdown('<p class="section-label">How it works</p>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="workflow-card">
                <div class="workflow-number">Step 1</div>
                <div class="workflow-title">📁 Upload Data</div>
                <div class="workflow-desc">Upload a CSV or connect directly to BigQuery</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="workflow-card">
                <div class="workflow-number">Step 2</div>
                <div class="workflow-title">⚙️ Configure</div>
                <div class="workflow-desc">Map columns, set significance threshold, define your hypothesis</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="workflow-card">
                <div class="workflow-number">Step 3</div>
                <div class="workflow-title">▶ Run Analysis</div>
                <div class="workflow-desc">Uplift runs power analysis, SRM check, and full statistical tests</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class="workflow-card">
                <div class="workflow-number">Step 4</div>
                <div class="workflow-title">📊 Get Results</div>
                <div class="workflow-desc">Clear verdict, health score, and export-ready report</div>
            </div>
            """, unsafe_allow_html=True)
        st.divider()

    st.markdown('<p class="section-label">Data Source</p>', unsafe_allow_html=True)
    data_source = st.radio("", options=["Upload CSV", "Connect BigQuery"],
                           horizontal=True, label_visibility="collapsed")
    st.divider()

    if data_source == "Upload CSV":
        with st.expander("What format does my data need to be in?"):
            st.markdown("""
            **Minimum 3 columns required:**

            | Column | What it is | Example values |
            |--------|-----------|----------------|
            | User ID | Unique per user | user_001, abc123 |
            | Group | Which group the user is in | control, treatment |
            | Metric | What you're measuring | 0/1 for conversion, or revenue amount |

            Optional: add a **date column** to enable time-based analysis in Deep Dive.
            """)
            st.code("""user_id,group,converted,revenue,date
u001,control,0,0,2024-01-01
u002,treatment,1,45.5,2024-01-01
u003,control,1,23.0,2024-01-02""")

        uploaded_file = st.file_uploader("", type=['csv'], label_visibility="collapsed")

        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ {len(df):,} rows loaded — {len(df.columns)} columns")

            with st.expander("Preview data"):
                st.dataframe(df.head(10), use_container_width=True)

            st.markdown('<p class="section-label">Column Mapping</p>', unsafe_allow_html=True)

            # Smart column detection
            cols = df.columns.tolist()
            def smart_default(options, keywords):
                for kw in keywords:
                    for col in options:
                        if kw.lower() in col.lower():
                            return options.index(col)
                return 0

            col1, col2, col3 = st.columns(3)
            with col1:
                user_idx = smart_default(cols, ['user', 'id', 'visitor'])
                user_col = st.selectbox("User ID", options=cols, index=user_idx)
            with col2:
                group_idx = smart_default(cols, ['group', 'variant', 'treatment', 'control'])
                group_col = st.selectbox("Group column", options=cols, index=group_idx)
            with col3:
                metric_idx = smart_default(cols, ['convert', 'revenue', 'metric', 'value', 'purchase'])
                metric_col = st.selectbox("Metric to test", options=cols, index=metric_idx)

            date_idx = smart_default(['None'] + cols, ['date', 'time', 'day'])
            date_col = st.selectbox("Date column (optional)", options=['None'] + cols, index=date_idx)

            if group_col:
                unique_groups = df[group_col].unique().tolist()
                st.caption(f"Groups detected: {unique_groups}")

            st.markdown('<p class="section-label">Experiment Configuration</p>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                metric_type = st.selectbox(
                    "Metric type",
                    options=["binary", "continuous"],
                    help="Binary = yes/no (converted, clicked, signed up). Continuous = a number (revenue, time, score)."
                )
                control_label = st.text_input("Control group label", value="control")
                treatment_label = st.text_input("Treatment group label", value="treatment")
            with col2:
                alpha = st.selectbox("Significance threshold (α)", options=[0.05, 0.01, 0.10],
                                     help="0.05 is industry standard. Below this = statistically significant.")
                baseline_rate = st.number_input("Current baseline rate (%)", 0.1, 100.0, 1.5, 0.1,
                                                help="Your metric rate before this experiment started.") / 100
                mde = st.number_input("Minimum detectable effect (%)", 0.1, 20.0, 0.2, 0.1,
                                      help="Smallest lift you want to reliably detect.") / 100

            min_practical = st.number_input(
                "Minimum practical effect (%) — business threshold",
                0.0, 20.0, 0.5, 0.1,
                help="Smallest lift that would actually matter to the business. A result can be statistically significant but too small to be worth shipping."
            )

            looks = st.number_input(
                "How many times have you checked results so far?",
                1, 20, 1, 1,
                help="If you've been peeking at results mid-experiment, we correct the p-value threshold to prevent false positives."
            )

            # Structured hypothesis
            st.markdown('<p class="section-label">Hypothesis</p>', unsafe_allow_html=True)
            st.caption("A good hypothesis has three parts: what changed, who it affects, and why you expect it to work.")
            col1, col2, col3 = st.columns(3)
            with col1:
                hyp_change = st.text_input("We changed", placeholder="e.g. the checkout button color")
            with col2:
                hyp_direction = st.selectbox("which will", ["increase", "decrease"])
            with col3:
                hyp_metric = st.text_input("metric", placeholder="e.g. conversion rate")
            hyp_reason = st.text_input("Because", placeholder="e.g. the new color is more visible and draws user attention")
            hyp_magnitude = st.text_input("Expected effect size", placeholder="e.g. 0.5% lift")

            if hyp_change and hyp_metric:
                st.markdown(f"""
                <div class="hypothesis-box">
                    📝 <strong>Hypothesis:</strong> Changing <em>{hyp_change}</em> will 
                    <em>{hyp_direction}</em> <em>{hyp_metric}</em> by approximately 
                    <em>{hyp_magnitude if hyp_magnitude else '?'}</em> because <em>{hyp_reason if hyp_reason else '...'}</em>
                </div>
                """, unsafe_allow_html=True)

            st.divider()
            if st.button("▶  Run Analysis", type="primary", use_container_width=True):
                with st.spinner("Running analysis..."):
                    control_df = df[df[group_col] == control_label].copy()
                    treatment_df = df[df[group_col] == treatment_label].copy()

                    if len(control_df) == 0 or len(treatment_df) == 0:
                        st.error("❌ Groups not found. Check your group labels match exactly what's in the data.")
                    else:
                        st.session_state.data = df
                        st.session_state.control = control_df
                        st.session_state.treatment = treatment_df
                        st.session_state.config = {
                            'user_col': user_col, 'group_col': group_col,
                            'metric_col': metric_col,
                            'date_col': date_col if date_col != 'None' else None,
                            'metric_type': metric_type, 'alpha': alpha,
                            'control_label': control_label, 'treatment_label': treatment_label,
                            'baseline_rate': baseline_rate, 'mde': mde,
                            'min_practical': min_practical, 'looks': int(looks),
                            'hypothesis': f"Changing {hyp_change} will {hyp_direction} {hyp_metric} by {hyp_magnitude} because {hyp_reason}"
                        }
                        st.session_state.analysis_complete = True
                        st.success(f"✅ Done. Control: {len(control_df):,} | Treatment: {len(treatment_df):,}")
                        st.info("→ Go to the **Results** tab")

    else:
        st.markdown('<p class="section-label">BigQuery Connection</p>', unsafe_allow_html=True)

        # Experiment registry table
        st.markdown("Select an experiment to analyze:")

        exp_data = {
            'ID': [1, 2, 3],
            'Experiment': ['Checkout Flow Optimization', 'Homepage Redesign', 'Mobile Experience Improvement'],
            'Period': ['Aug–Oct 2016', 'Nov 2016–Jan 2017', 'Feb–Apr 2017'],
            'Metric': ['Binary (Conversion)', 'Continuous (Revenue)', 'Binary (Conversion)'],
            'Users': ['199,661', '204,711', '43,430'],
            'Status': ['✅ Completed', '✅ Completed', '✅ Completed']
        }
        exp_df = pd.DataFrame(exp_data)
        st.dataframe(exp_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            project_id = st.text_input("Project ID", value="project-0cb31fa0-9ae1-4887-b38")
            dataset = st.text_input("Dataset", value="ab_testing")
        with col2:
            experiment_id = st.selectbox(
                "Experiment",
                options=[1, 2, 3],
                format_func=lambda x: {
                    1: "Exp 1 — Checkout Flow Optimization",
                    2: "Exp 2 — Homepage Redesign",
                    3: "Exp 3 — Mobile Experience"
                }[x]
            )
            alpha_bq = st.selectbox("Significance threshold", options=[0.05, 0.01, 0.10])

        col1, col2 = st.columns(2)
        with col1:
            baseline_bq = st.number_input("Baseline rate (%)", 0.1, 100.0, 1.5, 0.1) / 100
            mde_bq = st.number_input("MDE (%)", 0.1, 20.0, 0.2, 0.1) / 100
        with col2:
            min_practical_bq = st.number_input("Min practical effect (%)", 0.0, 20.0, 0.5, 0.1)
            looks_bq = st.number_input("Times checked so far", 1, 20, 1, 1)

        # Minimum duration warning
        est_days = int(np.ceil(
            power_analysis(baseline_bq / 100, mde_bq / 100)['required_sample_size_per_group'] / 500
        ))
        if est_days < 7:
            est_days = 7
        st.info(f"⏱ Recommended minimum experiment duration: **{est_days} days** to avoid weekly cycle bias and reach sufficient sample size.")

        if st.button("▶  Load from BigQuery", type="primary", use_container_width=True):
            with st.spinner("Connecting to BigQuery..."):
                try:
                    bq_client = bigquery.Client(project=project_id)
                    query = f"""
                    SELECT
                        ua.user_id, ua.group_name,
                        uf.converted, uf.total_revenue, uf.revenue_capped,
                        uf.total_sessions, uf.avg_pageviews_per_session,
                        uf.bounce_rate, uf.primary_device,
                        uf.primary_channel, uf.country, uf.user_value_segment
                    FROM `{project_id}.{dataset}.user_assignments` ua
                    JOIN `{project_id}.{dataset}.user_features` uf
                        ON ua.user_id = uf.user_id
                    WHERE ua.experiment_id = {experiment_id}
                    """
                    df = bq_client.query(query).to_dataframe()
                    mt_query = f"""
                    SELECT metric_type, hypothesis FROM `{project_id}.{dataset}.experiments`
                    WHERE experiment_id = {experiment_id}
                    """
                    mt_df = bq_client.query(mt_query).to_dataframe()
                    mt = mt_df['metric_type'].values[0]
                    hypothesis = mt_df['hypothesis'].values[0] if 'hypothesis' in mt_df.columns else ''
                    metric_col = 'converted' if mt == 'binary' else 'revenue_capped'
                    control_df = df[df['group_name'] == 'control'].copy()
                    treatment_df = df[df['group_name'] == 'treatment'].copy()

                    st.session_state.data = df
                    st.session_state.control = control_df
                    st.session_state.treatment = treatment_df
                    st.session_state.config = {
                        'user_col': 'user_id', 'group_col': 'group_name',
                        'metric_col': metric_col, 'date_col': None,
                        'metric_type': mt, 'alpha': alpha_bq,
                        'control_label': 'control', 'treatment_label': 'treatment',
                        'baseline_rate': baseline_bq, 'mde': mde_bq,
                        'min_practical': min_practical_bq, 'looks': int(looks_bq),
                        'experiment_id': experiment_id, 'project_id': project_id,
                        'dataset': dataset, 'hypothesis': hypothesis
                    }
                    st.session_state.analysis_complete = True
                    st.success(f"✅ Loaded {len(df):,} users")
                    st.info("→ Go to the **Results** tab")
                except Exception as e:
                    st.error(f"❌ {e}")

# ─────────────────────────────────────────
# TAB 2: RESULTS
# ─────────────────────────────────────────
with tab2:
    if not st.session_state.analysis_complete:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#444;">
            <div style="font-size:3rem;margin-bottom:16px;">📊</div>
            <div style="font-size:1.1rem;font-weight:600;color:#666;margin-bottom:8px;">No analysis run yet</div>
            <div style="font-size:0.85rem;color:#444;">Complete the Setup tab to see results here</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        control = st.session_state.control
        treatment = st.session_state.treatment
        config = st.session_state.config
        metric_col = config['metric_col']
        alpha = config['alpha']
        metric_type = config['metric_type']

        # Show hypothesis if set and not empty
        hyp = config.get('hypothesis', '')
        if hyp and len(hyp.replace('Changing', '').replace('will', '').replace('increase', '').replace('decrease', '').replace('by', '').replace('because', '').strip()) > 5:
            st.markdown(f"""
            <div class="hypothesis-box">
                📝 <strong>Hypothesis:</strong> {hyp}
            </div>
            """, unsafe_allow_html=True)

        # Run all stats
        srm = srm_check(len(control), len(treatment))
        power = power_analysis(config['baseline_rate'], config['mde'], alpha=alpha)

        if metric_type == 'binary':
            result = chi_square_test(
                int(control[metric_col].sum()), len(control),
                int(treatment[metric_col].sum()), len(treatment)
            )
        else:
            result = t_test(control[metric_col].values, treatment[metric_col].values)

        bayes = bayesian_ab_test(
            int(control[metric_col].sum()), len(control),
            int(treatment[metric_col].sum()), len(treatment)
        )

        seq = sequential_test_correction(result['p_value'], config['looks'], alpha)
        ps = practical_significance(result['absolute_lift'], config['min_practical'], metric_type)

        st.session_state.results.update({
            'statistical': result, 'bayesian': bayes,
            'sequential': seq, 'practical': ps,
            'srm': srm, 'power': power
        })

        # ── HEALTH SCORE ──
        health_score = 0
        health_items = []

        if not srm['srm_detected']:
            health_score += 25
            health_items.append(("✅", "Groups balanced", f"SRM p={srm['p_value']}"))
        else:
            health_items.append(("❌", "SRM detected", f"p={srm['p_value']} — groups not balanced"))

        powered = len(control) >= power['required_sample_size_per_group']
        if powered:
            health_score += 25
            health_items.append(("✅", "Well powered", f"{len(control):,} ≥ {power['required_sample_size_per_group']:,} needed"))
        else:
            health_items.append(("⚠️", "Underpowered", f"Need {power['required_sample_size_per_group']:,} (have {len(control):,})"))

        if result['is_significant']:
            health_score += 25
            health_items.append(("✅", "Statistically significant", f"p={result['p_value']} < {alpha}"))
        else:
            health_items.append(("❌", "Not significant", f"p={result['p_value']} > {alpha}"))

        if bayes['prob_treatment_better'] > 80:
            health_score += 25
            health_items.append(("✅", "Bayesian confidence", f"{bayes['prob_treatment_better']}% treatment wins"))
        else:
            health_items.append(("❌", "Low Bayesian confidence", f"{bayes['prob_treatment_better']}% treatment wins"))

        health_color = "#00CC96" if health_score >= 75 else "#FFA15A" if health_score >= 50 else "#EF553B"

        # ── VERDICT ──
        sig = result['is_significant']
        lift_pos = result['absolute_lift'] > 0
        bayes_strong = bayes['prob_treatment_better'] > 95
        bayes_promising = bayes['prob_treatment_better'] > 80
        practical_ok = ps['clears_practical_bar']

        if sig and lift_pos and bayes_strong and practical_ok:
            st.markdown("""<div class="verdict-ship">
                <h2 style="color:#00CC96;margin:0 0 8px 0;font-size:1.3rem;">✅ Ship it</h2>
                <p style="color:#aaa;margin:0;font-size:0.9rem;">Statistical significance confirmed. Bayesian confidence above 95%. Lift clears your business threshold. Safe to deploy.</p>
            </div>""", unsafe_allow_html=True)
            recommendation = "Ship it"

        elif sig and lift_pos and not practical_ok:
            st.markdown("""<div class="verdict-warn">
                <h2 style="color:#7C83FD;margin:0 0 8px 0;font-size:1.3rem;">⚠️ Significant but not practical</h2>
                <p style="color:#aaa;margin:0;font-size:0.9rem;">Result is statistically significant but the lift is below your minimum business threshold. Not worth the engineering cost to ship.</p>
            </div>""", unsafe_allow_html=True)
            recommendation = "Don't ship — lift too small"

        elif not sig and bayes_promising:
            st.markdown("""<div class="verdict-wait">
                <h2 style="color:#FFA15A;margin:0 0 8px 0;font-size:1.3rem;">🟡 Keep running</h2>
                <p style="color:#aaa;margin:0;font-size:0.9rem;">Bayesian analysis shows promise but the frequentist test hasn't reached significance. Collect more data before deciding.</p>
            </div>""", unsafe_allow_html=True)
            recommendation = "Keep running"

        elif sig and not lift_pos:
            st.markdown("""<div class="verdict-no">
                <h2 style="color:#EF553B;margin:0 0 8px 0;font-size:1.3rem;">🔴 Treatment is worse</h2>
                <p style="color:#aaa;margin:0;font-size:0.9rem;">Treatment significantly underperformed control. Do not ship. Roll back if already deployed.</p>
            </div>""", unsafe_allow_html=True)
            recommendation = "Don't ship — treatment worse"

        else:
            st.markdown("""<div class="verdict-no">
                <h2 style="color:#EF553B;margin:0 0 8px 0;font-size:1.3rem;">❌ No evidence of improvement</h2>
                <p style="color:#aaa;margin:0;font-size:0.9rem;">Not statistically significant. Cannot conclude treatment is better than control. Redesign the experiment or collect more data.</p>
            </div>""", unsafe_allow_html=True)
            recommendation = "Don't ship"

        st.session_state.results['recommendation'] = recommendation

        # ── HEALTH SCORE ──
        st.markdown('<p class="section-label">Experiment Health</p>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            st.progress(health_score / 100)
        with col2:
            st.markdown(f"<div style='color:{health_color};font-size:1.1rem;font-weight:700;padding-top:4px;'>{health_score}/100</div>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        for i, (icon, label, detail) in enumerate(health_items):
            col = [col1, col2, col3, col4][i]
            col.metric(f"{icon} {label}", detail)

        st.divider()

        # ── KEY NUMBERS ──
        st.markdown('<p class="section-label">Key Numbers</p>', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        if metric_type == 'binary':
            col1.metric("Control", f"{result['control_conversion_rate']}%",
                        help="Conversion rate in the control group")
            col2.metric("Treatment", f"{result['treatment_conversion_rate']}%",
                        help="Conversion rate in the treatment group")
        else:
            col1.metric("Control avg", f"${result['control_mean']}",
                        help="Average revenue per user in control")
            col2.metric("Treatment avg", f"${result['treatment_mean']}",
                        help="Average revenue per user in treatment")

        col3.metric("Lift", f"{result['absolute_lift']}{'%' if metric_type == 'binary' else '$'}",
                    delta=f"{result['absolute_lift']}{'%' if metric_type == 'binary' else '$'}",
                    help="Absolute difference between treatment and control")
        col4.metric("p-value", result['p_value'],
                    help=f"Probability this result happened by chance. Below {alpha} = significant.")
        col5.metric("Relative lift", f"{result['relative_lift_pct']}%",
                    help="Percentage improvement relative to control baseline")

        st.divider()

        # ── SIGNIFICANCE BARS ──
        st.markdown('<p class="section-label">Significance Check</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Statistical significance**")
            p_pct = min(int((1 - result['p_value'] / alpha) * 100), 100) if result['p_value'] < alpha else int((alpha / result['p_value']) * 50)
            p_pct = max(0, min(100, p_pct))
            bar_color = "#00CC96" if result['is_significant'] else "#EF553B"
            st.markdown(f"""
            <div class="sig-bar-container">
                <div class="sig-bar-fill" style="width:{p_pct}%;background:{bar_color};"></div>
            </div>
            <div style="font-size:0.8rem;color:#666;margin-top:4px;">
                p={result['p_value']} vs threshold {alpha} — {'✅ Significant' if result['is_significant'] else '❌ Not significant'}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("**Practical significance** (business threshold)")
            lift_val = abs(result['absolute_lift'])
            min_prac = config['min_practical']
            prac_pct = min(int((lift_val / min_prac) * 100), 100) if min_prac > 0 else 100
            prac_color = "#00CC96" if practical_ok else "#FFA15A"
            st.markdown(f"""
            <div class="sig-bar-container">
                <div class="sig-bar-fill" style="width:{prac_pct}%;background:{prac_color};"></div>
            </div>
            <div style="font-size:0.8rem;color:#666;margin-top:4px;">
                Lift {result['absolute_lift']}% vs minimum {min_prac}% — {'✅ Clears bar' if practical_ok else '⚠️ Below threshold'}
            </div>
            """, unsafe_allow_html=True)

        if config['looks'] > 1:
            st.warning(f"🔍 **Peeking detected** — You've checked results {config['looks']} times. {seq['warning']}")

        st.divider()

        # ── CI VISUALIZATION ──
        st.markdown('<p class="section-label">Confidence Interval</p>', unsafe_allow_html=True)
        ci_lower = float(result['confidence_interval_95'][0])
        ci_upper = float(result['confidence_interval_95'][1])
        lift = float(result['absolute_lift'])
        unit = "%" if metric_type == 'binary' else "$"

        fig_ci = go.Figure()
        fig_ci.add_shape(type="line", x0=0, x1=0, y0=-0.5, y1=0.5,
                         line=dict(color="#444", width=2, dash="dash"))
        fig_ci.add_shape(type="line", x0=ci_lower, x1=ci_upper, y0=0, y1=0,
                         line=dict(color="#7C83FD", width=3))
        fig_ci.add_trace(go.Scatter(
            x=[ci_lower, lift, ci_upper], y=[0, 0, 0],
            mode='markers',
            marker=dict(
                size=[10, 16, 10],
                color=["#7C83FD", "#00CC96" if lift > 0 else "#EF553B", "#7C83FD"],
                symbol=["circle", "diamond", "circle"]
            ),
            text=[f"Lower: {ci_lower}{unit}", f"Lift: {lift}{unit}", f"Upper: {ci_upper}{unit}"],
            hovertemplate="%{text}<extra></extra>"
        ))
        crosses_zero = ci_lower < 0 < ci_upper
        fig_ci.add_annotation(
            x=lift, y=0.3,
            text=f"Lift: {lift}{unit}",
            showarrow=False,
            font=dict(color="#ffffff", size=12)
        )
        fig_ci.update_layout(
            height=160,
            xaxis_title=f"Effect size ({unit})",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#888', family='Inter'),
            yaxis=dict(visible=False),
            xaxis=dict(gridcolor='#1e1e2e', zerolinecolor='#444'),
            margin=dict(t=30, b=30),
            showlegend=False
        )
        st.plotly_chart(fig_ci, use_container_width=True)
        if crosses_zero:
            st.caption("⚠️ The confidence interval crosses zero — the true effect could be positive or negative. More data needed.")
        else:
            st.caption(f"✅ The confidence interval does not cross zero — the effect is consistently {'positive' if lift > 0 else 'negative'}.")

        st.divider()

        # ── BAR CHART ──
        st.markdown('<p class="section-label">Control vs Treatment</p>', unsafe_allow_html=True)
        if metric_type == 'binary':
            y_vals = [result['control_conversion_rate'], result['treatment_conversion_rate']]
            y_label = "Conversion rate (%)"
            text_vals = [f"{result['control_conversion_rate']}%", f"{result['treatment_conversion_rate']}%"]
        else:
            y_vals = [result['control_mean'], result['treatment_mean']]
            y_label = "Average value"
            text_vals = [f"${result['control_mean']}", f"${result['treatment_mean']}"]

        fig = go.Figure(go.Bar(
            x=['Control', 'Treatment'],
            y=y_vals,
            marker_color=['#636EFA', '#00CC96' if lift_pos else '#EF553B'],
            text=text_vals,
            textposition='outside',
            textfont=dict(size=13, color='white'),
            width=0.35
        ))
        fig.update_layout(
            yaxis_title=y_label, height=360,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#888', family='Inter'),
            yaxis=dict(gridcolor='#1e1e2e', zerolinecolor='#1e1e2e'),
            xaxis=dict(gridcolor='#1e1e2e'),
            showlegend=False, margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── "WHY DID THIS HAPPEN?" ──
        st.markdown('<p class="section-label">What does this mean for the business?</p>', unsafe_allow_html=True)
        if sig and lift_pos and practical_ok:
            st.success(f"""
            Treatment improved {metric_type} by **{result['absolute_lift']}{'%' if metric_type == 'binary' else '$'}** 
            ({result['relative_lift_pct']}% relative improvement). Both statistical and business thresholds are cleared. 
            Bayesian analysis confirms {bayes['prob_treatment_better']}% probability treatment is genuinely better. 
            **Recommended action: deploy to 100% of users.**
            """)
        elif not sig and bayes_promising:
            st.warning(f"""
            Treatment shows a **{result['absolute_lift']}{'%' if metric_type == 'binary' else '$'}** lift 
            but hasn't reached statistical significance (p={result['p_value']}). 
            Bayesian analysis shows {bayes['prob_treatment_better']}% confidence — promising but not conclusive. 
            **Recommended action: continue running for at least {max(7, int(power['required_sample_size_per_group'] / max(len(control), 1) * 7))} more days.**
            """)
        elif sig and not practical_ok:
            st.info(f"""
            Treatment is statistically significant but the lift of **{result['absolute_lift']}{'%' if metric_type == 'binary' else '$'}** 
            is below your minimum practical threshold of **{config['min_practical']}%**. 
            Shipping this change won't move the needle enough to justify engineering cost. 
            **Recommended action: redesign the experiment with a bolder change.**
            """)
        else:
            st.error(f"""
            No meaningful difference detected between control and treatment (p={result['p_value']}). 
            This could mean the change had no effect, or the experiment was underpowered. 
            **Recommended action: {'collect more data — you need ' + str(power['required_sample_size_per_group'] - len(control)) + ' more users per group.' if not powered else 'the change likely has no effect. Consider a different approach.'}**
            """)

        # ── ADVANCED MODE ──
        if show_advanced:
            st.divider()
            st.markdown('<p class="section-label">Advanced Statistics</p>', unsafe_allow_html=True)

            with st.expander("Bayesian Analysis", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("P(Treatment > Control)", f"{bayes['prob_treatment_better']}%")
                col2.metric("Expected lift", f"{bayes['expected_lift']}%")
                col3.metric("95% Credible interval",
                            f"[{bayes['credible_interval_95'][0]}%, {bayes['credible_interval_95'][1]}%]")

                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=bayes['prob_treatment_better'],
                    title={'text': "P(Treatment wins)", 'font': {'color': '#888', 'size': 12}},
                    number={'font': {'color': 'white', 'size': 32}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#888'},
                        'bar': {'color': "#7C83FD"},
                        'bgcolor': '#13131f',
                        'steps': [
                            {'range': [0, 80], 'color': '#2a0d0d'},
                            {'range': [80, 95], 'color': '#2a2100'},
                            {'range': [95, 100], 'color': '#0d2818'}
                        ],
                        'threshold': {'line': {'color': "white", 'width': 2}, 'thickness': 0.75, 'value': 95}
                    }
                ))
                fig_gauge.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)',
                                        font=dict(color='#888', family='Inter'))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.markdown("""
                - 🔴 **< 80%** — Not enough evidence
                - 🟡 **80–95%** — Promising, keep running
                - 🟢 **> 95%** — Strong evidence, consider shipping
                """)

            with st.expander("Sequential Testing — Peeking Correction"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Original p-value", result['p_value'])
                col2.metric("Corrected threshold", seq['corrected_alpha'])
                col3.metric("Significant after correction", "Yes" if seq['adjusted_significant'] else "No")
                st.warning(seq['warning'])
                st.caption("If you check results multiple times during an experiment, you increase the chance of a false positive. Uplift corrects for this using Bonferroni correction.")

            with st.expander("Full Statistical Output"):
                st.json(result)

# ─────────────────────────────────────────
# TAB 3: DEEP DIVE
# ─────────────────────────────────────────
with tab3:
    if not st.session_state.analysis_complete:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#444;">
            <div style="font-size:3rem;margin-bottom:16px;">🔬</div>
            <div style="font-size:1.1rem;font-weight:600;color:#666;margin-bottom:8px;">No analysis run yet</div>
            <div style="font-size:0.85rem;color:#444;">Complete the Setup tab first</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        config = st.session_state.config
        df = st.session_state.data
        control = st.session_state.control
        treatment = st.session_state.treatment
        metric_col = config['metric_col']
        metric_type = config['metric_type']

        # ── SEGMENT ANALYSIS ──
        st.markdown('<p class="section-label">Segment Analysis</p>', unsafe_allow_html=True)
        st.markdown("Does the treatment effect hold across all user segments, or is it driven by a specific group?")

        available_segments = [col for col in df.columns
                              if col not in [config['user_col'], config['group_col'], config['metric_col']]
                              and df[col].dtype == 'object'
                              and df[col].nunique() < 20]

        if available_segments:
            segment_col = st.selectbox("Slice results by", options=available_segments)

            with st.spinner("Running segment analysis..."):
                seg_results = segment_analysis(
                    df, config['group_col'], metric_col,
                    segment_col, metric_type, config['alpha']
                )

            if len(seg_results) > 0:
                colors = ['#00CC96' if d == '✅ Treatment wins'
                          else '#EF553B' if d == '❌ Treatment loses'
                          else '#636EFA' for d in seg_results['direction']]

                fig_seg = go.Figure(go.Bar(
                    x=seg_results['segment'],
                    y=seg_results['lift'],
                    marker_color=colors,
                    text=[f"{l:+.2f}%" for l in seg_results['lift']],
                    textposition='outside',
                    textfont=dict(color='white', size=11)
                ))
                fig_seg.add_hline(y=0, line_color='#555', line_dash='dash')
                fig_seg.update_layout(
                    title=f"Lift by {segment_col} — green = treatment wins, red = treatment loses",
                    yaxis_title="Lift (%)", height=380,
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#888', family='Inter'),
                    yaxis=dict(gridcolor='#1e1e2e'), xaxis=dict(gridcolor='#1e1e2e')
                )
                st.plotly_chart(fig_seg, use_container_width=True)
                st.dataframe(seg_results, use_container_width=True, hide_index=True)

                # Segment interpretation
                winners = seg_results[seg_results['direction'] == '✅ Treatment wins']['segment'].tolist()
                losers = seg_results[seg_results['direction'] == '❌ Treatment loses']['segment'].tolist()
                if winners:
                    st.success(f"Treatment wins for: **{', '.join(winners)}**")
                if losers:
                    st.error(f"Treatment loses for: **{', '.join(losers)}**")
                if winners and losers:
                    st.warning("⚠️ Mixed results across segments — the overall verdict may mask important differences. Consider running targeted experiments for specific segments.")
            else:
                st.info("No segments had enough users (minimum 30 per group) for reliable analysis.")
        else:
            st.info("No categorical segment columns detected. Add columns like device, country, or channel to your data for segment analysis.")

        st.divider()

        if 'experiment_id' in config:
            bq_client = bigquery.Client(project=config['project_id'])

            # ── CUPED ──
            st.markdown('<p class="section-label">CUPED — Variance Reduction</p>', unsafe_allow_html=True)
            st.markdown("Uses pre-experiment behavior to reduce noise and produce a more precise estimate of the treatment effect. Used by Netflix, Spotify, and Booking.com.")

            with st.spinner("Running CUPED..."):
                cuped_query = f"""
                SELECT d.user_id, d.group_name,
                       d.post_converted as post_metric,
                       d.pre_converted as pre_metric
                FROM `{config['project_id']}.{config['dataset']}.did_metrics` d
                WHERE d.experiment_id = {config['experiment_id']}
                """
                cuped_df = bq_client.query(cuped_query).to_dataframe()
                control_c = cuped_df[cuped_df['group_name'] == 'control']
                treatment_c = cuped_df[cuped_df['group_name'] == 'treatment']
                cuped_result = cuped_ttest(
                    control_c['post_metric'].values, treatment_c['post_metric'].values,
                    control_c['pre_metric'].values, treatment_c['pre_metric'].values
                )

            col1, col2, col3 = st.columns(3)
            col1.metric("Standard p-value", cuped_result['regular_p_value'],
                        help="p-value without variance reduction")
            col2.metric("CUPED p-value", cuped_result['cuped_p_value'],
                        help="p-value after CUPED variance reduction — more precise")
            col3.metric("Variance reduction", f"{cuped_result['variance_reduction_pct']}%",
                        help="How much noise CUPED removed. Higher = more precise estimates.")
            st.info(cuped_result['interpretation'])
            st.divider()

            # ── DiD ──
            st.markdown('<p class="section-label">Difference-in-Differences</p>', unsafe_allow_html=True)
            st.markdown("Controls for pre-existing differences between groups. Isolates the true causal effect of the treatment — not just the observed difference.")

            with st.spinner("Loading DiD data..."):
                did_query = f"""
                SELECT group_name, pre_converted, post_converted
                FROM `{config['project_id']}.{config['dataset']}.did_metrics`
                WHERE experiment_id = {config['experiment_id']}
                """
                did_df = bq_client.query(did_query).to_dataframe()
                did = difference_in_differences(did_df)

            st.session_state.results['did'] = did
            col1, col2, col3 = st.columns(3)
            col1.metric("Control change", f"{did['control_change']}%",
                        delta=f"{did['control_change']}%",
                        help="How control group's metric changed from before to after the experiment")
            col2.metric("Treatment change", f"{did['treatment_change']}%",
                        delta=f"{did['treatment_change']}%",
                        help="How treatment group's metric changed from before to after")
            col3.metric("True causal effect (DiD)", f"{did['did_estimate']}%",
                        delta=f"{did['did_estimate']}%",
                        help="DiD estimate = treatment change minus control change. This is the true effect of the treatment, controlling for pre-existing trends.")
            st.info(did['interpretation'])

            fig_did = go.Figure(go.Bar(
                x=['Control\n(before)', 'Control\n(after)', 'Treatment\n(before)', 'Treatment\n(after)'],
                y=[did['control_pre'], did['control_post'], did['treatment_pre'], did['treatment_post']],
            marker=dict(
                color=['#636EFA', '#636EFA', '#EF553B', '#EF553B'],
                opacity=[0.4, 1.0, 0.4, 1.0]
            ),
                text=[f"{did['control_pre']}%", f"{did['control_post']}%",
                      f"{did['treatment_pre']}%", f"{did['treatment_post']}%"],
                textposition='outside', textfont=dict(color='white')
            ))
            fig_did.update_layout(
                yaxis_title="Conversion rate (%)", height=350,
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#888', family='Inter'),
                yaxis=dict(gridcolor='#1e1e2e'), xaxis=dict(gridcolor='#1e1e2e')
            )
            st.plotly_chart(fig_did, use_container_width=True)
            st.divider()

            # ── COHORT RETENTION ──
            st.markdown('<p class="section-label">Cohort Retention</p>', unsafe_allow_html=True)
            st.markdown("Does the treatment effect hold over time, or does it fade after the first week?")

            with st.spinner("Loading cohort data..."):
                cohort_query = f"""
                SELECT group_name, week_number, AVG(retention_rate_pct) as avg_retention
                FROM `{config['project_id']}.{config['dataset']}.cohort_retention`
                WHERE experiment_id = {config['experiment_id']}
                GROUP BY group_name, week_number
                ORDER BY week_number, group_name
                """
                cohort_df = bq_client.query(cohort_query).to_dataframe()

            fig_cohort = px.line(
                cohort_df, x='week_number', y='avg_retention', color='group_name',
                labels={'week_number': 'Weeks since experiment started',
                        'avg_retention': 'Retention rate (%)', 'group_name': 'Group'},
                color_discrete_map={'control': '#636EFA', 'treatment': '#EF553B'}
            )
            fig_cohort.update_layout(
                height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#888', family='Inter'),
                yaxis=dict(gridcolor='#1e1e2e'), xaxis=dict(gridcolor='#1e1e2e'),
                legend=dict(bgcolor='rgba(0,0,0,0)')
            )
            st.plotly_chart(fig_cohort, use_container_width=True)
            st.markdown("""
            - **Treatment drops faster than control** → novelty effect. Users tried it but didn't stick long term.
            - **Treatment stays consistently higher** → genuine long-term improvement worth shipping.
            - **Lines converge by week 4+** → no lasting difference. Short-term result may not hold.
            """)
            st.divider()

            # ── GUARDRAIL METRICS ──
            st.markdown('<p class="section-label">Guardrail Metrics</p>', unsafe_allow_html=True)
            st.markdown("Did the experiment accidentally hurt anything important while improving the primary metric?")

            with st.spinner("Loading guardrail data..."):
                guardrail_query = f"""
                SELECT * FROM `{config['project_id']}.{config['dataset']}.guardrail_metrics`
                WHERE experiment_id = {config['experiment_id']}
                """
                guardrail_df = bq_client.query(guardrail_query).to_dataframe()

            control_g = guardrail_df[guardrail_df['group_name'] == 'control'].iloc[0]
            treatment_g = guardrail_df[guardrail_df['group_name'] == 'treatment'].iloc[0]

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Bounce rate",
                        f"{treatment_g['avg_bounce_rate']}%",
                        delta=f"{round(treatment_g['avg_bounce_rate'] - control_g['avg_bounce_rate'], 2)}%",
                        delta_color="inverse",
                        help="Higher bounce rate = bad. Treatment should not significantly increase this.")
            col2.metric("Avg sessions",
                        f"{treatment_g['avg_sessions_per_user']}",
                        delta=f"{round(treatment_g['avg_sessions_per_user'] - control_g['avg_sessions_per_user'], 4)}",
                        help="Sessions per user. Should not drop significantly.")
            col3.metric("Avg pageviews",
                        f"{treatment_g['avg_pageviews_per_session']}",
                        delta=f"{round(treatment_g['avg_pageviews_per_session'] - control_g['avg_pageviews_per_session'], 4)}",
                        help="Pages viewed per session. Significant drop = engagement issue.")
            col4.metric("Time on site",
                        f"{treatment_g['avg_time_per_session']}s",
                        delta=f"{round(treatment_g['avg_time_per_session'] - control_g['avg_time_per_session'], 2)}s",
                        help="Time spent per session. Significant drop = usability concern.")
            col5.metric("Avg revenue",
                        f"${treatment_g['avg_revenue_capped']}",
                        delta=f"${round(treatment_g['avg_revenue_capped'] - control_g['avg_revenue_capped'], 4)}",
                        help="Average revenue per user. Should not drop.")
            st.caption("Green delta = treatment better than control. Red delta = treatment worse. Flag any metric with a large negative delta.")

        else:
            if config.get('date_col') and df is not None:
                st.markdown('<p class="section-label">Time Trend</p>', unsafe_allow_html=True)
                df['_date'] = pd.to_datetime(df[config['date_col']])
                daily = df.groupby(['_date', config['group_col']])[metric_col].mean().reset_index()
                fig_daily = px.line(
                    daily, x='_date', y=metric_col, color=config['group_col'],
                    color_discrete_map={config['control_label']: '#636EFA', config['treatment_label']: '#EF553B'}
                )
                fig_daily.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#888', family='Inter'),
                    yaxis=dict(gridcolor='#1e1e2e'), xaxis=dict(gridcolor='#1e1e2e')
                )
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.markdown("""
                <div style="text-align:center;padding:40px 20px;color:#444;border:1px dashed #1e1e2e;border-radius:12px;">
                    <div style="font-size:2rem;margin-bottom:12px;">🔬</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#555;margin-bottom:6px;">Advanced analysis requires BigQuery</div>
                    <div style="font-size:0.8rem;color:#444;">DiD, CUPED, cohort retention, and guardrail metrics are available when connecting via BigQuery.<br>For CSV uploads, add a date column to enable time-based analysis.</div>
                </div>
                """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# TAB 4: EXPORT
# ─────────────────────────────────────────
with tab4:
    if not st.session_state.analysis_complete or 'statistical' not in st.session_state.results:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#444;">
            <div style="font-size:3rem;margin-bottom:16px;">📄</div>
            <div style="font-size:1.1rem;font-weight:600;color:#666;margin-bottom:8px;">No results to export yet</div>
            <div style="font-size:0.85rem;color:#444;">Run your analysis in the Results tab first</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        config = st.session_state.config
        results = st.session_state.results
        freq = results['statistical']
        bayes = results.get('bayesian', {})
        ps = results.get('practical', {})
        recommendation = results.get('recommendation', 'N/A')

        st.markdown('<p class="section-label">Summary</p>', unsafe_allow_html=True)

        summary_data = {
            'Metric': [
                'Metric type', 'Control users', 'Treatment users',
                'Control performance', 'Treatment performance',
                'Absolute lift', 'Relative lift', 'p-value',
                'Statistically significant', 'Clears business threshold',
                'Bayesian probability treatment wins', 'Recommendation'
            ],
            'Value': [
                config['metric_type'],
                f"{len(st.session_state.control):,}",
                f"{len(st.session_state.treatment):,}",
                f"{freq['control_conversion_rate']}%" if config['metric_type'] == 'binary' else f"${freq['control_mean']}",
                f"{freq['treatment_conversion_rate']}%" if config['metric_type'] == 'binary' else f"${freq['treatment_mean']}",
                f"{freq['absolute_lift']}%",
                f"{freq['relative_lift_pct']}%",
                str(freq['p_value']),
                'Yes' if freq['is_significant'] else 'No',
                'Yes' if ps.get('clears_practical_bar') else 'No',
                f"{bayes.get('prob_treatment_better', 'N/A')}%",
                recommendation
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown('<p class="section-label">Downloads</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button("📥 Results CSV", data=summary_df.to_csv(index=False),
                               file_name="uplift_results.csv", mime="text/csv",
                               use_container_width=True)
        with col2:
            st.download_button("📥 Raw data CSV", data=st.session_state.data.to_csv(index=False),
                               file_name="uplift_experiment_data.csv", mime="text/csv",
                               use_container_width=True)
        with col3:
            methodology = f"""Statistical methodology:
- Primary test: {'Chi-square test (binary metric)' if config['metric_type'] == 'binary' else 'Welch t-test (continuous metric)'}
- Bayesian inference: Beta-Binomial model with 100K Monte Carlo simulations
- Causal inference: Difference-in-Differences (pre/post comparison)
- Variance reduction: CUPED (Controlled-experiment Using Pre-Experiment Data)
- Peeking correction: Bonferroni correction for {config['looks']} look(s)
- Significance threshold: α = {config['alpha']}
- Minimum practical effect: {config['min_practical']}%"""

            report = f"""UPLIFT — EXPERIMENT REPORT
==========================
Generated by Uplift · BigQuery · Python · Streamlit · GKE

HYPOTHESIS
----------
{config.get('hypothesis', 'Not specified')}

CONFIGURATION
-------------
Metric type: {config['metric_type']}
Significance threshold: {config['alpha']}
Minimum practical effect: {config['min_practical']}%
Control users: {len(st.session_state.control):,}
Treatment users: {len(st.session_state.treatment):,}

RESULTS
-------
Control: {freq['control_conversion_rate']}%
Treatment: {freq['treatment_conversion_rate']}%
Absolute lift: {freq['absolute_lift']}%
Relative lift: {freq['relative_lift_pct']}%
p-value: {freq['p_value']}
Statistically significant: {'Yes' if freq['is_significant'] else 'No'}
Clears business threshold: {'Yes' if ps.get('clears_practical_bar') else 'No'}
Bayesian probability treatment wins: {bayes.get('prob_treatment_better', 'N/A')}%

RECOMMENDATION
--------------
{recommendation}

METHODOLOGY
-----------
{methodology}
"""
            st.download_button("📥 Full report TXT", data=report,
                               file_name="uplift_report.txt", mime="text/plain",
                               use_container_width=True)

st.divider()
st.caption("Uplift · BigQuery · Python · Streamlit · GKE")
