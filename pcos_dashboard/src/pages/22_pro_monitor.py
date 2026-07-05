import streamlit as st
import pymysql
import pandas as pd
from utils.ui_helpers import load_css
from components.header import render_header
from components.sidebar import render_sidebar
from database.connection import get_connection
from database.queries import (
    GET_USER_PROFILE_BY_ID,
    GET_USER_PREDICTION_HISTORY,
    GET_USER_PERIOD_LOGS,
    GET_USER_QUEST_SCORE,
    GET_CLINICAL_NOTES,
    INSERT_CLINICAL_NOTE,
    DELETE_CLINICAL_NOTE,
    UPDATE_CLINICAL_NOTE
)

st.set_page_config(
    page_title="PCOS App - Patient Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css("assets/style.css")
render_sidebar(current_page="pro_connect")
render_header(current_page="pro_monitor")

# --- Auth ---
user_id = st.session_state.get('user_id')
user_role = st.session_state.get('role_id')
selected_patient_id = st.session_state.get('selected_patient_id')

if not user_id:
    st.warning("Please log in to access the portal.")
    st.stop()
if user_role != 2:
    st.error("🚫 Unauthorized Access. This portal is strictly for Healthcare Professionals.")
    st.stop()
if not selected_patient_id:
    st.warning("No patient selected. Please select a patient from the connection list.")
    if st.button("Go to Pro Connect"):
        st.switch_page("pages/21_pro_connect.py")
    st.stop()

# --- Session State Initialization ---
if 'show_note_form' not in st.session_state:
    st.session_state.show_note_form = False
if 'editing_note_id' not in st.session_state:
    st.session_state.editing_note_id = None

# ==========================================
# DATA FETCHING
# ==========================================
def run_query(sql, params=()):
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    except pymysql.MySQLError as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        conn.close()

def run_query_one(sql, params=()):
    rows = run_query(sql, params)
    return rows[0] if rows else None

def run_write(query, params):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
        except pymysql.MySQLError as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()

# ==========================================
# CLINICAL NOTES DIALOG
# ==========================================
@st.dialog("📝 Clinical Notes", width="large")
def clinical_notes_dialog(patient_id, doctor_id):
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown("#### Notes for this patient")
    with col_btn:
        if st.button("➕ Add Entry", type="primary", use_container_width=True):
            st.session_state.show_note_form = not st.session_state.show_note_form
            st.session_state.pop('editing_note_id', None)

    if st.session_state.get('show_note_form', False):
        st.divider()
        st.markdown("##### New Clinical Note")
        new_title = st.text_input("Entry Title", placeholder="e.g., Follow-up Consultation", key="note_title_input")
        new_content = st.text_area("Note Details", placeholder="Enter your clinical observations here...", key="note_content_input", height=120)

        col_save, col_cancel = st.columns([1, 1])
        with col_save:
            if st.button("💾 Save Note", type="primary", use_container_width=True):
                if new_title.strip():
                    run_write(INSERT_CLINICAL_NOTE, (doctor_id, patient_id, new_title.strip(), new_content.strip()))
                    st.session_state.show_note_form = False
                    st.rerun()
                else:
                    st.error("Title is required.")
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_note_form = False
                st.rerun()

    st.divider()
    notes = run_query(GET_CLINICAL_NOTES, (patient_id, doctor_id))

    if not notes:
        st.info("No clinical notes recorded.")
    else:
        h1, h2, h3, h4 = st.columns([2, 4, 1, 1])
        h1.markdown("**Date**")
        h2.markdown("**Entry Title**")
        h3.markdown("**Edit**")
        h4.markdown("**Delete**")
        st.divider()

        for note in notes:
            note_id = note['note_id']
            is_editing = st.session_state.get('editing_note_id') == note_id

            if is_editing:
                edit_title = st.text_input("Edit Title", value=note['title'], key=f"edit_title_{note_id}")
                edit_content = st.text_area("Edit Details", value=note.get('content', ''), key=f"edit_content_{note_id}", height=100)
                es1, es2 = st.columns([1, 1])
                with es1:
                    if st.button("💾 Save", key=f"save_{note_id}", type="primary", use_container_width=True):
                        run_write(UPDATE_CLINICAL_NOTE, (edit_title.strip(), edit_content.strip(), note_id, doctor_id))
                        st.session_state.pop('editing_note_id', None)
                        st.rerun()
                with es2:
                    if st.button("Cancel", key=f"cancel_{note_id}", use_container_width=True):
                        st.session_state.pop('editing_note_id', None)
                        st.rerun()
            else:
                c1, c2, c3, c4 = st.columns([2, 4, 1, 1], vertical_alignment="center")
                c1.write(note.get('created_at', 'N/A'))
                c2.write(note.get('title', ''))
                with c3:
                    if st.button("✏️", key=f"edit_{note_id}", use_container_width=True):
                        st.session_state['editing_note_id'] = note_id
                        st.session_state.show_note_form = False
                        st.rerun()
                with c4:
                    if st.button("🗑️", key=f"del_{note_id}", use_container_width=True):
                        run_write(DELETE_CLINICAL_NOTE, (note_id, doctor_id))
                        st.rerun()
            st.write("") 

# ==========================================
# LAYOUT & GRID DASHBOARD
# ==========================================

# 1. Header & Back Button (7:2 Ratio)
head_col, btn_col = st.columns([7, 2], vertical_alignment="bottom")
with head_col:
    st.title("📈 Patient Monitoring")
with btn_col:
    if st.button("← Back to List", use_container_width=True):
        st.session_state.pop('selected_patient_id', None)
        st.switch_page("pages/21_pro_connect.py")

st.divider()

# 2. PROFILE ROW (3:3:3 Ratio)
profile = run_query_one(GET_USER_PROFILE_BY_ID, (selected_patient_id,))

prof1, prof2, prof3 = st.columns(3, vertical_alignment="center")
with prof1:
    st.markdown(f"**👤 {profile.get('full_name', 'N/A')}**")
    st.caption(profile.get('email', 'N/A'))
with prof2:
    joined = profile.get('created_at')
    st.markdown("**Joined**")
    st.caption(joined.strftime('%b %d, %Y') if joined else 'N/A')
with prof3:
    if st.button("📝 Clinical Notes", use_container_width=True):
        clinical_notes_dialog(selected_patient_id, user_id)

st.divider()

# --- MIDDLE ROW: High Level Metrics ---
col_risk, col_period, col_vital = st.columns(3)

# RISK 
with col_risk:
    st.markdown("### 🔬 PCOS Risk")
    history = run_query(GET_USER_PREDICTION_HISTORY, (selected_patient_id,))
    if not history:
        st.info("No assessment completed yet.")
    else:
        latest = history[0]
        st.metric("Risk Level", latest.get('risk_level', 'N/A'), f"Score: {round(latest.get('risk_score', 0) * 100, 1)}%")

# PERIOD TRACKER
with col_period:
    st.markdown("### 🩸 Period Tracker")
    period_logs = run_query(GET_USER_PERIOD_LOGS, (selected_patient_id,))
    
    if not period_logs:
        st.info("No tracking data logged yet.")
    else:
        df_period = pd.DataFrame(period_logs)
        df_period['Date'] = pd.to_datetime(df_period['log_date'])
        display_cols = [c for c in ['Date', 'period', 'mood', 'symptoms', 'cervical_fluid'] if c in df_period.columns]
        df_filtered = df_period[display_cols].copy().replace({'Nothing': None, 'Neutral': None, '': None})
        df_filtered.dropna(subset=[c for c in display_cols if c != 'Date'], how='all', inplace=True)
        
        if not df_filtered.empty:
            df_chart = df_filtered[['Date']].copy()
            df_chart['Activity'] = "Log Entry"
            st.scatter_chart(df_chart, x='Date', y='Activity', color="#9333EA", height=150)
# VITALITY SCORE
with col_vital:
    st.markdown("### 🏆 Vitality")
    quest_data = run_query_one(GET_USER_QUEST_SCORE, (selected_patient_id,))
    
    if not quest_data:
        st.info("No vitality points earned yet.")
    else:
        total_vitality = quest_data.get('total_vitality') or 0
        streak = quest_data.get('streak') or 0
        
        v1, v2 = st.columns(2)
        v1.metric("⚡ Total Points", total_vitality)
        v2.metric("🔥 Current Streak", f"{streak} days")

st.write("")
st.divider()

# 3. VIEW DETAIL BUTTON (Bottom Right)
# Creates empty space on the left, pushing the button to the right side
_, detail_col = st.columns([5, 1])
with detail_col:
    if st.button("🔍 View Detail", type="primary", use_container_width=True):
        st.switch_page("pages/23_pro_details.py")