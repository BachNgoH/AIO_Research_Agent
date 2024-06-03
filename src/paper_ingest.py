import os
import torch
import chromadb
import qdrant_client
import json
import sys
import pandas as pd
from datetime import datetime
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Document
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from constants import EMBEDDING_MODEL_NAME, EMBEDDING_SERVICE, cfg
tqdm.pandas()

device_type = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_data():
    
    cols = ['id', 'title', 'abstract', 'categories', 'update_date', 'authors']
    data = []
    file_name = './data/arxiv-metadata-oai-snapshot.json'


    with open(file_name, encoding='latin-1') as f:
        for line in f:
            doc = json.loads(line)
            lst = [doc['id'], doc['title'], doc['abstract'], doc['categories'], doc['update_date'], doc['authors_parsed']]
            data.append(lst)

    df_data = pd.DataFrame(data=data, columns=cols)
    
    topics = ['cs.AI', 'cs.CV', 'cs.IR', 'cs.LG', 'cs.CL']

    # Create a regular expression pattern that matches any of the topics
    # The pattern will look like 'cs.AI|cs.CV|cs.IR|cs.LG|cs.CL'
    pattern = '|'.join(topics)

    # Filter the DataFrame to include rows where the 'categories' column contains any of the topics
    # The na=False parameter makes sure that NaN values are treated as False
    df_data = df_data[df_data['categories'].str.contains(pattern, na=False)]
    
    def clean_text(x):
        
        # Replace newline characters with a space
        new_text = " ".join([c.strip() for c in x.replace("\n", "").split()])
        # Remove leading and trailing spaces
        new_text = new_text.strip()
        
        return new_text

    df_data['title'] = df_data['title'].progress_apply(clean_text)
    df_data['abstract'] = df_data['abstract'].progress_apply(clean_text)

    df_data['prepared_text'] = df_data['title'] + '\n ' + df_data['abstract']
    return df_data

def ingest_paper():
    
    df_data = load_data()
    
    arxiv_documents = [Document(text=prepared_text, 
                                metadata={'paper_id': id, 
                                           'title': title, 
                                           'date': datetime.strptime(date, "%Y-%m-%d").timestamp()}) 
                       for _, (id, title, _, _, date, authors, prepared_text) in list(df_data.iterrows())]
        
    if EMBEDDING_SERVICE == "ollama":
        embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL_NAME)
    elif EMBEDDING_SERVICE == "hf":
        embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME, cache_folder="./models", device=device_type, embed_batch_size=10)
    elif EMBEDDING_SERVICE == "openai":
        embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL_NAME, api_key=os.environ["OPENAI_API_KEY"])
    else:
        raise NotImplementedError()   
    
    
    if cfg.MODEL.VECTOR_STORE == "chroma":
        client = chromadb.PersistentClient(path="./DB/arxiv")
        chroma_collection = client.get_or_create_collection(cfg.MODEL.PAPER_COLLECTION_NAME)


        # Create vector store
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    elif cfg.MODEL.VECTOR_STORE == "qdrant":
        client = qdrant_client.QdrantClient(host="localhost", port=6333)
        vector_store = QdrantVectorStore(client=client, collection_name=cfg.MODEL.PAPER_COLLECTION_NAME)
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        arxiv_documents, storage_context=storage_context, embed_model=embed_model, show_progress=True
    )
    
if __name__ == "__main__":
    ingest_paper()