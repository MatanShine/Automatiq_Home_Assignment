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
├─ backend/
│  ├─ app/
│  │  ├─ main.py                  # FastAPI app & router registration
│  │  ├─ api/
│  │  │  └─ endpoints.py          # /chat endpoint
│  │  ├─ db/
│  │  │  └─ queries.py            # SQLite data access helpers
│  │  ├─ services/
│  │  │  ├─ llm_client_setup.py   # LLM client wiring
│  │  │  ├─ llm_config.py         # model name, system prompts, constants
│  │  │  ├─ tools.py              # tool schemas/metadata
│  │  │  └─ llm_tool_handlers.py  # Python implementations of tools
│  │  └─ models/                  # Pydantic request/response models
│  └─ data/
│     └─ employees.db             # SQLite DB with employees & training data
│
├─ frontend/
│  ├─ src/
│  │  ├─ App.tsx                  # App root and routing
│  │  ├─ components/
│  │  │  ├─ Chat.tsx              # Chat UI
│  │  │  └─ MessageBubble.tsx     # Chat message rendering
│  │  ├─ hooks/
│  │  │  └─ useChatHistory.ts     # Session & history management
│  │  ├─ context/
│  │  │  └─ ThemeContext.tsx      # Light/dark theme
│  │  └─ api/
│  │     └─ client.ts             # Typed client for /chat
│  └─ vite.config.ts
│
├─ assignment/                    # Original home-assignment materials
├─ docker-compose.yml
├─ .env.example
└─ README.md
```
### 6. High-Level Architecture

Single /chat endpoint

All conversations (employee or CISO) go through one HTTP endpoint:
1. The frontend sends:messages (history)
	-	Optional employee_id and employee_name
2.	The backend:
	- Validates authentication (ID + name)
	- Calls the LLM with system and tool definitions
	- Lets the LLM pick tools (e.g., “get_employee_status”, “list_employees_by_status”)
	- Executes the corresponding handler (read-only DB queries)
	- Returns a ChatResponse back to the frontend

This design keeps:
	- Auth checks in one place.
	- Tool chaining and history formatting centralized.
	- The frontend completely unaware of database internals.
### 7. DataBase
- All DB access is done via simple helper functions in backend/app/db/queries.py using Python’s sqlite3.
- There is deliberately no ORM to keep the assignment **focused and transparent**.

### 8. Authentication flow:

The assignment requires ID + employee name before any meaningful answer. The flow is:
1.	Unauthenticated user:
	- The LLM is instructed to ask for name and ID first.
	- Until both are provided and verified, only generic prompts are allowed (“Please provide your name and ID”).
2.	Verification:
	- Backend checks (employee_id, employee_name) via employee_exists_in_database in db/queries.py.
	- If the record doesn’t exist, the LLM is instructed to respond as “unknown user”.
3.  Session handling:
	-	The frontend stores employee_id and employee_name in useChatHistory per session.
	-	Each /chat request includes these values so stateless backend instances can authenticate every call.
4.	Role detection (Employee vs CISO):
	-	The DB also tracks whether a user is a CISO (e.g., an is_ciso flag).
	-	After authentication, the backend computes is_ciso and includes it in the context passed to the LLM.
	-	Tool availability then depends on this flag (see next section).

### 9. Authorization rules:
-   Unauthorized:
    -   Can only query their name and id to "login".
-	Employees:
    -	Can only query their own training status and videos.
    -	No access to organization-wide stats or other employees.
-	CISO:
	•	Can query any employee by name and ID.
	•	Can list all employees by status.
	•	Can request global statistics.

All of this is enforced in the tool handlers, not in the frontend, to prevent bypassing via custom clients.

### 10. LLM & Tooling Design

The backend uses an OpenAI-compatible LLM (default: gpt-4o-mini **for maximum speed and minimum costs**) configured in:
-	llm_config.py – model name, system prompts, and instruction strings.
-	llm_client_setup.py – instantiated LLM client using env variables.

**Tools**

Tools are described in services/agent_tools/tools.py and implemented in llm_tool_handlers.py.

Each tool:
1.	Has a schema (name, description, parameters).
2.	Is wired to a handler that:
	-	Validates inputs (e.g., employee must exist).
	-	Reads from SQLite via db/queries.py.
	-	Returns a structured result (Python dict) for the LLM to verbalize.

This separation lets us:
-	Change prompts or models without touching business logic.
-	Add new capabilities by just:
    -	Declaring the tool schema.
    -	Implementing the handler.
	-	Registering it in TOOL_HANDLERS.

### 11. Scaling & Performance
- 	Stateless backend:
	-	/chat requests include all necessary context (history + auth).
	-	Any FastAPI instance can handle any request; no sticky sessions.
	-	Easily run multiple replicas behind a load balancer in production.
-	Database considerations:
	-	SQLite is sufficient for this assignment and easy to package in Docker.
	-	For higher scale, the same query abstraction could be backed by Postgres/MySQL.
-   Caching:
	-	we already cache expensive CISO statistics queries and llm responses to reduce time and costs.
-	Optimizations (future):
	-	Stream partial LLM responses to the frontend for better UX.

### 12. Known Limitations & Future Work
-	No persistent sessions across browser tabs or devices (history is in-memory on the frontend).
-	No admin UI for browsing training stats – CISO interacts only via chat.
-	No automated tests checked in yet; strategy exists but needs implementation.
-	Error handling is basic and could be extended (e.g., nicer error boundaries in the UI).


### 13. Summary

This project implements the CyFortis AI assistant as specified:
-	Employee & CISO natural language interface over training data.
-	Authentication enforced via name + ID.
-	Clear separation of concerns: React UI, FastAPI backend, LLM tools, SQLite database.
-	Read-only, guarded LLM usage focused strictly on the cybersecurity training task.
-	A single /chat endpoint that centralizes conversation logic, tools, and auth.

The design emphasizes safety, extensibility, and developer ergonomics, while staying faithful to the assignment constraints.
