import streamlit as st
from utils.ui_helpers import load_css

def render_sidebar(current_page=None):
    
    # 1. Load Styles & Fix "Invisible Sidebar" Bug
    load_css()
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: block !important; visibility: visible !important; }
    </style>
    """, unsafe_allow_html=True)

    role = st.session_state.get('role_id')

    with st.sidebar:
        st.markdown("### PCOS Dashboard")
        st.markdown("<br>", unsafe_allow_html=True)

        # ===================================
        # SECTION 1: UNIVERSAL PAGES (Visible to ALL Roles)
        # ===================================
        
        if st.button("Dashboard", use_container_width=True, 
                    type="primary" if current_page == "dashboard" else "secondary"):
            st.switch_page("pages/02_dashboard.py")

        if role == 1:
            if st.button("Questionnaire", use_container_width=True, 
                        type="primary" if current_page == "questionnaire" else "secondary"):
                st.switch_page("pages/03_questionnaire.py")

        if st.button("Resources", use_container_width=True, 
                    type="primary" if current_page == "resources" else "secondary"):
            st.switch_page("pages/04_resource.py")

        # ===================================
        # SECTION 2: ROLE SEPARATOR
        # ===================================
        st.markdown("---")

        # ===================================
        # SECTION 3: ROLE-SPECIFIC PAGES
        # ===================================
        
        # --- ROLE 1: PATIENT ---
        if role == 1:
            if st.button("My Journal", use_container_width=True, 
                        type="primary" if current_page == "journal" else "secondary"):
                st.switch_page("pages/11_user_journal.py")
                
            if st.button("Daily Quests", use_container_width=True, 
                        type="primary" if current_page == "quests" else "secondary"):
                st.switch_page("pages/12_user_daily_quest.py")
                
            if st.button("My Curated Resources", use_container_width=True, 
                        type="primary" if current_page == "personal_resources" else "secondary"):
                st.switch_page("pages/13_user_personal_resource.py")

        # --- ROLE 2: PROFESSIONAL ---
        elif role == 2:
            if st.button("Connect Patients", use_container_width=True, 
                        type="primary" if current_page == "pro_connect" else "secondary"):
                st.switch_page("pages/21_pro_connect.py")

        # --- ROLE 3: ADMIN ---
        elif role == 3:
            # Fixed the mismatch here!
            if st.button("System Stats", use_container_width=True, 
                        type="primary" if current_page == "admin_dashboard" else "secondary"):
                st.switch_page("pages/31_admin_dashboard.py")
                
            # Fixed the mismatch here!
            if st.button("User Management", use_container_width=True, 
                        type="primary" if current_page == "user_management" else "secondary"):
                st.switch_page("pages/32_user_management.py")