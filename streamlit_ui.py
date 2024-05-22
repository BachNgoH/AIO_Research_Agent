import streamlit as st 
import requests
from datetime import datetime
import streamlit.components.v1 as components


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="localbot", page_icon="🧑‍💼", layout="wide")
    
    
def send_query(text, api_key=None):
    headers = {"Content-Type": "application/json"}
    data={"message": text, "api_key": api_key}
    resp = requests.post("http://localhost:8008/v1/complete", json=data, headers=headers , stream=True)
    return resp

def run_app(username):
    st.sidebar.header("Visualization")
    # with st.sidebar:

    #     graph_cache_file = './outputs/nx_graph.html'
        
    #     HtmlFile = open(graph_cache_file, 'r', encoding='utf-8')
    #     source_code = HtmlFile.read()
    #     components.html(source_code, height = 500, width=500)
    # api_key = st.sidebar.text_input("Enter Groq API Key", key="api_key", type="password")
    
    # col1, col2 = st.columns([2, 1])
    
    # with col1: 
    st.title("💬 Chatbot")
    st.caption("🚀 I'm a Local Bot")    
    # Function to append and display a new message
    def append_and_display_message(role, content, links=None):
        if links:
            # Embed each link as a Markdown hyperlink
            for link in links:
                st.page_link(link, label=link)
        st.session_state.messages.append({"role": role, "content": content})
        st.chat_message(role).write(content)

    if "messages" not in st.session_state:
        # Load chat history from the database
        st.session_state["messages"] = []

        # Start with a greeting from the assistant if no history is found
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]
            
    # Initialize a unique chatID and session state for messages if not already present
    if "chatID" not in st.session_state:
        st.session_state["chatID"] = f"{username}-{str(datetime.now())}"

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    # Initialize the QA system using caching
    # translater = Translation(from_lang="en", to_lang='vi', mode='translate') 
    if query := st.chat_input():
        append_and_display_message("user", query)
        
        res = send_query(query)
            
        res.raise_for_status()
        
        # data = res.json()
        # answer = data["completion"]
        # links = data.get("sources", [])
        # with st.sidebar:

        #     graph_cache_file = './outputs/nx_graph.html'
            
        #     HtmlFile = open(graph_cache_file, 'r', encoding='utf-8')
        #     source_code = HtmlFile.read()
        #     components.html(source_code, height = 500, width=500)
            
        with st.chat_message("assistant"):
            # Create a placeholder for streaming messages
            message_placeholder = st.empty()
            full_response = ""

            for chunk in res.iter_content(
                chunk_size=None, decode_unicode=True
            ):
                # print(chunk)
                # try:
                streaming_resp = chunk
                full_response += streaming_resp
                message_placeholder.markdown(full_response + "▌")
                # except:
                    # continue
            message_placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )        
        # Save the chat history to the database
            
    # with col2:
    #     st.header("Don't know what to do yet!")

if __name__ == "__main__":
    username = "bachngo"
    run_app(username)
