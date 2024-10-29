# fetch_and_index_arxiv.py
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from sentence_transformers import SentenceTransformer
import xml.etree.ElementTree as ET

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Test Elasticsearch connection
if not es.ping():
    print("Could not connect to Elasticsearch")
    exit()
else:
    print("Connected to Elasticsearch")

INDEX_NAME = 'academic_papers'

def create_index():
    # Delete the index if it already exists
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    # Define the index mapping
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "authors": {"type": "text"},
                "abstract": {"type": "text"},
                "year": {"type": "integer"},
                "keywords": {"type": "text"},
                "embedding": {"type": "dense_vector", "dims": 384}
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=mapping)
    print("Index created.")

def fetch_arxiv_papers(max_results=1000):
    base_url = "http://export.arxiv.org/api/query?"
    query = "all"
    batch_size = 100  # arXiv API allows up to 30000 requests per day
    papers = []
    for start in range(0, max_results, batch_size):
        params = f"search_query={query}&start={start}&max_results={batch_size}&sortBy=submittedDate&sortOrder=descending"
        response = requests.get(base_url + params)
        if response.status_code != 200:
            print(f"Error fetching data from arXiv at start={start}.")
            continue
        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', namespace)
        if not entries:
            break  # No more entries
        for entry in entries:
            paper = {}
            paper['id'] = entry.find('atom:id', namespace).text
            paper['title'] = entry.find('atom:title', namespace).text.strip().replace('\n', ' ')
            authors = entry.findall('atom:author', namespace)
            paper['authors'] = [author.find('atom:name', namespace).text for author in authors]
            paper['abstract'] = entry.find('atom:summary', namespace).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', namespace).text
            paper['year'] = int(published[:4])
            # Extract categories as keywords
            categories = entry.findall('atom:category', namespace)
            paper['keywords'] = [category.get('term') for category in categories]
            papers.append(paper)
        print(f"Fetched {len(entries)} papers starting from {start}.")
    return papers

def index_papers(papers):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    actions = []
    for i, paper in enumerate(papers):
        # Generate embedding for the abstract
        embedding = model.encode(paper['abstract'])
        paper['embedding'] = embedding.tolist()
        action = {
            "_index": INDEX_NAME,
            "_id": paper['id'],
            "_source": paper
        }
        actions.append(action)
        # Bulk index every 100 documents
        if (i + 1) % 100 == 0 or (i + 1) == len(papers):
            bulk(es, actions)
            actions = []
            print(f"Indexed {i + 1} papers.")
    print(f"Total papers indexed: {len(papers)}")

if __name__ == '__main__':
    create_index()
    papers = fetch_arxiv_papers(max_results=1000)  # Adjust max_results as needed
    if papers:
        index_papers(papers)
    else:
        print("No papers found to index.")
