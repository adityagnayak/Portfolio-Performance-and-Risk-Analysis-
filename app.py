import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Risk Analyser",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #0d0f14;
    --surface:   #141720;
    --surface2:  #1c2030;
    --border:    #252a3a;
    --accent:    #4f8ef7;
    --accent2:   #e06c75;
    --accent3:   #98c379;
    --gold:      #e5c07b;
    --text:      #abb2bf;
    --text-hi:   #e6edf3;
    --text-lo:   #5c6370;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Header */
.app-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.app-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: var(--text-hi);
    letter-spacing: -0.5px;
    margin: 0;
}
.app-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-top: 4px;
}

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
}
.metric-card.red::before  { background: var(--accent2); }
.metric-card.green::before { background: var(--accent3); }
.metric-card.gold::before  { background: var(--gold); }

.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-lo);
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: var(--text-hi);
    line-height: 1;
}
.metric-value.pos { color: var(--accent3); }
.metric-value.neg { color: var(--accent2); }
.metric-hint {
    font-size: 0.7rem;
    color: var(--text-lo);
    margin-top: 6px;
}

/* Section headings */
.section-heading {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: var(--text-hi);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* Table */
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-lo);
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
}
.styled-table td {
    padding: 0.55rem 0.8rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: var(--text);
    border-bottom: 1px solid var(--border);
}
.styled-table tr:last-child td { border-bottom: none; }
.styled-table tr:hover td { background: var(--surface2); }
.pos { color: var(--accent3) !important; }
.neg { color: var(--accent2) !important; }

/* Info box */
.info-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.82rem;
    line-height: 1.6;
    color: var(--text);
}

/* Plotly chart background fix */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#abb2bf", size=11),
    xaxis=dict(gridcolor="#252a3a", linecolor="#252a3a", zerolinecolor="#252a3a"),
    yaxis=dict(gridcolor="#252a3a", linecolor="#252a3a", zerolinecolor="#252a3a"),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#252a3a", borderwidth=1),
)

ACCENT  = "#4f8ef7"
ACCENT2 = "#e06c75"
ACCENT3 = "#98c379"
GOLD    = "#e5c07b"
COLORS  = [ACCENT, ACCENT3, GOLD, ACCENT2, "#c678dd", "#56b6c2"]


@st.cache_data(show_spinner=False)
def fetch_data(tickers: list[str], benchmark: str, start: str, end: str):
    all_tickers = tickers + ([benchmark] if benchmark not in tickers else [])
    raw = yf.download(all_tickers, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]] if "Close" in raw.columns else raw
    prices.dropna(how="all", inplace=True)
    return prices


