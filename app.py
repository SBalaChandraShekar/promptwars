import streamlit as st
import requests
import json

st.set_page_config(page_title="Aegis: Universal Bridge", layout="wide")

st.title("🛡️ Aegis: Universal Crisis Bridge")
st.markdown("""
A Gemini-powered platform that converts messy, real-world inputs into structured, life-saving actions.
""")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Input Capture")
    input_type = st.radio("Input Type", ["Text", "Image/Multi-media"])
    
    if input_type == "Text":
        user_input = st.text_area("Describe the situation (e.g., 'Flooding in sector 4, need help')", height=200)
        if st.button("Process Situation"):
            if user_input:
                with st.spinner("Gemini is analyzing..."):
                    try:
                        response = requests.post("http://localhost:8000/process-text", json={"text": user_input})
                        st.session_state['result'] = response.json()
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")
            else:
                st.warning("Please provide some input.")
    
    else:
        uploaded_file = st.file_uploader("Upload an image, audio file, or document", type=["jpg", "jpeg", "png", "mp3", "wav", "m4a"])
        if st.button("Process Media"):
            if uploaded_file:
                with st.spinner("Gemini is analyzing multi-modal data..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    try:
                        response = requests.post("http://localhost:8000/process-media", files=files)
                        st.session_state['result'] = response.json()
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")
            else:
                st.warning("Please upload a file.")

with col2:
    st.header("📋 Structured Actions")
    if 'result' in st.session_state:
        res = st.session_state['result']
        
        if "error" in res:
            st.error(res["error"])
            st.code(res.get("raw", ""))
        else:
            st.subheader(f"Status: {res.get('Criticality', 'Unknown')}")
            st.info(f"**Category:** {res.get('Category', 'N/A')}")
            st.write(f"**Summary:** {res.get('Summary', 'N/A')}")
            st.write(f"**Location:** {res.get('Location', 'Unspecified')}")
            
            st.divider()
            st.subheader("Action Items")
            for item in res.get('Action Items', []):
                with st.expander(f"{item.get('priority', 'Low')} - {item.get('target', 'Responder')}"):
                    st.write(item.get('instruction', 'No instruction provided.'))
    else:
        st.write("Input a situation on the left to see structured actions here.")

st.sidebar.markdown("---")
st.sidebar.info("Built for societal benefit using Google Gemini.")
