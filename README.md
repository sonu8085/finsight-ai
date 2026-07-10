FinSight AI

An AI-powered personal finance management app. Users track income and expenses, set budgets and savings goals, import transactions from CSV, and get spending insights from a built-in AI assistant that reasons over their actual transaction data.

Live app: https://finsight-ai-kappa-six.vercel.app


Overview

FinSight AI is a full-stack finance tracker built with a decoupled architecture: a FastAPI backend exposing a REST API, and a React single-page app consuming it. The standout feature is the AI assistant — rather than generic advice, it's given a structured summary of the user's real spending data and asked to answer questions using only that data, so responses are grounded and specific (e.g. "you spent 22% more on dining out this month than your 3-month average").


Features 

Authentication — JWT-based auth with access + refresh tokens, secure password hashing
Transactions — add, edit, and categorize income/expenses
CSV Import — bulk-import transaction history from a bank statement export
Budgets — set spending limits per category and track progress
Goals — define savings goals and monitor progress over time
Dashboard — visual breakdown of spending by category and trends over time (charts via Recharts)
AI Assistant — chat interface that answers finance questions grounded in the user's actual transaction data; falls back to a rule-based insights engine if no OpenAI API key is configured, so the app degrades gracefully rather than breaking
Rule-based insight engine — detects patterns like recurring subscriptions, weekend vs. weekday spending, and category trends without needing an LLM call


Tech Stack

Backend


FastAPI (async Python web framework)
SQLAlchemy (async ORM) + Alembic (database migrations)
PostgreSQL
JWT authentication (access + refresh token rotation)
OpenAI API integration
Pytest for automated testing (auth, budgets, transactions, dashboard/AI test suites included)


Frontend


React 19 + TypeScript
Vite (build tooling)
Tailwind CSS
TanStack Query (server-state management/caching)
React Router
Recharts (data visualization)
Axios


Architecture pattern: the backend follows a layered structure — routes → services → repositories → models — separating HTTP handling, business logic, and data access rather than putting everything in the route handlers.

Project Structure
```
FinSight-AI/
├── backend/
│   ├── app/
│   │   ├── ai/            # AI assistant + rule-based analysis engine
│   │   ├── api/           # Route handlers
│   │   ├── core/          # Config, database, security, dependencies
│   │   ├── models/        # SQLAlchemy models (user, transaction, budget, goal, etc.)
│   │   ├── repositories/  # Data access layer
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic layer
│   │   └── tests/         # Pytest test suites
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/            # Axios client + API calls
    │   ├── components/     # Reusable UI components
    │   ├── context/        # React context providers
    │   ├── hooks/          # Custom hooks
    │   ├── pages/           # Dashboard, Transactions, Budgets, Goals, Assistant, Login, Register, Import
    │   └── types/           # TypeScript types
    └── package.json
```
Running Locally

Backend

bashcd backend
python -m venv .venv
.venv\Scripts\activate        # Windows — use `source .venv/bin/activate` on Mac/Linux
pip install -r requirements.txt
cp .env.example .env          # then fill in your own DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
alembic upgrade head
uvicorn app.main:app --reload

API runs at http://localhost:8000 — interactive docs at http://localhost:8000/docs.

Frontend

bashcd frontend
npm install
npm run dev

App runs at http://localhost:5173.

Testing

bashcd backend
pytest

Covers authentication, budgets, transactions, and dashboard/AI endpoints.

Deployment


Backend: Render (Web Service, FastAPI + Uvicorn)
Frontend: Vercel (static build via Vite)
Database: managed PostgreSQL
