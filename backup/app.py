
import csv
import re
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from tools import check_fee_status, check_scholarship_status
from ai_helper import ask_local_ai
from policy_search import search_policy
from memory import load_memory, save_preference, clear_memory


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "evaluation_logs.csv"

st.set_page_config(
    page_title="Intelligent Student Support Agent",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 Intelligent Student Support Agent")
st.write(
    "Ask questions about student records, college policies, "
    "scholarships, or general student support."
)


# ==================================================
# PERSISTENT MEMORY SIDEBAR
# ==================================================

with st.sidebar:
    st.header("🧠 Persistent Memory")
    st.caption("Save non-sensitive preferences between sessions.")

    with st.form("memory_form"):
        preference = st.text_input(
            "Preference to remember",
            placeholder="I prefer simple explanations",
        )
        save_clicked = st.form_submit_button("Save preference")

    if save_clicked:
        st.info(save_preference(preference))

    if st.button("View saved preferences"):
        preferences = load_memory()

        if preferences:
            for item in preferences:
                st.write(f"• {item}")
        else:
            st.write("No preferences saved yet.")

    if st.button("Clear all saved preferences"):
        st.info(clear_memory())


# ==================================================
# CHAT HISTORY
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# ==================================================
# EVALUATION LOGGING
# ==================================================

def log_evaluation(route, elapsed_time, answer, evidence=""):
    """Log operational metrics without storing the full question."""

    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        file_exists = LOG_FILE.exists()

        with LOG_FILE.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "timestamp",
                    "route",
                    "response_time_seconds",
                    "answer_length",
                    "retrieved_evidence",
                ],
            )

            if not file_exists or LOG_FILE.stat().st_size == 0:
                writer.writeheader()

            writer.writerow({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "route": route,
                "response_time_seconds": round(elapsed_time, 2),
                "answer_length": len(answer),
                "retrieved_evidence": evidence,
            })

    except OSError:
        pass


# ==================================================
# QUESTION ROUTING
# ==================================================

def process_question(question):
    """
    Route personal record lookups to student tools,
    policy questions to retrieval + local AI,
    and other questions to local AI.
    """

    question_lower = question.lower().strip()

    # --------------------------------------------------
    # 1. Explicit personal record requests
    # --------------------------------------------------

    record_phrases = [
        "my fee status",
        "check fee status",
        "check my fees",
        "my scholarship status",
        "check scholarship status",
        "check my scholarship",
        "what is my fee",
        "what is my scholarship",
    ]

    asks_for_record = any(
        phrase in question_lower
        for phrase in record_phrases
    )

    if asks_for_record:
        match = re.search(
            r"\bSTU\d+\b",
            question,
            re.IGNORECASE,
        )

        if not match:
            return (
                "Please include your student ID to check your personal "
                "record, for example STU001.",
                "student_tool_missing_id",
                "",
            )

        student_id = match.group().upper()

        # Scholarship record lookup
        if "scholarship" in question_lower:
            result = check_scholarship_status(student_id)

            if "error" in result:
                return result["error"], "scholarship_tool", ""

            answer = (
                f"Student ID: {result['student_id']}\n\n"
                f"Your scholarship status is: "
                f"{result['scholarship_status']}."
            )

            return answer, "scholarship_tool", ""

        # Fee record lookup
        result = check_fee_status(student_id)

        if "error" in result:
            return result["error"], "fee_tool", ""

        answer = (
            f"Student ID: {result['student_id']}\n\n"
            f"Your fee status is: {result['fee_status']}."
        )

        return answer, "fee_tool", ""

    # --------------------------------------------------
    # 2. Policy questions
    # --------------------------------------------------

    policy_keywords = [
        "policy",
        "what should i do",
        "fee payment process",
        "explain the fee payment",
        "pending fees",
        "fees are pending",
        "payment deadline",
        "accounts office",
        "scholarship application",
        "scholarship policy",
        "under review",
        "eligibility",
        "missing documents",
        "academic support",
        "faculty advisor",
        "college office",
        "college rules",
        "how do i pay",
        "how to pay",
    ]

    is_policy_question = any(
        keyword in question_lower
        for keyword in policy_keywords
    )

    if is_policy_question:
        result = search_policy(question)

        if "error" in result:
            return result["error"], "policy_search", ""

        results = result.get("results", [])

        if not results:
            return (
                "I couldn't find relevant information in the available "
                "policy document. Please contact the appropriate college "
                "office for confirmation.",
                "policy_search",
                "",
            )

        # Keep the retrieved evidence for the AI and evaluation log.
        evidence = "\n\n".join(
            item["text"] for item in results
        )

        # Include saved preferences without replacing policy evidence.
        preferences = load_memory()

        context_parts = [
            "Retrieved policy evidence:\n" + evidence
        ]

        if preferences:
            context_parts.append(
                "User's saved non-sensitive preferences:\n"
                + "\n".join(f"- {item}" for item in preferences)
            )

        context = "\n\n".join(context_parts)

        answer = ask_local_ai(question, context=context)

        answer += "\n\nSource: Sample Student Support Policy"

        return answer, "policy_search + local_ai", evidence

    # --------------------------------------------------
    # 3. General AI questions
    # --------------------------------------------------

    preferences = load_memory()

    if preferences:
        context = (
            "Follow these non-sensitive user preferences when relevant:\n"
            + "\n".join(f"- {item}" for item in preferences)
            + "\n\nAnswer the user's question normally."
        )

        answer = ask_local_ai(question, context=context)
    else:
        answer = ask_local_ai(question)

    return answer, "local_ai", ""


# ==================================================
# CHAT INPUT AND RESPONSE
# ==================================================

question = st.chat_input("Ask your question here...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start_time = time.time()

            try:
                answer, route, evidence = process_question(question)
            except Exception:
                answer = (
                    "Sorry, something went wrong while processing your "
                    "question. Please try again and check that Ollama "
                    "is running."
                )
                route = "error"
                evidence = ""

            elapsed_time = time.time() - start_time

            log_evaluation(
                route=route,
                elapsed_time=elapsed_time,
                answer=answer,
                evidence=evidence,
            )

        st.write(answer)
        st.caption(f"Response time: {elapsed_time:.2f} seconds")
        st.caption(f"Route used: {route}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })
