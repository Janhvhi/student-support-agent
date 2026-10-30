
import csv
import re
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from auth import authenticate
from tools import (
    check_fee_status,
    check_scholarship_status,
    get_academic_details,
    get_my_profile,
)
from ai_helper import ask_local_ai
from policy_search import search_policy
from memory import load_memory, save_preference, clear_memory
from approval import create_request, list_requests, review_request
from audit import record


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Support Agent",
    page_icon="🎓",
    layout="wide",
)

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

LOG = DATA / "evaluation_logs.csv"

for key, default in [
    ("messages", []),
    ("last_evidence", ""),
    ("student", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# --------------------------------------------------
# CUSTOM UI DESIGN
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
        radial-gradient(
            ellipse at 80% 5%,
            rgba(0,91,210,.18),
            transparent 38%
        ),
        linear-gradient(
            135deg,
            #080D1D,
            #101027 55%,
            #071729
        );
        color: #E8ECFF;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #15102F,
            #151936 55%,
            #102442
        );
    }

    h1, h2, h3 {
        color: #C4B5FD !important;
    }

    [data-testid="stChatMessage"] {
        background: rgba(20,28,57,.94);
        border: 1px solid rgba(89,99,171,.55);
        border-radius: 15px;
    }

    .stButton > button {
        background: linear-gradient(
            100deg,
            #7138F5,
            #394FE8
        );
        color: white;
        border: 1px solid #7775F5;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# EVALUATION LOGGING
# --------------------------------------------------

def log_eval(route, elapsed, answer, evidence=""):

    exists = LOG.exists() and LOG.stat().st_size > 0

    with LOG.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "route",
                "response_time_seconds",
                "answer_length",
                "retrieved_evidence",
            ],
        )

        if not exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "route": route,
            "response_time_seconds": round(elapsed, 3),
            "answer_length": len(answer),
            "retrieved_evidence": evidence[:1000],
        })


# --------------------------------------------------
# IDENTIFY PRIVATE QUESTIONS
# --------------------------------------------------

def private_question(q):

    private_terms = [
        "my fee",
        "my fees",
        "fee status",
        "fee details",
        "pending amount",
        "my scholarship",
        "scholarship status",
        "my attendance",
        "my profile",
        "my academic",
        "my student details",
        "show my student details",
        "show my details",
        "student details",
        "my details",
        "my record",
        "show my record",
        "academic details",
        "student information",
    ]

    return any(term in q for term in private_terms)


# --------------------------------------------------
# MAIN QUESTION PROCESSING
# --------------------------------------------------

def process_question(question):

    q = question.lower().strip()

    sid = (
        st.session_state.student["student_id"]
        if st.session_state.student
        else None
    )

    requested = re.search(
        r"\bSTU\d+\b",
        question,
        re.I
    )

    # Sensitive changes must go through approval.

    change_words = [
        "change my",
        "update my",
        "correct my",
        "modify my",
    ]

    if any(word in q for word in change_words):

        if not sid:
            record(
                "Anonymous",
                "Sensitive change request",
                "Blocked",
                "Login required",
            )

            return (
                "security",
                "Please log in before requesting a change to your record.",
                "",
            )

        action = "Student-requested record change"

        req = create_request(
            sid,
            action,
            question,
        )

        record(
            sid,
            action,
            "Approval required",
            "Pending",
            req["request_id"],
        )

        return (
            "approval",
            f"Your request **{req['request_id']}** has been submitted for human approval. No record has been changed yet.",
            "",
        )

    # Private student information lookup.

    if private_question(q) or requested:

        if not sid:

            record(
                "Anonymous",
                "Private student lookup",
                "Blocked",
                "Login required",
            )

            return (
                "security",
                "Please log in with your Student ID to access personal student information.",
                "",
            )

        # Block access to another student's record.

        if requested and requested.group(0).upper() != sid:

            record(
                sid,
                "Access another student's record",
                "Blocked",
                "Denied",
                requested.group(0).upper(),
            )

            return (
                "security",
                "🔒 **Access denied.** You can only view your own student information.",
                "",
            )

        target = sid

        # Profile lookup.

        if any(
            term in q
            for term in [
                "student details",
                "my details",
                "my record",
                "student information",
                "my profile",
                "profile",
            ]
        ):

            result = get_my_profile(sid)

        # Scholarship lookup.

        elif "scholarship" in q:

            result = check_scholarship_status(
                target,
                sid,
            )

        # Academic lookup.

        elif "attendance" in q or "academic" in q:

            result = get_academic_details(
                target,
                sid,
            )

        # Fee lookup.

        else:

            result = check_fee_status(
                target,
                sid,
            )

        route = "student_tool"

        if result.get("error"):

            record(
                sid,
                "Student record lookup",
                "Blocked",
                result["error"],
            )

            return route, result["error"], ""

        record(
            sid,
            "View own student record",
            "Allowed",
            "Success",
            route,
        )

        lines = [
            f"**{key.replace('_', ' ').title()}:** {value}"
            for key, value in result.items()
            if value
        ]

        return (
            route,
            "Here is your authorized student information:\n\n"
            + "\n\n".join(lines),
            "",
        )

    # University policy search.

    policy_terms = [
        "policy",
        "what should i do",
        "fee payment",
        "pending fees",
        "payment deadline",
        "accounts office",
        "scholarship application",
        "eligibility",
        "missing documents",
        "academic support",
        "faculty advisor",
        "college office",
        "college rules",
        "how do i pay",
        "how to pay",
    ]

    if any(term in q for term in policy_terms):

        results = search_policy(question)

        evidence = "\n\n".join(
            item["text"]
            for item in results
            if item.get("text")
        )

        if not evidence:

            return (
                "policy_search",
                "I couldn't find relevant information in the supplied policy document. Please contact the appropriate college office.",
                "",
            )

        context = (
            "Use only this supplied policy evidence for official "
            "policy claims. Do not invent rules or deadlines.\n\n"
            + evidence
        )

        prefs = load_memory()

        if prefs:

            context += (
                "\n\nResponse preferences: "
                + "; ".join(prefs)
            )

        return (
            "policy_search + local_ai",
            str(
                ask_local_ai(
                    question,
                    context=context,
                )
            ),
            evidence,
        )

    # General university questions.

    prefs = load_memory()

    context = (
        "Response preferences: " + "; ".join(prefs)
        if prefs
        else None
    )

    return (
        "local_ai",
        str(
            ask_local_ai(
                question,
                context=context,
            )
        ),
        "",
    )


