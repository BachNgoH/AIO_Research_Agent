import requests
from datetime import datetime, timedelta
import time
import feedparser
import os
import torch
import chromadb
import sys
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Document
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from constants import EMBEDDING_MODEL_NAME, EMBEDDING_SERVICE
from src.tasks.report_task import generate_daily_report

def clean_text(x):
    
    # Replace newline characters with a space
    new_text = " ".join([c.strip() for c in x.replace("\n", "").split()])
    # Remove leading and trailing spaces
    new_text = new_text.strip()
    
    return new_text


def get_daily_arxiv_papers():
    max_results = 800
    categories = ['cs.AI', 'cs.CV', 'cs.IR', 'cs.LG', 'cs.CL']
    base_url = 'http://export.arxiv.org/api/query?'
    all_categories = [f'cat:{category}' for category in categories]
    search_query = '+OR+'.join(all_categories)
    
    paper_list = []
    start = 0
    today = datetime.utcnow().date()
    new_papers_found = True
    wait_time = 3

    while new_papers_found:
        query = f'search_query={search_query}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
        response = requests.get(base_url + query)
        feed = feedparser.parse(response.content)
        
        for r in feed.entries:
            paper_date = datetime.strptime(r['published'][:10], '%Y-%m-%d').date()
            if paper_date >= today - timedelta(1):
                new_papers_found = True
                paper_list.append(Document(text=f"""
Title: {clean_text(r['title'])}
{r['summary']}
                """, metadata={'paper_id': r['id'].split("/")[-1], 'title': clean_text(r['title']), 'date': r['published'][:10]}))
            else:
                new_papers_found = False
                break
        
        start += max_results
        time.sleep(wait_time)

    return paper_list


def ingest_paper(arxiv_documents):
    if EMBEDDING_SERVICE == "ollama":
        embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL_NAME)
    elif EMBEDDING_SERVICE == "hf":
        device_type=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME, cache_folder="./models", device=device_type, embed_batch_size=64)
    elif EMBEDDING_SERVICE == "openai":
        embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL_NAME, api_key=os.environ["OPENAI_API_KEY"])
    else:
        raise NotImplementedError()   
    print("Embed model loaded successfully.")
           
    chroma_client = chromadb.PersistentClient(path="./DB/arxiv")
    chroma_collection = chroma_client.get_or_create_collection("gemma_assistant_arxiv_papers")


    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    VectorStoreIndex.from_documents(
        arxiv_documents, storage_context=storage_context, embed_model=embed_model, show_progress=True
    )
    print("Indexing successfully.")
    
def daily_ingest_analyze():
    print("Getting papers.")
    arxiv_documents = get_daily_arxiv_papers()
    print(f"Load paper successfully, found {len(arxiv_documents)} papers.")
    
    ingest_paper(arxiv_documents)
    
    print("Generating daily report")
    generate_daily_report(arxiv_documents)
    
    
    