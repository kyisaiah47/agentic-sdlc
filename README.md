<div align="center">

<img src="assets/banner.png" alt="banner" width="100%" />

# 🤖 Agentic SDLC Pipeline

**From PR to production — reviewed, tested, and deployed by AI agents.**

![UiPath](https://img.shields.io/badge/UiPath-Maestro%20BPMN-FF6D01?style=for-the-badge&logo=uipath&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Code%20Agent-7B5EA7?style=for-the-badge&logo=anthropic&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Webhooks-181717?style=for-the-badge&logo=github&logoColor=white)

*UiPath Agent Hackathon 2026 — Track 2: UiPath Maestro BPMN · Built with UiPath Studio Web*

</div>

<br/>

An end-to-end agentic software delivery pipeline that automates the entire path from pull request to production deployment. When a PR is opened, a Claude Code agent reviews the diff for quality, security, and logic issues; UiPath Test Cloud runs the automated test suite against the branch; and UiPath Maestro BPMN orchestrates the full flow — including a human-in-the-loop approval gate before any production deploy. If a post-deploy regression is detected, a monitoring agent automatically triggers a rollback.

---

## Project Description

Most engineering teams have no system connecting code review, testing, and deployment. PRs sit waiting for manual review, tests run late, and regressions get caught after the fact. This pipeline automates the entire SDLC handoff chain using UiPath Maestro BPMN as the orchestration backbone, with AI agents handling code review and post-deploy monitoring.

**Flow:**
```
GitHub PR opened
      │
      ▼
Vercel Webhook Handler — fetches diff, triggers BPMN
      │
      ▼
UiPath Maestro BPMN Process
      │
      ├── [Step 1] Claude Code Agent — reviews PR diff
      │           returns { approved, blocking_issues, suggestions, summary }
      │
      ├── [Step 2] UiPath Test Cloud — runs test suite on PR branch
      │           returns { passed, failed_tests, test_run_id }
      │
      ├── [Gateway] Both pass?
      │     ├── Yes → auto-merge to staging (GitHub API)
      │     └── No  → Human Review Gate (tech lead approves/rejects in Maestro)
      │
      ├── [Step 3] GitHub Actions workflow_dispatch → production deploy
      │
      └── [Step 4] Monitoring Agent — polls health endpoints post-deploy
                        └── regression detected → trigger RollbackBPMN case
```

---

## UiPath Components

| Component | Role |
|---|---|
| **Maestro BPMN** | Orchestrates the full SDLC flow — review, test, gate, deploy, monitor |
| **Agent Builder** | Claude Code reviewer agent and post-deploy monitoring agent |
| **API Workflows** | GitHub webhook receiver, GitHub merge API, GitHub Actions dispatch |
| **Test Cloud** | Automated test execution triggered against each PR branch |

---

## Agent Type

This solution uses **Coded Agents**.

- `agents/claude_reviewer.py` — a coded agent that calls the Anthropic API with the PR diff and returns a structured JSON verdict
- `agents/monitoring_agent.py` — a coded agent that polls health endpoints post-deploy and signals the BPMN process to trigger rollback if regressions are detected

Both agents are invoked as external service task steps inside the Maestro BPMN process.

---

## Features

- **AI-Powered Code Review** — Claude analyzes every PR diff for security vulnerabilities, logic errors, and code quality issues
- **Automated Test Execution** — UiPath Test Cloud runs the full test suite against the PR branch before any merge
- **BPMN Orchestration** — Maestro BPMN manages the entire flow with clear decision gateways and audit trails
- **Human Approval Gates** — Tech leads review and approve/reject directly inside Maestro at critical checkpoints
- **Automated Production Deploy** — Approved changes trigger GitHub Actions without manual intervention
- **Regression Monitoring & Rollback** — Post-deploy monitoring agent watches for regressions and initiates a rollback BPMN case automatically

---

## Setup Instructions

### Prerequisites

- UiPath Automation Cloud account (UiPath Labs)
- Anthropic API key
- GitHub repository with webhook configured
- Python 3.10+

### 1. Clone the repo

```bash
git clone https://github.com/kyisaiah47/uipath-agenthack.git
cd uipath-agenthack
```

### 2. Install dependencies

```bash
pip install anthropic requests python-dotenv
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```bash
ANTHROPIC_API_KEY=        # Anthropic console
GITHUB_TOKEN=             # GitHub PAT with repo scope
GITHUB_WEBHOOK_SECRET=    # Secret set in GitHub webhook settings
UIPATH_CLIENT_ID=         # UiPath Automation Cloud → API access
UIPATH_CLIENT_SECRET=
UIPATH_TENANT=
UIPATH_ORG=
UIPATH_API_KEY=           # UiPath API key for triggering BPMN
UIPATH_BPMN_TRIGGER_URL=  # Maestro process trigger URL
UIPATH_ACCESS_TOKEN=      # For monitoring agent rollback trigger
```

### 4. Import the BPMN process into Maestro

Import `workflows/bpmn/sdlc_pipeline.bpmn` into your UiPath Automation Cloud tenant via Maestro → Processes → Import.

### 5. Deploy the webhook handler

The webhook handler is a Vercel serverless function at `api/webhook.py`. Deploy with:

```bash
vercel --prod
```

Or run locally:

```bash
python webhooks/github_handler.py
```

### 6. Configure the GitHub webhook

In your target GitHub repository → Settings → Webhooks → Add webhook:

- **Payload URL:** `https://your-vercel-url.vercel.app/api/webhook`
- **Content type:** `application/json`
- **Events:** Pull requests

### 7. Test the reviewer agent locally

```bash
python scripts/test_reviewer.py
```

This runs a sample PR diff (with intentional SQL injection vulnerabilities) through the Claude reviewer and prints the structured JSON result.

The demo codebase used in testing is in `demo/sample_repo/`.

---

## Project Structure

```
agents/
  claude_reviewer.py        # Claude API code review agent (coded agent)
  monitoring_agent.py       # Post-deploy regression monitor (coded agent)
api/
  webhook.py                # Vercel serverless webhook handler
webhooks/
  github_handler.py         # Local webhook server (development)
workflows/
  bpmn/
    sdlc_pipeline.bpmn      # Maestro BPMN process definition
scripts/
  trigger_test_run.py       # UiPath Test Cloud API trigger
  deploy.py                 # GitHub Actions deployment trigger
  test_reviewer.py          # Local test for the Claude reviewer agent
demo/
  sample_repo/              # Sample codebase used in demo reviews
```

---

## Built with Claude Code

[Claude Code](https://claude.ai/code) by Anthropic was the primary development tool used throughout this project.

**How it contributed:**

- **Agent scaffolding** — Claude Code generated the initial structure and logic for both coded agents (`agents/claude_reviewer.py` and `agents/monitoring_agent.py`), including the Anthropic API call patterns, prompt construction, and structured JSON response handling.
- **BPMN workflow generation** — Claude Code authored the Maestro BPMN XML (`workflows/bpmn/sdlc_pipeline.bpmn`), including the sequence flows, exclusive gateways, service task definitions, and human task configuration for the approval gate.
- **UiPath API integration** — Claude Code wrote the UiPath Automation Cloud API integration code used in `scripts/trigger_test_run.py` and `scripts/deploy.py`, including OAuth token exchange, process trigger payloads, and polling logic.
- **Webhook handler** — Claude Code produced the Vercel serverless webhook handler (`api/webhook.py`) and the local development server (`webhooks/github_handler.py`), including HMAC signature verification and diff extraction.
- **Test harness** — Claude Code wrote `scripts/test_reviewer.py` and the sample vulnerable codebase in `demo/sample_repo/` used to validate the reviewer agent output.

Claude Code sessions were used continuously from initial scaffolding through final integration. The commit history and overall code structure reflect Claude Code's scaffolding approach throughout.

---

## Presentation Deck

[View the submission deck →](https://docs.google.com/presentation/d/1v8XQBxn0L4bH1Try-CgNg7esFZxQk-cL/edit?usp=sharing)

---

## License

MIT
