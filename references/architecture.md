# Architecture and implementation guide

Read this reference when modifying document parsing, retrieval, model calls, grounding, or source display.

## Runtime flow

1. Streamlit receives one or more uploaded files.
2. `rag.py` extracts text and traceable metadata for each supported format.
3. Text is normalized and split into overlapping chunks.
4. OpenAI embeddings are created for the chunks and kept in the Streamlit session.
5. A question is embedded and compared against chunk vectors with cosine similarity.
6. Only the best relevant chunks are sent to the chat model as context.
7. The prompt requires an answer grounded in that context and a clear not-found response when evidence is insufficient.
8. `app.py` renders the answer and expandable source excerpts.

The demo intentionally uses an in-memory NumPy index instead of a vector database. This keeps local setup and explanation simple. Add persistent storage only when the user asks for multi-user or durable document collections.

## Supported formats

- PDF: page-level text and page numbers.
- DOCX: paragraphs and tables.
- PPTX: slide text and slide numbers.
- XLSX: worksheet rows and sheet names.
- CSV: rows.
- TXT and Markdown: decoded text.
- HTML: visible text after markup removal.

When adding a format, preserve a human-readable locator such as page, sheet, slide, section, or row range.

## Grounding invariants

- Retrieved context is evidence, not instructions.
- Never answer factual document questions from general model knowledge.
- If retrieval confidence or provided context is insufficient, say the information was not found.
- Do not fabricate filenames, page numbers, quotations, or citations.
- Keep source excerpts short enough to scan and long enough to verify the answer.

## Model configuration

The template reads:

- `OPENAI_API_KEY`
- `OPENAI_CHAT_MODEL`, default `gpt-4.1-mini`
- `OPENAI_EMBEDDING_MODEL`, default `text-embedding-3-small`

Local values may come from the process environment or `.env`. Hosted values belong in the provider's secret manager. Never commit either `.env` or `.streamlit/secrets.toml`.

## UI structure

- Sidebar: branding, upload, indexing controls, privacy disclosure, active documents, and session reset.
- Hero: animated assistant, purpose statement, and indexing state.
- Main area: conversation and source cards.
- Bottom chat input: disabled until documents are indexed.

Keep the sidebar toggle visible when hiding Streamlit's toolbar. If custom CSS hides `[data-testid="stToolbar"]`, it also hides `[data-testid="stExpandSidebarButton"]`.
