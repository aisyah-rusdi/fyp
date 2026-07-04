import mariadb
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_connection():
    try:
        conn = mariadb.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "pcos_db")
        )
        return conn
    except mariadb.Error as e:
        # Only show detailed error in sidebar/logs, not to the main user interface if possible
        print(f"Database Connection Failed: {e}") 
        return None