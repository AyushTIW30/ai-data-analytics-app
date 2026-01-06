import sys
import os

# ---------- PATH FIX ----------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px

from backend.insights import generate_basic_insights, generate_text_insights
from backend.charts import get_chart_suggestions
from backend.query_engine import simple_english_query


# ---------- CONFIG ----------
st.set_page_config(page_title="AI Data App", layout="wide")
st.title("📊 AI Data Analytics App")


# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader(
    "Upload CSV / Excel / JSON file",
    type=["csv", "xlsx", "json"]
)

if uploaded_file:

    # ---------- LOAD DATA ----------
    if uploaded_file.name.endswith(".csv"):
        df_original = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df_original = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".json"):
        df_original = pd.read_json(uploaded_file)

    df_filtered = df_original.copy()

    # ---------- PREVIEW ----------
    st.subheader("🔍 Data Preview")
    st.dataframe(df_original.head())

    # ---------- SUMMARY ----------
    st.subheader("📌 Data Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Shape:**", df_original.shape)
        st.write("**Columns:**", list(df_original.columns))

    with col2:
        st.write("**Missing Values:**")
        st.dataframe(df_original.isnull().sum())

    # ---------- INSIGHTS ----------
    insights = generate_basic_insights(df_original)

    st.subheader("📊 Auto Insights")
    c1, c2, c3 = st.columns(3)

    c1.metric("Total Rows", insights["rows"])
    c2.metric("Total Columns", insights["columns"])
    c3.metric("Numeric Columns", len(insights["numeric_columns"]))

    st.markdown("### 🔢 Numeric Summary")
    for col, stats in insights["numeric_summary"].items():
        st.write(
            f"**{col}** → Min: {stats['min']} | Max: {stats['max']} | Mean: {round(stats['mean'], 2)}"
        )

    st.markdown("### ⚠️ Missing Values")
    st.dataframe(
        pd.DataFrame.from_dict(
            insights["missing_values"],
            orient="index",
            columns=["Missing Count"]
        )
    )

    st.markdown("### 🧠 AI Insights Summary")
    for line in generate_text_insights(insights):
        st.write("•", line)

    # ---------- FILTERS ----------
    st.subheader("🎚️ Filters")

    # Categorical Filters
    for col in insights["categorical_columns"]:
        options = df_original[col].dropna().unique().tolist()
        selected = st.multiselect(col, options, default=options)
        df_filtered = df_filtered[df_filtered[col].isin(selected)]

    # Numeric Filters
    for col in insights["numeric_columns"]:
        min_val, max_val = st.slider(
            f"{col} range",
            float(df_original[col].min()),
            float(df_original[col].max()),
            (float(df_original[col].min()), float(df_original[col].max()))
        )
        df_filtered = df_filtered[(df_filtered[col] >= min_val) & (df_filtered[col] <= max_val)]

    # ---------- ENGLISH QUERY ----------
    st.subheader("🗣️ Ask in English (Free Version)")
    user_query = st.text_input("Type your query")

    if user_query:
        result = simple_english_query(df_filtered, user_query)
        if isinstance(result, pd.DataFrame):
            df_filtered = result
        st.write(result)

    # ---------- FILTERED DATA ----------
    st.subheader("📄 Filtered Data")
    st.dataframe(df_filtered)

    # ---------- AUTO CHARTS ----------
    st.subheader("📈 Auto Charts")
    charts = get_chart_suggestions(df_filtered)[:6]

    for i in range(0, len(charts), 3):
        cols = st.columns(min(3, len(charts) - i))

        for j, chart in enumerate(charts[i:i + 3]):
            col_name = chart["column"]
            chart_type = chart["type"]

            with cols[j]:
                st.markdown(f"### {col_name} - {chart_type.capitalize()}")

                # ---------- BAR / HISTOGRAM ----------
                if chart_type in ["bar", "histogram"]:
                    bar_data = (
                        df_filtered[col_name]
                        .value_counts()
                        .reset_index(name="count")
                        .rename(columns={"index": col_name})
                    )

                    fig = px.bar(
                        bar_data,
                        x=col_name,
                        y="count",
                        title=f"{col_name} Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # ---------- LINE ----------
                elif chart_type == "line":
                    if pd.api.types.is_numeric_dtype(df_filtered[col_name]):
                        fig = px.line(
                            df_filtered,
                            y=col_name,
                            title=f"{col_name} Trend"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                # ---------- PIE ----------
                elif chart_type == "pie":
                    pie_data = (
                        df_filtered[col_name]
                        .value_counts()
                        .reset_index(name="count")
                        .rename(columns={"index": col_name})
                    )

                    fig = px.pie(
                        pie_data,
                        names=col_name,
                        values="count",
                        title=f"{col_name} Share"
                    )
                    st.plotly_chart(fig, use_container_width=True)
