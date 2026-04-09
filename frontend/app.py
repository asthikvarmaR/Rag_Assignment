import streamlit as st
import requests
import pandas as pd

# ---------- PAGE CONFIG ----------
st.set_page_config(layout="wide", page_title="PO Dashboard", page_icon="📊")

# ---------- HIDE STREAMLIT MENU ----------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- INPUT STYLING ----------
st.markdown("""
<style>
div[data-baseweb="input"] {
    border-radius: 30px !important;
    padding: 6px 14px !important;
    background-color: rgba(150, 150, 150, 0.18) !important;
    border: 1px solid rgba(200, 200, 200, 0.25) !important;
}

div[data-baseweb="input"] > div {
    background: transparent !important;
    border: none !important;
}

div[data-baseweb="input"] input {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-size: 16px !important;
    padding: 10px 6px !important;
}

.stButton>button {
    background-color: black;
    color: white;
    border-radius: 20px;
    height: 40px;
    width: 150px;
    border: none;
}

.stButton>button:hover {
    background-color: #333;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "history" not in st.session_state:
    st.session_state.history = []

if "last_results" not in st.session_state:
    st.session_state.last_results = None

if "last_insight" not in st.session_state:
    st.session_state.last_insight = ""

if "last_analytics" not in st.session_state:
    st.session_state.last_analytics = ""

# ---------- HEADER ----------
st.title("📊 AI powered data Extraction Dashboard")
st.caption("AI-powered dynamic data extraction")

# ---------- CONTROLS ----------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Data"):
        st.rerun()

with col2:
    if st.button("🧹 Clear History"):
        st.session_state.history = []
        st.session_state.last_results = None
        st.session_state.last_insight = ""
        st.session_state.last_analytics = ""
        st.rerun()

with col3:
    show_history = st.checkbox("🕘 Show Session History")

# ---------- INPUT ----------
query = st.text_input(
    "🔍 Enter your query",
    placeholder="Ask anything about your purchase orders..."
)

submit = st.button("Submit")

# ---------- ENTER KEY ----------
if query and not submit:
    submit = True

# ---------- EXECUTION ----------
if submit and query:

    # Save query
    st.session_state.history.append(query)

    with st.spinner("Processing..."):

        try:
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"question": query}
            )
            data = response.json()
        except:
            st.error("⚠️ Backend not running")
            st.stop()

    results = data.get("results", [])
    insight = data.get("insight", "")
    analytics = data.get("analytics", "")

    # Store latest results
    st.session_state.last_results = results
    st.session_state.last_insight = insight
    st.session_state.last_analytics = analytics

# ---------- DISPLAY LAST RESULT (PERSISTS AFTER RERUN) ----------
if st.session_state.last_results:

    df = pd.DataFrame(st.session_state.last_results)

    # ---------- DOWNLOAD ----------
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download Results", csv, "results.csv", "text/csv")

    # ---------- RESULTS ----------
    st.markdown("### 📋 Results")
    st.dataframe(df, use_container_width=True)

    # ---------- INSIGHT ----------
    if st.session_state.last_insight:
        st.markdown("### 🧠 Insight")
        st.success(st.session_state.last_insight)

    # ---------- ANALYTICS ----------
    if st.session_state.last_analytics and len(st.session_state.last_analytics.strip()) > 10:
        st.markdown("### 📈 Analytics")
        st.info(st.session_state.last_analytics)

    # ---------- GRAPH ----------
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:
        st.markdown("### 📊 Visualization")

        try:
            st.bar_chart(df[numeric_cols[0]])
        except:
            pass

# ---------- HISTORY ----------
if show_history and st.session_state.history:
    st.markdown("### 🕘 Session History")

    for q in reversed(st.session_state.history[-5:]):
        st.write("•", q)