from chainlit.types import ThreadDict

def setup_history(thread: ThreadDict):
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    history = []
    
    for message in root_messages:
        if message["type"] == "user_message":
            history.append({"role": "user",  "content": message["output"]})
            
        else:
            history.append({"role": "assistant", "content": message["output"]})

    return history