---
name: agent-chatbot-noi-bo
description: Build, customize, run, explain, and publish a polished Streamlit document chatbot with cited sources. Supports local ChatGPT/Codex-plan sign-in without an API key and hosted deployment with a server-side OpenAI API key. Use for document Q&A/RAG chatbot creation, UI changes, sharing, or deployment; not for general-purpose chatbots unrelated to uploaded documents.
---

# Agent Chatbot Noi Bo

Create a working chatbot, not merely a tutorial. Automate safe local setup and validation; ask the user only for decisions, credentials, permissions, or actions that cannot be completed on their behalf.

## Choose the operating mode

- **Local mode (default):** set `CHATBOT_MODE=local`. Use **Continue with ChatGPT** and the user's eligible ChatGPT/Codex plan; do not request an API key. Retrieval stays local.
- **Hosted mode:** set `CHATBOT_MODE=hosted`. Use `OPENAI_API_KEY` from the hosting provider's secret manager. This is the default when the user asks to publish on Streamlit Community Cloud.
- **New chatbot:** scaffold from `assets/streamlit-rag-template/`, install dependencies, configure, test, and open a local preview.
- **Existing chatbot:** inspect it first, preserve working features and unrelated user changes, then make the requested edits.
- **Customize UI:** keep the dark acid-green design by default, but adapt branding, copy, layout, animation, and supported formats to the user's request. Offer concise customization ideas after the first working version.
- **Publish/share:** when the user requests deployment, carry it through to a verified public or private URL. Do not stop at generic instructions when tools can complete the work.

## New chatbot workflow

1. Select an empty target directory. If the user did not name one, use a short project name such as `document-chatbot` inside the current workspace.
2. Run `python scripts/bootstrap.py <target-directory>`. On Windows, use `py -3.12` or an available Python 3.11+ interpreter when `python` is unavailable.
3. If Python 3.11+ or Git is missing, install it using the platform's normal package manager when permitted. Ask only when administrator approval or an interactive installer is required.
4. Let the bootstrap script copy the template, create `.venv`, upgrade pip, and install `requirements.txt`. Do not recreate these steps manually unless the script reports a concrete failure.
5. Select authentication from the intended runtime:
   - For local use, keep `CHATBOT_MODE=local`, start the app, and let the user complete **Continue with ChatGPT** in their browser. Read `references/local-chatgpt.md` before modifying this flow.
   - For hosted use, set `CHATBOT_MODE=hosted` and load `OPENAI_API_KEY` only from an environment variable or provider secret manager.
   - Never read or copy Codex/ChatGPT credential caches, never log OAuth tokens, and never commit credentials.
6. Run `python scripts/check_project.py <target-directory>` and the template tests. Fix failures before previewing.
7. Start Streamlit from the project's virtual environment and open the local URL. Verify upload, indexing, chat, source display, the no-answer behavior, responsive layout, and sidebar controls.
8. Give the user the short usage guide from `references/operator-guide.md` and offer targeted UI customization.

## Required behavior

The finished chatbot must:

- accept PDF, DOCX, PPTX, XLSX, CSV, TXT, Markdown, and HTML by default;
- extract text, split it into traceable chunks, create an in-memory local index, and retrieve relevant passages without an embeddings API;
- answer only from uploaded content;
- show file/page/sheet/slide or section evidence used for the answer;
- explicitly say when the documents do not contain the answer;
- avoid persisting uploaded document contents unless the user asks for storage;
- keep secrets outside Git and disclose that only retrieved passages are sent to the selected model;
- remain understandable to a non-programmer.

Read `references/architecture.md` when changing retrieval, file parsing, models, answer grounding, or source rendering.

## User onboarding

After the app works, explain only the essential actions:

1. Open the local or published URL.
2. Open **Kho tài liệu** and upload one or more supported files.
3. Select **Đọc và lập chỉ mục**.
4. Ask questions in the chat box and inspect the cited sources.
5. Use **Xóa phiên làm việc** before switching to an unrelated document set.

Do not overwhelm a non-technical user with architecture details unless requested.

## UI customization

Preserve accessibility and the existing interaction flow. Prefer CSS/HTML animation and lightweight assets over large videos or heavy UI frameworks. Verify desktop and narrow layouts after changes. Respect `prefers-reduced-motion` for non-essential animation.

Useful customization suggestions include:

- logo, colors, organization name, and welcome text;
- animated assistant character;
- suggested starter questions;
- compact or expanded source cards;
- Vietnamese/English language switching;
- per-file limits and accepted formats.

## Publishing and sharing

Only enter this flow after the user asks to publish or share.

1. Read `references/publishing.md`.
2. Remove or ignore `.env`, `.streamlit/secrets.toml`, uploaded files, caches, and virtual environments before Git operations.
3. Run tests and inspect the exact Git diff.
4. Create or reuse the requested GitHub repository, commit, and push. If visibility is unspecified, explain that public sharing normally requires a public repository and obtain a choice before changing an existing private repository's visibility.
5. Prefer Streamlit Community Cloud for this Python/Streamlit template. Complete repository selection, branch, entry point, and deployment through available tools.
6. Set `CHATBOT_MODE="hosted"` and put `OPENAI_API_KEY` in Streamlit Secrets. If secure automated transfer is unavailable, open the exact Secrets screen and ask the user to enter only those values.
7. Wait for the build to finish, inspect logs, open the deployed URL, and verify the app no longer reports a missing key.
8. Return the live URL, repository URL, current privacy state, and any remaining quota or hosting limitations.

Do not claim deployment succeeded until the live page has loaded. Do not make a repository public, purchase a plan, or create billable resources without the user's authorization.

## Cross-client compatibility

This skill follows the Agent Skills folder format and must work from either `~/.codex/skills/agent-chatbot-noi-bo` or `~/.claude/skills/agent-chatbot-noi-bo`. Keep the core workflow in this file and portable Python scripts. `agents/openai.yaml` is optional Codex UI metadata; Claude Code can ignore it.

Read `references/compatibility.md` when installation paths, shell commands, or tool availability differ between Codex and Claude Code.

## Completion criteria

For local creation, finish only when setup, tests, browser preview, ChatGPT sign-in, and one grounded answer succeed. For publishing, finish only when the live URL is reachable and the hosted API-key mode is usable, or report the exact external action still required from the user.