def compute_metrics(prices: pd.DataFrame, tickers: list[str], benchmark: str,
                    weights: np.ndarray, rf: float = 0.065):
    port_prices = prices[tickers].copy()
    port_prices.dropna(inplace=True)

    port_rets = port_prices.pct_change().dropna()
    port_daily = port_rets @ weights

    bench_rets = prices[benchmark].pct_change().dropna()
    bench_rets = bench_rets.reindex(port_daily.index).dropna()
    port_daily = port_daily.reindex(bench_rets.index).dropna()

    if len(port_daily) == 0:
        raise ValueError(
            "No overlapping trading days between your portfolio and the selected benchmark. "
            "This usually happens when mixing markets with different trading calendars "
            "(e.g. Indian stocks vs FTSE). Try switching to a same-market benchmark or "
            "widening your date range."
        )

    # Cumulative
    cum_port  = (1 + port_daily).cumprod()
    cum_bench = (1 + bench_rets).cumprod()

    # Annual return / vol
    ann_ret  = (cum_port.iloc[-1] ** (252 / len(port_daily))) - 1
    ann_vol  = port_daily.std() * np.sqrt(252)
    rf_daily = rf / 252
    sharpe   = (port_daily.mean() - rf_daily) / port_daily.std() * np.sqrt(252)

    # Drawdown
    roll_max  = cum_port.cummax()
    drawdown  = (cum_port - roll_max) / roll_max
    max_dd    = drawdown.min()

    # Beta / Alpha
    cov_mat  = np.cov(port_daily, bench_rets)
    beta     = cov_mat[0, 1] / cov_mat[1, 1]
    bench_ann = (cum_bench.iloc[-1] ** (252 / len(bench_rets))) - 1
    alpha    = ann_ret - (rf + beta * (bench_ann - rf))

    # Sortino
    downside = port_daily[port_daily < rf_daily]
    sortino  = (port_daily.mean() - rf_daily) / downside.std() * np.sqrt(252) if len(downside) else np.nan

    # Individual stock metrics
    stock_metrics = []
    for i, t in enumerate(tickers):
        r = port_rets[t]
        cr = (1 + r).cumprod()
        ar = (cr.iloc[-1] ** (252 / len(r))) - 1
        av = r.std() * np.sqrt(252)
        sh = (r.mean() - rf_daily) / r.std() * np.sqrt(252)
        cov_s = np.cov(r, bench_rets.reindex(r.index).fillna(0))
        bt = cov_s[0, 1] / cov_s[1, 1] if cov_s[1, 1] != 0 else np.nan
        stock_metrics.append({
            "Ticker": t,
            "Weight": f"{weights[i]*100:.1f}%",
            "Ann. Return": ar,
            "Ann. Volatility": av,
            "Sharpe": sh,
            "Beta": bt,
        })

    return {
        "port_daily": port_daily,
        "bench_rets": bench_rets,
        "cum_port":   cum_port,
        "cum_bench":  cum_bench,
        "drawdown":   drawdown,
        "ann_ret":    ann_ret,
        "ann_vol":    ann_vol,
        "sharpe":     sharpe,
        "sortino":    sortino,
        "max_dd":     max_dd,
        "beta":       beta,
        "alpha":      alpha,
        "stock_metrics": stock_metrics,
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    raw_tickers = st.text_input(
        "Portfolio Tickers (comma-separated)",
        value="RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS",
        help="Use Yahoo Finance symbols. Indian stocks: .NS suffix"
    )
    tickers = [t.strip().upper() for t in raw_tickers.split(",") if t.strip()]

    BENCHMARKS = {
        "NIFTY 50 (India)":   "^NSEI",
        "NYSE Composite (US)": "^NYA",
        "FTSE 100 (UK)":      "^FTSE",
        "Custom":             None,
    }
    bench_label = st.selectbox("Benchmark", list(BENCHMARKS.keys()))
    if BENCHMARKS[bench_label] is None:
        benchmark = st.text_input("Custom Benchmark Ticker", value="^NSEI",
                                  help="Any Yahoo Finance index symbol")
    else:
        benchmark = BENCHMARKS[bench_label]
        st.caption(f"Ticker: `{benchmark}`")

    st.markdown("#### Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=datetime.today() - timedelta(days=365*3))
    with col2:
        end_date = st.date_input("To", value=datetime.today())

    st.markdown("#### Portfolio Weights")
    weight_mode = st.radio("Weighting", ["Equal Weight", "Custom Weights"], horizontal=True)

    weights = np.array([1 / len(tickers)] * len(tickers))
    if weight_mode == "Custom Weights" and tickers:
        raw_weights = []
        for t in tickers:
            w = st.number_input(f"{t} (%)", min_value=0.0, max_value=100.0,
                                value=round(100 / len(tickers), 1), step=0.1, format="%.1f")
            raw_weights.append(w)
        total = sum(raw_weights)
        if total > 0:
            weights = np.array(raw_weights) / total
            st.caption(f"Total: {total:.1f}% → normalised to 100%")
        else:
            st.warning("Weights sum to 0.")

    rf_rate = st.number_input("Risk-Free Rate (%)", value=6.5, step=0.1, format="%.1f") / 100

    run = st.button("▶  Run Analysis", use_container_width=True, type="primary")

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-sub">Investment Analytics · Portfolio Risk</div>
  <div class="app-title">Portfolio Performance & Risk Analysis</div>
</div>
""", unsafe_allow_html=True)

if not run:
    st.markdown("""
    <div class="info-box">
    👈 Configure your portfolio in the sidebar, then click <strong>Run Analysis</strong>.<br><br>
    This tool evaluates whether your portfolio's returns come from <em>genuine skill</em> (positive alpha)
    or simply from riding the market (high beta). Key metrics: Sharpe ratio, max drawdown, beta,
    risk attribution, and benchmark comparison.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Fetch & compute ───────────────────────────────────────────────────────────
with st.spinner("Fetching market data…"):
    try:
        prices = fetch_data(tickers, benchmark, str(start_date), str(end_date))
    except Exception as e:
        st.error(f"Data fetch failed: {e}")
        st.stop()

missing = [t for t in tickers if t not in prices.columns]
if missing:
    st.error(f"Could not fetch data for: {', '.join(missing)}. Check ticker symbols.")
    st.stop()
if benchmark not in prices.columns:
    st.error(f"Benchmark '{benchmark}' not found.")
    st.stop()

try:
    m = compute_metrics(prices, tickers, benchmark, weights, rf_rate)
except ValueError as e:
    st.error(str(e))
    st.stop()

# ── KPI Row ───────────────────────────────────────────────────────────────────
def _cls(v): return "pos" if v >= 0 else "neg"
def _pct(v): return f"{v*100:+.2f}%"
def _f2(v):  return f"{v:.2f}"

kpis = [
    ("Annual Return",   _pct(m['ann_ret']),   _cls(m['ann_ret']),  "blue",  "Total annualised return"),
    ("Volatility",      _pct(m['ann_vol']),   "",                  "gold",  "Annualised std dev"),
    ("Sharpe Ratio",    _f2(m['sharpe']),      _cls(m['sharpe']),  "blue",  ">1 is good, >2 is great"),
    ("Sortino Ratio",   _f2(m['sortino']),     _cls(m['sortino']), "green", "Downside-adjusted Sharpe"),
    ("Max Drawdown",    _pct(m['max_dd']),    "neg",               "red",   "Worst peak-to-trough loss"),
    ("Beta",            _f2(m['beta']),        "",                  "gold",  "Sensitivity to benchmark"),
    ("Alpha (Ann.)",    _pct(m['alpha']),     _cls(m['alpha']),    "blue",  "Skill-based excess return"),
]

cards_html = '<div class="metric-grid">'
color_map = {"blue": "", "red": "red", "green": "green", "gold": "gold"}
for label, val, val_cls, card_color, hint in kpis:
    c = color_map.get(card_color, "")
    cards_html += f"""
    <div class="metric-card {c}">
      <div class="metric-label">{label}</div>
      <div class="metric-value {val_cls}">{val}</div>
      <div class="metric-hint">{hint}</div>
    </div>"""
cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

# ── Alpha / Beta Interpretation ───────────────────────────────────────────────
alpha_msg = (
    f"✅ <strong>Positive Alpha ({_pct(m['alpha'])})</strong> — returns appear to come from <em>skill</em>, not just market movement."
    if m['alpha'] >= 0 else
    f"⚠️ <strong>Negative Alpha ({_pct(m['alpha'])})</strong> — underperforming after adjusting for market risk. Consider reviewing stock selection."
)
beta_msg = (
    "Beta < 1: portfolio moves less than the market — lower systematic risk." if m['beta'] < 1 else
    "Beta > 1: portfolio amplifies market moves — higher systematic risk."
)
st.markdown(f'<div class="info-box">{alpha_msg}<br>{beta_msg}</div>', unsafe_allow_html=True)

# ── Chart 1: Cumulative Returns ───────────────────────────────────────────────
st.markdown('<div class="section-heading">Cumulative Returns vs Benchmark</div>', unsafe_allow_html=True)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=m['cum_port'].index, y=m['cum_port'].values,
    name="Portfolio", line=dict(color=ACCENT, width=2),
    fill="tozeroy", fillcolor="rgba(79,142,247,0.07)"
))
fig1.add_trace(go.Scatter(
    x=m['cum_bench'].index, y=m['cum_bench'].values,
    name="Benchmark", line=dict(color=GOLD, width=1.5, dash="dot")
))
fig1.update_layout(**CHART_LAYOUT, height=350,
    yaxis_title="Growth of ₹1", hovermode="x unified")
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: Drawdown ─────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">Drawdown Analysis</div>', unsafe_allow_html=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=m['drawdown'].index, y=m['drawdown'].values * 100,
    name="Drawdown %", line=dict(color=ACCENT2, width=1.5),
    fill="tozeroy", fillcolor="rgba(224,108,117,0.12)"
))
fig2.update_layout(**CHART_LAYOUT, height=280,
    yaxis_title="Drawdown (%)", hovermode="x unified")
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: Rolling Volatility & Beta ───────────────────────────────────────
st.markdown('<div class="section-heading">Rolling 30-Day Volatility & Beta</div>', unsafe_allow_html=True)

