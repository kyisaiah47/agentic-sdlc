<div align="center">

<img src="assets/banner.png" alt="banner" width="100%" />

# 🤖 Agentic SDLC Pipeline

**From PR to production — reviewed, tested, and deployed by AI agents.**

![UiPath](https://img.shields.io/badge/UiPath-Maestro%20BPMN-FF6D01?style=for-the-badge&logo=uipath&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Code%20Agent-7B5EA7?style=for-the-badge&logo=anthropic&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Webhooks-181717?style=for-the-badge&logo=github&logoColor=white)

*UiPath Agent Hackathon 2026 — Track 2: UiPath Maestro BPMN*

</div>

<br/>

An end-to-end agentic software delivery pipeline that automates the entire path from pull request to production deployment. When a PR is opened, a Claude Code agent reviews the diff for quality, security, and logic issues; UiPath Test Cloud runs the automated test suite against the branch; and UiPath Maestro BPMN orchestrates the full flow — including a human-in-the-loop approval gate before any production deploy. If a post-deploy regression is detected, a monitoring agent automatically triggers a rollback.

## ✨ Features

- **AI-Powered Code Review** — Claude Code agent analyzes every PR diff for security issues, logic errors, and code quality
- **Automated Test Execution** — UiPath Test Cloud runs the full test suite against the PR branch before any merge
- **BPMN Orchestration** — Maestro BPMN manages the entire SDLC flow with clear decision gateways and audit trails
- **Human Approval Gates** — Tech leads review and approve/reject directly inside Maestro at critical checkpoints
- **Automated Production Deploy** — Approved changes trigger GitHub Actions for deployment without manual intervention
- **Regression Monitoring & Rollback** — A post-deploy monitoring agent watches for regressions and initiates a rollback BPMN case automatically

## 🛠️ Tech Stack

UiPath Maestro BPMN · UiPath Agent Builder · UiPath Test Cloud · UiPath API Workflows · Anthropic Claude API · GitHub Webhooks & Actions · Python 3.10+ · Slack (optional notifications)

## 🚀 Getting Started

### Prerequisites

- UiPath Automation Cloud account
- Anthropic API key
- GitHub repo with webhook configured
- Python 3.10+

### Install

```bash
pip install anthropic requests python-dotenv
```

### Environment Variables

```bash
ANTHROPIC_API_KEY=...
GITHUB_TOKEN=...
UIPATH_CLIENT_ID=...
UIPATH_CLIENT_SECRET=...
UIPATH_TENANT=...
UIPATH_ORG=...
```

### Run the Webhook Handler

```bash
python webhooks/github_handler.py
```

This starts the GitHub webhook receiver locally. Configure your repo's webhook to point at this handler — it will trigger the Maestro BPMN process automatically on each new PR.

## 📄 License

MIT
