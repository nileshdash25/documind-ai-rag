import os
import sys
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv

# API Setup
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ API Key missing in .env file!")
    sys.exit(1)

client = Groq(api_key=api_key)

def extract_text(file_path):
    """File se text nikalne ka logic (PDF ya TXT)"""
    text = ""
    try:
        if file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        return text
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

def chat_with_doc(context):
    """Interactive Chat loop with Llama 3.1"""
    print("\n✅ Document loaded successfully!")
    print("🤖 DocuMind AI is ready. Ask anything about the document. (Type 'exit' to quit)\n")
    
    # System prompt mein hum document ka data daal denge
    messages = [
        {"role": "system", "content": f"You are an intelligent document assistant. Answer the user's questions strictly based on the following document context:\n\n{context}\n\nIf the answer is not in the context, say 'I cannot find this in the provided document.'"}
    ]

    while True:
        user_input = input("\n🧑 You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("🤖 DocuMind: Goodbye!")
            break
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            print("🤖 Thinking...")
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.3
            )
            reply = completion.choices[0].message.content
            print(f"\n🤖 DocuMind: {reply}")
            
            # AI ke reply ko bhi history mein save karo taaki usko purani baat yaad rahe
            messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python documind.py <path_to_pdf_or_txt>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    print(f"📄 Reading {file_path}...")
    
    document_text = extract_text(file_path)
    
    # AI ke paas text bhej do chat shuru karne ke liye
    chat_with_doc(document_text)
