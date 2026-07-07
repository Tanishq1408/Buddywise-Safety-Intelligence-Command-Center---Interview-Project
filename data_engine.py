"""
Buddywise Safety Intelligence Command Center
Enhanced Data Engine with Real-World Scenario Modeling

Maps directly to Buddywise product features:
- PPE Detection, Housekeeping, Area Control, Vehicle Control, Person Down, Crane Safety
- Zone-based configuration, camera-agnostic alerts, shift-aware analytics
"""

import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta, time
import random

faker = Faker('de_DE')

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# ─── BUDDYWISE PRODUCT MAPPING ───────────────────────────────────────────────
# These map 1:1 to their website's "Scenarios" page

RISK_SCENARIOS = {
    'PPE': {
        'violations': ['Missing Hard Hat', 'Missing Vest', 'Missing Goggles', 
                       'Missing Gloves', 'Missing Steel-Toe Boots', 'No Safety Harness'],
        'severity_base': {'Missing Hard Hat': 'HIGH', 'Missing Vest': 'MEDIUM',
                         'Missing Goggles': 'MEDIUM', 'Missing Gloves': 'LOW',
                         'Missing Steel-Toe Boots': 'MEDIUM', 'No Safety Harness': 'CRITICAL'},
        'zones': ['Assembly Line', 'Welding Bay', 'Construction Zone', 'Crane Zone', 'Scaffold Area'],
        'description': 'Personal Protection Equipment compliance monitoring'
    },
    'Housekeeping': {
        'violations': ['Obstruction in Walkway', 'Fire Exit Blocked', 'Spill Not Cleaned',
                       'Improper Material Storage', 'Trailing Cables'],
        'severity_base': {'Obstruction in Walkway': 'MEDIUM', 'Fire Exit Blocked': 'CRITICAL',
                         'Spill Not Cleaned': 'HIGH', 'Improper Material Storage': 'MEDIUM',
                         'Trailing Cables': 'HIGH'},
        'zones': ['Loading Dock', 'Warehouse Floor', 'Corridor', 'Storage Area', 'Packaging'],
        'description': 'Poor housekeeping hazard detection'
    },
    'Area Control': {
        'violations': ['Unauthorised Zone Entry', 'Vehicle in Pedestrian Zone',
                       'Worker in Restricted Zone', 'LOTO Procedure Violation'],
        'severity_base': {'Unauthorised Zone Entry': 'HIGH', 'Vehicle in Pedestrian Zone': 'CRITICAL',
                         'Worker in Restricted Zone': 'HIGH', 'LOTO Procedure Violation': 'CRITICAL'},
        'zones': ['Reactor Hall', 'Restricted Area', 'Crane Zone', 'High-Voltage Room', 'Chemical Storage'],
        'description': 'Restricted area and LOTO compliance monitoring'
    },
    'Vehicle Control': {
        'violations': ['Forklift Near-Miss', 'Forklift in Walkway', 'Pedestrian in Driveway',
                       'Vehicle Speeding', 'Unsafe Vehicle Proximity'],
        'severity_base': {'Forklift Near-Miss': 'CRITICAL', 'Forklift in Walkway': 'HIGH',
                         'Pedestrian in Driveway': 'HIGH', 'Vehicle Speeding': 'MEDIUM',
                         'Unsafe Vehicle Proximity': 'CRITICAL'},
        'zones': ['Loading Dock', 'Warehouse Floor', 'Truck Bay', 'Material Yard', 'Cross-Dock'],
        'description': 'Forklift and vehicle safety monitoring'
    },
    'Person Down': {
        'violations': ['Person Down - No Movement', 'Lone Worker Unresponsive',
                       'Person Down - Partial Movement', 'Worker Collapsed'],
        'severity_base': {'Person Down - No Movement': 'CRITICAL', 'Lone Worker Unresponsive': 'CRITICAL',
                         'Person Down - Partial Movement': 'HIGH', 'Worker Collapsed': 'CRITICAL'},
        'zones': ['Large Hall', 'Remote Area', 'Night Shift Floor', 'Isolation Zone', 'Storage Racks'],
        'description': 'Lone worker and person-down detection'
    },
    'Crane Safety': {
        'violations': ['Suspended Load Over Personnel', 'Crane Hook Near Worker',
                       'Load Swing Danger Zone', 'Crane Operation Without Spotter'],
        'severity_base': {'Suspended Load Over Personnel': 'CRITICAL', 'Crane Hook Near Worker': 'CRITICAL',
                         'Load Swing Danger Zone': 'HIGH', 'Crane Operation Without Spotter': 'HIGH'},
        'zones': ['Crane Zone', 'Drop Zone', 'Steel Erection', 'Foundation Pit', 'Material Yard'],
        'description': 'Dynamic suspended load and drop zone monitoring'
    }
}

