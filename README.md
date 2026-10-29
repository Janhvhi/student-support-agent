
# Intelligent Student Support Agent

## 1. Project Overview

The Intelligent Student Support Agent is a local AI-powered chatbot
that helps students with fee status, scholarship status, college
policy questions, and general student support.

## 2. Technologies Used

- Python
- Streamlit for the chat interface
- Ollama with the Llama 3.2 1B model
- CSV files for student records
- JSON for persistent memory
- Keyword-based retrieval for policy documents

## 3. Main Features

- Interactive chat interface
- Fee status lookup using student ID
- Scholarship status lookup using student ID
- Retrieval of relevant sections from a policy document
- Local AI responses using Ollama
- Persistent storage of non-sensitive preferences
- Basic evaluation logging, including response time and routing
- Error handling for missing records and AI connection failures

## 4. Project Structure

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
└── data/
    ├── students.csv
    ├── student_policy.txt
    ├── memory.json
    └── evaluation_logs.csv

## 5. Setup Instructions

1. Install Python.
2. Install Ollama.
3. Download the model:

   ollama run llama3.2:1b

4. Activate the project virtual environment.
5. Install dependencies:

   python -m pip install streamlit requests

6. Run the application:

   python -m streamlit run app.py

7. Open http://localhost:8501 in a browser.

## 6. Sample Test Cases

| Test | Input | Expected Result |
|---|---|---|
| Fee status | What is my fee status for STU001? | Paid |
| Scholarship | Check scholarship status for STU002 | Under Review |
| Policy retrieval | What should I do if my fees are pending? | Relevant fee policy |
| General AI | Explain student support | Local AI response |
| Persistent memory | Save a preference | Preference stored locally |

## 7. Limitations

- Policy retrieval currently uses keyword matching.
- Student records are sample CSV data.
- The policy document is sample content, not an official college policy.
- Local AI response quality and speed depend on the computer.
- Memory uses basic safeguards and is not a complete sensitive-data detector.
- Evaluation logs provide basic operational metrics, not a complete accuracy benchmark.

## 8. Privacy

The AI model runs locally through Ollama. Student records and
preferences are stored in local files. Do not use real sensitive
student data in this demonstration.
