from tqdm import tqdm
from datasets import load_dataset
import json
import re
import pandas as pd


def search_paper_by_name(name, title_dict):
    # matches = df_data['title'].str.contains(name, case=False, na=False, regex=False)
    # filtered_df = df_data[matches]
    # if len(filtered_df) == 0:
    #     return None
    # return filtered_df.iloc[0]['id']
    try:
        return title_dict[name]
    except:
        return None

# Function to normalize author names for comparison
def normalize_author_name(name):
    # Convert to lowercase and remove middle initials
    name = name.lower()
    name = re.sub(r"\s+[a-z]\.", "", name)  # Remove middle initials
    return name


# Refined function to identify and normalize the first author from a citation
def identify_and_normalize_first_author(citation_authors):
    # Check for 'et al.' and 'and' to find the first author
    if 'et al.' in citation_authors:
        first_author = citation_authors.split('et al.')[0].strip()
    elif ' and ' in citation_authors:
        first_author = citation_authors.rsplit(' and ', 1)[0].split(',')[0].strip()
    else:
        first_author = citation_authors.split(',')[0].strip()
    # Normalize the first author's name for comparison
    return first_author.lower()


# Function to split and parse citations in cases of citation 
# like (Culotta and Sorensen 2004; Bunescu and Mooney 2005; Ittoo and Bouma 2013)
def split_and_parse_citation(citation):

    # Remove outer parentheses
    citation = citation.strip("()")
    # Split on semicolon if it's present, indicating multiple citations within one
    if ';' in citation:
        sub_citations = citation.split(';')
    else:
        sub_citations = [citation]
    
    # Parse each sub-citation for author names and year
    for sub_citation in sub_citations:
        # Splitting based on the last occurrence of space which is assumed to be before the year
        *authors, year = sub_citation.rsplit(' ', 1)
        authors = ' '.join(authors)  # Joining back the authors in case there are multiple names
        parsed_citation = {'Author': identify_and_normalize_first_author(authors), 'Year': year}
    
    return parsed_citation

# Function to normalize and extract the first author's name
def get_first_author(authors_str):
    first_author = authors_str.split(';')[0].strip()
    # Normalize the first author's name for comparison
    return first_author.lower()

# Generalized regular expression for detecting years in various date formats and standalone years

# Function to detect various year patterns and extract the year
def extract_years(string):
    general_year_pattern = re.compile(r'(?:\b|\D)(\d{4})(?:\b|\D)')
    # Find all matches for the general year pattern

    matches = general_year_pattern.findall(string)
    # Add all unique years found in this string
    year = matches[0] if matches else None
    return year

# Function to match citations with references
def match_citations_with_references(citation, references):
    match = None
    citation_first_author = citation['Author']
    citation_year = citation['Year'].strip()
    for ref in references:
        ref_first_author = get_first_author(ref['authors'])
        ref_year = extract_years(ref['year']) if ref['year'] is not None else None
        # Check for match by first author and year
        if citation_first_author in ref_first_author: #and (citation_year == ref_year or ref_year is None):
            match = {
                'ref_id': ref['ref_id']
            }
    return match

def preprocess_citation_author_year(article):
    for citation in article['citation_data']:
        try:
            parsed_name = split_and_parse_citation(citation['Citation'])
            match = match_citations_with_references(parsed_name, article['references'])
            citation['ref_id'] = match['ref_id'] if match else None
        except:
            citation['ref_id'] = None
    return article

# Function to regroup citations by ref_id
def regroup_citations_by_ref_id(citations):
    grouped_citations = {}
    for citation in citations:
        if 'ref_id' in citation.keys():
            ref_id = citation['ref_id']
            # Create a copy of the citation without the ref_id
            citation_copy = {k: v for k, v in citation.items() if k != 'ref_id'}
            # Append the citation to the list associated with its ref_id
            if ref_id in grouped_citations:
                grouped_citations[ref_id].append(citation_copy)
            else:
                grouped_citations[ref_id] = [citation_copy]
    return grouped_citations


def split_numeric_citations(citations):
    # Helper function to parse ranges and individual numbers
    def parse_part(part):
        if '-' in part:  # Handle ranges
            start, end = map(int, part.split('-'))
            return list(range(start, end + 1))
        else:  # Handle individual numbers
            return [int(part)]

    # Initialize the result list
    result = []

    # Find all parts of the input that match the patterns
    parts = re.findall(r'\[([^]]+)]', citations)
    
    for part in parts:
        # For each part, remove spaces, split by commas and extend the result list
        for subpart in part.replace(' ', '').split(','):
            try:
                result.extend(parse_part(subpart))
            except:
                continue

    return [f"[{num}]" for num in result]

