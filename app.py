from __future__ import annotations

import os
from datetime import datetime
import streamlit as st

from providers import ProviderError, chat_completion
from storage import ChatStore

APP_TITLE = "WormGPT"
DB_PATH = os.getenv("DARKGPT_DB_PATH", "darkgpt.sqlite3")

st.set_page_config(page_title=APP_TITLE, page_icon="🐍", layout="wide", initial_sidebar_state="collapsed")

# Mobile-first styling inspired by the reference screenshot.
st.markdown(r"""
<style>
:root { color-scheme: dark; }
html, body, [data-testid="stAppViewContainer"], .stApp { background:#000 !important; color:#f5f5f7; }
[data-testid="stHeader"] { background:rgba(0,0,0,0.96); border-bottom:1px solid #171717; }
[data-testid="stToolbar"] { right:1rem; }
.block-container { max-width:100% !important; padding: .55rem .8rem 6.8rem !important; }
[data-testid="stSidebar"] { background:#080808; border-right:1px solid #292929; }
[data-testid="stSidebar"] * { color:#f5f5f7; }
/* Compact top navigation */
.topbar { display:flex; align-items:center; gap:8px; white-space:nowrap; overflow:hidden; padding:4px 0 12px; border-bottom:1px solid #171717; }
.brand-pill { border:1px solid #292929; background:#111; color:#f7f7f7; border-radius:13px; padding:11px 13px; font-weight:750; font-size:15px; }
.credit-pill { display:inline-block; border:1px solid #343434; background:#151515; border-radius:22px; padding:9px 13px; color:#f7f7f7; font-weight:700; }
.red-pill { background:linear-gradient(#ff334b,#d40c27); border:1px solid #ff5365; border-radius:24px; padding:10px 13px; color:white; font-weight:800; box-shadow:inset 0 1px 1px #ff9aa5; }
/* Make Streamlit controls look like the app header */
.stSelectbox [data-baseweb="select"] { background:#111 !important; border:1px solid #303030 !important; border-radius:13px !important; min-height:45px; }
.stSelectbox [data-baseweb="select"] * { color:#f4f4f5 !important; }
.stButton > button { border-radius:18px; border:1px solid #2d2d2d; background:#121212; color:#f5f5f7; min-height:43px; font-weight:700; }
.stButton > button:hover { border-color:#555; color:#fff; }
/* Welcome panel */
.welcome { min-height:calc(100dvh - 250px); display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:2rem .5rem 1rem; }
.worm-mark { font-size:72px; line-height:1; color:#ff1735; filter:drop-shadow(0 0 22px rgba(255,0,35,.22)); margin-bottom:25px; }
.welcome h1 { font-size:clamp(25px,5vw,36px); letter-spacing:-.8px; line-height:1.2; margin:0 0 25px; color:#f7f7f8; font-weight:850; }
.welcome p { font-size:clamp(16px,3.5vw,23px); color:#85858d; margin:0; }
/* Messages and input */
[data-testid="stChatMessage"] { background:#080808; border:1px solid #252525; border-radius:18px; padding:12px 14px; }
[data-testid="stChatInput"] { position:fixed; bottom:12px; left:2.2%; width:95.6%; max-width:none; background:#111 !important; border:1px solid #353535 !important; border-radius:28px !important; box-shadow:0 0 0 1px rgba(255,255,255,.02); z-index:999; }
[data-testid="stChatInput"] textarea { color:#f7f7f7 !important; background:transparent !important; font-size:17px !important; }
[data-testid="stChatInput"] textarea::placeholder { color:#777780 !important; }
[data-testid="stChatInput"] button { background:#202020 !important; border-radius:50% !important; }
[data-testid="stChatInput"] button svg { fill:#fff !important; }
.stCaption, small { color:#8a8a91 !important; }
hr { border-color:#222 !important; }
@media (max-width:600px) {
 .block-container { padding-left:.55rem !important; padding-right:.55rem !important; }
 .welcome { min-height:calc(100dvh - 260px); }
 .topbar { gap:5px; }
 .red-pill { padding:9px 9px; font-size:12px; }
}
</style>
""", unsafe_allow_html=True)

store = ChatStore(DB_PATH)
PROVIDER_DEFAULTS = {
    "OpenAI-compatible": {"model":"gpt-4o-mini", "base_url":"https://api.openai.com/v1", "key_env":"OPENAI_API_KEY"},
    "Gemini": {"model":"gemini-2.5-flash", "base_url":"https://generativelanguage.googleapis.com/v1beta", "key_env":"GEMINI_API_KEY"},
    "Ollama (local)": {"model":"llama3.2", "base_url":"http://localhost:11434", "key_env":""},
}

for key, value in {
    "messages": [], "chat_id": None, "provider": "OpenAI-compatible", "model": "gpt-4o-mini",
    "system_prompt": "You are a helpful, accurate assistant. Be clear about uncertainty and do not invent facts.",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
    if not st.session_state.messages:
        return
    first_user = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "New conversation")
    title = " ".join(first_user.strip().split())[:52] or "New conversation"
    st.session_state.chat_id = store.save_chat(
        chat_id=st.session_state.chat_id, title=title, provider=st.session_state.provider,
        model=st.session_state.model, messages=st.session_state.messages,
    )

