from elasticsearch import Elasticsearch
from flask import Flask

# 连接信息
cloud_id = "My_deployment:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDZlODAxZjQ5YzAwNDQ5MGRhNDFlOGM3Y2U0MmFmYmQxJGQ2ZTE2YjQ1OWNjMTRhNmZiNDE0ZGZmNmJmN2JjMjll"  # 从 Elastic Cloud 控制台获取
api_key = "TzVkMldKTUJDVjk5bTVXZVFFeGg6LVpiZk04UFZUUE95QXpjbE9VZUttdw=="

# 创建 Elasticsearch 客户端
client = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)
index_name = "course"
if not client.indices.exists(index=index_name):
    mappings = {
        "properties": {
            "title_vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": "true",
                "similarity": "cosine",
            }
        }
    }
    client.indices.create(index=index_name)
    with open('Amazon\data.json','r') as file:
        id = 0
        for line in file:
            data = json.loads(line)
            # Upload each document in the JSON data to Elasticsearch
            resp = client.index(index=index_name, id=id, body=data)
            # print(f"Document {id} indexed: {resp['result']}")
            id += 1
app = Flask(__name__)

@app.route("/")
def home():
    try:
        info = client.info()
        print("Connected to Elasticsearch:", info)
    except Exception as e:
        print("Error connecting to Elasticsearch:", e)
    return f"{info}"

if __name__ == "__main__":
    app.run(port=8000)
