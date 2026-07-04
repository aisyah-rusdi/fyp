import streamlit as st
import requests
from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header
from components.disclaimer import show_disclaimer_banner

# 1. Page Configuration
st.set_page_config(
    page_title="PCOS App - Resources",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Load Global CSS & Components
load_css("assets/style.css")
render_sidebar(current_page="resources")
render_header(current_page="resources")

# 3. Get User Auth
user_id = st.session_state.get('user_id')

# ==========================================
# HELPER FUNCTIONS
# ==========================================

@st.cache_data(ttl=3600) 
def fetch_pubmed_articles(keyword, max_results=3): 
    """Fetches articles from PubMed API based on a keyword search."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # THE FIX: Force PubMed to ONLY return free, readable articles
    filtered_keyword = f"({keyword}) AND free full text[filter]"
    
    search_url = f"{base_url}/esearch.fcgi?db=pubmed&term={filtered_keyword}&retmode=json&retmax={max_results}"
    
    try:
        search_res = requests.get(search_url).json()
        id_list = search_res.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return []
            
        ids = ",".join(id_list)
        summary_url = f"{base_url}/esummary.fcgi?db=pubmed&id={ids}&retmode=json"
        summary_res = requests.get(summary_url).json()
        
        articles = []
        result_data = summary_res.get("result", {})
        for uid in id_list:
            if uid in result_data:
                item = result_data[uid]
                title = item.get("title", "No title available")
                authors_list = item.get("authors", [])
                authors = ", ".join([a.get("name") for a in authors_list])
                pubdate = item.get("pubdate", "Unknown Date")
                url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                
                articles.append({
                    "title": title,
                    "url": url,
                    "authors": authors,
                    "pubdate": pubdate
                })
        return articles
    except Exception as e:
        st.error(f"Failed to fetch data from PubMed: {e}")
        return []

# ==========================================
# MAIN PAGE LAYOUT
# ==========================================
st.title("📚 Resources")
st.markdown("### Latest Clinical Research & Management Guides")
st.markdown("The resources below are fetched live directly from the PubMed medical database.")

# --- CUSTOM SEARCH BOX (Now Full-Width Results!) ---
st.markdown("### Search Specific Keywords")

# 1. We put ONLY the input and button inside the half-width column
search_col, empty_col = st.columns([1, 1])
with search_col:
    custom_query = st.text_input("Enter a topic (e.g., genetics, fertility, diet):")
    search_pressed = st.button("🔍 Search PubMed", type="primary")

# 2. We move the results OUTSIDE the column so they take up the full screen!
if search_pressed:
    if custom_query:
        with st.spinner("Fetching custom results..."):
            
            # Force the query to only search within PCOS literature
            enforced_query = f"(PCOS OR Polycystic Ovary Syndrome) AND ({custom_query})"
            
            custom_articles = fetch_pubmed_articles(enforced_query, max_results=5)
            
            if custom_articles:
                st.success(f"Found {len(custom_articles)} articles for '{custom_query}'")
                
                # --- THE FULL-WIDTH LIST LAYOUT ---
                for art in custom_articles:
                    with st.container(border=True):
                        # The [4, 1] ratio now stretches across the whole monitor!
                        text_col, btn_col = st.columns([4, 1], vertical_alignment="center")
                        
                        with text_col:
                            st.markdown(f"**{art['title']}**")
                            st.caption(f"✍️ {art['authors']} | 📅 {art['pubdate']}")
                            
                        with btn_col:
                            st.link_button("READ MORE", url=art['url'], use_container_width=True)
            else:
                st.warning(f"No PCOS-related articles found for '{custom_query}'. Try a different term!")

st.divider()

# ==========================================
# DYNAMIC RISK CATEGORIES WITH PAGINATION
# ==========================================

# 1. Define the categories FIRST so Python knows what they are!

dynamic_categories = {
    "High Risk (Complications & Management)": "(PCOS OR Polycystic Ovary Syndrome) AND (cardiovascular OR diabetes OR endometrial cancer OR severe complications)",
    "Medium Risk (Symptoms & Fertility)": "(PCOS OR Polycystic Ovary Syndrome) AND (infertility OR hyperandrogenism OR metabolic syndrome OR moderate)",
    "Low Risk (Lifestyle & Prevention)": "(PCOS OR Polycystic Ovary Syndrome) AND (lifestyle OR diet OR exercise OR mild management)"
}

# 2. Create our 3 columns
col1, col2, col3 = st.columns(3)
columns_list = [col1, col2, col3]

# --- DYNAMIC RISK CATEGORIES WITH PAGINATION ---
ITEMS_PER_PAGE = 3

# Loop through our categories and automatically fetch data for each column
for idx, (category_name, search_query) in enumerate(dynamic_categories.items()):
    with columns_list[idx]:
        st.markdown(f"#### {category_name}")
        
        # 1. Initialize session state to remember which page this column is on
        page_key = f"page_category_{idx}"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0
            
        # 2. Fetch a large batch of articles (50 instead of 3 or 5)
        with st.spinner(f"Loading {category_name}..."):
            all_articles = fetch_pubmed_articles(search_query, max_results=50)
            
        if not all_articles:
            st.info("No recent articles found.")
        else:
            # 3. Calculate exactly which articles to show on the current page
            total_articles = len(all_articles)
            total_pages = (total_articles - 1) // ITEMS_PER_PAGE + 1
            current_page = st.session_state[page_key]
            
            start_idx = current_page * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE
            
            # 4. Loop only through the slice of articles for this page
            for art in all_articles[start_idx:end_idx]:
                with st.container(border=True):
                    st.markdown(f"**{art['title']}**")
                    
                    authors_display = art['authors'] if len(art['authors']) < 50 else art['authors'][:47] + "..."
                    
                    st.markdown(f"""
                    <div style='font-size: 14px; color: #1A1A1A; margin-bottom: 15px;'>
                        ✍️ {authors_display}<br>
                        📅 {art['pubdate']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.link_button("READ ON PUBMED", url=art['url'], use_container_width=True)
            
            # 5. Render Pagination Controls at the bottom of the column
            st.write("") # Adds a tiny bit of space
            btn_col1, text_col, btn_col2 = st.columns([1, 1.2, 1], vertical_alignment="center")
            
            with btn_col1:
                if current_page > 0:
                    if st.button("Prev", key=f"prev_{idx}", use_container_width=True):
                        st.session_state[page_key] -= 1
                        st.rerun() # Refresh the page to show the new slice
            
            with text_col:
                # Show the user where they are (e.g., "Page 1 / 10")
                st.markdown(f"<div style='text-align: center; font-size: 14px;'>Page {current_page + 1} / {total_pages}</div>", unsafe_allow_html=True)
                
            with btn_col2:
                if current_page < total_pages - 1:
                    if st.button("Next", key=f"next_{idx}", use_container_width=True):
                        st.session_state[page_key] += 1
                        st.rerun() # Refresh the page to show the new slice

show_disclaimer_banner("The resources provided are for informational purposes and do not constitute medical advice.")