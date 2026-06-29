import pandas as pd
import numpy as np
from scipy import stats
from google.cloud import bigquery

client = bigquery.Client(project='project-0cb31fa0-9ae1-4887-b38')

def get_experiment_data(experiment_id):
    query = f"""
    SELECT
        ua.user_id,
        ua.group_name,
        uf.converted,
        uf.total_revenue,
        uf.revenue_capped,
        uf.total_sessions,
        uf.avg_pageviews_per_session,
        uf.bounce_rate
    FROM `project-0cb31fa0-9ae1-4887-b38.ab_testing.user_assignments` ua
    JOIN `project-0cb31fa0-9ae1-4887-b38.ab_testing.user_features` uf
        ON ua.user_id = uf.user_id
    WHERE ua.experiment_id = {experiment_id}
    """
    return client.query(query).to_dataframe()


def power_analysis(baseline_rate, min_detectable_effect, alpha=0.05, power=0.80):
    treatment_rate = baseline_rate + min_detectable_effect
    p_pool = (baseline_rate + treatment_rate) / 2
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    n = (2 * p_pool * (1 - p_pool) * (z_alpha + z_beta)**2) / (min_detectable_effect**2)
    return {
        'required_sample_size_per_group': int(np.ceil(n)),
        'baseline_rate': baseline_rate,
        'treatment_rate': treatment_rate,
        'min_detectable_effect': min_detectable_effect,
        'alpha': alpha,
        'power': power
    }


def srm_check(control_count, treatment_count):
    total = control_count + treatment_count
    expected = total / 2
    chi2_stat, p_value = stats.chisquare(
        f_obs=[control_count, treatment_count],
        f_exp=[expected, expected]
    )
    return {
        'control_count': control_count,
        'treatment_count': treatment_count,
        'expected_per_group': int(expected),
        'chi2_statistic': round(chi2_stat, 4),
        'p_value': round(p_value, 4),
        'srm_detected': p_value < 0.05,
        'status': '⚠️ SRM Detected - investigate' if p_value < 0.05 else '✅ No SRM - groups are balanced'
    }


def chi_square_test(control_conversions, control_total, treatment_conversions, treatment_total):
    contingency_table = [
        [control_conversions, control_total - control_conversions],
        [treatment_conversions, treatment_total - treatment_conversions]
    ]
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    control_rate = control_conversions / control_total
    treatment_rate = treatment_conversions / treatment_total
    lift = treatment_rate - control_rate
    relative_lift = lift / control_rate
    se = np.sqrt(
        (control_rate * (1 - control_rate) / control_total) +
        (treatment_rate * (1 - treatment_rate) / treatment_total)
    )
    z = stats.norm.ppf(0.975)
    ci_lower = lift - z * se
    ci_upper = lift + z * se
    return {
        'control_conversion_rate': round(control_rate * 100, 4),
        'treatment_conversion_rate': round(treatment_rate * 100, 4),
        'absolute_lift': round(lift * 100, 4),
        'relative_lift_pct': round(relative_lift * 100, 2),
        'chi2_statistic': round(chi2, 4),
        'p_value': round(p_value, 4),
        'confidence_interval_95': (round(ci_lower * 100, 4), round(ci_upper * 100, 4)),
        'is_significant': p_value < 0.05,
        'verdict': '✅ Significant - Treatment wins' if (p_value < 0.05 and lift > 0) else '❌ Not significant' if p_value >= 0.05 else '🔴 Significant - Treatment loses'
    }


def t_test(control_values, treatment_values):
    t_stat, p_value = stats.ttest_ind(control_values, treatment_values, equal_var=False)
    control_mean = np.mean(control_values)
    treatment_mean = np.mean(treatment_values)
    lift = treatment_mean - control_mean
    relative_lift = lift / control_mean if control_mean != 0 else 0
    se = np.sqrt(
        np.var(control_values, ddof=1) / len(control_values) +
        np.var(treatment_values, ddof=1) / len(treatment_values)
    )
    z = stats.norm.ppf(0.975)
    ci_lower = lift - z * se
    ci_upper = lift + z * se
    return {
        'control_mean': round(control_mean, 4),
        'treatment_mean': round(treatment_mean, 4),
        'absolute_lift': round(lift, 4),
        'relative_lift_pct': round(relative_lift * 100, 2),
        't_statistic': round(t_stat, 4),
        'p_value': round(p_value, 4),
        'confidence_interval_95': (round(ci_lower, 4), round(ci_upper, 4)),
        'is_significant': p_value < 0.05,
        'verdict': '✅ Significant - Treatment wins' if (p_value < 0.05 and lift > 0) else '❌ Not significant' if p_value >= 0.05 else '🔴 Significant - Treatment loses'
    }


