
import csv
import re
import time
import textwrap
from datetime import datetime
from pathlib import Path
from html import escape

import streamlit as st

from tools import check_fee_status, check_scholarship_status
from ai_helper import ask_local_ai
from policy_search import search_policy
from memory import load_memory, save_preference, clear_memory


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Support Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "evaluation_logs.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_evidence" not in st.session_state:
    st.session_state.last_evidence = ""


# ============================================================
# 2. HTML RENDERING HELPER
# ============================================================

def render_html(content):
    """Render HTML instead of displaying HTML tags as text."""
    cleaned_content = textwrap.dedent(content).strip()

    if hasattr(st, "html"):
        st.html(cleaned_content)
    else:
        st.markdown(cleaned_content, unsafe_allow_html=True)


# ============================================================
# 3. DARK BLUE-PURPLE THEME
# ============================================================

render_html("""
<style>
.stApp {
    background:
        radial-gradient(
            ellipse at 80% 5%,
            rgba(0, 91, 210, 0.20),
            transparent 38%
        ),
        radial-gradient(
            ellipse at 12% 75%,
            rgba(102, 25, 255, 0.20),
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
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #15102F,
        #151936 55%,
        #102442
    );
    border-right: 1px solid rgba(126, 93, 255, 0.4);
}

h1 {
    color: #B7B4FF !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #C4B5FD !important;
}

p, label, li {
    color: #DCE4FF;
}

.brand-title {
    color: #F5F3FF;
    font-size: 1.35rem;
    font-weight: 800;
    line-height: 1.3;
}

.brand-icon {
    font-size: 2.7rem;
    filter: drop-shadow(
        0 0 12px rgba(139, 92, 246, 0.65)
    );
}

.subtitle {
    color: #B9C7F5;
    font-size: 1.12rem;
    margin-top: 8px;
}

.description {
    color: #A9B8DE;
    font-size: 0.98rem;
    line-height: 1.7;
}

.online-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 24px;
    background: rgba(17, 24, 50, 0.9);
    border: 1px solid #45418C;
    color: #E5E7FF;
    font-size: 0.85rem;
}

.online-dot {
    height: 9px;
    width: 9px;
    background: #34D399;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 10px rgba(52, 211, 153, 0.7);
}

/* Standard buttons */

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(
        100deg,
        #7138F5,
        #394FE8
    );
    color: #FFFFFF;
    border: 1px solid #7775F5;
    border-radius: 11px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border-color: #B8B6FF;
    color: #FFFFFF;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background: rgba(20, 28, 57, 0.94);
    border: 1px solid rgba(89, 99, 171, 0.55);
    border-radius: 17px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}

/* Chat input */

[data-testid="stChatInput"] {
    background: rgba(12, 19, 43, 0.98);
    border: 1px solid #7660E9;
    border-radius: 17px;
    box-shadow: 0 0 20px rgba(104, 75, 255, 0.12);
}

[data-testid="stChatInput"] textarea {
    color: #F4F5FF !important;
    caret-color: #A78BFA;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #8292C3 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(
        135deg,
        #863EFF,
        #315DF6
    );
    border-radius: 12px;
}

/* Text fields and panels */

.stTextInput input,
.stTextArea textarea {
    background: #10182E;
    color: #F1F5F9;
    border: 1px solid #454D78;
    border-radius: 10px;
}

[data-testid="stExpander"],
[data-testid="stForm"] {
    background: rgba(20, 26, 52, 0.9);
    border: 1px solid #39385F;
    border-radius: 13px;
}

[data-testid="stForm"] {
    padding: 1rem;
}

.status-panel {
    padding: 15px;
    border: 1px solid #45418C;
    border-radius: 15px;
    background: rgba(27, 30, 72, 0.72);
    margin-top: 1.2rem;
}

.status-title {
    color: #F1F5FF;
    font-weight: 650;
}

.status-subtitle {
    color: #A9B8E9;
    font-size: 0.82rem;
    margin-top: 4px;
}

.info-panel {
    background: rgba(22, 30, 59, 0.85);
    border: 1px solid #45418C;
    border-radius: 16px;
    padding: 20px;
    color: #DCE4FF;
}

hr {
    border-color: rgba(106, 112, 185, 0.38);
}

[data-testid="stCaptionContainer"] {
    color: #9DAFD7;
}

footer {
    visibility: hidden;
}
</style>
""")


