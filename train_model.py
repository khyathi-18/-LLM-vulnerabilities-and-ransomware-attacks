"""
Trains supervised and unsupervised models on features.csv
Outputs saved models in models/
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, roc_auc_score
import joblib, os

def train_supervised(df, out_path="models/rf_model.joblib"):
    X = df[["bytes_total","file_reads","net_transfers","unique_files"]]
    y = df["label"]
    X_tr, X_te, y_tr, y_te = train_test_split(X,y,test_size=0.3, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_tr, y_tr)
    preds = clf.predict(X_te)
    print("Supervised classification report:\n", classification_report(y_te, preds))
    joblib.dump(clf, out_path)
    print("Saved", out_path)

def train_unsupervised(df, out_path="models/iso_model.joblib"):
    X = df[["bytes_total","file_reads","net_transfers","unique_files"]]
    iso = IsolationForest(contamination=0.05, random_state=42)
    iso.fit(X)
    joblib.dump(iso, out_path)
    print("Saved", out_path)

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    df = pd.read_csv("data/features.csv")
    train_supervised(df)
    train_unsupervised(df)
