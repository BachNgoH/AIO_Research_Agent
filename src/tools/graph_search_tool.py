from tqdm import tqdm
import json
import requests
import networkx as nx
from llama_index.core.schema import NodeWithScore

relationships_dict = {
    "Supporting Evidence": "Is Evidence For",
    "Methodological Basis": "Is Methodological Basis For",
    "Theoretical Foundation": "Is Theoretical Foundation For", 
    "Data Source": "Is Data Source For",
    "Extension or Continuation": "Is Extension or Continuation Of",
}

class PaperNode:
    title: str
    arxiv_id: str
    citation_count: int
    abbreviation: str
    def __init__(self, title, arxiv_id, citation_count, abbrv):
        self.title=title
        self.arxiv_id=arxiv_id
        self.citation_count=citation_count
        self.abbreviation=abbrv
        
    
    def __str__(self) -> str:
        return f"Title: {self.title},\n Arxiv ID: {self.arxiv_id}"

class PaperEdge:
    category: str
    explanation: str
    verbose = True

    def __init__(self, category, explanation):
        self.category = category
        self.explanation = explanation

    def __str__(self) -> str:
        if self.verbose:
            return f"Category: {self.category},\n Explanation: {self.explanation}"
        else:
            return f"Category: {self.category}"

def get_abbreviate_title(title):
    if ":" in title:
        return title.split(":")[0]
    # List of common stopwords to exclude from the abbreviation
    stopwords = set([
        "a", "an", "the", "and", "or", "but", "if", "while", "with",
        "of", "at", "by", "for", "to", "in", "on", "over", "under"
    ])
    
    # Split the title into words
    words = title.split()
    
    # Collect the first letter of each significant word (not in stopwords)
    abbreviation = ''.join([word[0].upper() for word in words if word.lower() not in stopwords])
    
    return abbreviation

def find_connected_nodes(graph, node, relationship=None):
    """
    Find nodes connected to the given node with an optional filter on the type of relationship.
    """
    connected_nodes = []
    for n, nbrs in graph.adj.items():
        if n == node:
            for nbr, eattr in nbrs.items():
                if relationship is None or eattr['label'] == relationship:
                    connected_nodes.append(nbr)
    return connected_nodes

# Function to search for a node by arxiv_id and return its details
def find_nodes_by_arxiv_id(graph, arxiv_id):
    for node, data in graph.nodes(data=True):
        if data.get('arxiv_id') == arxiv_id:
            return data  # or return data['paper_node'] to return the PaperNode object itself
    return "Paper not found in the graph."


def find_shortest_path(graph, source, target):
    """
    Find the shortest path between two nodes.
    """
    try:
        path = nx.shortest_path(graph, source=source, target=target)
        return path
    except nx.NetworkXNoPath:
        return None


def find_nodes_by_keyword(graph, keyword):
    """
    Find nodes that contain the given keyword in their name and retrieve their connected nodes and relationships.
    """
    keyword = keyword.lower()  # Convert keyword to lowercase for case-insensitive matching
    matching_nodes = [node for node in graph.nodes if keyword in node.lower()]

    # related_nodes = {}
    # for node in matching_nodes:
    #     connections = []
    #     for neighbor, details in graph[node].items():
    #         connections.append((neighbor, details['title'].split('\n')[0]))
    #     related_nodes[node] = connections

    return matching_nodes

def find_graph_nodes_from_retriever(graph, retrieved_nodes):
    all_nodes = []
    for r in retrieved_nodes:
        title = r.text.split("\n")[0]
        nodes = find_nodes_by_keyword(graph, title)
        if len(nodes) > 0:
            all_nodes += nodes
            
    return all_nodes

def load_graph_data() -> nx.DiGraph:
    paper_dict = {}
    with open("./outputs/parsed_arxiv_papers.json") as f:
        annotated_article = json.load(f)

    for article_dict in tqdm(annotated_article, total=len(annotated_article)):
        paper_dict[article_dict['title'].lower()] = PaperNode(title=article_dict['title'], arxiv_id=article_dict['arxiv_id'])

        if "mapped_citation" in article_dict.keys():
            for key,val in article_dict['mapped_citation'].items():
                title = val['title']
                if title not in paper_dict.keys():
                    paper_node = PaperNode(title=val['title'], arxiv_id=val['arxiv_id'])
                    paper_dict[title] = paper_node

    triplets = []
    error_count = 0

    for article_dict in annotated_article:
        if "mapped_citation" not in article_dict.keys():
            print(article_dict['title'])
            continue
        for key, val in article_dict['mapped_citation'].items():
            title = val['title']
            citation = val['citation']
            
            # Use a dictionary to group explanations by category
            category_explanations = {}
            for rel in citation:
                # try:
                if 'Category' in rel.keys() and 'Explanation' in rel.keys():
                    category = rel['Category']
                    explanation = rel['Explanation']
                    if category not in category_explanations:
                        category_explanations[category] = []
                    category_explanations[category].append(explanation)
                else:
                    error_count += 1


            source_node = paper_dict[title]
            target_node = paper_dict[article_dict['title'].lower()]

            # Construct triplets with aggregated explanations for each category
            if len(category_explanations.items()) > 0:
                for category, explanations in category_explanations.items():
                    if category not in relationships_dict.keys():
                        relationships_dict[category] = f"Is {category} Of"

                    aggregated_explanation = "; ".join(set(explanations))  # Remove duplicates and join explanations
                    rel = PaperEdge(category=category, explanation=aggregated_explanation)
                    reverse_rel = PaperEdge(category=relationships_dict[category], explanation=aggregated_explanation)

                    # Add the relationship in both directions
                    triplets.append((source_node, rel, target_node))
                    triplets.append((target_node, reverse_rel, source_node))
            else:
                rel = PaperEdge(category="Unk", explanation="Unk")
                triplets.append((source_node, rel, target_node))
                
    print("Number of triplets: ", len(triplets))
    
    G = nx.DiGraph()

    # Add nodes and edges
    for source_node, relationship, target_node in triplets:
        # Add nodes if they are not already in the graph
        if source_node.arxiv_id not in G:
            G.add_node(source_node.title, title=str(source_node), arxiv_id=source_node.arxiv_id)
        if target_node.arxiv_id not in G:
            G.add_node(target_node.title, title=str(target_node), arxiv_id=target_node.arxiv_id)
        
        # Add edge with relationship details
        G.add_edge(source_node.title, target_node.title, title=str(relationship), category=relationship.category, explanation=relationship.explanation)
        
    return G

