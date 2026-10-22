# Basic user guide

## Start locally

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS or Linux:

```bash
./.venv/bin/python -m streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically.

## Use the chatbot

1. Open the left sidebar with the `»` button.
2. Upload one or more supported documents.
3. Select **Đọc và lập chỉ mục** and wait for the ready status.
4. Ask a specific question in the chat input.
5. Open the source section below the answer to verify the supporting excerpt.
6. Select **Xóa phiên làm việc** before starting with an unrelated document set.

## Common issues

- **Missing API key:** add `OPENAI_API_KEY` to the local environment or `.env`; on Streamlit Cloud use App settings → Secrets.
- **Index button disabled:** select at least one supported file first.
- **No answer found:** ask a more specific question or confirm the information exists in the uploaded files.
- **Scanned PDF:** the basic template does not include OCR; convert it to searchable text or add an OCR provider.
- **Sidebar button missing:** ensure custom CSS does not hide the entire Streamlit toolbar.
