
# 🎓 Intelligent Student Support Agent

An AI-powered student support chatbot built with Python, Streamlit, and Ollama. It helps students check sample fee and scholarship records, retrieve relevant college policy information, and ask general questions using a locally running language model.

## 📌 Project Overview

The Intelligent Student Support Agent demonstrates how an AI agent can route student questions to appropriate tools, retrieve relevant policy information, and generate responses using a local language model.

## ✨ Features

- 💬 **Interactive Chat Interface:** Ask questions through a Streamlit chat interface.
- 💰 **Fee Status Lookup:** Check sample student fee records using a student ID.
- 🎓 **Scholarship Status Lookup:** Retrieve scholarship application status.
- 📚 **Policy Retrieval:** Search relevant sections of a sample policy document.
- 🤖 **Local AI Responses:** Generate general answers using Ollama and Llama 3.2 1B.
- 🧠 **Persistent Preferences:** Save non-sensitive response preferences locally.
- 📊 **Evaluation Logging:** Record response time, routing information, answer length, and retrieved policy evidence.
- 🛡️ **Error Handling:** Handle missing student records and AI connection failures.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Chat interface |
| Ollama | Local language model execution |
| Llama 3.2 1B | Language model |
| CSV | Sample student records and evaluation logs |
| JSON | Local preference storage |
| Keyword-based retrieval | Policy document search |

## 📁 Project Structure

```text
student-support-agent/
├── app.py
├── ai_helper.py
├── memory.py
├── policy_search.py
├── tools.py
├── test_ai.py
├── test_memory.py
├── test_policy.py
├── test_tools.py
├── requirements.txt
├── README.md
├── .gitignore
├── backup/
│   └── app.py
└── data/
    ├── students.csv
    └── student_policy.txt
```

Local files such as `data/memory.json` and
`data/evaluation_logs.csv` may be generated when the
application runs and are intentionally excluded from Git.

## ⚙️ Setup and Installation

### 1. Prerequisites

Install:

- Python 3.10 or a compatible version for your dependencies
- [Ollama](https://ollama.com/)
- Git (optional, for cloning and version control)

### 2. Clone the Repository

```bash
git clone https://github.com/Janhvhi/student-support-agent.git
cd student-support-agent
```

Alternatively, download the repository ZIP from GitHub and extract it.

### 3. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's Python executable directly.

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Download and Start the Local Model

Run:

```bash
ollama run llama3.2:1b
```

Wait for the model to download and start. Keep Ollama available while using the application.

### 6. Start the Application

Open a terminal in the project directory and run:

```bash
python -m streamlit run app.py
```

If you want to use port `8506`, run:

```bash
python -m streamlit run app.py --server.port 8506
```

Open the local URL printed in the terminal. The default Streamlit address is usually:

`http://localhost:8501`

When using port `8506`, open:

`http://localhost:8506`

## 🧪 Sample Test Cases

| Test | Example Input | Expected Result |
|---|---|---|
| Fee status | Check my fee status for STU001 | Paid |
| Scholarship status | Check scholarship status for STU002 | Under Review |
| Policy retrieval | What should I do if my fees are pending? | Relevant fee policy information |
| General AI | Explain student support | Response from the local AI model |
| Persistent memory | Save a non-sensitive preference | Preference stored locally |

These are expected outcomes based on the sample project data; actual test results should be recorded after running the tests.

## ▶️ Running Tests

Run the tool, memory, and policy tests from the project directory:

```bash
python -m unittest test_tools.py test_memory.py
python test_policy.py
```

The AI test may be an integration script rather than a formal unit test. Run it separately if needed:

```bash
python test_ai.py
```

AI integration tests require Ollama and the configured model to be available.

## ⚠️ Limitations

- Policy retrieval uses keyword matching rather than semantic search.
- Student records are sample CSV data.
- The policy document contains demonstration content, not verified official college policy.
- Response quality and speed depend on the local model and computer resources.
- Preference safeguards are basic and do not guarantee detection of all sensitive information.
- Evaluation logs provide basic operational metrics, not a complete accuracy benchmark.
- Model-reported token usage is not currently guaranteed to be available.

## 🔐 Privacy and Security

- Ollama runs the language model locally.
- Student records and saved preferences are stored in local files.
- Use fictional student records for demonstrations.
- Do not commit real student information, credentials, API keys, saved preferences, or generated logs.
- Review `.gitignore` before committing changes.

## 👨‍💻 Author

**Janhvhi Taunk**

Developed as an academic project demonstrating local AI assistance, tool-based routing, policy retrieval, and persistent preferences.
