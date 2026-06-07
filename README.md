# Agentic SDLC Pipeline — UiPath AgentHack 2026

**Track**: UiPath Maestro BPMN (Track 2)

An agentic software delivery pipeline that uses Claude Code for AI-powered code review, UiPath Test Cloud for automated testing, and UiPath Maestro BPMN to orchestrate the full flow from PR to production — with human approval gates at critical decision points.

## What it does

```
GitHub PR opened
       ↓
UiPath API Workflow (GitHub webhook receiver)
       ↓
Maestro BPMN process starts
       ↓
[Step 1] Claude Code Agent — reviews PR diff (quality, security, logic)
       ↓
[Step 2] UiPath Test Cloud — runs test suite against PR branch
       ↓
[Gateway] Both pass?
   ├─ Yes → auto-merge to staging, notify team
   └─ No  → Human review gate (tech lead approves/rejects in Maestro)
       ↓
[Step 3] Human approval gate → production deploy
       ↓
[Step 4] Deploy via GitHub Actions API
       ↓
[Step 5] Monitoring agent — watches for post-deploy regressions
       └─ If regression detected → trigger rollback BPMN case
```

## UiPath Components Used

| Component | Role |
|-----------|------|
| Maestro BPMN | Orchestrates the full SDLC flow |
| Agent Builder | Claude Code reviewer agent, monitoring agent |
| API Workflows | GitHub webhook receiver, GitHub API calls, deploy trigger |
| Test Cloud | Automated test execution on PR branch |
| UiPath for Coding Agents (Claude Code) | Used to build this solution + embedded in review step |

## External Integrations

- **GitHub** — PR events (webhook), merge API, Actions trigger
- **Anthropic Claude API** — code review agent
- **Slack** (optional) — human-in-the-loop notifications

## Project Structure

```
agents/
  claude_reviewer.py      # Claude API code review agent
  monitoring_agent.py     # Post-deploy regression monitor
webhooks/
  github_handler.py       # GitHub webhook receiver → triggers BPMN
workflows/
  bpmn/                   # Maestro BPMN diagram exports
scripts/
  trigger_test_run.py     # UiPath Test Cloud API trigger
  deploy.py               # GitHub Actions deployment trigger
demo/
  sample_repo/            # Sample codebase used in demo
```

## Setup

### Prerequisites

- UiPath Automation Cloud account (UiPath Labs)
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

### Run the webhook handler locally

```bash
python webhooks/github_handler.py
```

## License

MIT
