# CyFortis Training Assistant

AI assistant that answers **cybersecurity training** questions for both **employees** and the **CISO** using natural language.

The agent can:

- Tell an employee whether they’ve finished the training and which videos are missing.
- Let the CISO inspect a single employee’s status and training summary.
- Let the CISO query all employees by status and see overall statistics (min/max/avg time, fastest, slowest).
- Enforce authentication (ID + name) before any training data is exposed.
- Stay strictly on-topic (security training only) and operate in a **read-only** way.

---

## 🚀 Quickstart

### 1. Prerequisites

- Docker & Docker Compose
- OpenAI API key

### 2. Environment file

In the project root:

```bash
cp .env.example .env
```
Then edit .env with:
```bash
OPENAI_API_KEY=your_token_here
```
The backend reads these variables to configure the LLM client.


### 3. Run the full stack
From the project root:
```bash
docker-compose up --build
```
This starts:
- Backend: FastAPI app (Python) on http://localhost:8000
- Frontend: React/Vite app (TypeScript) on http://localhost:3000

Both services use bind mounts and hot reload for a smooth dev experience.

### 4. Where to Access
- Frontend (chat UI)
http://localhost:3000
Vite dev server with hot module replacement, reading and displaying messages from the backend.
- Backend (API) http://localhost:8000 FastAPI with:
    - POST /chat – single endpoint for all chat interactions.
    - Optional FastAPI docs: http://localhost:8000/docs


### 5. Repo structure
```bash
.
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py
│   │   ├── db/
│   │   │   └── queries.py
│   │   ├── main.py
│   │   ├── schemas/
│   │   └── services/
│   │       ├── agent_tools/
│   │       ├── cache.py
│   │       ├── cache/
│   │       └── llm/
│   ├── data/
│   │   └── employees.db            # assignment supplied data base
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── Chat.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── InputBar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── ThemeToggle.tsx
│   │   ├── context/
│   │   │   └── ThemeContext.tsx
│   │   ├── hooks/
│   │   │   └── useChatHistory.ts
│   │   ├── index.css
│   │   ├── main.tsx
│   │   └── styles/
│   │       └── chat.css
├── docker-compose.yml
├── .env.example
├── README.md
└── assignment/
```
### 6. Architecture overview

All conversations (employee or CISO) go through a single HTTP endpoint: POST /chat.
1.	The frontend sends:
	-	messages (conversation history)
	-	Optional employee_id and employee_name
2.	The backend:
	-	Validates authentication (ID + name) against the SQLite database
	-	Calls the LLM with system + tool definitions
	-	Lets the LLM pick tools (e.g., get_employee_status, list_employees_by_status)
	-	Executes the corresponding handler (read-only DB queries)
	-	Returns a structured ChatResponse to the frontend

This design:
	-	Keeps auth checks in one place.
	-	Centralizes tool chaining and history formatting.
	-	Keeps the frontend completely unaware of database internals.

**For detailed design decisions, tradeoffs, and future work, see:**
- `Explanations.pdf`

### 7. Known limitations
-	No persistent sessions across browser tabs or devices (history is in-memory on the frontend).
-	No admin UI for browsing training stats - the CISO interacts only via chat.
-	Error handling is basic and could be extended (e.g., nicer error boundaries in the UI).