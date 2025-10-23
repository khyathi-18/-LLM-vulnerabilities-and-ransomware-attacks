"""
Reads telemetry JSON and extracts features per time-window or per process-session.
Produces a CSV of feature vectors and labels (if known).
"""

import json, pandas as pd
from datetime import datetime
from collections import defaultdict
import os

def load_events(path):
    with open(path, "r") as f:
        return json.load(f)

def extract_features(events, window_seconds=60):
    # For simplicity extract per-process per-window features
    buckets = defaultdict(list)
    for e in events:
        ts = datetime.fromisoformat(e["timestamp"])
        w = int(ts.timestamp()) // window_seconds
        key = (e.get("process"), w, e.get("env"))
        buckets[key].append(e)
    rows = []
    for (proc, win, env), evs in buckets.items():
        bytes_total = sum(e.get("bytes",0) for e in evs)
        file_reads = sum(1 for e in evs if e["event_type"]=="file_read")
        net_transfers = sum(1 for e in evs if e["event_type"]=="network_transfer")
        unique_files = len(set(e.get("file_path") for e in evs if e.get("file_path")))
        suspicious_tags = sum(1 for e in evs if e.get("tag")=="seeded_exfil")
        sensitive_hits = sum(1 for e in evs if e.get("sensitive"))
        rows.append({
            "process": proc,
            "window": win,
            "env": env,
            "bytes_total": bytes_total,
            "file_reads": file_reads,
            "net_transfers": net_transfers,
            "unique_files": unique_files,
            "suspicious_tags": suspicious_tags,
            "sensitive_hits": sensitive_hits,
            "label": 1 if (suspicious_tags>0 or (net_transfers>0 and file_reads>10)) else 0
        })
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv)>1 else "data/telemetry/events.json"
    events = load_events(path)
    df = extract_features(events)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/features.csv", index=False)
    print("Wrote data/features.csv")
