import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="EmONC Training Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- PROFESSIONAL STYLING ----------------
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Sidebar Text */
    .author-tag {
        font-size: 18px;
        font-weight: 700;
        color: #3B82F6;
        text-align: center;
        margin-top: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Header Styles */
    h1, h2, h3 { color: #F3F4F6; }
    .stDataFrame { background-color: #1F2937; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR BRANDING ----------------
with st.sidebar:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    try:
        # Larger logo implementation
        st.image("logo.png", use_container_width=True)
    except:
        st.info("Upload logo.png to show logo")
    
    st.markdown('<p class="author-tag">Built by Ebenezer Kwaw</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    
    st.header("📂 Data Upload")
    uploaded_file = st.file_uploader("Upload result.csv", type=["csv", "xlsx"])

# ---------------- DATA ENGINE ----------------
def process_data(df):
    # Standardize column names
    df.columns = df.columns.str.strip()
    
    # 1. Handle Score Column (Parses "6.00 / 21" or "15")
    score_col = next((c for c in df.columns if "score" in c.lower()), None)
    if score_col:
        # Extract only the first number before any slash (e.g., 6.00 from 6.00 / 21)
        df['total_score'] = df[score_col].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
    
    # 2. Smart Mapping for filters
    mapping = {
        'facility': ['facility', 'health center', 'site', 'location'],
        'cadre': ['cadre', 'designation', 'role', 'rank'],
        'name': ['name', 'full name', 'participant', 'staff name']
    }
    
    for official, aliases in mapping.items():
        for col in df.columns:
            if col.lower() in aliases:
                df = df.rename(columns={col: official})
                break
    
    return df

# ---------------- MAIN CONTENT ----------------
if uploaded_file:
    # Load File
    df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df = process_data(df_raw)

    if 'total_score' in df.columns:
        st.title("🏥 Agona East Safe Motherhood (EmONC)")
        st.markdown("### Training Performance Analytics")
        st.divider()

        # --- FILTERS ---
        st.sidebar.subheader("🔍 Filters")
        filtered_df = df.copy()
        
        if 'facility' in df.columns:
            facilities = sorted(df['facility'].dropna().unique())
            sel_fac = st.sidebar.multiselect("Select Facility", facilities, default=facilities)
            filtered_df = filtered_df[filtered_df['facility'].isin(sel_fac)]

        # --- KEY METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Participants", len(filtered_df))
        m2.metric("Avg Score", f"{filtered_df['total_score'].mean():.1f}")
        m3.metric("Highest Score", f"{filtered_df['total_score'].max():.0f}")
        m4.metric("Lowest Score", f"{filtered_df['total_score'].min():.0f}")

        # --- VISUALS ---
        st.write("")
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("🎯 Score Distribution")
            fig_dist = px.histogram(
                filtered_df, x="total_score", 
                nbins=10, 
                color_discrete_sequence=['#3B82F6'],
                template="plotly_dark"
            )
            st.plotly_chart(fig_dist, use_container_width=True)

        with col_b:
            if 'facility' in filtered_df.columns:
                st.subheader("🏢 Facility Performance")
                fac_avg = filtered_df.groupby('facility')['total_score'].mean().reset_index()
                fig_bar = px.bar(
                    fac_avg, x='total_score', y='facility', 
                    orientation='h', color='total_score',
                    color_continuous_scale='Blues',
                    template="plotly_dark"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("💡 Tip: Add a 'Facility' column to your CSV to see facility performance.")

        # --- TABLE ---
        st.divider()
        st.subheader("🏆 Performance Leaderboard")
        # Display name and score if available
        display_cols = [c for c in ['name', 'facility', 'total_score'] if c in filtered_df.columns]
        if not display_cols: 
            display_cols = df.columns.tolist()[:5] # Fallback to first 5 columns
            
        st.dataframe(
            filtered_df.sort_values('total_score', ascending=False)[display_cols],
            use_container_width=True
        )

    else:
        st.error("⚠️ Could not find the Score column. Please check your file.")
else:
    st.title("🏥 Agona East EmONC Dashboard")
    st.info("Welcome! Please upload your **result.csv** file in the sidebar to generate the training analysis.")
    st.image("https://img.icons8.com/clouds/500/hospital.png", width=300)
