import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Simple Sales Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.date_range("2026-01-01", periods=180, freq="D")
    regions = ["North", "South", "East", "West"]
    categories = ["Hardware", "Software", "Services"]

    rows = []
    for date in dates:
        for region in regions:
            category = rng.choice(categories, p=[0.36, 0.42, 0.22])
            units = int(rng.integers(12, 85))
            unit_price = float(rng.normal(155, 34))
            conversion_rate = float(rng.uniform(0.06, 0.22))

            rows.append(
                {
                    "date": date,
                    "region": region,
                    "category": category,
                    "units": units,
                    "revenue": round(units * max(unit_price, 65), 2),
                    "conversion_rate": conversion_rate,
                }
            )

    return pd.DataFrame(rows)


df = load_data()

st.title("Simple Sales Dashboard")
st.caption("A lightweight Streamlit dashboard with generated sample data.")

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date range",
        value=(df["date"].min().date(), df["date"].max().date()),
        min_value=df["date"].min().date(),
        max_value=df["date"].max().date(),
    )
    selected_regions = st.multiselect(
        "Regions",
        options=sorted(df["region"].unique()),
        default=sorted(df["region"].unique()),
    )
    selected_categories = st.multiselect(
        "Categories",
        options=sorted(df["category"].unique()),
        default=sorted(df["category"].unique()),
    )

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date = df["date"].min()
    end_date = df["date"].max()

filtered = df[
    (df["date"].between(start_date, end_date))
    & (df["region"].isin(selected_regions))
    & (df["category"].isin(selected_categories))
]

total_revenue = filtered["revenue"].sum()
total_units = filtered["units"].sum()
average_order = total_revenue / max(total_units, 1)
average_conversion = filtered["conversion_rate"].mean() if not filtered.empty else 0

metric_cols = st.columns(4)
metric_cols[0].metric("Revenue", f"${total_revenue:,.0f}")
metric_cols[1].metric("Units Sold", f"{total_units:,.0f}")
metric_cols[2].metric("Avg. Unit Value", f"${average_order:,.2f}")
metric_cols[3].metric("Conversion", f"{average_conversion:.1%}")

st.divider()

chart_cols = st.columns((2, 1))

with chart_cols[0]:
    st.subheader("Revenue Trend")
    trend = (
        filtered.groupby("date", as_index=False)["revenue"]
        .sum()
        .set_index("date")
    )
    st.line_chart(trend, y="revenue", height=360)

with chart_cols[1]:
    st.subheader("Revenue by Category")
    by_category = (
        filtered.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .set_index("category")
    )
    st.bar_chart(by_category, y="revenue", height=360)

st.subheader("Filtered Records")
display_df = filtered.sort_values("date", ascending=False).assign(
    conversion_rate=lambda data: data["conversion_rate"] * 100
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "date": st.column_config.DateColumn("Date"),
        "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
        "conversion_rate": st.column_config.ProgressColumn(
            "Conversion",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        ),
    },
)