# Sidebar: working settings and saved conversations.
with st.sidebar:
    st.markdown("## 🐍 WormGPT")
    st.caption("Your AI assistant")
    if st.button("＋ New conversation", use_container_width=True):
        start_new_chat(); st.rerun()
    st.markdown("### Recent conversations")
    for item in store.list_chats(limit=30):
        if st.button(item["title"] or "New conversation", key=f"chat_{item['id']}", use_container_width=True):
            load_chat(item["id"]); st.rerun()
    st.divider()
    st.markdown("### AI settings")
    provider = st.selectbox("Provider", list(PROVIDER_DEFAULTS), index=list(PROVIDER_DEFAULTS).index(st.session_state.provider) if st.session_state.provider in PROVIDER_DEFAULTS else 0)
    defaults = PROVIDER_DEFAULTS[provider]
    base_url = st.text_input("API base URL", value=st.session_state.get(f"base_{provider}", defaults["base_url"]))
    model = st.text_input("Model name", value=st.session_state.get(f"model_{provider}", defaults["model"]))
    api_key = ""
    if defaults["key_env"]:
        api_key = st.text_input("API key", value=st.session_state.get(f"key_{provider}", os.getenv(defaults["key_env"], "")), type="password")
        st.session_state[f"key_{provider}"] = api_key
    st.session_state[f"base_{provider}"] = base_url
    st.session_state[f"model_{provider}"] = model
    st.session_state.provider = provider
    st.session_state.model = model.strip() or defaults["model"]
    st.session_state.system_prompt = st.text_area("System prompt", value=st.session_state.system_prompt, height=110)
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.select_slider("Max output tokens", options=[256,512,1024,2048,4096,8192], value=2048)
    st.caption("API usage may incur provider charges. Never share your API key.")

# Header modeled after the reference: menu, model picker, credits, and red action pills.
col_menu, col_model, col_credits, col_gift, col_topup = st.columns([.55, 1.45, .55, 1.15, 1.55], gap="small")
with col_menu:
    if st.button("☰", key="open_menu", help="Open menu and settings"):
        st.session_state.show_menu = not st.session_state.get("show_menu", False)
        st.rerun()
with col_model:
    model_choices = ["WormGPT", "GPT-4o mini", "Gemini Flash", "Llama 3.2"]
    chosen = st.selectbox("Model", model_choices, index=0, label_visibility="collapsed")
with col_credits:
    st.markdown('<div class="credit-pill">✧ 0</div>', unsafe_allow_html=True)
with col_gift:
    st.markdown('<div class="red-pill">♙ Giftcode</div>', unsafe_allow_html=True)
with col_topup:
    st.markdown('<div class="red-pill">＄ Nạp tín dụng</div>', unsafe_allow_html=True)

if st.session_state.get("show_menu", False):
    with st.container(border=True):
        st.markdown("**WormGPT menu**")
        m1, m2 = st.columns(2)
        with m1:
            if st.button("＋ Chat mới", use_container_width=True):
                start_new_chat(); st.rerun()
        with m2:
            if st.button("⚙ Cài đặt AI", use_container_width=True):
                st.session_state.show_settings_hint = True
        if st.session_state.get("show_settings_hint"):
            st.info("Mở menu ☰ ở góc trên để xem phần cài đặt và lịch sử chat.")

if not st.session_state.messages:
    st.markdown('''<section class="welcome"><div class="worm-mark">♆</div><h1>WormGPT Ready</h1><p>Trợ lý AI của bạn. Hãy bắt đầu trò chuyện!</p></section>''', unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_prompt = st.chat_input("Nhập tin nhắn...")
if user_prompt and user_prompt.strip():
    cleaned_prompt = user_prompt.strip()
    st.session_state.messages.append({"role":"user", "content":cleaned_prompt})
    with st.chat_message("user"):
        st.markdown(cleaned_prompt)
    request_messages = [{"role":m["role"], "content":m["content"]} for m in st.session_state.messages]
    defaults = PROVIDER_DEFAULTS[st.session_state.provider]
    with st.chat_message("assistant"):
        response_slot = st.empty()
        with st.spinner(f"Đang kết nối {st.session_state.model}…"):
            try:
                answer = chat_completion(
                    provider=st.session_state.provider, model=st.session_state.model,
                    base_url=st.session_state.get(f"base_{st.session_state.provider}", defaults["base_url"]),
                    api_key=st.session_state.get(f"key_{st.session_state.provider}", os.getenv(defaults["key_env"], "") if defaults["key_env"] else ""),
                    messages=request_messages, system_prompt=st.session_state.system_prompt,
                    temperature=temperature if "temperature" in locals() else 0.7,
                    max_tokens=int(max_tokens) if "max_tokens" in locals() else 2048,
                )
                response_slot.markdown(answer)
                st.session_state.messages.append({"role":"assistant", "content":answer})
                persist_chat()
            except ProviderError as exc:
                response_slot.error(str(exc))
            except Exception as exc:
                response_slot.error(f"Lỗi không mong đợi: {exc}")
    st.rerun()

if st.session_state.messages:
    with st.expander("Công cụ cuộc trò chuyện"):
        transcript = "\n\n".join(f"{'Bạn' if m['role']=='user' else 'WormGPT'}:\n{m['content']}" for m in st.session_state.messages)
        st.download_button("Tải lịch sử chat", data=transcript, file_name=f"wormgpt-chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md", mime="text/markdown")
        if st.button("Xóa cuộc trò chuyện"):
            start_new_chat(); st.rerun()
