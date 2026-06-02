import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
            
/* 🔥 FIX: Remove Streamlit default spacing */
header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 0rem !important;
}

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #ffffff;
    color: #1a1a2e;
}
.main { background-color: #ffffff; }
.block-container {
    padding: 0rem 2rem 2rem 2rem !important;
    max-width: 100% !important;  
}

/* ── Dashboard header ── */
.dash-header {
    display: flex;
    align-items: center;
    gap: 12px;

    padding: 12px 0 16px 0;
    margin-top: 0px;   /* 🔥 fix */
    margin-bottom: 12px;

    border-bottom: 1.5px solid #e8eaf0;

    position: relative;
    z-index: 999;

    background: #ffffff;  /* 🔥 ensures visibility */
}

/* Logo FIX */
.dash-logo {
    width: 42px;
    height: 42px;
    min-width: 42px;

    background: #2563EB;
    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    flex-shrink: 0;

    position: relative;
    z-index: 1000;
}

/* Logo text */
.dash-logo span {
    color: #ffffff;
    font-size: 16px;
    font-weight: 800;
    line-height: 1;
}

/* Title block */
.dash-title-block {
    flex: 1;
    min-width: 0;
}

/* Title FIX */
.dash-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.3;

    white-space: normal;
    word-break: break-word;

    /* 🔥 Prevent hiding */
    overflow: visible;
}

/* Subtitle */
.dash-sub {
    font-size: 0.7rem;
    color: #6b7280;
    margin-top: 2px;
}

/* ── KPI cards ── */
.kpi-card {
    background: #ffffff;
    border: 1.5px solid #e8eaf0;
    border-radius: 12px;
    padding: 12px 16px;
    text-align: center;
    box-shadow: 0 2px 6px #0000000a;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.68rem;
    color: #6b7280;
    font-weight: 500;
    margin-top: 3px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #f3f4f6;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 6px 18px;
    font-weight: 500;
    font-size: 0.83rem;
    color: #6b7280;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #1a1a2e !important;
    box-shadow: 0 1px 4px #0000001a;
}

