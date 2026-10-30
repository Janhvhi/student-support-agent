"""Human approval queue for sensitive student-record changes."""
import csv, uuid
from pathlib import Path
from datetime import datetime

FILE = Path(__file__).resolve().parent / "data" / "approval_requests.csv"
FIELDS = ["request_id","student_id","action","new_value","status","requested_at","reviewed_at","reviewer"]

def _read():
    if not FILE.exists(): return []
    with FILE.open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f))

def _write(rows):
    FILE.parent.mkdir(parents=True,exist_ok=True)
    with FILE.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

def create_request(student_id, action, new_value):
    rows=_read()
    item={"request_id":uuid.uuid4().hex[:8].upper(),"student_id":student_id,
          "action":action,"new_value":new_value,"status":"Pending",
          "requested_at":datetime.now().isoformat(timespec="seconds"),"reviewed_at":"","reviewer":""}
    rows.append(item); _write(rows); return item

def list_requests(student_id=None):
    rows=_read()
    return rows if student_id is None else [r for r in rows if r["student_id"]==student_id]

def review_request(request_id, decision, reviewer="Demo Administrator"):
    rows=_read(); found=None
    for r in rows:
        if r["request_id"]==request_id and r["status"]=="Pending":
            r["status"]=decision; r["reviewed_at"]=datetime.now().isoformat(timespec="seconds"); r["reviewer"]=reviewer; found=r
            break
    _write(rows); return found
