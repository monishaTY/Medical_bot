import streamlit as st
from bytez import Bytez
import re

# Initialize Bytez SDK
sdk = Bytez("01e652718e0e753c64c35d90498e03da")
model = sdk.model("Qwen/Qwen3-4B-Instruct-2507")

SYSTEM_PROMPT = """
You are an AI medical assistant chatbot.

Your ONLY job:
- Answer questions ONLY if they are directly about symptoms, diseases, treatments, medicines, prevention, diet, or healthcare.
- If the question is NOT medical, you MUST reply:
  "I can only answer medical-related questions."

STRICT RULES (follow EXACTLY):
1. If the question is outside the medical domain, DO NOT answer it. DO NOT explain anything. Only reply: "I can only answer medical-related questions."
2. Use short, clear sentences.
3. If listing symptoms or steps, use bullet points.
4. Do NOT use markdown symbols like **.
5. Do NOT give extra explanations.
6. Never break rule 1, even if the user insists.
"""


def format_response(text: str) -> str:
    """
    Clean bot response:
    - Remove markdown **asterisks**
    - Bold only important medical words (via regex pattern)
    - Display line by line
    """
    # Remove stray markdown asterisks
    text = text.replace("**", "")

    # Define keywords to bold (add more as needed)
    important_words = [
        "Malaria", "Anopheles", "Fever", "Chills", "Sweating", "Headache",
        "Muscle pain", "Nausea", "Vomiting", "Fatigue", "Diagnosis",
        "Treatment", "Prevention"
    ]

    # Replace keywords with <b>keyword</b>
    for word in important_words:
        text = re.sub(rf"\b{word}\b", f"<b>{word}</b>", text, flags=re.IGNORECASE)

    # Split into lines by bullet or newline
    lines = [line.strip("-• ") for line in text.replace("\n", "•").split("•") if line.strip()]

    # Wrap each line in <div>
    formatted = "".join(f'<div style="margin-bottom:5px;">- {line}</div>' for line in lines)
    return formatted


def ask_medical_chatbot(user_message):
    result = model.run([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ])

    # Bytez returns Response class → extract output → content
    if hasattr(result, "output"):
        output = result.output
        if isinstance(output, dict) and "content" in output:
            return output["content"].strip()

    # If result is dict fallback
    if isinstance(result, dict):
        if "response" in result and "content" in result["response"]:
            return result["response"]["content"].strip()
        if "output" in result:
            return str(result["output"]).strip()

    # Fallback
    return str(result)




# ---------------- Streamlit Chat UI ----------------
st.set_page_config(page_title="AI Medical Assistant", page_icon="🩺", layout="wide")

st.markdown("""
<style>
.chat-box {
    max-height: 550px;
    overflow-y: auto;
    padding: 10px;
}
.bot-container, .user-container {
    display: flex;
    margin-bottom: 10px;
}
.bot-container img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 8px;
}
.user-container img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-left: 8px;
}
.bot-msg {
    background-color: #fff3cd;
    color: black;
    padding: 12px 15px;
    border-radius: 15px;
    max-width: 70%;
}
.user-msg {
    background-color: #d1e7dd;
    color: black;
    padding: 12px 15px;
    border-radius: 15px;
    max-width: 70%;
}
.bot-container { justify-content: flex-start; }
.user-container { justify-content: flex-end; }
</style>
""", unsafe_allow_html=True)

st.title("🩺 AI Medical Assistant")
st.caption("💡 Ask your health-related question. Bot messages are left, your messages are right.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(("assistant", "👋 Hello! I'm your AI medical assistant. Ask me about symptoms, recovery, or health tips."))

with st.sidebar:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            ("assistant", "👋 Hello! I'm your AI medical assistant. Ask me about symptoms, recovery, or health tips.")
        ]

# Chat display
chat_container = st.container()
bot_avatar = "https://i.ibb.co/Xx7QxKwx/image.png"
user_avatar = "https://i.ibb.co/1GxPZ8R4/image.png"

with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f'''
                <div class="user-container">
                    <div class="user-msg">{content}</div>
                    <img src="{user_avatar}">
                </div>
            ''', unsafe_allow_html=True)
        else:
            formatted_lines = format_response(content)
            st.markdown(f'''
                <div class="bot-container">
                    <img src="{bot_avatar}">
                    <div class="bot-msg">{formatted_lines}</div>
                </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your question..."):
    st.session_state.messages.append(("user", prompt))
    with chat_container:
        st.markdown(f'''
            <div class="user-container">
                <div class="user-msg">{prompt}</div>
                <img src="{user_avatar}">
            </div>
        ''', unsafe_allow_html=True)

    with st.spinner("Thinking..."):
        response = ask_medical_chatbot(prompt)
        st.session_state.messages.append(("assistant", response))
        formatted_response = format_response(response)
        with chat_container:
            st.markdown(f'''
                <div class="bot-container">
                    <img src="{bot_avatar}">
                    <div class="bot-msg">{formatted_response}</div>
                </div>
            ''', unsafe_allow_html=True)


