

<div align="center">
<img src="./public/logo_dark.png" alt="pipeline" width=500/>
</div>

<!-- 
### Training the citation annotate model

```bash
sh train_citation.sh

``` -->

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/AIVIETNAMResearch/AIO_Research_Agent)](https://github.com/AIVIETNAMResearch/AIO_Research_Agent/stargazers)[![GitHub issues](https://img.shields.io/github/issues/AIVIETNAMResearch/AIO_Research_Agent)](https://github.com/AIVIETNAMResearch/AIO_Research_Agent/issues)

# AIO Research Agent


AIO Research Agent is an all-in-one intelligent companion for navigating the world of academic research. Stay on top of the latest research, effortlessly find relevant papers, engage in insightful conversations with our AI Agent, and quickly grasp key takeaways with AI-generated summaries. 

</div>

## Features

- Daily Paper Updates: Stay current with the latest research.
- Targeted Search: Find the exact papers you need.
- AI Chat Interface: Converse naturally, refine your search, and get personalized recommendations.
- Concise Summaries: Quickly grasp key takeaways with AI-generated summaries.

## Demo


https://github.com/AIVIETNAMResearch/AIO_Research_Agent/assets/81065083/195df8e8-60c9-442a-9604-33d2a585ff97


## Getting Started
To install this application, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/AIVIETNAMResearch/AIO_Research_Agent.git
cd AIO_Research_Agent
```

**2. (Optional) Create and activate a virtual environment:**
- For Unix/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

- For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

**3. Install the required dependencies:**
```bash
pip install -r requirements.txt
```

## Data Preparation
This project uses research papers from arXiv to search for relevant publications based on your topics of interest. 

### Option 1: Download Pre-extracted Embeddings
For a quick start, download pre-extracted embeddings for chromaDB from Hugging Face in this [link](https://huggingface.co/datasets/BachNgoH/ArxivDB_base/tree/main) and place them in the `./DB` folder. This dataset contains embeddings of the abstracts of approximately 330,000 arXiv papers in the fields of AI, ML, and DS, created using the `mixedbread-ai/mxbai-embed-large-v1` model/.

### Option 2: Self-Ingest Data
If you prefer to ingest your own data, you can use the Kaggle arXiv dataset.

**1. Download Data:** Obtain the arXiv dataset from Kaggle and store it in the `./data` folder.

**2. Ingest Paper Data:**

```bash
python src/paper_ingest.py
```


**Starting the Application**

Once everything is ready, you can launch the application by running:

```bash
chainlit run chainlit_app.py
```
The default username and password are `admin` and `admin`. Proper authentication will be added in the future.

### Daily Paper Update (In Progress)
This feature is currently under development. Upon completion, the application will automatically download and process new papers daily. The embeddings of these new papers will be extracted, and a summary of the day's updates will be compiled into a daily report.

These reports will be published in a separate repository: https://github.com/BachNgoH/DailyAIReports.git. You can clone this repository and place it in the outputs directory if you'd like your chatbot to interact with the daily reports:

```bash
mkdir outputs
cd outputs
git clone https://github.com/BachNgoH/DailyAIReports.git
```


## Acknowldgement

AIO Research Agent is made possible by these key technologies:

- [LlamaIndex](https://www.llamaindex.ai/): Providing the RAG (Retrieval Augmented Generation) framework.
- [Chainlit](https://docs.chainlit.io/get-started/overview): Enabling the intuitive user interface.
