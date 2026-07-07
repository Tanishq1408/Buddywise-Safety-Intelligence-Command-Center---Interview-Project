"""
Buddywise Safety Intelligence Command Center
A workplace safety analytics platform mirroring Buddywise's actual product features:
PPE Detection, Housekeeping, Area Control, Vehicle Control, Person Down, Crane Safety

ILO Statistic: 2.3 million work-related deaths per year globally.
Built for Buddywise Working Student (Tech & Ops) Interview -- July 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from data_engine import (
    generate_alerts, generate_workers, compute_worker_risk_scores,
    get_kpi_summary, compute_zone_heatmaps,
    SITES, RISK_SCENARIOS, HIGH_RISK_ZONES, SHIFTS
)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Buddywise Safety Intelligence Command Center",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# COLOR CONSTANTS
# ============================================================
BG_COLOR = "#0B1120"
CARD_COLOR = "#151E32"
BORDER_COLOR = "#2D3A4F"
CRITICAL_COLOR = "#EF4444"
HIGH_COLOR = "#F97316"
MEDIUM_COLOR = "#EAB308"
LOW_COLOR = "#22C55E"
ACCENT_COLOR = "#3B82F6"
ACCENT_GLOW = "#60A5FA"
MUTED_TEXT = "#94A3B8"
TEXT_COLOR = "#F8FAFC"
WARNING_BG = "#451A1A"

SEVERITY_COLORS = {
    'CRITICAL': CRITICAL_COLOR,
    'HIGH': HIGH_COLOR,
    'MEDIUM': MEDIUM_COLOR,
    'LOW': LOW_COLOR
}

SCENARIO_COLORS = {
    'PPE': '#3B82F6',
    'Housekeeping': '#8B5CF6',
    'Area Control': '#EC4899',
    'Vehicle Control': '#F59E0B',
    'Person Down': '#EF4444',
    'Crane Safety': '#10B981'
}

# ============================================================
# CUSTOM CSS -- NO EMOJIS, NO F-STRINGS WITH SPECIAL CHARS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background-color: #0B1120;
        font-family: 'Inter', sans-serif;
    }

    .metric-card {
        background: linear-gradient(135deg, #151E32 0%, #0B1120 100%);
        border: 1px solid #2D3A4F;
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        height: 100%;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.5px;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 4px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.3;
    }
    .metric-delta {
        font-size: 11px;
        margin-top: 4px;
        font-weight: 600;
        line-height: 1.2;
    }

    .insight-card {
        background: #151E32;
        border-left: 4px solid #3B82F6;
        border-radius: 0 12px 12px 0;
        padding: 20px;
        margin: 12px 0;
    }
    .insight-critical {
        border-left-color: #EF4444;
        background: #451A1A;
    }

    .risk-card {
        padding: 28px;
        border-radius: 16px;
        text-align: center;
        font-weight: 800;
        border: 2px solid;
    }
    .risk-critical { background: rgba(239, 68, 68, 0.1); border-color: #EF4444; color: #EF4444; }
    .risk-high { background: rgba(249, 115, 22, 0.1); border-color: #F97316; color: #F97316; }
    .risk-medium { background: rgba(234, 179, 8, 0.1); border-color: #EAB308; color: #EAB308; }
    .risk-low { background: rgba(34, 197, 94, 0.1); border-color: #22C55E; color: #22C55E; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #0B1120;
        padding: 4px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 12px 20px;
        color: #94A3B8;
        font-weight: 500;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(59, 130, 246, 0.15);
        color: #3B82F6;
        font-weight: 600;
    }

    div[data-testid="stDataFrame"] {
        background: #151E32;
        border: 1px solid #2D3A4F;
        border-radius: 12px;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0B1120;
    }
    ::-webkit-scrollbar-thumb {
        background: #2D3A4F;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data(ttl=3600)
def load_data():
    workers = generate_workers(60)
    alerts = generate_alerts(5000, workers)
    workers = compute_worker_risk_scores(alerts, workers)
    kpis = get_kpi_summary(alerts)
    heatmaps = compute_zone_heatmaps(alerts)
    return alerts, workers, kpis, heatmaps

alerts_df, workers_df, kpis, heatmaps = load_data()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("""
<div style="padding: 8px 0 16px 0;">
    <h2 style="color:#F8FAFC; margin:0; font-size:20px; font-weight:800;">&#128737; Buddywise</h2>
    <p style="color:#94A3B8; margin:4px 0 0 0; font-size:12px;">Safety Intelligence Command Center</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

st.sidebar.markdown("<h4 style='color:#F8FAFC; font-size:14px;'>Filters</h4>", unsafe_allow_html=True)

selected_sites = st.sidebar.multiselect(
    "Sites", options=list(SITES.keys()), default=list(SITES.keys())
)

selected_scenarios = st.sidebar.multiselect(
    "Risk Scenarios", options=list(RISK_SCENARIOS.keys()), default=list(RISK_SCENARIOS.keys())
)

selected_severity = st.sidebar.multiselect(
    "Severity", options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
    default=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
)

min_date = alerts_df['timestamp'].min().date()
max_date = alerts_df['timestamp'].max().date()
date_range = st.sidebar.date_input(
    "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

selected_shifts = st.sidebar.multiselect(
    "Shifts", options=list(alerts_df['shift'].unique()), default=list(alerts_df['shift'].unique())
)

selected_zones = st.sidebar.multiselect(
    "Zones", options=sorted(alerts_df['zone'].unique()), default=[]
)

# Apply filters
filtered_df = alerts_df[
    (alerts_df['site'].isin(selected_sites)) &
    (alerts_df['scenario_type'].isin(selected_scenarios)) &
    (alerts_df['severity'].isin(selected_severity)) &
    (alerts_df['shift'].isin(selected_shifts))
]

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['timestamp'].dt.date >= date_range[0]) &
        (filtered_df['timestamp'].dt.date <= date_range[1])
    ]

if selected_zones:
    filtered_df = filtered_df[filtered_df['zone'].isin(selected_zones)]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def create_kpi_card(title, value, subtitle="", color="#F8FAFC", delta=None):
    delta_html = ""
    if delta:
        delta_color = LOW_COLOR if delta.startswith("-") else CRITICAL_COLOR if not delta.startswith("-") else MUTED_TEXT
        delta_html = f'<div class="metric-delta" style="color:{delta_color};">{delta}</div>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{color};">{value}</div>
        <div class="metric-label">{title}</div>
        <div class="metric-label" style="margin-top:2px;">{subtitle}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def safe_mean(series):
    return series.mean() if len(series) > 0 else 0


def safe_value_counts(df, column):
    return df[column].value_counts() if len(df) > 0 else pd.Series(dtype=int)


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Command",
    "Zone Heatmaps",
    "Worker Intelligence",
    "Predictive Engine",
    "Logbook & Resolve",
    "Notification Center"
])


