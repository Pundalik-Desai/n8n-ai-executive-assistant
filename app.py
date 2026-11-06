import os
import requests
import streamlit as st

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="n8n AI Executive Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Webhook Configuration
# ---------------------------------------------------------
DEFAULT_WEBHOOK = "http://localhost:5678/webhook/1f775159-453d-4b8d-9674-91979537ecf9"
WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", DEFAULT_WEBHOOK)

# ---------------------------------------------------------
# Custom Styling
# ---------------------------------------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #888888;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .capability-card {
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 💼 Executive Control")
    st.markdown('<div class="status-badge">● System Online</div>', unsafe_allow_html=True)
    
    st.markdown("#### ⚡ Capabilities")
    st.markdown("""
    <div class="capability-card">🌐 <b>Web Search:</b> Real-time info via Tavily</div>
    <div class="capability-card">📅 <b>Calendar:</b> Google Calendar events & schedules</div>
    <div class="capability-card">✉️ <b>Gmail:</b> Read, summarize & draft replies</div>
    <div class="capability-card">📝 <b>Notes:</b> Create & append Google Docs</div>
    <div class="capability-card">📊 <b>Expenses:</b> Sheets tracking & Calculator</div>
    <div class="capability-card">✅ <b>Tasks:</b> Manage Google To-Do lists</div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Endpoint info
    with st.expander("⚙️ Backend Endpoint"):
        st.caption("Active n8n Webhook URL:")
        st.code(WEBHOOK_URL, language="text")
    
    # Clear conversation button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# Main Page Header
# ---------------------------------------------------------
st.markdown('<div class="main-title">💼 n8n AI Executive Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Autonomous workspace assistant powered by LangChain, OpenAI gpt-5.6-luna, and n8n</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Chat Session State
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display welcome message when empty
if len(st.session_state.messages) == 0:
    st.info(
        "👋 **Welcome! I am your AI Executive Assistant.**\n\n"
        "Here are a few things you can ask me to do:\n"
        "- *\"What meetings or events do I have scheduled today?\"*\n"
        "- *\"Check my unread emails and summarize them.\"*\n"
        "- *\"Create a meeting with the engineering team for tomorrow at 3 PM.\"*\n"
        "- *\"Add an expense of $45 for team lunch to my budget sheet.\"*\n"
        "- *\"Search the web for the latest updates on OpenAI and summarize them.\"*"
    )

# Render Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "💼"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------------------------------------------------------
# Chat Input & Execution
# ---------------------------------------------------------
user_message = st.chat_input("Type an instruction or question for your executive assistant...")

if user_message:
    # 1. Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_message)
    st.session_state.messages.append({"role": "user", "content": user_message})

    # 2. Call n8n Webhook
    with st.chat_message("assistant", avatar="💼"):
        with st.spinner("Executing task with n8n agent..."):
            try:
                response = requests.post(
                    WEBHOOK_URL,
                    json={"message": user_message},
                    timeout=60
                )

                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Handle array or object outputs from n8n
                        if isinstance(data, list) and len(data) > 0 and "output" in data[0]:
                            ai_response = data[0]["output"]
                        elif isinstance(data, dict) and "output" in data:
                            ai_response = data["output"]
                        elif isinstance(data, dict) and "text" in data:
                            ai_response = data["text"]
                        else:
                            ai_response = str(data)
                    except Exception:
                        ai_response = response.text if response.text else "Task executed successfully (empty response body)."
                else:
                    ai_response = (
                        f"⚠️ **n8n Workflow Error (Status {response.status_code}):**\n\n"
                        f"{response.text or 'No error response body received.'}\n\n"
                        f"Ensure the workflow is set to **Active** in n8n."
                    )
            except requests.exceptions.ConnectionError:
                ai_response = (
                    "❌ **Could not connect to n8n.**\n\n"
                    "Make sure n8n is running locally at `http://localhost:5678`."
                )
            except requests.exceptions.Timeout:
                ai_response = "⏳ **Request timed out.** The AI agent is taking longer than 60 seconds to process."
            except Exception as e:
                ai_response = f"❌ **Unexpected Error:** {str(e)}"

        st.markdown(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
