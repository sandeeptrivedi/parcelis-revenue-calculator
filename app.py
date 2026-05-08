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

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.header-bar {
    background: #131480;
    padding: 18px 28px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
}
.logo-text { font-size: 17px; font-weight: 600; color: #fff; letter-spacing: 0.01em; }
.logo-text span { color: #9496ea; font-weight: 400; font-size: 13px; margin-left: 6px; }
.header-sub { font-size: 11px; color: rgba(255,255,255,0.38); }

.section-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #4547d4; margin-bottom: 2px;
}
.divider-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #4547d4;
    border-top: 1px solid #dcddf9; padding-top: 14px; margin-top: 6px; margin-bottom: 4px;
}
.tier-pill {
    background: #f0f0fd; border: 1px solid #dcddf9;
    border-radius: 100px; padding: 6px 16px;
    font-size: 12px; font-weight: 500; color: #2e30c4;
    display: inline-block; margin-top: 8px;
}

.metric-card {
    background: #EDFAF4; border: 1px solid #A8E6CA;
    border-radius: 10px; padding: 18px 20px; text-align: center;
}
.metric-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #0A6640; opacity: 0.75; margin-bottom: 6px;
}
.metric-value {
    font-family: 'DM Mono', monospace; font-size: 26px;
    font-weight: 500; color: #0D7A4A; line-height: 1;
}
.metric-sub { font-size: 11px; color: #0A6640; opacity: 0.6; margin-top: 5px; }

.footer-text {
    text-align: center; font-size: 11px; color: rgba(12,13,46,0.4);
    margin-top: 32px; padding-top: 16px; border-top: 1px solid #f0f0fd;
}
.footer-text a { color: #4547d4; text-decoration: none; }

/* Override streamlit number input styling */
div[data-testid="stNumberInput"] input {
    font-family: 'DM Mono', monospace !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}
div[data-testid="stNumberInput"] label {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: rgba(12,13,46,0.7) !important;
}
</style>
""", unsafe_allow_html=True)


def get_tier(aov):
    if aov >= 1000:
        p = round(aov * 0.05, 2)
        m = round(aov * 0.03, 2)
        return p, m, f"AOV $1,000+  ·  5% premium  ·  3% markup"
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

col1, col2, col3 = st.columns(3)

with col1:
    orders = st.number_input("Monthly orders", min_value=1, value=10000, step=500,
                              help="Total orders shipped per month")
with col2:
    aov = st.number_input("Average order value ($)", min_value=1, value=200, step=10,
                           help="Sets the premium & markup tier automatically")
with col3:
    adopt = st.number_input("Adoption rate (%)", min_value=1, max_value=100, value=60, step=1,
                             help="Buyers who opt in to shipping protection at checkout")

auto_premium, auto_markup, tier_label = get_tier(aov)

st.markdown('<p class="divider-label">Auto-filled from AOV — override if needed</p>', unsafe_allow_html=True)

col4, col5 = st.columns(2)
with col4:
    premium = st.number_input("Protection premium — buyer pays ($)", min_value=0.01,
                               value=float(auto_premium), step=0.01, format="%.2f",
                               help="What the buyer pays at checkout")
with col5:
    markup = st.number_input("Markup per insured order ($)", min_value=0.01,
                              value=float(auto_markup), step=0.01, format="%.2f",
                              help="Your earnings per protected order")

st.markdown(f'<div class="tier-pill">● &nbsp; {tier_label}</div>', unsafe_allow_html=True)

st.markdown("---")

insured  = round(orders * adopt / 100)
rev_mo   = insured * markup
rev_ann  = rev_mo * 12
gmv      = orders * aov
pct      = (rev_mo / gmv * 100) if gmv > 0 else 0

st.markdown('<p class="section-label">Breakdown</p>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Revenue / month</div>
      <div class="metric-value">{fmt(rev_mo)}</div>
      <div class="metric-sub">from Parcelis markup</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Revenue / year</div>
      <div class="metric-value">{fmt(rev_ann)}</div>
      <div class="metric-sub">annualised</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">GMV uplift %</div>
      <div class="metric-value">{pct:.2f}%</div>
      <div class="metric-sub">of total GMV</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("See full calculation breakdown"):
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Orders insured / mo", f"{insured:,}")
    d2.metric("Premium / order", f"${premium:.2f}")
    d3.metric("Monthly GMV", fmt(gmv))
    d4.metric("Markup / order", f"${markup:.2f}")


st.markdown("---")
st.markdown('<p class="section-label">Annual revenue comparison</p>', unsafe_allow_html=True)

base_ann   = round(gmv * 12)
with_ann   = round(gmv * 12 + rev_ann)
uplift_ann = round(rev_ann)

labels = ["Without Parcelis", "With Parcelis"]

fig = go.Figure()

fig.add_trace(go.Bar(
    name="Annual revenue",
    x=labels,
    y=[base_ann, with_ann],
    marker_color=["#dcddf9", "#0D7A4A"],
    marker_line_width=0,
    width=0.4,
    yaxis="y",
    text=[f"${base_ann/1000:.1f}k" if base_ann < 1_000_000 else f"${base_ann/1_000_000:.2f}M",
          f"${with_ann/1000:.1f}k" if with_ann < 1_000_000 else f"${with_ann/1_000_000:.2f}M"],
    textposition="outside",
    textfont=dict(size=12, color="#0c0d2e"),
))

fig.add_trace(go.Scatter(
    name="GMV uplift",
    x=labels,
    y=[0, uplift_ann],
    mode="lines+markers+text",
    line=dict(color="#4547d4", width=2.5),
    marker=dict(color="#4547d4", size=8, line=dict(color="#fff", width=2)),
    fill="tozeroy",
    fillcolor="rgba(69,71,212,0.07)",
    yaxis="y2",
    text=["", f"+${uplift_ann/1000:.1f}k" if uplift_ann < 1_000_000 else f"+${uplift_ann/1_000_000:.2f}M"],
    textposition="top center",
    textfont=dict(size=12, color="#4547d4"),
))

fig.update_layout(
    plot_bgcolor="#f6f6fd",
    paper_bgcolor="#f6f6fd",
    font=dict(family="DM Sans, sans-serif", color="#0c0d2e"),
    height=340,
    margin=dict(l=0, r=0, t=40, b=0),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
        font=dict(size=11), bgcolor="rgba(0,0,0,0)"
    ),
    xaxis=dict(
        showgrid=False, zeroline=False,
        tickfont=dict(size=13, color="rgba(12,13,46,0.6)"),
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(12,13,46,0.06)", zeroline=False,
        tickfont=dict(size=10, color="rgba(12,13,46,0.4)"),
        tickprefix="$",
        title=dict(text="Annual revenue", font=dict(size=10, color="rgba(12,13,46,0.4)")),
    ),
    yaxis2=dict(
        overlaying="y", side="right", showgrid=False, zeroline=False,
        tickfont=dict(size=10, color="#4547d4"),
        tickprefix="$",
        title=dict(text="GMV uplift", font=dict(size=10, color="#4547d4")),
        range=[0, uplift_ann * 4],
    ),
    bargap=0.5,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="footer-text">
  Powered by <a href="https://myparcelis.com" target="_blank">Parcelis</a>
  &nbsp;·&nbsp; Underwritten by InsureShip &nbsp;·&nbsp; Zero cost to merchant
</div>
""", unsafe_allow_html=True)
