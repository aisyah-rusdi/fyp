# src/components/header.py

import streamlit as st
import time
from streamlit_cookies_controller import CookieController

def render_header(current_page="dashboard"):
    """
    Renders the Top Navigation Bar with dynamic user info.
    """
    cookie_controller = CookieController()
    
    # 1. Fetch User Info
    user_name = st.session_state.get('full_name', 'Guest User')
    
    # 2. Layout Configuration (Tighter spacing!)
    col_widths = [5.0, 1.0, 0.5, 0.5, 1.5]

    with st.container():
        c1, c2, c3, c4, c5 = st.columns(col_widths, gap="small", vertical_alignment="center")
        
        # Col 1: Massive Left Spacer
        with c1:
            st.empty()
        
        # Col 2: Username
        with c2:
            st.page_link("pages/01_profile.py", label=f"**{user_name}**", help="Go to Profile")

        # Col 3: Default Avatar
        with c3:
            avatar_url = "https://img.icons8.com/color/96/user-female-circle--v1.png"
            st.markdown(f"""
            <div style="display:flex; justify-content:center; align-items:center; height:38px; margin-top:-8px;">
                <img src="{avatar_url}" style="width:38px; height:38px; border-radius:50%; object-fit:cover;">
            </div>
            """, unsafe_allow_html=True)

        # Col 4: Notification Bell
        with c4:
            st.markdown("""
            <div style="display:flex; justify-content:center; align-items:center; height:38px; margin-top:-8px; cursor:pointer;">
                <span style="font-size:22px; line-height:1;">&#128276;</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Col 5: Logout Button
        with c5:
            if st.button("Log Out", key="header_logout_btn", type="secondary", use_container_width=True):
                # 1. Safely attempt to remove the cookie
                try:
                    cookie_controller.remove('pcos_auth_email')
                except KeyError:
                    pass # If the cookie is already gone, just ignore and keep going!
                
                # 2. Safely clear all session state variables
                for key in list(st.session_state.keys()):
                    st.session_state.pop(key, None)
                
                # 3. Redirect to the login/home app page
                time.sleep(0.5)
                st.switch_page("app.py")