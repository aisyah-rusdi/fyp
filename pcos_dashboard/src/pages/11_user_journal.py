import streamlit as st
import pandas as pd
import mariadb
import calendar
import time
from datetime import date, timedelta, datetime
from utils.ui_helpers import load_css
from components.sidebar import render_sidebar
from components.header import render_header
from database.connection import get_connection

from database.queries import (
    GET_MONTHLY_CYCLES,
    GET_MONTHLY_JOURNALS,
    UPSERT_CYCLE,
    UPSERT_CYCLE_ACTIVE_ONLY,
    DELETE_CYCLE,
    DELETE_JOURNAL,
    EXPORT_CYCLE_DATA,
    INSERT_JOURNAL
)

# ==========================================
# 1. Page Config
# ==========================================
st.set_page_config(page_title="PCOS App - Journal", layout="wide", initial_sidebar_state="expanded")
load_css("assets/style.css")
render_sidebar(current_page="journal")
render_header(current_page="journal")

user_id = st.session_state.get('user_id', 1)
if not user_id:
    st.warning("Please log in to view your journal.")
    st.stop()

# ==========================================
# 2. Initialize Session State
# ==========================================
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()
if 'view_month' not in st.session_state:
    st.session_state.view_month = date.today().month
if 'view_year' not in st.session_state:
    st.session_state.view_year = date.today().year

def change_month(delta):
    new_month = st.session_state.view_month + delta
    new_year  = st.session_state.view_year
    if new_month > 12:
        new_month = 1
        new_year += 1
    elif new_month < 1:
        new_month = 12
        new_year -= 1
    st.session_state.view_month = new_month
    st.session_state.view_year  = new_year

# ==========================================
# DATABASE FETCHING
# ==========================================
def get_monthly_data(user_id, year, month):
    monthly_data = {}
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)

            cur.execute(GET_MONTHLY_CYCLES, (user_id, year, month))
            for row in cur.fetchall():
                log_d = row['log_date']
                if isinstance(log_d, datetime):
                    log_d = log_d.date()
                if log_d not in monthly_data:
                    monthly_data[log_d] = {}
                monthly_data[log_d]['period']         = row['period']
                monthly_data[log_d]['mood_cycle']     = row['mood']
                monthly_data[log_d]['cervical_fluid'] = row['cervical_fluid']
                monthly_data[log_d]['symptoms']       = row['symptoms']
                monthly_data[log_d]['medication']     = row['medication']
                monthly_data[log_d]['blood_pressure'] = row['blood_pressure']
                monthly_data[log_d]['sugar_level']    = row['sugar_level']
                monthly_data[log_d]['notes']          = row['notes']

            cur.execute(GET_MONTHLY_JOURNALS, (user_id, year, month))
            for row in cur.fetchall():
                log_d = row['log_date']
                if isinstance(log_d, datetime):
                    log_d = log_d.date()
                if log_d not in monthly_data:
                    monthly_data[log_d] = {}
                if 'journals' not in monthly_data[log_d]:
                    monthly_data[log_d]['journals'] = []
                    monthly_data[log_d]['journal']  = True
                monthly_data[log_d]['journals'].append({
                    'id':         row['id'],
                    'entry_text': row['entry_text'],
                    'mood':       row['mood'],
                    'created_at': row.get('created_at')
                })

        except mariadb.Error as e:
            st.error(f"Error reading DB: {e}")
        finally:
            conn.close()
    return monthly_data

db_events        = get_monthly_data(user_id, st.session_state.view_year, st.session_state.view_month)
current_day_data = db_events.get(st.session_state.selected_date, {})

# ==========================================
# CALENDAR — unchanged from original
# ==========================================
st.title("📅 My Cycle & Journal")

col_prev, col_title, col_next = st.columns([1, 4, 1])
with col_prev:
    st.button("◀ Previous", on_click=change_month, args=(-1,), use_container_width=True)
with col_title:
    month_name = calendar.month_name[st.session_state.view_month]
    st.markdown(f"<h3 style='text-align: center;'>{month_name} {st.session_state.view_year}</h3>", unsafe_allow_html=True)
with col_next:
    st.button("Next ▶", on_click=change_month, args=(1,), use_container_width=True)

days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.columns(7)
for i, day in enumerate(days_of_week):
    cols[i].markdown(f"**{day}**")

