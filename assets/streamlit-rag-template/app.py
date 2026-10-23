"""Giao diện Streamlit cho demo chatbot hỏi đáp tài liệu nội bộ."""

from __future__ import annotations

import html
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from chatgpt_auth import (
    create_client,
    get_session,
    list_models,
    sign_in,
    sign_out,
)
from rag import Chunk, NOT_FOUND_ANSWER, answer_question, create_index, extract_document, retrieve


load_dotenv()

MAX_FILES = 5
MAX_FILE_SIZE = 10 * 1024 * 1024
SUPPORTED_UPLOAD_TYPES = ["pdf", "docx", "pptx", "xlsx", "csv", "txt", "md", "html", "htm"]
CHATBOT_MODE = os.getenv("CHATBOT_MODE", "local").strip().lower()
HOSTED_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
if CHATBOT_MODE not in {"local", "hosted"}:
    CHATBOT_MODE = "local"

st.set_page_config(
    page_title="Trợ lý tài liệu nội bộ",
    page_icon="◈",
    layout="wide",
)

st.markdown(
    """
    <style>
      :root {
        --acid: #dfff36;
        --acid-soft: #b9d91e;
        --ink: #070806;
        --panel: #0e100c;
        --text: #f5f7ee;
        --muted: #92998a;
      }
      html, body, [class*="css"] { color-scheme: dark; }
      [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(circle at 78% 6%, rgba(205, 231, 0, .16), transparent 24rem),
          linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px),
          #070806;
        background-size: auto, 38px 38px, 38px 38px, auto;
        color: var(--text);
      }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stDecoration"] { display: none; }
      [data-testid="stToolbar"] { display: flex !important; }
      [data-testid="stToolbar"] button:not([data-testid="stExpandSidebarButton"]) {
        display: none !important;
      }
      [data-testid="stExpandSidebarButton"] {
        display: inline-flex !important;
        color: var(--acid) !important;
        background: rgba(14, 16, 12, .92) !important;
        border: 1px solid rgba(223, 255, 54, .28) !important;
        border-radius: 10px !important;
        margin: .65rem !important;
        width: 2.35rem !important;
        height: 2.35rem !important;
        box-shadow: 0 0 18px rgba(223, 255, 54, .12) !important;
      }
      [data-testid="stSidebar"] {
        background: rgba(9, 10, 8, .97);
        border-right: 1px solid rgba(255,255,255,.07);
      }
      [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
      .block-container { max-width: 960px; padding-top: 1.2rem; padding-bottom: 7rem; }

      .side-brand, .top-brand { display: flex; align-items: center; gap: .65rem; }
      .side-brand { margin: 0 0 2rem; }
      .brand-mark {
        display: inline-flex; align-items: center; justify-content: center;
        width: 30px; height: 30px; border-radius: 9px;
        color: #080900; background: var(--acid); font-weight: 900;
        box-shadow: 0 0 22px rgba(223,255,54,.28);
      }
      .brand-name { color: var(--text); font-size: 1rem; font-weight: 760; letter-spacing: -.02em; }
      .brand-name small { color: var(--muted); font-size: .72rem; font-weight: 500; margin-left: .35rem; }
      .sidebar-label, .eyebrow {
        color: var(--muted); font-size: .71rem; font-weight: 700;
        letter-spacing: .13em; text-transform: uppercase;
      }
      .sidebar-label { margin: 0 0 .6rem; }
      .privacy-note { color: #70776b; font-size: .75rem; line-height: 1.5; margin: .8rem 0; }

      .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; }
      .model-badge {
        display: inline-flex; align-items: center; gap: .45rem;
        color: #a4aa9c; font-size: .74rem; padding: .42rem .7rem;
        border: 1px solid rgba(255,255,255,.08); border-radius: 999px;
        background: rgba(14,16,12,.72);
      }
      .model-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--acid); box-shadow: 0 0 10px var(--acid); }

      .hero-shell { text-align: center; padding: 2.1rem 0 1.35rem; transition: padding .2s ease; }
      .hero-shell.compact { padding: 1rem 0 .5rem; }
      .agent-stage {
        width: 112px; height: 104px; margin: 0 auto 1.2rem; position: relative;
        display: grid; place-items: center; transition: width .2s ease, height .2s ease, margin .2s ease;
      }
      .agent-bot {
        width: 100px; height: 88px; position: relative; transform-origin: 50% 60%;
        animation: agent-float 3.4s ease-in-out infinite;
        filter: drop-shadow(0 12px 22px rgba(191, 222, 0, .22));
      }
      .agent-halo {
        position: absolute; inset: 5px 0 0; border: 1px solid rgba(223,255,54,.18);
        border-radius: 50%; transform: rotate(18deg) scaleY(.64);
        animation: agent-orbit 7s linear infinite;
      }
      .agent-halo::after {
        content: ""; position: absolute; width: 6px; height: 6px; top: 7px; right: 12px;
        border-radius: 50%; background: var(--acid); box-shadow: 0 0 12px var(--acid);
      }
      .agent-antenna {
        position: absolute; z-index: 3; width: 2px; height: 17px; left: 49px; top: 0;
        background: linear-gradient(rgba(223,255,54,.25), var(--acid));
      }
      .agent-antenna::before {
        content: ""; position: absolute; width: 9px; height: 9px; left: -3.5px; top: -5px;
        border-radius: 50%; background: var(--acid); box-shadow: 0 0 14px rgba(223,255,54,.9);
        animation: agent-ping 1.8s ease-in-out infinite;
      }
      .agent-head {
        position: absolute; z-index: 2; width: 82px; height: 62px; left: 9px; top: 16px;
        border: 1px solid rgba(223,255,54,.72); border-radius: 25px 25px 29px 29px;
        background: linear-gradient(145deg, #20251a 0%, #0d100b 58%, #050604 100%);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.12), 0 0 28px rgba(199,231,0,.18);
      }
      .agent-head::before, .agent-head::after {
        content: ""; position: absolute; width: 8px; height: 25px; top: 18px;
        background: #151a10; border: 1px solid rgba(223,255,54,.32);
      }
      .agent-head::before { left: -9px; border-radius: 7px 2px 2px 7px; }
      .agent-head::after { right: -9px; border-radius: 2px 7px 7px 2px; }
      .agent-face {
        position: absolute; inset: 9px; border-radius: 18px;
        background: radial-gradient(circle at 50% 0, rgba(223,255,54,.11), transparent 68%), #080a07;
        border: 1px solid rgba(255,255,255,.055); overflow: hidden;
      }
      .agent-eye {
        position: absolute; width: 12px; height: 9px; top: 15px; border-radius: 50%;
        background: var(--acid); box-shadow: 0 0 11px rgba(223,255,54,.85);
        animation: agent-blink 4.8s infinite;
      }
      .agent-eye.left { left: 16px; }
      .agent-eye.right { right: 16px; }
      .agent-mouth {
        position: absolute; width: 24px; height: 4px; left: 50%; bottom: 11px;
        transform: translateX(-50%); border-radius: 999px;
        background: linear-gradient(90deg, transparent, var(--acid), transparent);
        opacity: .7; animation: agent-talk 2.2s ease-in-out infinite;
      }
      .agent-shadow {
        position: absolute; width: 56px; height: 8px; left: 22px; bottom: -1px;
        border-radius: 50%; background: rgba(0,0,0,.55); filter: blur(4px);
        animation: agent-shadow 3.4s ease-in-out infinite;
      }
      .hero-shell.compact .agent-stage { width: 76px; height: 68px; margin-bottom: .7rem; }
      .hero-shell.compact .agent-bot { scale: .68; }
      @keyframes agent-float {
        0%, 100% { transform: translateY(1px) rotate(-1deg); }
        50% { transform: translateY(-7px) rotate(1deg); }
      }
      @keyframes agent-orbit { to { transform: rotate(378deg) scaleY(.64); } }
      @keyframes agent-ping { 0%, 100% { scale: .82; opacity: .62; } 50% { scale: 1.14; opacity: 1; } }
      @keyframes agent-blink { 0%, 44%, 48%, 100% { transform: scaleY(1); } 46% { transform: scaleY(.12); } }
      @keyframes agent-talk { 0%, 100% { width: 18px; opacity: .48; } 50% { width: 28px; opacity: .92; } }
      @keyframes agent-shadow { 0%, 100% { transform: scaleX(1); opacity: .48; } 50% { transform: scaleX(.78); opacity: .28; } }
      @media (prefers-reduced-motion: reduce) {
        .agent-bot, .agent-halo, .agent-antenna::before, .agent-eye, .agent-mouth, .agent-shadow { animation: none !important; }
      }
      .eyebrow { color: var(--acid-soft); margin-bottom: .7rem; }
      .hero-title {
        color: var(--text); font-size: clamp(2.3rem, 5vw, 4.4rem); line-height: .98;
        font-weight: 800; margin: 0 auto .9rem; letter-spacing: -.055em; max-width: 820px;
      }
      .hero-title span { color: var(--acid); }
      .hero-shell.compact .hero-title { font-size: clamp(1.9rem, 3.5vw, 2.8rem); }
      .hero-copy { color: var(--muted); font-size: .98rem; max-width: 560px; line-height: 1.65; margin: 0 auto 1rem; }
      .status-pill {
        display: inline-flex; align-items: center; gap: .55rem;
        background: rgba(17,19,14,.88); border: 1px solid rgba(255,255,255,.08);
        border-radius: 999px; padding: .48rem .78rem; color: #b7bdaf; font-size: .78rem;
      }
      .status-pill.ready { border-color: rgba(223,255,54,.22); color: #ddeaaf; }
      .status-icon { width: 7px; height: 7px; border-radius: 50%; background: #676d61; }
      .ready .status-icon { background: var(--acid); box-shadow: 0 0 10px rgba(223,255,54,.8); }
      .empty-hint { color: #6f756a; font-size: .82rem; text-align: center; margin: .55rem 0 1.2rem; }

      [data-testid="stFileUploaderDropzone"] {
        background: #0d0f0b; border: 1px dashed rgba(223,255,54,.26); border-radius: 16px;
        padding: .45rem;
      }
      [data-testid="stFileUploaderDropzone"]:hover { border-color: rgba(223,255,54,.55); }
      [data-testid="stFileUploaderDropzone"] button {
        background: #181b14 !important; border: 1px solid rgba(255,255,255,.09) !important;
        color: #e9ede1 !important; border-radius: 10px !important;
      }
      [data-testid="stFileUploaderDropzoneInstructions"] > div > span { color: #b7bdaf; }
      [data-testid="stFileUploaderDropzoneInstructions"] small { color: #666d61; }

      .stButton > button[kind="primary"] {
        background: var(--acid); color: #0b0c06; border: 0; border-radius: 12px;
        font-weight: 750; min-height: 2.8rem; box-shadow: 0 0 22px rgba(223,255,54,.12);
      }
      .stButton > button[kind="primary"]:hover { background: #ebff72; color: #070806; }
      .stButton > button:disabled,
      .stButton > button[kind="primary"]:disabled {
        background: #151711 !important; color: #596052 !important;
        border: 1px solid rgba(255,255,255,.055) !important; box-shadow: none !important;
      }
      .stButton > button:not([kind="primary"]) {
        background: #11130f; color: #aeb5a6; border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
      }
      .doc-card {
        margin: .55rem 0; padding: .72rem .8rem; border-radius: 12px;
        background: #11130f; border: 1px solid rgba(255,255,255,.06);
      }
      .doc-name { color: #e8ebdf; font-size: .82rem; font-weight: 650; overflow-wrap: anywhere; }
      .doc-meta { color: #737a6e; font-size: .7rem; margin-top: .2rem; }

      [data-testid="stChatMessage"] {
        background: rgba(14,16,12,.9); border: 1px solid rgba(255,255,255,.07);
        border-radius: 18px; padding: .55rem .75rem; margin: .7rem 0;
        box-shadow: 0 14px 35px rgba(0,0,0,.2);
      }
      [data-testid="stChatMessageAvatarUser"] { background: #25281f; }
      [data-testid="stChatMessageAvatarAssistant"] { background: rgba(223,255,54,.13); }
      [data-testid="stChatInput"] {
        background: #090a08; border: 1px solid rgba(223,255,54,.18); border-radius: 20px;
        box-shadow: 0 18px 55px rgba(0,0,0,.55), 0 0 35px rgba(223,255,54,.045);
      }
      [data-testid="stChatInput"]:focus-within { border-color: rgba(223,255,54,.46); }
      [data-testid="stChatInput"] textarea { color: #edf0e7; }
      [data-testid="stChatInputSubmitButton"] { color: var(--acid); }
      [data-testid="stBottomBlockContainer"] { background: linear-gradient(transparent, #070806 38%); padding-top: 2rem; }
      [data-testid="stExpander"] { background: #0b0d09; border: 1px solid rgba(255,255,255,.07); border-radius: 13px; }
      .source-meta { color: var(--acid-soft); font-weight: 700; font-size: .78rem; }
      .source-text { color: #a9afa2; line-height: 1.62; font-size: .88rem; margin-top: .35rem; }
      [data-testid="stAlert"] { border-radius: 14px; background: #11130f; color: #c3c9ba; }
      hr { border-color: rgba(255,255,255,.07) !important; }
      footer { visibility: hidden; }

      @media (max-width: 760px) {
        .block-container { padding-top: .8rem; }
        .topbar { margin-bottom: 0; }
        .model-badge { display: none; }
        .hero-shell { padding-top: 1.2rem; }
        .agent-stage { width: 88px; height: 80px; }
        .hero-title { font-size: 2.6rem; }
        .hero-copy { font-size: .9rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    defaults = {
        "chunks": [],
        "index": None,
        "messages": [],
        "documents": [],
        "index_signature": None,
        "plan_models": [],
        "plan_model": None,
        "auth_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_knowledge() -> None:
    st.session_state.chunks = []
    st.session_state.index = None
    st.session_state.messages = []
    st.session_state.documents = []
    st.session_state.index_signature = None


def get_hosted_client() -> OpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return OpenAI(api_key=api_key) if api_key else None


def upload_signature(files: list) -> tuple | None:
    if not files:
        return None
    return tuple((item.name, item.size, hash(item.getvalue())) for item in files)


def show_sources(sources: list[dict]) -> None:
    if not sources:
        st.caption("Không có đoạn tài liệu đủ liên quan để làm nguồn.")
        return
    with st.expander(f"Xem {len(sources)} đoạn nguồn đã dùng"):
        for index, source in enumerate(sources, start=1):
            safe_filename = html.escape(source["filename"])
            safe_text = html.escape(source["text"])
            safe_location = html.escape(source.get("location") or f'Trang {source.get("page", "?")}')
            st.markdown(
                f'<div class="source-meta">Nguồn {index} · {safe_filename} · {safe_location}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="source-text">{safe_text}</div>', unsafe_allow_html=True)
            if index < len(sources):
                st.divider()


init_state()
client: OpenAI | None = None
active_model: str | None = None
local_session = None

if CHATBOT_MODE == "local":
    try:
        local_session = get_session()
    except Exception as error:
        st.session_state.plan_models = []
        st.session_state.plan_model = None
        st.session_state.auth_error = str(error)
else:
    client = get_hosted_client()
    active_model = HOSTED_CHAT_MODEL

with st.sidebar:
    st.markdown(
        '<div class="side-brand"><span class="brand-mark">◈</span><span class="brand-name">DocQuery</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-label">Kết nối AI</div>', unsafe_allow_html=True)
    if CHATBOT_MODE == "local":
        if local_session is None:
            st.info("Chế độ local · dùng hạn mức ChatGPT/Codex, không cần API key.")
            if st.session_state.get("auth_error"):
                st.warning(st.session_state.auth_error)
            if st.button("Continue with ChatGPT", type="primary", use_container_width=True):
                with st.spinner("Đang mở trang đăng nhập ChatGPT…"):
                    try:
                        local_session = sign_in()
                        st.session_state.plan_models = list_models(local_session)
                        st.session_state.plan_model = None
                        st.session_state.auth_error = None
                        st.rerun()
                    except Exception as error:
                        st.session_state.auth_error = str(error)
                        st.rerun()
        else:
            st.success(f"Đã kết nối · {local_session.email}")
            try:
                if not st.session_state.plan_models:
                    st.session_state.plan_models = list_models(local_session)
                choices = st.session_state.plan_models
                if not choices:
                    st.warning("Tài khoản chưa có model phù hợp.")
                else:
                    labels = {slug: label for slug, label in choices}
                    slugs = [slug for slug, _ in choices]
                    selected = st.session_state.plan_model
                    if selected not in slugs:
                        selected = slugs[0]
                    active_model = st.selectbox(
                        "Model ChatGPT",
                        slugs,
                        index=slugs.index(selected),
                        format_func=lambda slug: labels[slug],
                    )
                    st.session_state.plan_model = active_model
                    client = create_client(local_session)
            except Exception as error:
                st.warning(f"Không tải được model: {error}")
            if st.button("Ngắt kết nối ChatGPT", use_container_width=True):
                sign_out()
                st.session_state.plan_models = []
                st.session_state.plan_model = None
                st.rerun()
    else:
        st.caption(f"Chế độ publish · {HOSTED_CHAT_MODEL}")
        if client is None:
            st.warning("Chưa có OPENAI_API_KEY trong môi trường hoặc Streamlit Secrets.")
        else:
            st.success("API key đã được cấu hình an toàn.")

    st.markdown(
        '<div class="sidebar-label" style="margin-top:1.4rem">Kho tài liệu</div>',
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Tải tài liệu",
        type=SUPPORTED_UPLOAD_TYPES,
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="privacy-note">● Chỉ mục được tạo trên máy. Chỉ các đoạn liên quan '
        'được gửi tới model để tạo câu trả lời.</div>',
        unsafe_allow_html=True,
    )

    signature = upload_signature(uploaded_files)
    can_index = bool(uploaded_files)
    if st.button("Đọc và lập chỉ mục", type="primary", use_container_width=True, disabled=not can_index):
        if len(uploaded_files) > MAX_FILES:
            st.error(f"Chỉ được tải tối đa {MAX_FILES} tệp.")
        elif any(item.size > MAX_FILE_SIZE for item in uploaded_files):
            st.error("Có tệp vượt quá giới hạn 10 MB.")
        else:
            with st.spinner("Đang đọc, chia nhỏ và lập chỉ mục…"):
                try:
                    all_chunks: list[Chunk] = []
                    documents: list[dict] = []
                    for item in uploaded_files:
                        file_chunks, summary = extract_document(item.getvalue(), item.name)
                        all_chunks.extend(file_chunks)
                        documents.append(
                            {"name": item.name, "summary": summary, "chunks": len(file_chunks)}
                        )

                    if not all_chunks:
                        st.error("Không trích được văn bản. Tệp có thể rỗng, bị hỏng hoặc là PDF scan cần OCR.")
                    else:
                        lexical_index = create_index([chunk.text for chunk in all_chunks])
                        st.session_state.chunks = all_chunks
                        st.session_state.index = lexical_index
                        st.session_state.documents = documents
                        st.session_state.messages = []
                        st.session_state.index_signature = signature
                        st.success(f"Đã sẵn sàng: {len(all_chunks)} đoạn từ {len(documents)} tệp.")
                except Exception as error:
                    st.error(f"Không thể xử lý tài liệu: {error}")

    if st.session_state.documents:
        st.markdown(
            '<div class="sidebar-label" style="margin-top:1.4rem">Tài liệu đang dùng</div>',
            unsafe_allow_html=True,
        )
        for document in st.session_state.documents:
            st.markdown(
                f'<div class="doc-card"><div class="doc-name">{html.escape(document["name"])}</div>'
                f'<div class="doc-meta">{html.escape(document["summary"])} · {document["chunks"]} đoạn chỉ mục</div></div>',
                unsafe_allow_html=True,
            )
        if st.button("Xóa phiên làm việc", use_container_width=True):
            clear_knowledge()
            st.rerun()

hero_class = "hero-shell compact" if st.session_state.messages else "hero-shell"
if st.session_state.chunks:
    status_html = (
        f'<div class="status-pill ready"><span class="status-icon"></span>'
        f'Đã sẵn sàng · {len(st.session_state.chunks)} đoạn được lập chỉ mục</div>'
    )
else:
    status_html = (
        '<div class="status-pill"><span class="status-icon"></span>Chưa có tài liệu</div>'
        '<div class="empty-hint">Tải PDF, Word, PowerPoint, Excel hoặc tệp văn bản để bắt đầu</div>'
    )

st.markdown(
    f'<section class="{hero_class}">'
    '<div class="agent-stage" aria-hidden="true">'
    '<div class="agent-bot"><span class="agent-halo"></span>'
    '<span class="agent-antenna"></span><span class="agent-shadow"></span>'
    '<div class="agent-head"><div class="agent-face">'
    '<span class="agent-eye left"></span><span class="agent-eye right"></span>'
    '<span class="agent-mouth"></span></div></div></div></div>'
    '<div class="eyebrow">Trợ lý tài liệu nội bộ</div>'
    '<div class="hero-title">Hỏi tài liệu.<br><span>Nhận câu trả lời có nguồn.</span></div>'
    '<div class="hero-copy">Hỗ trợ PDF, Word, PowerPoint, Excel và tệp văn bản. Chỉ trả lời từ nội dung bạn cung cấp.</div>'
    f'{status_html}</section>',
    unsafe_allow_html=True,
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            show_sources(message.get("sources", []))

question = st.chat_input(
    "Hỏi về chính sách, quy trình, số liệu trong tài liệu…",
    disabled=not bool(st.session_state.chunks) or client is None or active_model is None,
)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm trong tài liệu…"):
            try:
                results = retrieve(
                    question,
                    st.session_state.chunks,
                    st.session_state.index,
                    top_k=4,
                )

                answer = answer_question(
                    client,
                    question,
                    results,
                    active_model,
                    recent_messages=st.session_state.messages[:-1],
                )
                sources = []
                if answer.strip() != NOT_FOUND_ANSWER:
                    sources = [
                        {
                            "filename": item.chunk.filename,
                            "location": item.chunk.source_location,
                            "text": item.chunk.text,
                            "score": item.score,
                        }
                        for item in results
                    ]
                st.markdown(answer)
                show_sources(sources)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except Exception as error:
                st.error(f"Không thể trả lời lúc này: {error}")
