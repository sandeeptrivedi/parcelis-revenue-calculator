import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Parcelis · Revenue Calculator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    }
)

# ── Hide Streamlit chrome ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="st-"], p, label, div, span {
    font-family: 'DM Sans', sans-serif !important;
}
#MainMenu { visibility: hidden !important; display: none !important; }
footer { visibility: hidden !important; display: none !important; }
header { visibility: hidden !important; display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
[data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }
[data-testid="stHeader"] { visibility: hidden !important; display: none !important; }
[data-testid="stAppViewBlockContainer"] > div:first-child { padding-top: 0 !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }
.css-18ni7ap { display: none !important; }
.css-1dp5vir { display: none !important; }
.block-container { padding-top: 1rem !important; max-width: 860px !important; }

/* Metric cards */
.mc {
    background: #EDFAF4; border: 1px solid #A8E6CA;
    border-radius: 10px; padding: 20px; text-align: center;
}
.mc .lbl {
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #0A6640; margin-bottom: 8px;
}
.mc .val {
    font-family: 'DM Mono', monospace; font-size: 28px;
    font-weight: 500; color: #0D7A4A; line-height: 1.1;
}
.mc .sub { font-size: 11px; color: #0A6640; opacity: 0.65; margin-top: 6px; }

/* Breakdown cards */
.bc {
    background: rgba(69,71,212,0.1); border: 1px solid rgba(69,71,212,0.25);
    border-radius: 8px; padding: 14px; text-align: center;
}
.bc .lbl {
    font-size: 10px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9496ea; margin-bottom: 6px;
}
.bc .val {
    font-family: 'DM Mono', monospace; font-size: 20px;
    font-weight: 500; color: #bdbef4; line-height: 1;
}

/* Tier pill */
.pill {
    background: rgba(69,71,212,0.12); border: 1px solid rgba(69,71,212,0.35);
    border-radius: 100px; padding: 6px 16px; font-size: 12px;
    font-weight: 500; color: #9496ea; display: inline-block;
    margin-top: 8px; margin-bottom: 4px;
}

/* Stepper buttons */
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    background: rgba(69,71,212,0.15) !important;
    border: 1px solid rgba(69,71,212,0.3) !important;
}
button[data-testid="stNumberInputStepUp"] svg,
button[data-testid="stNumberInputStepDown"] svg {
    fill: #9496ea !important; stroke: #9496ea !important;
}
input[type="number"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 15px !important; font-weight: 500 !important;
}

/* Expander — explicit color so it is always visible */
[data-testid="stExpander"] summary p {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #9496ea !important;
}

.footer {
    text-align: center; font-size: 11px;
    margin-top: 28px; padding-top: 14px;
    border-top: 1px solid rgba(120,121,232,0.2);
    color: rgba(148,150,234,0.6);
}
.footer a { color: #7879e8; text-decoration: none; }
</style>
""", unsafe_allow_html=True)


# ── HELPER FUNCTIONS ──
def get_adoption(aov):
    if aov < 50:       return 30, "30%",    "<$50"
    elif aov < 200:    return 45, "40-50%", "$50-200"
    elif aov < 400:    return 55, "50-60%", "$200-400"
    elif aov < 600:    return 65, "60-70%", "$400-600"
    elif aov < 1000:   return 75, "70-80%", "$600-1000"
    else:              return 80, "80%",    "$1000+"

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
    return p, m, f"AOV ${low}-{high}  ·  Premium ${p:.2f}  ·  Markup ${m:.2f} / order"

def fmt(n):
    n = round(n)
    if n >= 1_000_000: return f"${n/1_000_000:.2f}M"
    if n >= 1_000:     return f"${n/1_000:.1f}k"
    return f"${n:,}"


# ── HEADER — native Streamlit only, no custom HTML ──
col_logo, col_sub = st.columns([1, 2])
with col_logo:
    st.markdown("### 🛡️ Parcelis")
with col_sub:
    st.caption("Shipping protection · Zero cost to merchant · Underwritten by InsureShip")

st.markdown("#### How much will Parcelis add to your revenue?")
st.caption("Enter your store numbers. Premium, markup and adoption auto-fill from AOV — override anytime.")
st.divider()

# ── INPUTS TOP ──
_aov_preview = st.session_state.get("aov_input", 200)
_auto_adopt, _adopt_range, _adopt_label = get_adoption(_aov_preview)

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
                          key="aov_input", label_visibility="collapsed",
                          help="Drives premium, markup and adoption tier")
    st.caption("Drives all auto-fill tiers")
with col3:
    st.markdown("**Adoption rate (%)**")
    adopt = st.number_input("Adoption rate (%)", min_value=1, max_value=100,
                            value=int(_auto_adopt), step=1,
                            label_visibility="collapsed",
                            help="Auto-filled from AOV — override if needed")
    st.caption(f"Auto: {_adopt_range} for AOV {_adopt_label}")

# Compute auto-fills from confirmed aov
auto_premium, auto_markup, tier_label = get_tier(aov)
auto_adopt, adopt_range, adopt_aov_label = get_adoption(aov)

st.markdown("---")
st.caption("AUTO-FILLED FROM AOV — OVERRIDE IF NEEDED")

col4, col5 = st.columns(2)
with col4:
    st.markdown("**Protection premium — buyer pays ($)**")
    premium = st.number_input("Protection premium", min_value=0.01,
                              value=float(auto_premium), step=0.01, format="%.2f",
                              label_visibility="collapsed",
                              help="What the buyer pays at checkout")
    st.caption("Auto-filled · override if needed")
with col5:
    st.markdown("**Markup per insured order ($)**")
    markup = st.number_input("Markup per insured order", min_value=0.01,
                             value=float(auto_markup), step=0.01, format="%.2f",
                             label_visibility="collapsed",
                             help="Your earnings per protected order")
    st.caption("Auto-filled · override if needed")

st.markdown(f'<div class="pill">● &nbsp; {tier_label}  ·  Adoption {adopt_range}</div>',
            unsafe_allow_html=True)
st.divider()

# ── CALCULATIONS ──
insured = round(orders * adopt / 100)
rev_mo  = insured * markup
rev_ann = rev_mo * 12
gmv     = orders * aov
pct     = (rev_mo / gmv * 100) if gmv > 0 else 0

# ── METRIC CARDS ──
st.caption("BREAKDOWN")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"""<div class="mc">
      <div class="lbl">Revenue / month</div>
      <div class="val">{fmt(rev_mo)}</div>
      <div class="sub">from Parcelis markup</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="mc">
      <div class="lbl">Revenue / year</div>
      <div class="val">{fmt(rev_ann)}</div>
      <div class="sub">annualised</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class="mc">
      <div class="lbl">GMV uplift %</div>
      <div class="val">{pct:.2f}%</div>
      <div class="sub">of total GMV</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ── BREAKDOWN EXPANDER ──
with st.expander("Full calculation breakdown"):
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown(f"""<div class="bc">
          <div class="lbl">Orders insured / mo</div>
          <div class="val">{insured:,}</div>
        </div>""", unsafe_allow_html=True)
    with b2:
        st.markdown(f"""<div class="bc">
          <div class="lbl">Premium / order</div>
          <div class="val">${premium:.2f}</div>
        </div>""", unsafe_allow_html=True)
    with b3:
        st.markdown(f"""<div class="bc">
          <div class="lbl">Monthly GMV</div>
          <div class="val">{fmt(gmv)}</div>
        </div>""", unsafe_allow_html=True)
    with b4:
        st.markdown(f"""<div class="bc">
          <div class="lbl">Markup / order</div>
          <div class="val">${markup:.2f}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

st.divider()

# ── CHART ──
st.caption("ANNUAL REVENUE COMPARISON")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

base_ann   = round(gmv * 12)
with_ann   = round(gmv * 12 + rev_ann)
uplift_ann = max(round(rev_ann), 1)

fig = go.Figure()
fig.add_trace(go.Bar(
    name="Without Parcelis", x=["Without Parcelis"], y=[base_ann],
    marker=dict(color="#4547d4"), marker_line_width=0, width=0.38,
    text=[fmt(base_ann)], textposition="outside",
    textfont=dict(size=13, color="#9496ea", family="DM Mono, monospace"),
))
fig.add_trace(go.Bar(
    name="With Parcelis", x=["With Parcelis"], y=[with_ann],
    marker=dict(color="#0D7A4A"), marker_line_width=0, width=0.38,
    text=[fmt(with_ann)], textposition="outside",
    textfont=dict(size=13, color="#5DCAA5", family="DM Mono, monospace"),
))
fig.add_trace(go.Bar(
    name="GMV Uplift", x=["GMV Uplift"], y=[uplift_ann],
    marker=dict(color="#9496ea"), marker_line_width=0, width=0.38,
    text=[f"+{fmt(uplift_ann)}"], textposition="outside",
    textfont=dict(size=13, color="#bdbef4", family="DM Mono, monospace"),
))
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif"),
    height=360, margin=dict(l=10, r=10, t=50, b=10),
    showlegend=False,
    xaxis=dict(showgrid=False, zeroline=False,
               tickfont=dict(size=13, family="DM Sans, sans-serif")),
    yaxis=dict(showgrid=True, gridcolor="rgba(120,121,232,0.15)",
               zeroline=False, tickprefix="$",
               range=[0, max(with_ann * 1.28, 1)]),
    bargap=0.3,
)
st.plotly_chart(fig, use_container_width=True)

# ── FOOTER ──
st.markdown("""<div class="footer">
  Powered by <a href="https://myparcelis.com" target="_blank">Parcelis</a>
  &nbsp;·&nbsp; Underwritten by InsureShip &nbsp;·&nbsp; Zero cost to merchant
</div>""", unsafe_allow_html=True)
