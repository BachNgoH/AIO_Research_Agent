import os
from typing import Optional
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.gemini import Gemini
from llama_index.core.agent import AgentRunner
from llama_index.core.callbacks import CallbackManager
from src.agents.assistant_agent import AssistantAgent
from src.agents.gemini_agent import GeminiForFunctionCalling
from llama_index.core import Settings
from src.tools.paper_search_tool import load_paper_search_tool, load_daily_paper_tool, load_get_time_tool
from src.tools.web_search_tool import load_web_search_tool
from src.tools.summarize_tool import load_summarize_tool
from src.constants import SYSTEM_PROMPT
from starlette.responses import StreamingResponse, Response
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import logging
from src.constants import (
    SERVICE,
    TEMPERATURE,
    MODEL_ID,
    STREAM
)
load_dotenv(override=True)


class AssistantService:
    query_engine: AgentRunner
    tools_dict: dict
    
    def __init__(self, callback_manager: Optional[CallbackManager] = None):
        self.callback_manager = callback_manager
        self.query_engine = self.create_query_engine()
        
    def load_tools(self):
        paper_search_tool = load_paper_search_tool()
        paper_summarize_tool = load_summarize_tool()
        daily_paper_tool = load_daily_paper_tool()
        get_time_tool = load_get_time_tool()
        web_search_tool = load_web_search_tool()
        
        return [paper_search_tool, paper_summarize_tool, daily_paper_tool, get_time_tool, web_search_tool]
    
    def create_query_engine(self):
        """
        Creates and configures a query engine for routing queries to the appropriate tools.
        
        This method initializes and configures a query engine for routing queries to specialized tools based on the query type.
        It loads a language model, along with specific tools for tasks such as code search and paper search.
        
        Returns:
            AgentRunner: An instance of AgentRunner configured with the necessary tools and settings.
        """
        
        llm = self.load_model(SERVICE, MODEL_ID)
        Settings.llm = llm
        tools = self.load_tools()
        
        if SERVICE == "gemini":
            query_engine = GeminiForFunctionCalling(
                tools=tools,
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=TEMPERATURE
            )
        else:
            query_engine = AssistantAgent.from_tools(
                tools=tools,
                verbose=True,
                llm=llm,
                system_prompt = SYSTEM_PROMPT,
                callback_manager=self.callback_manager
            )
        
        return query_engine
    
    def load_model(self, service, model_id):
        """
        Select a model for text generation using multiple services.
        Args:
            service (str): Service name indicating the type of model to load.
            model_id (str): Identifier of the model to load from HuggingFace's model hub.
        Returns:
            LLM: llama-index LLM for text generation
        Raises:
            ValueError: If an unsupported model or device type is provided.
        """
        logging.info(f"Loading Model: {model_id}")
        logging.info("This action can take a few minutes!")

        if service == "ollama":
            logging.info(f"Loading Ollama Model: {model_id}")
            return Ollama(model=model_id, temperature=TEMPERATURE)
        elif service == "openai":
            logging.info(f"Loading OpenAI Model: {model_id}")
            return OpenAI(model=model_id, temperature=TEMPERATURE, api_key=os.getenv("OPENAI_API_KEY"))
        elif service == "groq":
            logging.info(f"Loading Groq Model: {model_id}")    
            return Groq(model=model_id, temperature=TEMPERATURE, api_key=os.getenv("GROQ_API_KEY"))
        elif service == "gemini":
            logging.info(f"Loading Gemini Model: {model_id}")
            return Gemini(model=model_id, temperature=TEMPERATURE, api_key=os.getenv("GOOGLE_API_KEY"))
        else:
            raise NotImplementedError("The implementation for other types of LLMs are not ready yet!")
    
    def predict(self, prompt):
        """
        Predicts the next sequence of text given a prompt using the loaded language model.

        Args:
            prompt (str): The input prompt for text generation.

        Returns:
            str: The generated text based on the prompt.
        """
        # Assuming query_engine is already created or accessible
        if STREAM:
            # self.query_engine.memory.reset()
            streaming_response = self.query_engine.stream_chat(prompt)
            
            return StreamingResponse(streaming_response.response_gen, media_type="application/text; charset=utf-8")
            # return StreamingResponse(streaming_response.response_gen, media_type="application/text; charset=utf-8")
            
        else:
            return Response(self.query_engine.chat(prompt).response, media_type="application/text; charset=utf-8")
        