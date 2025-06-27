import pandas as pd

df = pd.read_csv("E0.csv")
df = df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']]

df.to_csv('epl_team_summary.csv', index=False)

df.head()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("epl_team_summary.csv")
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)




home = df[['HomeTeam', 'FTHG', 'FTAG', 'FTR']].copy()
home.rename(columns={'HomeTeam': 'Team', 'FTHG': 'GoalsFor', 'FTAG': 'GoalsAgainst'}, inplace=True)
home['Win'] = (home['FTR'] == 'H').astype(int)
home['Draw'] = (home['FTR'] == 'D').astype(int)
home['Loss'] = (home['FTR'] == 'A').astype(int)

away = df[['AwayTeam', 'FTAG', 'FTHG', 'FTR']].copy()
away.rename(columns={'AwayTeam': 'Team', 'FTAG': 'GoalsFor', 'FTHG': 'GoalsAgainst'}, inplace=True)
away['Win'] = (away['FTR'] == 'A').astype(int)
away['Draw'] = (away['FTR'] == 'D').astype(int)
away['Loss'] = (away['FTR'] == 'H').astype(int)

full = pd.concat([home, away])
team_stats = full.groupby('Team').agg({
    'Win': 'sum',
    'Draw': 'sum',
    'Loss': 'sum', 
    'GoalsFor': 'sum',
    'GoalsAgainst': 'sum'}).reset_index()

team_stats['Matches'] = team_stats['Win'] + team_stats['Draw'] + team_stats['Loss']
team_stats['Points'] = team_stats['Win']*3 + team_stats['Draw']
team_stats['GD'] = team_stats['GoalsFor']-team_stats['GoalsAgainst']
team_stats['AvgPoints'] = (team_stats['Points'] / team_stats['Matches']).round(2)
team_stats['AvgGoalsFor'] = (team_stats['GoalsFor'] / team_stats['Matches']).round(2)
team_stats['AvgGoalsAgainst'] = (team_stats['GoalsAgainst']/team_stats['Matches']).round(2)

team_stats = team_stats.sort_values(by=['Points', 'GD', 'GoalsFor'], ascending=False)
team_stats['Rank'] = range(1, len(team_stats)+1)

st.title("EPL 2024/25 Dashboard")

st.subheader("Home vs Away Record")

home_stats = home.groupby('Team')[['Win', 'Draw', 'Loss']].sum().reset_index()
home_stats['Type'] = 'Home'
away_stats = away.groupby('Team')[['Win', 'Draw', 'Loss']].sum().reset_index()
away_stats['Type'] = 'Away'
homeaway = pd.concat([home_stats, away_stats])

team = st.selectbox("select a team", team_stats['Team'])
team_homeaway = homeaway[homeaway['Team']==team]

melted = team_homeaway.melt(id_vars='Type', value_vars=['Win', 'Draw', 'Loss'],
                            var_name='Result', value_name='Count')
plt.figure(figsize=(6, 4))
sns.barplot(data=melted, x='Result', y='Count', hue='Type')
plt.title(f'{team} Home vs Away Performance')
st.pyplot(plt)

st.subheader("Per-Match Averages")
st.dataframe(team_stats[['Team', 'AvgPoints', 'AvgGoalsFor', 'AvgGoalsAgainst']].set_index('Team'))

st.subheader("League Table")
st.dataframe(team_stats[['Rank', 'Team', 'Points', 'GD', 'GoalsFor', 'GoalsAgainst']].set_index('Rank'))

st.subheader("Team Summary")
row = team_stats[team_stats['Team'] == team].iloc[0]
summary = f"""
**{team}** finished the season ranked **#{row.Rank}** with **{row.Points} points**. 
They scored **{row.GoalsFor}** and conceded **{row.GoalsAgainst}** goals
(GD: {row.GD}).
Their average points per game was **{row.AvgPoints}**.
"""
st.markdown(summary)

st.markdown("---")
st.caption("Created with ❤️ using Streamlit | Data: football-data.co.uk")


