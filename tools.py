
import pandas as pd
from pathlib import Path

# Locate the student data file
DATA_FILE = Path(__file__).parent / "data" / "students.csv"


def get_student(student_id):
    """Find a student by ID."""
    df = pd.read_csv(DATA_FILE)

    student_id = student_id.strip().upper()

    student = df[
        df["student_id"].str.upper() == student_id
    ]

    if student.empty:
        return {"error": "Student record not found."}

    return student.iloc[0].to_dict()


def check_fee_status(student_id):
    """Tool 1: Check fee status."""
    student = get_student(student_id)

    if "error" in student:
        return student

    return {
        "student_id": student["student_id"],
        "fee_status": student["fee_status"]
    }


def check_scholarship_status(student_id):
    """Tool 2: Check scholarship status."""
    student = get_student(student_id)

    if "error" in student:
        return student

    return {
        "student_id": student["student_id"],
        "scholarship_status": student["scholarship_status"]
    }
