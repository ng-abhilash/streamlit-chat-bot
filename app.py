

import streamlit as st
import asyncio
import websockets
import json
import threading


WEBSOCKET_URL = st.secrets["WEBSOCKET_URL"]

st.title("Chat Bot")

st.markdown(
    """
    <style>
    .user {
        text-align: right;
        margin: 10px;
        padding: 10px;
        background-color: #dcf8c6;
        border-radius: 15px;
        max-width: 80%;
        align-self: flex-end;
    }
    .bot {
        text-align: left;
        margin: 10px;
        padding: 10px;
        background-color: #f1f0f0;
        border-radius: 15px;
        max-width: 80%;
        align-self: flex-start;
    }
    div[data-testid="stMarkdownContainer"] {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = ['<div class="bot"><p>Welcome to ChatBot!</p></div>']


response_placeholder = st.empty()


user_input = st.chat_input("Type your message here:", key=f"user_input")
async def chat_with_websocket(message):
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(json.dumps({"action": "message", "message": message}))        
        bot_response = "" 
        while True:
            try:
                response = await websocket.recv()
                response_data = json.loads(response)
                res = response_data.get('message')
                if res:
                    if res == "Internal server error":
                        break
                    bot_response+=res
                    st.session_state.chat_history[-1] = f'<div class="bot"><p>{bot_response}</p></div>'
                    response_placeholder.markdown("\n".join(st.session_state.chat_history), unsafe_allow_html=True)
            except websockets.exceptions.ConnectionClosed:
                if bot_response == "":
                    bot_response = "Sorry, I'm unable load the data please try again"
                    st.session_state.chat_history[-1] = f'<div class="bot"><p>{bot_response}</p></div>'

def periodic_call():
    print("started peroic_Call")
    asyncio.run(chat_with_websocket("user_input__"))
    threading.Timer(60, periodic_call).start()

if 'timer_started' not in st.session_state:
    response_placeholder.markdown("\n".join(st.session_state.chat_history), unsafe_allow_html=True)
    st.session_state.timer_started = True
    periodic_call()

if user_input:
    if user_input.strip() != "":
        st.session_state.chat_history.append(f'<div class="user"><p>{user_input}</p></div>')
        st.session_state.chat_history.append('<div class="bot"><p>...</p></div>')
        response_placeholder.markdown("\n".join(st.session_state.chat_history), unsafe_allow_html=True)
        asyncio.run(chat_with_websocket(user_input))
    else:
        response_placeholder.markdown("\n".join(st.session_state.chat_history), unsafe_allow_html=True)