def trim_graph_by_least_degree(G, max_nodes):
    """
    Trims a graph by removing nodes with the least degree until the number of nodes is less than or equal to max_nodes.
    
    Parameters:
    - G (nx.Graph): The original graph.
    - max_nodes (int): The maximum number of nodes the graph should have.
    """
    while len(G) > max_nodes:
        # Calculate the degree of each node
        degrees = G.degree()
        # Sort nodes by degree (ascending order) and remove the node with the smallest degree
        node_to_remove = sorted(degrees, key=lambda x: x[1])[0][0]
        G.remove_node(node_to_remove)
        
    return G

def create_ego_graph(retriever_response: NodeWithScore, service: str = "ss", graph: nx.DiGraph = None) -> nx.DiGraph:
    if service not in ["local", "ss"]:
        raise ValueError("Service must be either 'local' or 'ss'.")
    if service == "local":
                    
        graph_nodes = find_graph_nodes_from_retriever(graph, retriever_response)
        
        # Generate ego graphs
        ego_graphs = [nx.ego_graph(graph, node, radius=1) for node in graph_nodes]

        # Combine all ego graphs into one graph
        combined_ego_graph = nx.compose_all(ego_graphs)
        nodes_to_remove = [node for node in combined_ego_graph if combined_ego_graph.degree(node) < 3]

        # Remove the nodes from the ego graph
        combined_ego_graph.remove_nodes_from(nodes_to_remove)

        # Assign colors: highlighted nodes in red, others in blue
        highlight_color = "orange"
        for node in combined_ego_graph.nodes():
            if node in graph_nodes:
                combined_ego_graph.nodes[node]['color'] = highlight_color
        return trim_graph_by_least_degree(combined_ego_graph, 25)
    elif service == "ss":
        paper_ids = ["arxiv:"+ n.metadata["paper_id"] for n in retriever_response]
        url = 'https://api.semanticscholar.org/graph/v1/paper/batch'

        # Define which details about the paper you would like to receive in the response
        paper_data_query_params = {'fields': 'citationCount,references.title,references.paperId,references.citationCount'}
        G = nx.DiGraph()

        # Send the API request and store the response in a variable
        response = requests.post(url, params=paper_data_query_params, json={"ids": paper_ids})
        source_nodes = []
        if response.status_code == 200:
            data = response.json()
            for idx, item in enumerate(data):
                source_node = PaperNode(
                    title=retriever_response[idx].metadata["title"],
                    arxiv_id=retriever_response[idx].metadata["paper_id"],
                    citation_count=item["citationCount"],
                    abbrv=get_abbreviate_title(retriever_response[idx].metadata["title"])
                )
                source_nodes.append(source_node.abbreviation)
                for reference in item["references"]:
                    target_node = PaperNode(
                        title=reference["title"],
                        arxiv_id=reference["paperId"],
                        citation_count=reference["citationCount"],
                        abbrv=get_abbreviate_title(reference["title"])
                    )
                    if source_node.abbreviation not in G:
                        G.add_node(
                            source_node.abbreviation, 
                            size=min(100, source_node.citation_count * 10),
                            title=str(source_node), 
                            arxiv_id=source_node.arxiv_id, 
                            )
                    if target_node.abbreviation not in G:
                        G.add_node(
                            target_node.abbreviation, 
                            title=str(target_node), 
                            arxiv_id=target_node.arxiv_id, 
                            size=min(100, target_node.citation_count * 10) if target_node.citation_count is not None else 10)
                    G.add_edge(source_node.abbreviation, target_node.abbreviation)
            
            nodes_to_remove = [node for node in G if G.degree(node) < 2]

            # Remove the nodes from the ego graph
            G.remove_nodes_from(nodes_to_remove)
            # Assign colors: highlighted nodes in red, others in blue
            highlight_color = "orange"
            for node in G.nodes():
                if node in source_nodes:
                    G.nodes[node]['color'] = highlight_color

            return trim_graph_by_least_degree(G, 25)
        else:
            raise ValueError(f"Request failed with status code {response.status_code}.")