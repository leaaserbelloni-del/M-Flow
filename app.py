import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import urllib.request
import json

st.set_page_config(
    page_title="Calanques Flow - Marseille",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 50%, #0a1628 100%);
    color: #e8f4f8;
}
h1, h2, h3, p, label {
    color: #e8f4f8 !important;
}
section[data-testid="stSidebar"] {
    background: #07182f;
}
.kpi-card {
    background: #132848;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #00c9a7;
}
.kpi-label {
    font-size: 0.8rem;
    color: #9bb6c9;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.intro-box {
    background: #132848;
    border-left: 4px solid #00c9a7;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 20px;
}
.alert-box {
    background: #132848;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 14px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

CALANQUES = {
    "Calanque d'En-Vau": {"lat": 43.1988, "lon": 5.5012, "capacity": 500, "trail_km": 3.2, "type": "Iconic"},
    "Calanque de Port-Pin": {"lat": 43.2058, "lon": 5.4908, "capacity": 350, "trail_km": 2.5, "type": "Family-friendly"},
    "Calanque de Morgiou": {"lat": 43.2173, "lon": 5.4431, "capacity": 400, "trail_km": 4.1, "type": "Wild"},
    "Calanque de Sormiou": {"lat": 43.2142, "lon": 5.4244, "capacity": 450, "trail_km": 3.8, "type": "Popular"},
    "Calanque de Sugiton": {"lat": 43.2121, "lon": 5.4534, "capacity": 300, "trail_km": 1.8, "type": "Hiking"},
    "Calanque de Marseilleveyre": {"lat": 43.2050, "lon": 5.3500, "capacity": 250, "trail_km": 5.5, "type": "Remote"},
    "Calanque de Podestat": {"lat": 43.2130, "lon": 5.4300, "capacity": 200, "trail_km": 4.8, "type": "Hidden"},
    "Calanque de Devenson": {"lat": 43.2000, "lon": 5.5100, "capacity": 180, "trail_km": 6.0, "type": "Adventure"},
}

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOURS = list(range(6, 21))

HOUR_PATTERN = {
    6: 5, 7: 8, 8: 15, 9: 28, 10: 55, 11: 75, 12: 80,
    13: 78, 14: 82, 15: 85, 16: 72, 17: 55, 18: 35, 19: 20, 20: 10
}

MONTH_FACTOR = {
    0: .3, 1: .3, 2: .4, 3: .55, 4: .7, 5: .85,
    6: 1.0, 7: 1.0, 8: .8, 9: .6, 10: .35, 11: .3
}

DAY_FACTOR = {
    0: .7, 1: .65, 2: .65, 3: .7, 4: .85, 5: 1.0, 6: 1.0
}

SITE_FACTOR = {
    "Calanque d'En-Vau": 1.0,
    "Calanque de Port-Pin": 0.8,
    "Calanque de Morgiou": 0.75,
    "Calanque de Sormiou": 0.9,
    "Calanque de Sugiton": 0.85,
    "Calanque de Marseilleveyre": 0.45,
    "Calanque de Podestat": 0.35,
    "Calanque de Devenson": 0.25,
}

def get_live_weather():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=43.2965&longitude=5.3698"
            "&current=temperature_2m,weather_code,wind_speed_10m"
        )
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            current = data["current"]
            return {
                "temperature": current["temperature_2m"],
                "wind": current["wind_speed_10m"],
                "code": current["weather_code"],
                "time": current["time"],
            }
    except Exception:
        return None

def weather_label(code):
    if code == 0:
        return "Sunny"
    if code in [1, 2, 3]:
        return "Partly cloudy"
    if code in [45, 48]:
        return "Foggy"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Rainy"
    if code in [95, 96, 99]:
        return "Stormy"
    return "Cloudy"

def weather_factor(label, wind):
    factor = 1.0
    if label == "Sunny":
        factor = 1.15
    elif label == "Partly cloudy":
        factor = 1.0
    elif label == "Cloudy":
        factor = 0.85
    elif label in ["Rainy", "Stormy"]:
        factor = 0.35
    elif label == "Foggy":
        factor = 0.6

    if wind >= 45:
        factor *= 0.45
    elif wind >= 30:
        factor *= 0.7

    return factor

def density_pct(site, month_idx, day_idx, hour, wf=1.0, noise=True):
    base = (
        HOUR_PATTERN.get(hour, 20)
        * MONTH_FACTOR[month_idx]
        * DAY_FACTOR[day_idx]
        * SITE_FACTOR[site]
        * wf
    )

    if noise:
        base *= random.uniform(0.9, 1.1)

    return min(100, max(0, base))

def crowd_label(pct):
    if pct < 35:
        return "Low", "🟢"
    if pct < 65:
        return "Moderate", "🟡"
    if pct < 85:
        return "High", "🟠"
    return "Critical", "🔴"

