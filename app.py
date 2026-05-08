import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Parcelis Revenue Calculator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Base font */
html, body, [class*="st-"], .stMarkdown, .stCaption,
p, label, div { font-family: 'DM Sans', sans-serif !important; }

/* Header */
.header-bar {
    background: #131480;
    padding: 18px 28px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px;
}
.logo-text { font-size: 17px; font-weight: 600; color: #fff !important; }
.logo-text span { color: #9496ea !important; font-weight: 400; font-size: 13px; margin-left: 6px; }
.header-sub { font-size: 11px; color: rgba(255,255,255,0.45) !important; }

/* Section labels */
.section-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #7879e8; margin-bottom: 2px;
}
.divider-label {
    font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #7879e8;
    border-top: 1px solid rgba(120,121,232,0.3);
    padding-top: 14px; margin-top: 4px; margin-bottom: 4px;
}

/* Tier pill */
.tier-pill {
    background: rgba(69,71,212,0.15); border: 1px solid rgba(69,71,212,0.4);
    border-radius: 100px; padding: 6px 16px;
    font-size: 12px; font-weight: 500; color: #9496ea !important;
    display: inline-block; margin-top: 10px; margin-bottom: 4px;
}

/* Metric cards */
.metric-card {
    background: #EDFAF4; border: 1px solid #A8E6CA;
    border-radius: 10px; padding: 20px; text-align: center; height: 100%;
}
.metric-label {
    font-size: 10px !important; font-weight: 600 !important; letter-spacing: 0.1em;
    text-transform: uppercase; color: #0A6640 !important; margin-bottom: 8px;
}
.metric-value {
    font-family: 'DM Mono', monospace !important; font-size: 28px !important;
    font-weight: 500 !important; color: #0D7A4A !important; line-height: 1.1;
}
.metric-sub {
    font-size: 11px !important; color: #0A6640 !important;
    opacity: 0.65; margin-top: 6px;
}

/* Fix number input stepper buttons — make +/- labels visible */
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    background-color: #f0f0fd !important;
    border: 1px solid #dcddf9 !important;
    color: #1e2099 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}
button[data-testid="stNumberInputStepUp"]:hover,
button[data-testid="stNumberInputStepDown"]:hover {
    background-color: #dcddf9 !important;
    color: #1e2099 !important;
}
button[data-testid="stNumberInputStepUp"] svg,
button[data-testid="stNumberInputStepDown"] svg {
    fill: #1e2099 !important;
    stroke: #1e2099 !important;
}

/* Number input field */
input[type="number"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}

/* Input labels — high contrast for both light and dark mode */
.stNumberInput label, .stNumberInput > label,
div[data-testid="stNumberInput"] > label,
div[data-testid="stNumberInput"] label p,
div[data-testid="stNumberInput"] label span {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: inherit !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #4547d4 !important;
}

/* st.metric values inside expander */
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    color: #0c0d2e !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(12,13,46,0.55) !important;
    font-size: 12px !important;
}

