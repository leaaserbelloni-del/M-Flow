import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Calanques Flow - Marseille",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* Dark teal theme */
:root {
    --bg: #0a1628;
    --surface: #0f2040;
    --card: #132848;
    --accent: #00c9a7;
    --accent2: #ff6b35;
    --accent3: #ffd166;
    --text: #e8f4f8;
    --muted: #7a9db8;
    --border: #1e3a5f;
}

.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 50%, #0a1628 100%);
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1f40 0%, #061428 100%);
    border-right: 1px solid #1e3a5f;
}

section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Cards */
.kpi-card {
    background: linear-gradient(135deg, #132848 0%, #0f2040 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    margin: 0;
}
.kpi-label {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
}
.kpi-delta {
    font-size: 0.8rem;
    margin-top: 6px;
}

/* Alert */
.alert-high {
    background: linear-gradient(135deg, #3d1515, #5c1f1f);
    border: 1px solid #cc3333;
    border-left: 4px solid #ff4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #ffaaaa;
}
.alert-medium {
    background: linear-gradient(135deg, #3d2e00, #5c4500);
    border: 1px solid #cc8800;
    border-left: 4px solid #ffd166;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #ffe599;
}
.alert-low {
    background: linear-gradient(135deg, #003d2a, #005c3e);
    border: 1px solid #00cc88;
    border-left: 4px solid #00c9a7;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #99ffe0;
}

/* Recommendation card */
.rec-card {
    background: #132848;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
    transition: border-color 0.2s;
}
.rec-card:hover { border-color: var(--accent); }
.rec-title { font-weight: 700; color: var(--accent); font-size: 1rem; }
.rec-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-low { background: #003d2a; color: #00c9a7; border: 1px solid #00c9a7; }
.badge-medium { background: #3d2e00; color: #ffd166; border: 1px solid #ffd166; }
.badge-high { background: #3d1515; color: #ff6b6b; border: 1px solid #ff6b6b; }

/* Header */
.main-header {
    background: linear-gradient(90deg, #0a1628, #0f2040, #0a1628);
    border-bottom: 1px solid #1e3a5f;
    padding: 16px 0 12px 0;
    margin-bottom: 24px;
}
.site-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -1px;
}
.site-subtitle {
    font-size: 0.8rem;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0f2040;
    border-radius: 8px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
}
.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: var(--accent) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00c9a7, #00a88a);
    color: #0a1628;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-size: 0.8rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00ddb8, #00c9a7);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(0,201,167,0.3);
}

/* Selectbox, slider */
.stSelectbox > div > div, .stSlider > div {
    background: #132848 !important;
    border-color: #1e3a5f !important;
    color: var(--text) !important;
}

/* Plotly charts dark */
.js-plotly-plot .plotly { border-radius: 12px; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a1628; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a5080; }

/* Divider */
hr { border-color: #1e3a5f; }

p, li, label { color: var(--text); }
h1, h2, h3 { color: var(--text); }
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
CALANQUES = {
    "Calanque d'En-Vau": {"lat": 43.1988, "lon": 5.5012, "capacity": 500, "trail_km": 3.2, "parking": 80,  "type": "Emblématique"},
    "Calanque de Port-Pin": {"lat": 43.2058, "lon": 5.4908, "capacity": 350, "trail_km": 2.5, "parking": 60,  "type": "Famille"},
    "Calanque de Morgiou": {"lat": 43.2173, "lon": 5.4431, "capacity": 400, "trail_km": 4.1, "parking": 100, "type": "Sauvage"},
    "Calanque de Sormiou": {"lat": 43.2142, "lon": 5.4244, "capacity": 450, "trail_km": 3.8, "parking": 120, "type": "Populaire"},
    "Calanque de Sugiton":  {"lat": 43.2121, "lon": 5.4534, "capacity": 300, "trail_km": 1.8, "parking": 50,  "type": "Randonnée"},
    "Calanque de Marseilleveyre": {"lat": 43.2050, "lon": 5.3500, "capacity": 250, "trail_km": 5.5, "parking": 40,  "type": "Isolée"},
    "Calanque de Podestat": {"lat": 43.2130, "lon": 5.4300, "capacity": 200, "trail_km": 4.8, "parking": 30,  "type": "Secrète"},
    "Calanque de Devenson": {"lat": 43.2000, "lon": 5.5100, "capacity": 180, "trail_km": 6.0, "parking": 20,  "type": "Aventure"},
}

MONTHS = ["Janvier","Février","Mars","Avril","Mai","Juin",
          "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
DAYS   = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
HOURS  = list(range(6, 21))

# Base density patterns
HOUR_PATTERN  = {6:5,7:8,8:15,9:28,10:55,11:75,12:80,13:78,14:82,15:85,16:72,17:55,18:35,19:20,20:10}
MONTH_FACTOR  = {0:.3,1:.3,2:.4,3:.55,4:.7,5:.85,6:1.0,7:1.0,8:.8,9:.6,10:.35,11:.3}
DAY_FACTOR    = {0:.7,1:.65,2:.65,3:.7,4:.85,5:1.0,6:1.0}
SITE_FACTOR   = {
    "Calanque d'En-Vau": 1.0,
    "Calanque de Port-Pin": 0.8,
    "Calanque de Morgiou": 0.75,
    "Calanque de Sormiou": 0.9,
    "Calanque de Sugiton":  0.85,
    "Calanque de Marseilleveyre": 0.45,
    "Calanque de Podestat": 0.35,
    "Calanque de Devenson": 0.25,
}

def density_pct(site, month_idx, day_idx, hour, weather_factor=1.0, noise=True):
    base = (HOUR_PATTERN.get(hour, 20)
            * MONTH_FACTOR[month_idx]
            * DAY_FACTOR[day_idx]
            * SITE_FACTOR[site]
            * weather_factor)
    if noise:
        base *= random.uniform(0.88, 1.12)
    return min(100, max(0, base))

def crowd_label(pct):
    if pct < 35:  return "Faible", "low"
    if pct < 65:  return "Modérée", "medium"
    if pct < 85:  return "Élevée", "high"
    return "Critique", "high"

def weather_factor(weather):
    return {"Ensoleillé":1.15, "Nuageux":0.85, "Vent fort (Mistral)":0.4, "Pluie":0.2, "Partiellement nuageux":1.0}[weather]

# ── Session state ──────────────────────────────────────────────────────────────
if "refresh" not in st.session_state:
    st.session_state.refresh = 0
    random.seed(42)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:10px 0 20px 0;'>
        <div class='site-title'>🌊 CALANQUES<br>FLOW</div>
        <div class='site-subtitle'>Marseille · Prévision foule</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**⚙️ Paramètres de simulation**")

    now = datetime.now()
    month_idx = st.selectbox("📅 Mois", range(12), index=now.month-1,
                              format_func=lambda i: MONTHS[i])
    day_idx = st.selectbox("📆 Jour de la semaine", range(7), index=now.weekday(),
                            format_func=lambda i: DAYS[i])
    hour = st.select_slider("🕐 Heure", options=HOURS, value=min(HOURS, key=lambda h: abs(h-now.hour)))
    weather = st.selectbox("🌤 Météo", ["Ensoleillé","Partiellement nuageux","Nuageux","Vent fort (Mistral)","Pluie"])
    wf = weather_factor(weather)

    st.markdown("---")
    profile = st.selectbox("👤 Profil utilisateur",
                            ["Touriste","Résident local","Autorité publique","Office du tourisme","Agence environnementale"])

    st.markdown("---")
    if st.button("🔄 Actualiser les données"):
        st.session_state.refresh += 1
        random.seed(st.session_state.refresh)

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.7rem;color:#7a9db8;'>Simulation locale · Données synthétiques<br>Profil : <b style='color:#00c9a7'>{profile}</b></div>", unsafe_allow_html=True)

# ── Compute current densities ──────────────────────────────────────────────────
densities = {
    site: density_pct(site, month_idx, day_idx, hour, wf)
    for site in CALANQUES
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='main-header'>
    <span class='site-title'>🌊 CALANQUES FLOW</span> &nbsp;
    <span class='site-subtitle'>· {DAYS[day_idx]} {MONTHS[month_idx]} · {hour}h00 · {weather}</span>
</div>
""", unsafe_allow_html=True)

# ── KPI row ────────────────────────────────────────────────────────────────────
avg_density   = np.mean(list(densities.values()))
max_site      = max(densities, key=densities.get)
min_site      = min(densities, key=densities.get)
critical_count = sum(1 for v in densities.values() if v >= 85)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-value'>{avg_density:.0f}%</div>
        <div class='kpi-label'>Densité moyenne</div>
        <div class='kpi-delta' style='color:#7a9db8'>8 calanques suivies</div>
    </div>""", unsafe_allow_html=True)
with c2:
    lbl, cls = crowd_label(densities[max_site])
    col = "#ff6b6b" if cls=="high" else "#ffd166"
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-value' style='color:{col};font-size:1.3rem'>{max_site.split(" de ")[-1]}</div>
        <div class='kpi-label'>Site le + fréquenté</div>
        <div class='kpi-delta' style='color:{col}'>{densities[max_site]:.0f}% · {lbl}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-value' style='color:#00c9a7;font-size:1.3rem'>{min_site.split(" de ")[-1]}</div>
        <div class='kpi-label'>Meilleure alternative</div>
        <div class='kpi-delta' style='color:#00c9a7'>{densities[min_site]:.0f}% · Faible affluence</div>
    </div>""", unsafe_allow_html=True)
with c4:
    alert_color = "#ff4444" if critical_count > 0 else "#00c9a7"
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-value' style='color:{alert_color}'>{critical_count}</div>
        <div class='kpi-label'>Sites en surcharge</div>
        <div class='kpi-delta' style='color:{alert_color}'>{'⚠️ Alertes actives' if critical_count > 0 else '✅ Situation normale'}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Carte densité", "📈 Prévisions 48h", "💡 Recommandations", "🚨 Alertes & Rapports"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_map, col_bar = st.columns([3, 1])

    with col_map:
        st.markdown("#### 🗺️ Carte temps réel des densités")

        # Build scatter mapbox
        lats  = [CALANQUES[s]["lat"] for s in CALANQUES]
        lons  = [CALANQUES[s]["lon"] for s in CALANQUES]
        names = list(CALANQUES.keys())
        pcts  = [densities[s] for s in CALANQUES]
        caps  = [CALANQUES[s]["capacity"] for s in CALANQUES]
        labels, classes = zip(*[crowd_label(p) for p in pcts])
        colors = ["#ff4444" if c=="high" and p>=85 else "#ffd166" if c in ("high","medium") and p>=35 else "#00c9a7"
                  for p, c in zip(pcts, classes)]
        sizes  = [12 + p/4 for p in pcts]

        hover = [f"<b>{n}</b><br>Densité : {p:.0f}%<br>Statut : {l}<br>Capacité max : {c} pers."
                 for n, p, l, c in zip(names, pcts, labels, caps)]

        fig_map = go.Figure()

        # Density circles (heatmap-like)
        fig_map.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode="markers",
            marker=dict(
                size=[s*2.5 for s in sizes],
                color=pcts,
                colorscale=[[0,"#00c9a7"],[0.35,"#ffd166"],[0.65,"#ff9500"],[1,"#ff2244"]],
                cmin=0, cmax=100,
                opacity=0.35,
                showscale=False,
            ),
            hoverinfo="skip",
            name="Halo densité"
        ))

        # Point markers
        fig_map.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode="markers+text",
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.95,
            ),
            text=[f"{p:.0f}%" for p in pcts],
            textfont=dict(size=9, color="white"),
            textposition="top center",
            customdata=list(zip(names, pcts, labels, caps)),
            hovertemplate="<b>%{customdata[0]}</b><br>Densité : %{customdata[1]:.0f}%<br>Statut : %{customdata[2]}<br>Capacité : %{customdata[3]} pers.<extra></extra>",
            name="Sites"
        ))

        fig_map.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=43.208, lon=5.46),
                zoom=11.5,
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=480,
            paper_bgcolor="#0a1628",
            plot_bgcolor="#0a1628",
            legend=dict(bgcolor="#132848", bordercolor="#1e3a5f"),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_bar:
        st.markdown("#### Classement")
        sorted_sites = sorted(densities.items(), key=lambda x: x[1], reverse=True)
        for site, pct in sorted_sites:
            lbl, cls = crowd_label(pct)
            badge_cls = f"badge-{cls}"
            short = site.replace("Calanque de ","").replace("Calanque d'","")
            bar_color = "#ff4444" if cls=="high" and pct>=85 else "#ffd166" if pct>=35 else "#00c9a7"
            st.markdown(f"""
            <div style='margin-bottom:12px'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px'>
                    <span style='font-size:0.8rem;font-weight:600'>{short}</span>
                    <span class='rec-badge {badge_cls}'>{lbl}</span>
                </div>
                <div style='background:#1e3a5f;border-radius:4px;height:8px;overflow:hidden'>
                    <div style='background:{bar_color};height:100%;width:{pct:.0f}%;border-radius:4px;transition:width 0.5s'></div>
                </div>
                <div style='font-size:0.7rem;color:#7a9db8;margin-top:2px'>{pct:.0f}% · {CALANQUES[site]["capacity"]} pers. max</div>
            </div>
            """, unsafe_allow_html=True)

    # Hourly heatmap
    st.markdown("---")
    st.markdown("#### 🕐 Densité horaire — tous sites (aujourd'hui)")

    hm_data = []
    for site in CALANQUES:
        row = []
        for h in HOURS:
            row.append(density_pct(site, month_idx, day_idx, h, wf, noise=False))
        hm_data.append(row)

    short_names = [s.replace("Calanque de ","").replace("Calanque d'","") for s in CALANQUES]
    fig_hm = go.Figure(go.Heatmap(
        z=hm_data,
        x=[f"{h}h" for h in HOURS],
        y=short_names,
        colorscale=[[0,"#003d2a"],[0.35,"#00c9a7"],[0.6,"#ffd166"],[0.8,"#ff9500"],[1,"#ff2244"]],
        zmin=0, zmax=100,
        text=[[f"{v:.0f}%" for v in row] for row in hm_data],
        texttemplate="%{text}",
        textfont=dict(size=9, color="white"),
        hovertemplate="<b>%{y}</b><br>%{x} → %{z:.0f}%<extra></extra>",
        showscale=True,
        colorbar=dict(
            title="Densité %",
            tickfont=dict(color="#7a9db8"),
            titlefont=dict(color="#7a9db8"),
            bgcolor="#132848",
            bordercolor="#1e3a5f",
        )
    ))
    # Mark current hour
    if hour in HOURS:
        fig_hm.add_vline(x=HOURS.index(hour), line=dict(color="#00c9a7", width=2, dash="dot"),
                         annotation_text="maintenant", annotation_font_color="#00c9a7")

    fig_hm.update_layout(
        paper_bgcolor="#0f2040",
        plot_bgcolor="#0f2040",
        font=dict(color="#e8f4f8"),
        xaxis=dict(side="top", gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
        height=310,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_hm, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FORECAST
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 📈 Prévisions 24–48h par calanque")

    col_sel, col_wth = st.columns([2, 1])
    with col_sel:
        selected_sites = st.multiselect(
            "Sélectionner les calanques à comparer",
            list(CALANQUES.keys()),
            default=list(CALANQUES.keys())[:4]
        )
    with col_wth:
        forecast_weather = st.selectbox("Météo prévue", ["Ensoleillé","Partiellement nuageux","Nuageux","Vent fort (Mistral)","Pluie"], key="fw")
        fwf = weather_factor(forecast_weather)

    if selected_sites:
        # Generate 48h timeline
        timeline = []
        for offset_h in range(48):
            t = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=offset_h)
            timeline.append(t)

        fig_fc = go.Figure()

        # Shade zones
        fig_fc.add_hrect(y0=0,  y1=35,  fillcolor="rgba(0,201,167,0.05)", line_width=0)
        fig_fc.add_hrect(y0=35, y1=65,  fillcolor="rgba(255,209,102,0.05)", line_width=0)
        fig_fc.add_hrect(y0=65, y1=85,  fillcolor="rgba(255,149,0,0.05)", line_width=0)
        fig_fc.add_hrect(y0=85, y1=100, fillcolor="rgba(255,34,68,0.07)", line_width=0)

        PALETTE = ["#00c9a7","#ffd166","#ff6b35","#a78bfa","#60a5fa","#fb923c","#34d399","#f472b6"]

        for i, site in enumerate(selected_sites):
            vals = []
            for t in timeline:
                h = t.hour
                d = t.weekday()
                wfactor = fwf if offset_h > 0 else wf
                v = density_pct(site, month_idx, d, max(6, min(20, h)), wfactor, noise=True)
                vals.append(v)

            # Confidence band (±10%)
            upper = [min(100, v+10) for v in vals]
            lower = [max(0,   v-10) for v in vals]

            color = PALETTE[i % len(PALETTE)]

            fig_fc.add_trace(go.Scatter(
                x=timeline+timeline[::-1],
                y=upper+lower[::-1],
                fill='toself',
                fillcolor=color.replace("#", "rgba(").rstrip(")") if False else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)",
                line=dict(width=0),
                showlegend=False, hoverinfo="skip"
            ))

            short = site.replace("Calanque de ","").replace("Calanque d'","")
            fig_fc.add_trace(go.Scatter(
                x=timeline,
                y=vals,
                name=short,
                line=dict(color=color, width=2.5, shape="spline"),
                mode="lines",
                hovertemplate=f"<b>{short}</b><br>%{{x|%d/%m %Hh}}<br>Densité : %{{y:.0f}}%<extra></extra>"
            ))

        # Now marker
        fig_fc.add_vline(x=datetime.now(), line=dict(color="#7a9db8", width=1.5, dash="dash"),
                         annotation_text="maintenant", annotation_font_color="#7a9db8")

        # Threshold lines
        for lvl, col, lbl in [(35,"#ffd166","Modéré"), (65,"#ff9500","Élevé"), (85,"#ff4444","Critique")]:
            fig_fc.add_hline(y=lvl, line=dict(color=col, width=1, dash="dot"),
                             annotation_text=lbl, annotation_font_color=col, annotation_position="right")

        fig_fc.update_layout(
            paper_bgcolor="#0f2040",
            plot_bgcolor="#0f2040",
            font=dict(color="#e8f4f8", family="Space Mono"),
            legend=dict(bgcolor="#132848", bordercolor="#1e3a5f", font=dict(size=11)),
            xaxis=dict(gridcolor="#1e3a5f", tickformat="%Hh\n%d/%m", title=""),
            yaxis=dict(gridcolor="#1e3a5f", title="Densité (%)", range=[0,105]),
            height=400,
            margin=dict(l=10, r=80, t=20, b=10),
            hovermode="x unified",
        )
        st.plotly_chart(fig_fc, use_container_width=True)

        # Peak hour table
        st.markdown("#### 📊 Pic de fréquentation prévu (24h)")
        peak_data = []
        for site in selected_sites:
            peaks = []
            for h in HOURS:
                v = density_pct(site, month_idx, day_idx, h, fwf, noise=False)
                peaks.append((h, v))
            peak_h, peak_v = max(peaks, key=lambda x: x[1])
            lbl, cls = crowd_label(peak_v)
            short = site.replace("Calanque de ","").replace("Calanque d'","")
            emoji = "🔴" if cls=="high" and peak_v>=85 else "🟡" if peak_v>=35 else "🟢"
            peak_data.append({
                "Calanque": short,
                "Heure de pointe": f"{peak_h}h00",
                "Densité max": f"{peak_v:.0f}%",
                "Statut": f"{emoji} {lbl}",
                "Capacité max": f"{CALANQUES[site]['capacity']} pers."
            })
        df_peak = pd.DataFrame(peak_data)
        st.dataframe(df_peak, use_container_width=True, hide_index=True)
    else:
        st.info("Sélectionnez au moins une calanque pour afficher les prévisions.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 💡 Recommandations personnalisées")

    col_r1, col_r2 = st.columns([1,2])
    with col_r1:
        pref_type = st.multiselect("Type de visite", ["Baignade","Randonnée","Snorkeling","Famille","Calme / méditation","Accessibilité facile"],
                                    default=["Baignade"])
        max_crowd = st.slider("Tolérance à la foule (max %)", 10, 100, 50, 5)
        max_trail = st.slider("Distance de marche max (km)", 1.0, 7.0, 4.0, 0.5)
    with col_r2:
        site_scores = {}
        for site, info in CALANQUES.items():
            d = densities[site]
            if d > max_crowd: continue
            if info["trail_km"] > max_trail: continue
            score = (100 - d) * 0.6 + (1 - info["trail_km"]/7) * 40
            site_scores[site] = score

        if not site_scores:
            st.warning("⚠️ Aucune calanque ne correspond à vos critères. Essayez d'assouplir vos filtres.")
        else:
            sorted_recs = sorted(site_scores.items(), key=lambda x: x[1], reverse=True)
            st.markdown(f"**{len(sorted_recs)} calanque(s) recommandée(s)**")

            for rank, (site, score) in enumerate(sorted_recs[:5], 1):
                info = CALANQUES[site]
                d = densities[site]
                lbl, cls = crowd_label(d)
                short = site.replace("Calanque de ","").replace("Calanque d'","")
                medal = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"#{rank}"
                color_d = "#ff4444" if cls=="high" and d>=85 else "#ffd166" if d>=35 else "#00c9a7"

                st.markdown(f"""
                <div class='rec-card'>
                    <div style='display:flex;justify-content:space-between;align-items:start'>
                        <div>
                            <div class='rec-title'>{medal} {short}</div>
                            <div style='font-size:0.75rem;color:#7a9db8;margin-top:2px'>{info["type"]} · {info["trail_km"]} km de marche · {info["parking"]} places parking</div>
                        </div>
                        <div style='text-align:right'>
                            <div style='font-family:Space Mono;font-size:1.3rem;color:{color_d};font-weight:700'>{d:.0f}%</div>
                            <span class='rec-badge badge-{cls}'>{lbl}</span>
                        </div>
                    </div>
                    <div style='margin-top:10px;background:#0f2040;border-radius:4px;height:6px;overflow:hidden'>
                        <div style='background:{color_d};height:100%;width:{d:.0f}%;border-radius:4px'></div>
                    </div>
                    <div style='font-size:0.75rem;color:#7a9db8;margin-top:6px'>
                        Score d'adéquation : <b style='color:#00c9a7'>{score:.0f}/100</b> · 
                        Capacité : {info["capacity"]} pers. · Coords : {info["lat"]:.4f}N {info["lon"]:.4f}E
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Best visit time
    st.markdown("---")
    st.markdown("#### ⏰ Meilleur moment de visite (aujourd'hui)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        site_bvt = st.selectbox("Site", list(CALANQUES.keys()), key="bvt")
    with col_t2:
        target_crowd = st.slider("Densité cible max", 10, 70, 40, 5, key="tc")

    hour_densities = {h: density_pct(site_bvt, month_idx, day_idx, h, wf, noise=False) for h in HOURS}
    good_hours = [h for h,v in hour_densities.items() if v <= target_crowd]

    fig_bvt = go.Figure()
    bar_colors = ["#00c9a7" if v<=target_crowd else "#ff6b35" if v<85 else "#ff2244"
                  for v in [hour_densities[h] for h in HOURS]]
    fig_bvt.add_trace(go.Bar(
        x=[f"{h}h" for h in HOURS],
        y=[hour_densities[h] for h in HOURS],
        marker_color=bar_colors,
        hovertemplate="%{x} → %{y:.0f}%<extra></extra>"
    ))
    fig_bvt.add_hline(y=target_crowd, line=dict(color="#ffd166", dash="dot", width=2),
                      annotation_text=f"Cible {target_crowd}%", annotation_font_color="#ffd166")
    if hour in HOURS:
        fig_bvt.add_vline(x=HOURS.index(hour), line=dict(color="#7a9db8", dash="dash", width=1.5),
                          annotation_text="maintenant", annotation_font_color="#7a9db8")
    fig_bvt.update_layout(
        paper_bgcolor="#0f2040", plot_bgcolor="#0f2040",
        font=dict(color="#e8f4f8"), xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f", range=[0,105]),
        height=250, margin=dict(l=10,r=10,t=10,b=10),
        bargap=0.3,
    )
    st.plotly_chart(fig_bvt, use_container_width=True)

    if good_hours:
        ranges = []
        start = good_hours[0]
        prev  = good_hours[0]
        for h in good_hours[1:]:
            if h == prev+1:
                prev = h
            else:
                ranges.append(f"{start}h–{prev}h")
                start = prev = h
        ranges.append(f"{start}h–{prev}h")
        st.markdown(f"""<div class='alert-low'>
            ✅ <b>Créneaux recommandés :</b> {' · '.join(ranges)}<br>
            <span style='font-size:0.8rem'>Densité prévue &lt; {target_crowd}% — conditions optimales</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class='alert-high'>
            ❌ <b>Aucun créneau optimal aujourd'hui</b> pour une densité &lt; {target_crowd}%<br>
            <span style='font-size:0.8rem'>Essayez un autre jour ou augmentez votre tolérance</span>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ALERTS & REPORTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 🚨 Alertes actives")

    alert_count = 0
    for site, pct in sorted(densities.items(), key=lambda x: x[1], reverse=True):
        lbl, cls = crowd_label(pct)
        short = site.replace("Calanque de ","").replace("Calanque d'","")
        if pct >= 85:
            st.markdown(f"""<div class='alert-high'>
                🔴 <b>ALERTE CRITIQUE — {short}</b> : {pct:.0f}% de capacité<br>
                <span style='font-size:0.8rem'>Risque de surpopulation · Accès potentiellement limité · Recommandez des alternatives</span>
            </div>""", unsafe_allow_html=True)
            alert_count += 1
        elif pct >= 65:
            st.markdown(f"""<div class='alert-medium'>
                🟡 <b>AFFLUENCE ÉLEVÉE — {short}</b> : {pct:.0f}% de capacité<br>
                <span style='font-size:0.8rem'>Forte fréquentation · Temps d'attente possible · Anticipez votre visite</span>
            </div>""", unsafe_allow_html=True)
            alert_count += 1

    if alert_count == 0:
        st.markdown("""<div class='alert-low'>
            ✅ <b>Aucune alerte active</b> — Situation normale sur l'ensemble des calanques<br>
            <span style='font-size:0.8rem'>Densités dans les limites acceptables pour toutes les zones</span>
        </div>""", unsafe_allow_html=True)

    # Seasonal report
    st.markdown("---")
    st.markdown("#### 📊 Rapport saisonnier — Affluence par mois")

    monthly_avg = []
    for m in range(12):
        vals = [density_pct(s, m, 5, 13, 1.0, noise=False) for s in CALANQUES]
        monthly_avg.append(np.mean(vals))

    fig_seas = go.Figure()
    fig_seas.add_trace(go.Bar(
        x=MONTHS, y=monthly_avg,
        marker=dict(
            color=monthly_avg,
            colorscale=[[0,"#003d2a"],[0.5,"#ffd166"],[1,"#ff2244"]],
            cmin=0, cmax=100,
        ),
        hovertemplate="%{x}<br>Densité moy : %{y:.1f}%<extra></extra>"
    ))
    fig_seas.add_hline(y=65, line=dict(color="#ff9500", dash="dot"), annotation_text="Seuil élevé")
    fig_seas.add_hline(y=85, line=dict(color="#ff2244", dash="dot"), annotation_text="Seuil critique")

    if 0 <= month_idx <= 11:
        fig_seas.add_vline(x=month_idx, line=dict(color="#00c9a7", width=2, dash="solid"),
                           annotation_text="Ce mois", annotation_font_color="#00c9a7")

    fig_seas.update_layout(
        paper_bgcolor="#0f2040", plot_bgcolor="#0f2040",
        font=dict(color="#e8f4f8"), xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f", title="Densité moy (%)", range=[0,105]),
        height=280, margin=dict(l=10,r=10,t=10,b=10), bargap=0.25,
    )
    st.plotly_chart(fig_seas, use_container_width=True)

    # Weekly pattern
    st.markdown("#### 📅 Patterns hebdomadaires vs horaires")
    col_w1, col_w2 = st.columns(2)

    with col_w1:
        weekly_vals = [np.mean([density_pct(s, month_idx, d, 13, wf, noise=False) for s in CALANQUES]) for d in range(7)]
        fig_w = go.Figure(go.Bar(
            x=DAYS, y=weekly_vals,
            marker=dict(color=weekly_vals, colorscale=[[0,"#003d2a"],[0.6,"#ffd166"],[1,"#ff2244"]], cmin=0, cmax=100),
        ))
        fig_w.update_layout(
            title="Affluence par jour (13h00)", title_font=dict(color="#e8f4f8", size=12),
            paper_bgcolor="#0f2040", plot_bgcolor="#0f2040",
            font=dict(color="#e8f4f8", size=10),
            xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f", range=[0,100]),
            height=220, margin=dict(l=10,r=10,t=40,b=10), bargap=0.3,
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with col_w2:
        hourly_avg = [np.mean([density_pct(s, month_idx, day_idx, h, wf, noise=False) for s in CALANQUES]) for h in HOURS]
        fig_h = go.Figure(go.Scatter(
            x=[f"{h}h" for h in HOURS], y=hourly_avg,
            fill="tozeroy",
            fillcolor="rgba(0,201,167,0.15)",
            line=dict(color="#00c9a7", width=2, shape="spline"),
            mode="lines",
        ))
        fig_h.update_layout(
            title=f"Affluence horaire ({DAYS[day_idx]})", title_font=dict(color="#e8f4f8", size=12),
            paper_bgcolor="#0f2040", plot_bgcolor="#0f2040",
            font=dict(color="#e8f4f8", size=10),
            xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f", range=[0,100]),
            height=220, margin=dict(l=10,r=10,t=40,b=10),
        )
        st.plotly_chart(fig_h, use_container_width=True)

    # Summary stats table
    st.markdown("#### 📋 Tableau de synthèse complet")
    summary = []
    for site, info in CALANQUES.items():
        d = densities[site]
        lbl, cls = crowd_label(d)
        short = site.replace("Calanque de ","").replace("Calanque d'","")
        emoji = "🔴" if cls=="high" and d>=85 else "🟡" if d>=35 else "🟢"
        visitors_est = int(d/100 * info["capacity"])
        summary.append({
            "Site": short,
            "Statut": f"{emoji} {lbl}",
            "Densité": f"{d:.0f}%",
            "Visiteurs estimés": f"~{visitors_est}",
            "Capacité": info["capacity"],
            "Parking": f"{info['parking']} pl.",
            "Marche": f"{info['trail_km']} km",
            "Type": info["type"],
        })
    df_summary = pd.DataFrame(summary)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:30px 0 10px 0;color:#3a5a7a;font-size:0.7rem;font-family:Space Mono,monospace;'>
    CALANQUES FLOW · Marseille · Données synthétiques · Simulation locale 100% offline<br>
    Parc National des Calanques · aucune clé API requise · usage libre
</div>
""", unsafe_allow_html=True)