# ─── SITE CONFIGURATION (Buddywise has offices in Stockholm + Berlin) ───────
SITES = {
    'Hamburg Manufacturing Plant': {
        'cameras': 12,
        'scenarios': ['PPE', 'Housekeeping', 'Area Control', 'Vehicle Control', 'Crane Safety'],
        'zones': ['Assembly Line A', 'Assembly Line B', 'Welding Bay', 'Paint Shop', 
                 'Quality Control', 'Packaging', 'Loading Dock', 'Crane Zone'],
        'industry': 'Manufacturing',
        'shift_pattern': '3-shift',
        'risk_profile': 'medium'
    },
    'Berlin Logistics Hub': {
        'cameras': 8,
        'scenarios': ['PPE', 'Housekeeping', 'Area Control', 'Vehicle Control'],
        'zones': ['Loading Dock', 'Cold Storage', 'Sorting Area', 'Truck Bay', 
                 'Returns Zone', 'Mezzanine', 'Warehouse Floor', 'Cross-Dock'],
        'industry': 'Logistics',
        'shift_pattern': '2-shift',
        'risk_profile': 'high'
    },
    'Cologne Chemical Works': {
        'cameras': 15,
        'scenarios': ['PPE', 'Area Control', 'Person Down', 'Housekeeping'],
        'zones': ['Reactor Hall', 'Mixing Station', 'Storage Tanks', 'Lab Building', 
                 'Waste Treatment', 'Loading Ramp', 'Restricted Area', 'Chemical Storage'],
        'industry': 'Chemical',
        'shift_pattern': '3-shift',
        'risk_profile': 'critical'
    },
    'Munich Construction Site': {
        'cameras': 10,
        'scenarios': ['PPE', 'Area Control', 'Crane Safety', 'Person Down', 'Vehicle Control'],
        'zones': ['Crane Zone', 'Scaffold Area', 'Foundation Pit', 'Steel Erection', 
                 'Concrete Pour', 'Material Yard', 'Drop Zone', 'High-Voltage Room'],
        'industry': 'Construction',
        'shift_pattern': 'day-only',
        'risk_profile': 'critical'
    },
    'Dortmund Warehouse': {
        'cameras': 6,
        'scenarios': ['PPE', 'Housekeeping', 'Vehicle Control', 'Area Control'],
        'zones': ['High-Bay Storage', 'Pick & Pack', 'Receiving', 'Shipping', 
                 'Cross-Dock', 'Maintenance', 'Warehouse Floor', 'Truck Bay'],
        'industry': 'Logistics',
        'shift_pattern': '2-shift',
        'risk_profile': 'medium'
    }
}

DEPARTMENTS = ['Production', 'Logistics', 'Maintenance', 'Quality Assurance', 
               'Operations', 'Safety', 'Engineering', 'Management']
SHIFTS = ['Morning (06:00-14:00)', 'Afternoon (14:00-22:00)', 'Night (22:00-06:00)']
SHIFT_WEIGHTS = [0.40, 0.35, 0.25]

HIGH_RISK_ZONES = ['Reactor Hall', 'Crane Zone', 'Scaffold Area', 'Drop Zone', 
                   'Restricted Area', 'Chemical Storage', 'High-Voltage Room']

# ─── WORKER GENERATION ────────────────────────────────────────────────────────
def generate_workers(n=60):
    """Generate worker profiles with realistic tenure and training distributions"""
    workers = []
    for i in range(n):
        dept = random.choice(DEPARTMENTS)
        # Skew toward newer workers (higher risk)
        tenure = np.random.gamma(2, 1.5) + 0.3
        tenure = min(tenure, 20)

        # Training correlates with tenure and department
        training_prob = 0.85 if tenure > 2 else 0.60
        if dept in ['Safety', 'Management']:
            training_prob = 0.95

        workers.append({
            'worker_id': f'W{i+1:03d}',
            'name': faker.name(),
            'department': dept,
            'tenure_years': round(tenure, 1),
            'training_completed': random.random() < training_prob,
            'training_date': (datetime(2025, 1, 1) - timedelta(days=random.randint(30, 500))).strftime('%Y-%m-%d') if random.random() < training_prob else None,
            'certifications': random.sample(['PPE Basics', 'LOTO', 'Forklift', 'Crane Safety', 'Chemical Handling'], 
                                          k=random.randint(0, 3)),
            'is_lone_worker': random.random() < 0.15
        })
    return pd.DataFrame(workers)


