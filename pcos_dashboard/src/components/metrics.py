import streamlit as st

def render_traffic_metrics(df):
    st.subheader("Today's Activity")

    total_users = 0
    daily_checkins = 0
    total_assessments = 0

    if df is not None and not df.empty:
        total_users = df['total_users'].iloc[0]
        daily_checkins = df['daily_checkins'].iloc[0]
        total_assessments = df['total_assessments'].iloc[0]

    metrics = [
        {"value": f"{total_users:,}",        "label": "Total Users",             "color": "#2563EB"},
        {"value": f"{total_assessments:,}",  "label": "Assessments Completed",   "color": "#F43F5E"},
        {"value": f"{daily_checkins:,}",     "label": "Daily Check-ins",         "color": "#0D9488"},        
    ]

    cols = st.columns(3)
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(f"""
                <div style="
                    background: #FFFFFF;
                    border-radius: 16px;
                    border: 1px solid #E9D5FF;
                    border-top: 4px solid {m['color']};
                    padding: 20px 16px 16px 16px;
                    text-align: center;
                    box-shadow: 0 4px 16px rgba(107,33,168,0.10);
                    height: 110px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                ">
                    <div style="
                        font-size: 36px;
                        font-weight: 700;
                        color: {m['color']};
                        line-height: 1;
                        margin-bottom: 8px;
                    ">{m['value']}</div>
                    <div style="
                        font-size: 13px;
                        font-weight: 500;
                        color: #6B7280;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">{m['label']}</div>
                </div>
            """, unsafe_allow_html=True)