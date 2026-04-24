import streamlit as st
import pandas as pd
import os
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq

# ==========================================
# 1. PAGE CONFIG & PROFESSOR AESTHETICS (RED/WHITE/BLACK)
# ==========================================
st.set_page_config(page_title="Assistant Manager MIS", page_icon="📈", layout="wide")

# Custom CSS for the "Professor" Look and Red/Black/White Theme
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #ffffff; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111111;
        color: white;
    }
    
    /* Professional Headers */
    h1 { color: #cc0000; font-family: 'Georgia', serif; font-weight: bold; border-bottom: 3px solid #111111; }
    
    /* Buttons - Red and Black Theme */
    .stButton>button {
        background-color: #cc0000;
        color: white;
        border: none;
        border-radius: 2px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #000000;
        color: #cc0000;
        border: 1px solid #cc0000;
    }
    
    /* Chat Message Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #f1f1f1;
        border-left: 5px solid #cc0000;
        border-radius: 5px;
    }
    
    /* Input Box */
    .stTextInput>div>div>input { border: 2px solid #111111; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIN SYSTEM
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    st.markdown("<h1 style='text-align: center;'>OFFICE OF THE ASSISTANT MANAGER MIS</h1>", unsafe_allow_html=True)
    with st.container():
        _, mid, _ = st.columns([1,2,1])
        with mid:
            st.info("Please enter your corporate credentials to access the MIS Data Engine.")
            with st.form("login"):
                user = st.text_input("Staff ID")
                pwd = st.text_input("Security Key", type="password")
                if st.form_submit_button("Verify Identity"):
                    if user == "admin" and pwd == "mis2026": # You can change these
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("Unauthorized Access Attempt.")

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ==========================================
# 3. THE "PROFESSOR" BRAIN (MIS LOGIC)
# ==========================================
# Use Streamlit Secrets for Deployment or paste your key here
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "PASTE_YOUR_KEY_HERE")

st.markdown("<h1>Assistant Manager MIS</h1>", unsafe_allow_html=True)
st.caption("Strategic Intelligence & Data Analysis Portal")

with st.sidebar:
    st.title("🗄️ Control Desk")
    st.write(f"**Current User:** Admin")
    if st.button("Terminate Session"):
        st.session_state["authenticated"] = False
        st.rerun()
    st.divider()
    uploaded_file = st.file_uploader("Feed Data to the Engine (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Ensure date columns are actual dates for Quarter/Yearly logic
    for col in df.columns:
        if 'date' in col.lower():
            df[col] = pd.to_datetime(df[col], errors='ignore')

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "The data has been internalized. I am ready to provide summaries, achievement metrics, or quarterly insights. What is your inquiry?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter your search (e.g., 'What is the sum of sales for Q2?')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing Ledger..."):
                # ADVANCED MIS INSTRUCTIONS
                professor_logic = """
                You are the 'Assistant Manager MIS'. You speak with the authority and precision of a university professor.
                
                YOUR CAPABILITIES:
                1. SUMS: Automatically calculate total sums for any column mentioned.
                2. QUARTERLY/YEARLY: If a date column exists, group data by Quarter (Q1, Q2, etc.) or Year when asked.
                3. ACHIEVEMENT: Achievement % = (Actual / Target) * 100. Always look for columns representing 'Actual' and 'Target' (even if named 'Sales' and 'Goal').
                4. ACCURACY: No matter how the user types (even with bad grammar), identify their intent.
                5. FORMATTING: Use commas for numbers (1,000,000), 2 decimal places, and NEVER use scientific notation (e+08).
                
                If the user search is vague, analyze the most relevant column and provide a summary.
                """

                llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY, temperature=0)
                agent = create_pandas_dataframe_agent(
                    llm, df, verbose=False, agent_type="tool-calling", 
                    allow_dangerous_code=True, prefix=professor_logic
                )
                
                response = agent.invoke(prompt)
                ans = response["output"]
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
else:
    st.warning("Awaiting Excel Ledger Upload...")