# ─── ALERT GENERATION WITH SCENARIO-AWARE LOGIC ───────────────────────────────
def generate_alerts(n=5000, workers_df=None):
    """Generate alerts mapped to Buddywise's 6 risk scenarios"""
    if workers_df is None:
        workers_df = generate_workers()

    alerts = []
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    date_range = (end_date - start_date).days
    worker_list = workers_df.to_dict('records')

    for i in range(n):
        # Site selection with risk weighting
        site_names = list(SITES.keys())
        site_weights = [1.5 if SITES[s]['risk_profile'] == 'critical' else 
                       1.2 if SITES[s]['risk_profile'] == 'high' else 1.0 
                       for s in site_names]
        site = random.choices(site_names, weights=site_weights, k=1)[0]
        site_config = SITES[site]

        # Scenario selection based on site capabilities
        scenario_key = random.choice(site_config['scenarios'])
        scenario = RISK_SCENARIOS[scenario_key]

        # Zone selection (must match scenario's relevant zones)
        zone = random.choice([z for z in site_config['zones'] if any(rz in z for rz in scenario['zones']) 
                              or random.random() < 0.3])

        # Violation from scenario
        violation = random.choice(scenario['violations'])
        base_severity = scenario['severity_base'][violation]

        # Adjust severity based on contextual factors
        severity = base_severity

        # Timestamp with realistic patterns
        days_offset = random.randint(0, date_range)
        base_date = start_date + timedelta(days=days_offset)

        # Working hours bias + shift patterns
        if random.random() < 0.80:
            if site_config['shift_pattern'] == 'day-only':
                hour = random.randint(7, 18)
            else:
                hour = random.randint(6, 21)
        else:
            hour = random.choice([0, 1, 2, 3, 4, 5, 22, 23])

        minute = random.randint(0, 59)
        timestamp = base_date.replace(hour=hour, minute=minute, second=random.randint(0, 59))

        # Shift determination
        if 6 <= hour < 14:
            shift = SHIFTS[0]
        elif 14 <= hour < 22:
            shift = SHIFTS[1]
        else:
            shift = SHIFTS[2]

        # Worker selection with risk correlation
        worker = random.choice(worker_list)
        worker_id = worker['worker_id']

        # Untrained workers generate more alerts
        if not worker['training_completed'] and random.random() < 0.4:
            severity = escalate_severity(severity)

        # Night shift escalation
        if shift == SHIFTS[2] and random.random() < 0.3:
            severity = escalate_severity(severity)

        # High-risk zone escalation
        if zone in HIGH_RISK_ZONES and random.random() < 0.25:
            severity = escalate_severity(severity)

        # Response time logic
        response_time = calculate_response_time(severity, shift, zone, timestamp)
        responded = determine_response(severity, shift)

        # False positive (AI model quality indicator)
        is_false_positive = random.random() < 0.06  # 6% FP rate (Buddywise targets <5%)

        # Resolution
        resolved = responded and (random.random() > 0.12 if severity == 'CRITICAL' else random.random() > 0.08)

        # Camera ID (Buddywise is camera-agnostic)
        camera_id = f"CAM-{site[:3].upper()}-{random.randint(1, site_config['cameras']):02d}"

        # Notification channels (Buddywise feature)
        notification_channels = determine_notifications(severity, responded)

        alerts.append({
            'alert_id': f'ALT-{i+1:05d}',
            'timestamp': timestamp,
            'site': site,
            'zone': zone,
            'camera_id': camera_id,
            'scenario_type': scenario_key,
            'violation_type': violation,
            'severity': severity,
            'shift': shift,
            'worker_id': worker_id,
            'responded': responded,
            'response_time_mins': response_time if responded else None,
            'is_false_positive': is_false_positive,
            'resolved': resolved,
            'notification_channels': notification_channels,
            'assigned_to': random.choice(['Safety Officer', 'Supervisor', 'Site Manager', None]) if responded else None,
            'comments': random.choice(['', 'Investigated', 'Training recommended', 'Equipment checked', '']) if resolved else ''
        })

    return pd.DataFrame(alerts)


def escalate_severity(current):
    """Escalate severity by one level"""
    order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    idx = order.index(current)
    return order[min(idx + 1, len(order) - 1)]


def calculate_response_time(severity, shift, zone, timestamp):
    """Realistic response time based on multiple factors"""
    base = {'CRITICAL': 4, 'HIGH': 10, 'MEDIUM': 20, 'LOW': 40}[severity]

    # Night shift penalty
    if shift == SHIFTS[2]:
        base *= 1.5

    # Weekend penalty
    if timestamp.weekday() >= 5:
        base *= 1.3

    # High-risk zone priority (faster response)
    if zone in HIGH_RISK_ZONES:
        base *= 0.7

    # Add noise
    noise = np.random.exponential(base * 0.3)
    return max(1, round(base + noise, 1))


