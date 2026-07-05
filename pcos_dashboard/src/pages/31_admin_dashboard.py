import streamlit as st
import pymysql
import pandas as pd

from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header
from database.connection import get_connection

# Make sure you add 'render_global_shap_chart' to your components/charts.py file!
from components.charts import (
    render_risk_distribution_chart, 
    render_user_growth_chart,
)
from database.queries import (
    GET_TOTAL_USERS_BY_ROLE,
    GET_TOTAL_ASSESSMENTS,
    GET_RISK_DISTRIBUTION,
    GET_AVG_CONFIDENCE_SCORE,
    GET_USER_GROWTH_LAST_7_DAYS
)

# 1. Page Configuration
st.set_page_config(
    page_title="PCOS App - Admin Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Load Global CSS & Sidebar
load_css("assets/style.css")
render_sidebar(current_page="admin_dashboard")
render_header(current_page="admin_dashboard")

# 3. Authentication & Role Check
user_id = st.session_state.get('user_id')
user_role = st.session_state.get('role_id') 

if not user_id:
    st.warning("Please log in to access the Admin Hub.")
    st.stop()
if user_role != 3: 
    st.error("🚫 Unauthorized Access. This portal is strictly for System Administrators.")
    st.stop()

# ==========================================
# DATA FETCHING (100% Real DB Data)
# ==========================================
def fetch_admin_stats():
    # Safe defaults in case the database is empty
    stats = {
        "patients": 0, "doctors": 0, 
        "total_tests": 0, "avg_confidence": 0.0,
        "risk_dist": {},
        "user_growth": []
    }
    
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # 1. Users by Role (Assuming 1=Patient, 2=Doctor)
            cur.execute(GET_TOTAL_USERS_BY_ROLE)
            roles = cur.fetchall()
            if roles:
                stats["patients"] = next((r['count'] for r in roles if r['role_id'] == 1), 0)
                stats["doctors"] = next((r['count'] for r in roles if r['role_id'] == 2), 0)
                
            # 2. Total Assessments
            cur.execute(GET_TOTAL_ASSESSMENTS)
            tests = cur.fetchone()
            if tests and tests['total']:
                stats["total_tests"] = tests['total']
                
            # 3. Model Confidence
            cur.execute(GET_AVG_CONFIDENCE_SCORE)
            conf = cur.fetchone()
            if conf and conf['avg_score']:
                stats["avg_confidence"] = round(conf['avg_score'] * 100, 1)
                
            # 4. Risk Distribution
            cur.execute(GET_RISK_DISTRIBUTION)
            dist = cur.fetchall()
            if dist:
                stats["risk_dist"] = {row['risk_level']: row['count'] for row in dist}
                
            # 5. User Growth (Last 7 Days)
            cur.execute(GET_USER_GROWTH_LAST_7_DAYS)
            growth = cur.fetchall()
            if growth:
                stats["user_growth"] = growth
                
        except pymysql.MySQLError as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
            
    return stats

# ==========================================
# MAIN PAGE LAYOUT
# ==========================================
st.title("⚙️ Platform Analytics Overview")
st.markdown("Monitor system health, user growth, and Machine Learning performance in real-time.")

# Create columns with relative widths (e.g., 3 parts empty space, 1 part button)
spacer_col, button_col = st.columns([3, 1])

with button_col:
    if st.button("📄 Export Dashboard", use_container_width=True):
        st.info("Export functionality coming soon!")
st.write("---")

# Fetch Real Data
stats = fetch_admin_stats()

# --- ROW 1: TOP-LEVEL KPIs ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    with st.container(border=True):
        st.metric(label="👥 Total Patients", value=stats["patients"])
with m2:
    with st.container(border=True):
        st.metric(label="🩺 Registered Doctors", value=stats["doctors"])
with m3:
    with st.container(border=True):
        st.metric(label="📝 Assessments Taken", value=stats["total_tests"])
with m4:
    with st.container(border=True):
        st.metric(
            label="🤖 ML Avg Confidence", 
            value=f"{stats['avg_confidence']}%",
            help="""
**Model Certainty Score**
The average certainty of the AI's PCOS risk predictions.\n
**High (85% - 100%):** AI is healthy! Patient symptoms strongly match the training data.\n
**Low (Below 75%):** AI is uncertain. The model may need retraining.
"""
        )

st.write("<br>", unsafe_allow_html=True)

# --- ROW 2: CHARTS & VISUALS ---
col_chart1, col_chart2 = st.columns(2, gap="large")

with col_chart1:
    st.markdown("### System-Wide Risk Distribution")
    st.caption("How your users are scoring across the platform.")
    render_risk_distribution_chart(stats["risk_dist"])

with col_chart2:
    st.markdown("### User Growth Trend")
    st.caption("New registrations over the last 7 days.")
    render_user_growth_chart(stats["user_growth"])

st.write("---")