# --------------------------------------------------
# SIDEBAR AND NAVIGATION
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🎓 Student Support Agent")

    st.caption("Universal University Assistant")

    if st.session_state.student:

        student = st.session_state.student

        st.success(
            f"Signed in: {student['name']}"
        )

        st.caption(
            f"Student ID: {student['student_id']}"
        )

        if st.button(
            "Log out",
            use_container_width=True,
        ):

            record(
                student["student_id"],
                "Logout",
                "Allowed",
                "Success",
            )

            st.session_state.student = None
            st.session_state.messages = []

            st.rerun()

    else:

        st.info("Not signed in")

    page = st.radio(
        "Navigation",
        [
            "💬 Universal Search",
            "🔐 Student Login",
            "📝 Approval Requests",
            "⚙️ Preferences",
            "📊 Audit & Evaluation",
        ],
    )

    st.divider()

    st.caption("Local AI powered by Ollama")


# --------------------------------------------------
# STUDENT LOGIN
# --------------------------------------------------

if page == "🔐 Student Login":

    st.title("🔐 Student Login")

    st.write(
        "Sign in to access your own private student information."
    )

    with st.form("login_form"):

        student_id = st.text_input(
            "Student ID",
            placeholder="e.g. STU001",
        ).upper().strip()

        password = st.text_input(
            "Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Sign in",
            use_container_width=True,
        )

    if submitted:

        user = authenticate(
            student_id,
            password,
        )

        if user:

            st.session_state.student = user
            st.session_state.messages = []

            record(
                student_id,
                "Login",
                "Allowed",
                "Success",
            )

            st.success(
                f"Welcome, {user['name']}!"
            )

            st.rerun()

        else:

            record(
                student_id or "Unknown",
                "Login",
                "Denied",
                "Invalid credentials",
            )

            st.error(
                "Invalid Student ID or password."
            )

    with st.expander("Demo login credentials"):

        st.write("STU001 / student123")
        st.write("STU002 / student123")
        st.write("STU003 / student123")


# --------------------------------------------------
# UNIVERSAL SEARCH
# --------------------------------------------------

elif page == "💬 Universal Search":

    st.title("🎓 Student Support Agent")

    st.caption(
        "Ask general university questions or sign in "
        "to access your personal student information."
    )

    if st.session_state.student:

        student = st.session_state.student

        st.info(
            f"Personalized session: {student['name']} "
            f"({student['student_id']}). "
            "Private lookups are restricted to this account."
        )

    else:

        st.warning(
            "You can use universal search without signing in. "
            "Log in to access personal student records."
        )

    with st.expander("Example questions"):

        st.markdown(
            "- What should I do if my fees are pending?\n"
            "- Explain the scholarship application process.\n"
            "- What is my fee status?\n"
            "- What is my scholarship status?\n"
            "- Show my attendance.\n"
            "- Explain Python loops."
        )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    question = st.chat_input(
        "Ask anything about university support..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):

            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                start = time.perf_counter()

                try:

                    route, answer, evidence = process_question(
                        question
                    )

                except Exception as exc:

                    print("Processing error:", exc)

                    route = "error"

                    answer = (
                        "Something went wrong. "
                        "Check the terminal and try again."
                    )

                    evidence = ""

                elapsed = (
                    time.perf_counter() - start
                )

            st.markdown(answer)

            st.caption(
                f"Response time: {elapsed:.2f} seconds"
            )

            log_eval(
                route,
                elapsed,
                answer,
                evidence,
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "route": route,
            "latency": elapsed,
        })

        st.session_state.last_evidence = evidence

        st.rerun()

    if st.session_state.last_evidence:

        with st.expander("View retrieved policy evidence"):

            st.text(
                st.session_state.last_evidence
            )


