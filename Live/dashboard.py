import streamlit as st
import requests
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh
from report_generator import create_pdf

st.set_page_config(page_title="AI SOC Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --bg:       #060a0f;
    --bg2:      #0b1118;
    --bg3:      #0f1823;
    --panel:    #0d1520;
    --border:   #1a3a4a;
    --border2:  #0e2535;
    --amber:    #e8a020;
    --amber2:   #f5c842;
    --cyan:     #00d4ff;
    --cyan2:    #00f5ff;
    --green:    #00ff88;
    --red:      #ff3366;
    --yellow:   #f5c842;
    --text:     #c8d8e8;
    --text2:    #6888a0;
    --glow-a:   0 0 8px #e8a02088, 0 0 20px #e8a02044;
    --glow-c:   0 0 8px #00d4ff88, 0 0 20px #00d4ff44;
    --glow-g:   0 0 8px #00ff8888, 0 0 20px #00ff8844;
    --glow-r:   0 0 8px #ff336688, 0 0 20px #ff336644;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background-image: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,212,255,0.012) 2px, rgba(0,212,255,0.012) 4px
    ) !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── Header ── */
.soc-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 1.6rem 0; border-bottom: 1px solid var(--border);
    margin-bottom: 1.8rem; position: relative;
}
.soc-header::after {
    content: ''; position: absolute; bottom: -1px; left: 0;
    width: 220px; height: 1px;
    background: var(--cyan); box-shadow: var(--glow-c);
}
.soc-logo {
    font-family: 'Orbitron', monospace; font-size: 1.7rem; font-weight: 900;
    letter-spacing: 0.12em; color: var(--cyan2); text-shadow: var(--glow-c); line-height: 1;
}
.soc-subtitle {
    font-family: 'Share Tech Mono', monospace; font-size: 0.72rem;
    color: var(--text2); letter-spacing: 0.25em; text-transform: uppercase; margin-top: 4px;
}
.soc-live {
    display: flex; align-items: center; gap: 8px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.72rem;
    color: var(--green); letter-spacing: 0.2em;
}
.soc-live::before {
    content: ''; display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; background: var(--green); box-shadow: var(--glow-g);
    animation: blink 1.2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Status Banner ── */
.status-banner {
    border: 1px solid; border-radius: 2px; padding: 14px 24px;
    margin-bottom: 1.6rem; display: flex; align-items: center;
    justify-content: space-between; position: relative; overflow: hidden;
}
.status-banner::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
}
.status-safe   { border-color: #00ff8833; background: #00ff8808; }
.status-safe::before { background: var(--green); box-shadow: var(--glow-g); }
.status-warn   { border-color: #f5c84233; background: #f5c84208; }
.status-warn::before { background: var(--yellow); box-shadow: 0 0 8px #f5c84288; }
.status-danger { border-color: #ff336633; background: #ff336608; animation: flicker 3s infinite; }
.status-danger::before { background: var(--red); box-shadow: var(--glow-r); }
@keyframes flicker { 0%,96%,100%{opacity:1} 97%{opacity:0.85} 98%{opacity:1} 99%{opacity:0.9} }

.status-label {
    font-family: 'Orbitron', monospace; font-size: 1.05rem;
    font-weight: 700; letter-spacing: 0.18em;
}
.status-safe   .status-label { color: var(--green);  text-shadow: var(--glow-g); }
.status-warn   .status-label { color: var(--yellow); text-shadow: 0 0 8px #f5c84288; }
.status-danger .status-label { color: var(--red);    text-shadow: var(--glow-r); }
.risk-readout { font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: var(--text2); letter-spacing: 0.15em; }
.risk-value { font-family: 'Orbitron', monospace; font-size: 1.4rem; font-weight: 700; margin-left: 10px; }
.status-safe   .risk-value { color: var(--green);  }
.status-warn   .risk-value { color: var(--yellow); }
.status-danger .risk-value { color: var(--red);    }

/* ── Metric Cards ── */
[data-testid="metric-container"] {
    background: var(--panel) !important; border: 1px solid var(--border2) !important;
    border-radius: 2px !important; padding: 20px 24px !important;
    position: relative !important; overflow: hidden !important;
}
[data-testid="metric-container"]::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--cyan) 0%, transparent 60%);
}
[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important; font-size: 0.68rem !important;
    letter-spacing: 0.2em !important; text-transform: uppercase !important; color: var(--text2) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important; font-size: 1.65rem !important;
    font-weight: 700 !important; color: var(--cyan2) !important; text-shadow: var(--glow-c) !important;
}
[data-testid="stMetricDelta"] > div {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important; letter-spacing: 0.1em !important;
}

/* ── Section Headers ── */
h3 {
    font-family: 'Orbitron', monospace !important; font-size: 0.78rem !important;
    font-weight: 700 !important; letter-spacing: 0.3em !important;
    text-transform: uppercase !important; color: var(--text2) !important; margin-bottom: 1rem !important;
}

/* ── Chart ── */
[data-testid="stVegaLiteChart"] > div,
[data-testid="stArrowVegaLiteChart"] > div { background: transparent !important; }
.stBarChart > div { background: transparent !important; }

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid var(--border2) !important; margin: 1.6rem 0 !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 2px !important; font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.82rem !important; line-height: 1.7 !important; letter-spacing: 0.04em !important;
}

/* ── Download Button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important; border: 1px solid var(--amber) !important;
    color: var(--amber) !important; font-family: 'Orbitron', monospace !important;
    font-size: 0.72rem !important; font-weight: 700 !important;
    letter-spacing: 0.2em !important; text-transform: uppercase !important;
    border-radius: 2px !important; padding: 10px 28px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: var(--amber) !important; color: var(--bg) !important; box-shadow: var(--glow-a) !important;
}

/* ── Panel ── */
.panel {
    background: var(--panel); border: 1px solid var(--border2); border-radius: 2px;
    padding: 20px 24px; margin-bottom: 1.2rem; position: relative;
}
.panel::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--amber) 0%, transparent 50%);
}
.panel-label {
    font-family: 'Share Tech Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.28em; text-transform: uppercase; color: var(--amber); margin-bottom: 12px;
}
.panel-content {
    font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: var(--text); line-height: 1.8;
}

