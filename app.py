

import streamlit as st
import asyncio
import websockets
import json
import threading


WEBSOCKET_URL = st.secrets["WEBSOCKET_URL"]

st.title("Chat Bot")

css = """
    <style>
    .st-emotion-cache-4z1n4l{
    visibility: hidden;
    }
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
    """
st.markdown(css,

    unsafe_allow_html=True
)


import json
file_path = "test.json"
def update_time(data=None):
    with open(file_path, 'w') as json_file:
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        if not(data):
            json.dump({"updated_time":date_time}, json_file)
        else:
            json.dump(data, json_file)


def read_dict_from_file():
    try:
        read_dict = None
        if not(not os.path.exists(file_path) or os.path.getsize(file_path) == 0):
            with open(file_path, 'r') as json_file:
                read_dict = json.load(json_file)
        return read_dict
    except:
        return read_dict


response_placeholder = st.empty()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = ['<div class="bot"><p>Welcome to ChatBot!</p></div>']
    response_placeholder.markdown("\n".join(st.session_state.chat_history), unsafe_allow_html=True)




user_input = st.chat_input("Type your message here:", key=f"user_input")
async def chat_with_websocket(message):
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        if message == '__dummy_invoke__':
            await websocket.send(json.dumps({"action": "$connect"}))
        else:
            # now = datetime.now()
            # dict_ = {"updated_at":now,"query_updated_at":now}
            # update_time(dict_)
            await websocket.send(json.dumps({"action": "message", "message": message}))
            bot_response = "" 
            while True:
                try:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    res = response_data.get('message')
                    if res:
                        if res == "dummy_response":
                            break
                        bot_response+=res
                        st.session_state.chat_history[-1] = f'<div class="bot"><p>{bot_response}</p></div>'
                        response_placeholder.markdown("\n".join(st.session_state.chat_history), unsafe_allow_html=True)
                except websockets.exceptions.ConnectionClosed:
                    if bot_response == "":
                        bot_response = "Sorry, I'm unable load the data please try again"
                        st.session_state.chat_history[-1] = f'<div class="bot"><p>{bot_response}</p></div>'
                
        


time_period_in_sec = 120
# query_seconds_diff_perios = 60*60 
def periodic_call():
    read_dict = None
    seconds_diff = time_period_in_sec
    # query_seconds_diff = 0
    # latest_query_at = None
    print("maximum 90 seconds")
    try:
        read_dict = read_dict_from_file()
        if not read_dict:
            asyncio.run(chat_with_websocket("__dummy_invoke__"))
        else:
            lates_updated_at = read_dict.get("updated_time")
            lates_updated_at = datetime.strptime(lates_updated_at, "%m/%d/%Y, %H:%M:%S")
            seconds_diff = (datetime.now() - lates_updated_at).total_seconds()
        # latest_query_at = read_dict.get("query_updated_at")
        # latest_query_at = datetime.strptime(latest_query_at, "%m/%d/%Y, %H:%M:%S")
        # query_seconds_diff = (datetime.now() - latest_query_at).total_seconds()
    except:
        pass
    if seconds_diff>=time_period_in_sec:
        update_time()
        asyncio.run(chat_with_websocket("__dummy_invoke__"))
        print("triggered after 120 seconda")
    threading.Timer(90, periodic_call).start()

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