import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import numpy as np
import plotly.graph_objects as go

# ─── 1) Page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tobacco & Mortality – WHO Dashboard",
    layout="wide",
)
st.title("Effects of Tobacco on Tracheal, Bronchus, and Lung Cancer Mortality")

# ─── 2) Loaders ─────────────────────────────────────────────────────────
@st.cache_data
def load_tobacco(path, indicators):
    df = pd.read_excel(path, sheet_name="Sheet1")
    df = df[
        df["indicator_name"].isin(indicators)
        & df["subgroup"].isin(["Male", "Female"])
    ]

    return (
        df.rename(columns={
            "setting":   "country",
            "date":      "year",
            "subgroup":  "sex",
            "estimate":  "prevalence"
        })
        .assign(year=lambda d: d.year.astype(int))
    )

@st.cache_data
def load_mortality(path):
    indicators = ["2.A.05 Tracheal, bronchus, and lung cancer incidence (age standardized) (per 100 000 population)"]
    df = pd.read_excel(path, sheet_name="Sheet1")
    df = df[df["indicator_name"].isin(indicators) & df["subgroup"].isin(["Male", "Female"])]
    return (
        df.rename(columns={
            "setting":   "country",
            "date":      "year",
            "subgroup":  "sex",
            "estimate":  "mortality"
        })
        .assign(year=lambda d: d.year.astype(int))
    )

# ─── 3) Read data ───────────────────────────────────────────────────────
tob_path = Path(r"./data/rep_gho_tobacco/data.xlsx")                
mor_path = Path(r"./data/rep_ihme_inc/data.xlsx")

df_tob = load_tobacco(tob_path, ["Estimate of current tobacco use prevalence (age-standardized) (%)"])
df_mor = load_mortality(mor_path)

# ─── 4) In‐page Country selector & KPI panel ────────────────────────────
left, mid, right = st.columns([1,2,1], gap="large")

with left:
    country = st.selectbox(
        "Select Country",
        sorted(df_tob.country.unique()),
        index=sorted(df_tob.country.unique()).index("Lebanon")
            if "Lebanon" in df_tob.country.unique() else 0
    )
    # apply filter
    tob = df_tob[df_tob.country == country]
    mor = df_mor[df_mor.country == country]

    st.markdown("##### Key Metrics")
    # compute per‐sex averages
    male_prev   = tob.loc[tob.sex=="Male",    "prevalence"].mean()
    female_prev = tob.loc[tob.sex=="Female",  "prevalence"].mean()
    male_mort   = mor.loc[mor.sex=="Male",    "mortality"].mean()
    female_mort = mor.loc[mor.sex=="Female",  "mortality"].mean()

    # show them in a 2×2 grid
    for label, val in [
        (f"{country} Male Prevalence (%)",   f"{male_prev:.2f}"),
        (f"{country} Female Prevalence (%)", f"{female_prev:.2f}"),
        (f"{country} Male Mortality (per 100 000)",   f"{male_mort:,.0f}"),
        (f"{country} Female Mortality (per 100 000)", f"{female_mort:,.0f}")
    ]:
        st.markdown(f"""
        <div style="margin:4px 0;">
        <div style="font-size:14px; color:#444;">{label}</div>
        <div style="font-size:32px; font-weight:600; line-height:1;">{val}</div>
        </div>
        """, unsafe_allow_html=True)

with mid:
    map_df = (
        df_mor.groupby(["country","iso3"],as_index=False)
              .mortality.mean()
              .rename(columns={"mortality":"avg_prev"})
    )
    fig_map = px.choropleth(
        map_df, locations="iso3", color="avg_prev", hover_name="country",
        color_continuous_scale="Reds", labels={"avg_prev":"Deaths per 100k"},
        height=400
    )
    fig_map.update_layout(
        title_text="Tracheal, Bronchus & Lung Cancer Mortality Rates",
        title_x=0,             
        title_font=dict(size=20),   
        margin=dict(l=0, r=0, t=40, b=0), 
        coloraxis_colorbar=dict(thickness=15, len=0.5, y=0.5)
    )
    st.plotly_chart(fig_map, use_container_width=True)


