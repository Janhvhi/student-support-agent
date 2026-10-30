"""Student record tools. Every private lookup requires the authenticated identity."""
import pandas as pd
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "students.csv"

def get_student(student_id, authenticated_id):
    if not authenticated_id:
        return {"error": "Please log in to access personal student information."}
    requested = str(student_id).strip().upper()
    owner = str(authenticated_id).strip().upper()
    if requested != owner:
        return {"error": "Access denied. You can only access your own student record."}
    df = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    row = df[df["student_id"].str.upper() == owner]
    if row.empty:
        return {"error": "Student record not found."}
    return row.iloc[0].to_dict()

def get_my_profile(authenticated_id):
    return get_student(authenticated_id, authenticated_id)

def check_fee_status(student_id, authenticated_id):
    student = get_student(student_id, authenticated_id)
    if "error" in student: return student
    return {k: student.get(k, "") for k in ["student_id","name","fee_status","total_fee","paid_amount","pending_amount","payment_deadline"]}

def check_scholarship_status(student_id, authenticated_id):
    student = get_student(student_id, authenticated_id)
    if "error" in student: return student
    return {k: student.get(k, "") for k in ["student_id","name","scholarship_status"]}

def get_academic_details(student_id, authenticated_id):
    student = get_student(student_id, authenticated_id)
    if "error" in student: return student
    return {k: student.get(k, "") for k in ["student_id","name","programme","attendance"]}