/* Footer */
.footer-text {
    text-align: center; font-size: 11px; color: rgba(12,13,46,0.4) !important;
    margin-top: 32px; padding-top: 16px; border-top: 1px solid #ebebf8;
}
.footer-text a { color: #4547d4 !important; text-decoration: none; }
</style>
""", unsafe_allow_html=True)


def get_tier(aov):
    if aov >= 1000:
        p = round(aov * 0.05, 2)
        m = round(aov * 0.03, 2)
        return p, m, "AOV $1,000+  ·  5% premium  ·  3% markup"
    base, step = 2.50, 1.25
    bucket = max(0, int((aov - 200) / 100)) if aov >= 200 else 0
    extra  = (bucket + 1) * step if aov >= 200 else 0
    p = round(base + extra, 2)
    m = round(p * 0.60, 2)
    low  = 0 if aov < 200 else 200 + bucket * 100
    high = 200 if aov < 200 else low + 100
    return p, m, f"AOV ${low}–{high}  ·  Premium ${p:.2f}  ·  Markup ${m:.2f} / order"


def fmt(n):
    n = round(n)
    if n >= 1_000_000: return f"${n/1_000_000:.2f}M"
    if n >= 1_000:     return f"${n/1_000:.1f}k"
    return f"${n:,}"


def fmt_label(n):
    n = round(n)
    if n >= 1_000_000: return f"${n/1_000_000:.2f}M"
    if n >= 1_000:     return f"${n/1_000:.1f}k"
    return f"${n:,}"


# ── HEADER ──
st.markdown("""
<div class="header-bar">
  <div>
    <div class="logo-text">Parcelis <span>· Revenue Calculator</span></div>
  </div>
  <div class="header-sub">Shipping protection · Zero cost to merchant · Underwritten by InsureShip</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="section-label">Merchant uplift estimator</p>', unsafe_allow_html=True)
st.markdown("### How much will Parcelis add to your revenue?")
st.caption("Enter your store numbers. Premium and markup auto-fill from AOV — override anytime.")
st.markdown("---")

# ── INPUTS TOP ──
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Monthly orders**")
    orders = st.number_input("Monthly orders", min_value=1, value=10000, step=500,
                              label_visibility="collapsed",
                              help="Total orders shipped per month")
    st.caption("Orders shipped / month")
with col2:
    st.markdown("**Average order value ($)**")
    aov = st.number_input("Average order value ($)", min_value=1, value=200, step=10,
                           label_visibility="collapsed",
                           help="Sets the premium & markup tier automatically")
    st.caption("Drives premium & markup tier")
with col3:
    st.markdown("**Adoption rate (%)**")
    adopt = st.number_input("Adoption rate (%)", min_value=1, max_value=100, value=60, step=1,
                             label_visibility="collapsed",
                             help="Buyers who opt in to shipping protection at checkout")
    st.caption("Buyers opting in at checkout")

auto_premium, auto_markup, tier_label = get_tier(aov)

st.markdown('<p class="divider-label">Auto-filled from AOV — override if needed</p>', unsafe_allow_html=True)

# ── INPUTS BOTTOM ──
col4, col5 = st.columns(2)
with col4:
    st.markdown("**Protection premium — buyer pays ($)**")
    premium = st.number_input("Protection premium", min_value=0.01,
                               value=float(auto_premium), step=0.01, format="%.2f",
                               label_visibility="collapsed",
                               help="What the buyer pays at checkout")
    st.caption("Auto-filled from AOV · override if needed")
with col5:
    st.markdown("**Markup per insured order ($)**")
    markup = st.number_input("Markup per insured order", min_value=0.01,
                              value=float(auto_markup), step=0.01, format="%.2f",
                              label_visibility="collapsed",
                              help="Your earnings per protected order")
    st.caption("Auto-filled from AOV · override if needed")

st.markdown(f'<div class="tier-pill">● &nbsp; {tier_label}</div>', unsafe_allow_html=True)
st.markdown("---")

# ── CALCULATIONS ──
insured  = round(orders * adopt / 100)
rev_mo   = insured * markup
rev_ann  = rev_mo * 12
gmv      = orders * aov
pct      = (rev_mo / gmv * 100) if gmv > 0 else 0

# ── METRIC CARDS ──
st.markdown('<p class="section-label">Breakdown</p>', unsafe_allow_html=True)
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Revenue / month</div>
      <div class="metric-value">{fmt(rev_mo)}</div>
      <div class="metric-sub">from Parcelis markup</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Revenue / year</div>
      <div class="metric-value">{fmt(rev_ann)}</div>
      <div class="metric-sub">annualised</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">GMV uplift %</div>
      <div class="metric-value">{pct:.2f}%</div>
      <div class="metric-sub">of total GMV</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── EXPANDER ──
with st.expander("See full calculation breakdown"):
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Orders insured / mo", f"{insured:,}")
    d2.metric("Premium / order", f"${premium:.2f}")
    d3.metric("Monthly GMV", fmt(gmv))
    d4.metric("Markup / order", f"${markup:.2f}")

st.markdown("---")

# ── CHART ──
st.markdown('<p class="section-label">Annual revenue comparison</p>', unsafe_allow_html=True)
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

base_ann   = round(gmv * 12)
with_ann   = round(gmv * 12 + rev_ann)
uplift_ann = max(round(rev_ann), 1)  # guard against zero

bar_labels = ["Without Parcelis", "With Parcelis"]

fig = go.Figure()

fig.add_trace(go.Bar(
    name="Without Parcelis",
    x=["Without Parcelis"],
    y=[base_ann],
    marker=dict(color="#dcddf9"),
    marker_line_width=0,
    width=0.38,
    text=[fmt_label(base_ann)],
    textposition="outside",
    textfont=dict(size=13, color="#0c0d2e", family="DM Mono, monospace"),
))

fig.add_trace(go.Bar(
    name="With Parcelis",
    x=["With Parcelis"],
    y=[with_ann],
    marker=dict(color="#0D7A4A"),
    marker_line_width=0,
    width=0.38,
    text=[fmt_label(with_ann)],
    textposition="outside",
    textfont=dict(size=13, color="#0D7A4A", family="DM Mono, monospace"),
))

fig.add_trace(go.Bar(
    name="GMV uplift",
    x=["GMV Uplift"],
    y=[uplift_ann],
    marker=dict(color="#4547d4"),
    marker_line_width=0,
    width=0.38,
    text=[f"+{fmt_label(uplift_ann)}"],
    textposition="outside",
    textfont=dict(size=13, color="#4547d4", family="DM Mono, monospace"),
))

fig.update_layout(
    plot_bgcolor="#f6f6fd",
    paper_bgcolor="#f6f6fd",
    font=dict(family="DM Sans, sans-serif", color="#0c0d2e"),
    height=360,
    margin=dict(l=10, r=10, t=50, b=10),
    showlegend=False,
    xaxis=dict(
        showgrid=False, zeroline=False,
        tickfont=dict(size=13, color="rgba(12,13,46,0.65)", family="DM Sans, sans-serif"),
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(12,13,46,0.06)", zeroline=False,
        tickfont=dict(size=10, color="rgba(12,13,46,0.4)"),
        tickprefix="$",
        range=[0, max(with_ann * 1.25, 1)],
    ),
    bargap=0.3,
)

st.plotly_chart(fig, use_container_width=True)

# ── FOOTER ──
st.markdown("""
<div class="footer-text">
  Powered by <a href="https://myparcelis.com" target="_blank">Parcelis</a>
  &nbsp;·&nbsp; Underwritten by InsureShip &nbsp;·&nbsp; Zero cost to merchant
</div>
""", unsafe_allow_html=True)
