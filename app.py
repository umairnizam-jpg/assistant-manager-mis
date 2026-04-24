import streamlit as st
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq

# ==========================================
# 1. HIGH-END UI DESIGN (RED, BLACK, WHITE)
# ==========================================
st.set_page_config(page_title="Assistant Manager MIS", page_icon="👨‍🏫", layout="centered")

st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #f4f4f4; }
    
    /* Main Header Styling */
    .main-title {
        color: #cc0000;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* Floating Chat Bubble Look */
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        max-width: 85%;
    }
    
    /* User Message (Right Side / Black) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #111111 !important;
        color: white !important;
        margin-left: auto;
        border-bottom-right-radius: 2px;
    }

    /* Assistant Message (Left Side / Red Accent) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #ffffff !important;
        border-left: 6px solid #cc0000;
        margin-right: auto;
        border-bottom-left-radius: 2px;
    }

    /* Sidebar - Sleek Black */
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Floating Input Field */
    .stChatInputContainer {
        padding-bottom: 20px;
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIN SYSTEM
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login_screen():
    st.markdown("<div class='main-title'>OFFICE OF THE PROFESSOR</div>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>Strategic Management & MIS Engine</p>", unsafe_allow_html=True)
    
    with st.container():
        _, col, _ = st.columns([0.5, 1, 0.5])
        with col:
            st.markdown("---")
            user = st.text_input("Staff ID")
            pin = st.text_input("Security PIN", type="password")
            if st.button("Enter Portal"):
                if user == "admin" and pin == "mis2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

if not st.session_state["authenticated"]:
    login_screen()
    st.stop()

# ==========================================
# 3. CHAT INTERFACE & ENGINE
# ==========================================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "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")

st.markdown("<div class='main-title'>Assistant Manager MIS</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 👨‍🏫 Session Controls")
    if st.button("Secure Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
    st.divider()
    uploaded_file = st.file_uploader("Internalize Ledger (Excel)", type=["xlsx"])
    if uploaded_file:
        st.success("Ledger Synchronized.")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Auto-Cleaning for Dates (Essential for Quarters/Yearly)
    for col in df.columns:
        if 'date' in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Welcome. I am the Assistant Manager MIS. I have analyzed your dataset. What complex metrics or sums shall we solve today?"}]

    # Render Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat logic
    if prompt := st.chat_input("Ask about Achievement, Quarters, or Yearly Sums..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            # SYSTEM RULES
            rules = """
            You are the 'Assistant Manager MIS', acting as a highly intellectual Professor.
            Your logic is flawless. 
            - CALCULATIONS: Always calculate 'Achievement' as (Actual/Target)*100.
            - QUARTERS/YEARS: If asked, group data by dates (Q1, Q2, etc.).
            - PRECISION: Round all numbers to 2 decimals and use commas (1,234,567.89).
            - NO SCIENTIFIC NOTATION: Never use e+08.
            - TONE: Professional, authoritative, and direct.
            """
            
            llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY, temperature=0)
            agent = create_pandas_dataframe_agent(llm, df, allow_dangerous_code=True, prefix=rules)
            
            with st.spinner("Processing inquiry..."):
                response = agent.invoke(prompt)
                output = response["output"]
                st.write(output)
                st.session_state.messages.append({"role": "assistant", "content": output})

else:
    st.warning("Please provide the Excel Ledger in the sidebar to initiate analysis.")
