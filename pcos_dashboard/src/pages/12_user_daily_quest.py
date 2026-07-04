import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header

# Import your exact connection function
from database.connection import get_connection

# Ensure these are imported from your queries file
from database.queries import GET_USER_VITALITY_STATS, UPSERT_USER_VITALITY

# Import the new dynamic quest manager
from utils.quest import get_todays_quests

# 1. Load Components
load_css("assets/style.css")
render_sidebar(current_page="quests")
render_header(current_page="quests")

# --- DATABASE HELPER FUNCTIONS ---
def _fetch_stats(user_id):
    """Fetches user stats using your MariaDB connection."""
    conn = get_connection()
    if conn:
        try:
            # dictionary=True allows us to use stats['streak'] later
            cursor = conn.cursor(dictionary=True)
            cursor.execute(GET_USER_VITALITY_STATS, (user_id,))
            return cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching stats: {e}")
            return None
        finally:
            conn.close()
    return None

def _update_stats(user_id, streak, vitality):
    """Updates user stats using your MariaDB connection."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(UPSERT_USER_VITALITY, (user_id, streak, vitality))
            conn.commit()
        except Exception as e:
            st.error(f"Error updating stats: {e}")
        finally:
            conn.close()


def show_interactive_power_score():
    st.title("✨ Your PCOS Power Score")
    
    # We assume user_id is 1 for testing. In a real app, get this from login session.
    user_id = st.session_state.get('user_id', 1)

    # --- 1. DATABASE LOAD & AUTO-DECAY LOGIC ---
    if 'vitality_loaded' not in st.session_state:
        stats = _fetch_stats(user_id)
        
        today_date = datetime.now().date()
        
        if stats:
            db_streak = stats['streak']
            db_vitality = stats['total_vitality']
            last_login = stats['last_login']
            
            # Check days missed
            if last_login:
                days_missed = (today_date - last_login).days
            else:
                days_missed = 0
                
            # If they missed more than 1 day (e.g., yesterday)
            if days_missed > 1:
                # Calculate penalty based on their rank BEFORE decay
                if db_vitality < 500: decay_rate = 10
                elif db_vitality < 1500: decay_rate = 25
                else: decay_rate = 50
                
                penalty = decay_rate * (days_missed - 1)
                db_vitality = max(0, db_vitality - penalty)
                db_streak = 0 # Streak broken!
                
                st.warning(f"You missed {days_missed - 1} day(s). Lost {penalty} Vitality and your streak reset.", icon="⚠️")
                
                # Save the penalized stats back to the DB immediately
                _update_stats(user_id, db_streak, db_vitality)
            
            # Check if they already logged in TODAY
            if days_missed == 0 and last_login is not None:
                st.session_state.day_completed = True
            else:
                st.session_state.day_completed = False

            # Set session state to current DB values
            st.session_state.streak = db_streak
            st.session_state.total_vitality = db_vitality
            
        else:
            # First time user ever opening the app
            st.session_state.streak = 0
            st.session_state.total_vitality = 0
            st.session_state.day_completed = False
            
        st.session_state.vitality_loaded = True

    # --- 2. DYNAMIC RANK & DECAY CALCULATION (For the UI) ---
    if st.session_state.total_vitality < 500:
        rank = "Seedling 🌱"
        decay_rate = 10  
        next_rank_xp = 500
    elif st.session_state.total_vitality < 1500:
        rank = "Sprout 🌿"
        decay_rate = 25  
        next_rank_xp = 1500
    else:
        rank = "PCOS Warrior ⚔️"
        decay_rate = 50  
        next_rank_xp = 5000

    stat_col1, stat_col2, stat_col3 = st.columns([1, 1, 2])

    with stat_col1:
        st.markdown(f"""
            <div style="
                background: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E9D5FF;
                border-top: 4px solid #F97316;
                padding: 20px 16px 16px 16px;
                text-align: center;
                box-shadow: 0 4px 16px rgba(107,33,168,0.10);
            ">
                <div style="font-size: 28px; margin-bottom: 4px;">&#128293;</div>
                <div style="
                    font-size: 36px;
                    font-weight: 700;
                    color: #F97316;
                    line-height: 1;
                    margin-bottom: 8px;
                ">{st.session_state.streak}</div>
                <div style="
                    font-size: 12px;
                    font-weight: 600;
                    color: #6B7280;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">Day Streak</div>
            </div>
        """, unsafe_allow_html=True)

    with stat_col2:
        st.markdown(f"""
            <div style="
                background: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E9D5FF;
                border-top: 4px solid #0EA5E9;
                padding: 20px 16px 16px 16px;
                text-align: center;
                box-shadow: 0 4px 16px rgba(107,33,168,0.10);
            ">
                <div style="font-size: 28px; margin-bottom: 4px;">&#9889;</div>
                <div style="
                    font-size: 36px;
                    font-weight: 700;
                    color: #0EA5E9;
                    line-height: 1;
                    margin-bottom: 8px;
                ">{st.session_state.total_vitality}</div>
                <div style="
                    font-size: 12px;
                    font-weight: 600;
                    color: #6B7280;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">Total Vitality</div>
            </div>
        """, unsafe_allow_html=True)

        with stat_col3:
            st.markdown(f"### {rank}", help="Your Rank reflects your long-term dedication to hormonal balance.")
            progress_val = (st.session_state.total_vitality / next_rank_xp)
            st.progress(min(progress_val, 1.0))
            st.caption(f"Next Rank at {next_rank_xp} Vitality")

    st.divider()

    # --- 3. GET DYNAMIC QUESTS (WITH SESSION STATE PRESERVATION) ---
    today_date_str = datetime.now().strftime("%Y-%m-%d")
    today_name = datetime.now().strftime("%A")

    # Only generate new random quests if it's a new day or they haven't been loaded yet
    if 'quest_date' not in st.session_state or st.session_state.quest_date != today_date_str:
        major_tasks, minor_tasks, daily_theme = get_todays_quests(today_name, rank)
        st.session_state.major_tasks = major_tasks
        st.session_state.minor_tasks = minor_tasks
        st.session_state.daily_theme = daily_theme
        st.session_state.quest_date = today_date_str

    # Retrieve today's locked-in quests from session state
    major_tasks = st.session_state.major_tasks
    minor_tasks = st.session_state.minor_tasks
    daily_theme = st.session_state.daily_theme

    insight_container = st.empty() 
    st.markdown(f"### {today_name}'s Focus: {daily_theme}")

    # --- 4. THE UI LAYOUT ---
    col_tasks, col_gauge = st.columns([1, 1])
    total_added_points = 0
    
    with col_tasks:
        st.subheader("⭐ Major Quests")
        for task in major_tasks:
            # Checkbox key must be unique to the task name
            if st.checkbox(f"**{task['name']}** (+{task['points']})", key=task['name']):
                total_added_points += task['points']
            st.caption(f"💡 {task['desc']}")
        
        # Only render minor quests if the user's rank unlocked them
        if minor_tasks:
            st.divider()
            st.subheader("✅ Minor Quests")
            for task in minor_tasks:
                if st.checkbox(f"**{task['name']}** (+{task['points']})", key=task['name']):
                    total_added_points += task['points']
                st.caption(f"💡 {task['desc']}")

    # --- 5. CALCULATION & GAUGE ---
    final_score = min(total_added_points, 100)

    with col_gauge:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=final_score,
            number={
                'font': {'size': 48, 'color': "#6B21A8"},
                'suffix': '/100'
            },
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickfont': {'color': "#1A1A1A", 'size': 12},
                    'tickcolor': "#1A1A1A",
                },
                'bar': {'color': "#6B21A8", 'thickness': 0.3},
                'bgcolor': "#F3E8FF",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40],   'color': "#FCA5A5"},  # red-300
                    {'range': [40, 70],  'color': "#FCD34D"},  # amber-300
                    {'range': [70, 100], 'color': "#6EE7B7"},  # emerald-300
                ],
                'threshold': {
                    'line': {'color': "#6B21A8", 'width': 4},
                    'thickness': 0.75,
                    'value': final_score
                }
            }
        ))
        fig.update_layout(
            height=280,
            margin=dict(l=30, r=30, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#1A1A1A"},
            transition={                        # ← add this
                'duration': 500,
                'easing': 'cubic-in-out'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- 6. FILL AI INSIGHT (At Top) ---
    with insight_container:
        if final_score >= 80:
            st.success(f"🌟 **Powerhouse Status!** You're nailing the {daily_theme} focus today.")
        else:
            st.info(f"💡 **Pro-Tip:** Today's {daily_theme} quests are designed to balance your hormones.")

    # --- 7. FINISH DAY BUTTON (With DB Integration) ---
    st.markdown("---")
    
    if st.session_state.get('day_completed', False):
        st.success("You've already completed your quests for today! Come back tomorrow to continue your streak.")
    else:
        summary_col1, summary_col2 = st.columns([2, 1])
        
        with summary_col1:
            st.write(f"### Ready to wrap up?")
            st.write(f"You've earned **{final_score}** Vitality points today. Even small wins count toward hormonal balance!")
        
        with summary_col2:
            if st.button("Finish My Day", use_container_width=True, type="primary"):
                # 1. Update State
                new_vitality = st.session_state.total_vitality + final_score
                new_streak = st.session_state.streak + 1
                
                # 2. Save to Database
                _update_stats(user_id, new_streak, new_vitality)
                
                # 3. Update UI variables
                st.session_state.total_vitality = new_vitality
                st.session_state.streak = new_streak
                st.session_state.day_completed = True
                
                # 4. Success Feedback
                st.balloons()
                st.success(f"Great job! +{final_score} Vitality added to your journey.", icon="⚡")
                st.rerun()

show_interactive_power_score()