import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="BFT Transit Engagement Intelligence Dashboard",
    layout="wide"
)

st.title("BFT Transit Engagement Intelligence Dashboard")
st.caption(
    "A data-driven dashboard analyzing rider interactions with Transit App services, "
    "including nearby views, taps, routing suggestions, and GO trips."
)

# --------------------------------------------------
# GITHUB RAW EXCEL LINK
# --------------------------------------------------

GITHUB_EXCEL_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/Transit_App_Lines_Data.xlsx"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data(url):
    df = pd.read_excel(url)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_cols = [
        "nearby_views",
        "nearby_taps",
        "tapped_routing_suggestions",
        "go_trips"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["month_number"] = df["date"].dt.month
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    df["day"] = df["date"].dt.day
    df["week"] = df["date"].dt.isocalendar().week
    df["is_weekend"] = df["weekday"].isin(["Saturday", "Sunday"])

    def get_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"

    df["season"] = df["month_number"].apply(get_season)

    df["tap_rate"] = df["nearby_taps"] / df["nearby_views"].replace(0, pd.NA)
    df["routing_rate"] = df["tapped_routing_suggestions"] / df["nearby_taps"].replace(0, pd.NA)
    df["trip_conversion_rate"] = df["go_trips"] / df["tapped_routing_suggestions"].replace(0, pd.NA)
    df["view_to_trip_rate"] = df["go_trips"] / df["nearby_views"].replace(0, pd.NA)

    return df


df = load_data(GITHUB_EXCEL_URL)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

routes = sorted(df["route_short_name"].dropna().unique())
years = sorted(df["year"].dropna().unique())

selected_routes = st.sidebar.multiselect(
    "Select Routes",
    options=routes,
    default=routes
)

selected_years = st.sidebar.multiselect(
    "Select Years",
    options=years,
    default=years
)

filtered = df[
    (df["route_short_name"].isin(selected_routes)) &
    (df["year"].isin(selected_years))
]

# --------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------

st.subheader("Overview")

total_views = filtered["nearby_views"].sum()
total_taps = filtered["nearby_taps"].sum()
total_routing = filtered["tapped_routing_suggestions"].sum()
total_trips = filtered["go_trips"].sum()

tap_rate = total_taps / total_views if total_views > 0 else 0
routing_rate = total_routing / total_taps if total_taps > 0 else 0
trip_conversion = total_trips / total_routing if total_routing > 0 else 0
view_to_trip = total_trips / total_views if total_views > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Nearby Views", f"{total_views:,.0f}")
col2.metric("Nearby Taps", f"{total_taps:,.0f}")
col3.metric("Routing Suggestions", f"{total_routing:,.0f}")
col4.metric("GO Trips", f"{total_trips:,.0f}")

col5, col6, col7, col8 = st.columns(4)

col5.metric("Tap Rate", f"{tap_rate:.1%}")
col6.metric("Routing Rate", f"{routing_rate:.1%}")
col7.metric("Trip Conversion", f"{trip_conversion:.1%}")
col8.metric("View-to-Trip Rate", f"{view_to_trip:.1%}")

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Route Ranking",
    "Monthly Trends",
    "Weekday Patterns",
    "Seasonal Analysis",
    "Raw Data"
])

# --------------------------------------------------
# TAB 1 — ROUTE RANKING
# --------------------------------------------------

