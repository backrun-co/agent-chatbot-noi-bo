# Codex and Claude Code compatibility

The repository uses the portable Agent Skills layout: a root `SKILL.md`, optional references and scripts, and reusable assets.

## Codex

Install into either:

- user scope: `~/.codex/skills/document-chatbot-builder`
- project scope: `.codex/skills/document-chatbot-builder`

Codex may read `agents/openai.yaml` for UI metadata and automatic invocation. Restart or reload the client after installation when the skill is not discovered immediately.

## Claude Code

Install into either:

- user scope: `~/.claude/skills/document-chatbot-builder`
- project scope: `.claude/skills/document-chatbot-builder`

Claude Code uses the same `SKILL.md` and ignores Codex-specific `agents/openai.yaml` metadata. Restart the session or reload skills after installation when needed.

## Portable execution rules

- Use Python scripts for deterministic setup rather than shell-specific installers.
- Derive paths from the skill directory; do not hardcode the creator's machine path.
- On Windows use `.venv\\Scripts\\python.exe`; on macOS/Linux use `.venv/bin/python`.
- Use the agent's available terminal, browser, GitHub, and computer-use tools. Do not require a Codex-only connector for the core local workflow.
- When a browser or GitHub integration is unavailable, complete all safe local work and request only the smallest necessary user action.
