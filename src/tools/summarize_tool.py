import os
from datetime import datetime
from llama_index.core.tools import FunctionTool
from llama_index.llms.gemini import Gemini
from src.constants import STREAM
import chainlit as cl
import time
from chainlit import run_sync

from src.utils.load_papers_utils import download_paper, extract_text_from_document
from src.prompts.summarize_prompt import SUMMARIZE_PROMPT_TEMPLATE


def load_summarize_tool():
    
    summarize_llm = Gemini(model_name="models/gemini-1.5-flash-latest", api_key=os.environ["GOOGLE_API_KEY"])
    print("Load summarize LLM successfully.")
    
    def summarize(arxiv_id: str = None, paper_title: str = None):
        """
        Summarize the paper with the given arXiv ID or paper title.

        Parameters:
        - arxiv_id (str): The arXiv ID of the paper to summarize.
        - paper_title (str): The title of the paper, specify this or the arxiv_id.

        Returns:
        - str: The summary of the paper.
        """
        
        file_path = f"./outputs/temp_paper_{datetime.now()}"
        save_path = download_paper(arxiv_id, paper_title, file_path)
        if save_path:
            text_content = extract_text_from_document(save_path)
            print("Extracted text content:")
                
            prompt = SUMMARIZE_PROMPT_TEMPLATE.format(content=text_content)
            try:
                if STREAM:
                    msg = cl.Message(content="", author="Assistant")                        

                    response = summarize_llm.stream_complete(prompt)
                    for token in response:
                        run_sync(msg.stream_token(str(token)))
                    
                    run_sync(msg.send())
                    return {"content": "Summarize completed and responded to user. DON'T make any further response until the next message from user"}
                else:
                    response = summarize_llm.complete(prompt)
                    
            except Exception as _:
                time.sleep(120)
                response = summarize_llm.complete(prompt)

            # run_sync(cl.Message(content=response.text, author="Summarize Assistant").send())
            return {"content": response}
        else:
            return {"content":  f"Cannot find or download paper with id {arxiv_id}."}
    
    async def asummarize(arxiv_id: str = None, paper_title: str = None):
        """
        Summarize the paper with the given arXiv ID or paper title.

        Parameters:
        - arxiv_id (str): The arXiv ID of the paper to summarize.
        - paper_title (str): The title of the paper, specify this or the arxiv_id.

        Returns:
        - str: The summary of the paper.
        """
        
        
        file_path = f"./outputs/temp_paper_{datetime.now()}"
        save_path = download_paper(arxiv_id, paper_title, file_path)
        if save_path:
            text_content = extract_text_from_document(save_path)
            print("Extracted text content:")
                
            prompt = SUMMARIZE_PROMPT_TEMPLATE.format(content=text_content)
            try:
                if STREAM:
                    msg = cl.Message(content="", author="Assistant")

                    response = summarize_llm.stream_complete(prompt)
                    for token in response:
                        await msg.stream_token(token)
                    
                    await msg.send()
                else:
                    response = summarize_llm.complete(prompt)
                    
            except Exception as _:
                time.sleep(120)
                response = summarize_llm.acomplete(prompt)

            # run_sync(cl.Message(content=response.text, author="Summarize Assistant").send())
            return response
        else:
            return f"Cannot find paper with id {arxiv_id}."
    
    return FunctionTool.from_defaults(summarize, async_fn=asummarize)