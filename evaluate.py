"""
Loads models and evaluates on test split. Produces metrics and basic ROC plots.
"""

import pandas as pd, joblib
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import os

def evaluate():
    df = pd.read_csv("data/features.csv")
    X = df[["bytes_total","file_reads","net_transfers","unique_files"]]
    y = df["label"]
    clf = joblib.load("models/rf_model.joblib")
    probs = clf.predict_proba(X)[:,1]
    auc = roc_auc_score(y, probs)
    print("AUC:", auc)
    # PR metrics at default threshold
    preds = (probs>0.5).astype(int)
    p,r,f,_ = precision_recall_fscore_support(y, preds, average='binary', zero_division=0)
    print("P,R,F1:", p, r, f)
    # save simple plot
    os.makedirs("experiments/results", exist_ok=True)
    plt.figure()
    plt.hist(probs[y==0], bins=50, alpha=0.6, label="benign")
    plt.hist(probs[y==1], bins=50, alpha=0.6, label="malicious")
    plt.legend()
    plt.title("Score distributions")
    plt.savefig("experiments/results/score_dist.png")
    print("Saved experiments/results/score_dist.png")

if __name__ == "__main__":
    evaluate()
