# 🎓 Student Support Agent
### An AI-Powered Student Assistance System using Agentic AI

**Developed as part of the Agentic AI Engineering Assignments**

---

## 👨‍💻 Project Details

| Detail | Information |
|---|---|
| **Project Title** | Student Support Agent |
| **Student Name** | Janhvhi Taunk |
| **Subject** | Agentic AI Engineering |
| **Project Type** | Academic Project |
| **Programming Language** | Python |
| **Interface** | Streamlit |
| **AI Model** | Llama 3.2:1B |
| **LLM Runtime** | Ollama |
| **Assignments** | Assignment 1 and Assignment 2 |

---

## 📌 1. Project Overview

The **Student Support Agent** is an AI-powered application designed to provide students with an interactive and personalized support system.

The application uses Python, Streamlit, and a locally running Large Language Model (LLM) through Ollama to answer student queries and provide relevant information.

The project is developed in two stages:

- **Assignment 1:** Implements a basic AI-powered student support chatbot that can understand and respond to general queries.
- **Assignment 2:** Extends the application by introducing student authentication, personalized information retrieval, access control, human approval workflows, and activity monitoring.

The main objective is to demonstrate how an AI agent can provide useful assistance while maintaining privacy, security, and controlled access to student information.

---

## 🎯 2. Project Objectives

- Build an interactive AI-powered student assistance application.
- Provide quick responses to general student queries.
- Implement student authentication and personalized responses.
- Protect private student information through access control.
- Introduce human-in-the-loop approval for sensitive requests.
- Maintain audit logs and evaluation records.
- Demonstrate responsible and secure AI application development.

---

## 🛠️ 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Interactive web application interface |
| Ollama | Local LLM execution |
| Llama 3.2:1B | Language model for AI responses |
| Pandas | Data handling and processing |
| JSON / Local Files | Sample student data and application records |
| Git & GitHub | Version control and project hosting |

---

# 📘 4. Assignment 1 – Basic Student Support Agent

### Overview

Assignment 1 focuses on developing a basic AI-powered chatbot that allows users to interact with the Student Support Agent through a simple web interface.

### Key Features

- Interactive chat interface built using Streamlit.
- Accepts natural-language questions from users.
- Uses the locally running Llama 3.2:1B model through Ollama.
- Generates AI-based responses to general queries.
- Provides a simple and user-friendly interface.
- Supports a basic question-and-answer interaction.

### Working

1. The user opens the Streamlit application.
2. The user enters a question in the chat interface.
3. The application processes the input.
4. The query is passed to the local Ollama model.
5. Llama 3.2:1B generates a response.
6. The response is displayed in the chat interface.

---

# 📗 5. Assignment 2 – Personalized Student Support Agent

### Overview

Assignment 2 extends Assignment 1 by introducing authentication, personalized student assistance, privacy controls, and human-in-the-loop functionality.

The system identifies the logged-in student and provides access only to the information that the student is authorized to view.

### Key Features

**1. Student Authentication**
- Student login using unique student IDs and passwords.
- Maintains student-specific sessions.
- Provides personalized assistance after login.

**2. Personalized Student Information**
- Retrieves student-specific information.
- Supports queries related to academic records, fees, scholarships, and profile details.
- Uses the logged-in student's identity when retrieving private information.

**3. Access Control and Privacy**
- Prevents students from accessing another student's private information.
- Applies access restrictions to student-specific queries.
- Provides controlled access to sensitive information.

**4. Human-in-the-Loop (HITL) Approval**
- Sensitive requests generate approval requests.
- Reviewer can approve or reject pending requests.
- Reviewer authentication is required for the approval interface.
- Approval decisions are recorded for tracking.

**5. Audit Logs**
- Records relevant user activities and system actions.
- Helps maintain transparency and traceability.

**6. Evaluation Logs**
- Maintains evaluation-related records for monitoring application interactions.

**7. Student Preferences and Memory**
- Supports student preferences and stored context to improve personalized interactions.

**8. Policy-Based Responses**
- Supports policy-related information retrieval.
- Helps provide relevant responses to student queries.

### Working

1. The student opens the application.
2. The student logs in using their credentials.
3. The application identifies the authenticated student.
4. The student submits a query.
5. The system determines whether the query requires private student information, policy information, or a general AI response.
6. Access control checks are applied before retrieving private information.
7. Sensitive requests are sent for reviewer approval.
8. Approval or rejection decisions are recorded.
9. The application displays the appropriate response.

---

# 🏗️ 6. System Architecture

The application follows a modular architecture in which the Streamlit interface communicates with the application logic, authentication system, student data, and local AI model.

### Architecture Flow

