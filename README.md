# Agent Chatbot Nội Bộ

Skill dành cho Codex và Claude Code, giúp agent tự tạo, cài đặt, tùy chỉnh, hướng dẫn và publish một chatbot hỏi đáp dựa trên tài liệu.

Chatbot mẫu hỗ trợ PDF, Word, PowerPoint, Excel, CSV, TXT, Markdown và HTML; chỉ trả lời theo tài liệu và hiển thị nguồn.

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
- Nội dung tài liệu được gửi tới OpenAI API để tạo embedding và câu trả lời.

## Giấy phép

MIT