# --------------------------------------------------
# APPROVAL REQUESTS
# --------------------------------------------------

elif page == "📝 Approval Requests":

    st.title("📝 Human Approval")

    st.caption(
        "Sensitive changes remain pending until a reviewer approves them."
    )

    if not st.session_state.student:

        st.warning(
            "Sign in to view your requests. "
            "A reviewer can use the demo review section below."
        )

    else:

        mine = list_requests(
            st.session_state.student["student_id"]
        )

        st.subheader("Your requests")

        if mine:

            st.dataframe(
                mine,
                use_container_width=True,
            )

        else:

            st.info("You have no approval requests.")

    with st.expander("Reviewer demonstration"):

        st.warning(
            "Demo reviewer area. In a real deployment, "
            "protect this page with a separate administrator account."
        )

        code = st.text_input(
            "Reviewer passcode",
            type="password",
        )

        if code == "ADMIN2026":

            pending = [
                request
                for request in list_requests()
                if request["status"] == "Pending"
            ]

            if not pending:

                st.info("No pending requests.")

            for request in pending:

                st.write(
                    f"{request['request_id']} · "
                    f"{request['student_id']} · "
                    f"{request['action']} · "
                    f"{request['new_value']}"
                )

                col1, col2 = st.columns(2)

                if col1.button(
                    "Approve",
                    key="a" + request["request_id"],
                ):

                    review_request(
                        request["request_id"],
                        "Approved",
                    )

                    record(
                        "Demo Administrator",
                        "Review sensitive request",
                        "Approved",
                        "Request approved",
                        request["request_id"],
                    )

                    st.rerun()

                if col2.button(
                    "Reject",
                    key="r" + request["request_id"],
                ):

                    review_request(
                        request["request_id"],
                        "Rejected",
                    )

                    record(
                        "Demo Administrator",
                        "Review sensitive request",
                        "Rejected",
                        "Request rejected",
                        request["request_id"],
                    )

                    st.rerun()

        elif code:

            st.error("Incorrect reviewer passcode.")


# --------------------------------------------------
# SAVED PREFERENCES
# --------------------------------------------------

elif page == "⚙️ Preferences":

    st.title("⚙️ Saved Preferences")

    st.caption(
        "Only non-sensitive response preferences can be stored."
    )

    with st.form(
        "pref",
        clear_on_submit=True,
    ):

        pref = st.text_input(
            "Preference",
            placeholder="e.g. Explain things in simple language",
        )

        save = st.form_submit_button(
            "Save preference"
        )

    if save:

        result = save_preference(pref)

        if result.startswith("Preference saved"):

            st.success(result)

        else:

            st.warning(result)

    for item in load_memory():

        st.write("• " + item)

    if st.button("Clear preferences"):

        st.success(clear_memory())

        st.rerun()


# --------------------------------------------------
# AUDIT AND EVALUATION
# --------------------------------------------------

elif page == "📊 Audit & Evaluation":

    st.title("📊 Audit & Evaluation")

    st.caption(
        "Demonstration logs: access decisions, approvals, "
        "and response evaluation."
    )

    if st.session_state.student:

        st.info(
            "Students should only review their own audit events "
            "in a production system. This demo page shows project evaluation records."
        )

    audit_file = DATA / "audit_logs.csv"

    eval_file = DATA / "evaluation_logs.csv"

    if audit_file.exists():

        import pandas as pd

        audit_df = pd.read_csv(audit_file)

        if st.session_state.student:

            st.subheader("Your audit records")

            own = audit_df[
                audit_df["actor"]
                == st.session_state.student["student_id"]
            ]

            st.dataframe(
                own,
                use_container_width=True,
            )

            st.caption(
                "Other students' audit records are not displayed."
            )

        else:

            st.info(
                "Sign in as a student to view your own events, "
                "or use reviewer access."
            )

        with st.expander(
            "Reviewer: view complete audit trail"
        ):

            reviewer_code = st.text_input(
                "Reviewer passcode for audit",
                type="password",
            )

            if reviewer_code == "ADMIN2026":

                st.dataframe(
                    audit_df,
                    use_container_width=True,
                )

            elif reviewer_code:

                st.error("Incorrect reviewer passcode.")

    else:

        st.info("No audit events recorded yet.")

    if eval_file.exists():

        st.subheader("Evaluation records")

        st.dataframe(
            __import__("pandas").read_csv(eval_file),
            use_container_width=True,
        )

    else:

        st.info("No evaluation records yet.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "Academic demonstration using fictional sample student data. "
    "Confirm official information with the relevant university office."
)
