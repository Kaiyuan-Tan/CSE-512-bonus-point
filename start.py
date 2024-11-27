from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request, send_from_directory, render_template
from urllib.request import urlopen
import json
from sentence_transformers import SentenceTransformer
from flask_cors import CORS
import yaml

def load_config(file_path):
    with open(file_path, 'r',encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config

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
CORS(app)

@app.route("/")
def home():
    return render_template('index.html')

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
    config = load_config("config.yaml")

    cloud_id = config["cloud_id"]
    api_key = config["api_key"]
    url = config["url"]
    INDEX_NAME = "course"

    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key
    )

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
        # print(result)

    app.run(port=31002)