cal        = calendar.Calendar(firstweekday=0)
month_days = cal.monthdatescalendar(st.session_state.view_year, st.session_state.view_month)

for week in month_days:
    cols = st.columns(7)
    for i, day_date in enumerate(week):
        with cols[i]:
            if day_date.month != st.session_state.view_month:
                st.markdown(
                    f"<div style='color: gray; text-align: center; padding: 10px;'>{day_date.day}</div>",
                    unsafe_allow_html=True
                )
                continue

            label = str(day_date.day)
            event = db_events.get(day_date, {})
            if event.get("period") in ["Spotting", "Heavy"]:
                label += " 🩸"
            if event.get("journal"):
                label += " 📝"

            btn_type   = "primary" if day_date == st.session_state.selected_date else "secondary"
            is_future  = day_date > date.today()

            if is_future:
                st.markdown(
                    f"<div style='color: #C4B5D0; text-align: center; padding: 8px 4px; font-size: 13px;'>{label}</div>",
                    unsafe_allow_html=True
                )
            else:
                if st.button(label, key=f"btn_cal_{day_date}", type=btn_type, use_container_width=True):
                    st.session_state.selected_date = day_date
                    st.rerun()

st.write("---")

# ==========================================
# EXPORT — unchanged from original
# ==========================================
bleeding_days_raw = [
    {'log_date': d, **data}
    for d, data in db_events.items()
    if data.get('period') in ['Heavy', 'Spotting']
]

if not bleeding_days_raw:
    st.button("📥 Export CSV", disabled=True, use_container_width=True)
else:
    try:
        df = pd.DataFrame(bleeding_days_raw)
        df['log_date'] = pd.to_datetime(df['log_date'])
        df = df.sort_values('log_date')
        df['gap_days'] = df['log_date'].diff().dt.days
        df['cycle_id'] = (df['gap_days'] > 10).cumsum()
        grouped_cycles = df.groupby('cycle_id').agg(
            Cycle_Start_Date=('log_date', 'min'),
            Cycle_End_Date=('log_date', 'max')
        ).reset_index(drop=True)
        grouped_cycles['Bleeding_Days']    = (grouped_cycles['Cycle_End_Date'] - grouped_cycles['Cycle_Start_Date']).dt.days + 1
        grouped_cycles['Cycle_Start_Date'] = grouped_cycles['Cycle_Start_Date'].dt.strftime('%Y-%m-%d')
        grouped_cycles['Cycle_End_Date']   = grouped_cycles['Cycle_End_Date'].dt.strftime('%Y-%m-%d')
        csv_data = grouped_cycles.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name="My_Grouped_Cycles.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error building export: {e}")

st.write("---")

# ==========================================
# BOTTOM SECTION: TABS
# ==========================================
st.subheader(f"Data for: {st.session_state.selected_date.strftime('%B %d, %Y')}")
sel_date_str = str(st.session_state.selected_date)

tab_cycle, tab_journal = st.tabs(["🩸 Cycle Tracking", "✍️ Journal Entry"])

