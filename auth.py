"""Demo student authentication using salted PBKDF2 password hashes."""
import hashlib, hmac, secrets
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent / "data" / "students.csv"

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${digest}"

def verify_password(password, stored):
    try:
        salt, expected = stored.split("$", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, AttributeError):
        return False

def authenticate(student_id, password):
    df = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    sid = student_id.strip().upper()
    rows = df[df["student_id"].str.upper() == sid]
    if rows.empty:
        return None
    row = rows.iloc[0].to_dict()
    if verify_password(password, row.get("password_hash", "")):
        return {"student_id": sid, "name": row.get("name", sid), "programme": row.get("programme", "")}
    return None