def determine_response(severity, shift):
    """Response probability based on severity and shift"""
    probs = {
        'CRITICAL': 0.96,
        'HIGH': 0.88,
        'MEDIUM': 0.75,
        'LOW': 0.55
    }
    base_prob = probs[severity]
    if shift == SHIFTS[2]:
        base_prob *= 0.92  # Slightly lower night response
    return random.random() < base_prob


def determine_notifications(severity, responded):
    """Buddywise notification channels"""
    channels = []
    if severity == 'CRITICAL':
        channels = ['SMS', 'Email', 'Dashboard', 'IoT Alarm']
    elif severity == 'HIGH':
        channels = ['Email', 'Dashboard', 'IoT Alarm']
    elif severity == 'MEDIUM':
        channels = ['Email', 'Dashboard']
    else:
        channels = ['Dashboard']

    if not responded:
        channels.append('Escalation SMS')

    return ', '.join(channels)


# ─── ANALYTICS FUNCTIONS ──────────────────────────────────────────────────────
def compute_zone_heatmaps(alerts_df):
    """Generate zone × severity heatmap data for each site"""
    heatmaps = {}
    for site in alerts_df['site'].unique():
        site_data = alerts_df[alerts_df['site'] == site]
        heatmap = site_data.groupby(['zone', 'severity']).size().unstack(fill_value=0)
        for col in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if col not in heatmap.columns:
                heatmap[col] = 0
        heatmaps[site] = heatmap[['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']]
    return heatmaps


def compute_worker_risk_scores(alerts_df, workers_df):
    """Enhanced risk scoring with scenario diversity weight"""
    risk_scores = []
    for _, worker in workers_df.iterrows():
        worker_alerts = alerts_df[alerts_df['worker_id'] == worker['worker_id']]
        total = len(worker_alerts)
        critical = len(worker_alerts[worker_alerts['severity'] == 'CRITICAL'])
        unique_violations = worker_alerts['violation_type'].nunique()
        unique_scenarios = worker_alerts['scenario_type'].nunique()

        # Weighted risk score
        score = (total * 1.0) + (critical * 4.0) + (unique_violations * 0.8) + (unique_scenarios * 1.5)
        risk_scores.append(score)

    workers_df = workers_df.copy()
    workers_df['risk_score'] = risk_scores
    workers_df['alert_count'] = [len(alerts_df[alerts_df['worker_id'] == w]) for w in workers_df['worker_id']]
    workers_df['critical_count'] = [len(alerts_df[(alerts_df['worker_id'] == w) & (alerts_df['severity'] == 'CRITICAL')]) for w in workers_df['worker_id']]
    return workers_df


def get_kpi_summary(alerts_df):
    """Executive KPI calculations"""
    total = len(alerts_df)
    critical = len(alerts_df[alerts_df['severity'] == 'CRITICAL'])
    unresponded_critical = len(alerts_df[(alerts_df['severity'] == 'CRITICAL') & (alerts_df['responded'] == False)])
    fp_rate = alerts_df['is_false_positive'].mean() * 100
    avg_response = alerts_df[alerts_df['responded'] == True]['response_time_mins'].mean()
    resolved = alerts_df['resolved'].sum()
    resolution_rate = (resolved / total * 100) if total > 0 else 0

    # Scenario breakdown
    scenario_counts = alerts_df['scenario_type'].value_counts().to_dict()

    return {
        'total_alerts': total,
        'critical_count': critical,
        'critical_pct': (critical / total * 100) if total > 0 else 0,
        'unresponded_critical': unresponded_critical,
        'fp_rate': fp_rate,
        'avg_response_time': avg_response,
        'resolution_rate': resolution_rate,
        'scenario_breakdown': scenario_counts
    }


if __name__ == '__main__':
    workers = generate_workers(60)
    alerts = generate_alerts(5000, workers)
    workers = compute_worker_risk_scores(alerts, workers)
    kpis = get_kpi_summary(alerts)
    heatmaps = compute_zone_heatmaps(alerts)

    print(f"Generated {len(alerts)} alerts across {len(SITES)} sites")
    print(f"Critical alerts: {kpis['critical_count']} ({kpis['critical_pct']:.1f}%)")
    print(f"False positive rate: {kpis['fp_rate']:.2f}%")
    print(f"Unresponded critical: {kpis['unresponded_critical']}")
    print(f"Resolution rate: {kpis['resolution_rate']:.1f}%")
    print(f"\nTop scenarios: {kpis['scenario_breakdown']}")
    print(f"\nZone heatmaps computed for {len(heatmaps)} sites")
