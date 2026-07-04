# components/charts.py
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st 
import pandas as pd     

# Chart theme constants
PRIMARY_COLOR = "#6B21A8"
SECONDARY_COLOR = "#9333EA"
ACCENT_COLOR = "#D8B4FE"
BG_COLOR = "#F3E8FF"
TEXT_COLOR = "#000000"
TEXT_MUTED = "#6B7280"
SUCCESS_COLOR = "#16A34A"
WARNING_COLOR = "#D97706"
DANGER_COLOR = "#DC2626"
CHART_COLORS = [
    "#7C3AED",  # violet purple (on-brand)
    "#0EA5E9",  # sky blue
    "#F43F5E",  # rose pink
    "#10B981",  # emerald green
    "#F59E0B",  # warm amber
]
BORDER_COLOR = "#E9D5FF"
TRANSPARENT_BG = 'rgba(0,0,0,0)'

# 02_dashboard.py

# --- 1. UPDATED RISK TREND CHART ---
def create_assessed_risk_trend(df): # <-- Notice it now accepts 'df'
    fig = go.Figure()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # If database is empty, return empty chart
    if df is None or df.empty:
        fig.update_layout(
            title="Assessed Risk Trends (No Data)", 
            plot_bgcolor=TRANSPARENT_BG, paper_bgcolor=TRANSPARENT_BG,
            font=dict(color=TEXT_COLOR), height=250
        )
        return fig

    # Pivot the data to group by month and risk level
    pivot_df = df.pivot(index='month_name', columns='risk_level', values='total_count').reindex(months).fillna(0)

    # Add lines dynamically based on what exists in the database
    if 'Low Risk' in pivot_df.columns:
        fig.add_trace(go.Scatter(x=months, y=pivot_df['Low Risk'], mode='lines', name='Low Risk', line=dict(color=SUCCESS_COLOR, width=3, shape='spline')))
    if 'Medium Risk' in pivot_df.columns:
        fig.add_trace(go.Scatter(x=months, y=pivot_df['Medium Risk'], mode='lines', name='Medium Risk', line=dict(color=WARNING_COLOR, width=3, shape='spline')))
    if 'High Risk' in pivot_df.columns:
        fig.add_trace(go.Scatter(x=months, y=pivot_df['High Risk'], mode='lines', name='High Risk', line=dict(color=DANGER_COLOR, width=3, shape='spline')))
    
    fig.update_layout(
        title="Assessed Risk Trends", 
        plot_bgcolor=TRANSPARENT_BG, 
        paper_bgcolor=TRANSPARENT_BG,
        font=dict(color=TEXT_COLOR),
        height=250, 
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", y=-0.2, font=dict(color=TEXT_COLOR)), 
        xaxis=dict(showgrid=False, color=TEXT_COLOR, tickfont=dict(color=TEXT_COLOR)), 
        yaxis=dict(showgrid=True, gridcolor=BORDER_COLOR, color=TEXT_COLOR, tickfont=dict(color=TEXT_COLOR))
    )
    return fig


def create_lifestyle_vs_cycle_chart(df):
    fig = go.Figure()
    
    if df is None or df.empty:
        fig.update_layout(title="Exercise vs Cycle Data (No Data)", plot_bgcolor=TRANSPARENT_BG, paper_bgcolor=TRANSPARENT_BG, font=dict(color=TEXT_COLOR), height=300)
        return fig

    # 1. Clean the data
    df_clean = df.dropna(subset=['exercise', 'cycle_data']).copy()

    # 2. Force mapping 
    cycle_mapping = {2: 'Regular', 4: 'Irregular', '2': 'Regular', '4': 'Irregular', '2.0': 'Regular', '4.0': 'Irregular'}
    yn_mapping = {1: 'Yes', 0: 'No', '1': 'Yes', '0': 'No', '1.0': 'Yes', '0.0': 'No'}
    
    df_clean['cycle_data'] = df_clean['cycle_data'].replace(cycle_mapping)
    df_clean['exercise'] = df_clean['exercise'].replace(yn_mapping)

    # 3. Calculate Percentages
    counts = df_clean.groupby(['exercise', 'cycle_data']).size().reset_index(name='count')
    totals = counts.groupby('exercise')['count'].sum().reset_index(name='total')
    merged = pd.merge(counts, totals, on='exercise')
    merged['percentage'] = (merged['count'] / merged['total']) * 100

    regular_data = merged[merged['cycle_data'] == 'Regular']
    irregular_data = merged[merged['cycle_data'] == 'Irregular']

    # 4. Add the "Regular Cycle" bar block (Using the brand purple)
    fig.add_trace(go.Bar(
        x=regular_data['exercise'],
        y=regular_data['percentage'],
        name='Regular Cycle',
        marker_color="#7C3AED",
        text=regular_data['percentage'].round(1).astype(str) + '%', 
        textposition='inside'
    ))

    # 5. Add the "Irregular Cycle" bar block (Use the secondary purple)
    fig.add_trace(go.Bar(
        x=irregular_data['exercise'],
        y=irregular_data['percentage'],
        name='Irregular Cycle',
        marker_color="#F59E0B",
        text=irregular_data['percentage'].round(1).astype(str) + '%',
        textposition='inside'
    ))

    # 6. Formatting to make it 100% Stacked and move the legend
    fig.update_layout(
        title="Impact of Exercise on Cycle Regularity",
        barmode='stack', 
        plot_bgcolor=TRANSPARENT_BG, paper_bgcolor=TRANSPARENT_BG,
        font=dict(color=TEXT_COLOR),
        height=380, 
        margin=dict(l=20, r=20, t=50, b=80), # Extra bottom margin for the legend
        xaxis=dict(title="Exercises Regularly?", color=TEXT_COLOR, tickfont=dict(color=TEXT_COLOR)), 
        yaxis=dict(title="Percentage (%)", range=[0, 100], showgrid=False, color=TEXT_COLOR, tickfont=dict(color=TEXT_COLOR)),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.35,         # Pushes it completely below the X-axis title
            xanchor="center", 
            x=0.5,        # Centers it
            font=dict(color=TEXT_COLOR),
        ) 
    )
    return fig


