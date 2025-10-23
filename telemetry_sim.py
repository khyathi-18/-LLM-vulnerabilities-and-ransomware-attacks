"""
Simulates system telemetry: file access events, process launches, network transfer events.
This is safe: it writes CSV/JSON event logs only.
"""

import os, random, csv, json, time
from datetime import datetime, timedelta
from pathlib import Path
from src.utils import ensure_dir

OUT_DIR = "data/telemetry"
ensure_dir(OUT_DIR)

def simulate_events(metadata_path="data/raw/metadata.json", runs=1, seed=42):
    random.seed(seed)
    with open(metadata_path, "r") as f:
        meta = json.load(f)
    events = []
    now = datetime.utcnow()
    for env, files in meta.items():
        # simulate normal access patterns
        for _ in range(500):  # number of benign events per env
            fitem = random.choice(files)
            t = now + timedelta(seconds=random.randint(0, 3600))
            evt = {
                "timestamp": t.isoformat(),
                "env": env,
                "event_type": "file_read",
                "file_path": fitem["path"],
                "process": random.choice(["explorer.exe","python.exe","chrome.exe","systemd"]),
                "bytes": random.randint(0, 20480),
                "sensitive": fitem["sensitive"]
            }
            events.append(evt)
        # inject suspicious sequences: multiple reads + small exfil network
        for s in range(30):
            # choose a sensitive file if available else pick any
            sensitive_files = [f for f in files if f["sensitive"]]
            target = random.choice(sensitive_files) if sensitive_files else random.choice(files)
            t0 = now + timedelta(seconds=random.randint(3601, 7200))
            # pattern: scan many files quickly
            for i in range(random.randint(5, 15)):
                events.append({
                    "timestamp": (t0 + timedelta(milliseconds=i*50)).isoformat(),
                    "env": env,
                    "event_type": "file_read",
                    "file_path": random.choice(files)["path"],
                    "process": "suspicious_agent",
                    "bytes": random.randint(1000, 50000),
                    "sensitive": False
                })
            # exfil event (simulated)
            events.append({
                "timestamp": (t0 + timedelta(seconds=2)).isoformat(),
                "env": env,
                "event_type": "network_transfer",
                "process": "suspicious_agent",
                "dst_ip": "203.0.113." + str(random.randint(1,254)), # TEST-NET reserved
                "bytes": random.randint(10000, 1000000),
                "file_path": target["path"],
                "tag": "seeded_exfil"
            })
    # write events
    events_file = os.path.join(OUT_DIR, f"events_{int(time.time())}.json")
    with open(events_file, "w") as f:
        json.dump(events, f, indent=2)
    print("Wrote", events_file)
    return events_file

if __name__ == "__main__":
    simulate_events()
