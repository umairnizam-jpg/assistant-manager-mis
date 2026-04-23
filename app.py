import streamlit as st
import pandas as pd
import os
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq

# ==========================================
# 1. PAGE CONFIGURATION & PROFESSIONAL UI
# ==========================================
st.set_page_config(page_title="Assistant Manager MIS", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #0056b3; color: white; border-radius: 5px; width: 100%; }
    .stTextInput>div>div>input { border-radius: 5px; }
    h1 { color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
    .chat-header { font-size: 1.1rem; color: #6c757d; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION SYSTEM
# ==========================================
USER_CREDENTIALS = {
    "admin": "password123",
    "manager": "mis2026"
}

def login():
    st.title("🔒 MIS Portal Login")
    with st.container():
        left, mid, right = st.columns([1,2,1])
        with mid:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Access System")
                if submit:
                    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ==========================================
# 3. MAIN APP: ASSISTANT MANAGER MIS
# ==========================================

# INPUT YOUR GROQ API KEY HERE
GROQ_API_KEY = "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" 

st.title("📊 Assistant Manager MIS")
st.markdown(f"<div class='chat-header'>User Session: **{st.session_state['username'].upper()}** | Mode: Data Analysis</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Office Controls")
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
    
    st.divider()
    uploaded_file = st.file_uploader("Upload MIS Data (Excel)", type=["xlsx"])
    
    if uploaded_file:
        st.info("File received. Processing...")

if uploaded_file is not None:
    try:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)
        with st.expander("📁 View Raw Data Sheet"):
            st.dataframe(df, use_container_width=True)

        # Initialize Chat
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "I am ready. Ask me any question about the uploaded MIS report."}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat logic
        if prompt := st.chat_input("Ex: What was the total revenue per region?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Calculating..."):
                    try:
                        # Using Groq Llama 3 (Powerful and Free)
                        llm = ChatGroq(
                            temperature=0, 
                            model_name="llama-3.3-70b-versatile", 
                            groq_api_key=GROQ_API_KEY
                        )
                        
                        agent = create_pandas_dataframe_agent(
                            llm, 
                            df, 
                            verbose=False, 
                            agent_type="tool-calling",
                            allow_dangerous_code=True 
                        )
                        
                        response = agent.invoke(prompt)
                        ans = response["output"]
                        
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    except Exception as e:
                        st.error(f"Analysis Error: {e}")

    except Exception as e:
        st.error(f"File Error: {e}")
else:
    st.warning("Please upload an Excel file in the sidebar to activate the Assistant.")