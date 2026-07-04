import streamlit as st
import os

def load_css(path="assets/style.css"):
    with open(path, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)