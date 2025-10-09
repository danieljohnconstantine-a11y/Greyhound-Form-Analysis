import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model(ranked_path):
    df = pd.read_csv(ranked_path)

    # Simulated win labels: Score >= 6 → win (1), else (0)
    df["WinLabel"] = (df["Score"] >= 6).astype(int)

    # Features to use
    features = [
        "Box", "WinRate", "PlaceRate", "PrizeMoney", "SpeedKMH",
        "DaysSinceLastRun", "DistanceSpecialist", "TrackExperienceCount"
    ]

    # Prepare data
    X = df[features].fillna(0)
    y = df["WinLabel"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    print(f"✅ Accuracy: {accuracy_score(y_test, y_pred):.2f}")

    # Predict win probabilities
    df["WinProb"] = model.predict_proba(X)[:, 1]
    df.to_csv("outputs/ranked_with_probs.csv", index=False)
    print("✅ Win probabilities saved to: outputs/ranked_with_probs.csv")

if __name__ == "__main__":
    train_model("outputs/ranked.csv")
