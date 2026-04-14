import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="EmONC Dashboard | Agona East",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #374151;
    }
    .footer-text {
        font-size: 14px;
        color: #9CA3AF;
        text-align: center;
        margin-top: -10px;
        font-weight: 500;
    }
    .sidebar-brand {
        text-align: center;
        padding-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- LOGO & BRANDING ----------------
# Using a sidebar approach for the logo and your name for a professional feel
with st.sidebar:
    st.markdown('<div class="sidebar-brand">', unsafe_allow_html=True)
    # If logo.png is missing, this handles the error gracefully
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.info("Upload logo.png to directory")
    
    st.markdown('<p class="footer-text">Built by Ebenezer Kwaw</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

# ---------------- DATA LOADER UTILITY ----------------
def clean_and_map_columns(df):
    """Standardizes column names and maps them to expected keys."""
    # Strip spaces and lowercase everything
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    mapping = {
        'total_score': ['total_score', 'score', 'pre_test', 'pretest', 'marks'],
        'facility': ['facility', 'health_center', 'site', 'location'],
        'cadre': ['cadre', 'designation', 'role', 'job_title'],
        'name': ['name', 'participant', 'full_name', 'staff_name']
    }
    
    for official_name, aliases in mapping.items():
        if official_name not in df.columns:
            for alias in aliases:
                if alias in df.columns:
                    df = df.rename(columns={alias: official_name})
                    break
    
    # Force total_score to numeric
    if 'total_score' in df.columns:
        df['total_score'] = pd.to_numeric(df['total_score'], errors='coerce')
        df = df.dropna(subset=['total_score'])
        
    return df

# ---------------- MAIN HEADER ----------------
st.title("🏥 Agona East Safe Motherhood (EmONC)")
st.markdown("### Training Performance & Pre-test Analytics")
st.divider()

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.sidebar.file_uploader(
    "Upload Training Data (CSV or Excel)",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file:
    # Load Data
    if uploaded_file.name.endswith(".csv"):
        raw_df = pd.read_csv(uploaded_file)
    else:
        raw_df = pd.read_excel(uploaded_file)

    df = clean_and_map_columns(raw_df)

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.subheader("🔍 Filter Data")
    
    filtered_df = df.copy()
    
    if "facility" in df.columns:
        facilities = df["facility"].dropna().unique()
        facility_filter = st.sidebar.multiselect("Select Facility", facilities, default=facilities)
        filtered_df = filtered_df[filtered_df["facility"].isin(facility_filter)]

    if "cadre" in df.columns:
        cadres = df["cadre"].dropna().unique()
        cadre_filter = st.sidebar.multiselect("Select Cadre", cadres, default=cadres)
        filtered_df = filtered_df[filtered_df["cadre"].isin(cadre_filter)]

    # ---------------- DASHBOARD LAYOUT ----------------
    if "total_score" in df.columns:
        # KPI Row
        st.subheader("📊 Key Performance Indicators")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        avg_score = filtered_df["total_score"].mean()
        
        kpi1.metric("Total Participants", len(filtered_df))
        kpi2.metric("Average Score", f"{avg_score:.1f}%")
        kpi3.metric("Highest Score", f"{filtered_df['total_score'].max()}%")
        kpi4.metric("Lowest Score", f"{filtered_df['total_score'].min()}%")
        
        st.divider()

        # Visualizations Row 1
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("🎯 Score Distribution")
            fig_hist = px.histogram(
                filtered_df, x="total_score", 
                nbins=15, 
                color_discrete_sequence=['#3B82F6'],
                labels={'total_score': 'Score Result'}
            )
            fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_right:
            if "facility" in filtered_df.columns:
                st.subheader("🏢 Facility Comparison")
                fac_avg = filtered_df.groupby("facility")["total_score"].mean().sort_values().reset_index()
                fig_fac = px.bar(
                    fac_avg, x="total_score", y="facility", 
                    orientation='h',
                    color="total_score",
                    color_continuous_scale='Blues'
                )
                fig_fac.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_fac, use_container_width=True)

        # Leaderboard Table
        st.divider()
        st.subheader("🏆 Top Performers Leaderboard")
        if "name" in filtered_df.columns:
            leaderboard = filtered_df.sort_values(by="total_score", ascending=False).head(10)
            st.table(leaderboard[["name", "facility", "total_score"]])
        else:
            st.dataframe(filtered_df.sort_values(by="total_score", ascending=False).head(10), use_container_width=True)

    else:
        st.error("Error: Could not find a 'Score' column in your file. Please ensure your CSV contains a column named 'total_score' or 'score'.")
        st.info(f"Columns found in your file: {', '.join(raw_df.columns.tolist())}")

else:
    st.info("👋 Welcome! Please upload your pre-test CSV or Excel file in the sidebar to generate the analysis.")
