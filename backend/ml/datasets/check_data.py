import sys
sys.path.insert(0, '../../..')
import os
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent

def load(fname):
    p = BASE / fname
    if not p.exists():
        print(f"MISSING: {fname}")
        return pd.DataFrame()
    return pd.read_csv(p)

p = load("tourist_places.csv")
h = load("hotels.csv")
r = load("restaurants.csv")

print(f"tourist_places.csv : {len(p)} rows")
if not p.empty:
    print(f"  Cities: {sorted(p['city'].dropna().unique().tolist())}")

print(f"hotels.csv         : {len(h)} rows")
if not h.empty:
    print(f"  Cities: {sorted(h['city'].dropna().unique().tolist())}")

print(f"restaurants.csv    : {len(r)} rows")
if not r.empty:
    print(f"  Cities: {sorted(r['city'].dropna().unique().tolist())}")
