# DevPulse AI

> **"Other tools tell you what's wrong. DevPulse fixes it and proves the fix works."**

[![hackFront India 2026](https://img.shields.io/badge/hackFront%20India%202026-AI%20%26%20Developer%20Tools%20Track-indigo?style=for-the-badge)](https://whereuelevate.com/drills/hackfrontindia-2026)
[![Python 3.11](https://img.shields.io/badge/Backend-Python%203.11%20%7C%20FastAPI-blue?style=for-the-badge&logo=python)](https://fastapi.tiangolo.com)
[![React Vite](https://img.shields.io/badge/Frontend-React%20%7C%20Vite%20%7C%20Tailwind-purple?style=for-the-badge&logo=react)](https://vitejs.dev)

---

## Overview

**DevPulse AI** is an autonomous Pull Request auditing and verified refactoring engine built for modern developer workflows. When given any public GitHub Pull Request URL, DevPulse orchestrates three sequential AI and static analysis agents, namely Security Sentinel, Quality and Architecture, and Auto-Fix. Rather than merely listing warnings or inserting unverified TODO comments, DevPulse generates complete unified diff patches and verifies every fix in an isolated execution sandbox before presenting verified diffs to the developer.

---

## How It Works (3-Agent Pipeline)

DevPulse operates via a 3-agent sequential workflow:

```
[ GitHub PR URL ] -> [ Agent 1: Security Sentinel ] -> [ Agent 2: Quality & Architecture ] -> [ Agent 3: Auto-Fix Agent ] -> [ Isolated Sandbox ] -> [ Health Score & Verified Diffs ]
```

1. **Agent 1: Security Sentinel Agent**
   - Scans code for credential leaks using multi-pattern regex matching and Shannon Entropy analysis for high-randomness secrets.
   - Detects SQL Injection (CWE-89), Command Injection (CWE-78), and hardcoded tokens.

2. **Agent 2: Quality & Architecture Agent**
   - Analyzes Python Abstract Syntax Trees (AST) for Excessive Cyclomatic Complexity (CWE-1074, threshold > 7).
   - Catches resource descriptor leaks (unclosed `open()` calls without context managers, CWE-775).
   - Detects missing test coverage across PR modules (ignoring test files themselves).

3. **Agent 3: Auto-Fix Agent (Hero Feature)**
   - Generates precision unified diff patches (`+`/`-` line edits) for auto-fixable finding categories.
   - Automatically injects missing dependencies (e.g., `import os` at top of file when replacing secrets with `os.getenv`).
   - **Sandbox Verification**: Applies patches to an isolated sandbox environment, re-executes compilation checks, and verifies issue resolution before marking the fix as **`Verified`**.

> **Note on Auto-Fix Scope**: Auto-Fix currently generates verified diffs for **hardcoded secrets**, **SQL injection**, and **resource leaks / missing error handling**. Findings that require human architectural judgment (e.g. high cyclomatic complexity refactoring) are flagged with a **`"Manual review recommended"`** badge instead of generating an unsafe automated fix.

4. **Automated Jira REST API Ticket Triage**
   - Automatically triages Critical and High severity findings directly into Jira Cloud as structured `Bug` tickets via Atlassian REST API v3.
   - Embeds affected file, line numbers, and proposed code diff patches directly inside the Jira issue description.
   - Includes feature toggle control (`JIRA_INTEGRATION_ENABLED=true/false`) and renders clickable ticket links directly in the DevPulse UI.

---

## Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS v4, Lucide Icons, Glassmorphism Dark Theme.
- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic, Requests.
- **Integrations**: Atlassian Jira Cloud REST API v3 (Automated Issue Triage & ADF Formatting).
- **Scanners & Analysis**: AST (Abstract Syntax Tree) NodeVisitors, Shannon Entropy Estimator, Regex Pattern Matching, Unified Diff Generators (`difflib`).
- **Sandbox Environment**: Isolated temporary execution & compilation sandbox (`py_compile` + AST re-scan).

---

## Quickstart & Setup Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create & activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
cp .env.example .env
# Edit .env and set your API keys and configuration settings

# Run FastAPI backend server
python -m uvicorn main:app --port 8000 --reload
```

The backend API will run at `http://localhost:8000`.

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run Vite dev server
npm run dev -- --host 127.0.0.1
```

The frontend UI will run at `http://localhost:5173`.

---

## Environment Variables (`.env.example`)

Copy `.env.example` to `.env` in the root or `backend/` directory:

```ini
# DevPulse AI Environment Variables
LLM_API_KEY=your_openai_or_gemini_api_key_here
LLM_MODEL=gpt-4o
GITHUB_TOKEN=your_optional_github_personal_access_token
JIRA_INTEGRATION_ENABLED=false
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USER_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=DEV
```

*Note: If `LLM_API_KEY` is not configured, DevPulse AI automatically uses its high-accuracy deterministic rule engine for finding explanations and fixes.*

---

## Known Limitations

1. **Language Scope**: Currently optimized for Python codebases and PRs. Multi-language support (Java/TypeScript) is planned for future iterations.
2. **Sandbox Isolation**: The sandbox operates in a temporary execution environment with syntax & AST compilation verification and timeout safeguards, rather than full OS-level Docker container isolation.

---

## Hackathon Submission

Built for **hackFront India 2026 - AI & Developer Tools Track**.
