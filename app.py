import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Parcelis · Revenue Calculator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None}
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="st-"], p, label, div, span {
    font-family: 'DM Sans', sans-serif !important;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stHeader"] { visibility: hidden !important; display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp > header { display: none !important; }
.block-container { padding-top: 1.5rem !important; max-width: 820px !important; }

/* ── Brand header ── */
.brand-bar {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 4px;
}
.brand-name {
    font-size: 20px; font-weight: 600; color: #2626AE; letter-spacing: -0.02em;
}
.brand-sub {
    font-size: 12px; color: #6C757D; margin-top: 2px;
}

/* ── Section label ── */
.sec-label {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important; font-weight: 500 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #6C757D !important; margin-bottom: 10px !important;
}

/* ── Primary input cards ── */
.input-card {
    background: #fff;
    border: 1.5px solid #2626AE;
    border-radius: 12px;
    padding: 20px 20px 14px;
}
.input-card-label {
    font-size: 11px; font-weight: 600; letter-spacing: 0.07em;
    text-transform: uppercase; color: #2626AE; margin-bottom: 6px;
}
.input-card-hint {
    font-size: 11px; color: #9496ea; margin-top: 4px;
}

/* ── Auto-fill pills ── */
.auto-row {
    background: #EEEEFF;
    border: 1px solid #B0B0E8;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex; gap: 24px; flex-wrap: wrap; align-items: center;
}
.auto-item { text-align: center; }
.auto-item .al { font-size: 10px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9496ea; margin-bottom: 3px; }
.auto-item .av { font-family: 'DM Mono', monospace; font-size: 16px;
    font-weight: 500; color: #2626AE; }
.auto-divider { width: 1px; height: 32px; background: #B0B0E8; }
.auto-note { font-size: 11px; color: #9496ea; margin-left: auto; font-style: italic; }

/* ── Result metric cards ── */
.mc {
    background: #EDFAF4; border: 1px solid #A8E6CA;
    border-radius: 12px; padding: 22px 16px; text-align: center;
}
.mc .lbl { font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #0A6640; margin-bottom: 10px; }
.mc .val { font-family: 'DM Mono', monospace; font-size: 30px;
    font-weight: 500; color: #0D7A4A; line-height: 1.1; }
.mc .sub { font-size: 11px; color: #0A6640; opacity: 0.65; margin-top: 6px; }

/* ── Breakdown cards ── */
.bc {
    background: rgba(69,71,212,0.08); border: 1px solid rgba(69,71,212,0.2);
    border-radius: 8px; padding: 12px 10px; text-align: center;
}
.bc .lbl { font-size: 10px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9496ea; margin-bottom: 6px; }
.bc .val { font-family: 'DM Mono', monospace; font-size: 18px;
    font-weight: 500; color: #bdbef4; }

/* ── Override expander ── */
[data-testid="stExpander"] summary {
    padding-left: 1.5rem !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    font-size: 12px !important; font-weight: 600 !important;
    color: #9496ea !important;
}

/* ── Number inputs ── */
input[type="number"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 15px !important; font-weight: 500 !important;
}
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    background: rgba(69,71,212,0.15) !important;
    border: 1px solid rgba(69,71,212,0.3) !important;
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


# ── HELPERS ──
def get_adoption(aov):
    if aov < 50:     return 30, "<$50"
    elif aov < 200:  return 45, "$50–200"
    elif aov < 400:  return 55, "$200–400"
    elif aov < 600:  return 65, "$400–600"
    elif aov < 1000: return 75, "$600–1000"
    else:            return 80, "$1000+"

def get_tier(aov):
    if aov >= 1000:
        p = round(aov * 0.05, 2)
        m = round(aov * 0.03, 2)
        return p, m
    base, step = 2.50, 1.25
    bucket = max(0, int((aov - 200) / 100)) if aov >= 200 else 0
    extra  = (bucket + 1) * step if aov >= 200 else 0
    p = round(base + extra, 2)
    m = round(p * 0.60, 2)
    return p, m

def fmt(n):
    n = round(n)
    if n >= 1_000_000: return f"${n/1_000_000:.2f}M"
    if n >= 1_000:     return f"${n/1_000:.1f}k"
    return f"${n:,}"


# ── HEADER ──
st.markdown("""
<div class="brand-bar">
  <span style="font-size:22px;">🛡️</span>
  <span class="brand-name">Parcelis</span>
  <span style="color:#B0B0E8; margin: 0 4px;">·</span>
  <span class="brand-sub">Revenue Calculator</span>
</div>
<div class="brand-sub" style="margin-bottom:20px;">
  Underwritten by InsureShip &nbsp;·&nbsp; Zero cost to merchant &nbsp;·&nbsp; Native on Shopify
</div>
""", unsafe_allow_html=True)

st.divider()

# ── STEP 1: TWO PRIMARY INPUTS ──
st.markdown('<div class="sec-label">Step 1 — Tell us about your store</div>', unsafe_allow_html=True)
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="input-card-label">📦 Monthly orders</div>', unsafe_allow_html=True)
    orders = st.number_input(
        "Monthly orders", min_value=1, value=10000, step=500,
        label_visibility="collapsed",
        help="Total orders shipped per month"
    )
    st.markdown('<div class="input-card-hint">Orders shipped per month</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="input-card-label">💵 Average order value (USD)</div>', unsafe_allow_html=True)
    aov = st.number_input(
        "Average order value", min_value=1, value=200, step=10,
        key="aov_input", label_visibility="collapsed",
        help="Your store's average order value in USD"
    )
    st.markdown('<div class="input-card-hint">Used to auto-calculate everything below</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── AUTO-FILLS ──
auto_adopt, adopt_label = get_adoption(aov)
auto_premium, auto_markup = get_tier(aov)

st.markdown('<div class="sec-label">Auto-calculated from your AOV</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="auto-row">
  <div class="auto-item">
    <div class="al">Adoption rate</div>
    <div class="av">{auto_adopt}%</div>
  </div>
  <div class="auto-divider"></div>
  <div class="auto-item">
    <div class="al">Buyer premium</div>
    <div class="av">${auto_premium:.2f}</div>
  </div>
  <div class="auto-divider"></div>
  <div class="auto-item">
    <div class="al">Your markup</div>
    <div class="av">${auto_markup:.2f} / order</div>
  </div>
  <div class="auto-divider"></div>
  <div class="auto-item">
    <div class="al">AOV tier</div>
    <div class="av">{adopt_label}</div>
  </div>
  <div class="auto-note">Override below if needed ↓</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── OVERRIDES (COLLAPSED) ──
with st.expander("⚙️  Advanced — override auto-calculated values"):
    st.caption("These are pre-filled based on your AOV. Change only if you have specific data.")
    oc1, oc2, oc3 = st.columns(3)
    with oc1:
        st.markdown("**Adoption rate (%)**")
        adopt = st.number_input(
            "Adoption rate", min_value=1, max_value=100,
            value=int(auto_adopt), step=1, label_visibility="collapsed"
        )
    with oc2:
        st.markdown("**Premium per order ($)**")
        premium = st.number_input(
            "Premium", min_value=0.01, value=float(auto_premium),
            step=0.01, format="%.2f", label_visibility="collapsed"
        )
    with oc3:
        st.markdown("**Your markup per order ($)**")
        markup = st.number_input(
            "Markup", min_value=0.01, value=float(auto_markup),
            step=0.01, format="%.2f", label_visibility="collapsed"
        )
else:
    adopt   = auto_adopt
    premium = auto_premium
    markup  = auto_markup

st.divider()

# ── CALCULATIONS ──
insured = round(orders * adopt / 100)
rev_mo  = insured * markup
rev_ann = rev_mo * 12
gmv     = orders * aov
pct     = (rev_mo / gmv * 100) if gmv > 0 else 0

# ── STEP 2: RESULTS ──
st.markdown('<div class="sec-label">Step 2 — Your Parcelis revenue potential</div>', unsafe_allow_html=True)
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"""<div class="mc">
      <div class="lbl">Monthly revenue</div>
      <div class="val">{fmt(rev_mo)}</div>
      <div class="sub">from markup on insured orders</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="mc">
      <div class="lbl">Annual revenue</div>
      <div class="val">{fmt(rev_ann)}</div>
      <div class="sub">annualised projection</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class="mc">
      <div class="lbl">GMV uplift</div>
      <div class="val">{pct:.2f}%</div>
      <div class="sub">of total monthly GMV</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ── BREAKDOWN ROW ──
st.markdown("**How we got there**")
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns(4)
with b1:
    st.markdown(f"""<div class="bc">
      <div class="lbl">Orders insured / mo</div>
      <div class="val">{insured:,}</div>
    </div>""", unsafe_allow_html=True)
with b2:
    st.markdown(f"""<div class="bc">
      <div class="lbl">Markup / order</div>
      <div class="val">${markup:.2f}</div>
    </div>""", unsafe_allow_html=True)
with b3:
    st.markdown(f"""<div class="bc">
      <div class="lbl">Monthly GMV</div>
      <div class="val">{fmt(gmv)}</div>
    </div>""", unsafe_allow_html=True)
with b4:
    st.markdown(f"""<div class="bc">
      <div class="lbl">Adoption rate</div>
      <div class="val">{adopt}%</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── CHART ──
st.markdown('<div class="sec-label">Annual revenue comparison</div>', unsafe_allow_html=True)
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

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
    name="Parcelis Revenue", x=["Parcelis Revenue"], y=[uplift_ann],
    marker=dict(color="#9496ea"), marker_line_width=0, width=0.38,
    text=[f"+{fmt(uplift_ann)}"], textposition="outside",
    textfont=dict(size=13, color="#bdbef4", family="DM Mono, monospace"),
))
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif"),
    height=340, margin=dict(l=10, r=10, t=40, b=10),
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
  &nbsp;·&nbsp; Underwritten by InsureShip
  &nbsp;·&nbsp; <a href="https://apps.shopify.com/parcelis" target="_blank">Shopify App Store</a>
  &nbsp;·&nbsp; <a href="mailto:sandeep.t@myparcelis.com">sandeep.t@myparcelis.com</a>
</div>""", unsafe_allow_html=True)
