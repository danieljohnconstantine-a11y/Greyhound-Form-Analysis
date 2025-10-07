import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load and prepare data
df = pd.read_csv('greyhound_form_analysis.csv', parse_dates=['RaceDate'])
df['Win'] = df['Finish'].apply(lambda x: 1 if x == 1 else 0)
df['Distance_m'] = df['Distance'].str.replace('m', '').astype(float)
df['Speed_kmh'] = (df['Distance_m'] / df['RaceTime']) * 3.6
df.sort_values(['DogName', 'RaceDate'], inplace=True)
df['RecentWins'] = df.groupby('DogName')['Win'].rolling(3).sum().reset_index(level=0, drop=True)

# Sidebar filters
st.sidebar.title("🎛️ Filter Races")
track = st.sidebar.selectbox("Track", ["All"] + sorted(df['Track'].unique()))
weather = st.sidebar.selectbox("Weather", ["All"] + sorted(df['Weather'].unique()))
surface = st.sidebar.selectbox("Surface", ["All"] + sorted(df['Surface'].unique()))
grade = st.sidebar.selectbox("Grade", ["All"] + sorted(df['Grade'].unique()))
trainer = st.sidebar.selectbox("Trainer", ["All"] + sorted(df['Trainer'].unique()))

# Apply filters
filtered_df = df.copy()
if track != "All":
    filtered_df = filtered_df[filtered_df['Track'] == track]
if weather != "All":
    filtered_df = filtered_df[filtered_df['Weather'] == weather]
if surface != "All":
    filtered_df = filtered_df[filtered_df['Surface'] == surface]
if grade != "All":
    filtered_df = filtered_df[filtered_df['Grade'] == grade]
if trainer != "All":
    filtered_df = filtered_df[filtered_df['Trainer'] == trainer]

# Dashboard layout
st.title("🐾 Greyhound Racing Intelligence Dashboard")

st.subheader("🎯 Recommended Bets")
recommended = filtered_df[
    (filtered_df['RecentWins'] >= 2) &
    (filtered_df['Odds'] <= 10.0) &
    (filtered_df['Speed_kmh'] >= 30.0)
]
st.dataframe(recommended[['RaceDate', 'Track', 'DogName', 'Box', 'Odds', 'Trainer', 'Distance', 'Grade', 'RaceTime', 'Speed_kmh', 'Weather', 'Surface', 'RecentWins']])

st.subheader("📊 Win Rate by Box")
box_stats = (filtered_df[filtered_df['Win'] == 1].groupby('Box').size() / filtered_df.groupby('Box').size()).fillna(0)
fig_box, ax_box = plt.subplots()
box_stats.plot(kind='bar', color='skyblue', ax=ax_box)
ax_box.set_xlabel("Box")
ax_box.set_ylabel("Win Rate")
st.pyplot(fig_box)

st.subheader("🚀 Speed by Distance")
speed_stats = filtered_df.groupby('Distance')['Speed_kmh'].mean().sort_values(ascending=False)
st.dataframe(speed_stats.reset_index(name='AverageSpeed_kmh'))

st.subheader("💰 Betting ROI")
roi = filtered_df.groupby('DogName').agg({'Odds': 'count', 'Payout': 'sum'})
roi['ROI'] = roi['Payout'] / roi['Odds']
st.dataframe(roi.sort_values('ROI', ascending=False).reset_index())

st.subheader("🌦️ Weather Performance")
weather_stats = (filtered_df[filtered_df['Win'] == 1].groupby('Weather').size() / filtered_df.groupby('Weather').size()).fillna(0)
st.dataframe(weather_stats.reset_index(name='WinRate'))

st.subheader("🏁 Surface Performance")
surface_stats = (filtered_df[filtered_df['Win'] == 1].groupby('Surface').size() / filtered_df.groupby('Surface').size()).fillna(0)
st.dataframe(surface_stats.reset_index(name='WinRate'))

st.subheader("🎓 Grade Performance")
grade_stats = (filtered_df[filtered_df['Win'] == 1].groupby('Grade').size() / filtered_df.groupby('Grade').size()).fillna(0)
st.dataframe(grade_stats.reset_index(name='WinRate'))

st.subheader("👨‍🏫 Trainer Success")
trainer_stats = (filtered_df[filtered_df['Win'] == 1].groupby('Trainer').size() / filtered_df.groupby('Trainer').size()).fillna(0)
st.dataframe(trainer_stats.reset_index(name='WinRate'))
