# ⚡ DevPulse AI
> **Tagline**: *"Other tools tell you what's wrong. DevPulse fixes it and proves the fix works."*

[![Track](https://img.shields.io/badge/hackFront_India_2026-AI_%26_Developer_Tools-indigo.svg)](https://whereuelevate.com/drills/hackfrontindia-2026)
[![Framework](https://img.shields.io/badge/FastAPI-Python_3.10+-emerald.svg)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/React_Vite-Tailwind_CSS-purple.svg)](https://vitejs.dev)
[![Verification](https://img.shields.io/badge/Sandbox-Agentic_Verification-blue.svg)](#agentic-verification-pipeline)

---

## 🌟 Overview
**DevPulse AI** is an autonomous Pull Request auditing & verified refactoring engine built for **hackFront India 2026** (`AI and Developer Tools` track).

Unlike traditional static analyzers that merely list warnings, DevPulse AI:
1. **Audits PRs**: Scans Python code for security vulnerabilities, cyclomatic complexity, resource leaks, and missing test coverage.
2. **Generates Unified Diffs**: Automatically writes minimal, production-ready code fixes for top findings.
3. **Agentic Verification**: Runs each generated fix inside an **isolated sandbox environment** (`py_compile` syntax check, scanner re-verification, and pytest execution) to prove the fix works before showing it to the developer!

---

## 🏗️ Architecture & Pipeline

```
   ┌─────────────────────────────────────────────────────────────┐
   │ 1. GitHub PR Ingestion / Local Demo App                     │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ 2. Agent 1: Security Sentinel                               │
   │    • Regex + Shannon Entropy Secret Scanner                 │
   │    • AST Security Scanner (SQLi, CMDi, Insecure Deser)      │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ 3. Agent 2: Quality & Architecture Agent                    │
   │    • Cyclomatic Complexity Engine (Threshold > 7)           │
   │    • Unhandled Open Resource Leak Detection                 │
   │    • Test Suite Coverage Verification                       │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ 4. Agent 3: Auto-Fix Agent (The Hero Feature)               │
   │    • Top 3 Severity Finding Selection                       │
   │    • Unified Diff Generation                                │
   │    • Isolated Temporary Sandbox Execution                   │
   │    • Syntax check -> Scanner Re-Verification -> Pytest      │
   │    • Status: ✅ Verified  |  ⚠️ Unverified                   │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ 5. Glassmorphic Dark-Mode Dashboard                         │
   │    • Deterministic 0-100 Code Health Score Gauge            │
   │    • Unified Red/Green Patch Viewer + 1-Click Copy & Download│
   └─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
devpulse-ai/
├── backend/
│   ├── main.py                  # FastAPI Application Entry Point
│   ├── github_service.py        # GitHub REST API Integration & PR Parsing
│   ├── health_score.py          # Deterministic Formula-based Health Scoring
│   ├── llm.py                   # Configurable LLM & Diff Patch Generator
│   ├── requirements.txt         # Python Dependencies
│   ├── agents/
│   │   ├── security_sentinel.py # Agent 1: Security Sentinel
│   │   ├── quality_architecture.py # Agent 2: Quality & Architecture Agent
│   │   ├── auto_fix_agent.py    # Agent 3: Auto-Fix Engine
│   │   └── pipeline.py          # 3-Agent Pipeline Orchestrator
│   ├── scanners/
│   │   ├── secret_scanner.py    # Regex & Shannon Entropy Detector
│   │   ├── security_scanner.py  # Python AST Security Scanner
│   │   └── quality_scanner.py   # Complexity & Resource Leak Scanner
│   └── sandbox/
│       └── sandbox.py           # Temporary Isolated Sandbox Verification Engine
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Glassmorphic Dark-Mode UI Component
│   │   ├── index.css            # Tailwind & Glassmorphism Utility Classes
│   │   └── main.tsx             # React Application Entry Point
│   ├── vite.config.ts           # Vite + Tailwind v4 Configuration
│   └── package.json
├── demo/
│   └── vulnerable_app/          # Bundled Test Vulnerable Flask Application
│       ├── app.py               # Contains Hardcoded AWS Secret, SQLi & File Leak
│       └── test_app.py          # Pytest suite
├── .env.example                 # Environment Variables Template
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

### 2. Backend Setup & Launch
```bash
# Move to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```
*Backend API will run at `http://localhost:8000`*

### 3. Frontend Setup & Launch
```bash
# Move to frontend directory
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
*Frontend UI will run at `http://localhost:5173`*

---

## 🧪 Testing the Bundled Demo App
Click the **"Try Demo"** button on the UI landing page. DevPulse AI will run the 3-agent pipeline locally on `demo/vulnerable_app/app.py` and output:
- **Health Score**: 75/100 (Deterministic breakdown)
- **Detected Vulnerabilities**: Hardcoded AWS Secret (`AKIA...`), SQL Injection in `/user` route, and unhandled `open()` resource leak in `/read_log`.
- **Verified Fixes**: 2 Sandbox-verified unified diffs (`✅ Verified`) ready to copy or download as `.patch` files!

---

## 🛡️ Engineering Rules & Safety
- **Secret Masking**: All detected credentials and API keys are masked (`AKIA...****`) in logs and UI.
- **Sandbox Safety**: Fix execution runs inside `tempfile.TemporaryDirectory()` with a 20-second timeout and automatic cleanup.
- **Deterministic Formula**: Score formula is strictly weighted: Security 40%, Quality 30%, Testing 30% with severity deductions.

---

## 🏆 Credits
Built by **Rafia Minhaj** (Microsoft Certified AI Agent Engineer | GSSoC '26 Rank #29) for **hackFront India 2026**!