# ============================================================
# 4. EVALUATION LOGGING
# ============================================================

def log_evaluation(route, elapsed_time, answer, evidence=""):
    """Save response metadata for project evaluation."""

    try:
        file_exists = (
            LOG_FILE.exists()
            and LOG_FILE.stat().st_size > 0
        )

        with open(
            LOG_FILE,
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

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                ),
                "route": route,
                "response_time_seconds": round(
                    elapsed_time, 3
                ),
                "answer_length": len(answer),
                "retrieved_evidence": evidence[:1000],
            })

    except OSError as exc:
        print(f"Evaluation logging error: {exc}")


# ============================================================
# 5. STUDENT RECORD FORMATTING
# ============================================================

def format_student_result(result, student_id, record_type):
    if not isinstance(result, dict):
        return str(result)

    if result.get("error"):
        return str(result["error"])

    if (
        record_type == "fee"
        and result.get("fee_status") is not None
    ):
        return (
            f"Your fee status for "
            f"**{result.get('student_id', student_id)}** "
            f"is **{result['fee_status']}**."
        )

    if (
        record_type == "scholarship"
        and result.get("scholarship_status") is not None
    ):
        return (
            f"Your scholarship status for "
            f"**{result.get('student_id', student_id)}** "
            f"is **{result['scholarship_status']}**."
        )

    return "\n\n".join(
        f"**{str(key).replace('_', ' ').title()}:** {value}"
        for key, value in result.items()
    )


# ============================================================
# 6. AGENT QUESTION ROUTER
# ============================================================

def process_question(question):
    q = question.lower().strip()

    # Student fee and scholarship lookup
    record_phrases = [
        "my fee status",
        "check fee status",
        "check my fees",
        "check fee",
        "my scholarship status",
        "check scholarship status",
        "check my scholarship",
        "check scholarship",
        "what is my fee",
        "what is my scholarship",
        "fee status for",
        "scholarship status for",
    ]

    if any(phrase in q for phrase in record_phrases):
        match = re.search(
            r"\bSTU\d+\b",
            question,
            re.IGNORECASE,
        )

        if not match:
            return (
                "student_tool",
                "Please provide a sample student ID, "
                "such as STU001, so I can check the "
                "corresponding record.",
                "",
            )

        student_id = match.group(0).upper()

        try:
            if "scholarship" in q:
                result = check_scholarship_status(student_id)
                answer = format_student_result(
                    result, student_id, "scholarship"
                )
            else:
                result = check_fee_status(student_id)
                answer = format_student_result(
                    result, student_id, "fee"
                )

        except Exception as exc:
            print(f"Student tool error: {exc}")
            return (
                "student_tool",
                "I couldn't retrieve that student record. "
                "Please check the student ID and try again.",
                "",
            )

        return "student_tool", answer, ""

    # College policy retrieval
    policy_keywords = [
        "policy",
        "what should i do",
        "fee payment process",
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
        "leave policy",
        "attendance policy",
        "college procedure",
        "course change",
        "college deadline",
    ]

    if any(keyword in q for keyword in policy_keywords):
        try:
            results = search_policy(question)

        except Exception as exc:
            print(f"Policy search error: {exc}")
            return (
                "policy_search",
                "I couldn't retrieve policy information. "
                "Please check that data/student_policy.txt exists.",
                "",
            )

        if isinstance(results, dict):
            if results.get("error"):
                return (
                    "policy_search",
                    "Policy retrieval encountered a problem. "
                    "Please try again.",
                    "",
                )

            results = results.get("results", [])

        if not results:
            return (
                "policy_search",
                "I couldn't find relevant information in the "
                "supplied college policy document. Please contact "
                "the appropriate college office for confirmation.",
                "",
            )

        evidence_parts = []

        for item in results:
            if isinstance(item, dict) and item.get("text"):
                evidence_parts.append(str(item["text"]))
            elif isinstance(item, str):
                evidence_parts.append(item)

        evidence = "\n\n".join(evidence_parts)

        if not evidence.strip():
            return (
                "policy_search",
                "No usable policy text was retrieved. "
                "Please contact the relevant college office.",
                "",
            )

        context = (
            "Answer the policy question using only the supplied "
            "policy evidence. Do not invent rules, deadlines, "
            "or procedures. If the evidence does not answer the "
            "question, say the document does not provide enough "
            "information.\n\n"
            f"Policy evidence:\n{evidence}"
        )

        preferences = load_memory()

        if preferences:
            context += (
                "\n\nResponse style preferences: "
                + "; ".join(map(str, preferences))
            )

        try:
            answer = ask_local_ai(question, context=context)

        except Exception as exc:
            print(f"Local AI error: {exc}")
            return (
                "policy_search",
                "I found policy information, but the AI service "
                "could not be reached. Please check that Ollama "
                "is running.",
                evidence,
            )

        return "policy_search + local_ai", str(answer), evidence

    # General questions use local AI
    preferences = load_memory()
    context = None

    if preferences:
        context = (
            "Response style preferences: "
            + "; ".join(map(str, preferences))
        )

    try:
        answer = ask_local_ai(question, context=context)
        return "local_ai", str(answer), ""

    except Exception as exc:
        print(f"Local AI error: {exc}")
        return (
            "error",
            "I couldn't connect to the local AI model. "
            "Please confirm that Ollama is running and your "
            "configured model is available.",
            "",
        )


