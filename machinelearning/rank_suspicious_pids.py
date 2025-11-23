import pandas as pd
import joblib
from pathlib import Path

DATA_CSV = Path(__file__).parent / "miner_dataset.csv"
MODEL_PATH = Path(__file__).parent / "miner_rf_model.joblib"

def main():
    df = pd.read_csv(DATA_CSV)
    feature_cols = [c for c in df.columns if c not in ("pid", "label")]

    clf = joblib.load(MODEL_PATH)
    proba = clf.predict_proba(df[feature_cols])[:, 1]  # 预测为 miner 的概率

    df["miner_score"] = proba
    df_sorted = df.sort_values("miner_score", ascending=False)

    print(df_sorted[["pid", "label", "miner_score",
                     "total_events", "unique_files"]].head(10))

if __name__ == "__main__":
    main()
