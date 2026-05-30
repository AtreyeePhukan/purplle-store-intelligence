import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"
STORE_ID = "ST1008"

st.set_page_config(page_title="Purplle Store Intelligence", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background-color: #07050f; color: #ede9f6; }
header[data-testid="stHeader"] { display: none; }
.block-container { padding: 2.5rem 3.5rem; max-width: 1400px; }

.page-title { font-size: 32px; font-weight: 800; color: #ede9f6; letter-spacing: -0.04em; margin: 0; }
.page-sub { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #a78bfa; margin-top: 4px; }
.status-text { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #a78bfa; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.2em;
    text-transform: uppercase; color: #e879f9;
    margin: 32px 0 16px 0;
}
.card {
    background: linear-gradient(145deg, #130f20, #0e0b19);
    border: 1px solid #2a1f45; border-radius: 16px;
    padding: 24px 26px 20px 26px;
    position: relative; overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
    transition: border-color 0.2s;
}
.card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #e879f9, #7c3aed);
    opacity: 0; transition: opacity 0.2s;
}
.card:hover { border-color: #e879f9; }
.card:hover::before { opacity: 1; }
.card-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; letter-spacing: 0.12em;
    text-transform: uppercase; color: #e879f9;
    margin-bottom: 12px;
}
.card-value { font-size: 2.4rem; font-weight: 800; color: #ede9f6; letter-spacing: -0.03em; line-height: 1; }
.card-footer { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #a78bfa; margin-top: 10px; }

.anomaly-card {
    background: #110e1a; border-left: 3px solid;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px; margin-bottom: 10px;
}
.anomaly-CRITICAL { border-color: #ef4444; }
.anomaly-WARN     { border-color: #f59e0b; }
.anomaly-INFO     { border-color: #7c3aed; }
.anomaly-title { font-weight: 600; color: #ede9f6; font-size: 14px; }
.anomaly-action { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #a78bfa; margin-top: 5px; }

hr.div { border: none; border-top: 1px solid #1e1530; margin: 20px 0 4px 0; }
</style>
""", unsafe_allow_html=True)

def get(path):
    try:
        r = requests.get(f"{API_URL}{path}", timeout=3)
        r.raise_for_status()
        return r.json()
    except:
        return None

metrics   = get(f"/stores/{STORE_ID}/metrics")
analytics = get(f"/stores/{STORE_ID}/analytics")
anomalies = get(f"/stores/{STORE_ID}/anomalies")
health    = get("/health")

purplle_svg = """<svg width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="38" height="38" rx="11" fill="#e879f9"/>
  <text x="19" y="27" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-weight="800" font-size="24" fill="white">P</text>
</svg>"""

status_color = "#22c55e" if health else "#ef4444"
status_label = "live" if health else "down"

h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:4px">
      {purplle_svg}
      <div>
        <div class="page-title">Store Intelligence</div>
        <div class="page-sub">Brigade Road · {STORE_ID}</div>
      </div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div style="text-align:right;padding-top:12px">
      <span class="status-text">
        <span class="status-dot" style="background:{status_color}"></span>
        {status_label} · {datetime.now().strftime('%d %b %Y %H:%M')}
      </span>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="div">', unsafe_allow_html=True)

def card(label, value, footer=""):
    return f"""<div class="card">
        <div class="card-label">{label}</div>
        <div class="card-value">{value}</div>
        {"<div class='card-footer'>" + footer + "</div>" if footer else ""}
    </div>"""

if metrics:
    st.markdown('<div class="section-label">Visitors</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: st.markdown(card("Unique Visitors", metrics.get("unique_visitors", "—"), "from detection pipeline"), unsafe_allow_html=True)
    with c2: st.markdown(card("Entries", metrics.get("entries", "—"), "inbound crossings"), unsafe_allow_html=True)
    with c3: st.markdown(card("Exits", metrics.get("exits", "—"), "outbound crossings"), unsafe_allow_html=True)
    with c4: st.markdown(card("Re-entries", metrics.get("reentries", "—"), "same visitor returning"), unsafe_allow_html=True)

if analytics:
    st.markdown('<div class="section-label">Sales</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    rev = analytics.get("revenue", 0)
    aov = analytics.get("average_order_value", 0)
    cr  = analytics.get("conversion_rate", 0)
    with c1: st.markdown(card("Orders", analytics.get("orders", "—"), "unique transactions"), unsafe_allow_html=True)
    with c2: st.markdown(card("Revenue", f"₹{rev:,.0f}" if rev else "—", "total basket value"), unsafe_allow_html=True)
    with c3: st.markdown(card("Conversion", f"{cr:.1f}%" if cr else "—", "visitors → purchase"), unsafe_allow_html=True)
    with c4: st.markdown(card("Avg Order", f"₹{aov:,.0f}" if aov else "—", "per transaction"), unsafe_allow_html=True)

if anomalies:
    items = anomalies.get("anomalies", [])
    if items:
        st.markdown('<div class="section-label">Anomalies</div>', unsafe_allow_html=True)
        for a in items:
            sev = a.get("severity", "INFO")
            st.markdown(f"""<div class="anomaly-card anomaly-{sev}">
                <div class="anomaly-title">{a.get('type','')}</div>
                <div class="anomaly-action">→ {a.get('suggested_action','')}</div>
            </div>""", unsafe_allow_html=True)