# ============================================================
# 7. SIDEBAR
# ============================================================

with st.sidebar:

    render_html("""
        <div style="
            display:flex;
            align-items:center;
            gap:12px;
        ">
            <div class="brand-icon">🎓</div>
            <div class="brand-title">
                Student Support<br>Agent
            </div>
        </div>
    """)

    st.markdown(
        "<div style='height:24px'></div>",
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "💬 Chat",
            "⚙️ Saved Preferences",
            "ⓘ About",
        ],
        label_visibility="collapsed",
        key="navigation",
    )

    st.markdown("---")

    render_html("""
        <div class="status-panel">
            <div class="status-title">
                🟢 AI Assistant
            </div>
            <div class="status-subtitle">
                Powered by your local model
            </div>
        </div>
    """)

    st.markdown(
        "<div style='height:12px'></div>",
        unsafe_allow_html=True,
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_evidence = ""
        st.rerun()


# ============================================================
# 8. CHAT PAGE - NO SUGGESTED QUESTION CARDS
# ============================================================

if page == "💬 Chat":

    # Landing screen: title and description only.
    # All four suggested-question cards have been removed.

    if not st.session_state.messages:

        _, status_col = st.columns([5, 1])

        with status_col:
            render_html("""
                <div class="online-badge">
                    <span class="online-dot"></span>
                    Online
                </div>
            """)

        render_html("""
            <div style="
                text-align:center;
                padding-top:60px;
                padding-bottom:35px;
            ">
                <div style="
                    font-size:76px;
                    line-height:1.3;
                    filter:drop-shadow(
                        0 0 18px rgba(139,92,246,0.6)
                    );
                ">🎓</div>

                <h1 style="
                    font-size:2.8rem;
                    margin-bottom:8px;
                ">
                    Student Support Agent
                </h1>

                <div class="subtitle">
                    Your personal campus assistant ✨
                </div>

                <div class="description" style="
                    max-width:680px;
                    margin:14px auto 0 auto;
                ">
                    Ask anything about your academic journey,
                    college policies, student records, or general
                    queries.
                </div>
            </div>
        """)

    else:
        _, status_col = st.columns([5, 1])

        with status_col:
            render_html("""
                <div class="online-badge">
                    <span class="online-dot"></span>
                    Online
                </div>
            """)

    # Display conversation history
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if (
                message["role"] == "assistant"
                and message.get("latency") is not None
            ):
                st.caption(
                    f"Response time: "
                    f"{message['latency']:.2f} seconds"
                )

    # Chat input remains available
    question = st.chat_input(
        "Ask me questions...",
        key="chat_input",
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
                start_time = time.perf_counter()
                evidence = ""

                try:
                    route, answer, evidence = process_question(
                        question
                    )

                except Exception as exc:
                    print(f"Question processing error: {exc}")

                    route = "error"
                    answer = (
                        "Something went wrong while processing "
                        "your question. Please check the VS Code "
                        "terminal and confirm that Ollama and "
                        "the project files are available."
                    )

                elapsed_time = (
                    time.perf_counter() - start_time
                )

            st.markdown(answer)

            st.caption(
                f"Response time: {elapsed_time:.2f} seconds"
            )

            log_evaluation(
                route,
                elapsed_time,
                answer,
                evidence,
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "route": route,
            "latency": elapsed_time,
        })

        st.session_state.last_evidence = evidence
        st.rerun()

    # Show retrieved policy evidence when available
    if st.session_state.last_evidence:
        with st.expander("🔎 View policy evidence"):
            st.text(st.session_state.last_evidence)


# ============================================================
# 9. SAVED PREFERENCES PAGE
# ============================================================

elif page == "⚙️ Saved Preferences":

    st.title("⚙️ Saved Preferences")

    render_html("""
        <div class="description">
            Save non-sensitive preferences so the assistant can
            adapt its responses in future sessions.
        </div>
    """)

    st.markdown(
        "<div style='height:18px'></div>",
        unsafe_allow_html=True,
    )

    with st.form("preference_form", clear_on_submit=True):

        preference = st.text_input(
            "Your preference",
            placeholder="e.g. Use simple explanations",
        )

        save_clicked = st.form_submit_button(
            "✨ Save Preference",
            use_container_width=True,
        )

    if save_clicked:

        if preference.strip():

            try:
                result = save_preference(preference.strip())

                if result.startswith("Preference saved"):
                    st.success(result)
                elif "already saved" in result.lower():
                    st.info(result)
                else:
                    st.warning(result)

            except Exception as exc:
                st.error(f"Could not save preference: {exc}")

        else:
            st.warning("Please enter a preference first.")

    st.markdown("---")
    st.subheader("Your saved preferences")

    preferences = load_memory()

    if preferences:

        for item in preferences:
            safe_item = escape(str(item))

            render_html(f"""
                <div class="info-panel"
                     style="margin-bottom:10px;">
                    <span style="color:#A78BFA;">✦</span>
                    {safe_item}
                </div>
            """)

        if st.button(
            "🗑️ Clear Saved Preferences",
            use_container_width=True,
        ):

            try:
                clear_memory()
                st.success("Saved preferences cleared.")
                st.rerun()

            except Exception as exc:
                st.error(
                    f"Could not clear preferences: {exc}"
                )

    else:
        st.info("No saved preferences yet. Add one above.")


# ============================================================
# 10. ABOUT PAGE
# ============================================================

elif page == "ⓘ About":

    st.title("ⓘ About the Student Support Agent")

    render_html("""
        <div class="info-panel">
            <h3>🎓 Your campus assistant</h3>

            This project demonstrates an intelligent
            student-support agent that chooses an appropriate
            source for each question.

            <br><br>

            <b style="color:#A5B4FC;">Local AI</b><br>
            Uses your configured Ollama model to answer
            general questions.

            <br><br>

            <b style="color:#C084FC;">Student tools</b><br>
            Looks up sample fee and scholarship records
            using student IDs.

            <br><br>

            <b style="color:#67D8FF;">Policy retrieval</b><br>
            Searches the supplied college policy document
            for relevant information before generating
            policy-related answers.

            <br><br>

            <b style="color:#A5B4FC;">Persistent memory</b><br>
            Stores permitted response preferences across
            sessions.

            <br><br>

            <b style="color:#C084FC;">Evaluation logging</b><br>
            Records response times, routes, answer lengths,
            and retrieved policy evidence.
        </div>
    """)

    st.markdown(
        "<div style='height:16px'></div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "This application uses sample student records. "
        "Confirm important college information with the "
        "relevant office."
    )