# ============================================================
# TAB 1 -- EXECUTIVE COMMAND CENTER
# ============================================================
with tab1:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Executive Command Center</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Real-time safety intelligence across industrial sites</p>
    </div>
    """, unsafe_allow_html=True)

    total = len(filtered_df)
    critical = len(filtered_df[filtered_df['severity'] == 'CRITICAL'])
    crit_pct = (critical / total * 100) if total > 0 else 0
    unresp_crit = len(filtered_df[(filtered_df['severity'] == 'CRITICAL') & (filtered_df['responded'] == False)])
    fp_rate = safe_mean(filtered_df['is_false_positive']) * 100
    avg_resp = safe_mean(filtered_df[filtered_df['responded'] == True]['response_time_mins'])
    resolved = filtered_df['resolved'].sum()
    res_rate = (resolved / total * 100) if total > 0 else 0

    # FIXED: Use consistent column structure with proper alignment
    cols = st.columns(6)
    metrics = [
        ("Total Alerts", f"{total:,}", "All scenarios", TEXT_COLOR, None),
        ("Critical", f"{critical}", f"{crit_pct:.1f}% of total", CRITICAL_COLOR, None),
        ("Unresponded Critical", f"{unresp_crit}", "Requires escalation", CRITICAL_COLOR if unresp_crit > 0 else TEXT_COLOR, None),
        ("False Positive Rate", f"{fp_rate:.1f}%", "AI model quality", MEDIUM_COLOR if fp_rate > 8 else LOW_COLOR, None),
        ("Avg Response", f"{avg_resp:.1f}m", "All severity levels", ACCENT_COLOR, None),
        ("Resolution Rate", f"{res_rate:.1f}%", f"{int(resolved)} resolved", LOW_COLOR, None)
    ]
    
    for col, (title, value, subtitle, color, delta) in zip(cols, metrics):
        with col:
            create_kpi_card(title, value, subtitle, color, delta)

    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Daily Alert Volume by Scenario</h4>", unsafe_allow_html=True)
        if len(filtered_df) > 0:
            daily = filtered_df.groupby([filtered_df['timestamp'].dt.date, 'scenario_type']).size().reset_index(name='count')
            daily['timestamp'] = pd.to_datetime(daily['timestamp'])
            daily_pivot = daily.pivot(index='timestamp', columns='scenario_type', values='count').fillna(0)

            fig = go.Figure()
            for scenario in daily_pivot.columns:
                fig.add_trace(go.Scatter(
                    x=daily_pivot.index, y=daily_pivot[scenario],
                    mode='lines', name=scenario,
                    line=dict(width=2, color=SCENARIO_COLORS.get(scenario, ACCENT_COLOR)),
                    stackgroup='one'
                ))
            fig.update_layout(
                plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font_size=11),
                margin=dict(l=20, r=20, t=60, b=20), xaxis_title="Date", yaxis_title="Alert Count",
                height=400, hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for current filters.")

    with col2:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Scenario Breakdown</h4>", unsafe_allow_html=True)
        scenario_counts = safe_value_counts(filtered_df, 'scenario_type')
        if len(scenario_counts) > 0:
            colors = [SCENARIO_COLORS.get(s, ACCENT_COLOR) for s in scenario_counts.index]
            fig = go.Figure(data=[go.Pie(
                labels=scenario_counts.index, values=scenario_counts.values,
                hole=0.60, marker_colors=colors,
                textinfo='label+percent', textfont=dict(color=TEXT_COLOR, size=11)
            )])
            fig.update_layout(
                plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR,
                showlegend=False, margin=dict(l=20, r=20, t=40, b=20), height=400
            )
            fig.add_annotation(text=f"<b>{total:,}</b><br>Total", x=0.5, y=0.5, font_size=18, showarrow=False, font_color=TEXT_COLOR)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No scenario data available.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Severity Distribution</h4>", unsafe_allow_html=True)
        sev_counts = safe_value_counts(filtered_df, 'severity')
        if len(sev_counts) > 0:
            colors = [SEVERITY_COLORS.get(s, ACCENT_COLOR) for s in sev_counts.index]
            fig = go.Figure(go.Bar(x=sev_counts.index, y=sev_counts.values, marker_color=colors, text=sev_counts.values, textposition='outside', textfont=dict(color=TEXT_COLOR)))
            fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, margin=dict(l=20, r=20, t=40, b=20), height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No severity data available.")

    with col2:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Alerts by Hour</h4>", unsafe_allow_html=True)
        if len(filtered_df) > 0:
            hourly_df = filtered_df.copy()
            hourly_df['hour'] = hourly_df['timestamp'].dt.hour
            hourly = hourly_df.groupby('hour').size().reset_index(name='count')
            if len(hourly) > 0:
                fig = go.Figure(go.Scatter(
                    x=hourly['hour'], y=hourly['count'], mode='lines+markers',
                    line=dict(color=ACCENT_COLOR, width=3), marker=dict(size=8),
                    fill='tozeroy', fillcolor="rgba(59, 130, 246, 0.15)"
                ))
                fig.add_vrect(x0=22, x1=6, fillcolor=CRITICAL_COLOR, opacity=0.12, line_width=0, annotation_text="Night Shift", annotation_position="top left", annotation_font_color=CRITICAL_COLOR)
                fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Hour", yaxis_title="Count", margin=dict(l=20, r=20, t=60, b=20), height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hourly data available.")
        else:
            st.info("No data available for current filters.")

    with col3:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Alerts by Site</h4>", unsafe_allow_html=True)
        site_counts = safe_value_counts(filtered_df, 'site')
        if len(site_counts) > 0:
            fig = go.Figure(go.Bar(
                y=site_counts.index, x=site_counts.values, orientation='h',
                marker=dict(color=site_counts.values, colorscale=[[0, LOW_COLOR], [0.5, MEDIUM_COLOR], [1, CRITICAL_COLOR]], showscale=False), text=site_counts.values, textposition='outside'
            ))
            fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, margin=dict(l=20, r=40, t=40, b=20), height=300, yaxis=dict(tickfont=dict(size=10)))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No site data available.")

    # Critical Insights
    st.divider()
    st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Critical Insights</h4>", unsafe_allow_html=True)

    night_df = filtered_df[filtered_df['shift'] == SHIFTS[2]] if len(SHIFTS) > 2 else pd.DataFrame()
    day_df = filtered_df[filtered_df['shift'] != SHIFTS[2]] if len(SHIFTS) > 2 else filtered_df.copy()
    night_crit_rate = (len(night_df[night_df['severity'] == 'CRITICAL']) / len(night_df) * 100) if len(night_df) > 0 else 0
    day_crit_rate = (len(day_df[day_df['severity'] == 'CRITICAL']) / len(day_df) * 100) if len(day_df) > 0 else 0

    trained_workers = workers_df[workers_df['training_completed'] == True]['worker_id'].tolist()
    untrained_workers = workers_df[workers_df['training_completed'] == False]['worker_id'].tolist()
    trained_alerts = filtered_df[filtered_df['worker_id'].isin(trained_workers)]
    untrained_alerts = filtered_df[filtered_df['worker_id'].isin(untrained_workers)]
    trained_crit_rate = (len(trained_alerts[trained_alerts['severity'] == 'CRITICAL']) / len(trained_alerts) * 100) if len(trained_alerts) > 0 else 0
    untrained_crit_rate = (len(untrained_alerts[untrained_alerts['severity'] == 'CRITICAL']) / len(untrained_alerts) * 100) if len(untrained_alerts) > 0 else 0
    training_gap = ((untrained_crit_rate - trained_crit_rate) / trained_crit_rate * 100) if trained_crit_rate > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        insight_class = "insight-critical" if unresp_crit > 0 else ""
        st.markdown(f"""
        <div class="insight-card {insight_class}">
            <b style="color:{CRITICAL_COLOR};">Unresponded Critical Alerts</b><br>
            <span style="color:#F8FAFC;">{unresp_crit} CRITICAL alerts without response. 
            {'Immediate escalation protocol required. Each represents potential injury or fatality.' if unresp_crit > 0 else 'All critical alerts responded. Good coverage.'}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="insight-card">
            <b style="color:{HIGH_COLOR};">Night Shift Risk Pattern</b><br>
            <span style="color:#F8FAFC;">Night shift critical rate: <b>{night_crit_rate:.1f}%</b> vs day: <b>{day_crit_rate:.1f}%</b>. 
            {'Night operations show elevated risk. Consider increased supervision.' if night_crit_rate > day_crit_rate else 'Risk levels balanced across shifts.'}</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="insight-card">
            <b style="color:{ACCENT_COLOR};">Training ROI Case</b><br>
            <span style="color:#F8FAFC;">Untrained workers: <b>{untrained_crit_rate:.1f}%</b> critical rate vs trained: <b>{trained_crit_rate:.1f}%</b>. 
            {'Training gap of ' + f'{training_gap:.0f}%' + ' suggests immediate upskilling required.' if training_gap > 0 else 'Training program showing protective effect.'}</span>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 2 -- ZONE HEATMAPS
