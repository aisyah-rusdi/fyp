import streamlit as st
import mariadb
import base64
import os
from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header
from database.connection import get_connection  
from database.queries import GET_USER_PROFILE_BY_ID

# --- 🔒 SECURITY CHECK ---
if 'user_id' not in st.session_state or not st.session_state['user_id']:
    st.warning("⚠️ You must log in to view your profile.")
    st.switch_page("app.py")
    st.stop()

# 1. Page Configuration
st.set_page_config(
    page_title="PCOS App - Profile",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Load Global CSS
load_css("assets/style.css")

# 3. Render Navigation
render_sidebar(current_page="profile")
render_header(current_page="profile")

# --- 4. FETCH USER DATA FUNCTION ---
def get_user_profile(user_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True) 
        cur.execute(GET_USER_PROFILE_BY_ID, (user_id,))
        return cur.fetchone()
    except mariadb.Error as e:
        st.error(f"Error fetching profile: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Load the real data into a variable
user_data = get_user_profile(st.session_state['user_id'])

if not user_data:
    st.error("Could not load user profile. Please try logging in again.")
    st.stop()

# 5. Main Profile Content
st.title("My Profile")
st.write("") 

col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    # 1. Initialize memory variable to track if uploader should be visible
    if 'show_uploader' not in st.session_state:
        st.session_state['show_uploader'] = False

    # --- Profile Picture Section ---

    # 1. Determine the image source
    default_avatar = "https://img.icons8.com/color/96/user-female-circle--v1.png"
    img_src = default_avatar # Start with the default

    # Check if the database has a profile picture saved for this user
    # (Assuming your database column is called 'profile_pic' and stores the file path)
    if user_data.get('profile_pic') and os.path.exists(user_data['profile_pic']):
        # Convert the local image file to base64 so HTML can read it
        with open(user_data['profile_pic'], "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            img_src = f"data:image/jpeg;base64,{encoded_string}"

    # 2. Render the circular image
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <img src="{img_src}" style="width: 120px; height: 120px; margin-bottom: 5px; border-radius: 50%; object-fit: cover; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
    </div>
    """, unsafe_allow_html=True)

    # --- UPLOAD SECTION (Drag & Drop Box) ---
    # This only appears if they clicked "Upload New Photo"
    if st.session_state['show_uploader']:
        uploaded_photo = st.file_uploader("Choose a new profile picture", type=["png", "jpg", "jpeg"])
        
        if uploaded_photo is not None:
            st.image(uploaded_photo, caption="New Profile Picture Preview", width=120)
            
            if st.button("Save Profile Picture", type="primary", use_container_width=True):
                # (Your logic to save the image to the database goes here)
                st.success("Photo saved successfully!")
                
                # Hide the uploader again after successfully saving
                st.session_state['show_uploader'] = False 
                st.rerun()
                
        # Cancel button
        if st.button("Cancel Upload", use_container_width=True):
            st.session_state['show_uploader'] = False
            st.rerun()

    st.write("") # Spacer to give a little breathing room

    # --- USER INFO ---
    st.markdown(f"<h3 style='text-align: center; margin-top: 5px;'>{user_data['full_name']}</h3>", unsafe_allow_html=True)
    
    role_map = {1: "General User", 2: "Health Pro", 3: "Admin"}
    role_label = role_map.get(user_data['role_id'], "Member")
    
    join_year = user_data['created_at'].year if user_data.get('created_at') else "2024"
    st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.9em;'>{role_label} | Member since {join_year}</p>", unsafe_allow_html=True) 


with col_right:
    # --- User Details Form ---
    with st.container(border=True):
        st.subheader("Personal Information")
        st.write("")
        
        with st.form("profile_form"):
            # Split full name for display (Optional logic)
            full_name_parts = user_data['full_name'].split(" ", 1)
            first_name_val = full_name_parts[0]
            last_name_val = full_name_parts[1] if len(full_name_parts) > 1 else ""

            row1_a, row1_b = st.columns(2)
            with row1_a:
                new_first_name = st.text_input("First Name", value=first_name_val)
            with row1_b:
                new_last_name = st.text_input("Last Name", value=last_name_val)
            
            # --- CONDITIONAL LICENSE NUMBER ---
            # If the user is a Health Pro (role_id == 2), show the license input next to the email
            if user_data.get('role_id') == 2:
                row_email_a, row_email_b = st.columns(2)
                with row_email_a:
                    st.text_input("Email Address", value=user_data['email'], disabled=True)
                with row_email_b:
                    # Safely get the license number if it exists in the dict
                    lic_val = user_data.get('license_number', "") 
                    new_license = st.text_input("Professional License Number", value=lic_val)
            else:
                # Normal users just get the full-width email field
                st.text_input("Email Address", value=user_data['email'], disabled=True)
            
            row2_a, row2_b = st.columns(2)
            with row2_a:
                # If you have phone in DB, fetch it. Otherwise, leave blank or static for now.
                st.text_input("Phone Number", value="") 
            with row2_b:
                st.date_input("Date of Birth")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Form Buttons
            empty_col, btn_col = st.columns([4, 2]) 
            with btn_col:
                submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
            
            if submitted:
                # TODO: Add UPDATE SQL query here to save changes back to DB
                st.success(f"Profile updated! (Name: {new_first_name} {new_last_name})")

    # --- Account Settings Section ---
    st.write("")
    with st.expander("Account Settings & Security"):
        st.warning("Password Change")
        st.text_input("Current Password", type="password")
        st.text_input("New Password", type="password")
        st.button("Update Password")