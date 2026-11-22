"""
Tech Job Market & Salary Intelligence Platform (India)
Interactive Streamlit Business Intelligence Companion App
=========================================================
Provides an interactive replica of the 5-Page Power BI Dashboard:
  Page 1: Executive Overview
  Page 2: Role Comparison
  Page 3: Skills Intelligence & Matrix
  Page 4: Salary Intelligence
  Page 5: Geographic & Hiring Trends
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tech Job Market Intelligence (India)",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for clean, professional presentation
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)


def render_chart(fig):
    """Render Plotly chart with high-contrast, crystal-clear hover tooltips and readable labels."""
    # 1. Update layout defaults
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0F172A", family="Segoe UI, Inter, sans-serif"),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=13,
            font_color="#FFFFFF",
            font_family="Segoe UI, Inter, sans-serif",
            bordercolor="#38BDF8"
        )
    )
    # 2. Explicitly force dark background & white text on EVERY trace (Pie, Donut, Bar, etc.)
    fig.for_each_trace(lambda trace: trace.update(
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_color="#FFFFFF",
            font_size=13,
            bordercolor="#38BDF8"
        )
    ))
    st.plotly_chart(fig, use_container_width=True, theme=None)


# -----------------------------------------------------------------------------
# Data Loading with Cache
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    csv_path = "data/processed/cleaned_jobs.csv"
    if not os.path.exists(csv_path):
        st.error(f"Data file not found at {csv_path}. Please run cleaning pipeline first.")
        st.stop()
    df = pd.read_csv(csv_path)
    df["posted_date"] = pd.to_datetime(df["posted_date"])
    return df


df_all = load_data()


# -----------------------------------------------------------------------------
# Sidebar Navigation & Global Filters
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=64)
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Dashboard Page:",
    [
        "1. Executive Overview",
        "2. Role Comparison",
        "3. Skills Intelligence",
        "4. Salary Intelligence",
        "5. Geographic & Hiring Trends"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Global Slicers")

# Filter: Role
all_roles = sorted(df_all["role_category"].unique())
selected_roles = st.sidebar.multiselect("Role Category", all_roles, default=all_roles)

# Filter: City
all_cities = sorted(df_all["city"].unique())
selected_cities = st.sidebar.multiselect("Indian Tech City", all_cities, default=all_cities)

# Filter: Experience
all_exp = sorted(df_all["experience_bracket"].unique())
selected_exp = st.sidebar.multiselect("Seniority Tier", all_exp, default=all_exp)

# Filter: Company Tier
all_tiers = sorted(df_all["company_tier"].unique())
selected_tiers = st.sidebar.multiselect("Company Category", all_tiers, default=all_tiers)

# Apply Filters
df = df_all[
    (df_all["role_category"].isin(selected_roles)) &
    (df_all["city"].isin(selected_cities)) &
    (df_all["experience_bracket"].isin(selected_exp)) &
    (df_all["company_tier"].isin(selected_tiers))
].copy()

if len(df) == 0:
    st.warning("No job postings match your selected filters. Please adjust sidebar selections.")
    st.stop()


# -----------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if page == "1. Executive Overview":
    st.markdown('<div class="main-title">💼 Tech Job Market Intelligence — Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">High-level macro perspective on tech hiring demand, compensation benchmarks, and market share across India.</div>', unsafe_allow_html=True)

    # Top KPI Metrics
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Postings</div><div class="metric-value">{len(df):,}</div></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Companies</div><div class="metric-value">{df["company"].nunique():,}</div></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Average Salary</div><div class="metric-value">₹ {df["avg_salary_lpa"].mean():.1f} LPA</div></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Median Salary</div><div class="metric-value">₹ {df["avg_salary_lpa"].median():.1f} LPA</div></div>', unsafe_allow_html=True)
    with kpi5:
        top_role = df["role_category"].value_counts().index[0]
        st.markdown(f'<div class="metric-card"><div class="metric-title">Top Demanded Role</div><div class="metric-value" style="font-size:1.1rem; padding-top:0.3rem;">{top_role}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1: Role Share Donut & Salary by Role Bar
    col1, col2 = st.columns([1, 1])
    with col1:
        role_counts = df["role_category"].value_counts().reset_index()
        role_counts.columns = ["Role Category", "Total Jobs"]
        fig_role = px.pie(
            role_counts, 
            values="Total Jobs", 
            names="Role Category", 
            hole=0.45,
            title="<b>Job Distribution by Tech Role</b>",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_role.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(color="#0F172A", size=12),
            hovertemplate="<b>%{label}</b><br>Total Jobs: %{value:,}<br>Share: %{percent}<extra></extra>"
        )
        render_chart(fig_role)

    with col2:
        sal_by_role = df.groupby("role_category")["avg_salary_lpa"].mean().reset_index()
        sal_by_role.columns = ["Role Category", "Avg Salary (INR LPA)"]
        sal_by_role = sal_by_role.sort_values(by="Avg Salary (INR LPA)", ascending=True)
        fig_sal = px.bar(
            sal_by_role, 
            x="Avg Salary (INR LPA)", 
            y="Role Category", 
            orientation="h",
            text="Avg Salary (INR LPA)",
            title="<b>Average Salary Comparison by Role (₹ LPA)</b>",
            color="Avg Salary (INR LPA)",
            color_continuous_scale="Blues"
        )
        fig_sal.update_traces(texttemplate='₹%{x:.1f} LPA', textposition='outside', textfont=dict(color="#0F172A", size=12))
        render_chart(fig_sal)

    # Charts Row 2: Monthly Hiring Trend & Top Hiring Companies
    col3, col4 = st.columns([1, 1])
    with col3:
        monthly_trend = df.groupby("year_month").size().reset_index(name="Postings")
        fig_trend = px.line(
            monthly_trend, 
            x="year_month", 
            y="Postings", 
            markers=True,
            title="<b>Monthly Job Posting Trajectory (India)</b>",
            line_shape="spline"
        )
        fig_trend.update_traces(line_color="#2563EB", marker_size=8)
        render_chart(fig_trend)

    with col4:
        top_comp = df["company"].value_counts().head(10).reset_index()
        top_comp.columns = ["Company", "Openings"]
        fig_comp = px.bar(
            top_comp, 
            x="Openings", 
            y="Company", 
            orientation="h",
            title="<b>Top 10 Hiring Organizations</b>",
            color="Openings",
            color_continuous_scale="Viridis"
        )
        fig_comp.update_layout(yaxis=dict(autorange="reversed"))
        render_chart(fig_comp)


# -----------------------------------------------------------------------------
# PAGE 2: ROLE COMPARISON
# -----------------------------------------------------------------------------
elif page == "2. Role Comparison":
    st.markdown('<div class="main-title">⚖️ Cross-Role Deep-Dive Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Head-to-head comparison across SDE, Data Analyst, Data Scientist, and AI/ML Engineer.</div>', unsafe_allow_html=True)

    role_summary = df.groupby("role_category").agg(
        Postings=("job_id", "count"),
        Avg_Salary_LPA=("avg_salary_lpa", "mean"),
        Median_Salary_LPA=("avg_salary_lpa", "median"),
        Avg_Experience_Yrs=("experience_avg", "mean"),
        Min_Salary_LPA=("min_salary_lpa", "min"),
        Max_Salary_LPA=("max_salary_lpa", "max")
    ).round(2).reset_index()

    st.dataframe(
        role_summary.rename(columns={
            "role_category": "Role Category",
            "Avg_Salary_LPA": "Avg Salary (₹ LPA)",
            "Median_Salary_LPA": "Median Salary (₹ LPA)",
            "Avg_Experience_Yrs": "Avg Experience (Years)",
            "Min_Salary_LPA": "Min Salary (₹ LPA)",
            "Max_Salary_LPA": "Max Salary (₹ LPA)"
        }),
        use_container_width=True
    )

    c1, c2 = st.columns(2)
    with c1:
        # Experience distribution per role
        exp_role = pd.crosstab(df["role_category"], df["experience_bracket"], normalize="index") * 100
        fig_exp_role = px.bar(
            exp_role, 
            barmode="stack",
            title="<b>Experience Tier Breakdown by Role (%)</b>",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_exp_role.update_layout(yaxis_title="Share of Role (%)")
        render_chart(fig_exp_role)

    with c2:
        # Industry distribution per role
        ind_role = pd.crosstab(df["industry"], df["role_category"])
        fig_ind = px.bar(
            ind_role, 
            barmode="group",
            title="<b>Hiring Demand by Industry & Role</b>",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        render_chart(fig_ind)


# -----------------------------------------------------------------------------
# PAGE 3: SKILLS INTELLIGENCE
# -----------------------------------------------------------------------------
elif page == "3. Skills Intelligence":
    st.markdown('<div class="main-title">🧠 Skills Intelligence & Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Extracting technical tool demand, cross-role matrix, and high-synergy skill combinations.</div>', unsafe_allow_html=True)

    # Load skill relationships
    fjs = pd.read_csv("data/processed/fact_job_skills.csv")
    dim_skills = pd.read_csv("data/processed/dim_skills.csv")
    merged_s = fjs[fjs["job_id"].isin(df["job_id"])].merge(dim_skills, on="skill_id")
    merged_s = merged_s.merge(df[["job_id", "role_category"]], on="job_id")

    col_s1, col_s2 = st.columns([1, 1])

    with col_s1:
        top_skills = merged_s["skill_name"].value_counts().head(15).reset_index()
        top_skills.columns = ["Skill", "Mentions"]
        fig_top_s = px.bar(
            top_skills, 
            x="Mentions", 
            y="Skill", 
            orientation="h",
            title="<b>Top 15 Most Demanded Skills (Across Selected Postings)</b>",
            color="Mentions",
            color_continuous_scale="Purples"
        )
        fig_top_s.update_layout(yaxis=dict(autorange="reversed"))
        render_chart(fig_top_s)

    with col_s2:
        # Cross-role skill penetration matrix
        crosstab_s = pd.crosstab(merged_s["skill_name"], merged_s["role_category"], normalize="columns") * 100
        top_12 = top_skills["Skill"].head(12)
        crosstab_top12 = crosstab_s.loc[top_12].round(1)

        fig_matrix = px.imshow(
            crosstab_top12,
            text_auto=True,
            aspect="auto",
            title="<b>Skill Matrix: Penetration % Within Role</b>",
            color_continuous_scale="Blues"
        )
        render_chart(fig_matrix)


# -----------------------------------------------------------------------------
# PAGE 4: SALARY INTELLIGENCE
# -----------------------------------------------------------------------------
elif page == "4. Salary Intelligence":
    st.markdown('<div class="main-title">💰 Salary Intelligence & Compensation Drivers</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Understanding salary distributions, seniority premiums, and high-paying skill clusters.</div>', unsafe_allow_html=True)

    c_sal1, c_sal2 = st.columns(2)
    with c_sal1:
        fig_box = px.box(
            df, 
            x="role_category", 
            y="avg_salary_lpa", 
            color="role_category",
            title="<b>Salary Distribution & IQR Spread by Role (₹ LPA)</b>",
            points="outliers"
        )
        fig_box.update_layout(showlegend=False, xaxis_title="Role", yaxis_title="Average Salary (₹ LPA)")
        render_chart(fig_box)

    with c_sal2:
        # Company Tier Impact
        tier_sal = df.groupby(["company_tier", "role_category"])["avg_salary_lpa"].mean().reset_index()
        fig_tier = px.bar(
            tier_sal, 
            x="company_tier", 
            y="avg_salary_lpa", 
            color="role_category", 
            barmode="group",
            title="<b>Compensation by Employer Tier (₹ LPA)</b>"
        )
        fig_tier.update_layout(xaxis_title="Employer Tier", yaxis_title="Avg Salary (₹ LPA)")
        render_chart(fig_tier)

    # Scatter: Experience vs Salary
    fig_scatter = px.scatter(
        df, 
        x="experience_avg", 
        y="avg_salary_lpa", 
        color="role_category",
        trendline="ols",
        title="<b>Experience vs. Salary Correlation & Regression Fit</b>",
        labels={"experience_avg": "Years of Experience", "avg_salary_lpa": "Average Salary (₹ LPA)"}
    )
    render_chart(fig_scatter)


# -----------------------------------------------------------------------------
# PAGE 5: GEOGRAPHIC & HIRING TRENDS
# -----------------------------------------------------------------------------
elif page == "5. Geographic & Hiring Trends":
    st.markdown('<div class="main-title">🗺️ Geographic Hubs & Hiring Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Geographic breakdown of tech opportunities across Indian metropolitan centers.</div>', unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        city_stats = df.groupby("city").agg(
            Postings=("job_id", "count"),
            Avg_Salary_LPA=("avg_salary_lpa", "mean")
        ).reset_index().sort_values(by="Postings", ascending=False)

        fig_city_p = px.bar(
            city_stats, 
            x="city", 
            y="Postings", 
            text="Postings",
            color="Avg_Salary_LPA",
            color_continuous_scale="Teal",
            title="<b>Job Volume & Average Pay by Indian City</b>"
        )
        fig_city_p.update_traces(textposition="outside", textfont=dict(color="#0F172A", size=12))
        render_chart(fig_city_p)

    with g2:
        # Role share in cities
        city_role = pd.crosstab(df["city"], df["role_category"], normalize="index") * 100
        fig_city_role = px.bar(
            city_role, 
            barmode="stack",
            title="<b>Role Composition Across Indian Tech Hubs (%)</b>",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        render_chart(fig_city_role)

    # Raw Data Explorer & Download
    st.markdown("---")
    st.subheader("📥 Cleaned Data Explorer & Export")
    st.dataframe(df[["job_id", "job_title", "role_category", "company", "city", "avg_salary_lpa", "experience_bracket", "skills"]].head(100), use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="filtered_tech_jobs_india.csv",
        mime="text/csv"
    )
