import streamlit as st
import pymysql
import pandas as pd
import math
from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header
from database.connection import get_connection
from database.queries import (
    SEARCH_PATIENT_BY_EMAIL_OR_USERNAME,
    LINK_DOCTOR_PATIENT,
    GET_DOCTOR_PATIENTS,
    GET_USER_PREDICTION_HISTORY
)

# 1. Page Configuration
st.set_page_config(page_title="PCOS App - Pro Connect", layout="wide")

# 2. Load UI Elements
load_css("assets/style.css")
render_sidebar(current_page="pro_connect")
render_header(current_page="pro_connect")

# 3. Auth & Role Check
user_id = st.session_state.get('user_id')
user_role = st.session_state.get('role_id') 

if not user_id or user_role != 2:
    st.error("🚫 Unauthorized Access.")
    st.stop()

# ==========================================
# DB FUNCTIONS
# ==========================================
def fetch_my_patients():
    conn = get_connection()
    patients = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(GET_DOCTOR_PATIENTS, (user_id,))
            patients = cur.fetchall()
        finally:
            conn.close()
    return patients

def add_patient_link(patient_id):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(LINK_DOCTOR_PATIENT, (user_id, patient_id))
            conn.commit()
            st.success("✅ Patient successfully connected!")
            st.rerun()
        finally:
            conn.close()

# ==========================================
# HEADER & ADD PATIENT SECTION
# ==========================================
st.title("🩺 Pro Connect Dashboard")

st.subheader("➕ Add New Patient")
st.write("Search for a patient by their email address or username to link them to your account.")

# Use vertical_alignment to ensure the button and input line up perfectly
col_search, col_btn = st.columns([4, 1], vertical_alignment="bottom")

with col_search:
    search_term = st.text_input(
        "Patient Email or Username", 
        placeholder="Enter Patient Email or Username",
        label_visibility="collapsed" 
    )
with col_btn:
    do_search = st.button("Search", type="primary", use_container_width=True)

# 1. Handle the Search Click
if do_search and search_term:
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # We pass search_term twice because the SQL query will check both columns
            cur.execute(SEARCH_PATIENT_BY_EMAIL_OR_USERNAME, (search_term, search_term))
            found = cur.fetchone()
            
            if found:
                # Save the patient to session state so Streamlit remembers them
                st.session_state['found_patient'] = found 
            else:
                st.session_state['found_patient'] = None
                st.error("Patient not found. Please check the spelling and try again.")
        finally:
            conn.close()

# 2. Display the Found Patient (Independent of the Search button click)
if st.session_state.get('found_patient'):
    patient_to_link = st.session_state['found_patient']
    
    # Show the result in a clean info box
    st.info(f"**Found:** {patient_to_link['full_name']} ({patient_to_link['email']})")
    
    col_link, col_clear = st.columns([1, 4])
    with col_link:
        if st.button("Link this Patient", type="secondary"):
            # Clear the search result from session state before running the link function
            patient_id = patient_to_link['user_id']
            del st.session_state['found_patient'] 
            add_patient_link(patient_id)
            
    with col_clear:
        if st.button("Clear Search"):
            del st.session_state['found_patient']
            st.rerun()

st.divider()

# ==========================================
# PATIENT LIST, FILTERING & PAGINATION
# ==========================================
all_patients = fetch_my_patients()

# --- Filtering Logic ---
col_f1, col_f2 = st.columns([3, 2])
with col_f1:
    search_query = st.text_input("🔍 Filter by Name or Email", placeholder="Start typing...")

# Apply Filter
filtered_patients = [
    p for p in all_patients 
    if search_query.lower() in p['full_name'].lower() or search_query.lower() in p['email'].lower()
] if search_query else all_patients

# --- Pagination Logic ---
items_per_page = 25
total_pages = math.ceil(len(filtered_patients) / items_per_page) if filtered_patients else 1

with col_f2:
    page = st.selectbox("Page", range(1, total_pages + 1)) if total_pages > 1 else 1

start_idx = (page - 1) * items_per_page
end_idx = start_idx + items_per_page
page_patients = filtered_patients[start_idx:end_idx]

# --- Display List ---
st.subheader(f"👥 My Patients ({len(filtered_patients)})")

if not page_patients:
    st.info("No patients found.")
else:
    # Header Row
    h_col1, h_col2, h_col3, h_col4 = st.columns([3, 3, 2, 1])
    h_col1.markdown("**Full Name**")
    h_col2.markdown("**Email**")
    h_col3.markdown("**Connected Date**")
    h_col4.markdown("**Action**")
    st.divider()

    for p in page_patients:
        p_col1, p_col2, p_col3, p_col4 = st.columns([3, 3, 2, 1])
        
        with p_col1:
            st.write(p['full_name'])
        with p_col2:
            st.write(p['email'])
        with p_col3:
            st.write(p['connected_at'].strftime("%Y-%m-%d") if p['connected_at'] else "N/A")
        with p_col4: # <-- This just needed to be indented!
            if st.button(
                "📊", 
                key=f"insight_{p['user_id']}", 
                help="Click here to monitor this patient's PCOS insights, history, and clinical profile."
            ):
                st.session_state['selected_patient_id'] = p['user_id']
                st.session_state['selected_patient_name'] = p['full_name']
                st.switch_page("pages/22_pro_monitor.py")