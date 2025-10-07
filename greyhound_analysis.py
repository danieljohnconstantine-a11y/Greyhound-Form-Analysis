import pandas as pd
import matplotlib.pyplot as plt

def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

def analyze_box_performance(df):
    box_stats = df.groupby('Box')['Win'].mean()
    return box_stats

def plot_box_performance(box_stats):
    box_stats.plot(kind='bar', title='Win Rate by Box')
    plt.savefig('box_performance.png')

if __name__ == "__main__":
    df = load_data('Greyhound Form Analysis.csv')
    box_stats = analyze_box_performance(df)
    plot_box_performance(box_stats)
