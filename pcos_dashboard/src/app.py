#python -m streamlit run app.py

import streamlit as st
import time
import os
import mariadb
import random
from streamlit_cookies_controller import CookieController

# Ensure these match your file names and folder structures perfectly!
from utils.email_tool import send_otp_email  
from utils.ui_helpers import load_css
from utils.auth_tools import (
    hash_password, 
    verify_password, 
    login_user, 
    is_valid_email, 
    is_strong_password
)
from database.connection import get_connection
from database.queries import GET_USER_BY_EMAIL, CREATE_USER, GET_USER_NAME_BY_EMAIL

# 1. PAGE CONFIG (Must be the first command)
st.set_page_config(
    page_title="PCOS App - Login",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. INIT COOKIE CONTROLLER
cookie_controller = CookieController()

# ==========================================
# AUTO-LOGIN (COOKIE RESTORE)
# ==========================================
if not st.session_state.get('logged_in'):
    # Wrap the cookie fetch in a try-except block to handle the split-second where cookies are 'None'
    try:
        saved_email = cookie_controller.get('pcos_auth_email')
    except TypeError:
        # If the cookie controller isn't ready yet, safely default to None
        saved_email = None

    if saved_email:
        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(GET_USER_BY_EMAIL, (saved_email,))
                result = cur.fetchone()
                
                if result:
                    user_id, stored_hash, role_id, full_name, status = result
                    if status == 'active' or (role_id != 2 and status != 'pending'):
                        user_data = {
                            'user_id': user_id,
                            'role_id': role_id,
                            'full_name': full_name,
                            'email': saved_email,
                            'status': status
                        }
                        login_user(user_data)
                        
                        if role_id == 3:
                            st.switch_page("pages/31_admin_dashboard.py")
                        else:
                            st.switch_page("pages/02_dashboard.py")
            except mariadb.Error as e:
                pass 
            finally:
                conn.close()

# ==============================
# OTP VERIFICATION TRIGGER
# ==============================
def trigger_verification(email_input):
    conn = get_connection()
    if not conn:
        st.error("Database connection failed.")
        return None
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Try to find the user in the database
        cursor.execute(GET_USER_NAME_BY_EMAIL, (email_input,))
        result = cursor.fetchone()
        
        # 2. Pick the name: Use database name if found, otherwise use "User"
        display_name = result['full_name'] if result and result.get('full_name') else "User"
            
        otp = str(random.randint(100000, 999999))
        
        # 3. Pass the name to the email tool
        if send_otp_email(email_input, otp, username=display_name):
            return otp  # Return OTP so it can be saved in session_state
        else:
            st.error("Failed to send email. Please check your network or SMTP settings.")
            return None
            
    except mariadb.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# 3. LOAD ASSETS
load_css("assets/style.css")

# Hide Sidebar on Login Page
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# 4. SESSION STATE
if 'page_mode' not in st.session_state:
    st.session_state['page_mode'] = 'login'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def toggle_mode():
    st.session_state['page_mode'] = 'signup' if st.session_state['page_mode'] == 'login' else 'login'

def go_to_forgot():
    st.session_state['page_mode'] = 'forgot'

def go_to_login():
    st.session_state['page_mode'] = 'login'
    # Clean up OTP data if they cancel safely
    st.session_state.pop('otp_sent', None)
    st.session_state.pop('target_email', None)

# ==============================
# MAIN LAYOUT
# ==============================
left_space, card_container, right_space = st.columns([1, 5, 1])

with card_container:
    with st.container(border=True):
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        col_brand, col_form = st.columns([1, 1], gap="large")

        # --- LEFT SIDE (Branding) ---
        with col_brand:
            st.markdown('<div class="brand-title" style="text-align: center; font-size: 2.5rem; font-weight: bold; color: #6B21A8;">PCOS Dashboard</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="brand-subtitle" style="text-align: center; padding: 20px; color: #6B7280;">
                Welcome back! Log in to access your personalized health insights 
                and connect with resources tailored just for you.
            </div>
            """, unsafe_allow_html=True)

        # --- RIGHT SIDE (Forms) ---
        with col_form:
            
            # === LOGIN MODE ===
            if st.session_state['page_mode'] == 'login':
                st.markdown('<div class="login-header" style="font-size: 1.8rem; margin-bottom: 20px;">Log In</div>', unsafe_allow_html=True)
                
                login_email = st.text_input("Email", key="l_email")
                login_password = st.text_input("Password", type="password", key="l_pass")

                # Forgot Password Button
                st.button("Forgot Password?", on_click=go_to_forgot, type="tertiary", help="Click to reset your password")

                if st.button("Sign In", type="primary", use_container_width=True):
                    if not login_email or not login_password:
                        st.warning("Please enter both email and password.")
                    else:
                        conn = get_connection()
                        if conn:
                            try:
                                cur = conn.cursor()
                                cur.execute(GET_USER_BY_EMAIL, (login_email,))
                                result = cur.fetchone()

                                if result:
                                    user_id, stored_hash, role_id, full_name, status = result
                                    
                                    if role_id == 2 and status != 'active':
                                        st.error("Your professional account is pending Admin approval. Please check back later.")
                                        
                                    elif verify_password(login_password, stored_hash):
                                        user_data = {
                                            'user_id': user_id,
                                            'role_id': role_id,
                                            'full_name': full_name,
                                            'email': login_email,
                                            'status': status
                                        }
                                        login_user(user_data)
                                        
                                        # --- SAFETY NET FOR COOKIE SAVING ---
                                        try:
                                            cookie_controller.set('pcos_auth_email', login_email, max_age=86400)
                                        except TypeError:
                                            st.warning("Secure storage is initializing... Please click Sign In one more time!")
                                            st.stop()
                                        # ------------------------------------
                                        
                                        st.success(f"Welcome back, {full_name}!")
                                        time.sleep(0.5)
                                        
                                        if role_id == 3:
                                            st.switch_page("pages/31_admin_dashboard.py")
                                        else:
                                            st.switch_page("pages/02_dashboard.py")
                                    else:
                                        st.error("Invalid credentials")
                                else:
                                    st.error("User not found.")
                            except mariadb.Error as e:
                                st.error(f"Database error: {e}")
                            finally:
                                conn.close()

                # Footer Text
                st.markdown("<hr style='margin: 20px 0; opacity: 0.3;'>", unsafe_allow_html=True)
                col_text, col_btn = st.columns([1.5, 1]) 
                with col_text:
                    st.markdown("<div style='text-align: right; padding-top: 8px; color: #666;'>Not registered yet?</div>", unsafe_allow_html=True)
                with col_btn:
                    st.button("Create Account", on_click=toggle_mode, key="goto_signup", use_container_width=True)

            # === FORGOT PASSWORD MODE ===
            elif st.session_state['page_mode'] == 'forgot':
                st.markdown('<div class="login-header" style="font-size: 1.8rem; margin-bottom: 20px;">Reset Password</div>', unsafe_allow_html=True)
                
                # Step 1: Request OTP
                if "otp_sent" not in st.session_state:
                    reset_email = st.text_input("Enter your registered email", key="f_email")
                    
                    if st.button("Send Reset Code", type="primary", use_container_width=True):
                        if not reset_email:
                            st.warning("Please enter your email address.")
                        else:
                            otp_code = trigger_verification(reset_email)
                            
                            if otp_code:
                                st.session_state['otp_sent'] = otp_code
                                st.session_state['target_email'] = reset_email
                                st.success("Verification code sent to your email!")
                                st.rerun()
                                
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.button("Back to Login", on_click=go_to_login, use_container_width=True)

                # Step 2: Verify OTP and set new password
                else:
                    st.info(f"Code sent to **{st.session_state['target_email']}**")
                    entered_otp = st.text_input("Enter 6-Digit Code", key="f_otp")
                    new_pw = st.text_input("New Password", type="password", key="f_new_pw")
                    confirm_pw = st.text_input("Confirm New Password", type="password", key="f_conf_pw")

                    if st.button("Reset Password", type="primary", use_container_width=True):
                        if not entered_otp or not new_pw or not confirm_pw:
                            st.warning("Please fill all fields.")
                        elif entered_otp != st.session_state['otp_sent']:
                            st.error("Invalid verification code.")
                        elif new_pw != confirm_pw:
                            st.error("Passwords do not match.")
                        elif not is_strong_password(new_pw):
                            st.error("Password must be at least 8 characters long.")
                        else:
                            conn = get_connection()
                            if conn:
                                try:
                                    cur = conn.cursor()
                                    hashed = hash_password(new_pw)
                                    cur.execute("UPDATE users SET password_hash=? WHERE email=?", (hashed, st.session_state['target_email']))
                                    conn.commit()
                                    st.success("Password reset successful! You can now log in.")
                                    
                                    # Clean up and route back to login
                                    st.session_state.pop('otp_sent', None)
                                    st.session_state.pop('target_email', None)
                                    time.sleep(2)
                                    st.session_state['page_mode'] = 'login'
                                    st.rerun()
                                except mariadb.Error as e:
                                    st.error(f"Failed to update password: {e}")
                                finally:
                                    conn.close()

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.button("Cancel", on_click=go_to_login, use_container_width=True)

            # === SIGNUP MODE ===
            else:
                st.markdown('<div class="login-header" style="font-size: 1.8rem; margin-bottom: 20px;">Sign Up</div>', unsafe_allow_html=True)
                
                s_username = st.text_input("Username", key="s_user")
                s_full_name = st.text_input("Full Name", key="s_name")
                s_email = st.text_input("Email", key="s_email")
                
                role_options = {"Patient": 1, "Health Professional": 2}
                selected_role_name = st.selectbox("I am registering as a...", options=list(role_options.keys()), key="s_role")
                selected_role_id = role_options[selected_role_name]
                
                license_no = ""
                if selected_role_id == 2:
                    st.info("💡 Note: Professional accounts require Admin approval before full access to patient data is granted.")
                    license_no = st.text_input("Annual Practicing Certificate (APC) No.", key="s_license")

                s_password = st.text_input("Password", type="password", key="s_pass")
                s_confirm = st.text_input("Confirm Password", type="password", key="s_conf")

                if st.button("Create Account", type="primary", use_container_width=True):
                    if not s_username or not s_email or not s_password or (selected_role_id == 2 and not license_no):
                        st.warning("Please fill all required fields.")
                    elif not is_valid_email(s_email):
                        st.error("Please enter a valid email format (e.g., name@example.com).")
                    elif not is_strong_password(s_password):
                        st.error("Password must be at least 8 characters long.")
                    elif s_password != s_confirm:
                        st.error("Passwords do not match")
                    else:
                        conn = get_connection()
                        if conn:
                            try:
                                cur = conn.cursor()
                                hashed_pw = hash_password(s_password)
                                
                                # Set status and license based on role
                                initial_status = 'pending' if selected_role_id == 2 else 'active'
                                db_license = license_no if selected_role_id == 2 else None

                                # === ADD THESE 4 LINES ===
                                print("==== DEBUG INFO ====")
                                print(f"Selected Role ID: {selected_role_id}")
                                print(f"Status sending to DB: {initial_status}")
                                print("====================")

                                # Execute query
                                cur.execute(CREATE_USER, (selected_role_id, s_username, s_full_name, s_email, hashed_pw, db_license, initial_status))
                                conn.commit()

                                if selected_role_id == 2:
                                    st.success("Account created! Please wait for admin approval before full features unlock.")
                                else:
                                    st.success("Account created! Please log in.")
                                    
                                time.sleep(2)
                                st.session_state['page_mode'] = 'login'
                                st.rerun()
                            except mariadb.IntegrityError:
                                st.error("Username or Email already exists")
                            finally:
                                conn.close()

                # Footer Text
                st.markdown("<hr style='margin: 20px 0; opacity: 0.3;'>", unsafe_allow_html=True)
                col_text, col_btn = st.columns([1.5, 1])
                with col_text:
                    st.markdown("<div style='text-align: right; padding-top: 8px; color: #666;'>Already have an account?</div>", unsafe_allow_html=True)
                with col_btn:
                    st.button("Log In", on_click=toggle_mode, key="goto_login", use_container_width=True)