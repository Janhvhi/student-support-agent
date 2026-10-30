import csv, re, time
from datetime import datetime
from pathlib import Path
import streamlit as st
from auth import authenticate
from tools import check_fee_status, check_scholarship_status, get_academic_details, get_my_profile
from ai_helper import ask_local_ai
from policy_search import search_policy
from memory import load_memory, save_preference, clear_memory
from approval import create_request, list_requests, review_request
from audit import record

st.set_page_config(page_title="Student Support Agent", page_icon="🎓", layout="wide")
BASE=Path(__file__).resolve().parent
DATA=BASE/"data"; DATA.mkdir(exist_ok=True)
LOG=DATA/"evaluation_logs.csv"
for key, default in [("messages",[]),("last_evidence",""),("student",None)]:
    if key not in st.session_state: st.session_state[key]=default

st.markdown("""<style>
.stApp{background:radial-gradient(ellipse at 80% 5%,rgba(0,91,210,.18),transparent 38%),linear-gradient(135deg,#080D1D,#101027 55%,#071729);color:#E8ECFF}
.block-container{max-width:1100px;padding-top:1.5rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#15102F,#151936 55%,#102442)}
h1,h2,h3{color:#C4B5FD!important}
[data-testid="stChatMessage"]{background:rgba(20,28,57,.94);border:1px solid rgba(89,99,171,.55);border-radius:15px}
.stButton>button{background:linear-gradient(100deg,#7138F5,#394FE8);color:white;border:1px solid #7775F5;border-radius:10px}
</style>""",unsafe_allow_html=True)

def log_eval(route, elapsed, answer, evidence=""):
    exists=LOG.exists() and LOG.stat().st_size>0
    with LOG.open("a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["timestamp","route","response_time_seconds","answer_length","retrieved_evidence"])
        if not exists:w.writeheader()
        w.writerow({"timestamp":datetime.now().isoformat(timespec="seconds"),"route":route,"response_time_seconds":round(elapsed,3),"answer_length":len(answer),"retrieved_evidence":evidence[:1000]})

def private_question(q):
    """Identify questions that require the signed-in student's private record."""
    private_terms = [
        "my fee", "my fees", "fee status", "fee details", "pending amount",
        "my scholarship", "scholarship status", "my attendance", "my profile",
        "my academic", "my student details", "show my student details",
        "show my details", "student details", "my details", "my record",
        "show my record", "academic details", "student information",
    ]
    return any(term in q for term in private_terms)


def process_question(question):
    q = question.lower().strip()
    sid = st.session_state.student["student_id"] if st.session_state.student else None
    requested = re.search(r"\bSTU\d+\b", question, re.I)

    # Sensitive changes must be routed to approval before any read-only lookup.
    change_words = ["change my", "update my", "correct my", "modify my"]
    if any(word in q for word in change_words):
        if not sid:
            record("Anonymous", "Sensitive change request", "Blocked", "Login required")
            return "security", "Please log in before requesting a change to your record.", ""
        action = "Student-requested record change"
        req = create_request(sid, action, question)
        record(sid, action, "Approval required", "Pending", req["request_id"])
        return "approval", f"Your request **{req['request_id']}** has been submitted for human approval. No record has been changed yet.", ""

    # Private student questions always use the authenticated identity, never an ID supplied by the LLM.
    if private_question(q) or requested:
        if not sid:
            record("Anonymous", "Private student lookup", "Blocked", "Login required")
            return "security", "Please log in with your Student ID to access personal student information.", ""
        if requested and requested.group(0).upper() != sid:
            record(sid, "Access another student's record", "Blocked", "Denied", requested.group(0).upper())
            return "security", "🔒 **Access denied.** You can only view your own student information.", ""

        target = sid
        if any(term in q for term in ["student details", "my details", "my record", "student information", "my profile", "profile"]):
            result = get_my_profile(sid)
        elif "scholarship" in q:
            result = check_scholarship_status(target, sid)
        elif "attendance" in q or "academic" in q:
            result = get_academic_details(target, sid)
        else:
            result = check_fee_status(target, sid)

        route = "student_tool"
        if result.get("error"):
            record(sid, "Student record lookup", "Blocked", result["error"])
            return route, result["error"], ""
        record(sid, "View own student record", "Allowed", "Success", route)
        lines = [f"**{key.replace('_', ' ').title()}:** {value}" for key, value in result.items() if value]
        return route, "Here is your authorized student information:\n\n" + "\n\n".join(lines), ""

    policy_terms = [
        "policy", "what should i do", "fee payment", "pending fees",
        "payment deadline", "accounts office", "scholarship application",
        "eligibility", "missing documents", "academic support", "faculty advisor",
        "college office", "college rules", "how do i pay", "how to pay",
    ]