# --- SYMPTOMS CHART ---
def create_symptoms_chart(df):
    fig = go.Figure()
    
    if df is None or df.empty:
        fig.update_layout(title="Reported Symptoms (No Data)", plot_bgcolor=TRANSPARENT_BG, paper_bgcolor=TRANSPARENT_BG, font=dict(color=TEXT_COLOR), height=300)
        return fig

    # Map database feature_names to your UI initials
    symptom_map = {
        'pimples': 'P',
        'weight_gain': 'W',
        'skin_darkening': 'S',
        'hirsutism': 'H',
        'hair_loss': 'L'
    }
    
    # Apply mapping and sort
    df['ui_label'] = df['symptom'].map(symptom_map).fillna(df['symptom'])
    df = df.sort_values(by='count', ascending=True)

    fig.add_trace(go.Bar(
        x=df['count'], 
        y=df['ui_label'], 
        orientation='h', 
        marker=dict(color=CHART_COLORS[:len(df)])
    ))

    fig.update_layout(
        title="Top Reported Symptoms",
        plot_bgcolor=TRANSPARENT_BG, paper_bgcolor=TRANSPARENT_BG,
        font=dict(color=TEXT_COLOR),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor=BORDER_COLOR, color=TEXT_COLOR, tickfont=dict(color=TEXT_COLOR)), 
        yaxis=dict(showgrid=False, color=TEXT_COLOR, tickfont=dict(color=TEXT_COLOR))
    )
    return fig

# --- 2. UPDATED DEMOGRAPHICS TABLE ---
def render_demographics_table(df): # <-- Notice it now accepts 'df'
    st.markdown("### 👥 Demographics & Risk Factors")
    st.subheader("Risk Levels by Age Group")

    # If database is empty, show a message instead of crashing
    if df is None or df.empty:
        st.info("No prediction data available yet.")
        return

    # Clean up column names for the UI
    display_df = df.rename(columns={
        'age_group': 'Age Group',
        'total_respondents': 'Total Respondents',
        'high_risk_pct': 'High Risk %'
    })

    # Add the percentage sign to the UI
    display_df['High Risk %'] = display_df['High Risk %'].astype(int).astype(str) + '%'

    # Find the max respondents so the progress bar scales correctly
    max_respondents = max(display_df['Total Respondents'].max(), 100)

    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Total Respondents": st.column_config.ProgressColumn(
                "Total Respondents", format="%d", min_value=0, max_value=int(max_respondents)
            )
        }
    )

#32_admin_dashboard.py

def render_risk_distribution_chart(risk_dist_data):
    """Renders a bar chart showing the distribution of PCOS risk levels."""
    if risk_dist_data:
        df_risk = pd.DataFrame(
            list(risk_dist_data.items()), 
            columns=["Risk Level", "User Count"]
        ).set_index("Risk Level")
        
        st.bar_chart(df_risk, color=PRIMARY_COLOR, height=300)
    else:
        st.info("No assessment data available yet.")

def render_user_growth_chart(user_growth_data):
    """Renders a line chart tracking new user registrations over time."""
    if user_growth_data:
        # Convert DB rows to a DataFrame
        df_growth = pd.DataFrame(user_growth_data)
        # Format the date column nicely
        df_growth['date'] = pd.to_datetime(df_growth['date']).dt.strftime('%Y-%m-%d')
        df_growth = df_growth.set_index("date")
        
        st.line_chart(df_growth, y="new_users", color=SECONDARY_COLOR, height=300)
    else:
        st.info("No new users in the last 7 days.")