import pandas as pd
import matplotlib.pyplot as plt

def load_data(filepath):
    df = pd.read_csv(filepath, parse_dates=['RaceDate'])
    df.sort_values(['DogName', 'RaceDate'], inplace=True)
    df['Win'] = df['Finish'].apply(lambda x: 1 if x == 1 else 0)
    return df

def calculate_recent_form(df, window=3):
    df['RecentWins'] = df.groupby('DogName')['Win'].rolling(window).sum().reset_index(level=0, drop=True)
    return df

def calculate_speed(df):
    df['Distance_m'] = df['Distance'].str.replace('m', '').astype(float)
    df['Speed_kmh'] = (df['Distance_m'] / df['RaceTime']) * 3.6
    return df

def box_win_rate(df):
    return (df[df['Win'] == 1].groupby('Box').size() / df.groupby('Box').size()).fillna(0)

def trainer_success(df):
    return (df[df['Win'] == 1].groupby('Trainer').size() / df.groupby('Trainer').size()).fillna(0)

def track_bias(df):
    return (df[df['Win'] == 1].groupby('Track').size() / df.groupby('Track').size()).fillna(0)

def grade_performance(df):
    return (df[df['Win'] == 1].groupby('Grade').size() / df.groupby('Grade').size()).fillna(0)

def distance_trends(df):
    return (df[df['Win'] == 1].groupby('Distance').size() / df.groupby('Distance').size()).fillna(0)

def speed_by_distance(df):
    return df.groupby('Distance')['Speed_kmh'].mean().sort_values(ascending=False)

def weather_performance(df):
    return (df[df['Win'] == 1].groupby('Weather').size() / df.groupby('Weather').size()).fillna(0)

def surface_performance(df):
    return (df[df['Win'] == 1].groupby('Surface').size() / df.groupby('Surface').size()).fillna(0)

def betting_roi(df):
    roi = df.groupby('DogName').agg({
        'Odds': 'count',
        'Payout': 'sum'
    })
    roi['ROI'] = roi['Payout'] / roi['Odds']
    return roi.sort_values('ROI', ascending=False)

def recommend_bets(df, min_recent_wins=2, max_odds=10.0, min_speed=30.0):
    df_filtered = df[
        (df['RecentWins'] >= min_recent_wins) &
        (df['Odds'] <= max_odds) &
        (df['Speed_kmh'] >= min_speed)
    ]
    return df_filtered[['RaceDate', 'Track', 'DogName', 'Box', 'Odds', 'Trainer', 'Distance', 'Grade', 'RaceTime', 'Speed_kmh', 'Weather', 'Surface', 'RecentWins']]

def plot_box_performance(box_stats):
    box_stats.plot(kind='bar', title='Win Rate by Box', color='skyblue')
    plt.xlabel('Box Number')
    plt.ylabel('Win Rate')
    plt.tight_layout()
    plt.savefig('box_performance.png')

def save_dataframe(df, filename):
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    df = load_data('greyhound_form_analysis.csv')
    df = calculate_recent_form(df)
    df = calculate_speed(df)

    box_stats = box_win_rate(df)
    trainer_stats = trainer_success(df)
    track_stats = track_bias(df)
    grade_stats = grade_performance(df)
    distance_stats = distance_trends(df)
    speed_stats = speed_by_distance(df)
    weather_stats = weather_performance(df)
    surface_stats = surface_performance(df)
    roi_stats = betting_roi(df)
    recommended = recommend_bets(df)

    print("📊 Box Win Rates:\n", box_stats)
    print("\n👨‍🏫 Trainer Success Rates:\n", trainer_stats)
    print("\n🏟️ Track Bias:\n", track_stats)
    print("\n🎓 Grade Performance:\n", grade_stats)
    print("\n📏 Distance Trends:\n", distance_stats)
    print("\n🚀 Average Speed by Distance:\n", speed_stats)
    print("\n🌦️ Weather Performance:\n", weather_stats)
    print("\n🏁 Surface Performance:\n", surface_stats)
    print("\n💰 Betting ROI:\n", roi_stats)
    print("\n🎯 Recommended Bets:\n", recommended)

    plot_box_performance(box_stats)
    save_dataframe(recommended, 'recommended_bets.csv')
    save_dataframe(roi_stats.reset_index(), 'roi_table.csv')
    save_dataframe(speed_stats.reset_index(name='AverageSpeed_kmh'), 'speed_by_distance.csv')
    save_dataframe(weather_stats.reset_index(name='WinRate'), 'weather_performance.csv')
    save_dataframe(surface_stats.reset_index(name='WinRate'), 'surface_performance.csv')
