import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random
import os

# ---------- CONFIG ----------
st.set_page_config(
    page_title="M'Flow",
    page_icon="🌊",
    layout="wide"
)

# ---------- LOGO ----------
LOGO_PATH = "Capture d’écran 2026-04-24 à 11.18.59 2.png"

# ---------- COLORS ----------
BLUE = "#0077B6"
LIGHT_BLUE = "#4DB6E2"
ORANGE = "#F59E0B"
DARK = "#003B5C"
BG = "#FFF8ED"

# ---------- STYLE ----------
st.markdown(f"""
<style>
.stApp {{
    background: {BG};
}}

h1, h2, h3 {{
    color: {DARK};
}}

.sidebar .sidebar-content {{
    background: {BLUE};
}}

.kpi {{
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 2px solid {LIGHT_BLUE};
    text-align: center;
}}

.intro {{
    background: white;
    padding: 20px;
    border-left: 5px solid {ORANGE};
    border-radius: 12px;
}}
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
sites = {
    "En-Vau": 80,
    "Port-Pin": 65,
    "Morgiou": 55,
    "Sormiou": 70,
    "Sugiton": 60,
    "Marseilleveyre": 40,
    "Podestat": 30,
    "Devenson": 25
}

# ---------- SIDEBAR ----------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=140)

    st.markdown("## M'Flow")

    month = st.selectbox("Month", ["April","May","June","July","August"])
    day = st.selectbox("Day", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
    hour = st.slider("Hour", 6, 20, 12)

    weather = st.selectbox("Weather", ["Sunny","Cloudy","Windy"])

# ---------- HEADER ----------
col1, col2 = st.columns([1,5])

with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)

with col2:
    st.title("M'Flow")
    st.markdown("""
    <div class="intro">
    <b>All the infos you need in one place.</b><br><br>
    M'Flow provides real-time data including current date, weather and crowd predictions to help you choose the best calanque.
    </div>
    """, unsafe_allow_html=True)

# ---------- CALCUL ----------
densities = {k: min(100, v + random.randint(-10,10)) for k,v in sites.items()}

avg = int(np.mean(list(densities.values())))
max_site = max(densities, key=densities.get)
min_site = min(densities, key=densities.get)

# ---------- KPI ----------
c1,c2,c3 = st.columns(3)

with c1:
    st.markdown(f"<div class='kpi'><h2>{avg}%</h2>Average density</div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"<div class='kpi'><h2>{densities[max_site]}%</h2>Busiest: {max_site}</div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"<div class='kpi'><h2>{densities[min_site]}%</h2>Best choice: {min_site}</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------- MAP ----------
st.subheader("Density Map")

names = list(densities.keys())
values = list(densities.values())

fig = go.Figure(data=go.Bar(
    x=names,
    y=values,
    marker_color=values,
))

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# ---------- FOOTER ----------
st.markdown("---")
st.caption(f"Live data updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
