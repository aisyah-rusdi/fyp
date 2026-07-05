import pymysql
import pymysql.cursors
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "pcos_db"),
            cursorclass=pymysql.cursors.DictCursor  # enables dict-style rows by default
        )
        return conn
    except pymysql.MySQLError as e:
        print(f"Database Connection Failed: {e}")
        return None