import streamlit as st
import requests
import json
from datetime import datetime
import os

# ========== CONFIG ==========
API_KEY = "AIzaSyDDbnI2OUDk7cjiTLcRAMs8smEAI7c1Syc"   # replace with your API key
MODEL = "gemini-2.0-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
CHAT_DIR = "saved_chats"   # folder to store all chats

# Ensure folder exists
os.makedirs(CHAT_DIR, exist_ok=True)

# ========== FUNCTIONS ==========
def gemini_response(history):
    headers = {"Content-Type": "application/json"}
    data = {"contents": history}
    response = requests.post(API_URL, headers=headers, json=data)
    resp_json = response.json()
    try:
        return resp_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return f"⚠️ Error: {resp_json}"

def save_history():
    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(CHAT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(st.session_state.history, f, ensure_ascii=False, indent=2)
    return filename

def load_history(filename):
    filepath = os.path.join(CHAT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        st.session_state.history = json.load(f)

def list_chats():
    return sorted([f for f in os.listdir(CHAT_DIR) if f.endswith(".json")])

# ========== STREAMLIT APP ==========
st.set_page_config(page_title="Chatbot", layout="wide")
st.title("💬 Gemini Chatbot (with Memory & Chat Manager)")

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# ========== SIDEBAR ==========
st.sidebar.header("📂 Chat Manager")

# List saved chats
chats = list_chats()
selected_chat = st.sidebar.selectbox("Open a saved chat:", ["➕ New Chat"] + chats)

# Load selected chat
if selected_chat != "➕ New Chat":
    load_history(selected_chat)
    st.sidebar.success(f"Loaded: {selected_chat}")

# Button to save current chat
if st.sidebar.button("💾 Save Current Chat"):
    filename = save_history()
    st.sidebar.success(f"Saved as {filename}")

# Button to start new chat
if st.sidebar.button("🗑️ Start New Chat"):
    st.session_state.history = []
    st.sidebar.info("Started a new chat!")

# ========== MAIN CHAT WINDOW ==========
user_input = st.chat_input("Type your message...")

if user_input:
    # Append user message
    st.session_state.history.append({"role": "user", "parts": [{"text": user_input}]})

    # Get response
    bot_reply = gemini_response(st.session_state.history)

    # Append bot reply
    st.session_state.history.append({"role": "model", "parts": [{"text": bot_reply}]})

# Display chat history
for msg in st.session_state.history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["parts"][0]["text"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["parts"][0]["text"])
