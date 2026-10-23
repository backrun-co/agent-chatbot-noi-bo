# Publishing guide

Read this reference only when the user asks to publish or share the chatbot.

## Preferred path: Streamlit Community Cloud

This is the simplest host for the included Python application.

1. Verify `.gitignore` excludes `.env`, `.streamlit/secrets.toml`, `.venv`, caches, and uploaded documents.
2. Run the project checks and tests.
3. Initialize Git if needed, create a GitHub repository, and push the reviewed commit.
4. Sign in to Streamlit Community Cloud and connect the intended GitHub account.
5. Deploy with repository, branch, `app.py`, and a readable available subdomain.
6. In App settings → Secrets, add:

```toml
CHATBOT_MODE = "hosted"
OPENAI_API_KEY = "..."
OPENAI_CHAT_MODEL = "gpt-4.1-mini"
```

Never put the API key value in Git, chat output, screenshots, logs, or shell arguments. Do not deploy with `CHATBOT_MODE="local"`: the loopback OAuth flow is intended for local/open-source runtimes, not an ordinary shared Streamlit Cloud instance.

7. Wait for dependencies to install and the app to start. Inspect build logs when the page fails.
8. Verify the missing-key warning is gone and the upload control is enabled.

Community Cloud instances may sleep, restart, and lose in-memory indexes. Users should expect to upload and index documents again after a restart.

## Vercel and Cloudflare

Do not deploy the unchanged Streamlit server to Vercel or Cloudflare Pages. They are better suited to a separately designed frontend plus API/serverless backend. Offer that migration only when the user wants a production architecture and accepts the additional complexity.

Cloudflare Workers AI can reduce model cost but still requires an account and server-side credentials. It is not equivalent to a credential-free app.

## Publication boundaries

- A request to publish authorizes ordinary deployment steps for the named project, not unrelated account changes or paid upgrades.
- Ask the user only for interactive login, OAuth approval, secret entry, CAPTCHA, billing approval, or a material visibility choice that cannot be inferred safely.
- Prefer a public repository only when public sharing requires it and the user accepts public source code.
- Report the final URL and the repository visibility explicitly.
