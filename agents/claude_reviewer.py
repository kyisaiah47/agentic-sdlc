"""
Claude Code reviewer agent.
Called by UiPath as a Coded Agent step in the BPMN process.
Input: PR diff + metadata (JSON via stdin or UiPath argument)
Output: review result JSON { approved: bool, issues: [...], summary: str }
"""

import os
import json
import sys
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are a senior software engineer performing a code review.
Analyze the provided PR diff and return a structured JSON review.

Focus on:
- Security vulnerabilities (injection, auth bypass, secrets in code)
- Logic errors and edge cases
- Performance issues
- Code clarity and maintainability

Return ONLY valid JSON in this exact shape:
{
  "approved": <bool>,
  "confidence": <0.0-1.0>,
  "blocking_issues": [{"line": <int|null>, "severity": "critical|high|medium", "description": <str>}],
  "suggestions": [{"line": <int|null>, "description": <str>}],
  "summary": <str, 2-3 sentences>
}

approved=true only if there are zero critical/high blocking_issues."""


def review_pr(pr_diff: str, pr_title: str, pr_description: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"PR Title: {pr_title}\n\nPR Description: {pr_description}\n\nDiff:\n```\n{pr_diff}\n```",
            }
        ],
    )
    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()
    return json.loads(text)


if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    result = review_pr(
        pr_diff=payload["diff"],
        pr_title=payload.get("title", ""),
        pr_description=payload.get("description", ""),
    )
    print(json.dumps(result, indent=2))
