import streamlit as st
import os
from agent.agent_builder import Da3iAgentStreaming
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Page config
st.set_page_config(
    page_title="المُوَحِّد - Da3i Chat Agent", 
    page_icon="🕌", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern chat interface (style-only changes)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: radial-gradient(1200px 600px at 10% 10%, rgba(102,126,234,0.12), transparent 10%),
                    radial-gradient(1000px 400px at 90% 90%, rgba(118,75,162,0.08), transparent 10%),
                    linear-gradient(180deg, #0b1020 0%, #07070b 100%);
        min-height: 100vh;
        font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
        color: #e6eef8;
        padding: 30px 24px;
    }

    .chat-container {
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 10px 40px rgba(2,6,23,0.6), 0 2px 8px rgba(102,126,234,0.04);
        max-width: 920px;
        margin: 18px auto;
        border: 1px solid rgba(255,255,255,0.03);
        backdrop-filter: blur(6px) saturate(120%);
        text-align: right; /* Align everything to the right */
    direction: rtl;    /* Right-to-left text flow */
    }

    .main-title {
        text-align: center;
        color: white;
        font-size: 56px;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #9fa8ff, #7c57d6);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .subtitle {
        text-align: center;
        color: rgba(230,238,248,0.9);
        font-size: 22px;
        margin-bottom: 30px;
    }

    .methodology {
        text-align: center; /* centers text inside the element */
        color: #cfcfff;
        font-size: 20px;
        padding: 12px 16px;
        border-radius: 999px;
        display: block; /* make it a block element */
        background: linear-gradient(90deg, rgba(102,126,234,0.10), rgba(118,75,162,0.06));
        font-weight: 700;
        margin: 0 auto 20px auto; /* top/bottom 0 & 20px, left/right auto to center */
    }


    .chat-messages {
    display: flex;
    flex-direction: column;
    align-items: flex-end; /* Make new messages appear on the right */
    }

    .msg {
        display: inline-flex;
        align-items: flex-start;
        gap: 12px;
        padding: 14px 16px;
        border-radius: 16px;
        max-width: 78%;
        box-shadow: 0 6px 18px rgba(2,6,23,0.45);
        line-height: 1.6;
        font-size: 15px;
    }

    .user-msg {
        margin-left: auto;
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.04);
        color: #eaf0ff;
        border-top-right-radius: 6px;
        text-align: right;
        direction: rtl;
        font-weight: 600;
    }

    .bot-msg {
        margin-right: auto;
        background: linear-gradient(180deg, rgba(102,126,234,0.14), rgba(118,75,162,0.06));
        color: white;
        border: 1px solid rgba(102,126,234,0.18);
        box-shadow: 0 8px 30px rgba(118,75,162,0.06);
        border-top-left-radius: 6px;
        text-align: right;
        direction: rtl;
        font-weight: 600;
    }

    .user-icon, .bot-icon {
        width: 36px;
        height: 36px;
        display: inline-grid;
        place-items: center;
        border-radius: 50%;
        font-size: 18px;
    }

    .user-icon {
        background: linear-gradient(180deg, #0f1724, #0b1220);
        color: #cfe1ff;
    }

    .bot-icon {
        background: linear-gradient(90deg, #7c57d6, #667eea);
        color: white;
    }

    .input-row {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .stTextInput > div > div > input {
        border-radius: 999px;
        padding: 14px 18px;
        font-size: 16px;
        border: 1px solid rgba(255,255,255,0.06);
        background: rgba(255,255,255,0.02);
        color: #f4f8ff;
        direction: rtl;
        text-align: right;
        width: 100%;
        direction: rtl;
        text-align: right;
        outline: none;
    }

    .stTextInput > div > div > input:focus {
        box-shadow: 0 6px 20px rgba(102,126,234,0.14);
        border: 1px solid rgba(102,126,234,0.4);
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #7c57d6 100%);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 12px 18px;
        font-size: 16px;
        font-weight: 700;
        cursor: pointer;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
        box-shadow: 0 8px 20px rgba(102,126,234,0.16);
        min-width: 120px;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 30px rgba(102,126,234,0.2);
    }

    .clear-button {
        background: transparent;
        color: rgba(230,238,248,0.9);
        border: 1px dashed rgba(255,255,255,0.06);
        border-radius: 999px;
        padding: 8px 14px;
        font-weight: 600;
        cursor: pointer;
    }

    .clear-button:hover {background: rgba(255,255,255,0.03);}

    .typing-indicator { display:flex; gap:6px; align-items:center; }
    .typing-dot { width:8px; height:8px; background: #dfe7ff; border-radius:50%; opacity:0.9; animation: typing 1.25s infinite; }
    .typing-dot:nth-child(2) { animation-delay:0.15s; }
    .typing-dot:nth-child(3) { animation-delay:0.3s; }
    @keyframes typing { 0%{ transform:translateY(0);} 50%{transform:translateY(-6px);} 100%{transform:translateY(0);} }

    .chat-messages::-webkit-scrollbar { width:8px; }
    .chat-messages::-webkit-scrollbar-track { background: transparent; }
    .chat-messages::-webkit-scrollbar-thumb { background: rgba(124,87,214,0.26); border-radius:10px; }

    @media (max-width: 880px) {
        .main-title { font-size: 42px; }
        .chat-container { margin: 12px; padding: 18px; }
        .stButton > button { min-width: 90px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent" not in st.session_state:
    with st.spinner("🔄 جاري تحميل النموذج..."):
        st.session_state.agent = Da3iAgentStreaming(data_dir="data")

agent = st.session_state.agent

# Header
st.markdown("<h1 class='main-title'>🕌 المُوَحِّد</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>مساعدك الذكي في تعلم العقيدة الإسلامية الصافية</p>", unsafe_allow_html=True)
st.markdown("<p class='methodology'>بُني على منهج أهل السنة والجماعة 📚</p>", unsafe_allow_html=True)

# Main container
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    # Chat messages display
    st.markdown("<div class='chat-messages'>", unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='msg user-msg'><span class='user-icon'>👤</span><div>{msg['message']}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='msg bot-msg'><span class='bot-icon'>🤖</span><div>{msg['message']}</div></div>",
                unsafe_allow_html=True
            )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Input area
    col_input, col_button = st.columns([4, 1])
    
    with col_input:
        user_input = st.text_input(
            "اكتب سؤالك هنا...",
            key="input",
            placeholder="مثال: ما هو توحيد الألوهية؟",
            label_visibility="collapsed"
        )
    
    with col_button:
        send_button = st.button("📤 أرسل", use_container_width=True)
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ مسح المحادثة", key="clear"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Handle message sending
    if send_button and user_input:
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        st.markdown(
            f"<div class='msg user-msg'><span class='user-icon'>👤</span><div>{user_input}</div></div>",
            unsafe_allow_html=True
        )
        with st.spinner("🤔 جاري التفكير..."):
            response_placeholder = st.empty()
            full_response = ""
            try:
                for chunk in agent.ask(user_input, chat_history=st.session_state.chat_history):
                    full_response += chunk
                    response_placeholder.markdown(
                        f"<div class='msg bot-msg'><span class='bot-icon'>🤖</span><div>{full_response}▌</div></div>",
                        unsafe_allow_html=True
                    )
                response_placeholder.markdown(
                    f"<div class='msg bot-msg'><span class='bot-icon'>🤖</span><div>{full_response}</div></div>",
                    unsafe_allow_html=True
                )
                st.session_state.chat_history.append({"role": "assistant", "message": full_response})
            except Exception as e:
                st.error(f"❌ حدث خطأ: {str(e)}")
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
