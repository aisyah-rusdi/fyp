import streamlit as st

def show_disclaimer_banner(message: str, icon: str = "⚠️"):
    """Subtle persistent ribbon — used on dashboard, resource pages."""
    st.markdown(
        f"""
        <div style="
            background-color: #F3E8FF;
            border-left: 4px solid #6B21A8;
            padding: 10px 16px;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #1A1A1A;
            margin-bottom: 1rem;
        ">
            {icon} <em>{message}</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

def show_disclaimer_modal(message: str, key: str = "disclaimer_accepted"):
    """Full gate — blocks page content until user acknowledges."""
    if not st.session_state.get(key, False):
        with st.container(border=True):
            st.warning("⚠️ Please read before continuing")
            st.markdown(f"_{message}_")
            if st.button("I understand, continue →", type="primary", key=f"{key}_btn"):
                st.session_state[key] = True
                st.rerun()
        st.stop()  # Blocks everything below until accepted