# ==========================================
# TAB 1: CYCLE TRACKING
# ==========================================
with tab_cycle:

    # --- DATE RANGE PICKER ---
    with st.container(border=True):
        st.markdown("**Log Period Range**")
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input(
                "Start Date",
                value=st.session_state.selected_date,
                help="First day of this log.",
                key=f"start_date_{sel_date_str}"
            )
        with col_end:
            end_date = st.date_input(
                "End Date",
                value=st.session_state.selected_date,
                help="Last day of this log.",
                key=f"end_date_{sel_date_str}"
            )

        if end_date < start_date:
            st.warning("⚠️ End Date cannot be before Start Date!")

    st.write("---")

    is_single_day = (start_date == end_date) or (end_date < start_date)

    # ==========================================
    # SINGLE DAY — original logic, untouched
    # ==========================================
    if is_single_day:
        has_cycle_data = "period" in current_day_data
        edit_key       = f"edit_mode_cycle_{sel_date_str}"

        if edit_key not in st.session_state:
            st.session_state[edit_key] = not has_cycle_data

        # VIEW MODE
        if has_cycle_data and not st.session_state[edit_key]:
            with st.container(border=True):
                st.markdown(f"#### 🩸 Cycle Details")
                st.write(f"**Period Flow:** {current_day_data.get('period')}")
                st.write(f"**Mood:** {current_day_data.get('mood_cycle')}")

                cervical = current_day_data.get('cervical_fluid')
                st.write(f"**Cervical Fluid:** {cervical if cervical else 'None'}")

                symptoms = current_day_data.get('symptoms', '')
                if symptoms:
                    tags        = [tag.strip() for tag in symptoms.split(",") if tag.strip()]
                    tag_display = " ".join([f"` {tag} `" for tag in tags])
                    st.write(f"**Symptoms & Pains:** {tag_display}")
                else:
                    st.write("**Symptoms & Pains:** None")

                st.write(f"**Medication:** {current_day_data.get('medication') or 'None'}")
                st.write(f"**Blood Pressure:** {current_day_data.get('blood_pressure') or 'None'}")
                st.write(f"**Sugar Level:** {current_day_data.get('sugar_level') or 'None'}")

                notes = current_day_data.get('notes')
                if notes:
                    st.info(f"**Notes:** {notes}")

                st.write("---")
                c1, c2 = st.columns(2)
                if c1.button("✏️ Edit Entry", key=f"edit_c_{sel_date_str}", use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
                if c2.button("🗑️ Delete Entry", key=f"del_c_{sel_date_str}", use_container_width=True):
                    conn = get_connection()
                    if conn:
                        try:
                            cur = conn.cursor()
                            cur.execute(DELETE_CYCLE, (user_id, st.session_state.selected_date))
                            conn.commit()
                            st.success("Entry deleted.")
                            time.sleep(0.5)
                            st.session_state[edit_key] = True
                            st.rerun()
                        except mariadb.Error as e:
                            st.error(f"Error: {e}")
                        finally:
                            conn.close()

        # EDIT MODE
        else:
            with st.container(border=True):
                st.markdown(f"**Log for {st.session_state.selected_date.strftime('%b %d')}**")

                saved_period   = current_day_data.get("period", "Nothing")
                saved_mood     = current_day_data.get("mood_cycle", "Neutral")
                saved_cervical = current_day_data.get("cervical_fluid", "")
                saved_symptoms = current_day_data.get("symptoms", "")
                saved_meds     = current_day_data.get("medication", "")
                saved_bp       = current_day_data.get("blood_pressure", "")
                saved_sugar    = current_day_data.get("sugar_level", "")
                saved_notes    = current_day_data.get("notes", "")

                period_options = ["Nothing", "Spotting", "Heavy"]
                period_display = {"Nothing": "⚪ Nothing", "Spotting": "💧 Spotting", "Heavy": "🩸 Heavy"}
                period_idx     = period_options.index(saved_period) if saved_period in period_options else 0
                period_val     = st.radio(
                    "🩸 Period Flow",
                    options=period_options,
                    format_func=lambda x: period_display[x],
                    index=period_idx,
                    horizontal=True,
                    key=f"period_{sel_date_str}"
                )

                st.write("")
                mood_options = ["Awful", "Bad", "Neutral", "Good", "Great"]
                mood_display = {"Awful": "😫 Awful", "Bad": "☹️ Bad", "Neutral": "😐 Neutral", "Good": "🙂 Good", "Great": "😁 Great"}
                mood_idx     = mood_options.index(saved_mood) if saved_mood in mood_options else 2
                mood_val     = st.radio(
                    "🧠 Mood",
                    options=mood_options,
                    format_func=lambda x: mood_display[x],
                    index=mood_idx,
                    horizontal=True,
                    key=f"mood_cycle_{sel_date_str}"
                )

                st.write("")
                st.markdown("🧻 **Cervical Fluid**")
                cervical_options  = ["clear and sticky", "clear and liquidy", "starchy and sticky"]
                cervical_display  = {
                    "clear and sticky":   "💧 Clear & Sticky",
                    "clear and liquidy":  "💦 Clear & Liquidy",
                    "starchy and sticky": "☁️ Starchy & Sticky"
                }
                saved_list        = [item.strip() for item in saved_cervical.split(",")] if saved_cervical else []
                cerv_cols         = st.columns(len(cervical_options))
                selected_cervical = []
                for i, option in enumerate(cervical_options):
                    with cerv_cols[i]:
                        if st.checkbox(cervical_display[option], value=option in saved_list, key=f"cerv_chk_{option}_{sel_date_str}"):
                            selected_cervical.append(option)
                cervical_val_db = ", ".join(selected_cervical)

                st.write("---")
                saved_symptoms_list = [tag.strip() for tag in saved_symptoms.split(",") if tag.strip()] if saved_symptoms else []
                master_symptoms     = [
                    'none', 'cramps', 'headache', 'backache', 'breast tenderness',
                    'joint pain', 'muscle ache', 'pain passing urine', 'pain during intercourse',
                    'mood swings', 'anxiety', 'depression', 'irritability',
                    'social withdrawal', 'brain fog', 'insomnia', 'fatigue',
                    'bloating', 'nausea', 'vomiting', 'cravings',
                    'diarrhea', 'constipation', 'acne', 'weight gain',
                    'swelling', 'hair loss', 'hirsutism', 'dizziness',
                    'fever', 'heart palpitations', 'discharge'
                ]
                for s in saved_symptoms_list:
                    if s not in master_symptoms:
                        master_symptoms.append(s)

                symptoms_list = st.multiselect(
                    "🤒 Symptoms & Pains",
                    options=master_symptoms,
                    default=saved_symptoms_list,
                    key=f"symptoms_{sel_date_str}",
                    help="Select all that apply."
                )
                symptoms_val = ", ".join(symptoms_list)

                st.write("---")
                c3, c4, c5 = st.columns(3)
                with c3:
                    meds_val  = st.text_input("💊 Medication",     value=saved_meds,  placeholder="e.g., Metformin", key=f"meds_{sel_date_str}")
                with c4:
                    bp_val    = st.text_input("❤️ Blood Pressure",  value=saved_bp,    placeholder="e.g., 120/80",    key=f"bp_{sel_date_str}")
                with c5:
                    sugar_val = st.text_input("🩸 Sugar Level",    value=saved_sugar, placeholder="e.g., 90 mg/dL",  key=f"sugar_{sel_date_str}")

                notes_val = st.text_area("📝 Notes", value=saved_notes, height=100, key=f"notes_{sel_date_str}")

            if st.button("Save Cycle Data", type="primary", use_container_width=True, key=f"save_cycle_btn_{sel_date_str}"):
                conn = get_connection()
                if conn:
                    try:
                        cur = conn.cursor()
                        insert_data = (
                            user_id, st.session_state.selected_date,
                            period_val, mood_val, symptoms_val or "",
                            cervical_val_db, meds_val or "", bp_val or "",
                            sugar_val or "", notes_val or ""
                        )
                        update_data = (
                            period_val, mood_val, symptoms_val or "",
                            cervical_val_db, meds_val or "", bp_val or "",
                            sugar_val or "", notes_val or ""
                        )
                        cur.execute(UPSERT_CYCLE, insert_data + update_data)
                        conn.commit()
                        st.success("Cycle data saved!")
                        time.sleep(0.5)
                        st.session_state[edit_key] = False
                    except mariadb.Error as e:
                        st.error(f"Error: {e}")
                    finally:
                        conn.close()
                        st.rerun()

            if has_cycle_data:
                if st.button("Cancel Edit", use_container_width=True, key=f"cancel_c_{sel_date_str}"):
                    st.session_state[edit_key] = False
                    st.rerun()

    # ==========================================
    # RANGE FORM — new logic
    # ==========================================
    else:
        delta      = (end_date - start_date).days
        date_range = [start_date + timedelta(days=i) for i in range(delta + 1)]

        st.markdown(f"**Logging {len(date_range)} days: {start_date.strftime('%b %d')} → {end_date.strftime('%b %d')}**")
        st.info("Fill in the details for each day, then click **Save All** at the bottom.")

        period_options   = ["Nothing", "Spotting", "Heavy"]
        period_display   = {"Nothing": "⚪ Nothing", "Spotting": "💧 Spotting", "Heavy": "🩸 Heavy"}
        mood_options     = ["Awful", "Bad", "Neutral", "Good", "Great"]
        mood_display     = {"Awful": "😫 Awful", "Bad": "☹️ Bad", "Neutral": "😐 Neutral", "Good": "🙂 Good", "Great": "😁 Great"}
        cervical_options = ["clear and sticky", "clear and liquidy", "starchy and sticky"]
        cervical_display = {
            "clear and sticky":   "💧 Clear & Sticky",
            "clear and liquidy":  "💦 Clear & Liquidy",
            "starchy and sticky": "☁️ Starchy & Sticky"
        }
        master_symptoms  = [
            'none', 'cramps', 'headache', 'backache', 'breast tenderness',
            'joint pain', 'muscle ache', 'pain passing urine', 'pain during intercourse',
            'mood swings', 'anxiety', 'depression', 'irritability',
            'social withdrawal', 'brain fog', 'insomnia', 'fatigue',
            'bloating', 'nausea', 'vomiting', 'cravings',
            'diarrhea', 'constipation', 'acne', 'weight gain',
            'swelling', 'hair loss', 'hirsutism', 'dizziness',
            'fever', 'heart palpitations', 'discharge'
        ]

        # One expander per day in range
        for day_date in date_range:
            day_str  = str(day_date)
            day_data = db_events.get(day_date, {})

            with st.expander(f"📅 {day_date.strftime('%A, %b %d')}", expanded=False):

                # Period Flow
                saved_period = day_data.get("period", "Nothing")
                period_idx   = period_options.index(saved_period) if saved_period in period_options else 0
                st.radio(
                    "🩸 Period Flow",
                    options=period_options,
                    format_func=lambda x: period_display[x],
                    index=period_idx,
                    horizontal=True,
                    key=f"r_period_{day_str}"
                )

                st.write("")

                # Mood
                saved_mood = day_data.get("mood_cycle", "Neutral")
                mood_idx   = mood_options.index(saved_mood) if saved_mood in mood_options else 2
                st.radio(
                    "🧠 Mood",
                    options=mood_options,
                    format_func=lambda x: mood_display[x],
                    index=mood_idx,
                    horizontal=True,
                    key=f"r_mood_{day_str}"
                )

                st.write("")

                # Cervical Fluid
                st.markdown("🧻 **Cervical Fluid**")
                saved_cervical = day_data.get("cervical_fluid", "")
                saved_list     = [item.strip() for item in saved_cervical.split(",")] if saved_cervical else []
                cerv_cols      = st.columns(len(cervical_options))
                for ci, option in enumerate(cervical_options):
                    with cerv_cols[ci]:
                        st.checkbox(
                            cervical_display[option],
                            value=option in saved_list,
                            key=f"r_cerv_{option}_{day_str}"
                        )

                st.write("---")

                # Symptoms
                saved_symptoms      = day_data.get("symptoms", "")
                saved_symptoms_list = [t.strip() for t in saved_symptoms.split(",") if t.strip()] if saved_symptoms else []
                day_symptoms        = master_symptoms.copy()
                for s in saved_symptoms_list:
                    if s not in day_symptoms:
                        day_symptoms.append(s)

                st.multiselect(
                    "🤒 Symptoms & Pains",
                    options=day_symptoms,
                    default=saved_symptoms_list,
                    key=f"r_symptoms_{day_str}",
                    help="Select all that apply."
                )

                st.write("---")

                # Medical fields
                c3, c4, c5 = st.columns(3)
                with c3:
                    st.text_input("💊 Medication",     value=day_data.get("medication", ""),     placeholder="e.g., Metformin", key=f"r_meds_{day_str}")
                with c4:
                    st.text_input("❤️ Blood Pressure",  value=day_data.get("blood_pressure", ""), placeholder="e.g., 120/80",    key=f"r_bp_{day_str}")
                with c5:
                    st.text_input("🩸 Sugar Level",    value=day_data.get("sugar_level", ""),    placeholder="e.g., 90 mg/dL",  key=f"r_sugar_{day_str}")

        # Overall notes — applies to all days
        st.write("---")
        overall_notes = st.text_area(
            "📝 Overall Notes (saved to all days in this range)",
            height=100,
            key=f"r_overall_notes_{str(start_date)}_{str(end_date)}"
        )

        # Single save button
        if st.button("💾 Save All Days", type="primary", use_container_width=True, key=f"save_range_{str(start_date)}_{str(end_date)}"):
            conn = get_connection()
            if conn:
                try:
                    cur    = conn.cursor()
                    errors = 0

                    for day_date in date_range:
                        day_str = str(day_date)

                        period_val   = st.session_state.get(f"r_period_{day_str}", "Nothing")
                        mood_val     = st.session_state.get(f"r_mood_{day_str}", "Neutral")
                        symptoms_val = ", ".join(st.session_state.get(f"r_symptoms_{day_str}", []))
                        meds_val     = st.session_state.get(f"r_meds_{day_str}", "")
                        bp_val       = st.session_state.get(f"r_bp_{day_str}", "")
                        sugar_val    = st.session_state.get(f"r_sugar_{day_str}", "")

                        selected_cervical = [
                            opt for opt in cervical_options
                            if st.session_state.get(f"r_cerv_{opt}_{day_str}", False)
                        ]
                        cervical_val = ", ".join(selected_cervical)

                        try:
                            insert_data = (
                                user_id, day_date,
                                period_val, mood_val, symptoms_val,
                                cervical_val, meds_val, bp_val,
                                sugar_val, overall_notes or ""
                            )
                            update_data = (
                                period_val, mood_val, symptoms_val,
                                cervical_val, meds_val, bp_val,
                                sugar_val, overall_notes or ""
                            )
                            cur.execute(UPSERT_CYCLE, insert_data + update_data)
                        except mariadb.Error as e:
                            st.error(f"Error saving {day_date}: {e}")
                            errors += 1

                    conn.commit()
                    if errors == 0:
                        st.success(f"✅ Saved {len(date_range)} days successfully!")
                    else:
                        st.warning(f"Saved with {errors} error(s). Check above.")
                    time.sleep(0.5)

                except mariadb.Error as e:
                    st.error(f"Database error: {e}")
                finally:
                    conn.close()
                    st.rerun()

# ==========================================
# TAB 2: JOURNAL — unchanged from original
# ==========================================
with tab_journal:
    st.markdown("### 📖 Today's Journal Entries")

    entries              = current_day_data.get("journals", [])
    mood_options_journal = {"😊 Happy": 4, "😐 Neutral": 3, "😢 Sad": 2, "😡 Angry": 1}
    reverse_mood         = {v: k for k, v in mood_options_journal.items()}

    if not entries:
        st.info("No entries for this day yet. Add one below!")
    else:
        for entry in entries:
            with st.container(border=True):
                col_text, col_btn = st.columns([5, 1])
                with col_text:
                    mood_emoji = reverse_mood.get(entry['mood'])
                    if mood_emoji is None:
                        mood_emoji = f"❓ Unknown ({entry['mood']})"
                    time_str = ""
                    if entry.get('created_at') and isinstance(entry['created_at'], datetime):
                        time_str = f" • {entry['created_at'].strftime('%I:%M %p')}"
                    st.markdown(f"**Mood:** {mood_emoji} {time_str}")
                    st.write(entry['entry_text'])
                with col_btn:
                    if st.button("🗑️ Delete", key=f"del_j_{entry['id']}", use_container_width=True):
                        conn = get_connection()
                        if conn:
                            try:
                                cur = conn.cursor()
                                cur.execute(DELETE_JOURNAL, (entry['id'], user_id))
                                conn.commit()
                                st.success("Entry deleted!")
                                time.sleep(0.5)
                            except mariadb.Error as e:
                                st.error(f"Database Error: {e}")
                            finally:
                                conn.close()
                                st.rerun()

    st.write("---")
    st.markdown("#### ✨ Add New Entry")

    new_entry_text      = st.text_area("How are you feeling right now?", height=100, key=f"new_journal_text_{sel_date_str}")
    mood_labels_journal = list(mood_options_journal.keys())
    selected_mood_label = st.radio("Journal Mood:", options=mood_labels_journal, index=1, horizontal=True, key=f"new_journal_mood_{sel_date_str}")

    if st.button("💾 Save New Entry", type="primary", use_container_width=True, key=f"save_new_journal_{sel_date_str}"):
        if not new_entry_text.strip():
            st.warning("Please write something before saving!")
        else:
            mood_val_journal = mood_options_journal[selected_mood_label]
            conn = get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(INSERT_JOURNAL, (user_id, st.session_state.selected_date, new_entry_text, mood_val_journal))
                    st.success("New journal entry added!")
                    time.sleep(0.5)
                    st.rerun()
                except mariadb.Error as e:
                    st.error(f"Database Error: {e}")
                finally:
                    conn.close()