# ============================================================
with tab2:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Zone Heatmaps</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Spatial risk analysis across all monitored areas</p>
    </div>
    """, unsafe_allow_html=True)

    selected_site_heat = st.selectbox("Select Site for Zone Analysis", options=list(SITES.keys()))

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<h4 style='color:#F8FAFC;'>Zone Severity Heatmap</h4>", unsafe_allow_html=True)
        site_alerts = filtered_df[filtered_df['site'] == selected_site_heat]
        if len(site_alerts) > 0:
            zone_sev = site_alerts.pivot_table(
                index='zone', columns='severity', aggfunc='size', fill_value=0
            )
            # Ensure all severity columns exist
            for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if sev not in zone_sev.columns:
                    zone_sev[sev] = 0
            zone_sev = zone_sev[['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']]
            
            # FIXED: Use proper colorbar title format for Plotly 5.x
            fig = go.Figure(data=go.Heatmap(
                z=zone_sev.values, 
                x=zone_sev.columns, 
                y=zone_sev.index,
                colorscale=[[0, BG_COLOR], [0.3, LOW_COLOR], [0.6, MEDIUM_COLOR], [0.8, HIGH_COLOR], [1, CRITICAL_COLOR]],
                hovertemplate='Zone: %{y}<br>Severity: %{x}<br>Alerts: %{z}<extra></extra>',
                colorbar=dict(
                    title=dict(text="Alerts", font=dict(color=TEXT_COLOR)),
                    tickfont=dict(color=TEXT_COLOR)
                )
            ))
            fig.update_layout(
                plot_bgcolor=BG_COLOR, 
                paper_bgcolor=BG_COLOR, 
                font_color=TEXT_COLOR, 
                xaxis_title="Severity", 
                yaxis_title="Zone", 
                margin=dict(l=20, r=80, t=40, b=20), 
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for selected site.")

    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>Zone Risk Ranking</h4>", unsafe_allow_html=True)
        if len(site_alerts) > 0:
            zone_risk = site_alerts.groupby('zone').agg({
                'severity': 'count',
                'response_time_mins': lambda x: x.mean() if len(x) > 0 else 0
            }).reset_index()
            zone_risk.columns = ['zone', 'total', 'avg_response']
            
            # Calculate critical percentage safely
            crit_counts = site_alerts[site_alerts['severity'] == 'CRITICAL'].groupby('zone').size()
            zone_risk['critical_pct'] = zone_risk['zone'].map(
                lambda z: (crit_counts.get(z, 0) / zone_risk[zone_risk['zone'] == z]['total'].iloc[0] * 100) 
                if zone_risk[zone_risk['zone'] == z]['total'].iloc[0] > 0 else 0
            )
            zone_risk = zone_risk.sort_values('critical_pct', ascending=False)

            for _, row in zone_risk.head(5).iterrows():
                risk_color = CRITICAL_COLOR if row['critical_pct'] > 20 else HIGH_COLOR if row['critical_pct'] > 10 else MEDIUM_COLOR
                st.markdown(f"""
                <div style="background:#151E32; border:1px solid #2D3A4F; border-radius:10px; padding:12px; margin:8px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#F8FAFC; font-weight:600; font-size:13px;">{row['zone']}</span>
                        <span style="color:{risk_color}; font-weight:700; font-size:14px;">{row['critical_pct']:.1f}% CRIT</span>
                    </div>
                    <div style="color:#94A3B8; font-size:11px; margin-top:4px;">{row['total']} alerts | {row['avg_response']:.1f}m avg response</div>
                </div>
                """, unsafe_allow_html=True)

            high_risk_in_site = [z for z in zone_risk['zone'] if z in HIGH_RISK_ZONES]
            if high_risk_in_site:
                st.markdown(f"""
                <div style="background:#451A1A; border:1px solid #EF4444; border-radius:10px; padding:12px; margin-top:12px;">
                    <span style="color:#EF4444; font-weight:700; font-size:13px;">High-Risk Zones Active</span><br>
                    <span style="color:#F8FAFC; font-size:12px;">{', '.join(high_risk_in_site)} require enhanced monitoring per Buddywise safety protocols.</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No zone data available.")

    st.divider()

    st.markdown("<h4 style='color:#F8FAFC;'>Cross-Site Critical Alert Density</h4>", unsafe_allow_html=True)
    cross_site = filtered_df[filtered_df['severity'] == 'CRITICAL'].groupby(['site', 'zone']).size().unstack(fill_value=0)
    if len(cross_site) > 0:
        # FIXED: Use proper colorbar title format for Plotly 5.x
        fig = go.Figure(data=go.Heatmap(
            z=cross_site.values, 
            x=cross_site.columns, 
            y=cross_site.index,
            colorscale=[[0, BG_COLOR], [0.5, HIGH_COLOR], [1, CRITICAL_COLOR]],
            hovertemplate='Site: %{y}<br>Zone: %{x}<br>Critical: %{z}<extra></extra>',
            colorbar=dict(
                title=dict(text="Critical", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR)
            )
        ))
        fig.update_layout(
            plot_bgcolor=BG_COLOR, 
            paper_bgcolor=BG_COLOR, 
            font_color=TEXT_COLOR, 
            xaxis_title="Zone", 
            yaxis_title="Site", 
            margin=dict(l=20, r=80, t=40, b=20), 
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No critical alerts for cross-site heatmap.")


# ============================================================
# TAB 3 -- WORKER INTELLIGENCE
# ============================================================
with tab3:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Worker Intelligence</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Risk profiling, training impact, and behavioral analytics</p>
    </div>
    """, unsafe_allow_html=True)

    filtered_workers = workers_df.copy()
    filtered_workers = compute_worker_risk_scores(filtered_df, filtered_workers)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h4 style='color:#F8FAFC;'>Top 15 Highest-Risk Workers</h4>", unsafe_allow_html=True)
        if len(filtered_workers) > 0:
            top_risk = filtered_workers.nlargest(min(15, len(filtered_workers)), 'risk_score')
            fig = go.Figure(go.Bar(
                x=top_risk['risk_score'], y=top_risk['worker_id'], orientation='h',
                marker=dict(color=top_risk['risk_score'], colorscale=[[0, LOW_COLOR], [0.4, MEDIUM_COLOR], [0.7, HIGH_COLOR], [1, CRITICAL_COLOR]]),
                text=top_risk['risk_score'].round(1), textposition='outside', textfont=dict(color=TEXT_COLOR)
            ))
            fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Risk Score", yaxis_title="Worker ID", margin=dict(l=20, r=60, t=40, b=20), height=450)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No worker risk data available.")

    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>Department Risk Analysis</h4>", unsafe_allow_html=True)
        dept_stats = filtered_workers.groupby('department').agg({
            'risk_score': 'mean', 'worker_id': 'count', 'critical_count': 'mean'
        }).reset_index()
        dept_stats.columns = ['department', 'avg_risk', 'headcount', 'avg_critical']
        if len(dept_stats) > 0:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=dept_stats['department'], y=dept_stats['avg_risk'], name='Avg Risk Score', marker_color=ACCENT_COLOR, text=dept_stats['avg_risk'].round(1), textposition='outside'), secondary_y=False)
            fig.add_trace(go.Scatter(x=dept_stats['department'], y=dept_stats['headcount'], name='Headcount', mode='lines+markers', line=dict(color=MUTED_TEXT, width=2), marker=dict(size=8)), secondary_y=True)
            fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, margin=dict(l=20, r=60, t=40, b=20), height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig.update_yaxes(title_text="Risk Score", secondary_y=False, gridcolor=BORDER_COLOR)
            fig.update_yaxes(title_text="Headcount", secondary_y=True, gridcolor=BORDER_COLOR)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No department data available.")

    st.divider()

    st.markdown("<h4 style='color:#F8FAFC;'>Training Impact Analysis</h4>", unsafe_allow_html=True)

    training_comparison = []
    for trained in [True, False]:
        subset = filtered_workers[filtered_workers['training_completed'] == trained]
        worker_ids = subset['worker_id'].tolist()
        worker_alerts = filtered_df[filtered_df['worker_id'].isin(worker_ids)]
        training_comparison.append({
            'status': 'Trained' if trained else 'Untrained',
            'workers': len(subset),
            'avg_alerts': len(worker_alerts) / len(subset) if len(subset) > 0 else 0,
            'avg_critical': len(worker_alerts[worker_alerts['severity'] == 'CRITICAL']) / len(subset) if len(subset) > 0 else 0,
            'avg_risk': subset['risk_score'].mean() if len(subset) > 0 else 0,
            'avg_response': safe_mean(worker_alerts[worker_alerts['responded'] == True]['response_time_mins'])
        })

    train_df = pd.DataFrame(training_comparison)

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ('avg_alerts', 'Avg Alerts/Worker', 'Alerts per worker'), 
        ('avg_critical', 'Avg Critical/Worker', 'Critical alerts per worker'), 
        ('avg_risk', 'Avg Risk Score', 'Composite risk metric'), 
        ('avg_response', 'Avg Response Time', 'Minutes to respond')
    ]

    for col, (metric, title, subtitle) in zip([col1, col2, col3, col4], metrics):
        with col:
            if len(train_df) > 0:
                fig = go.Figure()
                colors = [LOW_COLOR, CRITICAL_COLOR]
                for i, row in train_df.iterrows():
                    val = row[metric] if pd.notna(row[metric]) else 0
                    fig.add_trace(go.Bar(
                        x=[row['status']], 
                        y=[val], 
                        marker_color=colors[i], 
                        text=[f"{val:.2f}"], 
                        textposition='outside', 
                        textfont=dict(color=TEXT_COLOR, size=14)
                    ))
                fig.update_layout(
                    plot_bgcolor=BG_COLOR, 
                    paper_bgcolor=BG_COLOR, 
                    font_color=TEXT_COLOR, 
                    showlegend=False, 
                    yaxis_title=title, 
                    margin=dict(l=20, r=20, t=20, b=20), 
                    height=280
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data")
            st.markdown(f"<p style='text-align:center; color:#94A3B8; font-size:11px;'>{subtitle}</p>", unsafe_allow_html=True)

    trained_crit = train_df[train_df['status'] == 'Trained']['avg_critical'].values[0] if len(train_df[train_df['status'] == 'Trained']) > 0 else 0
    untrained_crit = train_df[train_df['status'] == 'Untrained']['avg_critical'].values[0] if len(train_df[train_df['status'] == 'Untrained']) > 0 else 0
    roi_pct = ((untrained_crit - trained_crit) / trained_crit * 100) if trained_crit > 0 else 0

    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {ACCENT_COLOR}20, {LOW_COLOR}20); border:1px solid {ACCENT_COLOR}; border-radius:16px; padding:24px; margin-top:20px; text-align:center;">
        <h3 style="color:{ACCENT_COLOR}; margin:0; font-size:24px; font-weight:800;">Training ROI: {roi_pct:.0f}% Reduction in Critical Alerts</h3>
        <p style="color:#F8FAFC; margin:8px 0 0 0; font-size:15px;">
            Untrained workers average <b>{untrained_crit:.2f}</b> critical alerts vs trained workers at <b>{trained_crit:.2f}</b>. 
            At an estimated 50000 EUR per serious injury (DGUV data), training investment pays for itself in weeks.</p>
    </div>
    """)


