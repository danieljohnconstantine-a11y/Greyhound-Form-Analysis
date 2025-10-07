from greyhound_analysis import load_data, analyze_box_performance, plot_box_performance

def test_pipeline():
    df = load_data('sample_data.csv')  # Replace with actual file
    box_stats = analyze_box_performance(df)
    print(box_stats)
    plot_box_performance(box_stats)

if __name__ == "__main__":
    test_pipeline()
