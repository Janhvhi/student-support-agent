# Student Support Agent – Assignment 2

A Streamlit-based student support assistant extending Assignment 1 with student authentication, private record authorization, human approval requests, audit logs, policy retrieval, persistent safe preferences, and response evaluation.

## Features
- Universal university support chat powered by local Ollama (`llama3.2:1b`).
- Policy retrieval from `data/student_policy.txt`.
- Student login and own-record lookup only.
- Application-level authorization blocks attempts to access another student's record.
- Sensitive record-change requests are queued for reviewer approval; no change is applied automatically.
- Audit and evaluation CSV logs.
- Preference memory rejects common sensitive data, including passwords and OTPs.

## Demo accounts
All sample accounts use password `student123`:
- STU001
- STU002
- STU003

Demo reviewer passcode: `ADMIN2026` (classroom demonstration only; replace with proper administrator authentication before real deployment).

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.2:1b
ollama serve
```
In another terminal:
```powershell
.venv\Scripts\activate
streamlit run app.py
```

## Test scenarios
1. Log in as STU001 / student123 and ask "What is my fee status?"
2. Ask "Show STU002 fee details" while signed in as STU001 – must be blocked.
3. Ask "Change my phone number to 9999999999" – creates a pending approval request; it does not modify the student record.
4. Open Approval Requests, enter reviewer passcode `ADMIN2026`, and approve or reject the request.
5. Try saving an OTP/password as a preference – memory rejects it.
6. Ask a policy question such as "What should I do if my fees are pending?"

## Important limitations
This is a classroom prototype using fictional CSV records. The reviewer passcode is intentionally a demo mechanism, not production authentication. Approval status is audited, but this prototype does not execute a real student-record change after approval. Real deployment needs institution-managed identity, role-based reviewer accounts, a database, secure secret management, HTTPS, and retention controls.

Token counts are not currently exposed by the selected Ollama response path; response time and answer length are logged for evaluation.