def bayesian_ab_test(control_conversions, control_total, treatment_conversions, treatment_total, simulations=100000):
    control_alpha = control_conversions + 1
    control_beta_param = control_total - control_conversions + 1
    treatment_alpha = treatment_conversions + 1
    treatment_beta_param = treatment_total - treatment_conversions + 1
    control_samples = np.random.beta(control_alpha, control_beta_param, simulations)
    treatment_samples = np.random.beta(treatment_alpha, treatment_beta_param, simulations)
    prob_treatment_better = np.mean(treatment_samples > control_samples)
    expected_lift = np.mean(treatment_samples - control_samples)
    lift_samples = treatment_samples - control_samples
    ci_lower = np.percentile(lift_samples, 2.5)
    ci_upper = np.percentile(lift_samples, 97.5)
    return {
        'prob_treatment_better': round(prob_treatment_better * 100, 2),
        'prob_control_better': round((1 - prob_treatment_better) * 100, 2),
        'expected_lift': round(expected_lift * 100, 4),
        'credible_interval_95': (round(ci_lower * 100, 4), round(ci_upper * 100, 4)),
        'verdict': f'{"✅" if prob_treatment_better > 0.95 else "🟡" if prob_treatment_better > 0.80 else "❌"} {prob_treatment_better*100:.1f}% probability treatment is better'
    }


def difference_in_differences(df):
    control_pre = df[df['group_name'] == 'control']['pre_converted'].mean()
    control_post = df[df['group_name'] == 'control']['post_converted'].mean()
    treatment_pre = df[df['group_name'] == 'treatment']['pre_converted'].mean()
    treatment_post = df[df['group_name'] == 'treatment']['post_converted'].mean()
    did_estimate = (treatment_post - treatment_pre) - (control_post - control_pre)
    return {
        'control_pre': round(control_pre * 100, 4),
        'control_post': round(control_post * 100, 4),
        'treatment_pre': round(treatment_pre * 100, 4),
        'treatment_post': round(treatment_post * 100, 4),
        'control_change': round((control_post - control_pre) * 100, 4),
        'treatment_change': round((treatment_post - treatment_pre) * 100, 4),
        'did_estimate': round(did_estimate * 100, 4),
        'interpretation': f'After controlling for pre-existing trends, treatment {"increased" if did_estimate > 0 else "decreased"} conversion by {abs(did_estimate)*100:.4f}%'
    }


def run_full_analysis(experiment_id):
    print(f"\n{'='*50}")
    print(f"EXPERIMENT {experiment_id} FULL ANALYSIS")
    print(f"{'='*50}")
    df = get_experiment_data(experiment_id)
    control = df[df['group_name'] == 'control']
    treatment = df[df['group_name'] == 'treatment']
    print(f"Total users: {len(df)}")
    srm = srm_check(len(control), len(treatment))
    print(f"\nSRM: {srm['status']}")
    exp_query = f"""
    SELECT metric_type FROM `project-0cb31fa0-9ae1-4887-b38.ab_testing.experiments`
    WHERE experiment_id = {experiment_id}
    """
    metric_type = client.query(exp_query).to_dataframe()['metric_type'].values[0]
    if metric_type == 'binary':
        result = chi_square_test(
            int(control['converted'].sum()), len(control),
            int(treatment['converted'].sum()), len(treatment)
        )
        print(f"\nChi-Square: {result['verdict']}")
        print(f"p-value: {result['p_value']}")
        print(f"Lift: {result['absolute_lift']}%")
        print(f"95% CI: {result['confidence_interval_95']}")
        bayes = bayesian_ab_test(
            int(control['converted'].sum()), len(control),
            int(treatment['converted'].sum()), len(treatment)
        )
        print(f"\nBayesian: {bayes['verdict']}")
    else:
        result = t_test(
            control['revenue_capped'].values,
            treatment['revenue_capped'].values
        )
        print(f"\nT-Test: {result['verdict']}")
        print(f"p-value: {result['p_value']}")
        print(f"Lift: ${result['absolute_lift']}")
        print(f"95% CI: {result['confidence_interval_95']}")
        bayes = bayesian_ab_test(
            int(control['converted'].sum()), len(control),
            int(treatment['converted'].sum()), len(treatment)
        )
        print(f"\nBayesian: {bayes['verdict']}")
    did_query = f"""
    SELECT group_name, pre_converted, post_converted
    FROM `project-0cb31fa0-9ae1-4887-b38.ab_testing.did_metrics`
    WHERE experiment_id = {experiment_id}
    """
    did_df = client.query(did_query).to_dataframe()
    did = difference_in_differences(did_df)
    print(f"\nDiD: {did['interpretation']}")
    return {
        'experiment_id': experiment_id,
        'srm': srm,
        'result': result,
        'bayesian': bayes,
        'did': did
    }


if __name__ == '__main__':
    for exp_id in [1, 2, 3]:
        run_full_analysis(exp_id)


def cuped(post_values, pre_values):
    """
    CUPED - Controlled-experiment Using Pre-Experiment Data
    Reduces variance using pre-experiment behavior to get cleaner results
    Used by Netflix, Spotify, Booking.com
    """
    post = np.array(post_values, dtype=float)
    pre = np.array(pre_values, dtype=float)

    # Calculate theta — how much pre correlates with post
    covariance = np.cov(post, pre)[0][1]
    variance_pre = np.var(pre, ddof=1)
    theta = covariance / variance_pre if variance_pre != 0 else 0

    # Adjust post values using pre-experiment behavior
    pre_mean = np.mean(pre)
    cuped_values = post - theta * (pre - pre_mean)

    return cuped_values, theta


