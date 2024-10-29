# app.py
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

INDEX_NAME = 'academic_papers'

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        # Generate embedding for the query
        query_vector = model.encode(query).tolist()
        # Search in Elasticsearch using both vector similarity and text matching
        body = {
            "size": 10,
            "query": {
                "bool": {
                    "should": [
                        {
                            "script_score": {
                                "query": {
                                    "bool": {
                                        "should": [
                                            {"match": {"title": query}},
                                            {"match": {"abstract": query}},
                                            {"match": {"keywords": query}},
                                        ]
                                    }
                                },
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                    "params": {"query_vector": query_vector}
                                }
                            }
                        },
                        {
                            "match": {
                                "title": {
                                    "query": query,
                                    "boost": 3  # Increase importance
                                }
                            }
                        },
                        {
                            "match": {
                                "abstract": {
                                    "query": query,
                                    "boost": 2
                                }
                            }
                        },
                        {
                            "match": {
                                "keywords": {
                                    "query": query,
                                    "boost": 2
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        res = es.search(index=INDEX_NAME, body=body)
        results = res['hits']['hits']
        return render_template('results.html', query=query, results=results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