window = 30
roll_vol  = m['port_daily'].rolling(window).std() * np.sqrt(252) * 100
roll_cov  = m['port_daily'].rolling(window).cov(m['bench_rets'])
roll_vb   = m['bench_rets'].rolling(window).var()
roll_beta = roll_cov / roll_vb

fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                     subplot_titles=("Rolling Volatility (Ann. %)", "Rolling Beta"),
                     vertical_spacing=0.08)
fig3.add_trace(go.Scatter(x=roll_vol.index, y=roll_vol.values,
    line=dict(color=ACCENT3, width=1.5), name="Volatility"), row=1, col=1)
fig3.add_trace(go.Scatter(x=roll_beta.index, y=roll_beta.values,
    line=dict(color=GOLD, width=1.5), name="Beta"), row=2, col=1)
fig3.add_hline(y=1, line_dash="dot", line_color="#5c6370", row=2, col=1)
fig3.update_layout(**CHART_LAYOUT, height=400, showlegend=False)
fig3.update_yaxes(gridcolor="#252a3a", linecolor="#252a3a")
st.plotly_chart(fig3, use_container_width=True)

# ── Chart 4: Return Distribution ─────────────────────────────────────────────
st.markdown('<div class="section-heading">Daily Return Distribution</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    fig4 = go.Figure()
    fig4.add_trace(go.Histogram(
        x=m['port_daily'] * 100, nbinsx=60,
        marker_color=ACCENT, opacity=0.8, name="Portfolio"
    ))
    fig4.add_trace(go.Histogram(
        x=m['bench_rets'] * 100, nbinsx=60,
        marker_color=GOLD, opacity=0.5, name="Benchmark"
    ))
    fig4.update_layout(**CHART_LAYOUT, height=300,
        barmode="overlay", xaxis_title="Daily Return (%)",
        yaxis_title="Frequency", title="Return Histogram")
    st.plotly_chart(fig4, use_container_width=True)

with col_b:
    # Scatter: portfolio vs benchmark returns
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=m['bench_rets'] * 100,
        y=m['port_daily'] * 100,
        mode="markers",
        marker=dict(color=ACCENT, size=3, opacity=0.5),
        name="Daily Returns"
    ))
    # Regression line
    x_fit = np.linspace(m['bench_rets'].min(), m['bench_rets'].max(), 100)
    y_fit = m['alpha'] / 252 + m['beta'] * x_fit
    fig5.add_trace(go.Scatter(
        x=x_fit * 100, y=y_fit * 100,
        line=dict(color=ACCENT2, width=2), name=f"β={m['beta']:.2f}"
    ))
    fig5.update_layout(**CHART_LAYOUT, height=300,
        xaxis_title="Benchmark Return (%)", yaxis_title="Portfolio Return (%)",
        title="Portfolio vs Benchmark Scatter")
    st.plotly_chart(fig5, use_container_width=True)

