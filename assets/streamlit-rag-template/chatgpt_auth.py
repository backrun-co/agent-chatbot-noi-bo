"""Đăng nhập ChatGPT Plan cho ứng dụng mã nguồn mở chạy local."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import queue
import secrets
import tempfile
import threading
import time
import uuid
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
import jwt
from openai import OpenAI


APP_NAME = "Agent Chatbot Noi Bo"
RESOURCE = "https://api.openai.com/v1"
DISCOVERY_URL = "https://auth.openai.com/.well-known/openid-configuration"
DYNAMIC_CLIENT_ID = "dynamic_agent_client"
REQUIRED_SCOPE = "chatgpt.tokens.use.direct"
SCOPES = "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct"
CONFIG_DIR = Path(
    os.getenv("AGENT_CHATBOT_CONFIG_DIR", Path.home() / ".agent-chatbot-noi-bo")
).expanduser()
HOST_FILE = CONFIG_DIR / "host.json"
PROFILE_FILE = CONFIG_DIR / "chatgpt-profile.json"


class ChatGPTAuthError(RuntimeError):
    """Lỗi đăng nhập hoặc sử dụng ChatGPT Plan."""


@dataclass(frozen=True)
class ChatGPTSession:
    access_token: str
    email: str
    client_id: str


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ChatGPTAuthError(f"Không đọc được thông tin đăng nhập: {error}") from error


def _write_private_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _discovery() -> dict:
    response = httpx.get(DISCOVERY_URL, timeout=20)
    response.raise_for_status()
    return response.json()


def _host_id() -> str:
    try:
        saved = _read_json(HOST_FILE)
    except ChatGPTAuthError:
        saved = {}
    host_id = str(saved.get("ext_agent_host_id", ""))
    if host_id.startswith("urn:uuid:"):
        return host_id
    host_id = f"urn:uuid:{uuid.uuid4()}"
    _write_private_json(HOST_FILE, {"ext_agent_host_id": host_id})
    return host_id


def create_pkce_pair() -> tuple[str, str]:
    """Tạo PKCE verifier và S256 challenge không có padding."""
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _callback_listener() -> tuple[ThreadingHTTPServer, queue.Queue[dict[str, str]], str]:
    result: queue.Queue[dict[str, str]] = queue.Queue(maxsize=1)

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - tên hook của BaseHTTPRequestHandler
            parsed = urlparse(self.path)
            if parsed.path != "/auth/callback":
                self.send_error(404)
                return
            values = {key: items[0] for key, items in parse_qs(parsed.query).items() if items}
            if result.empty():
                result.put(values)
            body = (
                "<!doctype html><meta charset='utf-8'><title>Đã kết nối</title>"
                "<style>body{font-family:system-ui;background:#080907;color:#f4f6ee;"
                "display:grid;place-items:center;min-height:100vh;margin:0}"
                "main{max-width:520px;padding:36px;border:1px solid #dfff3655;"
                "border-radius:18px;background:#10120d}b{color:#dfff36}</style>"
                "<main><h2><b>Đã kết nối ChatGPT</b></h2>"
                "<p>Bạn có thể đóng tab này và quay lại chatbot.</p></main>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), CallbackHandler)
    port = int(server.server_address[1])
    redirect_uri = f"http://127.0.0.1:{port}/auth/callback"
    return server, result, redirect_uri


def _verify_identity(id_token: str, client_id: str, nonce: str, discovery: dict) -> dict:
    try:
        jwks = jwt.PyJWKClient(discovery["jwks_uri"])
        signing_key = jwks.get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=discovery["issuer"],
        )
    except Exception as error:
        raise ChatGPTAuthError(f"Không xác minh được danh tính ChatGPT: {error}") from error
    if claims.get("nonce") != nonce:
        raise ChatGPTAuthError("Nonce đăng nhập không khớp.")
    return claims


def sign_in(timeout_seconds: int = 300) -> ChatGPTSession:
    """Mở trình duyệt, đăng ký OAuth client local và lưu profile đã xác minh."""
    discovery = _discovery()
    try:
        existing = _read_json(PROFILE_FILE)
    except ChatGPTAuthError:
        existing = {}
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier, challenge = create_pkce_pair()
    server, callback_result, redirect_uri = _callback_listener()
    client_id = str(existing.get("client_id") or DYNAMIC_CLIENT_ID)

    parameters = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "resource": RESOURCE,
        "state": state,
        "nonce": nonce,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "ext_agent_host_id": _host_id(),
    }
    if client_id == DYNAMIC_CLIENT_ID:
        parameters["agent_name_hint"] = APP_NAME
    else:
        if existing.get("id_token"):
            parameters["id_token_hint"] = str(existing["id_token"])
        if existing.get("email"):
            parameters["login_hint"] = str(existing["email"])

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    authorization_url = f'{discovery["authorization_endpoint"]}?{urlencode(parameters)}'
    webbrowser.open(authorization_url, new=2)
    try:
        callback = callback_result.get(timeout=timeout_seconds)
    except queue.Empty as error:
        raise ChatGPTAuthError("Hết thời gian chờ đăng nhập ChatGPT.") from error
    finally:
        server.shutdown()
        server.server_close()

    if callback.get("state") != state:
        raise ChatGPTAuthError("State đăng nhập không khớp.")
    if callback.get("error"):
        raise ChatGPTAuthError(f'ChatGPT từ chối đăng nhập: {callback["error"]}')
    code = callback.get("code", "")
    issued_client_id = callback.get("client_id") or client_id
    if not code:
        raise ChatGPTAuthError("Không nhận được authorization code.")
    if client_id == DYNAMIC_CLIENT_ID and issued_client_id == DYNAMIC_CLIENT_ID:
        raise ChatGPTAuthError("ChatGPT chưa trả về client ID đã đăng ký.")
    if client_id != DYNAMIC_CLIENT_ID and issued_client_id != client_id:
        raise ChatGPTAuthError("Client ID trả về không khớp profile đã chọn.")

    response = httpx.post(
        discovery["token_endpoint"],
        data={
            "grant_type": "authorization_code",
            "client_id": issued_client_id,
            "code": code,
            "code_verifier": verifier,
            "redirect_uri": redirect_uri,
            "resource": RESOURCE,
        },
        timeout=30,
    )
    if response.is_error:
        try:
            error_code = str(response.json().get("error", "oauth_exchange_failed"))
        except ValueError:
            error_code = "oauth_exchange_failed"
        raise ChatGPTAuthError(
            f"Không đổi được OAuth code ({response.status_code}, {error_code})."
        )
    tokens = response.json()
    id_token = str(tokens.get("id_token", ""))
    if not id_token:
        raise ChatGPTAuthError("Token response thiếu ID token.")
    claims = _verify_identity(id_token, issued_client_id, nonce, discovery)
    granted_scopes = str(tokens.get("scope", callback.get("scope", ""))).split()
    if REQUIRED_SCOPE not in granted_scopes:
        raise ChatGPTAuthError("Bạn chưa cho phép ứng dụng sử dụng ChatGPT Plan.")

    now = int(time.time())
    profile = {
        "email": str(claims.get("email", "Tài khoản ChatGPT")),
        "issuer": str(claims.get("iss", "")),
        "subject": str(claims.get("sub", "")),
        "client_id": issued_client_id,
        "ext_agent_host_id": parameters["ext_agent_host_id"],
        "id_token": id_token,
        "access_token": str(tokens.get("access_token", "")),
        "refresh_token": str(tokens.get("refresh_token", "")),
        "token_type": str(tokens.get("token_type", "Bearer")),
        "expires_in": int(tokens.get("expires_in", 3600)),
        "expires_at": now + int(tokens.get("expires_in", 3600)),
        "scopes": granted_scopes,
        "saved_at": now,
    }
    if not profile["access_token"] or not profile["refresh_token"]:
        raise ChatGPTAuthError("Token response chưa đủ access token và refresh token.")
    _write_private_json(PROFILE_FILE, profile)
    return ChatGPTSession(profile["access_token"], profile["email"], issued_client_id)


def _refresh(profile: dict) -> dict:
    discovery = _discovery()
    response = httpx.post(
        discovery["token_endpoint"],
        data={
            "grant_type": "refresh_token",
            "client_id": profile["client_id"],
            "refresh_token": profile["refresh_token"],
            "resource": RESOURCE,
        },
        timeout=30,
    )
    if response.is_error:
        raise ChatGPTAuthError("Phiên ChatGPT đã hết hạn. Hãy đăng nhập lại.")
    tokens = response.json()
    now = int(time.time())
    profile.update(
        {
            "access_token": str(tokens.get("access_token", "")),
            "refresh_token": str(tokens.get("refresh_token", profile["refresh_token"])),
            "expires_in": int(tokens.get("expires_in", 3600)),
            "expires_at": now + int(tokens.get("expires_in", 3600)),
            "saved_at": now,
        }
    )
    if tokens.get("scope"):
        profile["scopes"] = str(tokens["scope"]).split()
    if not profile["access_token"] or REQUIRED_SCOPE not in profile.get("scopes", []):
        raise ChatGPTAuthError("Phiên mới không có quyền sử dụng ChatGPT Plan.")
    _write_private_json(PROFILE_FILE, profile)
    return profile


def get_session() -> ChatGPTSession | None:
    """Trả về phiên local còn hiệu lực; tự refresh khi gần hết hạn."""
    profile = _read_json(PROFILE_FILE)
    if not profile:
        return None
    if REQUIRED_SCOPE not in profile.get("scopes", []):
        raise ChatGPTAuthError("Profile chưa được cấp quyền sử dụng ChatGPT Plan.")
    if int(profile.get("expires_at", 0)) <= int(time.time()) + 60:
        profile = _refresh(profile)
    return ChatGPTSession(
        access_token=str(profile["access_token"]),
        email=str(profile.get("email", "Tài khoản ChatGPT")),
        client_id=str(profile["client_id"]),
    )


def list_models(session: ChatGPTSession) -> list[tuple[str, str]]:
    """Lấy catalog model được hiển thị cho tài khoản đã đăng nhập."""
    response = httpx.get(
        f"{RESOURCE}/models",
        headers={"Authorization": f"Bearer {session.access_token}"},
        timeout=30,
    )
    if response.is_error:
        raise ChatGPTAuthError("Không tải được danh sách model của tài khoản ChatGPT.")
    payload = response.json()
    models = payload.get("models", payload.get("data", []))
    choices = []
    for item in models:
        if item.get("visibility", "list") != "list":
            continue
        slug = str(item.get("slug") or item.get("id") or "")
        if slug:
            choices.append((slug, str(item.get("display_name") or slug)))
    return choices


def create_client(session: ChatGPTSession) -> OpenAI:
    return OpenAI(api_key=session.access_token, base_url=RESOURCE, max_retries=0)


def sign_out() -> None:
    """Thu hồi refresh token khi có thể rồi xóa profile cục bộ."""
    try:
        profile = _read_json(PROFILE_FILE)
    except ChatGPTAuthError:
        profile = {}
    if profile.get("refresh_token") and profile.get("client_id"):
        try:
            discovery = _discovery()
            endpoint = discovery.get("revocation_endpoint")
            if endpoint:
                httpx.post(
                    endpoint,
                    data={
                        "token": profile["refresh_token"],
                        "token_type_hint": "refresh_token",
                        "client_id": profile["client_id"],
                    },
                    timeout=20,
                )
        except Exception:
            pass
    if PROFILE_FILE.exists():
        PROFILE_FILE.unlink()
