"""Append-only style audit log for important application events."""
import csv
from pathlib import Path
from datetime import datetime
FILE=Path(__file__).resolve().parent/"data"/"audit_logs.csv"
FIELDS=["timestamp","actor","action","decision","result","details"]
def record(actor,action,decision,result,details=""):
    FILE.parent.mkdir(parents=True,exist_ok=True)
    exists=FILE.exists() and FILE.stat().st_size>0
    with FILE.open("a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if not exists: w.writeheader()
        w.writerow({"timestamp":datetime.now().isoformat(timespec="seconds"),"actor":actor or "Anonymous","action":action,"decision":decision,"result":result,"details":str(details)[:300]})
