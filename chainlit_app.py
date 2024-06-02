import os
import chainlit as cl
from chainlit.types import ThreadDict
from typing import Dict, Optional
from chainlit.server import app
from api.controller import router
from api.service import AssistantService
from src.callbacks.chainlit_callback import ChainlitCallback
from src.utils.chat_utils import setup_history
from llama_index.core.callbacks import CallbackManager
from llama_index.core.base.llms.types import ChatMessage

app.include_router(router=router, prefix="/v1")

@cl.cache
def create_assistant_serivce():
    return AssistantService(callback_manager=CallbackManager([ChainlitCallback()]))

assistant_service = create_assistant_serivce()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return cl.User(identifier=username, metadata={"role": "guest", "provider": "credentials"})

# @cl.oauth_callback
# def oauth_callback(
#   provider_id: str,
#   token: str,
#   raw_user_data: Dict[str, str],
#   default_user: cl.User,
# ) -> Optional[cl.User]:
#   return default_user

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    cl.user_session.set("query_engine", assistant_service.query_engine)
    
    await cl.Message(
        author="Assistant", content="Hello! Im an AI assistant. How may I help you?"
    ).send()
    

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    history = setup_history(thread)
    cl.user_session.set("query_engine", assistant_service.query_engine)
    cl.user_session.set("history", history)

@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get("query_engine")
    
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    message_history = [ChatMessage(**message) for message in history]
    
    res = await cl.make_async(query_engine.stream_chat)(message.content, message_history)
    # res = query_engine.stream_chat(message.content)

    msg = cl.Message(content="", author="Assistant")

    for token in res.response_gen:
        await msg.stream_token(token)
        
    await msg.send()
    
    history.append({"role": "assistant", "content": res.response})