# Function to apply citation splitting to a list of citation entries
def split_citations_in_entries(citation_entries):
    expanded_citation_entries = []
    for entry in citation_entries:
        try:
        # Use the split_citations function to get a list of individual citations from the Citation field
            split_citations_list = split_numeric_citations(entry['Citation'])
            for citation in split_citations_list:
                # Create a new citation entry for each split citation, keeping other fields the same
                
                new_entry = {
                    'Citation': citation,
                    'Category': entry['Category'],
                    'Explanation': entry['Explanation']
                }
                expanded_citation_entries.append(new_entry)
        except:
            continue
    return expanded_citation_entries


def proprocess_citation_numeric(article):
    
    article['citation_data'] = split_citations_in_entries(article['citation_data'])
    article['citation_data'] = match_numeric_citation(article['citation_data'])
    return article

def detect_citation_style(text):
    # Pattern to match numeric citations like [1], [1, 2], [1-6], [1, 2-6], [1, 2, 3-6], etc.
    numeric_pattern = re.compile(r'\[\d+(-\d+)?(,\s*\d+(-\d+)?)*\]')
    # Pattern for "Author-Year" citations like (Author, Year)
    author_year_pattern = re.compile(r'\([A-Za-z]+,\s*\d{4}\)')

    # Check for numeric citation style
    if numeric_pattern.search(text):
        return "Numeric"
    # Check for author-year citation style
    elif author_year_pattern.search(text):
        return "Author-Year"
    else:
        return "Author-Year"

def match_numeric_citation(citations):
    for citation in citations:
        # Regular expression to find single numbers inside square brackets
        pattern = re.compile(r'\[\(?(?P<number>\d+)\)?\]')
        try:
            #Find all matches in the text and convert them to integers
            reference_num = [int(match.group('number')) for match in pattern.finditer(citation['Citation'])][0]
            citation['ref_id'] = f"b{reference_num -1}"

        except:
            continue
    return citations



def load_and_save_graph_data():
    cols = ['id', 'title', 'abstract', 'categories', 'update_date', 'authors']
    data = []
    file_name = './data/arxiv-metadata-oai-snapshot.json'


    with open(file_name, encoding='latin-1') as f:
        for line in tqdm(f):
            doc = json.loads(line)
            lst = [doc['id'], doc['title'], doc['abstract'], doc['categories'], doc['update_date'], doc['authors_parsed']]
            data.append(lst)

    df_data = pd.DataFrame(data=data, columns=cols)
    title_dict = {title.lower(): arxiv_id for title, arxiv_id in zip(df_data['title'].tolist(), df_data['id'].to_list())}
    
    parsed_article = load_dataset("BachNgoH/ParsedArxivPapers")['train']
    parsed_article = parsed_article.to_list()

    for article in parsed_article:
        if article['citation_data'] is not None:
            article['citation_data'] = json.loads(article['citation_data'])
    annotated_article = [x for x in parsed_article if x['citation_data'] is not None]
    print(f"Loading data successfully! Number of annotated papers: {len(annotated_article)}")
    
    

    for article in tqdm(annotated_article, total=len(annotated_article)):
        # references = article['references']
        if len(article['citation_data']) == 0:
            continue
        citation_style = detect_citation_style(article['citation_data'][0]["Citation"])
        # try:
        if citation_style == "Author-Year":
            article = preprocess_citation_author_year(article)
        elif citation_style == "Numeric":
            article = proprocess_citation_numeric(article)
        else:
            print(f"Uncertain citation style: {citation_style}")
            continue
        # except Exception as e:
        #     print(article['citation_data'])
        #     print(e)
        #     break

        grouped_citations = regroup_citations_by_ref_id(article['citation_data'])
        article['grouped_citations'] = grouped_citations
    

    print("Adding paper id")
    for article_dict in tqdm(annotated_article, total=len(annotated_article)):

        article_dict["arxiv_id"] = search_paper_by_name(article_dict['title'].lower(), title_dict)

        if "grouped_citations" in article_dict.keys():
            article_dict["mapped_citation"] = {}
            for key,val in article_dict['grouped_citations'].items():
                for ref in article_dict["references"]:
                    if ref["ref_id"] == key:
                        title = ref["title"]

                title = title.lower()
                arxiv_id = search_paper_by_name(title, title_dict)
                article_dict['mapped_citation'][key] = {"title": title, 'arxiv_id': arxiv_id, 'citation': val}
                
    with open("./outputs/parsed_arxiv_papers.json", "w") as f:
        json.dump(annotated_article, f)

    print("Done processing!")
    
    
if __name__ == "__main__":
    load_and_save_graph_data()