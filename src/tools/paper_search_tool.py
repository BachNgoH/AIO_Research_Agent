import os
import torch
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.core.schema import MetadataMode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.tools import FunctionTool

from src.constants import EMBEDDING_MODEL_NAME, EMBEDDING_SERVICE
from datetime import datetime
import time
from pyvis.network import Network
from src.tools.graph_search_tool import create_ego_graph

simple_content_template = """
Paper link: {paper_link}
Paper: {paper_content}
"""

# class PaperYearNodePostprocessor(BaseNodePostprocessor):
#     def _postprocess_nodes(
#         self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle]
#     ) -> List[NodeWithScore]:
#         paper_year = query_bundle.query_str.split("\n")[0]
#         if paper_year == "None":
#             return nodes
#         filtered_nodes = []
#         for node in nodes:
#             date = node.metadata.get('date', '')  # Get the date or default to empty string if not present
#             if date:  # Check if date is not empty
#                 date_year = date.split('-')[0]  # Extract the year from the 'YYYY-MM-DD' format
#                 if date_year == str(paper_year):  # Compare the extracted year with the target year
#                     filtered_nodes.append(node)
#         return filtered_nodes


def load_paper_search_tool():
    device_type = torch.device("cuda" if torch.cuda.is_available() else "cpu") 
    if EMBEDDING_SERVICE == "ollama":
        embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL_NAME)
    elif EMBEDDING_SERVICE == "hf":
        embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME, cache_folder="./models", device=device_type, embed_batch_size=64)
    elif EMBEDDING_SERVICE == "openai":
        embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL_NAME, api_key=os.environ["OPENAI_API_KEY"])
    else:
        raise NotImplementedError()   


    chroma_client = chromadb.PersistentClient(path="./DB/arxiv")
    chroma_collection = chroma_client.get_or_create_collection("gemma_assistant_arxiv_papers")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)    
    # load the vectorstore
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    paper_index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context, embed_model=embed_model)
    
    # node_postporcessor = PaperYearNodePostprocessor()
    
    # graph = load_graph_data()
    graph = None
    
    def retrieve_paper(query_str: str, start_date: str = None, end_date: str = None):
        
        """
        Useful for answering questions about papers, research. Add paper year if needed.  
        Retrieves papers based on the given query string and optional year.

        Args:
            query_str (str): The query string used to search for papers.
            start_date (str, optional): The start range of retrieve papers. Defaults to "None".
            end_date (str, optional): The end range of retrieve papers. Defaults to today.
            
        Returns:
            list: A list of retrieved papers, each containing the paper link and content.
        """

        db_query = None
        
        if start_date != None:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            
            db_query = {"where": {"date": {
                    "$gt": datetime(start_date_obj.year, start_date_obj.month, start_date_obj.day).timestamp()
                }}
            }
        
        start = time.time()

        paper_retriever = paper_index.as_retriever(
            similarity_top_k=5,
            vector_store_kwargs=db_query if db_query else {}
        )
        
        end = time.time()
        print("Time to create retriever: ", end-start)
        
        retriever_response = paper_retriever.retrieve(query_str)
        print(len(retriever_response))
        retriever_result = []
        for n in retriever_response:
            paper_id = n.metadata["paper_id"]
            paper_content = n.node.get_content(metadata_mode=MetadataMode.LLM)
            
            paper_link = f"https://arxiv.org/abs/{paper_id}"
            retriever_result.append(
                simple_content_template.format(
                    paper_link=paper_link, 
                    paper_content=paper_content
                )
            )
            
        # combined_ego_graph = create_ego_graph(retriever_response, service="ss", graph=graph)
        # nt = Network(notebook=True)#, font_color='#10000000')
        # nt.from_nx(combined_ego_graph)
        # for node in nt.nodes:
        #     node['value'] = combined_ego_graph.nodes[node['id']]['size']

        # nt.save_graph("./outputs/nx_graph.html")
        
        return "\n================\n".join(retriever_result)
            
        
    # paper_search_tool = QueryEngineTool.from_defaults(
    #     query_engine=paper_query_engine,
    #     description="Useful for answering questions related to scientific papers",
    # )
    return FunctionTool.from_defaults(retrieve_paper)


def load_daily_paper_tool():
    def get_latest_arxiv_papers():
        
        # Directory path
        directory = './outputs/DailyAIReports/daily_reports'

        # List all files in the directory
        files = os.listdir(directory)

        # Extract and convert dates to datetime objects
        file_dates = [(file, datetime.strptime(file.split('_')[-1].split(".")[0], '%Y-%m-%d')) for file in files]

        # Sort files based on date in descending order
        sorted_files = sorted(file_dates, key=lambda x: x[1], reverse=True)


        # Get the latest file
        latest_file = sorted_files[0][0]

        with open(os.path.join(directory, latest_file), 'r') as file:
            md_content = file.read()
            
            
        return f"Report Link: https://github.com/BachNgoH/DailyAIReports/blob/main/daily_reports/{latest_file.split('/')[-1]}\n{md_content}"
            
    return FunctionTool.from_defaults(get_latest_arxiv_papers, description="Useful for getting latest daily papers")


def load_get_time_tool():

    def get_current_time():
        """
        Returns the current time in the format: "YYYY-MM-DD HH:MM:SS".
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return FunctionTool.from_defaults(get_current_time)