/* ── History Log ── */
.log-entry {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 9px 0; border-bottom: 1px solid var(--border2);
    font-family: 'Share Tech Mono', monospace; font-size: 0.72rem;
}
.log-entry:last-child { border-bottom: none; }
.log-time { color: var(--text2); min-width: 80px; letter-spacing: 0.06em; padding-top: 1px; }
.log-badge {
    font-size: 0.58rem; letter-spacing: 0.12em; padding: 2px 7px;
    border-radius: 2px; min-width: 74px; text-align: center; font-weight: 700; white-space: nowrap;
}
.badge-attack { background: #ff336622; color: var(--red);    border: 1px solid #ff336644; }
.badge-normal { background: #00ff8822; color: var(--green);  border: 1px solid #00ff8844; }
.badge-warn   { background: #f5c84222; color: var(--yellow); border: 1px solid #f5c84244; }
.log-detail { color: var(--text2); flex: 1; line-height: 1.5; }
.log-detail span { color: var(--cyan); }

/* ── Uptime box ── */
.uptime-box {
    background: var(--panel); border: 1px solid var(--border2); border-radius: 2px;
    padding: 16px 20px; text-align: center; height: 100%;
    display: flex; flex-direction: column; justify-content: center;
}
.uptime-label {
    font-family: 'Share Tech Mono', monospace; font-size: 0.62rem;
    letter-spacing: 0.22em; color: var(--text2); text-transform: uppercase; margin-bottom: 8px;
}
.uptime-value {
    font-family: 'Orbitron', monospace; font-size: 1.15rem; font-weight: 700;
    color: var(--green); text-shadow: var(--glow-g);
}
</style>
""", unsafe_allow_html=True)

# ─── Auto refresh every 10s ────────────────────────────────────────────────────

st_autorefresh(interval=10000, key="dashboardrefresh")

# ══════════════════════════════════════════════════════════════════════════════
# 1. st.session_state — persist history + uptime across reruns
#    Without this, every 10-second refresh would wipe all accumulated data.
#    session_state survives reruns for the lifetime of the browser session.
# ══════════════════════════════════════════════════════════════════════════════

if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)

if "history" not in st.session_state:
    st.session_state.history = []   # list of snapshot dicts

if "prev_attacks" not in st.session_state:
    st.session_state.prev_attacks = 0

# ══════════════════════════════════════════════════════════════════════════════
# 2. @st.cache_data(ttl=3) — cache the API response for 3 seconds
#    Streamlit reruns the whole script on every interaction AND every
#    autorefresh tick. Without caching, every rerun fires a new HTTP request.
#    cache_data memoises the return value; ttl=3 expires it after 3 seconds
#    so the dashboard still gets fresh data each cycle without flooding the API.
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3)
def fetch_stats(api_url: str) -> dict:
    r = requests.get(api_url, timeout=3)
    r.raise_for_status()
    return r.json()

# ─── Timestamps & uptime ─────────────────────────────────────────────────────

now = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
now_str = now.strftime("%Y-%m-%d  %H:%M:%S IST")

uptime_delta = now - st.session_state.start_time
uh = int(uptime_delta.total_seconds() // 3600)
um = int((uptime_delta.total_seconds() % 3600) // 60)
us = int(uptime_delta.total_seconds() % 60)
uptime_str = f"{uh:02d}:{um:02d}:{us:02d}"

# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="soc-header">
    <div>
        <div class="soc-logo">⬡ AI·SOC SENTINEL</div>
        <div class="soc-subtitle">Autonomous Intrusion Detection &amp; Response Platform</div>
    </div>
    <div style="text-align:right;">
        <div class="soc-live">LIVE MONITORING</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:var(--text2);margin-top:5px;letter-spacing:0.15em;">{now_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Fetch ────────────────────────────────────────────────────────────────────

API_STATS = "http://127.0.0.1:5000/stats"

try:
    data = fetch_stats(API_STATS)
except Exception:
    st.error("⚠  SENSOR ARRAY OFFLINE — Cannot reach API at http://127.0.0.1:5000/stats")
    st.stop()

total   = data.get("total_packets", 0)
attacks = data.get("attacks", 0)
normal  = data.get("normal", 0)
report  = data.get("last_report", "No incidents yet")

risk = attacks / total if total > 0 else 0

if risk < 0.3:
    status_cls, status_text, status_icon = "status-safe",   "NETWORK SECURE",      "▣"
elif risk < 0.5:
    status_cls, status_text, status_icon = "status-warn",   "SUSPICIOUS ACTIVITY", "◈"
else:
    status_cls, status_text, status_icon = "status-danger", "UNDER ATTACK",        "◉"

# ─── Append to history (session_state) ───────────────────────────────────────

st.session_state.history.append({
    "time": now_str, "total": total, "attacks": attacks,
    "normal": normal, "risk": risk, "status": status_text,
})
if len(st.session_state.history) > 50:
    st.session_state.history = st.session_state.history[-50:]

attack_delta = attacks - st.session_state.prev_attacks
st.session_state.prev_attacks = attacks

# ─── Status Banner ────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="status-banner {status_cls}">
    <div>
        <div class="status-label">{status_icon} &nbsp; {status_text}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:var(--text2);margin-top:4px;letter-spacing:0.15em;">
            THREAT CLASSIFICATION · REAL-TIME
        </div>
    </div>
    <div style="text-align:right;">
        <div class="risk-readout">RISK SCORE</div>
        <div style="display:flex;align-items:baseline;gap:4px;justify-content:flex-end;">
            <span class="risk-value">{risk:.3f}</span>
            <span style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:var(--text2);">/ 1.000</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. Improved layout — st.columns + st.container
#    st.container() creates a logical grouping so related widgets stay together.
#    st.columns([ratio, ratio]) splits the row by proportional widths, giving
#    much more control than the equal-thirds default.
# ══════════════════════════════════════════════════════════════════════════════

# ── Row 1: 3 metrics + uptime widget ─────────────────────────────────────────

st.subheader("Packet Analysis")

col1, col2, col3, col4 = st.columns([2, 2, 2, 1.4])

col1.metric("Total Packets Analyzed", f"{total:,}")
col2.metric("Normal Traffic",         f"{normal:,}")
col3.metric(
    "Detected Attacks", f"{attacks:,}",
    delta=f"+{attack_delta}" if attack_delta > 0 else (str(attack_delta) if attack_delta < 0 else None),
    delta_color="inverse"
)
with col4:
    st.markdown(f"""
    <div class="uptime-box">
        <div class="uptime-label">Session Uptime</div>
        <div class="uptime-value">{uptime_str}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Row 2: Chart (wider) | Event History log (narrower) ──────────────────────

chart_col, log_col = st.columns([1.6, 1], gap="large")

with chart_col:
    with st.container():
        st.subheader("Traffic Distribution")
        chart_df = pd.DataFrame({
            "Traffic Type": ["Normal", "Attack"],
            "Count":        [normal, attacks]
        })
        st.bar_chart(chart_df.set_index("Traffic Type"), color=["#00d4ff"], height=240)

with log_col:
    with st.container():
        st.subheader("Event History")
        recent = st.session_state.history[-10:][::-1]  # newest first

        if len(recent) < 2:
            st.markdown(
                "<div style='font-family:Share Tech Mono,monospace;font-size:0.72rem;"
                "color:var(--text2);padding:10px 0;letter-spacing:0.1em;'>Collecting data…</div>",
                unsafe_allow_html=True
            )
        else:
            rows = ""
            for e in recent:
                if e["status"] == "UNDER ATTACK":
                    badge = '<span class="log-badge badge-attack">ATTACK</span>'
                elif e["status"] == "SUSPICIOUS ACTIVITY":
                    badge = '<span class="log-badge badge-warn">WARN</span>'
                else:
                    badge = '<span class="log-badge badge-normal">SECURE</span>'
                rows += f"""
                <div class="log-entry">
                    <span class="log-time">{e['time'][11:19]}</span>
                    {badge}
                    <span class="log-detail">
                        <span>{e['total']:,}</span> pkts &nbsp;
                        {e['attacks']} atk &nbsp;
                        r={e['risk']:.3f}
                    </span>
                </div>"""
            st.markdown(
                f'<div class="panel" style="padding:14px 18px;">{rows}</div>',
                unsafe_allow_html=True
            )

st.divider()

# ── Row 3: AI Report | Download + session stats ───────────────────────────────

rep_col, dl_col = st.columns([2.4, 1], gap="large")

with rep_col:
    with st.container():
        st.subheader("Latest AI Investigation")
        if report != "No incidents yet":
            st.markdown(f"""
            <div class="panel">
                <div class="panel-label">◈ &nbsp; AI Threat Report</div>
                <div class="panel-content">{report}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No incidents detected. All systems nominal.")

with dl_col:
    with st.container():
        st.subheader("Incident Report")
        if report != "No incidents yet":
            pdf_buffer = create_pdf(report)
            st.download_button(
                label="⬇  Export PDF Report",
                data=pdf_buffer,
                file_name="SOC_Incident_Report.pdf",
                mime="application/pdf"
            )
            total_snaps  = len(st.session_state.history)
            attack_snaps = sum(1 for e in st.session_state.history if e["status"] == "UNDER ATTACK")
            st.markdown(f"""
            <div class="panel" style="margin-top:14px;">
                <div class="panel-label">◈ &nbsp; Session Stats</div>
                <div class="panel-content">
                    Snapshots recorded<br/>
                    <span style="color:var(--cyan2);font-size:1.05rem;">{total_snaps}</span>
                    <br/><br/>
                    Attack state events<br/>
                    <span style="color:var(--red);font-size:1.05rem;">{attack_snaps}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                        color:var(--text2);letter-spacing:0.08em;padding:10px 0;line-height:2;">
                Report will generate<br/>automatically upon<br/>attack detection.
            </div>
            """, unsafe_allow_html=True)

           