# ── Chart 5: Risk Attribution ─────────────────────────────────────────────────
st.markdown('<div class="section-heading">Risk Attribution</div>', unsafe_allow_html=True)

port_rets_df = prices[tickers].pct_change().dropna()
contrib_vol  = []
for i, t in enumerate(tickers):
    cov_port = np.cov(port_rets_df[t], m['port_daily'])[0, 1]
    contrib   = weights[i] * cov_port / (m['port_daily'].std() ** 2)
    contrib_vol.append(contrib)

contrib_vol = np.array(contrib_vol)
contrib_pct = contrib_vol / contrib_vol.sum() * 100

col_c, col_d = st.columns(2)
with col_c:
    fig6 = go.Figure(go.Bar(
        x=tickers, y=contrib_pct,
        marker_color=COLORS[:len(tickers)],
        text=[f"{v:.1f}%" for v in contrib_pct],
        textposition="outside",
    ))
    fig6.update_layout(**CHART_LAYOUT, height=300,
        yaxis_title="% of Portfolio Risk", title="Risk Contribution by Stock")
    st.plotly_chart(fig6, use_container_width=True)

with col_d:
    fig7 = go.Figure(go.Pie(
        labels=tickers, values=contrib_pct,
        marker_colors=COLORS[:len(tickers)],
        hole=0.55,
        textinfo="label+percent",
        textfont=dict(size=11),
    ))
    fig7.update_layout(**CHART_LAYOUT, height=300,
        title="Risk Attribution Donut",
        annotations=[dict(text="RISK", x=0.5, y=0.5,
                          font_size=13, showarrow=False,
                          font_color="#abb2bf")])
    st.plotly_chart(fig7, use_container_width=True)