with right:
    st.markdown(
    "<span style='font-size:16px; font-weight:600;'>Tobacco Prevalence by Income Group</span>",
    unsafe_allow_html=True
    )
    grp_prev = (
        df_tob.groupby("wbincome2024", as_index=False)
           .prevalence.mean()
           .rename(columns={"wbincome2024":"group","prevalence":"value"})
    )
    fig1 = px.pie(
        grp_prev, names="group", values="value", hole=0.4,
        labels={"group":"Income","value":"Avg %"}
    )
    fig1.update_traces(textinfo="percent", textposition="inside")
    # increase the height and trim margins
    fig1.update_layout(
        height=100,
        margin=dict(t=1, b=1, l=1, r=1)
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown(
    "<span style='font-size:16px; font-weight:600;'>Mortality by Income Group</span>",
    unsafe_allow_html=True
    )
    grp_mor = (
        df_mor.groupby("wbincome2023", as_index=False)
           .mortality.mean()
           .rename(columns={"wbincome2023":"group","mortality":"value"})
    )
    fig2 = px.pie(
        grp_mor, names="group", values="value", hole=0.4,
        labels={"group":"Income","value":"Avg deaths/100 000"}
    )
    fig2.update_traces(textinfo="percent", textposition="inside")
    # increase the height and trim margins
    fig2.update_layout(
        height=100,
        margin=dict(t=1, b=1, l=1, r=1)
    )
    st.plotly_chart(fig2, use_container_width=True)

# ─── 5) Top-10 Countries row ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4, gap="small")

# 1) Top-10 Prevalence
with col1:
    st.markdown("**Top 5 Countries with Highest Tobacco Use**")
    top_prev = (
        df_tob.groupby("country", as_index=False)
              .prevalence.mean()
              .nlargest(5, "prevalence")
    )
    fig_tp = px.bar(
        top_prev,
        x="prevalence", y="country",
        orientation="h",
        labels={"prevalence":"Avg %","country":""},
        height=200,
        text="prevalence",   
        text_auto=".1f",      
    )

    fig_tp.update_traces(
        textposition="inside",            
        texttemplate="%{text:.1f}%",     
        insidetextanchor="middle",
        marker_color="#1f77b4",
    )

    fig_tp.update_layout(
        margin=dict(l=1, r=1, t=1, b=1),
        yaxis={"categoryorder":"total ascending"},
        font=dict(size=10)
    )

    st.plotly_chart(fig_tp, use_container_width=True)

# 2) Top-10 Mortality
with col2:
    st.markdown("**Top 5 Countries with Highest Mortality**")
    top_mor = (
        df_mor.groupby("country", as_index=False)
              .mortality.mean()
              .nlargest(5, "mortality")
    )
    fig_tm = px.bar(
        top_mor,
        x="mortality", y="country",
        orientation="h",
        labels={"mortality":"Deaths/100 000","country":""},
        height=200,
        text="mortality",
        text_auto=".0f",       # integer formatting
    )

    fig_tm.update_traces(
        textposition="inside",
        texttemplate="%{text:.0f}",
        insidetextanchor="middle",
        marker_color="#1f77b4",
    )

    fig_tm.update_layout(
        margin=dict(l=1, r=1, t=1, b=1),
        yaxis={"categoryorder":"total ascending"},
        font=dict(size=10)
    )

    st.plotly_chart(fig_tm, use_container_width=True)

# 3) Prevalence over time
with col3:
    st.markdown(f"**{country}: Tobacco Prevalence Over Time**")
    prev_ts = (
        tob.groupby(["year","sex"], as_index=False)
           .prevalence.mean()
           .sort_values("year")
    )
    # 1) prepare historical data
    prev_ts = (
        tob.groupby(["year","sex"], as_index=False)
        .prevalence.mean()
        .sort_values("year")
    )
    prev_ts["type"] = "Actual"

    # 2) build forecasts
    years_future = [2025, 2030]
    forecasts = []
    for sex in ["Male","Female"]:
        df_sex = prev_ts[prev_ts.sex==sex]
        # simple linear fit: prevalence = m*year + b
        m, b = np.polyfit(df_sex.year, df_sex.prevalence, 1)
        for yr in years_future:
            forecasts.append({"year":yr, "sex":sex, 
                            "prevalence": m*yr + b, 
                            "type":"Forecast"})
            
    df_fut = pd.DataFrame(forecasts)

    # 3) combine
    df_plot = pd.concat([prev_ts, df_fut], ignore_index=True)

    # build a Figure from scratch
    fig3 = go.Figure()

    # draw the grouped bars for the historical (“Actual”) data
    for sex, color in [("Female","#1f77b4"), ("Male","#aec7e8")]:
        df_h = prev_ts[prev_ts.sex==sex]
        fig3.add_trace(go.Bar(
            x=df_h.year,
            y=df_h.prevalence,
            name=f"{sex} (Actual)",
            marker_color=color,
        ))

    # now overlay a dashed‐line for the forecast
    for sex, color in [("Female","#1f77b4"), ("Male","#aec7e8")]:
        df_f = df_fut[df_fut.sex==sex]
        fig3.add_trace(go.Scatter(
            x=df_f.year,
            y=df_f.prevalence,
            name=f"{sex} (Forecast)",
            mode="lines+markers",
            line=dict(color=color, dash="dash"),
            marker=dict(size=6),
        ))

    fig3.update_layout(
        barmode="group",
        height=300,
        margin=dict(l=10,r=10,t=30,b=50),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        xaxis_title="", yaxis_title="% of pop"
    )

    st.plotly_chart(fig3, use_container_width=True)

# 4) Mortality over time
with col4:
    st.markdown(f"**{country}: Cancer Mortality Over Time**")
    # 1) historical
    mort_ts = (
        mor.groupby(["year","sex"], as_index=False)
        .mortality.mean()
        .sort_values("year")
    )
    mort_ts["type"]="Actual"

    # 2) forecast
    forecasts = []
    for sex in ["Male","Female"]:
        df_s = mort_ts[mort_ts.sex==sex]
        m, b = np.polyfit(df_s.year, df_s.mortality, 1)
        for yr in years_future:
            forecasts.append({"year":yr,"sex":sex,
                            "mortality": m*yr + b,
                            "type":"Forecast"})
    df_fut2 = pd.DataFrame(forecasts)

    # 3) combine
    df_mplot = pd.concat([mort_ts, df_fut2], ignore_index=True)

    # 4) bar chart with pattern
    fig4 = go.Figure()

    for sex, color in [("Female","#1f77b4"), ("Male","#aec7e8")]:
        df_h = mort_ts[mort_ts.sex==sex]
        fig4.add_trace(go.Bar(
            x=df_h.year,
            y=df_h.mortality,
            name=f"{sex} (Actual)",
            marker_color=color,
        ))

    for sex, color in [("Female","#1f77b4"), ("Male","#aec7e8")]:
        df_f = df_fut2[df_fut2.sex==sex]
        fig4.add_trace(go.Scatter(
            x=df_f.year,
            y=df_f.mortality,
            name=f"{sex} (Forecast)",
            mode="lines+markers",
            line=dict(color=color, dash="dash"),
            marker=dict(size=6),
        ))

    fig4.update_layout(
        barmode="group",
        height=300,
        margin=dict(l=10,r=10,t=30,b=50),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        xaxis_title="", yaxis_title="Deaths/100 000"
    )

    st.plotly_chart(fig4, use_container_width=True)

# ── Adolescent vs Adult breakdown ──────────────────────────────────────
# Define sets of indicators:
all_inds = [
    "Current cigarette smoking among adolescents (%)",
    "Current e-cigarette use among adolescents (%)",
    "Current smokeless tobacco use among adolescents (%)",
    "Current tobacco smoking among adolescents (%)",
    "Current tobacco use among adolescents (%)",
    "Daily cigarette smoking among adolescents (%)",
    "Daily tobacco smoking among adolescents (%)",
    "Current cigarette smoking among adults (%)",
    "Current e-cigarette use among adults (%)",
    "Current smokeless tobacco use among adults (%)",
    "Current tobacco smoking among adults (%)",
    "Current tobacco use among adults (%)",
    "Daily cigarette smoking among adults (%)",
    "Daily e-cigarette use among adults (%)",
    "Daily smokeless tobacco use among adults (%)",
    "Daily tobacco smoking among adults (%)",
    "Daily tobacco use among adults (%)",
]

# Load data
df_tob = load_tobacco(tob_path, all_inds)

# Filter data
df_stack = (
    df_tob[
        (df_tob.country == country)
        & df_tob.indicator_name.isin(all_inds)
    ].copy()
)

# Create a combined column for grouping
df_stack['year_sex'] = df_stack['year'].astype(str) + ' - ' + df_stack['sex']

# Use Plotly Express for easier grouped stacked bars
fig = px.bar(
    df_stack,
    x='year_sex',
    y='prevalence',
    color='indicator_name',
    barmode = 'stack',
    title=f'Tobacco Use Indicators by Year and Sex - {country}',
    labels={
        'prevalence': 'Prevalence (%)',
        'year_sex': 'Year - Sex',
        'indicator_name': 'Indicator'
    },
    height=500
)

# Update layout for better appearance
fig.update_layout(
    xaxis_title="Year and Sex",
    yaxis_title="Prevalence (%)",
    margin=dict(l=20, r=20, t=50, b=50),
    legend=dict(
        orientation="v",
        x=1.02, y=1,
        title="Tobacco Use Indicators"
    ),
    xaxis=dict(
        tickangle=45,
        categoryorder='category ascending'
    )
)

# Make the plot responsive
fig.update_layout(
    autosize=True,
    bargap=0.1,
    bargroupgap=0.1
)

st.plotly_chart(fig, use_container_width=True)