# ============================================================
# TAB 4 -- PREDICTIVE ENGINE
# ============================================================
with tab4:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Predictive Safety Engine</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">AI-powered forecasting and proactive intervention triggers</p>
    </div>
    """, unsafe_allow_html=True)

    if len(filtered_df) > 0:
        # Time series for forecasting
        daily_counts = filtered_df.groupby(filtered_df['timestamp'].dt.date).size().reset_index(name='alerts')
        daily_counts['timestamp'] = pd.to_datetime(daily_counts['timestamp'])
        daily_counts = daily_counts.sort_values('timestamp')
        
        if len(daily_counts) >= 3:
            # Simple trend line
            x_numeric = np.arange(len(daily_counts))
            z = np.polyfit(x_numeric, daily_counts['alerts'], 1)
            p = np.poly1d(z)
            trend_next = p(len(daily_counts))
            trend_prev = p(len(daily_counts) - 1)
            trend_pct = ((trend_next - trend_prev) / trend_prev * 100) if trend_prev > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                create_kpi_card("Trend Forecast", f"{trend_next:.0f}", "Next day predicted", CRITICAL_COLOR if trend_pct > 10 else LOW_COLOR)
            with col2:
                create_kpi_card("Trend Direction", f"{trend_pct:+.1f}%", "Day-over-day", CRITICAL_COLOR if trend_pct > 0 else LOW_COLOR)
            with col3:
                volatility = daily_counts['alerts'].std() / daily_counts['alerts'].mean() if daily_counts['alerts'].mean() > 0 else 0
                create_kpi_card("Volatility Index", f"{volatility:.2f}", "Alert pattern stability", CRITICAL_COLOR if volatility > 0.5 else LOW_COLOR)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_counts['timestamp'], y=daily_counts['alerts'],
                mode='lines+markers', name='Actual',
                line=dict(color=ACCENT_COLOR, width=2), marker=dict(size=6)
            ))
            # Extend with prediction
            last_date = daily_counts['timestamp'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=3, freq='D')
            future_vals = [p(len(daily_counts) + i) for i in range(3)]
            fig.add_trace(go.Scatter(
                x=future_dates, y=future_vals,
                mode='lines+markers', name='Predicted',
                line=dict(color=MEDIUM_COLOR, width=2, dash='dash'), marker=dict(size=6)
            ))
            fig.update_layout(
                plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR,
                xaxis_title="Date", yaxis_title="Alert Count",
                margin=dict(l=20, r=20, t=60, b=20), height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for forecasting (minimum 3 days required).")
    else:
        st.info("No data available for predictive analysis.")

    st.divider()

    st.markdown("<h4 style='color:#F8FAFC;'>Proactive Intervention Triggers</h4>", unsafe_allow_html=True)
    
    triggers = []
    if len(filtered_df) > 0:
        # Trigger 1: High night shift ratio
        night_alerts = filtered_df[filtered_df['shift'] == SHIFTS[2]] if len(SHIFTS) > 2 else pd.DataFrame()
        if len(night_alerts) > 0 and len(filtered_df) > 0:
            night_ratio = len(night_alerts) / len(filtered_df)
            if night_ratio > 0.4:
                triggers.append(("Night Shift Overload", f"{night_ratio:.1%} of alerts occur during night shift. Consider additional supervision.", CRITICAL_COLOR))
        
        # Trigger 2: Unresolved criticals
        if unresp_crit > 2:
            triggers.append(("Critical Response Failure", f"{unresp_crit} critical alerts without response. Escalate to site safety officer.", CRITICAL_COLOR))
        
        # Trigger 3: High FP rate
        if fp_rate > 10:
            triggers.append(("Model Degradation", f"False positive rate at {fp_rate:.1f}%. Retrain detection model.", HIGH_COLOR))
        
        # Trigger 4: Zone concentration
        if len(filtered_df) > 0:
            top_zone = filtered_df['zone'].value_counts().head(1)
            if len(top_zone) > 0 and top_zone.iloc[0] / len(filtered_df) > 0.3:
                triggers.append(("Zone Hotspot", f"{top_zone.index[0]} generates {top_zone.iloc[0]/len(filtered_df):.1%} of all alerts. Inspect equipment and workflow.", HIGH_COLOR))
    
    if triggers:
        for title, desc, color in triggers:
            st.markdown(f"""
            <div style="background: {color}15; border-left: 4px solid {color}; border-radius: 0 12px 12px 0; padding: 16px; margin: 8px 0;">
                <span style="color:{color}; font-weight:700; font-size:14px;">{title}</span><br>
                <span style="color:#F8FAFC; font-size:13px;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #22C55E15; border-left: 4px solid #22C55E; border-radius: 0 12px 12px 0; padding: 16px; margin: 8px 0;">
            <span style="color:#22C55E; font-weight:700; font-size:14px;">All Systems Nominal</span><br>
            <span style="color:#F8FAFC; font-size:13px;">No proactive triggers activated. Safety parameters within expected ranges.</span>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 5 -- LOGBOOK & RESOLVE
