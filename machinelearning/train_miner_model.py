import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import numpy as np

DATA_CSV = Path(__file__).parent / "miner_dataset.csv"
MODEL_PATH = Path.__call__(Path(__file__).parent / "miner_rf_model.joblib")
# MODEL_PATH = Path(__file__).parent / "miner_rf_model.joblib"

def main():
    df = pd.read_csv(DATA_CSV)
    print("Loaded dataset:", df.shape)
    print(df["label"].value_counts())

    feature_cols = [c for c in df.columns if c not in ("pid", "label")]
    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"  # 关键：按类别频率平衡权重
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification report:")
    print(classification_report(y_test, y_pred, digits=4))

    # 简单 5 折交叉验证看整体稳定性
    scores = cross_val_score(clf, X, y, cv=5, scoring="f1_weighted")
    print("\n5-fold CV weighted F1 scores:", scores)
    print("Mean F1:", np.mean(scores))

    # 打印特征重要性，写报告时很好用
    importances = clf.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    print("\nFeature importances:")
    for idx in sorted_idx:
        print(f"{feature_cols[idx]:20s}: {importances[idx]:.4f}")

    joblib.dump(clf, MODEL_PATH)
    print("\nSaved model to:", MODEL_PATH)

if __name__ == "__main__":
    main()

