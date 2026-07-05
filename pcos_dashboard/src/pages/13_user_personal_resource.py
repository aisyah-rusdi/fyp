import streamlit as st
import pymysql
import requests
import math
from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header
from database.connection import get_connection
from database.queries import (
    GET_USER_PREDICTION_HISTORY, 
    GET_USER_SAVED_ARTICLES, 
    INSERT_SAVED_ARTICLE, 
    DELETE_SAVED_ARTICLE
)

# ==========================================
# 1. PAGE CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="PCOS App - My Resources", layout="wide", initial_sidebar_state="expanded")
load_css("assets/style.css")
render_sidebar(current_page="personal_resources")
render_header(current_page="personal_resources")

user_id = st.session_state.get('user_id')
if not user_id:
    st.warning("Please log in to see your personalized recommendations.")
    st.stop()

if 'pubmed_page' not in st.session_state:
    st.session_state.pubmed_page = 1
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def toggle_bookmark(user_id, title, url, authors, pubdate, saved_id=None, is_saved=False):
    """Adds or removes an article from the user's bookmarks."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            uid = int(user_id) # Force integer just in case session_state has it as a string
            
            if is_saved and saved_id:
                cur.execute(DELETE_SAVED_ARTICLE, (saved_id, uid))
                st.toast(f"Removed '{title}' from bookmarks.")
            else:
                cur.execute(INSERT_SAVED_ARTICLE, (uid, title, url, authors, pubdate))
                st.toast(f"Bookmarked '{title}'! ⭐")
                
            conn.commit()
        except Exception as e:
            # Catch all exceptions to see exactly what is failing
            st.error(f"Failed to save! Error: {e}") 
        finally:
            conn.close()

@st.cache_data(ttl=3600, show_spinner="Fetching latest medical literature...")
def fetch_pubmed_articles(risk_level, user_search="", page=1, per_page=9):
    """Fetches real scientific papers from PubMed tailored to the user's risk."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Base query tailored to their questionnaire results
    risk_queries = {
        "Low Risk": '("Polycystic Ovary Syndrome"[MeSH Terms] OR PCOS) AND (lifestyle OR diet OR exercise OR "mental health")',
        "Moderate Risk": '("Polycystic Ovary Syndrome"[MeSH Terms] OR PCOS) AND (symptoms OR management OR diagnosis)',
        "High Risk": '("Polycystic Ovary Syndrome"[MeSH Terms] OR PCOS) AND ("insulin resistance" OR hyperandrogenism OR treatment OR complications)'
    }
    
    query = risk_queries.get(risk_level, '"Polycystic Ovary Syndrome"[MeSH Terms]')
    
    # Enforce PCOS context even if they search something else
    if user_search:
        query = f"({query}) AND ({user_search})"
        
    retstart = (page - 1) * per_page
    
    try:
        # Step 1: Search for IDs
        search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retstart={retstart}&retmax={per_page}&retmode=json"
        res = requests.get(search_url, timeout=10).json()
        id_list = res.get('esearchresult', {}).get('idlist', [])
        total_count = int(res.get('esearchresult', {}).get('count', 0))
        
        if not id_list:
            return [], 0
            
        # Step 2: Fetch summaries for those IDs
        ids = ",".join(id_list)
        summary_url = f"{base_url}esummary.fcgi?db=pubmed&id={ids}&retmode=json"
        sum_res = requests.get(summary_url, timeout=10).json()
        
        articles = []
        for uid in id_list:
            doc = sum_res.get('result', {}).get(uid, {})
            articles.append({
                "title": doc.get('title', 'No Title'),
                "desc": f"{doc.get('source', 'Unknown Source')}. Published: {doc.get('pubdate', 'N/A')}",
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                "authors": ", ".join([a.get('name', '') for a in doc.get('authors', [])])[:80] + "...",
                "pubdate": doc.get('pubdate', 'N/A')
            })
        return articles, total_count
        
    except Exception as e:
        st.error(f"Failed to connect to PubMed API: {e}")
        return [], 0

# ==========================================
# 3. FETCH USER DATA
# ==========================================
user_risk_level = None
saved_articles_dict = {} 
saved_articles_list = [] # Keep full rows for the Bookmarked tab

conn = get_connection()
if conn:
    try:
        cur = conn.cursor()
        
        # 1. Get Risk Level
        cur.execute(GET_USER_PREDICTION_HISTORY, (user_id,))
        latest_prediction = cur.fetchone()
        if latest_prediction and latest_prediction.get('risk_level'):
            user_risk_level = latest_prediction['risk_level']
            
        # 2. Get Bookmarked Articles
        cur.execute(GET_USER_SAVED_ARTICLES, (user_id,))
        saved_articles_list = cur.fetchall()
        for row in saved_articles_list:
            saved_articles_dict[row['article_title']] = row['saved_id']
            
    except pymysql.MySQLError as e:
        st.error(f"Database error: {e}")
    finally:
        conn.close()

# ==========================================
# 4. MAIN PAGE UI
# ==========================================
st.title("🎯 My Resources")

