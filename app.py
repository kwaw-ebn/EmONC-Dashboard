import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="EmONC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: white;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([1,5])

with col1:
    st.image("logo.png", width=120)  # Add Ghana Health Service logo here

with col2:
    st.title("Agona East Safe Motherhood (EmONC)")
    st.caption("Training Performance Dashboard")

# ---------------- FILE UPLOAD ----------------
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx", "xls"]
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if uploaded_file:
    df = load_data(uploaded_file)

    # ---------------- CLEAN COLUMNS ----------------
    df.columns = df.columns.str.strip()

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("Filters")

    if "facility" in df.columns:
        facility_filter = st.sidebar.multiselect(
            "Select Facility",
            df["facility"].dropna().unique(),
            default=df["facility"].dropna().unique()
        )
        df = df[df["facility"].isin(facility_filter)]

    if "cadre" in df.columns:
        cadre_filter = st.sidebar.multiselect(
            "Select Cadre",
            df["cadre"].dropna().unique(),
            default=df["cadre"].dropna().unique()
        )
        df = df[df["cadre"].isin(cadre_filter)]

    if "test_type" in df.columns:
        test_filter = st.sidebar.multiselect(
            "Test Type",
            df["test_type"].dropna().unique(),
            default=df["test_type"].dropna().unique()
        )
        df = df[df["test_type"].isin(test_filter)]

    # ---------------- METRICS ----------------
    if "total_score" in df.columns:

        st.subheader("📊 Key Metrics")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Participants", len(df))
        col2.metric("Average Score", round(df["total_score"].mean(), 2))
        col3.metric("Highest Score", df["total_score"].max())
        col4.metric("Lowest Score", df["total_score"].min())

        # ---------------- PASS/FAIL ----------------
        if "pass_fail" in df.columns:
            st.subheader("Pass vs Fail")

            fig1 = px.pie(
                df,
                names="pass_fail",
                title="Pass vs Fail Distribution",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig1, use_container_width=True)

        # ---------------- SCORE DISTRIBUTION ----------------
        st.subheader("Score Distribution")

        fig2 = px.histogram(
            df,
            x="total_score",
            nbins=10,
            title="Score Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ---------------- SCORE BAND ----------------
        if "score_band" in df.columns:
            st.subheader("Score Band")

            fig3 = px.bar(
                df["score_band"].value_counts().reset_index(),
                x="index",
                y="score_band",
                labels={"index": "Band", "score_band": "Count"},
                title="Score Band Analysis"
            )
            st.plotly_chart(fig3, use_container_width=True)

        # ---------------- FACILITY PERFORMANCE ----------------
        if "facility" in df.columns:
            st.subheader("Facility Performance")

            facility_avg = df.groupby("facility")["total_score"].mean().reset_index()

            fig4 = px.bar(
                facility_avg,
                x="total_score",
                y="facility",
                orientation="h",
                title="Average Score by Facility"
            )
            st.plotly_chart(fig4, use_container_width=True)

        # ---------------- LEADERBOARD ----------------
        st.subheader("🏆 Top Performers")

        if "name" in df.columns:
            top = df.sort_values(by="total_score", ascending=False).head(10)
            st.dataframe(top[["name", "facility", "total_score"]])

    else:
        st.error("No 'total_score' column found in dataset.")

else:
    st.info("Upload a dataset to begin analysis.")