def cuped_ttest(control_post, treatment_post, control_pre, treatment_pre):
    """
    Run t-test on CUPED-adjusted values
    Returns both regular and CUPED results for comparison
    """
    # Regular t-test
    regular = t_test(control_post, treatment_post)

    # CUPED adjusted values
    control_cuped, theta_c = cuped(control_post, control_pre)
    treatment_cuped, theta_t = cuped(treatment_post, treatment_pre)

    # T-test on adjusted values
    cuped_result = t_test(control_cuped, treatment_cuped)

    # Variance reduction
    regular_var = np.var(control_post, ddof=1)
    cuped_var = np.var(control_cuped, ddof=1)
    variance_reduction = (1 - cuped_var / regular_var) * 100 if regular_var != 0 else 0

    return {
        'regular_p_value': regular['p_value'],
        'cuped_p_value': cuped_result['p_value'],
        'regular_lift': regular['absolute_lift'],
        'cuped_lift': cuped_result['absolute_lift'],
        'theta': round(float(theta_c), 4),
        'variance_reduction_pct': round(float(variance_reduction), 2),
        'cuped_ci': cuped_result['confidence_interval_95'],
        'interpretation': f"CUPED reduced variance by {variance_reduction:.1f}%. {'More precise estimate than standard t-test.' if variance_reduction > 0 else 'Pre-experiment data not predictive of post-experiment behavior.'}"
    }


def practical_significance(absolute_lift, minimum_practical_effect, metric_type='binary'):
    """
    Check if result clears the BUSINESS bar, not just the statistical bar
    A result can be statistically significant but too small to matter
    """
    clears_bar = abs(absolute_lift) >= abs(minimum_practical_effect)
    
    return {
        'absolute_lift': absolute_lift,
        'minimum_practical_effect': minimum_practical_effect,
        'clears_practical_bar': clears_bar,
        'verdict': f"✅ Lift of {absolute_lift}{'%' if metric_type == 'binary' else '$'} clears your minimum practical threshold of {minimum_practical_effect}{'%' if metric_type == 'binary' else '$'}" if clears_bar else f"❌ Lift of {absolute_lift}{'%' if metric_type == 'binary' else '$'} does NOT clear your minimum practical threshold of {minimum_practical_effect}{'%' if metric_type == 'binary' else '$'}. Not worth shipping even if statistically significant.",
        'recommendation': 'Consider shipping' if clears_bar else 'Not worth the engineering cost'
    }


def sequential_test_correction(p_value, looks, alpha=0.05):
    """
    Correct p-value for peeking (looking at results before experiment ends)
    Using Bonferroni correction as simple approximation
    Companies like Spotify use this to prevent p-hacking
    """
    corrected_alpha = alpha / looks
    adjusted_significant = p_value < corrected_alpha

    return {
        'original_p_value': p_value,
        'number_of_looks': looks,
        'corrected_alpha': round(corrected_alpha, 4),
        'adjusted_significant': adjusted_significant,
        'warning': f"⚠️ You've checked results {looks} times. Your significance threshold is now {corrected_alpha:.4f} not {alpha}. {'Still significant.' if adjusted_significant else 'No longer significant after correction.'}"
    }


def segment_analysis(df, group_col, metric_col, segment_col, metric_type='binary', alpha=0.05):
    """
    Slice experiment results by a segment (device, country, channel, etc.)
    Answers: does treatment win for ALL segments or just some?
    This is where you catch hidden effects - treatment wins overall
    but loses for mobile users, or wins for US but loses for EU
    """
    segments = df[segment_col].dropna().unique()
    results = []

    for segment in segments:
        seg_df = df[df[segment_col] == segment]
        control = seg_df[seg_df[group_col] == 'control'][metric_col]
        treatment = seg_df[seg_df[group_col] == 'treatment'][metric_col]

        if len(control) < 30 or len(treatment) < 30:
            continue  # Skip segments too small to analyze

        if metric_type == 'binary':
            result = chi_square_test(
                int(control.sum()), len(control),
                int(treatment.sum()), len(treatment)
            )
            control_perf = result['control_conversion_rate']
            treatment_perf = result['treatment_conversion_rate']
        else:
            result = t_test(control.values, treatment.values)
            control_perf = result['control_mean']
            treatment_perf = result['treatment_mean']

        results.append({
            'segment': str(segment),
            'control_n': len(control),
            'treatment_n': len(treatment),
            'control_performance': control_perf,
            'treatment_performance': treatment_perf,
            'lift': result['absolute_lift'],
            'p_value': result['p_value'],
            'significant': result['is_significant'],
            'direction': '✅ Treatment wins' if (result['is_significant'] and result['absolute_lift'] > 0) else '❌ Treatment loses' if (result['is_significant'] and result['absolute_lift'] < 0) else '➖ No difference'
        })

    return pd.DataFrame(results).sort_values('lift', ascending=False)
