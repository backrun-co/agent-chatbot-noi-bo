# Agent Chatbot Nội Bộ

Skill dành cho Codex và Claude Code, giúp agent tự tạo, cài đặt, tùy chỉnh, hướng dẫn và publish một chatbot hỏi đáp dựa trên tài liệu.

Chatbot mẫu hỗ trợ PDF, Word, PowerPoint, Excel, CSV, TXT, Markdown và HTML; chỉ trả lời theo tài liệu và hiển thị nguồn.

## Hai chế độ sử dụng

- **Local, không API key:** người dùng chọn **Continue with ChatGPT** và sử dụng hạn mức ChatGPT/Codex của chính họ. Chỉ mục tài liệu được tạo trên máy.
- **Publish Streamlit:** ứng dụng dùng `OPENAI_API_KEY` được lưu trong Streamlit Secrets; không đưa key vào mã nguồn.

## Cài cho Codex

macOS/Linux:

```bash
git clone https://github.com/backrun-co/agent-chatbot-noi-bo.git ~/.codex/skills/agent-chatbot-noi-bo
```

Windows PowerShell:

```powershell
git clone https://github.com/backrun-co/agent-chatbot-noi-bo.git "$env:USERPROFILE\.codex\skills\agent-chatbot-noi-bo"
```

## Cài cho Claude Code

macOS/Linux:

```bash
git clone https://github.com/backrun-co/agent-chatbot-noi-bo.git ~/.claude/skills/agent-chatbot-noi-bo
```

Windows PowerShell:

```powershell
git clone https://github.com/backrun-co/agent-chatbot-noi-bo.git "$env:USERPROFILE\.claude\skills\agent-chatbot-noi-bo"
```

Khởi động lại phiên agent nếu skill chưa xuất hiện ngay.

## Cách yêu cầu agent

```text
Hãy dùng agent-chatbot-noi-bo để tạo cho tôi một chatbot hỏi đáp tài liệu, cài đặt đầy đủ và mở bản local cho tôi xem.
```

Sau khi duyệt:

```text
Publish chatbot này lên Streamlit và gửi cho tôi link chia sẻ.
```

Agent sẽ tự thực hiện các bước có thể tự động hóa, chỉ yêu cầu bạn đăng nhập, phê duyệt quyền, nhập secret hoặc xác nhận thay đổi quan trọng khi thực sự cần.

## Tạo project thủ công bằng script

```bash
python scripts/bootstrap.py ./my-document-chatbot
```

Script sẽ sao chép template, tạo `.venv` và cài các thư viện cần thiết.

## Bảo mật

- Không commit `.env` hoặc `.streamlit/secrets.toml`.
- Tài liệu upload được giữ trong phiên làm việc theo mặc định.
- Chỉ mục tìm kiếm được tạo local, không gọi Embeddings API.
- Chỉ các đoạn liên quan được gửi tới model để tạo câu trả lời.
- Token ChatGPT local được lưu ngoài project và không được lấy từ bộ nhớ đăng nhập Codex.

## Giấy phép

MIT
