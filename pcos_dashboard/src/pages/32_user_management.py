import streamlit as st
import mariadb
import pandas as pd
from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header
from database.connection import get_connection
from database.queries import (
    GET_PENDING_DOCTORS,
    UPDATE_USER_STATUS,
    GET_ALL_USERS
)

# 1. Page Configuration
st.set_page_config(
    page_title="PCOS App - User Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Load Global CSS & Sidebar
load_css("assets/style.css")
render_sidebar(current_page="user_management")
render_header(current_page="user_management")

# 3. Authentication & Role Check
user_id = st.session_state.get('user_id')
user_role = st.session_state.get('role_id') 

if not user_id or user_role != 3: # Assuming 3 is Admin
    st.error("🚫 Unauthorized Access. System Administrators only.")
    st.stop()

# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================
def fetch_pending_doctors():
    conn = get_connection()
    doctors = []
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(GET_PENDING_DOCTORS)
            doctors = cur.fetchall()
        except mariadb.Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    return doctors

def fetch_all_users():
    conn = get_connection()
    users = []
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(GET_ALL_USERS)
            users = cur.fetchall()
        except mariadb.Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    return users

def change_user_status(target_user_id, new_status, user_name):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(UPDATE_USER_STATUS, (new_status, target_user_id))
            conn.commit()
            st.toast(f"✅ {user_name} is now {new_status.upper()}!")
        except mariadb.Error as e:
            st.error(f"Error updating status: {e}")
        finally:
            conn.close()

# ==========================================
# MAIN PAGE LAYOUT
# ==========================================
st.title("🛡️ User Management")
st.markdown("Approve medical professionals and manage platform access.")

tab1, tab2 = st.tabs(["✅ Verification Queue", "👥 User Directory"])

# --- TAB 1: VERIFICATION QUEUE ---
with tab1:
    st.markdown("### Pending Doctor Approvals")
    st.write("These professionals have registered but cannot access patient data until you verify their credentials.")
    
    pending_docs = fetch_pending_doctors()
    
    if not pending_docs:
        st.info("🎉 You're all caught up! There are no pending approvals.")
    else:
        for doc in pending_docs:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.markdown(f"**Dr. {doc['full_name']}**")
                    st.caption(f"📧 {doc['email']}")
                with col2:
                    st.write("**Registered On:**")
                    st.write(doc['created_at'].strftime("%Y-%m-%d") if doc['created_at'] else "Unknown")
                with col3:
                    st.write("") # Spacing
                    c_app, c_rej = st.columns(2)
                    with c_app:
                        if st.button("Approve", key=f"app_{doc['user_id']}", type="primary", use_container_width=True):
                            change_user_status(doc['user_id'], 'active', doc['full_name'])
                            st.rerun()
                    with c_rej:
                        if st.button("Reject", key=f"rej_{doc['user_id']}", use_container_width=True):
                            change_user_status(doc['user_id'], 'rejected', doc['full_name'])
                            st.rerun()

# --- TAB 2: USER DIRECTORY ---
with tab2:
    st.markdown("### Platform User Roster")
    st.write("Search, view, and manage all accounts on the platform.")
    
    all_users = fetch_all_users()
    
    if all_users:
        # 1. Convert to DataFrame for clean display
        df = pd.DataFrame(all_users)
        
        # Map role IDs to readable text
        role_map = {1: "Patient", 2: "Professional", 3: "Admin"}
        df['Role'] = df['role_id'].map(role_map)
        
        # Format dates
        df['Joined'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        
        # Reorder and rename columns for the UI
        df_display = df[['user_id', 'full_name', 'email', 'Role', 'status', 'Joined']]
        df_display.columns = ['ID', 'Name', 'Email', 'Role', 'Status', 'Joined']
        
        # Display the searchable, sortable dataframe
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.write("---")
        
        # 2. Account Action Area
        st.markdown("#### Take Action on an Account")
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            user_options = {"--- Select a User ---": None} 
            user_options.update({f"{u['full_name']} ({u['email']})": u['user_id'] for u in all_users})
            
            selected_user_label = st.selectbox("Select User:", options=list(user_options.keys()))
            selected_id = user_options[selected_user_label]
            
        with action_col2:
            action_options = ["--- Select an Action ---", "Suspend Account", "Reactivate Account"]
            action_choice = st.selectbox("Action:", action_options)
            
        with action_col3:
            st.write("<br>", unsafe_allow_html=True) # Align button with inputs
            
            # 3. Disable the button if EITHER dropdown is on the placeholder
            is_form_incomplete = (selected_id is None) or (action_choice == "--- Select an Action ---")
            
            if st.button("Apply Changes", type="primary", use_container_width=True, disabled=is_form_incomplete):
                new_stat = 'suspended' if action_choice == "Suspend Account" else 'active'
                # Extract just the name for the toast message
                just_name = selected_user_label.split(" (")[0]
                change_user_status(selected_id, new_stat, just_name)
                st.rerun()
    else:
        st.warning("No users found in the database.")