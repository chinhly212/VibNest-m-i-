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
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      :root { color-scheme: dark; }
      .stApp { background: #05070b; }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stSidebar"] { background: #0b101d; border-right: 1px solid #1a2336; }
      
      .block-container { 
        max-width: 600px !important; 
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        padding-top: 0.3rem !important; 
        padding-bottom: 5.5rem !important; 
      }

      /* Thanh Topbar thuần HTML/CSS flexbox tuyệt đối không bao giờ vỡ */
      .custom-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        background: #080d1a;
        border: 1px solid #1f2c44;
        padding: 8px 10px;
        border-radius: 14px;
        margin-bottom: 12px;
        width: 100%;
      }
      .topbar-btn {
        background: #0e1422;
        border: 1px solid #1f2c44;
        color: #f4f5f8;
        padding: 6px 10px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        text-decoration: none;
        white-space: nowrap;
      }
      .topbar-btn.primary {
        background: #e53935;
        border-color: #e53935;
        color: white;
      }
      .model-pill {
        background: #0e1422;
        border: 1px solid #1f2c44;
        color: #f4f5f8;
        padding: 6px 10px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 600;
        text-align: center;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .chat-hero {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 3.5rem 1rem 1.5rem 1rem;
      }
      .chat-hero-logo {
        width: 3.8rem;
        height: 3.8rem;
        display: grid;
        place-items: center;
        border-radius: 1.2rem;
        background: linear-gradient(135deg, #ff4b4b, #ff764b);
        color: white;
        font-size: 1.8rem;
        box-shadow: 0 0 25px rgba(255, 75, 75, 0.3);
        margin-bottom: 1rem;
      }
      .chat-hero h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f4f5f8;
        margin: 0 0 0.4rem 0;
      }
      .chat-hero p {
        color: #8b97b0;
        font-size: 0.88rem;
        margin: 0;
      }

      div[data-testid="stChatMessage"] { 
        background: #0e1422; 
        border: 1px solid #1b263b; 
        border-radius: 1rem; 
        padding: 0.8rem 1rem; 
        margin-bottom: 0.7rem;
      }

      [data-testid="stChatInput"] { 
        background: #0b101d !important;
        border: 1px solid #1f2c44 !important;
        border-radius: 1.2rem !important;
      }
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
        "model": "gemini-3.8-flash",
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

# Xử lý các sự kiện bấm nút trên topbar giả lập bằng query params hoặc st.button ẩn nếu cần
# Ở đây dùng 2 nút Streamlit gọn gàng kết hợp HTML thuần để bắt sự kiện chính xác
top_col1, top_col2, top_col3 = st.columns([1, 1.8, 1.2])

with top_col1:
    if st.button("＋ Mới", use_container_width=True):
        start_new_chat()
        st.rerun()

with top_col2:
    st.markdown(f'<div class="model-pill">◈ {st.session_state.model}</div>', unsafe_allow_html=True)

with top_col3:
    if st.button("💳 Nạp", use_container_width=True, type="primary"):
        st.toast("Xem thông tin STK ở Sidebar bên trái!")

# Sidebar giữ nguyên toàn bộ tính năng
with st.sidebar:
    st.markdown("### ◈ VibNest Dashboard")
    if st.button("＋ Cuộc trò chuyện mới", use_container_width=True, type="primary"):
        start_new_chat()
        st.rerun()

    st.markdown("#### Lịch sử trò chuyện")
    recent_chats = store.list_chats(limit=30)
    if recent_chats:
        for item in recent_chats:
            label = item["title"] or "Cuộc trò chuyện mới"
            is_current = item["id"] == st.session_state.chat_id
            button_label = ("● " if is_current else "　") + label[:30]
            if st.button(button_label, key=f"chat_{item['id']}", use_container_width=True):
                load_chat(item["id"])
                st.rerun()
    else:
        st.caption("Chưa có lịch sử chat.")

    st.divider()
    st.markdown("#### Kết nối mô hình AI")

    provider_options = list(PROVIDER_DEFAULTS.keys())
    current_provider = st.session_state.provider
    if current_provider not in provider_options:
        current_provider = "OpenAI-compatible"
    provider = st.selectbox("Nhà cung cấp (Provider)", provider_options, index=provider_options.index(current_provider))
    defaults = PROVIDER_DEFAULTS[provider]

    base_url = st.text_input("Base URL", value=st.session_state.get(f"base_{provider}", defaults["base_url"]), key=f"base_{provider}")
    model = st.text_input("Model name", value=st.session_state.get(f"model_{provider}", defaults["model"]), key=f"model_{provider}")
    
    if provider != "Ollama (local)":
        api_key = st.text_input("API Key", value=st.session_state.get(f"key_{provider}", os.getenv(defaults["key_env"], "")), type="password", key=f"key_{provider}")
    
    st.session_state.provider = provider
    st.session_state.model = model.strip() or defaults["model"]

    st.divider()
    st.markdown("#### 💎 Nạp tiền ngân hàng (Mẫu)")
    st.markdown("""
    - **Ngân hàng:** MB Bank / Vietcombank
    - **STK:** `123456789`
    - **Chủ TK:** CHINH LY
    - **Nội dung:** `nap [Tên tài khoản]`
    """)

if not st.session_state.messages:
    st.markdown(
        """
        <div class="chat-hero">
            <div class="chat-hero-logo">◈</div>
            <h2>VibNest Ready</h2>
            <p>Trợ lý AI của bạn. Hãy bắt đầu trò chuyện!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Nhập tin nhắn...")

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
                        api_key=st.session_state.get(f"key_{st.session_state.provider}", os.getenv(defaults["key_env"], "")),
                        messages=request_messages,
                        system_prompt=st.session_state.get("system_prompt", "Bạn là trợ lý hữu ích."),
                        temperature=0.7,
                        max_tokens=2048,
                    )
                    response_slot.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    persist_chat()
                except ProviderError as exc:
                    response_slot.error(str(exc))
                except Exception as exc:
                    response_slot.error(f"Lỗi không mong đợi: {exc}")
                    
