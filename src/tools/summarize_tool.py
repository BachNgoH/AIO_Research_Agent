import os
from datetime import datetime
from llama_index.core.tools import FunctionTool
from llama_index.llms.gemini import Gemini
from src.constants import STREAM
from src.utils.load_papers_utils import download_paper, extract_text_from_document
import chainlit as cl
import time
from chainlit import run_sync

summarize_template = """
You are an expert researcher, summarize the key points of the given paper.

===================================
If the paper is a research paper, the summary should include the following sections:

Introduction:

- Briefly describe the context and motivation for the study.
- What problem or question does the paper address?

Methods:

- Outline the methodology used in the study.
- What approach or techniques were used to address the problem?

Results:

- Summarize the main findings or results of the study.
- What are the key outcomes?

Discussion:

- Interpret the significance of the results.
- How do the findings contribute to the field?
- Are there any limitations mentioned?

Conclusion:

- Summarize the main conclusions of the paper.
- What future directions or questions do the authors suggest?

===================================
If the paper is a Survey paper, the summary should include the following sections:

Introduction and Motivation:

- What is the background and context of this survey?
- What motivated the authors to conduct this survey?
- Why is this survey significant in its field?

Scope of the Survey:

- What specific topics, technologies, methods, or trends does this survey cover?
- Are there any specific boundaries or limitations to what is included in the survey?

Classification and Taxonomy:

- Does the survey provide a classification scheme or taxonomy? If so, what is it?
- What are the main categories or groups identified in the survey?

Literature Review:

- Which key studies, papers, or contributions are highlighted in the survey?
- What trends, patterns, and emerging themes are identified from the literature?

Comparative Analysis:

- How are different approaches, methods, or technologies compared in the survey?
- What are the pros and cons of these various approaches?

Methodologies and Techniques:

- What common methodologies and techniques are discussed?
- Are there any novel or innovative methods mentioned in the survey?


Applications and Implications:

- What are the practical applications of the surveyed technologies or methods?
- What are the implications of the survey findings for practice and future research?


Challenges and Open Issues:

- What are the current challenges or limitations identified in the field?
- What research gaps and potential areas for future research are pointed out?

Conclusions and Future Directions:

- What are the main findings summarized in the survey?
- What directions for future research and development do the authors suggest?

References:

- What are some of the most important references cited in the survey, particularly those seminal to the field?


####
Here is the paper content

{content}

"""

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
                
            prompt = summarize_template.format(content=text_content)
            try:
                if STREAM:
                    msg = cl.Message(content="", author="Assistant")                        

                    response = summarize_llm.stream_complete(prompt)
                    for token in response:
                        run_sync(msg.stream_token(str(token)))
                    
                    run_sync(msg.send())
                    return "Summarize completed and responded to user. DON'T make any further response until the next message from user"
                else:
                    response = summarize_llm.complete(prompt)
                    
            except Exception as _:
                time.sleep(120)
                response = summarize_llm.complete(prompt)

            # run_sync(cl.Message(content=response.text, author="Summarize Assistant").send())
            return response
        else:
            return f"Cannot find or download paper with id {arxiv_id}."
    
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
                
            prompt = summarize_template.format(content=text_content)
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