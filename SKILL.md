---
name: document-chatbot-builder
description: Build, customize, run, explain, and publish a polished Streamlit chatbot that answers only from uploaded PDF, DOCX, PPTX, XLSX, CSV, TXT, Markdown, or HTML documents and cites its sources. Use when a user wants a local document Q&A/RAG chatbot, wants to improve this chatbot's interface, or asks to share or deploy it. Do not use for general-purpose chatbots that are not grounded in user documents.
---

# Document Chatbot Builder

Create a working chatbot, not merely a tutorial. Automate safe local setup and validation; ask the user only for decisions, credentials, permissions, or actions that cannot be completed on their behalf.

## Choose the operating mode

- **New chatbot:** scaffold from `assets/streamlit-rag-template/`, install dependencies, configure, test, and open a local preview.
- **Existing chatbot:** inspect it first, preserve working features and unrelated user changes, then make the requested edits.
- **Customize UI:** keep the dark acid-green design by default, but adapt branding, copy, layout, animation, and supported formats to the user's request. Offer concise customization ideas after the first working version.
- **Publish/share:** when the user requests deployment, carry it through to a verified public or private URL. Do not stop at generic instructions when tools can complete the work.

## New chatbot workflow

1. Select an empty target directory. If the user did not name one, use a short project name such as `document-chatbot` inside the current workspace.
2. Run `python scripts/bootstrap.py <target-directory>`. On Windows, use `py -3.12` or an available Python 3.11+ interpreter when `python` is unavailable.
3. If Python 3.11+ or Git is missing, install it using the platform's normal package manager when permitted. Ask only when administrator approval or an interactive installer is required.
4. Let the bootstrap script copy the template, create `.venv`, upgrade pip, and install `requirements.txt`. Do not recreate these steps manually unless the script reports a concrete failure.
5. Configure credentials without exposing them:
   - Reuse an existing `OPENAI_API_KEY` environment variable when present.
   - Otherwise ask the user to enter a key locally or in the hosting provider's secret manager. Never print, commit, or place the key in a command argument or public file.
   - If the user explicitly wants no API key, explain the quality trade-off and offer a deterministic retrieval-only mode; do not silently claim it is equivalent to an LLM answer.
6. Run `python scripts/check_project.py <target-directory>` and the template tests. Fix failures before previewing.
7. Start Streamlit from the project's virtual environment and open the local URL. Verify upload, indexing, chat, source display, the no-answer behavior, responsive layout, and sidebar controls.
8. Give the user the short usage guide from `references/operator-guide.md` and offer targeted UI customization.

## Required behavior

The finished chatbot must:

- accept PDF, DOCX, PPTX, XLSX, CSV, TXT, Markdown, and HTML by default;
- extract text, split it into traceable chunks, create an in-memory index, and retrieve relevant passages;
- answer only from uploaded content;
- show file/page/sheet/slide or section evidence used for the answer;
- explicitly say when the documents do not contain the answer;
- avoid persisting uploaded document contents unless the user asks for storage;
- keep secrets outside Git and display a clear disclosure when document content is sent to an external model API;
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
6. Put `OPENAI_API_KEY` in Streamlit Secrets. If secure automated transfer is unavailable, open the exact Secrets screen and ask the user to enter only that value.
7. Wait for the build to finish, inspect logs, open the deployed URL, and verify the app no longer reports a missing key.
8. Return the live URL, repository URL, current privacy state, and any remaining quota or hosting limitations.

Do not claim deployment succeeded until the live page has loaded. Do not make a repository public, purchase a plan, or create billable resources without the user's authorization.

## Cross-client compatibility

This skill follows the Agent Skills folder format and must work from either `~/.codex/skills/document-chatbot-builder` or `~/.claude/skills/document-chatbot-builder`. Keep the core workflow in this file and portable Python scripts. `agents/openai.yaml` is optional Codex UI metadata; Claude Code can ignore it.

Read `references/compatibility.md` when installation paths, shell commands, or tool availability differ between Codex and Claude Code.

## Completion criteria

For local creation, finish only when setup, tests, and a browser preview succeed and the user has basic usage instructions. For publishing, finish only when the live URL is reachable and the configured app is usable, or report the exact external action still required from the user.
