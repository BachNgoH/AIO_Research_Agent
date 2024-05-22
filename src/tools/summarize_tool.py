import os
import pypdf.errors
import requests
import pypdf  
import scholarly
import time
from urllib.parse import unquote
from datetime import datetime
from llama_index.core.tools import FunctionTool
from llama_index.llms.gemini import Gemini
from src.constants import STREAM
import chainlit as cl
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

def download_arxiv_paper(arxiv_id = None, save_path="./outputs/temp_paper.pdf"):
    """
    Downloads a paper from arXiv given its ID and saves the PDF file.

    Parameters:
    arxiv_id (str): The arXiv ID of the paper to download.
    save_path (str): The path where the PDF file will be saved.

    Returns:
    bool: True if the download was successful, False otherwise.
    """
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Paper {arxiv_id} has been downloaded successfully and saved to {save_path}.")
            return True
        else:
            print(f"Failed to download paper {arxiv_id}. HTTP status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred while downloading the paper: {e}")
        return False


def download_paper_pdf(paper_name, save_path="./outputs/temp_paper.pdf"):
    """
    Downloads the PDF of a research paper given its name.

    Args:
        paper_name (str): The title of the research paper.
        save_directory (str, optional): The directory to save the PDF. Defaults to "downloaded_papers".

    Returns:
        str: The path to the downloaded PDF file, or None if the download failed.
    """

    try:
        # Search for the paper
        search_query = scholarly.scholarly.search_pubs(paper_name)
        pub = next(search_query)  # Get the first result (assuming it's the correct one)
        print(pub)
        # Check if the paper has a PDF link
        if pub['eprint_url']:
            pdf_url = pub['eprint_url']
            pdf_url = unquote(pdf_url)
        else:
            print(f"No PDF link found for paper: {paper_name}")
            return None

        # Download the PDF
        os.makedirs("./outputs", exist_ok=True)  # Create the directory if it doesn't exist

        response = requests.get(pdf_url)
        with open(save_path, 'wb') as file:
            file.write(response.content)

        print(f"PDF downloaded to: {save_path}")
        return True
    except StopIteration:
        print(f"Paper not found: {paper_name}")
        return False
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return False

def download_paper(arxiv_id=None, paper_title = None, save_path="./outputs/temp_paper.pdf"):
    if paper_title:
        return download_paper_pdf(paper_title, save_path)
    elif arxiv_id:
        return download_arxiv_paper(arxiv_id, save_path)
    
    print("Please provide either arxiv_id or paper_title")
    return False

def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a PDF file.

    Parameters:
    pdf_path (str): The path to the PDF file.

    Returns:
    str: The extracted text content, or an empty string if an error occurs.
    """

    try:
        with open(pdf_path, 'rb') as file:  # Open in binary mode for PyPDF2
            reader = pypdf.PdfReader(file)  # Create a PdfReader object
            text = ""

            for page in reader.pages:  # Iterate directly over pages for cleaner code
                text += page.extract_text()

        return text
    
    except FileNotFoundError:
        print(f"File not found at the specified path: {pdf_path}")
        return ""
    except pypdf.errors.PdfReadError:
        print(f"Error reading the PDF file at: {pdf_path}. It may be corrupted or encrypted.")
        return ""
    except Exception as e:  # Catch any other unexpected errors
        print(f"An unexpected error occurred while extracting text: {e}")
        return ""


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
        
        file_path = f"./outputs/temp_paper_{datetime.now()}.pdf"
        if download_paper(arxiv_id, paper_title, file_path):
            text_content = extract_text_from_pdf(file_path)
            print("Extracted text content:")
                
            prompt = summarize_template.format(content=text_content)
            try:
                if STREAM:
                    msg = cl.Message(content="", author="Summarize Assistant")                        

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
            return f"Cannot find paper with id {arxiv_id}."
    
    async def asummarize(arxiv_id: str):
        """Summarize the paper with the given arXiv ID."""
        file_path = "./outputs/temp_paper.pdf"
        if download_arxiv_paper(arxiv_id, file_path):
            text_content = extract_text_from_pdf(file_path)
            print("Extracted text content:")
                
            prompt = summarize_template.format(content=text_content)
            try:
                if STREAM:
                    msg = cl.Message(content="", author="Summarize Assistant")

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