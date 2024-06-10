from chainlit.types import ThreadDict
from src.tasks.question_recommend_task import QuestionRecommender
import chainlit as cl

def setup_history(thread: ThreadDict):
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    history = []
    
    for message in root_messages:
        if message["type"] == "user_message":
            history.append({"role": "user",  "content": message["output"]})
            
        else:
            history.append({"role": "assistant", "content": message["output"]})

    return history


def handle_next_question_generation(tools: list, query_str: str, llm_response: str):
    
    question_recommender = QuestionRecommender.from_defaults()
    recommended_questions = question_recommender.generate(
        tools=[tool.metadata for tool in tools], 
        query_str=query_str, 
        llm_response=llm_response)
    
    return [q.sub_question for q in recommended_questions]


def handle_generate_actions(questions):
    
    assistant_service = cl.user_session.get("assistant_service")
    for question in questions:
        @cl.action_callback(question)
        async def next_question(action):
            message = cl.Message(content=action.value, author=cl.user_session.get("user").identifier)
            await message.send()
            await assistant_service.aon_message(message)