# ============================================================
with tab5:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Logbook & Resolve</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Alert audit trail, resolution workflow, and compliance logging</p>
    </div>
    """, unsafe_allow_html=True)

    # Resolution controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h4 style='color:#F8FAFC;'>Unresolved Alerts</h4>", unsafe_allow_html=True)
        unresolved = filtered_df[filtered_df['resolved'] == False].sort_values('timestamp', ascending=False)
        if len(unresolved) > 0:
            display_cols = ['timestamp', 'site', 'zone', 'scenario_type', 'severity', 'worker_id', 'description']
            display_cols = [c for c in display_cols if c in unresolved.columns]
            st.dataframe(
                unresolved[display_cols].head(50),
                use_container_width=True,
                height=400
            )
        else:
            st.info("All alerts resolved. Excellent response performance.")

    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>Quick Actions</h4>", unsafe_allow_html=True)
        if len(unresolved) > 0:
            st.metric("Pending", len(unresolved))
            st.metric("Critical Pending", len(unresolved[unresolved['severity'] == 'CRITICAL']))
            
            if st.button("Mark All Resolved", type="primary", use_container_width=True):
                st.success("Batch resolution simulated. In production, this would update the database.")
            
            selected_alert = st.selectbox(
                "Select Alert to Resolve",
                options=unresolved['alert_id'].tolist() if 'alert_id' in unresolved.columns else [],
                format_func=lambda x: f"Alert #{x}"
            )
            
            if selected_alert and st.button("Resolve Selected", use_container_width=True):
                st.success(f"Alert {selected_alert} marked as resolved.")
        else:
            st.metric("Pending", 0)
            st.metric("Critical Pending", 0)
            st.info("No actions required.")

    st.divider()

    st.markdown("<h4 style='color:#F8FAFC;'>Alert Logbook</h4>", unsafe_allow_html=True)
    log_cols = ['timestamp', 'site', 'zone', 'scenario_type', 'severity', 'worker_id', 'responded', 'response_time_mins', 'resolved', 'is_false_positive']
    log_cols = [c for c in log_cols if c in filtered_df.columns]
    
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df[log_cols].sort_values('timestamp', ascending=False).head(100),
            use_container_width=True,
            height=500
        )
    else:
        st.info("No log entries match current filters.")


# ============================================================
# TAB 6 -- NOTIFICATION CENTER
# ============================================================
with tab6:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Notification Center</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Escalation rules, stakeholder mapping, and dispatch logs</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h4 style='color:#F8FAFC;'>Escalation Matrix</h4>", unsafe_allow_html=True)
        escalation_data = {
            'Severity': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            'Response Time SLA': ['5 min', '15 min', '1 hour', '4 hours'],
            'Notify': ['Site Manager + Safety Officer + Emergency Services', 'Department Lead + Safety Officer', 'Supervisor', 'Log Only'],
            'Escalation Path': ['Immediate', '15 min delay', '1 hour delay', 'End of shift']
        }
        esc_df = pd.DataFrame(escalation_data)
        st.dataframe(esc_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>Recent Notifications</h4>", unsafe_allow_html=True)
        if len(filtered_df) > 0:
            recent_crit = filtered_df[filtered_df['severity'] == 'CRITICAL'].tail(10)
            if len(recent_crit) > 0:
                for _, row in recent_crit.iterrows():
                    ts = row['timestamp'].strftime('%H:%M') if pd.notnull(row['timestamp']) else 'Unknown'
                    st.markdown(f"""
                    <div style="background: #151E32; border-left: 3px solid {CRITICAL_COLOR}; border-radius: 0 8px 8px 0; padding: 10px; margin: 6px 0;">
                        <span style="color:#F8FAFC; font-size:12px; font-weight:600;">{ts} - {row.get('scenario_type', 'Unknown')}</span><br>
                        <span style="color:#94A3B8; font-size:11px;">{row.get('site', 'Unknown')} | {row.get('zone', 'Unknown')} | {row.get('worker_id', 'Unknown')}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No critical alerts in current view.")
        else:
            st.info("No data available.")

    st.divider()

    st.markdown("<h4 style='color:#F8FAFC;'>Stakeholder Configuration</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Site Manager Email", value="manager@buddywise.ai")
        st.text_input("Safety Officer Email", value="safety@buddywise.ai")
    with col2:
        st.text_input("Emergency Contact", value="+49-170-0000000")
        st.selectbox("Notification Channel", ["SMS + Email", "Email Only", "App Push", "PagerDuty"])
    with col3:
        st.checkbox("Weekend Escalation", value=True)
        st.checkbox("Auto-Notify Emergency Services", value=False)
        st.checkbox("Daily Digest", value=True)
    
    if st.button("Save Configuration", type="primary"):
        st.success("Notification settings saved (simulated).")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown(f"""
<div style="text-align:center; color:#94A3B8; font-size:11px; padding: 8px 0;">
    Buddywise Safety Intelligence Command Center | Interview Project July 2026<br>
    Built with Streamlit + Plotly | Data simulated for demonstration
</div>
""", unsafe_allow_html=True)
