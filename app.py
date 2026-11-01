from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import streamlit as st

from providers import ProviderError, chat_completion
from storage import ChatStore

APP_TITLE = "VibNest"
DB_PATH = os.getenv("DARKGPT_DB_PATH", "darkgpt.sqlite3")

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { color-scheme: dark; }
      .stApp { background: #090d16; }
      [data-testid="stHeader"] { background: rgba(9,13,22,.86); }
      [data-testid="stSidebar"] { background: #101827; border-right: 1px solid #202c40; }
      .block-container { max-width: 1120px; padding-top: 1.4rem; padding-bottom: 5rem; }
      .brand { display:flex; align-items:center; gap:.65rem; margin-bottom:.15rem; }
      .brand-mark { width:2.2rem; height:2.2rem; display:grid; place-items:center; border-radius:.8rem;
        background:linear-gradient(135deg,#5b7cff,#9b5cff); color:white; font-size:1.2rem; }
      .brand-name { font-size:1.45rem; font-weight:800; letter-spacing:-.04em; color:#f4f7ff; }
      .brand-sub { color:#8391a8; font-size:.82rem; margin:.15rem 0 1.2rem 2.9rem; }
      .hero { padding:1.2rem 1.3rem; border:1px solid #24324a; border-radius:1.1rem;
        background:linear-gradient(120deg,rgba(91,124,255,.13),rgba(155,92,255,.07)); margin-bottom:1.2rem; }
      .hero h1 { font-size:1.65rem; margin:0 0 .3rem 0; color:#f2f5ff; }
      .hero p { color:#a6b2c7; margin:0; font-size:.93rem; }
      .small-muted { color:#8492a8; font-size:.8rem; }
      div[data-testid="stChatMessage"] { background:#111a29; border:1px solid #223149; border-radius:1rem; padding:.8rem 1rem; }
      .stButton>button { border-radius:.65rem; }
      .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] { border-radius:.65rem; }
      [data-testid="stChatInput"] { border-color:#34435e; }
      hr { border-color:#243149; }
    </style>
    """,
    unsafe_allow_html=True,
)

store = ChatStore(DB_PATH)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "provider" not in st.session_state:
    st.session_state.provider = "OpenAI-compatible"
if "model" not in st.session_state:
    st.session_state.model = "gpt-4o-mini"

PROVIDER_DEFAULTS = {
    "OpenAI-compatible": {
        "model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY",
    },
    "Gemini": {
        "model": "gemini-2.5-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "key_env": "GEMINI_API_KEY",
    },
    "Ollama (local)": {
        "model": "llama3.2",
        "base_url": "http://localhost:11434",
        "key_env": "",
    },
}


def start_new_chat() -> None:
    st.session_state.chat_id = None
    st.session_state.messages = []


def load_chat(chat_id: int) -> None:
    saved = store.get_chat(chat_id)
    if saved:
        st.session_state.chat_id = saved["id"]
        st.session_state.messages = saved["messages"]
        st.session_state.provider = saved["provider"]
        st.session_state.model = saved["model"]


def persist_chat() -> None:
    messages = st.session_state.messages
    if not messages:
        return
    first_user = next((m["content"] for m in messages if m["role"] == "user"), "Cuộc trò chuyện mới")
    title = " ".join(first_user.strip().split())[:52] or "Cuộc trò chuyện mới"
    current_id = store.save_chat(
        chat_id=st.session_state.chat_id,
        title=title,
        provider=st.session_state.provider,
        model=st.session_state.model,
        messages=messages,
    )
    st.session_state.chat_id = current_id


# Sidebar: điều hướng và cài đặt kết nối.
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◈</div><div class="brand-name">VibNest</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Trợ lý AI đa mô hình</div>', unsafe_allow_html=True)

    if st.button("＋  Cuộc trò chuyện mới", use_container_width=True, type="primary"):
        start_new_chat()
        st.rerun()

    st.markdown("#### Lịch sử trò chuyện")
    recent_chats = store.list_chats(limit=30)
    if recent_chats:
        for item in recent_chats:
            label = item["title"] or "Cuộc trò chuyện mới"
            is_current = item["id"] == st.session_state.chat_id
            button_label = ("● " if is_current else "　") + label[:34]
            if st.button(button_label, key=f"chat_{item['id']}", use_container_width=True):
                load_chat(item["id"])
                st.rerun()
    else:
        st.caption("Các đoạn chat đã lưu sẽ hiển thị ở đây.")

    st.divider()
    st.markdown("#### Kết nối mô hình AI")

    provider_options = list(PROVIDER_DEFAULTS.keys())
    current_provider = st.session_state.provider
    if current_provider not in provider_options:
        current_provider = "OpenAI-compatible"
    provider = st.selectbox(
        "Nhà cung cấp (Provider)",
        provider_options,
        index=provider_options.index(current_provider),
        help="Chọn dịch vụ API đám mây hoặc máy chủ Ollama cục bộ.",
    )
    defaults = PROVIDER_DEFAULTS[provider]

    default_base = defaults["base_url"]
    default_model = defaults["model"]
    default_env_key = os.getenv(defaults["key_env"], "") if defaults["key_env"] else ""

    base_url = st.text_input(
        "Đường dẫn cơ sở API (Base URL)",
        value=st.session_state.get(f"base_{provider}", default_base),
        key=f"base_widget_{provider}",
        help="Đối với các dịch vụ tương thích OpenAI, dùng gốc API thường kết thúc bằng /v1.",
    )
    st.session_state[f"base_{provider}"] = base_url

    model = st.text_input(
        "Tên mô hình (Model name)",
        value=st.session_state.get(f"model_{provider}", default_model),
        key=f"model_widget_{provider}",
    )
    st.session_state[f"model_{provider}"] = model

    api_key = ""
    if provider != "Ollama (local)":
        api_key = st.text_input(
            "Khóa API (API key)",
            value=st.session_state.get(f"key_{provider}", default_env_key),
            type="password",
            key=f"key_widget_{provider}",
            help="Khóa được giữ trong phiên làm việc Streamlit này và không được lưu vào lịch sử chat.",
        )
        st.session_state[f"key_{provider}"] = api_key
    else:
        st.caption("Đảm bảo Ollama đang chạy và mô hình đã được cài đặt.")

    st.session_state.provider = provider
    st.session_state.model = model.strip() or default_model

    st.divider()
    st.markdown("#### Hành vi của trợ lý")
    system_prompt = st.text_area(
        "Prompt hệ thống",
        value=st.session_state.get(
            "system_prompt",
            "Bạn là một trợ lý hữu ích và chính xác. Hãy rõ ràng về mức độ chắc chắn và không bịa đặt thông tin.",
        ),
        height=120,
    )
    st.session_state.system_prompt = system_prompt

    temperature = st.slider("Nhiệt độ (Temperature)", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.select_slider("Số token đầu ra tối đa", options=[256, 512, 1024, 2048, 4096, 8192], value=2048)

    # Vị trí cố định của phần nạp tiền bằng tài khoản ngân hàng (dạng mẫu)
    st.divider()
    st.markdown("#### 💎 Nạp tiền ngân hàng")
    st.markdown("""
    *Chức năng nạp tiền qua tài khoản (Mẫu)*:
    - **Ngân hàng:** MB Bank / Vietcombank
    - **STK:** `123456789`
    - **Chủ TK:** CHINH LY
    - **Nội dung:** `nap [Tên tài khoản]`
    """)

    st.divider()
    st.markdown('<div class="small-muted">VibNest là dự án độc lập. Việc sử dụng API có thể phát sinh phí từ nhà cung cấp.</div>', unsafe_allow_html=True)

# Khu vực chính.
st.markdown(
    '<div class="hero"><h1>Bạn muốn khám phá điều gì hôm nay?</h1>'
    '<p>Trò chuyện với các mô hình AI khác nhau từ một không gian làm việc tối ưu.</p></div>',
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("##### Bắt đầu với một gợi ý nhanh")
    sample_prompts = [
        "Giải thích một chủ đề phức tạp bằng ngôn từ đơn giản.",
        "Giúp tôi lên kế hoạch kinh doanh nhỏ với ngân sách hạn chế.",
        "Đánh giá đoạn mã này và đề xuất các điểm cải tiến.",
    ]
    cols = st.columns(3)
    for index, prompt in enumerate(sample_prompts):
        with cols[index]:
            if st.button(prompt, key=f"sample_{index}", use_container_width=True):
                st.session_state.pending_prompt = prompt
                st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

pending_prompt = st.session_state.pop("pending_prompt", None)
user_prompt = st.chat_input("Nhắn cho VibNest…") or pending_prompt

if user_prompt:
    cleaned_prompt = user_prompt.strip()
    if cleaned_prompt:
        st.session_state.messages.append({"role": "user", "content": cleaned_prompt})
        with st.chat_message("user"):
            st.markdown(cleaned_prompt)

        request_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        with st.chat_message("assistant"):
            response_slot = st.empty()
            with st.spinner(f"Đang trò chuyện với {st.session_state.model}…"):
                try:
                    answer = chat_completion(
                        provider=st.session_state.provider,
                        model=st.session_state.model,
                        base_url=st.session_state.get(f"base_{st.session_state.provider}", defaults["base_url"]),
                        api_key=st.session_state.get(f"key_{st.session_state.provider}", default_env_key),
                        messages=request_messages,
                        system_prompt=st.session_state.system_prompt,
                        temperature=temperature,
                        max_tokens=int(max_tokens),
                    )
                    response_slot.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    persist_chat()
                except ProviderError as exc:
                    response_slot.error(str(exc))
                except Exception as exc:
                    response_slot.error(f"Lỗi không mong đợi: {exc}")

# Công cụ chân trang.
if st.session_state.messages:
    st.divider()
    col_a, col_b, col_c = st.columns([1, 1, 4])
    transcript = "\n\n".join(
        f"{'Bạn' if m['role'] == 'user' else 'VibNest'}:\n{m['content']}"
        for m in st.session_state.messages
    )
    with col_a:
        st.download_button(
            "Xuất cuộc trò chuyện",
            data=transcript,
            file_name=f"vibnest-chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_b:
        if st.button("Xóa cuộc trò chuyện", use_container_width=True):
            start_new_chat()
            st.rerun()
    with col_c:
        st.caption(f"Nhà cung cấp: {st.session_state.provider} · Mô hình: {st.session_state.model}")
        
