from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
from urllib.request import urlopen
import json
from sentence_transformers import SentenceTransformer


cloud_id = "My_deployment:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDZlODAxZjQ5YzAwNDQ5MGRhNDFlOGM3Y2U0MmFmYmQxJGQ2ZTE2YjQ1OWNjMTRhNmZiNDE0ZGZmNmJmN2JjMjll"  # 从 Elastic Cloud 控制台获取
api_key = "TzVkMldKTUJDVjk5bTVXZVFFeGg6LVpiZk04UFZUUE95QXpjbE9VZUttdw=="
url = "https://raw.githubusercontent.com/Kaiyuan-Tan/CSE-512-bonus-point/refs/heads/main/data.json"
model = SentenceTransformer("all-MiniLM-L6-v2")

client = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)
INDEX_NAME = "course"
# if client.indices.exists(index=INDEX_NAME):
    # client.indices.delete(index=INDEX_NAME)
if not client.indices.exists(index=INDEX_NAME):
    mappings = {
        "properties": {
            "title": {
                "type": "text",
            },
            "code": {
                "type": "integer",
            },
            "subject": {
                "type": "keyword",
            }, 
            "description_vector": {
                "type": "dense_vector",
                "dims": 384,
            },
            "instructor": {
                "type": "text",
            },    
        }
    }
    response = urlopen(url)
    courses = json.loads(response.read())
    operations = []
    client.indices.create(index=INDEX_NAME, mappings=mappings)
    for course in courses:
        operations.append({"index": {"_index": INDEX_NAME}})
        # Transforming the title into an embedding using the model
        course["description_vector"] = model.encode(course["description"]).tolist()
        operations.append(course)
    result = client.bulk(index=INDEX_NAME, operations=operations, refresh=True)
    print(result)

def pretty_response(response):
    outputs = []
    if len(response["hits"]["hits"]) == 0:
        return("Your search returned no results.")
    else:
        for hit in response["hits"]["hits"]:
            score = hit["_score"]
            pretty_output = {
                "title": hit["_source"]["title"],
                "code": hit["_source"]["code"],
                "subject": hit["_source"]["subject"],
                "description": hit["_source"]["description"],
                "instructor": hit["_source"]["instructor"],
                "credit": hit["_source"]["credit"]
            }
            outputs.append(pretty_output)
    return outputs
app = Flask(__name__)

@app.route("/")
def home():
    try:
        info = client.info()
        print("Connected to Elasticsearch:", info)
    except Exception as e:
        print("Error connecting to Elasticsearch:", e)
    return f"{info}"

@app.route("/search", methods=['GET'])
def search():
    description = request.args.get("description")  # get parameter
    response = client.search(
        index=INDEX_NAME,
        knn={
            "field": "description_vector",
            "query_vector": model.encode(description),
            "k": 10,
            "num_candidates": 100,
        },
    )
    # return pretty_response(response)
    return jsonify({"message": f"Get data successfully", "data": pretty_response(response)}), 200

@app.route("/filter", methods=['GET'])
def find():
    code = request.args.get("code") 
    title = request.args.get("title") 
    subject = request.args.get("subject") 
    instructor = request.args.get("instructor") 
    filter = []

    if subject:
        filter.append({"term": {"subject": subject}})
    if code:
        filter.append({"term": {"code": code}})
    if title:
        filter.append({"match": {"title": title}})
    if instructor:
        filter.append({"match": {"instructor": instructor}})

    query = {
        "query": {
            "bool": {
                "filter": filter
            }
        }
    }
    response = client.search(index=INDEX_NAME, body=query)
    return jsonify({"message": f"Get data successfully", "data": pretty_response(response)}), 200



if __name__ == "__main__":
    app.run(port=8000)
