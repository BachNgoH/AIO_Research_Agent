import os
import re
import pypdf.errors
import requests
import pypdf  
from scholarly import scholarly
from urllib.parse import unquote
from bs4 import BeautifulSoup

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
    
    save_path += ".pdf"
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Paper {arxiv_id} has been downloaded successfully and saved to {save_path}.")
            return save_path
        else:
            print(f"Failed to download paper {arxiv_id}. HTTP status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while downloading the paper: {e}")
        return None


def download_paper_pdf(paper_name, save_path="./outputs/temp_paper"):
    """
    Downloads the PDF of a research paper given its name. If the paper is in HTML format,
    it downloads the HTML and saves it as text.

    Args:
        paper_name (str): The title of the research paper.
        save_path (str, optional): The path to save the PDF or text file. Defaults to "./outputs/temp_paper.pdf".

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    try:
        # Search for the paper
        search_query = scholarly.search_pubs(paper_name)
        pub = next(search_query)  # Get the first result (assuming it's the correct one)

        # Check if the paper has a PDF link
        if 'eprint_url' in pub:
            pdf_url = pub['eprint_url']
            if '.pdf' in pdf_url:
                pdf_url = pdf_url.split(".pdf")[0] + ".pdf"  # Ensure the URL ends with .pdf
                
            pdf_url = unquote(pdf_url)
        else:
            print(f"No PDF link found for paper: {paper_name}")
            return None

        # Download the PDF or HTML content
        os.makedirs("./outputs", exist_ok=True)  # Create the directory if it doesn't exist

        response = requests.get(pdf_url)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')

            if 'application/pdf' in content_type:
                file_mode = 'wb'
                save_path += '.pdf'
            elif 'text/html' in content_type:
                file_mode = 'w'
                response.encoding = response.apparent_encoding  # Correct encoding for text files
                save_path += '.html'
            else:
                print(f"Unsupported content type: {content_type}")
                return None

            with open(save_path, file_mode) as file:
                file.write(response.content)
                
            print(f"Content downloaded to: {save_path}")
            return save_path
        else:
            print(f"Failed to download from: {pdf_url}. HTTP status code: {response.status_code}")
            return None
    except StopIteration:
        print(f"Paper not found: {paper_name}")
        return None
    except Exception as e:
        print(f"Error downloading content: {e}")
        return None



def download_paper(arxiv_id=None, paper_title = None, save_path="./outputs/temp_paper.pdf"):
    if paper_title:
        try:
            return download_paper_pdf(paper_title, save_path)
    
        except Exception as e:
            print(f"An error occurred while downloading the paper: {e}, download with arxiv_id")
            if arxiv_id:
                return download_arxiv_paper(arxiv_id, save_path)
    elif arxiv_id:
        return download_arxiv_paper(arxiv_id, save_path)
    
    print("Please provide either arxiv_id or paper_title")
    return None



def extract_text_from_document(file_path):
    """
    Extracts text content from a PDF or HTML file.

    Parameters:
    file_path (str): The path to the file.

    Returns:
    str: The extracted text content, or an empty string if an error occurs.
    """
    try:
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:  # Open in binary mode for PDFs
                reader = pypdf.PdfReader(file)
                text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        elif file_path.endswith('.html'):
            with open(file_path, 'r', encoding='utf-8') as file:  # Open in text mode for HTMLs
                soup = BeautifulSoup(file, 'html.parser')
                text = soup.get_text()
        else:
            raise ValueError("Unsupported file type. Only PDF and HTML are supported.")

        return text
    
    except FileNotFoundError:
        print(f"File not found at the specified path: {file_path}")
        return ""
    except pypdf.errors.PdfReadError:
        print(f"Error reading the PDF file at: {file_path}. It may be corrupted or encrypted.")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred while extracting text: {e}")
        return ""
