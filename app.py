import streamlit as st
import os
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv

# 1. Page Configuration
st.set_page_config(page_title="DocuMind AI", page_icon="🧠", layout="centered")

# 2. API Setup (Crash-Proof Logic)
load_dotenv()

api_key = None

# Defensive check for Streamlit Secrets to prevent "SecretNotFoundError"
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    # If secrets are not found/initialized, fallback to environment variable (.env)
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("🚨 GROQ_API_KEY nahi mili! Streamlit Dashboard ke 'Secrets' mein add karo ya local .env file check karo.")
    st.stop()

client = Groq(api_key=api_key)

# 3. Function to extract text from files
def extract_text(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            # For .txt files
            text = uploaded_file.read().decode("utf-8")
        return text
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# 4. App UI
st.title("🧠 DocuMind AI")
st.markdown("Upload any **PDF** or **TXT** document and chat with it using **Llama 3.1**!")

# Sidebar for file upload
with st.sidebar:
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader("Drop your file here", type=["pdf", "txt"])
    
    if st.button("Clear Chat History"):
        if "messages" in st.session_state:
            st.session_state.messages = []
            st.rerun()

# 5. Main Chat Logic
if uploaded_file is not None:
    # Read document text (cached in session state)
    if "doc_context" not in st.session_state or st.session_state.get("last_uploaded") != uploaded_file.name:
        with st.spinner("Reading document..."):
            st.session_state.doc_context = extract_text(uploaded_file)
            st.session_state.last_uploaded = uploaded_file.name
    
    context = st.session_state.doc_context
    
    if context:
        st.sidebar.success("✅ Document processed successfully!")
        
        # Manage Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display previous chat messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input from User
        if prompt := st.chat_input("Ask a question about your document..."):
            
            # Show user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # AI response generation
            with st.chat_message("assistant"):
                system_prompt = f"""You are DocuMind, a helpful AI assistant. 
                Answer the user's question STRICTLY based on the context provided below. 
                If the answer is not in the context, say 'I cannot find this in the document.'
                
                CONTEXT:
                {context}
                """
                
                api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                
                try:
                    with st.spinner("Thinking..."):
                        completion = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=api_messages,
                            temperature=0.3
                        )
                        reply = completion.choices[0].message.content
                        st.markdown(reply)
                        
                        # Save AI reply to history
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"AI Error: {e}")
else:
    st.info("👈 Please upload a document from the sidebar to start chatting!")