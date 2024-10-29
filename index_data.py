# index_data.py
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from sentence_transformers import SentenceTransformer

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Test Elasticsearch connection
if not es.ping():
    print("Could not connect to Elasticsearch")
    exit()
else:
    print("Connected to Elasticsearch")

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and suitable for small datasets

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

def index_data():
    with open('sample_data.json', 'r') as f:
        papers = json.load(f)
    actions = []
    for paper in papers:
        # Generate embedding for the abstract
        embedding = model.encode(paper['abstract'])
        paper['embedding'] = embedding.tolist()
        action = {
            "_index": INDEX_NAME,
            "_id": paper['id'],
            "_source": paper
        }
        actions.append(action)
    bulk(es, actions)
    print("Data indexed successfully.")

if __name__ == '__main__':
    create_index()
    index_data()