# ── Stock-by-stock table ──────────────────────────────────────────────────────
st.markdown('<div class="section-heading">Individual Stock Breakdown</div>', unsafe_allow_html=True)

table_rows = ""
for s in m['stock_metrics']:
    ar   = s['Ann. Return']
    av   = s['Ann. Volatility']
    sh   = s['Sharpe']
    bt   = s['Beta']
    ar_c = "pos" if ar >= 0 else "neg"
    sh_c = "pos" if sh >= 1 else ("neg" if sh < 0 else "")
    bt_c = "neg" if bt > 1.5 else ("pos" if bt < 0.8 else "")
    table_rows += f"""
    <tr>
      <td><strong>{s['Ticker']}</strong></td>
      <td>{s['Weight']}</td>
      <td class="{ar_c}">{ar*100:+.2f}%</td>
      <td>{av*100:.2f}%</td>
      <td class="{sh_c}">{sh:.2f}</td>
      <td class="{bt_c}">{bt:.2f}</td>
    </tr>"""

st.markdown(f"""
<table class="styled-table">
  <thead>
    <tr>
      <th>Ticker</th><th>Weight</th><th>Ann. Return</th>
      <th>Volatility</th><th>Sharpe</th><th>Beta</th>
    </tr>
  </thead>
  <tbody>{table_rows}</tbody>
</table>
""", unsafe_allow_html=True)

# ── Skill vs Market Footer ────────────────────────────────────────────────────
st.markdown('<div class="section-heading">Skill vs Market Verdict</div>', unsafe_allow_html=True)

market_contrib = m['beta'] * (((1 + m['ann_ret']) / (1 + m['ann_ret'] - m['alpha'])) - 1)
skill_contrib  = m['alpha']
total          = abs(market_contrib) + abs(skill_contrib)
skill_pct      = abs(skill_contrib) / total * 100 if total else 50
market_pct     = 100 - skill_pct

verdict = "SKILL-DRIVEN" if m['alpha'] > 0.02 else ("MARKET-DRIVEN" if m['alpha'] < -0.02 else "MIXED")
v_color = "#98c379" if m['alpha'] > 0.02 else ("#e06c75" if m['alpha'] < -0.02 else "#e5c07b")

st.markdown(f"""
<div class="info-box">
  <div style="font-family:'DM Mono',monospace; font-size:0.65rem; letter-spacing:3px;
              text-transform:uppercase; color:#5c6370; margin-bottom:12px;">
    Performance Attribution Verdict
  </div>
  <div style="font-family:'DM Serif Display',serif; font-size:2rem; color:{v_color}; margin-bottom:12px;">
    {verdict}
  </div>
  <div style="background:#1c2030; border-radius:6px; overflow:hidden; height:10px; margin-bottom:8px;">
    <div style="width:{skill_pct:.0f}%; background:#98c379; height:100%; float:left; border-radius:6px 0 0 6px;"></div>
    <div style="width:{market_pct:.0f}%; background:#4f8ef7; height:100%; float:left;"></div>
  </div>
  <div style="font-size:0.75rem; color:#abb2bf;">
    🟢 Skill (Alpha): <strong>{skill_pct:.0f}%</strong> &nbsp;|&nbsp;
    🔵 Market (Beta): <strong>{market_pct:.0f}%</strong>
  </div>
  <br>
  <div style="font-size:0.8rem; color:#abb2bf;">
    Alpha of <strong style="color:{v_color}">{m['alpha']*100:+.2f}%</strong> means
    this portfolio {"outperforms" if m['alpha'] >= 0 else "underperforms"} its
    risk-adjusted benchmark by that margin annually.
    {"This suggests active stock selection is adding value." if m['alpha'] >= 0 else
     "This suggests passive index exposure may be more efficient."}
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div style="text-align:center; font-family:DM Mono,monospace; font-size:0.65rem; '
    'color:#3c4050; padding:2rem 0 1rem;">Portfolio Risk Analyser · Built with Streamlit & yfinance</div>',
    unsafe_allow_html=True
)
