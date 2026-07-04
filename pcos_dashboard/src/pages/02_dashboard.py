import os
import io
import streamlit as st
import pandas as pd
import pydeck as pdk
import joblib 
from datetime import datetime
from dotenv import load_dotenv  
from urllib.parse import quote_plus

# Import your helpers and components
from utils.ui_helpers import load_css
from components.header import render_header
from components.sidebar import render_sidebar
from components.disclaimer import show_disclaimer_banner
from utils.maps import get_free_clinics_data

from database.queries import GET_RISK_TRENDS, GET_DEMOGRAPHICS_RISK, GET_EXERCISE_CYCLE, GET_SYMPTOMS, GET_KPIS
from components.metrics import render_traffic_metrics
from components.charts import (
    create_assessed_risk_trend, 
    create_lifestyle_vs_cycle_chart, 
    create_symptoms_chart,
)

# 1. PAGE CONFIG MUST BE ABSOLUTELY FIRST
st.set_page_config(
    page_title="PCOS Community Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. LOAD ENVIRONMENT VARIABLES (.env)
load_dotenv()

# 3. CONNECT TO DATABASE 
# Safely encode the password so the '@' symbol doesn't break the URL
safe_password = quote_plus(os.getenv('DB_PASSWORD'))

db_url = f"mysql+pymysql://{os.getenv('DB_USER')}:{safe_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
conn = st.connection('mariadb', type='sql', url=db_url)

# 4. DEFINE THE FETCH FUNCTION 
@st.cache_data(ttl=600)
def fetch_dashboard_data(query_string):
    return conn.query(query_string)

# 5. FETCH THE DATA FOR THE CHARTS
df_risk_trends = fetch_dashboard_data(GET_RISK_TRENDS)
df_demographics = fetch_dashboard_data(GET_DEMOGRAPHICS_RISK)
df_exercise_cycle = fetch_dashboard_data(GET_EXERCISE_CYCLE)  
df_symptoms = fetch_dashboard_data(GET_SYMPTOMS)
df_kpis = fetch_dashboard_data(GET_KPIS)     

@st.cache_data(ttl=600)
def fetch_shap_feature_data():
    """Fetches assessment data from the database to feed into SHAP."""
    # We are using the exact same connection method as your other charts now!
    query = """
        SELECT 
            age, bmi, cycle_length, weight_gain, hair_growth, pimples 
        FROM assessments 
        ORDER BY created_at DESC 
        LIMIT 100
    """
    try:
        return conn.query(query)
    except Exception as e:
        # Return empty dataframe if query fails while we are testing
        return pd.DataFrame()

# ---------------------------------------------------------
# YOUR DASHBOARD LAYOUT STARTS BELOW THIS LINE
# ---------------------------------------------------------

# LOAD STYLES & SIDEBAR
load_css("assets/style.css")
render_sidebar(current_page="dashboard")

# 5. HEADER
render_header(current_page="dashboard")

# 6. GET USER ROLE
role = st.session_state.get('role_id', 1)

# --- TITLE SECTION ---
# 1. Determine the time of day
current_hour = datetime.now().hour
if current_hour < 12:
    greeting = "Good morning"
elif 12 <= current_hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

head_c1, head_c2 = st.columns([4.5, 1.5], vertical_alignment="bottom")

with head_c1:
    # 2. Apply the dynamic greeting and a new welcoming subtitle
    st.markdown(f"<h1 style='margin-bottom: 0px;'>{greeting}! 👋</h1>", unsafe_allow_html=True)
    st.markdown("### Welcome to your PCOS Community Insights")
    st.caption(
        "We are turning shared experiences into powerful knowledge. "
        "Explore real-time trends, learn from the community, and discover how we're decoding PCOS together. 🌱"
    )

with head_c2:
    if role == 3:
        if st.button("⚙️ Edit Dashboard Layout", use_container_width=True):
            st.switch_page("pages/31_manage_dashboard.py")
    else:
        # 1. Create a buffer to hold the Excel file in memory
        buffer = io.BytesIO()
        
        # 2. Write each of your actual dataframes to a different sheet!
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            if not df_kpis.empty:
                df_kpis.to_excel(writer, sheet_name='Key Metrics', index=False)
            if not df_risk_trends.empty:
                df_risk_trends.to_excel(writer, sheet_name='Risk Trends', index=False)
            if not df_demographics.empty:
                df_demographics.to_excel(writer, sheet_name='Demographics', index=False)
            if not df_exercise_cycle.empty:
                df_exercise_cycle.to_excel(writer, sheet_name='Exercise & Cycle', index=False)
            if not df_symptoms.empty:
                df_symptoms.to_excel(writer, sheet_name='Symptoms', index=False)
                
        # 3. Create the download button using the real data
        st.download_button(
            label="📥 Export Live Data",
            data=buffer.getvalue(),
            file_name="pcos_dashboard_live_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

# --- ROW 1: KEY METRICS & ASSESSED RISK ---
st.markdown("### 📊 At a Glance")
col1, col2 = st.columns([2.3, 1.7])
with col1:
    render_traffic_metrics(df_kpis)
with col2:
    st.plotly_chart(
        create_assessed_risk_trend(df_risk_trends),
        use_container_width=True,
        config={"displayModeBar": True}  # also hides the plotly toolbar
    )

# --- ROW 2: SYMPTOM & LIFESTYLE TRENDS ---
st.markdown("### 📉 Clinical Trends")
r2c1, r2c2 = st.columns(2)

with r2c1:
    st.plotly_chart(create_lifestyle_vs_cycle_chart(df_exercise_cycle), use_container_width=True)

with r2c2:
    st.plotly_chart(create_symptoms_chart(df_symptoms), use_container_width=True) 
    st.markdown("""
        <div style='font-size: 0.8rem; color: #6B7280; display: flex; justify-content: space-around;'>
            <div><b>P</b> - Pimples<br><b>W</b> - Weight Gain<br><b>S</b> - Skin Darkening</div>
            <div><b>H</b> - Hirsutism<br><b>L</b> - Hair Loss</div>
        </div>
    """, unsafe_allow_html=True)

# --- ROW 3: RESOURCE MAP ---
st.markdown("---")
st.subheader("📍 Specialist Network Map")

# 1. Fetch the data
map_data = get_free_clinics_data()

# 2. DATA PREPARATION & AREA EXTRACTION
if not map_data.empty:
    # 1. Clean Coordinates
    map_data['lat'] = pd.to_numeric(map_data['lat'], errors='coerce')
    map_data['lon'] = pd.to_numeric(map_data['lon'], errors='coerce')
    map_data = map_data.dropna(subset=['lat', 'lon'])

    # 2. Advanced City Search (Checks address tag, then name)
    def assign_city(row):
        # Priority 1: Check if 'city' column exists from API
        if 'city' in row and pd.notna(row['city']) and row['city'] != 'Kuala Lumpur':
            return row['city']
        
        # Priority 2: Check Name for common areas
        name = str(row['name']).lower()
        if 'kuala lumpur' in name or 'kl cc' in name: return 'Kuala Lumpur'
        if 'selangor' in name or 'subang' in name or 'petaling' in name: return 'Selangor'
        if 'penang' in name or 'george town' in name: return 'Penang'
        if 'johor' in name: return 'Johor'
        
        return 'Kuala Lumpur' # Default for Malaysia Specialist Hubs

    map_data['city'] = map_data.apply(assign_city, axis=1)

# 3. CASCADING SEARCH UI
search_col1, search_col2 = st.columns(2)
filtered_data = pd.DataFrame()

if not map_data.empty:
    with search_col1:
        # Get unique areas from our new 'city' column
        area_list = sorted(map_data['city'].unique().tolist())
        selected_area = st.selectbox(
            "🗺️ Step 1: Select an Area",
            options=area_list,
            index=None,
            placeholder="Choose a region..."
        )

    # First Level Filter
    if selected_area:
        area_filtered_data = map_data[map_data['city'] == selected_area]
    else:
        area_filtered_data = map_data

    with search_col2:
        # Second Level Filter: Options change based on Step 1
        clinic_names = sorted(area_filtered_data['name'].unique().tolist())
        search_query = st.selectbox(
            "🔍 Step 2: Search for a specific clinic",
            options=clinic_names,
            index=None,
            placeholder="Search in this area..."
        )

    # Final Filter
    if search_query:
        filtered_data = area_filtered_data[area_filtered_data['name'] == search_query]
    else:
        filtered_data = area_filtered_data
else:
    st.info("Gathering clinic data from the network...")

# 4. MAP & INFO DISPLAY
map_col1, map_col2 = st.columns([3, 1])

with map_col1:
    if not filtered_data.empty:
        # Define the layer
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=filtered_data,
            get_position='[lon, lat]',
            get_color='[106, 82, 219, 200]', 
            get_radius=150, 
            radius_min_pixels=4,  
            radius_max_pixels=8, 
            pickable=True 
        )
        
        # SMART ZOOM: Centers the map based on your selection
        if search_query:
            c_lat, c_lon, zoom = filtered_data['lat'].mean(), filtered_data['lon'].mean(), 14
        elif selected_area and selected_area != "Other Regions":
            c_lat, c_lon, zoom = filtered_data['lat'].mean(), filtered_data['lon'].mean(), 11
        else:
            c_lat, c_lon, zoom = 3.1390, 101.6869, 10 # KL Default
            
        st.pydeck_chart(pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            layers=[layer],
            initial_view_state=pdk.ViewState(latitude=c_lat, longitude=c_lon, zoom=zoom),
            tooltip={"html": "<b>🏥 {name}</b><br>City: {city}", "style": {"backgroundColor": "#FFFFFF", "color": "#1A1A1A"}}
        ))

with map_col2:
    st.write("**Quick Info:**")
    if not filtered_data.empty:
        # Show top 4 relevant results
        for _, clinic in filtered_data.head(4).iterrows():
            with st.expander(f"🏥 {clinic['name']}"):
                st.write(f"📍 **Area:** {clinic['city']}")
                if clinic['website'] != 'N/A':
                    st.link_button("Visit Website", clinic['website'])
                else:
                    st.caption("No website available")
    else:
        st.write("Select an area to view local facilities.")

show_disclaimer_banner("This platform is not a diagnostic tool and does not replace professional clinical assessment.")
show_disclaimer_banner("If you are experiencing a medical emergency, please contact emergency services (999 / 112).", icon="🆘")