live_weather = get_live_weather()
now = datetime.now()

if live_weather:
    live_weather_name = weather_label(live_weather["code"])
    live_temp = live_weather["temperature"]
    live_wind = live_weather["wind"]
    wf = weather_factor(live_weather_name, live_wind)
else:
    live_weather_name = "Partly cloudy"
    live_temp = "N/A"
    live_wind = 0
    wf = 1.0

with st.sidebar:
    st.markdown("# 🌊 FLOW")
    st.markdown("### MARSEILLE · CROWD FORECAST")
    st.markdown("---")

    st.markdown("### ⚙️ Real-time settings")

    month_idx = st.selectbox(
        "📅 Month",
        range(12),
        index=now.month - 1,
        format_func=lambda i: MONTHS[i],
    )

    day_idx = st.selectbox(
        "📆 Day",
        range(7),
        index=now.weekday(),
        format_func=lambda i: DAYS[i],
    )

    hour = st.select_slider(
        "🕐 Hour",
        options=HOURS,
        value=min(HOURS, key=lambda h: abs(h - now.hour)),
    )

    st.markdown("---")
    st.markdown("### 🌤 Live weather")
    st.write(f"Weather: **{live_weather_name}**")
    st.write(f"Temperature: **{live_temp}°C**")
    st.write(f"Wind: **{live_wind} km/h**")

    st.markdown("---")
    profile = st.selectbox(
        "👤 User profile",
        ["Tourist", "Local resident", "Public authority", "Tourism office", "Environmental agency"],
    )

    st.markdown("---")
    if st.button("🔄 Refresh live data"):
        st.rerun()

densities = {
    site: density_pct(site, month_idx, day_idx, hour, wf)
    for site in CALANQUES
}

avg_density = np.mean(list(densities.values()))
max_site = max(densities, key=densities.get)
min_site = min(densities, key=densities.get)
critical_count = sum(1 for value in densities.values() if value >= 85)

