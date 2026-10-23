# Local mode: ChatGPT Plan without an API key

Read this reference when creating, changing, or troubleshooting local authentication.

## Supported scope

Use OpenAI's open-source **Sign in with ChatGPT** flow only for a local or otherwise eligible open-source runtime. The included template uses a loopback callback on `127.0.0.1`, OAuth Authorization Code with PKCE, a stable per-device host ID, and a dynamically issued client ID.

Do not scrape browser cookies, reuse Codex credential files, expose tokens to Streamlit widgets, or treat `dynamic_agent_client` as the issued client ID.

Official references:

- Registration and sign-in: <https://developers.openai.com/siwc/token-sharing-open-source/sign-in>
- Models and inference: <https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference>
- Preview limitations: <https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations>

## Runtime invariants

- Label the action **Continue with ChatGPT**.
- Use a fresh state, nonce, and PKCE verifier for every authorization attempt.
- Validate callback state, ID-token signature, issuer, audience, expiry, and nonce before saving credentials.
- Require the `chatgpt.tokens.use.direct` granted scope.
- Keep the issued client ID associated with the verified account and reuse it for reauthorization.
- Store profiles outside the project, write atomically, restrict file permissions when supported, and never log token values.
- Refresh the token before expiry and replace rotating refresh tokens together.
- Send model requests to the public Responses API with `store=false` and `stream=true`; treat only `response.completed` as success.
- Send retrieved document passages in the request input. File Search and the Embeddings endpoint are not part of this plan-sharing flow, so retrieval remains local.

## Hosted boundary

Do not present the local dynamic-registration flow as a drop-in authentication method for Streamlit Community Cloud. OpenAI's current documentation scopes this flow to open-source and locally hosted apps; remotely hosted apps require the applicable OpenAI access path. Use hosted API-key mode unless the user has confirmed approved remote-hosted access.
