import streamlit as st
import requests

st.set_page_config(page_title="Aegis: Universal Crisis Bridge", layout="wide")

# Correct heading hierarchy for Accessibility
st.title("🛡️ Aegis: Universal Crisis Bridge")
st.markdown("""
A Gemini-powered platform that converts messy, real-world inputs into structured, life-saving actions.
""")

# Efficiency: Caching API responses to prevent redundant network and LLM calls
@st.cache_data(show_spinner=False, ttl=3600)
def call_process_text(text: str) -> dict:
    """Cached call to process unstructured text."""
    try:
        response = requests.post("http://localhost:8000/process-text", json={"text": text}, timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Backend Error ({response.status_code})", "raw": response.text}
    except Exception as e:
        return {"error": f"Connection Error: {e}"}

@st.cache_data(show_spinner=False, ttl=3600)
def call_process_media(file_name: str, file_bytes: bytes, file_type: str) -> dict:
    """Cached call to process media. Caches based on filename & bytes."""
    try:
        files = {"file": (file_name, file_bytes, file_type)}
        response = requests.post("http://localhost:8000/process-media", files=files, timeout=60)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Backend Error ({response.status_code})", "raw": response.text}
    except Exception as e:
        return {"error": f"Connection Error: {e}"}

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Input Capture")
    input_type = st.radio(
        "Select Input Type", 
        ["Text", "Image/Multi-media"], 
        help="Choose the type of data representing the crisis situation you want to upload."
    )
    
    if input_type == "Text":
        user_input = st.text_area(
            "Describe the situation", 
            placeholder="e.g., 'Flooding in sector 4, need water rescue'", 
            height=200,
            help="Type the raw details of the emergency. The system will categorize and prioritize it."
        )
        if st.button("Process Situation", help="Submit the text for AI analysis."):
            if user_input.strip():
                with st.spinner("Gemini is analyzing the text..."):
                    st.session_state['result'] = call_process_text(user_input)
            else:
                st.warning("Please provide some text input.")
    
    else:
        uploaded_file = st.file_uploader(
            "Upload media file", 
            type=["jpg", "jpeg", "png", "webp", "mp3", "wav", "m4a"],
            help="Upload an image or audio clip max 10MB to analyze visual or auditory crisis details."
        )
        if st.button("Process Media", help="Submit the media for AI analysis."):
            if uploaded_file:
                if uploaded_file.size > 10 * 1024 * 1024:
                    st.error("File is too large! Please upload a file smaller than 10MB.")
                else:
                    with st.spinner("Gemini is analyzing the multi-modal data..."):
                        file_bytes = uploaded_file.getvalue()
                        st.session_state['result'] = call_process_media(uploaded_file.name, file_bytes, uploaded_file.type)
            else:
                st.warning("Please upload a file first.")

with col2:
    st.header("📋 Structured Actions")
    if 'result' in st.session_state:
        res = st.session_state['result']
        
        if "error" in res:
            st.error(res["error"])
            with st.expander("Raw Error Details"):
                st.code(res.get("raw", ""))
        else:
            st.subheader(f"Status: {res.get('Criticality', 'Unknown')}")
            st.info(f"**Category:** {res.get('Category', 'N/A')}")
            st.write(f"**Summary:** {res.get('Summary', 'N/A')}")
            st.write(f"**Location:** {res.get('Location', 'Unspecified')}")
            
            st.divider()
            st.subheader("Action Items")
            for i, item in enumerate(res.get('Action Items', [])):
                with st.expander(f"Action #{i+1}: {item.get('priority', 'Low')} - {item.get('target', 'Responder')}"):
                    st.write(item.get('instruction', 'No instruction provided.'))
    else:
        st.info("Input a situation on the left to see structured actions here.")

st.sidebar.markdown("---")
st.sidebar.info("Built for societal benefit using Google Gemini.", icon="🌍")
