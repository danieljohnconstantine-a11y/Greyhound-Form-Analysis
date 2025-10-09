import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_win_probabilities(csv_path):
    # Load data
    df = pd.read_csv(csv_path)

    # Filter and sort
    df = df[df["WinProb"] >= 0]  # Ensure valid probabilities
    df = df.sort_values(by=["RaceNumber", "WinProb"], ascending=[True, False])

    # Set up plot style
    sns.set(style="whitegrid")
    plt.figure(figsize=(14, 8))

    # Create barplot
    ax = sns.barplot(
        data=df,
        x="WinProb",
        y="DogName",
        hue="RaceNumber",
        dodge=False,
        palette="viridis"
    )

    # Highlight high-confidence picks
    for i, p in enumerate(ax.patches):
        prob = p.get_width()
        if prob >= 0.5:
            p.set_color("orange")

    # Labels and layout
    plt.title("🏁 Predicted Win Probabilities per Dog")
    plt.xlabel("Win Probability")
    plt.ylabel("Dog Name")
    plt.legend(title="Race #", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_win_probabilities("outputs/ranked_with_probs.csv")