st.markdown("# 🌊 Calanques Flow")
st.markdown("""
<div class="intro-box">
    <h3>All the infos you need in one place.</h3>
    <p>
    Calanques Flow gives you real-time data including current date, live weather,
    estimated crowd levels and smart recommendations to help you choose the best calanque to visit.
    </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_density:.0f}%</div>
        <div class="kpi-label">Average crowd density</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    label, emoji = crowd_label(densities[max_site])
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{densities[max_site]:.0f}%</div>
        <div class="kpi-label">Busiest site<br>{max_site}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{densities[min_site]:.0f}%</div>
        <div class="kpi-label">Best alternative<br>{min_site}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{critical_count}</div>
        <div class="kpi-label">Critical alerts</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Density map",
    "📈 48h forecast",
    "💡 Recommendations",
    "🚨 Alerts & reports"
])

with tab1:
    st.subheader("🗺️ Real-time density map")

    names = list(CALANQUES.keys())
    lats = [CALANQUES[s]["lat"] for s in names]
    lons = [CALANQUES[s]["lon"] for s in names]
    pcts = [densities[s] for s in names]
    labels = [crowd_label(p)[0] for p in pcts]

    fig_map = go.Figure()

    fig_map.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode="markers+text",
        marker=dict(
            size=[18 + p / 3 for p in pcts],
            color=pcts,
            colorscale=[
                [0, "#00c9a7"],
                [0.35, "#ffd166"],
                [0.65, "#ff9500"],
                [1, "#ff2244"],
            ],
            cmin=0,
            cmax=100,
            opacity=0.9,
            showscale=True,
            colorbar=dict(title="Density %"),
        ),
        text=[f"{p:.0f}%" for p in pcts],
        textposition="top center",
        customdata=list(zip(names, pcts, labels)),
        hovertemplate="<b>%{customdata[0]}</b><br>Density: %{customdata[1]:.0f}%<br>Status: %{customdata[2]}<extra></extra>",
    ))

    fig_map.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=43.208, lon=5.46),
            zoom=11.2,
        ),
        height=520,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0a1628",
        plot_bgcolor="#0a1628",
        font=dict(color="#e8f4f8"),
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("🕐 Hourly density by site")

    hm_data = []
    for site in names:
        row = []
        for h in HOURS:
            row.append(density_pct(site, month_idx, day_idx, h, wf, noise=False))
        hm_data.append(row)

    short_names = [
        s.replace("Calanque de ", "").replace("Calanque d'", "")
        for s in names
    ]

    fig_hm = go.Figure(data=go.Heatmap(
        z=hm_data,
        x=[f"{h}:00" for h in HOURS],
        y=short_names,
        colorscale=[
            [0, "#003d2a"],
            [0.35, "#00c9a7"],
            [0.6, "#ffd166"],
            [0.8, "#ff9500"],
            [1, "#ff2244"],
        ],
        zmin=0,
        zmax=100,
        text=[[f"{v:.0f}%" for v in row] for row in hm_data],
        texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.0f}%<extra></extra>",
        colorbar=dict(title="Density %"),
    ))

    fig_hm.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="#0f2040",
        plot_bgcolor="#0f2040",
        font=dict(color="#e8f4f8"),
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
    )

    st.plotly_chart(fig_hm, use_container_width=True)

with tab2:
    st.subheader("📈 48-hour crowd forecast")

    selected_sites = st.multiselect(
        "Choose calanques to compare",
        names,
        default=names[:4],
    )

    if selected_sites:
        timeline = [
            datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=i)
            for i in range(48)
        ]

        fig_fc = go.Figure()
        palette = ["#00c9a7", "#ffd166", "#ff6b35", "#a78bfa", "#60a5fa", "#34d399"]

        for i, site in enumerate(selected_sites):
            values = []
            for t in timeline:
                h = max(6, min(20, t.hour))
                d = t.weekday()
                values.append(density_pct(site, month_idx, d, h, wf, noise=True))

            fig_fc.add_trace(go.Scatter(
                x=timeline,
                y=values,
                mode="lines",
                name=site.replace("Calanque de ", "").replace("Calanque d'", ""),
                line=dict(color=palette[i % len(palette)], width=3),
                hovertemplate="%{x|%d/%m %H:%M}<br>Density: %{y:.0f}%<extra></extra>",
            ))

        fig_fc.add_hline(y=35, line_dash="dot", line_color="#ffd166", annotation_text="Moderate")
        fig_fc.add_hline(y=65, line_dash="dot", line_color="#ff9500", annotation_text="High")
        fig_fc.add_hline(y=85, line_dash="dot", line_color="#ff2244", annotation_text="Critical")

        fig_fc.update_layout(
            height=430,
            paper_bgcolor="#0f2040",
            plot_bgcolor="#0f2040",
            font=dict(color="#e8f4f8"),
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f", title="Density %", range=[0, 105]),
            hovermode="x unified",
        )

        st.plotly_chart(fig_fc, use_container_width=True)
    else:
        st.info("Please select at least one calanque.")

with tab3:
    st.subheader("💡 Smart recommendations")

    max_crowd = st.slider("Maximum crowd tolerance", 10, 100, 50, 5)
    max_trail = st.slider("Maximum walking distance in km", 1.0, 7.0, 4.0, 0.5)

    recommendations = []

    for site, info in CALANQUES.items():
        d = densities[site]
        if d <= max_crowd and info["trail_km"] <= max_trail:
            score = (100 - d) * 0.7 + (7 - info["trail_km"]) * 4
            recommendations.append((site, score))

    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    if not recommendations:
        st.warning("No calanque matches your filters. Try increasing your crowd tolerance or walking distance.")
    else:
        for rank, (site, score) in enumerate(recommendations[:5], start=1):
            info = CALANQUES[site]
            d = densities[site]
            label, emoji = crowd_label(d)

            st.markdown(f"""
            <div class="alert-box">
                <h4>{rank}. {site}</h4>
                <p>
                Status: <b>{emoji} {label}</b><br>
                Current density: <b>{d:.0f}%</b><br>
                Type: <b>{info["type"]}</b><br>
                Walking distance: <b>{info["trail_km"]} km</b><br>
                Recommendation score: <b>{score:.0f}/100</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.subheader("🚨 Active alerts")

    active_alerts = 0

    for site, pct in sorted(densities.items(), key=lambda x: x[1], reverse=True):
        label, emoji = crowd_label(pct)

        if pct >= 65:
            active_alerts += 1
            st.markdown(f"""
            <div class="alert-box">
                <h4>{emoji} {site}</h4>
                <p>
                Current density: <b>{pct:.0f}%</b><br>
                Status: <b>{label}</b><br>
                Recommendation: consider visiting another calanque or choosing a quieter time slot.
                </p>
            </div>
            """, unsafe_allow_html=True)

    if active_alerts == 0:
        st.success("No active alerts. Crowd levels are currently acceptable across all tracked calanques.")

    st.subheader("📋 Full summary")

    summary = []

    for site, info in CALANQUES.items():
        d = densities[site]
        label, emoji = crowd_label(d)
        visitors = int(d / 100 * info["capacity"])

        summary.append({
            "Site": site,
            "Status": f"{emoji} {label}",
            "Density": f"{d:.0f}%",
            "Estimated visitors": visitors,
            "Capacity": info["capacity"],
            "Walking distance": f"{info['trail_km']} km",
            "Type": info["type"],
        })

    df = pd.DataFrame(summary)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(
    f"Live update: {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"Weather source: Open-Meteo · Crowd density: predictive simulation based on season, time, weather and site popularity."
)
