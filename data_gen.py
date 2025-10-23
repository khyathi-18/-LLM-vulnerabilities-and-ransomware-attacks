"""
Generates synthetic file corpora for three environments:
- personal
- server
- embedded

Files are text or binaries (random bytes). Seeds 'sensitive' files as labeled examples.
No real personal data is created.
"""

import os, random, string
from pathlib import Path
from datetime import datetime
from src.utils import ensure_dir

ENV_CONFIG = {
    "personal": {"count": 200, "sensitive": 10, "ext": [".txt", ".pdf", ".xlsx"]},
    "server": {"count": 300, "sensitive": 10, "ext": [".log", ".conf", ".pem"]},
    "embedded": {"count": 120, "sensitive": 10, "ext": [".bin", ".fw", ".cfg"]},
}

BASE_DIR = "data/raw"

def random_text(n=200):
    return " ".join("".join(random.choices(string.ascii_lowercase, k=random.randint(3,8))) for _ in range(n//5))

def create_file(path, is_sensitive=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.endswith((".bin", ".fw")):
        # create pseudo-binary safe content
        content = os.urandom(512 if not is_sensitive else 1024)
        with open(path, "wb") as f: f.write(content)
    else:
        text = random_text(500 if not is_sensitive else 2000)
        if is_sensitive:
            # embed labelled markers (safe) so detection can rely on content patterns
            text = ("<SENSITIVE> " + text + " </SENSITIVE>")
        with open(path, "w", encoding="utf-8") as f: f.write(text)

def gen_env(env):
    conf = ENV_CONFIG[env]
    outdir = os.path.join(BASE_DIR, env)
    ensure_dir(outdir)
    meta = []
    for i in range(conf["count"]):
        ext = random.choice(conf["ext"])
        fname = f"file_{i}{ext}"
        path = os.path.join(outdir, fname)
        is_sensitive = i < conf["sensitive"]
        create_file(path, is_sensitive=is_sensitive)
        meta.append({"path": path, "sensitive": is_sensitive})
    # shuffle so sensitive are not clustered
    random.shuffle(meta)
    return meta

def generate_all():
    ensure_dir(BASE_DIR)
    all_meta = {}
    for env in ENV_CONFIG:
        all_meta[env] = gen_env(env)
    # write simple metadata
    import json
    with open(os.path.join(BASE_DIR, "metadata.json"), "w") as f:
        json.dump(all_meta, f, indent=2)
    print("Generated corpora in", BASE_DIR)

if __name__ == "__main__":
    generate_all()
