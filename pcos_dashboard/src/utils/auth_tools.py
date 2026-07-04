import streamlit as st
import bcrypt
import re

# ==========================================
# 1. PASSWORD CRYPTOGRAPHY
# ==========================================

def hash_password(plain_text_password: str) -> str:
    """
    Hashes a password using bcrypt before saving it to the database.
    Never store plain-text passwords!
    """
    # bcrypt requires bytes, so we encode the string
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string to store in MariaDB VARCHAR column
    return hashed_bytes.decode('utf-8')

def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """
    Checks if the entered password matches the hashed password in the DB.
    """
    password_bytes = plain_text_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)

# ==========================================
# 2. SESSION MANAGEMENT
# ==========================================

def login_user(user_data: dict):
    """
    Saves the user's data securely into Streamlit's session state.
    Call this ONLY after successful password verification.
    """
    st.session_state['user_id'] = user_data['user_id']
    st.session_state['role_id'] = user_data['role_id']
    st.session_state['full_name'] = user_data['full_name']
    st.session_state['email'] = user_data['email']
    st.session_state['logged_in'] = True

def logout_user():
    """
    Completely clears the user's session data and logs them out.
    """
    # Safely remove all authentication keys
    keys_to_clear = ['user_id', 'role_id', 'full_name', 'email', 'logged_in', 'selected_patient_id']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# ==========================================
# 3. ACCESS CONTROL (MIDDLEWARE)
# ==========================================

def require_auth(required_role_ids=None):
    """
    A helper function to place at the top of protected pages.
    It instantly stops unauthorized users from viewing the page.
    
    Args:
        required_role_ids (list): E.g., [2] for Doctors, [3] for Admin, [2, 3] for both.
    """
    if not st.session_state.get('logged_in'):
        st.warning("🔒 Please log in to access this page.")
        st.stop() # Halts the rest of the page from loading
        
    if required_role_ids is not None:
        user_role = st.session_state.get('role_id')
        if user_role not in required_role_ids:
            st.error("🚫 Unauthorized Access. You do not have permission to view this portal.")
            st.stop()

# ==========================================
# 4. INPUT VALIDATION
# ==========================================

def is_valid_email(email: str) -> bool:
    """Validates email format using regex."""
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, email) is not None

def is_strong_password(password: str) -> bool:
    """Ensures password is at least 8 chars long."""
    return len(password) >= 8