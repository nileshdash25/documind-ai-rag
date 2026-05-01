import streamlit as st
import os
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv

# Page Configuration
st.set_page_config(page_title="DocuMind AI", page_icon="🧠", layout="centered")

# API Setup
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY is missing. Please add it to your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# Function to extract text from files
def extract_text(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        else:
            text = uploaded_file.read().decode("utf-8")
        return text
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# App UI
st.title("🧠 DocuMind AI")
st.markdown("Upload any **PDF** or **TXT** document and chat with it using **Llama 3.1**!")

# Sidebar for file upload
with st.sidebar:
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader("Drop your file here", type=["pdf", "txt"])

# Main Chat Logic
if uploaded_file is not None:
    # 1. Read document text
    with st.spinner("Reading document..."):
        context = extract_text(uploaded_file)
    
    if context:
        st.sidebar.success("✅ Document processed successfully!")
        
        # 2. Manage Chat History in Session State
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 3. Display previous chat messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 4. Input from User
        if prompt := st.chat_input("Ask a question about your document..."):
            
            # Show user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Show AI response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                # Build context-aware prompt
                system_prompt = f"""You are DocuMind, a helpful AI assistant. 
                Answer the user's question STRICTLY based on the context below. 
                If the answer is not in the context, say "I cannot find this in the document."
                
                CONTEXT:
                {context}
                """
                
                # Format messages for Groq API
                api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                
                with st.spinner("Thinking..."):
                    try:
                        completion = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=api_messages,
                            temperature=0.3
                        )
                        reply = completion.choices[0].message.content
                        message_placeholder.markdown(reply)
                        
                        # Save AI reply to history
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"AI Error: {e}")
else:
    st.info("👈 Please upload a document from the sidebar to start chatting!")