hr { border: none; border-top: 1.5px solid #f0f1f5; margin: 0.8rem 0 1rem 0; }

/* 📱 Mobile Responsive */
@media (max-width: 768px) {
    .dash-header {
        flex-direction: row;
        align-items: center;
        gap: 8px;
    }

    .dash-logo {
        width: 38px;
        height: 38px;
        min-width: 38px;
    }

    .dash-title {
        font-size: 0.95rem;
    }

    .dash-sub {
        font-size: 0.6rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Colour palette (hex only – no rgba) ───────────────────────────────────────
C = {
    "blue1":  "#2563EB",
    "blue2":  "#3B82F6",
    "blue3":  "#60A5FA",
    "blue4":  "#93C5FD",
    "navy":   "#1E3A8A",
    "orange": "#F97316",
    "purple": "#7C3AED",
    "green":  "#10B981",
    "red":    "#EF4444",
    "gray":   "#9CA3AF",
    "bg":     "#ffffff",
    "grid":   "#F3F4F6",
}

DEPT_COLORS   = [C["blue2"], C["navy"], C["orange"]]
SALARY_COLORS = [C["blue2"], C["blue3"], C["blue1"], C["navy"]]

BASE_LAYOUT = dict(
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["bg"],
    font=dict(family="DM Sans, sans-serif", color="#374151", size=11),
    margin=dict(l=10, r=10, t=36, b=10),
)


def apply_layout(fig, title="", height=280):
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(size=13, color="#1a1a2e",
                                         family="DM Sans, sans-serif")),
        height=height,
        showlegend=False,
    )
    fig.update_xaxes(showgrid=True, gridcolor=C["grid"], zeroline=False,
                     tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor=C["grid"], zeroline=False,
                     tickfont=dict(size=10))
    return fig


def kpi(val, label, color="#1a1a2e"):
    return f"""
    <div class="kpi-card">
        <div class="kpi-value" style="color:{color}">{val}</div>
        <div class="kpi-label">{label}</div>
    </div>"""


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview():
    kpis = [
        ("1470",  "Total Employees"),
        ("1233",  "Active Employees"),
        ("7.01",  "Avg Tenure"),
        ("237",   "Total Attritions"),
        ("28.30", "Overtime Rate"),
        ("6.50K", "Avg Monthly Income"),
        ("416",   "Overtime Employees"),
        ("36.92", "Avg Age"),
        ("16.12", "Attrition Rate"),
    ]
    cols = st.columns(3)  # max 3 per row
    for i, (val, label) in enumerate(kpis):
      cols[i % 3].markdown(kpi(val, label), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(
            x=["No", "Yes"], y=[1054, 416],
            marker_color=[C["blue2"], C["blue3"]], width=0.5,
        ))
        apply_layout(fig, "Total Employees by OverTime")
        fig.update_layout(xaxis_title="OverTime", yaxis_title="Total Employees")
        st.plotly_chart(fig, use_container_width=True, key="ov_overtime")

    with c2:
        sal_labels = ["Medium (3–6K)", "Low (<3K)", "Very High (10K+)", "High (6–10K)"]
        sal_vals   = [543, 383, 278, 266]
        fig = go.Figure(go.Bar(
            x=sal_labels, y=sal_vals,
            marker_color=SALARY_COLORS, width=0.55,
        ))
        apply_layout(fig, "Total Employees by SalaryBand")
        fig.update_layout(xaxis_title="SalaryBand", yaxis_title="Total Employees")
        st.plotly_chart(fig, use_container_width=True, key="ov_salaryband")

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        age_bands = ["26–35", "36–45", "46–55", "18–25", "55+"]
        age_vals  = [588, 472, 221, 112, 77]
        fig = go.Figure(go.Bar(
            y=age_bands, x=age_vals, orientation="h",
            marker_color=[C["blue1"], C["blue2"], C["blue3"], C["blue4"], C["navy"]],
            width=0.6,
        ))
        apply_layout(fig, "Total Employees by AgeBand")
        fig.update_layout(xaxis_title="Total Employees", yaxis_title="AgeBand")
        st.plotly_chart(fig, use_container_width=True, key="ov_ageband")

    with c4:
        dept_labels = ["Research & Development", "Sales", "Human Resources"]
        dept_vals   = [133, 92, 12]
        fig = go.Figure(go.Pie(
            labels=dept_labels, values=dept_vals,
            hole=0.52,
            marker_colors=DEPT_COLORS,
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        apply_layout(fig, "Total Attritions by Department", height=300)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)),
        )
        st.plotly_chart(fig, use_container_width=True, key="ov_dept_pie")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – ATTRITION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_attrition():
    c_kpi1, _ = st.columns([1, 4])
    with c_kpi1:
        st.markdown(kpi("1470", "High Risk Employees"), unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(kpi("1.46", "Avg Risk Score"), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        roles = ["Sales Representative", "Laboratory Technician", "Human Resources",
                 "Sales Executive", "Research Scientist", "Manufacturing Director",
                 "Healthcare Representative", "Manager", "Research Director"]
        rates = [39.8, 23.9, 23.1, 17.5, 16.1, 10.3, 9.8, 5.1, 2.5]
        colors = [C["blue1"] if r > 20 else C["blue2"] if r > 10 else C["blue3"]
                  for r in rates]
        fig = go.Figure(go.Bar(
            y=roles, x=rates, orientation="h",
            marker_color=colors, width=0.65,
        ))
        apply_layout(fig, "Attrition Rate by JobRole", height=310)
        fig.update_layout(xaxis_title="Attrition Rate", yaxis_title="JobRole",
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True, key="att_jobrole")

    with c2:
        fig = go.Figure(go.Bar(
            x=["Yes", "No"], y=[30.5, 10.4],
            marker_color=[C["blue1"], C["blue3"]], width=0.45,
        ))
        apply_layout(fig, "Attrition Rate by OverTime")
        fig.update_layout(xaxis_title="OverTime", yaxis_title="Attrition Rate")
        st.plotly_chart(fig, use_container_width=True, key="att_overtime")

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        depts = ["Sales", "Human Resources", "Research &\nDevelopment"]
        dept_rates = [20.6, 19.0, 13.8]
        fig = go.Figure(go.Bar(
            x=depts, y=dept_rates,
            marker_color=[C["blue1"], C["blue2"], C["blue3"]], width=0.5,
        ))
        apply_layout(fig, "Attrition Rate by Department")
        fig.update_layout(xaxis_title="Department", yaxis_title="Attrition Rate")
        st.plotly_chart(fig, use_container_width=True, key="att_dept")

    with c4:
        tenure_bands = ["0–2 yrs", "3–5 yrs", "6–10 yrs", "20+ yrs", "11–20 yrs"]
        tenure_rates = [29.8, 14.0, 12.6, 12.1, 6.4]
        fig = go.Figure(go.Bar(
            x=tenure_bands, y=tenure_rates,
            marker_color=[C["blue1"], C["blue2"], C["blue3"], C["blue4"], C["navy"]],
            width=0.55,
        ))
        apply_layout(fig, "Attrition Rate by TenureBand")
        fig.update_layout(xaxis_title="TenureBand", yaxis_title="Attrition Rate")
        st.plotly_chart(fig, use_container_width=True, key="att_tenure")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – SALARY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_salary():
    kpis = [
        ("17.18K", "Max Role Income"),
        ("2.63K",  "Min Role Income"),
        ("14.56K", "Salary Gap"),
        ("15.21",  "Avg Salary Hike"),
    ]
    cols = st.columns(len(kpis))
    for col, (val, label) in zip(cols, kpis):
        col.markdown(kpi(val, label), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        sal_bands = ["Low (<3K)", "Medium (3–6K)", "High (6–10K)", "Very High (10K+)"]
        att_rates = [29.4, 11.8, 10.9, 6.7]
        fig = go.Figure(go.Bar(
            x=sal_bands, y=att_rates,
            marker_color=[C["blue1"], C["blue2"], C["blue3"], C["blue4"]], width=0.55,
        ))
        apply_layout(fig, "Attrition Rate by SalaryBand")
        fig.update_layout(xaxis_title="SalaryBand", yaxis_title="Attrition Rate")
        st.plotly_chart(fig, use_container_width=True, key="sal_attrition")

    with c2:
        gap_bands = ["Very High (10K+)", "Medium (3–6K)", "High (6–10K)", "Low (<3K)"]
        gaps      = [6200, 1400, 1300, 100]
        fig = go.Figure(go.Bar(
            x=gap_bands, y=gaps,
            marker_color=[C["blue1"], C["blue2"], C["blue3"], C["navy"]], width=0.55,
        ))
        apply_layout(fig, "Salary Gap by SalaryBand")
        fig.update_layout(xaxis_title="SalaryBand", yaxis_title="Salary Gap")
        st.plotly_chart(fig, use_container_width=True, key="sal_gap")

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        labels = ["Low (<3K)", "Medium (3–6K)", "High (6–10K)", "Very High (10K+)"]
        vals   = [113, 66, 33, 25]
        fig = go.Figure(go.Pie(
            labels=labels, values=vals,
            hole=0.52,
            marker_colors=[C["blue2"], C["navy"], C["orange"], C["purple"]],
            textinfo="percent+label",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        apply_layout(fig, "Total Attritions by SalaryBand", height=300)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)),
        )
        st.plotly_chart(fig, use_container_width=True, key="sal_att_pie")

    with c4:
        emp_labels = ["Medium (3–6K)", "Low (<3K)", "Very High (10K+)", "High (6–10K)"]
        emp_vals   = [543, 383, 278, 266]
        fig = go.Figure(go.Bar(
            x=emp_labels, y=emp_vals,
            marker_color=SALARY_COLORS, width=0.55,
        ))
        apply_layout(fig, "Total Employees by SalaryBand")
        fig.update_layout(xaxis_title="SalaryBand", yaxis_title="Total Employees")
        st.plotly_chart(fig, use_container_width=True, key="sal_emp")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – ROI SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
def page_roi():
    st.markdown("### 🔮 Salary Increase ROI Simulator")
    st.markdown("Adjust the salary increase % to see predicted impact on attrition and ROI.")
    st.markdown("<hr>", unsafe_allow_html=True)

    salary_pct = st.slider("Salary Increase %", min_value=0, max_value=50,
                            value=11, step=1, key="roi_slider")

    baseline_attrition  = 16.12
    predicted_attrition = max(0.0, round(baseline_attrition - salary_pct * 0.129, 2))
    employees_retained  = round((baseline_attrition - predicted_attrition) / 100 * 1470, 2)
    cost_per_hire       = 50000
    salary_cost_increase = 1470 * 6500 * 12 * (salary_pct / 100)
    annual_savings       = employees_retained * cost_per_hire
    net_roi              = annual_savings - salary_cost_increase

    def fmt(v):
        if abs(v) >= 1_000_000:
            return f"{v/1_000_000:+.2f}M"
        if abs(v) >= 1_000:
            return f"{v/1_000:.2f}K"
        return f"{v:.2f}"

    roi_color = C["green"] if net_roi > 0 else C["red"]

    c1, sp, c2 = st.columns([2, 0.3, 2])
    with c1:
        st.markdown(kpi(baseline_attrition, "Baseline Attrition Rate"),
                    unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(kpi(fmt(annual_savings), "Annual Savings", C["green"]),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(kpi(predicted_attrition, "Predicted Attrition Rate", C["blue1"]),
                    unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(kpi(fmt(net_roi), "Net ROI", roi_color),
                    unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(kpi(employees_retained, "Employees Retained"),
                    unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Sensitivity curve
    pct_range     = list(range(0, 51))
    pred_range    = [max(0, baseline_attrition - p * 0.129) for p in pct_range]
    savings_range = [(baseline_attrition - pr) / 100 * 1470 * cost_per_hire
                     for pr in pred_range]
    roi_range     = [s - 1470 * 6500 * 12 * (p / 100)
                     for s, p in zip(savings_range, pct_range)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pct_range, y=pred_range,
        name="Predicted Attrition %",
        line=dict(color=C["blue1"], width=2.5),
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=pct_range, y=[r / 1_000_000 for r in roi_range],
        name="Net ROI (M)",
        line=dict(color=C["orange"], width=2.5, dash="dash"),
        yaxis="y2",
    ))
    fig.add_vline(x=salary_pct, line_dash="dot", line_color=C["gray"],
                  annotation_text=f"{salary_pct}%",
                  annotation_position="top right")
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Attrition & ROI Sensitivity",
                   font=dict(size=13, color="#1a1a2e")),
        height=300,
        showlegend=True,
        legend=dict(x=0.75, y=0.95, font=dict(size=10)),
        yaxis=dict(title="Attrition Rate (%)", gridcolor=C["grid"]),
        yaxis2=dict(title="Net ROI (M)", overlaying="y", side="right",
                    gridcolor=C["grid"]),
    )
    fig.update_xaxes(title_text="Salary Increase %", gridcolor=C["grid"])
    st.plotly_chart(fig, use_container_width=True, key="roi_sensitivity")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN – Header + Tabs
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="dash-header">
    <div class="dash-logo"><span>HR</span></div>
    <div class="dash-title-block">
        <div class="dash-title">People Insights • Powered by Streamlit</div>
        <div class="dash-sub">HR Analytics Dashboard &nbsp;|&nbsp; Workforce Intelligence Platform</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📉 Attrition Analysis",
    "💰 Salary Analysis",
    "🔮 ROI Simulator",
])

with tab1:
    page_overview()

with tab2:
    page_attrition()

with tab3:
    page_salary()

with tab4:
    page_roi()