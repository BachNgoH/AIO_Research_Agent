import chainlit as cl
from chainlit.types import ThreadDict
from chainlit.server import app
from api.controller import router
from api.service import AssistantService
from src.callbacks.chainlit_callback import ChainlitCallback
from src.utils.chat_utils import setup_history, handle_next_question_generation
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

@cl.action_callback("Summarize any paper!")
async def on_summarize_action(action):
    await cl.Message(content=f"Executed {action.name}").send()
    # Optionally remove the action button from the chatbot user interface
    await action.remove()
    
    
@cl.action_callback("Search papers in any topic!")
async def on_search_action(action):
    await cl.Message(content=f"Executed {action.name}").send()
    # Optionally remove the action button from the chatbot user interface
    await action.remove()
    
    
@cl.action_callback("Get the latest trends in AI!")
async def on_trend_action(action):
    await cl.Message(content=f"Executed {action.name}").send()
    # Optionally remove the action button from the chatbot user interface
    await action.remove()


@cl.action_callback("next_question")
async def next_question(action):
    message = cl.Message(content=action.value, author="User")
    await message.send()
    await assistant_service.aon_message(message)

@cl.on_chat_start
async def on_chat_start():
    await assistant_service.aon_start()

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Morning routine ideation",
            message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
            icon="/public/idea.svg",
            ),

        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
            icon="/public/learn.svg",
            ),
        cl.Starter(
            label="Python script for daily email reports",
            message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
            icon="/public/terminal.svg",
            ),
        cl.Starter(
            label="Text inviting friend to wedding",
            message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
            icon="/public/write.svg",
            )
        ]

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    await assistant_service.aon_resume(thread)

@cl.on_message
async def on_message(message: cl.Message):
    await assistant_service.aon_message(message)