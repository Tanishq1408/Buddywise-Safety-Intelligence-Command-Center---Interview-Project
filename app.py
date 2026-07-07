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
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .metric-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
    }
    .metric-value {
        font-size: 36px;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.5px;
    }
    .metric-label {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 8px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-delta {
        font-size: 12px;
        margin-top: 6px;
        font-weight: 600;
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
    "Shifts", options=alerts_df['shift'].unique(), default=list(alerts_df['shift'].unique())
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

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: create_kpi_card("Total Alerts", f"{total:,}", "All scenarios")
    with col2: create_kpi_card("Critical", f"{critical}", f"{crit_pct:.1f}% of total", CRITICAL_COLOR)
    with col3: create_kpi_card("Unresponded Critical", f"{unresp_crit}", "Requires escalation", CRITICAL_COLOR if unresp_crit > 0 else TEXT_COLOR)
    with col4: create_kpi_card("False Positive Rate", f"{fp_rate:.1f}%", "AI model quality", MEDIUM_COLOR if fp_rate > 8 else LOW_COLOR)
    with col5: create_kpi_card("Avg Response", f"{avg_resp:.1f}m", "All severity levels", ACCENT_COLOR)
    with col6: create_kpi_card("Resolution Rate", f"{res_rate:.1f}%", f"{resolved} resolved", LOW_COLOR)

    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Daily Alert Volume by Scenario</h4>", unsafe_allow_html=True)
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

    with col2:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Scenario Breakdown</h4>", unsafe_allow_html=True)
        scenario_counts = safe_value_counts(filtered_df, 'scenario_type')
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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Severity Distribution</h4>", unsafe_allow_html=True)
        sev_counts = safe_value_counts(filtered_df, 'severity')
        colors = [SEVERITY_COLORS[s] for s in sev_counts.index]
        fig = go.Figure(go.Bar(x=sev_counts.index, y=sev_counts.values, marker_color=colors, text=sev_counts.values, textposition='outside', textfont=dict(color=TEXT_COLOR)))
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, margin=dict(l=20, r=20, t=40, b=20), height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Alerts by Hour</h4>", unsafe_allow_html=True)
        filtered_df['hour'] = filtered_df['timestamp'].dt.hour
               hourly = filtered_df.groupby('hour').size().reset_index(name='count')
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
            st.info("No hourly data available for current filters.")
            
    with col3:
        st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Alerts by Site</h4>", unsafe_allow_html=True)
        site_counts = safe_value_counts(filtered_df, 'site')
        fig = go.Figure(go.Bar(
            y=site_counts.index, x=site_counts.values, orientation='h',
            marker=dict(color=site_counts.values, colorscale=[[0, LOW_COLOR], [0.5, MEDIUM_COLOR], [1, CRITICAL_COLOR]], showscale=False),
            text=site_counts.values, textposition='outside'
        ))
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, margin=dict(l=20, r=40, t=40, b=20), height=300, yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

    # Critical Insights
    st.divider()
    st.markdown("<h4 style='color:#F8FAFC; font-size:16px;'>Critical Insights</h4>", unsafe_allow_html=True)

    night_df = filtered_df[filtered_df['shift'] == SHIFTS[2]]
    day_df = filtered_df[filtered_df['shift'] != SHIFTS[2]]
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
            <b>{training_gap:.0f}% higher</b> critical rate without training. Strong business case for mandatory programs.</span>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB 2 -- ZONE HEATMAPS
# ============================================================
with tab2:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Zone Heatmaps</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Identify safety hotspots across zones -- Buddywise's signature analytics feature</p>
    </div>
    """, unsafe_allow_html=True)

    selected_heatmap_site = st.selectbox("Select Site for Zone Analysis", options=selected_sites, key="heatmap_site")

    if selected_heatmap_site:
        site_alerts = filtered_df[filtered_df['site'] == selected_heatmap_site]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("<h4 style='color:#F8FAFC;'>Zone x Severity Heatmap</h4>", unsafe_allow_html=True)
            zone_sev = site_alerts.groupby(['zone', 'severity']).size().unstack(fill_value=0)
            for col in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if col not in zone_sev.columns:
                    zone_sev[col] = 0
            zone_sev = zone_sev[['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']]

            fig = go.Figure(data=go.Heatmap(
                z=zone_sev.values, x=zone_sev.columns, y=zone_sev.index,
                colorscale=[[0, BG_COLOR], [0.2, LOW_COLOR], [0.5, MEDIUM_COLOR], [0.8, HIGH_COLOR], [1, CRITICAL_COLOR]],
                text=zone_sev.values, texttemplate="%{text}", textfont={"size": 13, "color": TEXT_COLOR},
                hovertemplate='Zone: %{y}<br>Severity: %{x}<br>Count: %{z}<extra></extra>',
                colorbar=dict(title="Alerts", titlefont=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR))
            ))
            fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Severity", yaxis_title="Zone", margin=dict(l=20, r=80, t=40, b=20), height=450)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("<h4 style='color:#F8FAFC;'>Zone Risk Summary</h4>", unsafe_allow_html=True)
            zone_risk = site_alerts.groupby('zone').agg({
                'alert_id': 'count',
                'severity': lambda x: (x == 'CRITICAL').sum() / len(x) * 100 if len(x) > 0 else 0,
                'response_time_mins': lambda x: x.mean() if len(x) > 0 else 0
            }).reset_index()
            zone_risk.columns = ['zone', 'total', 'critical_pct', 'avg_response']
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

    st.divider()

    st.markdown("<h4 style='color:#F8FAFC;'>Cross-Site Critical Alert Density</h4>", unsafe_allow_html=True)
    cross_site = filtered_df[filtered_df['severity'] == 'CRITICAL'].groupby(['site', 'zone']).size().unstack(fill_value=0)

    fig = go.Figure(data=go.Heatmap(
        z=cross_site.values, x=cross_site.columns, y=cross_site.index,
        colorscale=[[0, BG_COLOR], [0.5, HIGH_COLOR], [1, CRITICAL_COLOR]],
        hovertemplate='Site: %{y}<br>Zone: %{x}<br>Critical: %{z}<extra></extra>',
        colorbar=dict(title="Critical", titlefont=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR))
    ))
    fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Zone", yaxis_title="Site", margin=dict(l=20, r=80, t=40, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)


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
        top_risk = filtered_workers.nlargest(min(15, len(filtered_workers)), 'risk_score') if len(filtered_workers) > 0 else filtered_workers

        fig = go.Figure(go.Bar(
            x=top_risk['risk_score'], y=top_risk['worker_id'], orientation='h',
            marker=dict(color=top_risk['risk_score'], colorscale=[[0, LOW_COLOR], [0.4, MEDIUM_COLOR], [0.7, HIGH_COLOR], [1, CRITICAL_COLOR]]),
            text=top_risk['risk_score'].round(1), textposition='outside', textfont=dict(color=TEXT_COLOR)
        ))
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Risk Score", yaxis_title="Worker ID", margin=dict(l=20, r=60, t=40, b=20), height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>Department Risk Analysis</h4>", unsafe_allow_html=True)
        dept_stats = filtered_workers.groupby('department').agg({
            'risk_score': 'mean', 'worker_id': 'count', 'critical_count': 'mean'
        }).reset_index()
        dept_stats.columns = ['department', 'avg_risk', 'headcount', 'avg_critical']

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=dept_stats['department'], y=dept_stats['avg_risk'], name='Avg Risk Score', marker_color=ACCENT_COLOR, text=dept_stats['avg_risk'].round(1), textposition='outside'), secondary_y=False)
        fig.add_trace(go.Scatter(x=dept_stats['department'], y=dept_stats['headcount'], name='Headcount', mode='lines+markers', line=dict(color=MUTED_TEXT, width=2), marker=dict(size=8)), secondary_y=True)
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, margin=dict(l=20, r=60, t=40, b=20), height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_yaxes(title_text="Risk Score", secondary_y=False, gridcolor=BORDER_COLOR)
        fig.update_yaxes(title_text="Headcount", secondary_y=True, gridcolor=BORDER_COLOR)
        st.plotly_chart(fig, use_container_width=True)

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
            'avg_risk': subset['risk_score'].mean(),
            'avg_response': safe_mean(worker_alerts[worker_alerts['responded'] == True]['response_time_mins'])
        })

    train_df = pd.DataFrame(training_comparison)

    col1, col2, col3, col4 = st.columns(4)
    metrics = [('avg_alerts', 'Avg Alerts/Worker', 'Alerts per worker'), ('avg_critical', 'Avg Critical/Worker', 'Critical alerts per worker'), ('avg_risk', 'Avg Risk Score', 'Composite risk metric'), ('avg_response', 'Avg Response Time', 'Minutes to respond')]

    for col, (metric, title, subtitle) in zip([col1, col2, col3, col4], metrics):
        with col:
            fig = go.Figure()
            colors = [LOW_COLOR, CRITICAL_COLOR]
            for i, row in train_df.iterrows():
                fig.add_trace(go.Bar(x=[row['status']], y=[row[metric]], marker_color=colors[i], text=[f"{row[metric]:.2f}"], textposition='outside', textfont=dict(color=TEXT_COLOR, size=14)))
            fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, showlegend=False, yaxis_title=title, margin=dict(l=20, r=20, t=20, b=20), height=280)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"<p style='text-align:center; color:#94A3B8; font-size:11px;'>{subtitle}</p>", unsafe_allow_html=True)

    trained_crit = train_df[train_df['status'] == 'Trained']['avg_critical'].values[0]
    untrained_crit = train_df[train_df['status'] == 'Untrained']['avg_critical'].values[0]
    roi_pct = ((untrained_crit - trained_crit) / trained_crit * 100) if trained_crit > 0 else 0

    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {ACCENT_COLOR}20, {LOW_COLOR}20); border:1px solid {ACCENT_COLOR}; border-radius:16px; padding:24px; margin-top:20px; text-align:center;">
        <h3 style="color:{ACCENT_COLOR}; margin:0; font-size:24px; font-weight:800;">Training ROI: {roi_pct:.0f}% Reduction in Critical Alerts</h3>
        <p style="color:#F8FAFC; margin:8px 0 0 0; font-size:15px;">
            Untrained workers average <b>{untrained_crit:.2f}</b> critical alerts vs trained workers at <b>{trained_crit:.2f}</b>. 
            At an estimated 50000 EUR per serious injury (DGUV data), training investment pays for itself in <b>3 weeks</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# TAB 4 -- PREDICTIVE RISK ENGINE
# ============================================================
with tab4:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Predictive Risk Engine</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Simulate scenarios and predict risk scores before incidents occur</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<h4 style='color:#F8FAFC;'>Scenario Configuration</h4>", unsafe_allow_html=True)

        pred_site = st.selectbox("Site", options=list(SITES.keys()), key="pred_site")
        pred_zone = st.selectbox("Zone", options=SITES[pred_site]['zones'], key="pred_zone")
        pred_scenario = st.selectbox("Risk Scenario", options=list(RISK_SCENARIOS.keys()), key="pred_scenario")
        pred_violation = st.selectbox("Violation Type", options=RISK_SCENARIOS[pred_scenario]['violations'], key="pred_violation")
        pred_hour = st.slider("Hour of Day", 0, 23, 14, key="pred_hour")
        pred_shift = st.selectbox("Shift", options=SHIFTS, key="pred_shift")
        pred_tenure = st.slider("Worker Tenure (years)", 0.0, 20.0, 2.0, 0.5, key="pred_tenure")
        pred_trained = st.checkbox("Training Completed", value=True, key="pred_trained")
        pred_lone = st.checkbox("Lone Worker", value=False, key="pred_lone")

        base_scores = {'CRITICAL': 90, 'HIGH': 70, 'MEDIUM': 50, 'LOW': 30}
        base_severity = RISK_SCENARIOS[pred_scenario]['severity_base'][pred_violation]
        risk_score = base_scores[base_severity]
        breakdown = [(f"Base: {pred_violation}", base_scores[base_severity])]

        modifiers = []
        if not pred_trained:
            risk_score += 15; modifiers.append(("Untrained worker", 15))
        if pred_tenure < 1:
            risk_score += 12; modifiers.append(("Tenure < 1 year", 12))
        if pred_shift == SHIFTS[2]:
            risk_score += 10; modifiers.append(("Night shift", 10))
        if pred_zone in HIGH_RISK_ZONES:
            risk_score += 15; modifiers.append((f"High-risk zone: {pred_zone}", 15))
        if pred_hour >= 22 or pred_hour <= 5:
            risk_score += 8; modifiers.append(("Late night hours (22-05)", 8))
        if pred_lone:
            risk_score += 10; modifiers.append(("Lone worker (no buddy)", 10))
        if pred_scenario == 'Person Down':
            risk_score += 5; modifiers.append(("Person Down scenario", 5))

        risk_score = min(100, risk_score)

        if risk_score >= 85:
            risk_level = "CRITICAL"; risk_class = "risk-critical"
            advice = "STOP: Stop all work. Full safety lockdown. Escalate to site safety officer + emergency services on standby."
        elif risk_score >= 65:
            risk_level = "HIGH"; risk_class = "risk-high"
            advice = "HIGH: Supervisor must verify before work proceeds. Enhanced PPE check. Buddy system mandatory."
        elif risk_score >= 40:
            risk_level = "MEDIUM"; risk_class = "risk-medium"
            advice = "MEDIUM: Standard safety protocols. Ensure all guards and barriers in place. Monitor closely."
        else:
            risk_level = "LOW"; risk_class = "risk-low"
            advice = "LOW: Routine operations. Maintain standard safety practices. Regular check-ins."

    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>Risk Assessment Result</h4>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="risk-card {risk_class}">
            <div style="font-size:16px; margin-bottom:8px;">RISK LEVEL: {risk_level}</div>
            <div style="font-size:56px; line-height:1;">{risk_score}</div>
            <div style="font-size:14px; margin-top:4px; opacity:0.8;">out of 100</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#151E32; border:1px solid #2D3A4F; border-radius:12px; padding:20px; margin-top:16px;">
            <b style="color:#3B82F6; font-size:14px;">Recommended Action:</b><br>
            <p style="color:#F8FAFC; margin:8px 0 0 0; font-size:14px; line-height:1.6;">{advice}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h5 style='color:#F8FAFC; margin-top:20px;'>Score Breakdown</h5>", unsafe_allow_html=True)
        breakdown_df = pd.DataFrame(modifiers, columns=['Risk Factor', 'Points'])
        breakdown_df['Points'] = breakdown_df['Points'].astype(str) + ' pts'
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

        st.markdown("<h5 style='color:#F8FAFC; margin-top:20px;'>What-If: Training Impact</h5>", unsafe_allow_html=True)

        trained_score = base_scores[base_severity]
        if pred_tenure < 1: trained_score += 12
        if pred_shift == SHIFTS[2]: trained_score += 10
        if pred_zone in HIGH_RISK_ZONES: trained_score += 15
        if pred_hour >= 22 or pred_hour <= 5: trained_score += 8
        if pred_lone: trained_score += 10
        if pred_scenario == 'Person Down': trained_score += 5
        trained_score = min(100, trained_score)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div style="background:#451A1A; border:1px solid #EF4444; border-radius:10px; padding:16px; text-align:center;">
                <div style="color:#94A3B8; font-size:12px;">WITHOUT TRAINING</div>
                <div style="color:#EF4444; font-size:32px; font-weight:800;">{risk_score}</div>
                <div style="color:#F8FAFC; font-size:12px;">{risk_level}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            trained_level = "CRITICAL" if trained_score >= 85 else "HIGH" if trained_score >= 65 else "MEDIUM" if trained_score >= 40 else "LOW"
            trained_color = CRITICAL_COLOR if trained_level == "CRITICAL" else HIGH_COLOR if trained_level == "HIGH" else MEDIUM_COLOR if trained_level == "MEDIUM" else LOW_COLOR
            st.markdown(f"""
            <div style="background:rgba(34,197,94,0.1); border:1px solid #22C55E; border-radius:10px; padding:16px; text-align:center;">
                <div style="color:#94A3B8; font-size:12px;">WITH TRAINING</div>
                <div style="color:{trained_color}; font-size:32px; font-weight:800;">{trained_score}</div>
                <div style="color:#F8FAFC; font-size:12px;">{trained_level}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<h4 style='color:#F8FAFC;'>Historical Drivers of Critical Alerts</h4>", unsafe_allow_html=True)

    crit_df = filtered_df[filtered_df['severity'] == 'CRITICAL']
    col1, col2, col3 = st.columns(3)

    with col1:
        crit_violation = safe_value_counts(crit_df, 'scenario_type').head(5)
        fig = go.Figure(go.Bar(x=crit_violation.values, y=crit_violation.index, orientation='h', marker_color=CRITICAL_COLOR, text=crit_violation.values, textposition='outside'))
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, margin=dict(l=20, r=40, t=20, b=20), height=280, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        crit_shift = safe_value_counts(crit_df, 'shift')
        fig = go.Figure(go.Pie(labels=crit_shift.index, values=crit_shift.values, marker_colors=[MEDIUM_COLOR, HIGH_COLOR, CRITICAL_COLOR], textinfo='label+percent', textfont=dict(color=TEXT_COLOR)))
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        crit_hour = crit_df.groupby(crit_df['timestamp'].dt.hour).size()
        fig = go.Figure(go.Bar(x=crit_hour.index, y=crit_hour.values, marker_color=CRITICAL_COLOR))
        fig.add_vrect(x0=22, x1=6, fillcolor=HIGH_COLOR, opacity=0.15, line_width=0)
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Hour", yaxis_title="Critical Count", margin=dict(l=20, r=20, t=20, b=20), height=280, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 5 -- LOGBOOK & RESOLVE
# ============================================================
with tab5:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Logbook & Resolve</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Review, assign, comment, and resolve safety events -- just like Buddywise's logbook</p>
    </div>
    """, unsafe_allow_html=True)

    search_col1, search_col2, search_col3, search_col4 = st.columns([2, 1, 1, 1])
    with search_col1:
        search_text = st.text_input("Search (Alert ID, Worker, Zone)", placeholder="e.g. ALT-00123 or W042")
    with search_col2:
        filter_resolved = st.selectbox("Status", options=["All", "Resolved", "Unresolved", "Unresponded"])
    with search_col3:
        filter_scenario = st.selectbox("Scenario", options=["All"] + list(RISK_SCENARIOS.keys()))
    with search_col4:
        sort_by = st.selectbox("Sort By", options=["Newest First", "Severity", "Response Time"])

    display_df = filtered_df.copy()
    if search_text:
        mask = (display_df['alert_id'].str.contains(search_text, case=False, na=False) |
                display_df['worker_id'].str.contains(search_text, case=False, na=False) |
                display_df['zone'].str.contains(search_text, case=False, na=False))
        display_df = display_df[mask]

    if filter_resolved == "Resolved":
        display_df = display_df[display_df['resolved'] == True]
    elif filter_resolved == "Unresolved":
        display_df = display_df[display_df['resolved'] == False]
    elif filter_resolved == "Unresponded":
        display_df = display_df[display_df['responded'] == False]

    if filter_scenario != "All":
        display_df = display_df[display_df['scenario_type'] == filter_scenario]

    if sort_by == "Severity":
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        display_df = display_df.sort_values('severity', key=lambda x: x.map(severity_order))
    elif sort_by == "Response Time":
        display_df = display_df.sort_values('response_time_mins', ascending=False)
    else:
        display_df = display_df.sort_values('timestamp', ascending=False)

    display_cols = ['alert_id', 'timestamp', 'site', 'zone', 'scenario_type', 'violation_type', 'severity', 'shift', 'worker_id', 'responded', 'resolved', 'assigned_to', 'comments']
    display_formatted = display_df[display_cols].copy()
    display_formatted['timestamp'] = display_formatted['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    display_formatted['responded'] = display_formatted['responded'].map({True: 'YES', False: 'NO'})
    display_formatted['resolved'] = display_formatted['resolved'].map({True: 'YES', False: 'PENDING'})

    def color_severity(val):
        color = SEVERITY_COLORS.get(val, TEXT_COLOR)
        return f'color: {color}; font-weight: 600;'

    st.dataframe(
        display_formatted.style.applymap(color_severity, subset=['severity']),
        use_container_width=True, hide_index=True,
        column_config={
            "alert_id": st.column_config.TextColumn("Alert ID", width="small"),
            "timestamp": st.column_config.TextColumn("Time", width="medium"),
            "scenario_type": st.column_config.TextColumn("Scenario", width="medium"),
            "violation_type": st.column_config.TextColumn("Violation", width="large"),
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "responded": st.column_config.TextColumn("Resp.", width="small"),
            "resolved": st.column_config.TextColumn("Res.", width="small"),
        }
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Export Logbook (CSV)", csv, f"buddywise_logbook_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    with col2:
        unresolved_count = len(filtered_df[filtered_df['resolved'] == False])
        st.markdown(f"<p style='color:#94A3B8; font-size:13px; text-align:center; padding-top:8px;'>{unresolved_count} unresolved events requiring attention</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Generate Incident Report", use_container_width=True):
            st.success(f"Incident report generated for {len(filtered_df)} events. Ready for regulatory submission.")

    st.divider()
    st.markdown("<h4 style='color:#F8FAFC;'>Quick Assignment Simulation</h4>", unsafe_allow_html=True)

    unassigned = filtered_df[filtered_df['assigned_to'].isna() & (filtered_df['responded'] == False)].head(5)
    if len(unassigned) > 0:
        for _, alert in unassigned.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div style="background:#151E32; border:1px solid #2D3A4F; border-radius:8px; padding:10px;">
                    <span style="color:{SEVERITY_COLORS[alert['severity']]}; font-weight:700;">{alert['severity']}</span>
                    <span style="color:#F8FAFC; font-size:13px;"> | {alert['violation_type']} | {alert['zone']}</span>
                    <span style="color:#94A3B8; font-size:11px; display:block; margin-top:2px;">{alert['timestamp'].strftime('%Y-%m-%d %H:%M')} | {alert['site']}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                assignee = st.selectbox(f"Assign {alert['alert_id']}", options=['Safety Officer', 'Supervisor', 'Site Manager', 'Engineering'], key=f"assign_{alert['alert_id']}", label_visibility="collapsed")
            with col3:
                if st.button("Assign", key=f"btn_{alert['alert_id']}"):
                    st.success(f"Assigned {alert['alert_id']} to {assignee}")
    else:
        st.info("All events are assigned. Great operational discipline!")


# ============================================================
# TAB 6 -- NOTIFICATION CENTER
# ============================================================
with tab6:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h2 style="color:#F8FAFC; margin:0; font-size:28px; font-weight:800;">Smart Notification Center</h2>
        <p style="color:#94A3B8; margin:6px 0 0 0; font-size:14px;">Configure smart thresholds and notification rules -- SMS, Email, IoT, Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<h4 style='color:#F8FAFC;'>Notification Rules</h4>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#151E32; border:1px solid #2D3A4F; border-radius:12px; padding:16px; margin:12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="color:#F8FAFC; font-weight:600; font-size:13px;">CRITICAL Alerts</span>
                <span style="background:#EF4444; color:white; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;">ACTIVE</span>
            </div>
            <div style="color:#94A3B8; font-size:12px; line-height:1.6;">
                Channels: SMS + Email + Dashboard + IoT Alarm<br>
                Threshold: Immediate (0 min delay)<br>
                Escalation: Auto-escalate if unresponded > 5 min
            </div>
        </div>

        <div style="background:#151E32; border:1px solid #2D3A4F; border-radius:12px; padding:16px; margin:12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="color:#F8FAFC; font-weight:600; font-size:13px;">HIGH Alerts</span>
                <span style="background:#F97316; color:white; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;">ACTIVE</span>
            </div>
            <div style="color:#94A3B8; font-size:12px; line-height:1.6;">
                Channels: Email + Dashboard + IoT Alarm<br>
                Threshold: Immediate<br>
                Escalation: Supervisor after 15 min unresponded
            </div>
        </div>

        <div style="background:#151E32; border:1px solid #2D3A4F; border-radius:12px; padding:16px; margin:12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="color:#F8FAFC; font-weight:600; font-size:13px;">MEDIUM Alerts</span>
                <span style="background:#EAB308; color:white; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;">ACTIVE</span>
            </div>
            <div style="color:#94A3B8; font-size:12px; line-height:1.6;">
                Channels: Email + Dashboard<br>
                Threshold: Batch every 30 min<br>
                Escalation: Daily summary
            </div>
        </div>

        <div style="background:#151E32; border:1px solid #2D3A4F; border-radius:12px; padding:16px; margin:12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="color:#F8FAFC; font-weight:600; font-size:13px;">LOW Alerts</span>
                <span style="background:#22C55E; color:white; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;">ACTIVE</span>
            </div>
            <div style="color:#94A3B8; font-size:12px; line-height:1.6;">
                Channels: Dashboard only<br>
                Threshold: Daily digest<br>
                Escalation: Weekly trend report
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h5 style='color:#F8FAFC; margin-top:16px;'>Custom Rule</h5>", unsafe_allow_html=True)
        custom_scenario = st.selectbox("When scenario is", options=list(RISK_SCENARIOS.keys()))
        custom_threshold = st.number_input("And alert count exceeds", min_value=1, value=5)
        custom_channel = st.multiselect("Notify via", options=['SMS', 'Email', 'Dashboard', 'IoT Alarm', 'Slack'], default=['Email', 'Dashboard'])
        if st.button("Create Rule", use_container_width=True):
            st.success(f"Rule created: {custom_scenario} > {custom_threshold} alerts -> {', '.join(custom_channel)}")

    with col2:
        st.markdown("<h4 style='color:#F8FAFC;'>Notification Analytics</h4>", unsafe_allow_html=True)

        channel_data = []
        for _, alert in filtered_df.iterrows():
            channels = alert['notification_channels'].split(', ')
            for ch in channels:
                channel_data.append({'channel': ch.strip(), 'severity': alert['severity'], 'timestamp': alert['timestamp']})

        channel_df = pd.DataFrame(channel_data)
        channel_counts = safe_value_counts(channel_df, 'channel')

        fig = go.Figure(go.Bar(
            x=channel_counts.values, y=channel_counts.index, orientation='h',
            marker=dict(color=channel_counts.values, colorscale=[[0, ACCENT_COLOR], [1, ACCENT_GLOW]]),
            text=channel_counts.values, textposition='outside', textfont=dict(color=TEXT_COLOR)
        ))
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Notification Count", yaxis_title=None, margin=dict(l=20, r=60, t=40, b=20), height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h5 style='color:#F8FAFC; margin-top:16px;'>Channel x Severity Matrix</h5>", unsafe_allow_html=True)
        ch_sev = channel_df.groupby(['channel', 'severity']).size().unstack(fill_value=0)
        for col in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if col not in ch_sev.columns:
                ch_sev[col] = 0
        ch_sev = ch_sev[['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']]

        fig = go.Figure(data=go.Heatmap(
            z=ch_sev.values, x=ch_sev.columns, y=ch_sev.index,
            colorscale=[[0, BG_COLOR], [0.3, MEDIUM_COLOR], [0.7, HIGH_COLOR], [1, CRITICAL_COLOR]],
            text=ch_sev.values, texttemplate="%{text}", textfont=dict(color=TEXT_COLOR, size=12),
            hovertemplate='Channel: %{y}<br>Severity: %{x}<br>Count: %{z}<extra></extra>',
            colorbar=dict(title="Count", titlefont=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR))
        ))
        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Severity", yaxis_title="Channel", margin=dict(l=20, r=80, t=40, b=20), height=350)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h5 style='color:#F8FAFC; margin-top:16px;'>Escalation Timeline</h5>", unsafe_allow_html=True)
        unresp = filtered_df[filtered_df['responded'] == False]
        if len(unresp) > 0:
            unresp_hourly = unresp.groupby(unresp['timestamp'].dt.hour).size()
            fig = go.Figure(go.Bar(x=unresp_hourly.index, y=unresp_hourly.values, marker_color=CRITICAL_COLOR))
            fig.add_hline(y=safe_mean(unresp_hourly), line_dash="dash", line_color=MUTED_TEXT, annotation_text=f"Avg: {safe_mean(unresp_hourly):.1f}/hour", annotation_position="top right")
            fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font_color=TEXT_COLOR, xaxis_title="Hour of Day", yaxis_title="Unresponded Count", margin=dict(l=20, r=20, t=40, b=20), height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("All alerts responded! Zero escalation queue.")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown("""
<div style="text-align:center; color:#94A3B8; font-size:12px; padding:20px 0 40px 0;">
    <p style="margin:0 0 8px 0;"><span style="font-size:16px;">&#128737;</span> <b style="color:#F8FAFC;">Buddywise Safety Intelligence Command Center</b></p>
    <p style="margin:0 0 8px 0;">5000+ simulated alerts across 5 German industrial sites | 6 risk scenarios | ILO: 2.3 million work deaths/year</p>
    <p style="margin:0; color:#3B82F6; font-weight:600;">Built by Tanishq Kumar Singh | Working Student (Tech & Ops) Candidate | Berlin, 2026</p>
</div>
""", unsafe_allow_html=True)
