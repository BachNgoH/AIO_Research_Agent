import chainlit as cl
from chainlit.types import ThreadDict
from chainlit.server import app
from api.controller import router
from api.service import AssistantService
from src.callbacks.chainlit_callback import ChainlitCallback
from llama_index.core.callbacks import CallbackManager

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
            label="Update AI Trends!",
            message="Can you give me an overview of the latest research papers published today?",
            icon="/public/default.png",
            ),

        cl.Starter(
            label="Targeted paper search!",
            message="I'm looking for research papers on transfer learning in computer vision. Can you help me find the most relevant ones?",
            icon="/public/default.png",
            ),
        cl.Starter(
            label="Summarize any paper!",
            message="Could you provide a brief summary of the key findings from the Llama 2 paper?",
            icon="/public/default.png",
            ),
        cl.Starter(
            label="Find content from the web!",
            message="Can you help me find recent blog posts discussing advancements in deep learning techniques?",
            icon="/public/default.png",
            )
        ]

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    await assistant_service.aon_resume(thread)

@cl.on_message
async def on_message(message: cl.Message):
    await assistant_service.aon_message(message)