with tab1:
    st.subheader("Route-Level Summary")

    route_summary = (
        filtered
        .groupby("route_short_name", as_index=False)
        .agg({
            "nearby_views": "sum",
            "nearby_taps": "sum",
            "tapped_routing_suggestions": "sum",
            "go_trips": "sum"
        })
    )

    route_summary["tap_rate"] = route_summary["nearby_taps"] / route_summary["nearby_views"].replace(0, pd.NA)
    route_summary["routing_rate"] = route_summary["tapped_routing_suggestions"] / route_summary["nearby_taps"].replace(0, pd.NA)
    route_summary["trip_conversion_rate"] = route_summary["go_trips"] / route_summary["tapped_routing_suggestions"].replace(0, pd.NA)
    route_summary["view_to_trip_rate"] = route_summary["go_trips"] / route_summary["nearby_views"].replace(0, pd.NA)

    st.dataframe(route_summary, use_container_width=True)

    metric_choice = st.selectbox(
        "Choose Metric to Rank Routes",
        [
            "nearby_views",
            "nearby_taps",
            "tapped_routing_suggestions",
            "go_trips",
            "tap_rate",
            "routing_rate",
            "trip_conversion_rate",
            "view_to_trip_rate"
        ]
    )

    ranked = route_summary.sort_values(metric_choice, ascending=False).head(20)

    fig = px.bar(
        ranked,
        x="route_short_name",
        y=metric_choice,
        title=f"Top Routes by {metric_choice.replace('_', ' ').title()}",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TAB 2 — MONTHLY TRENDS
# --------------------------------------------------

with tab2:
    st.subheader("Monthly Trends")

    monthly = (
        filtered
        .groupby("year_month", as_index=False)
        .agg({
            "nearby_views": "sum",
            "nearby_taps": "sum",
            "tapped_routing_suggestions": "sum",
            "go_trips": "sum"
        })
        .sort_values("year_month")
    )

    monthly_metric = st.selectbox(
        "Select Monthly Metric",
        ["nearby_views", "nearby_taps", "tapped_routing_suggestions", "go_trips"],
        key="monthly_metric"
    )

    fig = px.line(
        monthly,
        x="year_month",
        y=monthly_metric,
        markers=True,
        title=f"Monthly Trend: {monthly_metric.replace('_', ' ').title()}"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TAB 3 — WEEKDAY PATTERNS
# --------------------------------------------------

with tab3:
    st.subheader("Weekday Patterns")

    weekday_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    weekday = (
        filtered
        .groupby("weekday", as_index=False)
        .agg({
            "nearby_views": "sum",
            "nearby_taps": "sum",
            "tapped_routing_suggestions": "sum",
            "go_trips": "sum"
        })
    )

    weekday["weekday"] = pd.Categorical(
        weekday["weekday"],
        categories=weekday_order,
        ordered=True
    )

    weekday = weekday.sort_values("weekday")

    weekday_metric = st.selectbox(
        "Select Weekday Metric",
        ["nearby_views", "nearby_taps", "tapped_routing_suggestions", "go_trips"],
        key="weekday_metric"
    )

    fig = px.bar(
        weekday,
        x="weekday",
        y=weekday_metric,
        title=f"Activity by Day of Week: {weekday_metric.replace('_', ' ').title()}",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TAB 4 — SEASONAL ANALYSIS
# --------------------------------------------------

with tab4:
    st.subheader("Seasonal Analysis")

    season_order = ["Winter", "Spring", "Summer", "Fall"]

    seasonal = (
        filtered
        .groupby("season", as_index=False)
        .agg({
            "nearby_views": "sum",
            "nearby_taps": "sum",
            "tapped_routing_suggestions": "sum",
            "go_trips": "sum"
        })
    )

    seasonal["season"] = pd.Categorical(
        seasonal["season"],
        categories=season_order,
        ordered=True
    )

    seasonal = seasonal.sort_values("season")

    season_metric = st.selectbox(
        "Select Seasonal Metric",
        ["nearby_views", "nearby_taps", "tapped_routing_suggestions", "go_trips"],
        key="season_metric"
    )

    fig = px.bar(
        seasonal,
        x="season",
        y=season_metric,
        title=f"Seasonal Pattern: {season_metric.replace('_', ' ').title()}",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TAB 5 — RAW DATA
# --------------------------------------------------

with tab5:
    st.subheader("Filtered Raw Data")

    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False)

    st.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="filtered_transit_app_data.csv",
        mime="text/csv"
    )
