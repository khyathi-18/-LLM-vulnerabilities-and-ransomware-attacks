# src/detect_service.py
"""
A small service that reads streaming events (or file-based events) and runs detection.
This file demonstrates the logic and prints alerts. It does not perform destructive actions.
"""

import time, json, joblib
from src.feature_extract import extract_features, load_events

MODEL_PATH = "models/rf_model.joblib"

def run_once(events_path):
    events = load_events(events_path)
    df = extract_features(events)
    X = df[["bytes_total","file_reads","net_transfers","unique_files"]]
    clf = joblib.load(MODEL_PATH)
    probs = clf.predict_proba(X)[:,1]
    alerts = []
    for i, p in enumerate(probs):
        if p > 0.6:
            alerts.append({"row": df.iloc[i].to_dict(), "score": float(p)})
    print("Alerts:", len(alerts))
    for a in alerts:
        print("ALERT: possible ransomware behavior:", a["score"], a["row"])

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv)>1 else "data/telemetry/events.json"
    run_once(path)