```text
                 USER
                   |
                   v
          STREAMLIT INTERFACE
                   |
                   v
          APPLICATION LOGIC
                   |
          +--------+--------+
          |        |        |
          v        v        v
      GENERAL   STUDENT   POLICY
      QUERIES   QUERIES   QUERIES
          |        |        |
          v        v        v
        OLLAMA   AUTH &   POLICY
        LLM      ACCESS   RETRIEVAL
          |      CONTROL
          |        |
          |        v
          |   STUDENT DATA
          |        |
          |        v
          |   APPROVAL
          |   WORKFLOW
          |        |
          +--------+
                   |
                   v
             FINAL RESPONSE
                   |
                   v
              AUDIT LOGS
```

### Main Components

| Component | Responsibility |
|---|---|
| Streamlit UI | User interaction and application interface |
| Application Logic | Processes and routes user queries |
| Authentication | Validates student login |
| Student Data | Stores sample student information |
| Access Control | Restricts unauthorized data access |
| Ollama | Runs the local language model |
| Approval Module | Handles reviewer approval and rejection |
| Audit Module | Records application activities |
| Evaluation Module | Maintains evaluation records |

---

## ⚙️ 7. How to Install and Run the Project

### Prerequisites

Install the following software:

- Python 3.10 or above
- Git
- Visual Studio Code (recommended)
- Ollama

### Step 1: Clone the Repository

```bash
git clone https://github.com/Janhvhi/student-support-agent.git
```

### Step 2: Navigate to the Project Folder

```bash
cd student-support-agent
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Download the Ollama Model

Install and start Ollama, then run:

```bash
ollama pull llama3.2:1b
```

### Step 7: Run the Application

```bash
streamlit run app.py
```

### Step 8: Open the Application

Open the following URL in your browser:

```text
http://localhost:8501
```

---

## 🔐 8. Demo Login Credentials

The following sample credentials are provided for demonstration purposes.

### Student Login

| Student ID | Password |
|---|---|
| STU001 | student123 |
| STU002 | student123 |
| STU003 | student123 |

### Reviewer Login

```text
Reviewer Passcode: ADMIN2026
```

**Note:** These are demonstration credentials and should not be used in a production environment.

---

## 🧪 9. Testing and Demonstration

The following scenarios can be used to demonstrate the application.

### Assignment 1

- Ask general questions through the chatbot.
- Verify that the application generates AI responses.
- Demonstrate the interaction with the local Llama model.

### Assignment 2

- Log in using a student account.
- Ask questions about the logged-in student's information.
- Attempt to access another student's private information.
- Submit a sensitive request.
- Log in as a reviewer and approve or reject the request.
- Verify the relevant audit and evaluation records.
- Demonstrate student preferences and policy-related queries.

---

## 🔒 10. Security and Privacy Considerations

The project demonstrates important security concepts:

- Student authentication.
- Role-based access restrictions.
- Protection against unauthorized student data access.
- Controlled handling of sensitive requests.
- Human review before sensitive request decisions.
- Audit logging for traceability.
- Local LLM execution through Ollama.

**Important:** This is an academic demonstration project and is not intended to be deployed as a production-ready student information management system.

---

## ⚠️ 11. Current Limitations

- The application uses sample student data.
- The local Llama model has limited capabilities compared with larger language models.
- The approval workflow records reviewer decisions but does not automatically update the student database after approval.
- The project is intended for academic demonstration and learning purposes.

---

## 🚀 12. Future Enhancements

- Integrate a production database such as PostgreSQL.
- Implement stronger authentication and role-based permissions.
- Connect the system to an actual college ERP.
- Add automated email and notification services.
- Implement persistent conversation memory.
- Integrate advanced LLMs and retrieval-augmented generation (RAG).
- Add comprehensive automated testing and monitoring.
- Implement database updates after authorized approval.

---

## 📂 13. Project Structure

```text
student-support-agent/
│
├── app.py
├── ai_helper.py
├── approval.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── Student data and application records
│
├── backup/
│   └── Backup files
│
└── Other supporting application files
```

*Note: The exact contents of the folders may vary depending on the latest project version.*

---

## 👩‍💻 14. Developer

**Janhvhi Taunk**

Developed as part of the **Agentic AI Engineering** academic assignments.

**Project:** Student Support Agent

**Repository:** [GitHub – Student Support Agent](https://github.com/Janhvhi/student-support-agent)

---

## 🙏 15. Acknowledgement

This project was developed as part of the Agentic AI Engineering coursework to understand the practical implementation of AI agents, large language models, authentication, access control, and human-in-the-loop workflows.

Thank you for reviewing this project!

---

**⭐ If you find this project useful, feel free to explore the repository.**
