import os
import json
import requests
from typing import Optional
import dotenv
from llama_index.core.schema import MetadataMode
from llama_index.core.tools import FunctionTool
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.schema import NodeWithScore, Document

dotenv.load_dotenv(override=True)

simple_content_template = """
Link: {paper_link}
Document: {paper_content}
"""

simple_web_search_template = """
Title: {title}
Link: {search_link}
Content: {search_content}
"""

def search_output_parser(response):
    contents = response["organic"]
    web_search_results = []
    for content in contents:
        title = content["title"]
        link = content["link"]
        snippet = content["snippet"]
        web_search_results.append(
            NodeWithScore(
                node=Document(text=simple_web_search_template.format(
                    title=title, 
                    search_link=link, 
                    search_content=snippet),
                    metadata={
                        "title": title,
                        "link": link,
                        "content": snippet
                    }
                ),
                score=1
            ))
    return web_search_results

def web_search_function(query, location: Optional[str] = None):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        # "gl": location
    })
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return search_output_parser(response.json())


def load_web_search_tool():
    
    rerank_postprocessor = SentenceTransformerRerank(
        model='mixedbread-ai/mxbai-rerank-xsmall-v1',
        top_n=5, # number of nodes after re-ranking, 
        keep_retrieval_score=True
    )
    
    def search_web(query_str: str):
        """
        Search the internet for information on a given query
        
        """
        
        web_search_results = web_search_function(query_str)
            
        web_search_results = rerank_postprocessor.postprocess_nodes(
            web_search_results,
            query_str=query_str
        )

        return [res.metadata for res in web_search_results]
            
    return FunctionTool.from_defaults(search_web, description="Function to search the web, avoid using this tool if other tools can do the job")