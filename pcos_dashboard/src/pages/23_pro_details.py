import streamlit as st
import pandas as pd
import mariadb
from utils.ui_helpers import load_css
from components.header import render_header
from components.sidebar import render_sidebar
from database.connection import get_connection
from database.queries import (
    GET_USER_PROFILE_BY_ID,
    GET_USER_QUESTIONNAIRE,
    GET_USER_PERIOD_LOGS,
    GET_USER_QUEST_SCORE,
    GET_USER_QUEST_HISTORY 
)

st.set_page_config(page_title="PCOS App - Patient Details", layout="wide", initial_sidebar_state="expanded")
load_css("assets/style.css")
render_sidebar(current_page="pro_connect")
render_header(current_page="pro_monitor")

# --- Auth ---
user_role = st.session_state.get('role_id')
selected_patient_id = st.session_state.get('selected_patient_id')

if user_role != 2 or not selected_patient_id:
    st.switch_page("pages/22_pro_monitor.py")

def run_query(sql, params=()):
    conn = get_connection()
    if not conn: return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    except mariadb.Error as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        conn.close()

# Provide a handy function to convert DataFrames to CSV for the download buttons
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Header ---
profile = run_query(GET_USER_PROFILE_BY_ID, (selected_patient_id,))
patient_name = profile[0]['full_name'] if profile else "Patient"

col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
with col1:
    st.title(f"Detailed Logs: {patient_name}")
with col2:
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("pages/22_pro_monitor.py")

st.divider()

# ==========================================
# 3 TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["📋 Questionnaire Responses", "🗓️ Period Tracker", "🏆 Vitality Log"])

# --- TAB 1: QUESTIONNAIRE ---
with tab1:
    st.markdown("### Questionnaire Responses")
    questionnaire = run_query(GET_USER_QUESTIONNAIRE, (selected_patient_id,))
    if not questionnaire:
        st.info("No questionnaire data available.")
    else:
        rows = []
        for row in questionnaire:
            val = row.get('option_text') or row.get('numeric_value') or row.get('text_value') or 'N/A'
            submitted = row.get('submitted_at')
            rows.append({
                "Date": submitted.strftime("%Y-%m-%d") if submitted else "N/A",
                "Question": row.get('question_text', 'N/A'), 
                "Answer": val
            })
        
        q_df = pd.DataFrame(rows)
        
        st.download_button(
            label="📥 Export Questionnaire as CSV",
            data=convert_df(q_df),
            file_name=f"{patient_name}_questionnaire.csv",
            mime="text/csv",
            type="primary"
        )
        st.dataframe(q_df, use_container_width=True, hide_index=True)

# --- TAB 2: PERIOD TRACKER ---
with tab2:
    st.markdown("### 🩸 Period & Symptom Log")
    period_logs = run_query(GET_USER_PERIOD_LOGS, (selected_patient_id,))
    if not period_logs:
        st.info("No tracking data logged.")
    else:
        df_period = pd.DataFrame(period_logs)
        df_period['Date'] = pd.to_datetime(df_period['log_date']).dt.strftime('%Y-%m-%d')
        
        display_cols = [c for c in ['Date', 'period', 'mood', 'symptoms', 'cervical_fluid', 'blood_pressure', 'sugar_level', 'notes'] if c in df_period.columns]
        df_filtered = df_period[display_cols].copy().replace({'Nothing': None, 'Neutral': None, '': None})
        df_filtered.dropna(subset=[c for c in display_cols if c != 'Date'], how='all', inplace=True)
        df_display = df_filtered.sort_values('Date', ascending=False)
        
        if not df_display.empty:
            st.download_button(
                label="📥 Export Period Log as CSV",
                data=convert_df(df_display),
                file_name=f"{patient_name}_period_log.csv",
                mime="text/csv",
                type="primary"
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No meaningful entries.")

# --- TAB 3: VITALITY COMPLETIONS ---
with tab3:
    st.markdown("### 🏆 Vitality Quest Completions")
    
    # Fetch live data using your new query
    quest_history = run_query(GET_USER_QUEST_HISTORY, (selected_patient_id,))
    
    if not quest_history:
        st.info("No completed quests found for this patient.")
    else:
        df_quests = pd.DataFrame(quest_history)
        
        # Rename columns for a cleaner display in the dashboard and CSV
        df_quests.rename(columns={
            'completed_on': 'Date Completed',
            'quest_name': 'Quest / Task',
            'points_earned': 'Points Earned'
        }, inplace=True)
        
        st.download_button(
            label="📥 Export Vitality Log as CSV",
            data=convert_df(df_quests),
            file_name=f"{patient_name}_vitality_log.csv",
            mime="text/csv",
            type="primary"
        )
        st.dataframe(df_quests, use_container_width=True, hide_index=True)