# src/utils.py
import os, json, random, string
from pathlib import Path

def ensure_dir(p): 
    Path(p).mkdir(parents=True, exist_ok=True)

def write_json(p, o):
    ensure_dir(os.path.dirname(p))
    with open(p, "w") as f:
        json.dump(o, f, indent=2)