if not user_risk_level:
    st.info("👋 Welcome! Please take the PCOS Assessment to unlock your personalized medical recommendations.")
    # CORRECT
    if st.button("Take Assessment", type="primary"):
        st.switch_page("pages/03_questionnaire.py")
    st.stop()

st.markdown(f"Based on your recent assessment, your current profile indicates a **{user_risk_level}**.")
st.write("---")

# Replace Radio with Tabs
tab_rec, tab_book = st.tabs(["📚 Recommended Papers", "⭐ Bookmarked"])

# --- TAB 1: RECOMMENDED PAPERS (API) ---
with tab_rec:
    # Search Bar (Restricts context to PCOS automatically via API logic)
    col_search, col_btn = st.columns([5, 1])
    with col_search:
        search_input = st.text_input("Search literature (e.g., 'Metformin', 'Pregnancy')", value=st.session_state.search_query)
    with col_btn:
        st.write("") # Alignment
        st.write("") 
        if st.button("Search", use_container_width=True):
            st.session_state.search_query = search_input
            st.session_state.pubmed_page = 1 # Reset to page 1 on new search
            st.rerun()

    # Fetch API Data
    articles, total_results = fetch_pubmed_articles(
        risk_level=user_risk_level, 
        user_search=st.session_state.search_query, 
        page=st.session_state.pubmed_page
    )

    if not articles:
        st.info("No articles found for this search. Try different keywords.")
    else:
        st.markdown(f"**Showing {len(articles)} of {total_results} results** from PubMed")
        
        # Display Cards in a Grid
        rows = math.ceil(len(articles) / 3)
        for row in range(rows):
            cols = st.columns(3, gap="medium")
            for i in range(3):
                idx = row * 3 + i
                if idx < len(articles):
                    res = articles[idx]
                    is_saved = res['title'] in saved_articles_dict
                    saved_id = saved_articles_dict.get(res['title'])
                    
                    with cols[i]:
                        with st.container(border=True):
                            # Tighter layout for Title & Star at the very top right
                            c_title, c_star = st.columns([6, 1], vertical_alignment="top")
                            with c_title:
                                st.markdown(f"**{res['title']}**")
                            with c_star:
                                # Clean native streamlit button, floats right
                                if st.button("⭐" if is_saved else "☆", key=f"rec_{idx}_{res['title'][:10]}", type="tertiary"):
                                    toggle_bookmark(
                                        user_id=user_id, 
                                        title=res['title'], 
                                        url=res['link'], 
                                        authors=res['authors'], 
                                        pubdate=res['pubdate'], 
                                        saved_id=saved_id, 
                                        is_saved=is_saved
                                    )
                                    st.rerun() # Keep this commented out for one more test!
                            
                            st.caption(f"✍️ {res['authors']}")
                            st.markdown(f"<small>{res['desc']}</small>", unsafe_allow_html=True)
                            st.link_button("Read Paper", res['link'], use_container_width=True)

        # Pagination Controls
        st.write("---")
        p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
        with p_col1:
            if st.session_state.pubmed_page > 1:
                if st.button("Previous Page", use_container_width=True):
                    st.session_state.pubmed_page -= 1
                    st.rerun()
        with p_col2:
            st.markdown(f"<div style='text-align: center;'>Page {st.session_state.pubmed_page}</div>", unsafe_allow_html=True)
        with p_col3:
            if (st.session_state.pubmed_page * 9) < total_results:
                if st.button("Next Page", use_container_width=True):
                    st.session_state.pubmed_page += 1
                    st.rerun()

# --- TAB 2: BOOKMARKED ARTICLES ---
with tab_book:
    if not saved_articles_list:
        st.info("You haven't bookmarked any articles yet. Head over to the 'Recommended' tab and click the star on an article to save it!")
    else:
        st.markdown(f"**You have {len(saved_articles_list)} saved articles.**")
        
        # Display Cards in a Grid
        rows = math.ceil(len(saved_articles_list) / 3)
        for row in range(rows):
            cols = st.columns(3, gap="medium")
            for i in range(3):
                idx = row * 3 + i
                if idx < len(saved_articles_list):
                    res = saved_articles_list[idx]
                    
                    with cols[i]:
                        with st.container(border=True):
                            c_title, c_star = st.columns([6, 1], vertical_alignment="top")
                            with c_title:
                                st.markdown(f"**{res['article_title']}**")
                            with c_star:
                                if st.button("⭐", key=f"book_{res['saved_id']}", type="tertiary"):
                                    toggle_bookmark(
                                        user_id=user_id, 
                                        title=res['article_title'], 
                                        url=res['article_url'], 
                                        authors=None, 
                                        pubdate=None, 
                                        saved_id=res['saved_id'], 
                                        is_saved=True
                                    )
                                    st.rerun() # Keep this commented out for one more test!
                            
                            st.caption(f"✍️ {res.get('authors', 'Authors unavailable')}")
                            st.link_button("Read Paper", res['article_url'], use_container_width=True)